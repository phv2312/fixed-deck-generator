# Errors

An error is an `AppError` subclass. See [layers.md](./layers.md). The endpoint rules are in [fastapi.md](./fastapi.md).

`ErrorHandlers().install(app)` in `<app>/api/errors.py` registers these handlers. Each returns the error body of [api-contract.md](../common/api-contract.md).

| Exception | Status | `code` |
|---|---|---|
| `AppError` | `STATUS_CODE` | class name |
| `RequestValidationError` | 422 | `ValidationError`, with `loc` and `msg` of each error in `details` |
| Starlette `HTTPException` (404, 405) | its status | for example `NotFound` |
| any other `Exception` | 500 | `InternalServerError` |

- For a status of 500 or more, log the traceback and return a generic message. The fields of an error can contain internal data.
- Do not map a pydantic `ValidationError` from inside the app to 422. It is a server defect.

