"""Positioned elements. All coordinates are absolute slide pixels (top-left origin).
Colors are theme tokens (e.g. "primary") or hex strings ("#RRGGBB")."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

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
    type: Literal["table"] = "table"
    rows: list[list[str]]
    header: bool = True
    font_size: float = 14


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
    children: list[Element] = Field(default_factory=list)


Element = Annotated[
    Text | Shape | Image | Table | Chart | Polygon | Line | Group,
    Field(discriminator="type"),
]
Group.model_rebuild()
