from dataclasses import dataclass


@dataclass(frozen=True)
class HtmlPageStyle:
    """Look values of the HTML output. The templates read them as ``page``."""

    title: str = "Deck"
    backdrop: str = "#2b2f36"
    gap: int = 24
    margin: int = 48
    cell_padding: str = "6px 10px"
    bold_weight: int = 700
    regular_weight: int = 400
    no_color: str = "none"
    line_dash: str = "6 5"
    polygon_dash: str = "7 5"
    placeholder_border: str = "1px dashed #999"
    slide_number: str = "right:32px;bottom:20px;font-size:12px;"
