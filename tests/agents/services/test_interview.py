import pytest

from decks.agents.context import ProjectContext
from decks.agents.exceptions import (
    InvalidThemeError,
    MetaLengthMismatchError,
    NoSlidesError,
    PlanIncompleteError,
    PlanMetaMissingError,
    SlideNotFoundError,
    UnsupportedKindError,
)
from decks.agents.repos import Repos
from decks.models.plan import ContentBlock, SlideDraftPatch, SlideInput


@pytest.fixture
def ctx(repos: Repos) -> ProjectContext:
    """Context of a new project."""
    return ProjectContext.create(repos)


async def test_phase_moves_from_draft_to_review(ctx: ProjectContext, repos: Repos) -> None:
    """The service, not the model, moves the phase as the plan fills up."""
    await ctx.interview.set_meta("audience", "board")
    assert repos.project.load_state().phase == "interviewing"
    await ctx.interview.add_slide(
        after_id=None, purpose="open", title="Hi", kind="title", content=ContentBlock()
    )
    state = repos.project.load_state()
    assert state.phase == "review"
    assert state.plan_revision == 2


async def test_edit_revokes_approval(ctx: ProjectContext, repos: Repos) -> None:
    """Any plan edit clears the approval."""
    await ctx.interview.set_meta("audience", "board")
    await ctx.interview.add_slide(
        after_id=None, purpose="p", title="t", kind=None, content=ContentBlock()
    )
    await ctx.interview.approve()
    assert repos.project.load_state().phase == "approved"
    plan = await ctx.interview.set_meta("tone", "formal")
    assert not plan.approved
    assert repos.project.load_state().phase == "review"


async def test_approve_requires_complete_plan(ctx: ProjectContext) -> None:
    """Approval of an incomplete plan raises with the missing keys."""
    await ctx.interview.set_meta("tone", "formal")
    with pytest.raises(PlanIncompleteError) as info:
        await ctx.interview.approve()
    assert info.value.missing == ["audience", "slides"]


@pytest.mark.parametrize(
    ("key", "value", "error"),
    [("theme", "purple", InvalidThemeError)],
)
async def test_invalid_meta(
    ctx: ProjectContext, key: str, value: str, error: type[Exception]
) -> None:
    """A theme outside the allowed names is rejected."""
    with pytest.raises(error):
        await ctx.interview.set_meta(key, value)


async def test_slide_crud(ctx: ProjectContext) -> None:
    """Add, insert after, update and remove keep ids stable."""
    svc = ctx.interview
    await svc.set_meta("audience", "board")
    _, first = await svc.add_slide(
        after_id=None, purpose="a", title="A", kind=None, content=ContentBlock()
    )
    _, third = await svc.add_slide(
        after_id=None, purpose="c", title="C", kind=None, content=ContentBlock()
    )
    _, second = await svc.add_slide(
        after_id=first.id, purpose="b", title="B", kind=None, content=ContentBlock()
    )
    assert [s.id for s in svc.read().slides] == [first.id, second.id, third.id]
    _, changed = await svc.update_slide(second.id, SlideDraftPatch(title="B2", kind="statement"))
    assert (changed.title, changed.kind) == ("B2", "statement")
    plan = await svc.remove_slide(first.id)
    assert [s.id for s in plan.slides] == [second.id, third.id]


async def test_unknown_slide_and_kind(ctx: ProjectContext) -> None:
    """Unknown slide ids and kinds raise typed errors."""
    with pytest.raises(SlideNotFoundError):
        await ctx.interview.remove_slide("p9")
    with pytest.raises(UnsupportedKindError):
        await ctx.interview.add_slide(
            after_id=None, purpose="x", title="x", kind="nope", content=ContentBlock()
        )


async def test_variety_advice_does_not_block_approval(ctx: ProjectContext) -> None:
    """A plan with a broken variety rule still gets approved."""
    await ctx.interview.set_meta("audience", "board")
    for kind in ("pyramid", "funnel", "cycle"):
        await ctx.interview.add_slide(
            after_id=None, purpose="p", title=kind, kind=kind, content=ContentBlock()
        )
    plan = ctx.interview.read()
    assert len(ctx.interview.variety(plan)) == 1
    assert len(ctx.interview.variety(plan, complete=True)) == 3
    assert (await ctx.interview.approve()).approved


def test_variety_of_an_empty_plan(ctx: ProjectContext) -> None:
    """A plan without slides has no advice."""
    assert ctx.interview.variety(ctx.interview.read(), complete=True) == []


def _slide(title: str, kind: str) -> SlideInput:
    """A slide input with empty content."""
    return SlideInput(purpose="p", title=title, kind=kind, content=ContentBlock())


async def test_set_metas_sets_all_keys_in_one_commit(ctx: ProjectContext) -> None:
    """Lists of keys and values land in one plan revision, theme included."""
    plan = await ctx.interview.set_metas(["audience", "theme"], ["board", "orange"])
    assert (plan.meta, plan.theme, plan.revision) == ({"audience": "board"}, "orange", 1)


async def test_set_metas_rejects_unequal_lists(ctx: ProjectContext) -> None:
    """Lists of different length raise and change nothing."""
    with pytest.raises(MetaLengthMismatchError):
        await ctx.interview.set_metas(["audience", "theme"], ["board"])
    assert ctx.interview.read().revision == 0


async def test_slides_need_the_required_meta(ctx: ProjectContext) -> None:
    """Adding slides before the audience is set raises."""
    with pytest.raises(PlanMetaMissingError):
        await ctx.interview.add_slides([_slide("A", "title")], after_id=None)


async def test_add_slides_inserts_in_order_in_one_commit(ctx: ProjectContext) -> None:
    """A batch keeps its order, gets new ids and makes one revision."""
    svc = ctx.interview
    await svc.set_meta("audience", "board")
    plan = await svc.add_slides([_slide("A", "title"), _slide("C", "content")], after_id=None)
    revision = plan.revision
    plan = await svc.add_slides([_slide("B", "content")], after_id="p1")
    assert [s.title for s in plan.slides] == ["A", "B", "C"]
    assert [s.id for s in plan.slides] == ["p1", "p3", "p2"]
    assert plan.revision == revision + 1


async def test_move_slide(ctx: ProjectContext) -> None:
    """A slide moves after another one, or to the start."""
    svc = ctx.interview
    await svc.set_meta("audience", "board")
    await svc.add_slides([_slide(t, "content") for t in "ABC"], after_id=None)
    plan = await svc.move_slide("p1", "p3")
    assert [s.title for s in plan.slides] == ["B", "C", "A"]
    plan = await svc.move_slide("p1", None)
    assert [s.title for s in plan.slides] == ["A", "B", "C"]


async def test_next_action_follows_the_plan_state(ctx: ProjectContext) -> None:
    """The next step moves from meta to slides to final_check."""
    svc = ctx.interview
    assert "set_meta" in svc.next_action(svc.read())
    plan = await svc.set_meta("audience", "board")
    assert "add_plan_slides" in svc.next_action(plan)
    plan = await svc.add_slides([_slide("A", "title"), _slide("B", "content")], after_id=None)
    assert "closing slide" in svc.next_action(plan) or "last slide" in svc.next_action(plan)


async def test_final_check_stops_asking_after_two_revisions(ctx: ProjectContext) -> None:
    """final_check lists the issue, then tells the agent to stop after the third check."""
    svc = ctx.interview
    with pytest.raises(NoSlidesError):
        svc.final_check()
    await svc.set_meta("audience", "board")
    await svc.add_slides([_slide("A", "title"), _slide("B", "swot")], after_id=None)
    first = svc.final_check()
    assert not first.ok
    assert first.issues[0].slide_id == "p2"
    assert first.checks_remaining == 2
    svc.final_check()
    last = svc.final_check()
    assert last.checks_remaining == 0
    assert last.next_action.startswith("Stop revising")
    await svc.add_slides([_slide("End", "contact")], after_id=None)
    assert ctx.interview.final_check().ok
