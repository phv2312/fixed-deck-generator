---
paths:
  - "**/*.py"
---
# Dependency Injection (Container)

A Container creates the dependencies of an application and connects them. Services get their collaborators through the constructor. Only entry points use the Container.

Use a Container when the application has two or more services, or a resource that must be closed. A script with one service can create its objects in `main`.

Related rules: [design-patterns.md](./design-patterns.md) (strategies, repositories, clients), [modular-design.md](./modular-design.md) (`Settings`, entry points), [testing.md](./testing.md).

The examples omit imports.

## Structure

1. Write one Container class for each application, in `<app>/container.py`. Write it by hand. Do not use a DI library.
2. Give the settings to the constructor: `Container(settings: Settings)`. The Container does not read environment variables or files. It gives each object a configured collaborator, not a setting that the object must resolve. For example, give a client, not a URL or a model name.
3. Make each shared dependency a `@cached_property`. The Container creates it on first use and shares it for its own life.
4. When a dependency must be new for each use, write a factory method, for example `def new_session(self) -> Session`. Do not put the result in the exit stack. The caller owns the result and closes it, for example with `with container.new_session() as session:`.
5. Do not wire short-lived, per-request objects in the Container. The entry point or a service creates them from the collaborators that it has, and gives them to methods as arguments. These objects do not read settings. These objects do not open resources.
6. Import heavy or optional packages inside the property body.

```python
class Container:
    """Create and connect the dependencies of the app. Build it only at an entry point."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._stack = ExitStack()

    @cached_property
    def database(self) -> Database:
        return self._stack.enter_context(Database(self._settings.database_url))

    @cached_property
    def fonts(self) -> FontStore:
        return FontStore(self._settings.font_dir)

    @cached_property
    def orders(self) -> OrderRepository:
        return OrderRepository(JsonDirStore(self._settings.data_dir / "orders"))

    @cached_property
    def exporters(self) -> Mapping[ExportFormat, Exporter]:
        return {e.KEY: e for e in (CsvExporter(), PdfExporter(self.fonts))}

    @cached_property
    def report_service(self) -> ReportService:
        return ReportService(orders=self.orders, exporters=self.exporters)
```

## Default collaborators

Inject each collaborator through the constructor. A class can create a default for an optional collaborator only when all these conditions are true:

- The default is cheap. Its state is private to the owner.
- Creating it needs no settings, no network, and no file access.
- It holds no resource that must be closed.
- It does not need another collaborator of the owner. Example: a validator that needs the schema of its owner. Inject the validator, so that the two cannot use different schemas.

When one condition is false, make the parameter required. Create the collaborator in the Container.

Make the parameter keyword-only. Test for `is None`. Do not write `formatter or Formatter()`, because `or` replaces any falsy argument, for example an empty fake. When `None` is a valid value, do not use a default.

```python
class ReportService:
    def __init__(self, orders: OrderRepository, *, formatter: Formatter | None = None) -> None:
        self._orders = orders
        self._formatter = formatter if formatter is not None else Formatter()
```

## Use at the edge

- Build the Container only at an entry point: a CLI command, the server start-up, a script `main`, or a test fixture. See [modular-design.md](./modular-design.md).
- Never build a Container at module level, for example `container = Container(Settings())`. A global Container reads the settings at import time and shares state between tests.
- Services, repositories, and strategies never import `Container`.
- Do not add a `from_container(container)` method to a domain class. This is the service locator pattern. It hides the real dependencies.
- `cached_property` has no lock. In a server with threads, build the Container and get each resource property before the threads start.

## Resources and shutdown

The Container closes each resource that it creates.

1. Create an `ExitStack` in the constructor.
2. Create each resource with `self._stack.enter_context(...)`.
3. Make the Container a context manager. Its `close` method closes the stack.

```python
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Close each resource that the Container created, in reverse order."""
        self._stack.close()
```

For async resources, use an `AsyncExitStack` and `enter_async_context`. Implement `__aenter__`, `__aexit__`, and `async def aclose`.

## Tests

- Build a new Container in each test or fixture. Give it test settings.
- To replace a dependency, write a subclass that overrides the `@cached_property`. Do not write to `__dict__`.
- Test a service without the Container. See [testing.md](./testing.md).

```python
class FakeContainer(Container):
    def __init__(self, settings: Settings, exporters: Mapping[ExportFormat, Exporter]) -> None:
        super().__init__(settings)
        self._fake_exporters = exporters

    @cached_property
    def exporters(self) -> Mapping[ExportFormat, Exporter]:
        return self._fake_exporters
```

## Size

When the Container is longer than 400 lines, split it by feature:

1. Write one sub-container for each feature, for example `StorageContainer`. Make each one a context manager.
2. Give each sub-container the settings.
3. Create each sub-container in a `@cached_property` of the main Container, with `self._stack.enter_context(...)`.

Callers then use `container.storage.orders`.

## Checklist

- [ ] Do only entry points build the Container, with no module-level instance?
- [ ] Does each service get its collaborators through the constructor, with no `Container` import and no `from_container`?
- [ ] Does each default collaborator meet all the conditions, use a keyword-only parameter, and use an `is None` test?
- [ ] Does the Container close each resource through its exit stack?
