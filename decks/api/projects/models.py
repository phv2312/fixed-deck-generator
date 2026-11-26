from datetime import datetime

from pydantic import BaseModel

from decks.models.build import Phase, ProjectInfo


class ProjectSummary(BaseModel):
    """What the project list and the project page need to know about one project."""

    info: ProjectInfo
    phase: Phase
    updated_at: datetime
    slide_count: int

    @property
    def has_deck(self) -> bool:
        """Whether the project has a built deck with at least one slide."""
        return self.slide_count > 0
