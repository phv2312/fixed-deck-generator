"""Evaluation slides: scored criteria against options."""

import math

from decks.builders.base import BaseBuilder
from decks.builders.common import arc_pts, mid_text, title_el
from decks.design import BODY_TOP, MARGIN, RULE, TYPE, W
from decks.models.decisions import EvaluationSlide
from decks.models.elements import Element, Line, Polygon, Shape

X0, X1 = MARGIN, W - MARGIN
CRIT_W = 300
TOP = BODY_TOP


def ball(cx: float, cy: float, d: float, score: int) -> list[Element]:
    """Return a score ball or partial pie for one cell."""
    r = d / 2
    els: list[Element] = [
        Shape(
            x=cx - r,
            y=cy - r,
            w=d,
            h=d,
            shape="ellipse",
            fill="primary" if score == 4 else "bg",
            stroke="primary",
            stroke_width=RULE["thin"],
        )
    ]
    if 0 < score < 4:
        pts = [(cx, cy), *arc_pts(cx, cy, r, 0, 2 * math.pi * score / 4)]
        els.append(Polygon(points=pts, fill="primary"))
    return els


class EvaluationBuilder(BaseBuilder[EvaluationSlide]):
    """Render a scored evaluation matrix."""

    TYPE = "evaluation"
    DESCRIPTION = (
        "Use this slide to score options against criteria with 0 to 4 score balls. You can also "
        "mark a recommended option and add a legend."
    )
    SPEC = EvaluationSlide

    def build(self, spec: EvaluationSlide) -> list[Element]:
        m, n = len(spec.options), len(spec.criteria)
        col_w = (X1 - X0 - CRIT_W) / m
        row_h = min(84, 340 / n)
        rows_top = TOP + 54
        bottom = rows_top + row_h * n
        els: list[Element] = [title_el(spec.title)]

        def cx(j: int) -> float:
            return X0 + CRIT_W + col_w * (j + 0.5)

        if spec.recommended is not None:
            els.append(
                Shape(
                    x=cx(spec.recommended) - col_w / 2 + 6,
                    y=TOP,
                    w=col_w - 12,
                    h=bottom - TOP + 8,
                    fill="tint",
                )
            )
        els.append(
            mid_text(
                x=X0,
                y=TOP + 6,
                w=CRIT_W,
                h=40,
                text="Criteria",
                font_size=TYPE["small"],
                bold=True,
                color="muted",
            )
        )
        for j, option in enumerate(spec.options):
            els.append(
                mid_text(
                    x=cx(j) - col_w / 2 + 8,
                    y=TOP + 6,
                    w=col_w - 16,
                    h=40,
                    text=option,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
        els.append(Line(x1=X0, y1=rows_top - 4, x2=X1, y2=rows_top - 4, color="primary", width=2.5))

        for i, criterion in enumerate(spec.criteria):
            cy = rows_top + row_h * (i + 0.5)
            els.append(
                mid_text(
                    x=X0,
                    y=cy - row_h / 2,
                    w=CRIT_W - 16,
                    h=row_h,
                    text=criterion,
                    font_size=TYPE["body_l"],
                    bold=True,
                )
            )
            for j in range(m):
                cell = spec.scores[i][j]
                if cell.note:
                    els += ball(cx(j) - col_w * 0.18, cy, 36, cell.score)
                    els.append(
                        mid_text(
                            x=cx(j) - col_w * 0.18 + 28,
                            y=cy - row_h / 2,
                            w=col_w * 0.5,
                            h=row_h,
                            text=cell.note,
                            font_size=TYPE["caption"],
                            color="muted",
                        )
                    )
                else:
                    els += ball(cx(j), cy, 36, cell.score)
            if i < n - 1:
                els.append(
                    Line(
                        x1=X0,
                        y1=rows_top + row_h * (i + 1),
                        x2=X1,
                        y2=rows_top + row_h * (i + 1),
                        color="grid",
                        width=RULE["hair"],
                    )
                )

        ly = bottom + 28
        if spec.key:
            els.append(
                mid_text(
                    x=X0,
                    y=ly,
                    w=800,
                    h=24,
                    text=spec.key,
                    font_size=TYPE["small"],
                    color="muted",
                )
            )
        else:
            x = X0
            for score, label in ((0, "not met"), (2, "partly met"), (4, "fully met")):
                els += ball(x + 10, ly + 12, 20, score)
                els.append(
                    mid_text(
                        x=x + 28,
                        y=ly,
                        w=110,
                        h=24,
                        text=label,
                        font_size=TYPE["small"],
                        color="muted",
                    )
                )
                x += 150
        return els
