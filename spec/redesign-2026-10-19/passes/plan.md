# Pass: Plan (web/plan/**, web/assets/plan-ui.js)

Files: web/plan/index.html (page CSS rewritten, 490 lines from 542), plan.js, progress.js, wizard.js,
web/assets/plan-ui.js. Checks: `node --check` on the four JS files and the inline script, `python3 tools/check-ui.py`
(ok), no em dash in any touched file, every removed selector grepped across web/ (no outside use; tour.js hooks
`.pl-hero`, `.pl-how`, `.pl-tiles`, `.pl-tabbar`, `.pl-day-go` and ui.js's `.wz-note` all kept).

## First screen

Measured chains assume the lead's `.page` top of 16 (today's clamp gives 27 at 900 tall: add 11).

**Plan view, 1440x900.** Leads with the Day card and its orange Start. Chain: page 16 + title row 38 (h1, tabs,
Edit, menu on one row) + settings line 24 + panel gap 12 + card pad 16 + day head 34 + 12 = **Start at ~152px**
(was ~411; ~603 with two banners). One banner adds ~72 (only one ever shows). Moved out of the way: the four tiles
are now one status card at the top of the sticky right column (Days to exam, Score, Plan done, This week), then
Coming up, Phases, Map, Habits, Sweep beside the Day and Calendar cards; the tab bar sits on the title row; banners
past the first fold behind "N more".
**Plan view, 390x844.** Leads with the name, the settings line, the sticky tabs, then the Day card. Chain: bar 56 +
16 + name row 44 + settings 20 + tabs 52 + 12 + pad 12 + day head (two lines) 68 + 12 = **Start at ~292px** (was
~458, below the fold with two banners). The status block sits under the Day card as a 2x2 card; the side cards
follow the calendar.

**Landing, 1440x900.** Leads with "Study plan" and its one pill on the same row (Continue with a draft, else Use
this plan, else Create my plan) at the top of the page. Main: "Your plan, ready" (settings line, month and Day 1
side by side) or "A day in your plan"; then Your plans. Aside: Your numbers or the mini tiles, and How it works as
one folded line. Gone: the wash hero, the kicker, the 44px slogan, three numbered cards, the mono bank line.
**Landing, 390x844.** Title and pill on top, the preview card, then the aside content below.

**Wizard, 1440x900.** Leads with the step under a slim 4-part stepper (number and name, a 2px bar: amber current,
ink done); Next is the pill in the sticky foot. The Glance is a card in the sticky right column (top 16, was 88).
Gone: "1 / 4", "Your draft saves as you go." (the foot says "Draft saved" or "Can't save right now"), the step
intros. **390x844:** stepper numbers only, step, Glance under it, foot above the tabs.

**Progress tab.** Main: Score path, What your time bought, Ready on every skill, Domains, All 19 skills (folded,
remembered), Study time, Checks, Weeks. Aside: Since (as rows), Checkpoint, Why you lose points, Pace, Planned time
by task. The 2-column holes are gone.

**Test-day sheet (?print=sheet):** unchanged layout (traps, What to bring sticky beside); badges and h1 on the shared
scale; no folding (shared FOLD_OFF covers `?print=`).

## Big changes

- Plan view: the four stat tiles became one status card in a right column; the Day card and Start come first.
- The Plan, Progress, Plans tabs sit on the title row (sticky under the bar on a phone only; on a laptop the tab
  row now scrolls away with the title).
- Banners show one at a time, most urgent first (missed, behind, drift, Map done, registration, built, server);
  "N more" opens the rest. Banner buttons are ink, so Start stays the page's only orange.
- The plan's settings ("5 days · 45 min · module weekly · Focus Algebra") are a visible line under the name (they
  were a hover tooltip).
- Landing rebuilt as a page: title plus one pill, the plan preview, the side facts; the orange hero and the three
  How it works cards are gone, their text kept in one folded paragraph.
- Wizard: the live plan is a right-column card from 1280px; the stepper has no circles; step intros removed
  (step 4's meaning is now its (i)); "Study"/"Rest" in sentence case.
- Progress tab has a side column; the long skills table folds and remembers.
- Plans list: Edit or Open shows; Make active, Duplicate, Remove appear on hover or focus (always on touch).
- Task rows are 10px tighter; a row's detail line (its skills or mistakes) shows on every row on a touch screen and
  on the focused row with keys (J/K), not only on the next task.
- Changed days (L15) are marked again, now as a dot on the month; the week's goals and theme are a line under the
  week head again.

## Bugs fixed

- Fold dead on /plan/: `aria-live="off"` removed from #plan. Notes the student acts on (`.wz-note`, the "Very
  ambitious" date help, the focus limits) carry `data-nofold`; banner headlines too.
- `/plan/#today` and `/plan/#week` land: ids `today` (Day card) and `week` (Calendar card, its head is the week);
  after the first draw, and on `hashchange`, the page switches to the Plan tab, picks today and scrolls there.
- Changed-day dot (L15): drawn. `markWeek()` marks calendar cells the plan changed (unopened) with `data-chg`, a
  6px ink dot, and ", changed by the plan" in the cell's label; opening the day clears it. Week theme drawn as a
  `.help` (folds when long). The dot sits after the date number, clear of the phase name, your-own mark, minutes and
  task count. Dead code removed: `changeLog()`, the `.pl-wd` branch of `markTargets`, `.pl-week`,
  `.pl-wd*`, `.pl-wdn`, `.pl-print-months`, `.wz-range`, `.pl-have .chips`, `.pl-log`, the duplicate missed-dot,
  duplicate `.wz-dates` and `.pl-big small`.
- "Review week" (needs `UI.weekReview`, defined nowhere): dead branch removed (see For the user).
- Sticky offsets: phone tab bar at `calc(56px + safe-area)` (was `--bar` 64, an 8px slit), and the head steps
  aside (`display: contents`) so the tabs stick for the whole view; Glance at 16 (was 88); phone thumb Start at 64
  over the tabs (was 68); `scroll-margin-top` 0 desktop / 44 phone; `revealDay()` uses the tab bar only when it is
  sticky.
- Hover-only text now reachable on touch: tile sub-lines (visible in the status card), plan settings (visible
  line), Coming up skills (in the row), phase purposes (third line), a row's detail (`.trow-detail` shows on coarse
  pointers and on a focused row), Map squares ("Not measured yet: ..." line), Checkpoint squares ("Slipped: ...,
  Still missed: ..." line).
- leversPop buttons over 48px: now a `UI.menu`, each lever with its fit as the sub line. The pace the target needs
  ("Making +8 a week · needs +12") is a visible line in the Score row; What changes it shows only when there are
  levers, so the menu is never empty.
- Progress observers: the score chart's MutationObserver and the stack bar's ResizeObserver are disconnected on
  each redraw (were added per draw).
- Em dashes as missing values: progress.js `pct`, wizard week strip: en dash.

## Not done

- Desktop `scroll-margin`: cards scrolled into view land 72px down because `html { scroll-padding-top }` is
  `--bar` + 8 (shared; see asks). Not patched locally with a negative margin.
- `.wz-wd select` stays 12.5px (under the 16px iOS floor): "1 h 30 min" at 16px does not fit a 7-column day tile.
- In-cell glyphs keep their fixed-box sizes (map and checkpoint squares 9px, calendar task count 10.5px, drop tag
  9px), per DIRECTION's out-of-scale list.
- ▾/▴ text on dropdown labels ("Today I have 45 min ▾", the wizard's More options and Later dates, a domain's
  skills toggle): kept as the only dropdown cue; a shared chevron would replace them (ask).
- `.pl-i` (the (i) info button, plan-ui.js) stays a 20px circle: it is shared by every plan page and reads as a
  mark; the lead's 50% rule may want a square.
- Inline `style` grids inside popovers and sheets (numberPop, ownForm, scoreSheet, shareSheet) left as they are.
- Your plans on the landing sits in main, not the aside the audit named: its rows hold up to four buttons and need
  the width.
- PROGRESS.md's "Custom amount" per-day minutes option: deferred by the user.

## Shared asks

- `ui.css` `html { scroll-padding-top: calc(var(--bar) + 8px) }`: 72px on desktop where no top bar exists; 16px
  from 760px wide would let `#today`, `#week` and `revealDay()` land at the top.
- `.twocol-side` with a sticky footer: a `--twocol-bottom` (default 16px) used in its `max-height`. The wizard
  overrides `.wz .twocol-side { max-height: calc(100vh - 16px - 88px) }` locally so the Glance clears the foot.
- `.tablist` inside a title row: the plan head draws a full-width hairline (`.pl-head::before`) that coincides with
  the tablist's inset line; a `.tablist.inline` (no own line) would make that explicit.
- `.badge`: 6px corners as queued. Orange-tint `.badge` now carries Active, Focus, Ahead, Passed; an amber-fill
  word badge only if the user wants those louder.
- A dropdown chevron for `.btn[aria-haspopup="menu"]` (replaces the ▾ text in plan and elsewhere).
- Plan no longer calls `UI.date(..., 'eyebrow')`.

## For the user

- `UI.weekPlanner` (plan-ui.js, "shape next week": busy/short days, a focus swap) has no host anywhere, and the
  "Review week" button that would open it needed a `UI.weekReview` that was never written. The server has
  `PUT /api/plan/{id}/week/{monday}` (it ignores the swap). Build the sheet, or delete weekPlanner?
- The tab bar is no longer sticky on a laptop (it sits on the title row); keys 1, 2, 3 still switch tabs.
- Between 1080 and 1279px the wizard's Glance and the plan's side cards now sit under the main column (the shared
  right column starts at 1280).
- On a phone the four status figures are a 2x2 card under the Day card, no longer a swipe strip above it.

## Polish round

Files: web/plan/index.html (page CSS), plan.js, progress.js, wizard.js, web/assets/plan-ui.js. Checks: `python3 tools/check-ui.py`
(ok), `node --check` on the four JS files and the inline script (ok), no em dash in any touched file, `.pl-i` grepped across web/
(no use left), official smoke `plan/` at 1440 and 390 (no errors, as before). The official smoke only reaches the landing, so a
copy with an active-plan fixture and query strings also ran `plan/`, `?tab=progress`, `?setup=1&step=3`, `step=4`, `?print=sheet`
and `?view=` at both widths (no errors before or after), and drove the slider row (value, aria-valuetext, Glance update, focus
kept across the redraw) and a week row (it opens that week and the mark follows).

### First screen

**Plan view, 1440 and 390.** Still leads with the Day card and its one orange Start. What changed in the look: the status card's
units sit at 12.5 `--soft` beside their 28 figure ("1h 20m of 3h 45m", "560 → 650"); This week's minutes are a tick meter, one
block per study day, with each day's mark under it; the calendar card's week head counts tasks as blocks (one a task) and says
its dates once ("Week 4 of 7 · Oct 19–25"); the Phases card is now a tree: each phase a group (name, dates, what it does, a
chevron), its weeks nested under a 1px guide line with a right-aligned count (tasks done of planned for past weeks and this one,
planned time ahead). The week on show carries the amber mark on the guide and moves with the calendar; a week row opens that
week. The amber bar on the current phase went (one amber mark in the card; "now" stays in its date line). The (i) circles are
the shared `?`. On a phone the week rows are 44px.
**Wizard, step 3.** "A study day" is one slider row: the label left and the value right inside a 44px track, the part up to the
value a step darker (greyscale; Next stays the one orange). It replaces a label over nine chips that wrapped to two lines. The
per-day dropdowns and their options are as they were.
**Wizard, step 4.** Normal's grey ring rides the sliding thumb (no amber at its corners, no ring on the button during the slide);
the `?` replaces (i); a domain's skills hang from a 1px guide line (was 2px), the same pattern as the plan's weeks.
**Progress tab.** `?` in Score path and Ready on every skill; week ranges said once ("Oct 12–18").
**Landing.** Unchanged apart from the `?` in Your plans.

### New components added

- `UI.meter({ticks})`: This week (blocks = study days this week; was a 4px bar) and the calendar week head's Tasks (blocks =
  tasks planned, at most 40; was a bar). `.meter-n` text and the aria values are the meter's own.
- Slider row (bencho), local: `.wz-slide` in plan/index.html and `slideRow()` in wizard.js, on step 3's minutes a study day. The
  native range lies over the row, invisible, and steps through the same nine values by index (a plan's own value off the list
  joins it), so drag, arrows, Home/End and `aria-valuetext` ("1 h 30 min") work as on any range; the value is set on change. A
  touch tap anywhere on the row sets the step under the finger (iOS moves a range only from its thumb); the invisible 24px thumb
  sits where the fill ends, so a drag from the edge catches it.
- Nested week rows with a 1px guide line (aceternity nav): the Phases card (`details.pl-ph`, `summary.pl-ph-s`, `.pl-wks`,
  `.pl-wkr`). The phase of the week on show opens by default; a toggle is kept for the session.
- `UI.why`: the eight plan `?` marks (Map days, Edit and Save as new, the score path, the coverage grid, step 4's Focus, Normal and
  Strong, each R&W domain, each extra, every `fieldTip`). A tap opens it on touch, as before.

### Removed local copies

- `UI.infoTip`'s own button and the `.pl-i` CSS (a 20px round (i), plan-ui.js). `UI.infoTip` stays as a one-line wrapper over
  `UI.why` ('About X' becomes about 'X'); no caller uses it now.
- Step 3's nine-chip minutes control (the `UI.chips` call), replaced by the slider row.

### Not done

- `UI.weekPlanner` untouched (the user has not decided). "Time you have" per-day dropdown options untouched (Custom amount later).
- The other minutes pickers (the Built banner's "45 min × Mon–Fri" pop, the day menu's "Change today's time…" pop, "Today I have"
  menu) stay chips or a menu: in a popover one tap applies and closes, a slider would apply on its first key press.
- The Day card's meter stays a minutes bar: its label counts tasks and its bar minutes, and ticking it would change what it measures.
- This week keeps its day marks under the ticks: a tick meter lights a count from the left, so it cannot say which day was
  missed, partly done or today (see Shared asks).
- Score sliders (Math, target, R&W) stay `UI.scoreSlider` (shared, with the typed field and the average and your-tests marks).
- INSPO's "test date distance" slider is not in this page's lines; the date rows stay.
- ▾ / ▴ text cues stay until a shared dropdown chevron exists.

### Shared asks

- A shared slider row (`.slide-row` + `UI.slideRow(host, {label, options, value, format, onChange})`) if another page wants one;
  plan's `.wz-slide` and `slideRow()` are ready to lift into ui.css and kit.js.
- `.why-q` brings a 4px left margin; inside a flex label with a gap (`.wz-lab`, `.pl-hmeta`, gap 8) it sits 12px off its text.
  A zero margin when its parent is flex would make it even everywhere.
- `UI.meter` ticks with a state per tick (done, partial, missed, today) would let This week be one row instead of ticks plus marks.

### For the user

- The plan's Phases card lists the plan's weeks under each phase; click a week to open it. The orange mark moved from the current
  phase to the week on show.
- In the plan builder, "A study day" is a slider (the same nine amounts, 15 min to 4 h).

## Premium build (part 1)

Files: web/plan/index.html (page CSS), plan.js, wizard.js, progress.js, web/assets/plan-ui.js. Checks: `python3 tools/check-ui.py`
(ok), `node --check` on the four JS files and the inline script (ok), `smoke/weekplanner.js` (4 checks passed, after the rewrite
and at the end), no em dash in any touched file, removed selectors grepped across web/ (`.pl-flash`, the `.cal-tk` bar rules, the
`.wplan-c select` rule, `.trow-more` colour rules, `.wz-gain .big`, `.trow[data-led]::before`: no outside use; `data-led` is still
set, unstyled). Official smoke and inventory on `plan` (the landing) at 1440 and 390: no errors, inventory identical. The official
fixture has no active plan, so a scratch copy fed a real GET /api/plan (a mid-plan Monday: 4 tasks, 19 days in the month), its
preview and /api/map, and ran the plan view, `?tab=progress`, `?tab=plans`, wizard steps 1 to 4 and `?print=sheet` at both widths
(no errors before or after), plus a driven pass: both tile popovers, the levers menu from the Score popover, the minutes menu, the
calendar key, picking a day, the Shape sheet with a Busy press (no errors).

### First screen (plan view, 1440, that fixture; "visible" leaves out what shows only on row hover or focus)

| | Before | After |
|---|---|---|
| Day card | 14 buttons (Start and "Today I have ▾" on one row, 4 ⋯ squares), 1 tag badge | 8 (Start alone; the minutes in the facts line open the same menu; the next row's ⋯ only, the other rows' actions on hover), 0 badges |
| Calendar card | 5 buttons (week ‹ ›, month ‹ ›, Shape), 19 boxed days, a task bar and "2/3" in every past day, Tasks ticks, 10-item legend | 4 (Shape, week ‹ ›, the key's ?); the week on show is a soft band, other days a number and mark; no Tasks ticks on this week |
| Status card | 4 taps + Set/links, 3 to 8 lines | 3 taps + 1 link, each tile a figure and one line (This week keeps its ticks and day marks) |
| Side | 5 to 7 cards (Coming up, Phases, Map, Habits, Sweep) | Coming up on the page, Phases, one "This phase" card |
| Phone rows of controls before the first task | 5 (6 with a banner) | 4 (5) |

**Wizard, 1440.** Step 2: 11 buttons and 7 quick chips in the step become 7 and 3; the Glance showed the month, Week 1, Day 1 and
8 rows at once, now the month, Week 1 or Day 1 (a seg), the 3 rows step 2 changes (Exam, Pace, Phases) and "All settings (N)"
folded. Step 3: five per-day selects and five record lines go behind "Different times on some days". Step 4: Math and R&W (about
40 controls) become one section at a time; Where your points are shows 3 of 6.

### Hero

- Plan view: the Day card is `.card.hero` (shadow 3 on the warm wash); everything else stays a plain card. No amber top edge: the
  wash marks "now" and Start stays the one orange.
- Landing: "Your plan, ready" (or "A day in your plan") is the hero.
- Wizard: the Glance is `.card.hero`; step 2's figure is `.hero-num` ("560 → 650", the target in amber-deep, the gain badge
  beside), on a white raised box.

### What moved behind which control

- "Today I have 45 min ▾" (a row of its own) is the minutes word in the day's facts line ("Practice · Build · 45 min"), same menu.
  A rest day keeps "Practice anyway" as its one button. Start reads "Start · 40 min" or "Resume · 25 min left".
- Task rows: the kind is the meta line's first word ("Check · 4 questions · 6 min"; one-line compact rows keep the badge); a row
  that isn't next shows its Start, Review, Undo and ⋯ on hover or focus (`.reveal`, always on touch); the ⋯ are ghost `.ibtn`s
  (row, day and plan menus).
- Score tile: At this pace, Making/needs, the R&W line, Take this week's test and What changes it are in a popover the tile
  opens (aria-haspopup=dialog, a small chevron after its label); What changes it opens the levers menu by the tile.
- Days to exam tile: tests left and "Fits with N h to spare" in its popover, with "Show the calendar" (the old tap); with nothing
  to add the tile still taps to the calendar. Short of time (with Set) and Not booked stay on the tile. The moved lines print
  (`.print-only`).
- Plan done: "8 of 35 study days" as the figure (counts over percentages); the percentage is in its label.
- Calendar: the month's ‹ ›, Today and legend are hidden in the plan view (the week nav, This week and PageUp/PageDown cover them);
  the key opens from a ? beside the month's title, listing only this month's marks. The per-day task bar and count are gone
  (the day's mark, its label and its card say them).
- Map, Your habits and Sweep: one "This phase" card, a group each, only those that apply.
- Wizard: see First screen; the per-day minutes stay open while any day has its own time; a refused R&W setting switches step 4
  to Reading and Writing.
- Shape sheet: each day's minutes select, Busy and Short became one seg [Busy · 15 min · its minutes −15, ±0, +15] (same values;
  a day under 15 min is no longer offered); a one-line key under the title; seven bars with the week's total, "7h 30m → 6h" as you
  change it. `weekplanner.js` passes unchanged.
- Progress: Study time per day with nothing logged shows a dimmed sample week (aria-hidden, inert) above "Nothing logged yet".

### Motion and feedback

- Picking a day: the Day card's content fades in over 160 ms (off under reduced motion) instead of the 1.1 s amber blink.
- Banners rise once per view; a redraw after a change keeps a shown banner still.
- Pulled into part 2: the 8px slide in the time direction, the tick chain, wizard step slides, the Shape bars' morph and rolling
  total, Save via UI.saving.

### A1 follow-ups (the lead's message)

Sticky bars (phone tabs, the thumb Start, the wizard foot) on `--page`; the wizard's notes, choice cards, dates, day tiles, own
tasks and gain box on `--raised` (notes and forms `--edge`, the tappable ones `--shadow-1`, `--shadow-2` on hover, picked =
`--sel-bg` + `--sel-edge`); Glance week tiles, the trap sheet's choices and the week band in `--well`. Side stripes removed: the
led task row's amber bar, the Phases week-on-show stripe (now wash and 600) and the trap sheet answer's stripe. Focus: `.pl-tap`
and the slider row use the amber-deep ring. Gaps: panel and `.pl-sec` 24 under the title, landing mini tiles 16, the test-day
sheet's columns `--card-gap`; the grids already use `--card-gap`.

### Icons changed

None yet (part 2). The two new triggers use a CSS chevron (`.pl-have::after`, tile labels) rather than ▾.

### Bugs fixed

- 9: banners replayed their entry on every redraw (now once per key per view); picking a day blinked 1.1 s (now a 160 ms fade).
- Found on the way: the week-on-show ring overrode the picked day's amber ring and today's 2px ring (same specificity, page CSS
  later); the new rules leave both to ui.css.

### Inventory diff, accounted

- Plan, Progress and Plans tabs: "Start today · 4 tasks · 89 min" is "Start · 89 min"; "Today I have 90 min ▾" is "Today I have
  90 min: change" (the facts-line trigger); "47 days to the SAT; show the calendar" is "…: details" (its popover holds Show the
  calendar); "Take this week's test" and "What changes it" are in the Score popover ("Score 520 to 700: details"); new "About the
  calendar's marks". Ids: only generated meter ids (`kclip*`, `kmk*`) shift; `chh1` is the sample chart's.
- Progress tab (nothing logged): the sample week's bars appear as buttons in the inventory; they are inert and aria-hidden.
- Wizard step 2: quick chips +150, +200, 750, 800 gone (+50, +100 and the next round score stay; the slider and its number field
  set any value). Steps 1 to 4: new Week 1 / Day 1 seg. Step 3: the five "X minutes" selects are behind "Different times on some
  days". Step 4: the four R&W "About …" marks and their segs are behind the Reading and Writing seg; points rows 4 to 6 behind
  "3 more".
- The Shape sheet is not in the inventory: its 3 controls per day became one seg with the same values (above).

### Not done

- Icons, drawn marks (✓ ○ – goals, map, sweep, checkpoint), kind glyphs, spot drawings: part 2.
- Shared controls (drawn task checkbox, busy and done states, UI.saving in the Shape sheet), motion moments: part 2.
- Banner amber left rule (§4): left out, a side stripe above the orange Start.
- Sticky bars with blur (§3): BUILD rule 5 allows blur only under sheets and the phone tabs; scroll shadows wait for `.scrolled`.
- Progress tab hero: none; it has no one number (Score path could take `.hero` if wanted).
- The Glance's Score row still shows on step 1 (the audit hid it on 1 and 2): step 1 has no other place that shows the target and
  the gain. Hidden on step 2, where the hero figure says it.
- This week keeps ticks, day marks and the streak line: ticks with a state each are still a shared ask.

### Shared asks

- `UI.calendar({ nav: false, legend: 'why' })` (or similar), and a way to skip `.cal-tk`: the plan hides the month nav, the
  legend and the task bar with CSS today.
- A shared dropdown chevron for text triggers (the plan's local `.pl-have::after`).
- `UI.meter` ticks with a state per tick (repeat).

### For the user

- The day's minutes ("45 min" in its line) are the old "Today I have" menu; Start stands alone.
- Tap Days to exam or Score in the status card for the rest (tests left, whether it fits, the pace, R&W, What changes it).
- The calendar has one set of arrows (the week's) and a ? for its key; only the week on show, today, the day picked, test days,
  days off and the SAT are boxed.
- In the plan builder the live plan shows what this step changes; everything else is under "All settings".
- Shape this week: one choice per day (Busy, 15 min, or its time 15 less or more) and the week's bars with its total.

## Premium build (part 2)

Files: web/plan/index.html, plan.js, wizard.js, web/assets/plan-ui.js (progress.js untouched in part 2). Checks: `tools/check-ui.py`
ok, `node --check` on the four JS files and the inline script ok, `smoke/weekplanner.js` 4 of 4 (after the planner change and at
the end), no em dash in any touched file. Official smoke and inventory on the landing at 1440 and 390: no errors, inventory
identical. The active-plan harness (a real GET /api/plan; its fixture now applies a task PATCH so the reload agrees) at both
widths for the plan view, Progress, Plans, wizard steps 1 to 4 and the test-day sheet: no errors. Driven: ticking all four of
today's tasks through "Did it elsewhere?" (1 done, 2, 3, 4 done; the last starts the ring; the reload after it keeps "4 done" and
"Day done"), both tile popovers, the levers menu, the key, a day pick, the Shape sheet's Busy (total "7h 30m → 6h"), wizard Next
three times (the stepper's `--i` 1, 2, 3; the Glance rows per step), the Week 1 / Day 1 seg, step 4's Reading and Writing.

### Shared pieces adopted

- Ghost `.ibtn` menus (part 1) now draw `UI.icon('more')`; the week stepper is `.ibtn` with `caret_left` / `caret_right`.
- Start: A1's busy spinner (aria-busy, unchanged call) and, on a mouse, its `Shift+Enter` keycap (`.pill .kbd`).
- Shape sheet Save: `UI.saving` in the sheet's own button (Saving, Saved with the drawn check, the sheet closes 600 ms later); the
  "Week saved" toast is gone.
- Task checkbox: the ring turns ink on hover, the fill eases (160 ms); the check draws on a tick (`UI.fx.check`). The round
  28px box stays (a task, not a form checkbox).
- Wizard cards (starting score, SAT dates): a press sinks them (.98), a picked one shows a check in its corner (amber-deep, not
  colour alone); day tiles press .97; the foot shows its shadow only while the step slides under it (`data-scrolled="bottom"`).
- Hover bands (`--hover`) on Coming up rows and the status tiles (a press darkens 6%); Phases week rows have theirs from part 1.
- Spot drawings (`UI.spotArt('start')`) on the two first-use empties: no plans yet, no traps yet. None in sheets or popovers.

### Motion and feedback

- Page entry (`data-m="stagger"`, once per visit): the plan view's main column (the Day card holds Start: `data-m-now`) and side
  cards; the landing (its header holds the pill); the wizard (its foot holds Next). Later redraws are marked `data-m-done`.
- A tick: the check draws in place, then the row tucks into "N done" (`UI.glide`: the row fades where it stood, the rest close
  the gap), the count rolls (`UI.roll`), the first one's fold rises in; the last one sweeps a ring shut beside "Day done" and
  draws its check (`UI.fx.ring`, `UI.fx.check`). The reload that follows waits for that (at most 1 s), then the status figures
  that moved roll: Plan done, This week's minutes, the streak line. The day's meter is kept while the day is on show, so it
  sweeps (`UI.meter().set`). Undo brings the row back the same way.
- Picking a day: the Day card's content comes in from the side time moves to (8px, 200 ms; by key a fade only); the calendar's
  picked day, today and week band ease between days (160 ms).
- A plan just made (the wizard and the one-tap proposal, one function): the Day card rises, the month's weeks fade in 30 ms apart.
- Shape sheet: the seven bars keep their elements and change height (200 ms) as a day changes; the total rolls.
- Wizard: a step comes in from its side (12px, 200 ms; by key at once); one amber bar slides along the stepper to the step; a
  Glance row the last change touched washes once (600 ms).
- Everything respects reduced motion (kit's `UI.motion.off`, `html[data-motion="reduce"]`, the media query).

### Icons changed

plan-ui.js: CHECK, GRIP, DOTS copies gone (`check`, `grip`, `more`); the swap arrow `arrow`. plan.js: DOTS and X gone (`more`,
`x`); week ‹ › to `caret_left` / `caret_right`; the minutes trigger, Practice anyway, the tile labels with details and the "N
done" fold carry `caret_down` (turned while open); "+ …" quick chips to `plus`; "College Board ↗" to the label plus `arrow` turned
up-right; the week goals ✓ ○ – are drawn marks (dot, ring, dash). wizard.js: the stepper ✓ to `check`, ▾ ▴ on the domain toggles
and the Later dates, More options, Extras and All settings summaries to `caret_down`, × to `x`, "↑ Focus" to `up` + "Focus", "+ …"
chips to `plus`. Task rows: a 16px kind mark before the title (warm-up `again`, mistakes `fix`, learn `learn`, check `twin`, habit
`trap`, pace `clock`, map `grid`, focus `bolt`, test `tests`, sweep `clean`, words `words`, extras `plus`, your own `pen`, R&W
`book`); one-line rows lost their tag badge (the word is read to screen readers), other rows keep the word in their meta line where
the title doesn't say it. Kept as text: ✓ ✕ ✗ in the 9px map, sweep and checkpoint squares (Marks draws them), → in sentences. No
filled twins: Plan has no icon toggles.

### Inventory diff, accounted (part 2 vs end of part 1)

- Start's name now includes its keycap text in the inventory ("Start · 89 minShift+Enter"; the keycap is aria-hidden, so its
  accessible name is unchanged).
- Wizard step 4: "+ …" chips lost the "+" text (now a plus icon); the domain toggles lost "▾" ("5 skills").
- Nothing removed. The done rows are in "N done" (a `details`, closed until opened, kept open for the view once opened); J/K walk
  the rows that show.

### Not done

- The 9px ✓ ✕ marks in squares stay text (Marks draws them).
- The phone tab bar's scroll shadow: it sticks right under the top bar, whose own shadow would sit between them.
- Drop-target pulse after a drag and the changed-day dot pulse after a Shape save: small, left out.
- Skeleton-to-content crossfade: the page entry covers a fresh visit; the skeleton still swaps.

### Shared asks

- `UI.calendar({ nav: false, legend: 'why', marks: false })`: the plan still hides the month nav, the legend and the task bar
  with CSS (and draws its own `?` key).
- `UI.meter({ticks})` with a state per tick (done, today, missed): This week still pairs ticks with its day marks.
- An external-link icon (`arrow_up_right`): College Board's link turns `arrow` by CSS.
- `UI.motion.enter(el, 'slide', {dx})`: the day change and the wizard step use their own 8px / 12px keyframes.

### For the user

- Ticking a task draws its check and tucks it under "N done"; finishing the day closes a ring by "Day done".
- Picking a day slides it in from that side; the Shape sheet's bars move as you change a day; Save says Saved in the button.
- Task rows show a small mark for their kind; the wizard's picked cards show a check.

## Visual review

Shots: `premium/shots/app-review/plan-r0-*` (before), `plan-r1-*`, `plan-r2-*`, `plan-r3-*` (after), 1440 light and dark and 390, from
a headless Chromium against the DB copy: learner `a:s790a6684c9aed61f5` (active plan, a missed week behind it) for the plan view,
a fresh learner for the landing and the builder. States: Shape sheet (open, a Busy press), Score popover, minutes menu, row hover,
Tab focus, a day picked, a tick ("Did it elsewhere?"), the calendar key, Progress, Plans, builder steps 1 to 4 (step 3 also with
"Different times on some days" open, and a key's focus ring). Files: web/plan/index.html, plan.js, wizard.js, web/assets/plan-ui.js.
Checks: `tools/check-ui.py` ok; `node --check` on the four JS files and the inline script; no em dash; `smoke/weekplanner.js` 4 of
4; official smoke `plan` at 1440 and 390 NO ERRORS, inventory identical to before; the browser runs logged no console errors.

### Per screen

- **Day card (hero).** Good: one orange Start, the wash corner, quiet rows. Fixed: a task's kind mark sat alone on its own line
  whenever the title wrapped (phone, the builder's Live plan, the landing preview); the head is one line now and the title wraps
  inside itself. On a phone a row with several topics says them as one line of text (three chips stacked one a line), and the
  rows' own Starts are a quiet word (they show without hover there, three white buttons under the orange one). "Did it
  elsewhere?" Save, and every `btn sm ink` on the page (Discard, Switch, Remove, Apply, Catch up, Raise to...), was ink text on an
  ink button: the page's `.pl .ink` helper beat `.btn.ink`; it is `:where()` now.
- **Calendar.** Was: today a thick 2px ink box, the week on show seven grey tiles with gaps, missed days loud ink ⊗. Now the week
  on show is one soft band with round ends (each day fills the gaps beside it), today is its date on a small ink chip (the picked
  day keeps the one boxed amber look), missed marks and rings are graphite so the past recedes. From the lead's round 3: the
  month nav, the task bar and the hand-made key are `UI.calendar({ nav: false, tasks: false, legend: 'why' })` (CSS hides and
  the key code gone; the key now lists every mark, one a line, behind the same ?).
- **Status tiles.** The Score arrow sat small and low between 520 and 700: now a soft arrow on the figures' line. This week's
  ticks and its separate row of day rings are one `UI.meter({ tickStates })` (done, partly, missed, today outlined) with the day
  letters under the blocks, graphite like Plan done.
- **Shape this week.** Was five amber-ringed choices at rest over five black slabs (pale slabs in dark). Now the day as planned
  wears a grey ring and only a change lights amber (as the builder's Normal); bars are graphite, a changed day's bar turns ink.
  Its total was stuck at "7h 30m" after Busy (kit.js `roll()` threw "off is not a function"; fixed in kit.js since, it rolls to
  "7h 30m → 6h").
- **Builder, step 3 "Time you have"** (the user's "busy"). Was five amber study tiles (five orange edges in dark), a label-like
  "Different times on some days", the tests seg wrapping "Every study day" alone on a phone. Now the week is one recessed track,
  a study day a raised white key, a rest day flat in it (no orange; Next is the step's one); seven keys a row on a phone (four
  only while each day shows its own minutes); the toggle is a soft line with a turning caret; the tests seg fits one line at 390;
  the slider row has a grip at the fill's end.
- **Builder, Live plan column.** The month's days lost their 13 hairline boxes and the phase underlines (only today, picked,
  SAT and days off keep a shape); Day 1's rows keep their mark on the title's line.
- **Builder, other steps.** Step 2's "Other date" field is 200px (it spanned the column); More options has one hairline, not two.
- **Landing.** Calm. The Math score tile is a tile like Next SAT ("–", Find it in 30 min, links to Tests) instead of a different
  shape; the phone preview's Map row is one line of topics.
- **From the lead (round 3).** College Board's link draws `external` (the rotated arrow and its CSS gone); a picked day and a
  builder step enter by `UI.motion.enter(..., { axis: 'x' })` (the `.pl-in` keyframes gone).

### Inventory diff, accounted

The official fixture stops at the landing (identical before and after). In the plan view, from the browser runs: the month's
Previous / Next / Today buttons and the per-day `.cal-tk` chips are no longer in the DOM (they were CSS-hidden; PageUp / PageDown,
the week arrows and `select()` still move the month, and the plan range stays `min` start to `max` exam day, so no one-month
clamp); the key is the shared `?` with the same label ("the calendar's marks"); This week's ring row became a letters row with
the same aria-label, the meter keeps its value / max; the landing's Math score link reads "Math score – Find it in 30 min"; a
phone's row Start is `.quiet` (class only); the builder's "Different times on some days" carries a caret (same label).

### Other pages

plan-ui.js also draws Today's plan card and the session summary: the one-line row head, a phone's text topics (when more than
one) and its quiet row Starts reach them too. Today's smoke (`run.js plan` and `fresh`, 1440 and 390): NO ERRORS.

### Round 4

Shots `plan-r4-*` (1440, 1440 dark, 390 with touch, banners opened at both widths). From the lead's shots:
- **"1 more" is part of the banner.** It sat alone as plain text between the banner and the Today card; now it ends the first
  banner's line as a disclosure ("Missed Fri, Oct 16 · Module test · 1 more", a caret that turns; "Show less" when open).
- **The Missed banner is one compact row on a phone**: the line wraps inside itself beside Do it now (`.btn.sm`) and the x,
  instead of text over a row of buttons. At 390 the Today card now starts at about 37% of the first screen (was about half),
  with the shared sign-in banner gone from this page (one banner at a time).
- **Missed days are faint**: ring and cross in `--faint`, and a past test day loses its box (only a test still to come keeps
  one), so 16's mark weighs the same as 13 to 15.
Checks: check-ui ok, node --check, no em dash, weekplanner 4/4, smoke `plan` 1440 and 390 NO ERRORS, inventory identical.

### Shared asks

- ui.css `.cal-sw.practice` / `.cal-sw.test` (the plan look's key): a filled dot and a filled bar, while the plan's cells draw a
  14px ring and an outlined box; the key should draw what the cells draw.
- A default ring for segs: Plan grey-rings the default option in two places (`.wz-seg3` Normal, `.wplan-c [data-base]`); a
  shared `[data-base]` (or `UI.seg({ base })`) look in ui.css would replace both.
- ui.js: the phone's "Hold a tab for shortcuts" toast lands on the builder's sticky foot (Back, Draft saved, Next) and over the
  first task rows; lift toasts above a page's sticky action bar, or skip the hint while one shows.
- ui.js: the "Have progress on another device?" banner is a second amber wash above Plan's own banner on a first visit.
- Optional: the Start pill's `⇧Enter` keycap is mono on the orange; Geist with `⇧↵` would read less like code.

### Not done

- "· changed" in the day's line (a day you edited) is left as worded.
- Progress tab: looked at, not reworked (not in this pass's list).
