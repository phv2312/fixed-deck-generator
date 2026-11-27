from http import HTTPStatus
from typing import ClassVar

from decks.agents.exceptions import ProjectNotFoundError, TurnInProgressError
from decks.api.openapi import EmptyResponse, ErrorResponse, ExampleResponse, Responses
from decks.api.projects.openapi.examples import ProjectExamples


class ProjectResponses:
    """OpenAPI responses of the project endpoints."""

    LIST: ClassVar[Responses] = {
        HTTPStatus.OK: ExampleResponse(ProjectExamples.LIST).to_openapi(),
    }
    CREATE: ClassVar[Responses] = {
        HTTPStatus.CREATED: ExampleResponse(ProjectExamples.READ).to_openapi(),
    }
    READ: ClassVar[Responses] = {
        HTTPStatus.OK: ExampleResponse(ProjectExamples.READ).to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(ProjectNotFoundError).to_openapi(),
    }
    DELETE: ClassVar[Responses] = {
        HTTPStatus.NO_CONTENT: EmptyResponse("Project deleted").to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(ProjectNotFoundError).to_openapi(),
        HTTPStatus.CONFLICT: ErrorResponse(TurnInProgressError).to_openapi(),
    }
