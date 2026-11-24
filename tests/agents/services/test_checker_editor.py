import json

import pytest
from agents.testing import ScriptedModel, assistant_message

from decks.agents.exceptions import ElementNotFoundError, StyleNotSupportedError
from decks.agents.models import StylePatch
from decks.agents.repos import Repos
from decks.models.elements import Shape, Text
from decks.models.plan import Plan
from decks.models.slides import Slide
from decks.text_metrics import TextMetrics
from tests.agents.conftest import make_context


def _slide(*elements: Text | Shape) -> Slide:
    return Slide(id="p1", family="layout", kind="content", elements=list(elements))


def test_fit_font_size_shrinks_to_scale() -> None:
    """The fitted size is a design-scale size no larger than the request."""
    size = TextMetrics().fit_font_size("word " * 30, 36, (300, 100)).size
    assert size < 36
    assert size in {12, 14, 16, 18, 22, 28}


async def _deck(repos: Repos, approved_plan: Plan) -> Repos:
    repos.plan.save(approved_plan.model_copy(update={"slides": approved_plan.slides[:1]}))
    spec = {"type": "content", "title": "One", "body": ["Revenue grew 42%"]}
    model = ScriptedModel([[assistant_message(json.dumps(spec))]])
    await make_context(repos, model).generator.generate()
    return repos


async def test_editor_style_and_text(repos: Repos, approved_plan: Plan) -> None:
    """Style edits persist, mark the slide edited and bump the revision."""
    await _deck(repos, approved_plan)
    editor = make_context(repos, ScriptedModel([])).editor
    view = editor.read_slide("p1")
    text_id = next(e.id for e in view.elements if e.type == "text")
    change = editor.update_element("p1", text_id, StylePatch(bold=True, underline=True))
    assert change.element.style["underline"] == "True"
    result = editor.set_text("p1", text_id, "word " * 400)
    assert result.overflow
    assert result.suggested_font_size is not None
    state = repos.project.load_state()
    assert state.built["p1"].edited
    assert state.deck_revision == 3


async def test_editor_rejects_unsupported_style(repos: Repos, approved_plan: Plan) -> None:
    """A fill on a text element, or an unknown element, raises a typed error."""
    await _deck(repos, approved_plan)
    editor = make_context(repos, ScriptedModel([])).editor
    text_id = next(e.id for e in editor.read_slide("p1").elements if e.type == "text")
    with pytest.raises(StyleNotSupportedError):
        editor.update_element("p1", text_id, StylePatch(fill="primary"))
    with pytest.raises(ElementNotFoundError):
        editor.update_element("p1", "nope", StylePatch(bold=True))


async def test_regenerating_warns_about_manual_edits(repos: Repos, approved_plan: Plan) -> None:
    """A rebuilt slide that had manual edits is reported in the warnings."""
    await _deck(repos, approved_plan)
    ctx = make_context(repos, ScriptedModel([]))
    text_id = next(e.id for e in ctx.editor.read_slide("p1").elements if e.type == "text")
    ctx.editor.update_element("p1", text_id, StylePatch(bold=True))
    plan = repos.plan.load()
    assert plan is not None
    changed = plan.slides[0].model_copy(update={"title": "New"})
    repos.plan.save(plan.model_copy(update={"slides": [changed]}))
    spec = {"type": "content", "title": "New", "body": ["x"]}
    model = ScriptedModel([[assistant_message(json.dumps(spec))]])
    report = await make_context(repos, model).generator.generate()
    assert "slide p1: manual edits were replaced" in report.warnings
