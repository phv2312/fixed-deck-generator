# API Contract

These rules define what a client of an HTTP API can rely on. A server and a client both follow them.

## Error body

Each error response has this JSON body:

```json
{"code": "UserNotFoundError", "message": "user not found: 4f1c", "details": null}
```

- `code` is a stable name. A client branches on `code`, never on `message`.
- `message` is English text for a developer. A client does not show it to a user.
- `details` is `null`, or a list of `{loc, msg}` items for a validation error.
- A server returns a generic `message` for a status of 500 or more.

## Status codes

| Status | Use |
|---|---|
| 400 | The request is malformed. |
| 401 | The client is not authenticated. |
| 403 | The client lacks permission. |
| 404 | The resource does not exist. |
| 409 | The resource exists or is in a conflicting state. |
| 422 | The request body or parameters fail validation. |
| 500 | The server has a defect. |

## Authentication

A client sends `Authorization: Bearer <token>`. The server never reads a token from a query parameter.

## Request ID

A client can send `X-Request-ID`. The server returns the same header on each response. When the client sent none, the server creates a new value. A client gives this value when it reports an error. The server puts the value in each log event of the request.

## Lists

A list response has `items` and `total`. The request has a page size with a maximum, and a stable sort.

## Versions

- Put the version in the path prefix: `/api/v1`.
- A breaking change needs a new version. A breaking change removes or renames a field, changes a type, or changes the meaning of a value.
- Adding an optional field or a new endpoint is not a breaking change.
- Renaming an error `code` is a breaking change.
