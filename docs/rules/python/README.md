# Python rules

| Rule | Apply it when |
|---|---|
| [oop.md](./oop.md) | You add a function or a method. Non-negotiable. |
| [coding-style.md](./coding-style.md) | You write any code. |
| [docstrings.md](./docstrings.md) | You add a public function, method, or class. |
| [tooling.md](./tooling.md) | You change the lint, type, or import checks, or you start a project. |
| [modular-design.md](./modular-design.md) | You add a module, a feature, or an error class, or you start a project. |
| [design-patterns.md](./design-patterns.md) | You add variants of one task, or code that reads or writes persistent data. |
| [dependency-injection.md](./dependency-injection.md) | You create services, repositories, strategies, clients, or resources. |
| [templates.md](./templates.md) | You produce multi-line text such as prompts, HTML, or Markdown. |
| [logging.md](./logging.md) | You add a log event, or you configure logging. |
| [testing.md](./testing.md) | You write a test. |

## Stack

This is the default stack of these rules: Python 3.12 or later, uv, ruff, ty, pytest, pydantic, structlog, and Jinja2. They apply to a CLI, a library, a service, or a script.

## Checks

```bash
uv run ruff check
uv run ruff format --check
uv run ty check
uv run lint-imports   # needs import-linter. Required when the project has layer contracts.
uv run pytest
```
