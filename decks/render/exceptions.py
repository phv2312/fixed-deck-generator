from dataclasses import dataclass, fields
from typing import ClassVar


@dataclass
class RenderError(Exception):
    """Base class of render errors. Subclasses set ``TEMPLATE`` and typed fields."""

    TEMPLATE: ClassVar[str] = "render error"

    def __str__(self) -> str:
        return self.TEMPLATE.format(**{f.name: getattr(self, f.name) for f in fields(self)})


@dataclass
class UnsupportedElementError(RenderError):
    """Raised when a renderer receives an element type that it does not know."""

    TEMPLATE = "unsupported element type: {element_type}"
    element_type: str


@dataclass
class GalleryTemplateError(RenderError):
    """Raised when the gallery template cannot be rendered."""

    TEMPLATE = "gallery template {name} failed: {detail}"
    name: str
    detail: str
