"""Mekko slides: variable-width stacked columns."""

from decks.builders.base import BaseBuilder
from decks.builders.common import fmt, mid_text, on, title_el
from decks.design import BODY_TOP, TYPE
from decks.models.analytics import MekkoSlide
from decks.models.elements import Element, Shape

X0, X1 = 64, 1020
TOP, BOTTOM = BODY_TOP, 560
GAP = 4
COLORS = ["light", "primary", "accent", "tint"]


class MekkoBuilder(BaseBuilder[MekkoSlide]):
    """Render a mekko chart of parts within variable-width columns."""

    TYPE = "mekko"
    DESCRIPTION = (
        "Use this slide to show market share or composition. In this slide, the column width and "
        "the stacked parts both have a meaning."
    )
    SPEC = MekkoSlide

    def build(self, spec: MekkoSlide) -> list[Element]:
        total = sum(c.size for c in spec.columns)
        avail = X1 - X0 - GAP * (len(spec.columns) - 1)
        unit = f" {spec.unit}" if spec.unit is not None else ""
        els: list[Element] = [title_el(spec.title)]
        x = X0
        for ci, col in enumerate(spec.columns):
            w = avail * col.size / total
            vsum = sum(col.values) or 1
            avail_h = BOTTOM - TOP - GAP * (len(spec.parts) - 1)
            y = TOP
            for pi, v in enumerate(col.values):
                h = avail_h * v / vsum
                hi = spec.highlight == (ci, pi)
                fill = "ink" if hi else COLORS[pi % len(COLORS)]
                els.append(Shape(x=x, y=y, w=w, h=h, fill=fill))
                els.append(
                    mid_text(
                        x=x,
                        y=y,
                        w=w,
                        h=h,
                        text=f"{v / vsum * 100:.0f} %",
                        font_size=TYPE["body"],
                        color=on(fill),
                        align="center",
                    )
                )
                if ci == len(spec.columns) - 1:
                    els.append(
                        mid_text(
                            x=X1 + 14,
                            y=y + h / 2 - 12,
                            w=220,
                            h=24,
                            text=spec.parts[pi],
                            font_size=TYPE["small"],
                        )
                    )
                y += h + GAP
            els.append(
                mid_text(
                    x=x,
                    y=BOTTOM + 10,
                    w=w,
                    h=24,
                    text=col.name,
                    font_size=TYPE["body"],
                    bold=True,
                    align="center",
                )
            )
            els.append(
                mid_text(
                    x=x,
                    y=BOTTOM + 34,
                    w=w,
                    h=22,
                    text=f"{fmt(col.size)}{unit}",
                    font_size=TYPE["small"],
                    color="muted",
                    align="center",
                )
            )
            x += w + GAP
        return els
