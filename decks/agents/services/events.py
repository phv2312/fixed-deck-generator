import asyncio
from collections.abc import AsyncIterator

from agents import (
    RawResponsesStreamEvent,
    RunItemStreamEvent,
    ToolCallItem,
    ToolCallOutputItem,
)
from agents import StreamEvent as SdkStreamEvent
from openai.types.responses import ResponseFunctionToolCall, ResponseTextDeltaEvent

from decks.agents.models import (
    Done,
    StreamEvent,
    Token,
    ToolFinished,
    ToolStarted,
)


class EventSink:
    """Queue of ``StreamEvent`` for one chat turn. Services emit; the SSE layer reads."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[StreamEvent | None] = asyncio.Queue()
        self._seen: set[str] = set()

    def has_emitted(self, event_type: str) -> bool:
        """Return whether an event of ``event_type`` was emitted on this sink."""
        return event_type in self._seen

    async def emit(self, event: StreamEvent) -> None:
        """Add ``event`` to the stream."""
        self._seen.add(event.type)
        await self._queue.put(event)

    async def close(self) -> None:
        """End the stream after the last event. Emit ``done`` first."""
        await self._queue.put(Done())
        await self._queue.put(None)

    async def events(self) -> AsyncIterator[StreamEvent]:
        """Yield events until ``close`` is called."""
        while (event := await self._queue.get()) is not None:
            yield event


class SdkEventMapper:
    """Translate SDK stream events into our events. Tool arguments are never forwarded."""

    def __init__(self) -> None:
        self._names: dict[str, str] = {}

    def map(self, event: SdkStreamEvent) -> StreamEvent | None:
        """Return the matching event, or ``None`` for events we do not expose."""
        if isinstance(event, RawResponsesStreamEvent):
            data = event.data
            return Token(text=data.delta) if isinstance(data, ResponseTextDeltaEvent) else None
        if not isinstance(event, RunItemStreamEvent):
            return None
        item = event.item
        if isinstance(item, ToolCallItem) and isinstance(item.raw_item, ResponseFunctionToolCall):
            self._names[item.raw_item.call_id] = item.raw_item.name
            return ToolStarted(name=item.raw_item.name)
        if isinstance(item, ToolCallOutputItem) and isinstance(item.raw_item, dict):
            call_id = str(item.raw_item.get("call_id", ""))
            return ToolFinished(name=self._names.get(call_id, ""))
        return None
