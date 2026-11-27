from typing import Annotated

from fastapi import Depends

from decks.api.deps import ContainerDep
from decks.api.plan.services import PlanService


async def get_plan_service(container: ContainerDep) -> PlanService:
    """Return the plan service of this request."""
    return PlanService(container.repositories, container.slide_catalog)


PlanServiceDep = Annotated[PlanService, Depends(get_plan_service)]
