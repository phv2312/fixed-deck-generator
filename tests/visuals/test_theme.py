import pytest

from decks.models.theme import THEMES, ThemeName
from decks.visuals.theme import TOKENS, ThemeInjector
from tests.visuals import svgs


@pytest.mark.parametrize("theme", ["green", "orange"])
def test_style_defines_every_token(theme: ThemeName) -> None:
    """The style has the colour variable and both classes of each token."""
    style = ThemeInjector().style(theme)
    for name, value in THEMES[theme].items():
        assert f"--{name}:{value}" in style
        assert f".fill-{name}" in style
        assert f".stroke-{name}" in style


def test_inject_puts_style_after_opening_tag() -> None:
    """The style is the first child of the svg element."""
    out = ThemeInjector().inject(svgs.GOOD, "green")
    assert out.startswith('<svg viewBox="0 0 1152 440" xmlns="http://www.w3.org/2000/svg"><style>')


def test_inject_without_svg_returns_text() -> None:
    """Text that has no svg tag stays as it is."""
    assert ThemeInjector().inject("plain", "green") == "plain"


def test_prompt_lists_every_token() -> None:
    """The prompt names each token with its class."""
    prompt = ThemeInjector().prompt
    assert all(f"fill-{token}" in prompt for token in TOKENS)
