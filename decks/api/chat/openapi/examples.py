from typing import ClassVar, Final

from decks.api.chat.payloads import (
    ChatHistoryResponse,
    ChatMessageResponse,
    ToolCallResponse,
    ToolFieldResponse,
)
from decks.api.payloads import QuestionResponse

QUESTION: Final = QuestionResponse(
    question="Who is the deck for?",
    options=["Students", "ML engineers", "Nontechnical stakeholders"],
    allow_multiple=False,
    free_text=True,
)
FIELD_URL: Final = "/api/v1/projects/4f1c9a2e/tool-calls/call_1/fields/{key}"


class ChatExamples:
    """Examples of the chat endpoints. A wrong example fails at import."""

    HISTORY: ClassVar[ChatHistoryResponse] = ChatHistoryResponse(
        messages=[
            ChatMessageResponse(
                id="m0",
                role="user",
                text="Make a deck for the autumn launch.",
                tool_calls=[],
                question=None,
            ),
            ChatMessageResponse(
                id="m1",
                role="assistant",
                text="",
                tool_calls=[
                    ToolCallResponse(
                        id="call_1",
                        name="ask_user_question",
                        summary="Who is the deck for?",
                        status="done",
                        duration_ms=None,
                        fields=[
                            ToolFieldResponse(
                                key="input.question",
                                size=20,
                                mime="text/plain",
                                preview="Who is the deck for?",
                                url=FIELD_URL.format(key="input.question"),
                            )
                        ],
                    )
                ],
                question=QUESTION,
            ),
        ],
        running=False,
        pending_question=QUESTION,
    )
    STREAM: ClassVar[str] = (
        'event: run_started\ndata: {"type":"run_started","agent":"interview","phase":"draft"}\n\n'
        'event: tool_started\ndata: {"type":"tool_started","name":"set_meta"}\n\n'
        'event: token\ndata: {"type":"token","text":"The plan is ready."}\n\n'
        'event: done\ndata: {"type":"done"}\n\n'
    )
