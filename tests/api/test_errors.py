from fastapi import FastAPI
from httpx import AsyncClient

from decks.exceptions import AppError


async def test_unknown_path_has_error_body(client: AsyncClient) -> None:
    """Test that an unknown path returns the error body with code ``NotFound``."""
    response = await client.get("/api/v1/nothing")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "NotFound"
    assert body["details"] is None


async def test_validation_error_lists_details(client: AsyncClient) -> None:
    """Test that a bad body returns 422, ``ValidationError``, and ``loc`` with ``msg``."""
    response = await client.post("/api/v1/projects", json={"name": "x" * 200})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "ValidationError"
    assert body["details"][0]["loc"] == ["body", "name"]
    assert body["details"][0]["msg"]


async def test_server_error_message_is_generic(app: FastAPI, client: AsyncClient) -> None:
    """Test that an ``AppError`` with a 500 status hides its own message."""

    class BoomError(AppError):
        TEMPLATE = "secret internal detail"

    @app.get("/boom")
    async def boom() -> None:
        raise BoomError

    response = await client.get("/boom")
    assert response.status_code == 500
    assert response.json()["code"] == "BoomError"
    assert "secret" not in response.json()["message"]


async def test_request_id_is_echoed(client: AsyncClient) -> None:
    """Test that a valid ``X-Request-ID`` comes back unchanged."""
    response = await client.get("/api/v1/projects", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


async def test_request_id_is_created_when_missing_or_invalid(client: AsyncClient) -> None:
    """Test that the server makes a new id when the client sends none or a bad one."""
    missing = await client.get("/api/v1/projects")
    invalid = await client.get("/api/v1/projects", headers={"X-Request-ID": "bad value!"})
    assert missing.headers["X-Request-ID"]
    assert invalid.headers["X-Request-ID"] != "bad value!"


async def test_cors_allows_the_vite_origin(client: AsyncClient) -> None:
    """Test that the dev origin of the frontend may call the API."""
    response = await client.get("/api/v1/projects", headers={"Origin": "http://localhost:5173"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
