import pytest

from decks.text_metrics import MIN_FONT, TextMetrics


@pytest.mark.parametrize("size", [17.0, 20.0, 16.0])
def test_fit_keeps_size_when_text_fits(size: float) -> None:
    """A size outside the design scale stays as it is when the text fits."""
    assert TextMetrics().fit_font_size("hi", size, (400, 100)) == size


def test_fit_shrinks_to_scale_size() -> None:
    """Text that does not fit gets the largest smaller scale size that fits."""
    size = TextMetrics().fit_font_size("word " * 30, 36, (300, 100))
    assert size in {12, 14, 16, 18, 22, 28}


def test_fit_floor_is_min_font() -> None:
    """Text that fits at no size falls back to the minimum font."""
    assert TextMetrics().fit_font_size("word " * 5000, 36, (100, 20)) == MIN_FONT


def test_fit_floor_when_font_is_below_scale() -> None:
    """A requested size below the whole scale is tried first, not raised."""
    assert TextMetrics().fit_font_size("hi", 10.0, (400, 100)) == 10.0


def test_bold_text_is_estimated_narrower() -> None:
    """Bold headlines wrap later than the regular estimate, matching the browser."""
    title = "Scaled dot-product attention turns scores into weighted averages"
    metrics = TextMetrics()

    assert metrics.height(title, 36, 1152) > metrics.height(title, 36, 1152, bold=True)
    assert metrics.height(title, 36, 1152, bold=True) <= 60
