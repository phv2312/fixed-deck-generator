"""family=analytics: parameters of chart and data slides."""

from typing import Literal, Self

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from .base import Text, TextList
from .exceptions import ChartSeriesLengthError, MekkoColumnLengthError


class Axis(BaseModel):
    label: str = Field(description="Axis title shown along the axis.")
    min: float | None = Field(
        default=None,
        description=(
            "Lower bound of the axis scale. If you omit it, the slide derives it from the data."
        ),
    )
    max: float | None = Field(
        default=None,
        description=(
            "Upper bound of the axis scale. If you omit it, the slide derives it from the data."
        ),
    )


class BubbleItem(BaseModel):
    name: str = Field(description="Label shown next to the bubble.")
    x: float = Field(description="Horizontal value of the bubble.")
    y: float = Field(description="Vertical value of the bubble.")
    size: float = Field(description="Size weight of the bubble. Larger values draw larger bubbles.")


class BubbleSlide(BaseModel):
    type: Literal["bubble"] = Field(
        default="bubble", description="Slide type discriminator. The value is always 'bubble'."
    )
    title: str = Field(description="Slide headline.")
    items: list[BubbleItem] = Field(description="Bubbles to plot.")
    x_axis: Axis | str = Field(
        description="Horizontal axis: structured Axis settings, or a plain axis label string."
    )
    y_axis: Axis | str = Field(
        description="Vertical axis: structured Axis settings, or a plain axis label string."
    )
    split: tuple[float, float] | None = Field(
        default=None,
        description=(
            "Optional (x, y) split values for the dashed quadrant lines. The slide shades "
            "the top-right quadrant."
        ),
    )
    size_label: str | float | None = Field(
        default=None, description="Label for the bubble-size legend, e.g. a unit or scale note."
    )
    highlight: int | None = Field(
        default=None, description="0-based index into items drawn in the primary color."
    )


class MekkoColumn(BaseModel):
    name: str = Field(description="Column label.")
    size: float = Field(
        description=(
            "Width weight of the column. The slide normalises the widths across all columns."
        )
    )
    values: list[float] = Field(
        description="Segment values, one per entry in parts. The slide normalises them to 100%."
    )


class MekkoSlide(BaseModel):
    type: Literal["mekko"] = Field(
        default="mekko", description="Slide type discriminator. The value is always 'mekko'."
    )
    title: str = Field(description="Slide headline.")
    columns: list[MekkoColumn] = Field(
        description="Columns, each with a width weight and one value per part."
    )
    parts: list[str] = Field(description="Segment labels, stacked top to bottom.")
    highlight: tuple[int, int] | None = Field(
        default=None, description="(column index, part index) pair to emphasise."
    )
    unit: str | float | None = Field(default=None, description="Unit of the column size values.")

    @model_validator(mode="after")
    def _check(self) -> Self:
        for c in self.columns:
            if len(c.values) != len(self.parts):
                raise MekkoColumnLengthError(c.name, len(self.parts))
        return self


ChartType = Literal[
    "column", "bar", "stacked", "hstacked", "bar100", "line", "doughnut", "waterfall"
]


class Chart(BaseModel):
    type: ChartType = Field(description="Chart type to render.")
    categories: TextList = Field(description="Category labels along the value axis.")
    series: dict[str, list[float]] | list[float] = Field(
        description=(
            "A mapping of series name to values, or one unnamed list of values, one per category."
        )
    )
    unit: Text | None = Field(
        default=None, description="Unit suffix shown with the values, e.g. 'k€'."
    )
    labels: bool = Field(default=True, description="If true, the chart prints value labels.")
    highlight: int | None = Field(default=None, description="0-based category index to emphasise.")
    centre: Text | None = Field(default=None, description="Centre text for doughnut charts.")
    totals: list[int] | None = Field(
        default=None,
        description=(
            "Waterfall only: indices of the total bars. A value of 0 uses the running sum. "
            "Any other value sets the total to that value."
        ),
    )

    def named_series(self) -> dict[str, list[float]]:
        return self.series if isinstance(self.series, dict) else {"": self.series}

    @model_validator(mode="after")
    def _check(self) -> Self:
        for k, v in self.named_series().items():
            if len(v) != len(self.categories):
                raise ChartSeriesLengthError(k, len(self.categories))
        return self


class ExhibitSlide(BaseModel):
    type: Literal["exhibit"] = Field(
        default="exhibit", description="Slide type discriminator. The value is always 'exhibit'."
    )
    title: str = Field(description="Slide headline.")
    chart: Chart = Field(description="Chart configuration for the exhibit.")
    takeaway: Text | None = Field(
        default=None,
        description=(
            "Takeaway text. Omit takeaway, so_what and figure to get a bare full-width chart."
        ),
    )
    so_what: TextList = Field(
        default=[], description="Optional 'so what' bullets shown beside the chart."
    )
    figure: Text | None = Field(default=None, description="Optional figure label for the exhibit.")
    source: Text | None = Field(
        default=None, description="Source line shown at the bottom of the slide."
    )
    note: Text | None = Field(default=None, description="Additional footnote text.")


class ChartSide(BaseModel):
    head: Text = Field(description="Side heading.")
    chart: Chart = Field(description="Chart for this side.")
    note: Text | None = Field(default=None, description="Optional note under the chart.")


class TwoChartsSlide(BaseModel):
    type: Literal["twocharts"] = Field(
        default="twocharts",
        description=("Slide type discriminator. The value is always 'twocharts'."),
    )
    title: str = Field(description="Slide headline.")
    left: ChartSide = Field(description="Left-hand chart panel.")
    right: ChartSide = Field(description="Right-hand chart panel.")
