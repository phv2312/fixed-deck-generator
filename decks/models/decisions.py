"""family=decisions: options, assessments and decisions."""

from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    model_validator,
)

from .base import Text, TextList
from .exceptions import (
    EvaluationCriteriaMismatchError,
    EvaluationOptionMismatchError,
    RaciAccountableCountError,
    RaciAssignmentCountError,
    RaciInvalidAssignmentError,
)


class Cell(BaseModel):
    score: int = Field(ge=0, le=4, description="Harvey-ball fill from 0 (empty) to 4 (full).")
    note: str | None = Field(default=None, description="Optional note shown under the rating.")


def _cell(v: object) -> object:
    return {"score": v} if isinstance(v, (int, float)) else v


class EvaluationSlide(BaseModel):
    type: Literal["evaluation"] = Field(
        default="evaluation",
        description=("Slide type discriminator. The value is always 'evaluation'."),
    )
    title: str = Field(description="Slide headline.")
    criteria: TextList = Field(description="Evaluation criteria. Each criterion is one matrix row.")
    options: TextList = Field(description="Options to compare. Each option is one matrix column.")
    scores: list[list[Annotated[Cell, BeforeValidator(_cell)]]] = Field(
        description=(
            "Rating matrix indexed as scores[criterion][option]. Each cell is a Harvey-ball "
            "score or an object with a score and a note."
        )
    )
    recommended: int | None = Field(
        default=None,
        description=("0-based index of the recommended option. The slide shades its column."),
    )
    key: Text | None = Field(
        default=None, description="Legend text for the rating scale. It replaces the default."
    )

    @model_validator(mode="after")
    def _check(self) -> Self:
        if len(self.scores) != len(self.criteria):
            raise EvaluationCriteriaMismatchError(len(self.scores), len(self.criteria))
        if any(len(r) != len(self.options) for r in self.scores):
            raise EvaluationOptionMismatchError(len(self.options))
        return self


class Option(BaseModel):
    name: Text = Field(description="Option name.")
    pros: TextList = Field(default=[], description="Advantages of the option.")
    cons: TextList = Field(default=[], description="Drawbacks of the option.")
    icon: Text | None = Field(default=None, description="Optional icon name.")


class OptionsSlide(BaseModel):
    type: Literal["options"] = Field(
        default="options", description="Slide type discriminator. The value is always 'options'."
    )
    title: str = Field(description="Slide headline.")
    options: list[Option] = Field(
        min_length=2, max_length=4, description="Options to compare, between 2 and 4."
    )
    recommended: int | None = Field(
        default=None, description="0-based index of the recommended option."
    )


class Figure(BaseModel):
    figure: Text = Field(description="Large figure value.")
    label: Text = Field(description="Caption under the figure.")


class DecisionSlide(BaseModel):
    type: Literal["decision"] = Field(
        default="decision", description="Slide type discriminator. The value is always 'decision'."
    )
    title: str = Field(description="Slide headline.")
    question: Text = Field(description="The decision question.")
    recommendation: Text = Field(description="Recommended course of action.")
    reasons: TextList = Field(default=[], description="Reasons supporting the recommendation.")
    figures: list[Figure] = Field(
        default=[], max_length=3, description="Supporting figures, at most 3."
    )
    otherwise: Text | None = Field(default=None, description="Consequence of taking no action.")


class Activity(BaseModel):
    name: Text = Field(description="Activity name.")
    assignments: list[str] = Field(
        description="One R/A/C/I assignment per role. Use a blank string for no assignment."
    )


class RaciSlide(BaseModel):
    type: Literal["raci"] = Field(
        default="raci", description="Slide type discriminator. The value is always 'raci'."
    )
    title: str = Field(description="Slide headline.")
    roles: TextList = Field(min_length=2, max_length=8, description="Role names, between 2 and 8.")
    activities: list[Activity] = Field(
        min_length=1, max_length=12, description="Activities, between 1 and 12."
    )

    @model_validator(mode="after")
    def _check(self) -> Self:
        for a in self.activities:
            if len(a.assignments) != len(self.roles):
                raise RaciAssignmentCountError(a.name, len(self.roles))
            cells = [x.strip().upper() for x in a.assignments]
            if any(c not in ("", "R", "A", "C", "I", "A/R", "R/A") for c in cells):
                raise RaciInvalidAssignmentError(a.name)
            if sum("A" in c for c in cells) != 1:
                raise RaciAccountableCountError(a.name)
        return self


class Kpi(BaseModel):
    name: Text = Field(description="KPI name.")
    actual: Text = Field(description="Current value.")
    target: Text | None = Field(default=None, description="Target value.")
    trend: Literal["up", "flat", "down"] | None = Field(
        default=None, description="Trend direction indicator."
    )
    state: Text | None = Field(default=None, description="Optional status label, e.g. 'On track'.")
    unit: Text | None = Field(default=None, description="Unit suffix for the values.")


class ScorecardSlide(BaseModel):
    type: Literal["scorecard"] = Field(
        default="scorecard",
        description=("Slide type discriminator. The value is always 'scorecard'."),
    )
    title: str = Field(description="Slide headline.")
    kpis: list[Kpi] = Field(min_length=1, max_length=10, description="KPIs, between 1 and 10.")


class SwotSlide(BaseModel):
    type: Literal["swot"] = Field(
        default="swot", description="Slide type discriminator. The value is always 'swot'."
    )
    title: str = Field(description="Slide headline.")
    strengths: TextList = Field(default=[], description="Strengths (internal, positive).")
    weaknesses: TextList = Field(default=[], description="Weaknesses (internal, negative).")
    opportunities: TextList = Field(default=[], description="Opportunities (external, positive).")
    threats: TextList = Field(default=[], description="Threats (external, negative).")
    highlight: Literal["strengths", "weaknesses", "opportunities", "threats"] | None = Field(
        default=None, description="Quadrant to emphasise."
    )


class ForAgainstSlide(BaseModel):
    type: Literal["forandagainst"] = Field(
        default="forandagainst",
        description=("Slide type discriminator. The value is always 'forandagainst'."),
    )
    title: str = Field(description="Slide headline.")
    for_: TextList = Field(alias="for", description="Arguments in favour.")
    against: TextList = Field(description="Arguments against.")
    for_label: Text = Field(
        default="For", description="Heading for the 'for' column, e.g. 'Do' or 'Pros'."
    )
    against_label: Text = Field(
        default="Against",
        description="Heading for the 'against' column, e.g. 'Don't' or 'Cons'.",
    )
    verdict: Text | None = Field(default=None, description="Optional conclusion line.")

    model_config = {"populate_by_name": True}
