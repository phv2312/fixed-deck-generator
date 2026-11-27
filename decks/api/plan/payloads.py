from typing import Self

from pydantic import BaseModel, Field

from decks.api.payloads import QuestionResponse
from decks.api.plan.models import PlanSnapshot
from decks.models.build import Phase
from decks.models.plan import SlideDraft


class PlanSlideResponse(BaseModel):
    """One slide of the plan."""

    id: str = Field(description="Id of the plan slide.")
    kind: str | None = Field(description="Slide kind from the catalog, or null while undecided.")
    purpose: str = Field(description="Why the slide exists.")
    title: str = Field(description="Slide title.")
    summary: str = Field(description="One or two sentences of the key message. May be empty.")
    points: list[str] = Field(description="Key points of the slide. May be empty.")

    @classmethod
    def from_draft(cls, draft: SlideDraft) -> Self:
        """Build the response from a slide draft."""
        return cls(
            id=draft.id,
            kind=draft.kind,
            purpose=draft.purpose,
            title=draft.title,
            summary=draft.content.summary,
            points=draft.content.points,
        )


class PlanResponse(BaseModel):
    """Response body for the plan of a project."""

    phase: Phase = Field(description="Phase of the project.")
    revision: int = Field(description="Plan revision. 0 before the first plan change.")
    approved: bool = Field(description="Whether the user approved the plan.")
    can_approve: bool = Field(description="Whether the plan is complete and not yet approved.")
    theme: str = Field(description="Theme name.")
    meta: dict[str, str] = Field(
        description="Facts that the interview collected, such as audience."
    )
    slides: list[PlanSlideResponse] = Field(description="The planned slides, in order.")
    missing: list[str] = Field(description="What the plan still lacks: meta keys or `slides`.")
    variety: list[str] = Field(description="Advice about the variety of slide kinds.")
    pending_question: QuestionResponse | None = Field(
        description="The question that waits for an answer, or null."
    )

    @classmethod
    def from_snapshot(cls, snapshot: PlanSnapshot) -> Self:
        """Build the response from a plan snapshot."""
        plan, question = snapshot.plan, snapshot.pending_question
        return cls(
            phase=snapshot.phase,
            revision=plan.revision,
            approved=plan.approved,
            can_approve=snapshot.can_approve,
            theme=plan.theme,
            meta=plan.meta,
            slides=[PlanSlideResponse.from_draft(d) for d in plan.slides],
            missing=plan.missing,
            variety=[v.line for v in snapshot.variety],
            pending_question=QuestionResponse.from_question(question) if question else None,
        )
