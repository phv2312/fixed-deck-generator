from dataclasses import dataclass
from http import HTTPStatus

from decks.exceptions import AppError


@dataclass(eq=False)
class ChatApiError(AppError):
    """Base class of the errors of the chat endpoints."""


@dataclass(eq=False)
class ToolCallNotFoundError(ChatApiError):
    """Raised when the chat of a project has no tool call with the given id."""

    TEMPLATE = "project {project_id} has no tool call {call_id}"
    STATUS_CODE = HTTPStatus.NOT_FOUND
    project_id: str
    call_id: str


@dataclass(eq=False)
class ToolFieldNotFoundError(ChatApiError):
    """Raised when a tool call has no field with the given key."""

    TEMPLATE = "tool call {call_id} has no field {key}"
    STATUS_CODE = HTTPStatus.NOT_FOUND
    call_id: str
    key: str
