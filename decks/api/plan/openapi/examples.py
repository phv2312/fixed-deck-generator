from typing import ClassVar

from decks.api.payloads import QuestionResponse
from decks.api.plan.payloads import PlanResponse, PlanSlideResponse


class PlanExamples:
    """Response examples of the plan endpoints. A wrong example fails at import."""

    READ: ClassVar[PlanResponse] = PlanResponse(
        phase="review",
        revision=4,
        approved=False,
        can_approve=True,
        theme="green",
        meta={"audience": "Sales team", "tone": "plain"},
        slides=[
            PlanSlideResponse(
                id="p1",
                kind="title",
                purpose="Open the deck",
                title="Autumn launch",
                summary="What is new this autumn.",
                points=[],
            )
        ],
        missing=[],
        variety=[],
        pending_question=None,
    )
    ASKING: ClassVar[PlanResponse] = PlanResponse(
        phase="interviewing",
        revision=0,
        approved=False,
        can_approve=False,
        theme="green",
        meta={},
        slides=[],
        missing=["audience", "slides"],
        variety=[],
        pending_question=QuestionResponse(
            question="Who is the deck for?",
            options=["Students", "ML engineers"],
            allow_multiple=False,
            free_text=True,
        ),
    )
