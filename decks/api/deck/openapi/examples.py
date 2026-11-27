from pathlib import Path
from typing import ClassVar

from decks.api.deck.payloads import DeckResponse, EditResponse

EXAMPLES = Path(__file__).parent / "examples"


class DeckExamples:
    """Response examples of the deck endpoints. A wrong example fails at import."""

    DECK: ClassVar[DeckResponse] = DeckResponse.model_validate_json(
        (EXAMPLES / "deck.json").read_text()
    )
    EDIT: ClassVar[EditResponse] = EditResponse.model_validate_json(
        (EXAMPLES / "edit.json").read_text()
    )
