"""family=programme: plans, timelines and project status."""

from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from .base import Text, TextList


class Milestone(BaseModel):
    date: Text = Field(description="Date or period label for the milestone.")
    label: Text | None = Field(default=None, description="Milestone heading.")
    detail: Text | None = Field(default=None, description="Supporting detail text.")
    icon: Text | None = Field(default=None, description="Optional icon name.")


class TimelineSlide(BaseModel):
    type: Literal["timeline"] = Field(
        default="timeline", description="Slide type discriminator. The value is always 'timeline'."
    )
    title: str = Field(description="Slide headline.")
    milestones: list[Milestone] = Field(
        min_length=2, max_length=10, description="Milestones in order, between 2 and 10."
    )
    today: int | None = Field(
        default=None,
        description="0-based index of the milestone that represents 'now'.",
    )


class Step(BaseModel):
    head: Text = Field(description="Step heading.")
    text: Text | None = Field(default=None, description="Supporting text for the step.")
    owner: Text | None = Field(default=None, description="Responsible owner.")
    date: Text | None = Field(default=None, description="Target date.")
    done: bool = Field(default=False, description="Whether the step is complete.")


class StepsSlide(BaseModel):
    type: Literal["steps"] = Field(
        default="steps", description="Slide type discriminator. The value is always 'steps'."
    )
    title: str = Field(description="Slide headline.")
    steps: list[Step] = Field(min_length=1, max_length=8, description="Steps, between 1 and 8.")
    ask: Text | None = Field(default=None, description="Optional 'ask' callout.")


class GanttRow(BaseModel):
    name: Text = Field(description="Row name.")
    start: float = Field(description="0-based index of the first period.")
    end: float = Field(
        description=(
            "0-based index of the last period, inclusive. The bar covers start through end + 1."
        )
    )
    group: Text | None = Field(default=None, description="Optional group label.")
    progress: float | None = Field(
        default=None, ge=0, le=100, description="Optional completion percentage, 0-100."
    )


class GanttMilestone(BaseModel):
    label: Text = Field(description="GanttMilestone label.")
    at: float = Field(
        description=("Position in periods. The value 0 is the start of the first period.")
    )


class GanttSlide(BaseModel):
    type: Literal["gantt"] = Field(
        default="gantt", description="Slide type discriminator. The value is always 'gantt'."
    )
    title: str = Field(description="Slide headline.")
    periods: TextList = Field(
        min_length=2, max_length=24, description="Period labels, between 2 and 24."
    )
    rows: list[GanttRow] = Field(
        min_length=1, max_length=14, description="Gantt rows, between 1 and 14."
    )
    milestones: list[GanttMilestone] = Field(default=[], description="Optional milestones.")
    today: float | None = Field(default=None, description="Optional 'today' position in periods.")

    @model_validator(mode="after")
    def _check(self):
        n = len(self.periods)
        for r in self.rows:
            if not (0 <= r.start <= r.end < n):
                raise ValueError(f"gantt: '{r.name}' must satisfy 0 <= start <= end < {n}")
        return self


class TrackerRow(BaseModel):
    stream: Text = Field(description="Workstream name.")
    owner: Text | None = Field(default=None, description="Owner.")
    state: Text = Field(description="Current state label.")
    percent: float | None = Field(
        default=None, ge=0, le=100, description="Completion percentage, 0-100."
    )
    next: Text | None = Field(default=None, description="Next step.")
    date: Text | None = Field(default=None, description="Next-step date.")


class TrackerSlide(BaseModel):
    type: Literal["tracker"] = Field(
        default="tracker", description="Slide type discriminator. The value is always 'tracker'."
    )
    title: str = Field(description="Slide headline.")
    rows: list[TrackerRow] = Field(
        min_length=1, max_length=10, description="Tracker rows, between 1 and 10."
    )


class DiscussionSlide(BaseModel):
    type: Literal["discussion"] = Field(
        default="discussion",
        description=("Slide type discriminator. The value is always 'discussion'."),
    )
    title: str = Field(description="Slide headline.")
    question: Text = Field(description="Discussion question.")
    prompts: TextList = Field(default=[], description="Optional discussion prompts.")
    timebox: Text | None = Field(default=None, description="Optional timebox, e.g. '15 min'.")
