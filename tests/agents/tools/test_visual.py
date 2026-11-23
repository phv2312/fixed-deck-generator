import json

import pytest
from agents import RunConfig, Runner
from agents.testing import ScriptedModel, assistant_message, function_call

from decks.agents.agents.interview import build_interview_agent
from decks.agents.catalog import SlideCatalog
from decks.agents.repos import Repos
from decks.visuals.rasterizer import Rasterizer
from tests.agents.conftest import make_context
from tests.visuals import svgs

needs_chrome = pytest.mark.skipif(
    Rasterizer.find_chrome() is None, reason="Chrome is not installed"
)
REQUEST = {
    "brief": "Revenue by quarter",
    "rows": [],
    "stages": [],
    "items": [],
}


def _save(svg: str, call_id: str) -> list:
    args = {"svg": svg, "alt": "bars"}
    return [function_call("save_visual", args, call_id=call_id)]


async def _run(repos: Repos, script: list) -> tuple[ScriptedModel, str]:
    model = ScriptedModel(script)
    context = make_context(repos, model)
    agent = build_interview_agent(SlideCatalog().prompt)
    result = await Runner.run(
        agent,
        "make a diagram",
        context=context,
        run_config=RunConfig(model=model, tracing_disabled=True),
    )
    return model, str(result.final_output)


def test_interview_agent_has_two_visual_tools_and_no_chart_tool() -> None:
    """The interview agent gets create_diagram and create_mockup. A chart is a slide kind."""
    agent = build_interview_agent(SlideCatalog().prompt)
    names = {tool.name for tool in agent.tools}
    assert {"create_diagram", "create_mockup"} <= names
    assert "create_chart" not in names


@needs_chrome
async def test_visual_tool_saves_and_returns_path(repos: Repos) -> None:
    """The nested agent fixes an SVG with a hex colour, saves the second one and stops."""
    script = [
        [function_call("create_diagram", REQUEST, call_id="outer")],
        _save(svgs.HEX_COLOR, "n1"),
        _save(svgs.GOOD, "n2"),
        [assistant_message("done")],
    ]
    model, final = await _run(repos, script)
    assert final == "done"
    model.assert_complete()
    manifests = repos.assets.manifests()
    assert [(m.id, m.kind) for m in manifests] == [("v1", "diagram")]
    assert repos.assets.resolve("assets/v1.png").is_file()


@needs_chrome
async def test_failed_visual_tells_the_agent_to_fall_back(repos: Repos) -> None:
    """When the nested agent never saves, the outer agent gets the fallback message."""
    script = [
        [function_call("create_diagram", REQUEST, call_id="outer")],
        *[_save(svgs.HEX_COLOR, f"n{i}") for i in range(5)],
        [assistant_message("text slide instead")],
    ]
    model, _ = await _run(repos, script)
    outer_input = json.dumps([str(call) for call in model.calls[-1:]])
    assert "text-only" in outer_input
    assert repos.assets.manifests() == []
