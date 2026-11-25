from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from agents import Model, RunConfig

from decks.agents.agents.deck import build_deck_agent
from decks.agents.agents.interview import build_interview_agent
from decks.agents.catalog import SlideCatalog
from decks.agents.context import ProjectContext
from decks.agents.models import StreamEvent
from decks.agents.repos import ProjectLocks, ProjectRepositories, Repos
from decks.agents.runner import ProjectRunner
from decks.models.plan import ContentBlock, Plan, SlideDraft


@pytest.fixture
def repos(tmp_path: Path) -> Repos:
    """Repositories of a new project 'demo' under a temp folder."""
    return ProjectRepositories(tmp_path, ProjectLocks()).create("demo", "Demo")


@pytest.fixture
def approved_plan() -> Plan:
    """A complete, approved plan with two slides of kind content."""
    slides = [
        SlideDraft(
            id=f"p{i}",
            kind="content",
            purpose="explain",
            title=f"Slide {i}",
            content=ContentBlock(points=["Revenue grew 42%"]),
        )
        for i in (1, 2)
    ]
    return Plan(approved=True, meta={"audience": "board"}, slides=slides)


def make_context(repos: Repos, model: Model | None = None) -> ProjectContext:
    """Create a context whose LLM calls go to ``model``."""
    return ProjectContext.create(repos, run_config=RunConfig(model=model, tracing_disabled=True))


def make_runner(repositories: ProjectRepositories, run_config: RunConfig) -> ProjectRunner:
    """Create a runner whose LLM calls use ``run_config``."""
    return ProjectRunner(
        repositories,
        build_interview_agent(SlideCatalog().prompt),
        build_deck_agent(),
        run_config=run_config,
    )


def stream_turn(runner: ProjectRunner, project_id: str, query: str) -> AsyncIterator[StreamEvent]:
    """Run one turn of ``project_id`` with a new context and return the event stream."""
    repos = runner._repositories.for_project(project_id)
    return runner.run(query, make_context(repos))
