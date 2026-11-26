from typing import Annotated

from fastapi import APIRouter, Query

from decks.api.deck.deps import DeckServiceDep
from decks.api.deck.openapi.descriptions import DeckDocs
from decks.api.deck.openapi.responses import DeckResponses
from decks.api.deck.payloads import (
    DeckResponse,
    EditResponse,
    ElementCreate,
    ElementDuplicate,
    ElementId,
    ElementOrder,
    ElementUpdate,
)
from decks.api.projects.payloads import ProjectId, SlideIndex

router = APIRouter()

DECK = "/{project_id}/deck"
ELEMENTS = DECK + "/slides/{index}/elements"
ElementPath = ELEMENTS + "/{element_id}"


@router.get(
    DECK,
    summary=DeckDocs.READ.summary,
    description=DeckDocs.READ.description,
    response_model=DeckResponse,
    responses=DeckResponses.READ,
)
async def read_deck(project_id: ProjectId, decks: DeckServiceDep) -> DeckResponse:
    """Return the deck."""
    return DeckResponse.from_info(await decks.get(project_id))


@router.post(
    DECK + "/undo",
    summary=DeckDocs.UNDO.summary,
    description=DeckDocs.UNDO.description,
    response_model=EditResponse,
    responses=DeckResponses.HISTORY,
)
async def undo(project_id: ProjectId, decks: DeckServiceDep) -> EditResponse:
    """Undo the last edit."""
    return EditResponse.from_result(await decks.undo(project_id))


@router.post(
    DECK + "/redo",
    summary=DeckDocs.REDO.summary,
    description=DeckDocs.REDO.description,
    response_model=EditResponse,
    responses=DeckResponses.HISTORY,
)
async def redo(project_id: ProjectId, decks: DeckServiceDep) -> EditResponse:
    """Redo the last undo."""
    return EditResponse.from_result(await decks.redo(project_id))


@router.post(
    ELEMENTS,
    status_code=201,
    summary=DeckDocs.CREATE.summary,
    description=DeckDocs.CREATE.description,
    response_model=EditResponse,
    responses=DeckResponses.CREATE,
)
async def add_element(
    project_id: ProjectId, index: SlideIndex, body: ElementCreate, decks: DeckServiceDep
) -> EditResponse:
    """Add one element."""
    result = await decks.add_element(project_id, index, body.kind, body.props, body.base_revision)
    return EditResponse.from_result(result)


@router.patch(
    ElementPath,
    summary=DeckDocs.UPDATE.summary,
    description=DeckDocs.UPDATE.description,
    response_model=EditResponse,
    responses=DeckResponses.EDIT,
)
async def update_element(
    project_id: ProjectId,
    index: SlideIndex,
    element_id: ElementId,
    body: ElementUpdate,
    decks: DeckServiceDep,
) -> EditResponse:
    """Change one element."""
    result = await decks.update_element(
        project_id, index, element_id, body.changes, body.base_revision
    )
    return EditResponse.from_result(result)


@router.delete(
    ElementPath,
    summary=DeckDocs.DELETE.summary,
    description=DeckDocs.DELETE.description,
    response_model=EditResponse,
    responses=DeckResponses.EDIT,
)
async def delete_element(
    project_id: ProjectId,
    index: SlideIndex,
    element_id: ElementId,
    decks: DeckServiceDep,
    base_revision: Annotated[
        int | None, Query(description="The deck revision that the client saw.")
    ] = None,
) -> EditResponse:
    """Delete one element."""
    result = await decks.delete_element(project_id, index, element_id, base_revision)
    return EditResponse.from_result(result)


@router.post(
    ElementPath + "/duplicate",
    status_code=201,
    summary=DeckDocs.DUPLICATE.summary,
    description=DeckDocs.DUPLICATE.description,
    response_model=EditResponse,
    responses=DeckResponses.CREATE,
)
async def duplicate_element(
    project_id: ProjectId,
    index: SlideIndex,
    element_id: ElementId,
    body: ElementDuplicate,
    decks: DeckServiceDep,
) -> EditResponse:
    """Duplicate one element."""
    result = await decks.duplicate_element(project_id, index, element_id, body.base_revision)
    return EditResponse.from_result(result)


@router.post(
    ElementPath + "/order",
    summary=DeckDocs.ORDER.summary,
    description=DeckDocs.ORDER.description,
    response_model=EditResponse,
    responses=DeckResponses.EDIT,
)
async def reorder_element(
    project_id: ProjectId,
    index: SlideIndex,
    element_id: ElementId,
    body: ElementOrder,
    decks: DeckServiceDep,
) -> EditResponse:
    """Change the stacking order of one element."""
    result = await decks.reorder_element(
        project_id, index, element_id, body.move, body.base_revision
    )
    return EditResponse.from_result(result)
