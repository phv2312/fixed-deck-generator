from agents import RunContextWrapper, function_tool

from decks.agents.context import ProjectContext
from decks.agents.exceptions import DeckMissingError, PlanMissingError
from decks.agents.models import (
    CheckReport,
    DeckReport,
    ElementChange,
    FixResult,
    SlideView,
    StylePatch,
    TextFitResult,
)
from decks.agents.tools.errors import tool_error


# `function_tool` detects the context parameter from the literal annotation; an alias hides it.
@function_tool(failure_error_function=tool_error)
async def generate_deck(ctx: RunContextWrapper[ProjectContext]) -> DeckReport:
    """Build the slides that are missing or changed since the last build."""
    return await ctx.context.generator.generate()


@function_tool(failure_error_function=tool_error)
def check_deck(ctx: RunContextWrapper[ProjectContext], slide_id: str | None = None) -> CheckReport:
    """Check the deck, or one slide, for layout problems. It reports; it never fails."""
    deck = ctx.context.repos.deck.load()
    plan = ctx.context.repos.plan.load()
    if deck is None:
        raise DeckMissingError
    if plan is None:
        raise PlanMissingError
    issues = ctx.context.checker.check_deck(deck, plan)
    if slide_id is not None:
        issues = [i for i in issues if i.slide_id == slide_id]
    left = ctx.context.repos.project.load_state().repairs_remaining
    return CheckReport(
        ok=not any(i.severity == "error" for i in issues), issues=issues, repairs_remaining=left
    )


@function_tool(failure_error_function=tool_error)
async def fix_slide(
    ctx: RunContextWrapper[ProjectContext], slide_id: str, instructions: str
) -> FixResult:
    """Rebuild one slide with the given instructions. It uses one repair."""
    return await ctx.context.generator.fix_slide(slide_id, instructions)


@function_tool(failure_error_function=tool_error)
def read_slide(ctx: RunContextWrapper[ProjectContext], slide_id: str) -> SlideView:
    """Read a short view of the elements of one slide."""
    return ctx.context.editor.read_slide(slide_id)


@function_tool(failure_error_function=tool_error)
def update_element(
    ctx: RunContextWrapper[ProjectContext], slide_id: str, element_id: str, patch: StylePatch
) -> ElementChange:
    """Change the style of one element: font, colour, bold, italic, underline, fill."""
    return ctx.context.editor.update_element(slide_id, element_id, patch)


@function_tool(failure_error_function=tool_error)
def set_text(
    ctx: RunContextWrapper[ProjectContext],
    slide_id: str,
    element_id: str,
    text: str,
    *,
    autofit: bool = True,
) -> TextFitResult:
    """Replace the text of one element. With autofit the font shrinks until the text fits."""
    return ctx.context.editor.set_text(slide_id, element_id, text, autofit=autofit)


DECK_TOOLS = [generate_deck, check_deck, fix_slide, read_slide, update_element, set_text]
