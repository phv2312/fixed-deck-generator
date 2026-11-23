"""Chrome headless: measure an SVG and render it to a PNG."""

import asyncio
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from decks.models.theme import ThemeName
from decks.visuals.exceptions import (
    ChromeFailedError,
    ChromeNotFoundError,
    ChromeTimeoutError,
)
from decks.visuals.models import Measurement
from decks.visuals.theme import ThemeInjector

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)
CHROME_ENV = "CHROME_PATH"  # set it to use a Chrome that is not on the usual paths
SCALE = 2  # PNG pixels per SVG pixel
_RESULT = re.compile(r'<pre id="res">(.*?)</pre>', re.DOTALL)

_MEASURE_SCRIPT = """
const svg = document.querySelector('svg');
const frame = svg.getBoundingClientRect();
const rel = (r) => ({x: r.left - frame.left, y: r.top - frame.top, w: r.width, h: r.height});
const boxes = [...svg.querySelectorAll('text')]
  .filter((t) => t.textContent.trim() !== '')
  .map((t) => ({text: t.textContent.trim(), ...rel(t.getBoundingClientRect())}));
const shown = [...svg.querySelectorAll('rect,circle,ellipse,path,line,polyline,polygon,text')]
  .filter((e) => {
    const s = getComputedStyle(e);
    const r = e.getBoundingClientRect();
    const paints = s.fill !== 'none' || (s.stroke !== 'none' && s.strokeWidth !== '0px');
    const inside = r.right > frame.left && r.left < frame.right
      && r.bottom > frame.top && r.top < frame.bottom;
    return paints && inside && s.visibility !== 'hidden' && s.opacity !== '0'
      && (r.width > 0 || r.height > 0);
  });
const out = document.createElement('pre');
out.id = 'res';
out.textContent = JSON.stringify({boxes, painted: shown.length});
document.body.appendChild(out);
"""


class Rasterizer:
    """Run Chrome headless on an SVG. One semaphore limits parallel Chrome processes."""

    def __init__(
        self,
        chrome: str | None = None,
        *,
        timeout: float = 30.0,
        concurrency: int = 2,
        injector: ThemeInjector | None = None,
    ) -> None:
        self._chrome = chrome if chrome is not None else self.find_chrome()
        self._timeout = timeout
        self._gate = asyncio.Semaphore(concurrency)
        self._injector = injector or ThemeInjector()

    @staticmethod
    def find_chrome() -> str | None:
        """Return the path of a Chrome or Chromium executable, or ``None``."""
        override = os.environ.get(CHROME_ENV)
        if override and Path(override).is_file():
            return override
        for name in ("google-chrome", "chromium", "chromium-browser"):
            found = shutil.which(name)
            if found:
                return found
        return next((c for c in CHROME_CANDIDATES if Path(c).is_file()), None)

    @property
    def available(self) -> bool:
        """Whether Chrome is installed."""
        return self._chrome is not None

    async def measure(self, svg: str, size: tuple[int, int], theme: ThemeName) -> Measurement:
        """Load the SVG in Chrome and return the text boxes and the painted count."""
        async with self._gate:
            return await asyncio.to_thread(self._measure, svg, size, theme)

    async def render(self, svg: str, size: tuple[int, int], theme: ThemeName) -> bytes:
        """Render the SVG to PNG bytes at ``SCALE`` times its size."""
        async with self._gate:
            return await asyncio.to_thread(self._render, svg, size, theme)

    def _page(self, svg: str, size: tuple[int, int], theme: ThemeName, script: str) -> str:
        width, height = size
        body = self._injector.inject(svg, theme)
        background = self._injector.background(theme)
        return (
            "<!doctype html><html><head><meta charset='utf-8'><style>"
            f"html,body{{margin:0;background:{background}}}"
            f"#frame{{width:{width}px;height:{height}px;overflow:hidden}}"
            "#frame>svg{width:100%;height:100%;display:block}"
            f"</style></head><body><div id='frame'>{body}</div>"
            f"<script>{script}</script></body></html>"
        )

    def _measure(self, svg: str, size: tuple[int, int], theme: ThemeName) -> Measurement:
        page = self._page(svg, size, theme, _MEASURE_SCRIPT)
        output = self._run("measure", page, ["--dump-dom"], size, scale=1)
        match = _RESULT.search(output)
        if match is None:
            raise ChromeFailedError("measure", "no result in the page")
        return Measurement.model_validate(json.loads(html.unescape(match.group(1))))

    def _render(self, svg: str, size: tuple[int, int], theme: ThemeName) -> bytes:
        page = self._page(svg, size, theme, "")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.png"
            self._run("render", page, [f"--screenshot={target}"], size, scale=SCALE, work=tmp)
            if not target.is_file():
                raise ChromeFailedError("render", "no PNG was created")
            return target.read_bytes()

    def _run(
        self,
        step: str,
        page: str,
        flags: list[str],
        size: tuple[int, int],
        *,
        scale: int,
        work: str | None = None,
    ) -> str:
        if self._chrome is None:
            raise ChromeNotFoundError
        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(work or tmp) / f"{step}.html"
            html_path.write_text(page, encoding="utf-8")
            command = [
                self._chrome,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-first-run",
                "--disable-extensions",
                f"--force-device-scale-factor={scale}",
                f"--window-size={size[0]},{size[1]}",
                f"--user-data-dir={tmp}/profile",
                *flags,
                html_path.as_uri(),
            ]
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True, check=False, timeout=self._timeout
                )
            except subprocess.TimeoutExpired as exc:
                raise ChromeTimeoutError(step, self._timeout) from exc
        if result.returncode != 0:
            raise ChromeFailedError(step, result.stderr.strip()[:300])
        return result.stdout
