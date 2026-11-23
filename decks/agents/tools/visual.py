from typing import Any

from agents import (
    Agent,
    FunctionTool,
    FunctionToolResult,
    RunContextWrapper,
    Tool,
    ToolsToFinalOutputResult,
    function_tool,
)
from agents.agent_tool_input import StructuredToolInputBuilderOptions

from decks.agents.context import ProjectContext
from decks.agents.tools.errors import tool_error
from decks.models.theme import DEFAULT_THEME
from decks.visuals.models import VisualKind, VisualRequest, VisualResult
from decks.visuals.prompts import VisualPromptBuilder

SAVE_TOOL = "save_visual"
VISUAL_MAX_TURNS = 5  # model calls one visual agent may use

FAILED = (
    "The visual could not be made. Do not set content.image. Choose a text-only slide kind "
    "for this slide and tell the user that the picture failed."
)

DESCRIPTIONS = {
    "diagram": "Draw a flow, structure or relation diagram. Returns the image path.",
    "mockup": "Draw a simplified screen mockup. Returns the image path.",
}


def stop_when_saved(
    _: RunContextWrapper[ProjectContext], results: list[FunctionToolResult]
) -> ToolsToFinalOutputResult:
    """End the visual agent only when ``save_visual`` saved the picture. Issues keep it going."""
    for result in results:
        saved = result.output
        if result.tool.name == SAVE_TOOL and isinstance(saved, VisualResult) and saved.ok:
            return ToolsToFinalOutputResult(
                is_final_output=True, final_output=saved.model_dump_json()
            )
    return ToolsToFinalOutputResult(is_final_output=False)


def make_save_tool(kind: VisualKind) -> FunctionTool:
    """Create the ``save_visual`` tool of a visual agent of ``kind``."""

    # `function_tool` detects the context parameter from the literal annotation.
    @function_tool(name_override=SAVE_TOOL, failure_error_function=tool_error)
    async def save_visual(
        ctx: RunContextWrapper[ProjectContext],
        svg: str,
        alt: str,
    ) -> VisualResult:
        """Check and save the SVG. It returns issues to fix, or the path of the saved picture.

        Pass a short `alt` text that says what the picture shows.
        """
        plan = ctx.context.repos.plan.load()
        theme = plan.theme if plan is not None else DEFAULT_THEME
        return await ctx.context.visuals.save(kind, alt, svg, theme)

    return save_visual


def visual_enabled(ctx: RunContextWrapper[ProjectContext], _: Any) -> bool:
    """The visual tools exist only when Chrome is installed."""
    return ctx.context.visuals.available


def visual_tool(
    kind: VisualKind,
    prompts: VisualPromptBuilder,
    model: str | None = None,
    max_turns: int = VISUAL_MAX_TURNS,
) -> FunctionTool:
    """Wrap the visual agent of ``kind`` as a tool: ``create_<kind>``."""
    agent = Agent[ProjectContext](
        name=f"visual-{kind}",
        instructions=prompts.system(kind),
        tools=[make_save_tool(kind)],
        tool_use_behavior=stop_when_saved,
        model=model,
    )

    def build_input(options: StructuredToolInputBuilderOptions) -> str:
        params = options["params"]
        request = (
            params if isinstance(params, VisualRequest) else VisualRequest.model_validate(params)
        )
        return prompts.request(request)

    return agent.as_tool(
        tool_name=f"create_{kind}",
        tool_description=DESCRIPTIONS[kind],
        parameters=VisualRequest,
        input_builder=build_input,
        is_enabled=visual_enabled,
        failure_error_function=lambda _ctx, _error: FAILED,
        max_turns=max_turns,
    )


def visual_tools(model: str | None = None) -> list[Tool]:
    """Return the two visual tools: diagram and mockup. A chart is a slide kind, not a picture."""
    prompts = VisualPromptBuilder()
    return [visual_tool(kind, prompts, model) for kind in ("diagram", "mockup")]
