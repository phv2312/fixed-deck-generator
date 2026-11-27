from collections.abc import AsyncGenerator, Awaitable, Callable
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from decks.api.main import create_app
from decks.container import Container
from decks.models.elements import Text
from decks.models.slides import Deck, Slide
from decks.models.theme import FONT, THEMES
from decks.settings import Settings


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Settings:
    """Settings with fake Azure variables and a temporary project root."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "v1")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt")
    monkeypatch.setenv("DECKS_PROJECTS_ROOT", str(tmp_path / "projects"))
    return Settings(_env_file=None)


@pytest.fixture
async def app(settings: Settings) -> AsyncGenerator[FastAPI]:
    """Return an app with an open test Container."""
    app = create_app(settings=settings)
    async with Container(settings) as container:
        app.state.container = container
        yield app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient]:
    """Return an HTTP client for ``app``."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http


@pytest.fixture
def deck() -> Deck:
    """A deck with two slides, each with one text."""
    slides = [
        Slide(
            id=f"s{i}",
            family="body",
            kind="content",
            elements=[Text(id=f"s{i}e1", x=10, y=10, w=300, h=40, text=f"Slide {i}")],
        )
        for i in (1, 2)
    ]
    return Deck(revision=1, theme="green", palette=THEMES["green"], font=FONT, slides=slides)


@pytest.fixture
def write_chat(app: FastAPI) -> Callable[[str, list[dict[str, object]]], Awaitable[None]]:
    """Return a function that appends items to the chat of a project."""
    container: Container = app.state.container

    async def write(project_id: str, items: list[dict[str, object]]) -> None:
        await container.repositories.for_project(project_id).chat.add_items(cast(Any, items))

    return write
