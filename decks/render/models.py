"""View models of the gallery page. Python fills them; the template only arranges them."""

from dataclasses import dataclass

from markupsafe import Markup


@dataclass(frozen=True, slots=True)
class GalleryFrame:
    """One theme render of a slide. ``html`` is trusted slide markup, so it is not escaped."""

    theme: str
    html: Markup


@dataclass(frozen=True, slots=True)
class GalleryCard:
    """One gallery card. ``search`` is the lower-case text that the search box matches."""

    family: str
    type: str
    number: int
    label: str
    title: str
    search: str
    frames: tuple[GalleryFrame, ...]


@dataclass(frozen=True, slots=True)
class GalleryType:
    """A slide type in the side navigation, with its number of slides."""

    name: str
    count: int


@dataclass(frozen=True, slots=True)
class GalleryFamily:
    """A slide family in the side navigation, with its slide types."""

    name: str
    count: int
    types: tuple[GalleryType, ...]


@dataclass(frozen=True, slots=True)
class GalleryPage:
    """Everything the gallery template needs. ``font`` is a trusted CSS font stack."""

    width: int
    height: int
    font: Markup
    total: int
    families: tuple[GalleryFamily, ...]
    cards: tuple[GalleryCard, ...]
