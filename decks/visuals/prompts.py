import json
from pathlib import Path

from decks.prompting.services import PromptTemplates
from decks.visuals.models import PICTURE_SIZE, VisualKind, VisualRequest
from decks.visuals.theme import ThemeInjector

GUIDELINES = Path(__file__).parent / "guidelines"


class VisualPromptBuilder:
    """Build the system prompt and the input text of a visual agent."""

    def __init__(
        self, injector: ThemeInjector | None = None, templates: PromptTemplates | None = None
    ) -> None:
        self._injector = injector or ThemeInjector()
        self._templates = templates or PromptTemplates(GUIDELINES)

    def system(self, kind: VisualKind) -> str:
        """System prompt of ``kind``: intro, core rules with tokens, and the kind section."""
        return self._templates.render("system.j2", kind=kind, tokens=self._injector.prompt)

    def request(self, request: VisualRequest) -> str:
        """Input text for the agent: frame, brief and data."""
        width, height = PICTURE_SIZE
        parts = [
            f'use viewBox="0 0 {width} {height}"',
            f"brief: {request.brief}",
        ]
        data = request.model_dump(exclude={"brief"}, exclude_defaults=True, exclude_none=True)
        if data:
            parts.append(f"data (JSON): {json.dumps(data, ensure_ascii=False)}")
        return "\n".join(parts)
