# Logging (structlog)

Use structlog. Log events with key-value data, not sentences.

The examples omit imports.

## Events

- Log one event with a fixed name and named values. Do not build a message with an f-string or `%`.
- Name an event in `snake_case`: `user_created`, `payment_failed`, `request_finished`. Name an action as object and past action. Name another event by what happened.
- Put each variable value in a key, not in the name.
- Do not use `print` for output that is not the result of a command.

```python
# Wrong
logger.info(f"created user {user.id} with role {user.role}")

# Correct
logger.info("user_created", user_id=user.id, role=user.role)
```

## Levels

| Level | Use |
|---|---|
| `debug` | Detail for a developer. Off in production. |
| `info` | A normal business event. |
| `warning` | A problem that the program handled. |
| `error` | An operation failed. Someone must look at it. |
| `critical` | The program cannot continue. |

A client error that the program handled (a 4xx response) is `info`, or `warning` when it can show an attack or a broken client. A server error (a 5xx response) is `error`.

## Data in logs

- Never log a secret, a token, a password, or personal data.
- Log an id, not the whole object.
- A `SecretStr` value shows as `**********`. Use it for each secret.

## Configuration

- Configure logging in one function, in one module. Call it once from the entry point. Do not give the module the name of a standard-library module.
- Output JSON in production. Output readable text in development. Select it with a setting.
- Send the records of other libraries through structlog too. Connect the standard `logging` module to structlog, so that all records have the same shape.
- Do not configure logging at import time.

## Loggers

- Use structlog in application code. A library that other projects reuse can use the standard `logging` module, so that it has no structlog dependency.
- Get the logger in each module: `logger = structlog.get_logger()`. This is a lazy proxy and it holds no state. It is the exception to the rule on global state in [coding-style.md](./coding-style.md).
- Do not pass a logger as an argument.

## Context

Bind values that every later event needs, for example a request id, with `structlog.contextvars.bind_contextvars(...)`. Clear them at the end of the unit of work. Then each event carries them, and no function receives them as arguments.

## Errors

- Log an error one time, at the boundary that handles it: an entry point or an error handler.
- Do not log an error and raise it again in each layer.
- Give the exception to the logger: `logger.error("sync_failed", exc_info=True)`.

## Tests

Assert the event name and its values with `structlog.testing.capture_logs`. Do not assert message text.

```python
def test_create_logs_event(service: UserService) -> None:
    """Test that ``create`` logs ``user_created``."""
    with capture_logs() as logs:
        service.create("a")
    assert logs[0]["event"] == "user_created"
```
