from pathlib import Path

import pytest

from decks.agents.repos.assets import AssetRepository
from decks.visuals.exceptions import AssetMissingError, AssetPathError
from decks.visuals.models import VisualManifest


def _manifest(visual_id: str) -> VisualManifest:
    return VisualManifest(id=visual_id, kind="diagram", alt="a", theme="green")


@pytest.fixture
def assets(tmp_path: Path) -> AssetRepository:
    """Asset repository in a temp folder."""
    return AssetRepository(tmp_path / "assets")


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("assets/v1.png", True),
        ("assets/v12.png", True),
        ("assets/v1.svg", False),
        ("assets/../v1.png", False),
        ("/tmp/assets/v1.png", False),
        ("https://x.test/assets/v1.png", False),
        ("v1.png", False),
    ],
)
def test_is_asset_path(path: str, expected: bool) -> None:
    """Only the exact form assets/v<number>.png is an asset path."""
    assert AssetRepository.is_asset_path(path) is expected


def test_next_id_follows_highest(assets: AssetRepository) -> None:
    """The next id is one above the highest manifest, so a gap is not reused."""
    assert assets.next_id() == "v1"
    assets.save(_manifest("v1"), "<svg/>", b"png")
    assets.save(_manifest("v4"), "<svg/>", b"png")
    assert assets.next_id() == "v5"
    assert [m.id for m in assets.manifests()] == ["v1", "v4"]


def test_resolve_errors(assets: AssetRepository) -> None:
    """A bad path and a missing file raise their own errors."""
    with pytest.raises(AssetPathError):
        assets.resolve("../x.png")
    with pytest.raises(AssetMissingError):
        assets.resolve("assets/v1.png")


def test_resolve_needs_manifest(assets: AssetRepository, tmp_path: Path) -> None:
    """A PNG without a manifest is not a usable asset."""
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "v1.png").write_bytes(b"png")
    with pytest.raises(AssetMissingError):
        assets.resolve("assets/v1.png")


def test_save_png_keeps_svg(assets: AssetRepository) -> None:
    """Replacing the PNG leaves the SVG source as it is."""
    assets.save(_manifest("v1"), "<svg/>", b"old")
    assets.save_png(_manifest("v1").model_copy(update={"theme": "orange"}), b"new")
    assert assets.svg("v1") == "<svg/>"
    assert assets.resolve("assets/v1.png").read_bytes() == b"new"
    assert assets.manifests()[0].theme == "orange"
