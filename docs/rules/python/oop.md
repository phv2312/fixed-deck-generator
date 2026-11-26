# OOP Method Placement (NON-NEGOTIABLE)

When you write a function, find its first parameter whose type is a class of this repository. Call this class the **owned class**. Ignore parameters of third-party types.

Behavior goes with the data that it reads. Behavior that does I/O goes in a service. Use this decision tree to apply the idea.

## Case A: method on the owned class

Use Case A when all these conditions are true:

- The other parameters are primitives, enums, or types from the same module or an inner layer (`models`).
- The body uses only symbols from the same module or from these inner layers.
- The owned class is in the same module.

```python
# Wrong
def process_expense(expense: Expense, owner_id: str) -> None: ...


# Correct
class Expense:
    def process(self, owner_id: str) -> None: ...
```

When only the third condition is false, move the function to the module of the owned class. Then make it a method.

When a method takes only `self`, does no I/O, and derives its value from the instance, make it a `@property`.

### Dangling modules

When all functions of a module take the same owned class as their first parameter, move each function into that class. Delete the module. Do not keep a re-export shim.

## Case B: method on a service class

Use Case B when the function needs a repository, an external client, an event publisher, or more than one owned type. A service class in `services.py` owns the logic. The service gets the collaborators through its constructor.

```python
# Wrong
def sync_expense(expense: Expense, repo: ExpenseRepo, pub: EventPublisher) -> None: ...


# Correct
class ExpenseService:
    def __init__(self, repo: ExpenseRepo, pub: EventPublisher) -> None:
        self._repo = repo
        self._pub = pub

    def sync(self, expense: Expense) -> None: ...
```

A `@staticmethod` that receives repositories or clients as arguments is also a Case B violation. It is a free function inside a class. Move the collaborators to the constructor.

## Exemptions

- Functions without an owned-class parameter, for example pure utilities.
- Framework entry points: callbacks that a framework calls, for example CLI commands, event handlers, and start-up hooks. Keep them thin. Delegate to a service immediately.
- `@classmethod` and `@staticmethod` factory methods.

## Checklist

- [ ] Does the function take an owned class? If yes, is it a method on that class or on a service?
- [ ] If it is a free function, does an exemption apply?
