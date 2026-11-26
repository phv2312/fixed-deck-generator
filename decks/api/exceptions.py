from dataclasses import dataclass

from decks.exceptions import AppError


@dataclass(eq=False)
class ContainerNotStartedError(AppError):
    """Raised when a request arrives before the lifespan opened the Container."""

    TEMPLATE = "the app container is not started"
