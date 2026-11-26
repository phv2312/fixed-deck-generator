from http import HTTPStatus
from typing import ClassVar

from decks.agents.exceptions import ProjectNotFoundError, TurnInProgressError
from decks.api.chat.exceptions import ToolCallNotFoundError, ToolFieldNotFoundError
from decks.api.chat.openapi.examples import ChatExamples
from decks.api.openapi import ErrorResponse, ExampleResponse, Responses, StreamExample


class ChatResponses:
    """OpenAPI responses of the chat endpoints."""

    SEND: ClassVar[Responses] = {
        HTTPStatus.OK: StreamExample(ChatExamples.STREAM, description="Event stream").to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(ProjectNotFoundError).to_openapi(),
        HTTPStatus.CONFLICT: ErrorResponse(TurnInProgressError).to_openapi(),
    }
    HISTORY: ClassVar[Responses] = {
        HTTPStatus.OK: ExampleResponse(ChatExamples.HISTORY).to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(ProjectNotFoundError).to_openapi(),
    }
    FIELD: ClassVar[Responses] = {
        HTTPStatus.OK: {
            "description": "Full value of the field",
            "content": {
                "text/plain": {"example": "Who is the deck for?"},
                "application/json": {"example": {"slides": []}},
                "image/svg+xml": {"example": "<svg xmlns='http://www.w3.org/2000/svg'/>"},
            },
        },
        HTTPStatus.NOT_FOUND: ErrorResponse(
            ProjectNotFoundError, ToolCallNotFoundError, ToolFieldNotFoundError
        ).to_openapi(),
    }
