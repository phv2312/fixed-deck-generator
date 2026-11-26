# Design Patterns

This rule covers two patterns: Strategy and Repository. Use a pattern only when its "Use it when" conditions are true.

The examples omit imports.

## Strategy

### Use it when

- You have two or more ways to do the same task, for example export formats or payment providers.
- You expect more variants later.

Do not use it when there is only one variant, or when the variants differ only in data.

### Structure

1. Define the keys as a `StrEnum`. A `ClassVar[str]` key is allowed when plugins define the keys.
2. Define one abstract base class with `ABC` and `@abstractmethod`.
3. Declare the metadata of each strategy as `ClassVar` attributes, for example `KEY`.
4. Put each strategy in its own class. Keep it stateless between calls. Give collaborators to its constructor.
5. Create the strategy instances in the Container.
6. The service gets its strategy, or a mapping of strategies, through its constructor. It never imports a concrete strategy.

```python
class ExportFormat(StrEnum):
    CSV = "csv"
    PDF = "pdf"


class Exporter(ABC):
    """Write a report in one format."""

    KEY: ClassVar[ExportFormat]

    @abstractmethod
    def export(self, report: Report) -> bytes:
        """Return ``report`` in the format of this exporter."""


class PdfExporter(Exporter):
    KEY = ExportFormat.PDF

    def __init__(self, fonts: FontStore) -> None:
        self._fonts = fonts

    def export(self, report: Report) -> bytes: ...
```

Do not branch on a type string with `if`/`elif`. Do not keep a dictionary of free functions.

### Select a strategy

- **The settings select it.** The Container reads the key and gives one strategy to the service.
- **Each request selects it.** The Container gives a `Mapping[ExportFormat, Exporter]` to the service. The entry point converts the user input to `ExportFormat`, so that an unknown value fails at the edge.

Create the mapping explicitly in the Container: `{e.KEY: e for e in (CsvExporter(), PdfExporter(self.fonts))}`. Do not find strategies with import side effects or `__subclasses__()`. Add a test that each enum member has a strategy.

### Dispatch on a closed set of types

When the variants are a closed set of input types, define a union alias, one abstract method for each type, and one `match` statement that ends with `case _: assert_never(node)`. The type checker then finds a missing method and a missing `case`.

## Repository

### Use it when

Code reads or writes persistent data: files, a database, a cache, or a remote API that stores records.

### Structure

Use two layers.

1. **Store.** It does the raw I/O for one location: one directory, one table, or one bucket. It knows paths, SQL, or HTTP. It does not know the domain rules. For file storage, define one interface with one backend for each target, for example local disk and S3.
2. **Repository.** It gives a domain API: `get`, `find`, `save`, `delete`. It takes the store in its constructor.

```python
class OrderRepository:
    """Persist orders."""

    def __init__(self, store: JsonDirStore) -> None:
        self._store = store

    def get(self, order_id: str) -> Order:
        """Return the order. Raise ``OrderNotFoundError`` when it does not exist."""
        order = self.find(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order

    def find(self, order_id: str) -> Order | None:
        """Return the order, or ``None`` when it does not exist."""
        return self._store.read(order_id, Order)

    def save(self, order: Order) -> None:
        """Write ``order``."""
        self._store.write(order.id, order)
```

For a relational database, the database session is the store. A repository can then return ORM objects.

### Rules

- A repository returns domain models. It never returns a `dict`, a path, or a raw response.
- `get` returns an item that must exist and raises a typed "not found" error. `find` returns `None` when the item is absent.
- Return a `Page[T]` with `items` and `total` for a paged list. Do not return a tuple.
- Convert storage and driver errors into feature errors.
- Make a write atomic when a partial write can corrupt data.
- A service never opens a file, builds SQL, or calls a store directly.
- Use a generic repository when many models need only `get`, `save`, and `delete`.
- When you need two backends, define a `Protocol`. Services depend on the `Protocol`.

### External clients

A client that does not store records is not a repository, for example an LLM API or an email sender.

- Create it in the Container. Give it to the service through the constructor.
- Wrap the third-party SDK in a small class of your own.
- Define a `Protocol` when you need a second backend or a fake.

Test a file repository against a real store in `tmp_path`.

## Checklist

- [ ] Do two or more variants exist? If yes, is there a strategy base class with `StrEnum` keys?
- [ ] Are strategies created in the Container, and never found by import side effects?
- [ ] Does each service get its data only through repositories?
- [ ] Does each repository raise feature errors, and use `get` and `find` correctly?
