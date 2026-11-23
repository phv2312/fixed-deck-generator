"""Options slides: parallel options with pros and cons."""

from decks.builders.base import BaseBuilder
from decks.builders.common import (
    CONTENT_W,
    MARGIN,
    RADIUS,
    TYPE,
    bullets,
    icon_badge,
    mid_text,
    title_el,
)
from decks.models.decisions import OptionsSlide
from decks.models.elements import Element, Line, Shape, Text

GAP = 24
TOP, HEAD_H, BOTTOM = 160, 58, 610


class OptionsBuilder(BaseBuilder[OptionsSlide]):
    """Render competing options with pros, cons and a recommended one."""

    TYPE = "options"
    DESCRIPTION = (
        "Use this slide to compare 2 to 4 options directly. Each option has pros and cons. You can "
        "also mark one option as recommended."
    )
    SPEC = OptionsSlide

    def build(self, spec: OptionsSlide) -> list[Element]:
        m = len(spec.options)
        w = (CONTENT_W - GAP * (m - 1)) / m
        els: list[Element] = [title_el(spec.title)]
        for i, option in enumerate(spec.options):
            x = MARGIN + (w + GAP) * i
            recommended = spec.recommended == i
            els.append(
                Shape(
                    x=x,
                    y=TOP,
                    w=w,
                    h=HEAD_H,
                    fill="primary" if recommended else None,
                    radius=RADIUS["md"],
                )
            )
            if not recommended:
                els.append(
                    Line(x1=x, y1=TOP + HEAD_H, x2=x + w, y2=TOP + HEAD_H, color="primary", width=2)
                )
            off = 16
            if option.icon:
                els += icon_badge(
                    x + 14,
                    TOP + HEAD_H / 2 - 16,
                    32,
                    option.icon,
                    "bg" if recommended else "accent",
                )
                off = 58
            els.append(
                mid_text(
                    x=x + off,
                    y=TOP,
                    w=w - off - 12,
                    h=HEAD_H,
                    text=option.name,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="bg" if recommended else "primary",
                )
            )
            if recommended:
                els.append(
                    Shape(
                        x=x,
                        y=TOP + HEAD_H + 8,
                        w=w,
                        h=BOTTOM - TOP - HEAD_H - 8,
                        fill="tint",
                        radius=RADIUS["md"],
                    )
                )
            body_y = TOP + HEAD_H + 24
            section = (BOTTOM - body_y - 16) / 2
            for k, (label, items) in enumerate((("Pros", option.pros), ("Cons", option.cons))):
                y = body_y + section * k
                els.append(
                    mid_text(
                        x=x + 18,
                        y=y,
                        w=w - 36,
                        h=24,
                        text=label,
                        font_size=TYPE["body"],
                        bold=True,
                        color="primary",
                    )
                )
                els.append(
                    Text(
                        x=x + 18,
                        y=y + 28,
                        w=w - 36,
                        h=section - 34,
                        text=bullets(items),
                        font_size=TYPE["body"],
                    )
                )
            if recommended:
                els.append(
                    Shape(x=x + w - 128, y=TOP - 11, w=116, h=22, fill="ink", radius=RADIUS["pill"])
                )
                els.append(
                    mid_text(
                        x=x + w - 128,
                        y=TOP - 11,
                        w=116,
                        h=22,
                        text="Recommended",
                        font_size=TYPE["caption"],
                        bold=True,
                        color="bg",
                        align="center",
                    )
                )
        return els
