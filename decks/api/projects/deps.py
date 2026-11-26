from typing import Annotated

from fastapi import Depends

from decks.api.deps import ContainerDep
from decks.api.projects.services import ProjectService


async def get_project_service(container: ContainerDep) -> ProjectService:
    """Return the project service of this request."""
    return ProjectService(container.repositories)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
