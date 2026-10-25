# UI redesign, 2026-10-19: direction (v2, after the audits)

The spec every page pass follows. Read [BRIEF.md](BRIEF.md) first (the user's words and the fixed rules), then
this, then your audit in [audit/](audit/). Taste research: [INSPO.md](INSPO.md). The shared layer described here
is built by the lead before any page pass starts; page passes use it and never edit `ui.css`, `ui.js`, `kit.js`.

Taste in one line: a calm, dense study tool in the Linear / Stripe register. Small confident type, one orange
accent, the task in the middle, context in the sidebars, extra detail one tap away.

## 0. The point: a better looking, simpler app

This is a redesign, not a bug sweep. Fixing what is broken is the floor; the job is that every page looks
deliberate and is obvious to use. A page pass is judged on these, in this order:

1. **One focal point per screen.** In the first 900px of a laptop, the eye lands on one thing: the page's task and
   its one orange primary. Everything else is quieter (smaller, `--soft`, in the side column, or folded).
2. **Clear hierarchy.** Title, then the task, then context. Sizes and weights come from the scale in section 1 and
   step down visibly; no two neighbours compete at the same weight.
3. **Composition, not a pile of cards.** Main column for the task, right column for context. Rows instead of
   card grids for lists. Related things share one card with hairlines between them; unrelated things are not
   boxed at all if spacing can separate them.
4. **Alignment and rhythm.** Shared left edges, one row height per list, one gap per grid, figures on a
   baseline. Nothing floats at an arbitrary offset; nothing stretches over empty space.
5. **Fewer words.** Labels say what a thing is; no line explains the UI. If a sentence can go, it goes; if a
   student might need it, it folds.
6. **Calm colour.** Orange marks the primary action and progress only. Status uses the existing state tokens
   and never colour alone.

Each pass reports, per page, what the first screen now leads with and what moved out of the way.

## 1. Type

Geist (self-hosted, `/assets/fonts/Geist.woff2`) for everything but question text. Source Serif 4 stays for
questions (`--serif`, `--q-size`, `--q-opt` unchanged). **Words are never mono.** Geist Mono (`--mono`) only for
`kbd`, code, the test timer (`.t-digits`), OTP and code inputs, the countdown digits, the scientific calculator
and scratch pad. Chart svg text is Geist 11.5 tabular; charts.js `textW` measures at 11.5. Figures are Geist: `tabular-nums` in
columns, counters and clocks; a lone headline figure stays proportional.

The scale. Eight steps, weights 400 / 500 / 600 only. No new rule uses a size outside it.

| Step | Size / weight / tracking | Absorbs | Where |
|---|---|---|---|
| hero | 44 / 600 / -0.03em, lh 1 | 34-96 | the one score or count a page is about (`.gauge-v`, score reports) |
| figure | 28 / 600 / -0.02em, lh 1.05 | 24-32 | `.stat-v`, countdowns, a card's big number |
| page | 22 / 600 / -0.02em, lh 1.2 | 20-26 | `.h1`, one per page |
| section | 16 / 600 / -0.01em, lh 1.3 | 16-19 | `.h2`, card and sheet titles |
| body | 14.5 / 400 (titles 600), lh 1.5 | 14.5-15.5 | paragraphs, rows, `.h3` |
| control | 14 / 600 on `.pill` `.btn`, 500 on chips, tabs, nav | 13.5-14 | buttons, chips, tabs, menu rows, labels |
| meta | 12.5 / 400-500, `--soft` | 12-13 | `.k`, `.meta`, `.help`, legends, table heads |
| micro | 11.5 / 500 | 7-11.5 | badges, kbd, rail counts, cell glyphs |

- Inputs stay 16px (the iOS focus-zoom floor); `.field.sm` goes 15 to 16.
- `.k` is meta: Geist 12.5/500, sentence case, no tracking, `--soft`. A card title needs no kicker above it; a
  kicker above an `.h1` goes. `UI.date(d, 'eyebrow')` no longer upper-cases.
- Every `text-transform: uppercase` on words goes, except `kbd`, the printed sheet's table head and code inputs.
  All-caps strings typed in JS (compete) are rewritten in sentence case by their page pass.
- Out of scale by design: serif question text, em-relative math (`.frac`, `.sp`, `.rad`), glyphs drawn in fixed
  boxes (`.cell::after`, `.cal-sat`, `.heat-d`).
- Headings `text-wrap: balance`, paragraphs `text-wrap: pretty`.

## 2. Space

4px grid: 4 8 12 16 20 24 32 48. 2 and 6 only inside a control or a mark grid.

| Token / rule | Was | Now |
|---|---|---|
| `--card-pad` | 22 (16 phone) | 16 (12 phone) |
| `--card-gap` (new) | page-local 20 | 12 |
| `.card-head` margin-bottom / `.card-foot` margin-top | 16 / 18 | 12 / 12 |
| `--ctl` (fine pointer) | 40 | 36 (44 on coarse pointers, unchanged) |
| `.btn.sm` / `.pill.sm` | 32 / 34 | 34 / 34 |
| `.seg` option | `--ctl` - 6 | `--ctl` - 4 |
| `--row-h` (new) | 40-60 | 40: list rows, hairline dividers, inside one card |
| `--radius-card` | 14 | 12 |
| sheet head / body / foot padding | 16/14/10/24, 4/24/22, 14/24 | 12/12/8/20, 0/20/16, 12/20 |
| `.page` top / bottom | clamp(16,3vh,32) / 88 | 16 / 48 (the phone keeps room for the tabs) |

- `.pill` stays 42px with 10px corners (the user's rule). It is the page's one primary; in cards and rows use
  `.pill.sm`.
- Page header: `.h1` and the page's primary action on one row; a subtitle only when it carries a fact.
- Lists are rows, not cards.

## 3. Surfaces

- Page `--paper`. Sidebar `--tile` with a hairline edge. **A card is `--tile` with a 1px `--line` hairline**
  (the audits measured `--tile` on `--paper` at 1.10:1; every source separates cards; listed for the user).
  `.card.line` stays as the card-on-a-tile variant.
- Two inherited tokens decide what sits inside a surface: `--surface` (the colour you are on) and `--well` (a
  track or button one step darker). `:root` paper / tile-2; inside `.card, .panel, .stat, .side, .now-strip > *`
  tile / mat; inside dialogs, popovers, menus paper / tile-2. Components that vanished inside a card (`.stat`,
  `.chips`, `.chip`, `.opt`, `.countdown`, `.btn`, `.skel`, `.seg`) read `--well`. Fields stay on paper.
- A `.stat` inside a card has no fill of its own. No card in a card: inside a card, group with hairlines.
- One track colour, `--track` (alpha, works on any surface): meters, skill tracks, ranges, switches, `.mbar`.
- Shadows only on things that float: menus, popovers, sheets, toasts, tooltips (`--shadow-pop`). `.pill:hover`
  is a 6% darker fill, not a glow.
- Radius scale: 4 marks, 6 badges and tags, 8 chips, `.btn.sm`, menu rows, cells, 10 `.btn` `.pill` fields,
  12 cards and floats. `50%` only for avatars, dots, rings, radio marks and knobs, never a button.
- One tag: `.badge` (6px corners; `.badge.soft`, `.badge.line`). Pages drop their local tag clones for it.

## 4. The shell: sidebars that work

Left sidebar from 1100px wide (the 68px rail below it, phone bar and tabs under 760px):

1. Brand row 48px: the mark, the wordmark (`.side-word`, the brand lockup, kept as is), the collapse toggle.
2. Search (`Mod+K`) fills the row; Quick is a square button beside it.
3. Nav: nine items, 34px rows; the two groups split by a 12px gap; "Study" / "Progress" kept for screen readers only.
4. The Now block, pinned above the user row: Up next (title, Start, the more button; meta and reason in the
   tooltip) and the Today card (streak, minutes against the goal, exam countdown). It shows from 700px tall;
   below that it goes back to the Now strip in main, as today.
5. User row 48px with Help and Feedback as icon buttons beside it.

Rules:
- When the sidebar shows Up next, the Now strip and `.sections-next` are hidden (they repeat it).
- When Up next's first item is a link to the page you are on, the Now strip and `.sections-next` skip it.
- `UI.shell({ now: false })` (Today, Plan, Tests; Sign in, Welcome and Pair should pass it too): no Now strip and
  no `.sections-next`, since the page carries its own Start. `nowBlock: false` (Today, Plan) also hides the
  sidebar Now block (`body.no-now`); Tests keeps it.
- Section chips (`.sections`) get 8px corners.

Right context column: `.twocol` (the name `.split` is taken by the Check button) with `aside.twocol-side`.
From 1280px wide: main plus a 300px aside, sticky 16px under the top, scrolling inside itself when taller than
the window. Below 1280 the aside stacks after the main content, or before it with `.twocol.side-first`.
Filters, summaries, legends, the selected item's detail and secondary stats go there. Today moves from its
measured `.td-side` balancing to `.twocol`.

The session, the test window, the challenge and print pages have no chrome and no `.twocol`.

## 5. Auto-hide

- Long helper text folds automatically (`FOLD_SEL`). Fixed in the shared layer: nothing that contains a button
  or a form control folds; `aria-live="off"` no longer blocks folding (Plan); popovers never fold; sheets fold
  only when the dialog has `data-fold`; the Report folds (`FOLD_OFF` is print pages, `?print=`, help and
  `/words/run`); `.spr-rule` and `.x-card` left `FOLD_SEL` (question.js folds its Explanation itself); timer
  ticks do not trigger rescans. Page passes add new info-box classes to their audit's notes for the lead, and
  use `data-nofold` for errors, live status and anything the student must read first.
- `.reveal`: an element that shows when its parent is hovered or has focus inside, on fine pointers; always on
  coarse pointers (phones show everything desktop shows). Hidden with opacity and visibility, so nothing shifts.
- Empty states: one line and one action.
- Explanations of how the UI works go to Help or a `?` tooltip, never a paragraph on the page.

## 6. Banned (the slop list)

Uppercase letter-spaced kickers; mono for words; 999px or 50% on chips or buttons; gradients other than a chart
fill or a scroll-edge fade; glow, glass, blur, grain; decorative icons beside headings; emoji; three equal
"feature" cards; exclamation marks; em dashes (the missing-value glyph is an en dash); Title Case; copy that
praises, explains the UI, or restates the label; animation on load for its own sake.

## 7. Motion

One curve, `--ease` (cubic-bezier(.23, 1, .32, 1)); `linear` only for timed fills. Entries 160 / 200 / 240ms,
exits about 75% of that (120 / 150 / 180), press 120ms `scale(.97)`. Dialogs 240 in, 180 out; popovers 150 from
`scale(.95)`. Tooltips wait 400ms, sit 6px off, do not move. Hover motion only under `(hover: hover) and
(pointer: fine)`. Nothing animates on load: `countUp` is opt-in, `.rise` is a no-op, `.mbar` fills in 200ms.
Reduced motion turns movement off.

## 8. Ownership and the page passes

- Shared layer (`ui.css`, `ui.js`, `kit.js`, `tools/check-ui.py`, fonts): the lead only.
- Each page pass owns the files its audit scopes, never edits the shared files, and lists what it needs there
  under "Shared asks" in its report.
- Required in every pass: the audit's BIG proposals, its bug list, and its ranked proposals in order as far as
  they go. Anything not done is listed under "Not done" with the reason; nothing is narrowed silently.
- Zero functionality loss: every action, link, figure, state, shortcut, tooltip, empty / error / loading state and
  phone path stays reachable. Moving or folding is fine; dropping is not. Features the code holds but students
  cannot reach today (Words: Export CSV, Import, the 14-day forecast, By exam day, offline cards) are made
  reachable again.
- Never rename or remove a class or id another file uses (grep first). Contracts named in the audits stay (Review:
  `#start`, `#rhtabs`, `#list`, `.rh-pane`; chart text sizes tied to charts.js `textW`).
- Checks before reporting: `python3 tools/check-ui.py`, `node --check` on touched JS, a grep that no removed
  selector is still referenced, a grep for em dashes in touched files. No browser, no screenshots, no git.

## 9. Polish round (v3): decisions from INSPO-VISUAL.md

- **Orange stays the selection colour** (the user: "keep the orange, that is brand color"). Selected chips, `.seg`,
  pressed `.btn`, `.dd.on`, `.sections` current, the sidebar current item and `.badge` keep their orange. Do not
  neutralise them. Where a control stacks fill + ring + bold, keep it; tidy only if a page has two competing
  orange marks on one control.
- Titles stay 600 (INSPO-VISUAL 6.1 not taken).
- New shared pieces, built by the lead (use them, delete local copies): `UI.why(text, {label})` (the one `?` that
  explains: click, tap or Enter opens it), the tooltip tap fallback on touch for info triggers, `UI.saving(btn,
  promise)` (Save, Saving, Saved in place), `.meter.ticks` (a tick meter), the heatmap readout line, `.choice-row`
  (a row-shaped toggle button: wash-2 + amber inset when pressed, `--row-h`, 8px corners), `--shadow-float` for
  menus, popovers, tooltips and toasts, scroll-edge fades, a fold on the sidebar Now card.
- Per-page polish follows INSPO-VISUAL section 4 and the section 5 items assigned to each page.
