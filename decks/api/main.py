from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from decks.api.errors import ErrorHandlers
from decks.api.log_setup import LogSetup
from decks.api.middlewares import Middlewares
from decks.api.openapi import API_DESCRIPTION, DEFAULT_RESPONSES, RouteIds
from decks.api.routers import create_api_router
from decks.container import Container
from decks.settings import Settings


def create_app(*, settings: Settings | None = None) -> FastAPI:
    """Create the HTTP application. Run it: ``uvicorn decks.api.main:create_app --factory``."""
    settings = settings if settings is not None else Settings()
    LogSetup(json_logs=settings.json_logs).configure()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        async with Container(settings) as container:
            app.state.container = container
            yield

    app = FastAPI(
        title=settings.title,
        description=API_DESCRIPTION,
        responses=DEFAULT_RESPONSES,
        generate_unique_id_function=RouteIds.generate,
        lifespan=lifespan,
    )
    Middlewares(settings).install(app)
    ErrorHandlers().install(app)
    app.include_router(create_api_router())
    return app
