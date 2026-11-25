# AGENTS.md

Read this file before you change the repository. These rules apply to humans and to AI agents.

## Mandatory rules

Read the rule file for your task before you write code. The rule files are the source of truth. Every change must obey them. Run the `Checks` of each area that you changed.

| Area | Index | Apply it when |
|---|---|---|
| Common | [docs/rules/common/](./docs/rules/common/README.md) | Always: commits, documentation, API contract, definition of done, writing rules. |
| Python | [docs/rules/python/](./docs/rules/python/README.md) | You write Python. The OOP method placement rule is non-negotiable. |
| Backend | [docs/rules/backend/](./docs/rules/backend/README.md) | You write an HTTP service, SQL repositories, or migrations. |

The areas and the non-negotiable rules are in [docs/rules/README.md](./docs/rules/README.md).

## Project documents

Read these documents to learn how the system works. Do this before you change more than one module.

| Document | Read it when |
|---|---|
| [docs/architecture/](./docs/architecture/README.md) | You need to know how the system is built: the deck engine, the agent layer, deck generation, and the visual agent. |
| [docs/builder-authoring.md](./docs/builder-authoring.md) | You add or change a slide kind. |
| [docs/slide-catalog/](./docs/slide-catalog/README.md) | You need the list of slide kinds, their parameters, and their previews. Do not edit it. Run `uv run python -m scripts.gen_catalog` to update it. |

Update the matching document when you change one of these areas.

## Commands

Follow [docs/rules/common/definition-of-done.md](./docs/rules/common/definition-of-done.md) before you mark a change as complete.
