from dataclasses import dataclass

from decks.exceptions import AppError


@dataclass(eq=False)
class ProjectsApiError(AppError):
    """Base class of the errors of the project endpoints."""
