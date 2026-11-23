from decks.agents.catalog import SlideCatalog
from decks.agents.prompts import INTERVIEW_SYSTEM
from decks.models.plan import ContentBlock


def test_interview_prompt_sends_charts_to_slide_kinds() -> None:
    """A chart is a slide kind: the prompt names no chart picture tool and points to the kinds."""
    prompt = INTERVIEW_SYSTEM.format(catalog=SlideCatalog().prompt, state="{}")

    assert "create_chart" not in prompt
    assert "Charts are slide kinds, never pictures" in prompt
    assert "content.categories" in prompt


def test_plan_content_holds_the_category_labels_of_a_chart() -> None:
    """Chart kinds need labels beside the values, so the plan content has a categories field."""
    block = ContentBlock(categories=["Q1", "Q2"])

    assert block.categories == ["Q1", "Q2"]
