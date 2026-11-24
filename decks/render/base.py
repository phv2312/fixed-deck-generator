from abc import ABC, abstractmethod

from decks.models.elements import (
    Chart,
    Element,
    Group,
    Image,
    Line,
    Polygon,
    Shape,
    Table,
    Text,
)
from decks.models.slides import Deck, Slide

from .exceptions import UnsupportedElementError


class DeckRenderer[T](ABC):
    """Turn a ``Deck`` into one output value ``T`` per element and per slide.

    A backend implements one method for each element type and ``slide``. It adds its own
    entry points, such as a full document, on top of ``slides``.
    """

    def __init__(self, deck: Deck) -> None:
        self.deck = deck

    @abstractmethod
    def text(self, e: Text) -> T:
        """Render a text element."""

    @abstractmethod
    def shape(self, e: Shape) -> T:
        """Render a rectangle or an ellipse."""

    @abstractmethod
    def line(self, e: Line) -> T:
        """Render a line, with an arrowhead when ``e.arrow`` is true."""

    @abstractmethod
    def polygon(self, e: Polygon) -> T:
        """Render a polygon."""

    @abstractmethod
    def image(self, e: Image) -> T:
        """Render an image."""

    @abstractmethod
    def table(self, e: Table) -> T:
        """Render a table."""

    @abstractmethod
    def group(self, e: Group, children: list[T]) -> T:
        """Render a group from its already rendered children."""

    @abstractmethod
    def chart(self, e: Chart) -> T:
        """Render a chart."""

    @abstractmethod
    def slide(self, slide: Slide, parts: list[T], number: int) -> T:
        """Render one slide from its rendered elements. ``number`` starts at 1."""

    def element(self, e: Element) -> T:
        """Send ``e`` to the method for its type.

        Raises:
            UnsupportedElementError: If the type of ``e`` has no method.
        """
        match e:
            case Text():
                return self.text(e)
            case Shape():
                return self.shape(e)
            case Line():
                return self.line(e)
            case Polygon():
                return self.polygon(e)
            case Image():
                return self.image(e)
            case Table():
                return self.table(e)
            case Group():
                return self.group(e, [self.element(child) for child in e.children])
            case Chart():
                return self.chart(e)
            case _:
                raise UnsupportedElementError(type(e).__name__)

    def slides(self) -> list[T]:
        """Render every slide of the deck, in order."""
        return [
            self.slide(s, [self.element(e) for e in s.elements], number)
            for number, s in enumerate(self.deck.slides, 1)
        ]
