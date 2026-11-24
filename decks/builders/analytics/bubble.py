"""Bubble slides: items positioned on two axes with size."""

import math

from decks.builders.base import BaseBuilder
from decks.builders.common import fmt, mid_text, nice_range, title_el
from decks.design import BANNER_Y, MARGIN, RULE, TYPE, W
from decks.models.analytics import Axis, BubbleSlide
from decks.models.elements import Element, Line, Shape

PL, PT, PR, PB = 130, 180, W - MARGIN, BANNER_Y
R_MAX = 42


class BubbleBuilder(BaseBuilder[BubbleSlide]):
    """Render a bubble chart with optional quadrant split."""

    TYPE = "bubble"
    DESCRIPTION = (
        "Use this slide to position items on two numeric axes. Bubble size adds a third measure. "
        "You can also split the chart into quadrants."
    )
    SPEC = BubbleSlide

    @staticmethod
    def _axis(axis: Axis | str) -> Axis:
        return axis if isinstance(axis, Axis) else Axis(label=axis)

    def build(self, spec: BubbleSlide) -> list[Element]:
        xa, ya = self._axis(spec.x_axis), self._axis(spec.y_axis)
        xs = [i.x for i in spec.items]
        ys = [i.y for i in spec.items]
        x0, x1, xstep = nice_range(min(xs), max(xs))
        y0, y1, ystep = nice_range(min(ys), max(ys))
        x0 = xa.min if xa.min is not None else x0
        x1 = xa.max if xa.max is not None else x1
        y0 = ya.min if ya.min is not None else y0
        y1 = ya.max if ya.max is not None else y1

        def px(v: float) -> float:
            return PL + (v - x0) / (x1 - x0) * (PR - PL)

        def py(v: float) -> float:
            return PB - (v - y0) / (y1 - y0) * (PB - PT)

        els: list[Element] = [title_el(spec.title)]

        if spec.split:
            sx, sy = px(spec.split[0]), py(spec.split[1])
            els.append(Shape(x=sx, y=PT, w=PR - sx, h=sy - PT, fill="tint", opacity=0.9))

        t = math.ceil(y0 / ystep) * ystep
        while t <= y1 + 1e-9:
            els.append(Line(x1=PL, y1=py(t), x2=PR, y2=py(t), color="grid", width=RULE["hair"]))
            els.append(
                mid_text(
                    x=PL - 70,
                    y=py(t) - 10,
                    w=60,
                    h=20,
                    text=fmt(t),
                    font_size=TYPE["small"],
                    color="muted",
                    align="right",
                )
            )
            t += ystep
        t = math.ceil(x0 / xstep) * xstep
        while t <= x1 + 1e-9:
            els.append(
                mid_text(
                    x=px(t) - 30,
                    y=PB + 8,
                    w=60,
                    h=20,
                    text=fmt(t),
                    font_size=TYPE["small"],
                    color="muted",
                    align="center",
                )
            )
            t += xstep
        els.append(Line(x1=PL, y1=PB, x2=PR, y2=PB, color="muted", width=1.5))
        els.append(Line(x1=PL, y1=PT, x2=PL, y2=PB, color="muted", width=1.5))

        els.append(
            mid_text(
                x=MARGIN,
                y=PT - 40,
                w=500,
                h=24,
                text=ya.label,
                font_size=TYPE["body"],
                bold=True,
                color="muted",
            )
        )
        els.append(
            mid_text(
                x=PR - 500,
                y=PB + 36,
                w=500,
                h=24,
                text=xa.label,
                font_size=TYPE["body"],
                bold=True,
                color="muted",
                align="right",
            )
        )

        if spec.split:
            sx, sy = px(spec.split[0]), py(spec.split[1])
            els.append(Line(x1=sx, y1=PT, x2=sx, y2=PB, color="muted", width=1.5, dash=True))
            els.append(Line(x1=PL, y1=sy, x2=PR, y2=sy, color="muted", width=1.5, dash=True))

        smax = max(i.size for i in spec.items)
        order = sorted(range(len(spec.items)), key=lambda k: -spec.items[k].size)
        for k in order:
            it = spec.items[k]
            r = max(10.0, R_MAX * math.sqrt(it.size / smax))
            cx, cy = px(it.x), py(it.y)
            hi = spec.highlight == k
            els.append(
                Shape(
                    x=cx - r,
                    y=cy - r,
                    w=2 * r,
                    h=2 * r,
                    shape="ellipse",
                    fill="primary" if hi else "accent",
                    opacity=1.0 if hi else 0.55,
                    stroke="primary" if hi else "accent",
                    stroke_width=1.5,
                )
            )
            els.append(
                mid_text(
                    x=cx + r + 8,
                    y=cy - 12,
                    w=200,
                    h=24,
                    text=it.name,
                    font_size=TYPE["body"],
                    bold=hi,
                    color="text",
                )
            )

        if spec.size_label is not None:
            els.append(
                mid_text(
                    x=W - MARGIN - 400,
                    y=PT - 40,
                    w=400,
                    h=24,
                    text=f"{spec.size_label}",
                    font_size=TYPE["small"],
                    color="muted",
                    align="right",
                )
            )
        return els
