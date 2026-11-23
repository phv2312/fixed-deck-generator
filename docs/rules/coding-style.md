---
paths:
  - "**/*.py"
---
# Coding Style

## Python version

Target Python 3.13 or later. Use current syntax. Do not use backports or compatibility shims.

## Type annotations (MANDATORY)

Add type annotations to all functions, methods, and class attributes.

Use PEP 695 syntax for generics and type aliases:

```python
# type alias
type Vector = list[float]


# generic function
def first[T](items: list[T]) -> T: ...


# generic class
class Stack[T]:
    def push(self, item: T) -> None: ...
```

### Type parameter naming

Name a type parameter `T`. Add a descriptive name only when it helps the reader. Use a descriptive name when several type parameters would collide, or when the name shows the intent, such as `KeyT`/`ValueT`. Never use a bare descriptive noun such as `Item` or `Value` as a type parameter name.

- One type parameter → always `T`.
- More than one type parameter → add the suffix `T` to each name: `KeyT`, `ValueT`, `ResultT`.

```python
# Wrong
class Fetcher[Item](Protocol): ...


# Correct — single param
class Fetcher[T](Protocol): ...


# Correct — multiple params
class Cache[KeyT, ValueT]: ...
```

Use `TypeVar` only when a third-party API needs it.

Never add `from __future__ import annotations`. Resolve forward references with `if TYPE_CHECKING:` blocks, or move the imports.

## Line length

Use a maximum of 100 characters per line.

## Guard clauses — fail fast

Validate the preconditions at the top of the function. Return or raise an error early. Do not nest the normal path.

```python
# Wrong
def process(items: list[str]) -> str:
    if items:
        if len(items) > 1:
            return items[0]
    return ""


# Correct
def process(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) <= 1:
        return ""
    return items[0]
```

## RORO pattern

A function that takes many parameters must receive an object. A function that returns many values must return an object, not a tuple.

## Data classes

There are three tiers. Select the correct tier:

| Use case | Type |
|---|---|
| Complex data needing validation + serialization | `pydantic.BaseModel` |
| Intermediate structs needing validation | `pydantic.dataclasses.dataclass` |
| Simple value containers, no validation | `dataclasses.dataclass` |

## OOP over functional

Prefer classes and methods to standalone functions. A free function whose first parameter is an instance of a local struct is an implicit method. Make it an explicit method.

See [common coding-style rule](~/.claude/rules/common/coding-style.md) for the full OOP method placement decision tree.

## Datetime

Always give `tz` to `datetime.now()`. Use UTC as the default:

```python
from datetime import UTC, datetime

now = datetime.now(tz=UTC)
```

## Boolean arguments

Boolean parameters must be keyword-only:

```python
# Wrong
def run(verbose: bool) -> None: ...


# Correct
def run(*, verbose: bool) -> None: ...
```

## Naming

Name an intermediate dict variable `mp_<keytype>_<valuetype>` (for example, `mp_str_int`).

### Module names

Never give a module the name of a standard-library module (`types.py`, `io.py`, `email.py`, ...). The name hides the standard-library module for all absolute imports in the package and causes awkward relative imports. Select a different name (`typedefs.py`, not `types.py`).

## Immutability

Return new objects. Do not change an object in place.

## No global variables

Limit global state. Pass dependencies explicitly.

## Ruff + ty

All code must pass `uv run ruff check`, `uv run ruff format --check`, and `uv run ty check` before you mark a change as complete.

## Type narrowing over hasattr/getattr

Prefer `isinstance()`/`issubclass()` to narrow a type. Do not use `hasattr()` or `getattr(obj, name, default)`. `hasattr` and `getattr` with a default accept any object shape, including the wrong shape. They give the type checker nothing to narrow. The next line still sees the original type, possibly `Any`. `isinstance`/`issubclass` against a real type (a concrete class or a `Protocol`) narrow the static type of the variable for the rest of the block. Thus the type checker finds a shape mismatch that `hasattr`/`getattr` let through.

```python
# Wrong
if hasattr(schema, "is_deleted"):
    ...
owner = getattr(self, "owner", None)

# Correct
if issubclass(schema, IsDeletedMixin):
    ...
if isinstance(self, IScopedRepository):
    owner = self.owner
```

One caution: `issubclass()` raises `TypeError` on a `Protocol` that has a non-method (data) member. Only a `Protocol` with method members only supports `issubclass()`. For a class-level check against a shape with data, check a concrete class (as with `IsDeletedMixin` above). Do not check a data `Protocol`. `isinstance()` has no such restriction and works on any `@runtime_checkable` `Protocol`, with data members included. Prefer `isinstance()` for instance-level structural checks.

## No suppression comments

Fix the cause. Do not use `# noqa`, `# type: ignore`, or a similar comment to silence the linter or the type checker. The only exception is a real limitation of a third-party dependency. This is a library function or class that is untyped or incorrectly typed, and no change on our side can make the call typed. An example is a third-party constructor whose `__init__` has no return annotation. In this case, use the narrowest possible suppression (for example, `# type: ignore[no-untyped-call]`, never a bare `# type: ignore`). Apply it only on the line that the third-party gap affects.
