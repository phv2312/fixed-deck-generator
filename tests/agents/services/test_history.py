from typing import Any, cast

import pytest
from agents.items import TResponseInputItem

from decks.agents.services.history import ELIDED_NOTE, HistoryTrimmer


def _user(text: str) -> TResponseInputItem:
    return cast(TResponseInputItem, {"role": "user", "content": text})


def _call(call_id: str) -> TResponseInputItem:
    return cast(
        TResponseInputItem,
        {"type": "function_call", "call_id": call_id, "name": "t", "arguments": "{}"},
    )


def _output(call_id: str, text: str) -> TResponseInputItem:
    return cast(
        TResponseInputItem, {"type": "function_call_output", "call_id": call_id, "output": text}
    )


def _outputs(items: list[TResponseInputItem]) -> list[str]:
    return [cast(dict[str, Any], i)["output"] for i in items if "output" in i]


def test_drops_items_before_the_first_user_message() -> None:
    """An output whose call was cut off by the session limit is removed."""
    items = [_output("c0", "orphan"), _user("hi"), _call("c1"), _output("c1", "ok")]
    assert HistoryTrimmer().trim(items) == items[1:]


def test_keeps_items_when_there_is_no_user_message() -> None:
    """Without a user message there is no safe start, so nothing is dropped."""
    items = [_call("c1"), _output("c1", "ok")]
    assert HistoryTrimmer().trim(items) == items


@pytest.mark.parametrize(
    ("turn", "expected_shortened"),
    [
        ("old", True),
        ("current", False),
    ],
)
def test_shortens_only_outputs_of_earlier_turns(turn: str, expected_shortened: bool) -> None:
    """A long output is cut in an earlier turn and kept whole in the current turn."""
    big = "x" * 50
    items = [_user("a"), _call("c1"), _output("c1", big), _user("b")]
    if turn == "current":
        items = [_user("a"), _user("b"), _call("c1"), _output("c1", big)]
    result = _outputs(HistoryTrimmer(max_output_chars=10).trim(items))
    assert result == (["x" * 10 + ELIDED_NOTE] if expected_shortened else [big])


def test_short_outputs_are_unchanged() -> None:
    """An output under the limit is returned as it is."""
    items = [_user("a"), _call("c1"), _output("c1", "short"), _user("b")]
    assert HistoryTrimmer(max_output_chars=10).trim(items) == items
