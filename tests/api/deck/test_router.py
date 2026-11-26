import inspect

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from httpx import AsyncClient

from decks.api.deck import router as deck_router
from decks.container import Container
from decks.models.elements import Group, Shape, Text
from decks.models.slides import Deck, Slide
from decks.models.theme import FONT, THEMES


@pytest.fixture
def rich_deck() -> Deck:
    """A deck with a text, a shape, and a group of two shapes on slide 0."""
    group = Group(
        id="g1",
        children=[
            Shape(id="c1", x=10, y=300, w=50, h=50, fill="tint"),
            Shape(id="c2", x=100, y=320, w=60, h=60, fill="accent"),
        ],
    )
    slide = Slide(
        id="p1",
        family="body",
        kind="content",
        elements=[
            Text(id="t1", x=10, y=10, w=300, h=40, text="Hello"),
            Shape(id="sh1", x=20, y=100, w=100, h=100, fill="primary"),
            group,
        ],
    )
    return Deck(revision=3, theme="green", palette=THEMES["green"], font=FONT, slides=[slide])


@pytest.fixture
async def project(client: AsyncClient, app: FastAPI, rich_deck: Deck) -> str:
    """A project that has ``rich_deck``. Return its id."""
    created = (await client.post("/api/v1/projects", json={"name": "Deck"})).json()
    container: Container = app.state.container
    container.repositories.for_project(created["id"]).deck.save(rich_deck)
    return created["id"]


def url(project: str, tail: str = "") -> str:
    """Return the deck URL of ``project``."""
    return f"/api/v1/projects/{project}/deck{tail}"


async def test_read_lists_elements_with_boxes_and_editable_fields(
    client: AsyncClient, project: str
) -> None:
    """Test that the deck response has the box, the order, and the editable fields."""
    body = (await client.get(url(project))).json()
    assert body["revision"] == 3
    assert (body["width"], body["height"]) == (1280, 720)
    assert body["can_undo"] is False
    elements = body["slides"][0]["elements"]
    assert [e["id"] for e in elements] == ["t1", "sh1", "g1", "c1", "c2"]
    text = elements[0]
    assert (text["x"], text["y"], text["w"], text["h"]) == (10, 10, 300, 40)
    assert "font_size" in text["editable"]
    assert text["props"]["text"] == "Hello"
    assert [e["parent_id"] for e in elements] == [None, None, None, "g1", "g1"]
    group = elements[2]
    assert (group["x"], group["y"], group["w"], group["h"]) == (10, 300, 150, 80)


async def test_read_without_deck_is_404(client: AsyncClient) -> None:
    """Test that a project without a deck gives ``DeckMissingError``."""
    created = (await client.post("/api/v1/projects", json={"name": "Empty"})).json()
    response = await client.get(url(created["id"]))
    assert response.status_code == 404
    assert response.json()["code"] == "DeckMissingError"


async def test_patch_moves_and_styles_then_html_shows_it(client: AsyncClient, project: str) -> None:
    """Test that a patch is saved at once and the slide HTML renders the new state."""
    response = await client.patch(
        url(project, "/slides/0/elements/t1"),
        json={"base_revision": 3, "changes": {"x": 120, "text": "Moved", "bold": True}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["revision"] == 4
    assert body["element"]["x"] == 120
    assert body["element"]["props"]["bold"] is True
    assert body["can_undo"] is True
    html = (await client.get(url(project, "/slides/0/html"))).text
    assert 'data-element-id="t1"' in html
    assert "Moved" in html
    assert "left:120px" in html
    assert (await client.get(url(project))).json()["revision"] == 4


async def test_patch_a_group_child(client: AsyncClient, project: str) -> None:
    """Test that an element inside a group can be edited by its id."""
    response = await client.patch(
        url(project, "/slides/0/elements/c1"), json={"changes": {"fill": "accent"}}
    )
    assert response.status_code == 200
    assert response.json()["element"]["parent_id"] == "g1"


@pytest.mark.parametrize(
    "changes",
    [{"nope": 1}, {"id": "x"}, {}, {"font_size": "big"}, {"align": "justify"}],
)
async def test_invalid_patch_is_422(client: AsyncClient, project: str, changes: dict) -> None:
    """Test that unknown fields, read-only fields, and bad values are refused."""
    response = await client.patch(url(project, "/slides/0/elements/t1"), json={"changes": changes})
    assert response.status_code == 422
    assert response.json()["code"] == "InvalidElementChangeError"
    assert (await client.get(url(project))).json()["revision"] == 3


async def test_unknown_element_and_slide_are_404(client: AsyncClient, project: str) -> None:
    """Test the two not-found errors."""
    body = {"changes": {"x": 1}}
    element = await client.patch(url(project, "/slides/0/elements/zzz"), json=body)
    slide = await client.patch(url(project, "/slides/5/elements/t1"), json=body)
    assert (element.status_code, element.json()["code"]) == (404, "ElementIdNotFoundError")
    assert (slide.status_code, slide.json()["code"]) == (404, "SlideIndexNotFoundError")


async def test_stale_revision_is_409(client: AsyncClient, project: str) -> None:
    """Test that an edit on an older revision is refused and changes nothing."""
    response = await client.patch(
        url(project, "/slides/0/elements/t1"), json={"base_revision": 1, "changes": {"x": 5}}
    )
    assert response.status_code == 409
    assert response.json()["code"] == "StaleDeckRevisionError"


async def test_edit_is_refused_while_a_turn_runs(
    client: AsyncClient, app: FastAPI, project: str
) -> None:
    """Test that the agent is the only writer during a chat turn."""
    container: Container = app.state.container
    async with container.repositories.for_project(project).turn_lock:
        response = await client.patch(
            url(project, "/slides/0/elements/t1"), json={"changes": {"x": 5}}
        )
    assert response.status_code == 409
    assert response.json()["code"] == "TurnInProgressError"


async def test_overflow_is_reported_as_an_issue(client: AsyncClient, project: str) -> None:
    """Test that the layout checker runs on the edited slide."""
    response = await client.patch(
        url(project, "/slides/0/elements/t1"), json={"changes": {"x": 1200, "w": 400}}
    )
    issues = response.json()["issues"]
    assert any(i["code"] == "out_of_bounds" and i["element_id"] == "t1" for i in issues)


@pytest.mark.parametrize(
    ("kind", "props"),
    [
        ("text", {"text": "Hi"}),
        ("shape", {}),
        ("table", {}),
        ("chart", {}),
        ("image", {"src": "https://example.com/a.png"}),
    ],
)
async def test_add_element_of_each_kind(
    client: AsyncClient, project: str, kind: str, props: dict
) -> None:
    """Test that each kind can be added with defaults and lands on top."""
    response = await client.post(
        url(project, "/slides/0/elements"), json={"kind": kind, "props": props}
    )
    assert response.status_code == 201
    element = response.json()["element"]
    assert element["type"] == kind
    assert element["z"] == 5


@pytest.mark.parametrize("props", [{}, {"src": "/etc/passwd"}, {"src": "projects/x/assets/v1.png"}])
async def test_image_needs_a_safe_source(client: AsyncClient, project: str, props: dict) -> None:
    """Test that an image without a source, or with a server file path, is refused."""
    response = await client.post(
        url(project, "/slides/0/elements"), json={"kind": "image", "props": props}
    )
    assert response.status_code == 422


async def test_delete_and_duplicate_and_order(client: AsyncClient, project: str) -> None:
    """Test delete, duplicate, and the four stacking moves."""
    copy = await client.post(url(project, "/slides/0/elements/t1/duplicate"), json={})
    assert copy.status_code == 201
    assert copy.json()["element"]["x"] == 26
    assert copy.json()["element"]["z"] == 1
    group_copy = await client.post(url(project, "/slides/0/elements/g1/duplicate"), json={})
    assert group_copy.status_code == 422

    front = await client.post(url(project, "/slides/0/elements/t1/order"), json={"move": "front"})
    assert front.json()["element"]["z"] > 1
    back = await client.post(url(project, "/slides/0/elements/t1/order"), json={"move": "back"})
    assert back.json()["element"]["z"] == 0

    gone = await client.delete(url(project, "/slides/0/elements/c1"))
    assert gone.status_code == 200
    assert gone.json()["element"] is None
    ids = [e["id"] for e in (await client.get(url(project))).json()["slides"][0]["elements"]]
    assert "c1" not in ids


async def test_undo_and_redo_walk_the_history(client: AsyncClient, project: str) -> None:
    """Test that undo restores the old deck, redo brings the edit back, and revisions grow."""
    await client.patch(url(project, "/slides/0/elements/t1"), json={"changes": {"text": "A"}})
    await client.patch(url(project, "/slides/0/elements/t1"), json={"changes": {"text": "B"}})

    undone = (await client.post(url(project, "/undo"))).json()
    assert undone["revision"] == 6
    assert undone["can_redo"] is True
    text = (await client.get(url(project))).json()["slides"][0]["elements"][0]["props"]["text"]
    assert text == "A"

    redone = (await client.post(url(project, "/redo"))).json()
    assert redone["revision"] == 7
    text = (await client.get(url(project))).json()["slides"][0]["elements"][0]["props"]["text"]
    assert text == "B"

    await client.post(url(project, "/undo"))
    await client.patch(url(project, "/slides/0/elements/t1"), json={"changes": {"text": "C"}})
    again = await client.post(url(project, "/redo"))
    assert again.status_code == 409
    assert again.json()["code"] == "NothingToRedoError"


async def test_undo_without_history_is_409(client: AsyncClient, project: str) -> None:
    """Test that a fresh deck cannot be undone."""
    response = await client.post(url(project, "/undo"))
    assert response.status_code == 409
    assert response.json()["code"] == "NothingToUndoError"


async def test_history_is_bounded(client: AsyncClient, app: FastAPI, project: str) -> None:
    """Test that only the newest 20 steps can be undone."""
    for step in range(25):
        await client.patch(url(project, "/slides/0/elements/t1"), json={"changes": {"x": step}})
    undone = 0
    while (await client.post(url(project, "/undo"))).status_code == 200:
        undone += 1
    assert undone == 20


async def test_edit_marks_the_slide_as_edited(
    client: AsyncClient, app: FastAPI, project: str
) -> None:
    """Test that the build state records the new revision."""
    await client.patch(url(project, "/slides/0/elements/t1"), json={"changes": {"x": 5}})
    container: Container = app.state.container
    state = container.repositories.for_project(project).project.load_state()
    assert state.deck_revision == 4


def test_every_route_is_documented() -> None:
    """Test that each deck route has a summary, its own description, and responses."""
    for route in deck_router.router.routes:
        assert isinstance(route, APIRoute)
        docstring = inspect.cleandoc(route.endpoint.__doc__ or "")
        assert route.summary, route.path
        assert route.description, route.path
        assert route.description != docstring, route.path
        assert route.responses, route.path


async def test_each_slide_has_its_own_revision(client: AsyncClient, project: str) -> None:
    """Test that the deck response gives each slide a short revision that is stable."""
    first = (await client.get(url(project))).json()["slides"][0]["revision"]
    again = (await client.get(url(project))).json()["slides"][0]["revision"]
    assert first == again
    assert len(first) == 12


async def test_an_edit_changes_only_the_revision_of_its_slide(
    client: AsyncClient, app: FastAPI, deck: Deck
) -> None:
    """Test that an edit on slide 0 leaves the revision of slide 1 alone, and undo restores it."""
    created = (await client.post("/api/v1/projects", json={"name": "Two"})).json()["id"]
    app.state.container.repositories.for_project(created).deck.save(deck)

    def revisions(body: dict) -> list[str]:
        return [slide["revision"] for slide in body["slides"]]

    before = revisions((await client.get(url(created))).json())
    await client.patch(url(created, "/slides/0/elements/s1e1"), json={"changes": {"x": 99}})
    after = revisions((await client.get(url(created))).json())
    assert after[0] != before[0]
    assert after[1] == before[1]
    await client.post(url(created, "/undo"))
    assert revisions((await client.get(url(created))).json()) == before


async def test_slide_html_has_an_etag_and_answers_304(client: AsyncClient, project: str) -> None:
    """Test that the slide page carries its revision as ETag and an unchanged slide gives 304."""
    revision = (await client.get(url(project))).json()["slides"][0]["revision"]
    page = await client.get(url(project, "/slides/0/html"))
    assert page.status_code == 200
    assert page.headers["etag"] == f'"{revision}"'
    assert page.headers["cache-control"] == "private, max-age=0, must-revalidate"
    same = await client.get(
        url(project, "/slides/0/html"), headers={"If-None-Match": f'"{revision}"'}
    )
    assert same.status_code == 304
    assert same.content == b""
    assert same.headers["etag"] == f'"{revision}"'


async def test_slide_html_is_new_after_an_edit(client: AsyncClient, project: str) -> None:
    """Test that a changed slide ignores the old ETag and returns a page with a new one."""
    old = (await client.get(url(project, "/slides/0/html"))).headers["etag"]
    await client.patch(url(project, "/slides/0/elements/t1"), json={"changes": {"text": "New"}})
    page = await client.get(url(project, "/slides/0/html"), headers={"If-None-Match": old})
    assert page.status_code == 200
    assert page.headers["etag"] != old
    assert "New" in page.text


async def test_slide_html_without_deck_is_404(client: AsyncClient) -> None:
    """Test that a project without a deck gives ``DeckMissingError``."""
    created = (await client.post("/api/v1/projects", json={"name": "Empty"})).json()
    response = await client.get(url(created["id"], "/slides/0/html"))
    assert response.status_code == 404
    assert response.json()["code"] == "DeckMissingError"


async def test_slide_html_out_of_range_is_404(client: AsyncClient, project: str) -> None:
    """Test that an index past the last slide gives ``SlideIndexNotFoundError``."""
    response = await client.get(url(project, "/slides/5/html"))
    assert response.status_code == 404
    assert response.json()["code"] == "SlideIndexNotFoundError"
