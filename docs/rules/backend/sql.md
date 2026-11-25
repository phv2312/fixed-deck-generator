# SQL Repositories (SQLAlchemy async)

This rule extends the Repository pattern in [design-patterns.md](../python/design-patterns.md) for a relational database. The examples use SQLAlchemy 2 with `AsyncSession`. The examples omit imports.

## Classes of one entity

| Class | File | Use |
|---|---|---|
| `User` (ORM) | `<feature>/tables.py` | The table. Subclass the shared `Base` and mixins such as `AuditMixin`. |
| `UserDBCreate`, `UserDBUpdate` | `<feature>/models.py` | The values that the repository writes. `UserDBUpdate` has only optional fields. |
| `User` (pydantic) | `<feature>/models.py` | Optional. Add it only when a service needs the data apart from the table. |

Repositories can return ORM objects. Services can read them. Only an entry point converts them to a payload.

## Shared code in `<app>/db/`

- `Database` owns the engine and the session factory. The Container creates one `Database` and disposes it at shutdown.
- Create the session factory with `expire_on_commit=False`. Without it, an attribute read after a commit raises `MissingGreenlet` in async code.
- `Base` is the declarative base. Put shared column types in its `type_annotation_map`. Annotate it as `ClassVar[dict[Any, Any]]`. `BaseWithID` is an abstract subclass of `Base` with `id: Mapped[Any]`. Each table that has an `id` subclasses it.
- The `AsyncSession` is the store of an SQL repository. There is no separate store class.
- `EntityRepository[TableT: BaseWithID, IdT]` gives `get`, `find`, `find_many`, `create`, `update`, and `remove`. These names replace `save` and `delete` of the generic repository, because SQL writes a new row and a changed row differently.
- Bind `TableT` to `BaseWithID`, so that `self.Table.id` type-checks. Do not add a suppression comment. Declare the table as `Table: type[TableT]`. Do not write `ClassVar[type[TableT]]`. A type variable is not valid in `ClassVar`.
- The repository keeps the session in `self._session`.
- `restrain(stmt)` adds the scope conditions to a statement. Scope mixins override it and call `super().restrain(stmt)`. Examples are `SoftDeleteMixin` (hides deleted rows) and `OwnerScopeMixin` (shows only the rows of the owner).

```python
class UserRepository(SoftDeleteMixin[User, UUID], EntityRepository[User, UUID]):
    """Persist users."""

    Table = User

    async def find_by_username(self, username: str) -> User | None:
        """Return the user with ``username``, or ``None``."""
        stmt = select(User).where(User.username == username)
        return await self._session.scalar(self.restrain(stmt))
```

Rules:

- Send every statement through `restrain()`. A query that skips the scope is a security defect.
- Load each relationship that the caller needs inside the repository, with `selectinload` or `joinedload`.
- Set `lazy="raise"` on relationships. Then an unplanned lazy load fails in tests, not in production.
- Convert driver errors into feature errors, for example an `IntegrityError` on a unique name into `UserExistsError`.

## Sessions and transactions

One unit of work has one session and one transaction.

1. The entry point opens the session: a request dependency in FastAPI, or the `main` of a worker or CLI.
2. Each repository gets the session through its constructor.
3. A repository can call `flush()` to get generated values. **A repository never commits.**
4. A service that writes owns the transaction through a `UnitOfWork` collaborator. The service never calls the session directly.
5. The session closes at the end of the unit of work. A transaction that nobody committed rolls back.

```python
class UnitOfWork:
    """Commit the session when the block succeeds. Roll it back when the block raises."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        if exc_type is None:
            await self._session.commit()
            return
        await self._session.rollback()


class UserService:
    def __init__(self, users: UserRepository, groups: GroupRepository, uow: UnitOfWork) -> None:
        self._users = users
        self._groups = groups
        self._uow = uow

    async def create(self, user: UserDBCreate, group_id: UUID) -> User:
        """Create the user and add it to the group in one transaction."""
        async with self._uow:
            created = await self._users.create(user)
            await self._groups.add_member(group_id, created.id)
        return created
```

- Do not share one `AsyncSession` between concurrent tasks. Give each task of a `TaskGroup` its own session.
- Do not commit in a dependency teardown. The response can already be sent when the teardown runs, and a failed commit is then lost.

## Multi-tenancy

When each tenant has its own schema:

- Get the tenant from a verified source, for example a signed token claim. Look up the schema name in the tenant table. Never take a schema name from a header, a path, or a query parameter.
- Bind the session of a request to `engine.execution_options(schema_translate_map={None: schema})`. Do not set the schema on the session connection. That setting ends with the transaction, and the next transaction of the session can then reach the wrong tenant.
- Keep shared tables (tenants, global users) in a fixed schema.

## Sort, filter, and pagination

- Define the sort keys of a feature as a `StrEnum`. Map each key to a column in the repository. Do not accept a raw column name or path from the user.
- Add the primary key as the last sort key, so that the order is stable between pages.
- Limit the page size with a maximum, for example `Annotated[int, Field(ge=1, le=100)]`.

## Migrations

- Use Alembic. Each schema change has one migration in the same change as the code.
- Review each autogenerated migration. Autogenerate misses enum changes, server defaults, and renames.
- Never call `Base.metadata.create_all` outside tests of the ORM itself. Production and repository tests run the migrations.
- With one schema for each tenant, the migration environment applies each migration to each tenant schema.

## Tests

- Test a repository against a real database of the production engine. Start it with `testcontainers`. Do not use SQLite in place of PostgreSQL.
- Start the container one time for each test session. Run the migrations one time.
- With `pytest-xdist`, give each worker its own database or schema.
- Isolate each test. Either `TRUNCATE` the tables after it, or run it in an outer transaction that the fixture rolls back. For the second method, create the session with `join_transaction_mode="create_savepoint"`, so that a commit of the `UnitOfWork` releases a savepoint only.
- A session-scoped async engine needs session-scoped event loops. Set `asyncio_default_fixture_loop_scope = "session"` and `asyncio_default_test_loop_scope = "session"`. Otherwise the engine raises "attached to a different loop".

## Checklist

- [ ] Does each statement go through `restrain()`?
- [ ] Does only the `UnitOfWork` of a service commit?
- [ ] Does the tenant schema come from a verified source?
- [ ] Does each schema change have a reviewed migration?
