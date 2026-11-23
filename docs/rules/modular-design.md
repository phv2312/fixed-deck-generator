---
paths:
  - "**/*.py"
---
# Modular Design

## File structure

Organize the code by feature or domain, not by type. Each module has this structure:

```
stevard/
  <feature>/
    __init__.py
    models.py       # data classes, pydantic models
    services.py     # business logic
    commands.py     # typer commands (controllers)
    exceptions.py   # module-specific exceptions
```

## File size

Use 200 to 400 lines in a typical file. The hard limit is 800 lines. Extract code when the file nears the limit.

## Exceptions

Each module defines its own exception hierarchy. The base class is at module level:

```python
class FeatureError(Exception): ...


class FeatureNotFoundError(FeatureError): ...


class FeatureValidationError(FeatureError): ...
```

Never raise a bare `Exception` or `RuntimeError` from module code.

Never put an error message in a local variable and raise a generic exception, or a generic field such as `detail`, with that message:

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

Every different error condition gets its own `TemplatedError` subclass (see `mint/exc.py` for the shared base). The subclass has a `TEMPLATE` string and typed fields for the data that the caller already has. Never use one opaque `msg`/`detail` string that the call site builds. Thus the exception type is precise enough for a separate `except`, and the message is complete: each relevant value is a named field, not a value that the caller interpolated.

## Separation of concerns

- `models.py` — only data. No I/O. No side effects.
- `services.py` — business logic and orchestration. It can do I/O.
- `commands.py` — only Typer entry points. Delegate to services immediately.
- `exceptions.py` — only exception classes.
