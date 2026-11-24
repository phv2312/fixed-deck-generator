"""Exhibit slides: a chart with an optional takeaway and note card."""

from decks.builders.base import BaseBuilder
from decks.builders.charts import ChartRenderer
from decks.builders.common import bullets, mid_text, title_el
from decks.design import CONTENT_W, MARGIN, RADIUS, TYPE, W, snap_down
from decks.models.analytics import ExhibitSlide
from decks.models.elements import Element, Line, Shape, Text


class ExhibitBuilder(BaseBuilder[ExhibitSlide]):
    """Render a chart exhibit with optional takeaway and so-what card."""

    TYPE = "exhibit"
    DESCRIPTION = (
        "Use this slide for a chart-led slide. It supports column, stacked, bar, hstacked, bar100, "
        "line, doughnut and waterfall charts. You can also add a takeaway, a hero figure, "
        "a so-what list and a source note."
    )
    SPEC = ExhibitSlide

    def build(self, spec: ExhibitSlide) -> list[Element]:
        chart = spec.chart
        renderer = ChartRenderer(chart)
        els: list[Element] = [title_el(spec.title)]
        foot = "   ".join(
            x for x in (spec.note, f"Source: {spec.source}" if spec.source else None) if x
        )
        card = bool(spec.so_what or spec.figure)
        if spec.takeaway is None and not card:
            bottom = 600 if foot else 650
            els += renderer.draw(MARGIN, 130, CONTENT_W, bottom - 130)
        else:
            if spec.takeaway:
                els.append(
                    mid_text(
                        x=MARGIN,
                        y=118,
                        w=740 if card else CONTENT_W,
                        h=44,
                        text=spec.takeaway,
                        font_size=TYPE["lead"],
                        bold=True,
                        color="text",
                    )
                )
            if card:
                els += renderer.render()
            else:
                els += renderer.draw(MARGIN, 170, CONTENT_W, 430)
        if card:
            cx0, cw = 850, W - MARGIN - 850
            els.append(Shape(x=cx0, y=190, w=cw, h=420, fill="tint", radius=RADIUS["md"]))
            y = 214
            if spec.figure:
                els.append(
                    mid_text(
                        x=cx0 + 20,
                        y=y,
                        w=cw - 40,
                        h=70,
                        text=spec.figure,
                        font_size=snap_down(min(48, (cw - 40) / (0.6 * len(spec.figure)))),
                        bold=True,
                        color="primary",
                    )
                )
                els.append(
                    Line(x1=cx0 + 20, y1=y + 80, x2=cx0 + 80, y2=y + 80, color="accent", width=3)
                )
                y += 100
            if spec.so_what:
                els.append(
                    Text(
                        x=cx0 + 20,
                        y=y,
                        w=cw - 40,
                        h=610 - y - 20,
                        text=bullets(spec.so_what),
                        font_size=TYPE["body"],
                    )
                )
        if foot:
            els.append(
                mid_text(
                    x=MARGIN,
                    y=620,
                    w=CONTENT_W,
                    h=30,
                    text=foot,
                    font_size=TYPE["caption"],
                    color="muted",
                )
            )
        return els
