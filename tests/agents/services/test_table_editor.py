import pytest
from agents.testing import ScriptedModel
from pydantic import ValidationError

from decks.agents.exceptions import ElementNotFoundError
from decks.agents.repos import Repos
from decks.models.elements import Table, Text
from decks.models.slides import Deck, Slide
from decks.models.theme import FONT, THEMES
from tests.agents.conftest import make_context

TABLE = Table(
    id="tb1",
    x=64,
    y=150,
    w=1152,
    h=162,
    rows=[["Head", "Score"], ["CTC", "12"], ["RNN-T", "14"]],
    font_size=18,
    row_height=54,
    col_widths=[0.5, 0.5],
    align=["left", "right"],
)


@pytest.fixture
def saved(repos: Repos) -> Repos:
    """Repos whose deck has one slide with a title text and ``TABLE``."""
    title = Text(id="t1", x=64, y=40, w=1152, h=60, text="Title")
    slide = Slide(id="p1", family="body", kind="table", elements=[title, TABLE])
    deck = Deck(revision=1, theme="green", palette=THEMES["green"], font=FONT, slides=[slide])
    repos.deck.save(deck)
    return repos


def test_agent_reads_every_cell_of_a_table(saved: Repos) -> None:
    """Test that the slide view lists the cells, so the agent can change them."""
    editor = make_context(saved, ScriptedModel([])).editor

    view = next(e for e in editor.read_slide("p1").elements if e.id == "tb1")

    assert view.text == '[["Head", "Score"], ["CTC", "12"], ["RNN-T", "14"]]'
    assert "rows" not in view.style


def test_agent_adds_a_row_and_a_column(saved: Repos) -> None:
    """Test that new rows and columns get a layout and the edit is saved and marked."""
    editor = make_context(saved, ScriptedModel([])).editor
    rows = [["Head", "Score", "Note"], ["CTC", "12", "a"], ["RNN-T", "14", "b"], ["Att", "9", "c"]]

    editor.set_table("p1", "tb1", rows)

    table = saved.deck.load().slides[0].element("tb1")
    assert isinstance(table, Table)
    assert table.rows == rows
    assert table.h == 4 * 54
    assert len(table.col_widths or []) == 3
    assert len(table.align or []) == 3
    assert saved.deck.load().revision == 2


def test_agent_cannot_set_rows_of_a_text(saved: Repos) -> None:
    """Test that a non-table element raises the typed not-found error."""
    editor = make_context(saved, ScriptedModel([])).editor

    with pytest.raises(ElementNotFoundError):
        editor.set_table("p1", "t1", [["a"]])


def test_view_keeps_every_row_of_a_long_table(saved: Repos) -> None:
    """Test that a big table is not cut, so a set_table call never drops a row it did not see."""
    editor = make_context(saved, ScriptedModel([])).editor
    rows = [["Head", "Score"], *([[f"row {i} " + "x" * 40, "1"] for i in range(30)])]
    editor.set_table("p1", "tb1", rows)

    view = next(e for e in editor.read_slide("p1").elements if e.id == "tb1")

    assert view.text is not None
    assert len(view.text) > 1500
    assert view.text.count("row ") == 30


@pytest.mark.parametrize("rows", [[["a", "b"], ["c"]], [[]], []])
def test_set_table_refuses_rows_that_are_not_a_table(saved: Repos, rows: list[list[str]]) -> None:
    """Test that uneven or empty rows raise and leave the saved deck as it was."""
    editor = make_context(saved, ScriptedModel([])).editor

    with pytest.raises(ValidationError):
        editor.set_table("p1", "tb1", rows)

    assert saved.deck.load().revision == 1


def test_view_shows_a_highlight_on_the_first_row_and_column(saved: Repos) -> None:
    """Test that a highlight index of 0 reaches the agent: 0 is a real value, not False."""
    deck = saved.deck.load()
    slide = deck.slides[0].patched("tb1", {"highlight_row": 0, "highlight_col": 0, "header": False})
    saved.deck.save(deck.model_copy(update={"slides": [slide]}))
    editor = make_context(saved, ScriptedModel([])).editor

    view = next(e for e in editor.read_slide("p1").elements if e.id == "tb1")

    assert view.style["highlight_row"] == "0"
    assert view.style["highlight_col"] == "0"
    assert "header" not in view.style  # False stays hidden
