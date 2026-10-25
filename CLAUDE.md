# SAT Freshman: project rules

## Buttons
- Primary action is `.pill` (amber, 42px, 10px corners; `.pill.sm` is a size down). Secondary is `.btn`, quiet is `.quiet`. Never write a new button style.
- Banned: fully rounded buttons (`border-radius: 999px` or anything 24px and up), round buttons (`50%`; an answer bubble opts out with `/* check-ui: round-ok */` in its rule) and buttons taller than 48px.
- `python3 tools/check-ui.py` checks this; run it before committing UI changes.

## Writing
- No em dashes in code, UI text, docs or commits.

## Extra detail
- Long helper text, intro lines, notes and banner text fold behind a small toggle automatically (`ui.js` fold, selectors in `FOLD_SEL`); question.js folds the Explanation card the same way. Nothing that holds a button or field folds. Open boxes are remembered. Put a new kind of info box in `FOLD_SEL`, or add `data-nofold` where text must always show (errors, live status, anything the user must read first).
