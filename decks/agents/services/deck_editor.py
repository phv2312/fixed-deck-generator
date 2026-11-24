from decks.agents.exceptions import (
    DeckMissingError,
    ElementNotFoundError,
    SlideNotFoundError,
    StyleNotSupportedError,
)
from decks.agents.models import (
    ElementChange,
    ElementView,
    SlideLocation,
    SlideView,
    StylePatch,
    TextFitResult,
)
from decks.agents.repos import Repos
from decks.agents.services.checker import DeckChecker, TextMetrics
from decks.models.elements import Polygon, Shape, Text
from decks.models.slides import Deck, Slide

TEXT_FIELDS = frozenset(
    {"font_size", "bold", "italic", "underline", "color", "font_family", "align", "valign"}
)
FILL_FIELDS = frozenset({"fill", "stroke", "opacity"})


class DeckEditor:
    """Read and change elements of the built deck."""

    def __init__(
        self, repos: Repos, checker: DeckChecker, metrics: TextMetrics | None = None
    ) -> None:
        self._repos = repos
        self._checker = checker
        self._metrics = metrics or TextMetrics()

    def read_slide(self, slide_id: str) -> SlideView:
        """Return a short view of every element of a slide."""
        slide = self._locate(slide_id).slide
        return SlideView(
            id=slide.id, kind=slide.kind, elements=[ElementView.of(e) for e in slide.flat]
        )

    def update_element(self, slide_id: str, element_id: str, patch: StylePatch) -> ElementChange:
        """Apply the style fields that are set. Raise when the element cannot take one."""
        location = self._locate(slide_id)
        deck, slide, index = location.deck, location.slide, location.index
        element = slide.element(element_id)
        if element is None:
            raise ElementNotFoundError(slide_id, element_id)
        changes = patch.model_dump(exclude_none=True)
        for name in changes:
            allowed = (
                TEXT_FIELDS
                if isinstance(element, Text)
                else FILL_FIELDS
                if isinstance(element, Shape | Polygon)
                else frozenset()
            )
            if name not in allowed:
                raise StyleNotSupportedError(element_id, element.type, name)
        return self._save(deck, slide, index, element_id, changes)

    def set_text(
        self, slide_id: str, element_id: str, text: str, *, autofit: bool = True
    ) -> TextFitResult:
        """Replace the text of an element. With ``autofit`` shrink the font until it fits."""
        location = self._locate(slide_id)
        deck, slide, index = location.deck, location.slide, location.index
        element = slide.element(element_id)
        if not isinstance(element, Text):
            raise ElementNotFoundError(slide_id, element_id)
        size = element.font_size
        fitted = self._metrics.fit_font_size(
            text, size, (element.w, element.h), bold=element.bold
        ).size
        overflow = fitted < size
        changes: dict[str, object] = {"text": text}
        if autofit and overflow:
            changes["font_size"] = fitted
        change = self._save(deck, slide, index, element_id, changes)
        final = changes.get("font_size", size)
        return TextFitResult(
            element=change.element,
            overflow=overflow,
            font_size=float(final) if isinstance(final, int | float) else size,
            suggested_font_size=fitted if overflow else None,
            issues=change.issues,
        )

    def _locate(self, slide_id: str) -> SlideLocation:
        deck = self._repos.deck.load()
        if deck is None:
            raise DeckMissingError
        for index, slide in enumerate(deck.slides):
            if slide.id == slide_id:
                return SlideLocation(deck=deck, slide=slide, index=index)
        raise SlideNotFoundError(slide_id)

    def _save(
        self, deck: Deck, slide: Slide, index: int, element_id: str, changes: dict[str, object]
    ) -> ElementChange:
        updated = slide.updated(element_id, changes)
        slides = list(deck.slides)
        slides[index] = updated
        revision = deck.revision + 1
        self._repos.deck.save(deck.model_copy(update={"slides": slides, "revision": revision}))
        state = self._repos.project.load_state()
        built = state.built.get(slide.id)
        if built is not None:
            marked = built.model_copy(update={"edited": True})
            state = state.model_copy(update={"built": {**state.built, slide.id: marked}})
        self._repos.project.save_state(state.model_copy(update={"deck_revision": revision}))
        element = updated.element(element_id)
        if element is None:
            raise ElementNotFoundError(slide.id, element_id)
        plan = self._repos.plan.load()
        draft = plan.slide(slide.id) if plan else None
        return ElementChange(
            element=ElementView.of(element), issues=self._checker.check_slide(updated, draft)
        )
