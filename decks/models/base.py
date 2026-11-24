"""Shared building blocks for slide parameter models."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, field_validator

from .exceptions import SeriesLengthError


class Series(BaseModel):
    name: str = Field(description="Series name shown in the legend.")
    values: list[float] = Field(
        description="Data values, one per category, in the same order as the categories."
    )

    @field_validator("name", mode="before")
    @classmethod
    def _name_str(cls, v: object) -> str:
        return str(v)


def same_len(what: str, n: int, series: list[Series]) -> None:
    for s in series:
        if len(s.values) != n:
            raise SeriesLengthError(what, s.name, len(s.values), n)


Text = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, (int, float)) else v)]

TextList = list[Text]
