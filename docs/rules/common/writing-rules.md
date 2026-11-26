# Writing Rules

## Where a rule goes

- Put a rule in the lowest area that applies to it. See [../README.md](../README.md).
- Give each fact one owner file. Link to the owner from other files.
- Let a tool enforce each rule that a tool can check. The rule file gives the idea. The tool setting goes in the tooling file of the area, if it has one, or in the README of the area.
- Link with relative paths. Link only to the same area or a lower area. Do not point to a higher area in plain text.
- Add a new area when a rule does not fit any existing area. Give it a `README.md` with an index table and a `Checks` section.

## How to write a rule

- Write the idea first. Add an example only when the idea is not clear.
- Write each Python code block so that `ruff format` accepts it. Ruff formats the code blocks in Markdown. Show a method inside its class.
- Start with a short purpose, then the rules, then a checklist when the rule has more than five items.
- Keep a rule file under 300 lines. Split a longer file. Code files have their own limit, which the area rules give.
- Write in ASD-STE100. See [documentation.md](./documentation.md).
- Do not add frontmatter. The `README.md` of the area tells when to read each rule.
- Add the file to the `README.md` of its area. Do not list it in `AGENTS.md`.

## How to change a rule

- Change the owner file. Then check each file that links to it.
- To remove a rule, delete the text and its links in the same change.
- To break a rule for one case, write the reason in a comment next to the code. Do not weaken the rule.
