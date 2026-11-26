HTTP API of the slide deck generator. Every path starts with `/api/v1`.

## Errors

Each error response has the body `{"code": "...", "message": "...", "details": null}`.
Branch on `code`. `message` is English text for developers. A validation error (422) lists
`{loc, msg}` items in `details`. A server error (500) has a generic message.

## Request ID

Send `X-Request-ID` to name a request. The server returns the same header. It creates a value
when you send none or when the value is not valid. Give this value when you report an error.

## Lists

A list response has `items` and `total`. Use `limit` (at most 100) and `offset` to page.
