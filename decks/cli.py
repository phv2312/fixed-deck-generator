import argparse
import json
from pathlib import Path

from .builders import build_deck
from .models.slides import Deck, DeckSpec
from .models.theme import THEMES
from .render.htmldoc.services import HtmlRenderer

EXAMPLES_DIR = "examples"
OUT_DIR = Path("out")  # generated files go here, not in the repo root


def main() -> None:
    p = argparse.ArgumentParser(prog="slide_decks")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="stage 1: spec.json -> deck.json")
    b.add_argument("spec")
    b.add_argument("-o", "--out", default=str(OUT_DIR / "deck.json"))
    b.add_argument("--theme", choices=list(THEMES), help="override theme")
    r = sub.add_parser("render", help="stage 2: deck.json -> html")
    r.add_argument("deck")
    r.add_argument("-o", "--out", default=str(OUT_DIR / "deck.html"))
    g = sub.add_parser("gallery", help="build every examples/*.json in both themes for review")
    g.add_argument("--examples", default=EXAMPLES_DIR)
    g.add_argument("--out", default=str(OUT_DIR / "gallery"))
    rv = sub.add_parser(
        "review", help="one self-contained gallery.html with every example, both themes"
    )
    rv.add_argument("--examples", default=EXAMPLES_DIR)
    rv.add_argument("-o", "--out", default=str(OUT_DIR / "gallery.html"))
    a = p.parse_args()

    if a.cmd == "review":
        from .render.gallery import build_gallery

        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(build_gallery(a.examples))
        print(f"wrote {a.out} ({Path(a.out).stat().st_size / 1e6:.1f} MB)")
        return

    if a.cmd == "gallery":
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        for theme in THEMES:
            all_slides = []
            for f in sorted(Path(a.examples).glob("*.json")):
                data = json.loads(f.read_text())
                data["theme"] = theme
                deck = build_deck(DeckSpec.model_validate(data))
                (out / f"{f.stem}_{theme}.html").write_text(HtmlRenderer(deck).document())
                all_slides += deck.slides
            deck.slides = all_slides
            (out / f"all_{theme}.html").write_text(HtmlRenderer(deck).document())
        print(f"wrote {sorted(x.name for x in out.iterdir())}")
        return

    if a.cmd == "build":
        data = json.loads(Path(a.spec).read_text())
        if a.theme:
            data["theme"] = a.theme
        deck = build_deck(DeckSpec.model_validate(data))
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(deck.model_dump_json(indent=2))
    else:
        deck = Deck.model_validate_json(Path(a.deck).read_text())
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(HtmlRenderer(deck).document())
    print(f"wrote {a.out}")
