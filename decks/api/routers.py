from fastapi import APIRouter

from decks.api.chat import router as chat
from decks.api.deck import router as deck
from decks.api.plan import router as plan
from decks.api.projects import router as projects


def create_api_router() -> APIRouter:
    """Mount each API version under ``/api``."""
    router = APIRouter(prefix="/api")
    router.include_router(create_v1_router(), prefix="/v1")
    return router


def create_v1_router() -> APIRouter:
    """Mount the feature routers of version 1."""
    router = APIRouter()
    router.include_router(projects.router, prefix="/projects", tags=["Projects"])
    router.include_router(chat.router, prefix="/projects", tags=["Chat"])
    router.include_router(plan.router, prefix="/projects", tags=["Plan"])
    router.include_router(deck.router, prefix="/projects", tags=["Deck"])
    return router
