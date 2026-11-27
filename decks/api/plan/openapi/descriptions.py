from typing import ClassVar

from decks.api.openapi import RouteDoc


class PlanDocs:
    """Swagger text of the plan endpoints."""

    READ: ClassVar[RouteDoc] = RouteDoc(
        "Read the plan",
        "Return the plan of the project: the facts that the interview collected, the planned "
        "slides, what is still missing, the phase, and the question that waits for an answer. A "
        "project without a plan gives an empty plan. To change the plan, send a chat message.",
    )
    APPROVE: ClassVar[RouteDoc] = RouteDoc(
        "Approve the plan",
        "Approve a complete plan. The phase becomes `approved`. After this, ask the agent in the "
        "chat to build the deck. To ask for changes instead, send them as a chat message.",
    )
