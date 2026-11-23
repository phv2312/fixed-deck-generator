import json

import pytest
from agents import Agent, FunctionTool, RunConfig, RunContextWrapper, Runner
from agents.testing import ScriptedModel, assistant_message, function_call

from decks.agents.agents.interview import build_interview_agent
from decks.agents.catalog import SlideCatalog
from decks.agents.context import ProjectContext
from decks.agents.repos import Repos
from decks.agents.tools.deck import DECK_TOOLS
from decks.agents.tools.errors import tool_error
from decks.agents.tools.interview import INTERVIEW_TOOLS
from tests.agents.conftest import make_context


@pytest.mark.parametrize("tool", [*INTERVIEW_TOOLS, *DECK_TOOLS], ids=lambda t: t.name)
def test_tool_schema_is_strict_and_dict_free(tool: FunctionTool) -> None:
    """Every tool uses strict schema and has no free-form object parameter."""
    assert tool.strict_json_schema
    assert '"additionalProperties": true' not in json.dumps(tool.params_json_schema)
    assert "context" not in tool.params_json_schema.get("properties", {})


def _interviewer() -> Agent[ProjectContext]:
    return build_interview_agent(SlideCatalog().prompt)


async def test_interviewer_records_a_fact_and_replies(repos: Repos) -> None:
    """The interviewer records a fact and ends the turn with its text reply."""
    ctx = make_context(repos, ScriptedModel([]))
    script = ScriptedModel(
        [
            [function_call("set_meta", {"keys": ["audience"], "values": ["board"]}, call_id="c2")],
            [assistant_message("Noted. How many slides?")],
        ]
    )
    result = await Runner.run(
        _interviewer(),
        "make a deck",
        context=ctx,
        run_config=RunConfig(model=script, tracing_disabled=True),
        session=repos.chat,
    )
    assert "How many slides?" in str(result.final_output)
    assert ctx.interview.read().meta == {"audience": "board"}
    assert repos.project.load_state().phase == "interviewing"
    assert len(await repos.chat.get_items()) > 0
    script.assert_complete()


async def test_question_ends_the_turn_and_emits_event(repos: Repos) -> None:
    """ask_user_question stops the interview agent and emits a question event."""
    ctx = make_context(repos, ScriptedModel([]))
    script = ScriptedModel(
        [
            [
                function_call(
                    "ask_user_question",
                    {
                        "question": "Who is the audience?",
                        "options": ["board", "team"],
                        "allow_multiple": False,
                        "free_text": True,
                    },
                    call_id="c2",
                )
            ],
        ]
    )
    result = await Runner.run(
        _interviewer(),
        "hi",
        context=ctx,
        run_config=RunConfig(model=script, tracing_disabled=True),
    )
    assert "Who is the audience?" in str(result.final_output)
    await ctx.sink.close()
    types = [e.type async for e in ctx.sink.events()]
    assert types == ["question", "done"]


@pytest.mark.parametrize("tool", [*INTERVIEW_TOOLS, *DECK_TOOLS], ids=lambda t: t.name)
def test_every_tool_reports_concrete_errors(tool: FunctionTool) -> None:
    """No tool falls back to the SDK's generic error message."""
    assert tool._failure_error_function is tool_error


async def test_tool_failure_names_the_cause(repos: Repos) -> None:
    """A failing tool returns the error message to the model, not a generic text."""
    ctx = make_context(repos, ScriptedModel([]))
    script = ScriptedModel(
        [
            [function_call("remove_plan_slide", {"slide_id": "p9"}, call_id="c1")],
            [assistant_message("done")],
        ]
    )
    result = await Runner.run(
        _interviewer(),
        "remove it",
        context=ctx,
        run_config=RunConfig(model=script, tracing_disabled=True),
    )
    outputs = [i.output for i in result.new_items if i.type == "tool_call_output_item"]
    assert outputs == ["slide p9 does not exist"]


async def test_interview_prompt_holds_the_current_plan(repos: Repos) -> None:
    """The instructions of every turn carry the plan, so the agent needs no extra read."""
    ctx = make_context(repos, ScriptedModel([]))
    await ctx.interview.set_meta("audience", "board")
    agent = _interviewer()
    assert callable(agent.instructions)
    text = await agent.get_system_prompt(RunContextWrapper(ctx))
    assert "audience=board" in str(text)
    assert "Current plan:" in str(text)
