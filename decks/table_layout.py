"""Size a table: the font step, the row height, the column widths and the alignment.

The table builder, the deck API, the checker and the fitter all use this one class, so a table
that a person edits keeps the layout that the builder gives to a new table.
"""

import re
from dataclasses import dataclass
from typing import Literal

from decks.design import TYPE
from decks.models.elements import Table
from decks.text_metrics import OVERFLOW_TOLERANCE, TextMetrics

NUM = re.compile(r"^[\s\-+−]?[\d.,'’ ]+\s*(%|[A-Za-z]{0,4})?$")
CELL_PAD = 10  # horizontal padding of a cell, each side
MAX_ROW_H = 54
TABLE_H = 450  # the height that the rows share
MIN_WEIGHT, MAX_WEIGHT = 6, 40  # clamp of the character count that sets a column width

# The fields that ``relaid`` can change.
LAYOUT_FIELDS = frozenset(
    {"font_size", "row_height", "h", "col_widths", "align", "highlight_row", "highlight_col"}
)

type Align = Literal["left", "center", "right"]


@dataclass(frozen=True)
class CellOverflow:
    """A cell whose text needs more height than its row has."""

    row: int
    col: int
    need: float


class TableLayout:
    """Compute and repair the layout of a ``Table``."""

    def __init__(self, metrics: TextMetrics | None = None) -> None:
        self._metrics = metrics or TextMetrics()

    @staticmethod
    def font_step(body_rows: int) -> float:
        """Return the largest font size on the type scale that suits ``body_rows`` rows."""
        if body_rows <= 8:
            return float(TYPE["body_l"])
        return float(TYPE["body"] if body_rows <= 12 else TYPE["small"])

    @staticmethod
    def row_height(total_rows: int) -> float:
        """Return the height of one row when ``total_rows`` rows share the table height."""
        return min(MAX_ROW_H, TABLE_H / max(1, total_rows))

    @staticmethod
    def col_widths(rows: list[list[str]]) -> list[float]:
        """Return the width of each column as a fraction of the table, from the longest cell."""
        weights = [
            max(MIN_WEIGHT, min(MAX_WEIGHT, max(len(row[j]) for row in rows)))
            for j in range(len(rows[0]))
        ]
        return [weight / sum(weights) for weight in weights]

    @staticmethod
    def auto_align(body: list[list[str]], columns: int) -> list[Align]:
        """Return ``right`` for a column of numbers and ``left`` for any other column."""
        return [
            "right" if all(NUM.match(row[j]) for row in body) else "left" for j in range(columns)
        ]

    def adapted(self, before: Table, after: Table) -> Table:
        """Return ``after``, with its layout made again when it has another shape than ``before``.

        A change of the cell text alone keeps the layout, so a size that a person chose stays.
        """
        if (len(after.rows), after.columns) == (len(before.rows), before.columns):
            return after
        return self.relaid(after)

    def layout_changes(self, before: Table, after: Table) -> dict[str, object]:
        """Return the layout fields that ``after`` needs, or none when the shape is as before."""
        laid = self.adapted(before, after)
        return {} if laid is after else laid.model_dump(include=set(LAYOUT_FIELDS))

    def relaid(self, table: Table) -> Table:
        """Return ``table`` with the layout that its rows need.

        The font size only goes down, so a size that a person chose stays. A column list that no
        longer matches the columns is computed again. A highlight that left the table is dropped.
        The height of the table follows the rows. A table with uneven rows is returned as it is.
        """
        rows = table.rows
        if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
            return table
        columns = len(rows[0])
        row_h = self.row_height(len(rows))
        widths = self._matching(table.col_widths, columns)
        align = self._matching(table.align, columns)
        body = rows[1:] if table.header else rows
        return table.model_copy(
            update={
                "font_size": min(table.font_size, self.font_step(len(body))),
                "row_height": row_h,
                "h": row_h * len(rows),
                "col_widths": widths or self.col_widths(rows),
                "align": align or self.auto_align(body, columns),
                "highlight_row": self._kept(table.highlight_row, len(body)),
                "highlight_col": self._kept(table.highlight_col, columns),
            }
        )

    def overflow(self, table: Table) -> list[CellOverflow]:
        """Return the cells that need more height than their row has."""
        if not table.rows:
            return []
        row_h, widths = self._row_height(table), self._widths(table)
        found = []
        for i, row in enumerate(table.rows):
            bold = table.header and i == 0
            for j, cell in enumerate(row):
                need = self._need(cell, table.font_size, widths[j] * table.w, bold=bold)
                if need > row_h * OVERFLOW_TOLERANCE:
                    found.append(CellOverflow(row=i, col=j, need=need))
        return found

    def fitted(self, table: Table) -> Table:
        """Return ``table`` with the largest font size at which every cell fits its row."""
        if not table.rows:
            return table
        row_h, widths = self._row_height(table), self._widths(table)
        size = table.font_size
        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row):
                box = (max(1.0, widths[j] * table.w - 2 * CELL_PAD), row_h)
                bold = table.header and i == 0
                size = min(size, self._metrics.fit_font_size(cell, size, box, bold=bold).size)
        return table if size >= table.font_size else table.model_copy(update={"font_size": size})

    def _need(self, text: str, font_size: float, width: float, *, bold: bool) -> float:
        return self._metrics.height(text, font_size, max(1.0, width - 2 * CELL_PAD), bold=bold)

    @staticmethod
    def _row_height(table: Table) -> float:
        return table.row_height or table.h / len(table.rows)

    @staticmethod
    def _widths(table: Table) -> list[float]:
        return table.col_widths or [1 / table.columns] * table.columns

    @staticmethod
    def _matching[T](values: list[T] | None, columns: int) -> list[T] | None:
        """Return ``values`` when it has one entry for each column, else ``None``."""
        return values if values and len(values) == columns else None

    @staticmethod
    def _kept(index: int | None, size: int) -> int | None:
        return index if index is not None and 0 <= index < size else None
