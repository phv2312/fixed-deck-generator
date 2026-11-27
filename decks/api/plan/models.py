from pydantic import BaseModel

from decks.agents.models import Question, VarietyViolation
from decks.models.build import Phase
from decks.models.plan import Plan


class PlanSnapshot(BaseModel):
    """The plan of a project, the phase, the variety advice and the question that waits."""

    plan: Plan
    phase: Phase
    variety: list[VarietyViolation]
    pending_question: Question | None

    @property
    def can_approve(self) -> bool:
        """Whether the plan is complete and waits for approval."""
        return not self.plan.missing and not self.plan.approved
