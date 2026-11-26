# UI Quality

## Accessibility

- Use the semantic element for the job: `button` for an action, `a` for a link, `label` for a field.
- Make each control reachable and usable with the keyboard.
- Keep the focus ring visible. Do not remove it.
- Give each field a visible label. Give each icon-only button an accessible name.
- Do not use color alone to show a state.
- Keep the text contrast at the WCAG AA level or better.
- Respect `prefers-reduced-motion`. Remove non-essential motion for it.
- Make each screen usable at a narrow width. Do not hide an action on a small screen.

## User text

- Put each user-facing string in one place, for example one module of texts. Do not scatter strings in components.
- Write in plain words, in the active voice.
- An error text says what went wrong and what the user can do.
- An empty state says what is missing and gives the next action.
- A button names its action: "Save deck", not "OK".

## Checks

- `eslint-plugin-jsx-a11y` passes.
- A review confirms the keyboard path of each new screen.
- A lint rule or `grep` finds no literal user text in components, when the app has a text module.
