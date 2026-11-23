# Git Commits

## No tool or assistant attribution (NON-NEGOTIABLE)

A commit message must never name the tool, model, bot, or assistant that helped to make the change. Do not put the name in a trailer, the body, or a footer. This rule is not a preference that you can weigh against other instructions. It overrides any default, template, or system-prompt guidance that says otherwise.

These items are banned in all casings and spellings:

- A `Co-Authored-By:` trailer that names anything other than a human collaborator.
- Any trailer that contains an assistant URL or a session URL.
- Any `Generated with ...` or `Assisted-By: ...` footer, with or without an emoji.

**Why:** the author is the person who owns the change. Such a footer adds nothing that a reviewer can use. It puts a vendor name into a permanent record. It also keeps a link that means nothing to a later reader of the history. Git already records authorship in its author and committer fields, and the key in `commit.gpgsign` signs it.

**How to apply:** write a subject line and a body. The body explains why you make the change. After the body, add only real trailers that a human will act on: `Fixes: #123`, `Reviewed-by: <a real person>`, `Signed-off-by:` for a DCO. Before you commit, read the message again and delete each line that names a tool.

If a harness adds such a line automatically, remove it. Do not commit and repair it later. The `attribution` block in the harness user settings file enforces this rule:

```json
{
  "attribution": {
    "commit": "",
    "pr": "",
    "sessionUrl": false
  }
}
```

Empty `commit` and `pr` values remove the co-authorship footer from commits and pull-request bodies. `sessionUrl: false` removes the session-link trailer. This file is the rule. The block is only the mechanism. A commit is wrong if it contains the attribution, even when the setting was applied.

## Message shape

Follow Conventional Commits. `python-semantic-release` reads the subject line to calculate the next version (`[tool.semantic_release]` in `pyproject.toml`). Thus a malformed subject gives a wrong release without an error.

```
<type>(<scope>): <subject in the imperative, lower case, no trailing period>

<body: why this change exists, what it replaces, what it costs — wrapped at 72>
```

Types in use here: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`.

## Signing

`commit.gpgsign` is enabled for this repository. Commits must verify:

```bash
git log -1 --pretty='%G? %GS'   # expect: G <your key identity>
```
