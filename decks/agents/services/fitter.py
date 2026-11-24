"""Shrink overflowing text so that a layout error needs no new LLM call."""

from decks.models.elements import BULLET, Element, Group, Text
from decks.models.slides import Slide
from decks.text_metrics import TextMetrics


class LayoutFitter:
    """Lower the font size of each text that overflows its box, down to the smallest scale size."""

    def __init__(self, metrics: TextMetrics | None = None) -> None:
        self._metrics = metrics or TextMetrics()

    def fit(self, slide: Slide) -> Slide:
        """Return a copy of ``slide`` in which every text fits its box when the scale allows."""
        return slide.model_copy(update={"elements": [self._element(e) for e in slide.elements]})

    def _element(self, element: Element) -> Element:
        if isinstance(element, Group):
            return element.model_copy(
                update={"children": [self._element(child) for child in element.children]}
            )
        if isinstance(element, Text):
            return self._text(element)
        return element

    def _text(self, text: Text) -> Text:
        indent = text.font_size if BULLET in text.text else 0  # the checker counts it too
        size = self._metrics.fit_font_size(
            text.text, text.font_size, (text.w - indent, text.h), bold=text.bold
        ).size
        return text if size >= text.font_size else text.model_copy(update={"font_size": size})
