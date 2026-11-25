from agents import Agent, RunContextWrapper, StopAtTools
from agents.models.interface import Model

from decks.agents.context import ProjectContext
from decks.agents.prompts import AgentPrompts
from decks.agents.tools.interview import INTERVIEW_TOOLS, ask_user_question
from decks.agents.tools.visual import visual_tools


def build_interview_agent(
    catalog_prompt: str, model: str | Model | None = None
) -> Agent[ProjectContext]:
    """Create the interview agent. A question to the user ends its run."""

    prompts = AgentPrompts()

    def instructions(ctx: RunContextWrapper[ProjectContext], _: Agent[ProjectContext]) -> str:
        state = ctx.context.interview.snapshot().model_dump_json(indent=2)
        return prompts.interview(catalog=catalog_prompt, state=state)

    return Agent[ProjectContext](
        name="interview",
        instructions=instructions,
        tools=[*INTERVIEW_TOOLS, *visual_tools(model)],
        tool_use_behavior=StopAtTools(stop_at_tool_names=[ask_user_question.name]),
        model=model,
    )
