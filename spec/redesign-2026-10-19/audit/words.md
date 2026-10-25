# Audit: Words (library, My words, Flashcards/Quiz setup, run, print, words-ui.js)

Code-level, 2026-10-19. Files: web/words/{index,mine,study,run,print}, web/vocabulary/index.html, web/assets/words-ui.js (+ words/sw.js).
Geometry used: 1440x900 with the 248px sidebar leaves main 1192px; `.page` max 1120 with 40px gutters gives a 1040px
content column, top pad clamp(16, 3vh, 32) = 27px. 900px tall is under the shell's 1099px tier, so the Now strip (Up next)
sits at the top of main (+16px margin + the page's own grid gap). 390x844: 16px gutters (358px), phone bar on top,
64px tab bar at the bottom, about 724px usable.

## 1. Library (web/words/index.html)

First screen, 1440x900: Now strip ~52 +36, header 44, gap 20, Today's words card ~120 (22 pad, h2, 40px row, debt
note), Make a set field +52 (index.html:145, rendered as a sibling after the card, words-ui.js:457), gap 20, tabs 40, 20,
the strip ~140 (4 stat tiles: Due today, New today, Word of the day, Transition), 20, empty `#finish` 0 +20, Collections
summary 16, 20, filter row 44, 20, legend row 32, 20. The word grid, the page's actual content, starts at ~790px:
one row of tiles at most is visible on arrival. 390x844: the same stack reaches the grid at ~1,100px (more than a screen).

- A. Two jobs on one page: daily launcher (Today's words + strip) and the word bank (search, filters, grid, study bar).
  The grid and the study bar (Flashcards/Quiz) are the page; Start (Today's words) is the daily primary. No single
  first-screen action: three "start" surfaces (Today's words Start, strip Review / Learn 10, Now strip Start).
- B. `.wl` gap 20 and padding-bottom 150 (index.html:20; phone 240 at :128) though the study bar is 68px (56 on phone)
  and hidden on arrival; empty `#finish` (:148) still costs a 20px grid gap; `.wl-more` margin-top 24 (:92); tiles
  min-height 92 with 10/12 padding (:72-73); `.ctile` 92 (:51); strip tiles min-height 160 on phone (:118).
- C. Always on but secondary: the legend line (:68, :600-606, a glyph key that explains the UI; DIRECTION 5 says
  tooltip or Help); the strip's Word of the day and Transition (useful, but side-column material); Collections tiles
  (already folded, :365, but open while a collection is chosen, :366). FOLD_SEL catches only `.help` / `.tw-note` here:
  the logic map's "Most mixed up with" `.help` (:583) is under 70 chars, never folds; nothing else on the page folds.
- D. Right column (`.split-side`, 300px): Today's words (with Make a set), Due/New facts, Word of the day, Transition,
  Collections as a filter list with known bars, By exam day (see section 7). Main keeps header, filter row, grid.
- E. The due count shows five times: sidebar nav badge (ui.js:1502), the "My words" tab count (words-ui.js:324), Today's
  words facts (words-ui.js:395), the strip's Due today tile (index.html:262-273), the DUE marks on tiles. The debt
  actions "Spread over N days" / "Do all now" appear twice: strip (:263-267) and the card's `.tw-note`
  (words-ui.js:459-464), because `noDebt: true` (:225) is passed but never read in words-ui.js. Learn 10 / Review exist
  in both the card (words-ui.js:401-405) and the strip (:269, :281). The Collection dropdown in the filter row and the
  Collections tiles set the same `c` filter. Up next in the Now strip is often Today's words itself.
- F. `.wl-strip .big` (:32) re-implements `.stat-v` in mono 26px instead of `UI.tile`; `.wtile .w` clamp(14px, 1.15vw,
  17px) (:75) is off-scale (16.6px at 1440); `.wtile .tag` 10.5px mono uppercase .06em (:77) on every tile; `.qd-key`
  700 20px (:38); `.logic-col h3` 700 15px (:98); search and Add words at 44px (:25-27) beside 40px dropdowns. `.wl-bar`
  shadow rgba(0,0,0,.25) (:104). `DUE` (:516, styled :83) is --amber-deep at 10.5px: 3.2:1, below AA for text. Three local tile buttons (`.ctile`, `.wtile`, `.logic-col .wtile`) with the same pressed state.
- G. Uppercase mono part-of-speech tag on ~1,300 tiles (the loudest tell in scope), `.k` kickers ("Collections", group
  names), `.stat-k` uppercase ("DUE TODAY"), glyph soup in the legend (dots, bars, check, squiggle, star), triangle
  glyphs drawn by CSS content (:43-44), "Add words" with a text caret (:142), "+ New list" (:357), a card grid of
  collections with progress bars.
- H. "Practise · 8" (:578) vs "Practice 10" (words-ui.js:865): pick one spelling. soon() "That is not ready yet." (:202)
  is dead (UI.bringWords always exists). Tooltip "Daily goal, set in Plan. It is never a cap." (:283) is fine.
- I. `#q` is in the header in HTML (:141) and is moved into `#fbar` after load (:444): layout jump, and the header row
  loses its search. `#fbar > #q` min-width 240 + height 44 (:26). The gear's option row is shown with inline
  `style.display` (:440). Phone: `.wl-bar` (56px) sits on the 64px tabs, ~120px covered while the grid is in view.

## 2. My words (web/words/mine/index.html)

First screen, 1440x900: Now strip, header 38, Today's words compact card ~88, tabs 40, stat tiles ~110, two cards
(traps, habits) ~250, view bar 44, gaps 22 each: the list starts at ~860px. Default view is the wall, which shows every
library word (~1,300 cells, :360) although the meta says "312 studied or saved". 390x844: stats 2 columns (:67), the
two cards stack (:65), `.wm-view` nowrap (:35) holds "Filters · n" plus the Table/Wall seg; the list starts well below
the first screen, and the wall paints 13.2px cells (:50), far under a 44px tap target until the hidden `.k` toggle.

- A. Purpose: see and act on the words you have touched. Primary action is unclear: Review (inside a tile), Twin x10
  per trap, bulk bar. The add/import/export tools are gone (section 7).
- B. `.wm` gap 22, padding-bottom 150 (:19) with no fixed bar; `.wm-stats` repeat(4) (:22) but `stats()` renders at most
  3 tiles (:152): a permanent empty quarter. `.wm-empty` padding 24 (:63).
- C. `.wm-line` explanations always on and not in FOLD_SEL: "No trap has caught you... name the trap behind every miss"
  (:196, 97 chars), "After a few due reviews this shows..." (:226). Wall legend "Tap a word's cell to open it" (:428)
  explains the UI and says Tap on desktop. Empty-state `.help` (:375) is 62 chars, never folds.
- D. Right column: the status tiles as a filter list (Due today with Review, Learning, Saved), How you miss words, How
  your schedule is working, and the restored forecast and By exam day. Main: view bar + table/wall + bulk bar.
- E. Due count five times again: sidebar badge, tab count, meta (:138), compact Today's words facts, Due today tile.
- F. Wall cells 13.2 / 3.3 / 48.4px (:49-57, off the 4px grid); `.wcell.learning` and its legend rgba(63,63,63,.3)
  (:51, :60) stay dark grey in dark mode and nearly vanish on --paper #1A1917; `.wall-legend` and `.wm-list .due` mono
  (:44, :58), the latter amber-deep 12.5px (3.2:1). Inline styles :202, :208, :311.
- G. `.k` row labels ("EASY · 412"), trend triangles (:198), "Twin ×10" (:200) with a times sign.
- H. "Practise finding the clue · 10" (:211); h2 "How your schedule is working" vs aria "Your schedule" (:93);
  import placeholder and table use the em dash character (:266, :298; the parser at :281 must keep accepting it).
- I. `.wm-bulk .selbar { bottom: 0 }` (:64) out-specifies ui.css's phone `bottom: calc(76px + safe)`: on a phone the bulk
  bar sticks under the 64px tab bar (z 25 vs 30). Review is a `<button>` inside the `button.stat` from UI.tile (:162):
  nested interactive. Wall arrows move ±20 (:436) but a 1040px row holds ~57 cells, so Down is not down. The phone
  "big cells" toggle is a click on a `.k` span (:421), bound only if the page was painted under 760px, no keyboard, no
  affordance. Phone table hides Level, Right/total, Last reviewed and Saved (:401): desktop info the phone never shows.

## 3. Flashcards / Quiz setup (web/words/study/index.html)

First screen, 1440x900: header 38, compact Today's words ~88, tabs 40, then `.st-grid` (main 696px + 24 + 320px
glance). Decks auto-fill 200px gives 3 columns at fixed 104px rows (:35): 10 non-empty decks = 4 rows = 440px, then
the empty-decks fold and the options. Start (glance, sticky, :45) is visible on arrival. 390: the glance becomes a
fixed bar above the tabs (:57-68) and Start stays in reach; good.

- A. Clear: pick a deck, set options, Start. The compact Today's words card (:131) adds a second Start
  ("Start today's words") for what the "Today's words" deck (:150) already is.
- B. Padding-bottom 140 on desktop (:19) though the glance is not fixed there; `.st-opts` gap 22 (:23), `.st-more-in`
  22 (:31); deck tiles 104px rows with 12/14 padding.
- C. Good pattern already: long explanations sit in ⓘ tooltips (:238, :243, :262, :271, :279) and timer / Method /
  Move on are under "More options" (:282). The "At a glance" kicker (:313) and the descriptive `.line` (:316) repeat the
  options just chosen. `.deck .help` lines are short, never fold.
- D. The glance already is a right column (320px, from 1000px). Align it with `.split-side` (300px, 1280px+) or keep
  its own breakpoint; Print / Grade a worksheet (:321-323) belongs there (it is).
- E. Meta "12 due · 212 known · 64 claimed" (:130) repeats the Due deck count and the sidebar badge.
- F. `.glance .pill` 46px, font 15 (:49) against the 42px rule; `.glance .big` mono 28px (:46); `.deck .n` mono (:40);
  triangle-glyph summaries (:28-33) are a second local copy (library and words-ui have others).
- I. Decks are `<button role=radio>` holding a `<select>` (:202-213): nested interactive (Firefox does not open a select
  inside a button reliably; screen readers flatten it). Phone: `.deck .n` goes static (:72) so decks with count + select
  (Fell for a trap, My own) need ~112px in a 104px fixed row and overflow into the next row.

## 4. Run (web/words/run/index.html, no chrome)

A: one item, grade or answer, then the summary; keep chrome-free. 390: `.fcard` 56vh (:136), grades fixed at the
bottom (:138); fine. Issues are local styling:
- F/G. Mono for words: `.wr-left` "12 left" (:44), `.fpicks` "Last time you picked" (:62), `.guess-chip` (:118); clocks
  in mono are fine (:37). Radius 999px: `.guess-chip` (:118) and the auto-next ring around a 10px-corner pill (:116).
  `.fword` 800 clamp(36-56px) (:55) and `.wsum .score` 800 clamp(44-64px) (:120): content display, keep big but 700.
  `.fstack::before/::after` fake cards behind the card (:46-49) are decoration. Summary rows are filled `--tile` boxes
  (:124) instead of hairline rows. 20 inline styles (:237-242, :363-366, :421, :535, :551, :612, :622, :633, :673,
  :675, :788, :868, :882, :888); fail() and the offline finish use class `.wl-msg`, which only index.html defines.
- B/I. `.sort-btns button`, `.wstage .btn`, `.wquick .btn` min-height 52px (:80, :87): over the 48px rule;
  check-ui.py does not flag `min-height` on generic buttons. Up next row (:891-907) can hold 6 equal buttons.
- C. FOLD_OFF covers /print, /report, /help but not /words/run, so a `.help` of 70+ chars folds mid-run: the server's
  `s.caution` (:865, :885). The commit hint (:554) is 69 chars, one character from folding.

## 5. Print, vocabulary, sw.js

- print: A is preview, print, grade back; clear. 390: QR hidden, options one column (:53-56); fine. Loads the shell (:79) although DIRECTION 4 lists print pages as chrome-free; the toolbar has its
  own Back. Paper colours #fff / #16150f / #55534a (:25-50) are defensible (a paper preview stays white in dark mode):
  make them local custom properties. `.ph h1` 800 22px (:28). Empty key letter is the em dash character (:136).
- vocabulary/index.html: a redirect to /words/, nothing links to it; keep as is.
- sw.js: SHELL (sw.js:9-10) omits /assets/fonts/Geist.woff2, so an offline run falls back to a system font; bump the
  cache name when the redesign ships.

## 6. words-ui.js (every Words page; quick.js:629 also lazy-loads it on any page for Add a word)

- F, global leak: the injected sheet `:is(.tw-row, .go, .ws-foot, .sheet-foot, .upnext, .wr-ctl, .hook) > :is(button, a,
  .btn, .pill, .quiet) { min-height: 44px }` and `> .pill { height: 44px }` (:128-130) restyle every shared `.sheet-foot`
  on any page once loaded, and claim the generic `.go`. `.wsheet > .sheet-head h2 { font: 800 32px !important }` (:60,
  28px phone :58).
- F, pill overrides: `.tw-row .pill` min-width 150 (:45), phone min-height 48 (:50), then `.today-words .tw-row > .pill`
  height 40, min-height 40 (:140) wins by specificity, so the phone Start is 40px (under the 44 touch target).
  `.tw-modes > .btn { border-radius: 0 }` joined group (:141-143) is a de facto new button style.
- F, other: `.wtabs` (:32-39) is a hand copy of `.seg` with a --tile track and wash state (seg uses tile-2 and paper);
  `.wtag` radius 999px (:68); `.shade-bar` gradient (:162); mono for words in `.tw-facts` (:43), `.ws-sub` (:66), `.wtag.m`
  (:69), `.confu .fell` (:91), `.journey .nx` (:102), `.ws-mode` (:114), `.wfin-left` (:159), "Covered" (:111); h2 sizes
  17 (:42) and 15 (:137) vs the 16px section step. Inline styles :729, :760, :830, :1138, :1157.
- C. FOLD_SEL hits here: `.tw-note` (debt line with two action buttons, :461) folds if it ever reaches 70 chars and would
  hide its actions; the server `s.reason` `.help` (:466) may fold (fine); the offline line "Grades wait on this device..."
  (:364, 80 chars) folds although it is live status. Everything inside a sheet (word sheet, Add, Bring, Grade) never
  folds (dialog is in FOLD_SKIP).
- C/G, word sheet (:577-899): every block has an uppercase mono `.k` (Meaning, Shades, Built from, Examples, SAT-style,
  Same as, Easy to mix up, Your record); ws-sub plus a row of 999px tags before the meaning; the SAT-style sample sits
  mid-sheet and pushes Same as / Mix-ups down. "Your record" is mostly meta (reviews by kind, first seen).
- H. Em dash character as the blank part-of-speech option (:945). "Twin" (:782) is the app verb; fine if Help defines it.

## 7. Unreachable today (not a redesign loss, but the user may think these exist)

- My words tools: `tools()` (mine:230-241) is never called and `#tools` is not in the HTML, so Add a word (button),
  Bring words, Export CSV, Print this list, Share a list and Grade a worksheet are gone from My words. Import a file
  (`importSheet`, :265) and the Add a word button show only in the empty state (:372-376, via `bringItems` :242-246) and
  vanish after the first touched word; Export CSV (:257) is reachable nowhere. (Add, Bring, Grade live in the library.)
- Forecast: `forecast()` (mine:167-189, 14-day due chart, reviewed today / this week / streak, weeks to the exam) has
  no `#forecast` host and is never called.
- By exam day: `UI.wordsFinish` (words-ui.js:486) is exported, no page calls it; the library's `#finish` div is empty.
  It held at-risk words + Review them, what is left to learn, and the New-words-a-day goal chips.
- Offline cards: `offlineRow` is commented out (words-ui.js:371), so `offline.take()` never runs, the service worker is
  never registered and the IndexedDB queue only serves runs stored before the change.
- Ask the user: restore each into the right column (recommended for forecast, By exam day, the tools menu) or delete.

## Redesign proposals (ranked by first-screen gain)

1. BIG. Library on `.split` (index.html:134-152). Main: one header row (h1 + meta | `.wtabs` | Add words), the filter
   row with `#q` placed there in the HTML, the grid. Aside (sticky top block): Today's words with Make a set inside it,
   the Due/New facts merged into its fact line (delete the strip's Due today / New today tiles and the duplicate debt
   actions, read `noDebt`), Word of the day and Transition as two compact rows, Collections as a radio-ish filter list
   with known bars (keep the fold below 1280px), By exam day restored and collapsed. Legend becomes a `?` popover by the
   result count. Grid starts at ~135px instead of ~790 (~225px if the shell keeps the Now strip in main). Must survive: every filter key and URL param (c t f d s p sort
   q m w), Select with shift-range and X, `/` and `N`, the ⋯ menu (Share, Print, Grade), the logic map and roots views,
   `?w=` deep link, daily answer sheets, New list, Spread / Do all now, the placement entry for fresh learners. Phone:
   aside stacks after the header (Today's words), daily rows swipe, Collections fold, then search + grid. Risk: medium
   (DOM moves only; all handlers are id-based).
2. BIG. My words on `.split` (mine:86-97). Aside: status filters as rows (Due today with Review as a sibling button, not
   nested), traps, habits, restored forecast (barChart fits 300px), By exam day. Header: h1 + tabs + Add a word +
   Bring words + ⋯ (restore `tools()`: Export CSV, Import, Print this list, Share a list, Grade a worksheet). Default
   the wall to `mine` unless a collection or tile is chosen, or relabel it "All words by difficulty". Drop the 4th
   empty column (:22). Must survive: `?tile=` `?view=`, bulk bar, J/K/X, wall arrow grid (fix to real row length),
   print stylesheet. Risk: medium; the wall default is a visible behaviour change, ask the user.
3. BIG. Study decks as rows (study:35-43, :198-221): a 2-column radio list of 40px rows (label, count right-aligned,
   help as tooltip), the chosen row expands to show its `<select>` outside the radio button. Fixes the nested select and
   the 104px overflow, and cuts ~200px. Delete the compact Today's words card here (the Today's words deck is the same),
   moving "Find your level" for fresh learners into the glance. Must survive: radio semantics, `aria-description` on
   empty decks, the empty-decks fold, `?words=` from deck, `?deck=`, Enter to start. Risk: medium.
4. Kill the global leak (words-ui.js:128-131): scope to `.wsheet .sheet-foot`, `.today-words .tw-row`, `.wr-ctl`,
   `.wsum .upnext`, `.hook`; rename nothing. Drop the h2 `!important` (:58, :60) for 22px/600. Risk: low.
5. One pill size: remove `.today-words .tw-row > .pill` (:140), `.tw-row .pill` min-width (:45), `.glance .pill`
   (study:49); phone Start gets 44 from `--touch`. Make `.tw-modes` three plain `.btn` with an 8px gap. Risk: low.
6. Slop pass in scope: `.wtile .tag` to 11.5px Geist sentence case, or hide it behind `.reveal` (POS stays in the tile's
   aria-label); `DUE` text to a dot + "due" in --ink; `.wtag` and `.guess-chip` to 8px corners; auto-next ring to 10px;
   every local mono-for-words rule to Geist (list in sections 1-6); one shared summary chevron instead of three copies
   of the triangle glyph CSS; `.shade-bar` gradient to a plain hairline; drop `.fstack` fake cards. Risk: low.
7. Word sheet: ws-sub + tags on one meta line, Meaning first; "Your record" details (reviews by kind, first seen,
   looked up) behind a fold; SAT-style sample after Examples and Same as. Must survive: every block, Covered / Open
   (W14), keys arrows Space 1 2 P B, hook save, own-word Edit / Delete, Report. Risk: low to medium.
8. Run tidy: 20 inline styles to classes, `.wl-msg` to a run-local class, summary rows to hairlines, 52px option buttons
   to 48, `.wr-left` / `.fpicks` to Geist, scores 700. Keep the no-chrome surface and every key. Risk: low.
9. Whitespace: padding-bottom 150/140/240 to bar height + 16 (68+16 desktop when a bar can show, else the `.page`
   default); grid gaps 20/22 to 12; drop empty `#finish` or render By exam day into it; tiles min-height 92 to 72.
10. Fixes: mine bulk bar under the phone tabs (:64, delete the bottom: 0); nested Review button (:162); wall arrows;
   wall `.learning` colour to a token mix of --ink; amber-deep small text to --ink; phone table shows the hidden
   columns as a second meta line; `.tw-note` and the offline line get `data-nofold`; sw.js caches Geist. Risk: low.
11. Copy: one spelling (Practice), "Twin ×10" to "10 more like this" if the shared verb allows, wall hint without
   "Tap", import placeholder without the em dash character (parser unchanged), print key blank as a plain hyphen.

## Shared asks (lead only: ui.css, ui.js, kit.js)

- Add `/words/run` handling: either `\/words\/run` in FOLD_OFF or document that run pages mark `.help` with data-nofold.
- `.k`, `.meta`, `.stat-k`, `.stat-v` off mono and uppercase (already planned); the Words sheet and pages inherit it.
- `.chips` radius 999px to 8px (ui.css:1065-1067): study's Question types, the time box and By exam day chips inherit it.
- `.split` / `.split-side` and `.reveal` primitives (proposals 1-3, 6).
- A shared pressed-tile button (wash + amber inset) to replace `.ctile`, `.deck`, `.wtile` local copies, or a
  documented `.btn[aria-pressed]` row variant.
- `UI.tile` option for a secondary action rendered beside, not inside, a button tile (mine:162).
- `.selbar` phone offset should win over page rules (or pages must not set `bottom`).
- Optional: a sub-nav slot under the active left-nav item, so Library / Flashcards / Quiz / My words can leave the page.
