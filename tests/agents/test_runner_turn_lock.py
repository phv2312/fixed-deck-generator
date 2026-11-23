from pathlib import Path

import pytest
from agents import RunConfig
from agents.testing import ScriptedModel, assistant_message

from decks.agents.models import StreamEvent
from decks.agents.repos import ProjectLocks, ProjectRepositories
from decks.agents.runner import ProjectRunner


@pytest.fixture
def repositories(tmp_path: Path) -> ProjectRepositories:
    """Repositories with projects 'a' and 'b'."""
    repositories = ProjectRepositories(tmp_path, ProjectLocks())
    repositories.create("a", "A")
    repositories.create("b", "B")
    return repositories


def _runner(repositories: ProjectRepositories, steps: list) -> ProjectRunner:
    config = RunConfig(model=ScriptedModel(steps), tracing_disabled=True)
    return ProjectRunner(repositories, run_config=config)


async def _types(runner: ProjectRunner, project_id: str) -> list[StreamEvent]:
    return [event async for event in runner.run(project_id, "hi")]


async def test_busy_project_gets_error_event(repositories: ProjectRepositories) -> None:
    """A turn on a project whose turn lock is held ends with [error, done]."""
    runner = _runner(repositories, [])
    async with repositories.for_project("a").turn_lock:
        events = await _types(runner, "a")
    assert [e.type for e in events] == ["error", "done"]
    assert events[0].code == "TurnInProgressError"


async def test_other_project_is_not_blocked(repositories: ProjectRepositories) -> None:
    """A held lock on project 'a' does not block project 'b'."""
    runner = _runner(repositories, [[assistant_message("ok")]])
    async with repositories.for_project("a").turn_lock:
        events = await _types(runner, "b")
    assert events[0].type == "run_started"
    assert events[-1].type == "done"


async def test_lock_released_after_stream(repositories: ProjectRepositories) -> None:
    """The lock is free after a normal turn, so the next turn runs."""
    runner = _runner(repositories, [[assistant_message("one")], [assistant_message("two")]])
    await _types(runner, "a")
    assert not repositories.for_project("a").turn_lock.locked()
    events = await _types(runner, "a")
    assert "error" not in [e.type for e in events]


async def test_lock_released_after_error(repositories: ProjectRepositories) -> None:
    """A failing turn still frees the lock."""
    runner = _runner(repositories, [])
    events = await _types(runner, "a")
    assert "error" in [e.type for e in events]
    assert not repositories.for_project("a").turn_lock.locked()


async def test_lock_released_when_consumer_stops(repositories: ProjectRepositories) -> None:
    """Closing the stream early cancels the turn and frees the lock."""
    runner = _runner(repositories, [[assistant_message("one")]])
    stream = runner.run("a", "hi")
    await anext(stream)
    await stream.aclose()
    assert not repositories.for_project("a").turn_lock.locked()
