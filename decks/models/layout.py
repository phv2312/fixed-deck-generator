"""family=layout: structural slides (opening, dividers, agenda, plain text, closing)."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    BeforeValidator,
    Field,
    model_validator,
)


def _lines(v):
    if v is None:
        return v
    if isinstance(v, (str, int, float)):
        return [str(v)]
    return [str(x) for x in v]


Lines = Annotated[list[str], BeforeValidator(_lines)]  # text, number or a list of them -> list[str]


Txt = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, (int, float)) else v)]


class AgendaItem(BaseModel):
    text: Txt = Field(
        validation_alias=AliasChoices("text", "topic"), description="Agenda entry text."
    )
    icon: Txt | None = Field(default=None, description="Optional icon name.")
    time: Txt | None = Field(
        default=None,
        description="Optional time slot. Any item with a time or owner makes a timed agenda table.",
    )
    owner: Txt | None = Field(default=None, description="Optional owner or speaker.")


class AgendaSlide(BaseModel):
    type: Literal["agenda"] = Field(
        default="agenda", description="Slide type discriminator. The value is always 'agenda'."
    )
    title: Txt = Field(default="Agenda", description="Slide title.")
    lead: Lines | None = Field(
        default=None, description="Optional lead-in text. Use a string or a list of lines."
    )
    current: int | None = Field(
        default=None,
        description=("0-based index of the current entry. A plain agenda dims the others."),
    )
    items: list[AgendaItem] = Field(
        min_length=1, max_length=10, description="Agenda entries, between 1 and 10."
    )


class ChapterSlide(BaseModel):
    type: Literal["chapter"] = Field(
        default="chapter", description="Slide type discriminator. The value is always 'chapter'."
    )
    title: str = Field(description="Chapter title.")
    number: Lines = Field(
        description=(
            "Chapter number. The value 2 renders as '02'. The slide joins a list with spaces."
        )
    )


class Person(BaseModel):
    name: Txt = Field(description="Person's name.")
    role: Txt | None = Field(default=None, description="Role or title.")
    mail: Txt | None = Field(default=None, description="Email address.")
    phone: Txt | None = Field(default=None, description="Phone number.")
    text: Txt | None = Field(default=None, description="Short bio or note. Makes a team grid.")
    photo: Txt | None = Field(
        default=None, description="Optional image file path or URL. Makes a team grid."
    )


class ContactSlide(BaseModel):
    type: Literal["contact"] = Field(
        default="contact", description="Slide type discriminator. The value is always 'contact'."
    )
    title: Txt = Field(default="Contact", description="Slide title.")
    people: list[Person] = Field(
        min_length=1,
        max_length=8,
        description=(
            "People, between 1 and 8. Contact cards take up to 6. Any person with a photo or a "
            "text makes a team grid instead."
        ),
    )

    @model_validator(mode="after")
    def _check(self):
        if len(self.people) > 6 and not any(p.photo or p.text for p in self.people):
            raise ValueError("contact: cards take at most 6 people; add a text for a team grid")
        return self


class ContentSlide(BaseModel):
    type: Literal["content"] = Field(
        default="content", description="Slide type discriminator. The value is always 'content'."
    )
    title: str = Field(description="Slide headline.")
    body: Lines = Field(description="Body text. Use a string or a list of lines.")
    lead: Lines | None = Field(
        default=None, description="Optional lead-in text. Use a string or a list of lines."
    )
    small: bool = Field(default=False, description="Use smaller body text to fit more content.")
    box: Lines | None = Field(
        default=None,
        description="Optional highlighted 'one thing to remember' box on the right.",
    )


class StatementSlide(BaseModel):
    type: Literal["statement"] = Field(
        default="statement",
        description=("Slide type discriminator. The value is always 'statement'."),
    )
    title: str = Field(description="Slide headline.")
    lead: Lines | None = Field(
        default=None, description="Optional lead-in text. Use a string or a list of lines."
    )
    points: Annotated[list[str], BeforeValidator(_lines)] = Field(
        default=[], max_length=3, description="Up to 3 supporting points."
    )
    figure: Lines | None = Field(default=None, description="Optional large figure.")
    label: Lines | None = Field(default=None, description="Optional label for the figure.")
    author: Txt | None = Field(
        default=None, description="Optional attribution. Use it when the title is a quotation."
    )
    image: Txt | None = Field(
        default=None, description="Optional background image path or URL, darkened under the text."
    )


class TitleSlide(BaseModel):
    type: Literal["title"] = Field(
        default="title", description="Slide type discriminator. The value is always 'title'."
    )
    title: str = Field(description="Slide headline.")
    subtitle: Lines | None = Field(default=None, description="Optional subtitle lines.")
    meta: Lines | None = Field(
        default=None, description="Optional metadata lines, e.g. date or author."
    )
    image: Txt | None = Field(
        default=None, description="Optional image path or URL shown on the right half."
    )
