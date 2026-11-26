# FastAPI

This rule covers HTTP applications with FastAPI. Database sessions are in [sql.md](./sql.md). The examples omit imports.

The layout and the layer direction are in [layers.md](./layers.md).

## Application factory

`<app>/main.py` has one factory: `create_app(*, settings: Settings | None = None) -> FastAPI`.

- Do not create the app at module level. Start the server with `uvicorn <app>.main:create_app --factory`.
- The lifespan opens the Container and puts it on `app.state.container`.
- The factory adds the middlewares, the routers, and the exception handlers.

```python
def create_app(*, settings: Settings | None = None) -> FastAPI:
    """Create the HTTP application."""
    settings = settings if settings is not None else Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        async with Container(settings) as container:
            app.state.container = container
            yield

    app = FastAPI(
        title=settings.title,
        description=API_DESCRIPTION,
        responses=DEFAULT_RESPONSES,
        generate_unique_id_function=RouteIds.generate,
        lifespan=lifespan,
    )
    Middlewares(settings).install(app)
    ErrorHandlers().install(app)
    app.include_router(create_api_router())
    return app
```

## Routers and versions

- Each feature has one `router.py` with `router = APIRouter()`. The feature router sets no prefix, no tags, and no router-level auth. A route can add its own permission check.
- `<app>/api/routers.py` mounts the feature routers. It is the only module that assigns the version prefixes, the tags, and the router-level dependencies.
- Add a version only for a breaking change. Put the changed endpoints in `<feature>/router_v2.py` and the changed payloads in `payloads.py` with the suffix `V2`. Mount the unchanged routers again. Do not copy an unchanged endpoint.
- To serve one router under two prefixes, mount it two times. Do not stack two route decorators on one function.

```python
def create_api_router() -> APIRouter:
    """Mount each API version under ``/api``."""
    router = APIRouter(prefix="/api")
    router.include_router(create_v1_router(), prefix="/v1")
    return router


def create_v1_router() -> APIRouter:
    """Mount the feature routers of version 1."""
    router = APIRouter()
    router.include_router(
        users.router,
        prefix="/users",
        tags=["Users"],
        dependencies=[AUTHENTICATED],
        responses=AUTH_RESPONSES,
    )
    router.include_router(auth.router, prefix="/auth", tags=["Auth"])
    return router
```

`AUTH_RESPONSES` holds the 401 and 403 responses. Pass it only for protected routers, so that public routes do not show 401 and 403 in Swagger. Write the arguments in full. Do not unpack a dictionary with `**`: the type checker cannot check it.

```python
AUTH_RESPONSES: Final[Responses] = {
    HTTPStatus.UNAUTHORIZED: ErrorResponse(NotAuthenticatedError).to_openapi(),
    HTTPStatus.FORBIDDEN: ErrorResponse(PermissionDeniedError).to_openapi(),
}
```

## Endpoints

An endpoint is an entry point:

1. FastAPI validates the input through the payload model and the dependencies.
2. The endpoint calls one service method.
3. The endpoint converts the result to a response payload.

An endpoint does not build SQL, call a repository, or contain business rules.

```python
@router.get(
    "/{user_id}",
    summary=UserDocs.READ.summary,
    description=UserDocs.READ.description,
    response_model=UserResponse,
    responses=UserResponses.READ,
    dependencies=[Depends(RequirePermission(Perm.USER_READ))],
)
async def read_user(user_id: UUID, users: UserServiceDep) -> UserResponse:
    """Return one user."""
    return UserResponse.model_validate(await users.get(user_id), from_attributes=True)
```

## Dependencies

There are two scopes:

| Scope | Examples | Source |
|---|---|---|
| Process | database, clients, storage | `@cached_property` on the Container. See [dependency-injection.md](../python/dependency-injection.md). |
| Request | session, current user, repositories, services | providers in `<feature>/deps.py` and `<app>/api/deps.py` |

Write each dependency as an `Annotated` alias named `<Name>Dep`. Use a plain assignment, not the `type` statement, so that FastAPI reads the `Depends` metadata. Do not write `= Depends(...)` as a default value.

```python
async def get_container(request: Request) -> Container:
    """Return the Container that the lifespan opened."""
    try:
        return request.app.state.container
    except AttributeError as error:
        raise ContainerNotStartedError() from error


ContainerDep = Annotated[Container, Depends(get_container)]


async def get_session(container: ContainerDep) -> AsyncGenerator[AsyncSession]:
    """Open one session for the request. Roll back what nobody committed."""
    async with container.database.session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_user_service(session: SessionDep, container: ContainerDep) -> UserService:
    """Return the user service of this request."""
    return UserService(
        users=UserRepository(session),
        groups=GroupRepository(session),
        uow=UnitOfWork(session),
        mailer=container.mailer,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
```

- Put each alias directly after its provider. Python evaluates annotations when the `def` runs, so an alias must exist before a provider uses it.
- A provider only creates objects and reads the request. It has no business logic.
- Never import a module-level Container in a provider, a route class, or a middleware.
- FastAPI caches the result of each provider for one request. All parameters that use the same provider get the same object.

## Authentication and permissions

- Authenticate in a dependency, not in a middleware. An error from a middleware does not reach the `AppError` handler. It becomes a 500 outside CORS, and a browser then reports a CORS failure.
- `get_current_user` reads the token through a FastAPI security scheme (for example `HTTPBearer(auto_error=False)`), so that Swagger shows the "Authorize" button. It raises `NotAuthenticatedError` (401).
- Mount protected routers with `dependencies=[AUTHENTICATED]`, where `AUTHENTICATED = Depends(get_current_user)`.
- Write a permission check as a class with `__init__` and `async def __call__`:

```python
class RequirePermission:
    """Reject the request when the current user does not have ``permission``."""

    def __init__(self, permission: Perm) -> None:
        self._permission = permission

    async def __call__(self, user: CurrentUserDep) -> User:
        if not user.has_permission(self._permission):
            raise PermissionDeniedError(self._permission)
        return user
```

- Get the tenant from the verified token. See [sql.md](./sql.md).

## Payloads

`<feature>/payloads.py` holds the HTTP contract. Keep it apart from `models.py` and `tables.py`.

| Name | Use |
|---|---|
| `XCreate` | Request body to create `X`. |
| `XUpdate` | Request body to change `X`. All fields are optional. |
| `XResponse` | Response body for one `X`. |
| `PageResponse[XResponse]` | Response body for a list, with `items` and `total`. |

- Never return an ORM object or a domain model. Return a payload.
- Give each field a `Field(description=...)`. Add `examples=[...]` when the format is not clear.
- Forbid unknown request fields: `model_config = ConfigDict(extra="forbid")`.

## Errors

Errors and their handlers are in [errors.md](./errors.md).

## OpenAPI documentation

Every route has complete Swagger documentation. See [openapi.md](./openapi.md).

## Middlewares and background work

See [middleware.md](./middleware.md).

## Tests

Test endpoints through HTTP with `httpx.AsyncClient` and `ASGITransport`. `ASGITransport` does not run the lifespan, so the fixture opens the Container.

```python
@pytest.fixture
async def app(settings: Settings) -> AsyncGenerator[FastAPI]:
    """Return an app with an open test Container."""
    app = create_app(settings=settings)
    async with Container(settings) as container:
        app.state.container = container
        yield app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient]:
    """Return an HTTP client for ``app``."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http
```

- Replace a request dependency with `app.dependency_overrides[get_current_user] = ...`. A new `app` for each test makes cleanup automatic.
- An override matches the callable object. Override `get_current_user`, not a `RequirePermission(...)` instance.
- Assert the status and the `code` of an error, not the message text.

Add one test for each feature router that checks its documentation. Walk the routes of the feature router. Do not walk `app.routes`. Recent FastAPI versions keep an included router as one `_IncludedRouter` entry, so a loop over `app.routes` finds no `APIRoute` and checks nothing.

```python
def test_every_route_is_documented() -> None:
    """Test that each user route has a summary, its own description, and responses."""
    for route in users.router.routes:
        assert isinstance(route, APIRoute)
        docstring = inspect.cleandoc(route.endpoint.__doc__ or "")
        assert route.summary, route.path
        assert route.description, route.path
        assert route.description != docstring, route.path
        assert route.responses, route.path
```

A route without `description=` gets the docstring as its description. The test compares with the docstring to find this case. Keep the `isinstance` assertion. It fails when the loop would skip a route.

## Checklist

- [ ] Does `create_app` build the app, with no module-level app or Container?
- [ ] Does each endpoint call one service method and return a payload?
- [ ] Is each dependency an `Annotated` alias named `<Name>Dep`?
- [ ] Does authentication run in a dependency, not in a middleware?
- [ ] Does each route have a summary, a description, and a `responses` entry for each status? Does each feature router have a documentation test? See [openapi.md](./openapi.md).
