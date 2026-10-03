# SAT Freshman: project rules

## Buttons
- Primary action is `.pill` (amber, 42px, 10px corners; `.pill.sm` is a size down). Secondary is `.btn`, quiet is `.quiet`. Never write a new button style.
- Banned: fully rounded buttons (`border-radius: 999px` or anything 24px and up) and buttons taller than 48px.
- `python3 tools/check-ui.py` checks this; run it before committing UI changes.

## Writing
- No em dashes in code, UI text, docs or commits.
