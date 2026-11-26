# Coding Style

Tools enforce many style rules. See [tooling.md](./tooling.md). This file covers the rules that a tool cannot check, or that need an explanation.

## Python version

Target Python 3.12 or later. Use current syntax. Do not use backports or compatibility shims.

## Type annotations

Annotate all functions, methods, and class attributes.

Use PEP 695 syntax for generics and type aliases:

```python
type Vector = list[float]


def first[T](items: list[T]) -> T: ...


class Stack[T]:
    def push(self, item: T) -> None: ...
```

- Name one type parameter `T`. Name each of several type parameters with the suffix `T`: `KeyT`, `ValueT`. Do not use a bare noun such as `Item`.
- Use `TypeVar` only when a third-party API needs it.
- Use `if TYPE_CHECKING:` blocks for imports that only annotations need. Quote each name from such a block, for example `mocker: "MockerFixture"`. Python 3.12 evaluates annotations at runtime, so an unquoted name raises `NameError`.
- Do not move a type into a `TYPE_CHECKING` block when a framework reads it at runtime, for example a pydantic field.
- Use concrete generic types: `set[str]`, not `set`.

## Guard clauses

Validate the preconditions at the top of the function. Return or raise early. Do not nest the normal path.

```python
# Wrong
def first_of_many(items: list[str]) -> str:
    if items:
        if len(items) > 1:
            return items[0]
    return ""


# Correct
def first_of_many(items: list[str]) -> str:
    if len(items) <= 1:
        return ""
    return items[0]
```

## RORO

A function that takes many values receives one object. A function that returns many values returns one object, not a tuple.

## Data classes

| Use case | Type |
|---|---|
| Data that needs validation and serialization | `pydantic.BaseModel` |
| Intermediate data that needs validation | `pydantic.dataclasses.dataclass` |
| A simple value container | `dataclasses.dataclass` |

## Classes, not free functions

Prefer classes and methods to free functions, except as [oop.md](./oop.md) allows.

## Datetime

Use UTC as the default time zone: `datetime.now(tz=UTC)`.

## Keyword-only parameters

Make each parameter with a default value keyword-only. Ruff checks only the boolean parameters.

```python
def create(repos: Repos, *, sink: EventSink | None = None) -> Context: ...
```

## Naming

- Do not give a module the name of a standard-library module (`types.py`, `io.py`). Use another name, for example `typedefs.py`.
- Name an intermediate `dict` variable `mp_<key>_<value>`, for example `mp_id_user`.

## Immutability

Return new objects. Do not change an argument in place.

These objects are exempt, because their framework expects changes in place: ORM entities in a session, `app.state`, and test fixtures such as `dependency_overrides`.

## Global state

Do not use module-level mutable state. Give dependencies explicitly. These items are allowed at module level:

- Constants.
- A registry that the import fills one time and that nothing changes later, for example a framework router.
- A lazy logger proxy. See [logging.md](./logging.md).

## Async

- Run blocking work that has no async library with `await asyncio.to_thread(...)`. Run CPU-heavy work in an executor.
- Keep a reference to each task from `asyncio.create_task`. Remove it in a done callback. Python can delete a task that has no reference.
- Use `asyncio.TaskGroup` for tasks that must all finish.
- Give each network call a timeout.

## Type narrowing

Use `isinstance()` or `issubclass()` to narrow a type. Do not use `hasattr()` or `getattr(obj, name, default)`. These accept any shape and do not narrow the type.

```python
# Wrong
if hasattr(schema, "is_deleted"):
    ...

# Correct
if issubclass(schema, SoftDeleteMixin):
    ...
```

`issubclass()` raises `TypeError` on a `Protocol` with data members. Use `isinstance()` with a `@runtime_checkable` `Protocol`, or check a concrete class.

When a framework object raises `AttributeError` for a missing attribute (for example a framework state object), catch `AttributeError` and raise a typed error.

## Suppression comments

Fix the cause. Do not hide a finding with a suppression comment.

The only exception is a third-party API that is untyped or typed incorrectly. Use the narrowest code on that line only, for example `# type: ignore[no-untyped-call]`.
