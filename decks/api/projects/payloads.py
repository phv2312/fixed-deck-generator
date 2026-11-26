from datetime import datetime
from typing import Annotated, Self

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from decks.api.projects.models import ProjectSummary
from decks.models.build import Phase

SLIDE_HTML_URL = "/api/v1/projects/{project_id}/deck/slides/{index}/html"

ProjectId = Annotated[
    str,
    Path(
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$",
        description="Project id.",
        examples=["4f1c9a2e7b3d4c5e8a6b0d1e2f3a4b5c"],
    ),
]
SlideIndex = Annotated[int, Path(ge=0, description="Slide position, counted from 0.")]


class ProjectCreate(BaseModel):
    """Request body to create a project."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)] = (
        Field(description="Name of the project, shown in the project list.", examples=["Q3 review"])
    )


class ProjectResponse(BaseModel):
    """Response body for one project."""

    id: str = Field(description="Project id.")
    name: str = Field(description="Name of the project.")
    phase: Phase = Field(description="Where the project is: from draft to generated.")
    created_at: datetime = Field(description="When the project was created.")
    updated_at: datetime = Field(description="When a file of the project changed last.")
    slide_count: int = Field(description="Number of slides in the built deck. 0 before a deck.")
    thumbnail_url: str | None = Field(
        description="HTML page of the first slide, or null before a deck exists."
    )

    @classmethod
    def from_summary(cls, summary: ProjectSummary) -> Self:
        """Build the response from a domain summary."""
        project_id = summary.info.id
        return cls(
            id=project_id,
            name=summary.info.name,
            phase=summary.phase,
            created_at=summary.info.created_at,
            updated_at=summary.updated_at,
            slide_count=summary.slide_count,
            thumbnail_url=(
                SLIDE_HTML_URL.format(project_id=project_id, index=0) if summary.has_deck else None
            ),
        )
