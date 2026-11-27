from typing import Annotated

from fastapi import Depends, Request

from decks.api.exceptions import ContainerNotStartedError
from decks.container import Container


async def get_container(request: Request) -> Container:
    """Return the Container that the lifespan opened."""
    try:
        return request.app.state.container
    except AttributeError as error:
        raise ContainerNotStartedError from error


ContainerDep = Annotated[Container, Depends(get_container)]
