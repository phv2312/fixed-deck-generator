from typing import Any

from agents import RunContextWrapper

from decks.agents.exceptions import AgentsError

MAX_ERROR_CHARS = 300


def tool_error(ctx: RunContextWrapper[Any], error: Exception) -> str:
    """Tell the model why a tool call failed, so that it can correct the call.

    Use it as ``failure_error_function``. An ``AgentsError`` gives its own message. Any other
    error gives its class name and its message, cut to ``MAX_ERROR_CHARS``.
    """
    if isinstance(error, AgentsError):
        return str(error)
    return f"{type(error).__name__}: {error}"[:MAX_ERROR_CHARS]
