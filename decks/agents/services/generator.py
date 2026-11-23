import asyncio
from dataclasses import dataclass, field

from agents import Agent, AgentOutputSchema, RunConfig, Runner
from agents.exceptions import AgentsException
from pydantic import ValidationError

from decks.agents.catalog import FALLBACK_KIND, SlideCatalog
from decks.agents.exceptions import (
    DeckMissingError,
    FillFailedError,
    GenerationInProgressError,
    PlanIncompleteError,
    PlanMissingError,
    PlanNotApprovedError,
    RepairBudgetExceededError,
    SlideNotFoundError,
)
from decks.agents.models import DeckProgress, DeckReady, DeckReport, FixResult, LayoutIssue
from decks.agents.prompts import FILL_SYSTEM
from decks.agents.repos import Repos
from decks.agents.repos.assets import ASSET_DIR
from decks.agents.services.checker import DeckChecker
from decks.agents.services.events import EventSink
from decks.agents.services.fallback import SlideFallback
from decks.agents.services.fitter import LayoutFitter
from decks.models.build import MAX_REPAIRS, BuildState, BuiltSlide
from decks.models.plan import Plan, SlideDraft
from decks.models.slides import Deck, Slide
from decks.models.theme import FONT, THEMES
from decks.visuals.service import VisualService

DEFAULT_CONCURRENCY = 4  # slides filled in parallel
MAX_FILL_ATTEMPTS = 2  # first try plus one retry with the error as feedback
ERROR_DETAIL_CHARS = 120  # longest error text kept in a warning
FILL_MAX_TURNS = 1  # the filler agent answers in one turn


@dataclass
class FilledSlide:
    """Result of filling one slide."""

    draft: SlideDraft
    slide: Slide | None
    warnings: list[str] = field(default_factory=list)


class DeckGenerator:
    """Build the deck of one project. Needs an approved, complete plan."""

    def __init__(
        self,
        repos: Repos,
        sink: EventSink,
        catalog: SlideCatalog,
        checker: DeckChecker,
        *,
        run_config: RunConfig | None = None,
        concurrency: int = DEFAULT_CONCURRENCY,
        visuals: VisualService | None = None,
    ) -> None:
        self._repos = repos
        self._sink = sink
        self._catalog = catalog
        self._checker = checker
        self._run_config = run_config or RunConfig()
        self._concurrency = concurrency
        self._visuals = visuals
        self._fallbacks = SlideFallback(catalog)
        self._fitter = LayoutFitter()

    async def generate(self) -> DeckReport:
        """Build every missing or changed slide and return a small report."""
        plan = self._precondition()
        if self._repos.lock.locked():
            raise GenerationInProgressError(self._repos.project_id)
        async with self._repos.lock:
            before = self._repos.project.load_state()
            self._repos.project.save_state(
                before.model_copy(update={"phase": "generating", "repairs_remaining": MAX_REPAIRS})
            )
            try:
                report = await self._generate(plan)
            except BaseException:
                self._repos.project.save_state(before)
                raise
        await self._sink.emit(
            DeckReady(built=report.built, failed=report.failed, warnings=report.warnings)
        )
        return report

    async def fix_slide(self, slide_id: str, instructions: str) -> FixResult:
        """Refill one slide with ``instructions``. Each call uses one repair."""
        plan = self._precondition()
        async with self._repos.lock:
            deck = self._repos.deck.load()
            if deck is None:
                raise DeckMissingError
            draft = plan.slide(slide_id)
            index = next((i for i, s in enumerate(deck.slides) if s.id == slide_id), None)
            if draft is None or index is None:
                raise SlideNotFoundError(slide_id)
            state = self._repos.project.load_state()
            if state.repairs_remaining <= 0:
                raise RepairBudgetExceededError(self._repos.project_id)
            filled = await self._fill(draft, plan, instructions)
            if filled.slide is None:
                raise FillFailedError(draft.kind or FALLBACK_KIND, slide_id, "no slide built")
            slides = list(deck.slides)
            slides[index] = filled.slide.numbered(index + 1)
            revision = deck.revision + 1
            self._repos.deck.save(deck.model_copy(update={"slides": slides, "revision": revision}))
            built = {
                **state.built,
                slide_id: BuiltSlide(
                    content_hash=draft.content_hash, revision=revision, warnings=filled.warnings
                ),
            }
            left = state.repairs_remaining - 1
            self._repos.project.save_state(
                state.model_copy(
                    update={"built": built, "deck_revision": revision, "repairs_remaining": left}
                )
            )
        return FixResult(
            slide_id=slide_id,
            issues=self._checker.check_slide(slides[index], draft),
            repairs_remaining=left,
        )

    def _precondition(self) -> Plan:
        plan = self._repos.plan.load()
        if plan is None:
            raise PlanMissingError
        if plan.missing:
            raise PlanIncompleteError(plan.missing)
        if not plan.approved:
            raise PlanNotApprovedError
        return plan

    async def _generate(self, plan: Plan) -> DeckReport:
        state = self._repos.project.load_state()
        deck = self._repos.deck.load()
        asset_warnings = await self._visuals.sync(plan.theme) if self._visuals else []
        targets = [
            s
            for s in plan.slides
            if s.id not in state.built or state.built[s.id].content_hash != s.content_hash
        ]
        if not targets and deck is not None and self._is_current(plan, deck):
            self._repos.project.save_state(state.model_copy(update={"phase": "generated"}))
            return DeckReport(
                built=0, failed=[], issues=[], warnings=asset_warnings, revision=deck.revision
            )
        results = await self._fill_all(targets, plan)
        warnings = [
            *asset_warnings,
            *(
                f"slide {s.id}: manual edits were replaced"
                for s in targets
                if s.id in state.built and state.built[s.id].edited
            ),
        ]
        return self._commit(plan, state, deck, results, warnings)

    def _is_current(self, plan: Plan, deck: Deck) -> bool:
        """Return whether ``deck`` already has the plan's theme, slides and slide order."""
        return deck.theme == plan.theme and [s.id for s in deck.slides] == [
            s.id for s in plan.slides
        ]

    def _commit(
        self,
        plan: Plan,
        state: BuildState,
        deck: Deck | None,
        results: list[FilledSlide],
        warnings: list[str],
    ) -> DeckReport:
        revision = (deck.revision if deck else 0) + 1
        fresh = {r.draft.id: r for r in results if r.slide is not None}
        old = {s.id: s for s in deck.slides} if deck else {}
        slides: list[Slide] = []
        built: dict[str, BuiltSlide] = {}
        for draft in plan.slides:
            if draft.id in fresh:
                slide = fresh[draft.id].slide
                built[draft.id] = BuiltSlide(
                    content_hash=draft.content_hash,
                    revision=revision,
                    warnings=fresh[draft.id].warnings,
                )
            elif draft.id in old:
                slide = old[draft.id]
                built[draft.id] = state.built[draft.id]
            else:
                continue
            if slide is not None:
                slides.append(slide.numbered(len(slides) + 1))
        new_deck = Deck(
            revision=revision,
            theme=plan.theme,
            palette=THEMES[plan.theme],
            font=FONT,
            slides=slides,
        )
        self._repos.deck.save(new_deck)
        self._repos.project.save_state(
            state.model_copy(
                update={"phase": "generated", "built": built, "deck_revision": revision}
            )
        )
        issues = self._checker.check_deck(new_deck, plan)
        failed = [r.draft.id for r in results if r.slide is None]
        all_warnings = warnings + [w for r in results for w in r.warnings]
        return DeckReport(
            built=len(fresh), failed=failed, issues=issues, warnings=all_warnings, revision=revision
        )

    def _valid(self, kind: str | None) -> str:
        kind = self._catalog.resolve(kind)
        return kind if kind is not None and kind in self._catalog else FALLBACK_KIND

    async def _fill_all(self, targets: list[SlideDraft], plan: Plan) -> list[FilledSlide]:
        gate = asyncio.Semaphore(self._concurrency)

        async def one(index: int, draft: SlideDraft) -> FilledSlide:
            async with gate:
                filled = await self._fill(draft, plan, "")
            await self._sink.emit(
                DeckProgress(
                    index=index, total=len(targets), slide_id=draft.id, kind=draft.kind or ""
                )
            )
            return filled

        return list(await asyncio.gather(*(one(i, d) for i, d in enumerate(targets, 1))))

    def _with_asset(self, draft: SlideDraft) -> SlideDraft | None:
        """Return ``draft`` with a project asset path made absolute, or ``None`` when unusable.

        A path that is not an asset path (a URL, a file path) stays as it is.
        """
        image = draft.content.image
        if image is None or not image.startswith(f"{ASSET_DIR}/"):
            return draft
        resolved = self._visuals.resolve(image) if self._visuals else None
        if resolved is None:
            return None
        return draft.model_copy(
            update={"content": draft.content.model_copy(update={"image": resolved})}
        )

    async def _fill(self, draft: SlideDraft, plan: Plan, feedback: str) -> FilledSlide:
        usable = self._with_asset(draft)
        if usable is None:
            imageless = draft.content.model_copy(update={"image": None})
            fallback = self._fallback(draft.model_copy(update={"content": imageless}))
            note = f"slide {draft.id}: asset {draft.content.image} is missing"
            return FilledSlide(draft, fallback.slide, [note, *fallback.warnings])
        draft = usable
        kind = self._valid(draft.kind)
        if "image" in self._catalog.required_fields(kind) and not draft.content.image:
            fallback = self._fallback(draft)
            note = f"slide {draft.id}: kind {kind} needs an image and the plan has none"
            return FilledSlide(draft, fallback.slide, [note, *fallback.warnings])
        cause = ""
        for _ in range(MAX_FILL_ATTEMPTS):
            try:
                slide = self._fitter.fit(await self._build(draft, plan, kind, feedback))
            except (AgentsException, ValidationError, ValueError) as exc:
                cause = (
                    f"{kind}: {type(exc).__name__}: {str(exc).splitlines()[0][:ERROR_DETAIL_CHARS]}"
                )
                feedback = f"The previous attempt failed: {exc}"
                continue
            errors = [i for i in self._checker.check_slide(slide, draft) if i.severity == "error"]
            if not errors:
                return FilledSlide(draft, slide)
            cause = f"{kind}: " + ", ".join(f"{i.code} {i.element_id} {i.message}" for i in errors)
            feedback = self._feedback(errors)
        return self._fallback(draft, cause)

    def _feedback(self, issues: list[LayoutIssue]) -> str:
        return "Fix these layout problems: " + "; ".join(
            f"{i.message} ({i.suggestion})" for i in issues
        )

    async def _build(self, draft: SlideDraft, plan: Plan, kind: str, feedback: str) -> Slide:
        builder = self._catalog.builder(kind)
        agent = Agent(
            name=f"fill-{kind}",
            instructions=FILL_SYSTEM,
            output_type=AgentOutputSchema(
                builder.SPEC, strict_json_schema=self._catalog.strict(kind)
            ),
        )
        result = await Runner.run(
            agent,
            self._fill_prompt(draft, plan, kind, feedback),
            max_turns=FILL_MAX_TURNS,
            run_config=self._run_config,
            session=None,
        )
        spec = builder.SPEC.model_validate(result.final_output)
        slide = Slide(
            id=draft.id,
            family=self._catalog.family_of(kind),
            kind=kind,
            elements=builder.build(spec),
        )
        return slide

    def _fill_prompt(self, draft: SlideDraft, plan: Plan, kind: str, feedback: str) -> str:
        outline = "\n".join(f"{i}. {s.title}" for i, s in enumerate(plan.slides, 1))
        parts = [
            f"Deck audience: {plan.meta.get('audience', '')}",
            f"Deck outline:\n{outline}",
            f"Slide kind: {kind}",
            f"Slide title: {draft.title}",
            f"Slide purpose: {draft.purpose}",
            f"Slide content (JSON): {draft.content.model_dump_json(exclude_defaults=True)}",
        ]
        if feedback:
            parts.append(f"Change request: {feedback}")
        return "\n\n".join(parts)

    def _fallback(self, draft: SlideDraft, cause: str = "") -> FilledSlide:
        slide, warnings = self._fallbacks.build(draft, cause=cause)
        return FilledSlide(draft, slide, warnings)
