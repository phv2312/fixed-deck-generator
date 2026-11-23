"""The visual pipeline: check an SVG, render it, store it, and render it again on a new theme."""

import asyncio

from decks.agents.repos.assets import AssetRepository
from decks.models.theme import ThemeName
from decks.visuals.checker import SvgChecker
from decks.visuals.exceptions import AssetMissingError, AssetPathError, VisualError
from decks.visuals.models import (
    PICTURE_SIZE,
    VisualIssue,
    VisualKind,
    VisualManifest,
    VisualResult,
)
from decks.visuals.rasterizer import Rasterizer

CONTENT_WARNING = "content_not_verified: numbers and labels are not checked; treat it as a draft"


class VisualService:
    """Save visuals of one project. It never trusts the agent that wrote the SVG."""

    def __init__(
        self,
        assets: AssetRepository,
        rasterizer: Rasterizer | None = None,
        checker: SvgChecker | None = None,
    ) -> None:
        self._assets = assets
        self._rasterizer = rasterizer or Rasterizer()
        self._checker = checker or SvgChecker()
        self._lock = asyncio.Lock()

    @property
    def available(self) -> bool:
        """Whether visuals can be made: Chrome is installed."""
        return self._rasterizer.available

    async def check(self, svg: str, theme: ThemeName) -> list[VisualIssue]:
        """Run every check. A Chrome failure becomes an issue; it does not raise."""
        pixels = PICTURE_SIZE
        issues = self._checker.static(svg, pixels)
        if any(i.severity == "error" for i in issues):
            return issues
        try:
            measurement = await self._rasterizer.measure(svg, pixels, theme)
        except VisualError as exc:
            return [
                *issues,
                VisualIssue(
                    code="render_failed",
                    severity="error",
                    message=str(exc),
                    suggestion="Simplify the SVG and try again.",
                ),
            ]
        return [*issues, *self._checker.geometry(measurement, pixels)]

    async def save(self, kind: VisualKind, alt: str, svg: str, theme: ThemeName) -> VisualResult:
        """Check ``svg``. When it passes, render it and store it as a new asset."""
        issues = await self.check(svg, theme)
        if any(i.severity == "error" for i in issues):
            return VisualResult(ok=False, issues=issues)
        try:
            png = await self._rasterizer.render(svg, PICTURE_SIZE, theme)
        except VisualError as exc:
            failure = VisualIssue(
                code="render_failed",
                severity="error",
                message=str(exc),
                suggestion="Simplify the SVG and try again.",
            )
            return VisualResult(ok=False, issues=[*issues, failure])
        warnings = [CONTENT_WARNING, *(i.message for i in issues)]
        async with self._lock:
            visual_id = self._assets.next_id()
            manifest = VisualManifest(
                id=visual_id, kind=kind, alt=alt, theme=theme, warnings=warnings
            )
            self._assets.save(manifest, svg, png)
        width, height = PICTURE_SIZE
        return VisualResult(
            ok=True,
            id=visual_id,
            path=self._assets.relative_path(visual_id),
            alt=alt,
            width=width,
            height=height,
            warnings=warnings,
        )

    async def sync(self, theme: ThemeName) -> list[str]:
        """Render again every asset whose PNG has another theme. Return warnings.

        It needs no LLM call: the SVG source uses tokens only.
        """
        warnings: list[str] = []
        for manifest in self._assets.manifests():
            if manifest.theme == theme:
                continue
            svg = self._assets.svg(manifest.id)
            if svg is None:
                warnings.append(f"asset {manifest.id}: the SVG source is missing")
                continue
            try:
                png = await self._rasterizer.render(svg, PICTURE_SIZE, theme)
            except VisualError as exc:
                warnings.append(f"asset {manifest.id}: {exc}")
                continue
            self._assets.save_png(manifest.model_copy(update={"theme": theme}), png)
        return warnings

    def resolve(self, path: str) -> str | None:
        """Return the absolute file of an asset path, or ``None`` when it is not usable."""
        try:
            return str(self._assets.resolve(path))
        except (AssetPathError, AssetMissingError):
            return None
