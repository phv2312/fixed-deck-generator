"""For/against slides: two opposing lists and a verdict."""

from decks.builders.base import BaseBuilder
from decks.builders.common import banner, mid_text, title_el
from decks.design import CONTENT_W, MARGIN, RULE, TYPE
from decks.models.decisions import ForAgainstSlide
from decks.models.elements import Element, Line, Shape


class ForAgainstBuilder(BaseBuilder[ForAgainstSlide]):
    """Render arguments for and against a position, with optional verdict."""

    TYPE = "forandagainst"
    DESCRIPTION = (
        "Use this slide to weigh arguments for and against a proposal. You can also add a verdict "
        "banner at the end."
    )
    SPEC = ForAgainstSlide

    def build(self, spec: ForAgainstSlide) -> list[Element]:
        gap = 24
        cw = (CONTENT_W - gap) / 2
        bottom = 540 if spec.verdict else 620
        els: list[Element] = [title_el(spec.title)]
        cols = (
            (spec.for_label, "✓", spec.for_, "primary", "light"),
            (spec.against_label, "✕", spec.against, "muted", "muted"),
        )
        for k, (head, glyph, items, fill, glyph_fill) in enumerate(cols):
            x = MARGIN + (cw + gap) * k
            els.append(Line(x1=x, y1=200, x2=x + cw, y2=200, color=fill, width=3))
            els.append(
                mid_text(
                    x=x,
                    y=144,
                    w=cw,
                    h=52,
                    text=head,
                    font_size=TYPE["h3"],
                    bold=True,
                    color=fill,
                )
            )
            rh = min(62, (bottom - 216) / max(1, len(items)))
            for i, text in enumerate(items):
                y = 216 + rh * i
                els.append(
                    Shape(x=x + 8, y=y + rh / 2 - 15, w=30, h=30, shape="ellipse", fill=glyph_fill)
                )
                els.append(
                    mid_text(
                        x=x + 8,
                        y=y + rh / 2 - 15,
                        w=30,
                        h=30,
                        text=glyph,
                        font_size=TYPE["body"],
                        bold=True,
                        color="primary" if glyph == "✓" else "bg",
                        align="center",
                    )
                )
                els.append(
                    mid_text(
                        x=x + 52,
                        y=y,
                        w=cw - 60,
                        h=rh,
                        text=text,
                        font_size=TYPE["body_l"],
                    )
                )
                els.append(
                    Line(
                        x1=x + 52, y1=y + rh, x2=x + cw, y2=y + rh, color="grid", width=RULE["hair"]
                    )
                )
        if spec.verdict:
            els += banner(spec.verdict, 552)
        return els
