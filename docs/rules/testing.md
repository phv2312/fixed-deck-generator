---
paths:
  - "./tests/**/*.py"
---
# Testing

## Framework

Use pytest only. Never import `unittest`. Use `pytest-mock` for mocking.

## Test location

Put all tests in `./tests/`. Mirror the source layout:

```
tests/
  <feature>/
    __init__.py
    test_models.py
    test_services.py
    test_commands.py
```

## Annotations

Add full type annotations and docstrings to all test functions and fixtures.

## Parametrize

Use `pytest.mark.parametrize` with tuples for the argument list:

```python
@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("hello", "HELLO"),
        ("", ""),
    ],
)
def test_upper(input: str, expected: str) -> None:
    """Test upper conversion."""
    assert upper(input) == expected
```

## Async tests

Mark async tests with `pytest.mark.asyncio`. `asyncio_mode = "auto"` is set in `pyproject.toml`. Thus the decorator is optional, but include it for clarity.

## Mocking

Use `pytest-mock` fixtures. Apply `autospec=True` when possible:

```python
@pytest.fixture
def mock_client(mocker: MockerFixture) -> MagicMock:
    """Autospecced Client mock."""
    return mocker.patch("stevard.services.Client", autospec=True)
```

## TYPE_CHECKING imports in tests

Import only what the test file uses:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture  # only if using capsys/capfd
    from _pytest.fixtures import FixtureRequest  # only if using request fixture
    from _pytest.logging import LogCaptureFixture  # only if using caplog
    from _pytest.monkeypatch import MonkeyPatch  # only if using monkeypatch
    from pytest_mock.plugin import MockerFixture  # only if using mocker
```

## Concrete generics

Use concrete generic types in annotations (for example, `set[str]`, not a bare `set`).
