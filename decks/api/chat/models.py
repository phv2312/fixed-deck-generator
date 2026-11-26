import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal, Self

from pydantic import BaseModel, Field, ValidationError

from decks.agents.models import Question

PREVIEW_CHARS = 200
SUMMARY_CHARS = 100
SNIFF_CHARS = 2000
QUESTION_TOOL = "ask_user_question"

type Item = Mapping[str, object]
type ToolStatus = Literal["running", "done", "error"]
type Role = Literal["user", "assistant"]


class FieldValue(BaseModel):
    """The full text of one input or output of a tool call, with its media type."""

    content: str
    mime: str

    @classmethod
    def of(cls, value: object) -> Self:
        """Describe ``value``. A string stays as it is; any other value becomes JSON."""
        if isinstance(value, str):
            return cls(content=value, mime=cls._mime_of_text(value))
        return cls(content=json.dumps(value, ensure_ascii=False), mime="application/json")

    @property
    def size(self) -> int:
        """Size of the text in bytes (UTF-8)."""
        return len(self.content.encode())

    @property
    def preview(self) -> str:
        """The first characters of the text."""
        return self.content[:PREVIEW_CHARS]

    @property
    def extension(self) -> str:
        """File extension for a download of this value."""
        return {"image/svg+xml": "svg", "application/json": "json"}.get(self.mime, "txt")

    @staticmethod
    def _mime_of_text(text: str) -> str:
        """Return ``image/svg+xml``, ``application/json`` or ``text/plain`` for ``text``."""
        head = text.lstrip()
        if head.startswith(("<svg", "<?xml")) and "<svg" in head[:SNIFF_CHARS]:
            return "image/svg+xml"
        if head[:1] in ("{", "["):
            try:
                json.loads(head)
            except ValueError:
                return "text/plain"
            return "application/json"
        return "text/plain"


class ToolField(BaseModel):
    """One input or output of a tool call, without its full value."""

    key: str
    size: int
    mime: str
    preview: str


class ToolCall(BaseModel):
    """One tool call of an assistant turn."""

    id: str
    name: str
    summary: str
    status: ToolStatus
    duration_ms: int | None = Field(
        default=None, description="Not stored in chat.json, so it is always None for now."
    )
    fields: list[ToolField]


class ChatMessage(BaseModel):
    """One message of the chat. An assistant message has the tool calls of its turn."""

    id: str
    role: Role
    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    question: Question | None = None


@dataclass
class _RawCall:
    """A tool call as chat.json stores it: its arguments and, once it ran, its output."""

    id: str
    name: str
    arguments: dict[str, object]
    output: str | None = None

    @property
    def values(self) -> dict[str, FieldValue]:
        """Every input (``input.<name>``) and the output (``output``) as full values."""
        values = {f"input.{key}": FieldValue.of(value) for key, value in self.arguments.items()}
        if self.output is not None:
            values["output"] = FieldValue.of(self.output)
        return values

    @property
    def summary(self) -> str:
        """One short line: the question for a question call, else the start of the output."""
        question = self.question
        text = question.question if question is not None else (self.output or "")
        line = " ".join(text.split())[:SUMMARY_CHARS]
        return line or self.name

    @property
    def question(self) -> Question | None:
        """The question that this call asks, or ``None`` for any other tool."""
        if self.name != QUESTION_TOOL or "question" not in self.arguments:
            return None
        try:
            return Question.model_validate(self.arguments)
        except ValidationError:
            return None

    def to_tool_call(self, *, running: bool) -> ToolCall:
        """Describe the call. A call without output is running, or interrupted when no turn runs."""
        if self.output is not None:
            status: ToolStatus = "done"
        else:
            status = "running" if running else "error"
        fields = [
            ToolField(key=key, size=v.size, mime=v.mime, preview=v.preview)
            for key, v in self.values.items()
        ]
        return ToolCall(
            id=self.id, name=self.name, summary=self.summary, status=status, fields=fields
        )


@dataclass
class _Turn:
    """The items of one message: a user text, or the calls and the text of one assistant turn."""

    id: str
    role: Role
    texts: list[str] = field(default_factory=list)
    calls: list[_RawCall] = field(default_factory=list)

    @property
    def question(self) -> Question | None:
        """The last question that a call of this turn asks."""
        asked = [q for call in self.calls if (q := call.question) is not None]
        return asked[-1] if asked else None

    def to_message(self, *, running: bool) -> ChatMessage:
        """Build the message of this turn."""
        return ChatMessage(
            id=self.id,
            role=self.role,
            text="\n\n".join(self.texts),
            tool_calls=[call.to_tool_call(running=running) for call in self.calls],
            question=self.question,
        )


class ChatTranscript:
    """The chat of a project as the UI shows it, read from the items of chat.json.

    chat.json holds SDK items. A user item starts a user message. The function calls, their
    outputs and the text items that follow it make one assistant message. Reasoning is skipped.
    """

    def __init__(self, items: Sequence[Item], *, running: bool = False) -> None:
        self._running = running
        self._turns = self._parse(items)

    @property
    def running(self) -> bool:
        """Whether a chat turn runs now."""
        return self._running

    @property
    def messages(self) -> list[ChatMessage]:
        """The messages, oldest first. A message id is ``m<index of its first item>``."""
        last = len(self._turns) - 1
        return [
            turn.to_message(running=self._running and i == last)
            for i, turn in enumerate(self._turns)
        ]

    @property
    def pending_question(self) -> Question | None:
        """The question that waits: the last message asks it and no user message follows."""
        if not self._turns or self._turns[-1].role != "assistant":
            return None
        return self._turns[-1].question

    def values_of(self, call_id: str) -> dict[str, FieldValue] | None:
        """Return the full values of tool call ``call_id`` by key, or ``None`` for an unknown id."""
        for turn in self._turns:
            for call in turn.calls:
                if call.id == call_id:
                    return call.values
        return None

    @classmethod
    def _parse(cls, items: Sequence[Item]) -> list[_Turn]:
        """Group the items into turns."""
        turns: list[_Turn] = []
        calls: dict[str, _RawCall] = {}
        current: _Turn | None = None
        for index, item in enumerate(items):
            kind, role = item.get("type"), item.get("role")
            if role == "user":
                turns.append(_Turn(f"m{index}", "user", [cls._text_of(item.get("content"))]))
                current = None
                continue
            if kind not in ("function_call", "function_call_output") and role != "assistant":
                continue
            if current is None:
                current = _Turn(f"m{index}", "assistant")
                turns.append(current)
            if kind == "function_call":
                call = _RawCall(
                    id=str(item.get("call_id", "")),
                    name=str(item.get("name", "")),
                    arguments=cls._arguments_of(item.get("arguments")),
                )
                calls[call.id] = call
                current.calls.append(call)
            elif kind == "function_call_output":
                matching = calls.get(str(item.get("call_id", "")))
                if matching is not None:
                    matching.output = FieldValue.of(item.get("output", "")).content
            elif text := cls._text_of(item.get("content")):
                current.texts.append(text)
        return turns

    @staticmethod
    def _text_of(content: object) -> str:
        """Return the text of a message content: a string, or a list of text parts."""
        if isinstance(content, str):
            return content
        if not isinstance(content, list):
            return ""
        parts = [p.get("text") for p in content if isinstance(p, dict)]
        return "".join(part for part in parts if isinstance(part, str))

    @staticmethod
    def _arguments_of(arguments: object) -> dict[str, object]:
        """Return the arguments of a call as a dict. A bad value gives an empty dict."""
        if not isinstance(arguments, str):
            return {}
        try:
            parsed = json.loads(arguments)
        except ValueError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
