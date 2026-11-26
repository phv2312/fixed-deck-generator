from http import HTTPStatus
from typing import ClassVar

from decks.agents.exceptions import DeckMissingError, ProjectNotFoundError, TurnInProgressError
from decks.api.deck.exceptions import (
    ElementIdNotFoundError,
    InvalidElementChangeError,
    NothingToRedoError,
    NothingToUndoError,
    SlideIndexNotFoundError,
    StaleDeckRevisionError,
)
from decks.api.deck.openapi.examples import DeckExamples
from decks.api.openapi import ErrorResponse, ExampleResponse, Responses

NOT_FOUND = ErrorResponse(
    ProjectNotFoundError, DeckMissingError, SlideIndexNotFoundError, ElementIdNotFoundError
).to_openapi()
UNPROCESSABLE = ErrorResponse(InvalidElementChangeError).to_openapi()
EDIT_CONFLICT = ErrorResponse(StaleDeckRevisionError, TurnInProgressError).to_openapi()


class DeckResponses:
    """OpenAPI responses of the deck endpoints."""

    READ: ClassVar[Responses] = {
        HTTPStatus.OK: ExampleResponse(DeckExamples.DECK).to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(ProjectNotFoundError, DeckMissingError).to_openapi(),
    }
    EDIT: ClassVar[Responses] = {
        HTTPStatus.OK: ExampleResponse(DeckExamples.EDIT).to_openapi(),
        HTTPStatus.NOT_FOUND: NOT_FOUND,
        HTTPStatus.CONFLICT: EDIT_CONFLICT,
        HTTPStatus.UNPROCESSABLE_ENTITY: UNPROCESSABLE,
    }
    CREATE: ClassVar[Responses] = {
        HTTPStatus.CREATED: ExampleResponse(DeckExamples.EDIT).to_openapi(),
        HTTPStatus.NOT_FOUND: NOT_FOUND,
        HTTPStatus.CONFLICT: EDIT_CONFLICT,
        HTTPStatus.UNPROCESSABLE_ENTITY: UNPROCESSABLE,
    }
    SLIDE_HTML: ClassVar[Responses] = {
        HTTPStatus.OK: {
            "description": "HTML page of the slide",
            "content": {"text/html": {"example": "<!doctype html><html>…</html>"}},
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "The client already has this revision of the slide"
        },
        HTTPStatus.NOT_FOUND: ErrorResponse(
            ProjectNotFoundError, DeckMissingError, SlideIndexNotFoundError
        ).to_openapi(),
    }
    HISTORY: ClassVar[Responses] = {
        HTTPStatus.OK: ExampleResponse(DeckExamples.EDIT).to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(ProjectNotFoundError, DeckMissingError).to_openapi(),
        HTTPStatus.CONFLICT: ErrorResponse(
            NothingToUndoError, NothingToRedoError, TurnInProgressError
        ).to_openapi(),
    }
