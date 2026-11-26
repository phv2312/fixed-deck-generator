# Common rules

| Rule | Apply it when |
|---|---|
| [git-commit.md](./git-commit.md) | You commit. |
| [documentation.md](./documentation.md) | You add a command or a feature, or you write a document. |
| [api-contract.md](./api-contract.md) | You write or call an HTTP API. |
| [definition-of-done.md](./definition-of-done.md) | You finish a change. |
| [writing-rules.md](./writing-rules.md) | You add or change a rule file. |

## Checks

- The commit has a Conventional Commits subject and no tool attribution trailer.
- `README.md` and the documents that the change affects are up to date.
- Each new rule file is in the `README.md` of its area.
- A change to an HTTP API follows the error body and the status table of [api-contract.md](./api-contract.md).
