import asyncio
import os
from pathlib import Path

from pydantic import BaseModel, ValidationError

from decks.agents.exceptions import ArtifactCorruptError


class ProjectLocks:
    """One asyncio lock per project. Create one instance at start-up and share it."""

    def __init__(self) -> None:
        self._locks: dict[str, asyncio.Lock] = {}
        self._turn_locks: dict[str, asyncio.Lock] = {}

    def turn(self, project_id: str) -> asyncio.Lock:
        """Return the chat-turn lock of ``project_id``. It is separate from ``get``."""
        return self._turn_locks.setdefault(project_id, asyncio.Lock())

    def get(self, project_id: str) -> asyncio.Lock:
        """Return the lock of ``project_id``. Create it on first use."""
        return self._locks.setdefault(project_id, asyncio.Lock())


class ModelRepository[T: BaseModel]:
    """Persist one pydantic model in one JSON file. Use it for the plan and for the deck."""

    def __init__(self, model: type[T], store: "AtomicJsonStore") -> None:
        self._model = model
        self._store = store

    def load(self) -> T | None:
        """Return the stored value, or ``None`` when there is none."""
        return self._store.read_model(self._model)

    def save(self, value: T) -> None:
        """Write ``value``."""
        self._store.write_model(value)

    def delete(self) -> None:
        """Remove the stored value."""
        self._store.delete()


class AtomicJsonStore:
    """Read and write one JSON file. A write goes to a temp file, then replaces the target."""

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        """File that this store owns."""
        return self._path

    def exists(self) -> bool:
        """Return ``True`` when the file exists."""
        return self._path.is_file()

    def read_model[T: BaseModel](self, model: type[T]) -> T | None:
        """Return the file as ``model``, or ``None`` when it does not exist."""
        if not self.exists():
            return None
        try:
            return model.model_validate_json(self._path.read_text())
        except ValidationError as exc:
            raise ArtifactCorruptError(str(self._path)) from exc

    def write_model(self, value: BaseModel) -> None:
        """Atomically write ``value`` as indented JSON."""
        self.write_text(value.model_dump_json(indent=2))

    def read_text(self) -> str | None:
        """Return the raw text, or ``None`` when the file does not exist."""
        return self._path.read_text() if self.exists() else None

    def write_text(self, text: str) -> None:
        """Atomically write ``text``."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_name(self._path.name + ".tmp")
        tmp.write_text(text)
        os.replace(tmp, self._path)

    def write_bytes(self, data: bytes) -> None:
        """Atomically write ``data``."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_name(self._path.name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, self._path)

    def delete(self) -> None:
        """Remove the file when it exists."""
        self._path.unlink(missing_ok=True)
