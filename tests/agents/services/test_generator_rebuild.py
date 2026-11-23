import json

import pytest
from agents.testing import ScriptedModel, assistant_message

from decks.agents.repos import Repos
from decks.models.plan import Plan
from decks.models.theme import THEMES
from tests.agents.conftest import make_context


def _content(title: str) -> list:
    spec = {"type": "content", "title": title, "body": ["Revenue grew 42%"]}
    return [assistant_message(json.dumps(spec))]


async def _built(repos: Repos, plan: Plan) -> int:
    """Generate a deck for ``plan`` and return its revision."""
    repos.plan.save(plan)
    model = ScriptedModel([_content(s.title) for s in plan.slides])
    report = await make_context(repos, model).generator.generate()
    return report.revision


async def test_removed_slide_is_dropped(repos: Repos, approved_plan: Plan) -> None:
    """Removing a plan slide rebuilds the deck without it, with no LLM call."""
    revision = await _built(repos, approved_plan)
    repos.plan.save(approved_plan.model_copy(update={"slides": approved_plan.slides[1:]}))
    model = ScriptedModel([])
    report = await make_context(repos, model).generator.generate()
    deck = repos.deck.load()
    assert deck is not None
    assert model.calls == ()
    assert (report.built, report.revision) == (0, revision + 1)
    assert [s.id for s in deck.slides] == ["p2"]
    assert deck.slides[0].elements[0].id == "s1e1"
    assert list(repos.project.load_state().built) == ["p2"]


async def test_reordered_slides_follow_plan(repos: Repos, approved_plan: Plan) -> None:
    """Reordering plan slides reorders the deck and renumbers element ids."""
    revision = await _built(repos, approved_plan)
    repos.plan.save(approved_plan.model_copy(update={"slides": approved_plan.slides[::-1]}))
    model = ScriptedModel([])
    report = await make_context(repos, model).generator.generate()
    deck = repos.deck.load()
    assert deck is not None
    assert model.calls == ()
    assert report.revision == revision + 1
    assert [s.id for s in deck.slides] == ["p2", "p1"]
    assert deck.slides[0].elements[0].id == "s1e1"
    assert deck.slides[1].elements[0].id == "s2e1"


async def test_theme_change_updates_palette(repos: Repos, approved_plan: Plan) -> None:
    """A theme change rebuilds the deck with the new palette and no refill."""
    revision = await _built(repos, approved_plan)
    repos.plan.save(approved_plan.model_copy(update={"theme": "orange"}))
    model = ScriptedModel([])
    report = await make_context(repos, model).generator.generate()
    deck = repos.deck.load()
    assert deck is not None
    assert model.calls == ()
    assert report.revision == revision + 1
    assert (deck.theme, deck.palette) == ("orange", THEMES["orange"])


@pytest.mark.parametrize("runs", [1, 2])
async def test_unchanged_plan_keeps_revision(repos: Repos, approved_plan: Plan, runs: int) -> None:
    """With the plan unchanged, generate builds nothing and keeps the revision."""
    revision = await _built(repos, approved_plan)
    for _ in range(runs):
        model = ScriptedModel([])
        report = await make_context(repos, model).generator.generate()
        assert (report.built, report.revision) == (0, revision)
        assert model.calls == ()
