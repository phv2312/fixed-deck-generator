[← Architecture](README.md)

# Visual agent

The interview agent can call `create_diagram` or `create_mockup`. Each tool is a visual agent made with `Agent.as_tool()`. It has no chat history.

1. The visual agent writes SVG. It uses theme token classes such as `fill-accent`.
2. `SvgChecker` checks the SVG.
3. `Rasterizer` builds the measuring page from `decks/visuals/templates/page.html.j2`, through `PageTemplates` in `decks/visuals/pages.py`. It measures the page in headless Chrome and renders a PNG.
4. `VisualService` stores `v<n>.svg`, `v<n>.png` and `v<n>.json` in the `assets/` folder of the project.
5. The interview agent puts the PNG path in `content.image` of a `figure` slide.

At generation, `VisualService.sync` renders again each PNG whose theme differs from the plan theme. This step needs no LLM call.

A chart is never drawn. Data goes to a chart kind (`exhibit`, `twocharts`, `bubble`, `mekko`).

Chrome or Chromium must be installed. Without it, the visual tools are hidden from the agent.
