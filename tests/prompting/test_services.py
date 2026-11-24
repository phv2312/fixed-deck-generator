from pathlib import Path

import pytest

from decks.prompting.exceptions import PromptTemplateNotFoundError, PromptVariableMissingError
from decks.prompting.services import PromptTemplates


@pytest.fixture
def templates(tmp_path: Path) -> PromptTemplates:
    """Templates of a temporary directory with one greeting template."""
    (tmp_path / "greet.j2").write_text("Hello {{ name }}.\n")
    return PromptTemplates(tmp_path)


def test_render_substitutes_variables_and_drops_the_last_newline(
    templates: PromptTemplates,
) -> None:
    """The variable is replaced and the file's final newline is not in the prompt."""
    assert templates.render("greet.j2", name="Ada") == "Hello Ada."


@pytest.mark.parametrize(
    "value",
    [
        "{}",
        '{"a": 1}',
        "<b>&amp;</b>",
        "{{ not_a_variable }}",
    ],
)
def test_render_keeps_braces_and_markup_of_a_value(templates: PromptTemplates, value: str) -> None:
    """A value is inserted as it is: no format error, no HTML escape, no second render."""
    assert templates.render("greet.j2", name=value) == f"Hello {value}."


def test_render_raises_when_a_variable_is_missing(templates: PromptTemplates) -> None:
    """A variable that the caller did not give is an error, not an empty string."""
    with pytest.raises(PromptVariableMissingError, match=r"greet\.j2"):
        templates.render("greet.j2")


def test_render_raises_when_the_template_does_not_exist(templates: PromptTemplates) -> None:
    """An unknown template name raises a typed error that names the template."""
    with pytest.raises(PromptTemplateNotFoundError, match=r"nope\.j2"):
        templates.render("nope.j2")
