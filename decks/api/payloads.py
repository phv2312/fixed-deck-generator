from pydantic import BaseModel, ConfigDict, Field

from decks.agents.models import Question

MAX_PAGE_SIZE = 100


class PageQuery(BaseModel):
    """Query parameters of each list endpoint."""

    model_config = ConfigDict(extra="forbid")

    limit: int = Field(
        default=50, ge=1, le=MAX_PAGE_SIZE, description="How many items to return at most."
    )
    offset: int = Field(default=0, ge=0, description="How many items to skip.")


class PageResponse[T](BaseModel):
    """Response body of a list endpoint."""

    items: list[T] = Field(description="The items of this page.")
    total: int = Field(description="How many items exist in all pages.")


class QuestionResponse(BaseModel):
    """A question that the agent asks the user. The user answers it with the next chat message."""

    question: str = Field(description="The question text.")
    options: list[str] | None = Field(
        description="Answers to pick from, or null for a free-text question."
    )
    allow_multiple: bool = Field(description="Whether the user may pick more than one option.")
    free_text: bool = Field(description="Whether the user may type an answer of their own.")

    @classmethod
    def from_question(cls, question: Question) -> "QuestionResponse":
        """Build the response from the question of the agent layer."""
        return cls(
            question=question.question,
            options=question.options,
            allow_multiple=question.allow_multiple,
            free_text=question.free_text,
        )
