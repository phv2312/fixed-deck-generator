import pytest

from decks.visuals.models import VisualKind
from decks.visuals.prompts import VisualPromptBuilder
from decks.visuals.theme import TOKENS


@pytest.mark.parametrize(
    ("kind", "section_marker"),
    [
        ("diagram", "Read order is left to right"),
        ("mockup", "frame, panels, items"),
    ],
)
def test_system_prompt_joins_intro_core_and_kind_section(
    kind: VisualKind, section_marker: str
) -> None:
    """The system prompt holds the intro, the core rules with tokens, and the kind section."""
    prompt = VisualPromptBuilder().system(kind)

    assert prompt.startswith("You draw one picture for a slide as SVG.")
    assert "## Rules for every picture" in prompt
    assert all(f"fill-{token}" in prompt for token in TOKENS)
    assert section_marker in prompt
    assert "{{" not in prompt
    assert "{%" not in prompt


def test_system_prompt_of_one_kind_has_no_section_of_the_other() -> None:
    """A diagram prompt carries the diagram section only."""
    builder = VisualPromptBuilder()

    assert "frame, panels, items" not in builder.system("diagram")
    assert "Read order is left to right" not in builder.system("mockup")
