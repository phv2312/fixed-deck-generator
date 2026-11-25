---
paths:
  - "**/*.py"
---
# Design Patterns

This rule covers two patterns: Strategy and Repository. Use a pattern only when its "Use it when" conditions are true.

Related rules:

- [dependency-injection.md](./dependency-injection.md): the Container creates the strategies, repositories, and clients, and gives them to services.
- [templates.md](./templates.md): Jinja2 templates for prompts, HTML, and other text.
- [modular-design.md](./modular-design.md): the project layout, the `Settings` class, and the exception base class.

The examples omit imports. The names come from `abc`, `collections.abc`, `enum`, `typing`, and `pydantic`.

## Strategy

### Use it when

- You have two or more ways to do the same task. Examples are export formats, payment providers, output backends, and item kinds that each need different code.
- You expect to add more variants later.

### Do not use it when

- There is only one variant. Write a plain class. Add the abstraction when the second variant arrives.
- The variants differ only in data. Use a data class or a configuration value.

### Structure

1. Define the keys as a `StrEnum` when the set of keys is closed. A `ClassVar[str]` key is allowed when plugins or a framework define the keys.
2. Define one abstract base class. Use `ABC` and `@abstractmethod`. Use PEP 695 generics when the input or output type changes between strategies.
3. Declare the metadata of each strategy as `ClassVar` attributes, for example `KEY` and `DESCRIPTION`. Do not use a separate dictionary of metadata.
4. Put each concrete strategy in its own class. Keep a strategy stateless between calls. Give collaborators to the constructor.
5. Create the strategy instances in the Container (see [dependency-injection.md](./dependency-injection.md)).
6. The service gets its strategy, or the mapping of strategies, through its constructor. The service never imports a concrete strategy class.

```python
# Correct
class ExportFormat(StrEnum):
    CSV = "csv"
    PDF = "pdf"


class Exporter(ABC):
    """Write a report in one format."""

    KEY: ClassVar[ExportFormat]

    @abstractmethod
    def export(self, report: Report) -> bytes:
        """Return ``report`` in the format of this exporter."""


class CsvExporter(Exporter):
    KEY = ExportFormat.CSV

    def export(self, report: Report) -> bytes: ...


class PdfExporter(Exporter):
    KEY = ExportFormat.PDF

    def __init__(self, fonts: FontStore) -> None:
        self._fonts = fonts

    def export(self, report: Report) -> bytes: ...
```

```python
# Wrong — the caller branches on a string. Each new format changes this function.
def export(report: Report, fmt: str) -> bytes:
    if fmt == "csv":
        ...
    elif fmt == "pdf":
        ...


# Wrong — a dictionary of free functions. It has no shared contract and no metadata.
EXPORTERS = {"csv": export_csv, "pdf": export_pdf}
```

### Select a strategy

There are two cases.

**The settings select the strategy.** The Container reads the key from the settings and gives one strategy to the service. The service does not know the key.

**Each request selects the strategy.** An example is a user who selects the export format for each export. The Container gives a `Mapping[ExportFormat, Exporter]` to the service. The entry point converts the user input to `ExportFormat` and gives it to the service. An unknown value then fails at the edge, as a validation error, and not as a `KeyError` in the service.

```python
class ReportService:
    def __init__(self, orders: OrderRepository, exporters: Mapping[ExportFormat, Exporter]) -> None:
        self._orders = orders
        self._exporters = exporters

    def export(self, order_id: str, fmt: ExportFormat) -> bytes:
        return self._exporters[fmt].export(self._orders.get(order_id).report)
```

Rules for the mapping:

- Create the instances explicitly in the Container: `{e.KEY: e for e in (CsvExporter(), PdfExporter(self.fonts))}`. Then a strategy can have constructor arguments.
- Do not find strategies with import side effects, decorators that change global state, or `__subclasses__()`.
- Add a test that each `ExportFormat` member has a strategy in the mapping.

### Dispatch on a closed set of types

Sometimes the variants are a closed set of input types, for example the node types of a tree. Each output backend handles every type. In this case, do these steps:

1. Define the set as a union type alias.
2. Put one abstract method for each type on the base class.
3. Dispatch with one `match` statement. End it with `case _: assert_never(node)`.

```python
type Node = TextNode | ImageNode


class NodeRenderer[T](ABC):
    @abstractmethod
    def text(self, node: TextNode) -> T: ...

    @abstractmethod
    def image(self, node: ImageNode) -> T: ...

    def node(self, node: Node) -> T:
        match node:
            case TextNode():
                return self.text(node)
            case ImageNode():
                return self.image(node)
            case _:
                assert_never(node)
```

The type checker then finds two errors. It finds a backend that does not implement a method. It finds a new member of `Node` that has no `case`.

## Repository

### Use it when

- Code reads or writes persistent data: files, a database, a cache, or a remote API that stores records.

### Structure

Use two layers.

1. **Store.** It does the raw I/O for one location, such as one directory, one table, or one bucket. It knows paths, SQL, or HTTP. It does not know the domain rules.
2. **Repository.** It gives a domain API, such as `get`, `find`, `save`, or `delete`. It takes the store in its constructor. It accepts and returns domain models only.

```python
class JsonDirStore:
    """Keep one JSON file for each key in one directory. Each write is atomic."""

    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def read[T: BaseModel](self, key: str, model: type[T]) -> T | None: ...

    def write(self, key: str, value: BaseModel) -> None: ...


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

### Rules

- A repository returns domain models, for example pydantic models or data classes. It never returns a `dict`, a row, a path, or a raw response.
- Use `get` for an item that must exist. It raises a typed "not found" error. Use `find` for an item that can be absent. It returns `None`.
- Convert storage errors into module errors. For example, a JSON file that fails validation raises `CorruptRecordError(path)`. Do not let `ValidationError` or a driver error leave the repository.
- Make a write atomic when a partial write can corrupt the data. Write to a temporary file and then replace the target, or use a transaction.
- Services depend on repositories. A service never opens a file, builds SQL, or calls a store directly.
- Create repositories in the Container (see [dependency-injection.md](./dependency-injection.md)). Give them to services through the constructor.
- Use a generic repository, such as `ModelRepository[T: BaseModel]`, when many models need only `load`, `save`, and `delete`. Write a specific repository when a model needs queries or domain errors.
- When you need two backends, for example a file and a database, define a `Protocol` for the repository. Services depend on the `Protocol`.

```python
# Wrong — the service knows the storage format.
class BillingService:
    def close(self, order_id: str) -> None:
        data = json.loads(Path(f"orders/{order_id}.json").read_text())
        data["status"] = "closed"
        ...


# Correct
class BillingService:
    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders

    def close(self, order_id: str) -> None:
        order = self._orders.get(order_id)
        self._orders.save(order.closed())
```

### External clients

An external client that does not store records is not a repository. Examples are an LLM API, a payment API, and an email sender. Treat it as a collaborator:

- Create it in the Container. Give it to the service through the constructor.
- Wrap the third-party SDK in a small class of your own. The service calls your class, not the SDK.
- Define a `Protocol` for it when you need a second backend or a fake in tests.

### Tests

- Test a repository against a real store in `tmp_path`.
- Test a service with a repository mock. Use `mocker.create_autospec(OrderRepository, instance=True)`.

## Checklist

Answer these questions before you mark the change as complete:

- [ ] Do two or more variants of one task exist? If yes, is there a strategy base class with `StrEnum` keys, and no `if`/`elif` on a type string?
- [ ] Are the strategy instances created in the Container, and never found by import side effects?
- [ ] Does each service get its data through a repository, and never from a file, SQL, or a store directly?
- [ ] Does each repository return domain models and raise module errors?
