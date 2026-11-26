from dataclasses import dataclass, fields
from http import HTTPStatus
from typing import ClassVar


@dataclass(eq=False)
class AppError(Exception):
    """Base class of all app errors. The class name is the public error code of the HTTP API."""

    TEMPLATE: ClassVar[str] = "app error"
    STATUS_CODE: ClassVar[HTTPStatus] = HTTPStatus.INTERNAL_SERVER_ERROR

    def __str__(self) -> str:
        return self.TEMPLATE.format(**{f.name: getattr(self, f.name) for f in fields(self)})
