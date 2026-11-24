"""Scorecard slides: KPI actuals, targets, trends and status."""

from typing import Literal

from decks.builders.base import BaseBuilder
from decks.builders.common import colour, mid_text, title_el
from decks.design import CONTENT_TOP, MARGIN, RULE, TREND_ARROWS, TYPE, W
from decks.models.decisions import ScorecardSlide
from decks.models.elements import Element, Line, Shape


class ScorecardBuilder(BaseBuilder[ScorecardSlide]):
    """Render a KPI scorecard with trend glyphs and status colours."""

    TYPE = "scorecard"
    DESCRIPTION = (
        "Use this slide for a KPI scorecard. Each row shows the actual value, the target, the "
        "trend direction and a traffic-light status."
    )
    SPEC = ScorecardSlide

    def build(self, spec: ScorecardSlide) -> list[Element]:
        n = len(spec.kpis)
        rh = min(58, 440 / n)
        cols: list[tuple[float, float, str, Literal["left", "center", "right"]]] = [
            (MARGIN, 380, "KPI", "left"),
            (460, 160, "Actual", "right"),
            (640, 160, "Target", "right"),
            (830, 100, "Trend", "center"),
            (950, 266, "Status", "left"),
        ]
        els: list[Element] = [title_el(spec.title)]
        for x, w, label, align in cols:
            els.append(
                mid_text(
                    x=x,
                    y=CONTENT_TOP,
                    w=w,
                    h=36,
                    text=label,
                    font_size=TYPE["small"],
                    bold=True,
                    color="muted",
                    align=align,
                )
            )
        els.append(
            Line(x1=MARGIN, y1=180, x2=W - MARGIN, y2=180, color="primary", width=RULE["thin"])
        )
        for i, kpi in enumerate(spec.kpis):
            y = 186 + rh * i
            unit = f" {kpi.unit}" if kpi.unit else ""
            els.append(
                mid_text(
                    x=MARGIN,
                    y=y,
                    w=380,
                    h=rh,
                    text=kpi.name,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                )
            )
            els.append(
                mid_text(
                    x=460,
                    y=y,
                    w=160,
                    h=rh,
                    text=kpi.actual + unit,
                    font_size=TYPE["lead"],
                    bold=True,
                    align="right",
                )
            )
            if kpi.target:
                els.append(
                    mid_text(
                        x=640,
                        y=y,
                        w=160,
                        h=rh,
                        text=kpi.target + unit,
                        font_size=TYPE["body_l"],
                        color="muted",
                        align="right",
                    )
                )
            if kpi.trend:
                glyph, color = TREND_ARROWS[kpi.trend]
                els.append(
                    mid_text(
                        x=830,
                        y=y,
                        w=100,
                        h=rh,
                        text=glyph,
                        font_size=TYPE["body_l"],
                        color=color,
                        align="center",
                    )
                )
            if kpi.state:
                color, glyph = colour(kpi.state)
                els.append(Shape(x=950, y=y + rh / 2 - 13, w=26, h=26, shape="ellipse", fill=color))
                els.append(
                    mid_text(
                        x=950,
                        y=y + rh / 2 - 13,
                        w=26,
                        h=26,
                        text=glyph,
                        font_size=TYPE["small"],
                        bold=True,
                        color="bg",
                        align="center",
                    )
                )
                els.append(
                    mid_text(
                        x=986,
                        y=y,
                        w=230,
                        h=rh,
                        text=kpi.state,
                        font_size=TYPE["body"],
                    )
                )
            els.append(
                Line(
                    x1=MARGIN, y1=y + rh, x2=W - MARGIN, y2=y + rh, color="grid", width=RULE["hair"]
                )
            )
        return els
