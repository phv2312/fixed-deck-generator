import json

import pytest
from agents.testing import ScriptedModel, assistant_message

from decks.agents.exceptions import (
    GenerationInProgressError,
    PlanNotApprovedError,
    RepairBudgetExceededError,
)
from decks.agents.repos import Repos
from decks.models.plan import Plan
from tests.agents.conftest import make_context


def _content(title: str, body: str = "Revenue grew 42%") -> list:
    spec = {"type": "content", "title": title, "body": [body]}
    return [assistant_message(json.dumps(spec))]


async def test_generate_builds_all_slides(repos: Repos, approved_plan: Plan) -> None:
    """A first generation builds every slide, numbers elements and bumps the revision."""
    repos.plan.save(approved_plan)
    model = ScriptedModel([_content("One"), _content("Two")])
    report = await make_context(repos, model).generator.generate()
    deck = repos.deck.load()
    assert deck is not None
    assert (report.built, report.failed, report.revision) == (2, [], 1)
    assert [s.id for s in deck.slides] == ["p1", "p2"]
    assert deck.slides[0].elements[0].id == "s1e1"
    assert deck.slides[1].elements[0].id == "s2e1"
    assert repos.project.load_state().phase == "generated"
    model.assert_complete()


async def test_second_run_rebuilds_only_changed_slide(repos: Repos, approved_plan: Plan) -> None:
    """The content hash limits a rebuild to the slide that changed."""
    repos.plan.save(approved_plan)
    await make_context(
        repos, ScriptedModel([_content("One"), _content("Two")])
    ).generator.generate()
    plan = repos.plan.load()
    assert plan is not None
    changed = plan.slides[1].model_copy(update={"title": "Changed"})
    repos.plan.save(plan.model_copy(update={"slides": [plan.slides[0], changed]}))
    model = ScriptedModel([_content("Two v2")])
    report = await make_context(repos, model).generator.generate()
    assert (report.built, report.revision) == (1, 2)
    model.assert_complete()


async def test_nothing_to_do(repos: Repos, approved_plan: Plan) -> None:
    """With every hash current, no LLM call happens."""
    repos.plan.save(approved_plan)
    await make_context(
        repos, ScriptedModel([_content("One"), _content("Two")])
    ).generator.generate()
    model = ScriptedModel([])
    report = await make_context(repos, model).generator.generate()
    assert report.built == 0
    assert model.calls == ()


async def test_bad_fill_falls_back_to_content(repos: Repos, approved_plan: Plan) -> None:
    """Two invalid fills give a plain content slide and a warning."""
    repos.plan.save(approved_plan.model_copy(update={"slides": approved_plan.slides[:1]}))
    bad = [assistant_message('{"type": "content"}')]
    report = await make_context(repos, ScriptedModel([bad, bad])).generator.generate()
    assert report.built == 1
    assert any("fell back" in w for w in report.warnings)


@pytest.mark.parametrize("approved", [False])
async def test_precondition_not_approved(
    repos: Repos, approved_plan: Plan, *, approved: bool
) -> None:
    """An unapproved plan is refused before any LLM call."""
    repos.plan.save(approved_plan.model_copy(update={"approved": approved}))
    model = ScriptedModel([])
    with pytest.raises(PlanNotApprovedError):
        await make_context(repos, model).generator.generate()
    assert model.calls == ()


async def test_concurrent_generation_is_refused(repos: Repos, approved_plan: Plan) -> None:
    """A second request while the lock is held raises GenerationInProgressError."""
    repos.plan.save(approved_plan)
    async with repos.lock:
        with pytest.raises(GenerationInProgressError):
            await make_context(repos, ScriptedModel([])).generator.generate()


async def test_fix_slide_uses_repair_budget(repos: Repos, approved_plan: Plan) -> None:
    """Each fix costs one repair; at zero the next fix raises."""
    repos.plan.save(approved_plan.model_copy(update={"slides": approved_plan.slides[:1]}))
    ctx = make_context(repos, ScriptedModel([_content("One")] + [_content("Fixed")] * 3))
    await ctx.generator.generate()
    for left in (2, 1, 0):
        result = await ctx.generator.fix_slide("p1", "shorter")
        assert result.repairs_remaining == left
    with pytest.raises(RepairBudgetExceededError):
        await ctx.generator.fix_slide("p1", "shorter")


async def test_missing_asset_falls_back_to_text_slide(repos: Repos, approved_plan: Plan) -> None:
    """A slide whose asset file is gone becomes a plain content slide, with no LLM call."""
    slide = approved_plan.slides[0].model_copy(
        update={
            "kind": "figure",
            "content": approved_plan.slides[0].content.model_copy(
                update={"image": "assets/v1.png"}
            ),
        }
    )
    repos.plan.save(approved_plan.model_copy(update={"slides": [slide]}))
    model = ScriptedModel([])
    report = await make_context(repos, model).generator.generate()
    assert report.built == 1
    assert any("assets/v1.png is missing" in w for w in report.warnings)
    deck = repos.deck.load()
    assert deck is not None
    assert deck.slides[0].kind == "content"
    assert model.calls == ()


async def test_asset_path_is_resolved_before_fill(repos: Repos, approved_plan: Plan) -> None:
    """A saved asset reaches the fill prompt as an absolute path, and the theme is synced."""
    from decks.visuals.models import VisualManifest

    repos.assets.save(
        VisualManifest(id="v1", kind="diagram", alt="a", theme="green"), "<svg/>", b"png"
    )
    slide = approved_plan.slides[0].model_copy(
        update={
            "kind": "figure",
            "content": approved_plan.slides[0].content.model_copy(
                update={"image": "assets/v1.png"}
            ),
        }
    )
    repos.plan.save(approved_plan.model_copy(update={"slides": [slide], "theme": "green"}))
    spec = {"type": "figure", "title": "T", "image": "x", "caption": "c"}
    model = ScriptedModel([[assistant_message(json.dumps(spec))]])
    await make_context(repos, model).generator.generate()
    prompt = json.dumps([str(call) for call in model.calls])
    assert str(repos.assets.resolve("assets/v1.png")) in prompt
    model.assert_complete()


async def test_image_kind_without_image_falls_back(repos: Repos, approved_plan: Plan) -> None:
    """A figure slide with no image is not sent to the model; it becomes a text slide."""
    slide = approved_plan.slides[0].model_copy(update={"kind": "figure"})
    repos.plan.save(approved_plan.model_copy(update={"slides": [slide]}))
    model = ScriptedModel([])
    report = await make_context(repos, model).generator.generate()
    deck = repos.deck.load()
    assert deck is not None
    assert deck.slides[0].kind == "content"
    assert any("needs an image" in w for w in report.warnings)
    assert model.calls == ()


async def test_fallback_keeps_the_picture_and_says_what_it_dropped(
    repos: Repos, approved_plan: Plan
) -> None:
    """A failed figure fill keeps the picture and the caption, and the warnings say why and what."""
    from decks.models.elements import Image, Text
    from decks.visuals.models import VisualManifest

    repos.assets.save(
        VisualManifest(id="v1", kind="diagram", alt="a", theme="green"), "<svg/>", b"png"
    )
    content = approved_plan.slides[0].content.model_copy(
        update={
            "summary": "Attention(Q, K, V)",
            "points": ["first point"],
            "rows": [["Queries", "from the decoder"]],
            "image": "assets/v1.png",
        }
    )
    slide = approved_plan.slides[0].model_copy(update={"kind": "figure", "content": content})
    repos.plan.save(approved_plan.model_copy(update={"slides": [slide], "theme": "green"}))
    bad = [assistant_message('{"type": "figure"}')]
    report = await make_context(repos, ScriptedModel([bad, bad])).generator.generate()
    deck = repos.deck.load()
    assert deck is not None
    built = deck.slides[0]
    assert built.kind == "figure"
    assert any(isinstance(e, Image) for e in built.elements)
    texts = " ".join(e.text for e in built.elements if isinstance(e, Text))
    assert "Attention(Q, K, V)" in texts
    expected = "fell back to a plain figure slide (figure: ModelBehaviorError"
    assert any(expected in w for w in report.warnings)
    assert any("2 text lines are not on the slide" in w for w in report.warnings)


async def test_overflow_is_shrunk_instead_of_retried(repos: Repos, approved_plan: Plan) -> None:
    """A long title is fitted by the fitter, so one LLM call is enough and nothing falls back."""
    title = "A very long headline that goes on and on and on and on and on and on and on and on"
    repos.plan.save(approved_plan.model_copy(update={"slides": approved_plan.slides[:1]}))
    model = ScriptedModel([_content(title)])
    report = await make_context(repos, model).generator.generate()
    assert report.warnings == []
    assert len(model.calls) == 1
