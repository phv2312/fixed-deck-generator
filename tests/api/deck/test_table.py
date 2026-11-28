import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from decks.container import Container
from decks.models.elements import Table
from decks.models.slides import Deck, Slide
from decks.models.theme import FONT, THEMES

TABLE = Table(
    id="tb1",
    x=64,
    y=150,
    w=1152,
    h=162,
    rows=[["Head", "Score"], ["CTC", "12"], ["RNN-T", "14"]],
    font_size=18,
    col_widths=[0.5, 0.5],
    align=["left", "right"],
    row_height=54,
    highlight_row=1,
    highlight_col=1,
    rules="lines",
)


@pytest.fixture
async def project(client: AsyncClient, app: FastAPI) -> str:
    """A project with one slide that holds ``TABLE``. Return its id."""
    created = (await client.post("/api/v1/projects", json={"name": "Deck"})).json()
    slide = Slide(id="p1", family="body", kind="table", elements=[TABLE])
    deck = Deck(revision=1, theme="green", palette=THEMES["green"], font=FONT, slides=[slide])
    container: Container = app.state.container
    container.repositories.for_project(created["id"]).deck.save(deck)
    return created["id"]


async def patch(client: AsyncClient, project: str, changes: dict) -> dict:
    """PATCH the table and return the JSON body."""
    url = f"/api/v1/projects/{project}/deck/slides/0/elements/tb1"
    response = await client.patch(url, json={"changes": changes})
    return {"status": response.status_code, **response.json()}


def rows(count: int, columns: int = 2) -> list[list[str]]:
    """Return ``count`` rows of ``columns`` cells."""
    return [[f"r{i}c{j}" for j in range(columns)] for i in range(count)]


async def test_text_edit_keeps_the_layout(client: AsyncClient, project: str) -> None:
    """Test that a change of cell text alone leaves the height and the font as they are."""
    body = await patch(
        client, project, {"rows": [["Head", "Score"], ["CTC", "99"], ["RNN-T", "14"]]}
    )

    props = body["element"]["props"]
    assert body["status"] == 200
    assert props["rows"][1] == ["CTC", "99"]
    assert (props["h"], props["font_size"], props["row_height"]) == (162, 18, 54)


async def test_added_row_grows_the_table(client: AsyncClient, project: str) -> None:
    """Test that one more row makes the table one row height taller."""
    body = await patch(client, project, {"rows": rows(4)})

    props = body["element"]["props"]
    assert props["h"] == 4 * 54
    assert props["highlight_row"] == 1  # the highlighted row is still there


async def test_many_rows_shrink_the_rows_and_the_font(client: AsyncClient, project: str) -> None:
    """Test that 13 rows share the table height and take a smaller font, as the builder does."""
    props = (await patch(client, project, {"rows": rows(14)}))["element"]["props"]

    assert props["row_height"] == pytest.approx(450 / 14)
    assert props["h"] == pytest.approx(450)
    assert props["font_size"] == 14  # 13 body rows: the small step


async def test_added_column_gets_a_width_and_an_alignment(
    client: AsyncClient, project: str
) -> None:
    """Test that a third column makes new widths that sum to 1 and a 3 entry alignment."""
    props = (await patch(client, project, {"rows": rows(3, columns=3)}))["element"]["props"]

    assert len(props["col_widths"]) == 3
    assert sum(props["col_widths"]) == pytest.approx(1)
    assert len(props["align"]) == 3
    assert props["highlight_col"] == 1


async def test_removed_row_and_column_drop_the_highlight(client: AsyncClient, project: str) -> None:
    """Test that a highlight that leaves the table becomes null instead of an error."""
    props = (await patch(client, project, {"rows": [["Head"], ["CTC"]]}))["element"]["props"]

    assert props["highlight_row"] is None  # only the body row 0 is left
    assert props["highlight_col"] is None  # the column 1 is gone
    assert props["col_widths"] == [1.0]


@pytest.mark.parametrize(
    "changes",
    [
        {"rows": [["a", "b"], ["c"]]},
        {"rows": "not rows"},
        {"rows": [[]]},
        {"rows": [["a"]] * 41},
        {"col_widths": [1.0]},
        {"highlight_row": 5},
    ],
)
async def test_invalid_table_change_is_refused(
    client: AsyncClient, project: str, changes: dict
) -> None:
    """Test that a ragged table, bad rows, or a list of the wrong size gives 422."""
    body = await patch(client, project, changes)

    assert body["status"] == 422
    assert body["code"] == "InvalidElementChangeError"


async def test_cell_overflow_is_reported(client: AsyncClient, project: str) -> None:
    """Test that a very long cell shows as an issue on the table."""
    long = "word " * 200
    body = await patch(client, project, {"rows": [["Head", "Score"], [long, "1"], ["a", "2"]]})

    assert any(i["code"] == "text_overflow" and i["element_id"] == "tb1" for i in body["issues"])


async def test_client_values_win_over_the_computed_layout(
    client: AsyncClient, project: str
) -> None:
    """Test that an explicit height in the same patch is kept when the rows change shape."""
    props = (await patch(client, project, {"rows": rows(4), "h": 300}))["element"]["props"]

    assert props["h"] == 300
    assert props["row_height"] == 54
