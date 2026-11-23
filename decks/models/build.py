from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

type Phase = Literal["draft", "interviewing", "review", "approved", "generating", "generated"]

MAX_REPAIRS = 3


class BuiltSlide(BaseModel):
    """Build record of one slide. A changed hash means the slide must be rebuilt."""

    content_hash: str
    revision: int
    edited: bool = False
    warnings: list[str] = Field(default_factory=list)


class BuildState(BaseModel):
    """Phase and build bookkeeping of a project."""

    phase: Phase = "draft"
    plan_revision: int = 0
    deck_revision: int | None = None
    built: dict[str, BuiltSlide] = Field(default_factory=dict)
    repairs_remaining: int = MAX_REPAIRS


class ProjectInfo(BaseModel):
    """Metadata of a project."""

    id: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
