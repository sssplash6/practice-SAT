# Pass: Review and Mistakes (web/review/**, web/mistakes/)

Files touched: web/review/index.html, review.js, sheet/index.html, sheet/sheet.js, walk/index.html, walk/walk.js,
print.html. Not touched: item.js (only EVENT labels; left), mistakes/index.html (a redirect; nothing to redesign).

## First screen

**Review hub, 1440x900** (sidebar Now block shows from 700px tall, so no Now strip).
Now: one header row (Review, Start review split button on the right), the new-misses line if any, a 40px tab row
with counts inline, the open tab's sub-line, one closed Insights toggle, the filter row (Search, Status, Sort,
Filters · n), then the list column (380px, sticky, own scroll) beside the question pane. List and pane start at
about 280px (were about 1000 and 1100 on Redo). Moved out of the way: the minutes seg (into the Start ▾ menu with
"See the list first"), the six 80px tiles (now tabs; their sub-lines are each tab's title and the open tab's line),
the Why / Worth / Habits / Instincts / Right but slow / chart cards (one closed Insights disclosure per tab), the set
options box (behind Options in the action bar), seven of ten Redo filters (behind Filters · n), the six secondary
list actions (a More menu in the list head).
**Review hub, 390x844.** Now: header row (title and Start split side by side), the new-misses line, sticky tabs
(label over count, 48px, under the phone bar with the safe area), the sub-line, Insights toggle, Search plus
Filters · n, then the rows, vertical. First row at about 420px (was past 1300). Bottom padding is reserved only
while the action bar shows.
**Worksheet answers.** Leads with the back link, title and ⋯ on one row, the count line, then the answer rows
(hairline rows, no tiles). From 1280px Minutes taken, the count and Submit sit in a sticky right column; below
that Submit stays in the sticky foot (now clear of the tab bar on a phone).
**Walk.** Back link and title on one row, the counts, one card with Resume the walk. The always-on explainer line
is gone (it was replaced by the counts on load anyway).
**Print (trap sheet, error log).** Back link and title on one row, the date and count, Print / Save as PDF, content.

## Big changes

- The question list is a vertical list again at every width, with each row's status tags and its meta line
  (skill, level, last date, source, picked, points) visible. From 1280px it is a column beside the question pane.
- The six stat tiles are a tab row with the counts inline ("Redo 23").
- Start review is one split button; its ▾ holds "See the list first" and the minutes (5 to 60, All).
- The insight cards on each tab (Why you lose points, Worth the most, Habits, Your instincts, Right but slow, the
  made-and-fixed chart and forecast) sit in one closed "Insights" toggle per tab, remembered open or closed.
- Set options (Questions, Clock, Feedback, Each, Level) open from an Options button in the action bar.
- Filters: Search, Status and Sort stay in the row; the rest are behind "Filters · n" on desktop too.
- The list's secondary actions (Walk these, Drill my blind spots, Print worksheet, Ask for help, Share, Error log,
  Same questions again, Unmark, Unsave) are in a More menu in the list head.
- One orange button per screen: the action bar's when it shows, otherwise Start. Walk them, Rematch, Worth the
  most, Final check and Fluency sprint are grey buttons now.
- Rows are hairline rows inside one bordered list, not filled tiles; group, day and sitting heads are row headers.

## Bugs fixed

- Dark mode worksheet: answer bubbles, grid-in and minutes inputs and the sticky foot used `var(--bg, #fff)`
  (white with light text). Now `--paper` / `.field` / `--on-ink`.
- `--ink-soft` (defined nowhere) in sheet, walk and print: now `--soft`. `var(--bg)` on the rules textarea and the
  undefined `--bar-h` are gone too.
- The worksheet page reused `.ws` (the question workspace root): 120px under every printed key question and the
  fold guard switched off for the whole page. Renamed the page's classes to `wks-*`.
- "Why you lose points · last 30 days" counted every open mistake (the first 100): now "Why you lose points ·
  open mistakes". Server data unchanged.
- The list hid its tags and meta at every width (audit I4); sitting cards nested a second sideways scroller (I5).
- Phone sticky tabs ignored the notch inset (I6); the pane drew two edges (I7); the sheet foot sat 2px under the
  tab bar (I8); set options and their Start were a whole list apart (I9).
- Mistake statuses on the pane's strip and legend (open, half, relapsed, stuck, sure, unchecked, due, held,
  dismissed) are page-local `--st-*` values instead of raw fills, and now also apply in the phone's player dialog,
  which sat outside `.rh-pane` and got no styling.
- U+2014 placeholders (the duration fallback and the loading tab count) are en dashes.

## Ranked proposals

1-7 done (list beside the pane; header row; tab row; Insights fold; Options in the bar; filters folded; one
primary). 8 copy pass done: Walk N misses, Rematch, Fix N, Redo N blanks, Final check · N · about M min,
avoided in N other types, Practise N new versions, Same questions again, Nothing open, Step 2 of 4, Misses are in
Review; glyphs dropped from labels (Check-in ✓, Sure ✕ is now Blind spot, Half fixed ●○, Then → Now, ▲ is
", over", ▸/▾ n tries is "n tries" / "Hide n tries", Learned ✓, Held ✓); the praise line on Fixed is gone.
9 token fix done. 10 type scale done (h1s use `.h1`, no local 36/32px, `.rh-k` 14/600 sentence case, l1 14.5,
metas Geist). 11 phone done except the one-line bar (Not done). 12 already covered by the shell (ui.js `here1`).
13 cleanup done (dead CSS, about 25 inline styles, 999px chips, the 40px split pill). 14 done (back links inline
as `.quiet`; the sheet's sticky right column).

## Not done

- Phone action bar on one line (P11): the summary carries figures (selected, types, questions, minutes); one line
  would truncate them. It wraps instead, with Options and the primary on the row under it.
- Exam-week line keeps "Your SAT is <date>" (audit E said drop it): a phone has no sidebar Now block, so it would
  be the only place left on this page. The line is now one row with Final check and the trap sheet link.
- The list head keeps "N of N selected" beside the bar's "N selected": it is the label of the select-all checkbox.
- The sheet's right column is page-local, not `.twocol`: below 1280 `.twocol-side` would hold the Submit foot and
  its sticky would stop working over the answer rows.
- item.js story labels ("clean ✓", "Check-in ✓") and the Fixed row's proven-level ✓ / ○ marks stay: they are
  state marks, not decoration.
- The closing-row exit animation in paneOn.closed still writes `.style` (it needs the row's measured height).
- History, Marked and Saved have no Status or Sort filter, so only Search stays in their row.

## Shared asks

- tour.js `review` step 1 (`#start`): "Choose how many minutes you have, then Start." The minutes are now in the
  Start ▾; suggest "Start today's review. The ▾ sets the minutes and shows the list first."
- runner.js pane mode: the footer's `.pill.sm.rv-next` makes a second orange button beside the page's primary at
  1280px and up; in `mode: 'pane'` it could be `.btn.sm`.
- kit.js `UI.filterBar`: an option to keep chosen keys in the row (for example `keep: ['status', 'sort']`, adding
  `filters-keep`) and to show the Filters · n button at every width. Review now marks Status and Sort by matching
  `FB.el.children` to the defs by index (`.rh-fk`), which breaks if filterBar ever adds an element per def.
- ui.css: if other pages need the mistake statuses, move the nine page-local `[data-status]` rules from
  review/index.html into the `--st-*` block.
- Relies on the lead's in-flight changes: `.meta` and `.k` in Geist sentence case, `.badge` at 6px corners, `.h1`
  at 22/600. Nothing new needed in FOLD_SEL (Insights are page-local `details.fold`, which FOLD_SKIP skips).

## For the user

- From 1280px the question pane is about 650px wide beside the list (was the full 1040). R&W passages wrap
  narrower.
- On tabs where the action bar shows (Redo, Marked, Saved, Fixed with a selection), Start review turns grey and
  the bar's button is the orange one.
- Changing review minutes is one more tap (Start ▾, then the minutes).
- Print worksheet, Ask for help, Share and the Error log are one tap deeper, in the list's More menu.
- The worksheet's A-D answer bubbles stay round (marked `check-ui: round-ok`), as on the paper sheet.
- Renamed labels: "Twin this set" is "Practise N new versions", "Sure ✕" is "Blind spot", "Again, exactly" is
  "Same questions again".

## Polish round

Files touched: web/review/index.html, review.js, sheet/index.html, walk/index.html. Not touched: print.html, item.js,
sheet.js, walk.js, mistakes/index.html (a redirect).

### First screen

**Review hub, 1440x900.** Same order as round one (header with Start, notes, tabs, sub-line, Insights, filters, list
beside the pane). What changed in the look:
- The tab row is `UI.tabs`: one amber 2px underline slides to the open tab (it was a static ink underline), counts
  in the shared count pill (orange tint on the open tab), the shared tab size and focus ring.
- Rows: 40px minimum (one-line rows are 40; a row with its meta line about 56; was 52 minimum). The open row's bar is
  amber (was ink). Row actions (Learn this type, Note / Edit note, Unsave, n tries, Prove it at X, Reopen, Due's
  Not today ×) are hidden until the row is hovered or holds focus, and then sit over the row's top right end; before,
  each row with actions carried a blank 44px band under it on desktop. A hovered or focused row tints the same way.
- Difficulty is a chip row (Easy, Medium, Hard) in the filter row, orange while pressed; Status and Sort stay
  dropdowns (orange while set).
- Saved questions come first in Redo (inside each group), Fixed and each Marked sitting, each with a Saved tag;
  the list head says "N saved first" ("N saved" on Marked).
- While the page loads no tab reads as open (UI.tabs starts on one; review.js may open another).
- The action bar floats on `--shadow-float` (the small float shadow) instead of `--shadow-pop`.
**Review hub, 390x844.** Tabs keep one row of six (short label over the count), labels top-aligned so a tab without a
count lines up, and the underline slides there too. Row actions always show (touch), as before. Difficulty sits in
the Filters sheet as chips (was a checkbox list).
**Worksheet answers.** The focused answer row's bar is amber (was ink). **Walk.** The current dot's ring is amber
(was ink). **Print.** Unchanged.

### New components added

- `UI.tabs` for `#rhtabs` (mounted inside it; `#rhtabs`, `.rh-tabs`, `tab-<id>` ids, `aria-controls="panel"`, the
  counts, titles and aria-labels, arrows / Home / End and the click all kept). It replaces the hand-built tab buttons.
  The sliding `.tab-ind` comes with it. A click on the open tab still reloads it (a capture listener; UI.tabs ignores
  it). `UI.edgeFade` on the tab row (soft edges when the row scrolls sideways on a narrow desktop).
- filterBar `pills` for Difficulty (replaces the multi dropdown; same value list, URL and server parameter).
- Saved-first grouping (INSPO section 5, item 13): review.js `savedSet` / `pinSaved`, rows get `data-saved`.
- `.reveal` on Due's ×; the existing `.ract.reveal` actions now overlay instead of taking room on a mouse.

### Removed local copies

- review.js: the hand-built tab buttons and their keydown handler.
- index.html: `.rh-tab` button look, its ink underline, focus ring and hover, `.rh-tn` (count), the phone
  `.rh-tn:empty` spacer, the wrapper's own hairline and scroll (the shared `.tablist` draws them),
  `.rh-row.compact > .rh-rb` (now the base row). `role="tablist"` and its label moved from the wrapper to UI.tabs'
  element (one tablist, not two nested).

### Not done

- Rows exactly 40: a row with a meta line (skill, level, date, source, points) is about 56; hiding that line would
  drop figures. One-line rows are 40.
- Status as chips: filterBar chips are multi only, while Redo's server takes one status (Blind spots is a separate
  lens) and Fixed's status is filtered on the client as one value. Status stays a dropdown, orange while set.
- Saved first on History (a log by day or sitting; pinning breaks its order), Due (keeps the order today's review
  serves; its saved-deck rows already say Saved) and Saved (every row is saved).
- No "N saved" head row inside the list: in grouped Redo a second kind of head above the topic heads read as a group
  of its own; the count sits in the list head and each pinned row is tagged.
- A vertical edge fade on the sticky list column: it would fade the sticky list head.
- `UI.why` and `.choice-row`: nothing in these pages is a local `?` explainer or a row-shaped toggle (the Saved view
  and deck switches are `.seg`, the calibration grid buttons open History, Spot the trap's choices are one-shot picks).
- "Twin this set" stays: FOR-USER item 2 (the lead put "Twin" back until the user chooses).

### Shared asks

- kit `UI.tabs`: a shared-panel mode (today each tab's `panel` is hidden unless its tab is open, so one `#panel` for
  six tabs cannot be passed), a per-tab `short` label for the phone, per-tab `title` / `aria-label`, and an
  `onReselect`. Review now patches the buttons after UI.tabs builds them (`.rh-tk` / `.rh-ts`, `aria-controls`).
- kit `UI.filterBar`: a single-value chip type, so Review's Status (and Fixed's) can sit as chips.
- Server, later: a `saved` flag on /api/review/{redo,fixed,marked,history} rows. Review fetches
  /api/review/saved?limit=100 once (only when the student has saved questions) to know which rows to pin, so only the
  newest 100 saved questions pin (`ponytail:` note in review.js), and the first list paint waits for that request.

### For the user

- Review's tab underline is orange and slides between tabs; tab counts sit in small grey pills (orange tint on the
  open tab), as on other pages.
- Row actions (Note, Unsave, Learn this type, Prove it, Reopen, n tries, Not today ×) show when the mouse is on the
  row or it has keyboard focus, and always on a phone. While shown they cover the row's right end (its tags); in the
  narrow list beside the question pane, the end of the title's first line.
- Saved questions come first in Redo, Fixed and each Marked sitting, tagged Saved, with "N saved first" in the list
  head. The list's sort still orders each part. When you have saved questions, the first list on Redo, Fixed or
  Marked waits once per visit for the saved list as well (one extra request).
- Difficulty is three chips in the filter row on desktop.

## Premium build (part 1)

Files touched: web/review/index.html, review.js, walk/index.html, walk/walk.js, sheet/index.html, sheet/sheet.js,
print.html, web/mistakes/index.html. Not touched: item.js, runner.css (shared asks below). No git (the brief).

### First screen, Redo, 1440x900 (counted as the audit's section 1 did)

| | Before | After |
|---|---|---|
| Rows of controls before the first mistake | 8 (header, notes, tabs, sub-line, Insights, filters, list head, group head) | 5 (header, tabs, tools row, list head, group head); new misses, when there are any, are the list's first row |
| Controls, not counting the rows themselves | about 22 | about 17 (group Fix and fold show on hover) |
| Inputs on screen | 8 (Search, 7 ticked boxes) | 2 (Search, Select all); row and group boxes show on hover or once the selection is changed |
| Chips, badges, count pills | about 19 | about 8 (2 tab pills, one status badge a row at most) |
| Boxes | 6 (bordered list, 2 tinted group bands, pane, facts panel, floating bar) | 3 (the hero pane, its facts panel, the docked bar) |
| Meta lines a row | 2-3 (up to 10 facts, up to 5 tags) | 1 (tier bars, last date, points on the right) |
| Mistakes visible | about 4 (the bar covered the last ~70px and the pane's foot) | about 6-7, the bar under the list |

**390x844.** Header, sticky tabs, one tools row (Search, Filters · n, Insights), list head, the pinned new-misses
row, group head, rows; the bar is one line (about 60px, was about 110). About 3 mistakes above the bar (was 1).

### Hero

The question pane is the page's one raised card: `#pane` is `.card.hero` (shadow 3 over `--hero-wash`); inside
`.rh-pane` the runner's own frame (`.rv-pane` border, its paper, the top bar's and foot's paper) gives way so the
corner wash shows. The list is flat on the page: no outer border, hairline rows, group heads on `--page` (no tinted
bands), the sticky list head on `--page`. Insights and Your rules are `.card.line` (flat). Walk: the paused and done
card is the hero; done shows "4 of 5 named" as `.hero-num`. Worksheet: the score after Submit is the hero with the
number at `.hero-num`; the sticky Submit column is a raised card instead of a bordered box.

### What moved behind which control

- Difficulty and Status: behind Filters · n (the sheet, every width). The tools row is Search left; Sort, Filters · n
  and Insights right. Each set filter shows as a token in the list head ("Medium ×", "Half fixed ×"), Clear beside
  two or more (the kit's own Clear was hidden at every width).
- The tab sub-line: gone as a row. Its figure leads the list head ("≈ 24 pts at stake"; Due "about 8 min left
  today"), the whole line stays in each tab's tooltip and aria-label.
- Insights: the closed disclosure row is now the Insights button at the end of the tools row (its title and figures,
  "Trap 3, Slip 1", are the button's tooltip); the body opens under the tools row, open state still remembered.
- The notes row: new misses (Walk) and a worksheet waiting (Enter answers) are pinned at the top of the Due and Redo
  lists, same buttons and hrefs; Redo's tab carries an amber unread dot (and "1 new" in its label) while new misses
  wait; Start ▾ gains "Enter worksheet answers" so every tab reaches the worksheet.
- Tab counts: pills on Due and Redo only; Marked, Saved, Fixed a plain soft figure; History none (aria-label keeps it).
- Redo rows: one status badge (Blind spot, else Relapsed, Stuck, Half fixed), New as an amber dot before the title,
  tier bars, last date, points as a right-hand figure (the topic too when the list is not grouped by topic). Skill,
  MC / Grid-in, missed n×, source, your pick, avoided in, kind, cause, other types: the pane head, the row's tooltip
  and its aria-label (avoided in and the kind are only in the tooltip and label).
- Group heads: "2 open · ≈ 12 pts"; domain and per-test on the title's tooltip (and read out). Fix N and the fold
  show on hover or keyboard focus (always on touch, always on a folded group). From 1280 they stick under the list
  head while their rows scroll.
- Checkboxes sit over the lead and show on hover or keyboard focus, or on every row once the selection differs from
  the tab's default (`.rh-selmode`); the pips give way while the box shows. Touch: Select all or a long press turns
  the boxes on; until then a tap on the lead opens the row.
- The action bar: one line, "4 selected · about 11 min" (a phone "4 selected"), Options, the primary. The full
  figures (types, questions, can't go harder) head the Options popover; options away from their default count on
  the button ("Options · 2", named in its tooltip). From 1280 the bar is docked at the foot of the list column (the
  column is one sticky flex column: list scrolling, bar under it); below 1280 it is sticky at the bottom of the body.
- History: the tier figures join the summary line (one row, was two); Download CSV is in the list head's More
  (More now shows on History without a selection).
- Counts over percentages: the named rate, flags caught, Right but slow, relapsed in Fixed.

### Shared pieces adopted (the lead's A1 note)

- Start review and the sitting Fix are `.split-btn` (the local `.rh-split` is gone).
- No side stripes: the open row has the one selected look (`--sel-bg` + `--sel-edge`); the worksheet's answering row
  the hover band. No ink focus rings: the row button keeps only an inset offset under the shared amber-deep ring.
- Page-level boxes: hover band `--hover` (was `--tile`, invisible on the warm page), wells inherit the page's, the
  phone tab strip and the worksheet foot on `--page`, worksheet bubbles and the Insights calibration cells on `--face`,
  print's example box `--tile-2`. The sticky list head drops its own line from 1280 (the first row's hairline is its
  edge; part 2's `.scrolled` can add the scroll shadow).

### Motion and feedback (part 1)

Only one: a row fixed in the pane fades out (a class, 250ms; was an inline-style height animation). Everything else
waits for part 2.

### Bugs fixed

- 6, stale counts: when a mistake closes in the pane, its row leaves, the group head ("4 open", Fix N), the list
  head, the bar (selected, Fix N) and the tabs count it out at once. The list is not refetched (that would move the
  pane to the next mistake while the verdict shows); the row is found by identity, so a single opened from Worth the
  most never closes the wrong row.
- 6, the bar over the pane's foot from 1280: docked under the list. Phone toasts under the bar: lifted above it while
  it shows (index.html, `body:has(#actbar:not(:empty)) .toasts`).
- 14, mistakes/index.html: favicon, apple-touch-icon, viewport-fit, ui.css (after the redirect script, so it never
  delays it, render-blocking so the moment before the move paints the page colour), the fallback link in `.page`.

### Inventory diff (accounted)

Official inventory.js (fixture answers `{}` for /review): review gains ids `insbtn`, `insights` (the tools-row slot and
the Insights host) and loses `tabsub` (the sub-line row; its text is the list head figure and each tab's tooltip and
aria-label). walk, sheet, print, mistakes: no difference. A Review harness with rich fixtures (counts, Due, Redo in two
groups, Marked, Saved, History, Fixed; every tab at 1440 and 390, NO ERRORS before and after): "Insights" is a new
button (it was the disclosure's summary); "Download CSV" moved into History's More (More shows there now); Redo rows
are the same buttons with an aria-label (name changed); Redo's tab label gains "1 new"; ids `rh-ins-<tab>` on the
Insights disclosure. Nothing else appears or disappears. Smoke page.js: review, walk, sheet, print 1440 and 390
"NO ERRORS" as before; mistakes the same jsdom navigation note as before (all rerun on the final files, with
check-ui, node --check on every touched file and inline script, and the em dash grep). The row tooltips are native
`title` (no shared code turns them into chips).

### Not done in part 1, and why

- Icons (part 2): ▾ on Start, group fold and the sitting Fix; ⋯; ✓ / – leads; × / ↺ in the preview; ‹ back links;
  the Due ✓ count. The new filter tokens use " ×" text for now (aria-hidden; the button says "Remove filter ...").
- Phone row actions into one row ⋯ menu: needs the `more` icon; part 2.
- Saved as a bookmark after the title: an icon; Saved stays a soft badge, so a saved row with a status shows two.
- The fix moment (pip fill, wash, counts roll, no desktop toast), folds that animate, bar rise, tab counts that roll,
  Insights chart icon, empty-state line spots, sheet bubble fill, Spot the trap ring: part 2.
- Walk done as one row per mistake with its pips: the walk summary has no per-mistake pips; the figure is done.
- The calibration matrix keeps its percentages (the rate per certainty is the point of that table).
- Group heads keep their italic tell line (a fact about the habit, not helper text).
- The sticky group heads' offset reads the list head's measured height (`--rh-lh`); jsdom has no layout, so unverified.

### Shared asks

- runner.js / runner.css: the pane's 52px "Tools ▾" band as an icon in the head's top right; fold the odds line and
  History timeline into the facts card; in `mode: 'pane'` the Twin pill and `.rv-next` as `.btn` while Review's bar
  shows (two oranges from 1280). Review now frames the pane itself (`#pane.card.hero`, the `.rv-pane` border and paper
  zeroed inside `.rh-pane`): if runner raises `.rv-pane:not(.rv-dlg-in)` on its own, the pane gets two frames.
- ui.css: `::view-transition { pointer-events: none }` (bug 14's second half).
- kit: export `icon()` as `UI.icon` (Review builds its token × and part 2 carets with it), and `more`, `left`, a down
  chevron and `x` in UI.ICON. Optional: `UI.filterBar({tokens: host})` so other pages get the set-filter tokens.
- Every page's `<meta name="theme-color" content="#FFFFFF">` against the warm page (head.js may set it; lead's call).

### For the user

- Difficulty and Status are one tap deeper (Filters · n); whatever is set shows as a removable token above the list.
- Redo rows show the title, one status, the level, the last date and the points; the rest is in the question pane and
  the row's tooltip.
- Tick boxes appear when the mouse is on a row, or on every row once you change the selection (on a phone: Select all
  or a long press).
- New misses and a waiting worksheet sit at the top of the Due and Redo lists, not above the tabs; Redo has an amber
  dot while new misses wait; Start ▾ also has "Enter worksheet answers".
- History shows no count on its tab; Marked, Saved and Fixed show plain numbers. History's Download CSV is in More.
- The bar is one line; the types and question count are at the top of Options. From 1280px it sits under the list.
- The open row is tinted amber with a ring instead of the amber side bar.

## Premium build (part 2)

Files touched: web/review/index.html, review.js, walk/index.html, walk/walk.js, sheet/index.html, sheet/sheet.js,
print.html. Not touched: item.js, mistakes/index.html, every shared file. No git, no browser.

### Changed from part 1 (DEMO.md "Visual review")

- "Lists live in one card": the list is a white card again (`#panel.card`, shadow 1, no padding), its list head,
  group, day and sitting heads on `--raised`; the question pane stays the one hero (`.card.hero`, shadow 3). Part 1
  had the rows flat on the page.
- "Counts that are not alerts are neutral": the row badges that were amber (Half fixed, Due, Check due, Not checked
  yet) are `.badge.line`; ink stays for Blind spot, Relapsed, Stuck, Never came back, Rushed.

### Shared controls adopted (step 3)

- `.split-btn` with `UI.icon('caret_down', 16)` as the menu part's child (Start review, a sitting's Fix): the caret
  turns while the menu is open. Tactile pill and `.btn` faces, busy spinners (`aria-busy` on Start, Fix, Walk,
  Rematch, the bar's primary), drawn checkboxes and the focus ring all come from ui.css.
- Quiet menus: a sitting's ⋯ and the worksheet's ⋯ are `.ibtn` ghost icons (`more`).
- The open row keeps the one selected look; it now eases in (background and edge, 160ms).

### Motion and feedback (step 4)

- Page entry: `data-m="stagger"` on main, `data-m-now` on the header (Start never waits).
- The fix moment: the fixed row steps out of the selected look, glows amber and leaves (`UI.fx.glow`, its gap closing by glide); then the list,
  list head and bar repaint with the row counted out, the rows below sliding up (glideRows), and the Redo and Fixed
  tab counts roll (`UI.roll`). Beside the pane there is no toast (a polite live line says "Fixed: label"); in the
  phone's dialog the toast stays, with a check.
- Tab counts roll on any change (a fix, a snooze, a refresh); Due done for today is a check icon, not a glyph.
- The list glides on a filter or sort change: the rows stay (dimmed) while the new list loads, then rows that stay
  slide to their place, new ones rise 4px. UI.glide moves one level of children and Review's rows sit inside group
  sections, so review.js runs the same FLIP over every row by `data-key` (`glideRows`, at most 40, instant by key
  or with reduced motion). Unsave and Unmark close their gap the same way.
- A tab's first list fades in over its skeleton (UI.motion.enter 'fade').
- Group folds close and open in height (`UI.motion.grow`; folding flips at the end of the close; by key at once). Insights opens
  with the shared `details.fold` animation.
- The action bar rises in when a selection first shows it and nudges out when the selection empties (its content
  stays, inert, while it leaves).
- The sticky list head takes the scroll shadow while rows slide under it (`UI.scrolled` with the list column as
  root); the phone's sticky tabs too (`data-scrolled`).
- Redo's unread dot pulses once when it first appears (none with reduced motion).
- Spot the trap: a right pick draws a check after the line (`UI.fx.check`).
- Walk done: "4 of 5 named" rolls up from 0 once. Worksheet: the score rolls up from 0 once, right after Submit.

### Icons (step 5)

- `caret_down`: Start's caret, the group fold, a sitting's Fix caret. `more`: a sitting's ⋯, the worksheet's ⋯, the
  phone row menu. `x`: Due's Not today, the preview's drop, the filter tokens (the temporary " ×" text is gone).
  `again`: the preview's put back (was ↺). `check`: the Due tab when done, the Due and Fixed row leads (dismissed
  keeps its en dash). `results`: the Insights button. `bookmark` (outline, soft ink): Saved on Redo, Marked and
  Fixed rows instead of a badge. `caret_left`: the back links on Walk, Worksheet and Print (drawn by their scripts;
  the links read "Review").
- Text marks left to the Marks font (A3: no change needed): "missed 2×", "Relapsed ×2", Fixed's proven levels ✓ / ○,
  item.js's story labels.
- Spot drawings: `UI.spotArt('clear')` on Redo's Nothing open and Due's Nothing due today; `'start'` on the first-use
  History and Fixed empties. Redo for a new student, Marked and Saved keep their dimmed sample rows instead (one
  illustration each); filtered empties get none.
- Filled twins: Review has no toggles of its own; the bookmark is a status mark, shown as the quiet outline.

### The phone row menu

On touch, a row's actions (Learn this type; Note and Unsave; n tries; Prove it and Reopen) are one ⋯ at the row's
end ("Actions: <row>") that opens them as a menu; each item clicks the same button, so the note editor, the tries
list and Prove it work as before. A mouse keeps them over the row's end on hover or focus.

### Inventory diff (part 2 against part 1, Review harness, every tab at 1440 and 390, NO ERRORS)

New buttons "Actions: <row>" (the touch menu, hidden on a mouse) on rows with actions; the Fixed row's name loses
its leading "✓" (now an icon). Official inventory.js: as part 1 (ids `insbtn`, `insights` added, `tabsub` gone);
walk, sheet, print, mistakes unchanged. Smoke page.js: review, walk, sheet, print 1440 and 390 "NO ERRORS",
mistakes the same jsdom navigation note as before. check-ui ok, node --check on every touched file and inline
script, no em dash.

### Not done, and why

- Rolling the group head ("2 open"), list head and the bar's figures after a fix: they repaint (the tab counts roll).
- Note save stays a toast: the note saves on blur or Cmd+Enter, so there is no Save button to say Saving, Saved.
- The clip tab indicator (`{mark: 'clip'}`): an amber tab beside Start and Fix would be a second orange.
- Due's tick meter, Fixed's "Held all 3" seal, Walk's per-step icons and Spot the trap's ring draw: small delights,
  left so this page stays calm; say if you want them.
- jsdom has no layout or animation: the glides, folds, glow and roll ran as code paths only; the critic's shots
  will show them.
- Page entry rises `#body` (a transform) for about 300ms at load; on a phone the fixed action bar sits inside it,
  so if Redo's list paints inside that window the bar can sit a few pixels off for those frames. If the shot
  catches it: wrap the top blocks in one staggered div so `#body` is not a staggered child.
- Touch: the hidden row buttons still take `aria-busy` (Reopen) and the note editor's Escape returns focus to the
  hidden Note button; both silent, the menu is the visible path.

### Shared asks

- runner (as the lead told its builder): do not frame `.rv-pane` inside `.rh-pane`; Twin and `rv-next` as `.btn`
  while Review's bar shows; the pane's "Tools ▾" band as a head icon.
- kit `UI.glide`: an option to glide nested rows (`{ rows: '.rh-row' }`), so pages with grouped lists need no
  local FLIP like review.js `glideRows`.

### For the user

- The list is a white card again beside the raised question card.
- Fixing a mistake in the pane: its row glows amber and leaves, the counts move; no toast beside the pane.
- Filters and sort no longer flash a skeleton: the rows dim, then slide to their new places.
- On a phone, each row's extra buttons are behind one ⋯ at the row's end.
- Half fixed, Due and Check due badges are grey outlines now; Blind spot, Relapsed and Stuck stay dark.

## Visual review

Real app at 127.0.0.1:8071 (DB copy), learner `a:v2revresults01` (most attempts) plus a fresh learner; headless Chromium
of my own (touch and coarse pointer under 600px). Rounds r0 (before), r1-r2 (after the first fixes), r3-r4 (final), at
1440 light, 1440 dark and 390, with hover, Tab focus, press, Start ▾, More, Options popover, Filters sheet, Insights open,
the phone row menu, a sort glide sampled at 60/140/260/600ms, the worksheet with answers picked. Shots:
`premium/shots/app-review/review-r{0,1,2,3,4}-*.png`. Files touched: web/review/index.html, review.js,
sheet/index.html, walk/index.html, print.html. Not touched: walk.js, sheet.js, item.js, mistakes/index.html.

### Per screen

- **Hub, first screen (1440).** Was: two orange Starts (sidebar Up next and the page), about 75px of dead air between
  the title, the tabs and the tools (the shell's zero-height sentinels and waiting section chips each took the column's
  16px gap), Search floating mid-row between Sort and Filters, Insights a bare text link beside the Filters key, and on
  Redo the action bar below the fold. Now: `UI.shell({ page, ownPrimary: true })` (Up next's Start is a `.btn`), the
  helpers take no gap, Search left with Sort, Filters and Insights as one set of keys on the right (Insights open wears
  the selected look), and from 1280 the bar sticks to the viewport foot inside the list column, so the one orange
  button shows on the first screen (shadow 3 while it floats). Reads premium.
- **The list card beside the raised pane.** Was: the open row a heavy amber box (fill plus a 1.5px amber ring, the same
  look as the focus ring); each status badge on a line of its own; Due rows five lines (title, badge, domain and type,
  tier and points, the closes-it line); metas breaking mid-fact ("took 0 / days", a proven mark alone); History leads a
  blank tile with a 9px corner mark that read as a broken image; notes rows with Walk / Enter answers wrapped under the
  text. Now: the open row is the wash band alone (DEMO: picked rows are bands; focus keeps the ring); the badge stays at
  the title's right end; Due rows trimmed like Redo's (tier, points right; domain and type in the tooltip and label);
  metas wrap fact by fact and a wrapped line starts without a dot (each fact carries its dot, a 14px clip hides the
  line-start ones); tier bars sit in their own span (`.dbars::before` is the bars, so the meta dot was landing on
  them); empty History, Saved and Marked-sample leads show the result glyph centred at 22px; notes rows are a grid
  (text and minutes left, the button right, centred); "≈ 1 pts" reads "≈ 1 pt" everywhere; the empty card's sample row
  lost its stray top hairline. Fixed's badge is the state word ("Not checked yet"); its date ("first check Oct 22")
  joins the meta (the long badge was clipped in the column). Group heads' Fix is 14px.
- **Filter row and tokens.** Search first (order -1), Sort, Filters · n and Insights right, all one key height; on a
  phone Insights is the icon alone (aria-label "Insights") so the placeholder no longer clips. Tokens unchanged.
- **Action bar.** One line on a phone; in the 380px column the count on top and the minutes under it (it truncated to
  "19 selecte..." beside "Check these now · 10"). Options popover: a real bug, its head read "about 15 min**null**"
  (`replaceChildren` stringifies null), fixed; the number field sits on the label's line instead of wrapping alone.
  Press on the pill sinks as designed (r2-press-start).
- **Insights fold.** Was a jumble (name, tip, figures and Drill buttons in one flowing line; Worth the most a wall of
  chips with Fix 5 mixed in). Now Habits and Right but slow are aligned rows (name over its tip, the figure, the button
  in a column), Worth the most a grid of equal keys (label left, points right), Fix 5 on its own line under it.
- **Touch row menu (390).** The ⋯ at the row end opens the actions as a menu (r3/r4-rowmenu); fine. The list head keeps
  "25 of 25 selected" and More on one line, the stake figure under it (More wrapped alone before).
- **History summary (390).** Dots no longer hang at line ends (each fact a `.rh-bit`; the dot is drawn before it on
  desktop, dropped on a phone where the gap separates).
- **Worksheet.** Rows were hairlines floating on the page and grid-in rows taller than bubble rows (an empty preview
  line). Now one white card, every row the same height (the preview sits beside its field); the side card reads
  "Minutes taken · optional" over a full-width field, then the count and Submit. ownPrimary on its shell.
- **Walk.** The card butted the title (0px); now 20px. Only the fallback can be judged: the server has POST
  /api/review/walk but no GET /api/review/walk/{id} and no `cfg.walk` on the drill, so every walk (the hub's "Walk 15
  misses" too) lands on "This walk can't be opened yet". The real walk UI (steps, dots, "4 of 5 named") was not seen.
- **Print (traps, error log).** On screen the sheet is now a page of white paper on the warm ground (print unchanged);
  the log's headers and Cause no longer wrap ("PICKED → / KEY", "Fell for / a trap").
- **Dark.** Hub, Fixed, worksheet, walk, print checked; the band, keys and bar hold up. Nothing dark-only to fix.
- **Glide.** Swapped the local FLIP for `UI.glide(list, paint, { rows: '.rh-row[data-key]' })` (one line, same four
  callers); a sort change slides rows from their old places by 140ms and settles (r2-glide-60..600).

- **Scrolling the list (1440).** The list column had `overscroll-behavior: contain`, so with the pointer on the list the
  page never moved and the column's foot (and the docked bar's slot) stayed below the fold. Dropped: at its end the
  list hands the wheel to the page, the column rises and the bar docks under the list (r5-wheel). Review's own preview
  sheet (Start ▾, See the list first) checked: its meta dots clip cleanly too (r4-preview).

Not triggered: the fix moment (a row closing in the pane). A new miss's field is read-only until "What happened?" and
a half-fixed one opens as a reviewed question (the fix comes from Twin or a session), so no row closed here. To watch
in a real browser: since the swap to `UI.glide`, the glowed row is still in the list when `after()` repaints, so
UI.glide also fades a ghost of it where it stood (the old local FLIP dropped it silently). Code path only, unseen.

### Checks

check-ui ok; `node --check` review.js and every inline script ok; no em dash in the touched files; smoke page.js
review, walk, sheet, print at 1440 and 390 NO ERRORS (mistakes: the same jsdom navigation note); inventory.js for
review, walk, sheet, print, mistakes identical to part 2; the rich Review harness (every tab, 1440 and 390, NO ERRORS)
differs only in Due rows' names gaining the domain and type ("Check-in: Due one, S", moved from the visible meta) and
runner's "Tools ▾" now "Tools" (not mine).

### Shared asks

- runner.js ~3561: a facts panel whose only content is the "New" tag renders a full grey panel with one centred chip;
  treat tags-only like the thin case. ~3546: the Fixed line's `' · ' + label` wraps to a line starting with "·" (use
  the `rv-mlabel` span as the open case does). ~3575: on a new miss the "History" heading prints over nothing visible.
  The head's skill line wraps with a leading "·" ("· A system of one line written twice") and Redo's head ends in a
  stray "·" after "Module · Sep 23". The dark Q1 ID chip is DEMO's "dark ID chip next to content".
- runner.js / ui.css: the pane's History timeline cells are blank tiles with a 9px corner mark (they read as broken
  images); centre the glyph when a cell has no number (Review's list does this page-locally with `:has(> .n:empty)`).
- kit `UI.filterBar`: its sheet is about 890px wide with a 300px column of topic boxes; a narrower sheet (about 560) or
  two topic columns would read calmer.
- ui.css: Review's flex column needed `.rh > :is(div[aria-hidden="true"]:empty, nav.sections) { margin-top: -16px }`
  because the shell's scroll sentinels and the waiting section chips are flex children; any page that lays main out
  with `gap` gets the same dead air (check Today, Tests, Plan).
- Server: GET /api/review/walk/{id} (or `cfg.walk` on the drill) so the walk page can open.

### Round 6 (the lead's notes on Due at 1440)

- Rows said "half fixed" three ways (●○, the badge, "1 clean answer closes it"). Badges now only for the exceptional
  states: Redo keeps Blind spot, Relapsed, Stuck; Due drops Half fixed (the pips and the closes-it line say it) and
  Done (the tick and the struck line say it); Saved drops Due ("due today" is in its meta); Fixed keeps its state word
  (Not checked yet, Check due, Held, Dismissed: nothing else on the row says it). Screen readers lose nothing: Redo's
  and Due's row labels still name Half fixed and done.
- Marks are graphite on this page: the ●○ pips (list and pane, scoped to `.rh`), the notes rows' bullets and a New
  row's dot. The orange left on a screen: the primary (Start or the bar's), the open row's wash, the tab underline and
  Redo's unread dot. The selected wash is unchanged.
- Shots: `premium/shots/app-review/review-r6-*` (hub Due 1440, Redo 1440 light and dark, Redo 390, Saved).
- Checks: check-ui ok, `node --check` ok, no em dash, smoke review 1440 and 390 NO ERRORS, inventory.js unchanged. Rich
  harness: badge text removed from visible names only where the name is the row's text: Saved rows lose "Due" ("A saved
  stemDueCircles..." is now "A saved stemCircles... due today"); Redo and Due row names are aria-labels and keep the
  state words.
