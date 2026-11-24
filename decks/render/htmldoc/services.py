import base64
import mimetypes
from html import escape
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from decks.design import LINE_HEIGHT, MONO_FONT
from decks.models.elements import BULLET, Chart, Group, Image, Line, Polygon, Shape, Table, Text
from decks.models.slides import Deck, Slide
from decks.render.base import DeckRenderer

from .models import HtmlFragments, HtmlPageStyle

TEMPLATE_DIR = Path(__file__).parent / "templates"


def img_src(src: str) -> str:
    """Inline a local image file as a data URI so the HTML stays self-contained."""
    if src.startswith(("http://", "https://", "data:")):
        return src
    path = Path(src)
    if not path.is_file():
        return src
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


class HtmlRenderer(DeckRenderer[str]):
    """Render a deck as HTML with absolutely positioned elements.

    The markup lives in the Jinja2 templates in ``templates/``. The methods compute the values
    that a template cannot get from the element itself.
    """

    def __init__(self, deck: Deck, style: HtmlPageStyle | None = None) -> None:
        super().__init__(deck)
        self.style = style or HtmlPageStyle()
        self._env = self._make_environment()

    def fragments(self) -> HtmlFragments:
        """Return one ``<section>`` string per slide, plus the deck size and font."""
        return HtmlFragments(self.slides(), self.deck.width, self.deck.height, self.deck.font)

    def document(self) -> str:
        """Return the full self-contained HTML page."""
        return self._render("page", slides="".join(self.slides()))

    def text_body(self, text: str) -> str:
        """Escape ``text``. A bullet line gets a 1em marker so its wraps hang under its text."""
        return self._render("text_body", text=text, has_bullets=BULLET in text)

    def text(self, e: Text) -> str:
        """Render a flex box that holds the escaped text."""
        return self._render("text", e=e, body=self.text_body(e.text))

    def shape(self, e: Shape) -> str:
        """Render a rectangle or an ellipse as a styled box."""
        return self._render("shape", e=e)

    def line(self, e: Line) -> str:
        """Render a line as an SVG that covers the slide."""
        marker_id = f"ah{abs(hash((e.x1, e.y1, e.x2, e.y2)))}"
        return self._render("line", e=e, marker_id=marker_id)

    def polygon(self, e: Polygon) -> str:
        """Render a polygon as an SVG that covers the slide."""
        return self._render("polygon", e=e)

    def image(self, e: Image) -> str:
        """Render an image. A local file becomes a data URI."""
        return self._render("image", e=e, src=img_src(e.src))

    def table(self, e: Table) -> str:
        """Render a table. The first row is a header when ``e.header`` is true."""
        return self._render("table", e=e)

    def group(self, e: Group, children: list[str]) -> str:
        """Render a group as a wrapper that keeps the child coordinates."""
        return self._render("group", e=e, children=children)

    def chart(self, e: Chart) -> str:
        """Render a dashed placeholder, because charts have no native HTML output yet."""
        return self._render("chart", e=e)

    def slide(self, slide: Slide, parts: list[str], number: int) -> str:
        """Render a ``<section>`` with the elements and the slide number."""
        return self._render("slide", slide=slide, parts=parts, number=number)

    def _render(self, name: str, **context: object) -> str:
        """Render the template ``name`` with the deck, the page style and ``context``."""
        template = self._env.get_template(f"{name}.html.j2")
        return template.render(
            deck=self.deck,
            page=self.style,
            color=self._color,
            mono_font=MONO_FONT,
            line_height=LINE_HEIGHT,
            bullet=BULLET,
            **context,
        )

    def _color(self, value: str | None) -> str:
        """Return the palette color for a token, a hex string as it is, or the no-color value."""
        if value is None:
            return self.style.no_color
        return self.deck.palette.get(value, value)

    @staticmethod
    def _make_environment() -> Environment:
        """Build the Jinja2 environment. Templates escape with the ``esc`` filter."""
        env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )
        env.filters["esc"] = escape
        env.filters["g"] = HtmlRenderer._number
        env.filters["inline"] = HtmlRenderer._inline
        return env

    @staticmethod
    def _number(value: float) -> str:
        """Format a number as the shortest exact text, so ``16.0`` becomes ``16``."""
        return f"{value:g}"

    @staticmethod
    def _inline(value: str) -> str:
        """Join the lines of a multi-line style so that it fits in one attribute."""
        return "".join(line.strip() for line in value.splitlines())
