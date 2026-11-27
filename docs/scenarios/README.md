# Scenarios

Each scenario is a short walk through the app. Use a scenario to learn the app. Use it also as a light smoke test: if every check in a scenario is true, that part of the app works.

| Scenario | What you do | Needs the LLM |
|---|---|---|
| [1. Create a project](./01-create-project.md) | Make an empty deck from the start page. | No |
| [2. Make a deck in the chat](./02-chat-to-deck.md) | Talk to the assistant, approve the plan, get a deck. | Yes |
| [3. Edit elements](./03-edit-elements.md) | Change text, move shapes, add elements, undo. | No (needs a built deck) |
| [4. Work with the layout](./04-layout-and-navigation.md) | Fold the chat, move between decks, see the deck name. | No |
| [5. Delete a deck](./05-delete-a-deck.md) | Remove a deck and its chat. | No |

Do the scenarios in order the first time. Scenario 3 needs a deck that scenario 2 built.

## Before you start

1. Fill in `.env` with the Azure OpenAI values. See `.env.example`. Scenario 2 needs them. The others do not.
2. Start the API and the app, each in its own terminal:

   ```bash
   uv run uvicorn decks.api.main:create_app --factory
   cd frontend && npm run dev
   ```

3. Open `http://localhost:5173`.

## Quick check from the terminal

Run this command when the app does not load. It must print `200`.

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/projects
```

If it prints another value, or nothing, restart the API. Then reload the page.

## How to read a scenario

- **Steps** tell you what to do. Do them one by one.
- **Check** lists what you must see. A deck passes when each item is true.
- **If it fails** gives the first thing to try.
