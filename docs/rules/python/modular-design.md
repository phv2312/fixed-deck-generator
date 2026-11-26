# Modular Design

## Project layout

Organize the code by feature, not by type. `<app>` is the top-level package.

```
<app>/
  settings.py        # Settings
  container.py       # Container: creates and connects the process-wide objects
  exceptions.py      # AppError, the base class of all errors
  <feature>/
    models.py        # data classes and pydantic models
    services.py      # business logic
    repositories.py  # stores and repositories
    <strategies>.py  # a strategy base class and its strategies
    commands.py      # CLI commands
    exceptions.py    # feature errors
    templates/       # Jinja2 templates
tests/
  <feature>/         # mirrors <app>/<feature>/
```

Add a file only when the feature needs it. When a file grows too large, make it a package.

## Layer direction

Imports go in one direction:

```
commands  →  services  →  repositories  →  models
```

- A lower layer never imports a higher layer.
- `models.py` and `exceptions.py` never import a framework.
- A feature can import the services and models of another feature. It never imports the commands of another feature.
- [tooling.md](./tooling.md) shows how to enforce this with import-linter.

## Settings

Put all configuration in one `Settings` class in `<app>/settings.py`. Use `pydantic_settings.BaseSettings`.

```python
class Settings(BaseSettings):
    """Configuration of the app. Read from environment variables with the prefix ``APP_``."""

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", frozen=True)

    database_url: SecretStr
    export_format: ExportFormat = ExportFormat.CSV
```

- Create `Settings` only at an entry point. Give it to the Container.
- Type each choice as a `StrEnum` or a `Literal`.
- Type each secret as `SecretStr`.
- When there are many fields, write one mixin for each part (`PostgresSettings`, `RedisSettings`) and combine them: `class Settings(PostgresSettings, RedisSettings)`.
- In tests, give the fields as arguments and pass `_env_file=None`.

## Entry points

An entry point is a CLI command, a server factory, or a script `main`. It does only these steps:

1. Create `Settings`.
2. Create the Container.
3. Call the top-level service.
4. Show the result.

```python
@cli.command()
def export(order_id: str, fmt: ExportFormat) -> None:
    """Export one order."""
    with Container(Settings()) as container:
        sys.stdout.buffer.write(container.report_service.export(order_id, fmt))
```

## File size

Use 200 to 400 lines in a typical file. The hard limit is 800 lines.

## Exceptions

`<app>/exceptions.py` defines one base class. It builds the message from `TEMPLATE` and the dataclass fields.

```python
@dataclass(eq=False)
class AppError(Exception):
    """Base class of all app errors."""

    TEMPLATE: ClassVar[str] = "app error"

    def __str__(self) -> str:
        return self.TEMPLATE.format(**{f.name: getattr(self, f.name) for f in fields(self)})
```

Each feature has one base error and one subclass for each error condition:

```python
@dataclass(eq=False)
class UserError(AppError):
    """Base class of user errors."""


@dataclass(eq=False)
class UserNotFoundError(UserError):
    TEMPLATE = "user not found: {user_id}"
    user_id: UUID
```

- Use `@dataclass(eq=False)`. A plain `@dataclass` makes the exception unhashable. Do not use `frozen=True`.
- An area can add class variables to `AppError`. An error class never imports a framework.
- Write messages in English.
- Put the fields that the caller has into typed fields. Do not build a message string at the call site.
- Put error classes only in `exceptions.py`. Do not define them in a service or repository module.
- Do not raise a bare `Exception` or `RuntimeError`.

```python
# Wrong
raise InvalidArgumentsError(f"unsupported ref type: {type(ref).__name__}")

# Correct
raise UnsupportedRefTypeError(path, type(ref).__name__)
```

## Separation of concerns

| File | Contains |
|---|---|
| `models.py` | Data only. No I/O. |
| `services.py` | Business logic. I/O only through constructor collaborators. |
| `repositories.py` | All storage I/O of the feature. |
| `commands.py` | CLI entry points only. Delegate to a service. |
| `exceptions.py` | Error classes only. |
| `container.py` | Object creation and wiring only. |
