# Frontend

Browser app for the slide deck workspace. Stack: React, TypeScript (strict), Vite, MUI, Tailwind (layout only), TanStack Query, React Router.

The rules are in [../docs/rules/frontend/](../docs/rules/frontend/README.md).

## Commands

| Command | Use |
|---|---|
| `npm install` | Install the dependencies. |
| `npm run dev` | Start the dev server. It sends `/api` to `http://localhost:8000`. |
| `npm run typecheck` | Check the types. |
| `npm run lint` | Run ESLint. It includes the layer rules and the code limits. |
| `npm run build` | Check the types and build for production. |

Set `VITE_API_BASE_URL` (see `.env.example`) when the API runs on another origin. Leave it empty in development.

## Layout

```
src/
  app/        entry, router, providers
  pages/      one component per route
  features/   one folder per feature (projects); import through its index.ts
  shared/     theme, API client, shared UI, hooks, texts
```

- `src/shared/theme/theme.ts` is the only place for colors, fonts, spacing, radius, and shadow.
- Each layer has its own `texts.ts` for user-facing strings.
