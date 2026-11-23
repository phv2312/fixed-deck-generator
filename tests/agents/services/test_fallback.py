from decks.agents.catalog import SlideCatalog
from decks.agents.services.fallback import SlideFallback
from decks.agents.services.fitter import LayoutFitter
from decks.models.elements import BULLET, Group, Image, Text
from decks.models.plan import ContentBlock, ContentItem, ContentSeries, SlideDraft
from decks.models.slides import Slide


def _draft(**content: object) -> SlideDraft:
    return SlideDraft(
        id="p1", kind="rows", purpose="why", title="T", content=ContentBlock(**content)
    )


def test_lines_cover_every_text_field() -> None:
    """Points, items, rows, stages and series all become lines; none is dropped."""
    draft = _draft(
        points=["a"],
        items=[ContentItem(label="KPI", value="5")],
        rows=[["x", "y"]],
        stages=["one", "two"],
        series=[ContentSeries(name="s", values=[1, 2.5])],
    )

    assert SlideFallback(SlideCatalog()).lines(draft) == [
        "a",
        "KPI: 5",
        "x · y",
        "1. one",
        "2. two",
        "s: 1, 2.5",
    ]


def test_content_fallback_without_an_image() -> None:
    """A draft with no image becomes a content slide with summary first, then the lines."""
    slide, warnings = SlideFallback(SlideCatalog()).build(
        _draft(summary="sum", rows=[["k", "v"]]), cause="rows: boom"
    )

    assert slide is not None and slide.kind == "content"
    texts = " ".join(e.text for e in slide.elements if isinstance(e, Text))
    assert "sum" in texts and "k · v" in texts
    assert warnings == ["slide p1: fell back to a plain content slide (rows: boom)"]


def test_picture_fallback_keeps_the_image_and_reports_dropped_lines() -> None:
    """A draft with an image becomes an image-only figure; the lines it cannot show are reported."""
    slide, warnings = SlideFallback(SlideCatalog()).build(
        _draft(summary="cap", points=["p"], image="http://x/y.png", source="src")
    )

    assert slide is not None and slide.kind == "figure"
    assert [e.src for e in slide.elements if isinstance(e, Image)] == ["http://x/y.png"]
    assert any(isinstance(e, Text) and "Source: src" in e.text for e in slide.elements)
    assert (
        warnings[1] == "slide p1: 1 text lines are not on the slide; the picture should carry them"
    )


def test_fitter_shrinks_text_in_a_group_and_leaves_fitting_text() -> None:
    """Overflowing text, also inside a group, gets a smaller size; fitting text is untouched."""
    long = Text(x=0, y=0, w=100, h=30, text="word " * 30, font_size=36)
    short = Text(x=0, y=0, w=300, h=60, text="hi", font_size=36)
    bullet = Text(x=0, y=0, w=300, h=60, text=f"{BULLET}hi", font_size=36)
    slide = Slide(
        id="s", family="f", kind="k", elements=[short, bullet, Group(name="g", children=[long])]
    )

    fitted = LayoutFitter().fit(slide)

    group = fitted.elements[2]
    assert isinstance(group, Group) and isinstance(group.children[0], Text)
    assert group.children[0].font_size < 36
    assert [e.font_size for e in fitted.elements[:2] if isinstance(e, Text)] == [36, 36]
    assert long.font_size == 36
