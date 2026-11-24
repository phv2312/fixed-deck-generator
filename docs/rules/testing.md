---
paths:
  - "tests/**/*.py"
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

Mark async tests with `pytest.mark.asyncio`. Set `asyncio_mode = "auto"` in `pyproject.toml`. The decorator is then optional, but include it for clarity.

## Mocking

Use `pytest-mock` fixtures. Always use an autospec mock.

Services get their collaborators through the constructor (see [dependency-injection.md](./dependency-injection.md)). Create the mock and give it to the constructor:

```python
@pytest.fixture
def orders(mocker: MockerFixture) -> MagicMock:
    """Return an autospec mock of the order repository."""
    return mocker.create_autospec(OrderRepository, instance=True)


def test_close_saves_closed_order(orders: MagicMock) -> None:
    """Test that ``close`` saves the closed order."""
    BillingService(orders).close("o-1")
    orders.save.assert_called_once()
```

Use `mocker.patch("<app>.<module>.<Name>", autospec=True)` only for code that you cannot inject. An example is a third-party call in an entry point.

Do not use a Container in a service test. Use a Container only in a test of an entry point. See the "Tests" section in [dependency-injection.md](./dependency-injection.md).

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
