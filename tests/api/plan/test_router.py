import inspect
from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from fastapi.routing import APIRoute
from httpx import AsyncClient

from decks.api.plan import router as plan_router
from decks.container import Container
from decks.models.build import Phase
from decks.models.plan import ContentBlock, Plan, SlideDraft
from tests.api.chat.conftest import QUESTION_ARGS, call, output

WriteChat = Callable[[str, list[dict[str, object]]], Awaitable[None]]


async def create(client: AsyncClient) -> str:
    """Create a project through the API and return its id."""
    return (await client.post("/api/v1/projects", json={"name": "Demo"})).json()["id"]


def save_plan(app: FastAPI, project_id: str, plan: Plan, phase: Phase) -> None:
    """Write a plan and a phase into the project folder."""
    repos = app.state.container.repositories.for_project(project_id)
    repos.plan.save(plan)
    repos.project.save_state(repos.project.load_state().model_copy(update={"phase": phase}))


def complete_plan() -> Plan:
    """A plan with the audience and one slide."""
    slide = SlideDraft(
        id="p1",
        kind="title",
        purpose="Open",
        title="Autumn launch",
        content=ContentBlock(summary="What is new.", points=["One", "Two"]),
    )
    return Plan(revision=3, meta={"audience": "Sales"}, slides=[slide])


async def test_plan_of_a_new_project_is_empty(client: AsyncClient) -> None:
    """Test that a project without a plan gives an empty plan that lacks audience and slides."""
    project = await create(client)
    body = (await client.get(f"/api/v1/projects/{project}/plan")).json()
    assert body["phase"] == "draft"
    assert body["slides"] == []
    assert body["missing"] == ["audience", "slides"]
    assert (body["can_approve"], body["pending_question"]) == (False, None)


async def test_plan_has_meta_and_slides_with_key_info(client: AsyncClient, app: FastAPI) -> None:
    """Test that the plan shows the meta and each slide with kind, title, summary and points."""
    project = await create(client)
    save_plan(app, project, complete_plan(), "review")
    body = (await client.get(f"/api/v1/projects/{project}/plan")).json()
    assert (body["phase"], body["revision"], body["approved"]) == ("review", 3, False)
    assert body["meta"] == {"audience": "Sales"}
    assert body["missing"] == []
    assert body["can_approve"] is True
    assert body["slides"] == [
        {
            "id": "p1",
            "kind": "title",
            "purpose": "Open",
            "title": "Autumn launch",
            "summary": "What is new.",
            "points": ["One", "Two"],
        }
    ]


async def test_plan_shows_the_pending_question(
    client: AsyncClient, app: FastAPI, write_chat: WriteChat
) -> None:
    """Test that an unanswered question shows while the interview runs, and not after it."""
    project = await create(client)
    await write_chat(
        project,
        [
            {"role": "user", "content": "go"},
            call("c1", "ask_user_question", QUESTION_ARGS),
            output("c1", "q"),
        ],
    )
    asking = (await client.get(f"/api/v1/projects/{project}/plan")).json()
    assert asking["pending_question"]["question"] == "Who is the deck for?"
    save_plan(app, project, complete_plan(), "generating")
    later = (await client.get(f"/api/v1/projects/{project}/plan")).json()
    assert later["pending_question"] is None


async def test_approve_moves_the_project_to_approved(client: AsyncClient, app: FastAPI) -> None:
    """Test that approving a complete plan approves it and sets the phase."""
    project = await create(client)
    save_plan(app, project, complete_plan(), "review")
    response = await client.post(f"/api/v1/projects/{project}/plan/approve")
    assert response.status_code == 200
    body = response.json()
    assert (body["approved"], body["phase"], body["can_approve"]) == (True, "approved", False)
    assert (await client.get(f"/api/v1/projects/{project}")).json()["phase"] == "approved"


async def test_approve_without_a_plan_is_409(client: AsyncClient) -> None:
    """Test that a project without a plan cannot be approved."""
    project = await create(client)
    response = await client.post(f"/api/v1/projects/{project}/plan/approve")
    assert (response.status_code, response.json()["code"]) == (409, "PlanMissingError")


async def test_approve_an_incomplete_plan_is_409(client: AsyncClient, app: FastAPI) -> None:
    """Test that a plan without slides cannot be approved."""
    project = await create(client)
    save_plan(app, project, Plan(meta={"audience": "Sales"}), "interviewing")
    response = await client.post(f"/api/v1/projects/{project}/plan/approve")
    assert (response.status_code, response.json()["code"]) == (409, "PlanIncompleteError")


async def test_approve_after_the_interview_is_409(client: AsyncClient, app: FastAPI) -> None:
    """Test that a plan in use cannot be approved again, so the phase is not reset."""
    project = await create(client)
    save_plan(app, project, complete_plan(), "generated")
    response = await client.post(f"/api/v1/projects/{project}/plan/approve")
    assert (response.status_code, response.json()["code"]) == (409, "PlanLockedError")
    assert (await client.get(f"/api/v1/projects/{project}")).json()["phase"] == "generated"


async def test_approve_while_a_turn_runs_is_409(client: AsyncClient, app: FastAPI) -> None:
    """Test that approval waits for the running turn."""
    project = await create(client)
    save_plan(app, project, complete_plan(), "review")
    container: Container = app.state.container
    async with container.repositories.for_project(project).turn_lock:
        response = await client.post(f"/api/v1/projects/{project}/plan/approve")
    assert (response.status_code, response.json()["code"]) == (409, "TurnInProgressError")


async def test_unknown_project_is_404(client: AsyncClient) -> None:
    """Test that both plan endpoints give ``ProjectNotFoundError``."""
    assert (await client.get("/api/v1/projects/missing/plan")).json()[
        "code"
    ] == "ProjectNotFoundError"
    approve = await client.post("/api/v1/projects/missing/plan/approve")
    assert approve.json()["code"] == "ProjectNotFoundError"


def test_every_route_is_documented() -> None:
    """Test that each plan route has a summary, its own description, and responses."""
    for route in plan_router.router.routes:
        assert isinstance(route, APIRoute)
        docstring = inspect.cleandoc(route.endpoint.__doc__ or "")
        assert route.summary, route.path
        assert route.description, route.path
        assert route.description != docstring, route.path
        assert route.responses, route.path
