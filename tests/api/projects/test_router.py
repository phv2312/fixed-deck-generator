import inspect

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from httpx import AsyncClient

from decks.api.projects import router as projects
from decks.api.projects.payloads import SLIDE_HTML_URL
from decks.container import Container
from decks.models.build import BuildState
from decks.models.slides import Deck


async def create(client: AsyncClient, name: str = "Q3 review") -> dict[str, object]:
    """Create a project through the API and return its body."""
    response = await client.post("/api/v1/projects", json={"name": name})
    assert response.status_code == 201
    return response.json()


def save_deck(app: FastAPI, project_id: str, deck: Deck) -> None:
    """Write a deck into the project folder."""
    container: Container = app.state.container
    container.repositories.for_project(project_id).deck.save(deck)


async def test_create_returns_a_draft_project(client: AsyncClient) -> None:
    """Test that a new project is a draft without a deck or a thumbnail."""
    body = await create(client, "  Q3 review  ")
    assert body["name"] == "Q3 review"
    assert body["phase"] == "draft"
    assert body["slide_count"] == 0
    assert body["thumbnail_url"] is None


async def test_read_returns_the_project(client: AsyncClient) -> None:
    """Test that a created project can be read by its id."""
    created = await create(client)
    response = await client.get(f"/api/v1/projects/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_read_unknown_project_is_404(client: AsyncClient) -> None:
    """Test that an unknown project gives ``ProjectNotFoundError``."""
    response = await client.get("/api/v1/projects/missing")
    assert response.status_code == 404
    assert response.json()["code"] == "ProjectNotFoundError"


@pytest.mark.parametrize("project_id", ["bad.id", "-start", "a" * 65])
async def test_invalid_project_id_is_422(client: AsyncClient, project_id: str) -> None:
    """Test that an id that is not a safe folder name is rejected."""
    response = await client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 422


async def test_list_has_items_total_and_pages(client: AsyncClient) -> None:
    """Test that the list pages with ``limit`` and ``offset`` and counts all projects."""
    for number in range(3):
        await create(client, f"Project {number}")
    response = await client.get("/api/v1/projects", params={"limit": 2, "offset": 0})
    rest = await client.get("/api/v1/projects", params={"limit": 2, "offset": 2})
    assert response.json()["total"] == 3
    assert len(response.json()["items"]) == 2
    assert len(rest.json()["items"]) == 1


async def test_list_sorts_by_last_change(client: AsyncClient, app: FastAPI) -> None:
    """Test that the project that changed last comes first."""
    first = await create(client, "First")
    second = await create(client, "Second")
    container: Container = app.state.container
    repos = container.repositories.for_project(str(first["id"]))
    repos.project.save_state(BuildState(phase="interviewing"))
    ids = [item["id"] for item in (await client.get("/api/v1/projects")).json()["items"]]
    assert ids == [first["id"], second["id"]]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"x": 1}])
async def test_list_rejects_bad_paging(client: AsyncClient, params: dict[str, int]) -> None:
    """Test that the page size has a maximum and unknown parameters fail."""
    response = await client.get("/api/v1/projects", params=params)
    assert response.status_code == 422


async def test_delete_removes_the_project(client: AsyncClient) -> None:
    """Test that a deleted project is gone."""
    created = await create(client)
    deleted = await client.delete(f"/api/v1/projects/{created['id']}")
    after = await client.get(f"/api/v1/projects/{created['id']}")
    assert deleted.status_code == 204
    assert after.status_code == 404


async def test_delete_is_blocked_while_a_turn_runs(client: AsyncClient, app: FastAPI) -> None:
    """Test that a running chat turn gives ``TurnInProgressError``."""
    created = await create(client)
    container: Container = app.state.container
    repos = container.repositories.for_project(str(created["id"]))
    async with repos.turn_lock:
        response = await client.delete(f"/api/v1/projects/{created['id']}")
    assert response.status_code == 409
    assert response.json()["code"] == "TurnInProgressError"


async def test_thumbnail_points_to_a_working_slide_page(
    client: AsyncClient, app: FastAPI, deck: Deck
) -> None:
    """Test that a project with a deck has a thumbnail URL that serves HTML."""
    created = await create(client)
    save_deck(app, str(created["id"]), deck)
    body = (await client.get(f"/api/v1/projects/{created['id']}")).json()
    assert body["slide_count"] == 2
    assert body["thumbnail_url"] == SLIDE_HTML_URL.format(project_id=created["id"], index=0)
    page = await client.get(body["thumbnail_url"])
    assert page.status_code == 200
    assert page.headers["content-type"].startswith("text/html")
    assert "Slide 1" in page.text
    assert "Slide 2" not in page.text


async def test_slide_html_without_deck_is_404(client: AsyncClient) -> None:
    """Test that a project without a deck gives ``DeckMissingError``."""
    created = await create(client)
    response = await client.get(f"/api/v1/projects/{created['id']}/deck/slides/0/html")
    assert response.status_code == 404
    assert response.json()["code"] == "DeckMissingError"


async def test_slide_html_out_of_range_is_404(
    client: AsyncClient, app: FastAPI, deck: Deck
) -> None:
    """Test that an index past the last slide gives ``SlideIndexNotFoundError``."""
    created = await create(client)
    save_deck(app, str(created["id"]), deck)
    response = await client.get(f"/api/v1/projects/{created['id']}/deck/slides/2/html")
    assert response.status_code == 404
    assert response.json()["code"] == "SlideIndexNotFoundError"


def test_every_route_is_documented() -> None:
    """Test that each project route has a summary, its own description, and responses."""
    for route in projects.router.routes:
        assert isinstance(route, APIRoute)
        docstring = inspect.cleandoc(route.endpoint.__doc__ or "")
        assert route.summary, route.path
        assert route.description, route.path
        assert route.description != docstring, route.path
        assert route.responses, route.path
