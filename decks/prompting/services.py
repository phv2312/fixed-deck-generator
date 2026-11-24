from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound, UndefinedError

from decks.prompting.exceptions import PromptTemplateNotFoundError, PromptVariableMissingError


class PromptTemplates:
    """Render the Jinja2 prompt templates of one directory.

    Prompts are plain text, so the environment does not escape. A variable that the caller does
    not give is an error. Jinja drops the last newline of a template, so a template file ends with
    a newline and the rendered text does not.
    """

    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._env = Environment(
            loader=FileSystemLoader(directory),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )

    def render(self, template: str, /, **context: object) -> str:
        """Render ``template`` with ``context`` and return the prompt text."""
        try:
            return self._env.get_template(template).render(**context)
        except TemplateNotFound as error:
            raise PromptTemplateNotFoundError(template, str(self._directory)) from error
        except UndefinedError as error:
            raise PromptVariableMissingError(template, str(error)) from error
