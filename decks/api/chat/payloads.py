from collections.abc import AsyncIterator
from typing import Annotated, Self

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from decks.agents.models import StreamEvent
from decks.api.chat.models import ChatMessage, ChatTranscript, Role, ToolCall, ToolField, ToolStatus
from decks.api.payloads import QuestionResponse

TOOL_FIELD_URL = "/api/v1/projects/{project_id}/tool-calls/{call_id}/fields/{key}"

CallId = Annotated[
    str,
    Path(
        pattern=r"^[A-Za-z0-9_-]{1,128}$",
        description="Id of a tool call, as the chat history gives it.",
        examples=["call_2G47cunkqZ2eHDttTqgcVhA3"],
    ),
]
FieldKey = Annotated[
    str,
    Path(
        pattern=r"^(output|input\.[A-Za-z0-9_-]{1,64})$",
        description="`output`, or `input.<argument name>`, as the chat history gives it.",
        examples=["input.svg"],
    ),
]


class ChatMessageCreate(BaseModel):
    """Request body to send one chat message."""

    model_config = ConfigDict(extra="forbid")

    message: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=8000)
    ] = Field(
        description="The text of the user message.", examples=["Make a deck for the sales team."]
    )


class ToolFieldResponse(BaseModel):
    """One input or output of a tool call. The full value is at ``url``."""

    key: str = Field(description="`output`, or `input.<argument name>`.")
    size: int = Field(description="Size of the full value in bytes.")
    mime: str = Field(description="Media type of the full value, for example `image/svg+xml`.")
    preview: str = Field(description="The first 200 characters of the value.")
    url: str = Field(description="Where to get the full value.")

    @classmethod
    def from_field(cls, field: ToolField, *, project_id: str, call_id: str) -> Self:
        """Build the response and the URL of the full value."""
        return cls(
            key=field.key,
            size=field.size,
            mime=field.mime,
            preview=field.preview,
            url=TOOL_FIELD_URL.format(project_id=project_id, call_id=call_id, key=field.key),
        )


class ToolCallResponse(BaseModel):
    """One tool call of an assistant turn."""

    id: str = Field(description="Id of the tool call.")
    name: str = Field(description="Name of the tool.")
    summary: str = Field(description="One short line about the call.")
    status: ToolStatus = Field(
        description="`done` when the call has an output. Without one: `running` during a turn, "
        "else `error` (the turn stopped before the call finished)."
    )
    duration_ms: int | None = Field(description="Run time in ms. Null: chat.json does not keep it.")
    fields: list[ToolFieldResponse] = Field(
        description="Inputs and the output, without full values."
    )

    @classmethod
    def from_call(cls, call: ToolCall, *, project_id: str) -> Self:
        """Build the response from a tool call."""
        return cls(
            id=call.id,
            name=call.name,
            summary=call.summary,
            status=call.status,
            duration_ms=call.duration_ms,
            fields=[
                ToolFieldResponse.from_field(f, project_id=project_id, call_id=call.id)
                for f in call.fields
            ],
        )


class ChatMessageResponse(BaseModel):
    """One message of the chat."""

    id: str = Field(description="Stable id of the message.")
    role: Role = Field(description="Who wrote the message.")
    text: str = Field(description="Text of the message. An assistant turn may have none.")
    tool_calls: list[ToolCallResponse] = Field(description="Tool calls of an assistant turn.")
    question: QuestionResponse | None = Field(
        description="The question that this assistant turn asks, or null."
    )

    @classmethod
    def from_message(cls, message: ChatMessage, *, project_id: str) -> Self:
        """Build the response from a chat message."""
        question = message.question
        return cls(
            id=message.id,
            role=message.role,
            text=message.text,
            tool_calls=[
                ToolCallResponse.from_call(c, project_id=project_id) for c in message.tool_calls
            ],
            question=QuestionResponse.from_question(question) if question is not None else None,
        )


class ChatHistoryResponse(BaseModel):
    """Response body for the chat of a project: the whole transcript, oldest message first."""

    messages: list[ChatMessageResponse] = Field(description="The messages, oldest first.")
    running: bool = Field(description="Whether a chat turn runs now.")
    pending_question: QuestionResponse | None = Field(
        description="The question that waits for an answer, or null."
    )

    @classmethod
    def from_transcript(cls, transcript: ChatTranscript, *, project_id: str) -> Self:
        """Build the response from a transcript."""
        pending = transcript.pending_question
        return cls(
            messages=[
                ChatMessageResponse.from_message(m, project_id=project_id)
                for m in transcript.messages
            ],
            running=transcript.running,
            pending_question=QuestionResponse.from_question(pending)
            if pending is not None
            else None,
        )


class ServerSentEvents:
    """Encode the stream events of one chat turn as ``text/event-stream`` text.

    Each event is one frame: ``event: <type>`` and ``data: <JSON of the event>``.
    """

    def __init__(self, events: AsyncIterator[StreamEvent]) -> None:
        self._events = events

    def __aiter__(self) -> AsyncIterator[str]:
        return self._encode()

    async def _encode(self) -> AsyncIterator[str]:
        async for event in self._events:
            yield f"event: {event.type}\ndata: {event.model_dump_json()}\n\n"
