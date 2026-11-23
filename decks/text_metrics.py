"""Estimate how much room a text needs. The builders and the layout checker share it."""

import math

from decks.design import BOLD_CHAR_WIDTH, CHAR_WIDTH, LINE_HEIGHT, TYPE

MIN_FONT = float(min(TYPE.values()))


class TextMetrics:
    """Estimate how much room a text needs. It is a heuristic, not a browser layout."""

    def height(self, text: str, font_size: float, width: float, *, bold: bool = False) -> float:
        """Return the estimated height of ``text`` wrapped into ``width``."""
        glyph = BOLD_CHAR_WIDTH if bold else CHAR_WIDTH
        per_line = max(1, int(width / (font_size * glyph)))
        lines = sum(max(1, math.ceil(len(line) / per_line)) for line in text.split("\n"))
        return lines * font_size * LINE_HEIGHT

    def fit_font_size(
        self, text: str, font_size: float, box: tuple[float, float], *, bold: bool = False
    ) -> float:
        """Return ``font_size`` if ``text`` fits, else the largest smaller scale size that fits."""
        width, height = box
        smaller = sorted((float(s) for s in TYPE.values() if s < font_size), reverse=True)
        for size in [font_size, *smaller]:
            if self.height(text, size, width, bold=bold) <= height:
                return size
        return MIN_FONT
