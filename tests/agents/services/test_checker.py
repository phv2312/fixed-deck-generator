import pytest

from decks.agents.services.checker import DeckChecker
from decks.models.elements import BULLET, Chart, Element, Group, Line, Shape, Text
from decks.models.plan import ContentBlock, SlideDraft
from decks.models.slides import Slide


def _slide(*elements: Element) -> Slide:
    return Slide(id="p1", family="layout", kind="content", elements=list(elements))


def _codes(slide: Slide, draft: SlideDraft | None = None) -> list[str]:
    return [i.code for i in DeckChecker().check_slide(slide, draft)]


def test_empty_slide_is_an_error() -> None:
    """A slide without elements gives one error and no other check runs."""
    issues = DeckChecker().check_slide(_slide(), None)

    assert [(i.code, i.severity) for i in issues] == [("empty_slide", "error")]


@pytest.mark.parametrize(
    "element",
    (
        Text(x=1200, y=0, w=200, h=40, text="x"),
        Shape(x=1200, y=0, w=400, h=40),
        Chart(x=0, y=700, w=100, h=40),
        Line(x1=0, y1=0, x2=1300, y2=0),
    ),
)
def test_element_leaving_the_slide_is_an_error(element: Element) -> None:
    """Every positioned element is checked, not only text, images and tables."""
    issues = DeckChecker().check_slide(_slide(element), None)

    assert [(i.code, i.severity) for i in issues if i.code == "out_of_bounds"] == [
        ("out_of_bounds", "error")
    ]


def test_group_children_are_checked() -> None:
    """A child of a group that leaves the slide is found."""
    group = Group(name="g", children=[Shape(x=1270, y=0, w=50, h=10)])

    assert "out_of_bounds" in _codes(_slide(group))


@pytest.mark.parametrize(
    ("text", "overflows"),
    (("short", False), ("word " * 12, True), ("word " * 200, True)),
)
def test_text_overflow_is_one_rule(text: str, overflows: bool) -> None:
    """Text taller than its box is an error. There is no softer tier."""
    slide = _slide(Text(id="t", x=0, y=0, w=300, h=36, text=text, font_size=16))

    issues = [i for i in DeckChecker().check_slide(slide, None) if i.code == "text_overflow"]

    assert [i.severity for i in issues] == (["error"] if overflows else [])


def test_bulleted_text_loses_one_em_of_width() -> None:
    """The hanging indent narrows each bullet line, so a line that just fits plain can overflow."""
    box = {"x": 0, "y": 0, "w": 20 * 16 * 0.55, "h": 16 * 1.3, "font_size": 16}

    assert "text_overflow" not in _codes(_slide(Text(text="x" * 20, **box)))
    assert "text_overflow" in _codes(_slide(Text(text=BULLET + "x" * 20, **box)))


def _draft(**content: object) -> SlideDraft:
    return SlideDraft(id="p1", purpose="p", title="T", content=ContentBlock(**content))


@pytest.mark.parametrize(
    ("plan_text", "slide_text", "mismatch"),
    (
        ("Revenue grew 42%", "Revenue grew 42%", False),
        ("10 %", "10%", False),
        ("1,000 users", "1000 users", False),
        ("12.0 points", "12 points", False),
        ("Revenue grew 42%", "Revenue grew 51%", True),
        ("only 5", "5", False),  # a single digit is never reported
    ),
)
def test_numbers_must_come_from_the_plan(plan_text: str, slide_text: str, mismatch: bool) -> None:
    """A figure on the slide that the plan does not hold is a warning; formats are normalised."""
    slide = _slide(Text(id="t", x=0, y=0, w=600, h=60, text=slide_text))

    issues = DeckChecker().check_slide(slide, _draft(summary=plan_text))

    assert [i.severity for i in issues if i.code == "number_mismatch"] == (
        ["warning"] if mismatch else []
    )


def test_numbers_are_not_checked_without_a_draft() -> None:
    """No plan slide, no number check."""
    slide = _slide(Text(id="t", x=0, y=0, w=600, h=60, text="Revenue grew 99%"))

    assert "number_mismatch" not in _codes(slide)
