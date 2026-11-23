from agents import RunContextWrapper, function_tool

from decks.agents.context import ProjectContext
from decks.agents.models import (
    PlanCheck,
    PlanMetaView,
    PlanView,
    Question,
    QuestionEvent,
    SlideRef,
)
from decks.agents.tools.errors import tool_error
from decks.models.plan import ContentBlock, SlideDraftPatch, SlideInput


# `function_tool` detects the context parameter from the literal annotation; an alias hides it.
@function_tool(failure_error_function=tool_error)
async def ask_user_question(
    ctx: RunContextWrapper[ProjectContext],
    question: str,
    options: list[str] | None = None,
    allow_multiple: bool = False,
    free_text: bool = True,
) -> Question:
    """Ask the user one question and end the turn. Offer options when the answers are few."""
    asked = Question(
        question=question, options=options, allow_multiple=allow_multiple, free_text=free_text
    )
    await ctx.context.sink.emit(QuestionEvent(**asked.model_dump()))
    return asked


@function_tool(failure_error_function=tool_error)
async def set_meta(
    ctx: RunContextWrapper[ProjectContext], keys: list[str], values: list[str]
) -> PlanMetaView:
    """Set plan facts. `keys[i]` gets `values[i]`; the lists have equal length.

    The key `theme` accepts green or orange. Set every known fact in one call.
    """
    service = ctx.context.interview
    plan = await service.set_metas(keys, values)
    return PlanMetaView.of(plan, ctx.context.phase, service.next_action(plan))


@function_tool(failure_error_function=tool_error)
async def remove_meta(ctx: RunContextWrapper[ProjectContext], key: str) -> PlanMetaView:
    """Remove one plan fact."""
    service = ctx.context.interview
    plan = await service.remove_meta(key)
    return PlanMetaView.of(plan, ctx.context.phase, service.next_action(plan))


@function_tool(failure_error_function=tool_error)
async def add_plan_slide(
    ctx: RunContextWrapper[ProjectContext],
    purpose: str,
    title: str,
    content: ContentBlock,
    kind: str,
    after_id: str | None = None,
) -> SlideRef:
    """Add one slide after `after_id`, or at the end. Prefer add_plan_slides for a draft."""
    service = ctx.context.interview
    plan, draft = await service.add_slide(
        after_id=after_id, purpose=purpose, title=title, kind=kind, content=content
    )
    return SlideRef.of(
        plan, draft, ctx.context.phase, service.variety(plan), service.next_action(plan)
    )


@function_tool(failure_error_function=tool_error)
async def add_plan_slides(
    ctx: RunContextWrapper[ProjectContext], slides: list[SlideInput], after_id: str | None = None
) -> PlanView:
    """Add many slides in order after `after_id`, or at the end, in one call.

    Set content.image first for a slide that needs a picture.
    """
    service = ctx.context.interview
    plan = await service.add_slides(slides, after_id=after_id)
    return PlanView.of(plan, service.variety(plan), service.next_action(plan))


@function_tool(failure_error_function=tool_error)
async def update_plan_slide(
    ctx: RunContextWrapper[ProjectContext], slide_id: str, patch: SlideDraftPatch
) -> SlideRef:
    """Change fields of a plan slide. Fields left empty stay as they are."""
    service = ctx.context.interview
    plan, draft = await service.update_slide(slide_id, patch)
    return SlideRef.of(
        plan, draft, ctx.context.phase, service.variety(plan), service.next_action(plan)
    )


@function_tool(failure_error_function=tool_error)
async def remove_plan_slide(ctx: RunContextWrapper[ProjectContext], slide_id: str) -> PlanView:
    """Remove a slide from the plan."""
    service = ctx.context.interview
    plan = await service.remove_slide(slide_id)
    return PlanView.of(plan, service.variety(plan), service.next_action(plan))


@function_tool(failure_error_function=tool_error)
async def move_plan_slide(
    ctx: RunContextWrapper[ProjectContext], slide_id: str, after_id: str | None = None
) -> PlanView:
    """Move a slide after `after_id`, or to the start when `after_id` is empty."""
    service = ctx.context.interview
    plan = await service.move_slide(slide_id, after_id)
    return PlanView.of(plan, service.variety(plan), service.next_action(plan))


@function_tool(failure_error_function=tool_error)
def final_check(ctx: RunContextWrapper[ProjectContext]) -> PlanCheck:
    """Check the whole plan. It lists issues with the slide to change and the fix."""
    return ctx.context.interview.final_check()


INTERVIEW_TOOLS = [
    ask_user_question,
    set_meta,
    remove_meta,
    add_plan_slide,
    add_plan_slides,
    update_plan_slide,
    remove_plan_slide,
    move_plan_slide,
    final_check,
]
