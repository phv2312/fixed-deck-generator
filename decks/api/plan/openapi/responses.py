from http import HTTPStatus
from typing import ClassVar

from decks.agents.exceptions import (
    PlanIncompleteError,
    PlanMissingError,
    ProjectNotFoundError,
    TurnInProgressError,
)
from decks.api.openapi import ErrorResponse, ExampleResponse, MultipleExamples, Responses
from decks.api.plan.exceptions import PlanLockedError
from decks.api.plan.openapi.examples import PlanExamples


class PlanResponses:
    """OpenAPI responses of the plan endpoints."""

    READ: ClassVar[Responses] = {
        HTTPStatus.OK: MultipleExamples(
            {"review": PlanExamples.READ, "asking": PlanExamples.ASKING},
            description="Successful response",
        ).to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(ProjectNotFoundError).to_openapi(),
    }
    APPROVE: ClassVar[Responses] = {
        HTTPStatus.OK: ExampleResponse(PlanExamples.READ).to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(ProjectNotFoundError).to_openapi(),
        HTTPStatus.CONFLICT: ErrorResponse(
            PlanMissingError, PlanIncompleteError, PlanLockedError, TurnInProgressError
        ).to_openapi(),
    }
