from typing import ClassVar

from decks.api.openapi import RouteDoc


class ChatDocs:
    """Swagger text of the chat endpoints."""

    SEND: ClassVar[RouteDoc] = RouteDoc(
        "Send a chat message",
        "Send one user message and stream the answer as server-sent events. Each event has "
        "`event: <type>` and a JSON `data` line. The types are `run_started`, `status`, `token`, "
        "`tool_started`, `tool_finished`, `question`, `plan_updated`, `deck_progress`, "
        "`deck_ready`, `error` and `done`. The last event is always `done`. A failure during the "
        "turn arrives as an `error` event, not as an HTTP error. When a turn already runs, the "
        "answer is 409 `TurnInProgressError`. If the client closes the connection, the turn stops.",
    )
    HISTORY: ClassVar[RouteDoc] = RouteDoc(
        "Read the chat history",
        "Return the whole chat, oldest message first. An assistant message lists the tool calls "
        "of its turn. A call has a short summary and its fields without their full values; each "
        "field has a `url` for the full value. `pending_question` is the question that waits for "
        "an answer. Send the answer as the next chat message.",
    )
    FIELD: ClassVar[RouteDoc] = RouteDoc(
        "Read one tool field",
        "Return the full value of one input or output of a tool call, with its own media type "
        "(`text/plain`, `application/json` or `image/svg+xml`). Add `download=true` to get it as "
        "a file. The value is sent with a `sandbox` Content-Security-Policy, so a script in an "
        "SVG does not run.",
    )
