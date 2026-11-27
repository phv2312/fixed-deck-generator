from pathlib import Path

import pytest

from decks.models.elements import (
    BULLET,
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
from decks.render.htmldoc.models import HtmlPageStyle
from decks.render.htmldoc.services import HtmlRenderer, img_src

BOX = {"x": 1, "y": 2, "w": 30, "h": 40}


def make_deck(*elements: Element) -> Deck:
    """Build a one-slide deck that holds ``elements``."""
    slide = Slide(id="s1", family="body", kind="content", elements=list(elements))
    return Deck(revision=1, theme="green", palette=THEMES["green"], font=FONT, slides=[slide])


def body(text: str) -> str:
    """Return the escaped text body that ``HtmlRenderer`` makes for ``text``."""
    return HtmlRenderer(make_deck()).text_body(text)


def test_text_without_bullets_is_only_escaped() -> None:
    """Plain text keeps its old output, so wrapped prose is not indented."""
    assert body("a < b\nc") == "a &lt; b\nc"


def test_bullet_lines_hang_their_wrapped_lines() -> None:
    """A bullet line gets a fixed-width marker and a negative first-line indent."""
    html = body(f"{BULLET}one & two\n{BULLET}three")

    assert html.count("padding-left:1em;text-indent:-1em") == 2
    assert html.count("&bull;") == 2
    assert "one &amp; two" in html
    assert BULLET not in html


def test_non_bullet_line_beside_bullets_is_not_hung() -> None:
    """A plain line in a mixed text keeps the normal left edge."""
    html = body(f"intro\n{BULLET}point")

    assert html.count("padding-left:1em") == 1
    assert "<div>intro</div>" in html


def test_document_uses_the_bullet_markup() -> None:
    """The full document carries the hanging markup for a bulleted Text element."""
    deck = make_deck(Text(text=f"{BULLET}hello", **BOX))

    assert "text-indent:-1em" in HtmlRenderer(deck).document()


@pytest.mark.parametrize(
    ("element", "expected"),
    [
        (Text(text="a<b", bold=True, align="center", valign="middle", **BOX), "font-weight:700"),
        (Text(text="a<b", **BOX), "a&lt;b"),
        (Text(text="a", mono=True, font_family="X", **BOX), "font-family:X;"),
        (Shape(shape="ellipse", fill="#fff", **BOX), "border-radius:50%;"),
        (Shape(radius=4, stroke="#000", dash=True, **BOX), "border:1px dashed #000;"),
        (Line(x1=0, y1=0, x2=5, y2=5, arrow=True), 'marker-end="url(#ah'),
        (Line(x1=0, y1=0, x2=5, y2=5, dash=True), 'stroke-dasharray="6 5"'),
        (Polygon(points=[(0, 0), (4, 4), (0, 4)], dash=True), 'points="0,0 4,4 0,4"'),
        (Image(src="https://x/y.png", **BOX), 'src="https://x/y.png"'),
        (Table(rows=[["h"], ["c"]], **BOX), "<tr><th>h</th></tr><tr><td>c</td></tr>"),
        (Chart(kind="pie", **BOX), "chart: pie"),
        (
            Group(name="g<1", children=[Shape(**BOX)]),
            '<div class="g" data-element-id="" data-name="g&lt;1">',
        ),
    ],
)
def test_each_element_type_has_its_markup(element: Element, expected: str) -> None:
    """Every element type renders its own markup inside the slide."""
    slides = HtmlRenderer(make_deck(element)).slides()

    assert expected in slides[0]


def test_slides_return_one_section_per_slide() -> None:
    """``slides`` returns one ``<section>`` string per slide."""
    slides = HtmlRenderer(make_deck(Shape(**BOX))).slides()

    assert len(slides) == 1
    assert slides[0].startswith('<section class="slide" data-family="body"')


def test_missing_color_renders_as_none() -> None:
    """A shape with no fill gets the CSS value ``none``."""
    assert "background:none;" in HtmlRenderer(make_deck(Shape(**BOX))).document()


def test_page_style_sets_title_and_backdrop() -> None:
    """The viewer page takes its title and backdrop from ``HtmlPageStyle``."""
    style = HtmlPageStyle(title="A & B", backdrop="#123456")

    page = HtmlRenderer(make_deck(), style).document()

    assert "<title>A &amp; B</title>" in page
    assert "background: #123456" in page


@pytest.mark.parametrize(
    "src",
    ["http://x/a.png", "https://x/a.png", "data:image/png;base64,AAAA", "missing/file.png"],
)
def test_img_src_keeps_remote_data_and_missing_sources(src: str) -> None:
    """Only an existing local file is inlined."""
    assert img_src(src) == src


def test_img_src_inlines_a_local_file(tmp_path: Path) -> None:
    """A local file becomes a data URI with its MIME type."""
    path = tmp_path / "a.png"
    path.write_bytes(b"png")

    assert img_src(str(path)) == "data:image/png;base64,cG5n"


def test_slide_document_holds_only_the_chosen_slide() -> None:
    """The page of one slide has its text and no other slide."""
    deck = make_deck(Text(**BOX, text="first"))
    second = deck.slides[0].model_copy(update={"elements": [Text(**BOX, text="second")]})
    deck.slides.append(second)
    page = HtmlRenderer(deck).slide_document(1)
    assert "second" in page
    assert "first" not in page


def test_every_element_carries_its_id_for_the_editor_overlay() -> None:
    """Each rendered element has ``data-element-id`` with the id of the model element."""
    elements: list[Element] = [
        Text(id="a", text="x", **BOX),
        Shape(id="b", **BOX),
        Image(id="c", src="https://x/y.png", **BOX),
        Table(id="d", rows=[["h"]], **BOX),
        Chart(id="e", **BOX),
        Line(id="f", x1=0, y1=0, x2=5, y2=5),
        Polygon(id="g", points=[(0, 0), (4, 4), (0, 4)]),
        Group(id="h", children=[Shape(id="i", **BOX)]),
    ]
    html = HtmlRenderer(make_deck(*elements)).slides()[0]

    for element_id in "abcdefghi":
        assert f'data-element-id="{element_id}"' in html
