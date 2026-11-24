import pytest

from decks.agents.catalog import SlideCatalog
from decks.agents.prompts import AgentPrompts
from decks.models.plan import ContentBlock


def test_interview_prompt_sends_charts_to_slide_kinds() -> None:
    """A chart is a slide kind: the prompt names no chart picture tool and points to the kinds."""
    prompt = AgentPrompts().interview(catalog=SlideCatalog().prompt, state="{}")

    assert "create_chart" not in prompt
    assert "Charts are slide kinds, never pictures" in prompt
    assert "content.categories" in prompt


def test_interview_prompt_ends_with_the_state_and_the_catalog() -> None:
    """The plan state and the catalog go in as they are, braces included."""
    prompt = AgentPrompts().interview(catalog="CATALOG {x}", state='{"slides": []}')

    assert 'Current plan:\n{"slides": []}\n\n' in prompt
    assert prompt.endswith("Slide kind catalog:\nCATALOG {x}")


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        (AgentPrompts().fill, "You fill the parameters of ONE slide"),
        (AgentPrompts().deck, "You are the deck agent."),
    ],
)
def test_static_prompts_render_without_variables(prompt: str, expected: str) -> None:
    """The fill and deck prompts need no variable and keep their opening text."""
    assert prompt.startswith(expected)
    assert "{{" not in prompt
    assert not prompt.endswith("\n")


def test_plan_content_holds_the_category_labels_of_a_chart() -> None:
    """Chart kinds need labels beside the values, so the plan content has a categories field."""
    block = ContentBlock(categories=["Q1", "Q2"])

    assert block.categories == ["Q1", "Q2"]
