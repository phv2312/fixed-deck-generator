from dataclasses import dataclass, fields
from typing import ClassVar


@dataclass
class BuilderError(Exception):
    """Base class of builder errors. Subclasses set ``TEMPLATE`` and typed fields."""

    TEMPLATE: ClassVar[str] = "builder error"

    def __str__(self) -> str:
        return self.TEMPLATE.format(**{f.name: getattr(self, f.name) for f in fields(self)})


@dataclass
class DuplicateSlideTypeError(BuilderError):
    """Raised when two builders claim the same slide type."""

    TEMPLATE = "duplicate slide type: {kind}"
    kind: str
