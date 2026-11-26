# Backend rules

These rules build on the [Python rules](../python/README.md).

| Rule | Apply it when |
|---|---|
| [layers.md](./layers.md) | You add a feature, or you change the layout or the layer direction. |
| [fastapi.md](./fastapi.md) | You write an HTTP application: endpoints, dependencies, payloads, or errors. |
| [errors.md](./errors.md) | You add an error class, or you change the error handlers. |
| [middleware.md](./middleware.md) | You add a middleware, an access log, or background work. |
| [openapi.md](./openapi.md) | You write Swagger descriptions, examples, or response documentation. |
| [sql.md](./sql.md) | You write ORM tables, SQL repositories, sessions, transactions, or migrations. |

These rules are for Python services. A service in another language needs its own area.

These topics are not covered yet: idempotency, secrets and environment configuration, and how to implement pagination. The contract for lists is in [../common/api-contract.md](../common/api-contract.md).

## Checks

Run the checks of the [Python rules](../python/README.md). Also check these items:

- The import-linter contracts of [layers.md](./layers.md) pass.
- Each feature router has a documentation test. See [fastapi.md](./fastapi.md).
