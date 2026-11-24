---
paths:
  - "**/*.py"
---
# Modular Design

## Project layout

Organize the code by feature or domain, not by type. `<app>` is the name of the top-level package.

```
<app>/
  __init__.py
  __main__.py        # calls cli.app()
  cli.py             # Typer app. Entry points only.
  settings.py        # Settings (pydantic-settings)
  container.py       # Container. Creates and connects all dependencies.
  errors.py          # TemplatedError, the base of all exceptions
  <feature>/
    __init__.py
    models.py        # data classes, pydantic models
    services.py      # business logic
    repositories.py  # stores and repositories
    <strategies>.py  # a strategy base class and its strategies, for example exporters.py
    commands.py      # Typer commands (controllers)
    exceptions.py    # feature exceptions
    templates/       # Jinja2 templates of this feature
tests/
  <feature>/         # mirrors <app>/<feature>/
```

Add a file only when the feature needs it. When a feature has many strategies, make `<strategies>/` a package with one module for each strategy.

Related rules:

- [design-patterns.md](./design-patterns.md): Strategy and Repository.
- [dependency-injection.md](./dependency-injection.md): the Container.
- [templates.md](./templates.md): Jinja2 templates.

## Settings

Put all configuration in one `Settings` class in `<app>/settings.py`. Use `pydantic_settings.BaseSettings`.

```python
class Settings(BaseSettings):
    """Configuration of the app. Read from environment variables with the prefix ``APP_``."""

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", frozen=True)

    data_dir: Path = Path("data")
    export_format: ExportFormat = ExportFormat.CSV
    database_url: str
```

- Create `Settings` only at an entry point. Give it to the Container.
- Type each choice as a `StrEnum` or a `Literal`. Then a wrong value fails when the settings load.
- In tests, give each field that the test uses as an argument. Arguments have priority over environment variables. Pass `_env_file=None` so that the test does not read `.env`.

## Entry points

An entry point is a Typer command, a server start-up function, or a script `main`. It does only these steps:

1. Create `Settings`.
2. Create the Container.
3. Get the top-level service from the Container and call it.
4. Show the result.

```python
@app.command()
def export(order_id: str, fmt: ExportFormat) -> None:
    """Export one order."""
    with Container(Settings()) as container:
        sys.stdout.buffer.write(container.report_service.export(order_id, fmt))
```

## File size

Use 200 to 400 lines in a typical file. The hard limit is 800 lines. Extract code when the file nears the limit.

## Exceptions

### Base class

Put this base class in `<app>/errors.py`. All exceptions of the app come from it.

```python
@dataclass
class TemplatedError(Exception):
    """Base of all app errors. The message comes from ``TEMPLATE`` and the fields."""

    TEMPLATE: ClassVar[str] = "unexpected error"

    def __str__(self) -> str:
        return self.TEMPLATE.format_map(vars(self))
```

Do not make an exception dataclass `frozen`. Python sets attributes on an exception when it is raised.

### Feature hierarchy

Each feature defines its own exception hierarchy in `exceptions.py`. The base class of the feature comes from `TemplatedError`:

```python
@dataclass
class FeatureError(TemplatedError): ...


@dataclass
class FeatureNotFoundError(FeatureError):
    TEMPLATE = "feature not found: {feature_id}"
    feature_id: str
```

Never raise a bare `Exception` or `RuntimeError` from module code.

### One class for each error condition

Give each error condition its own subclass. The subclass has a `TEMPLATE` string and typed fields. The fields hold the data that the caller already has.

Do not use one opaque `msg` or `detail` string that the call site builds. Do not put a message in a local variable and raise a generic exception with it.

```python
# Wrong
_msg = f"unsupported ref type: {type(ref).__name__}"
raise InvalidArgumentsError(_msg)


# Correct — dedicated class, typed fields, no pre-formatted string
@dataclass
class UnsupportedRefTypeError(FileStorageError):
    TEMPLATE = "unsupported ref type for {path}: {ref_type}"
    path: str
    ref_type: str


raise UnsupportedRefTypeError(path, type(ref).__name__)
```

Then a caller can catch the exact error type in a separate `except`. The message is complete, because each value is a named field.

## Separation of concerns

- `models.py` — only data. No I/O. No side effects.
- `services.py` — business logic and orchestration. It does I/O only through the repositories and clients that it gets in its constructor.
- `repositories.py` — stores and repositories. All storage I/O of the feature is here.
- `commands.py` — only Typer entry points. Delegate to services immediately.
- `exceptions.py` — only exception classes.
- `<app>/container.py` — only object creation and wiring. No business logic.
