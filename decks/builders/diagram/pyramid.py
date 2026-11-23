"""Pyramid slides: ranked levels with notes."""

from decks.builders.base import BaseBuilder
from decks.builders.common import MARGIN, TYPE, W, mid_text, title_el
from decks.models.diagram import PyramidSlide
from decks.models.elements import Element, Line, Polygon, Shape, Text

XC, TOP, H, BASE = 330, 150, 440, 520
TX = 660
COLORS = ["primary", "muted", "light", "tint", "tint", "tint"]


class PyramidBuilder(BaseBuilder[PyramidSlide]):
    """Render a pyramid of levels with side notes."""

    TYPE = "pyramid"
    DESCRIPTION = (
        "Use this slide for ranked or hierarchical levels, widest at the base. Each level has an "
        "explanatory note. Use style rings for layers from a core outward, such as priority rings."
    )
    SPEC = PyramidSlide

    def build(self, spec: PyramidSlide) -> list[Element]:
        if spec.style == "rings":
            return self._rings(spec)
        return self._stack(spec)

    def _stack(self, spec: PyramidSlide) -> list[Element]:
        n = len(spec.levels)
        gap = 4
        lh = (H - gap * (n - 1)) / n

        def width(y: float) -> float:
            return BASE * (y - TOP) / H

        els: list[Element] = [title_el(spec.title)]
        for i, level in enumerate(spec.levels):
            y0 = TOP + (lh + gap) * i
            y1 = y0 + lh
            w0, w1 = width(y0), width(y1)
            col = COLORS[i]
            pts = [(XC - w0 / 2, y0), (XC + w0 / 2, y0), (XC + w1 / 2, y1), (XC - w1 / 2, y1)]
            if i == 0:
                pts = [(XC, y0), (XC + w1 / 2, y1), (XC - w1 / 2, y1)]
            els.append(Polygon(points=pts, fill=col))
            fg = "bg" if col in ("primary", "muted") else "primary"
            ty = y0 + (lh * 0.45 if i == 0 else 0)
            tw = max(80, (w0 + w1) / 2 - 40) if i else w1 * 0.5
            els.append(
                mid_text(
                    x=XC - tw / 2,
                    y=ty,
                    w=tw,
                    h=lh * (0.55 if i == 0 else 1),
                    text=level.label,
                    font_size=TYPE["body"],
                    bold=True,
                    color=fg,
                    align="center",
                )
            )
            cy = y0 + lh / 2
            els.append(
                Line(
                    x1=XC + (w0 + w1) / 4 + 12,
                    y1=cy,
                    x2=TX - 12,
                    y2=cy,
                    color="grid",
                    width=1,
                    dash=True,
                )
            )
            if level.text:
                els.append(
                    mid_text(
                        x=TX,
                        y=cy - 30,
                        w=1216 - TX,
                        h=60,
                        text=level.text,
                        font_size=TYPE["body_l"],
                    )
                )
        return els

    def _rings(self, spec: PyramidSlide) -> list[Element]:
        """Render concentric rings with a legend, core first."""
        n = len(spec.levels)
        cx, cy, R = 360, 385, 235
        els: list[Element] = [title_el(spec.title)]
        fills = ["tint", "light", "accent", "primary", "ink"]
        palette = fills[-n:] if n < 5 else fills
        for i in range(n - 1, -1, -1):
            r = R * (i + 1) / n
            fill = "ink" if spec.highlight == i else palette[n - 1 - i]
            els.append(
                Shape(
                    x=cx - r,
                    y=cy - r,
                    w=2 * r,
                    h=2 * r,
                    shape="ellipse",
                    fill=fill,
                    stroke="bg",
                    stroke_width=3,
                )
            )
        for i in range(n):
            inner, outer = R * i / n, R * (i + 1) / n
            ymid = cy - (inner + outer) / 2
            fill = "ink" if spec.highlight == i else palette[n - 1 - i]
            els.append(
                mid_text(
                    x=cx - 30,
                    y=ymid - 12,
                    w=60,
                    h=24,
                    text=str(i + 1),
                    font_size=TYPE["body"],
                    bold=True,
                    color="primary" if fill in ("light", "tint") else "bg",
                    align="center",
                )
            )
        for k, i in enumerate(range(n - 1, -1, -1)):
            ry = 160 + k * (460 / n)
            ring = spec.levels[i]
            els.append(
                Shape(
                    x=650,
                    y=ry,
                    w=6,
                    h=460 / n - 14,
                    fill="ink" if spec.highlight == i else palette[n - 1 - i],
                )
            )
            els.append(
                mid_text(
                    x=672,
                    y=ry,
                    w=W - MARGIN - 672,
                    h=30,
                    text=f"{i + 1}  {ring.label}",
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                )
            )
            if ring.text:
                els.append(
                    Text(
                        x=672,
                        y=ry + 32,
                        w=W - MARGIN - 672,
                        h=460 / n - 50,
                        text=ring.text,
                        font_size=TYPE["body"],
                    )
                )
        return els
