from agents import Agent

from decks.agents.context import ProjectContext
from decks.agents.prompts import AgentPrompts
from decks.agents.tools.deck import DECK_TOOLS


def build_deck_agent(model: str | None = None) -> Agent[ProjectContext]:
    """Create the deck agent."""
    return Agent[ProjectContext](
        name="deck", instructions=AgentPrompts().deck, tools=list(DECK_TOOLS), model=model
    )
