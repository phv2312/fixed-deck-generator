# Architecture

This folder shows how the system is built. Read it before you change more than one module. Use [../builder-authoring.md](../builder-authoring.md) to add a slide type. Use [../slide-catalog/](../slide-catalog/README.md) for the list of slide types.

| Page | Content |
|---|---|
| [deck-engine.md](deck-engine.md) | Models, builders, the registry, layout rules and the HTML render. |
| [agent-layer.md](agent-layer.md) | Project storage, phases, one chat turn, agents, tools and services. |
| [deck-generation.md](deck-generation.md) | How `DeckGenerator` turns a plan into a deck. |
| [visual-agent.md](visual-agent.md) | How the interview agent makes diagrams and mockups. |

## Purpose

The system makes a slide deck. It has two parts:

1. A **deck engine**. It turns a JSON deck spec into positioned elements, and then into self-contained HTML. It uses no LLM.
2. An **agent layer**. It turns a chat into a plan, and then a plan into a deck spec. It uses LLM agents and calls the deck engine.

The engine does not know the agent layer. The agent layer calls the engine.

## Data flow

```
chat ──► interview agent ──► Plan ──► DeckGenerator ──► slide specs ──► builders ──► Deck ──► HTML
                              │            ▲                                          │
                              │            └── DeckChecker, LayoutFitter ◄────────────┘
                              └── visual agent ──► SVG ──► PNG asset ──► figure slide
```

| Stage | Input | Output | Code |
|---|---|---|---|
| Interview | Chat messages | `Plan` (`plan.json`) | `decks/agents/` |
| Fill | `SlideDraft` of the plan | Slide spec (one pydantic model per kind) | `decks/agents/services/generator.py` |
| Stage 1: build | `DeckSpec` | `Deck` (`deck.json`) | `decks/builders/` |
| Stage 2: render | `Deck` | One HTML file | `decks/render/htmldoc/services.py` |

## Package map

| Path | Role |
|---|---|
| `decks/models/` | Pydantic models. One file for each slide family, plus `elements.py`, `plan.py`, `build.py`, `theme.py`, `base.py` and `slides.py`. |
| `decks/builders/` | One builder class for each slide kind, grouped by family. Also the registry. |
| `decks/builders/charts/` | The shared chart renderer. |
| `decks/render/` | HTML renderer and the review gallery. |
| `decks/agents/` | The agent layer. |
| `decks/visuals/` | The visual agent: SVG check, Chrome measure, PNG render. |
| `decks/design.py` | Design tokens: canvas size, type scale, spacing. |
| `decks/text_metrics.py` | Text size estimate. Builders and the checker share it. |
| `decks/settings.py` | Azure OpenAI settings. |

## Entry points

| Command | Use |
|---|---|
| `uv run python -m scripts.pipeline build spec.json -o out/deck.json` | Stage 1. |
| `uv run python -m scripts.pipeline render out/deck.json -o out/deck.html` | Stage 2. |
| `uv run python -m scripts.pipeline gallery` | Render every example in both themes. |
| `uv run python -m scripts.pipeline review -o gallery.html` | One review gallery. |
| `uv run python -m scripts.chat` | Chat client for the agent layer. |
| `uv run python -m scripts.pipeline` | Build, render and gallery commands (`scripts/pipeline.py`). |
| `uv run python -m scripts.gen_catalog` | Regenerate `docs/slide-catalog/`. |

## Design decisions

- **The engine is deterministic.** A builder has fixed coordinates and uses no LLM. Thus a slide is the same each time.
- **The LLM fills parameters. It does not draw.** The spec model is the contract. A wrong spec fails validation, and the generator repairs it.
- **Layout errors cost no LLM call when possible.** `LayoutFitter` fixes overflow before the checker asks for a new fill.
- **Advice does not block.** `VarietyPolicy` returns advice in the tool result. It never stops `/approve`.
- **One writer for each project turn.** The turn lock stops two chat turns on one project.
- **A merged kind keeps old plans alive.** `KIND_ALIASES` maps a removed kind to its successor.

## Rules

Read [AGENTS.md](../../AGENTS.md) and the files in [rules/](../rules/) before you change code.
