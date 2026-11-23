from pydantic import BaseModel

from decks.builders import REGISTRY
from decks.builders.base import BaseBuilder
from decks.builders.registry import Registry

# Spec fields use `dict` or a union of shapes, so strict JSON schema output cannot represent them.
NON_STRICT_KINDS = frozenset({"exhibit", "twocharts"})
FALLBACK_KIND = "content"

# Kinds that were merged into another kind. A saved plan that names one still builds.
KIND_ALIASES: dict[str, str] = {
    "agenda_list": "agenda",
    "target": "pyramid",
    "photo": "figure",
    "gallery": "figure",
    "quote": "statement",
    "bignumber": "statement",
    "icons": "panels",
    "team": "contact",
    "checklist": "steps",
    "phases": "process",
    "gates": "process",
    "roadmap": "gantt",
    "heatmap": "evaluation",
    "growth": "exhibit",
    "benchmark": "exhibit",
    "butterfly": "exhibit",
    "progress": "tracker",
    "nownextlater": "panels",
    "forcefield": "forandagainst",
    "kanban": "panels",
}


class SlideCatalog:
    """Describe the slide kinds of a registry, for prompts and validation."""

    def __init__(self, registry: Registry = REGISTRY) -> None:
        self._registry = registry

    def __contains__(self, kind: object) -> bool:
        return kind in self._registry

    def resolve(self, kind: str | None) -> str | None:
        """Return the registered kind for ``kind``, following an alias of a merged kind."""
        if kind is None:
            return None
        return kind if kind in self._registry else KIND_ALIASES.get(kind, kind)

    def builder(self, kind: str) -> BaseBuilder[BaseModel]:
        """Return the builder of ``kind``."""
        return self._registry[kind].builder

    def family_of(self, kind: str) -> str:
        """Return the family name of ``kind``."""
        return self._registry.family_of(kind)

    def required_fields(self, kind: str) -> list[str]:
        """Return the required spec fields of ``kind``, without the type discriminator."""
        schema = self._registry[kind].builder.SPEC.model_json_schema()
        return [f for f in schema.get("required", []) if f != "type"]

    def strict(self, kind: str) -> bool:
        """Return whether the spec of ``kind`` can use strict JSON schema output."""
        return kind not in NON_STRICT_KINDS

    @property
    def prompt(self) -> str:
        """One line per kind: ``family/kind: description [required fields]``."""
        lines = []
        for kind in self._registry:
            builder = self.builder(kind)
            required = ", ".join(self.required_fields(kind))
            lines.append(f"- {kind}: {builder.DESCRIPTION} [needs: {required}]")
        return "\n".join(lines)
