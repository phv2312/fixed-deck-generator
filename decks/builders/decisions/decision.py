"""Decision slides: recommendation, reasons and figures."""

from decks.builders.base import BaseBuilder
from decks.builders.common import (
    CONTENT_W,
    MARGIN,
    RADIUS,
    TYPE,
    W,
    bullets,
    mid_text,
    snap_down,
    title_el,
)
from decks.models.decisions import DecisionSlide
from decks.models.elements import Element, Line, Shape, Text


class DecisionBuilder(BaseBuilder[DecisionSlide]):
    """Render a recommendation panel with reasons and supporting figures."""

    TYPE = "decision"
    DESCRIPTION = (
        "Use this slide to state a recommendation with its question and reasons. You can add "
        "figures and the cost of no action."
    )
    SPEC = DecisionSlide

    def build(self, spec: DecisionSlide) -> list[Element]:
        els: list[Element] = [title_el(spec.title)]
        els.append(
            mid_text(
                x=MARGIN,
                y=120,
                w=CONTENT_W,
                h=64,
                text=spec.question,
                font_size=TYPE["lead"],
                color="muted",
            )
        )
        lw = 704 if spec.figures else CONTENT_W
        bottom = 536 if spec.otherwise else 624
        top = 208
        els.append(
            Shape(x=MARGIN, y=top, w=lw, h=bottom - top, fill="primary", radius=RADIUS["md"])
        )
        els.append(
            mid_text(
                x=MARGIN + 32,
                y=top + 24,
                w=lw - 64,
                h=88,
                text=spec.recommendation,
                font_size=TYPE["h3"],
                bold=True,
                color="bg",
            )
        )
        if spec.reasons:
            els.append(
                Line(
                    x1=MARGIN + 32,
                    y1=top + 128,
                    x2=MARGIN + 96,
                    y2=top + 128,
                    color="light",
                    width=2,
                )
            )
            els.append(
                Text(
                    x=MARGIN + 32,
                    y=top + 144,
                    w=lw - 64,
                    h=bottom - top - 160,
                    text=bullets(spec.reasons),
                    font_size=TYPE["body_l"],
                    color="bg",
                )
            )
        if spec.figures:
            n = len(spec.figures)
            fx = MARGIN + lw + 32
            fw = W - MARGIN - fx
            fh = (bottom - top - 16 * (n - 1)) / n
            for i, figure in enumerate(spec.figures):
                y = top + (fh + 16) * i
                els.append(Line(x1=fx, y1=y, x2=fx + fw, y2=y, color="grid", width=1))
                els.append(
                    mid_text(
                        x=fx,
                        y=y + 8,
                        w=fw,
                        h=fh * 0.5,
                        text=figure.figure,
                        font_size=snap_down(min(TYPE["display"], fh * 0.45)),
                        bold=True,
                        color="primary",
                    )
                )
                els.append(
                    Text(
                        x=fx,
                        y=y + 8 + fh * 0.5,
                        w=fw,
                        h=fh * 0.5 - 16,
                        text=figure.label,
                        font_size=TYPE["body"],
                        color="muted",
                    )
                )
        if spec.otherwise:
            els.append(Line(x1=MARGIN, y1=560, x2=W - MARGIN, y2=560, color="grid", width=1))
            els.append(
                mid_text(
                    x=MARGIN,
                    y=568,
                    w=CONTENT_W,
                    h=56,
                    text=f"If we do nothing: {spec.otherwise}",
                    font_size=TYPE["body_l"],
                    color="text",
                )
            )
        return els
