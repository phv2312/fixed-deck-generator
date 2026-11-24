"""Two-chart slides: two charts side by side with headings."""

from decks.builders.base import BaseBuilder
from decks.builders.charts import ChartRenderer
from decks.builders.common import mid_text, title_el
from decks.design import CONTENT_W, MARGIN, RULE, SPACE, TYPE
from decks.models.analytics import TwoChartsSlide
from decks.models.elements import Element, Line


class TwoChartsBuilder(BaseBuilder[TwoChartsSlide]):
    """Render two charts side by side, each with a heading and note."""

    TYPE = "twocharts"
    DESCRIPTION = (
        "Use this slide to place two charts side by side for comparison. Each chart has a heading "
        "and an optional note."
    )
    SPEC = TwoChartsSlide

    def build(self, spec: TwoChartsSlide) -> list[Element]:
        gap = SPACE["xl"]
        cw = (CONTENT_W - gap) / 2
        els: list[Element] = [title_el(spec.title)]
        for k, side in enumerate((spec.left, spec.right)):
            x = MARGIN + (cw + gap) * k
            els.append(
                mid_text(
                    x=x,
                    y=125,
                    w=cw,
                    h=36,
                    text=side.head,
                    font_size=TYPE["lead"],
                    bold=True,
                    color="primary",
                )
            )
            els.append(Line(x1=x, y1=164, x2=x + cw, y2=164, color="grid", width=RULE["hair"]))
            els += ChartRenderer(side.chart).draw(x, 180, cw, 390)
            if side.note:
                els.append(
                    mid_text(
                        x=x,
                        y=582,
                        w=cw,
                        h=40,
                        text=side.note,
                        font_size=TYPE["small"],
                        color="muted",
                    )
                )
        return els
