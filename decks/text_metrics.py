from dataclasses import dataclass

from decks.design import BOLD_CHAR_WIDTH, CHAR_WIDTH, LINE_HEIGHT, TYPE

MIN_FONT = float(min(TYPE.values()))
OVERFLOW_TOLERANCE = 1.02  # the height estimate is a heuristic: allow a little slack


@dataclass(frozen=True)
class Fit:
    """A font size and the number of lines the text takes at that size."""

    size: float
    lines: int


class TextMetrics:
    """Estimate how much room a text needs. It is a heuristic, not a browser layout."""

    def lines(self, text: str, font_size: float, width: float, *, bold: bool = False) -> int:
        """Return a conservative count of the lines ``text`` takes when wrapped at word breaks.

        A word that is longer than a line is split across lines. Each ``\\n`` starts a new line.
        """
        glyph = BOLD_CHAR_WIDTH if bold else CHAR_WIDTH
        per_line = max(1, int(width / (font_size * glyph)))
        total = 0
        for paragraph in text.split("\n"):
            used, count = 0, 1
            for word in paragraph.split(" "):
                length = len(word)
                if used == 0:
                    used = length
                elif used + 1 + length <= per_line:
                    used += 1 + length
                else:
                    count += 1
                    used = length
                while used > per_line:
                    count += 1
                    used -= per_line
            total += count
        return total

    def height(self, text: str, font_size: float, width: float, *, bold: bool = False) -> float:
        """Return the estimated height of ``text`` wrapped into ``width``."""
        return self.lines(text, font_size, width, bold=bold) * font_size * LINE_HEIGHT

    def fit_font_size(
        self,
        text: str,
        font_size: float,
        box: tuple[float, float],
        lo: float = MIN_FONT,
        *,
        bold: bool = False,
        snap: bool = False,
        step: float | None = None,
    ) -> Fit:
        """Return the largest size in [``lo``, ``font_size``] at which ``text`` fits ``box``.

        With ``snap`` false, ``font_size`` is tried as it is, then the smaller scale sizes.
        With ``snap`` true, only scale sizes at or below ``font_size`` are tried.
        With ``step`` set, the sizes go down from ``font_size`` by ``step`` and ignore the scale.
        Use it for a hero figure that is larger than the scale.
        When no size fits, the result is ``lo``.
        """
        width, height = box
        for size in self._candidates(font_size, lo, snap=snap, step=step):
            lines = self.lines(text, size, width, bold=bold)
            if lines * size * LINE_HEIGHT <= height:
                return Fit(size=size, lines=lines)
        return Fit(size=lo, lines=self.lines(text, lo, width, bold=bold))

    @staticmethod
    def _candidates(font_size: float, lo: float, *, snap: bool, step: float | None) -> list[float]:
        """Return the sizes to try, largest first."""
        if step is not None:
            return [font_size - i * step for i in range(int((font_size - lo) / step) + 1)]
        scale = sorted((float(s) for s in TYPE.values() if lo <= s <= font_size), reverse=True)
        if snap:
            return scale
        return [font_size, *(s for s in scale if s < font_size)]
