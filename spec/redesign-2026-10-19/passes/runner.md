# Pass: the answering screens (runner, session, test window, challenge, diagnostic)

Files: `web/assets/runner.css`, `web/assets/runner.js`, UI parts of `web/assets/question.js`, `web/practice/session/*`,
`web/test/*`, `web/challenge/index.html`, `web/diagnostic/*.html`. No shell chrome and no `.twocol` on the session and
test pages. Bluebook fidelity kept: Source Serif 4 question text, the `[data-status]` / `--st-*` tokens, status never
colour alone (the current segment is taller and ink-edged, not just recoloured).

## First screen

**Practice session, math, 1440x900.** Leads with the stem at about 140px (was ~242): the 64px top bar (Exit, the set's
title with "2 right · 2 in a row" beside it, the clock, the tools) whose bottom edge is the progress strip, then the
question strip as one quiet row over a hairline (number, skill, type, difficulty, stopwatch, icon tools), then the
question. One orange primary: Check (Sure) in the footer, then Next. Moved out of the way: the separate progress row
and its "3 of 10" (the footer says it), the "why this one" line, the verdict's tail (mastery, then, saved note,
formula, everyone) and the second Mark / Note / History / Report under the verdict. Right: a 300px Details column
(why this one, you and this type, everyone, formula, skill, type, difficulty, format, ID and link; after the reveal
the verdict's tail joins it), open by itself from 1280 wide unless the student closed it.
**Practice R&W, 1440.** Passage pane on the left with a hairline divider; the question column sits against it (no
~130px dead gutter). Details opens by itself only when the column keeps 560px beside the passage at its own width
(1366 and up); it never squeezes the passage.
**Practice, 390x844.** Stem at about 200px (was ~264): 56px bar with the segments on its edge, one line "Set title ·
2 right", the strip (number, skill, stopwatch; six tools icon over label at 11.5px; Mark lives in the footer only),
the question. Footer unchanged (Sure / Not sure / Guessing, then Back, Mark, 3 / 10).
**Test window, 1440.** Bluebook layout kept; the module strip moved from above the question header into the top bar's
bottom edge, so the stem starts about 30px higher (~150px). 390: same move, stem ~135px.
**Summary, 1440.** Two columns from 1100: left (sticky) the score at the hero step (44, was 96), the first-try line,
one meta line (date, time, pace), what changed, then the orange next-set pill with two buttons and More. Right: the
Review list as rows, then the breakdown folds. Moved: the "Set complete · date" kicker (date joins the meta line), the
amber-barred note (now plain text). 390: the same, stacked; pill full width.
**Test lobby, 1440.** h1 "Practice test #3" (no kicker, no wash card), facts as hairline rows with no icons, then one
row: the settings line with Settings on the left and "Enter fullscreen and begin" on the right (about 300px down, was
~430). Quiet links under it: Begin without fullscreen, Directions, Keyboard shortcuts, Start over. 390: the pill goes
full width under the settings line.
**Between modules.** h1, one meta line ("12 of 22 answered · 2 left marked · 31:40 used · 0:00 away", was four stat
tiles), the test-day countdown panel with its Begin, then the next module's facts as plain lines.
**Challenge (shell page).** h1 "Daily challenge", the count or your rank at the figure step with its meta line (a
skeleton until the API answers, no hard-coded "10 · 16 min"), Start / Resume top right, day chips, the board as
hairline rows (no zebra).
**Diagnostic.** Index: h1, one meta line, Start on the same row; the three facts as hairline rows (no wash door, no
104px number). Sign-up: h1 and labelled fields, no kickers. Verified: unchanged, tightened.

## Big changes

- The progress strip is now the top bar's bottom edge, in practice and in the test window (the question starts ~100px higher in practice).
- Practice from 1280 wide has a Details column on the right; it opens by itself, and closing it is remembered.
- After an answer, the mastery / everyone / formula / then lines move into that Details column on wide screens.
- The "why this one" line left the question column (it is the first row of Details; the popover below 1280).
- One Explanation toggle (was up to three "Explanation" labels); the card heading is gone.
- On phones Mark, Note, History and Report each appear once (the verdict row keeps Twin and Desmos way only).
- The Summary is a two-column page from 1100 wide, the score at 44px.
- The test lobby and hand-in screens lost their card, kicker and decorative icons; facts are rows.
- Between modules: one meta line instead of four tiles.
- R&W: the question sits against the passage, with a divider, as in Bluebook.
- Exits are one component (`.rn-exit`) on the session, Summary and test screens; the review player's nav pill is `.rn-navb`.
- Tags are the shared `.badge` (Ranked / Training, Grid-in, Again, the trap name, route and rank chips); no caps.
- Words are off mono throughout these screens (only the test clock, the calculator and scratch keep it).

## Bugs fixed

- `.pv` collision: the print wrapper is `.pv-page` now; the grid-in preview's `span.pv` is no longer centred and padded.
- Explanation double toggle: verified the shared skip (ui.js 2820), then proposal 3: question.js wraps every card in one
  `details.fold.x-fold` (the shared fold's look and `satf.fold` "explanation" memory). Must-open cases (review, example,
  quiz, Always open explanations, a miss, a sure miss, a guess) start open but stay collapsible; others start closed
  unless one was left open. No flash, no second fold, works in sheets and where the fold is off.
- "Include answer key" unticked now calls `ws.setHidden(true)` on every answered question: no picks, ticks, captions,
  verdicts, reasons or explanations print; ticking it back restores them.
- Challenge `?day=`: Today's "Yesterday: #4" opens that day's board (Yesterday chip, or a dated chip for older days).
- Challenge board fetched once (was painted from `/api/challenge`'s top five, then fetched again).
- Challenge `.line` renamed `.ch-row` (it also hit `.skel.line` and `.badge.line`); the inline `style="margin:0"` is gone.
- Fold rescans: the timer's Hide button is rebuilt only when it flips, its aria-label only when the text changes; the
  stopwatch updates its text and bar in place; the between-modules clock writes once a second, not four times.
- Right-slot tabs: "Entering your answer" is "Entry rules" in the tab (the sheet keeps the long title); the tab row
  scrolls sideways instead of pushing the close button out.
- Dead CSS: `.rn-qstrip .rn-qtools { padding-left: 34px }` removed. The `max-width: 999px` tool rule was not dead on
  phones (it gave practice's strip its icon-over-label layout): those properties moved into the phone rule, the block went.
- `.rn-col` with a dock, slot or passage now caps at 700 + 32 (it used the 20px pad: 8px too wide).
- Found here: the Details popover showed the skill, type and "why" in a mix-up set before the answer; now hidden until the verdict.
- Found here: note, highlight-note and scratch textareas were 14-14.5px (iOS zooms on focus); now 16.
- Copy: Back (not Previous) in practice; "Questions" for both navigators; "Ask how sure on Check"; "Then and now";
  "Older open mistakes"; "Sure, but wrong. It comes back first."; "Retake these exact questions (tests memory)" and
  "Rematch: same types, new numbers" in both menus; the challenge Summary's Board goes to `/challenge/`; the stale
  "Reports open here soon" fallbacks removed (UI.report always exists); missing values are en dashes; the hidden clock
  reads "–:––".
- Lead's ask from the Review pass: in Review's pane (not the phone dialog) the player's Next is `.btn.sm`, not a second pill.

## Not done

- Stopwatch only past half the budget (audit C): not a ranked proposal and it changes what "Show question stopwatch" means. User decision.
- The exam More menu still repeats Directions, Notes, Scratch, Report and Save and exit on desktop (audit E: fine as phone fallbacks); left as is.
- The finished set's print view still shows each question's review and then the key section (audit E); not a ranked proposal, left.
- Summary rendered inside `UI.shell` (proposal 9 option): needs `#bar`/`#tabs` on the session page and the brief says no chrome there. User decision.
- Review player (`.rv-*`) and history sheet (`.hist-*`) type and mono sweep: that is the review audit's scope. Here only
  what this audit names: `.rv-navpill` uses `.rn-navb`, `.rv-tag` takes the badge's values, `.rv-tlh` lost its caps.
- `'#3F3F3F'` in runner.js's scratch pad: a canvas fallback when `--ink` cannot be read; kept.
- `.strike` (40px round circled letter) kept: Bluebook fidelity exception.
- Check your work keeps its tiles: they are filters (pressed state), not decoration; their 40px figure override is gone.

## Shared asks

- ui.js fold: drop `.x-card` from `FOLD_SEL` and the `:scope > .x-toggle` check in `foldOne` (no `.x-toggle` exists
  now; every card already sits in its own `details.fold.x-fold`). Optional: export the fold memory (`UI.foldMem` or
  `UI.fold(el, {label, id})`) so question.js stops reading `satf.fold` itself (`foldList` / `foldKeep` in explanation()).
- ui.js fold `ticking` selector: add `.rn-between-clock` beside `.timer, .rn-watch, .t-digits` (it still changes once a
  second), and `.rn-segs` (in Training the pace ticks rebuild the strip every 5 s; it now lives in the top bar).
- ui.css `.stat-v` at the figure step (Check your work relied on a local 40px, removed).
- Relied on as planned: `.badge` 6px corners; `.btn` reads `--well` (`.ws-cover` sets `--well: var(--paper)` instead
  of a local paper fill); `.k` and `.meta` in Geist sentence case (Check your work's "Show" / "Order", "Module 1 pace",
  "These cost the route"); `.num` at weight 600 (the Summary and challenge figures set only their size).
- Already in place, no ask: `foldOff()` covers `?print=1`.

## For the user

- Details column: opens by itself in practice from 1280 wide (not beside an R&W passage under ~1366); closing it keeps it closed. Keep the default open?
- Explanations: one toggle. Misses, sure misses, guesses and "Always open explanations" open it (still collapsible); a right answer's stays closed unless you left one open before. Inline, the mastery line now sits with the other tail lines below the mistake lines.
- The test window's progress strip now sits on the top bar's edge (it already existed; Bluebook has only its dashed line there).
- On a phone the strip is a hairline: a tap on it opens the navigator (as the test window already did) instead of picking a segment.
- "Begin without fullscreen" moved from beside the primary into the quiet links row under it.
- A paused test's lobby says "Practice test #3, paused" in the h1 (the "Paused" kicker is gone).
- Summary inside the app shell after a set (sidebar visible): say if wanted.

## Polish round

Files touched: `web/assets/runner.css`, `web/assets/runner.js`, `web/challenge/index.html`, `web/test/index.html`,
`web/test/test.js`. question.js unchanged (its Explanation already uses `UI.tabs`, so it slides for free).

### First screen

**Practice session (1440 and 390).** The answer states now read in order. A pick is the orange edge on paper with its
letter filled ink (Bluebook's filled bubble; was an orange letter, the same as a right answer's), so before Check
nothing on screen looks like a verdict. On Check the right option turns orange (wash fill, orange letter, check) and
a wrong pick keeps an edge, now ink, with its cross, its struck line and "Your answer" in ink (was a tile with a faint
letter, about as quiet as the faded options around it). The running count beside the title ("2 right · 3 in a row";
the phone's line under the bar) rolls a digit when it changes; the first paint and a count that just appears are
plain. The 1280+ side column's tabs are the shared tabs: one underline slides between Details, Reference, Notes and
Entry rules, arrows and Home / End move between them, the notes count is a badge, a fourth tab scrolls with a soft
edge; the tab text sits on the body's 12px edge.
**Test window.** Picks look the same as in practice (orange edge, ink letter). Settings: Timing is a list of
`.choice-row` rows (name left, minutes right; selected is the orange fill and ring) instead of tile boxes with radio
dots and a second line.
**Save and next sets (end mode).** A saved grid-in entry has the orange edge, as a saved choice does (was an ink ring,
the same as the field's focus ring).
**Inside a card elsewhere** (Today's question, the Review pane, See one solved, a twin tile): the Explanation sits under
one hairline with no tile box of its own, its steps on the verdict's left edge. On the session page (paper) the card
keeps its tile.
**Challenge.** Today / Yesterday (and a dated day from `?day=`) is a `UI.seg` with the sliding thumb (was a hand-built
chip group). Your row on the board is the wash with a 2px orange bar on its left edge (was a ringed, rounded box inside
a hairline list).
**Summary, lobby, between modules, diagnostic.** Unchanged this round.

### New components added

- `UI.roll`: the practice runner's running counts (`paintCounts` in runner.js: one span per count, keyed by its word,
  rolled only when the same count changes on screen). Replaced a joined text string.
- `UI.tabs` (+ `UI.edgeFade`): the runner's right slot. Replaced the hand-built `role=tablist` that was rebuilt on every
  paint; one instance now lives until the set of tabs changes, so the mark can slide.
- `UI.seg`: the challenge's day switch. Replaced `.choices.days` and its click handler.
- `.choice-row`: the test settings' Timing list. Replaced `.tw-radio`.

### Removed local copies

- test/index.html: `.tw-radio` and its five child rules (kept `.tw-radios` as the list, plus one `.off` line).
- runner.css: `.rn-slot-tabs` tab styles (`[role="tab"]`, selected colour, its own `::after` underline, scrollbar
  rules); `.rn-slot-tabs` is now only the flex wrapper (`min-width: 0`).
- challenge/index.html: the two hard-coded day buttons, `pick()`, the delegated click listener.

### Not done

- Summary roll: its figures arrive once from `/finish` and nothing changes after the paint, so a roll there would be a
  load animation (banned). Nothing on the lobby, between modules or the challenge changes on screen either.
- The footer's "3 / 10" and the question number do not roll: they are a position, not a count, and would move on
  every Next.
- Training's Sure / Unsure / Guess stays chips: tapping the pressed one clears it, which `UI.seg` cannot do.
- The navigator's view switch is already `UI.seg` (slides); its round-one local size override (12.5px, 9px padding)
  stays so the six views fit one row.
- Check your work's tiles stay pressed `.stat` buttons (they are filters, not a single choice).
- Inside the Explanation the type line, the step numbers (10px, the diverge box's padding) and the tab text (12px, the
  shared tablist's padding) keep three left edges, as before this round; pulling the tabs out with a negative margin
  would push their hairline past the one above the Explanation. Left as is.

### Shared asks

- kit.js `slideMark`: the selected tab or option goes to weight 600 (ui.css `.tablist [aria-selected]`, `.seg
  [aria-checked]`), which widens it; the ResizeObserver then runs `place()` with `slide` false in the same frame and
  sets `transition: none`, which cancels the slide the click just started. Every `UI.tabs` / `UI.seg` click probably
  jumps (jsdom has no layout, so the smoke cannot show it). Keep the transition while a slide runs (remember when it
  started and skip `transition: none` for 200ms), or hold the selected weight at 500 (INSPO-VISUAL 3 row 9).
- ui.css `.tablist.sm` for a narrow column (12.5px, 8px padding, `.tab-ind::after` inset 8): the runner's 300px slot
  fits three tabs at the shared density; Details + Reference + Notes + Entry rules scroll.
- ui.css `label.choice-row:has(input:disabled)` (faint, default cursor, no hover): test/index.html keeps
  `.tw-radios .off` until then.

### For the user

- A picked answer is the orange edge with its letter filled dark (as in Bluebook); Check turns the right one orange.
  Your wrong pick keeps a dark edge with the cross and "Your answer".
- A saved grid-in answer in a Save and next set now has the orange edge (was the dark focus ring).
- The practice side column's tabs are the app's standard tabs, a little larger: on a grid-in from 1280 wide the fourth
  tab (Entry rules) scrolls into view. The notes count is a small badge on Notes.
- Challenge: Today / Yesterday is a segmented switch; your row on the board has an orange bar on its left edge.
- Test settings: the timing choices are rows (name left, minutes right) without the radio dots.

## Premium build (part 1)

Files: `web/assets/runner.css`, `web/assets/runner.js`, `web/assets/question.js` (the split Check's tooltips only),
`web/practice/session/index.html`, `session.js`, `web/test/test.js` (keys sheet copy), `web/challenge/index.html`,
`web/diagnostic/index.html`, `signup.html`. Part 1 only: layout, the heroes, the open bugs, the items that need no
new shared JS. No motion, feedback moment or icon swap yet (part 2).

### First screen, before / after (counts at rest)

- **Practice, math MC, 1440x900.** Buttons 28 + 10 rail segments -> about 24 + rail: the strip 6 icon tools -> 5
  (Mark, Eliminate, Highlight, Note, Details); Hide shows only on the clock's hover or focus (a hidden clock's Show
  always shows; touch keeps it); the Details column 6 buttons (3 tabs, close, 2 Copy) -> 5 (3 tabs, close, the
  "Question info" fold; Copy lives in the fold). Key chips 3 -> 0 (they show on hover and focus, and all the time in
  a learner's first 3 sets). Details labels 10 -> 2 before the answer (Why this one, You and this type). Bars 2 -> 1
  (the stopwatch's bar from half the budget; its time stays). Boxes: the Details card box and the ink number tile
  are gone (a well with an ink figure); one raised sheet holds the question.
- **Practice, 390x844.** Buttons about 20 -> 14 before a pick: the strip's 5 labelled tools -> Eliminate and Note
  as 44px icons on the number's row (the tools row is gone, the stem moves up about 50px); the footer is one row
  (Back, Mark, 3 / 10, Sure) until there is an answer, then Not sure and Guessing join above it (was two rows, ~128px).
- **Test window, 1440.** Buttons 18 -> 15, badges 1 -> 0: the question bar is Bluebook's (Q number, Mark for review,
  Eliminate); Save and Report went to More, "Add a note" under every question went (More, Notes; the O key), the
  Ranked / Training badge is the title's tooltip and More's first line.
- **Summary, 1440.** Buttons about 22 -> 16: the next row is one pill, one `.btn` (Same settings) and More (was a
  pill, up to 3 buttons and More); the Review list's up to 8 filter chips are one "Show: All" menu. 390: 5 stacked
  full-width buttons -> the pill, then Same settings and More on one row.
- **Challenge.** The head is one hero (the rank or today's count, its meta line, Start); the day switch and the
  board sit 32px under it. **Diagnostic.** The h1, meta and Start are one hero with a dimmed sample band.

### Heroes

- **Practice: the question sheet.** From 760 wide (not beside an R&W passage) the page is `--page` and the
  question (`.rn-q`: stem, options, Hint and Skip, the verdict) sits on a white sheet, 14px corners, `--shadow-3`,
  24px under the strip. The strip, the rail and the footer stay outside it; the Details column sits on the page
  with no box. The options are raised keys (white, a line edge, a 1px warm foot); a pick sinks in with the orange
  edge and a 3px wash halo; right floods the wash; your wrong pick keeps its ink edge. Phones and R&W passages keep
  one flat paper page (Bluebook's). The top bar and the footer are flat at rest and lift only while the question
  slides under them (CSS scroll-driven, practice only; no support means flat). A faint edge on question figures.
- **Summary: the score card** (`.card.hero`): the score at `--fs-hero` in `--ink-strong`, the first-try line (a
  clean set says "10 of 10, first try"), the set's own strip as the receipt (`UI.strip`, status, marks, notes),
  time and pace as two figures ("11:45 in all", "0:50 a question · pace 1:00"), then the date line. What changed
  sits under the card, flat (760-1099: beside it, the user's earlier ask). Groups 32px apart; the page is warm.
- **Between modules (test):** the countdown is the figure: "Module 2 starts in" then 0:48 at 44px.
- **Challenge:** the rank or the count at `--fs-hero`. **Diagnostic:** a dimmed 480-680 band on the 200-800
  scale ("Example") under Start.
- **Test window:** no depth on purpose. Bluebook's ink number box and ink "Question 7 of 22" button.

### What moved behind which control

- Practice strip: Report (R) and Attempt history (Y) -> More, "This question" (desktop and phone). Phone also:
  Highlight (L, a checkbox item) and Details (V) -> More. The set's items are under "This set".
- Details column: Skill, Question type, Difficulty, Format, Question ID, Link -> the "Question info" fold (open state
  remembered, `satf.qinfo`); Everyone and Formula show after the verdict (as before, the verdict's tail joins it).
- Test window: Save to Review (a checkbox item) and Report -> More, "This question"; "Add a note" -> More, Notes
  (and O); the Ranked / Training chip -> the title's tooltip and More's first line.
- Phone: the question type (`.rn-type`) leaves the strip under 760; it is in Details (More).
- Summary: Fix my misses and SAT words · n due -> More (Fix stays the pill's when the next set is the fix set);
  the filter chips -> the "Show" menu (same filters, same counts, radio items).

### New motion and feedback moments

None in part 1 (part 2, on the shared motion API). The only movement added is scroll-linked: the practice bars'
shadow while the question slides under them.

### Icons changed

None in part 1 (part 2). The More menus now pass the runner's own icon nodes, so Notes, Scratch and Report no
longer draw an empty slot where kit's map had no such name.

### Bugs fixed

- 5: after Check the verdict's head scrolls into view (`block: nearest`, 96px above the footer; smooth unless
  reduced motion), then focus goes to Next as before. Practice only.
- 12 (my part): the between-modules bar scales (`transform: scaleX`) instead of animating `width`.
- The lead's: the challenge "you" row has no side stripe (wash, the rank amber-deep, the name 600, same height); it
  sticks to the top or bottom edge when scrolled off (the phone's bar and tabs counted). The two ink focus outlines
  (`.step`, `.rn-seg`) are gone; the shared amber-deep ring draws. Pressed tools lost their 2px amber underline
  (the selected fill and an amber icon; Mark's wash is the selected fill too); the prediction grid's dashed ink
  outline and the highlight picker's ring are the one selected look (`--sel-bg` + `--sel-edge`).
- Found: the test's keys sheet listed Z as Save to Review; no such key exists (Z is the global Undo). It now says
  Save and Report are in More.
- Found: the challenge page crashed when `/api/challenge` had no board or day (the smoke failed on it); guarded.
- Warm page: `.rn-exit` and `.t-hide` hover use `--hover` (the tile vanished on the Summary's page-coloured bar);
  the Summary's row and fold hovers too; the side column's note rows are white keys on the page.

### Inventory diff, accounted for

Smoke `page.js` at 1440 and 390: practice/session, test, diagnostic, signup, verified as before (session and test
need a session the fixtures lack; signup's navigation note is jsdom's); challenge now passes (it crashed before).
`inventory.js`: diagnostic adds `doorSample`; nothing else changed (the session and test pages render no runner
there). A fixture harness with a practice set, an answered question, a finished set's Summary, a live test, its
lobby, between modules and the challenge boards (scratchpad `runner/harness.js`) shows these and only these:
- Practice: "Report a problem with this question" and "History 1" (ids `reportBtn`, `attemptsBtn`) leave the strip:
  More, "Report a problem" (R) and "Attempt history" (Y). The elements still exist detached; no file references
  the ids. Phone: Highlight and Details are in the DOM, hidden under 760; More lists them.
- Test: "Save", "Report a problem with this question" (ids `saveBtn`, `reportBtn`) -> More; "Add a note" -> More,
  Notes and O. No file references the ids (words/run has its own `saveBtn`).
- Summary: chips All, Incorrect, Marked, Slow, Has note -> the "Show: All" menu; `/words/` -> More's "SAT words".
- Removed CSS with no element left: `.rn-cond`, `.rn-addnote`, `.rn-qhead [data-tool="report"]`, `.sm-filter`.

### Not done (part 1)

- Motion, feedback and icons: the answer stamp, the rail's fill and sliding marker, the Summary count-up, the flame
  chip, mastery roll, the drawn verdict disc, the X on Exit, the confidence trio as one split shape, spot drawings
  (Paused, empty Notes, the challenge's empty board) and every ✓ ✕ ▸ ▾ glyph: part 2, on the shared API.
- R&W practice: the passage pane and the question as one sheet. They are two sticky grid columns; they keep one
  flat paper page with the divider (Bluebook's) for now.
- The scroll shadows use CSS scroll-driven animation; when `UI.scrolled` (A2) lands, part 2 can switch to `.scrolled`.
- The 60 s clock pulse stays in the test window (MOTION 3.9 keeps it; AUDIT 12 asked to drop it).

### Shared asks

- None blocking. Relied on A1: `.card.hero`, `.hero-num`, `--fs-hero`, `--ink-strong`, `--page`, `--raised`,
  `--shadow-3`, `--shadow-scroll`, `--hover`, `--sel-bg`, `--sel-edge`, `--edge`, `UI.strip` (kit) and `UI.scale`.

### For the user

- Practice from 760 wide: the question sits on a white sheet over the warm page; options are raised keys. Phones
  and R&W passages stay one paper page.
- Report and Attempt history moved from the strip into More (keys R and Y unchanged); on a phone Highlight and
  Details are there too. In the test, Save to Review, Report and the Ranked badge left the question bar (More).
- The Details column shows two rows before you answer; the rest is under "Question info".
- Key chips (Enter, ⇧Enter, I) show on hover and focus after your first 3 sets; every key is in the tooltips.
- The question stopwatch's bar appears from half the budget; its time always shows.
- Summary: one pill, Same settings and More; the filters are one Show menu.
- The test window changed in three quiet ways: Bluebook's ink number box and ink "Question 7 of 22" button; a pressed
  tool (Highlights & Notes, Scratch, Calculator, Reference, Eliminate) is a soft selected fill with an amber icon
  instead of an amber underline; Save, Report and the badge left the question bar.
- Question figures in practice get a faint 1px edge. A figure that draws its own frame would show two: look at a
  graph question first and say if it should go.

## Premium build (part 2)

Files: `web/assets/question.js`, `runner.js`, `runner.css`, `web/practice/session/session.js` and `index.html`,
`web/challenge/index.html`, `web/diagnostic/index.html`. (`web/test/test.js`'s dot fallback was already changed by
the lead; nothing else in the test page moved.) No browser; jsdom harness and the smoke only.

### Shared controls adopted

- Twin is the shared `.split-btn` (one shape, the edges merged, `caret_down` that turns while its menu is open).
  In Review's pane it steps down to a `.btn` while Review's own action bar shows (a MutationObserver on `.rh-bar`;
  it returns to the pill when the bar empties); `rv-next` stays `.btn` in the pane. The pane (`.rv-pane` in
  `.rh-pane`) gets no frame or raise from runner.css.
- Busy states: the Summary's next set, Keep going, the button beside it and Fix now carry `aria-busy` (A1's
  spinner after 300ms at the same width) and keep it while the next set loads; a failure clears it.
- Sure, Not sure and Guessing read as one control on desktop (one shape with dividers).
- Key chips: after a learner's first 3 sets they are a small keycap that floats above the button on hover or focus
  (0.4s), so the buttons no longer carry blank room at rest. Next's arrow nudges 3px on hover (practice).
- Menus and menu triggers: the Summary's More and Show use `caret_down` (turns open); the review player's
  "Tools ▾" band is one icon button (`.ibtn`, `more`) in the head: in Review's pane it sits in the question's
  top-right corner and the band appears only while the tools are open.
- Scroll shadows: the practice top bar and footer and the Summary bar use A2's `data-scrolled` (`.scrolled`); the
  part 1 scroll-timeline CSS is gone.

### Motion and feedback (practice only; the test window gets nothing new)

- Answers that land (question.js, a fresh verdict only, never a revisit or restore): right, the key fills (its
  transition), its letter pops once (`UI.fx.pop`) and its check draws (`UI.fx.check`); wrong, the pick dims and is
  struck and its cross draws, the key fills beside it; no shake. The verdict's disc draws its mark. The
  rail's segment for that question fills left to right in 220ms as the verdict lands.
- One current marker slides along the rail from question to question (180ms); the test window's strip is still.
- Streak: from 3 in a row the count carries a flame (filled amber); at 3, 5 and 10 it fills and pops once.
- Mastery moves: on a fresh verdict the bar slides old to new (600ms after 150ms) and the word changes as it
  lands (Developing to Proficient).
- Next, Back and a jump by pointer: the question rises in 4px over 140ms (desktop; keys stay instant, the phone
  keeps its swipe slide).
- Summary, once per finished set on this device (`satf.sumseen`): the score rolls up (`UI.roll`), the receipt's
  cells fill 30ms apart, the done drawing's corners fill in; a later view is still. The Show filter glides
  (`UI.glide`); the breakdowns open in height (`details.fold`): they are filled when the Summary paints, so the
  height is known; Time per question keeps its first-open fill (its chart measures a visible box) and opens
  without the height motion. The Summary's next row (the pill) is never delayed by the page entry (`data-m-now`).
- Page entry (`data-m="stagger"`): the Summary's lead column, the challenge page (the hero holds Start), the
  diagnostic door. The challenge's day switch glides the board.
- Exit's X turns a quarter on hover (practice and the Summary); "Your rule" opens in height (not in the test).

### Icons and illustrations

- runner.js's `RI` and question.js's `I` maps are gone: both draw `UI.icon` (UI.qicon stays its alias).
  question.js `chev` -> `caret_down` (Why each wrong answer, the twin caret); the calculator's close is the shared
  `x`; More menu items pass the runner's icon nodes.
- Option marks and the verdict glyph are drawn `check` / `x` icons (they draw in); the verdict is a 24px disc
  (amber with a dark check, an ink ring with a cross, a dashed ring for blank). "New best on this type" is a quiet
  badge with the trophy.
- Mark for review is an `aria-pressed` button with the flag's filled twin (practice strip, the phone footer, the
  test's question bar); the three CSS fill rules went. Text triangles: "Your rule" (▸ ▾), the attempt history's
  "▸ 3 tries" and the review player's "Tools ▾" are drawn carets or an icon now. ✓ ✕ inside text stay (Marks).
- `UI.spotArt('done', ms)` sits in the Summary's score card: the four domains' mastery from the shell's fresh
  copy. The Paused screen shows the pause icon in a 64px ring.
- session.js draws nothing for an unknown icon name (was the orange dot).

### Bugs fixed

- Found in review of this part: the pane's Twin stayed orange on its first paint while Review's bar showed (the
  action row is built before the workspace joins the player); the step-down now looks in the new row too.
- The quiet Next of a Save and next set anchors its floating key chip (it is positioned now).
- A double turn: `.split-btn`'s `transform: rotate(180deg)` plus icons.css's `rotate: 180deg` on `caret_down` would
  turn the twin caret back to closed; the twin's caret drops the transform (see Shared asks).

### Inventory diff, accounted for

The harness and `inventory.js` show nothing new against part 1 (the same moves). The challenge's inventory now
lists Start: the page no longer crashes on the stub (part 1's guard). Smoke: practice/session, challenge,
diagnostic, verified, review, results/report clean; test and signup keep jsdom's navigation note (as before).

### Not done

- The R&W passage and question as one sheet (part 1's note stands).
- Spot drawings on the challenge's empty board and the empty Notes tab: A3 keeps spots to first use, all clear,
  404 and done; the board keeps its dimmed sample row.
- The test window's finished card (`done()` in test.js) without a spot: it shows only for contests, the route
  trainer and flagged questions, and its payload carries no domain mastery.

### Shared asks

- ui.css / icons.css: the twin fill's 150ms fade (`g.ph-f`) also runs in the test window on Mark and the top-bar
  toggles; `body[data-page="test"] { --i-t: 0ms; }` would keep MOTION 3.9 literal (nothing moves there).
- ui.css: `.split-btn > [aria-haspopup][aria-expanded="true"] > svg { transform: rotate(180deg) }` turns any
  `caret_down` back to closed (icons.css already turns it with `rotate`). Drop the transform there, or scope it to
  svgs without `g.ph-turn`. runner.css works around it for the twin only.

### For the user

- A right answer now lands: the letter pops, a check draws, the progress segment fills. A wrong one draws a cross
  on your pick; nothing shakes. The test window has none of it.
- The rail has one sliding marker for the current question; from 3 right in a row the count shows a small flame.
- The Summary's score rolls up the first time you see a finished set, with a small drawing of your four domains
  beside it; later visits are still.
- Key chips float above the buttons on hover after your first 3 sets (they no longer leave blank space).
- In Review's pane, the tools are one icon in the question's corner; Twin is quiet while Review's own bar shows.
- The Summary's drawing sits in the score card's top-right corner. The breakdown folds open in height; if By skill
  or another one snaps or jumps in a browser, say so and it goes back to opening at once.

## Visual review

Three rounds in my own headless Chromium against the DB copy (learner a:v2revresults01; a fresh learner for the
diagnostic gate): 1440 light, 1440 dark, 390 (touch, coarse pointer), with hover, Tab focus, press, a pick, a right
and a wrong answer frozen at 120ms (every running animation paused) and after, menus, the navigator, a sheet.
Shots: `premium/shots/app-review/runner-r0-*` (before), `runner-r1-*`, `runner-r2-*` (after). Scripts in the
scratchpad `rn/` (practice.js, summary.js, test.js, review.js, review2.js, pages.js, quick.js).

### Per screen

- **Practice question (sheet, raised keys).** Verdict: premium at 1440, dark and 390 after the fixes. A pick is one
  amber edge (the 3px wash halo made a double ring; the Practice reviewer's ask); a picked option that also has
  keyboard focus shows one deeper amber-deep edge instead of the edge inside the focus ring (quick sheet too). The
  disabled Sure's keycap was invisible in dark: disabled split-check keycaps are outlined now.
- **Answer feedback.** Right at 120ms: the key fills, the letter pops, the check draws, the rail segment fills, the
  count rolls; purposeful, nothing shakes. Wrong: your pick was a 1.5px ink box (a white box in dark), now a faint
  edge with the struck line, the cross and "Your answer". Each option's line now sits under the option's text (64px,
  was 46: a third left edge); your pick's line is no longer bold (the verdict says it in bold right below); "Practise
  this trap" is quiet (500, soft) instead of four bold ink links. "Sure, but wrong" is plain text (was an ink-bordered
  box). What happened? chips sit in three even columns in the runner's sheet from 760 (the fifth wrapped alone; inline
  cards elsewhere keep wrapping, they are narrower). The Explanation inside the
  white sheet is flat under a hairline (it was a grey box in the sheet); phones keep it on paper.
- **Verdict actions.** Twin is a `.btn` in the practice runner (`ctx.surface === 'runner'`), so the footer's Next is
  the one orange; Review's pane and inline cards unchanged. Its caret turns once without runner.css's workaround
  (line removed; ui.css now skips drawn carets).
- **Rail.** One sliding marker, the segment fills on the verdict; the test window's strip stays still. Good as was.
- **Phone practice.** The tools under the options (Cover choices, Read aloud, Calculator, Reference) were four grey
  tiles in two rows; now quiet icon-over-label tools in one row, like the top bar's (the test window's two too). The
  footer's keycaps are hidden on touch (`.rn-foot .kbd` joins the `hover: none` rule).
- **Summary.** The Review list's 40px solid status tiles became the 28px cells (`size: 'sm'`), rows 44; the level
  ("Easy · L2") is gone from the rows (internal calibration stays off screen, as in the strip). The lead column is
  380 wide so the fix-set pill keeps one line (it wrapped "min" onto a second line, 2 lines tall). More and Show use
  ui.css's drawn caret (their own `caret_down` svg dropped). The roll, receipt fill and done drawing read as a reward;
  no change there.
- **Test window.** Calm and Bluebook-faithful: flat options, flat pills, nothing moves on pick, mark or Next (shot at
  60ms). Fixed: the navigator's "Go through 22", the directions sheet's Close and the lobby's primary carried the
  practice pill's sheen (dialogs and popovers live on body, outside `.rn-exam`): `body[data-page="test"] .pill` is
  flat too. The lobby, time-up and hand-in screens focus their button on load (Enter goes on) but no longer draw the
  ring until a key moves focus (`quietFocus`, `data-quiet`; FocusOptions.focusVisible is not in Chromium). The
  lobby's four quiet links sit in two columns (the fourth wrapped alone), weight 500.
- **Review's pane (runner.js / runner.css only, Review's files untouched).** The status chip wrapped alone onto line
  two: the skill takes the room and the type is its own line under it (no line starts with "·"). The Review
  reviewer's six: a tags-only facts panel ("New") is plain chips, also when the rest is held back before the reveal;
  the Fixed line in the pane is "Fixed date" over the name (no leading "·"); the History heading hides with its
  timeline; the cause chip's dot hides with the chip (no trailing "·"); the Q1 chip is a quiet neutral badge (was
  ink, mono); the timeline's arrows end a line instead of starting one, and the number-less cells centre their glyph
  (ui.css's new `.cell:has(> .n:empty)` rule; my duplicate went). The head's `L5` level is gone too. On a phone (the dialog) the type
  is its own line as well; the status chip then sits on its own row under the skill, left-aligned, which reads as
  intended.
- **Challenge (`web/challenge/index.html`).** The route 307s to `/compete/contest/?id=daily` (server/api_compete.py
  849), so this page is reachable only as `/challenge/index.html`. Your row: the wash band, rank amber-deep, name 600
  and a "You" badge, same height, no stripe (there was none in the file; the badge is the lead's ask).
- **Diagnostic, sign-up, verified.** Calm. Each had two oranges (the sidebar's and the phone strip's Up next Start
  beside the page's own): `UI.shell({ ownPrimary: true })` on all three.

### Bugs found

- kit.js `roll()`: a local `off` shadowed `off()`, so every count change threw "off is not a function" and the
  practice runner stopped after a right answer (footer stuck on Sure, counts frozen). Already fixed in kit.js by the
  time of round 2 (`shift`); re-checked with no harness patch.
- On the phone a full-page screenshot resets Chromium's touch emulation, so a keycap can appear in a phone shot taken
  after one; real touch hides them (checked with `matchMedia('(hover: none)')`).

### Checks

check-ui.py ok; `node --check` runner.js, question.js, session.js, test.js and the four pages' inline scripts ok; no
em dash in the touched files; smoke page.js at 1440 and 390 for practice/session, test, challenge, diagnostic,
signup, verified, review: as before (test and signup keep jsdom's navigation note); the runner fixture harness
(24 scenarios) shows no inventory change, one text change: "AzizYou" (the You badge).

### Shared asks

- None blocking. Optional, ui.css: `.pill:disabled .kbd` reads `--ink-deep` on the grey disabled fill, invisible in
  dark (runner.css fixes the split Check only); and the generic `:focus-visible` ring on an option that is already
  picked (runner.css merges them for `.ws .opt`).
- For the lead: `/challenge/` redirects to the contest page, which drops Today's `?day=` deep link; either the
  redirect or web/challenge goes. Not the runner's: the contest page shows "null" under Other days.

### For the user

- Practice: after a miss, Twin is a white button; Next is the only orange. Your wrong pick has a light grey edge
  instead of a black box; the trap lines under the options are lighter.
- The Summary's list uses small status squares and no longer shows the level (L2, L5).
- Test lobby: no focus ring around the start button when the page opens (Enter still starts).
- Review: the question number is a light grey badge instead of a black one.

### Round 3

Shots `premium/shots/app-review/runner-r3-*` (practice at 1440, 1440 dark and 390; Review's pane).
- Each option's reason line is just the reason (and "Practise this trap"): the letter and the raw value ("A · w^2 +
  4w · ...") repeated the option right above it, unrendered. The same change shows in Review's "Why each wrong answer
  is wrong" (the options sit above their lines there too); "Your pick · " stays on your own pick in Review.
- Under the verdict, a mistake that closed is one line: "Fixed · <mistake> · check-in in 3 days". The server's next
  step ("That closes it: <mistake> is fixed · a check-in comes back in 3 days") no longer prints under it.
- Found while checking: after a wrong pick the bold mistake line under "Incorrect" repeated your pick's reason line
  (it differed only in its capital letter, so the "already under its option" check missed it). Compared without
  case or a full stop now; it still shows with a trap chip or a trap check, or where option lines are off.
- See one solved: the trap's value is rendered with the options' formatter ("Here it gives w²"), and the example's
  caption says "Your mistake lands here" (the value sits right above it).
- Checks: check-ui ok, `node --check` question.js and runner.js, no em dash, smoke practice/session and review clean,
  the runner harness's answer, session and summary scenarios show no inventory change.
