"""Pipeline of the command line: build a spec, render a deck, write the galleries."""

import json
from pathlib import Path

from .builders import build_deck
from .models.slides import Deck, DeckSpec
from .models.theme import THEMES
from .render.htmldoc.services import HtmlRenderer
from .render.services import build_gallery


class DeckPipeline:
    """Run each stage of the command line. Each method writes its output files."""

    def build(self, spec_path: Path, out: Path, theme: str | None) -> None:
        """Build a deck from a spec file, optionally overriding its theme."""
        data = json.loads(spec_path.read_text())
        if theme:
            data["theme"] = theme
        deck = build_deck(DeckSpec.model_validate(data))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(deck.model_dump_json(indent=2))

    def render(self, deck_path: Path, out: Path) -> None:
        """Render a built deck file to one HTML document."""
        deck = Deck.model_validate_json(deck_path.read_text())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(HtmlRenderer(deck).document())

    def review(self, examples: str, out: Path) -> None:
        """Write one self-contained gallery HTML with every example, in both themes."""
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build_gallery(examples))

    def gallery(self, examples: str, out: Path) -> None:
        """Write one HTML document per example and per theme, plus one per theme with all."""
        out.mkdir(parents=True, exist_ok=True)
        for theme in THEMES:
            all_slides = []
            for f in sorted(Path(examples).glob("*.json")):
                data = json.loads(f.read_text())
                data["theme"] = theme
                deck = build_deck(DeckSpec.model_validate(data))
                (out / f"{f.stem}_{theme}.html").write_text(HtmlRenderer(deck).document())
                all_slides += deck.slides
            deck.slides = all_slides
            (out / f"all_{theme}.html").write_text(HtmlRenderer(deck).document())
