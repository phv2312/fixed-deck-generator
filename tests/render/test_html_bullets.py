from decks.models.elements import BULLET, Text
from decks.models.slides import Deck, Slide
from decks.models.theme import FONT, THEMES
from decks.render.html import render_html, text_html


def test_text_without_bullets_is_only_escaped() -> None:
    """Plain text keeps its old output, so wrapped prose is not indented."""
    assert text_html("a < b\nc") == "a &lt; b\nc"


def test_bullet_lines_hang_their_wrapped_lines() -> None:
    """A bullet line gets a fixed-width marker and a negative first-line indent."""
    html = text_html(f"{BULLET}one & two\n{BULLET}three")

    assert html.count("padding-left:1em;text-indent:-1em") == 2
    assert html.count("&bull;") == 2
    assert "one &amp; two" in html
    assert BULLET not in html


def test_non_bullet_line_beside_bullets_is_not_hung() -> None:
    """A plain line in a mixed text keeps the normal left edge."""
    html = text_html(f"intro\n{BULLET}point")

    assert html.count("padding-left:1em") == 1
    assert "<div>intro</div>" in html


def test_render_html_uses_the_bullet_markup() -> None:
    """The full document carries the hanging markup for a bulleted Text element."""
    slide = Slide(
        id="s1",
        family="body",
        kind="content",
        elements=[Text(x=0, y=0, w=300, h=100, text=f"{BULLET}hello")],
    )
    deck = Deck(revision=1, theme="green", palette=THEMES["green"], font=FONT, slides=[slide])

    assert "text-indent:-1em" in render_html(deck)
