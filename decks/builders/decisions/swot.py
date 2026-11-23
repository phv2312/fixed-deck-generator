"""SWOT slides: strengths, weaknesses, opportunities, threats."""

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_W, MARGIN, RADIUS, TYPE, bullets, mid_text, title_el
from decks.models.decisions import SwotSlide
from decks.models.elements import Element, Line, Shape, Text


class SwotBuilder(BaseBuilder[SwotSlide]):
    """Render a four-quadrant SWOT analysis."""

    TYPE = "swot"
    DESCRIPTION = (
        "Use this slide for a SWOT analysis with strengths, weaknesses, opportunities and threats. "
        "You can highlight one quadrant."
    )
    SPEC = SwotSlide

    def build(self, spec: SwotSlide) -> list[Element]:
        quads = [
            ("S", "Strengths", spec.strengths, "strengths"),
            ("W", "Weaknesses", spec.weaknesses, "weaknesses"),
            ("O", "Opportunities", spec.opportunities, "opportunities"),
            ("T", "Threats", spec.threats, "threats"),
        ]
        gap = 32
        qw, qh = (CONTENT_W - gap) / 2, (464 - gap) / 2
        els: list[Element] = [title_el(spec.title)]
        for k, (_letter, name, items, key) in enumerate(quads):
            r, c = divmod(k, 2)
            x, y = MARGIN + (qw + gap) * c, 136 + (qh + gap) * r
            hi = spec.highlight == key
            if hi:
                els.append(Shape(x=x, y=y, w=qw, h=qh, fill="primary", radius=RADIUS["md"]))
            else:
                els.append(Line(x1=x, y1=y, x2=x + qw, y2=y, color="grid", width=1))
            px = x + (16 if hi else 0)
            els.append(
                mid_text(
                    x=px + 16,
                    y=y + 16,
                    w=qw - 48,
                    h=40,
                    text=name,
                    font_size=TYPE["lead"],
                    bold=True,
                    color="bg" if hi else "primary",
                )
            )
            els.append(
                Text(
                    x=px + 16,
                    y=y + 64,
                    w=qw - 48,
                    h=qh - 76,
                    text=bullets(items),
                    font_size=TYPE["body"],
                    color="bg" if hi else "text",
                )
            )
        return els
