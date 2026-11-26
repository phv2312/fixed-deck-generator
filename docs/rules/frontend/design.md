# Design Guide

This file is a guide. Prefer these practices. The brief of the product always wins. When the brief gives a visual direction, follow it.

## Before you design

State three facts, and confirm them with the owner of the product:

- The subject: what the product is.
- The audience: who uses it.
- The primary job: what the user must do first.

Take visual choices from the subject and its field. Do not take them from a template.

## Token plan

Write a short plan before you write UI code. Keep it in the pull request or in the theme file as a comment.

| Part | Content |
|---|---|
| Color | 4 to 6 named colors, with hex values. |
| Type | The typefaces and the role of each. |
| Layout | One sentence for the concept, a simple wireframe, and the alignment of the content. |
| Principles | What makes this product look like itself. |

Then review the plan. When a part is what you would choose for any similar product, change it. Write down what you changed and why.

Put the final values in the theme file. See [styling.md](./styling.md). When the brief gives no direction, keep the default theme.

## Type

- Prefer one typeface or two. When you use two, make them clearly different.
- Set a clear type scale with fixed sizes, weights, and spacing.
- Keep a line under 80 characters. Give serif body text a little more line height.
- Prefer not to accent one word in a headline, set a label in capitals, or add a label above content that does not need it.

## Structure

- A border, a divider, a number, or a label must carry information about the content.
- Use numbered markers only for a real sequence, such as steps or a timeline.
- Prefer a different shape for a different level of importance. Do not put every item in the same card.

## Motion

- Use motion to show what changed after an action: open, expand, confirm.
- Use motion that the user did not start only to draw attention, and only once.
- Prefer not to add an entrance effect to each section or a hover effect to each card.

## Restraint

- Spend boldness in one place. Let one element be the memorable one. Keep the rest quiet.
- Before you finish, remove one decoration.

## Common defaults to question

Each item below is allowed when the brief asks for it. Do not use it only because it is the default.

- A cream background with a serif headline and a warm clay accent.
- A near-black background with one bright accent.
- A newspaper layout with hairline rules and sharp corners.
- A kit of identical rounded cards with the same shadow and gradient washes.
- A capitalized label above each heading, texts joined with middle dots, and an arrow added to each link.

## Checks

- A review confirms that the token plan exists and that the theme file matches it.
- A review confirms that one element is the focus of each screen.
