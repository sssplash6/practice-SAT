# Premium audit: Today (web/index.html)

Code-level only (no browser). Files: `web/index.html` (page CSS 20-357, markup 359-393, script 399-2756), shared
`web/assets/ui.css`. Line refs are `index.html:N` unless named. State audited: a returning student on a plan day,
5 tasks (3 plan rows + 2 others), the step merged into row 1, streak not at risk, QotD unanswered (math tab), every
aside block filled. Round 1 and 2 (passes/today.md) already made the two columns, the merged Up next, the aside as one
surface of rows, `UI.why`, `.reveal`, tick meters and `UI.roll` on minutes. What is left is depth, calm and the daily moments.

## 1. First screen inventory

**1440x900** (sidebar 248, main about 728, aside 300; sidebar not counted below: about 15 controls of its own).
- y 16-44 header: greeting h1 22px + date meta (`paintHero` 753-774). No controls. Good.
- y 60-430 Up next (`paintNext` 849): head meta "about 25 min · fits your 30-min goal", 3 rows, "2 more due" fold,
  "1 done" fold, "Or a practice session" toggle (1075).
- y 440-900 QotD surface: head + streak button, tab strip (4 tabs + Full screen), stem, 4 options; its orange Check
  (question.js:1781) lands at about y 870-910, on the fold.
- Aside y 60-900: Today (streak, best, 10-tick meter, Plan, Since yesterday + 3 lines), SAT (40 days, date button,
  Register by, Details), Score (28px band, scale, gap line, Details row, Add a score), Pace (28px figure, bar, drill
  row with a button, Details row), Daily challenge head and its rules line.

| 1440x900 | Count | Where |
|---|---|---|
| Buttons at rest | 25 | Up next 6 (Start, 2 play, 2 fold rows, toggle); QotD 11 (streak, 4 tabs, full screen, 4 options, Check on the fold); aside 8 (date, Details, Target, Score Details, Add a score, drill, Pace Details, challenge ?) |
| Buttons on hover | +15 | 9 card chevrons (`.reveal`, 493), 3 `?` (1276), 3 `⋯` (1293) |
| Links | 3-6 | streak, Plan "1 of 3 done", score source, up to 3 Since-yesterday links |
| Inputs | 3 | native plan checkboxes (1235) |
| Chips / badges | 1-3 + 4 marks | row tags `.badge.soft` (1256); tab marks `.mk` (1456) |
| Boxes | 3 surfaces, about 14 hairlines | hero card, main rows surface, aside surface |
| Bars | 3 | tick meter, score scale, pace `bar4` (1859) |
| Labels / meta lines | about 14 | date, head meta, 3 row metas, 2 fold metas, best, plan, Since, Register by, score source, pace meta, challenge rule |
| Helper text lines | 5 | 3 Since-yesterday lines, gap to target, pace drill line |
| Orange marks | 7+ | Start, Check, lit ticks, flame, tab underline, scale target tick, checked boxes |

Biggest figures on screen are both in the aside (score band and pace at 28px, 264, 1858); the main column tops out at
the 22px greeting and 16px titles, so the eye is pulled right, away from the task. Rows of controls before content:
none above Up next (good); one inside QotD (tab strip, 1492); one in the aside (SAT date row, 2221).

**390x844** (phone bar 56, bottom tabs about 64, so about 720px of view).
- Phone bar: mark, search, review chip, streak, Quick, menu (ui.js:1931). Tabs: 5.
- Header y 72-250: greeting, date (wraps), glance links over 2 lines ("18 of 30 min today", "Plan · 1 of 3 done",
  "SAT in 40 days", 790-795), "Since yesterday" fold row (772).
- Up next y 270-700: head + meta (wraps to 2 lines), 3 rows at about 64px, 2 fold rows, the toggle.
- QotD head peeks at the bottom.

| 390x844 | Count | Note |
|---|---|---|
| Buttons | 3 bar + 14 page | `.reveal` is always on for touch: every row shows checkbox, `?`, `⋯` and play (12 controls in 3 rows) |
| Links | 3 bar + 5 tabs + 3 glance | |
| Inputs | 3 | checkboxes |
| Boxes / bars | 1 card / 0 | |
| Meta lines | about 9 | date, glance, Since meta, head meta x2 lines, 3 row metas, fold metas |

Rows before the first task: phone bar, two lines of glance links, the Since-yesterday row, Up next's head and its
two-line meta. The first Start lands at about y 330, under five rows of chrome and figures.

## 2. Clutter fixes

- **Aside: one disclosure per row.** SAT, Score and Pace each carry two disclosures (the card chevron that folds the
  row, 493, and a Details toggle inside, 2226, 1969, 1882). Make each aside row rest as label, value, chevron; opening
  it shows everything (the old Details content inline). Values at rest: Today "18 of 30 min" + flame; SAT "40 days";
  Score "560-600" (or "Set a target"); Pace "31:20 of 35:00"; Challenge "120 in today" / "#4 of 30"; Words "12 due · 5 new".
  Default open: Today only. Remembered per row as today (`satf.card.<id>`). Zero loss: every block is one tap away.
- **Up next footer: three rows to one.** "2 more due" (1210), "1 done" (1212) and "Or a practice session" (1075)
  stack as three full-width rows. One quiet footer line: `2 more due · 1 done` (each opens its list in place) left,
  `Or a practice session` right.
- **Defer the retrospective.** "Since yesterday" sits above the task on phones (772) and in the Today row at 1440
  (816). Move it under Up next on phones (a single fold row after the card) and keep it in the Today row (open) at 1440.
- **Phone glance: one strip, not two lines of links.** Replace the 3 wrapping links with a 44px day strip: a small
  goal ring with "18 / 30 min", then "Plan 1/3" and "SAT 40d" as quiet links. One line, same three destinations.
- **Phone rows: fold `?` into `⋯`.** On coarse pointers a plan row shows `?` and `⋯`; give `⋯` a first item "Why
  this" that opens the same `.dwhy` (1274). Rows without a menu (non-plan) keep `?`. Saves 3 controls in view.
- **Second orange.** QotD's Check is a `.pill` (question.js:1781) on the first screen at 1440. Shared ask (open since
  round 1): an embedded workspace whose Check is `.btn`, turning amber only once an option is picked.
- **Space between groups.** Header to hero 16 (90) to 24; hero to the QotD surface `--card-gap` 12 (30) to 32; aside
  rows 12px padding (71) to 14. Density stays inside lists (40px rows).

Calm first screen, 1440, top to bottom: greeting and date on one line. Left, the lifted Up next card: its head
("Up next", minutes left), the lead task as a featured row (20px title, one meta line, the 42px Start), two compact
rows, one quiet footer line. 32px of air, then the flat QotD / Mistakes / Points surface. Right, aligned to the hero
top: the Today row open (goal ring, streak, plan, since yesterday), then five one-line rows (SAT, Score, Pace,
Challenge, Words). Orange on screen: Start, the ring's arc, the flame.

390: phone bar; greeting; one day strip; Up next with its featured lead and Start by about y 230; compact rows;
footer line; then Since yesterday, QotD and the glance rows.

## 3. Depth and hero

- **The hero is Up next's lead task and its Start.** Today it is a 34px `pill.sm` on an ordinary 40px row (1285)
  inside a flat tile card like every other card.
- Lift the card: `--paper` fill (page is paper, the other cards are `--tile`), 1px `--line`, a layered warm shadow
  (`0 1px 2px rgb(60 40 10 / .05), 0 12px 32px -16px rgb(60 40 10 / .18)`), 12px radius. Dark: `--tile-2` fill, top
  inner highlight `inset 0 1px 0 rgb(255 255 255 / .05)`, deeper shadow. It is the only raised plate on the page.
- Featured lead row (`mode === 'lead'`, 1195): title 20/600 (step between section and figure), meta with a 14px
  clock glyph, full `.pill` 42px with a trailing play glyph. The `.lead` block (915) gets the same look so both
  shapes of the step (merged row or block) read as one hero.
- The Today row is the second figure: a 44px goal ring (minutes against goal) beside the streak, in the aside at 1440
  and in the day strip on phones. No other card gets elevation: QotD, Mistakes, Points and the aside stay flat
  tiles with hairlines (they are lists and context, not things that float). Sheets and menus keep `--shadow-float`.
- Optional, last: a very soft warm radial wash behind the hero's top edge (amber at 4%), screen only. Med slop risk.

## 4. Buttons, controls, highlights

| Control (where) | Now | Should feel |
|---|---|---|
| Start (1285, ui.css:855) | `pill.sm` 34px, 8% darker hover, scale .97 press, busy at opacity .6 | Hero: 42px pill; tactile edge (`inset 0 1px 0 rgb(255 255 255/.3)`, `inset 0 -1px 0 rgb(0 0 0/.08)`, `0 1px 2px rgb(150 80 0/.25)`); hover: glyph nudges 2px right; press .97; loading: label to "Starting" with a 14px spinner, width held (the `UI.saving` pattern); focus `--ring` |
| Row play (1286, `.dplay`) | grey `--well` 44x34 always | quiet at rest (no fill), `--well` on row hover; play glyph nudges 1px; always filled on touch |
| Plan checkbox (1235, 180) | native box, amber accent, beside drawn `.st` rings on other rows (173) | one drawn ring for both: 22px ring, fills amber with a stroke-drawn check (200ms) on tick; the input stays, visually hidden |
| Fold rows (`button.fold`, 80) | hairline, label + meta + chevron, underline hover | 8px-radius row wash on hover (`--well` 50%), chevron nudges 2px; body opens with motion (5) |
| Card chevron (493) | `.reveal` on hover | aside: always visible at rest (it is the row's only control); main: keep `.reveal` |
| `?` and `⋯` (1276, 1293) | `.reveal` | fine on desktop; phone change in 2 |
| QotD tabs (1473) | raw tablist, amber underline jumps | `UI.tabs` sliding `.tab-ind` (kit.js:1097); marks drawn as SVG |
| Aside quiet buttons (Target 1896, date 2166, Add a score 1971) | text buttons on the row | live inside the opened row; Target keeps its pencil |
| Streak at risk (764) | 600 14.5px text + `btn.sm` | warm callout: `--wash` fill, 10px corners, outlined flame glyph, `1 question` as `btn.sm`; stays `data-nofold` |
| Receipt "Today's work" (885) | `.k` + one figure line + Details | the goal-met moment (7): figures roll, drawn check |
| Goal tick meter (811) | 10 amber blocks, `.done` adds a text "✓" (ui.css:1276) | ring in the hero glance; check drawn as SVG, not a text glyph |

Selected states keep orange (DIRECTION 9). Focus everywhere: `--ring`, never a glow.

## 5. Motion moments

| Trigger | What moves | How |
|---|---|---|
| First data replaces a skeleton (`card()` 486, after `firstPaint` 639) | each surface's content | opacity 0 to 1, translateY 4px, 160ms `--ease`; hero 0ms, main surface 40ms, aside 80ms; only on the skeleton swap, never on repaint; reduced motion: none |
| Task ticked (`patchTask` 1332 repaints all) | ring check, the row, "N done" | check strokes in 200ms; row collapses (FLIP, 200ms) into the footer; the done count rolls (`UI.roll`) |
| Fold row / card chevron / practice toggle (465, 496, 1079) | body | `grid-template-rows: 0fr` to `1fr` + opacity, 200ms in, 150ms out; chevron already rotates (82) |
| Minutes change on screen (681) | ring arc and figure | arc sweeps to the new value 400ms `--ease`; figure rolls (exists) |
| QotD tab switch (1511) | underline, panel | `.tab-ind` slides 200ms; panel crossfade 120ms |
| QotD answered (1577) | tab mark, today's strip tile | mark scales .9 to 1 with its fill 160ms; strip dots fill |
| Both QotD answered (1592) | streak number | `UI.roll` instead of `replaceWith` |
| Start pressed | label | blur(2px) crossfade to "Starting" + spinner, then the existing 120ms main fade |
| Row hover | row | `--well` wash 160ms; play glyph 1px nudge; gated by `(hover: hover)` |

Nothing loops; all of it off under reduced motion except opacity.

## 6. Icons and imagery

- Text glyphs as icons: tab marks `✓` `✕` (1457), the repeat `↻` (225), the meter's `"\2713"` (ui.css:1276). Draw
  them with `ICON.check`, `ICON.x`, `ICON.review` at the 1.7 stroke the set uses.
- Rows have no kind mark: a warm-up, a skill set, Words, QotD, the challenge and Review all start with the same ring.
  Add a 16px kind glyph in the meta line (bolt, practice, words, today, trophy, review: all in `ICON`).
- Two status marks in one list (native checkbox vs `.st` ring, 173-180): one drawn ring (4).
- Flame: one look today; add an outlined "at risk" state and a filled "done today" state (no animation loop).
- Empty states that deserve a spot illustration (line style, 1.5 stroke, `--soft` with one amber accent):
  the rest day lead (911, "Rest day"), the brand-new "Unlocks as you practise" row (729) as a small locked
  preview with "12 of 30 answers" ticks, and Mistakes' "No open mistakes" (1360).
- Meta glyphs: clock before minutes in the lead's meta, a small target before "≈ +N". Data glyphs only; no icons
  beside headings.

## 7. Delight and feedback (all once per day, keyed `satf.moment.<kind>.<day>`, never on load)

- **Goal met on screen**: the ring closes, a check strokes in, the head says "Goal met", the receipt slides in
  at the top of Up next with its figures rolling. Start relabels to "Keep going" (1086) as now.
- **Streak +1** (back from the day's first session): the flame goes from outline to filled amber with a 1 to 1.12 to 1
  scale over 320ms; the number rolls. Milestones 7, 30, 100: one toast with the flame, "30-day streak", no exclamation.
- **Task done**: the check draw and the row tucking into "N done" (5).
- **QotD**: crowd line "You're one of the first 4 today" (1604) gets the tab mark pop; both answered rolls the
  day's-questions streak.
- **Challenge finished**: the row value rolls to "#4 of 30" (2523).
- **New day** note (2728): show as a toast-like line that fades after 6s instead of a static paragraph.

## 8. Ranked top 10

1. Lift Up next (paper plate, layered warm shadow) with a featured lead row and the 42px Start: one obvious hero. M, low.
2. Aside rows rest as label, value, chevron (Today open), one disclosure per row: a true glance column. M, low.
3. Goal ring + streak as the daily figure (aside at 1440, day strip on phone), closing with a drawn check. M, med.
4. Up next footer: "2 more due · 1 done" and "Or a practice session" on one quiet line (three rows to one). S, low.
5. One drawn status ring for every row, check stroke on tick, FLIP into "N done" with a rolling count. M, low.
6. Phone: day strip instead of two lines of links, Since yesterday below Up next, `?` inside `⋯`: Start by y 230. M, low.
7. Fold and collapse motion (0fr to 1fr, 200 / 150ms) for every disclosure on the page. S, low.
8. Streak moments: at-risk callout, once-a-day ignite, rolling number, milestone toast. S, med.
9. QotD polish: sliding tab mark, SVG marks that pop on answer, Check as `.btn` until picked (shared ask). M, low.
10. Skeleton-to-content crossfade with a 40ms stagger by surface, first load only. S, med.

## Shared asks

`ui.css`: tactile `.pill` edge and a busy spinner; a `--shadow-raise` token for the one raised plate; a drawn
check for `.meter.done`; a `.fold` open transition. `kit.js`: `UI.ring` (goal ring, sweeps on change, check on
done); `UI.roll` for any figure (streak, done count, rank). `question.js`: embedded Check as `.btn` (round 1 ask).
