from fastapi import APIRouter

from decks.api.plan.deps import PlanServiceDep
from decks.api.plan.openapi.descriptions import PlanDocs
from decks.api.plan.openapi.responses import PlanResponses
from decks.api.plan.payloads import PlanResponse
from decks.api.projects.payloads import ProjectId

router = APIRouter()


@router.get(
    "/{project_id}/plan",
    summary=PlanDocs.READ.summary,
    description=PlanDocs.READ.description,
    response_model=PlanResponse,
    responses=PlanResponses.READ,
)
async def read_plan(project_id: ProjectId, plans: PlanServiceDep) -> PlanResponse:
    """Return the plan of a project."""
    return PlanResponse.from_snapshot(await plans.get(project_id))


@router.post(
    "/{project_id}/plan/approve",
    summary=PlanDocs.APPROVE.summary,
    description=PlanDocs.APPROVE.description,
    response_model=PlanResponse,
    responses=PlanResponses.APPROVE,
)
async def approve_plan(project_id: ProjectId, plans: PlanServiceDep) -> PlanResponse:
    """Approve the plan of a project."""
    return PlanResponse.from_snapshot(await plans.approve(project_id))
