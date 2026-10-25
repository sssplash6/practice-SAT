# Pass report: Today (web/index.html)

File: `web/index.html` only (page CSS, markup, inline script). 3054 lines before, 2722 after.
Checks run: `python3 tools/check-ui.py` (ok); `node --check` on the three inline scripts (ok); em dash grep on
`web/index.html` (none; the row title regex now writes the em and en dash as `\u` escapes); every removed class grepped across `web/`
(all were page-local; `.reason`, `.rise` and `.tag` exist elsewhere with their own rules, untouched). Extra: a jsdom
smoke run (scratchpad, not in the repo) painted the page from hand-made `/api` payloads in five states (plan step
merged into its row, a running test, a Review step with the receipt, a brand-new student, the final stretch) at
1440 and 390 wide, and clicked the folds, the card chevron, the practice toggle, QotD full screen, tab and Escape,
and Enter on the header's title (it still runs the at-risk "1 question"): no errors.

## First screen

**Today, 1440x900** (sidebar 248, content about 1040: main about 728 plus the 300px sticky aside).
- Leads with: one header row, the greeting at the page size (22) with the date beside it as meta. Then **Up next**
  at about y 60: the day's tasks as 40px rows in one card. The step Up next would start is the first row and carries
  the page's one orange Start (`.pill.sm`, about y 110 to 145); the other tasks have the quiet play button. A step
  with more to it (a running test's clock, Timed or Untimed, a rehearsal) keeps its own block on top with the 42px
  Start, and its row below gives up its Start. Then "N more due", "N done", "Or a practice session".
- Right column, top to bottom: Today (streak with best, study time meter against the goal, plan n of m, since
  yesterday), SAT (the day count as the card's figure, Register by, Details), Score (band, target, scale, gap,
  Details), Pace, Daily challenge, Words (one row). Sticky, scrolls inside itself.
- Moved out of the way: the 36px greeting with its caps date eyebrow (now one 27px row); the hero chips and the
  "brief" line (to the aside's Today card); the separate Due today card (merged into Up next, `#due` kept as an
  anchor inside it); the measured card shuffling between two bands; most of Score (trend chart, verdict, evidence,
  where points went, scores you added) and of Study time (time split, this week against last) behind one Details
  row each; older test sittings behind one row each.

**Today, 390x844.**
- Leads with: the greeting and date, then one row of the day's figures as plain links (minutes against the goal,
  plan n of m, SAT in N days; the streak stays in the phone bar), the streak-at-risk line with "1 question" when it
  applies (never folds), and "Since yesterday" as one fold row. Up next starts at about y 250; its Start lands at
  about y 300 to 340 (it was about y 400 to 430, after a 250 to 290px hero).
- Then Questions of the day, Mistakes, Points on the table, Study time, Calendar, Recent tests, then the aside's
  cards (SAT, Score, Pace, challenge, Words). Below 1280px the aside's Today card is hidden because the header row
  carries the same figures.
- In the final stretch the SAT card moves into main right under Up next and Mistakes follows it, at every width.

## Big changes

1. Today is two columns: the day's work on the left, the day at a glance on the right (from 1280px wide; one
   column below that, work first). Cards no longer jump between columns as they load.
2. Up next and Due today are one card. The thing to do next is the first task in the list with the one orange
   Start; every other task has its own small Start. No task has two Starts any more.
3. The big greeting is now a slim header row; the streak, minutes, plan and "since yesterday" live in a Today card
   on the right (or one row under the greeting on smaller screens). "Since yesterday" is the bottom part of that
   Today card, not a card of its own (the two are one glance).
4. Score keeps the band, target, scale and gap in view; the rest is under Details. Study time keeps its four
   figures; the rest is under Details.
5. Words is a one-row card in the right column: counts, Start, the reason behind an (i), All words, the link to the
   day's word question.
6. Recent tests shows the latest sitting in full; each older one is a row (date, kind, band) that opens to the same
   full card.
7. The Up next card is no longer tinted orange; orange marks the one Start.

## Bugs fixed

- I1: `openDay` was declared twice; QotD's past days opened the calendar's Day details. QotD's is now `openQDay`
  (its strip tiles and Older use it); the calendar keeps `openDay`.
- I2: the shared fold no longer folds the lead (it holds a button), but `.lead-t` could still fold alone on a 70+
  character title (the rehearsal step's is longer). The lead now carries `data-nofold`. The page's own `.fold`
  rules are scoped to `button.fold`, so ui.js's `details.fold` keeps its look.
- I3: `TODAY_CARDS` listed `plan` (no such section), so a failed `/today` threw before Up next got its Retry. The map
  now lists only cards on the page (`due` left too: it lives inside Up next). Retry text is "Couldn't load today."
- I4: the stretch rules for the calendar targeted `#study`; they now target `#cal`, so the month fills its card.
- I5: the side column at 1100 to 1279 with the sidebar was 200px inside; one column below 1280 now.
- I6: double dividers between Points rows: the local `border-bottom` is gone (the shared `border-top` stays); extra
  and domain rows use `border-top` too.
- I7: dead QotD two-column CSS and the hidden `.qd-lab` / `.qd-rowk` nodes are gone; Full screen is one button at the
  end of the tab strip (it sat over the first line of an R&W passage) and follows the tab on screen; Escape exits.
- I8: the Points sort row stuck at 68px below 1080 with no bar there; it sticks at 8px, under the phone bar only on
  phones.
- I9: Mistakes is no longer a 300px inner scroller resized by `balance()`; three rows plus the "N more" fold is the cap.
- I10: dead code deleted (below).
- Kept working through the move: J / K still reach the header (it is a `header` now, `cards()` includes it) and Enter
  on its title still runs the at-risk "1 question"; the task list `#due` is a labelled group ("Due today") so screen
  readers keep its name, and the tour's `#next` / `#due` / `#qotd` / `#gain` / `#soon` steps still find their targets.

Dead code deleted, with why it was unreachable: `paintPlan` was an empty function, so `planSet` and `planNone` (only
called from the old plan card) never ran; `stripDays`, `weekDay`, `startDayTask`, `saveDraftThen`, `planPreview` were
only called from those two; `reasonText` had no caller; `targetSheet`'s `draft` branch was only reached from
`planNone`; the three `paintPlan()` calls (paint, target save, shell dates) and `S.week` / `S.draft` went with them;
`place` / `balance` / `ensure` / `phoneOrder` / `WIDE` replaced by a nine-line `place(stretch)`; the unused `phone()`
helper; the receipt's `satf.done.<day>` key (it only fed the entrance animation). CSS: `.reason`, `hr.sep`, `.tag`,
`.tag.ink`, `.sp*`, `.cal-wrap`, `.wk-hd`, the plan block (`.plan-stats` to `.cta-steps`), `.wk-day` phone rules,
`.td-takes`, `.hero-*`, `.brief`, `.exam-trig`, `.clock-tog`, `.td-col` grid, `.rise`. `showDay` and `calSheet` stay
(live).

Also done from the ranked list: spacing on the 4px grid with `--card-gap`, `--row-h` rows, 12px blocks, 8+8 fold
rows (P7); every size on the scale, figures Geist tabular (`.big`, `.score-band`, `.band` at 28; row figures 16),
no mono on words, `.sub` sentence case 12.5/600, the `.td .card .k` / `.meta` / `.help` / `.quiet` / `.pill`
overrides gone (P8); the lead's Start is a plain `.pill`, the SAT date trigger a `.btn.sm` with a chevron icon, the
clock toggle `.btn.sm.icon` with `aria-pressed`, QotD tabs the shared `.tablist`, glyphs out of labels (pencil icon
for Target and Goal, "+4 on last week" for the arrows, words for the day window's opened / closed marks, a drawn key
for wrong / blank, "College Board" without the arrow) (P9); no boxes inside cards: `.q1`, `.receipt`, `.tchip`,
`.figs`, `.wk-t`, `.causes-fix`, `.slot-detail`, `.tcard` lose their fill and group with hairlines; orange hairlines
are `--line` (P10); touch parity: the goal fit, the week's mistakes, the thin-domain counts, the study tips and the
stretch rule are visible text or an (i) now (P14); tags are `.badge.soft`; about 30 inline styles replaced by
classes; copy: "Fix" to "Review", "Start the mentor's set" to "10 questions to start", "Now its twin" to "Try its
twin", "Sweep" to "Recheck fixed mistakes", one card name for Points, verbs "practise" and nouns "practice", the
target line on one line (P16).

## Not done

- `.reveal` for the task rows: the shared rule needs the hovered element to be the direct parent; the row's (i) and
  menu sit deeper, so `.drow` keeps its local hover rule. The card chevron uses `.reveal` (a folded card always
  shows it).
- The (i) beside facts (`.why-i`) is still a 50% ring that is a button: there is no shared info mark to swap to.
- QotD's question shows its own orange Check (question.js, not this page), so on a 900px laptop the first screen can
  hold two orange buttons when QotD's top is in view.
- `≈ +N` estimates kept on buttons and rows: they are data, not decoration.
- Recent tests: older sittings open to the full card instead of a row with Review and a menu, so every figure, chip
  and button each one had stays on the page.
- A few inline styles stay where they are one-offs in sheets and popovers (the calendar sheet rows, the goal popover
  grid, the target slider's width, the suggested goal chip's ring).
- `targetSheet`'s `later` (a later exam date) is never set, so its branches never run; left alone, it is not part of
  the plan builder this pass was asked to remove.
- The day window's figure and skill tiles (`.dd-fig`, `.dd-sk`) are still tinted boxes inside the sheet.

## Shared asks

- `ui.css` `.reveal`: an ancestor form, e.g. `.reveal-host:hover .reveal, .reveal-host:focus-within .reveal`, so a
  list row can reveal its secondary actions; then Today's `.drow` rule goes.
- A shared info mark (an `.info` or `UI.info(text, label)` in kit.js) with the shape DIRECTION allows for a button,
  to replace Today's `.why-i` (Practice and Review have their own copies).
- `ui.css` `.cal-grid`: a fluid variant (`repeat(7, minmax(36px, 1fr))`, max 640) so Today stops overriding
  `#cal .cal-grid / .cal-d / .cal-head` by id.
- `ui.js` FOLD_SEL: `.lead-t` on its own can still fold a long title on other pages; drop `.lead-t` or skip it when
  its parent `.lead` holds a button.
- `ui.css` `.skill-row.gain`: min-height 60 to `--row-h`; Points rows are the tallest rows on the page.
- `question.js` / runner: an embedded (inline) workspace whose Check is `.btn`, not `.pill`, for questions that sit
  in a page under another primary (QotD, Up next's first question).
- `ui.js`: the nav Today meta counts questions while the page counts minutes; one unit.
- `ui.css` `.streak`: still mono 13 soft (Today's header and Today card use it).

## For the user

- The header still says "Good morning, Name". It could say "Today" instead (the nav already does); your call.
- In the final stretch the SAT card used to sit above Up next on a phone; it now sits right under it (the task
  comes first). Say if you want it back on top.
- Words became a one-row card instead of disappearing; it can go entirely, since Up next's Words row starts it.
- Older test sittings are now one row each that opens to the full card. If you would rather see Review and Fix on
  the row itself, that is a small change.
- Copy changed in a few places (listed under Bugs fixed, P16): "Recheck fixed mistakes", "10 questions to start",
  "Try its twin", "the mistakes it opened are in Review".

## Polish round

File: `web/index.html` only (2722 lines before, 2759 after). Checks: `python3 tools/check-ui.py` (ok); `node --check` on the
three inline scripts (ok); em dash grep on `web/index.html` (none); every removed selector grepped across `web/` (`.why-i`,
`.info-pop`, `.pace-fig`, `.words-row` and the local `.drow` hover rule were page-local; nothing else uses them); smoke
`page.js ... / 1440` and `390`: no errors, same as before the edits. Extra jsdom run (scratchpad) over the plan, stretch,
fresh, test and review fixtures at 1440 and 390: no errors; the aside and main rows hold the right blocks in the right
order (the SAT joins main in the stretch), the readout follows a hovered day, and a refresh with more minutes rolls the
three minute figures to the new value.

### First screen

**Today, 1440x900.** Main leads with the slim header and then Up next, whose Start is the one orange button on the
page; QotD's own Check is question.js's (see Not done). Under it, Questions of the day, Mistakes and Points on the
table are now one surface: three blocks split by hairlines instead of three boxes, each keeping its head, fold and
actions. The aside is one calm "Today at a glance" surface with six rows split by hairlines instead of six cards. Each
row's head is the label on the left (14.5/600, a step below the main column's card titles) and its value on the right:
Today and the streak; SAT and the day count ("40 days"); Score and the Target control; Pace; Daily challenge and how
many are in (the rank once finished: "#4 of 30"); Words and its counts with their `?`. Only Score and Pace keep a big
figure, and they lead their row: the band (or the pace) at 28 with what it is beside it on the same baseline, then the
evidence (the scale; the new pace meter). The Today row reads as quick stats: Study time with a 10-tick meter against
the goal, Plan with "1 of 3 done" on the right, then Since yesterday. Words shows a tick meter of the day's new words
(one tick a word). A folded row is now exactly label and value.

**Today, 390x844.** The same order as round one: header, Up next, then the QotD, Mistakes, Points surface, Study time,
Calendar (with its readout line), Recent tests, then the glance surface (SAT, Score, Pace, challenge, Words; the Today
row stays hidden under 1280 because the header carries its figures). Row values sit on the right; a long value (Words)
wraps at its " · " inside its slot so the fold chevron keeps its place.

Moved out of the way: the six aside boxes and three main boxes (now rows of two surfaces); the SAT day count at 28 (now
the row's value at 14.5; the date picker moved to the line under it, beside Register by and Details); the challenge
rank at 28 (now the row's value); All words (from the Words head to the Words row's action line, beside Start).

### New components added

- `UI.why` (kit) replaces the page's `info()` (`.why-i` popover button) on all seven: the Unlocks row (`About Points`
  and the rest; its hover tooltip comes with `UI.why`), Mistakes' empty line, Blind spots, Points' "from N answers",
  the final stretch, the challenge, Words. Names went from sentences to `About <noun>`.
- `.reveal` / `.reveal-host` replaces the local `.drow` hover rule: each Up next task row is a `reveal-host`; its `?`
  (the reasons disclosure) and its ⋯ menu are `.reveal`. Start stays visible; touch shows everything, as before.
- Tick meter (`UI.meter({ticks})`): the Today row's Study time (10 ticks, a tick a tenth of the goal) and the Words
  row's new words (a tick a word, up to 12). The thin bars under Study time's figures stay (they are on phones the
  only minutes-against-goal visual, and two kinds in one figure row would clash).
- `UI.roll`: today's minutes roll to their new value where they show (header figures under 1280, the Today row's
  meter text, Study time's Today figure) when they change on screen: back from a session through the back button or the
  tab, a question of the day answered, a task ticked. Never on load: only paints after a `refresh()` roll; the two
  startup paints (the day's stored copy, then the fresh one) set the text plainly.
- Heatmap readout: the kit adds its line only under `UI.heatmap` (`.heat-wrap`). Today has no `UI.heatmap`: `#cal` is
  `UI.calendar` in its heat look and `#study` has no grid, so the readout did not show. The calendar now has its own:
  one fixed line under the month (the shared `.heat-readout` look) with the hovered or focused day's label ("Mon Oct
  19, 20 minutes, 14 questions, 71% right"), else the picked day; nothing floats over the grid. It sits outside the
  figure, so the calendar's own redraws keep it. `#study` gets no heatmap (it would repeat the calendar and need its own
  request).
- Number-first heads: Score's band and its source line on one baseline (`.figline`, which Pace now shares); Pace gets
  a 4px graphite meter of the module time against the SAT's 35 minutes (full when over).
- One surface of rows (`.td-rows`): a tile with the card hairline and padding; its blocks keep `.card` (and so their
  ids, `--surface`, fold, J/K, tour targets) and lose their own box; a 1px line on top of each block, the first one
  lying on the surface's edge whichever block is first (`#sum` hidden under 1280, a block hidden by Unlocks). `place()`
  now orders three boxes: main, the main surface (QotD, Mistakes, Points; Mistakes first in the stretch) and the aside
  surface; the SAT moves to main in the stretch and is a plain card there.

### Removed local copies

- `info()` and its CSS (`.why-i`, `.why-i::before`, `.why-i[aria-expanded]`, `.why-i.q`, `.info-pop` and its children).
  The task row's reasons toggle (an inline disclosure, not a popover) now wears the shared `.why-q` look with `?`;
  QotD's streak popover uses `.why-pop`.
- The local `.drow` hover-hide block (now `.reveal`).
- `.pace-fig` (now `.figline`), `.words-row` (the Words row is head value plus an action line).

### Not done

- `#study` heatmap: see above; the calendar is Today's heatmap and carries the readout.
- QotD's question shows its own orange Check (question.js), so the first screen can still hold a second orange
  button when QotD's top is in view (round-one shared ask, still open).
- The day window's tinted tiles (`.dd-fig`, `.dd-sk`) and the remaining one-off inline styles in sheets and popovers,
  as in round one.
- The Study time card's `.bar4` stays a plain bar (reason under Tick meter).

### Shared asks

- kit.js heatmap readout: also cover `UI.calendar`'s heat look (`.cal:not(.plan) .cal-d[data-day]`, the line after
  the figure); then Today's `calReadout()` goes. Better still, charts.js draws the line in both `heatmap()` and
  `calendar()`.
- `UI.meter`: a way to say "over is not done" (no `.done` check when value passes max), so Pace can use the shared
  meter instead of the page's `.bar4.ink`.
- `spec/redesign-2026-10-19/smoke/run.js` prints "aside order" from `.twocol-side`'s children, which is now the one
  `.td-aside` surface (no id), so that line comes out empty; point it at `.td-aside` (the blocks are all there).
- Still open from round one: `.cal-grid` fluid variant (Today still overrides `#cal .cal-grid / .cal-d / .cal-head`),
  FOLD_SEL `.lead-t` alone, `.skill-row.gain` min-height 60, an inline Check for embedded questions, one unit for the
  nav Today meta, `.streak` style.

### For the user

- The right column is now one block of rows instead of six cards, and Questions of the day, Mistakes and Points share
  one block in the main column. Every figure, link and button is still there; each row still folds to its title.
- The SAT's day count is now a plain "40 days" at the right of its row instead of a big number; the date picker sits
  under it. Say if you want the big number back.
- Today's minutes roll to their new value when they change while you watch (back from a session, a question answered);
  they never move when the page first opens.
- The calendar has a line under it that shows the day under your pointer or focus.

## Premium build (part 1)

File: `web/index.html` only. Part 1 covers the calm first screen, the hero, the open bugs and the Per page and More items that need no new shared JS. The lead's follow-ups after A1 landed are in too: no page-level tile boxes, no side stripes, no ink focus rings. Motion, feedback moments, icons and spot drawings are part 2.

Checks: `python3 tools/check-ui.py` ok. `node --check` on the three inline scripts ok. No em dashes. Every removed selector was page-local (`.size`, `.size-picks`, `.td-fold`, `#sum .meter`, `.qd-day.mon`, `.tcard.open`, `#due:not(:empty) + .sess`). Smoke `run.js` fresh/plan/review/stretch/test at 1440 and 390: NO ERRORS in all ten. Each run has exactly one `.pill` in `#next` (Study, Start, Start, Start, Resume), the same as before. `page.js / 1440` and `390`: NO ERRORS. A scratch act script (not in the repo) drove these, all working in the five states plus exam morning:
- the hero class and the featured row's pill
- the footer toggles and the builder toggle
- the size menu: a pick, then Timed for a number of questions
- the Since row
- the aside defaults and the head click
- the day strip ring and the Today ring
- the older test fold
- Enter on the h1
- a plan tick

### First screen

Counts are structural (jsdom, plan state, approximate). The audit's "before" was 25 buttons at rest plus 15 on hover at 1440.

**1440x900**
- Header: unchanged (greeting and date on one line; at-risk line when it applies).
- Up next:
  - The controls stay the same: 7 at rest, 4 on hover.
  - It now takes 4 lines instead of 6. "2 more due", "1 done" and "Or a practice session" were three full-width rows and are now one footer line.
  - For a fresh student, Up next went from 11 controls to 5. The size row (Minutes | Questions, five chips, the clock) is now one menu.
- Aside:
  - Before: 6 open blocks with 17 controls at rest plus 6 chevrons on hover.
  - After: the Today row stays open (ring, minutes, plan, since yesterday). The other 5 rows show label, value and chevron only. That is 10 controls at rest and none hidden on hover.
- Surfaces: still 3. Only Up next is raised now.
- Orange at rest: the Start, the ring's arc and the flame. QotD's Check is solid grey until an option is picked (A1's disabled look).

**390x844**
- Header: 6 controls to 5. Two wrapping lines of links became one strip: a 28px goal ring with "20 of 30 min", "Plan 1/3" and "SAT in 40 days". Each link's full sentence is its label.
- Since yesterday left the header. It is the first row of the surface under Up next.
- On touch, a plan row's `?` is the first item of its ⋯ menu ("Why this"), so each such row has one control fewer.
- Up next starts right under the strip.

### Hero

- `#next` is `.card.hero` in the markup: `--shadow-3` on `--hero-wash`, from ui.css. Its own title recedes to 14.5/600 soft, so the task is the largest text in main.
- The day's step as a row (`dueRow` mode `lead`) is the featured task:
  - a 20/600 `--ink-strong` title
  - its facts on one line
  - the full 42px `.pill` under them (it was a 34px `pill.sm` at the row's end)
  - checkbox, `?` and ⋯ stay
- The other shape of the step (the `.lead` block: test, resume, plan test, rehearsal, after the SAT, rest day) gets the same 20px title. Its Start moved from beside the title to the head of its action line, so both shapes read as one hero.
- Compact rows: the play button is a quiet `.ibtn` (no grey fill at rest).
- No `--fs-hero` on Today. The page is about a task, not a number. The day's figure is the 44px goal ring in the Today row: today's minutes inside it, "of 30 min" beside it, and the number read out by a `.sr` span.
- AUDIT 12 Today 2 (the SAT countdown as a 40px figure) conflicts with pages/today.md 2 (the SAT as a row value). I followed the page audit.

### What moved behind which control

- **Session size:** Minutes | Questions, the size chips and the clock toggle became one `.btn` "15 min" with a chevron, beside Study. Its menu has a Minutes radio group, a Questions radio group (with Endless) and, for a number of questions, a Timed checkbox. The button says the choice ("10 questions · timed"). The estimate sits on Study's line. "Short on time?" sits under it. "See an example first" and "More options" are on a quiet line below. `DEF`, `SZ.sel`, `askPreview`, `pillLabel` and the More options link work as before.
- **Aside rows:** SAT, Score, Pace, Challenge and Words rest folded. Today stays open. A choice already stored in `satf.card.<id>` still wins. The whole head opens a row, and the chevron always shows there.
- **Values on folded rows:** Score shows the band ("540–580", "≈ 560" or "No score yet") and Pace shows "33:00 of 35:00". Both hide while the row is open, because the 28px figure leads then. SAT, Challenge and Words keep the values they had.
- **One disclosure per row:**
  - SAT's Details applies only when the SAT is a card in main (final stretch).
  - Score's, Pace's and Challenge's Details folds are gone; their content shows in line once the row is open.
  - Score's Target moved from the head into the open row's action line, beside Add a score or Get a score.
- **Up next footer:** "N more due" and "N done" (keys `due.also`, `due.done` kept) open their lists above the line. What each holds is its tooltip. "Or a practice session" opens the builder under it. On exam morning the toggles sit inside "The usual parts".

### Other part 1 items

- **Day strip under 1280px:** one line with the goal ring (see above).
- **Streak at risk:** a warm callout (wash fill, 10px corners, the flame, "1 question"). Still `data-nofold`.
- **Unlocks line:** counts where the server has them ("Points 4 of 30", "Pace 7 of 20").
- **Spacing:** header to Up next 24 (was 16). Aside rows padded 14. `--card-gap` 32 comes from ui.css.
- **`.td-rows` has `overflow: clip`, and its blocks `margin-top: -1px`.** The card edge is now outside the box, so the first block's hairline would have drawn a line across the top of the white surface. It now tucks under the top edge, whichever block is first. Clip is not a scroll container, so the sticky Points sort still sticks, and kit mounts layers on body.
- **The day strip's 28px ring uses `--ring-w: 3px`.** The 44px Today ring keeps the shared 6px.
- **The lead's asks after A1:**
  - `.td-rows` surfaces now use the card look (`--raised`, `--shadow-1`). They were a tile with an inset line.
  - The sticky Points sort bar is `--raised`. The Updating chip is `--raised` with `--edge`, not `--tile`.
  - Side stripes removed: the In progress test card's amber bar and the Monday bar in the QotD day strip.
  - Ink focus ring on mistake labels replaced by the links' amber-deep underline on a wash.
  - Picked QotD day: the one selected look (`--sel-bg`, `--sel-edge`). Picked challenge slot: the shared current-cell mark (`--ring`).
  - In the day window, the figures and skills are no longer tinted tiles inside the sheet. Figures are 20/600; skills are rows split by hairlines.
  - Tile grids keep their own gaps (8-12); only `.td-main` uses `--card-gap`.

### Bugs fixed

- Open bug 10 (Today's part): Up next holds the only orange button in every state. QotD's Check is solid grey until a pick, because of A1's disabled look, so the first screen has one orange button at rest.
- The tinted tiles in the day window (round 1 and polish "Not done") are fixed (see above).

### Inventory diff (1440, plan state)

Every change is accounted for:
- **Gone: buttons "5", "15", "30", "45", "60"** (the minute chips). They are now the size menu's Minutes items.
- **Hidden in the diff, also moved:**
  - Session "Minutes" and "Questions" (the calendar's metric switch has the same names) are now the menu's two groups.
  - The question counts and the clock toggle are now Questions items and Timed.
  - The four "Details" buttons (SAT in the aside, Score, Pace, Challenge) have their content in line once the row opens. Study's and the blocks' Details remain.
- **"Collapse SAT", "Collapse Score", "Collapse Pace", "Collapse Daily challenge", "Collapse Words"** are now "Expand ..." because these rows rest folded.
- **New: "Session size: 30 min"** (the menu button) and `#since` (the Since yesterday row under 1280).
- **ids `kclip`/`kmk`:** kit uid renumbering, not real changes.

### Not done (part 1), with reasons

- Motion (fold height, page entry, list glide, ring sweep, rolls on the ring), feedback (task tick, goal met, streak ignite, new-day toast), icons (`svgI`, `MORE`, `PEN`, ✓ ✕ ↻ marks, kind marks on rows, the clock in the lead's meta, the play glyph in the Start), spot drawings and sample rows for empties: all part 2 by the brief.
- Status marks: plan rows use the native checkbox, which ui.css now draws; other rows use the `.st` ring. Making them one drawn ring with a check stroke needs A2's check draw (part 2).
- Fold rows' hover wash and chevron nudge: part 2, adopting the shared hover band.
- Page title at 26-28 (AUDIT 4.3): `.h1` is shared and A1 kept it at 22.

### Shared asks

- `spec/redesign-2026-10-19/smoke/run.js` act mode:
  - `#due button.fold` should become `#next .td-foot button.fold` (the toggles left `#due` for the footer line).
  - `#hero button.fold` should become `#since button.fold`. As it stands the act run stops at line 67 on the missing node; the rest of it passed in the scratch run.
  - The "aside order" line should read `.td-aside`'s children.
- A2 / kit: a ring that sweeps on change and closes with a drawn check (`.td-ring` holds the minutes in `[data-min]`, so `UI.roll` already reaches the number).
- Still open from earlier rounds: `.cal-grid` fluid variant, FOLD_SEL `.lead-t`, `.skill-row.gain` min-height, nav Today meta unit, `.streak` style.

### For the user

- The right column now rests as one line per row (SAT, Score, Pace, Challenge, Words). Tap a row (anywhere on its line) to open it, with everything in it at once; Today stays open. Your choice is remembered.
- The practice session's size is one "15 min" button beside Study. The five chips and the Minutes / Questions switch are in its menu.
- On Score, the Target button is inside the opened row.
- On a phone, the figures under the greeting are one strip, and Since yesterday sits under Up next.
- The orange bar on the In progress test card and the Monday marks in the question-of-the-day strip are gone (the "no side stripes" note). Say if you miss the Monday marks.

## Premium build (part 2)

File: `web/index.html` only. This part adopts the merged phase A layer (A1 controls, A2 motion and feedback, A3 icons) and finishes what part 1 left for it.

Checks:
- `python3 tools/check-ui.py` ok. `node --check` on the three inline scripts ok. No em dashes.
- `run.js` fresh/plan/review/stretch/test at 1440 and 390: NO ERRORS in all ten. Each still has exactly one `.pill` in `#next`.
- `run.js plan 1440 act` (with the lead's updated selectors): every step passes. In the other states, act mode stops where that fixture has no node to click: no at-risk button in stretch, test or review; no footer or Since row for a fresh student. Stretch also stops on the original file.
- `page.js / 1440` and `390`: NO ERRORS. Exam morning (scratch, `TZ` set to a morning): NO ERRORS.
- A scratch act script (not in the repo) checked these in plan, review, test and fresh:
  - kit's tabs: the sliding mark, a click shows its panel
  - kind marks, the play glyph on the featured and lead Start, the status marks, the spots
  - a tick: the row leaves, "1 done" rolls to "2 done"
  - a refresh with more minutes and a longer streak: both rings sweep to 1, the goal check shows after the close, the streak reads 6 in both places
- Inventory (1440, plan): against part 1 the only change is the id `dayNote` (now a toast, below). Against the morning baseline the diff is part 1's, all accounted there, plus `dayNote`.

### Shared controls adopted

- **Own primary:** `UI.shell({ page: 'today', now: false, nowBlock: false, ownPrimary: true })`, so the sidebar's and the Now strip's Up next Start is a `.btn` and Up next keeps the one orange button.
- **Busy:** Starts get A1's spinner after 300ms through the page's `run()` (it sets `aria-busy`).
- **Way forward:** the featured task's Start and the lead block's Start are `.pill.go` with a trailing play glyph that nudges on hover (not for "after the SAT", which opens a sheet).
- **Checkboxes:** plan rows use ui.css's drawn checkbox; the page's 20px / `accent-color` rules are gone, and the check grows in when ticked. Other rows' status mark `.st` now matches it: 18px, the same 1.5px edge, the same drawn check on amber (11px on the round mark). It stays round, because it is a status, not a control.
- **QotD tabs** are kit's `UI.tabs`: the underline slides, arrows and Home/End move along, each tab leads with its mark. The page's own keydown handler is gone. `qt-*` ids and panels are kept, and Full screen, the swipe and Escape still follow the tab.
- **Scroll shadow:** the sticky Points sort row carries `data-scrolled`, so its shadow shows only while the list slides under it.
- **Quiet menus:** ⋯ stays a ghost `.ibtn`.

### Motion and feedback (never on load; by a key or under reduced motion they are instant or a fade, per kit)

- **Page entry:** `data-m="stagger"` on `.td-main` with `data-m-now` on Up next (the primary is never delayed), and on the aside. Once per visit, by kit.
- **Folds grow:** every page fold (fold rows, the footer toggles, Since yesterday, Mistakes, Points, Study, older tests), the card and row collapse (`.collapsed`, which A2's observer does not cover), "Or a practice session", a row's `?` reasons, the receipt's Details and the SAT's Details in main all open and close in height through `UI.motion.grow` (260 in, 195 out). Each keeps an explicit open state, so a quick second tap is right.
- **Task tick:** `patchTask`'s optimistic paint runs inside `UI.glide` on `#due`. `#due` is now reused across paints and its fold bodies carry `data-key`, so the ticked row leaves where it stood while the rows under it close up. Then the "N done" count rolls (`UI.roll`), or the toggle rises in when it is the first one.
- **Goal ring:** when today's minutes change on screen (back from a session, a question answered), the Today ring and the phone strip's ring sweep from where they stood (`UI.fx.ring`). When one closes the goal, the check beside "goal met" waits, then draws in (`UI.fx.check`) once a day (`UI.motion.once('goal', 'local')`). The check waits only when it will draw: on a later close the same day it stays put, with no blink. The minutes keep rolling as before.
- **Streak:** when it grows on screen, the number rolls and the flame fills (`UI.fx.flame`), once a day. 7, 30, 100 and 365 days get one toast with the flame.
- **Questions of the day:**
  - An answered tab's mark pops once (`UI.fx.pop`).
  - With both answered, the streak number rolls instead of being swapped.
- **New day:** the note is a toast ("It's a new day. Here are today's questions.") that leaves by itself. The static `#dayNote` paragraph is gone; nothing else used it.

### Icons

- `svgI`, `CHEV`, `PEN`, `MORE`, `CAL_TICK`, `FS_IN`/`FS_OUT`, the inline calendar and every `UI.ICON.x || ...` / `UI.ICON.play || ...` fallback are gone. A one-line `ic(name, size)` calls `UI.icon`.
- Disclosures (fold rows, the card chevron, the footer toggles, Get a score, the SAT date, the size menu) use `caret_down` as the control's direct child, so ui.css turns it while open. The page's own rotate rules went.
- Other icons: `caret_right` (a mistake's go chevron), `pen` (Target, Goal), `calendar_check` (the questions streak), `expand`/`shrink` (Full screen), `calendar` (an older day), `more`, `x`, `play`, `check`.
- **Kind marks on rows:** a 16px mark leads each task's facts. focus is practice, learn is learn, fix is fix, recheck and sweep are again, twin is twin, test is tests, review is review, words is words, warm-up is bolt, own task is pen, the day's questions are today, challenge and contest are trophy.
  - The tag word (Focus, Test, ...) is the mark's label and tooltip instead of a badge.
  - "Your own" stays a badge, and a tag with no mark keeps its badge.
- ✓ ✕ ↻ in the QotD tab marks stay text: the Marks font draws them (A3).
- **Spot drawings (`UI.spotArt`):**
  - `clear` over "Nothing left for today." when every task of the day is done and no receipt already says so.
  - `start` above the "Unlocks as you practise" line while Points is still locked (first use).
  - None in sheets, popovers or filtered lists. `UI.spot` (Review's "Spot it") is untouched.

### Not done, with reasons

- **Skeleton to content crossfade:** no shared hook for it, and kit's page entry already rises the first blocks. Left as is.
- **Challenge rank rolling in once:** the value changes from "30 in today" to "#4 of 30", a different shape, so there is nothing to roll.
- **Hover band on task rows:** the rows are not one control (a checkbox, a title, `?`, ⋯ and a Start). The shared band is for whole-row controls, so they keep the hairline.
- **Phone haptics and sound:** not in this pass.

### Shared asks

- `run.js` act mode could guard its fixture-specific clicks (the at-risk button exists only in plan; fresh has no footer or Since row), so the other states finish their runs.
- A shared skeleton-to-content fade (MOTION M2), if wanted, would need a kit hook. Today would call it from `card()`.

### For the user

- Ticking a task makes it leave the list as the others close up, and "1 done" rolls to "2 done".
- When your minutes reach the day's goal while you watch, the ring closes and a small check draws in (once a day). A longer streak rolls and fills its flame once a day.
- Each task shows a small mark for its kind. The words that used to sit beside the title (Focus, Test) are in the mark's tooltip.
- The day's questions tabs slide their underline. The new-day note is a short toast now.

## Visual review

File: `web/index.html` only. Real app at http://127.0.0.1:8071 on the DB copy, my own headless Chromium. Learners: history
`a:v2revresults01` (most attempts; other reviewers were using it at the same time, so its name and a running mock appear
from round 1), plan `a:s7a12891cb412e8b9c` (active plan, exam date, 60-min goal; every active plan in the copy belongs to a
`server/checks/s7.py` fixture learner, and the fixtures whose review queues hold synthetic templates do not load Today, so
I used one that does), fresh (cleared storage). Shots:
`spec/redesign-2026-10-19/premium/shots/app-review/today-r0-*` (before) to `today-r4-*`, `-full` for whole pages; states
`history`, `plan`, `fresh` at 1440, 1440 dark and 390; interactions `hover-row`, `focus-start`, `focus-foot`, `hover-start`,
`press-start`, `menu-row`, `menu-size`, `builder`, `hover-aside`, `aside-open`, `sheet-cal`, `tick-mid`, `tick-after`,
`tick-toast` (1440, light and dark), `menu-row-390`, `since-390`, plus `today-r3-history-1024`. The tick was undone after.

Checks: `tools/check-ui.py` ok; the three inline scripts parse; no em dash; smoke `run.js` fresh/plan/review/stretch/test at
1440 and 390 NO ERRORS and byte-identical to the same runs on the pre-review file; `page.js / 1440` NO ERRORS; inventory
(`inventory.js` at 1440 and 390) identical before and after.

### Verdicts and fixes, per screen

**1440, first screen (light).** Before: the glance column glanced at nothing (SAT, Score, Pace, Words rows showed a label
and a chevron, no value), Today's chevron sat in a grey square between the label and the streak, "Add your name" read as a
second heading, the hero's Start floated 28px under its title, five heavy black play triangles competed with it, and the
Questions of the day streak was a native bordered button. After: one raised hero with one orange Start, a calm column of
label, value, chevron rows. Premium, apart from the shared banner's orange (asks).
- Folded aside rows show their value again (`54 days`, `≈ 520`, `22:51 of 35:00`, `10 new · ~5 min`): the page's
  `.card.collapsed .card-act { display: none }` hid them; it now applies to main's cards only.
- Fold chevrons: no well while open (ui.css gives an open `.ibtn` one, a menu's look); the hover keeps it. In the aside and on
  touch the chevron is the head's last item, after the value.
- The hero's Start: ui.css's way-forward class `.go` collided with the page's `.go` row rule (flex, 12px top margin), so
  every `.pill.go` sat 12px low. The page's row is `.td-go` now; the Start is 16px under the title.
- Row play buttons 16px in `--ink-2` (ink on hover); the hero Start's glyph 14px.
- The name offer sits on the greeting's row, 14px soft with a pen mark, on the text baseline.
- Today row: with a goal the ring always shows (an empty track and "Nothing yet · goal 60 min" before the first minute, no
  zero in it), so the row keeps its shape and the first minutes sweep it from empty. No "0" streak on a first run (decision
  7), here and in the day strip; a streak or a best still shows.
- SAT with no date: the folded row says "No date yet". Words: "-6 new" (more learned than the goal) is gone.
- Questions of the day streak: the button wears the streak's look (no native border; dark mode showed a grey box).
- Mistakes: the row dots are graphite, not amber (the one orange is the Start; pips keep their state colour).
- Focus: fold rows ("2 more due", "Details", the older tests) and the day strip's links take the links' focus (amber-deep
  underline on a wash) instead of a box around words. The Start keeps the ring 2px out (checked).
- Since yesterday: a drop reads "−90" (minus sign), not "-90".

**1440 dark.** Depth and the hero wash hold; the grey streak box and the chevron wells were the only misses, both fixed.

**390 (phone).** Before: three stacked header lines (greeting, a bold "Add your name", a lone "Set your SAT date" with a 44px
strip), a grey square beside "Up next", and its minutes wrapped right-aligned under the chevron. After: the header is the
greeting and date, then one line with the offers or the day's figures (`✎ Add your name · Plan · 3 tasks · SAT in 54 days`
fits; a first run reads `✎ Add your name` and `Set your SAT date` with its calendar mark); the hero starts about 30px higher.
- `#hero` is one wrapping row (`.td-head` is `display: contents`), so the day strip shares the offer's line when it fits
  (760-1279 gets one header row: greeting, date, streak, minutes, SAT). The risk callout keeps its own full line.
- "Set your SAT date" is an offer like the name: soft, with a calendar mark; the figures stay ink.
- Up next's minutes sit on their own line under its title on phones.
- Since yesterday, open, hides its one-line summary (the facts are right under it).

**Menus, sheet, feedback.** Row ⋯ menu and the size menu: good. Add to calendar: the checkbox touched its label and the time
field ran the sheet's full width; now a 10px gap and "Start at" beside a sized field (classes, no inline styles). The
aside's SAT workload line is 500, not 600, in the column. The tick: the row leaves, the rest close up, "1 done" appears,
the aside's Plan reads "1 of 3 done", the toast offers Undo; good.

**First run, below the fold.** The Unlocks line sits beside its start drawing with its label on its own line, so the six
names fit one line ("Tests" wrapped alone before).

### Shared asks (not my files)

- `ui.js` banners: "Save progress" (and any banner action) is a `.pill`, a second orange above every hero, at 1440 and 390.
  Make banner actions `.btn`, or `.btn` whenever the page set `ownPrimary`.
- `ui.js` rail (1024-1279): Up next in the collapsed sidebar is an orange round play button even with `ownPrimary: true`;
  make it quiet like the full sidebar's `.btn` (seen in `today-r3-history-1024.png`).
- `ui.css` `.ibtn[aria-expanded="true"] { background: var(--well) }`: scope it to `[aria-haspopup]` so disclosure chevrons
  are not pressed squares while open; then Today's `.cardfold:where([aria-expanded="true"])` reset goes.
- `ui.css` `.streak` is styled for a link; a `button.streak` shows native chrome. Add `appearance: none; border: 0;
  background: none; padding: 0;` (then Today's `.qd-streak` reset shrinks to its hover).
- `results-ui.js` `sittingCard`: `main.append(h(...), subtitle(row) ? h(...) : null)` prints the word "null" under every sitting
  without a subtitle (Today's Recent tests showed "Full section / null"). Use `''`.
- kit toast: the Undo countdown line is amber; DEMO D5 made it graphite (Undo's underline is the toast's one orange).
- `ui.css` calendar current day (`--ring`, a 2px ink box): heavy on Today's month grid; A1 asked whether it should go thinner:
  yes, 1.5px `--ink-2`.
