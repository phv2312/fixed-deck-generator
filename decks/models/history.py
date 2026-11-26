from pydantic import BaseModel, Field

from decks.models.slides import Deck

MAX_HISTORY = 20


class DeckHistory(BaseModel):
    """Deck snapshots for undo and redo. Each list holds at most ``MAX_HISTORY`` decks."""

    past: list[Deck] = Field(default_factory=list, description="Older decks, oldest first.")
    future: list[Deck] = Field(default_factory=list, description="Undone decks, next redo last.")

    @property
    def can_undo(self) -> bool:
        """Whether there is an older deck to return to."""
        return bool(self.past)

    @property
    def can_redo(self) -> bool:
        """Whether there is an undone deck to bring back."""
        return bool(self.future)

    def recorded(self, deck: Deck) -> "DeckHistory":
        """Return the history after an edit of ``deck``: ``deck`` joins the past, redo is lost."""
        return DeckHistory(past=[*self.past, deck][-MAX_HISTORY:], future=[])

    def undone(self, current: Deck) -> tuple["DeckHistory", Deck]:
        """Return the history after an undo, and the deck to restore."""
        *older, previous = self.past
        return DeckHistory(past=older, future=[*self.future, current][-MAX_HISTORY:]), previous

    def redone(self, current: Deck) -> tuple["DeckHistory", Deck]:
        """Return the history after a redo, and the deck to restore."""
        *later, following = self.future
        return DeckHistory(past=[*self.past, current][-MAX_HISTORY:], future=later), following
