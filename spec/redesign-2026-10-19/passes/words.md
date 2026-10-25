# Words pass (2026-10-19)

Files: web/words/{index,mine,study,run,print}/index.html, web/words/sw.js, web/assets/words-ui.js. web/vocabulary/index.html
is a redirect to /words/ and stays as it is. Estimates below assume the shared layer as specified (Now block in the
sidebar from 700px tall, so no Now strip at 1440x900); add about 70px if the Now strip shows.

## First screen

**Library** (`/words/`)
- 1440x900: one header row (Words, meta, the four tabs, Add words). Main leads with search and filters (two lines in
  the 728px column, with the result count, `?` and the view gear at the end), then the word grid from about 160px
  (was about 790px). The aside holds Today's words (Start, the page's one orange button), the two daily questions as
  rows, By exam day (one line) and Collections as a filter list. Moved out of the way: the Due today / New today
  tiles (their figures are in Today's words), the legend line (a `?` popover), the Collections tile grid (aside list),
  Make a set (inside the card), the Collection dropdown (hidden on a wide screen unless it is narrowing).
- 390x844: header, Today's words (Start full width), daily rows, By exam day line, Collections (folded), then search,
  filters and the grid from about 560px (was about 1,100px).

**My words** (`/words/mine/`)
- 1440x900: header row with Add a word, Bring words and `⋯`. Main leads with the view bar (search, filters,
  Table / Wall) and the list from about 120px (was about 860px). The aside: status rows (Due today with Review beside
  it, Learning, Saved), Due in the next 14 days, By exam day, How you miss words, How your schedule is working, and
  the compact Today's words line last.
- 390x844: header and tools, status rows, four folded card titles, the compact Today's words line, then the view bar
  and the list from about 520px.

**Flashcards / Quiz** (`/words/study/`)
- 1440x900: header (title, meta, tabs). Main leads with the deck list (two columns of 40px rows, about 240px for ten
  decks instead of 440px), then the options. The aside is the glance: what Start will do, about how long, Start,
  Print / Grade a worksheet. The compact Today's words card is gone.
- 390x844: the same deck rows; the glance is the fixed bar above the tabs with Start in reach.

**Run** (`/words/run/`): no chrome, unchanged layout. The card, the grades and the summary are calmer (weight 600,
hairline summary rows, no stacked fake cards).

**Worksheet** (`/words/print/`): no sidebar or tabs; the toolbar (Back, Key on its own page, New version, Grade,
Print) and the sheet.

## Big changes

1. Library: the word grid is near the top. Today's words, the two daily questions, By exam day and Collections sit in
   a right column on a wide screen, and above the grid on a phone or a narrower screen.
2. Library: the Due today and New today tiles are gone. Their figures (due, when the next ones are due, new words
   today against the goal, goal met, the "never a cap" note) are in Today's words' summary line.
3. Library: Collections is a list of rows with a thin known bar under each, open on a wide screen. The legend line is
   a `?` button next to the result count.
4. My words: the list comes first. The status filters are rows in the right column, with Review beside Due today.
   The traps card, the schedule card, the 14-day forecast and By exam day are in the right column too. Below 1280px
   they fold to their titles.
5. My words: the tools are back in the header and always visible: Add a word, Bring words, and `⋯` with Export your
   own words (CSV), Import, Print this list, Share a list and Grade a worksheet.
6. Flashcards and Quiz: decks are a two-column list of rows. The chosen deck shows its note and its picker under it.
   Start is in a right column, or a bar at the foot below 1280px. The small Today's words card is gone (the Today's
   words deck does the same). "Find your level" moved under Start for new students.
7. Today's words: Make a set is inside the card now. "Take today's cards offline" is back at the card's foot.
8. Word sheet: everything above the meaning is on one line: part of speech, tags, level, and Covered / Open. The
   SAT-style question now comes after Easy to mix up. Review counts, first seen and look-ups fold under "Reviews and
   history".
9. The worksheet print page has no sidebar or tabs. It is a print surface (DIRECTION 4), and its toolbar has Back.
10. Import a file or a paste is also in the library's Add words menu (it moved into words-ui.js as
    `UI.bringWords('import')`).

## Bugs fixed

- The words-ui.js stylesheet no longer restyles every `.sheet-foot`, `.go`, `.upnext` or `.hook` on any page that
  loads it. The rule is gone: the word sheet's footer uses the sheet's own `.pill.sm` / `.btn.sm`, and the run page
  keeps a one-height rule for its own `.wr-ctl` and `.wsum .upnext`.
- On a phone, the My words bulk bar no longer sits under the tab bar. The page no longer sets `bottom: 0`, and the
  wrapper is `display: contents`, so the shared `.selbar` sticks at the foot of the list column, above the tabs.
- Flashcards / Quiz: a `<select>` is no longer inside a radio `<button>`. Decks no longer spill into the next row on
  a phone.
- My words: Review is no longer a button inside the Due today button. The grid's empty fourth column is gone.
- My words wall: Up and Down go to the nearest cell on the next line, at any row length. The phone-only "tap the
  label" big-cells switch is now a real Big cells button on every screen. Learning cells are a mix of `--ink`, so
  they show in dark mode. The legend no longer says "Tap".
- My words, phone table: Level, Right / total, Last reviewed and Saved show on a second line (named where a number
  alone is unclear). Before, the phone hid them.
- Today's words Start: the 40px pill override is gone, so it is 42px, and `--touch` on a phone or touch screen.
  `.tw-row .pill` min-width is gone. The joined three-button group is now three plain `.btn.sm`.
- `.tw-note` (the Spread / Do all now line), the offline line and the kept-cards line have `data-nofold`.
- `ⓘ` notes (`W.info`) did nothing on a touch screen: tooltips show only on hover or keyboard focus. A tap now opens
  the same text in a popover. This covers the Flashcards / Quiz notes, the new-words note and the legend.
- Library: `#q` is in the filter row in the HTML, so the header no longer jumps when the page loads. The gear
  options use `hidden`, not an inline style. The dead `soon()` is removed. The `noDebt` flag that nothing read is
  removed. `DUE` in amber-deep at 10.5px (3.2:1) is now an outlined `Due` badge. The same goes for My words' Next
  review column.
- Run: `.wl-msg` (defined only on the library) became the run's own `.wr-msg`. All 20 inline styles became classes;
  the one left sets a bar's width from data. Option buttons and order rows are 48px, down from 52. The auto-next
  ring has 14px corners instead of 999px. The guess tag is a `.badge`.
- Run pages no longer auto-fold (shared FOLD_OFF), so their long hints were shortened. Method, Relationship first and
  the triage note now sit in a closed `details.fold` written into the page.
- Print: the empty key letter is a hyphen, not an em dash. The paper colours are local custom properties.
- Em dashes: none left in any file I own. The import parser still accepts a spaced em dash, written as the regex escape for U+2014.
- sw.js caches `/assets/fonts/Geist.woff2`; cache name bumped to `satf-words-2`.
- Padding: library 150 / 240 → bar height + 16 (72 desktop; phone 96 + 52); My words 150 → the `.page` default;
  study 140 → the default on a wide screen (96 / 168 where the bar shows). Gaps 20 / 22 → 12 / 16.

Also done, from the ranked proposals:
- Slop: no mono or uppercase on words anywhere in scope. The part-of-speech tag on tiles is 11.5px Geist and shows on
  hover (always on touch, still in each tile's aria-label). `.wtag` became `.badge.soft`, and the corrected note is
  `.meta`. `.guess-chip` became `.badge`. The three triangle-glyph summary copies became the shared
  `details.fold` / `.fold-s` chevron. The `.shade-bar` gradient is a hairline. `.fstack` fake cards are gone. "Add
  words ▾" and "Bring words ▾" use the `.dd` chevron. Trend triangles are words (rising, falling, steady).
- Type: `.fword` and `.wsum .score` stay big at weight 600. The word sheet title is 22/600 with no `!important`.
  `.glance .pill` is the shared 42px pill (`.pill.wide`). `.glance .big` is `.stat-v`. Off-scale sizes in scope (13,
  13.5, 15, 17, 18) moved to 12.5 / 14 / 14.5 / 16. Clocks and counters are Geist with tabular-nums. `.wtabs` now
  matches `.seg` (the `--well` track, the selected option on paper with the amber ring).
- Copy: "Practise" is spelled "Practice" everywhere. "Twin ×10" is now "Practice 10" (title: ten in-context questions
  with this trap). The import placeholder has no em dash. "How your schedule is working" matches its aria label.
  Empty-state and helper sentences that explained the UI are shorter.

## Not done

- `.wl-strip .big` to `UI.tile`: the strip is gone. Due and New are now in Today's words and the daily items are
  rows, so nothing is left to convert. The Study glance figure uses `.stat-v`.
- Daily rows that swipe on a phone (audit phone note): two stacked rows take about 100px, so swiping would not help.
- Wall default (only your words, or every library word): this is the user's call, see below. The wall now says what
  it holds: "N library words, studied or not".
- The journey dots on the word sheet keep their per-review detail in hover and focus tooltips; the group's aria-label
  carries the totals. A tap per dot would need a button per review; not in the audit.
- The print sheet's own paper sizes (13, 13.5, 15) stay. They are print typography for the paper, not screen UI.
- Three local pressed-row buttons (`.ctile`, `.deck`, `.wm-srow-b`) are still page-local. Merging them needs a shared
  primitive (see Shared asks).

## Shared asks

- `.twocol`: a bottom offset for pages with a fixed bottom bar, for example `--twocol-bottom` in the aside's
  `max-height`. The library sets it locally:
  `body:has(.wl-bar:not([hidden])) .wl .twocol-side { max-height: calc(100vh - 32px - 56px) }`.
- One pressed-row button (wash-2 fill and amber inset when `aria-pressed` / `aria-checked` is true, `--row-h` tall,
  8px corners) to replace `.ctile` (library), `.deck` (study) and `.wm-srow-b` (My words).
- `UI.tooltip` shows nothing on touch. `W.info` now opens a `UI.pop` on tap; a shared fallback (tap opens the tip for
  non-interactive or info triggers) would cover other pages.
- `.pill` at `--touch` height on coarse pointers, everywhere. Today the shared rule covers only `.nextup-go .pill`, so
  Words sets it locally for `.today-words .tw-row > .pill` and `.wr-ctl > .pill`.
- `UI.selbar`: document that the host must not be a sticky box of its own. My words makes its wrapper
  `display: contents` so the shared phone offset applies.
- Planned and relied on: `.k`, `.meta`, `.stat-v` off mono and uppercase; `.chips` at 8px corners (study's question
  types, the time box, New words a day); `.badge` at 6px corners.
- Question: should the library pass `UI.shell('words', { now: false })`? It has its own Start in Today's words. I did
  not pass it, because DIRECTION 4 lists who passes it.
- Optional (from the audit): a sub-nav slot under the active left-nav item, for Library, Flashcards, Quiz and My
  words.

## For the user

- My words' Wall shows every library word (or every word in the chosen collection), studied or not. The table shows
  only the words you have touched. Should the Wall also default to only your words?
- On a wide screen, the library hides the Collection dropdown while the right-hand Collections list is on screen. The
  dropdown comes back as soon as it is narrowing the grid. Keep it hidden, or show both?
- "Take today's cards offline" is back on Today's words. It registers the Words service worker the first time it is
  used. Keep it?
- Flashcards / Quiz no longer has its own Today's words card; the Today's words deck is the same thing. OK?
- The worksheet print page has no sidebar or tabs now (DIRECTION 4). Back is in its toolbar.
- "Twin ×10" on trap rows is now "Practice 10". Keep "Twin" if it is the term the app teaches.

## Polish round

Files: web/assets/words-ui.js, web/words/{index,mine,study,run}/index.html. Print and web/vocabulary/index.html (the
redirect) needed nothing. "Twin ×10" stays on My words' trap rows and the run summary. Every function from round one is
kept, including Export CSV, Import, the 14-day forecast, By exam day and offline cards.

### First screen

**Library** (`/words/`)
- Today's words (aside) leads with its title and one facts line (due, proofs, minutes). The daily new-words goal is
  now a tick meter under it ("New words today, 3 of 10", ten blocks, the "never a cap" note in its `?`), so the
  figure left the facts line.
- Collections are the shared `.choice-row`: name left; the due count and known share quiet and right-aligned
  ("3 due · 40/120 known"); the hairline known bar still runs along each row's foot. "New list" is a quiet
  `+ New list` button under the Yours group, not a fake collection row.
- The marks legend is the shared `?` (`UI.why`), now beside the word count it explains ("214 words ?"), before the
  view toggles and the gear.
- Word tiles have the card hairline (`--tile` on `--paper` was 1.10:1 and barely read as a boundary).

**My words** (`/words/mine/`)
- The status rows (Due today, Learning, Saved) are `.choice-row`: name with its note under it, the count quiet on the
  right (it was 16/600 ink). Review stays beside Due today.
- Due in the next 14 days: a number leads ("26 due · most on Sun, Oct 25 (8)"), then 14 bars with no axis, dated
  only at their two ends ("Today", "Nov 1"). Every bar keeps its tooltip and the chart its data table. The weeks
  to the exam chart is unchanged.

**Flashcards / Quiz** (`/words/study/`)
- The decks are `.choice-row` radios (`role=radio`, `aria-checked`, `aria-disabled`, `aria-description` kept), the
  count quiet on the right. Empty decks take the shared disabled look (faint text) instead of the outlined one.
- The option notes (Show first, Mode, Question types, Method, Relationship first, Move on by itself) use `UI.why`.

**Run** (`/words/run/`)
- After a run, the summary's meta line reads "4 min · 212 known in all". When the run moved words to Known, the
  total shows the count from before the run and rolls to the new one (`UI.roll`) 400 ms after the summary is on
  screen. A finished run reopened later shows it still.

**Word sheet and Add sheet** (words-ui.js)
- Shades' note is `UI.why`.
- Add a word: Save and "Save and add another" say Adding, then Added with a check (Saving, Saved when editing), or
  "Not added" for a duplicate or a library word, with the reason line under the form as before. "Save and add
  another" no longer raises a toast (the button confirms in place); Save closes the sheet, so it keeps the toast
  that names the word and its list.

### New components added

- `UI.meter({ticks})`: Today's words, the daily new-words goal (ticks = the goal, up to 10). Replaced the
  "3 of 10 new" fact.
- `UI.saving`: the Add sheet's two save buttons (`{busy: 'Adding', done: 'Added', fail: 'Not added'}`; defaults
  when editing). Validation runs first, so an empty field never flashes Adding.
- `UI.roll`: the run summary's known total, only when the run just ended on this screen and moved words to Known.
- `UI.why`: the new-words note, the Shades note, the six study option notes, the library's marks legend.
- `.choice-row`: library collections (was `.ctile`), study decks (was `.deck`), My words status rows (was
  `.wm-srow-b`).
- `--twocol-bottom`: the library sets it to 72px while the study bar shows (was its own max-height rule).

### Removed local copies

- `info()` / `UI.word.info` and the `.winfo`, `.winfo-t` CSS (words-ui.js). Study called it; it now calls `UI.why`.
- `.ctile` base, pressed, hover and `.ctile.new` rules (library; `.ctile` stays as a hook for its name, meta and
  known bar). `.deck` and every `.deck` rule (study). `.wm-srow-b` and its rules (My words).
- The library's `.btn.sm.icon` `?` that opened `UI.pop` with the legend.
- `body:has(.wl-bar:not([hidden])) .wl .twocol-side { max-height: ... }` (library).
- Grep: no file in web/ references `winfo`, `wm-srow-b`, `word.info` or `W.info`.

### Not done

- The forecast's end labels are an HTML line under the chart, not chart text: `UI.barChart` thins x labels from the
  last bar backwards (`(n - 1 - i) % every`) and its `labels` function gets no index, so with 14 bars in a 300px
  aside the first date is always dropped. The chart runs in its mini mode (64px, no axis) so the bars span the
  width and the two labels sit at their ends. See Shared asks.
- The run's live tally ("3 right of 4") does not roll: `progress()` rebuilds it each answer and the brief asked for
  the learnt count, which is the summary's known total.
- The collection rows and the status rows take `.choice-row`'s `--well` fill. 21st's nav rows have no fill; I did
  not override the shared look.

### Shared asks

- charts.js `barChart`: a `labels: 'ends'` option (first and last bar only, anchored start and end), or pass the
  index to a `labels` function and keep index 0 when thinning. Then My words can drop its `.wm-fx` line.
- `.choice-row` on a long filter list (library Collections, 6 to 15 rows): a `.choice-row.plain` variant with no fill
  until hover would read like 21st's nav. Optional.

### For the user

- My words' 14-day forecast now leads with the total and the busiest day, then bars without an axis, dated only at
  the first and last day (it showed a weekday letter under every bar). Each bar's tooltip still has its day and count.
- Counts on My words' status rows and on the collection rows are small and grey now, right-aligned.
- Collections and decks are filled rows (the shared row style); the chosen one keeps the orange outline.
- Add a word: the button says Adding, then Added. "Save and add another" no longer shows a toast.
- The run summary shows your total of known words and counts up when the run moved words to Known.
- "New list" in the library's Collections is a quiet "+ New list" button now.

## Premium build (part 1)

Files: web/words/{index,mine,study,run,print}/index.html, web/assets/words-ui.js. web/vocabulary/index.html (the
redirect) needed nothing. Kept, as asked: "Twin ×10" on My words' trap rows and the run summary, Export and Import
(My words ⋯), the 14-day forecast and By exam day, offline cards (Today's words: Other ways, and the kept-cards line).
A1's ask from the lead is in here too: no page-level `--tile` box left on the warm page, no side stripe, no ink focus
ring, the word grid and deck rows keep their own gaps under `--card-gap` 32.

### First screen, before and after (code estimates, sidebar not counted)

| Page, viewport | Before | After |
|---|---|---|
| Library 1440 | 3 control rows before the grid (header; search and 7 dropdowns, count, `?`, gear over 2 lines); about 30 controls outside the tiles; 4 aside cards and the fixed study bar; about 150 empty pip dots and a known bar on every collection | 1 control row (search, Filters · n, A–Z, count, ⋯); about 17 controls; 1 raised hero and an unboxed Collections list; no bar until the view is narrowed; no empty pips, known bars only where something is known; grid from about 110px |
| Library 390 | Today's words with 4 control rows, 2 daily-question rows, By exam day, Collections, search, a filter scroller, count and gear | the hero (figure, facts, ticks, Start and Other ways, one daily line, one By exam day line), Collections as one closed line, search, one Filters row; grid from about 700px (the hero's 56px figure costs about 70px; see For the user) |
| My words 1440 | header over 2 rows (Add a word, Bring words, ⋯ wrapped); the view bar wrapped (search, 3 dropdowns, Table / Wall); 6 aside boxes, all open from 1280 | 1 header row (Add words, ⋯); 1 view row (search, Filters · n, Table / Wall); 4 aside boxes: the hero, the forecast (open), one card holding By exam day, How you miss words and How your schedule is working (closed to title and fact), the compact Today's words line |
| Flashcards 1440 | 12 to 16 deck rows in 2 columns, How many beside Order, Show first: about 27 controls | 3 lead decks as 48px rows (Today's words, Due today, New), "More decks · 13" closed, How many, More options closed (Order, Show first): about 10 controls |
| Quiz 1440 | the same decks, How many and Mode, Question types, More options | 3 lead decks, More decks closed, How many and Mode, Question types, More options |
| Run, a card | flat `--tile` card; Open word on the back face; 3 top tools | the card raised (paper, `--shadow-3`) with the deck's edges under it (2, 1, then none); Open word is the 4th top tool; the back face drops its "Meaning" label |
| Run summary | the score, then up to 5 Up next buttons (Next, Review, 10 new, Quiz these, Library) | the score in a hero plate with this run's strip; Up next is 1 pill, 1 button and More |
| Worksheet | sheet edged on white | a desk: the warm page, the sheet as white paper at `--shadow-3` (print still resets to white) |

### The hero on each page

- Library: Today's words is `.card.hero` (`.wl-today`), the due count as `.hero-num` ("12 due today"); the daily
  questions and By exam day are lines at its foot (`#strip`, `#finish` moved inside it). Collections lost its card.
  `UI.todayWords(host, {card: false})` and `UI.wordsFinish(host, ins, {card: false})` render without their own card.
- My words: the status card is the hero: known as `.hero-num`, a stacked 8px status bar (learning, claimed, known,
  the rest of the track not started) with its key, then the Due today (Review), Learning and Saved rows.
- Flashcards / Quiz: the glance is `.card.hero`; below 1280 it stays the bar at the foot (`.st .glance` outranks the
  hero look there, on `--page`).
- Run: the flashcard (paper, `--shadow-3`); the summary's score plate is `.card.hero`, the score `.hero-num`.

### What moved behind which control

- Library filter row: Collection, Topic, Family, Difficulty, Status, Part of speech behind "Filters · n" (a popover of
  the same dropdowns from 760px, the shared bottom sheet on a phone; `filterBar` `pop` is a getter for that). The
  sort stays in the row and shows its value alone ("A–Z"). Facets that are on show as removable chips under the row
  (`#fchips`, a Clear at the end when 2 or more).
- Library ⋯ (was the gear and the `?`): Meanings and Select (checkbox items), What the marks mean (opens the legend
  popover), Flashcards and Quiz on this view, Share these words, Print a worksheet, Grade a worksheet.
- Study bar: shows only while the view is narrowed or words are being selected, with "Done selecting" while
  selecting. Its Flashcards, Quiz and ⋯ (Share, Print, Grade) are unchanged.
- Today's words "Other ways" (a `.btn.dd` beside Start): Review cards, Learn 10, Quiz, Time box (No time box, 5, 10,
  15 min as radio items; a set box shows in the facts line as "stops at 10 min"), Preview today's words, Make a set
  (opens its field inline; Esc on an empty field closes it), Take today's cards offline. The offline line shows only
  while cards are kept on the device. A fresh learner keeps one button, Find your level (Other ways only if Make a
  set or offline is on offer).
- Daily questions: one line ("2 to answer", "1 of 2 done", "both done") with Answer or See them, opening a sheet with
  both rows; each row's Answer it / See it again opens the question as before.
- My words: Add a word and Bring words are one "Add words" menu, the library's items (A word with N, From a text, A
  word list, A question I missed, Import a file or a paste). Collection, Difficulty, Part of speech behind Filters ·
  n; the search is the row's own field now (it was a filterBar search, which the popover would have pulled out of
  the row), still in the URL as `q`. The aside folds remember their state (`satf.words.mineOpen`).
- Flashcards: Order and Show first under More options (the quiz's fold, the same remembered key).
- Run: Open word from the back face to the top tools (an icon; O still works; before a verdict it says why not).
  Summary: Learn N new, Quiz these N and Library under More when there are more than two ways on (Library alone
  stays a quiet link).

### Motion and feedback

None new in part 1 (part 2 adopts the shared moments). Static depth only: the deck edges under the flashcard follow
the real count.

### Icons

Part 2. Two uses of the shared map now: the library chips' remove mark (`UI.ICON.x`) and Open word (`UI.ICON.words`).
The library ⋯ uses words-ui's `more` icon in place of the settings gear.

### Bugs fixed

- Bug 8 (Words Start shows nothing while it saves; a double tap starts two runs): `startWords` and `W.print` run
  through one `busy()` guard in words-ui.js. The button that was clicked gets `aria-busy` (ui.css: spinner after
  300ms, no second press), a second call returns the first promise, a failure clears it, a back navigation from the
  run (bfcache) clears it. Every caller is covered without passing a trigger (`window.event` names the clicked
  button; `o.trigger` overrides).
- Bug 7 (flashcard): the card no longer keeps its transition while dragged (`.fcard.dragging`), so it follows the
  pointer 1:1; a mouse drags too (touch only before), from 6px, never from a button, link or summary; a graded swipe
  leaves the card out instead of springing back; the old card no longer waits 900ms: the grade's line ("word: Know ·
  Back in 3 days") rides under the next card for 1.6s. The stamps and the fly-out are part 2 motion.
- A1 follow-ups: word tiles white at `--shadow-1` (`--shadow-2` on hover, no lift; selected is `--sel-bg` /
  `--sel-edge`); the transitions map's columns are white cards with flat tiles inside; the study bar and the study
  glance bar on `--page`; `.wtabs` thumb is the seg thumb (`--face`, `--seg-thumb`) on a recessed track; My words'
  ink focus outline on wall cells removed (the shared amber-deep ring applies); the run's order rows are control
  keys (`--face`, `--shadow-btn`) with the one selected look; `.wquick` pressed and `.wchip` current use the selected
  tokens.
- Word sheet: covered blocks are face-down plates (`--well`, 8px corners) instead of a faint "Covered".

### Also done (Per page and More items with no new shared JS)

- Quiet tiles: no empty pips on new words; strength is a 2px amber line at the foot once studied (`role=img`, "strength
  n of 5"); difficulty bars moved into the hover line with the part of speech (always shown on touch, in the
  aria-label as before). The legend shows the line.
- Run summary: Sprint's "New best" is a `.badge`; this run's strip (a 10px segment per item, Know / Don't know /
  Right / Wrong / Skipped / not reached, each opens its word) for a run that ended on this screen, up to 60 items.
- My words empty state: a dimmed sample wall (`.empty-sample`, "Example") above the line and the Library pill.
- Library: `UI.shell('words', { now: false })`: Today's words is the page's Start, so the Now strip and the section
  bar's Up next do not repeat it.
- Copy: the run summary's "10 new" is "Learn 10 new".

### Inventory diff (smoke/inventory.js at 1440, fresh fixtures; plus a richer local stub for the non-fresh states)

- Library: "About the marks on a word" (`?`), "Meanings", "Select", "View options" are now items of "View options,
  study, share or print" (⋯). New: "Done selecting" (`#barDone`), `#fchips`. Not in the fresh fixture but checked
  with the richer stub: Review cards, Learn 10, Quiz, the time box 5 / 10 / 15, Preview and Take today's cards
  offline are Other ways items; Make a set is behind Other ways; the two daily rows' Answer it / See it again are in
  the daily sheet. `#strip`, `#finish`, `#today`, `#colls` keep their ids. `kclip*` ids are generated.
- My words: "Add a word" and "Bring words" are one "Add words" menu (all six items kept). The three dropdowns are in
  the Filters popover or sheet (same controls, moved, not rebuilt).
- Flashcards / Quiz, Run, Worksheet, the redirect: no control gone (Order and Show first are in the fold; Open word
  moved to the top tools).
- Removed selectors, grep of web/ clean: `.tw-modes`, `.tw-box`, `.wl-legopts`, `.wl-cdd`, `.deck-empty`, `.open-w`,
  `[data-daily]`, the library's `tidyChips` hooks.

### Checks

check-ui ok; `node --check` words-ui.js and every inline script; no em dash in my files; smoke page.js at 1440 and 390
for words, words/mine, words/study, words/run, words/print: NO ERRORS before and after (vocabulary: the same jsdom
navigation line before and after); the same pages with a richer local stub (words, today, insights, a 3-card run, a
finished run): NO ERRORS, menus, popover, selection, a swipe-free grade and the summary exercised.

### Not done (part 1)

- Phone Collections as a chip row above the grid: on a phone it is one closed line already, and Filters holds
  Collection.
- Flashcard stamps, fly-out, flip timing and mid-flip lift, tick fills, chip cascades, the band bars growing, sheet
  paging slides, the ladder FLIP, the save-star pop and the Speak playing state: part 2 (motion and feedback).
- Lead deck glyphs, the stubborn mark, ✓ ⌇ ★ ⠿ ‹ › ⋯ as drawn icons, spot drawings for the empty run and My words:
  part 2 (icons).
- `.split-btn` for Start plus Other ways, the drawn checkbox on tiles, `.wchip` as a white key: part 2 (shared
  controls).
- Tile word at 16px (the audit's size): at 4 columns in 728px it truncates more words; kept at 14.5.

### Shared asks

- `filterBar`: a documented `pop: 'wide'` (popover from 760px, the sheet on a phone). Words passes a getter for it;
  Tests passes `pop: true` and gets a popover on phones too.
- `.filters-pop` styling in ui.css (Tests, the library and My words each carry the same three rules).
- `.choice-row.plain` (no fill until hover) for long filter lists; the library sets it locally on Collections.
- The sidebar's Up next could skip an item whose start is the page's own Start (Today's words on /words/), instead
  of each page passing `now: false`.

### For the user

- Library: one filter row. Filters opens the six filters; the sort shows as "A–Z"; ⋯ holds Meanings, Select, what the
  marks mean, and study, share or print this view. The bar at the foot comes only once you search, filter or select.
- Today's words is the one raised card: the due count big, Start, and "Other ways" for Review cards, Learn 10, Quiz,
  the time box, Preview, Make a set and offline cards. The daily questions and By exam day are one line each in it.
- On a phone the first word now sits under the Today's words card (about 700px down): the big due number and the two
  footer lines are in it. Say if the number should stay small on phones.
- New words show no strength dots; a studied word gets a thin amber line at its foot.
- My words: one Add words menu (as in the library), Filters for the three dropdowns, your known count big with a
  status bar, and the three lower cards folded into one.
- Flashcards: three decks up front, the rest under More decks; Order and Show first under More options.
- Cards follow your finger (or the mouse) and the next card comes at once, with the last grade's line under it.
- The library no longer shows the Now strip on phones (its own Start is Today's words).
- Untested in a browser: the daily questions sheet closes and the question's sheet opens in the same tap; worth one
  look once A2's sheet exits are in.

## Premium build (part 2)

Files: web/assets/words-ui.js, web/words/{index,mine,study,run}/index.html (print and the redirect needed nothing new:
print's Back takes the caret through words-ui's map). Kept: "Twin ×10", Export and Import, the forecast and By exam
day, offline cards. No browser used (the lead's rule).

### Shared controls adopted (step 3)

- Today's words: Start and its menu are one `.split-btn` (Start, then a pill with `caret_down` that turns while the
  menu is open; aria-label "Other ways to practice"). `caret_down` turns by itself (icons.css `rotate`) and
  `.split-btn` turns it again (`transform`), so it would spin 360deg: words-ui sets `rotate: none` on its split. A fresh learner with nothing else to offer keeps Find your level
  alone. Both parts take `--touch` height on a phone or touch screen.
- Busy: every start sets `aria-busy` (part 1), so A1's spinner shows after 300ms at the same width.
- Quiet menus: the library's view ⋯, the study bar's ⋯, My words' ⋯ and the word sheet's ⋯ are `.ibtn` ghosts with
  `UI.icon('more')`.
- Drawn checkbox: a tile's select box is A1's checkbox look (18px, 5px corners, the check growing in); My words'
  table checkboxes drop their local size and accent-color, so the shared one applies.
- Chips: `.wchip` is a small white key (`--face`, `--shadow-btn`, the face hover, a pressed shadow); the current one
  uses the one selected look.
- Words tabs: the current tab's thumb (the seg thumb) is its own layer named `wtab-mark`, so a page change (Library,
  Flashcards, Quiz, My words) slides it to the new tab on A2's cross-document view transition.
- Collections' plain rows reset their fill through `:where()` (the critic's rule), so the shared hover and selected
  states still win.

### Motion and feedback (step 4)

- Flashcards (`swipe`): the card follows the pointer 1:1, turning up to 10deg; a Know (amber edge) or Again (ink)
  stamp fades in with the distance; past 80px or on a flick (0.11 px/ms, same direction) it flies out (220ms) and the
  grade waits for it; short of that it springs back with the finger's speed (`UI.motion.spring(.3, .15, v)`). A
  failed save brings the card back. Reduced motion: no follow, a long enough release still grades.
- Know / Don't know by a pointer: the card moves 24px toward its side and fades (140ms) while the grade saves; by a
  key it is instant. The next card rises from the deck's first edge (160ms); the deck's edges thin with the real count
  (part 1). The flip is 360ms on `--ease-move` with a 1.03 lift at the midpoint (pointer only).
- Order the ladder: rows are keyed and glide to their place on a drag move (`UI.glide`); the held row lifts
  (`--shadow-3`, 1.02). The drag now captures the pointer on the list, not on a row's handle: the rebuilt rows used to
  drop the capture after the first swap (a fix found while doing this).
- Mixed runs: the deck rise and the grade line under the card reset on any non-card item, so they never show on a
  later card.
- Run summary, only for a run that ended on this screen: the score rolls up from 0 (`UI.roll`), the Moved to Known
  chips (white keys with a check) land 40ms apart (chips past the 12th land with the 12th), then the known total
  rolls (part 1's roll, now timed after the chips).
- Today's words ticks: back from a run in the same tab, the ticks learnt since the last look light in turn
  (`UI.meter().set()`, kit's 20ms steps); reaching the goal just then draws a check by the label (`UI.fx.check`).
  Never on a cold load (a sessionStorage note per day).
- Library grid: a filter or a collection glides the tiles (`UI.glide`, keyed by slug; stayers slide, new ones rise; up
  to 160 tiles, beyond that it repaints at once) and the count rolls (`UI.roll`). Show more glides up to 600 tiles
  (only the added ones enter). Search keystrokes stay instant.
- Word sheet: paging by the arrows or a grade slides the body 12px the way it went (160ms); Show wipes the covered
  blocks open top to bottom (200ms). Both pointer only; Space and the arrow keys stay instant.
- Page entry (`data-m="stagger"`, kit plays it once per fresh visit): the library's main column and aside after the
  first paint (`data-m-now` on the hero), the study options' sections, My words' aside (`data-m-now` on its hero).

### Icons and drawings (step 5)

- words-ui.js `PATHS` and its stroke string are gone: `ic()` (still `UI.word.icon`) calls `UI.icon`, reading `left` /
  `right` as `caret_left` / `caret_right` (the steppers; in the map left / right are arrows). Speak, star, flag, more,
  plus come from the map.
- The star: the sheet's and the run's Save are `aria-pressed` buttons with the star twin (amber fill, amber-deep
  edge); the local `svg path { fill }` hacks in words-ui.js and run are removed. A saved tile and the legend show
  `UI.ICON_FILL.star` in amber.
- Run: the exit `x` from the map (the local XICON is gone); ‹ › on the card steppers and "‹ Previous" are
  `caret_left` / `caret_right`; the ladder's ⠿ is `grip`. The library ⋯ and the study bar ⋯ were text; My words' ⋯ was
  text. The filter chips' remove mark is `x`.
- Flashcards / Quiz: the lead decks carry a glyph (Today's words `today`, Due `review`, New `plus`, From the Library
  `list`); the chosen one shows the filled twin.
- `UI.spotArt`: `start` on My words' first-use empty (in place of part 1's sample wall: one drawing per empty), the
  library's "No words yet" and the run page with no run; `lost` on "No such run"; `clear` beside "Done for today" in
  Today's words (48px). Filtered empties have none.
- Left as text, drawn by Marks: ✓ and ⌇ on tiles and in the legend, ★ in My words' table, • and ⌇ in the wall
  legend, ● ○ ◐ in Bring words from a text.

### Checks

check-ui ok; `node --check` words-ui.js and every inline script; no em dash; smoke page.js at 1440 and 390 for words,
mine, study, run, print: NO ERRORS; the richer local stub: NO ERRORS, with the split button, a collection change
(the same grid node kept, 39 tiles, count and chip updated), a swipe (stamp at full strength, the card at the
pointer, the grade line under the next card), the summary (score, check chips) and a ladder drag (the rows reorder,
the held row marked) exercised. Inventory diff unchanged from part 1 (the split's menu part is "Other ways to
practice"; it was "Other ways").

### Not done

- The progress strip's fill-in per grade and the save star's pop: a star is not a reward (one bounce is for
  rewards), and the twin's crossfade already marks it.
- Speak's playing state: a pulse would loop (nothing loops but a spinner).
- Sprint "New best" pop and the placement band bars growing: kept static (the badge and bars show at once).
- The worksheet's New version crossfade and code roll.

### Shared asks

- Part 1's asks stand (`filterBar` `pop: 'wide'`, shared `.filters-pop`, `.choice-row.plain`, the sidebar skipping an
  Up next that is the page's own Start).
- ui.css: `.split-btn > [aria-haspopup][aria-expanded="true"] > svg` (transform) and icons.css's `ph-turn` (rotate)
  both turn `caret_down`, a full turn together; one of them should go (Report's `.rp-split` swap meets it too).
- A shared dropdown chevron on `.dd` / `[aria-haspopup]` buttons (BUILD's open item): the Words `.dd` buttons (Add
  words, the run summary's More) still use the CSS chevron.

### For the user

- Flashcards: drag a card (finger or mouse): a Know or Again stamp shows; let go past about 80px or flick, and it flies
  off and grades; a short drag springs back. The next card comes up from the stack.
- Start in Today's words is one button with a small menu part on its right for the other ways.
- After a run the score counts up, the words that moved to Known land one by one, and the Today's words ticks you
  earned light up when you come back to the library.
- The Words tabs' highlight slides to the new tab when you switch pages.

## Visual review

Files: web/words/{index,mine,study,run}/index.html, web/assets/words-ui.js (print and web/vocabulary/index.html needed
nothing). Three rounds of real-browser shots against the local copy (a learner seeded with 110 studied words: 40 known,
15 claimed, 28 due, 10 saved), each at 1440 light, 1440 dark and 390, plus hover, Tab focus, the Filters popover, the
Start menu, the ⋯ menu, the word sheet, a collection pick, a flashcard flip, a half drag each way (stamps), a grade
and the run summary. Shots: `spec/redesign-2026-10-19/premium/shots/app-review/words-r0-*` (before), `words-r1-*`,
`words-r2-*` (after).

### Per screen

- **Every Words page with the sidebar (Library, Flashcards / Quiz, My words)**: the header sat about 64px below the
  save-progress banner. The shell puts its banner and a 1px sentinel inside `main`, and these pages made `main` a grid
  with a 32px gap, so each shell node added a gap. `main` is block now and only the page's own blocks are spaced
  (`.wl-head ~ *`, `.st-head ~ *`, `.wm-head ~ *`). The header sits under the banner as on Profile.
- **Library, one orange**: `UI.shell('words', { now: false })` passed its options as a second argument, which the shell
  ignores, so the phone still showed the Now strip and the sidebar's Start stayed orange beside the hero's Start.
  Now `UI.shell({ page: 'words', now: false, ownPrimary: true })`. Flashcards / Quiz and My words pass `ownPrimary`
  too (their hero holds the orange: Start, Review). The banner's Save progress is the shell's.
- **Library, word grid**: the word reserved 64px on its right for marks every tile, so "accommodate", "acknowledge"
  and every sense ("abstract · summary") were cut. The marks (Due, ✓, ⌇, the star) now share the word's line and take
  room only when present. The hover line (part of speech, difficulty bars) moved under the topic, so a tile at rest
  reads as the word with its topic under it, with no empty middle row.
- **Library, other tile views** (r2 `lib-roots`, `lib-transitions`, `lib-select`): the rows under the word keep their
  source order and span the tile; only the hover line goes last. Root tiles read root name, "root", three words,
  "family known n/m", and long root names ("in.into") are no longer cut. The transitions map and Select mode (the
  checkbox at the foot, the strength line stopping short of it) are unchanged.
- **Library, one filter row**: no change needed. The Filters popover, the A–Z sort and the ⋯ menu show one drawn
  caret each, and the Start / Other ways caret turns once (rotate 180, no transform).
- **Library, Collections**: the amber dot before every due count (five decorative oranges) and the 2px known bar
  under each row (they read as stray dashes and hairlines) are gone. The meta line still says both ("18 due ·
  17/550 known"). The name truncates before the meta can overflow the column ("Answer-choice langu…" pushed past the
  edge).
- **Library 390**: Add words sits beside the title, the meta wraps under it, and the tabs take their own row. Add
  words no longer sits alone on a row.
- **Today's words hero**: unchanged; reads well in both themes. The Start / Other ways split turns its caret once.
- **My words**: the Wall's 1,200 outlined "new" cells were the clustered part. A new cell is now a faint solid
  square with no outline (the legend's key matches), and Learning, Claimed and Known keep their fills. "Big cells"
  wrapped alone under the legend; the legend now wraps in its own column and Big cells stays at the right of its first
  line. The hero's Due today, Learning and Saved rows are plain rows (a hover band; the picked one keeps the shared
  selected look) instead of three grey slabs in the card. At 390, Add words and ⋯ stay beside the title.
- **Flashcards / Quiz, deck rows**: plain rows like Collections; the chosen deck keeps the wash band and amber edge.
  The glance card is the aside itself, so it took the aside's -8px shadow room (8px past the content edge). `.card`'s
  `position: relative` also beat the aside's sticky and its `top: 16px` pushed it 16px down. It now lines up with the
  content and stays sticky. On a touch screen, Start no longer shows an "Enter" key.
- **Run, the raised card over a stack**: the deck edges shrank from the centre, so the 6px and 12px offsets were
  eaten and no edge showed. They shrink toward the card's foot now (7px and 14px show), with room so "4 left" clears
  them. Checked at rest, mid-drag both ways, light and dark.
- **Run, top bar**: the exit and four tools were five bordered keys (heavy at 390). They are the shared `.ibtn` ghosts,
  and the Save star's twin still fills when pressed. The current progress segment was ringed in 3px ink (the thick
  dark ring the user turned down); it is now one fill step darker, with no ring.
- **Run, controls**: Previous and Next showed a caret and a ← / → key cap side by side, the same arrow twice. Now
  just the caret, with the key in the title. "More examples" used the browser's ▶ marker; it is the shared
  `details.fold` caret now.
- **Run, stamps**: Know (amber-deep on an amber edge, -6deg) and Again (ink, 6deg) fade in with the distance; they
  read well. No change.
- **Run summary**: a word the run requeued showed twice under Still learning ("arrest · halt" ×2). One chip per word
  now. At 390, More wrapped alone; the pill now takes the row and the button and More share the next one.
- **Word sheet** (words-ui.js): the five bordered tool keys in the head are `.ibtn` ghosts. The covered plates no
  longer have a hairline between them (the plates already separate the blocks; the hairline before "Easy to mix up"
  stays). On a touch screen the foot drops its Space / 1 / 2 key caps.
- **Print, the /vocabulary/ redirect, fresh learner (library, My words, Flashcards)**: fine as they were.
- **The lead's round-3 checks**: the local `.filters-pop` rules are gone from the library and My words (the shared ones
  apply). Every `.dd` on Library, My words and the run summary's More shows one drawn caret (no svg, one `::after`);
  Study has none. The Start / Other ways caret turns once. words-ui.js's stale "keep one turn" comment is removed.
  All 390 shots ran with touch and a coarse pointer (`hasTouch`, `isMobile`).

### Checks

check-ui ok; `node --check` words-ui.js and every inline script of the five pages; no em dash in my files; smoke
page.js at 1440 and 390 for words, mine, study, run, print: NO ERRORS, the same output as the pre-review files
(vocabulary: the same jsdom navigation line as before); inventory.js at 1440 and 390 for the five pages identical
before and after.

### Shared asks

- **Blocking, kit.js `roll()`**: `const from = el.textContent, off = from.length - text.length` shadows the module's
  `off()`, so `off()` a few lines down throws "off is not a function" whenever a digit moves. Rename the local (e.g.
  `shift`, used once more in `from[i + off]`). On Words this shows as: the run summary's score stuck at "0 known / 6"
  (the page sets 0, then rolls), the known total never rolls, and on the library a collection or filter pick throws
  inside `legend()`, so the grid, the count and the study bar do not repaint (r2 `words-r2-lib-coll-1440.png`).
  Every `UI.roll` caller on other pages hits it too. The r2 summary shots show 0 until this lands.
- ui.css: when the `.twocol-side` aside is itself a `.card` (Study's glance), `.card { position: relative }` wins over
  the aside's sticky, and the aside's `top: 16px` then shifts it 16px down; its -8px shadow margin also pushes the
  card past the content edge. Words fixes this locally (`.st .glance { margin: 0; position: sticky }` from 1280px). A
  shared `.twocol-side.card` rule would cover any other page.
- ui.css: one rule hiding `.kbd` on touch screens (`@media (hover: none) and (pointer: coarse)`). Words now carries
  three local copies (run, study, words-ui's sheet and Today's words).
- ui.js: `UI.shell(page, opts)` silently drops `opts`. Accepting the second argument, or warning on localhost, would
  have caught the library's lost `now: false`.
- ui.js: the shell's banner and sentinel go inside `main`, so a page that makes `main` a grid with a gap gets two
  extra gaps above its header. No other page does this today (checked); worth a line in the shell's header comment.
- Data, not UI: the summary's "Next reviews: 6 in 3 days" counts a requeued card twice (server `schedule`), while the
  chips now show 5 words.


### Round 3

After the lead's kit.js fix (`roll()`'s local is `shift`), checked in the browser at 1440 light, 1440 dark and 390
(touch), shots `words-r3-*`. **No page or console errors** on any of the runs below.

- **Run summary** (`words-r3-summary-*`): the score rolls up to the real figure, "5 known / 6" (one requeued card),
  in all three. "Still learning · all 5 back in 3 days" shows one chip per word.
- **Library redraws** (`words-r3-lib-coll-*`, `words-r3-lib-filter-*`): picking SAT core sets the count to "550 words",
  adds the SAT core chip, shows the study bar and repaints the grid. Adding Status = Known (popover at 1440, the
  shared sheet at 390) gives "17 words", 17 tiles and both chips. Picking All again leaves Known on: "40 words".
- **The lead's four asks**:
  1. Past the goal, the new-words meter says "146 · goal 10 ✓" under "New words today" (the label already says
     today), not "146 of 10". Up to the goal it still reads "3 of 10". The animated count-up passes the same text.
  2. The picked row is a tint band in 600 with no 2px amber edge, like the nav's current item. This applies to the
     library's Collections, the Flashcards / Quiz decks and My words' status rows (the same list look on all three
     Words pages). The row height is unchanged (the edge was an inset shadow).
  3. Library tiles fit their content: the word, the topic, and the strength line at the foot when studied (about
     60px, was about 76px with an empty reserved row; 8 rows on the 1440 first screen, was 7). On a mouse, the part
     of speech and difficulty show in the topic's place on hover or focus, with no reserved row. On a touch screen
     they show always, on their own line. Root tiles, the transitions map and Select mode keep their layout. Meanings
     mode keeps its own line.
  4. Once the goal is met, the ticks turn the calm `--amber-200` tone, so Start under them is the one orange in
     the card. Ticks still lighting toward the goal stay amber.
- Also: the My words tab's due dot is graphite, like the shell's count dots now (it was amber beside the hero's
  orange).
- The narrowed library's study bar: Flashcards is a plain `.btn` now, like Quiz beside it (the lead's call). The hero's
  Start is the one orange (`words-r3b-lib-coll-*`, `words-r3b-lib-filter-*`; the same redraw checks pass, with no
  errors).

Checks: check-ui ok; `node --check` words-ui.js; no em dash; smoke page.js NO ERRORS for words, mine, study, run and
print at 1440 and 390; inventory.js identical to the pre-review files for words, mine, study and run at 1440 and 390.

### For the user

- My words passes `ownPrimary`, so the sidebar's Start is a white button there. A learner with history but nothing
  due today sees no orange button on My words' first screen (Review shows only when words are due). Say if that page
  should keep an orange Start.

