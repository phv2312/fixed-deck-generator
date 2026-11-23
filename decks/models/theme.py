from typing import Literal

ThemeName = Literal["green", "orange"]
DEFAULT_THEME: ThemeName = "green"

# Semantic tokens. Elements reference these names; the palette is embedded in deck.json.
THEMES: dict[str, dict[str, str]] = {
    "green": {
        "bg": "#FFFFFF",
        "text": "#1F2937",
        "muted": "#6B7280",
        "primary": "#0B3D2E",
        "accent": "#2FA37A",
        "light": "#A7E3D2",
        "ink": "#06281E",
        "tint": "#D5F0E6",
        "grid": "#D1D5DB",
    },
    # graphite text and headings with a burnt-orange accent on white,
    # instead of a cream/terracotta look
    "orange": {
        "bg": "#FFFFFF",
        "text": "#1F2933",
        "muted": "#667085",
        "primary": "#1F2933",
        "accent": "#D9480F",
        "light": "#FFC8A2",
        "ink": "#0F1419",
        "tint": "#F4F1EE",
        "grid": "#D9D5D0",
    },
}
# One family on purpose (the owner's reference decks are sans); fonts that exist on every machine
# keep a later PPTX export predictable.
FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif"
