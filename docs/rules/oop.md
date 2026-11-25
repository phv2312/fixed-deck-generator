---
paths:
  - "**/*.py"
---
# OOP Method Placement (NON-NEGOTIABLE)

When you write a function, examine the first parameter that belongs to a class defined in this repository. Call this an **owned class**. Ignore leading dependency-injection parameters of third-party types that we do not control. These parameters do not trigger this rule.

When you find the first owned-class parameter, use this decision tree.

## Case A → method on that class

All these conditions must be true:

- All other parameters are primitives (`str`, `int`, `float`, `bool`, `None`), enums, or types from the same module or an inner layer (`models`, `entities`).
- The function body refers only to symbols from the same module or from these inner layers.
- The class is in the same module.

```python
# WRONG — dangling function
def process_expense(expense: Expense, owner_id: str) -> None: ...


# CORRECT — Case A
class Expense:
    def process(self, owner_id: str) -> None: ...
```

### Dangling modules

If every function in a module takes the same owned class as its first parameter, the module is the problem. An example is a `_serialize_x`/`build_x` module. Move each function into that class as a method. **Delete the module.** Do not leave a thin re-export shim.

```python
# WRONG — serialize.py exists only to hold functions keyed on Order
def serialize_order(order: Order) -> dict[str, object]: ...
def serialize_line_item(item: LineItem) -> dict[str, object]: ...


# CORRECT — folded into the owning classes, serialize.py deleted
class Order:
    @property
    def as_dict(self) -> dict[str, object]: ...


class LineItem:
    @property
    def as_dict(self) -> dict[str, object]: ...
```

### Zero-argument derivations → `@property`

A Case A method must be a `@property`, not a plain method, when all these conditions are true:

- It takes only `self`.
- It does no I/O.
- It returns a value that comes only from the instance state.

```python
# WRONG
class TreeNode:
    def as_dict(self) -> dict[str, object]: ...


node.as_dict()


# CORRECT
class TreeNode:
    @property
    def as_dict(self) -> dict[str, object]: ...


node.as_dict
```

## Case B → method on a service class

The function needs a repository, an external client, an event publisher, or more than one owned type. In this case, a service class must own the logic. Give the collaborators to the constructor. The service class is in `services.py`.

```python
# WRONG — dangling function pulling outer-layer deps
def sync_expense(
    expense: Expense,
    repo: ExpenseRepo,
    pub: EventPublisher,
) -> None: ...


# CORRECT — Case B
class ExpenseService:
    def __init__(self, repo: ExpenseRepo, pub: EventPublisher) -> None:
        self._repo = repo
        self._pub = pub

    def sync(self, expense: Expense) -> None: ...
```

## What does NOT trigger this rule

- Functions with no owned-class parameters. Examples are pure utilities, factory functions, and validators that receive only primitives.
- CLI command callbacks (for example Typer). These are framework entry points, not domain logic. Delegate to a service method immediately. Keep the callback thin.
- `@classmethod` and `@staticmethod` factory methods. These are Case A variants and are permitted.

## Enforcement checklist

Answer these questions before you mark a function as complete:

- [ ] Is the type of the first parameter defined in this repository?
- [ ] If yes, is the function a method on that class or on a service class?
- [ ] If it is a free function, does it meet one of the exemptions above?
