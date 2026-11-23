"""Glossary slides: term and definition pairs in two columns."""

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_W, MARGIN, TYPE, mid_text, title_el
from decks.models.body import GlossarySlide
from decks.models.elements import Element, Line, Text


class GlossaryBuilder(BaseBuilder[GlossarySlide]):
    """Render a two-column glossary of terms and definitions."""

    TYPE = "glossary"
    DESCRIPTION = (
        "Use this slide to define terms or acronyms. The slide shows two columns of term and "
        "definition pairs."
    )
    SPEC = GlossarySlide

    def build(self, spec: GlossarySlide) -> list[Element]:
        n = len(spec.terms)
        per = -(-n // 2)
        gap = 48
        cw = (CONTENT_W - gap) / 2
        rh = min(100, 460 / per)
        els: list[Element] = [title_el(spec.title)]
        for i, term in enumerate(spec.terms):
            c, r = divmod(i, per)
            x, y = MARGIN + (cw + gap) * c, 150 + rh * r
            els.append(
                mid_text(
                    x=x,
                    y=y,
                    w=cw,
                    h=28,
                    text=term.term,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                )
            )
            els.append(
                Text(
                    x=x,
                    y=y + 28,
                    w=cw,
                    h=rh - 34,
                    text=term.definition,
                    font_size=TYPE["body"] if rh >= 72 else TYPE["small"],
                )
            )
            els.append(Line(x1=x, y1=y + rh - 4, x2=x + cw, y2=y + rh - 4, color="grid", width=1))
        return els
