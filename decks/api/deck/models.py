import hashlib
import json
from typing import Literal, Self

from pydantic import BaseModel, Field

from decks.agents.models import LayoutIssue
from decks.models.elements import Chart, Element, Group, Image, Line, Polygon, Shape, Table, Text
from decks.models.slides import Deck, Slide

type NewKind = Literal["text", "image", "table", "shape", "chart"]

READ_ONLY_FIELDS = frozenset({"id", "type", "children"})

NEW_DEFAULTS: dict[str, dict[str, object]] = {
    "text": {"x": 64, "y": 200, "w": 400, "h": 60, "text": "New text", "font_size": 16},
    "shape": {"x": 64, "y": 200, "w": 200, "h": 120, "fill": "tint", "radius": 8},
    "image": {"x": 64, "y": 200, "w": 320, "h": 200},
    "table": {
        "x": 64,
        "y": 200,
        "w": 480,
        "h": 120,
        "rows": [["Header", "Header"], ["", ""]],
    },
    "chart": {"x": 64, "y": 200, "w": 480, "h": 280, "kind": "bar"},
}
NEW_TYPES: dict[str, type[Element]] = {
    "text": Text,
    "shape": Shape,
    "image": Image,
    "table": Table,
    "chart": Chart,
}


class ElementInfo(BaseModel):
    """One element with the box that an overlay needs and the fields that an edit may change."""

    id: str
    type: str
    parent_id: str | None
    z: int = Field(description="Position in the render order of the slide. Higher is on top.")
    box: tuple[float, float, float, float] = Field(description="Left, top, width, height.")
    props: dict[str, object]
    editable: list[str]

    @classmethod
    def of(cls, element: Element, z: int, parent_id: str | None = None) -> Self:
        """Describe ``element``."""
        return cls(
            id=element.id,
            type=element.type,
            parent_id=parent_id,
            z=z,
            box=cls._box(element),
            props=element.model_dump(mode="json", exclude=set(READ_ONLY_FIELDS)),
            editable=sorted(set(type(element).model_fields) - READ_ONLY_FIELDS),
        )

    @classmethod
    def _box(cls, element: Element) -> tuple[float, float, float, float]:
        match element:
            case Line():
                xs, ys = [element.x1, element.x2], [element.y1, element.y2]
            case Polygon():
                xs, ys = [x for x, _ in element.points], [y for _, y in element.points]
            case Group():
                boxes = [cls._box(child) for child in element.children]
                xs = [b[0] for b in boxes] + [b[0] + b[2] for b in boxes]
                ys = [b[1] for b in boxes] + [b[1] + b[3] for b in boxes]
            case _:
                return (element.x, element.y, element.w, element.h)
        if not xs:
            return (0, 0, 0, 0)
        return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


class SlideInfo(BaseModel):
    """One slide of the deck with its elements in render order."""

    index: int
    id: str
    kind: str
    title: str | None
    revision: str
    elements: list[ElementInfo]

    @classmethod
    def of(cls, index: int, slide: Slide, title: str | None, revision: str) -> Self:
        """Describe ``slide``. Group children come after their group."""
        return cls(
            index=index,
            id=slide.id,
            kind=slide.kind,
            title=title,
            revision=revision,
            elements=cls.elements_of(slide),
        )

    @classmethod
    def elements_of(cls, slide: Slide) -> list[ElementInfo]:
        """Return the elements of ``slide`` in render order, group children after their group."""
        elements: list[ElementInfo] = []
        cls._collect(slide.elements, None, elements)
        return elements

    @classmethod
    def _collect(cls, source: list[Element], parent_id: str | None, out: list[ElementInfo]) -> None:
        for element in source:
            out.append(ElementInfo.of(element, len(out), parent_id))
            if isinstance(element, Group):
                cls._collect(element.children, element.id, out)


class DeckInfo(BaseModel):
    """The built deck as the editor needs it."""

    revision: int
    width: int
    height: int
    slides: list[SlideInfo]
    can_undo: bool
    can_redo: bool


class EditResult(BaseModel):
    """What an edit changed: the new revision, the element, and the layout issues."""

    revision: int
    element: ElementInfo | None
    issues: list[LayoutIssue]
    can_undo: bool
    can_redo: bool


class SlideDigest:
    """Short hash of what a slide page shows: the slide and the look of its deck.

    The hash ignores the deck revision, so an edit changes only the hash of the slide that it
    touches. Undo and redo bring back the old hash with the old slide.
    """

    LENGTH = 12

    def __init__(self, deck: Deck) -> None:
        self._look = json.dumps(
            [deck.width, deck.height, deck.theme, deck.palette, deck.font], sort_keys=True
        )

    def of(self, slide: Slide) -> str:
        """Return the hash of ``slide``."""
        data = self._look + slide.model_dump_json()
        return hashlib.sha256(data.encode()).hexdigest()[: self.LENGTH]


class SlideHtml(BaseModel):
    """The HTML page of one slide, or only its revision when the client already has the page."""

    revision: str
    html: str | None
