from dataclasses import dataclass, fields
from typing import ClassVar


@dataclass
class PromptingError(Exception):
    """Base class of every prompt template error. Subclasses set ``TEMPLATE`` and typed fields."""

    TEMPLATE: ClassVar[str] = "prompt template error"

    def __str__(self) -> str:
        return self.TEMPLATE.format(**{f.name: getattr(self, f.name) for f in fields(self)})


@dataclass
class PromptTemplateNotFoundError(PromptingError):
    """Raised when a prompt template does not exist in the template directory."""

    TEMPLATE = "prompt template {name} not found in {directory}"
    name: str
    directory: str


@dataclass
class PromptVariableMissingError(PromptingError):
    """Raised when a prompt template uses a variable that the caller did not give."""

    TEMPLATE = "prompt template {name} needs a value: {detail}"
    name: str
    detail: str
