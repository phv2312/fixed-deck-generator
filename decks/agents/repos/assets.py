import re
from pathlib import Path

from decks.agents.repos.base import AtomicJsonStore
from decks.visuals.exceptions import AssetMissingError, AssetPathError
from decks.visuals.models import VisualManifest

ASSET_DIR = "assets"
_ASSET_PATH = re.compile(rf"^{ASSET_DIR}/(v\d+)\.png$")


class AssetRepository:
    """Persist the visuals of one project in its ``assets`` folder.

    Each visual has three files: ``<id>.svg`` (the source), ``<id>.png`` (the render) and
    ``<id>.json`` (the manifest).
    """

    def __init__(self, folder: Path) -> None:
        self._folder = folder

    @staticmethod
    def is_asset_path(path: str) -> bool:
        """Return ``True`` when ``path`` has the form ``assets/v<number>.png``."""
        return _ASSET_PATH.match(path) is not None

    def next_id(self) -> str:
        """Return an unused id: ``v`` and one more than the highest number in use."""
        numbers = [int(p.stem[1:]) for p in self._folder.glob("v*.json") if p.stem[1:].isdigit()]
        return f"v{max(numbers, default=0) + 1}"

    def relative_path(self, visual_id: str) -> str:
        """Return the path that the plan stores, such as ``assets/v1.png``."""
        return f"{ASSET_DIR}/{visual_id}.png"

    def resolve(self, path: str) -> Path:
        """Return the absolute PNG file of a stored path.

        Raise ``AssetPathError`` when ``path`` is not an asset path, and ``AssetMissingError``
        when the file or its manifest does not exist.
        """
        match = _ASSET_PATH.match(path)
        if match is None:
            raise AssetPathError(path)
        visual_id = match.group(1)
        png = self._folder / f"{visual_id}.png"
        if not png.is_file() or not self._manifest_store(visual_id).exists():
            raise AssetMissingError(path)
        return png

    def save(self, manifest: VisualManifest, svg: str, png: bytes) -> None:
        """Write the three files of a visual. The manifest goes last."""
        self._store(manifest.id, "svg").write_text(svg)
        self._store(manifest.id, "png").write_bytes(png)
        self._manifest_store(manifest.id).write_model(manifest)

    def save_png(self, manifest: VisualManifest, png: bytes) -> None:
        """Replace the PNG and the manifest of a visual. The SVG stays."""
        self._store(manifest.id, "png").write_bytes(png)
        self._manifest_store(manifest.id).write_model(manifest)

    def svg(self, visual_id: str) -> str | None:
        """Return the SVG source, or ``None``."""
        return self._store(visual_id, "svg").read_text()

    def manifests(self) -> list[VisualManifest]:
        """Return every manifest, sorted by id number."""
        found = [self._manifest_store(p.stem).read_model(VisualManifest) for p in self._ids()]
        return [m for m in found if m is not None]

    def _ids(self) -> list[Path]:
        paths = [p for p in self._folder.glob("v*.json") if p.stem[1:].isdigit()]
        return sorted(paths, key=lambda p: int(p.stem[1:]))

    def _store(self, visual_id: str, suffix: str) -> AtomicJsonStore:
        return AtomicJsonStore(self._folder / f"{visual_id}.{suffix}")

    def _manifest_store(self, visual_id: str) -> AtomicJsonStore:
        return self._store(visual_id, "json")
