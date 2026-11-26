[← Architecture](README.md)

# HTTP API

The HTTP API is a thin layer over the agent layer. It lives in `decks/api/`. It follows [../rules/backend/](../rules/backend/README.md) and the contract in [../rules/common/api-contract.md](../rules/common/api-contract.md). The domain code does not import it.

Run it with `uv run uvicorn decks.api.main:create_app --factory`. Swagger is at `/docs`.

## Layout

| Path | Role |
|---|---|
| `decks/api/main.py` | `create_app`. The lifespan opens the `Container` and puts it on `app.state.container`. |
| `decks/api/routers.py` | Mounts the feature routers under `/api/v1`. It sets the prefixes and the tags. |
| `decks/api/errors.py` | `ErrorBody` and `ErrorHandlers`. One error body for every failure. |
| `decks/api/middlewares.py` | Request id (`X-Request-ID`), access log, CORS. |
| `decks/api/openapi.py` | Response helpers, `RouteDoc`, default 422 and 500 responses. |
| `decks/api/deps.py`, `payloads.py` | `ContainerDep`, `PageQuery`, `PageResponse`. |
| `decks/api/projects/` | The project feature: `router`, `deps`, `payloads`, `services`, `models`, `exceptions`, `openapi/`. |
| `decks/api/chat/`, `decks/api/plan/` | The chat feature (send, history, tool fields) and the plan feature (read, approve). Same layers as `projects`. |

A feature has the layers `router → deps | openapi → payloads → services → models | exceptions`. import-linter checks them (`uv run lint-imports`).

## Errors

Every error is an `AppError` (`decks/exceptions.py`). The class name is the `code`. `STATUS_CODE` is the HTTP status. The agent-layer errors extend `AppError`. `ProjectNotFoundError` and `DeckMissingError` are 404. `TurnInProgressError`, `GenerationInProgressError`, `PlanMissingError` and `PlanIncompleteError` are 409. An error with a status of 500 or more has a generic message.

An error that Starlette raises outside the middlewares (an unhandled `Exception`) goes through the outermost handler. It has no `X-Request-ID` header and no CORS headers.

## Endpoints (v1)

| Method and path | Result |
|---|---|
| `GET /api/v1/projects?limit&offset` | `{items, total}`. The newest change comes first. `limit` is at most 100. |
| `POST /api/v1/projects` `{name}` | 201 and the new project. The server makes the id. |
| `GET /api/v1/projects/{id}` | One project. 404 `ProjectNotFoundError`. |
| `DELETE /api/v1/projects/{id}` | 204. 409 `TurnInProgressError` while a chat turn runs. |
| `GET /api/v1/projects/{id}/deck/slides/{index}/html` | `text/html` of one slide, for an `iframe`. 404 for no deck or a bad index. |
| `POST /api/v1/projects/{id}/chat` `{message}` | `text/event-stream`: one frame for each `StreamEvent`, last `done`. 404, 409 `TurnInProgressError`. |
| `GET /api/v1/projects/{id}/chat` | `{messages, running, pending_question}`: the transcript of the chat. |
| `GET /api/v1/projects/{id}/tool-calls/{call_id}/fields/{key}?download` | The full value of one tool input or output. |
| `GET /api/v1/projects/{id}/plan` | The plan, the phase and the open question. |
| `POST /api/v1/projects/{id}/plan/approve` | Approves a complete plan. 409 for no plan, an incomplete plan, a later phase, or a running turn. |

A project has `id`, `name`, `phase`, `created_at`, `updated_at`, `slide_count` and `thumbnail_url`. `phase` is the `BuildState` phase as it is. `updated_at` is the newest file time in the project folder. `thumbnail_url` is `null` until a deck exists.

The slide page comes from `HtmlRenderer.slide_document`. It has no backdrop and no gap, and it scales to the width of its frame.

A project id in a path matches `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`. This keeps an id from leaving the projects folder.

## Chat and plan

The `chat` and `plan` features are in `decks/api/chat/` and `decks/api/plan/`.

**Send a message.** `POST …/chat` starts a turn with `ProjectRunner.run` and streams its events as server-sent events. A frame is `event: <type>` and `data: <JSON of the event>`. The types are those of `StreamEvent` in [agent-layer.md](agent-layer.md). The last frame is `done`. A failure during the turn is an `error` frame. A missing project or a running turn gives a normal 404 or 409, before the stream starts. The response has `Cache-Control: no-cache`, `X-Accel-Buffering: no` and `X-Request-ID`. When the client closes the connection, the turn stops.

**Read the chat.** `GET …/chat` turns the items of `chat.json` into messages. A user item is a user message. The function calls, outputs and text items after it are one assistant message, with `tool_calls` and `text`. A message id is `m<index of its first item>`. Reasoning items are not shown. A tool call has `id`, `name`, `summary`, `status` and `fields`.

- `status` is `done` when the call has an output. A call without output is `running` while the turn lock is held, and `error` when the turn stopped before the call ended. `chat.json` does not store a tool failure, so a failed tool call that the agent corrected shows as `done`.
- `duration_ms` is `null`: `chat.json` keeps no timing.
- `summary` is the question for a question call, and the first line of the output for any other call (at most 100 characters).
- A question call fills `question` of its message. `pending_question` is the question of the last message when no user message follows. The user's answer is the next chat message, one question at a time.

**Tool fields.** A tool input or output can be large, for example an SVG. The history never has a full value. Each field has `key` (`output` or `input.<argument>`), `size` in bytes, `mime`, `preview` (the first 200 characters) and `url`. `GET …/tool-calls/{call_id}/fields/{key}` returns the full value with its own media type (`text/plain`, `application/json` or `image/svg+xml`). `download=true` adds `Content-Disposition: attachment`. The value is sent with `Content-Security-Policy: sandbox; default-src 'none'` and `nosniff`, so an SVG cannot run a script. The values are read from `chat.json`, which keeps every item.

**Plan.** `GET …/plan` returns `phase`, `revision`, `approved`, `can_approve`, `theme`, `meta`, `slides` (`id`, `kind`, `purpose`, `title`, `summary`, `points`), `missing`, `variety` and `pending_question`. A project without a plan gives an empty plan. `pending_question` is only set during `draft`, `interviewing` and `review`.

**Approve.** `POST …/plan/approve` calls `InterviewService.approve`, like `/approve` in `scripts/chat.py`. It works only in `draft`, `interviewing` and `review`, so that it cannot move a built project back to `approved` (`PlanLockedError`). `PlanMissingError` and `PlanIncompleteError` are 409. To ask for changes, send them as a chat message. The agent edits the plan with its plan tools.

## Deck editing

The `deck` feature (`decks/api/deck/`) reads the built deck and edits its elements. The editor shows `GET …/slides/{index}/html` in an `iframe` and draws selection boxes over it. Each element in that HTML has `data-element-id`, which is the `id` of the deck response. A line or a polygon is an SVG that covers the whole slide. Use the `x, y, w, h` of the response for its box, not the DOM box.

| Method and path (under `/api/v1/projects/{id}/deck`) | Result |
|---|---|
| `GET` | `{revision, width, height, slides, can_undo, can_redo}`. Each slide has `index`, `id`, `kind`, `title` and `elements`. Each element has `id`, `type`, `parent_id`, `z`, `x`, `y`, `w`, `h`, `props` and `editable`. |
| `PATCH /slides/{i}/elements/{eid}` `{base_revision?, changes}` | Change fields that are in `editable`. Returns `{revision, element, issues, can_undo, can_redo}`. |
| `POST /slides/{i}/elements` `{base_revision?, kind, props}` | 201. Add a `text`, `image`, `table`, `shape` or `chart` on top. An image needs `props.src`. |
| `DELETE /slides/{i}/elements/{eid}?base_revision` | Remove an element, also from inside a group. |
| `POST /slides/{i}/elements/{eid}/duplicate` | 201. Copy a top-level element, 16 units down and right, above the original. |
| `POST /slides/{i}/elements/{eid}/order` `{move}` | `forward`, `backward`, `front` or `back`. |
| `POST /undo`, `POST /redo` | Move along the edit history. `element` is `null`. |

- **Save at once.** Each edit writes `deck.json`, so a later `GET` and the slide HTML show it. The write goes through `DeckEditor.commit`, which also marks the slide as edited in the build state.
- **Revision.** `Deck.revision` grows by one with each edit, undo and redo. An edit with an older `base_revision` fails with 409 `StaleDeckRevisionError`.
- **One writer.** An edit takes the write lock of the project. While a chat turn runs it fails with 409 `TurnInProgressError`.
- **Bad edit.** A field that is not in `editable`, a bad value, an empty change, a group duplicate, or a reorder of a group child gives 422 `InvalidElementChangeError`. An image `src` must be an `http(s)` URL or a `data:image` URI, so that the renderer never reads a file from the server disk. `issues` holds the `DeckChecker` result of the edited slide (bounds, text overflow). An issue never blocks the edit.
- **History.** `deck_history.json` (`DeckHistory`, `ModelRepository[DeckHistory]`) keeps the last 20 decks to undo and 20 to redo. A new edit clears the redo list. Undo and redo save the restored deck with the next revision.
- **Not supported.** Slide duplicate, move and delete are not endpoints. A slide belongs to a plan slide, and the build state keys on the slide id. Change slides through the plan (`move_plan_slide`, `remove_plan_slide`) and rebuild.
- **No `alt`.** The `Image` model has no alt field, so it cannot be edited.

## Settings

`Settings` has `title`, `cors_origins` (default `["http://localhost:5173"]`, the Vite dev server) and `json_logs`. Variables use the prefix `DECKS_`.
