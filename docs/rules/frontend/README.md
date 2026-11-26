# Frontend rules

These rules are for a browser app. They build on the [common rules](../common/README.md). The reference stack is React, TypeScript, Vite, MUI, Tailwind, and TanStack Query.

| Rule | Apply it when |
|---|---|
| [structure.md](./structure.md) | You add a feature, a page, or an import between modules. |
| [react.md](./react.md) | You write components, hooks, API calls, or configuration. |
| [styling.md](./styling.md) | You style a component, or you change the theme. |
| [design.md](./design.md) | You design a new screen or a new look, or you change the theme values. |
| [ui-quality.md](./ui-quality.md) | You add a screen, a form, or user text. |

Not covered yet: tests, folder and file naming, and multiple languages. Add a rule file when the first real need appears.

## Code limits

A tool enforces each limit.

| Item | Limit |
|---|---|
| Cyclomatic complexity | 10 |
| Nesting depth | 4 |
| Function length | 80 lines |
| File length | 300 lines |
| Function parameters | 4. Use an options object for more. |

## Checks

Run the checks of the [common rules](../common/README.md). Also run these checks. The script names are the default names of a Vite app. Use the real names of the app.

- `npm run typecheck` passes with `strict` enabled.
- `npm run lint` passes. It includes the layer rules of [structure.md](./structure.md) and the limits above.
- `npm run build` passes.
- `grep` finds no hard-coded color or pixel value outside the theme file. See [styling.md](./styling.md).
