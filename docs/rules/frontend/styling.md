# Styling

MUI is the component library. One MUI theme is the only source of colors, fonts, spacing, and shape. Tailwind is for layout only.

## Rules

- Define the theme in one file. Change a design value there and nowhere else.
- Use a theme value for each color, font, spacing, radius, and shadow. Do not write a hex color or a pixel value in a component.
- Use Tailwind utilities for layout and spacing only: `flex`, `grid`, `gap`, `p-*`, `m-*`, `w-*`.
- Do not use Tailwind for colors, fonts, or shadows.
- Do not restyle an MUI component with Tailwind classes. Use the `sx` prop or a theme override.
- Prefer an MUI component to a custom one.
- Support the light mode first. Add the dark mode through the theme only.

## Default theme

Start from these values. Change a value only for a stated reason.

| Item | Default |
|---|---|
| Font | One system font stack. |
| Base text size | 16 px. |
| Type scale | About five sizes. |
| Line length | At most 80 characters. |
| Spacing | A base of 8 px. Use multiples. |
| Colors | One primary color, neutrals, and the colors for success, warning, and error. |
| Radius | One value. |
| Shadow | One level for raised surfaces. |

## Preferred design practice

These are guides, not hard rules.

- Prefer a plain, consistent screen to a decorated screen.
- Prefer one clear accent to many accents.
- Use motion only to explain a change. Keep it short.
- Keep the same pattern for the same task on each screen.

## Checks

- `grep` finds no hex color and no `px` value outside the theme file.
- A review confirms that no component restyles MUI with Tailwind classes.
