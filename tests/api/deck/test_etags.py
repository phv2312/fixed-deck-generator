import pytest

from decks.api.deck.etags import ETags


def test_header_quotes_the_revision() -> None:
    """Test that the ETag value is the revision in quotes."""
    assert ETags.header_of("abc123") == '"abc123"'


@pytest.mark.parametrize(
    ("header", "revision"),
    [
        ('"abc123"', "abc123"),
        ('W/"abc123"', "abc123"),
        ('"abc123", "other"', "abc123"),
        ("", None),
        (None, None),
        ('""', None),
    ],
)
def test_revision_is_read_from_if_none_match(header: str | None, revision: str | None) -> None:
    """Test that the first tag is read, with or without the weak mark."""
    assert ETags.revision_of(header) == revision
