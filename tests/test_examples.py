"""Smoke tests: every example builds and renders in both themes, and every slide type has examples."""

import json
from pathlib import Path

import pytest

from decks.builders import REGISTRY, build_deck
from decks.models.slides import DeckSpec
from decks.render.html import render_html

FILES = sorted(Path("examples").glob("*.json"))


@pytest.mark.parametrize("theme", ["green", "orange"])
@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
def test_example_builds_and_renders(path, theme):
    data = json.loads(path.read_text())
    data["theme"] = theme
    deck = build_deck(DeckSpec.model_validate(data))
    assert deck.slides
    html = render_html(deck)
    assert html.count('class="slide"') == len(deck.slides)


def test_every_slide_type_has_examples():
    used = {s["type"] for f in FILES for s in json.loads(f.read_text())["slides"]}
    assert set(REGISTRY) <= used, f"no example for: {sorted(set(REGISTRY) - used)}"


def test_each_family_has_a_unique_type_name():
    names = [t for t in REGISTRY]
    assert len(names) == len(set(names))
