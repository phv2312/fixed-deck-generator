from dataclasses import dataclass
from http import HTTPStatus

from decks.exceptions import AppError


@dataclass(eq=False)
class PlanApiError(AppError):
    """Base class of the errors of the plan endpoints."""


@dataclass(eq=False)
class PlanLockedError(PlanApiError):
    """Raised when the plan is approved or in use: only a plan under interview can be approved."""

    TEMPLATE = "the plan of project {project_id} cannot be approved in phase {phase}"
    STATUS_CODE = HTTPStatus.CONFLICT
    project_id: str
    phase: str
