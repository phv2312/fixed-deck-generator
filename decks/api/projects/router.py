from typing import Annotated

from fastapi import APIRouter, Query, Response

from decks.api.payloads import PageQuery, PageResponse
from decks.api.projects.deps import ProjectServiceDep
from decks.api.projects.openapi.descriptions import ProjectDocs
from decks.api.projects.openapi.responses import ProjectResponses
from decks.api.projects.payloads import (
    ProjectCreate,
    ProjectId,
    ProjectResponse,
)

router = APIRouter()


@router.get(
    "",
    summary=ProjectDocs.LIST.summary,
    description=ProjectDocs.LIST.description,
    response_model=PageResponse[ProjectResponse],
    responses=ProjectResponses.LIST,
)
async def list_projects(
    page: Annotated[PageQuery, Query()], projects: ProjectServiceDep
) -> PageResponse[ProjectResponse]:
    """Return one page of projects."""
    items, total = await projects.page(limit=page.limit, offset=page.offset)
    return PageResponse(items=[ProjectResponse.from_summary(item) for item in items], total=total)


@router.post(
    "",
    status_code=201,
    summary=ProjectDocs.CREATE.summary,
    description=ProjectDocs.CREATE.description,
    response_model=ProjectResponse,
    responses=ProjectResponses.CREATE,
)
async def create_project(body: ProjectCreate, projects: ProjectServiceDep) -> ProjectResponse:
    """Create one project."""
    return ProjectResponse.from_summary(await projects.create(body.name))


@router.get(
    "/{project_id}",
    summary=ProjectDocs.READ.summary,
    description=ProjectDocs.READ.description,
    response_model=ProjectResponse,
    responses=ProjectResponses.READ,
)
async def read_project(project_id: ProjectId, projects: ProjectServiceDep) -> ProjectResponse:
    """Return one project."""
    return ProjectResponse.from_summary(await projects.get(project_id))


@router.delete(
    "/{project_id}",
    status_code=204,
    summary=ProjectDocs.DELETE.summary,
    description=ProjectDocs.DELETE.description,
    responses=ProjectResponses.DELETE,
)
async def delete_project(project_id: ProjectId, projects: ProjectServiceDep) -> Response:
    """Delete one project."""
    await projects.delete(project_id)
    return Response(status_code=204)
