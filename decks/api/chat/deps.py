from typing import Annotated

from fastapi import Depends

from decks.agents import ProjectRunner
from decks.api.chat.services import ChatHistoryService, ChatTurnService
from decks.api.deps import ContainerDep


async def get_chat_history_service(container: ContainerDep) -> ChatHistoryService:
    """Return the chat history service of this request."""
    return ChatHistoryService(container.repositories)


ChatHistoryServiceDep = Annotated[ChatHistoryService, Depends(get_chat_history_service)]


async def get_runner(container: ContainerDep) -> ProjectRunner:
    """Return the chat-turn runner. It builds the model client on first use."""
    return container.runner


RunnerDep = Annotated[ProjectRunner, Depends(get_runner)]


async def get_chat_turn_service(container: ContainerDep, runner: RunnerDep) -> ChatTurnService:
    """Return the chat turn service of this request."""
    return ChatTurnService(
        container.repositories, runner, container.slide_catalog, container.run_config
    )


ChatTurnServiceDep = Annotated[ChatTurnService, Depends(get_chat_turn_service)]
