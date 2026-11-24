[← Architecture](README.md)

# Agent layer

The agent layer uses the OpenAI Agents SDK. It connects to Azure OpenAI through `AzureOpenAISettings`.

## Project storage

One folder holds one project. Each file has one repository class in `decks/agents/repos/`:

| File | Repository | Content |
|---|---|---|
| `project.json` | `ProjectRepository` | Name and creation time. |
| `state.json` | `ProjectRepository` | `BuildState`: phase, revisions, build record of each slide. |
| `plan.json` | `ModelRepository[Plan]` | The plan: meta and a list of `SlideDraft`. |
| `deck.json` | `ModelRepository[Deck]` | The built deck. |
| `chat.json` | `ChatRepository` | The chat history. It is an SDK `Session`. |
| `assets/` | `AssetRepository` | Pictures from the visual agent. |

`AtomicJsonStore` writes each file atomically. `ProjectLocks` gives each project a write lock and a chat-turn lock.

## Phases

`BuildState.phase` has six values:

```
draft ─► interviewing ─► review ─► approved ─► generating ─► generated
```

`ProjectRunner.agent_for(phase)` picks the agent. The **interview agent** owns `draft`, `interviewing` and `review`. The **deck agent** owns the later phases. Both agents share the chat session. Thus the deck agent sees every earlier question and answer.

## One chat turn

1. `ProjectRunner.run(project_id, query)` starts a task and streams events.
2. The runner takes the turn lock of the project. A second turn at the same time gets a `TurnInProgressError` event.
3. The runner creates a `ProjectContext` and starts the agent with `Runner.run_streamed`.
4. `SdkEventMapper` maps SDK events to `StreamEvent` objects (`RunStarted`, `Status`, `Token`, `ToolStarted`, `ToolFinished`, `QuestionEvent`, `PlanUpdated`, `DeckProgress`, `DeckReady`, `ErrorEvent`, `Done`).
5. The stream always ends with `Done`. An error does not raise out of the stream. It arrives as an `ErrorEvent`.

## Agents and tools

- `agents/interview.py` builds the interview agent. A question to the user ends its run. The system prompt comes from `AgentPrompts.interview` in `decks/agents/prompts.py`. It renders the template `decks/agents/templates/interview.j2` with the slide catalog and the plan state.
- `agents/deck.py` builds the deck agent.
- `tools/interview.py` has the plan tools: `ask_user_question`, `set_meta`, `remove_meta`, `add_plan_slide`, `add_plan_slides`, `update_plan_slide`, `remove_plan_slide`, `move_plan_slide` and `final_check`. Every plan tool returns a `next_action`.
- `tools/deck.py` has the deck tools: `generate_deck`, `check_deck`, `fix_slide`, `read_slide`, `update_element` and `set_text`. Each `fix_slide` call uses one of `MAX_REPAIRS` repairs of the project.
- `tools/visual.py` has the visual tools. See [visual-agent.md](visual-agent.md).

## Services

| Service | Job |
|---|---|
| `InterviewService` | Edits the plan. Keeps the phase. Runs `final_check`. |
| `DeckGenerator` | Turns a plan into a deck. See [deck-generation.md](deck-generation.md). |
| `DeckEditor` | Edits single elements of a built deck. |
| `DeckChecker` | Checks slides: empty, bounds, text overflow, numbers. |
| `LayoutFitter` | Lowers the font size of a text that overflows its box. |
| `VarietyPolicy` | Gives advice on the variety rules. It never blocks. |
| `SlideFallback` | Builds a plain `content` slide when a fill fails. |
| `EventSink` | Carries events from the services to the stream. |

## The slide catalog

`SlideCatalog` reads the registry. `SlideCatalog.prompt` has one line for each kind: the description and the required fields. The interview agent reads it. The interview agent chooses the kind of every slide. The rules for this choice are in [rules/slide-variety.md](../rules/slide-variety.md).

## Prompt templates

Every system prompt is a Jinja2 template. Do not build a prompt with `str.format` or with string concatenation.

- `PromptTemplates` in `decks/prompting/services.py` renders the templates of one directory. It does not escape text. It raises an error when a variable is missing.
- `AgentPrompts` in `decks/agents/prompts.py` renders the prompts of the interview, deck, and fill agents. The templates are `fill.j2`, `interview.j2`, and `deck.j2` in `decks/agents/templates/`.
- `VisualPromptBuilder.system` in `decks/visuals/prompts.py` renders `system.j2` in `decks/visuals/guidelines/`. This template includes `core.md.j2` and the section of the picture kind. `VisualPromptBuilder.request` stays in code, because it computes the JSON of the request.
- A value that you give to a template is inserted as it is. A brace in the value is safe.
