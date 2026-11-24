---
paths:
  - "**/*.py"
---
# Dependency Injection (Container)

A Container creates the dependencies of an application and connects them. Services get their collaborators through the constructor. Only entry points use the Container.

Related rules:

- [design-patterns.md](./design-patterns.md): the strategies, repositories, and clients that the Container creates.
- [modular-design.md](./modular-design.md): the `Settings` class and the entry points.

The examples omit imports. The names come from `collections.abc`, `contextlib`, `functools`, and `typing`.

## Use it when

- The application has two or more services, or it has a resource that must be closed. Examples of resources are a database pool and an HTTP client.

A small script with one service can create its objects in `main`. It does not need a Container.

## Structure

1. Write one Container class for each application, in `<app>/container.py`. Write it by hand. Do not use a DI library.
2. Give the settings to the Container constructor: `Container(settings: Settings)`. The Container does not read environment variables or files itself.
3. Make each dependency a `@cached_property`. The Container creates the dependency on first use and shares it for its own life.
4. When a dependency must be new for each use, add a factory method, for example `def new_session(self) -> Session`. Do not use a property for it.
5. Do heavy or optional imports inside the property body. Then the application loads them only when it needs them.
6. When the settings select a strategy, the Container does the selection.

```python
class Container:
    """Create and connect the dependencies of the app. Build it only at an entry point."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._stack = ExitStack()

    @cached_property
    def fonts(self) -> FontStore:
        return FontStore(self._settings.font_dir)

    @cached_property
    def exporters(self) -> Mapping[ExportFormat, Exporter]:
        return {e.KEY: e for e in (CsvExporter(), PdfExporter(self.fonts))}

    @cached_property
    def database(self) -> Database:
        return self._stack.enter_context(Database(self._settings.database_url))

    @cached_property
    def orders(self) -> OrderRepository:
        return OrderRepository(JsonDirStore(self._settings.data_dir / "orders"))

    @cached_property
    def report_service(self) -> ReportService:
        return ReportService(orders=self.orders, exporters=self.exporters)
```

## Default collaborators

A class may take an optional collaborator and create a default for it. Use this form:

```python
class VisualService:
    def __init__(self, assets: AssetRepository, rasterizer: Rasterizer | None = None) -> None:
        self._assets = assets
        self._rasterizer = rasterizer if rasterizer is not None else Rasterizer()
```

Use a default only when all these conditions are true:

- The default is cheap and has no shared state. Its state is private to the owner.
- Creating it needs no settings, no network, and no file access.
- It holds no resource that must be closed.

Test for `is None`. Do not write `rasterizer or Rasterizer()`. The `or` form replaces any falsy argument, for example a fake with `__bool__` or `__len__`.

When one condition is false, make the collaborator a required parameter. Create it in the Container.

## Where to build it

- Build the Container only at an entry point: a CLI command, the server start-up, a script `main`, or a test fixture.
- Never build a Container at module level. A global Container reads the settings at import time. It also shares state between tests.

```python
# Wrong — a global instance, created at import time
container = Container(Settings())


# Correct — the Typer command builds it
@app.command()
def export(order_id: str, fmt: ExportFormat) -> None:
    with Container(Settings()) as container:
        sys.stdout.buffer.write(container.report_service.export(order_id, fmt))
```

`cached_property` has no lock. In a server with threads, build the Container before the server starts its threads. Get each resource property one time at start-up.

## The Container stays at the edge

- Only entry points use the Container. They get the top-level service from it and call that service.
- Services, repositories, strategies, and models never import `Container`. They get their collaborators through the constructor, or they create a default as "Default collaborators" allows.
- Do not add a `from_container(container)` method to a domain class. This is the service locator pattern. It hides the real dependencies and puts the selection keys into domain code.

```python
# Wrong — a domain class pulls its dependencies from the Container
class ReportService:
    @classmethod
    def from_container(cls, container: Container) -> Self:
        return cls(exporter=container.exporters[ExportFormat.PDF], ...)


# Correct — the Container gives the dependencies to the constructor
class ReportService:
    def __init__(self, orders: OrderRepository, exporters: Mapping[ExportFormat, Exporter]) -> None:
        ...
```

## Resources and shutdown

The Container must close each resource that it creates. Do these steps:

1. Create an `ExitStack` in the constructor. For async resources, use an `AsyncExitStack`.
2. Create each resource with `self._stack.enter_context(...)`, as `database` shows above.
3. Make the Container a context manager. Its `close` method closes the stack.

```python
class Container:
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Close each resource that the Container created, in reverse order."""
        self._stack.close()
```

The stack closes only the resources that the Container created. A resource that was never used is not created, so it is not closed.

## Tests

- Build a new Container in each test or fixture. Give it test settings.
- To replace a dependency, write a subclass that overrides the `@cached_property`. Do not write to `__dict__`.

```python
class FakeContainer(Container):
    """Container with fake exporters."""

    def __init__(self, settings: Settings, exporters: Mapping[ExportFormat, Exporter]) -> None:
        super().__init__(settings)
        self._fake_exporters = exporters

    @cached_property
    def exporters(self) -> Mapping[ExportFormat, Exporter]:
        return self._fake_exporters
```

- Test a service without the Container when you can. Give the mocks to the constructor directly.

## Size

Split the Container by feature when it is longer than 400 lines. Do these steps:

1. Make one sub-container for each feature, for example `StorageContainer` and `LlmContainer`.
2. Give each sub-container the settings.
3. Create each sub-container in a `@cached_property` of the main Container, with `self._stack.enter_context(...)`. Then `close` also closes the sub-containers.

Callers then use `container.storage.orders` and `container.llm.chat_model`.

## Checklist

Answer these questions before you mark the change as complete:

- [ ] Does the Container create each dependency that needs settings or a resource, and do only entry points build it?
- [ ] Does each default collaborator meet the "Default collaborators" conditions and use an `is None` test?
- [ ] Is the Container free of global instances, and do domain classes never import it?
- [ ] Does each service get its collaborators through the constructor, with no `from_container` method?
- [ ] Does the Container close each resource through its `ExitStack`?
