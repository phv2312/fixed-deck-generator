import asyncio
from collections.abc import Callable
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError

from decks.agents.exceptions import DeckMissingError, TurnInProgressError
from decks.agents.repos import ProjectRepositories, Repos
from decks.agents.services.checker import DeckChecker
from decks.agents.services.deck_editor import DeckEditor
from decks.api.deck.exceptions import (
    ElementIdNotFoundError,
    InvalidElementChangeError,
    NothingToRedoError,
    NothingToUndoError,
    SlideIndexNotFoundError,
    StaleDeckRevisionError,
)
from decks.api.deck.models import (
    NEW_DEFAULTS,
    NEW_TYPES,
    READ_ONLY_FIELDS,
    DeckInfo,
    EditResult,
    ElementInfo,
    NewKind,
    SlideDigest,
    SlideHtml,
    SlideInfo,
)
from decks.models.elements import Element, Image, Table
from decks.models.history import DeckHistory
from decks.models.slides import Deck, Slide, ZMove
from decks.render.htmldoc.models import HtmlPageStyle
from decks.render.htmldoc.services import HtmlRenderer
from decks.table_layout import LAYOUT_FIELDS, TableLayout

# A slide page that sits in an iframe: no backdrop, no gap, and it scales to the frame width.
EMBEDDED_PAGE = HtmlPageStyle(title="Slide", backdrop="transparent", gap=0, margin=0)
SAFE_IMAGE_PREFIXES = ("http://", "https://", "data:image/")
ROWS = TypeAdapter(list[list[str]])


def new_element_id() -> str:
    """Return a new element id."""
    return f"e{uuid4().hex[:8]}"


class DeckService:
    """Read the built deck and edit its elements. Each edit is saved at once and can be undone.

    An edit waits for the write lock of the project and is refused while a chat turn runs,
    because the agent is then the only writer of the deck.
    """

    def __init__(
        self,
        repositories: ProjectRepositories,
        new_id: Callable[[], str] = new_element_id,
        table_layout: TableLayout | None = None,
    ) -> None:
        self._repositories = repositories
        self._new_id = new_id
        self._tables = table_layout or TableLayout()

    async def get(self, project_id: str) -> DeckInfo:
        """Return the deck with the box and the fields of every element."""
        repos = self._repositories.for_project(project_id)
        return await asyncio.to_thread(self._info, repos)

    async def slide_html(
        self, project_id: str, index: int, known_revision: str | None
    ) -> SlideHtml:
        """Return the HTML page of slide ``index`` (counted from 0).

        The page is left out when ``known_revision`` is the revision of the slide, because the
        client already has that page.
        """
        repos = self._repositories.for_project(project_id)
        return await asyncio.to_thread(self._slide_html, repos, index, known_revision)

    async def update_element(
        self,
        project_id: str,
        index: int,
        element_id: str,
        changes: dict[str, object],
        base_revision: int | None,
    ) -> EditResult:
        """Apply ``changes`` to one element."""
        return await self._edit(
            project_id,
            index,
            base_revision,
            lambda slide: (self._patched(slide, index, element_id, changes), element_id),
        )

    async def add_element(
        self,
        project_id: str,
        index: int,
        kind: NewKind,
        props: dict[str, object],
        base_revision: int | None,
    ) -> EditResult:
        """Add an element of ``kind`` on top of the slide."""
        element_id = self._new_id()
        return await self._edit(
            project_id,
            index,
            base_revision,
            lambda slide: (slide.appended(self._built(kind, element_id, props)), element_id),
        )

    async def delete_element(
        self, project_id: str, index: int, element_id: str, base_revision: int | None
    ) -> EditResult:
        """Remove one element."""

        def change(slide: Slide) -> tuple[Slide, str | None]:
            self._require(slide, index, element_id)
            return slide.without(element_id), None

        return await self._edit(project_id, index, base_revision, change)

    async def duplicate_element(
        self, project_id: str, index: int, element_id: str, base_revision: int | None
    ) -> EditResult:
        """Copy a top-level element, shifted a little, above the original."""
        copy_id = self._new_id()

        def change(slide: Slide) -> tuple[Slide, str | None]:
            self._require(slide, index, element_id)
            try:
                return slide.duplicated(element_id, copy_id), copy_id
            except KeyError as error:
                reason = "only a top-level element that is not a group can be duplicated"
                raise InvalidElementChangeError(element_id, reason) from error

        return await self._edit(project_id, index, base_revision, change)

    async def reorder_element(
        self, project_id: str, index: int, element_id: str, move: ZMove, base_revision: int | None
    ) -> EditResult:
        """Move a top-level element in the stacking order."""

        def change(slide: Slide) -> tuple[Slide, str | None]:
            self._require(slide, index, element_id)
            try:
                return slide.reordered(element_id, move), element_id
            except KeyError as error:
                reason = "only a top-level element has a stacking order"
                raise InvalidElementChangeError(element_id, reason) from error

        return await self._edit(project_id, index, base_revision, change)

    async def undo(self, project_id: str) -> EditResult:
        """Return the deck to the revision before the last edit."""
        return await self._locked(project_id, self._undo)

    async def redo(self, project_id: str) -> EditResult:
        """Bring back the deck that the last undo removed."""
        return await self._locked(project_id, self._redo)

    async def _edit(
        self,
        project_id: str,
        index: int,
        base_revision: int | None,
        change: Callable[[Slide], tuple[Slide, str | None]],
    ) -> EditResult:
        return await self._locked(
            project_id, lambda repos: self._apply(repos, index, base_revision, change)
        )

    async def _locked(self, project_id: str, work: Callable[[Repos], EditResult]) -> EditResult:
        repos = self._repositories.for_project(project_id)
        if repos.turn_lock.locked():
            raise TurnInProgressError(project_id)
        async with repos.lock:
            return await asyncio.to_thread(work, repos)

    def _apply(
        self,
        repos: Repos,
        index: int,
        base_revision: int | None,
        change: Callable[[Slide], tuple[Slide, str | None]],
    ) -> EditResult:
        deck = self._load(repos)
        if base_revision is not None and base_revision != deck.revision:
            raise StaleDeckRevisionError(base_revision, deck.revision)
        if not 0 <= index < len(deck.slides):
            raise SlideIndexNotFoundError(repos.project_id, index)
        updated, element_id = change(deck.slides[index])
        slides = list(deck.slides)
        slides[index] = updated
        history = (repos.history.load() or DeckHistory()).recorded(deck)
        repos.history.save(history)
        editor = DeckEditor(repos, DeckChecker())
        revision = editor.commit(deck.model_copy(update={"slides": slides}), updated)
        return EditResult(
            revision=revision,
            element=self._element(index, updated, element_id),
            issues=editor.check_slide(updated),
            can_undo=history.can_undo,
            can_redo=history.can_redo,
        )

    def _undo(self, repos: Repos) -> EditResult:
        deck = self._load(repos)
        history = repos.history.load() or DeckHistory()
        if not history.can_undo:
            raise NothingToUndoError
        history, previous = history.undone(deck)
        return self._restore(repos, deck, previous, history)

    def _redo(self, repos: Repos) -> EditResult:
        deck = self._load(repos)
        history = repos.history.load() or DeckHistory()
        if not history.can_redo:
            raise NothingToRedoError
        history, following = history.redone(deck)
        return self._restore(repos, deck, following, history)

    def _restore(
        self, repos: Repos, current: Deck, target: Deck, history: DeckHistory
    ) -> EditResult:
        """Save ``target`` as the next revision, so that a client sees a change."""
        repos.history.save(history)
        editor = DeckEditor(repos, DeckChecker())
        revision = editor.commit(target.model_copy(update={"revision": current.revision}))
        return EditResult(
            revision=revision,
            element=None,
            issues=[],
            can_undo=history.can_undo,
            can_redo=history.can_redo,
        )

    def _info(self, repos: Repos) -> DeckInfo:
        deck = self._load(repos)
        plan = repos.plan.load()
        history = repos.history.load() or DeckHistory()
        digest = SlideDigest(deck)
        slides = []
        for index, slide in enumerate(deck.slides):
            draft = plan.slide(slide.id) if plan else None
            title = draft.title if draft else None
            slides.append(SlideInfo.of(index, slide, title, digest.of(slide)))
        return DeckInfo(
            revision=deck.revision,
            width=deck.width,
            height=deck.height,
            slides=slides,
            can_undo=history.can_undo,
            can_redo=history.can_redo,
        )

    def _slide_html(self, repos: Repos, index: int, known_revision: str | None) -> SlideHtml:
        deck = self._load(repos)
        if not 0 <= index < len(deck.slides):
            raise SlideIndexNotFoundError(repos.project_id, index)
        revision = SlideDigest(deck).of(deck.slides[index])
        if revision == known_revision:
            return SlideHtml(revision=revision, html=None)
        html = HtmlRenderer(deck, EMBEDDED_PAGE).slide_document(index)
        return SlideHtml(revision=revision, html=html)

    def _load(self, repos: Repos) -> Deck:
        deck = repos.deck.load()
        if deck is None:
            raise DeckMissingError
        return deck

    def _element(self, index: int, slide: Slide, element_id: str | None) -> ElementInfo | None:
        if element_id is None:
            return None
        return next((e for e in SlideInfo.elements_of(slide) if e.id == element_id), None)

    def _require(self, slide: Slide, index: int, element_id: str) -> Element:
        element = slide.element(element_id)
        if element is None:
            raise ElementIdNotFoundError(index, element_id)
        return element

    def _patched(
        self, slide: Slide, index: int, element_id: str, changes: dict[str, object]
    ) -> Slide:
        element = self._require(slide, index, element_id)
        editable = set(type(element).model_fields) - READ_ONLY_FIELDS
        unknown = sorted(set(changes) - editable)
        if not changes or unknown:
            reason = f"fields that cannot be edited: {unknown}" if unknown else "no change given"
            raise InvalidElementChangeError(element_id, reason)
        self._check_source(element_id, changes, element.src if isinstance(element, Image) else None)
        try:
            return slide.patched(element_id, self._relaid(element, changes))
        except ValidationError as error:
            raise InvalidElementChangeError(element_id, self._reason(error)) from error

    def _relaid(self, element: Element, changes: dict[str, object]) -> dict[str, object]:
        """Add the layout of a table to ``changes`` when the rows get another shape."""
        if not isinstance(element, Table) or "rows" not in changes:
            return changes
        try:
            rows = ROWS.validate_python(changes["rows"])
        except ValidationError:
            return changes  # the validation of the whole element reports it
        candidate = element.model_copy(update={**changes, "rows": rows})
        laid = self._tables.adapted(element, candidate)
        if laid is candidate:
            return changes
        return {**changes, **laid.model_dump(include=set(LAYOUT_FIELDS))}

    def _built(self, kind: NewKind, element_id: str, props: dict[str, object]) -> Element:
        model = NEW_TYPES[kind]
        unknown = sorted(set(props) - (set(model.model_fields) - READ_ONLY_FIELDS))
        if unknown:
            raise InvalidElementChangeError(element_id, f"fields that do not exist: {unknown}")
        self._check_source(element_id, props, None)
        try:
            return model.model_validate({**NEW_DEFAULTS[kind], **props, "id": element_id})
        except ValidationError as error:
            raise InvalidElementChangeError(element_id, self._reason(error)) from error

    @staticmethod
    def _check_source(element_id: str, changes: dict[str, object], current: str | None) -> None:
        """Refuse an image source that the renderer would read from the server disk."""
        source = changes.get("src")
        if source is None or source == current:
            return
        if not (isinstance(source, str) and source.startswith(SAFE_IMAGE_PREFIXES)):
            reason = "an image source must be an http(s) URL or a data:image URI"
            raise InvalidElementChangeError(element_id, reason)

    @staticmethod
    def _reason(error: ValidationError) -> str:
        return "; ".join(
            f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}"
            for item in error.errors()
        )
