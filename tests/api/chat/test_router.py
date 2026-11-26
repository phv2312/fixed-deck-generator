import inspect
from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from fastapi.routing import APIRoute
from httpx import AsyncClient

from decks.agents.models import Done, QuestionEvent, RunStarted, Token
from decks.api.chat import router as chat
from decks.container import Container
from tests.api.chat.conftest import QUESTION_ARGS, SVG, ScriptedRunner, assistant, call, output

WriteChat = Callable[[str, list[dict[str, object]]], Awaitable[None]]


def parse_sse(text: str) -> list[tuple[str, str]]:
    """Split an event stream into ``(event, data)`` pairs."""
    pairs = []
    for frame in filter(None, text.split("\n\n")):
        event_line, data_line = frame.split("\n")
        pairs.append((event_line.removeprefix("event: "), data_line.removeprefix("data: ")))
    return pairs


async def test_send_streams_one_sse_frame_per_event(
    client: AsyncClient, project: str, runner: ScriptedRunner
) -> None:
    """Test that the answer is an event stream that ends with ``done``."""
    runner.events = [
        RunStarted(agent="interview", phase="draft"),
        Token(text="Hello"),
        QuestionEvent(question="Who?", options=["A", "B"]),
        Done(),
    ]
    response = await client.post(f"/api/v1/projects/{project}/chat", json={"message": " hi "})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-cache"
    assert response.headers["x-accel-buffering"] == "no"
    assert response.headers["x-request-id"]
    frames = parse_sse(response.text)
    assert [name for name, _ in frames] == ["run_started", "token", "question", "done"]
    assert frames[1][1] == '{"type":"token","text":"Hello"}'
    assert runner.queries == ["hi"]


async def test_send_to_unknown_project_is_404(client: AsyncClient, runner: ScriptedRunner) -> None:
    """Test that an unknown project gives ``ProjectNotFoundError``, not a stream."""
    response = await client.post("/api/v1/projects/missing/chat", json={"message": "hi"})
    assert response.status_code == 404
    assert response.json()["code"] == "ProjectNotFoundError"


async def test_send_while_a_turn_runs_is_409(
    client: AsyncClient, app: FastAPI, project: str, runner: ScriptedRunner
) -> None:
    """Test that a second turn gets ``TurnInProgressError`` before any event."""
    container: Container = app.state.container
    async with container.repositories.for_project(project).turn_lock:
        response = await client.post(f"/api/v1/projects/{project}/chat", json={"message": "hi"})
    assert response.status_code == 409
    assert response.json()["code"] == "TurnInProgressError"
    assert runner.queries == []


async def test_send_rejects_an_empty_message(client: AsyncClient, project: str) -> None:
    """Test that a blank message is a validation error."""
    response = await client.post(f"/api/v1/projects/{project}/chat", json={"message": "   "})
    assert response.status_code == 422


async def test_history_of_a_new_project_is_empty(client: AsyncClient, project: str) -> None:
    """Test that a project without a chat has no messages and no question."""
    response = await client.get(f"/api/v1/projects/{project}/chat")
    assert response.json() == {"messages": [], "running": False, "pending_question": None}


async def test_history_lists_messages_tool_calls_and_the_pending_question(
    client: AsyncClient, project: str, write_chat: WriteChat
) -> None:
    """Test the shape of the history: messages, calls with field urls, and the open question."""
    await write_chat(
        project,
        [
            {"role": "user", "content": "Make a deck"},
            call("c1", "make_picture", {"svg": SVG}),
            output("c1", "saved"),
            call("c2", "ask_user_question", QUESTION_ARGS),
            output("c2", "question='Who is the deck for?'"),
        ],
    )
    body = (await client.get(f"/api/v1/projects/{project}/chat")).json()
    assert [m["role"] for m in body["messages"]] == ["user", "assistant"]
    tools = body["messages"][1]["tool_calls"]
    assert [(t["id"], t["status"], t["duration_ms"]) for t in tools] == [
        ("c1", "done", None),
        ("c2", "done", None),
    ]
    svg_field = tools[0]["fields"][0]
    assert svg_field == {
        "key": "input.svg",
        "size": len(SVG.encode()),
        "mime": "image/svg+xml",
        "preview": SVG[:200],
        "url": f"/api/v1/projects/{project}/tool-calls/c1/fields/input.svg",
    }
    question = body["pending_question"]
    assert question["question"] == "Who is the deck for?"
    assert question["options"] == ["Students", "ML engineers"]
    assert body["messages"][1]["question"] == question


async def test_history_clears_the_question_after_the_answer(
    client: AsyncClient, project: str, write_chat: WriteChat
) -> None:
    """Test that an answer becomes the next user message and the question is no longer pending."""
    await write_chat(
        project,
        [
            {"role": "user", "content": "Make a deck"},
            call("c1", "ask_user_question", QUESTION_ARGS),
            output("c1", "q"),
            {"role": "user", "content": "Students"},
            assistant("Thanks."),
        ],
    )
    body = (await client.get(f"/api/v1/projects/{project}/chat")).json()
    assert [m["role"] for m in body["messages"]] == ["user", "assistant", "user", "assistant"]
    assert body["pending_question"] is None


async def test_history_marks_a_running_turn(
    client: AsyncClient, app: FastAPI, project: str, write_chat: WriteChat
) -> None:
    """Test that an unfinished call is ``running`` while the turn lock is held."""
    await write_chat(project, [{"role": "user", "content": "go"}, call("c1", "slow", {})])
    container: Container = app.state.container
    async with container.repositories.for_project(project).turn_lock:
        body = (await client.get(f"/api/v1/projects/{project}/chat")).json()
    assert body["running"] is True
    assert body["messages"][1]["tool_calls"][0]["status"] == "running"


async def test_field_returns_the_full_value_with_its_own_type(
    client: AsyncClient, project: str, write_chat: WriteChat
) -> None:
    """Test that a field is not cut, has its media type, and cannot run a script."""
    await write_chat(
        project,
        [{"role": "user", "content": "go"}, call("c1", "pic", {"svg": SVG}), output("c1", "ok")],
    )
    response = await client.get(f"/api/v1/projects/{project}/tool-calls/c1/fields/input.svg")
    assert response.status_code == 200
    assert response.text == SVG
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert "sandbox" in response.headers["content-security-policy"]
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "content-disposition" not in response.headers
    output_field = await client.get(f"/api/v1/projects/{project}/tool-calls/c1/fields/output")
    assert output_field.text == "ok"
    assert output_field.headers["content-type"].startswith("text/plain")


async def test_field_download_sets_a_file_name(
    client: AsyncClient, project: str, write_chat: WriteChat
) -> None:
    """Test that ``download=true`` adds an attachment header with the right extension."""
    await write_chat(project, [{"role": "user", "content": "go"}, call("c1", "pic", {"svg": SVG})])
    response = await client.get(
        f"/api/v1/projects/{project}/tool-calls/c1/fields/input.svg", params={"download": "true"}
    )
    assert response.headers["content-disposition"] == 'attachment; filename="c1-input.svg.svg"'


async def test_field_errors(client: AsyncClient, project: str, write_chat: WriteChat) -> None:
    """Test the 404 and 422 answers of the field endpoint."""
    await write_chat(project, [{"role": "user", "content": "go"}, call("c1", "pic", {"a": 1})])
    base = f"/api/v1/projects/{project}/tool-calls"
    missing_call = await client.get(f"{base}/nope/fields/output")
    assert (missing_call.status_code, missing_call.json()["code"]) == (404, "ToolCallNotFoundError")
    missing_field = await client.get(f"{base}/c1/fields/output")
    assert (missing_field.status_code, missing_field.json()["code"]) == (
        404,
        "ToolFieldNotFoundError",
    )
    assert (await client.get(f"{base}/c1/fields/bad key")).status_code == 422
    unknown_project = await client.get("/api/v1/projects/missing/tool-calls/c1/fields/output")
    assert unknown_project.json()["code"] == "ProjectNotFoundError"


def test_every_route_is_documented() -> None:
    """Test that each chat route has a summary, its own description, and responses."""
    for route in chat.router.routes:
        assert isinstance(route, APIRoute)
        docstring = inspect.cleandoc(route.endpoint.__doc__ or "")
        assert route.summary, route.path
        assert route.description, route.path
        assert route.description != docstring, route.path
        assert route.responses, route.path
