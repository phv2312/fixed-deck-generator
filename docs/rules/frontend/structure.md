# Frontend Structure

This rule defines which code may import which code. It does not define folder or file names.

## Layers

```
app       entry, router, providers
  ↓
pages     one per route
  ↓
features  one per business feature
  ↓
shared    theme, UI components, API client, generic hooks and utilities
```

A layer imports only from the layers below it.

| Layer | May import | Must not import |
|---|---|---|
| `shared` | Third-party packages | Any other layer |
| `features/<name>` | `shared` | Another feature, `pages`, `app` |
| `pages` | `features`, `shared` | `app` |
| `app` | All layers below | None |

- A page composes features. It has no business logic.
- A feature never imports another feature. Move code that two features need to `shared`.
- Other layers import a feature through its `index` file only.
- `shared` has no knowledge of a feature.

## Inside a feature

```
component  →  query hook  →  api function  →  types
```

- A component renders and handles events. It never calls `fetch` or the API client.
- A query hook wraps TanStack Query and owns the query keys. See [react.md](./react.md).
- An api function makes one call through the shared API client.
- Types hold the request and response shapes. A type never imports upward.

## Imports

- Use a path alias. Do not use `../../` imports.
- Do not create an import cycle.
- Use `import type` for a type-only import.

## Checks

- A lint rule enforces the layer direction. Use `eslint-plugin-boundaries` or `dependency-cruiser`.
- A lint rule forbids import cycles and `../../` imports.
- A lint rule forbids `fetch` and the API client in component files.
