from typing import Annotated

from fastapi import Depends

from decks.api.deck.services import DeckService
from decks.api.deps import ContainerDep


async def get_deck_service(container: ContainerDep) -> DeckService:
    """Return the deck service of this request."""
    return DeckService(container.repositories)


DeckServiceDep = Annotated[DeckService, Depends(get_deck_service)]
