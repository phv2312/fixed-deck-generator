"""family=body: parameters of text, table and key-figure slides."""

from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from .base import Text, TextList


class Side(BaseModel):
    head: Text = Field(description="Heading of this side.")
    items: TextList = Field(
        default=[],
        description=("Bullet items. Both sides need the same number of items, from 1 to 6."),
    )
    icon: Text | None = Field(default=None, description="Optional icon name.")


class FromToSlide(BaseModel):
    type: Literal["fromto"] = Field(
        default="fromto", description="Slide type discriminator. The value is always 'fromto'."
    )
    title: str = Field(description="Slide headline.")
    left: Side = Field(description="Starting-state side.")
    right: Side = Field(description="Target-state side.")

    @model_validator(mode="after")
    def _check(self):
        if len(self.left.items) != len(self.right.items) or not 1 <= len(self.left.items) <= 6:
            raise ValueError("fromto: left and right need the same number (1-6) of items")
        return self


class Panel(BaseModel):
    head: Text = Field(description="Panel heading.")
    items: TextList = Field(default=[], description="Bullet items in the panel.")
    icon: Text | None = Field(default=None, description="Optional icon name.")
    text: Text | None = Field(
        default=None, description="Optional supporting text. The icons style shows it, not items."
    )


class PanelsSlide(BaseModel):
    type: Literal["panels"] = Field(
        default="panels", description="Slide type discriminator. The value is always 'panels'."
    )
    title: str = Field(description="Slide headline.")
    panels: list[Panel] = Field(
        min_length=1,
        max_length=8,
        description="Panels. The columns style takes 1 to 4. The icons style takes 2 to 8.",
    )
    highlight: int | None = Field(
        default=None, description="0-based index of the panel to emphasise. Columns style only."
    )
    style: Literal["columns", "icons"] = Field(
        default="columns",
        description=(
            "'columns' for panels with bullet lists, or 'icons' for a grid of icon, heading and "
            "text."
        ),
    )
    banner: Text | None = Field(
        default=None, description="Optional banner text across the bottom. Icons style only."
    )

    @model_validator(mode="after")
    def _check(self):
        count = len(self.panels)
        if self.style == "columns" and count > 4:
            raise ValueError("panels: style columns takes at most 4 panels")
        if self.style == "icons" and count < 2:
            raise ValueError("panels: style icons needs at least 2 panels")
        return self


class Row(BaseModel):
    label: Text = Field(description="Row heading.")
    text: Text | None = Field(default=None, description="Row body text.")
    icon: Text | None = Field(default=None, description="Optional icon name.")


class RowsSlide(BaseModel):
    type: Literal["rows"] = Field(
        default="rows", description="Slide type discriminator. The value is always 'rows'."
    )
    title: str = Field(description="Slide headline.")
    rows: list[Row] = Field(min_length=1, max_length=6, description="Rows, between 1 and 6.")
    highlight: int | None = Field(
        default=None, description="0-based index of the row to emphasise."
    )
    conclusion: Text | None = Field(
        default=None, description="Optional closing banner, executive-summary style."
    )


class Tile(BaseModel):
    figure: Text = Field(description="Headline figure.")
    label: Text = Field(description="Caption under the figure.")
    caption: Text | None = Field(default=None, description="Optional supporting caption.")


class KeyFiguresSlide(BaseModel):
    type: Literal["keyfigures"] = Field(
        default="keyfigures",
        description=("Slide type discriminator. The value is always 'keyfigures'."),
    )
    title: str = Field(description="Slide headline.")
    tiles: list[Tile] = Field(
        min_length=2, max_length=6, description="Figure tiles, between 2 and 6."
    )
    highlight: int | None = Field(
        default=None, description="0-based index of the tile to emphasise."
    )


class Term(BaseModel):
    term: Text = Field(description="Term to define.")
    definition: Text = Field(description="Definition of the term.")


class GlossarySlide(BaseModel):
    type: Literal["glossary"] = Field(
        default="glossary", description="Slide type discriminator. The value is always 'glossary'."
    )
    title: str = Field(description="Slide headline.")
    terms: list[Term] = Field(min_length=1, max_length=12, description="Terms, between 1 and 12.")


class TermLine(BaseModel):
    text: Text = Field(description="Line text.")
    kind: Literal["command", "output", "comment"] = Field(
        default="output", description="Line style: command, output, or comment."
    )


class TerminalSlide(BaseModel):
    type: Literal["terminal"] = Field(
        default="terminal", description="Slide type discriminator. The value is always 'terminal'."
    )
    title: str = Field(description="Slide headline.")
    lines: list[TermLine] = Field(
        min_length=1, max_length=14, description="Terminal lines, between 1 and 14."
    )


class TableSlide(BaseModel):
    type: Literal["table"] = Field(
        default="table", description="Slide type discriminator. The value is always 'table'."
    )
    title: str = Field(description="Slide headline.")
    header: list[Text] = Field(description="Column headers.")
    rows: list[list[Text]] = Field(
        min_length=1,
        max_length=16,
        description="Table rows, each with one cell per header. Use between 1 and 16 rows.",
    )
    align: list[Literal["left", "center", "right"]] | None = Field(
        default=None,
        description="Per-column alignment. The default is numbers right and text left.",
    )
    highlight_row: int | None = Field(default=None, description="0-based row index to emphasise.")
    highlight_col: int | None = Field(
        default=None, description="0-based column index to emphasise."
    )
    note: Text | None = Field(default=None, description="Optional footnote.")

    @model_validator(mode="after")
    def _check(self):
        n = len(self.header)
        if any(len(r) != n for r in self.rows):
            raise ValueError(f"table: every row needs {n} cells")
        if self.align is not None and len(self.align) != n:
            raise ValueError(f"table: align needs {n} entries")
        return self
