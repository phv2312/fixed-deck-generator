"""Panel slides: parallel panels of bullet points."""

import math

from decks.builders.base import BaseBuilder
from decks.builders.common import banner, bullets, icon_badge, mid_text, title_el
from decks.design import (
    BANNER_Y,
    BODY_TOP,
    CONTENT_W,
    GUTTER,
    MARGIN,
    RADIUS,
    RULE,
    TYPE,
    snap_down,
)
from decks.models.body import PanelsSlide
from decks.models.elements import Element, Line, Shape, Text

TOP, BOTTOM = BODY_TOP, BANNER_Y


class PanelsBuilder(BaseBuilder[PanelsSlide]):
    """Render parallel panels, optionally highlighting one."""

    TYPE = "panels"
    DESCRIPTION = (
        "Use this slide for 2 to 4 parallel themes or workstreams. Each panel has a heading, a "
        "bullet list, and an optional icon. Use style icons for 2 to 8 parallel concepts, each "
        "with an icon, a heading and a short text."
    )
    SPEC = PanelsSlide

    def build(self, spec: PanelsSlide) -> list[Element]:
        if spec.style == "icons":
            return self._icons(spec)
        return self._columns(spec)

    def _columns(self, spec: PanelsSlide) -> list[Element]:
        m = len(spec.panels)
        w = (CONTENT_W - GUTTER * (m - 1)) / m
        els: list[Element] = [title_el(spec.title)]
        for i, panel in enumerate(spec.panels):
            x = MARGIN + (w + GUTTER) * i
            hi = spec.highlight == i
            fill = "primary" if hi else "tint"
            fg = "bg" if hi else "text"
            if hi:
                els.append(Shape(x=x, y=TOP, w=w, h=BOTTOM - TOP, fill=fill, radius=RADIUS["md"]))
            head_w = w - 40
            if panel.icon:
                els += icon_badge(x + w - 54, TOP + 14, 34, panel.icon, "bg" if hi else "accent")
                head_w -= 44
            els.append(
                mid_text(
                    x=x + 20,
                    y=TOP + 14,
                    w=head_w,
                    h=36,
                    text=panel.head,
                    font_size=TYPE["lead"],
                    bold=True,
                    color="bg" if hi else "primary",
                )
            )
            els.append(
                Line(
                    x1=x + 20,
                    y1=TOP + 60,
                    x2=x + w - 20,
                    y2=TOP + 60,
                    color="light" if hi else "accent",
                    width=1.5,
                )
            )
            els.append(
                Text(
                    x=x + 20,
                    y=TOP + 74,
                    w=w - 40,
                    h=BOTTOM - TOP - 90,
                    text=bullets(panel.items),
                    font_size=TYPE["body_l"],
                    color=fg,
                )
            )
        return els

    def _icons(self, spec: PanelsSlide) -> list[Element]:
        """Render a grid of icon, heading and text items."""
        n = len(spec.panels)
        rows = 1 if n <= 4 else 2
        per = math.ceil(n / rows)
        bottom = 560 if spec.banner else 620
        ch = (bottom - BODY_TOP - GUTTER * (rows - 1)) / rows
        cw = (CONTENT_W - GUTTER * (per - 1)) / per
        els: list[Element] = [title_el(spec.title)]
        for i, item in enumerate(spec.panels):
            text = item.text or "\n".join(f"• {line}" for line in item.items)
            r, c = divmod(i, per)
            x = MARGIN + (cw + GUTTER) * c
            y = BODY_TOP + (ch + GUTTER) * r
            els.append(Line(x1=x, y1=y, x2=x + cw, y2=y, color="grid", width=RULE["hair"]))
            d = min(80, ch * 0.34)
            iy = y + 24
            els.append(Shape(x=x + cw / 2 - d / 2, y=iy, w=d, h=d, shape="ellipse", fill="primary"))
            els.append(
                mid_text(
                    x=x + cw / 2 - d / 2,
                    y=iy,
                    w=d,
                    h=d,
                    text=(item.icon or str(i + 1)),
                    font_size=snap_down(d * 0.5),
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
            ty = iy + d + 16
            els.append(
                mid_text(
                    x=x + 12,
                    y=ty,
                    w=cw - 24,
                    h=30,
                    text=item.head,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
            if text:
                els.append(
                    Text(
                        x=x + 16,
                        y=ty + 34,
                        w=cw - 32,
                        h=y + ch - ty - 44,
                        text=text,
                        font_size=TYPE["body"],
                        align="center",
                    )
                )
        if spec.banner:
            els += banner(spec.banner, 580)
        return els
