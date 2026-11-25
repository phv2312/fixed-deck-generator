# Middlewares and Background Work

The endpoint rules are in [fastapi.md](./fastapi.md).

## Middlewares

- Use middlewares only for transport concerns: CORS, request ID, compression, access logs.
- Do not raise an `AppError`, do business logic, or open a database session in a middleware.
- Each `add_middleware` call wraps the earlier ones. Add the innermost middleware first. Add CORS last, so that it is the outermost.
- Implement the request ID contract of [api-contract.md](../common/api-contract.md). Bind the id for the logs as [logging.md](../python/logging.md) describes.
- Bind `user_id` and `tenant_id` after authentication, in the dependency that authenticates.
- Write one access log event for each request, with the method, the route path template, the status, and the duration. Use the template (`/users/{user_id}`), not the real URL.
- Clear the bound values at the end of the request.

## Background work

Use `BackgroundTasks` only for short work after the response, for example one email. It must not use the request session. Send long work to a queue.
