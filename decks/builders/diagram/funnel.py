"""Funnel slides: narrowing stages with conversion notes."""

from decks.builders.base import BaseBuilder
from decks.builders.common import TYPE, mid_text, snap_down, title_el, trapezoid
from decks.models.diagram import FunnelSlide
from decks.models.elements import Element, Line, Polygon

XC, TOP, H = 320, 150, 440
W0, W1 = 500, 130
TX = 640


def num(value: str | None) -> float | None:
    """Parse a numeric stage value, returning None when it is not numeric."""
    try:
        return float(str(value).replace(",", "").replace("'", ""))
    except (TypeError, ValueError):
        return None


class FunnelBuilder(BaseBuilder[FunnelSlide]):
    """Render a narrowing funnel with stage notes and conversion rates."""

    TYPE = "funnel"
    DESCRIPTION = (
        "Use this slide to show a progressive narrowing through 2 to 6 stages. Each stage can have "
        "a note and a conversion value from the previous stage."
    )
    SPEC = FunnelSlide

    def build(self, spec: FunnelSlide) -> list[Element]:
        n = len(spec.stages)
        hi = n - 1 if spec.highlight is None else spec.highlight
        gap = 4
        sh = (H - gap * (n - 1)) / n

        def width(t: float) -> float:
            return W0 + (W1 - W0) * t

        els: list[Element] = [title_el(spec.title)]
        for i, stage in enumerate(spec.stages):
            y0 = TOP + (sh + gap) * i
            y1 = y0 + sh
            w0, w1 = width((y0 - TOP) / H), width((y1 - TOP) / H)
            fill = "primary" if i == hi else "tint"
            els.append(Polygon(points=trapezoid(XC, y0, y1, w0, w1), fill=fill))
            label = f"{stage.value}  {stage.label}" if stage.value is not None else stage.label
            els.append(
                mid_text(
                    x=XC - w1 / 2 + 6,
                    y=y0,
                    w=w1 - 12,
                    h=sh,
                    text=label,
                    font_size=snap_down(TYPE["body"]),
                    bold=True,
                    color="bg" if i == hi else "primary",
                    align="center",
                )
            )
            cy = y0 + sh / 2
            els.append(
                Line(
                    x1=XC + (w0 + w1) / 4 + 10,
                    y1=cy,
                    x2=TX - 12,
                    y2=cy,
                    color="grid",
                    width=1,
                    dash=True,
                )
            )
            lines = []
            if stage.text:
                lines.append(stage.text)
            a, b = num(stage.value), num(spec.stages[i - 1].value) if i else None
            if a is not None and b:
                lines.append(f"{a / b * 100:.0f} % of previous stage")
            if lines:
                els.append(
                    mid_text(
                        x=TX,
                        y=cy - 30,
                        w=1216 - TX,
                        h=60,
                        text="\n".join(lines),
                        font_size=TYPE["body"],
                    )
                )
        return els
