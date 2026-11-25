from typing import Any, cast

from agents.items import TResponseInputItem
from agents.run_config import CallModelData, ModelInputData

MAX_OUTPUT_CHARS = 1_000  # a tool output in an earlier turn keeps this many characters
ELIDED_NOTE = "\n...[output shortened to save context]"


class HistoryTrimmer:
    """Cut the cost of the history that the runner sends to the model.

    The session limit can cut the history at any item. Two things then cost context or break the
    request. The oldest items can be a tool output without its call. Tool outputs of earlier turns
    can be large, and the model no longer needs them in full. This class repairs the first and
    shortens the second. The turn in progress is never changed.

    An instance is a ``RunConfig.call_model_input_filter``.
    """

    def __init__(self, *, max_output_chars: int = MAX_OUTPUT_CHARS) -> None:
        self._max_output_chars = max_output_chars

    def __call__(self, data: CallModelData[Any]) -> ModelInputData:
        """Return the model input with a clean start and short old tool outputs."""
        return ModelInputData(
            input=self.trim(data.model_data.input), instructions=data.model_data.instructions
        )

    def trim(self, items: list[TResponseInputItem]) -> list[TResponseInputItem]:
        """Return ``items`` starting at a user message, with old tool outputs shortened."""
        first = self._first_user_index(items)
        last = self._last_user_index(items)
        kept = items[first:]
        return [
            self._shorten(item) if index < last - first else item for index, item in enumerate(kept)
        ]

    @staticmethod
    def _is_user(item: TResponseInputItem) -> bool:
        return cast(dict[str, Any], item).get("role") == "user"

    def _first_user_index(self, items: list[TResponseInputItem]) -> int:
        return next((i for i, item in enumerate(items) if self._is_user(item)), 0)

    def _last_user_index(self, items: list[TResponseInputItem]) -> int:
        return next((i for i in reversed(range(len(items))) if self._is_user(items[i])), 0)

    def _shorten(self, item: TResponseInputItem) -> TResponseInputItem:
        raw = cast(dict[str, Any], item)
        output = raw.get("output")
        if raw.get("type") != "function_call_output" or not isinstance(output, str):
            return item
        if len(output) <= self._max_output_chars:
            return item
        return cast(
            TResponseInputItem, {**raw, "output": output[: self._max_output_chars] + ELIDED_NOTE}
        )
