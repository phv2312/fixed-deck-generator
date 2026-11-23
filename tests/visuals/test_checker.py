import pytest

from decks.visuals.checker import SvgChecker
from decks.visuals.models import Measurement, TextBox
from tests.visuals import svgs

SIZE = (1152, 440)


def _codes(svg: str) -> list[str]:
    return [i.code for i in SvgChecker().static(svg, SIZE) if i.severity == "error"]


def test_good_svg_has_no_issues() -> None:
    """A clean SVG with token classes passes the static checks."""
    assert SvgChecker().static(svgs.GOOD, SIZE) == []


@pytest.mark.parametrize(
    ("svg", "code"),
    [
        (svgs.HEX_COLOR, "color_literal"),
        (svgs.STYLE_COLOR, "color_literal"),
        (svgs.UNKNOWN_TOKEN, "unknown_token"),
        (svgs.SCRIPT, "forbidden_element"),
        (svgs.FOREIGN, "forbidden_element"),
        (svgs.EVENT, "forbidden_attr"),
        (svgs.EXTERNAL, "external_ref"),
        (svgs.DOCTYPE, "unsafe_xml"),
        (svgs.SMALL_FONT, "font_too_small"),
        (svgs.WRONG_RATIO, "wrong_ratio"),
        (svgs.NO_VIEWBOX, "bad_root"),
        (svgs.NOT_XML, "xml_invalid"),
        (svgs.EMPTY, "empty_svg"),
    ],
)
def test_static_issue_codes(svg: str, code: str) -> None:
    """Each broken fixture reports its own issue code."""
    assert code in _codes(svg)


def test_warning_for_too_many_texts() -> None:
    """Too many text nodes is a warning, not an error."""
    texts = "".join(f'<text x="1" y="{i}" font-size="12">t</text>' for i in range(45))
    svg = f'<svg viewBox="0 0 1152 440">{texts}</svg>'
    issues = SvgChecker().static(svg, SIZE)
    assert [(i.code, i.severity) for i in issues] == [("too_many_texts", "warning")]


def _box(text: str, x: float, y: float, w: float = 40, h: float = 16) -> TextBox:
    return TextBox(text=text, x=x, y=y, w=w, h=h)


@pytest.mark.parametrize(
    ("measurement", "codes"),
    [
        (Measurement(boxes=[_box("a", 10, 10)], painted=3), []),
        (Measurement(boxes=[], painted=0), ["blank_render"]),
        (Measurement(boxes=[_box("a", 1140, 10)], painted=3), ["text_clipped"]),
        (Measurement(boxes=[_box("a", 10, -20)], painted=3), ["text_clipped"]),
        (Measurement(boxes=[_box("a", 10, 10), _box("b", 20, 12)], painted=3), ["text_overlap"]),
        (Measurement(boxes=[_box("a", 10, 10), _box("b", 60, 10)], painted=3), []),
    ],
)
def test_geometry_issue_codes(measurement: Measurement, codes: list[str]) -> None:
    """Clipping, overlap and a blank render are found from the measurement."""
    issues = SvgChecker().geometry(measurement, SIZE)
    assert [i.code for i in issues] == codes
