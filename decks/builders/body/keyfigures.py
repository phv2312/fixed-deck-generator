"""Key figure slides: tiles with a number, its label and a caption."""

import math

from decks.builders.base import BaseBuilder
from decks.builders.common import mid_text, title_el
from decks.design import BODY_TOP, CONTENT_W, GUTTER, MARGIN, RADIUS, TYPE, snap_down
from decks.models.body import KeyFiguresSlide
from decks.models.elements import Element, Line, Shape, Text


class KeyFiguresBuilder(BaseBuilder[KeyFiguresSlide]):
    """Render a grid of key-figure tiles."""

    TYPE = "keyfigures"
    DESCRIPTION = (
        "Use this slide for hero numbers: a grid of tiles with a figure and a label. Each tile can "
        "have a caption, and you can highlight one tile."
    )
    SPEC = KeyFiguresSlide

    def build(self, spec: KeyFiguresSlide) -> list[Element]:
        n = len(spec.tiles)
        per = n if n <= 3 else math.ceil(n / 2)
        rows = math.ceil(n / per)
        th = (470 - GUTTER * (rows - 1)) / rows
        tw = (CONTENT_W - GUTTER * (per - 1)) / per
        els: list[Element] = [title_el(spec.title)]
        fs = snap_down(
            max(
                34,
                min(
                    84 if rows == 1 else 64,
                    (tw - 48) / (0.58 * max(len(tile.figure) for tile in spec.tiles)),
                ),
            )
        )
        for i, tile in enumerate(spec.tiles):
            r, c = divmod(i, per)
            x, y = MARGIN + (tw + GUTTER) * c, BODY_TOP + (th + GUTTER) * r
            hi = spec.highlight == i
            fg = "bg" if hi else "primary"
            if hi:
                els.append(Shape(x=x, y=y, w=tw, h=th, fill="primary", radius=RADIUS["md"]))
            else:
                els.append(Line(x1=x, y1=y, x2=x + tw, y2=y, color="grid", width=1.5))
            els.append(
                mid_text(
                    x=x + 24,
                    y=y + th * 0.12,
                    w=tw - 48,
                    h=fs * 1.4,
                    text=tile.figure,
                    font_size=fs,
                    bold=True,
                    color=fg,
                )
            )
            ly = y + th * 0.12 + fs * 1.4 + 6
            els.append(
                mid_text(
                    x=x + 24,
                    y=ly,
                    w=tw - 48,
                    h=34,
                    text=tile.label,
                    font_size=TYPE["lead"],
                    bold=True,
                    color=fg,
                )
            )
            if tile.caption:
                els.append(
                    Text(
                        x=x + 24,
                        y=ly + 38,
                        w=tw - 48,
                        h=max(30, y + th - ly - 52),
                        text=tile.caption,
                        font_size=TYPE["body"],
                        color="bg" if hi else "text",
                    )
                )
        return els
