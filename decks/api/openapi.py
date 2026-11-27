from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Any, Final

from fastapi.routing import APIRoute
from pydantic import BaseModel

from decks.api.errors import ErrorBody, ErrorDetail
from decks.exceptions import AppError

type Responses = dict[int | str, dict[str, Any]]

API_DESCRIPTION: Final[str] = (Path(__file__).parent / "docs" / "description.md").read_text()


@dataclass(frozen=True)
class RouteDoc:
    """Swagger text of one endpoint."""

    summary: str
    description: str


class ExampleResponse:
    """A response with one JSON example that comes from a response model."""

    def __init__(self, example: BaseModel, *, description: str = "Successful response") -> None:
        self._example = example
        self._description = description

    def to_openapi(self) -> dict[str, Any]:
        """Return the OpenAPI response object."""
        return {
            "description": self._description,
            "content": {"application/json": {"example": self._example.model_dump(mode="json")}},
        }


class MultipleExamples:
    """A response with several named JSON examples."""

    def __init__(self, examples: dict[str, BaseModel], *, description: str) -> None:
        self._examples = examples
        self._description = description

    def to_openapi(self) -> dict[str, Any]:
        """Return the OpenAPI response object."""
        return {
            "description": self._description,
            "content": {
                "application/json": {
                    "examples": {
                        name: {"value": model.model_dump(mode="json")}
                        for name, model in self._examples.items()
                    }
                }
            },
        }


class ErrorResponse:
    """An error response. Each error class gives one example from its ``TEMPLATE``."""

    def __init__(self, *errors: type[AppError]) -> None:
        self._errors = errors

    def to_openapi(self) -> dict[str, Any]:
        """Return the OpenAPI response object."""
        status = self._errors[0].STATUS_CODE
        examples = {
            error.__name__: {
                "value": ErrorBody(code=error.__name__, message=error.TEMPLATE).model_dump(
                    mode="json"
                )
            }
            for error in self._errors
        }
        return {
            "model": ErrorBody,
            "description": status.phrase,
            "content": {"application/json": {"examples": examples}},
        }


class EmptyResponse:
    """A response without a body, for example 204."""

    def __init__(self, description: str = "No content") -> None:
        self._description = description

    def to_openapi(self) -> dict[str, Any]:
        """Return the OpenAPI response object."""
        return {"description": self._description}


class StreamExample:
    """A ``text/event-stream`` response with one example text."""

    def __init__(self, text: str, *, description: str = "Event stream") -> None:
        self._text = text
        self._description = description

    def to_openapi(self) -> dict[str, Any]:
        """Return the OpenAPI response object."""
        return {
            "description": self._description,
            "content": {"text/event-stream": {"example": self._text}},
        }


class RouteIds:
    """Make stable operation ids from the tag and the function name."""

    @staticmethod
    def generate(route: APIRoute) -> str:
        """Return ``<tag>_<function name>`` in lower case."""
        tag = route.tags[0] if route.tags else "api"
        return f"{str(tag).lower()}_{route.name}"


DEFAULT_RESPONSES: Final[Responses] = {
    HTTPStatus.UNPROCESSABLE_ENTITY: ExampleResponse(
        ErrorBody(
            code="ValidationError",
            message="request is not valid",
            details=[ErrorDetail(loc=["body", "name"], msg="Field required")],
        ),
        description="Validation error",
    ).to_openapi(),
    HTTPStatus.INTERNAL_SERVER_ERROR: ExampleResponse(
        ErrorBody(code="InternalServerError", message="internal server error"),
        description="Server error",
    ).to_openapi(),
}
