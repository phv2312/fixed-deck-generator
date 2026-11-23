from decks.builders.pictures.figure import FigureBuilder
from decks.models.elements import Image, Text
from decks.models.pictures import FigureSlide


def test_figure_picture_spans_the_content_width() -> None:
    """The picture fills the width between the margins and stays whole (contain)."""
    spec = FigureSlide(title="T", image="http://x/y.png", caption="c")

    images = [e for e in FigureBuilder().build(spec) if isinstance(e, Image)]

    assert len(images) == 1
    assert (images[0].x, images[0].w, images[0].fit) == (64, 1152, "contain")


def test_figure_has_a_caption_below_the_picture_and_no_side_text() -> None:
    """Title, caption and optional source are the only texts; none sits beside the picture."""
    spec = FigureSlide(title="T", image="http://x/y.png", caption="cap", source="src")

    elements = FigureBuilder().build(spec)
    picture = next(e for e in elements if isinstance(e, Image))
    texts = [e for e in elements if isinstance(e, Text)]

    assert [t.text for t in texts] == ["T", "cap", "Source: src"]
    assert all(t.x == 64 for t in texts)
    assert all(t.y >= picture.y + picture.h for t in texts[1:])
