from pathlib import Path

import pytest
from agents import RunConfig
from agents.testing import ScriptedModel, assistant_message, function_call

from decks.agents.exceptions import ProjectNotFoundError
from decks.agents.models import StreamEvent
from decks.agents.repos import ProjectLocks, ProjectRepositories
from decks.agents.runner import ProjectRunner
from tests.agents.conftest import make_runner, stream_turn


def _runner(tmp_path: Path, model: ScriptedModel) -> ProjectRunner:
    repositories = ProjectRepositories(tmp_path, ProjectLocks())
    repositories.create("demo", "Demo")
    config = RunConfig(model=model, tracing_disabled=True)
    return make_runner(repositories, config)


async def _collect(runner: ProjectRunner, project_id: str, query: str) -> list[StreamEvent]:
    return [event async for event in stream_turn(runner, project_id, query)]


async def test_run_streams_events_and_saves_chat(tmp_path: Path) -> None:
    """A turn yields run_started, tool events, the reply as a token, and done."""
    model = ScriptedModel(
        [
            [function_call("set_meta", {"keys": ["audience"], "values": ["board"]}, call_id="c2")],
            [assistant_message("Noted. How many slides?")],
        ]
    )
    runner = _runner(tmp_path, model)
    events = await _collect(runner, "demo", "deck for the board")
    types = [e.type for e in events]
    assert types[0] == "run_started"
    assert "plan_updated" in types
    assert types[-1] == "done"
    tokens = [e.text for e in events if e.type == "token"]
    assert "How many slides?" in "".join(tokens)
    assert len(await runner._repositories.for_project("demo").chat.get_items()) > 0


def test_unknown_project_is_rejected_before_the_turn(tmp_path: Path) -> None:
    """The caller resolves the project first, so an unknown project raises before a turn."""
    runner = _runner(tmp_path, ScriptedModel([]))
    with pytest.raises(ProjectNotFoundError):
        runner._repositories.for_project("nope")


def test_agent_is_chosen_by_phase(tmp_path: Path) -> None:
    """The interviewer owns the phases before approval; the deck agent owns the rest."""
    runner = _runner(tmp_path, ScriptedModel([]))
    assert runner.agent_for("interviewing").name == "interview"
    assert runner.agent_for("review").name == "interview"
    assert runner.agent_for("approved").name == "deck"
    assert runner.agent_for("generated").name == "deck"
