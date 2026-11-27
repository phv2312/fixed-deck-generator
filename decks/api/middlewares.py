import re
import time
from uuid import uuid4

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from decks.settings import Settings

logger = structlog.get_logger()

REQUEST_ID_HEADER = "X-Request-ID"
VALID_REQUEST_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")


class RequestIdMiddleware:
    """Read or create the request id, bind it for the logs, and return it in a header."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        request_id = self._pick(scope)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self._app(scope, receive, send_with_id)
        finally:
            structlog.contextvars.clear_contextvars()

    @staticmethod
    def _pick(scope: Scope) -> str:
        """Return the id that the client sent when it is valid, else a new id."""
        sent = dict(scope["headers"]).get(REQUEST_ID_HEADER.lower().encode(), b"").decode("latin-1")
        return sent if VALID_REQUEST_ID.fullmatch(sent) else uuid4().hex


class AccessLogMiddleware:
    """Write one ``request_finished`` event for each request."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        started = time.perf_counter()
        status = 500

        async def send_and_note(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self._app(scope, receive, send_and_note)
        finally:
            route = scope.get("route")
            logger.info(
                "request_finished",
                method=scope["method"],
                path=getattr(route, "path", "<unmatched>"),
                status=status,
                duration_ms=round((time.perf_counter() - started) * 1000, 1),
            )


class Middlewares:
    """Add the transport middlewares of the app."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def install(self, app: FastAPI) -> None:
        """Add the middlewares. The last one added is the outermost."""
        app.add_middleware(AccessLogMiddleware)
        app.add_middleware(RequestIdMiddleware)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self._settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=[REQUEST_ID_HEADER],
        )
