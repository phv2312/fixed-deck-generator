from typing import Annotated

from fastapi import APIRouter, Query, Response
from fastapi.responses import StreamingResponse

from decks.api.chat.deps import ChatHistoryServiceDep, ChatTurnServiceDep
from decks.api.chat.openapi.descriptions import ChatDocs
from decks.api.chat.openapi.responses import ChatResponses
from decks.api.chat.payloads import (
    CallId,
    ChatHistoryResponse,
    ChatMessageCreate,
    FieldKey,
    ServerSentEvents,
)
from decks.api.projects.payloads import ProjectId

router = APIRouter()

STREAM_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}
VALUE_HEADERS = {
    "Content-Security-Policy": "sandbox; default-src 'none'",
    "X-Content-Type-Options": "nosniff",
}


@router.post(
    "/{project_id}/chat",
    summary=ChatDocs.SEND.summary,
    description=ChatDocs.SEND.description,
    response_class=StreamingResponse,
    responses=ChatResponses.SEND,
)
async def send_chat_message(
    project_id: ProjectId, body: ChatMessageCreate, turns: ChatTurnServiceDep
) -> StreamingResponse:
    """Run one chat turn and stream its events."""
    events = await turns.start(project_id, body.message)
    return StreamingResponse(
        ServerSentEvents(events), media_type="text/event-stream", headers=STREAM_HEADERS
    )


@router.get(
    "/{project_id}/chat",
    summary=ChatDocs.HISTORY.summary,
    description=ChatDocs.HISTORY.description,
    response_model=ChatHistoryResponse,
    responses=ChatResponses.HISTORY,
)
async def read_chat_history(
    project_id: ProjectId, chat: ChatHistoryServiceDep
) -> ChatHistoryResponse:
    """Return the chat of a project."""
    transcript = await chat.transcript(project_id)
    return ChatHistoryResponse.from_transcript(transcript, project_id=project_id)


@router.get(
    "/{project_id}/tool-calls/{call_id}/fields/{key}",
    summary=ChatDocs.FIELD.summary,
    description=ChatDocs.FIELD.description,
    response_class=Response,
    responses=ChatResponses.FIELD,
)
async def read_tool_field(
    project_id: ProjectId,
    call_id: CallId,
    key: FieldKey,
    chat: ChatHistoryServiceDep,
    *,
    download: Annotated[bool, Query(description="Send the value as a file download.")] = False,
) -> Response:
    """Return the full value of one tool field."""
    value = await chat.field(project_id, call_id, key)
    headers = dict(VALUE_HEADERS)
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{call_id}-{key}.{value.extension}"'
    return Response(value.content, media_type=value.mime, headers=headers)
