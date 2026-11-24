import argparse
from pathlib import Path

from .models.theme import THEMES
from .services import DeckPipeline

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
    pipeline = DeckPipeline()
    out = Path(a.out)

    if a.cmd == "review":
        pipeline.review(a.examples, out)
        print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")
    elif a.cmd == "gallery":
        pipeline.gallery(a.examples, out)
        print(f"wrote {sorted(x.name for x in out.iterdir())}")
    elif a.cmd == "build":
        pipeline.build(Path(a.spec), out, a.theme)
        print(f"wrote {out}")
    else:
        pipeline.render(Path(a.deck), out)
        print(f"wrote {out}")
