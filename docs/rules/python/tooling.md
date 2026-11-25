# Tooling

Let tools enforce each rule that a tool can check. The rule files give the idea. This file gives the tool setting.

The checks to run are in the [README](./README.md).

## Ruff

Start a project with this configuration. Add a rule code to `ignore` only with a comment that gives the reason.

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
  "E", "F", "I", "UP", "B", "RUF", "ANN", "TID",
  "DTZ",    # datetime.now() without tz
  "FBT",    # positional boolean parameters
  "TRY",    # exception anti-patterns
  "PT",     # pytest style, tuple parametrize (PT006, PT007)
  "ASYNC",  # blocking calls in async functions
  "PGH",    # blanket type: ignore (PGH003) and noqa (PGH004)
  "T20",    # print
  "G",      # string formatting in standard logging calls
]

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "parents"

[tool.ruff.lint.flake8-tidy-imports.banned-api]
"unittest.TestCase".msg = "Use pytest test functions."
"__future__.annotations".msg = "Use TYPE_CHECKING blocks and quoted names."

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["FBT001"]  # parametrize passes booleans positionally

[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

## Import-linter

Enforce the layer direction of [modular-design.md](./modular-design.md). Write one contract for each rule.

```ini
[importlinter]
root_package = app
include_external_packages = True

[importlinter:contract:layers]
name = Feature layers
type = layers
containers =
    app.users
    app.orders
layers =
    (commands)
    (services)
    (repositories)
    (models)
```

- Put each layer in parentheses. A feature can then skip a layer.
- Add each new feature to `containers`.
- `a | b` in `layers` means that `a` and `b` cannot import each other.
- Use a `forbidden` contract for a package that a layer must not import. Set `include_external_packages = True` when the package is third-party.
