"""Shared contract for every slide builder."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from pydantic import BaseModel

from decks.models.elements import Element


@dataclass(frozen=True)
class BuilderSchema:
    """Machine-readable description of a builder for tool/LLM selection."""

    description: str
    spec: dict[str, Any]


class BaseBuilder[SpecT: BaseModel](ABC):
    """Base class for a slide builder.

    Each subclass owns one slide type: it declares the registry key, the
    LLM-facing description, the spec model it consumes, and renders that spec
    into positioned elements.
    """

    TYPE: ClassVar[str]
    DESCRIPTION: ClassVar[str]
    SPEC: type[SpecT]

    @abstractmethod
    def build(self, spec: SpecT) -> list[Element]:
        """Render ``spec`` into positioned slide elements."""

    @classmethod
    def builder_schema(cls) -> BuilderSchema:
        """Return the builder description and JSON schema of its spec."""
        return BuilderSchema(
            description=cls.DESCRIPTION,
            spec=cls.SPEC.model_json_schema(),
        )
