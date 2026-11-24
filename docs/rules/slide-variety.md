# Slide Variety Rules

These rules make a deck look varied. The interview agent picks the kind of every slide. It must
follow these rules. `VarietyPolicy` in `decks/agents/services/variety.py` checks them.

The check is advice. It never blocks a plan or `/approve`:

- `add_plan_slide`, `add_plan_slides`, `update_plan_slide`, `remove_plan_slide`
  and `move_plan_slide` return a `variety` list. They check only the rules that are
  true for every part of a plan (rules 1 and 2 and the image check).
- `final_check` checks the full list. It checks rules 3 and 5 as well, because they need the
  whole deck. It returns each issue with the slide to change. It asks for a fix at most
  2 times; then it tells the agent to stop.
- `/approve` in `scripts/chat.py` prints the full list and still approves the plan.

The interview prompt template (`decks/agents/templates/interview.j2`) states the rules. A kind that the user asked for stays.

## Rules

1. Do not put 2 slides in a row with the same kind.
2. Do not put 3 slides in a row from the same family. (`MAX_FAMILY_RUN = 2`)
3. The first slide has kind `title`. The last slide has kind `contact` or `statement`.
4. Match the kind to the content. Rows go to a table kind, stages go to a process kind, and series
   go to a chart kind. Never choose a kind that needs data the slide does not have.
   Only the prompt states this rule. Code does not check it.

5. A deck of 6 or more slides has at least one visual slide: a kind of the `diagram`,
   `analytics` or `pictures` family, or a slide with `content.image`. Use `create_diagram` or
   `create_mockup` only when the slide has a real flow or structure. Data goes to a chart kind. Never draw a picture without
   content. `final_check` checks this rule. The rule is off when Chrome is not installed.
   `VarietyPolicy` takes `visuals_available` for this.

## Later

- Tighten rule 5 to "a visual slide at least every 3 slides" when the visual tools check the
  content of a picture.
