from http import HTTPStatus
from typing import ClassVar

from decks.agents.exceptions import DeckMissingError, ProjectNotFoundError, TurnInProgressError
from decks.api.openapi import EmptyResponse, ErrorResponse, ExampleResponse, Responses
from decks.api.projects.exceptions import SlideIndexNotFoundError
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
    SLIDE_HTML: ClassVar[Responses] = {
        HTTPStatus.OK: {
            "description": "HTML page of the slide",
            "content": {"text/html": {"example": "<!doctype html><html>…</html>"}},
        },
        HTTPStatus.NOT_FOUND: ErrorResponse(
            ProjectNotFoundError, DeckMissingError, SlideIndexNotFoundError
        ).to_openapi(),
    }
