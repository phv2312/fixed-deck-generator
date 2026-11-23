"""Row slides: numbered rows of labelled content."""

from decks.builders.base import BaseBuilder
from decks.builders.common import MARGIN, RADIUS, TYPE, W, banner, icon_badge, mid_text, title_el
from decks.models.body import RowsSlide
from decks.models.elements import Element, Line, Polygon, Shape

PILL_W = 400
TX = 540


class RowsBuilder(BaseBuilder[RowsSlide]):
    """Render numbered rows with optional icons and a conclusion banner."""

    TYPE = "rows"
    DESCRIPTION = (
        "Use this slide for a short numbered list of points. Each point has a label and an "
        "explanation. You can also add a conclusion at the end."
    )
    SPEC = RowsSlide

    def build(self, spec: RowsSlide) -> list[Element]:
        n = len(spec.rows)
        row_h = min(100, (410 if spec.conclusion else 450) / n)
        h = row_h - 22
        els: list[Element] = [title_el(spec.title)]
        for i, row in enumerate(spec.rows):
            y = 150 + row_h * i
            hi = spec.highlight == i
            els.append(
                Shape(
                    x=MARGIN,
                    y=y,
                    w=PILL_W,
                    h=h,
                    fill="primary" if hi else "tint",
                    radius=RADIUS["pill"] if h < 70 else RADIUS["md"],
                )
            )
            els.append(
                Shape(
                    x=MARGIN + 10,
                    y=y + h / 2 - 18,
                    w=36,
                    h=36,
                    shape="ellipse",
                    fill="bg" if hi else "primary",
                )
            )
            els.append(
                mid_text(
                    x=MARGIN + 10,
                    y=y + h / 2 - 18,
                    w=36,
                    h=36,
                    text=str(i + 1),
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary" if hi else "bg",
                    align="center",
                )
            )
            label_w = PILL_W - 66
            if row.icon:
                els += icon_badge(
                    MARGIN + PILL_W - 46, y + h / 2 - 17, 34, row.icon, "bg" if hi else "accent"
                )
                label_w -= 46
            els.append(
                mid_text(
                    x=MARGIN + 58,
                    y=y,
                    w=label_w,
                    h=h,
                    text=row.label,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="bg" if hi else "primary",
                )
            )
            ay = y + h / 2
            ax = MARGIN + PILL_W + 24
            els.append(
                Polygon(
                    points=[(ax, ay - 13), (ax, ay + 13), (ax + 22, ay)],
                    fill="primary" if hi else "light",
                )
            )
            if row.text:
                els.append(
                    mid_text(
                        x=TX,
                        y=y,
                        w=W - MARGIN - TX,
                        h=h,
                        text=row.text,
                        font_size=TYPE["body_l"],
                    )
                )
            if i < n - 1:
                els.append(
                    Line(
                        x1=TX,
                        y1=y + row_h - 11,
                        x2=W - MARGIN,
                        y2=y + row_h - 11,
                        color="grid",
                        width=1,
                    )
                )
        if spec.conclusion:
            els += banner(spec.conclusion, 585)
        return els
