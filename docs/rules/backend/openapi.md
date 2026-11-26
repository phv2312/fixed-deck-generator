# OpenAPI Documentation

Every route has complete Swagger documentation. Keep it in data, not in decorators. The endpoint layout is in [fastapi.md](./fastapi.md). The examples omit imports.

## Application level

- Keep the API description in `<app>/api/docs/description.md` (status codes, authentication steps). Read it one time at import.
- Set `DEFAULT_RESPONSES` for 422 and 500 on the app. Set the 401 and 403 responses only on protected routers (`AUTH_RESPONSES`).
- Set the tags in `routers.py`. Use `include_in_schema=False` for internal routes.
- Generate stable operation IDs from the tag and the function name.

## Feature level

```
<feature>/openapi/
  descriptions.py   # UserDocs: one RouteDoc(summary, description) for each endpoint
  examples.py       # UserExamples: response examples loaded from JSON
  responses.py      # UserResponses: one Responses mapping for each endpoint
  examples/*.json
```

1. **Descriptions.** A one-line `summary` and a Markdown `description`. Follow the length limit for static text in [templates.md](../python/templates.md).
2. **Examples.** Keep each example in a JSON file. Load it through its response model: `UserResponse.model_validate_json(path.read_text())`. An example that does not match the model then fails at import.
3. **Responses.** Map each status code to an example or to the errors of that status. List every error that the endpoint can raise.

```python
class UserResponses:
    """OpenAPI responses of the user endpoints."""

    READ: ClassVar[Responses] = {
        HTTPStatus.OK: ExampleResponse(UserExamples.READ).to_openapi(),
        HTTPStatus.FORBIDDEN: ErrorResponse(PermissionDeniedError).to_openapi(),
        HTTPStatus.NOT_FOUND: ErrorResponse(UserNotFoundError).to_openapi(),
    }
```

`<app>/api/openapi.py` has the helpers. Each has a `to_openapi()` method:

| Helper | Output |
|---|---|
| `ExampleResponse(model)` | One JSON example. |
| `MultipleExamples({name: model})` | Named examples for one status. |
| `ErrorResponse(*errors)` | The error body. Each error class gives one example from its `TEMPLATE`. |
| `EmptyResponse()` | A 204 response. |
| `StreamExample(text)` | A `text/event-stream` example. |

The endpoint docstring is for developers. Each route must also set `description`, because FastAPI uses the docstring only as a fallback.
