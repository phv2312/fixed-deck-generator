"""Table slides: a table with a header row."""

import re
from typing import Literal

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_W, MARGIN, TYPE, W, mid_text, title_el
from decks.models.body import TableSlide
from decks.models.elements import Element, Line, Shape

NUM = re.compile(r"^[\s\-+−]?[\d.,'’ ]+\s*(%|[A-Za-z]{0,4})?$")
Align = Literal["left", "center", "right"]


class TableBuilder(BaseBuilder[TableSlide]):
    """Render a table with proportional column widths and highlights."""

    TYPE = "table"
    DESCRIPTION = (
        "Use this slide for tabular data with a header row. You can highlight a column or a row, "
        "align each column and add a note."
    )
    SPEC = TableSlide

    def build(self, spec: TableSlide) -> list[Element]:
        cols, n = len(spec.header), len(spec.rows)
        fs = TYPE["body_l"] if n <= 8 else (TYPE["body"] if n <= 12 else TYPE["small"])
        rh = min(54, 450 / (n + 1))
        longest = [
            max(len(spec.header[j]), *(len(row[j]) for row in spec.rows)) for j in range(cols)
        ]
        weights = [max(6, min(40, length)) for length in longest]
        total_w = CONTENT_W
        ws = [total_w * weight / sum(weights) for weight in weights]
        xs = [MARGIN + sum(ws[:j]) for j in range(cols)]
        align: list[Align] = spec.align or [
            "right" if all(NUM.match(row[j]) for row in spec.rows) else "left" for j in range(cols)
        ]
        top = 150
        els: list[Element] = [title_el(spec.title)]
        if spec.highlight_col is not None:
            j = spec.highlight_col
            els.append(Shape(x=xs[j], y=top, w=ws[j], h=rh * (n + 1), fill="tint"))
        if spec.highlight_row is not None:
            els.append(
                Shape(x=MARGIN, y=top + rh * (spec.highlight_row + 1), w=total_w, h=rh, fill="tint")
            )
        for j, header in enumerate(spec.header):
            els.append(
                mid_text(
                    x=xs[j] + 10,
                    y=top,
                    w=ws[j] - 20,
                    h=rh,
                    text=header,
                    font_size=fs,
                    bold=True,
                    color="primary",
                    align=align[j],
                )
            )
        els.append(
            Line(x1=MARGIN, y1=top + rh, x2=W - MARGIN, y2=top + rh, color="primary", width=2.5)
        )
        for i, row in enumerate(spec.rows):
            y = top + rh * (i + 1)
            hi = spec.highlight_row == i
            for j, cell in enumerate(row):
                els.append(
                    mid_text(
                        x=xs[j] + 10,
                        y=y,
                        w=ws[j] - 20,
                        h=rh,
                        text=cell,
                        font_size=fs,
                        bold=hi,
                        color="primary" if hi else "text",
                        align=align[j],
                    )
                )
            els.append(Line(x1=MARGIN, y1=y + rh, x2=W - MARGIN, y2=y + rh, color="grid", width=1))
        if spec.note:
            els.append(
                mid_text(
                    x=MARGIN,
                    y=top + rh * (n + 1) + 12,
                    w=total_w,
                    h=28,
                    text=spec.note,
                    font_size=TYPE["caption"],
                    color="muted",
                )
            )
        return els
