# AGENTS.md

Read this file before you change the repository. These rules apply to humans and to AI agents.

## Mandatory rules

Read the rule file for your task before you write code. Do not rely on memory or on the summaries below. The rule files are the source of truth.

Every feature, fix, refactor, or test must obey these rules.

| Area | Rule file | Apply it when |
|---|---|---|
| OOP method placement (non-negotiable) | [docs/rules/oop.md](./docs/rules/oop.md) | You add a function or a method. Do not write a free function when the first parameter belongs to a class in this repository. Make it a method, or a method on a service class. |
| Coding style | [docs/rules/coding-style.md](./docs/rules/coding-style.md) | You write any code. The rule covers type annotations, PEP 695 generics, the 100-character line limit, guard clauses, RORO, the data-class tiers, `datetime.now(tz=...)`, keyword-only booleans, immutability, global state, and suppression comments. |
| Modular design | [docs/rules/modular-design.md](./docs/rules/modular-design.md) | You organize new code or start a new project. Use the project layout (`settings.py`, `container.py`, `errors.py`, `cli.py`) and feature modules (`models.py`, `services.py`, `repositories.py`, `commands.py`, `exceptions.py`). Keep a file between 200 and 400 lines. The hard limit is 800 lines. Give each module an exception hierarchy with a `TEMPLATE` and typed fields. |
| Design patterns | [docs/rules/design-patterns.md](./docs/rules/design-patterns.md) | You add variants of one task, or code that reads or writes persistent data. Use a strategy base class with `StrEnum` keys, and a repository over a store. |
| Dependency injection | [docs/rules/dependency-injection.md](./docs/rules/dependency-injection.md) | You create services, repositories, strategies, clients, or resources. Use one hand-written Container that only entry points build. Inject collaborators through the constructor. |
| Templates | [docs/rules/templates.md](./docs/rules/templates.md) | You produce multi-line text such as prompts, HTML, or Markdown. Use Jinja2 templates through one wrapper class with `StrictUndefined`. |
| Testing | [docs/rules/testing.md](./docs/rules/testing.md) | You write a test. Use pytest only. Mirror the source layout in `tests/`. Add full annotations and docstrings. Use tuple parametrize. Use `pytest-mock` with `autospec=True`. |
| Documentation | [docs/rules/documentation.md](./docs/rules/documentation.md) | You add a public function, method, or class. Add a docstring. Update `README.md` when you add a command or a feature. |
| Git commits | [docs/rules/git-commit.md](./docs/rules/git-commit.md) | You commit. Use a Conventional Commits subject. Do not add tool or assistant attribution, or `Co-Authored-By` trailers. Sign the commit with GPG. |

## Project documents

Read these documents to learn how the system works. Do this before you change more than one module.

| Document | Read it when |
|---|---|
| [docs/architecture/](./docs/architecture/README.md) | You need to know how the system is built: the deck engine, the agent layer, deck generation, and the visual agent. |
| [docs/builder-authoring.md](./docs/builder-authoring.md) | You add or change a slide kind. |
| [docs/slide-catalog/](./docs/slide-catalog/README.md) | You need the list of slide kinds, their parameters, and their previews. Do not edit it. Run `uv run python -m scripts.gen_catalog` to update it. |
| [docs/rules/slide-variety.md](./docs/rules/slide-variety.md) | You change how the interview agent chooses slide kinds. |

Update the matching document when you change one of these areas.

## Documentation language

Write `AGENTS.md` and each file in `docs/` in ASD-STE100 Simplified Technical English. Use short sentences, the active voice, and one instruction per sentence. Keep code, paths, and technical names as they are.

## Commands

Run these commands before you mark a change as complete:

```bash
uv run ruff check
uv run ruff format --check
uv run ty check
uv run pytest
```
