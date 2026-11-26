# Rules

Rules are in areas. A lower area applies to more projects. An area can link to a lower area. A lower area never links to a higher area.

| Area | Scope | Index |
|---|---|---|
| `common/` | Language-independent rules for all projects. | [common/README.md](./common/README.md) |
| `python/` | All Python projects: CLI, library, backend, script. | [python/README.md](./python/README.md) |
| `backend/` | HTTP services. Builds on `python/`. | [backend/README.md](./backend/README.md) |

Any file can link to this README. It is not an area. Read `common/`, then the areas of your task. Read the rule file before you write code.

To add an area, follow [common/writing-rules.md](./common/writing-rules.md).

## Non-negotiable rules

- No tool or assistant attribution in commits. See [common/git-commit.md](./common/git-commit.md).
- OOP method placement. See [python/oop.md](./python/oop.md).
