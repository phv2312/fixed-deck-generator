import itertools

from decks.builders.common import MARGIN, TYPE, H, W, deco_blocks, title_el
from decks.models.elements import Shape


def test_deco_blocks_default_stack() -> None:
    """The default stack has three accent squares with falling size and opacity."""
    blocks = deco_blocks()

    assert all(isinstance(b, Shape) and b.w == b.h and b.fill == "accent" for b in blocks)
    assert [b.w for b in blocks] == [96, 56, 28]
    assert [b.opacity for b in blocks] == sorted((b.opacity for b in blocks), reverse=True)


def test_deco_blocks_anchored_bottom_right() -> None:
    """The largest square touches the inset corner and all squares share a bottom edge."""
    blocks = deco_blocks()

    assert blocks[0].x + blocks[0].w == W - MARGIN
    assert {b.y + b.h for b in blocks} == {H - MARGIN}


def test_deco_blocks_do_not_overlap() -> None:
    """Neighbouring squares are separated by the gap."""
    blocks = deco_blocks(gap=16)

    for right, left in itertools.pairwise(blocks):
        assert right.x - (left.x + left.w) == 16


def test_title_el_keeps_a_one_line_title_at_h2() -> None:
    """A title of up to 55 characters fits one line of the full-width box, so it keeps h2."""
    title = "Scaled dot-product attention turns scores into averages"

    assert title_el(title).font_size == TYPE["h2"]


def test_title_el_steps_a_64_character_title_down_to_h3() -> None:
    """The bold width is conservative: a 64-character title wraps at h2 and drops to h3."""
    title = "Scaled dot-product attention turns scores into weighted averages"

    assert title_el(title).font_size == TYPE["h3"]


def test_title_el_shrinks_a_title_that_would_wrap() -> None:
    """A title too long for one line steps down the type scale so it stays inside the box."""
    title = "A very long headline " * 6

    assert title_el(title).font_size < TYPE["h2"]
