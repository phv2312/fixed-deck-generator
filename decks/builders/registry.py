"""Builder lookup by slide type."""

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from types import ModuleType
from typing import Any

from decks.builders.base import BaseBuilder
from decks.builders.exceptions import DuplicateSlideTypeError


@dataclass(frozen=True)
class RegisteredBuilder:
    """One builder instance and the family that owns it."""

    builder: BaseBuilder[Any]
    family: str


class Registry(Mapping[str, RegisteredBuilder]):
    """Registered builders keyed by slide type.

    ``families`` are the family packages. Each one has a ``FAMILY`` name and a ``BUILDERS`` list.
    Each builder is created once, when the registry is built.
    """

    def __init__(self, families: Iterable[ModuleType]) -> None:
        self._by_kind: dict[str, RegisteredBuilder] = {}
        self._families: list[str] = []
        for module in families:
            name: str = module.FAMILY
            self._families.append(name)
            for builder_class in module.BUILDERS:
                if builder_class.TYPE in self._by_kind:
                    raise DuplicateSlideTypeError(builder_class.TYPE)
                self._by_kind[builder_class.TYPE] = RegisteredBuilder(builder_class(), name)

    def family_of(self, kind: str) -> str:
        """Return the family name for ``kind``. Raise ``KeyError`` when unknown."""
        return self._by_kind[kind].family

    @property
    def families(self) -> tuple[str, ...]:
        """Family names in registry order."""
        return tuple(self._families)

    def __getitem__(self, kind: str) -> RegisteredBuilder:
        return self._by_kind[kind]

    def __iter__(self) -> Iterator[str]:
        return iter(self._by_kind)

    def __len__(self) -> int:
        return len(self._by_kind)
