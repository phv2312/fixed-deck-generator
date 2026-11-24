"""One self-contained gallery.html for reviewing every slide type, in both themes."""

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError, select_autoescape
from markupsafe import Markup

from decks.builders import REGISTRY, build_deck
from decks.models.slides import DeckSpec
from decks.models.theme import THEMES as PALETTES

from .exceptions import GalleryTemplateError
from .htmldoc.services import HtmlRenderer
from .models import GalleryCard, GalleryFamily, GalleryFrame, GalleryPage, GalleryType

THEMES = tuple(PALETTES)
TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_NAME = "gallery.html.j2"


class GalleryTemplates:
    """Render the gallery page template of one directory.

    The environment escapes every value. A value that is already safe HTML must be a ``Markup``.
    """

    def __init__(self, directory: Path = TEMPLATE_DIR) -> None:
        self._env = Environment(
            loader=FileSystemLoader(directory),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(("html.j2",), default_for_string=False),
        )

    def render(self, page: GalleryPage) -> str:
        """Return the gallery HTML for ``page``."""
        try:
            return self._env.get_template(TEMPLATE_NAME).render(page=page)
        except TemplateError as error:
            raise GalleryTemplateError(TEMPLATE_NAME, str(error)) from error


def build_gallery(examples_dir: str = "examples", templates: GalleryTemplates | None = None) -> str:
    """Return the self-contained gallery HTML for every example slide."""
    entries: list[GalleryCard] = []
    width = height = 0
    font = ""
    for f in sorted(Path(examples_dir).glob("*.json")):
        raw = json.loads(f.read_text())
        per_theme: dict[str, list[str]] = {}
        for theme in THEMES:
            data = {**raw, "theme": theme}
            deck = build_deck(DeckSpec.model_validate(data))
            fragments = HtmlRenderer(deck).fragments()
            width, height, font = fragments.width, fragments.height, fragments.font
            per_theme[theme] = fragments.slides
        for i, spec in enumerate(raw["slides"]):
            entries.append(_card(spec, i, per_theme))
    page = GalleryPage(
        width=width,
        height=height,
        # The font is a trusted CSS stack from the theme, so it is not HTML-escaped.
        font=Markup(font),
        total=len(entries),
        families=_families(entries),
        cards=tuple(entries),
    )
    return (templates or GalleryTemplates()).render(page)


def _card(spec: dict[str, object], index: int, per_theme: dict[str, list[str]]) -> GalleryCard:
    """Return the card of slide ``index``. ``spec`` is the raw slide of the example file."""
    kind = str(spec["type"])
    chart = spec.get("chart")
    extra = str(chart.get("type", "")) if isinstance(chart, dict) else ""
    family = REGISTRY[kind].family
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", per_theme["green"][index]))
    title = str(spec.get("title") or spec.get("question") or spec.get("text") or kind)[:90]
    return GalleryCard(
        family=family,
        type=kind,
        number=index + 1,
        label=f"{family}{' · ' + extra if extra else ''}",
        title=title,
        search=f"{family} {kind} {extra} {title} {text}".lower(),
        frames=tuple(GalleryFrame(theme=t, html=Markup(per_theme[t][index])) for t in THEMES),
    )


def _families(cards: list[GalleryCard]) -> tuple[GalleryFamily, ...]:
    """Group the cards by family and then by type, in first-seen order."""
    counts: dict[str, dict[str, int]] = {}
    for card in cards:
        types = counts.setdefault(card.family, {})
        types[card.type] = types.get(card.type, 0) + 1
    return tuple(
        GalleryFamily(
            name=family,
            count=sum(types.values()),
            types=tuple(GalleryType(name=t, count=n) for t, n in types.items()),
        )
        for family, types in counts.items()
    )
