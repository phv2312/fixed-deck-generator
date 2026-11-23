"""Contract tests for every registered slide builder."""

import json
import re
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from decks.builders import FAMILIES, REGISTRY, Registry
from decks.builders.base import BaseBuilder
from decks.models.slides import DeckSpec

EXAMPLES = sorted(Path("examples").glob("*.json"))
BUILDERS_DIR = Path("decks")
BASE_IMPORT = re.compile(r"from \.{2,}")


def _example_specs() -> dict[str, BaseModel]:
    """Return one example spec per slide type, keyed by type."""
    specs: dict[str, BaseModel] = {}
    for path in EXAMPLES:
        raw = json.loads(path.read_text())
        deck = DeckSpec.model_validate({**raw, "theme": "green"})
        for slide in deck.slides:
            specs.setdefault(slide.type, slide)
    return specs


def _missing_descriptions(
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str,
    seen: frozenset[str],
) -> list[str]:
    """Return dotted paths of schema properties that lack a description."""
    if "$ref" in schema:
        ref = str(schema["$ref"])
        if ref in seen:
            return []
        name = ref.rsplit("/", 1)[-1]
        return _missing_descriptions(root["$defs"][name], root, path or name, seen | {ref})

    missing: list[str] = []
    for key in ("anyOf", "oneOf", "allOf"):
        for sub in schema.get(key, []):
            missing += _missing_descriptions(sub, root, path, seen)

    for name, prop in schema.get("properties", {}).items():
        dotted = f"{path}.{name}" if path else name
        if not prop.get("description"):
            missing.append(dotted)
        missing += _missing_descriptions(prop, root, dotted, seen)

    if isinstance(schema.get("items"), dict):
        missing += _missing_descriptions(schema["items"], root, f"{path}[]", seen)

    if isinstance(schema.get("additionalProperties"), dict):
        missing += _missing_descriptions(schema["additionalProperties"], root, f"{path}{{}}", seen)

    return missing


SPECS = _example_specs()


@pytest.mark.parametrize(
    ("kind", "builder"),
    [(kind, registered.builder) for kind, registered in sorted(REGISTRY.items())],
)
def test_builder_contract(kind: str, builder: BaseBuilder[Any]) -> None:
    """Every builder describes itself and renders its example spec into elements."""
    assert builder.TYPE == kind
    assert builder.DESCRIPTION.strip()
    assert issubclass(builder.SPEC, BaseModel)

    schema = builder.builder_schema()
    assert schema.description == builder.DESCRIPTION
    assert "type" in schema.spec["properties"]

    spec = SPECS[kind]
    assert isinstance(spec, builder.SPEC)
    elements = builder.build(spec)
    assert elements


@pytest.mark.parametrize(
    ("kind", "builder"),
    [(kind, registered.builder) for kind, registered in sorted(REGISTRY.items())],
)
def test_every_parameter_is_described(kind: str, builder: BaseBuilder[Any]) -> None:
    """Every input field, including nested model fields, has an LLM-facing description."""
    schema = builder.builder_schema().spec
    assert _missing_descriptions(schema, schema, "", frozenset()) == [], kind


def test_registry_covers_every_family_builder() -> None:
    """The registry is complete, unique and derived from the family exports."""
    builders = [builder_class for family in FAMILIES for builder_class in family.BUILDERS]
    assert len(builders) == len({builder_class.TYPE for builder_class in builders})
    assert set(REGISTRY) == {builder_class.TYPE for builder_class in builders}


def test_registry_family_lookup() -> None:
    """The registry resolves builders per family and keeps the flat mapping intact."""
    registry = Registry(FAMILIES)
    assert registry.families == tuple(family.FAMILY for family in FAMILIES)
    assert len(registry) == len(REGISTRY)

    registered = REGISTRY["decision"]
    assert registry.family_of("decision") == registered.family

    with pytest.raises(KeyError):
        registry.family_of("unknown")


def test_no_parent_relative_imports() -> None:
    """Modules use single-dot (`from .base`) or absolute imports, never `from ..`."""
    offenders = [
        f"{path}:{lineno}"
        for path in sorted(BUILDERS_DIR.rglob("*.py"))
        for lineno, line in enumerate(path.read_text().splitlines(), start=1)
        if BASE_IMPORT.search(line)
    ]
    assert not offenders
