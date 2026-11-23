---
paths:
  - "**/*.py"
---
# Documentation

## Docstrings

Add a docstring to all public functions, methods, and classes. A private helper (leading `_`) needs a docstring only when its purpose is not clear.

Use a one-line docstring for a simple case:

```python
def greet(name: str) -> str:
    """Return a greeting string for the given name."""
    ...
```

Use a multi-line docstring for a complex case:

```python
def process(items: list[str], *, reverse: bool = False) -> list[str]:
    """Process items and return transformed results.

    Args:
        items: Input strings to process.
        reverse: If True, reverse each string before processing.

    Returns:
        Transformed list of strings.

    Raises:
        ValueError: If items contains an empty string.
    """
    ...
```

## Module docstrings

Do not add a docstring at the top of a module. Put the intent in the file name, in the class
docstrings, and in `README.md`. This rule applies to source files and to test files.

## README

Update `README.md` when you add a command or a feature.
