from http import HTTPStatus
from typing import ClassVar

from decks.agents.exceptions import DeckMissingError, ProjectNotFoundError, TurnInProgressError
from decks.api.deck.exceptions import (
    ElementIdNotFoundError,
    InvalidElementChangeError,
    NothingToRedoError,
    NothingToUndoError,
    StaleDeckRevisionError,
)
from decks.api.deck.openapi.examples import DeckExamples
from decks.api.openapi import ErrorResponse, ExampleResponse, Responses
from decks.api.projects.exceptions import SlideIndexNotFoundError

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
    HISTORY: ClassVar[Responses] = {
        HTTPStatus.OK: ExampleResponse(DeckExamples.EDIT).to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(ProjectNotFoundError, DeckMissingError).to_openapi(),
        HTTPStatus.CONFLICT: ErrorResponse(
            NothingToUndoError, NothingToRedoError, TurnInProgressError
        ).to_openapi(),
    }
