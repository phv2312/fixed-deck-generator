"""family=diagram: parameters of process and concept diagram slides."""

from typing import Literal, Self

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from .base import Text, TextList
from .exceptions import (
    OrgNeedsMembersError,
    PyramidRingLevelsError,
    SwimlaneLinkOutOfRangeError,
    SwimlaneUnknownLaneError,
)


class DriverNode(BaseModel):
    label: Text = Field(description="Node label.")
    value: Text | None = Field(default=None, description="Value shown at the node.")
    op: Literal["×", "+", "-", "x", "*"] | None = Field(
        default=None, description="Operator combining the children into this node."
    )
    children: list["DriverNode"] = Field(
        default=[], description=("Child nodes. The list is empty for a leaf.")
    )


class DriverTreeSlide(BaseModel):
    type: Literal["drivertree"] = Field(
        default="drivertree",
        description=("Slide type discriminator. The value is always 'drivertree'."),
    )
    title: str = Field(description="Slide headline.")
    root: DriverNode = Field(description="Root node of the driver tree.")
    highlight: Text | None = Field(default=None, description="Label of the node to emphasise.")


class CycleItem(BaseModel):
    label: Text = Field(description="Step label.")
    text: Text | None = Field(default=None, description="Supporting text for the step.")
    icon: Text | None = Field(default=None, description="Optional icon name.")


class CycleSlide(BaseModel):
    type: Literal["cycle"] = Field(
        default="cycle", description="Slide type discriminator. The value is always 'cycle'."
    )
    title: str = Field(description="Slide headline.")
    centre: Text = Field(description="Text in the centre of the cycle.")
    items: list[CycleItem] = Field(
        min_length=3, max_length=6, description="Cycle steps, between 3 and 6."
    )
    highlight: int | None = Field(
        default=None, description="0-based index of the step to emphasise."
    )


class Stage(BaseModel):
    label: Text = Field(description="Stage label.")
    value: Text | None = Field(default=None, description="Value shown for the stage.")
    text: Text | None = Field(default=None, description="Supporting text for the stage.")


class FunnelSlide(BaseModel):
    type: Literal["funnel"] = Field(
        default="funnel", description="Slide type discriminator. The value is always 'funnel'."
    )
    title: str = Field(description="Slide headline.")
    stages: list[Stage] = Field(
        min_length=2, max_length=6, description="Funnel stages, between 2 and 6, widest first."
    )
    highlight: int | None = Field(
        default=None,
        description="0-based index of the stage to emphasise. The default is the last stage.",
    )


class Layer(BaseModel):
    name: Text = Field(description="Layer name.")
    elements: TextList = Field(default=[], description="Elements contained in the layer.")


class LayersSlide(BaseModel):
    type: Literal["layers"] = Field(
        default="layers", description="Slide type discriminator. The value is always 'layers'."
    )
    title: str = Field(description="Slide headline.")
    layers: list[Layer] = Field(
        min_length=1, max_length=7, description="Layers, between 1 and 7, top layer first."
    )
    highlight: int | list[int] | None = Field(
        default=None, description="0-based layer index, or list of indices, to emphasise."
    )


class MatrixAxis(BaseModel):
    low: Text | None = Field(default=None, description="Low-end axis label.")
    high: Text | None = Field(default=None, description="High-end axis label.")
    name: Text | None = Field(default=None, description="Axis name.")


class MatrixItem(BaseModel):
    label: Text = Field(description="Item label.")
    x: float = Field(description="Horizontal position.")
    y: float = Field(description="Vertical position.")


class MatrixSlide(BaseModel):
    type: Literal["matrix"] = Field(
        default="matrix", description="Slide type discriminator. The value is always 'matrix'."
    )
    title: str = Field(description="Slide headline.")
    x_axis: MatrixAxis = Field(description="Horizontal axis configuration.")
    y_axis: MatrixAxis = Field(description="Vertical axis configuration.")
    items: list[MatrixItem] = Field(
        min_length=1, max_length=12, description="Items to plot, between 1 and 12."
    )
    quadrants: TextList | None = Field(
        default=None,
        description="Optional quadrant labels in order [top-left, top-right, bottom-left, "
        "bottom-right].",
    )
    highlight: int | None = Field(
        default=None, description="0-based index of the item to emphasise."
    )
    scale: tuple[float, float] = Field(
        default=(0, 10), description="(min, max) value range shared by the x and y axes."
    )


class Person(BaseModel):
    name: Text = Field(description="Person's name.")
    role: Text | None = Field(default=None, description="Role or title.")


class OrgGroup(BaseModel):
    label: Text = Field(description="Group name.")
    members: list[Person] = Field(default=[], description="People in the group.")


class OrgSlide(BaseModel):
    type: Literal["org"] = Field(
        default="org", description="Slide type discriminator. The value is always 'org'."
    )
    title: str = Field(description="Slide headline.")
    head: Person = Field(description="Person at the top of the organisation.")
    members: list[Person] = Field(default=[], description="Direct reports of the head.")
    groups: list[OrgGroup] = Field(
        default=[], description="Grouped reports. The members or groups must not be empty."
    )

    @model_validator(mode="after")
    def _check(self) -> Self:
        if not self.members and not self.groups:
            raise OrgNeedsMembersError
        return self


class Level(BaseModel):
    label: Text = Field(description="Level name.")
    text: Text | None = Field(default=None, description="Supporting text for the level.")


class PyramidSlide(BaseModel):
    type: Literal["pyramid"] = Field(
        default="pyramid", description="Slide type discriminator. The value is always 'pyramid'."
    )
    title: str = Field(description="Slide headline.")
    levels: list[Level] = Field(
        min_length=2,
        max_length=6,
        description=(
            "Levels, between 2 and 6. A pyramid lists the top first. Rings list the core first, "
            "between 3 and 5."
        ),
    )
    style: Literal["pyramid", "rings"] = Field(
        default="pyramid",
        description="'pyramid' for stacked levels, or 'rings' for concentric rings around a core.",
    )
    highlight: int | None = Field(
        default=None, description="0-based index of the ring to emphasise. Only for style rings."
    )

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.style == "rings" and not 3 <= len(self.levels) <= 5:
            raise PyramidRingLevelsError(len(self.levels))
        return self


class Circle(BaseModel):
    label: Text = Field(description="Circle label.")
    items: TextList = Field(default=[], description="Items belonging to this circle.")


class VennSlide(BaseModel):
    type: Literal["venn"] = Field(
        default="venn", description="Slide type discriminator. The value is always 'venn'."
    )
    title: str = Field(description="Slide headline.")
    circles: list[Circle] = Field(
        min_length=2, max_length=3, description="Circles, between 2 and 3."
    )
    overlap: Text = Field(description="Text for the shared overlap region.")


class Category(BaseModel):
    label: Text = Field(description="Cause category label.")
    causes: TextList = Field(
        default=[], max_length=5, description="Causes in this category, at most 5."
    )


class FishboneSlide(BaseModel):
    type: Literal["fishbone"] = Field(
        default="fishbone", description="Slide type discriminator. The value is always 'fishbone'."
    )
    title: str = Field(description="Slide headline.")
    effect: Text = Field(description="The effect or problem to analyse.")
    categories: list[Category] = Field(
        min_length=3, max_length=6, description="Cause categories, between 3 and 6."
    )


class Pillar(BaseModel):
    head: Text = Field(description="Pillar heading.")
    items: TextList = Field(default=[], description="Items supporting the pillar.")


class PillarsSlide(BaseModel):
    type: Literal["pillars"] = Field(
        default="pillars", description="Slide type discriminator. The value is always 'pillars'."
    )
    title: str = Field(description="Slide headline.")
    roof: Text = Field(description="Text on the roof of the structure.")
    pillars: list[Pillar] = Field(
        min_length=3, max_length=5, description="Pillars, between 3 and 5."
    )
    foundation: Text | None = Field(default=None, description="Optional foundation text.")


class ProcessStep(BaseModel):
    head: Text = Field(description="Step heading.")
    items: TextList = Field(default=[], description="Supporting details for the step.")
    icon: Text | None = Field(default=None, description="Optional icon name.")
    period: Text | None = Field(
        default=None, description="Optional period or date label shown under the heading."
    )


class ProcessSlide(BaseModel):
    type: Literal["process"] = Field(
        default="process", description="Slide type discriminator. The value is always 'process'."
    )
    title: str = Field(description="Slide headline.")
    steps: list[ProcessStep] = Field(
        min_length=3, max_length=6, description="Process steps, between 3 and 6."
    )
    highlight: int | None = Field(
        default=None, description="0-based index of the step to emphasise."
    )


class LaneStep(BaseModel):
    lane: Text = Field(
        description=("Name of the lane that contains the step. The value must match one of lanes.")
    )
    label: Text = Field(description="Step label.")
    col: int = Field(ge=0, le=7, description="0-based column position, 0-7.")


class Link(BaseModel):
    from_: int = Field(alias="from", description="0-based index of the source step.")
    to: int = Field(description="0-based index of the target step.")
    model_config = {"populate_by_name": True}


class SwimlanesSlide(BaseModel):
    type: Literal["swimlanes"] = Field(
        default="swimlanes",
        description=("Slide type discriminator. The value is always 'swimlanes'."),
    )
    title: str = Field(description="Slide headline.")
    lanes: TextList = Field(min_length=2, max_length=5, description="Lane names, between 2 and 5.")
    steps: list[LaneStep] = Field(
        min_length=2, max_length=14, description="Steps, between 2 and 14."
    )
    links: list[Link] = Field(default=[], description="Optional links between step indices.")

    @model_validator(mode="after")
    def _check(self) -> Self:
        for s in self.steps:
            if s.lane not in self.lanes:
                raise SwimlaneUnknownLaneError(s.label, s.lane)
        n = len(self.steps)
        for link in self.links:
            if not (0 <= link.from_ < n and 0 <= link.to < n):
                raise SwimlaneLinkOutOfRangeError(link.from_, link.to, n - 1)
        return self
