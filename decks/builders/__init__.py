from decks.models.slides import Deck, DeckSpec, Slide
from decks.models.theme import FONT, THEMES

from . import analytics, body, decisions, diagram, layout, pictures, programme
from .base import BaseBuilder
from .registry import RegisteredBuilder, Registry

__all__ = [
    "FAMILIES",
    "REGISTRY",
    "BaseBuilder",
    "RegisteredBuilder",
    "Registry",
    "build_deck",
]

FAMILIES = [analytics, body, decisions, diagram, layout, pictures, programme]

REGISTRY = Registry(FAMILIES)


def build_deck(spec: DeckSpec) -> Deck:
    """Render every slide in ``spec`` into a complete deck."""
    slides = []
    for slide_spec in spec.slides:
        registered = REGISTRY[slide_spec.type]
        slides.append(
            Slide(
                family=registered.family,
                kind=slide_spec.type,
                elements=registered.builder.build(slide_spec),
            )
        )
    return Deck(theme=spec.theme, palette=THEMES[spec.theme], font=FONT, slides=slides)
