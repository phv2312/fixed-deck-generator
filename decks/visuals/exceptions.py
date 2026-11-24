"""Errors of the visual pipeline."""

from dataclasses import dataclass, fields
from typing import ClassVar


@dataclass
class VisualError(Exception):
    """Base class of visual errors. Subclasses set ``TEMPLATE`` and typed fields."""

    TEMPLATE: ClassVar[str] = "visual error"

    def __str__(self) -> str:
        return self.TEMPLATE.format(**{f.name: getattr(self, f.name) for f in fields(self)})


@dataclass
class ChromeNotFoundError(VisualError):
    """Raised when no Chrome or Chromium executable exists."""

    TEMPLATE = "Chrome or Chromium is not installed"


@dataclass
class ChromeFailedError(VisualError):
    """Raised when Chrome exits with an error or does not create its output."""

    TEMPLATE = "Chrome failed during {step}: {detail}"
    step: str
    detail: str


@dataclass
class ChromeTimeoutError(VisualError):
    """Raised when Chrome does not end in time."""

    TEMPLATE = "Chrome did not end in {seconds} seconds during {step}"
    step: str
    seconds: float


@dataclass
class AssetPathError(VisualError):
    """Raised when a path is not a project asset path."""

    TEMPLATE = "{path} is not an asset path; use assets/v<number>.png"
    path: str


@dataclass
class AssetMissingError(VisualError):
    """Raised when an asset file does not exist."""

    TEMPLATE = "asset {path} does not exist"
    path: str


@dataclass
class PageTemplateError(VisualError):
    """Raised when a Chrome page template cannot be rendered."""

    TEMPLATE = "page template {name} failed: {detail}"
    name: str
    detail: str
