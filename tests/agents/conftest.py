from pathlib import Path

import pytest
from agents import RunConfig
from agents.testing import ScriptedModel

from decks.agents.context import ProjectContext
from decks.agents.repos import ProjectLocks, ProjectRepositories, Repos
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


def make_context(repos: Repos, model: ScriptedModel) -> ProjectContext:
    """Create a context whose LLM calls go to ``model``."""
    return ProjectContext.create(repos, run_config=RunConfig(model=model, tracing_disabled=True))
