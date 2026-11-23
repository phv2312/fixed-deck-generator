"""Theme tokens for SVG: the agent uses token names, the renderer injects the colours."""

import re

from decks.models.theme import FONT, THEMES, ThemeName

TOKENS = tuple(THEMES["green"])

TOKEN_ROLES = {
    "primary": "headings and key text; the strongest dark shade",
    "accent": "the one highlighted series, node or number",
    "light": "secondary fills next to accent",
    "tint": "soft background panels and bands",
    "muted": "axis labels, captions and secondary text",
    "grid": "axes, grid lines and borders",
    "text": "default body text",
    "ink": "text on a primary or accent fill",
    "bg": "the slide background; also text on a primary or accent fill",
}

_SVG_OPEN = re.compile(r"<svg\b[^>]*>", re.IGNORECASE)


class ThemeInjector:
    """Add the theme colours, the font and the token classes to an SVG."""

    def style(self, theme: ThemeName) -> str:
        """Return the ``<style>`` element for ``theme``."""
        palette = THEMES[theme]
        variables = ";".join(f"--{name}:{value}" for name, value in palette.items())
        classes = "".join(
            f".fill-{name}{{fill:var(--{name})}}.stroke-{name}{{stroke:var(--{name})}}"
            for name in palette
        )
        base = f"svg{{font-family:{FONT};fill:var(--text)}}"
        return f"<style>:root{{{variables}}}{base}{classes}</style>"

    def inject(self, svg: str, theme: ThemeName) -> str:
        """Return ``svg`` with the theme style right after the opening ``<svg>`` tag."""
        match = _SVG_OPEN.search(svg)
        if match is None:
            return svg
        return svg[: match.end()] + self.style(theme) + svg[match.end() :]

    def background(self, theme: ThemeName) -> str:
        """Return the background colour of ``theme``."""
        return THEMES[theme]["bg"]

    @property
    def prompt(self) -> str:
        """Token list for the agent prompt."""
        lines = [
            f"- `{name}` ({role}): class `fill-{name}` or `stroke-{name}`"
            for name, role in TOKEN_ROLES.items()
        ]
        return "\n".join(lines)
