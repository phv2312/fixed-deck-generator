from decks.api.chat.models import ChatTranscript, FieldValue
from tests.api.chat.conftest import QUESTION_ARGS, SVG, assistant, call, output


def user(text: str) -> dict[str, object]:
    """Return a user item."""
    return {"role": "user", "content": text}


def test_groups_items_into_messages() -> None:
    """Test that user items and assistant items become alternating messages."""
    transcript = ChatTranscript(
        [
            user("hi"),
            {"type": "reasoning", "id": "r1", "summary": []},
            call("c1", "set_meta", {"key": "audience"}),
            output("c1", "ok"),
            assistant("Done."),
            user("thanks"),
        ]
    )
    messages = transcript.messages
    assert [(m.id, m.role, m.text) for m in messages] == [
        ("m0", "user", "hi"),
        ("m2", "assistant", "Done."),
        ("m5", "user", "thanks"),
    ]
    assert [c.name for c in messages[1].tool_calls] == ["set_meta"]


def test_tool_call_has_summary_status_and_field_refs() -> None:
    """Test that a finished call has a short summary and fields with size, mime and preview."""
    transcript = ChatTranscript(
        [user("go"), call("c1", "make_picture", {"svg": SVG}), output("c1", "ok\nsecond line")]
    )
    (tool,) = transcript.messages[1].tool_calls
    assert (tool.status, tool.summary, tool.duration_ms) == ("done", "ok second line", None)
    by_key = {f.key: f for f in tool.fields}
    assert by_key["input.svg"].mime == "image/svg+xml"
    assert by_key["input.svg"].size == len(SVG.encode())
    assert by_key["input.svg"].preview == SVG[:200]
    assert by_key["output"].mime == "text/plain"


def test_call_without_output_is_running_or_error() -> None:
    """Test that an unfinished call is running during a turn and an error after it stopped."""
    items = [user("go"), call("c1", "slow", {})]
    assert ChatTranscript(items, running=True).messages[1].tool_calls[0].status == "running"
    assert ChatTranscript(items, running=False).messages[1].tool_calls[0].status == "error"


def test_question_is_pending_until_the_user_answers() -> None:
    """Test that an unanswered question is pending and an answer clears it."""
    asked = [user("go"), call("c1", "ask_user_question", QUESTION_ARGS), output("c1", "question=")]
    transcript = ChatTranscript(asked)
    question = transcript.messages[1].question
    assert question is not None
    assert question.options == ["Students", "ML engineers"]
    assert transcript.messages[1].tool_calls[0].summary == "Who is the deck for?"
    assert transcript.pending_question == question
    assert ChatTranscript([*asked, user("Students")]).pending_question is None


def test_bad_arguments_do_not_break_the_transcript() -> None:
    """Test that a call with arguments that are not JSON still shows, without fields."""
    broken = {"type": "function_call", "call_id": "c1", "name": "x", "arguments": "{oops"}
    (tool,) = ChatTranscript([user("go"), broken]).messages[1].tool_calls
    assert tool.fields == []


def test_values_of_gives_full_values() -> None:
    """Test that the full value of a field is not cut."""
    transcript = ChatTranscript([user("go"), call("c1", "pic", {"svg": SVG, "n": 3})])
    values = transcript.values_of("c1")
    assert values is not None
    assert values["input.svg"].content == SVG
    assert values["input.n"] == FieldValue(content="3", mime="application/json")
    assert transcript.values_of("nope") is None
