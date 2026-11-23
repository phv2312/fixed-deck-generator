from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from decks.agents.repos.assets import AssetRepository
from decks.visuals.exceptions import ChromeTimeoutError
from decks.visuals.models import Measurement, TextBox
from decks.visuals.rasterizer import Rasterizer
from decks.visuals.service import CONTENT_WARNING, VisualService
from tests.visuals import svgs

PAINTED = Measurement(boxes=[TextBox(text="Q1", x=40, y=340, w=20, h=16)], painted=3)


@pytest.fixture
def rasterizer(mocker: MockerFixture) -> MagicMock:
    """Autospecced Rasterizer that measures a fine picture and renders fake PNG bytes."""
    mock = mocker.create_autospec(Rasterizer, instance=True)
    mock.measure.return_value = PAINTED
    mock.render.return_value = b"\x89PNG-fake"
    mock.available = True
    return mock


@pytest.fixture
def assets(tmp_path: Path) -> AssetRepository:
    """Asset repository in a temp folder."""
    return AssetRepository(tmp_path / "assets")


@pytest.fixture
def service(assets: AssetRepository, rasterizer: MagicMock) -> VisualService:
    """Service with the mocked rasterizer."""
    return VisualService(assets, rasterizer)


async def test_save_stores_three_files(service: VisualService, assets: AssetRepository) -> None:
    """A good SVG is stored as SVG, PNG and manifest, with the draft warning."""
    result = await service.save("diagram", "bars", svgs.GOOD, "green")
    assert (result.ok, result.path, result.width, result.height) == (
        True,
        "assets/v1.png",
        1152,
        440,
    )
    assert CONTENT_WARNING in result.warnings
    assert assets.svg("v1") == svgs.GOOD
    assert assets.resolve("assets/v1.png").read_bytes() == b"\x89PNG-fake"
    assert assets.manifests()[0].theme == "green"


async def test_save_returns_alt_to_match_a_slide(service: VisualService) -> None:
    """The result carries the alt text, so the agent matches parallel pictures to slides."""
    result = await service.save("diagram", "bars per quarter", svgs.GOOD, "green")
    assert result.alt == "bars per quarter"


async def test_ids_increase(service: VisualService) -> None:
    """Each save gets the next id."""
    first = await service.save("diagram", "a", svgs.GOOD, "green")
    second = await service.save("diagram", "b", svgs.GOOD, "green")
    assert (first.id, second.id) == ("v1", "v2")


async def test_static_error_stops_before_chrome(
    service: VisualService, rasterizer: MagicMock, assets: AssetRepository
) -> None:
    """A colour literal returns issues, calls no Chrome and stores nothing."""
    result = await service.save("diagram", "x", svgs.HEX_COLOR, "green")
    assert not result.ok
    assert [i.code for i in result.issues] == ["color_literal"]
    assert rasterizer.measure.call_count == 0
    assert assets.manifests() == []


async def test_geometry_error_is_returned(
    service: VisualService, rasterizer: MagicMock, assets: AssetRepository
) -> None:
    """Clipped text from the measurement fails the save."""
    rasterizer.measure.return_value = Measurement(
        boxes=[TextBox(text="Q1", x=1140, y=10, w=40, h=16)], painted=3
    )
    result = await service.save("diagram", "x", svgs.GOOD, "green")
    assert [i.code for i in result.issues] == ["text_clipped"]
    assert assets.manifests() == []


async def test_chrome_failure_becomes_issue(service: VisualService, rasterizer: MagicMock) -> None:
    """A Chrome error does not raise; it is a render_failed issue."""
    rasterizer.render.side_effect = ChromeTimeoutError("render", 30)
    result = await service.save("diagram", "x", svgs.GOOD, "green")
    assert [i.code for i in result.issues] == ["render_failed"]


async def test_sync_renders_other_theme_only(
    service: VisualService, rasterizer: MagicMock, assets: AssetRepository
) -> None:
    """A theme change renders again the assets of the old theme and keeps the others."""
    await service.save("diagram", "a", svgs.GOOD, "green")
    await service.save("diagram", "b", svgs.GOOD, "orange")
    rasterizer.render.reset_mock()
    assert await service.sync("orange") == []
    assert rasterizer.render.call_count == 1
    assert {m.id: m.theme for m in assets.manifests()} == {"v1": "orange", "v2": "orange"}


async def test_sync_reports_failure(service: VisualService, rasterizer: MagicMock) -> None:
    """A failed re-render is a warning, and the other assets continue."""
    await service.save("diagram", "a", svgs.GOOD, "green")
    rasterizer.render.side_effect = ChromeTimeoutError("render", 30)
    warnings = await service.sync("orange")
    assert len(warnings) == 1
    assert "v1" in warnings[0]


async def test_resolve(service: VisualService) -> None:
    """Resolve gives a path for a saved asset and None for a bad or missing one."""
    await service.save("diagram", "a", svgs.GOOD, "green")
    assert service.resolve("assets/v1.png") is not None
    assert service.resolve("assets/v9.png") is None
    assert service.resolve("../secret.png") is None
    assert service.resolve("https://x.test/a.png") is None
