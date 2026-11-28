"""Table slides: a table with a header row."""

from decks.builders.base import BaseBuilder
from decks.builders.common import title_el
from decks.design import BODY_TOP, CONTENT_W, MARGIN, TYPE
from decks.models.body import TableSlide
from decks.models.elements import Element, Table
from decks.table_layout import TableLayout


class TableBuilder(BaseBuilder[TableSlide]):
    """Render one native table element with proportional column widths, highlights and a note."""

    TYPE = "table"
    DESCRIPTION = (
        "Use this slide for tabular data with a header row. You can highlight a column or a row, "
        "align each column and add a note."
    )
    SPEC = TableSlide

    def __init__(self, layout: TableLayout | None = None) -> None:
        self._layout = layout or TableLayout()

    def build(self, spec: TableSlide) -> list[Element]:
        table = Table(
            x=MARGIN,
            y=BODY_TOP,
            w=CONTENT_W,
            h=0,
            rows=[list(spec.header), *(list(row) for row in spec.rows)],
            font_size=TYPE["body_l"],
            align=spec.align,
            rules="lines",
            caption=spec.note,
        )
        table = self._layout.relaid(
            table.model_copy(
                update={"highlight_row": spec.highlight_row, "highlight_col": spec.highlight_col}
            )
        )
        return [title_el(spec.title), table]
