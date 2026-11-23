"""Prompts of the visual agents, built from the guideline sections."""

import json
from pathlib import Path

from decks.visuals.models import PICTURE_SIZE, VisualKind, VisualRequest
from decks.visuals.theme import ThemeInjector

GUIDELINES = Path(__file__).parent / "guidelines"

INTRO = """You draw one picture for a slide as SVG. The request is complete: you have no chat
history. Never invent data. Use only the facts of the request. When the data is missing, draw
the structure without numbers."""


class VisualPromptBuilder:
    """Build the system prompt and the input text of a visual agent."""

    def __init__(self, injector: ThemeInjector | None = None) -> None:
        self._injector = injector or ThemeInjector()

    def system(self, kind: VisualKind) -> str:
        """System prompt of ``kind``: intro, core rules with tokens, and the kind section."""
        core = (GUIDELINES / "core.md").read_text().format(tokens=self._injector.prompt)
        section = (GUIDELINES / f"{kind}.md").read_text()
        return "\n\n".join([INTRO, core, section])

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
