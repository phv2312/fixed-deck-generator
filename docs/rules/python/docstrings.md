# Docstrings

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

A module docstring is optional. When you add one, keep it to one line that states the purpose of the module.
