# Testing

## Framework

Use pytest only. Do not use `unittest.TestCase`. Use `pytest-mock` for mocks.

## Location

Put all tests in `tests/`. Mirror the source layout: `tests/<feature>/test_services.py` tests `<app>/<feature>/services.py`.

## Annotations

Annotate all test functions and fixtures, and give each one a docstring.

## Parametrize

Give the argument names as a tuple and the cases as a list of tuples:

```python
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hello", "HELLO"),
        ("", ""),
    ],
)
def test_upper(text: str, expected: str) -> None:
    """Test upper conversion."""
    assert text.upper() == expected
```

## Async tests

Set `asyncio_mode = "auto"` and `asyncio_default_fixture_loop_scope = "function"` in `pyproject.toml`. Then write async tests as `async def` with no marker.

## Mocks

Use an autospec mock. Give it to the constructor of the object under test:

```python
@pytest.fixture
def orders(mocker: "MockerFixture") -> MockType:
    """Return an autospec mock of the order repository."""
    return mocker.create_autospec(OrderRepository, instance=True)


def test_close_saves_closed_order(orders: MockType) -> None:
    """Test that ``close`` saves the closed order."""
    BillingService(orders).close("o-1")
    orders.save.assert_called_once()
```

- `create_autospec` makes an `AsyncMock` for each `async def` method.
- Use `mocker.patch("<app>.<module>.<Name>", autospec=True)` only for code that you cannot inject.
- Do not use a Container in a service test. See [dependency-injection.md](./dependency-injection.md).

## Factory helpers

When an object needs many collaborators, write one `make_<name>` helper in `conftest.py`. Tests call the helper, not the constructor. When the constructor changes, update only the helper.

```python
def make_service(orders: OrderRepository, *, clock: Clock | None = None) -> BillingService:
    """Create a billing service with test defaults."""
    return BillingService(orders, clock=clock if clock is not None else FixedClock())
```

## TYPE_CHECKING imports

Import fixture types only for type checking, and only the ones that the file uses. Quote them in annotations. Import `MockType` normally, because the test uses it as a return type.

```python
from pytest_mock import MockType

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
```
