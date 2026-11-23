import subprocess
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from decks.visuals.exceptions import ChromeFailedError, ChromeNotFoundError, ChromeTimeoutError
from decks.visuals.rasterizer import Rasterizer
from tests.visuals import svgs

SIZE = (700, 400)


def _completed(stdout: str = "", returncode: int = 0, stderr: str = "") -> MagicMock:
    done = MagicMock(spec=subprocess.CompletedProcess)
    done.stdout, done.returncode, done.stderr = stdout, returncode, stderr
    return done


@pytest.fixture
def run(mocker: MockerFixture) -> MagicMock:
    """Autospecced subprocess.run."""
    return mocker.patch("decks.visuals.rasterizer.subprocess.run", autospec=True)


async def test_measure_parses_page_result(run: MagicMock) -> None:
    """The result element of the dumped DOM becomes a Measurement."""
    dom = '<pre id="res">{"boxes":[{"text":"a","x":1,"y":2,"w":3,"h":4}],"painted":2}</pre>'
    run.return_value = _completed(stdout=f"<html>{dom}</html>")
    measurement = await Rasterizer("chrome").measure(svgs.GOOD, SIZE, "green")
    assert measurement.painted == 2
    assert measurement.boxes[0].text == "a"
    assert "--dump-dom" in run.call_args.args[0]


async def test_measure_without_result_fails(run: MagicMock) -> None:
    """A page without the result element is a Chrome failure."""
    run.return_value = _completed(stdout="<html></html>")
    with pytest.raises(ChromeFailedError):
        await Rasterizer("chrome").measure(svgs.GOOD, SIZE, "green")


async def test_nonzero_exit_fails(run: MagicMock) -> None:
    """A non-zero exit code raises with the stderr text."""
    run.return_value = _completed(returncode=1, stderr="boom")
    with pytest.raises(ChromeFailedError, match="boom"):
        await Rasterizer("chrome").measure(svgs.GOOD, SIZE, "green")


async def test_timeout_raises(run: MagicMock) -> None:
    """A timeout becomes ChromeTimeoutError."""
    run.side_effect = subprocess.TimeoutExpired("chrome", 1)
    with pytest.raises(ChromeTimeoutError):
        await Rasterizer("chrome", timeout=1).render(svgs.GOOD, SIZE, "green")


async def test_render_without_output_file_fails(run: MagicMock) -> None:
    """Chrome that exits 0 but writes no PNG is a failure."""
    run.return_value = _completed()
    with pytest.raises(ChromeFailedError, match="no PNG"):
        await Rasterizer("chrome").render(svgs.GOOD, SIZE, "green")


async def test_no_chrome_raises(mocker: MockerFixture) -> None:
    """Without Chrome, a call raises ChromeNotFoundError."""
    mocker.patch.object(Rasterizer, "find_chrome", return_value=None)
    rasterizer = Rasterizer()
    assert not rasterizer.available
    with pytest.raises(ChromeNotFoundError):
        await rasterizer.render(svgs.GOOD, SIZE, "green")


needs_chrome = pytest.mark.skipif(
    Rasterizer.find_chrome() is None, reason="Chrome is not installed"
)


@needs_chrome
async def test_real_chrome_measures_and_renders() -> None:
    """With real Chrome: the boxes are found, and the PNG has the 2x size and the PNG magic."""
    rasterizer = Rasterizer()
    measurement = await rasterizer.measure(svgs.GOOD, SIZE, "orange")
    assert measurement.painted >= 3
    assert {b.text for b in measurement.boxes} == {"Q1", "Q2"}
    png = await rasterizer.render(svgs.GOOD, SIZE, "orange")
    assert png.startswith(b"\x89PNG")
    assert int.from_bytes(png[16:20]) == SIZE[0] * 2
