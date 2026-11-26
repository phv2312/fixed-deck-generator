# Backend Layers

This rule extends [modular-design.md](../python/modular-design.md) for an HTTP service.

## Layout

Add these items to the feature layout:

```
<app>/
  main.py            # create_app()
  api/               # shared HTTP code: deps, errors, openapi, middlewares, routers
  db/                # database session, ORM base classes, base repositories
  <feature>/
    tables.py        # ORM tables
    deps.py          # request-scoped dependency providers
    payloads.py      # request and response models
    router.py        # endpoints
    openapi/         # OpenAPI descriptions, examples, and responses
```

| File | Contains |
|---|---|
| `tables.py` | ORM tables only. No queries. |
| `deps.py` | Dependency providers only. |
| `payloads.py` | Request and response models only. |
| `router.py` | Endpoints only. Delegate to a service. |
| `openapi/` | Descriptions, examples, and responses only. |

Version the API in `api/routers.py`, not in folders.

## Layer direction

```
router  →  deps  →  services  →  repositories  →  tables, models
```

- `services.py`, `repositories.py`, `models.py`, `tables.py`, and `exceptions.py` never import the web framework, `payloads.py`, or `<app>/api`.
- A service accepts and returns domain models or tables. It never accepts or returns a payload.
- A feature never imports the router, deps, or payloads of another feature.

## Errors

Add `STATUS_CODE: ClassVar[HTTPStatus]` to `AppError`. The default is 500. Each feature error sets its own status. Use `http.HTTPStatus`, so that no error imports the web framework.

The class name of an error is its public error code. See [../common/api-contract.md](../common/api-contract.md). A rename is a breaking change.

## Checks

Use two import-linter contracts. The first enforces the direction above. The second forbids the web framework in core code.

```ini
[importlinter:contract:layers]
name = Feature layers
type = layers
containers =
    app.users
layers =
    (router)
    (deps)
    (services)
    (repositories)
    (tables) | (models)

[importlinter:contract:no-web-in-core]
name = Core code does not import the web layer
type = forbidden
source_modules =
    app.exceptions
    app.*.services
    app.*.repositories
    app.*.models
    app.*.tables
    app.*.exceptions
forbidden_modules =
    fastapi
    starlette
    app.api
    app.*.payloads
```

Set `include_external_packages = True` under `[importlinter]`.
