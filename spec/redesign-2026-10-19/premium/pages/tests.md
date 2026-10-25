# Premium audit: Tests (web/tests/**)

Files read in full: `web/tests/index.html`, `tests.js`, `start.js`, `talk.js`, `compare.js`; ui.css tokens and the
components used; ui.js `sections`, `nextBlock`, fold; passes/tests.md (rounds 1 and 2). No app code changed.
Lens rule: the brief fixes `.pill` 42/10, orange, Geist + Source Serif. So no fully rounded pills, no nested icon
circles, no font swap. Anything from DIRECTION 6 (gradients, glow, grain, load motion) is tagged "reopens D6".

## 1. First screen inventory

Assumed student: estimate at Mixed, target and exam set, plan set, no In progress, no cycle, twin available (9 kinds),
12 papers, 3 sittings, Up next = Full section. Basis: `.page` top 16; section bar 36 + 16 (ui.css:802-806) prepended
to main above the h1 (ui.js:2449); kind row = text line + reserved `.reveal` line + 8/8 padding, about 55px
(index.html:126,133); card pad 16; main column 728px, aside 300px (ui.css:329).

**1440x900** (y positions estimated from the CSS)

| Zone | Buttons | Links | Chips | Inputs | Boxes | Bars | Labels | Helper lines |
|---|---|---|---|---|---|---|---|---|
| Section bar y16-60 | 0 | 0 | 3 (New test 9, Papers 12, Your sittings 3) | 0 | 0 | 0 | 0 | 0 |
| h1 + hero y76-189 | 1 orange Start | 0 | 0 | 0 | 1 card | 0 | h1, h2, meta | 0 |
| New test y201-750 | 18 (9 Start, 9 text `⋯`), 1 orange `.pill.sm` | 1 "Which ones?" | 0 | 0 | 1 surface | 0 | h2, 9 h3, about 16 metas | 0 visible, **9 blank reserved lines** |
| Papers head y780-900 | Filters, Sort, fold summary | 0 | 0 | 0 | 3 preview wells (cut) | 3 tick meters (cut) | h2, count | 1 folded |
| Aside y76-900 | `?`, "Sit one more section", fold, seg x2, 4 cause actions | Target, Exam | badge "Mixed" | 0 | 1 surface, chart | chart bands | 2 h2, about 8 metas | goal line, "From your last 3" |
| Sidebar | about 17 (nav 9, search, Quick, Up next Start + chevron, user, Help, Feedback) | | | | Up next, Today | Today meter | | |

Totals: about 54 interactive targets, **3 orange fills** (sidebar Up next `.pill.sm` ui.js:1642, hero `.pill`
tests.js:251, recommended kind `.pill.sm` tests.js:457) plus the amber-ringed current chip (ui.css:816), 9 blank lines.
With 1 sitting in progress: +1 chip, +84px row with Resume, Hand in, Discard, and when Up next is `resume` the hero
and the In progress row show the same sitting twice (tests.js:215 and 295).

Rows of controls before content:
- 1440: section chips above the h1 (tests.js:923-934 via ui.js:2449).
- Papers: Filters + Sort, then the folded help toggle, then active-filter chips, before any tile (tests.js:513-517).
- Your sittings: Filters + Sort, then chips (tests.js:645-650).
- Aside What moves: the seg (tests.js:156); in Habits two more segs (tests.js:342-343): three control rows first.
- Start sheet: stepper, then "Start now" + 6 preset buttons, then 7-8 choice rows (start.js:274-298).

**390x844** (pbar 56 on top, tabs 64 below: content y56-780)
- Section chips row y72-116: 5 chips (adds Estimate, Habits, tests.js:930-933), 2-3 in view, scrolls sideways.
- h1 y132, estimate line under it (1 link, 12.5px soft, wraps, tests.js:111).
- Hero y193-311: h2, meta, 1 orange Start (left, index.html:317).
- New test y323-780: head h2 + 2-line meta + 1 link; 4 kind rows, each 2 lines + an always-shown tags line
  (`.reveal` is on for touch), Start + `⋯` each = 8 buttons.
- Counts: 9 buttons, 7 links (incl. 5 tabs), 5 chips, 2 boxes, 0 bars, about 20 labels, about 6 helper lines.

## 2. Clutter fixes

Hide behind one control:
- Kind tags and "what it is for" (tests.js:460) into the row's `⋯` menu head or a `UI.why` on the title: every kind row
  becomes one 40px line (title, facts soft, your result right, actions). Kills the 9 blank lines (about 135px).
- Papers help (tests.js:515, folds via `.ts-sub`) to a `UI.why` beside "Papers". Sort and Filters merge into one
  "Best for me" button whose popover holds the four filters (shared ask: filterBar `pop` + sort in one).
- "Sit one more section" / "Full section · 70 min" (tests.js:109-110) into the confidence `?` popover as its action.
- Skills worth the most (tests.js:196-199) behind a fold, remembered like the score fold (tests.js:145-147).

Defer until relevant:
- Section bar at 1100px+: `visibility: hidden` and no height until `.stuck`, as the chipless path already does
  (ui.js:2278-2281). Shared ask: `UI.sections(list, { until: 'stuck' })`. Phone keeps it.
- New test: show 4 rows (the recommended kind, Full section, Module 1, Trap test) and a quiet "5 more kinds" toggle,
  remembered. Rows past 4 keep J/K and Enter once open.
- Row Start and `⋯` as `.reveal` on fine pointers (ui.css:341-343), except the recommended row. Touch unchanged.
- What moves cause actions (tests.js:184) as `.reveal`; the row shows name, count, points.
- Start sheet step 1 (start.js:274-298): the recommended preset as one `.pill.sm` plus a quiet "More presets" that
  opens the other 5; the kind choices one column at size l (`.st-cards` 2-col, index.html:203): one calm list.
- In progress skips the sitting the hero carries (filter `u.session` in liveCard, tests.js:295); the hero takes its
  tick meter.

Merge: recommended row `.pill.sm` to `.btn.sm` with a 3px amber left tick and a "Next" badge (tests.js:457, 596), so main
has one orange fill. Shared: the sidebar Up next Start drops to `.btn.sm` when its item is the hero's test.
Shorten the New test head meta to a "14 of 61 types met" link (tests.js:430).

Space: `.ts-main` gap 12 to 24 under the hero (index.html:24); sections in `.ts-one` 16+16 to 24+24 (index.html:29);
the aside keeps 16.

Calm first screen, 1440 top to bottom: Tests h1 (no chip row) / the hero, elevated, with its shape and Start / 24px /
one flat surface: New test, 4 one-line rows, "5 more kinds" / Papers head with one control and a `?` / tiles.
Aside: band figure, goal line, chart, Best Target Exam, fold; hairline; What moves, top 3 causes. Visible targets in
main drop from about 26 to about 7.
Calm first screen, 390: pbar / chips / h1 with the band as a 16/600 figure and badge / hero, Start `.pill.wide`
(ui.css:864) / New test 4 one-line rows / "5 more kinds".

## 3. Depth and hero

Hero = the Next test card (round 1 made the estimate secondary; keep that). Now it is a plain `.card`
(ui.css:1203) with a 16px h2 and a meta line (tests.js:249), the same weight as the list surface under it.
- Surface: paper on the paper page, 1px `--line`, the page's only shadow: two warm layers
  `0 1px 2px rgba(63,50,30,.06), 0 12px 32px -16px rgba(63,50,30,.22)` plus `inset 0 1px 0 rgba(255,255,255,.7)`.
  Dark: black layers, highlight 4% white. A faint amber radial (5%) in the corner behind Start (reopens D6, low).
- Bigger figure: the title stays at the section step (16/600) so it never ties the 22px h1 (DIRECTION 0.2); the hero
  wins by surface, shadow and its figure: the test's shape as a `.lg` `UI.meter` ticks strip: section =
  M1 22 blocks with the route tick at 14, then M2; paper = expected M1 (reuse tests.js:569); resume = answered
  (reuse tests.js:306). Information, not decoration.
- Facts as one meta line, "44 questions · 70 min · 2 modules"; "Next test ·" prefix goes (the card says it).
- Start: `.pill` with `ICON.play` leading (ui.js:438), right-aligned, vertically centred on the title block.
- No overlap with the list (touch conflicts); the shadow carries the layering.
Elevation elsewhere: none. `.ts-one`, the aside and paper wells stay flat tiles with hairlines; tiles lift only on
hover (section 5). Sheets keep `--shadow-pop`; menus and `?` pops keep `--shadow-float`.

## 4. Buttons, controls, highlights

| Control | Now | Should feel |
|---|---|---|
| Hero `.pill` | hover 8% darker (ui.css:871), press scale .97 (873), focus ink outline (308) | inset top highlight + 1px darker bottom edge + small warm drop; hover lifts 1px, shadow grows; press translateY(1px) scale .98, shadow collapses, 120ms; focus `--ring` |
| Start loading | opacity .6 + "Building…" text swap, width jumps (ui.css:875, start.js:75) | full opacity, width locked, play icon to 16px spinner, label "Building"; success: check 150ms, then navigate |
| Row Start `.btn.sm` | well, hover 7% darker (ui.css:906), always shown x9 | revealed with the row; row hover wash (well at 50%, 8px radius, bleeds 8px) so the row reads as one target |
| `⋯` | text glyph (tests.js:421, 754) | svg "more"; open state keeps wash-2 + amber ring (ui.css:904) |
| Row focus (J/K) | 2px ink ring hugging the text, 6px radius (index.html:128, 163) | same wash as hover + `--ring` around 8px inner padding; no motion (keyboard) |
| Section chips | tile, current wash-2 + amber (ui.css:816) | unchanged, only shown when stuck |
| Filters | text button, no icon | `ICON.filter` (kit.js:180), active count as `.badge.n` |
| Filter chip | "×" via `::after` (index.html:156) | svg x 12px; hover darkens, x goes ink; removal scales .95 and fades 120ms |
| Compare tick | native box, accent ink (index.html:167) | 18px box, 6px corners, amber fill + ink-deep check when on, 120ms |
| Stepper | 4px bar flips colour (index.html:192-193) | bar fills by scaleX from the left, 200ms |
| Choice rows | wash-2 + amber inset + 600 (ui.css:365) | add a leading check that scales .8 to 1 in 160ms |
| Saves | note Save (tests.js:798), name Save (talk.js:251), Copy (tests.js:840, 855) hand-rolled | `UI.saving` (kit.js:907): Saving, Saved / Copied in place |
| Discard | quiet, confirm sheet, row slides out (index.html:111-113) | keep |

## 5. Motion moments

| Moment | Trigger | What moves | How |
|---|---|---|---|
| Arrival | first paint per session (sessionStorage flag), never the cached-to-fresh repaint (tests.js:970) | hero, then the band figure | opacity + 6px rise, 220ms `--ease`, aside 40ms later. Reopens D6/D7, low |
| Band changed since last seen | `estimate.latest.at` differs from a stored "seen" | band figure, newest chart point, move line | `UI.roll` (kit.js:1639) old to new; point scales .6 to 1; move line gets wash once |
| Start press | click | label to spinner | 2px blur crossfade 160ms; check 150ms; main view-transition (exists) |
| Start sheet step | Next, Back, stepper click (start.js:252) | pane | 12px slide from the travel side + fade, 200ms; Back reverses |
| Start sheet choice | any choice (start.js:262) | summary line | 120ms crossfade of the text |
| Filter change | tests.js:540, 670 | list, chips | list opacity out/in 120ms; chips in from scale .95 |
| Show all / more | tests.js:548, 676 | new rows | 4px rise + fade, 30ms stagger, cap 8 |
| "5 more kinds" | toggle | the 5 rows | same as Show all |
| Levers seg | tests.js:156-165 | panes | opacity crossfade 150ms (thumb slide exists) |
| Paper tile hover | fine pointer | preview well | -2px + `--shadow-float`, 160ms in, 120ms out |
| Discard | confirm | row out, counts roll | exists (index.html:113, tests.js:329) |
Reduced motion: the global rule (ui.css end) already flattens all of it to opacity or none.

## 6. Icons and imagery

- Unicode stand-ins: `⋯` (tests.js:421, 754; no "more" icon in ui.js:438 or kit.js:180, shared ask); `×`
  (index.html:156); `!` and `✓` in 50% circles (tests.js:358, index.html:83); `✓ ✕ –` (talk.js:156, compare.js:22),
  which should reuse the `UI.cell` state marks the miss chips use (tests.js:695); `→` in "Test → Fix → Prove"
  (tests.js:266) and "14 of 22 →" (tests.js:897).
- Icons present but unused here: `play` (hero Start), `filter`, `copy` (Copy buttons), `twin` (menu, tests.js:748),
  `fix` (tests.js:744).
- Kind rows have no mark while skill chips get `UI.glyph` (start.js:399). A 16px shape mark (one bar, two bars, fork,
  loop) only if it carries the module shape; med slop risk.
- How scoring works (tests.js:896-898): text boxes become a small inline SVG route diagram: M1, fork at 14 of 22,
  harder (to 800) in amber, easier (to 580) in ink. The page's one spot illustration, and it explains.
- Empty states: "No estimate yet" (tests.js:97), "Nothing sat yet" (661), "Sit a full section…" (172): dimmed samples via
  `UI.empty` (kit.js:2439, `.empty-sample` ui.css:1357): a ghost band chart, a ghost sitting row, ghost cause rows.
  "Not rated for you yet" (tests.js:570): an empty 22-block meter with its route tick, dimmed.

## 7. Delight and feedback

- First estimate: the ghost chart resolves into the real one (240ms crossfade) on the first visit after it exists.
- Target inside the band: the goal line becomes "At your 650 target" with a check, the chart's target line goes amber, once.
- Confidence steps up (Rough to Mixed to Consistent): the badge settles from scale .96 once; its `?` says what changed.
- Test, fix, prove: a step bar fills amber by scaleX when it completes; "Proved n" ticks fill in order (20ms each) when n rose.
- Route-up trainer: "Best streak 3" as 3 amber pips (`UI.pips`) on its row.
- Sittings: "Route line +2" badge gets the wash when the sitting routed up (tests.js:718).
- Race made and link copied (tests.js:479, 836): "Copied" with a check in place, not only a toast.

## 8. Ranked top 10

1. Hero Next test: paper surface, the only shadow, shape tick strip as its figure, play Start. Focal point. M, low.
2. One-line kind rows: tags and help into `⋯`/`?`, no blank reserved line. Removes 9 gaps. S, low.
3. New test shows 4 rows + "5 more kinds"; row Starts reveal on hover/focus, recommended stays. Calm list. M, low.
4. Section bar only when stuck at 1100+, and In progress skips the hero's sitting. Nothing repeats the task. S, low.
5. One orange fill in main: recommended row to `.btn.sm` + amber tick; sidebar Start quiet when it is the hero's test. S, low.
6. Tactile `.pill` with honest loading: width lock, spinner, check before navigate. Feels physical. M, low.
7. Calm heads: Papers one control + `?`, "Sit one more" into the confidence `?`, cause actions reveal, skills folded. M, low.
8. Band changed since last seen: roll, newest point, wash on the move line, once. Earned delight. M, med.
9. Start sheet motion: directional pane slide, stepper fill, summary crossfade. Feels guided. M, med.
10. Icon and empty-state pass: svg more, x, check, alert, filter, copy; route diagram; ghost samples. M, med.
