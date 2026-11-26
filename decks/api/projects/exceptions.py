from dataclasses import dataclass
from http import HTTPStatus

from decks.exceptions import AppError


@dataclass(eq=False)
class ProjectsApiError(AppError):
    """Base class of the errors of the project endpoints."""


@dataclass(eq=False)
class SlideIndexNotFoundError(ProjectsApiError):
    """Raised when a project has no slide at the given index."""

    TEMPLATE = "project {project_id} has no slide at index {index}"
    STATUS_CODE = HTTPStatus.NOT_FOUND
    project_id: str
    index: int
