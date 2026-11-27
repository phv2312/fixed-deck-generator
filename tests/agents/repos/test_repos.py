from pathlib import Path

import pytest

from decks.agents.exceptions import ArtifactCorruptError, ProjectNotFoundError
from decks.agents.repos import ProjectLocks, ProjectRepositories, Repos
from decks.agents.repos.base import AtomicJsonStore
from decks.models.plan import Plan


def test_plan_round_trip(repos: Repos) -> None:
    """A saved plan loads back equal, and a new project has none."""
    assert repos.plan.load() is None
    plan = Plan(meta={"audience": "board"})
    repos.plan.save(plan)
    assert repos.plan.load() == plan


def test_state_defaults_to_draft(repos: Repos) -> None:
    """A new project starts in the draft phase."""
    assert repos.project.load_state().phase == "draft"


def test_unknown_project(tmp_path: Path) -> None:
    """Opening a project that does not exist raises a typed error."""
    with pytest.raises(ProjectNotFoundError) as info:
        ProjectRepositories(tmp_path, ProjectLocks()).for_project("nope")
    assert str(info.value) == "project nope does not exist"


def test_corrupt_artifact(tmp_path: Path) -> None:
    """A file that does not match the model raises ArtifactCorruptError."""
    path = tmp_path / "plan.json"
    path.write_text('{"revision": "x"}')
    with pytest.raises(ArtifactCorruptError):
        AtomicJsonStore(path).read_model(Plan)


def test_atomic_write_leaves_no_temp_file(tmp_path: Path) -> None:
    """After a write only the target file exists."""
    store = AtomicJsonStore(tmp_path / "a" / "plan.json")
    store.write_model(Plan())
    assert [p.name for p in (tmp_path / "a").iterdir()] == ["plan.json"]


async def test_chat_session(repos: Repos) -> None:
    """The chat repository follows the SDK Session contract."""
    chat = repos.chat
    await chat.add_items([{"role": "user", "content": "a"}, {"role": "user", "content": "b"}])
    assert len(await chat.get_items()) == 2
    assert await chat.get_items(limit=1) == [{"role": "user", "content": "b"}]
    assert await chat.pop_item() == {"role": "user", "content": "b"}
    await chat.clear_session()
    assert await chat.get_items() == []
    assert await chat.pop_item() is None


def test_lock_is_shared_per_project(tmp_path: Path) -> None:
    """The same project id gets the same lock."""
    locks = ProjectLocks()
    assert locks.get("a") is locks.get("a")
    assert locks.get("a") is not locks.get("b")


def test_ids_modified_at_and_delete(tmp_path: Path) -> None:
    """The repositories list the projects, report a change time, and delete a folder."""
    repositories = ProjectRepositories(tmp_path)
    repositories.create("b", "B")
    repositories.create("a", "A")
    (tmp_path / "not-a-project").mkdir()
    assert repositories.ids() == ["a", "b"]
    assert repositories.modified_at("a").tzinfo is not None
    repositories.delete("a")
    assert repositories.ids() == ["b"]
    with pytest.raises(ProjectNotFoundError):
        repositories.delete("a")
