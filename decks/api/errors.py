from http import HTTPStatus

import structlog
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from decks.exceptions import AppError

logger = structlog.get_logger()

GENERIC_MESSAGE = "internal server error"


class ErrorDetail(BaseModel):
    """One problem of a request that failed validation."""

    loc: list[str | int] = Field(description="Path to the invalid value in the request.")
    msg: str = Field(description="What is wrong with the value.")


class ErrorBody(BaseModel):
    """Body of each error response. See the API contract."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(description="Stable error name. Clients branch on it.")
    message: str = Field(description="English text for a developer. Do not show it to a user.")
    details: list[ErrorDetail] | None = Field(
        default=None, description="Validation problems, or null."
    )


class ErrorHandlers:
    """Turn each exception into the error body of the API contract."""

    def install(self, app: FastAPI) -> None:
        """Register the handlers on ``app``."""
        app.add_exception_handler(AppError, self._app_error)
        app.add_exception_handler(RequestValidationError, self._validation_error)
        app.add_exception_handler(StarletteHTTPException, self._http_error)
        app.add_exception_handler(Exception, self._unhandled)

    def _app_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Answer an ``AppError`` with its status and its class name as the code."""
        if not isinstance(exc, AppError):
            raise TypeError(type(exc).__name__)
        status = exc.STATUS_CODE
        if status >= HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.error("request_failed", code=type(exc).__name__, exc_info=exc)
            return self._respond(status, type(exc).__name__, GENERIC_MESSAGE)
        return self._respond(status, type(exc).__name__, str(exc))

    def _validation_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Answer a failed validation with 422 and the ``loc`` and ``msg`` of each problem."""
        if not isinstance(exc, RequestValidationError):
            raise TypeError(type(exc).__name__)
        details = [
            ErrorDetail(loc=list(error["loc"]), msg=str(error["msg"])) for error in exc.errors()
        ]
        return self._respond(
            HTTPStatus.UNPROCESSABLE_ENTITY, "ValidationError", "request is not valid", details
        )

    def _http_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Answer a Starlette ``HTTPException``, for example an unknown path or a bad method."""
        if not isinstance(exc, StarletteHTTPException):
            raise TypeError(type(exc).__name__)
        status = HTTPStatus(exc.status_code)
        code = status.phrase.replace(" ", "").replace("-", "")
        message = GENERIC_MESSAGE if status >= HTTPStatus.INTERNAL_SERVER_ERROR else str(exc.detail)
        return self._respond(status, code, message)

    def _unhandled(self, request: Request, exc: Exception) -> JSONResponse:
        """Answer any other exception with 500 and a generic message."""
        logger.error("request_failed", code="InternalServerError", exc_info=exc)
        return self._respond(
            HTTPStatus.INTERNAL_SERVER_ERROR, "InternalServerError", GENERIC_MESSAGE
        )

    @staticmethod
    def _respond(
        status: HTTPStatus, code: str, message: str, details: list[ErrorDetail] | None = None
    ) -> JSONResponse:
        """Build the JSON response of one error."""
        body = ErrorBody(code=code, message=message, details=details)
        return JSONResponse(status_code=status, content=jsonable_encoder(body))
