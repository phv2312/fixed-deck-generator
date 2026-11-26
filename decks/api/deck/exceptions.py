from dataclasses import dataclass
from http import HTTPStatus

from decks.exceptions import AppError


@dataclass(eq=False)
class DeckApiError(AppError):
    """Base class of the errors of the deck endpoints."""


@dataclass(eq=False)
class ElementIdNotFoundError(DeckApiError):
    """Raised when a slide has no element with the given id."""

    TEMPLATE = "slide {index} has no element {element_id}"
    STATUS_CODE = HTTPStatus.NOT_FOUND
    index: int
    element_id: str


@dataclass(eq=False)
class InvalidElementChangeError(DeckApiError):
    """Raised when an edit does not fit the element: unknown field, bad value, not allowed."""

    TEMPLATE = "element {element_id} cannot take this change: {reason}"
    STATUS_CODE = HTTPStatus.UNPROCESSABLE_ENTITY
    element_id: str
    reason: str


@dataclass(eq=False)
class StaleDeckRevisionError(DeckApiError):
    """Raised when the client edits an older revision of the deck than the saved one."""

    TEMPLATE = "the deck is at revision {current}, not {given}"
    STATUS_CODE = HTTPStatus.CONFLICT
    given: int
    current: int


@dataclass(eq=False)
class NothingToUndoError(DeckApiError):
    """Raised when there is no older deck to return to."""

    TEMPLATE = "there is nothing to undo"
    STATUS_CODE = HTTPStatus.CONFLICT


@dataclass(eq=False)
class NothingToRedoError(DeckApiError):
    """Raised when there is no undone deck to bring back."""

    TEMPLATE = "there is nothing to redo"
    STATUS_CODE = HTTPStatus.CONFLICT
