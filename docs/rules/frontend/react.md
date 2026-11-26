# React and TypeScript

## TypeScript

- Enable `strict`. Do not use `any`. Use `unknown` and narrow the value.
- Give each component a props type. Give each exported function an explicit return type.
- Do not use a type assertion to hide a type error. Fix the type.

## Components and hooks

- A component is a function. Name it in PascalCase. Name a hook `useXxx`.
- Keep a component small. Move logic to a hook or a function when a limit in [README.md](./README.md) fails.
- Derive a value during render. Do not copy it to state.
- Use an effect only to synchronize with a system outside React.
- Give each list item a stable `key`. Do not use the index when the list can change.
- Do not define a component inside another component.
- Do not add `useMemo` or `useCallback` without a measured need.

## Server state

TanStack Query owns the server state. Do not copy it to local state.

- Call TanStack Query from a query hook only. A component uses the hook.
- Build a query key as an array: the feature name first, then the resource, then the parameters. The key lives next to its query hook.
- A mutation invalidates the keys that it changes.
- Each query shows a loading state, an error state, and an empty state. Use shared components for the three states.

## API client

- The app has one API client in `shared`. It sets the base URL, the `Authorization` header, and the `X-Request-ID` header.
- The client turns an error response into one error type. It keeps `code`, `message`, and `details`. See [../common/api-contract.md](../common/api-contract.md).
- Code branches on `code`. It never branches on `message`.
- Show a user-facing text for an error. Never show `message`.

## Local state

Use component state for state that one component owns. Use context for state that a subtree shares. Do not add a global store without a written reason.

## Configuration and dependencies

- Read configuration from Vite environment variables. Only variables with the `VITE_` prefix reach the browser.
- Put no secret in client code or in an environment variable of the client. Anyone can read them.
- Commit the lockfile. Pin the version of each dependency.

## Checks

- `tsc` with `strict` forbids implicit `any`. A lint rule forbids explicit `any`.
- `eslint-plugin-react-hooks` passes, including `exhaustive-deps`.
- A lint rule forbids `key` from an array index and a component defined inside a component.
- `grep` finds no `process.env` or secret in `src/`.
