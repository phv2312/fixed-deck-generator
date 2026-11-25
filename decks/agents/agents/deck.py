from agents import Agent
from agents.models.interface import Model

from decks.agents.context import ProjectContext
from decks.agents.prompts import AgentPrompts
from decks.agents.tools.deck import DECK_TOOLS


def build_deck_agent(model: str | Model | None = None) -> Agent[ProjectContext]:
    """Create the deck agent."""
    return Agent[ProjectContext](
        name="deck", instructions=AgentPrompts().deck, tools=list(DECK_TOOLS), model=model
    )
