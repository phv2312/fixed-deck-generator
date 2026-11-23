import json
from typing import cast

from agents.items import TResponseInputItem
from agents.memory import SessionABC, SessionSettings

from decks.agents.repos.base import AtomicJsonStore


class ChatRepository(SessionABC):
    """Store the conversation items in chat.json. Pass it as ``session=`` to ``Runner.run``."""

    session_settings: SessionSettings | None = None

    def __init__(self, session_id: str, store: AtomicJsonStore) -> None:
        self.session_id = session_id
        self._store = store

    def _read(self) -> list[TResponseInputItem]:
        text = self._store.read_text()
        return cast(list[TResponseInputItem], json.loads(text)) if text else []

    def _write(self, items: list[TResponseInputItem]) -> None:
        self._store.write_text(json.dumps(items, ensure_ascii=False))

    async def get_items(self, limit: int | None = None) -> list[TResponseInputItem]:
        """Return all items, or the latest ``limit`` items, oldest first."""
        items = self._read()
        return items if limit is None else items[-limit:] if limit > 0 else []

    async def add_items(self, items: list[TResponseInputItem]) -> None:
        """Append ``items`` to the history."""
        self._write([*self._read(), *items])

    async def pop_item(self) -> TResponseInputItem | None:
        """Remove and return the latest item."""
        items = self._read()
        if not items:
            return None
        last = items.pop()
        self._write(items)
        return last

    async def clear_session(self) -> None:
        """Remove the whole history."""
        self._store.delete()
