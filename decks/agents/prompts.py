from pathlib import Path

from decks.prompting.services import PromptTemplates

TEMPLATE_DIR = Path(__file__).parent / "templates"


class AgentPrompts:
    """Render the system prompts of the interview, deck and fill agents."""

    def __init__(self, templates: PromptTemplates | None = None) -> None:
        self._templates = templates or PromptTemplates(TEMPLATE_DIR)

    @property
    def fill(self) -> str:
        """System prompt of a fill agent, which fills the parameters of one slide."""
        return self._templates.render("fill.j2")

    @property
    def deck(self) -> str:
        """System prompt of the deck agent."""
        return self._templates.render("deck.j2")

    def interview(self, *, catalog: str, state: str) -> str:
        """System prompt of the interview agent, with the slide catalog and the plan state."""
        return self._templates.render("interview.j2", catalog=catalog, state=state)
