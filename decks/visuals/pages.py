"""Jinja2 wrapper for the HTML page that Chrome loads."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError, select_autoescape

from decks.visuals.exceptions import PageTemplateError

TEMPLATE_DIR = Path(__file__).parent / "templates"


class PageTemplates:
    """Render the page templates of one directory. Values are escaped unless they are ``Markup``."""

    def __init__(self, directory: Path = TEMPLATE_DIR) -> None:
        self._env = Environment(
            loader=FileSystemLoader(directory),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(("html.j2",), default_for_string=False),
        )

    def render(self, name: str, /, **context: object) -> str:
        """Render the template ``name`` with ``context``."""
        try:
            return self._env.get_template(name).render(**context)
        except TemplateError as error:
            raise PageTemplateError(name, str(error)) from error
