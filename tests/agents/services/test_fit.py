import pytest

from decks.design import LINE_HEIGHT
from decks.text_metrics import MIN_FONT, Fit, TextMetrics


@pytest.mark.parametrize("size", [17.0, 20.0, 16.0])
def test_fit_keeps_size_when_text_fits(size: float) -> None:
    """A size outside the design scale stays as it is when the text fits."""
    assert TextMetrics().fit_font_size("hi", size, (400, 100)).size == size


def test_fit_shrinks_to_scale_size() -> None:
    """Text that does not fit gets the largest smaller scale size that fits."""
    size = TextMetrics().fit_font_size("word " * 30, 36, (300, 100)).size
    assert size in {12, 14, 16, 18, 22, 28}


def test_fit_floor_is_min_font() -> None:
    """Text that fits at no size falls back to the minimum font."""
    assert TextMetrics().fit_font_size("word " * 5000, 36, (100, 20)).size == MIN_FONT


def test_fit_floor_when_font_is_below_scale() -> None:
    """A requested size below the whole scale is tried first, not raised."""
    assert TextMetrics().fit_font_size("hi", 10.0, (400, 100)).size == 10.0


@pytest.mark.parametrize(
    ("font_size", "expected"),
    [
        (26.0, 22.0),
        (22.0, 22.0),
        (38.0, 36.0),
    ],
)
def test_fit_snap_lands_on_the_scale(font_size: float, expected: float) -> None:
    """With ``snap`` the result is the largest scale size at or below the request."""
    assert TextMetrics().fit_font_size("hi", font_size, (400, 100), snap=True).size == expected


def test_fit_step_ignores_the_scale() -> None:
    """With ``step`` a hero figure shrinks in small steps, not to a scale size."""
    result = TextMetrics().fit_font_size("02", 220, (1120, 230), 100, bold=True, step=2)

    assert result == Fit(size=176, lines=1)


def test_fit_falls_back_to_lo() -> None:
    """Text that fits at no size gets ``lo`` and the line count at ``lo``."""
    metrics = TextMetrics()
    text = "word " * 5000

    result = metrics.fit_font_size(text, 36, (100, 20), 20, snap=True)

    assert result == Fit(size=20, lines=metrics.lines(text, 20, 100))


def test_fit_never_goes_below_lo() -> None:
    """Scale sizes below ``lo`` are not tried even when only they would fit."""
    result = TextMetrics().fit_font_size("word " * 30, 36, (300, 100), 20, snap=True)
    assert result.size >= 20


def test_fit_reports_lines_at_the_chosen_size() -> None:
    """The returned line count is the count at the returned size."""
    metrics = TextMetrics()
    text = "word " * 30

    result = metrics.fit_font_size(text, 36, (300, 100))

    assert result.lines == metrics.lines(text, result.size, 300)


@pytest.mark.parametrize(
    ("text", "font_size", "width", "bold", "expected"),
    [
        ("hi", 16, 400, False, 1),
        ("", 16, 400, False, 1),
        ("a\nb\nc", 16, 400, False, 3),
        ("aaaa bbbb cccc", 10, 57, False, 2),  # 14 chars wrap at 10 per line
        ("aaaaaaa bbbbbbb ccc", 10, 57, False, 3),  # words do not split: 19 chars, 3 lines
        ("a" * 25, 10, 57, False, 3),  # a word longer than a line is split
        ("a" * 10, 10, 57, False, 1),
        ("a" * 10, 10, 57, True, 2),  # bold is wider: 9 per line
    ],
)
def test_lines_wraps_at_word_breaks(
    text: str, font_size: float, width: float, bold: bool, expected: int
) -> None:
    """The line count follows word wrapping, not the raw character count."""
    assert TextMetrics().lines(text, font_size, width, bold=bold) == expected


def test_height_is_lines_times_line_height() -> None:
    """The height is built on the line count, so the two never disagree."""
    metrics = TextMetrics()
    text = "aaaaaaa bbbbbbb ccc"

    assert metrics.height(text, 10, 57) == metrics.lines(text, 10, 57) * 10 * LINE_HEIGHT


def test_bold_text_is_estimated_wider() -> None:
    """Bold wraps earlier than regular, so the estimate never under-counts."""
    title = "a" * 28 + " " + "a" * 28
    metrics = TextMetrics()

    assert metrics.lines(title, 36, 1152) == 1
    assert metrics.lines(title, 36, 1152, bold=True) == 2
