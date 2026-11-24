from typing import cast

import pytest

from decks.models.elements import (
    Chart,
    Element,
    Group,
    Image,
    Line,
    Polygon,
    Shape,
    Table,
    Text,
)
from decks.models.slides import Deck, Slide
from decks.models.theme import FONT, THEMES
from decks.render.base import DeckRenderer
from decks.render.exceptions import UnsupportedElementError


class RecordingRenderer(DeckRenderer[str]):
    """Renderer that returns the name of the method that handled each element."""

    def text(self, e: Text) -> str:
        """Return the method name."""
        return "text"

    def shape(self, e: Shape) -> str:
        """Return the method name."""
        return "shape"

    def line(self, e: Line) -> str:
        """Return the method name."""
        return "line"

    def polygon(self, e: Polygon) -> str:
        """Return the method name."""
        return "polygon"

    def image(self, e: Image) -> str:
        """Return the method name."""
        return "image"

    def table(self, e: Table) -> str:
        """Return the method name."""
        return "table"

    def group(self, e: Group, children: list[str]) -> str:
        """Return the method name with the rendered children."""
        return f"group({','.join(children)})"

    def chart(self, e: Chart) -> str:
        """Return the method name."""
        return "chart"

    def slide(self, slide: Slide, parts: list[str], number: int) -> str:
        """Return the slide number and its parts."""
        return f"{number}:{'+'.join(parts)}"


def make_deck(*slides: Slide) -> Deck:
    """Build a small deck from ``slides``."""
    return Deck(revision=1, theme="green", palette=THEMES["green"], font=FONT, slides=list(slides))


BOX = {"x": 0, "y": 0, "w": 10, "h": 10}


@pytest.mark.parametrize(
    ("element", "expected"),
    [
        (Text(text="a", **BOX), "text"),
        (Shape(**BOX), "shape"),
        (Line(x1=0, y1=0, x2=1, y2=1), "line"),
        (Polygon(points=[(0, 0), (1, 1), (0, 1)]), "polygon"),
        (Image(src="a.png", **BOX), "image"),
        (Table(rows=[["a"]], **BOX), "table"),
        (Chart(**BOX), "chart"),
        (Group(children=[Shape(**BOX), Text(text="a", **BOX)]), "group(shape,text)"),
    ],
)
def test_element_goes_to_the_method_of_its_type(element: Element, expected: str) -> None:
    """Each element type reaches its own method, and a group gets its rendered children."""
    assert RecordingRenderer(make_deck()).element(element) == expected


def test_unknown_element_raises_unsupported_element_error() -> None:
    """A value that is not an element is rejected with its type name."""
    renderer = RecordingRenderer(make_deck())

    with pytest.raises(UnsupportedElementError, match="unsupported element type: object"):
        renderer.element(cast(Element, object()))


def test_slides_number_from_one_and_keep_the_order() -> None:
    """``slides`` renders every slide with a 1-based number."""
    first = Slide(id="a", family="body", kind="content", elements=[Shape(**BOX)])
    second = Slide(id="b", family="body", kind="content", elements=[Text(text="a", **BOX)])

    assert RecordingRenderer(make_deck(first, second)).slides() == ["1:shape", "2:text"]
