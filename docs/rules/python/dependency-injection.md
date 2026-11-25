# Dependency Injection (Container)

A Container creates the process-wide objects of an application and connects them. Services get their collaborators through the constructor. Only entry points use the Container.

Use a Container when the application has two or more services, or a resource that must be closed. A script with one service can create its objects in `main`.

The examples omit imports.

## Structure

1. Write one Container class for each application, in `<app>/container.py`. Write it by hand. Do not use a DI library.
2. Give the settings to the constructor. The Container does not read environment variables or files.
3. Give each object a configured collaborator, not a setting. For example, give a client, not a URL.
4. Make each shared object a `@cached_property`.
5. When an object must be new for each use, write a factory method, for example `new_session()`. The caller owns and closes the result.
6. Do not wire short-lived objects (for each request or each run) in the Container. The entry point creates them from Container objects.
7. Import heavy or optional packages inside the property body.

```python
class Container:
    """Create and connect the process-wide objects. Build it only at an entry point."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._stack = ExitStack()

    @cached_property
    def http(self) -> httpx.Client:
        return self._stack.enter_context(httpx.Client(timeout=self._settings.timeout))

    @cached_property
    def exporters(self) -> Mapping[ExportFormat, Exporter]:
        return {e.KEY: e for e in (CsvExporter(), PdfExporter(self.fonts))}

    @cached_property
    def report_service(self) -> ReportService:
        return ReportService(orders=self.orders, exporters=self.exporters)
```

## Resources and shutdown

The Container closes each resource that it creates, in reverse order.

1. Create an `ExitStack` in the constructor.
2. Register each resource on the stack.
3. Make the Container a context manager. Its `close` method closes the stack.

```python
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Close each resource that the Container created."""
        self._stack.close()
```

### Async resources

A `@cached_property` cannot `await`. Use an `AsyncExitStack`:

- When creating the resource needs no `await` but closing it does, create it in the property. Register the close call with `push_async_callback`.
- When the resource needs `await` to open, open it in `__aenter__`.

```python
class Container:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._stack = AsyncExitStack()

    @cached_property
    def database(self) -> Database:
        database = Database(self._settings.database_url.get_secret_value())
        self._stack.push_async_callback(database.dispose)
        return database

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._stack.aclose()
```

## Default collaborators

Inject each collaborator through the constructor. A class can create a default for an optional collaborator only when all these conditions are true:

- The default is cheap, and its state is private to the owner.
- It needs no settings, no network, and no file access.
- It holds no resource that must be closed.
- It does not need another collaborator of the owner.

Make the parameter keyword-only. Test for `is None`. Do not write `formatter or Formatter()`.

```python
class ReportService:
    def __init__(self, orders: OrderRepository, *, formatter: Formatter | None = None) -> None:
        self._orders = orders
        self._formatter = formatter if formatter is not None else Formatter()
```

## Use at the edge

- Build the Container only at an entry point or in a test fixture.
- Never build a Container at module level.
- Services, repositories, and strategies never import `Container`.
- Do not add a `from_container(container)` method. This is the service locator pattern.
- `cached_property` has no lock. In a threaded server, get each property before the threads start.
- A framework can own the Container in its start-up hook. A request-scoped object then comes from the framework, not from the Container.

## Tests

- Build a new Container in each test or fixture. Give it test settings.
- To replace an object, write a subclass that overrides the `@cached_property`. Do not write to `__dict__`.
- Test a service without the Container. See [testing.md](./testing.md).

## Size

When the Container file is too long, split it into one sub-container for each feature. See the file-size rule in [modular-design.md](./modular-design.md). The main Container creates each sub-container in a `@cached_property`. It registers each one on its stack.

## Checklist

- [ ] Do only entry points and fixtures build the Container?
- [ ] Does each service get its collaborators through the constructor?
- [ ] Does the Container close each resource through its exit stack?
