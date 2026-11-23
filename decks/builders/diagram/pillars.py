"""Pillar slides: supporting pillars under a roof."""

from decks.builders.base import BaseBuilder
from decks.builders.common import (
    CONTENT_TOP,
    CONTENT_W,
    MARGIN,
    SPACE,
    TYPE,
    W,
    bullets,
    mid_text,
    title_el,
)
from decks.models.diagram import PillarsSlide
from decks.models.elements import Element, Line, Polygon, Shape, Text


class PillarsBuilder(BaseBuilder[PillarsSlide]):
    """Render a roof supported by pillars, with an optional foundation."""

    TYPE = "pillars"
    DESCRIPTION = (
        "Use this slide for a strategy house: an overarching roof on pillars. You can also add a "
        "foundation below the pillars."
    )
    SPEC = PillarsSlide

    def build(self, spec: PillarsSlide) -> list[Element]:
        n = len(spec.pillars)
        gap = SPACE["m"]
        pw = (CONTENT_W - gap * (n - 1)) / n
        els: list[Element] = [title_el(spec.title)]
        els.append(
            Polygon(
                points=[
                    (MARGIN, 215),
                    (MARGIN + 60, 140),
                    (W - MARGIN - 60, 140),
                    (W - MARGIN, 215),
                ],
                fill="primary",
            )
        )
        els.append(
            mid_text(
                x=MARGIN + 80,
                y=CONTENT_TOP,
                w=CONTENT_W - 160,
                h=75,
                text=spec.roof,
                font_size=TYPE["lead"],
                bold=True,
                color="bg",
                align="center",
            )
        )
        bottom = 540 if spec.foundation else 620
        for i, pillar in enumerate(spec.pillars):
            x = MARGIN + (pw + gap) * i
            els.append(
                mid_text(
                    x=x,
                    y=228,
                    w=pw,
                    h=50,
                    text=pillar.head,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                )
            )
            els.append(Line(x1=x, y1=280, x2=x + pw, y2=280, color="primary", width=2))
            els.append(Line(x1=x, y1=280, x2=x, y2=bottom, color="grid", width=1))
            els.append(
                Text(
                    x=x + 12,
                    y=292,
                    w=pw - 12,
                    h=bottom - 300,
                    text=bullets(pillar.items),
                    font_size=TYPE["body"],
                )
            )
        if spec.foundation:
            els.append(Shape(x=MARGIN - 10, y=550, w=CONTENT_W + 20, h=64, fill="primary"))
            els.append(
                mid_text(
                    x=MARGIN + 20,
                    y=550,
                    w=CONTENT_W - 40,
                    h=64,
                    text=spec.foundation,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
        return els
