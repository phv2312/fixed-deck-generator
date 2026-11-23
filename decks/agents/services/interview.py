from typing import get_args

from decks.agents.catalog import SlideCatalog
from decks.agents.exceptions import (
    InvalidThemeError,
    MetaLengthMismatchError,
    NoSlidesError,
    PlanIncompleteError,
    PlanMetaMissingError,
    PlanMissingError,
    SlideNotFoundError,
    UnsupportedKindError,
)
from decks.agents.models import CheckIssue, PlanCheck, PlanUpdated, PlanView, VarietyViolation
from decks.agents.repos import Repos
from decks.agents.services.events import EventSink
from decks.agents.services.variety import VarietyPolicy
from decks.models.plan import (
    REQUIRED_META,
    ContentBlock,
    Plan,
    SlideDraft,
    SlideDraftPatch,
    SlideInput,
)
from decks.models.theme import ThemeName

MAX_CHECKS = 3  # the first final_check and two revisions


class InterviewService:
    """Read and change the plan of one project.

    One instance serves one chat turn. It counts the reads and the checks of that turn.
    """

    def __init__(
        self,
        repos: Repos,
        sink: EventSink,
        catalog: SlideCatalog,
        *,
        visuals_available: bool = True,
    ) -> None:
        self._repos = repos
        self._sink = sink
        self._catalog = catalog
        self._variety = VarietyPolicy(catalog, visuals_available=visuals_available)
        self._checks = 0

    def read(self) -> Plan:
        """Return the plan, or an empty one when none exists yet."""
        return self._repos.plan.load() or Plan()

    def variety(self, plan: Plan, *, complete: bool = False) -> list[VarietyViolation]:
        """Return the variety advice. ``complete`` checks the first and last slide too."""
        if not plan.slides:
            return []
        return self._variety.violations(plan, complete=complete)

    def snapshot(self) -> PlanView:
        """Summarise the plan with its advice and next step, for the interview prompt."""
        plan = self.read()
        return PlanView.of(plan, self.variety(plan), self.next_action(plan))

    def next_action(self, plan: Plan) -> str:
        """Tell the agent the one step that follows the state of ``plan``."""
        gaps = [key for key in REQUIRED_META if not plan.meta.get(key)]
        if gaps:
            return (
                f"Ask the user with ask_user_question, or pick a default, then call set_meta "
                f"for: {', '.join(gaps)}."
            )
        if not plan.slides:
            return (
                "Make the pictures the slides need, then call add_plan_slides once with every "
                "slide. The first has kind title; the last has kind terminal, contact or statement."
            )
        issues = self.variety(plan, complete=True)
        if issues:
            return f"Fix {issues[0].line}. Then call final_check."
        return "Call final_check, then summarise the plan in two sentences and stop."

    def final_check(self) -> PlanCheck:
        """Check the whole plan. It lists concrete issues and stops asking for fixes after two."""
        plan = self.read()
        if not plan.slides:
            raise NoSlidesError
        self._checks += 1
        issues = [
            CheckIssue(slide_id=v.slide_id, fix=v.message)
            for v in self.variety(plan, complete=True)
        ]
        remaining = max(MAX_CHECKS - self._checks, 0)
        return PlanCheck(
            revision=plan.revision,
            ok=not issues,
            issues=issues,
            checks_remaining=remaining,
            next_action=self._check_action(issues, remaining),
        )

    def _check_action(self, issues: list[CheckIssue], remaining: int) -> str:
        if not issues:
            return "The plan is complete. Summarise it in two sentences and stop."
        if remaining == 0:
            return "Stop revising. Summarise the plan and tell the user about the open issues."
        return (
            "Fix the issues with update_plan_slide, remove_plan_slide, move_plan_slide or "
            f"add_plan_slides, then call final_check again ({remaining} left)."
        )

    async def set_meta(self, key: str, value: str) -> Plan:
        """Set one meta key. The key ``theme`` is validated and stored as the theme."""
        return await self.set_metas([key], [value])

    async def set_metas(self, keys: list[str], values: list[str]) -> Plan:
        """Set several meta keys in one commit. ``keys`` and ``values`` have equal length."""
        if len(keys) != len(values):
            raise MetaLengthMismatchError(len(keys), len(values))
        plan = self.read()
        for key, value in zip(keys, values, strict=True):
            plan = self._with_meta(plan, key, value)
        return await self._commit(plan)

    def _with_meta(self, plan: Plan, key: str, value: str) -> Plan:
        if key != "theme":
            return plan.model_copy(update={"meta": {**plan.meta, key: value}})
        allowed = list(get_args(ThemeName))
        if value not in allowed:
            raise InvalidThemeError(value, allowed)
        return plan.model_copy(update={"theme": value})

    async def remove_meta(self, key: str) -> Plan:
        """Remove one meta key. Removing an unknown key changes nothing."""
        plan = self.read()
        return await self._commit(
            plan.model_copy(update={"meta": {k: v for k, v in plan.meta.items() if k != key}})
        )

    async def add_slide(
        self,
        *,
        after_id: str | None,
        purpose: str,
        title: str,
        kind: str | None,
        content: ContentBlock,
    ) -> tuple[Plan, SlideDraft]:
        """Insert a slide after ``after_id``, or at the end. Return the plan and the new slide."""
        plan = self.read()
        self._check_kind(kind)
        self._require_meta(plan)
        draft = SlideDraft(
            id=plan.next_slide_id, kind=kind, purpose=purpose, title=title, content=content
        )
        slides = list(plan.slides)
        position = len(slides)
        if after_id is not None:
            position = self._index(plan, after_id) + 1
        slides.insert(position, draft)
        return await self._commit(plan.model_copy(update={"slides": slides})), draft

    async def add_slides(self, slides: list[SlideInput], *, after_id: str | None) -> Plan:
        """Insert ``slides`` in order after ``after_id``, or at the end, in one commit."""
        plan = self.read()
        for item in slides:
            self._check_kind(item.kind)
        self._require_meta(plan)
        position = len(plan.slides) if after_id is None else self._index(plan, after_id) + 1
        numbers = int(plan.next_slide_id[1:])
        drafts = [
            SlideDraft(
                id=f"p{numbers + offset}",
                kind=item.kind,
                purpose=item.purpose,
                title=item.title,
                content=item.content,
            )
            for offset, item in enumerate(slides)
        ]
        merged = [*plan.slides[:position], *drafts, *plan.slides[position:]]
        return await self._commit(plan.model_copy(update={"slides": merged}))

    async def move_slide(self, slide_id: str, after_id: str | None) -> Plan:
        """Move a slide after ``after_id``, or to the start when ``after_id`` is ``None``."""
        plan = self.read()
        moved = plan.slides[self._index(plan, slide_id)]
        rest = [s for s in plan.slides if s.id != slide_id]
        position = 0
        if after_id is not None:
            position = self._index(plan.model_copy(update={"slides": rest}), after_id) + 1
        rest.insert(position, moved)
        return await self._commit(plan.model_copy(update={"slides": rest}))

    async def update_slide(self, slide_id: str, patch: SlideDraftPatch) -> tuple[Plan, SlideDraft]:
        """Apply ``patch`` to a slide. Return the plan and the changed slide."""
        plan = self.read()
        self._check_kind(patch.kind)
        draft = plan.slides[self._index(plan, slide_id)]
        changes = patch.model_dump(exclude_none=True, exclude={"content"})
        if patch.content is not None:
            changes["content"] = patch.content
        changed = draft.model_copy(update=changes)
        slides = [changed if s.id == slide_id else s for s in plan.slides]
        return await self._commit(plan.model_copy(update={"slides": slides})), changed

    async def remove_slide(self, slide_id: str) -> Plan:
        """Remove a slide."""
        plan = self.read()
        self._index(plan, slide_id)
        slides = [s for s in plan.slides if s.id != slide_id]
        return await self._commit(plan.model_copy(update={"slides": slides}))

    async def approve(self) -> Plan:
        """Approve the plan. Raise when it is missing or incomplete."""
        plan = self._repos.plan.load()
        if plan is None:
            raise PlanMissingError
        if plan.missing:
            raise PlanIncompleteError(plan.missing)
        approved = plan.model_copy(update={"approved": True})
        self._repos.plan.save(approved)
        state = self._repos.project.load_state()
        self._repos.project.save_state(state.model_copy(update={"phase": "approved"}))
        return approved

    def _require_meta(self, plan: Plan) -> None:
        gaps = [key for key in REQUIRED_META if not plan.meta.get(key)]
        if gaps:
            raise PlanMetaMissingError(gaps)

    def _check_kind(self, kind: str | None) -> None:
        if kind is not None and kind not in self._catalog:
            raise UnsupportedKindError(kind)

    def _index(self, plan: Plan, slide_id: str) -> int:
        index = plan.index_of(slide_id)
        if index is None:
            raise SlideNotFoundError(slide_id)
        return index

    async def _commit(self, plan: Plan) -> Plan:
        saved = plan.model_copy(update={"revision": plan.revision + 1, "approved": False})
        self._repos.plan.save(saved)
        state = self._repos.project.load_state()
        self._repos.project.save_state(
            state.model_copy(
                update={
                    "plan_revision": saved.revision,
                    "phase": saved.phase_after_edit(state.phase),
                }
            )
        )
        await self._sink.emit(
            PlanUpdated(
                revision=saved.revision, slide_count=len(saved.slides), missing=saved.missing
            )
        )
        return saved
