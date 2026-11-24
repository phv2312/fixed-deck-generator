---
paths:
  - "**/*.py"
  - "**/*.j2"
---
# Templates (Jinja2)

Use Jinja2 for prompts, HTML, Markdown, and other text that has a fixed shape.

The examples omit imports. The names come from `pathlib` and `jinja2`.

## Use it when

- You produce text that is longer than one line and has a fixed shape. Examples are LLM prompts, HTML, Markdown, emails, and configuration files.

Use Jinja2 for this text. Do not build it with f-strings, `str.format`, or string concatenation. These items are exempt:

- A one-line message.
- A log message.
- The `TEMPLATE` string of an exception class.

## File layout

- Put the templates in a `templates/` directory next to the module that renders them. Keep this directory inside the package, so that the build includes it.
- Name a template `<name>.<output-extension>.j2`, for example `summary.md.j2`, `page.html.j2`, or `system.txt.j2`.
- Put shared macros in `macros.j2`. Import them with `{% from "macros.j2" import ... %}`.
- End each template file with a newline. Jinja2 removes one final newline, so the rendered text has no final newline.

## One wrapper class for each template set

Do not create an `Environment` in each function. Make one class that owns the environment. The class converts each Jinja2 error into a module error.

```python
class TextTemplates:
    """Render the Jinja2 templates of one directory.

    Templates that end in ``.html.j2`` or ``.xml.j2`` escape every value. Other templates do not.
    """

    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._env = Environment(
            loader=FileSystemLoader(directory),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(("html.j2", "xml.j2"), default_for_string=False),
        )

    def render(self, template: str, /, **context: object) -> str:
        """Render ``template`` with ``context``."""
        try:
            return self._env.get_template(template).render(**context)
        except TemplateNotFound as error:
            raise TemplateMissingError(template, str(self._directory)) from error
        except UndefinedError as error:
            raise TemplateVariableMissingError(template, str(error)) from error
        except TemplateError as error:
            raise TemplateRenderError(template, str(error)) from error
```

Create the wrapper in the Container (see [dependency-injection.md](./dependency-injection.md)). Give it to the services that render text.

## Environment settings

- Always use `undefined=StrictUndefined`. A missing variable must raise an error. It must not render as an empty string.
- Always use `trim_blocks=True` and `lstrip_blocks=True`. Then block tags do not add blank lines.
- Select escaping by file name with `select_autoescape`, as in the example. Then HTML and XML templates escape every value, and text templates do not. Use `Markup` for a value that is already safe HTML.
- Register custom filters and globals in the wrapper class only. Make each filter a small, pure function or a `@staticmethod`.

## Logic in templates

- Python computes the values. The template only arranges them.
- A template can use `if`, `for`, macros, and simple filters.
- A template must not compute business values, call services, do I/O, or contain long expressions. Compute the value in Python and give it to the template as a variable.
- Give the template typed objects, such as models or data classes. Do not give it a large untyped `dict`.

```jinja
{# Wrong — business logic in the template #}
Total: {{ (items | sum(attribute="price")) * (1 - discount / 100) | round(2) }}

{# Correct — Python computes ``order.total`` #}
Total: {{ order.total }}
```

## Prompts

- Keep each prompt in its own template file. Do not keep prompt text in Python constants.
- Use one template for the system prompt and separate templates for repeated parts. Join them with `{% include %}` or macros.
- Give the prompt the data that it needs as variables. Use the `tojson` filter when you need JSON. Do not join JSON text into the prompt in Python.

## Tests

- Render each template one time in a test with real context values. This catches a missing variable.
- For a prompt, compare the output with a short expected text, or assert that key lines are present. Do not snapshot a long prompt unless it must not change.

## Checklist

Answer these questions before you mark the change as complete:

- [ ] Is each multi-line text output a Jinja2 template with `StrictUndefined`?
- [ ] Does one wrapper class own the `Environment` and convert each Jinja2 error into a module error?
- [ ] Is template logic limited to layout, with the values computed in Python?
