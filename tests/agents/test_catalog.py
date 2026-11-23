"""Tests for the slide catalog."""

import pytest

from decks.agents.catalog import KIND_ALIASES, SlideCatalog


def test_aliases_point_to_registered_kinds() -> None:
    """Every alias names a kind that the registry has, and no alias shadows a live kind."""
    catalog = SlideCatalog()
    assert all(target in catalog for target in KIND_ALIASES.values())
    assert not any(old in catalog for old in KIND_ALIASES)


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("agenda_list", "agenda"),
        ("roadmap", "gantt"),
        ("title", "title"),
        ("unknown", "unknown"),
        (None, None),
    ],
)
def test_resolve_follows_aliases(kind: str | None, expected: str | None) -> None:
    """A merged kind resolves to its successor. Other kinds stay as they are."""
    assert SlideCatalog().resolve(kind) == expected
