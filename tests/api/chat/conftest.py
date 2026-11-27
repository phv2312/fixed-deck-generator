import json
from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from decks.agents import ProjectContext
from decks.agents.models import StreamEvent
from decks.api.chat.deps import get_runner

QUESTION_ARGS = {
    "question": "Who is the deck for?",
    "options": ["Students", "ML engineers"],
    "allow_multiple": False,
    "free_text": True,
}
SVG = "<svg xmlns='http://www.w3.org/2000/svg'>" + "<path d='M0 0'/>" * 50 + "</svg>"


class ScriptedRunner:
    """Stands in for ``ProjectRunner``: yields the given events and records the queries."""

    def __init__(self, events: list[StreamEvent]) -> None:
        self.events = events
        self.queries: list[str] = []

    async def run(self, query: str, context: ProjectContext) -> AsyncIterator[StreamEvent]:
        """Yield the scripted events."""
        self.queries.append(query)
        for event in self.events:
            yield event


def call(call_id: str, name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Return a function-call item as chat.json stores it."""
    return {
        "type": "function_call",
        "call_id": call_id,
        "name": name,
        "arguments": json.dumps(arguments),
        "id": f"fc_{call_id}",
    }


def output(call_id: str, text: str) -> dict[str, object]:
    """Return the output item of a function call."""
    return {"type": "function_call_output", "call_id": call_id, "output": text}


def assistant(text: str) -> dict[str, object]:
    """Return an assistant text item."""
    return {
        "type": "message",
        "role": "assistant",
        "id": "msg_1",
        "content": [{"type": "output_text", "text": text, "annotations": []}],
    }


@pytest.fixture
async def project(client: AsyncClient) -> str:
    """Create a project through the API and return its id."""
    response = await client.post("/api/v1/projects", json={"name": "Demo"})
    return response.json()["id"]


@pytest.fixture
def runner(app: FastAPI) -> ScriptedRunner:
    """Replace the runner of the app with a scripted one."""
    scripted = ScriptedRunner([])
    app.dependency_overrides[get_runner] = lambda: scripted
    return scripted
