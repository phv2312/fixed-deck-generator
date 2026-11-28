"""Positioned elements. All coordinates are absolute slide pixels (top-left origin).
Colors are theme tokens (e.g. "primary") or hex strings ("#RRGGBB")."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator

from decks.models.exceptions import (
    TableHighlightRangeError,
    TableListLengthError,
    TableRowWidthError,
)

BULLET = "• "  # a text line that starts with this is a list item; the renderer hangs its wraps


class _Box(BaseModel):
    id: str = ""
    x: float
    y: float
    w: float
    h: float


class Text(_Box):
    type: Literal["text"] = "text"
    text: str
    font_size: float = 16
    bold: bool = False
    color: str = "text"
    align: Literal["left", "center", "right"] = "left"
    valign: Literal["top", "middle", "bottom"] = "top"
    mono: bool = False
    italic: bool = False
    underline: bool = False
    font_family: str | None = None


class Shape(_Box):
    type: Literal["shape"] = "shape"
    shape: Literal["rect", "ellipse"] = "rect"
    fill: str | None = None
    stroke: str | None = None
    stroke_width: float = 1
    opacity: float = 1.0
    dash: bool = False
    radius: float = 0  # corner radius for rect


class Image(_Box):
    type: Literal["image"] = "image"
    src: str
    fit: Literal["cover", "contain"] = "cover"


class Table(_Box):
    """A table. Every optional field keeps the plain grid look when it is left out.

    ``col_widths`` are fractions of ``w``. ``row_height`` is in px. ``highlight_row`` counts the
    rows after the header when ``header`` is true, else all rows. ``rules`` ``"lines"`` draws a
    heavy rule under the header and a hairline under each row, with no vertical lines.
    ``caption`` is a note under the table. It sits outside the box, so it follows the table.
    """

    type: Literal["table"] = "table"
    rows: list[list[str]]
    header: bool = True
    font_size: float = 14
    col_widths: list[float] | None = None
    align: list[Literal["left", "center", "right"]] | None = None
    row_height: float | None = None
    highlight_row: int | None = None
    highlight_col: int | None = None
    rules: Literal["grid", "lines"] = "grid"
    caption: str | None = None

    @property
    def columns(self) -> int:
        """Return the number of columns, counted on the first row."""
        return len(self.rows[0]) if self.rows else 0

    @property
    def body_rows(self) -> int:
        """Return the number of rows below the header."""
        return len(self.rows) - (1 if self.header and self.rows else 0)

    @model_validator(mode="after")
    def _check(self) -> Self:
        n = self.columns
        if any(len(row) != n for row in self.rows):
            raise TableRowWidthError(n)
        for field, value in (("col_widths", self.col_widths), ("align", self.align)):
            if value is not None and len(value) != n:
                raise TableListLengthError(field, n)
        for field, index, size in (
            ("highlight_row", self.highlight_row, self.body_rows),
            ("highlight_col", self.highlight_col, n),
        ):
            if index is not None and not 0 <= index < size:
                raise TableHighlightRangeError(field, index, size - 1)
        return self


class Chart(_Box):
    """Native chart (data only). Not rendered natively yet; builders use primitives."""

    type: Literal["chart"] = "chart"
    kind: Literal["bar", "line", "pie", "bubble"] = "bar"
    data: dict = Field(default_factory=dict)


class Polygon(BaseModel):
    type: Literal["polygon"] = "polygon"
    id: str = ""
    points: list[tuple[float, float]]
    fill: str | None = None
    stroke: str | None = None
    stroke_width: float = 1
    opacity: float = 1.0
    dash: bool = False


class Line(BaseModel):
    type: Literal["line"] = "line"
    id: str = ""
    x1: float
    y1: float
    x2: float
    y2: float
    color: str = "grid"
    width: float = 1
    dash: bool = False
    arrow: bool = False  # arrowhead at (x2, y2)


class Group(BaseModel):
    """Logical grouping only; children keep absolute slide coordinates."""

    type: Literal["group"] = "group"
    id: str = ""
    name: str = ""
    children: list["Element"] = Field(default_factory=list)


Element = Annotated[
    Text | Shape | Image | Table | Chart | Polygon | Line | Group,
    Field(discriminator="type"),
]
Group.model_rebuild()
