# Audit: Today (web/index.html)

Code-level only. Line numbers are web/index.html unless a file is named. Heights marked "est." are stacked from CSS, not measured.

Geometry. 1440x900, sidebar 248: main 1192, `.page` max 1120, gutter 40, content 1040. From 1080px the grid is 12 cols, gap 20: main column 687 (inner 643 at `--card-pad` 22), side column 333 (inner 289). 1100 to 1279 with the sidebar: content about 772, side column 244, inner 200. 390x844: gutter 16, card inner 326, phone bar 56, tabs at the bottom.

## A. Purpose and primary action

- Question the page should answer: "what do I do now". Answer today: the Up next lead's Start (`leadFrom` 1033, pill moved into the head at 1079), else the session builder's Study pill (1169).
- First screen 1440x900 (est., warm-up lead, plan with 3 parts): top pad 27, hero 90 (date eyebrow, 36px greeting, chips, brief), gap 20, Up next 190 (lead + "Or a practice session"), then Points on the table runs past the fold. Side: Due today from y 137 (about 300), Mistakes below it. Questions of the day starts under the taller of the two columns: est. 1100 to 1500, so on the second screen.
- With no lead, Up next is the builder: size row, blocks fold, an inline first question (`paintQ1` 1274), Study row. Est. 600+ px; Points starts below the fold.
- 390x844 (est.): hero 250 to 290 (chips wrap to 2 rows, brief stacked as 3 rows of 40px, 138), Up next Start at y 400 to 430, Due today from about 600.
- Two primaries compete: the lead's Start and the Due today row play button for the same plan task (next.queue emits `Plan · <task>`, server/next.py ~100; api_today builds the same task as a Due row). On a test day a third: Recent tests "Resume".
- The 36px greeting is the largest thing on the page and carries no information.

## B. Whitespace (now -> DIRECTION target)

| Where | Now | Target |
|---|---|---|
| `.page` top | clamp(16, 3vh, 32) = 27 at 900 | 16 |
| `.td` bottom (23) | 110 at every width (beats `.page` 88) | 48 desktop, 88 phone |
| `#today` gap, `.td-col` gap (36, 52) | 20 / 20 | 12 |
| card padding | 22 (16 phone) | 16 (14 phone) |
| `.card-head` margin (61 vs 67) | 14 then 8; 61 is dead | 10 |
| Up next `.lead` (142) | pad 18 + border + margin 18 = 37 | 12 + 12, `--line` hairline |
| `.td .sub` (72) | 18 top, 8 bottom | 12 / 6 |
| `.blk` (409), `.go` (183), inline 14/16/18 tops (1498, 2045, 2078, 2465, 2500, 2510, 2517) | 18 | 12 |
| `.fold` row (110) | margin 12 + pad 10/10 = 46px per row | 8 + 8/8, 36px |
| `.qd-past` (298) | margin 22 + pad 16 | 12 + 12 |
| `.drow` (194), `.mrow` (230), gain `.skill-row` (326, shared min-height 60) | rows 60 / 70 to 80 / 78 | 40 to 48 |
| hero (120-138) | eyebrow + h1 36/1.06 + brief margin 10 = 90 | one 40px row |

## C. Non-essential content that is always on

FOLD_SEL (ui.js 2794) on Today catches:
- `.lead` and `.lead-t`: the Up next lead block, Start pill included. `foldOne` wraps any match with 70+ chars of text in a closed `<details>`. A warm-up lead ("Warm-up · 4 check-ins" + "Start") stays under 70; a resume or test lead (title + "34:12 left · 5 of 22 answered" + "The clock keeps running while you're away." + "Resume", 94 chars), a plan test lead (Timed/Untimed, Twin/Fresh, "I took a Bluebook test instead") and rehearsal leads fold. The summary is a garbled first 56 chars with no spaces between blocks ("Resume · Module 1Resume34:12 left…") and the primary action is hidden. Intermittent, so easy to miss. Bug, see I2.
- `.help`: entry-drill rule in Score > causes (2150, 107 chars) folds, fine. Rehearsal popover help (1103, 81) and goal popover `gs.arithmetic` (2531) fold inside a 320px popover, which is silly; popovers are `div[role=dialog]` and FOLD_SKIP only skips `dialog`. Rare-skills help (1519) is 68, size help (1162) 62: not folded. Target sheet help (2200) is in a `<dialog>`: skipped.
- Not caught, and always on: `.line.soft` explanations ("No study time yet. Your first answer starts your streak and fills this calendar." 2435, "Your SAT words live on the Words page." 2684, rest-day line 1029), the answer-changes sentence in Score (2136, 120 chars), the slip advice (2145), the long `needLine` in SAT details (2366), Words' "Word and transition of the day · in the day's questions ↑" (2695).

What to hide or move:
- Per-card collapse chevrons (`cardfold`, 594) on all 14 cards at opacity .6: hover/focus-within reveal on fine pointers, always on coarse (the `.drow` pattern at 208-211 already does this; becomes shared `.reveal`).
- Hero brief (3 server facts, "Yesterday: 30 of 45 min · 2 fixed · challenge #3 of 40"): side column "Since yesterday" on desktop, one fold row on phone.
- Score card (2012-2097) in a 289px column holds band, meta, total, scale, gap fold, practice delta, thin + Sharpen, trend chart, scores you added, verdict, per-week line, calibration, causes bar + fix row, drift block, Add a score. Keep band + target + scale + gap line + one action; the rest under one Details.
- Study time: "This week vs last" tiles (2441-2458) and time split (2499) under Details; the four figs stay.
- Words card: nothing but a meta line and "All words" when the Due Words row exists (2690). Delete or fold into a side row (P5).
- Recent tests: every finished sitting is a full `.tcard` (band, route tag, causes, time lines, scale, missed chips, legend, 4 buttons). Latest open, older ones as one-line rows.
- Tooltip-only facts (invisible on touch, against "phone shows everything"): Due sum goal fit (1317 `title`), Mistakes "fixed this week, half fixed, marked" (1494 `title`), thin-domain evidence (2068 `title`), hero SAT stretch tip (945). Move into the (i) pop or a fold.

## D. Sidebar use

- Left sidebar at 1440x900 is nav only: ui.css 550-557 hides `.nextup` and `.side-day` under 1100px tall; Today passes `now: false` (492) and `.sections-next` skips Today (ui.js 2236). No duplication on a laptop today.
- At 1100px tall and up the sidebar repeats Up next and the hero chips (streak, minutes, exam). PROGRESS step 3 already plans to hide the sidebar Now block on Today; keep that.
- Nav metas visible at 1440 already carry: Today n/m questions + ring, Review "N due · M open", Words "N due", Compete "New/#rank", Plan "Test day/Rest". They make the Words card and the challenge-not-started state redundant.
- Right column today: `.td-side` (span 4 of 12) filled by `place()`/`balance()` (775-852), which moves cards between two bands by measured height. Not sticky, reorders after load, changes tab order with content height, and forces `.mlist` into an inner scroller (843-849).
- Belongs in a right column: Today summary (minutes vs goal, streak, plan n of m), SAT countdown + register, Score summary, Pace figure, Daily challenge, Words, Since yesterday. Belongs in main: Up next + Due today (the task), Questions of the day (a 643px measure is right for Source Serif), Mistakes list, Points on the table, Study time, Calendar, Recent tests.

## E. Redundancy

| Fact | On Today | Shell | Proposal |
|---|---|---|---|
| Study streak | hero chip 938, risk line 926, Study foot "best streak" 2463 | pbar flame (phone), side-day (>=1100 tall), rail ring | side Today panel; pbar on phone |
| Other streaks | QotD calendar-tick streak 1630, challenge streak 2634 | | three streak marks on one page; keep only as tooltips |
| SAT date | hero chip 945, SAT summary "N days" 2343, trigger date 2291, countdown boxes 2320, sr line 2323 | side-day-foot (>=1100 tall) | SAT card only; drop hero chip |
| Today progress | hero minutes chip 942, Plan chip 950, Due sum 1317, Study "Today" fig 2426, receipt 1006 | nav Today meta counts questions, the page counts minutes | one meter in the side Today panel; same unit as nav |
| Up next | lead 1033 + Due plan row 1372 (same task, two Starts) | sidebar nextup (>=1100 tall) | merge cards (P3) |
| Mistakes | Mistakes card, Due Review row, brief "checks" fact (filtered 921), stretch meta 2326 | nav Review meta, phone pbar chip | fine; drop stretch meta |
| Words | Words card, Due Words row | nav Words meta | P5 |
| Module test button | Get a score menu 2030, Up next alt row 1251, verdict fold 2086, Pace tests row | | keep two |
| Score history | Score trend chart 2079, Recent tests bands, brief score fact | | chart under Details |

## F. Local overrides, colours, sizes, radii, inline styles

- Buttons: `#next .lead-head .pill` 40px tall, radius 14 (145) breaks the 42/10 rule; use `.pill` or `.pill.sm`. `.exam-trig` (350) is a new button style (CLAUDE.md forbids): `.btn.sm`. `.clock-tog` (160) a 50% circle at `--ctl`. `.hero-stats a` (126) radius 16 on 32px: a pill. `.qd-tabs button` (275) and `.days7 button` (432, dead) are hand-made segmented controls: `UI.seg`. `.td .quiet` (96), `.td .pill:disabled` (98), `.td .size-picks .chips > button` (164) override shared rules.
- Redefined shared classes: `.streak` (151 vs ui.css 331), `.mrow .dot` 8px (232 vs ui.css 1880 7px), `.td .skill-row.gain` grid (329 vs ui.css 2300), `.td .card .k` (93).
- Type: 23 px sizes in the page `<style>`: 10, 10.5, 11, 12, 12.5, 13, 13.5, 14, 14.5, 15, 16, 17, 18, 20, 22, 24, 26, 28, 34, 38, 40, 44, 48. Scale has 8.
- Mono on figures and words: `.big` 44 (82), `.score-band` 48 (343), `.wk-n` 26 (269), `.fig .v` 24 (366), `.tcard .band` 34 (444), `.dd-fig b` 22 (385), `.extra-row b` 18 (333), `.receipt .rfig` 16 (188, a words line), `.mchips` (446), `.blocks .no/.qm` (170, 173). Only clocks (pace mm:ss, countdown) may stay mono.
- Uppercase: 72, 80, 263, 420 in CSS; hero eyebrow via kit.js 215 `.toUpperCase()`.
- Radii in use: 2, 4, 6, 8, 10, 12, 14, 16, 50% (9 values).
- Colours: tokens only. Orange-tinted hairlines `color-mix(amber 25/16/14%)` (142, 169, 194) instead of `--line`. `#000` only inside a mask (217).
- Card in card (paper box on a tile): `.q1` 181, `.receipt` 186, `.tchip` 178, `.figs > .fig` 365, `.wk-t` 268, `.causes-fix` 344, `.slot-detail` 407, `.tcard` 442.
- Inline styles: about 50 `style:` props. Worst: target line cssText (1894) and its `<br>` (1893), `gain-sort` flex inline (1890), sheet actions row (2201), `stat()` font override (2707, dead), `margin:0` on `.line` (1250, 1483, 1976, 1998, 2001, 2312, 2601, 2924, 2931), `margin-top` 14/16/18 family.

## G. AI-slop tells

- Greeting h1 "Good morning, Name" with an uppercase date eyebrow above it.
- Uppercase letter-spaced `.sub` labels in most cards: TOP 3, WORTH FIXING NOW, BLIND SPOTS, OPEN, READINESS, THIS WEEK VS LAST, WHERE THE TIME WENT, WHERE POINTS WENT, SCORES YOU ADDED, YOUR PLAN'S START; `.k` kickers TODAY'S WORK, IN PROGRESS, ITS TWIN.
- KPI tile rows: `.figs` (4 tiles) and `.wk` (3 to 5 tiles with ▲▼ deltas).
- Text glyphs as icons beside SVG icons: ✎ (2016, 2421), ▾ (2291), ↗ (2314), ↑ (2695), ✓ (942, 2053, 2692, 1762), ▲▼ (2449, 2457), ■▢ (2981), ○ (2577).
- Pill chips in the hero; orange glow on `.pill:hover` (shared ui.css 793).
- `≈ +N` on a dozen buttons and rows; "· 10" count suffixes on most buttons.
- Receipt `rise` animation on first view (1004).

## H. Copy

- Em dashes: comment 1044 (a literal em dash before "answered"); the regex char class at 1378 holds a literal em dash and en dash (keep the behaviour, write them as \u2014 and \u2013 escapes).
- Practice vs practise mixed: "Practice anyway" 1205, "Practise anyway" 1261, "Practice again" 1413, "Practise the top 3" 1925, "practise" 888. Pick one.
- Stale: "the mistakes it opened are in Fix" (1013); there is no Fix page, the nav says Review.
- One card, three names: "Points on the table" (1871), "Where your points are" (1930), "Shows where your points are" (1872).
- Jargon: "Start the mentor's set" (1873, 2358): say "10 questions to start". "Now its twin" (1750): "Try its twin". "Sweep" row (1377).
- Explains the UI: 2684, 2695, 2435, the `SOON_WHAT` strings are fine as `?` pops.
- Target line forced to two lines with `<br>` so the sort fits (1893): one meta line, sort on its own row.
- "Couldn't load today. Your cards wait for this Retry." (714): "Couldn't load today." + Retry.

## I. Bugs

1. `function openDay` is declared twice in one scope (1850 QotD, 2493 calendar). The later wins (checked in node), so QotD past-day tiles (1826) and the Older picker (1833) open the calendar's Day details sheet; a past day's questions load only via `?day=`. Same commit (1a6fc8a9), pre-existing. Fix: rename 1850 to `openQDay`, update 1826, 1833. Risk low.
2. FOLD_SEL folds the Up next lead and its Start (C above). Page fix: `'data-nofold': ''` on the `.lead` in `leadItem` (1029) and `leadFrom` (1035). Also the page `.fold` rule (110-116) styles ui.js's `details.fold` (display flex, border-top, `.fold .meta` nowrap ellipsis clips metas inside): scope it to `button.fold`. Two fold systems on one page (page `fold()` 559 with `satf.fold.*` keys, ui.js `details.fold` with `satf.fold`). Risk low.
3. `TODAY_CARDS` (709) has `plan`; there is no `#plan` section and `card()` (589) has no null guard. When `/today` fails the forEach (713) throws at `plan`: exam, study and words keep their skeletons and Up next never gets its Retry. Fix: drop `plan` from the map. Risk low.
4. The calendar moved to `#cal` but the stretch rules still target `#study .cal-grid / .cal-d / .cal-head` (369-371). Today does not pass `look: 'plan'`, so the shared `--c: 40px` gives a 304px month left-aligned in a 643px card: the half-empty strip the 368 comment says is fixed. Fix: `#cal` selectors. Risk low.
5. Side column at 1100 to 1279 with the sidebar: inner 200px; Due row titles get about 70px. The 1080 breakpoint is viewport-based and ignores the 248 sidebar. Risk of fix: medium (P2).
6. `.gain-rows .skill-row` adds `border-bottom` (326) on top of the shared `border-top` (ui.css 2289): 2px dividers between gain rows.
7. QotD CSS 273-311 is overridden by 312-319; `.qd-lab` and `.qd-rowk` are built (1617, 1683) and hidden. With slot padding 0 (318) the absolute `.qd-fs` (285) sits over the first line of an R&W `.qd-text`.
8. `.gain-sort` sticky `top: calc(var(--bar) + 4px)` = 68 below 1080 (323): rail widths have no top bar, the phone bar is 56. A gap shows content above the stuck row.
9. `#mist .mlist` is a 300px inner scroller (227) that `balance()` shrinks to 160 (848), while folds already cap the list at 3 rows. Nested scroll in a side card.
10. Dead code: `paintPlan` is a no-op (2700), so `planSet`, `stripDays`, `weekDay`, `startDayTask`, `planNone`, `saveDraftThen`, `planPreview` (2701-2909, keep `showDay` 2801 and `calSheet` 654: live), `reasonText` (1266), the `targetSheet` draft branch; CSS `.reason` 166, `hr.sep` 85, `.tag.ink` 87/117, `.sp*` 257-266, `.cal-wrap` 374, `.wk-hd` 411, plan block 413-439, `.wk-day` phone rules 458-459.

## Redesign proposals (ranked)

1. Fix I1 to I4 (rename `openDay`, `data-nofold` + `button.fold`, drop `plan` from TODAY_CARDS, `#cal` selectors). Risk low, half an hour.
2. BIG: static two-column layout instead of `place()`/`balance()`/`ensure()` (775-852, CSS 33-59). HTML gets `<div class="td-main">` and `<aside class="td-side">` with the cards in place; below the breakpoint both are `display: contents` and the phone `order` list (now `phoneOrder` 780) moves to CSS `order`, so DOM order is the non-stretch phone order (on stretch days one card moves by `order` and tab order lags it; or do that one move in the DOM at paint time, no measuring). Breakpoint on width the main area actually has: 1280px with the sidebar (DIRECTION `.split`), 1080px in rail mode via `body.has-rail`. Aside 300px. Stretch and exam-day orders become `#today.stretch #exam { order: -1 }`. Honest trade-off: with seven side cards the aside is taller than 900, so sticky buys nothing unless side cards default to one-line summaries (Exam and Pace already fold their details; Score needs P6). Then `position: sticky; top: 16px` under `@media (min-height: 800px)`. Columns no longer end level (the user once asked for that, comment 33-35): main is longer by design. J/K (`cards()` 2996) sorts by rect, so it survives. Risk medium.
3. BIG: merge Up next and Due today into one main card "Today" (ids `#next` and `#due` kept as anchors; hero Plan chip links `#due`). Lead row with the one pill on top, then the due rows (ring, title, play, ⋯), the "N more due" and "N done" folds, then "Or a practice session" with the builder. A lead that equals a due row (`Plan · X`) shows once. `paintNext` already calls `paintDue` (996) and `patchTask` repaints through it. Due's "about N min left" goes in the card head. Risk medium.
4. Hero to a header row (907-953, 120-138): h1 at 22px (greeting text may stay, or "Today"), date as `.meta` on the same row, no eyebrow; chips move to the side Today panel at the 2-column width and stay as a compact row below it. Keep "Add your name" (919) as a quiet link and the at-risk line with its "1 question" button (926) as an always-on, `data-nofold` line. Brief facts: side "Since yesterday" list, one fold row on phone. Saves about 50px desktop, 150px phone. Risk low.
5. BIG: dissolve the Words card (2681-2697). With a Due Words row it already offers nothing; without one, a one-line side row: "Words · 12 due · ~5 min" + Start, `Done for today` state, "All words". Drop the QotD pointer line (the tabs name Words/Transitions). Zero loss: Start, done state, reason (as the row's (i)) and the link remain. Risk low.
6. Score card for a 300px column (2012-2097): band, target button, scale, gap line, Get a score / Add a score open; trend chart, verdict, per-week, calibration, causes, scores you added under one `fold('score.more')`; drift block stays open (it asks for a decision). Risk low.
7. Spacing per table B; `.td` bottom padding only under 760px. Risk low.
8. Type map: 44/48/38/40/34 figures -> 32/600 Geist tabular; 26/24/22/20/18 -> 16/600 (section) or 32 when it is the card's one number; 17/16/15 -> 14.5; 13.5/13 -> 12.5 meta; 12/11/10.5/10 -> 11.5 micro. `.sub` -> 12.5/600 sentence case `--soft`; drop the `.td .card .k` override. Mono stays on mm:ss and the countdown only. Risk low.
9. Controls: lead pill back to `.pill` (145 out); `.exam-trig` -> `.btn.sm` with an SVG chevron; `.clock-tog` -> `.btn.sm.icon` with `aria-pressed`, radius 8; hero chips radius 8; `.qd-tabs` -> `UI.seg`; glyphs out of labels (✎ -> "Edit" or pencil icon; ✓ -> word or check icon; ▲▼ -> "+4" / "-4" with colour + sign). Risk low.
10. Card-in-card: `.q1`, `.receipt`, `.figs > .fig`, `.wk-t`, `.tchip`, `.causes-fix`, `.slot-detail`, `.tcard` lose their fill; group with `--line` hairlines and 12px spacing. Orange hairlines (142, 169, 194) -> `--line`. Risk low.
11. Recent tests: latest sitting as today's `.tcard` content without the box; older ones as 44px rows (date, kind, band, Review, ⋯ with Fix / Twin / New one like this). "Show 6 more" stays. Risk low-medium.
12. Mistakes: remove the 300px scroller and the `balance()` resize; three rows + "N more" fold is the one cap. The `.mist-fig` 44px number goes to the 32px figure size. Risk low.
13. QotD: delete the dead two-column CSS and the hidden `.qd-lab`/`.qd-rowk` nodes (keep `refreshMarks` working on the tab mark only); move `.qd-fs` into the tab row's right end; past-day tiles 44 -> 36 on fine pointers (`--touch` 44 kept on coarse). Risk low.
14. Touch parity: the four title-only facts in C become (i) pops or fold rows. Risk low.
15. Delete dead code (I10), about 250 lines JS + 40 lines CSS. Grep before each removal; nothing reachable is lost. Risk low.
16. Copy list in H. Risk none.

Big changes for the user: 2 (static two-column layout, sticky summaries), 3 (Up next + Due today become one card), 5 (no Words card), 4 (greeting shrinks to a header row).

## Shared asks (ui.css / ui.js / kit.js)

- FOLD_SEL (ui.js 2794): `.lead` and `.lead-t` are too broad. Skip matches that contain a button, link or `.pill`, or narrow to `p.lead`. Also skip `[role=dialog]` popovers.
- kit.js 215: the `'eyebrow'` date style upper-cases in JS; make it sentence case with `.k`.
- `.reveal` primitive (DIRECTION 5) to replace `.drow` 208-211 and the cardfold reveal.
- `.k` sentence case; `.meta` off mono (ui.css 767); figures to Geist tabular.
- `.chips > button` 999px (ui.css 1067), `.badge` 999px (1192), `.skill-play` 50% (2301) -> 8px.
- `.cal-grid` fluid variant (`repeat(7, minmax(36px, 1fr))`, max 640) so pages do not override it by id.
- Hide `.side .nextup, .side .side-day` on `body[data-page="today"]` once the Now block shows from 700px tall.
- `.pill:hover` glow (ui.css 793): drop for the slop list.
- Nav Today meta counts questions while the page counts minutes: one unit.
