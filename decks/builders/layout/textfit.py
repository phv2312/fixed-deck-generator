"""Text fitting utilities for full-bleed layout slides."""

from decks.builders.common import snap_down
from decks.design import BOLD_CHAR_WIDTH_SAFE, CHAR_WIDTH, LINE_HEIGHT

LH = LINE_HEIGHT


def est_lines(text: str, w: float, fs: float, *, bold: bool = False) -> int:
    """Return a conservative wrapped line count for text in a given width."""
    cw = fs * (BOLD_CHAR_WIDTH_SAFE if bold else CHAR_WIDTH)
    per = max(1, int(w / cw))
    total = 0
    for paragraph in text.split("\n"):
        cur, count = 0, 1
        for word in paragraph.split(" "):
            length = len(word)
            if cur == 0:
                cur = length
            elif cur + 1 + length <= per:
                cur += 1 + length
            else:
                count += 1
                cur = length
            while cur > per:
                count += 1
                cur -= per
        total += count
    return total


def fit(
    text: str,
    w: float,
    h: float,
    hi: float,
    lo: float,
    *,
    bold: bool = False,
    snap: bool = True,
) -> tuple[float, int]:
    """Return the largest font size in [lo, hi] whose wrapped text fits, and its line count."""
    fs = hi
    while fs > lo:
        lines = est_lines(text, w, fs, bold=bold)
        if lines * fs * LH <= h:
            return (snap_down(fs) if snap else fs), lines
        fs -= 2
    return lo, est_lines(text, w, lo, bold=bold)
