# Audit: Review (web/review/**, web/mistakes/)

Code-level only. Geometry at 1440x900: sidebar 248, main 1192, `.page` 1120 max with 40 gutters, so 1040 of
content; the Now strip shows (height < 1100). Phone 390x844: pbar 56, gutter 16, 358 of content, tabs 64.

## Files

| File | What it is | Weight |
|---|---|---|
| review/index.html (301) | the hub: header, notes, six tiles as tabs, tab head, options, filters, list strip, pane, action bar; 245 lines of page CSS | main |
| review/review.js (2053) | all of the hub | main |
| review/item.js (58) | API item to UI.review item; only UI surface is `EVENT` labels and `srcWord` | none |
| review/sheet/ (85 + 266) | worksheet answer sheet, result card, printed key | medium |
| review/walk/ (56 + 219) | holding page for the walk player (dialog over it) | low |
| review/print.html (252) | trap sheet and error log, screen + paper | low |
| mistakes/index.html (24) | redirect to `/review/?tab=redo` (server 307s first). Nothing to redesign; keep. | none |

## Headline: two things every student hits

1. **The list is a sideways ribbon at every width.** `#list.rh-list` is `display:flex; overflow-x:auto` with
   rows `flex: 0 0 min(400px, 86vw)` (index.html:113-115) and `.l2` and `.tags` hidden inside it (167), with no
   phone override. So a phone swipes sideways through 335px cards, and on every width the status tags (New,
   Stuck, Relapsed xN, Sure x, Half fixed, Due, Check due, Not checked yet) and the meta line (skill, level,
   last date, source, picked X, pts) are never shown in any list. Group heads (`.rh-group` is
   `display:contents`, 114), History day `h3`s (944-948) and whole `.rh-sit` sitting cards (957-961) become
   flex items in the same ribbon; sitting cards have no flex-basis and nest a second horizontal scroller
   (1051). "Load 50 more" sits at the far right end (594-597). The preview sheet reuses `.rh-list` (249), so
   the modal list scrolls sideways too. The comment at 102 says the strip is deliberate: confirm before undoing.
   Directly contradicts DIRECTION "lists are rows, not cards".
2. **The task starts below the fold.** Redo at 1440x900 with 5+ open and new misses, top to bottom: page top 27,
   Now strip 60, header 88 (Minutes seg 40 + 8 + Start 40), new-misses card 20+74, tiles 18+80, tab head
   18 + named-rate line + Why card ~150 + Worth ~120 + Habits ~170 (gaps 14), set options 14+~60, filters
   18+~88 (10 dropdowns wrap to two rows), body gap 30, list head 44. First row at about 1000px, the question
   pane at about 1100px: nothing of the task is in the first screen. Due tab is better: pane top at ~500.
   Phone Redo: pbar 56, top 25, Now strip 60, header 152 (seg on its own row), new-misses card ~146, sticky
   tabs 72, tab-head cards, options ~210 (each option's label takes a full row, 230-231), filters 58, list
   head 44: first row past 1300px, while the fixed bar (~110) and tabs (64) cover 174 of 844 for good.

## A. Purpose and primary action

- Purpose: "what do I fix now". Primary: Start review (Due) or Fix N (Redo). Clear on Due, buried on Redo.
- Too many amber pills at once on Redo: header Start (review.js:190), Walk them (283), Worth the most go
  (1239, `.pill.sm`), exam Final check (1340), bar Fix N (1695). History adds a Rematch pill per sitting
  (1013) and Fluency sprint (1483). Up to five primaries in one view.
- With nothing selected the Redo/Fixed/History bar pill reads "Select all N" (1752, 1761, 1782): a primary
  pill that selects rows instead of starting anything.
- Sheet: primary Submit answers (sheet.js:142), fine. Walk: Resume the walk (walk.js:180), fine. Print: Print
  / Save as PDF, fine.

## B. Whitespace (concrete)

- `.rh-head .h1` 36px (index.html:25), phone 28 (228); scale says 22. Sheet/walk h1 800 36px (sheet:26,
  walk:24), print 800 32px (print:24).
- Gaps: notes 20 (36), tiles 18 (45), head box 18 + 14 between cards (57), opts 14 (216), filters 18 (98),
  body 30 (103), pane 16 (105), bar 18 (203). Six stacked 14-30 gaps before the list: about 120px of air.
- Tiles: 10x12 padding + stat-k + 20px value + sub that wraps to 2-3 lines at 165px wide: ~80px tall.
- Cards: `.rh-card` 18x20 padding (60), `.card-head` margin 12 (61); rows `min-height: 64` (137), tall 88 (139).
- `.rh { padding-bottom: 140px }` (22) and phone `200px + safe` (226) are reserved even on Due, where no bar renders.
- Sub-pages stack back link (44px tall) + h1 + sub + 20-24 margin before content (sheet:23-27, walk:22-25).

## C. Always-on content that is not essential

FOLD_SEL (ui.js:2792) catches only `.help` here, and only at 70+ chars: "Tag how sure you are..." (1258, an
empty state: give it `data-nofold`), "Your first answer..." (1284, under 70, never folds), the low-topic flag
tip (1291), "That's after your SAT..." (1545). Nothing else folds: `.rh-line`, `.rh-big`, `.rh-foot`, `.meta`,
`.empty-text`, the tab-head cards are not in FOLD_SEL. Walk: `#walk[aria-live]` is in FOLD_SKIP. Sheet: the
`.ws` guard in foldOne skips the whole page (see I3). Print: FOLD_OFF matches `/print`, correct for paper.

| Content | Where | Do |
|---|---|---|
| Why you lose points, Worth the most, Habits (3 cards) | review.js:1172-1244 | one closed "Insights" disclosure with a one-line summary |
| Your instincts matrix + readings | 1250-1299 | same disclosure on Marked |
| History summary, Right but slow, rushed line | 1440-1493 | summary line stays; Right but slow folds |
| Made and fixed chart + forecast + stat line | 1509-1551 | headline line stays; chart and forecast fold |
| Set options (Questions, Clock, Level, Feedback, Each) | 1661-1682, `#optsbox` | move into the bar behind an Options button; the bar's echo line (1688-1692) already states non-defaults |
| 10 Redo filters always open on desktop | 416-430 | Search, Status, Sort inline; rest behind "Filters · n" (the kit's phone sheet) |
| Minutes seg (8 options, ~390px) | 178-188 | into the Start split menu |
| Secondary actions row (Walk these, blind spots, Print worksheet, Ask for help, Share, Error log) | 1554-1587 | `.reveal` or a "More" menu in the bar |
| Tile sub-lines (half fixed, relapsed, pts at stake...) | 317-336 | `title`/aria only; the active tab's sub shows once as `.rh-tabsub` (exists, phone only, 246) |
| Empty-state paragraphs that explain the UI | 621-627, rules 1368 | one line + one action |

## D. Sidebars

- Left nav already says "N due · M open" on Review (ui.js:1494-1499). Nothing more belongs there.
- The pane is the task and cannot live in a 300px `.split-side`: it renders a Source Serif question with
  tools. Two shapes for the lead:
  (a) page-local grid: list column 360-380px (sticky, own scroll) + pane fills the rest (~640 at 1440). No
      shared change. (b) `.split` with a wide-aside variant holding the pane: shared ask.
- With the pane on the right, filters and set options do not fit a side column too: keep them inline but
  folded (C). Insights stay a disclosure above the list.
- Sheet at 1440: a 760 column in 1040, 280 unused. At 1280+ the count, Minutes taken and Submit could sit in a
  sticky right column instead of the sticky foot (sheet:42). Walk and print: no side column.

## E. Redundancy

- Shell: Up next can be "Review what's due" (server/next.py:211-213); at laptop heights the Now strip
  (ui.js:2204) then sits right above the page's own Start review. Two Starts for one thing.
- Exam date: `examCard` (review.js:1333-1354) restates the date the sidebar Now block will carry; keep its two
  actions, drop the date line. Streak and Today progress: not on this page.
- Counts: the Redo number is in the nav badge, the tile, the Status filter counts (421-422), the list head
  "N of N selected" (568) and the bar "N selected" (1758). List head and bar say the same selection: keep the bar.
- Points: tile sub (329), group head (770), row meta (821), Worth card (1234, 1239), cause bar. Keep group + row.
- The ▾ preview sheet (192, 230-268) repeats the Due tab's list (it differs: drop-for-this-set vs Not today).
  Keep, but as a menu item, not a second amber pill (P2).
- Pane footer Prev/Next and nav cells repeat the list's navigation; fine once list and pane sit side by side.

## F. Local overrides, colours, sizes, inline styles

- Undefined tokens: `--ink-soft` is defined nowhere, used in sheet:23,24,32,38,45,49; walk:22,25,28;
  print:22,25,28,48,50,54,64. Every "soft" line renders full ink (kills the label/meta hierarchy on paper).
  `--bg` is defined nowhere: `var(--bg, #fff)` (sheet:34,35,37,41,42) and `var(--bg)` (index:71). `--bar-h`
  undefined (index:238). Use `--soft`, `--paper`.
- Hardcoded colours: `#fff`, `#ccc`, `#e5e5e5`, `#ddd` fallbacks (sheet:34-47, print:31-70, walk:31);
  `rgba(0,0,0,.18)` split seam (index:34).
- 999px chips: `.rh-kind` (74), `.rh-row .tag` (170). Circle answer bubbles `border-radius: 50%` on 44px
  buttons (sheet:34): escapes check-ui.py (regex wants px and a .pill/.btn selector). Bubble-sheet fidelity
  may justify it: lead's call.
- A second button style: `.rh-split > .pill` 40px, 15px, own padding (31-34). Spot-the-trap choices are
  `.btn` with inline height/padding/alignment (review.js:2014).
- Status cells restyled locally: `.rh-pane .cell[data-status=open|half|relapsed|stuck|sure|unchecked|due|
  held|dismissed]` (index:150-154) with raw fills, outside the `--st-*` contract (ui.css:185-205 has none of
  these). Shared ask.
- Shared component overrides: `.rh-pane .rv-tools/.rv-tool` 11px nowrap (148-149); `.rh-tab .stat-v` 20px
  (50); `.rh-start .seg` 13px (28) and `.rh-opt .seg` 12.5px (212) do nothing (the seg button sets its own font).
- 14 font sizes in index.html (11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 17, 20, 28, 36) plus inline
  16/15/14 in JS (711, 1100, 1458). Map: 11/11.5 to micro, 12-13.5 to meta, 14-15.5 to body/item, 17 to section.
- Mono for words: `.rh-row .l2` (158), `.rh-wait`, `.rh-sit .kids` (192), `.rh-tries` (185), `.rh-foot` (96),
  `.rh-sum small` (207), `.rh-tabsub` (246), `.rh-matrix .rl small` (91), `.rh-startmeta` (35); most inherit
  the habit from shared `.meta` (ui.css:767).
- 27 inline `style:` attributes in review.js (254, 255, 642, 711, 766, 1097, 1100, 1183, 1200, 1205, 1276,
  1277, 1308, 1337, 1373, 1439, 1458, 1461, 1485, 1529, 1544, 1550, 1634, 2009, 2010, 2012, 2014) plus
  `.style.*` writes (259, 719, 1989, 2020). Nearly all are margins a card `gap` replaces.
- Dead CSS: `.rh-helper` (26), `.rh-startmeta` (35, 237; its DOM is built and never appended, review.js:
  195-205), `.rh-today/.ring/.rh-fc` (79-81, 221-222, 249), `.rh-kinds` (73), `.rh-wait` (82), `.rh-panenote` (109).

## G. AI-slop tells

- Uppercase letter-spaced mono kickers: `.rh-k` card titles (62), tile `.stat-k`, `.rh-opt > .k` (211),
  `.rh-matrix .h` (89); print `.pr-sec > h2` (28) and `.pr-ch .tag` (47). (`.pr-log th` (50) is a printed
  table head: allowed.)
- Card soup: three to four stacked kicker cards per tab head, each a filled `--tile` box.
- Glyph decoration in labels: "Half fixed ●○", "Check-in ✓", "Sure ✕" (692), "Then → Now" (1013, 1022),
  "▲" over budget (974), "▸/▾ n tries" text toggles (985-987).
- Middle-dot chains as labels: every button and meta joins 3-5 clauses with " · ".
- Praise: "Fixing them faster than you make them." (1527). U+2014 placeholders at review.js:27 and 362.

## H. Copy

| Line | Now | Proposed |
|---|---|---|
| 283 | Walk them · name each, then prove it | Walk N misses (explanation to `title`) |
| 1013 | Rematch · same N types, new numbers · Then → Now | Rematch |
| 1017 | Walk these misses · name each, then prove it · ~N min | Walk misses |
| 1022 | Fix N · Then → Now | Fix N |
| 1029 | Blanks · N · fresh twins | Redo N blanks |
| 1340 | Final check · one fresh question per trap · N · about M min | Final check · N |
| 1172 | Why you lose points · last 30 days | Why you lose points (data is every open mistake, not 30 days: api_review.py:406+, review.js:1175-1178) |
| 770-771 | about 1.2 of 44 a test | drop or "1 a test" |
| 820 | dodged in N other types | avoided in N other types |
| 1774, 1779 | Twin this set · all N | Practise N new versions |
| 1037 | Again, exactly (tests memory) | Same questions again |
| 622 | Nothing open. Every wrong answer lands here, named by the mistake behind it. | Nothing open. + Keep going |
| walk:44 | Try it again, name the mistake, see the trap, then prove it on new numbers. | counts only (already replaced on load, walk.js:211) |
| walk.js:179 | Step 2 of 4 · you can come back to it any time | Step 2 of 4 |
| sheet.js:177 | Filed like online answers: misses are named in Review, clean rights fill their pips. | Misses are in Review. |

## I. CSS / layout bugs

1. Dark mode on the sheet: `var(--bg, #fff)` gives white A-E bubbles, grid-in and minutes inputs and a white
   sticky foot with light `--ink` text (sheet:34-42). Letters unreadable. High.
2. `--ink-soft` undefined in sheet/walk/print (F). Medium.
3. `.ws` collision: the sheet's `<main class="page ws">` (sheet:67) reuses the question workspace root class
   (question.js:567, runner.css:34+). Its `.ws { max-width: 760px; padding-bottom: 120px }` (sheet:22) also
   hits every UI.workspace in the key (sheet.js:234): 120px under each question. `.ws-skill` (sheet:32)
   collides with question.js:613-617. Medium.
4. List ribbon hides tags and meta at every width (index:167); comment says "the title and the date only" but
   the date is in the hidden `.l2`. High (information invisible).
5. Sitting cards, day heads and group heads as flex items in the ribbon; nested scroller (1051). Medium.
6. Phone sticky tiles `top: var(--bar-h, 56px)` (238) ignore `env(safe-area-inset-top)`: under the pbar in
   the installed app on notched phones. Medium.
7. Double edge: `.rh-pane` inset line (105-106) plus `.rv-pane:not(.rv-dlg-in)` border (runner.css:850). Low.
8. Sheet foot `bottom: calc(62px + safe)` (sheet:55) vs tabs `64px + safe`: 2px under the tab bar. Low.
9. Set options (`#optsbox`, above the filters) and their primary (the bar, at the bottom) are a whole list
   apart on desktop. Low (layout logic).

## Redesign proposals (ranked)

1. **BIG. Vertical list beside the pane.** index.html:102-116, 165-168; review.js 249. At 1280+: grid
   `minmax(320px, 380px) 1fr`, list column sticky with its own scroll, pane fills the rest. 960-1279
   (`wide()` keeps the pane there): vertical list with a capped height, pane beneath. Below 960 a plain
   vertical list, tap opens the player as today. Rows 44px: lead, title, tags right; `.l2` meta, `.l3`
   note/why (715, 823, 884) and `.ract` buttons (Learn this type 825, Note/Unsave 886-890, Prove it/Reopen
   1105-1112, n tries 985) in `.reveal` (always shown on coarse pointers); Due's `×` Not today (718) stays
   the trailing control. Group, day and sitting heads become row headers. Keep `#list`, `.rh-pane`
   (runner.css:1195), `.rh-row`, `[data-i]`, ArrowUp/Down, `X`. Risk: medium; undoes a deliberate strip (102)
   and narrows the pane to ~640 at 1440 (check R&W passages). Needs `.reveal` (shared). Tell the user.
2. **Header in one 42px row.** h1 22px left, Start split right. Minutes seg (178-188) and "See the list
   first" (192) move into the ▾ as a menu (minutes as radio items). Saves ~60px desktop, ~100 phone.
   Keep `#start`, Shift+R, `aria-keyshortcuts`. Risk: low-medium (one more tap to change minutes; it is a
   remembered pref).
3. **BIG. Tiles to a 40px tab row.** Six tiles (45-55, 317-372) become underline tabs with the count inline
   ("Redo 23"), at every width (the phone style at 238-245 already is this). Sub-lines go to `title`/aria and
   the active tab's sub shows once in `.rh-tabsub`. Keep `#rhtabs`, roles, arrow keys. Saves ~40px. Risk: low.
4. **Insights fold.** Tab-head cards (`part()`, 1126-1140, and 1227, 1440, 1509) render inside one closed
   `<details>` per tab with a one-line summary ("Why you lose points · Trap 12, Slip 4"), open state
   remembered (page-local key, or the shared `satf.fold`). Saves 300-450px on Redo. Risk: low; nothing removed.
5. **Options into the bar.** `#optsbox` (1661-1682) moves behind an Options `.quiet` in `.rh-bar` (popover
   on desktop, sheet on phone); echo line stays. Saves 60-210px. Risk: low.
6. **Filters folded on desktop too.** Page CSS applies the kit's phone rule (ui.css:1098-1101) at all
   widths inside `.rh-filters`, with Search, Status and Sort marked keep. Risk: low; needs filterBar to mark
   which keep (`filters-keep` on chosen defs) or a shared ask.
7. **One primary per view.** Demote to `.btn`: 283, 1013, 1239, 1340, 1483. With no selection the bar pill
   becomes a `.btn` "Select all N" (1752, 1761, 1782). Risk: low.
8. **Copy pass** (table H) and drop glyph decoration in KIND/labels (692, 974, 985). Risk: low.
9. **Sheet/walk/print token fix.** `--ink-soft` to `--soft`, `var(--bg, #fff)` to `var(--paper)`, drop hex
   fallbacks; rename the sheet's page-local `ws`, `ws-skill` to a non-colliding prefix (only sheet uses them;
   grep first). Risk: low. Fixes I1-I3.
10. **Type scale.** h1s to `.h1` 22/600 (25, 228, sheet:26, walk:24, print:24); `.rh-k` to section 16/600
    sentence case; `.rh-opt > .k`, `.rh-matrix .h` to `.k` once shared `.k` is sentence case; l1 15 to 14.5;
    l2 to Geist meta. Risk: low.
11. **Phone.** Reserve bottom padding only with a bar (`.rh:has(#actbar:not(:empty))`, 22, 226); sticky tabs
    `top: calc(56px + env(safe-area-inset-top, 0px))` (238); bar summary one line. Risk: low.
12. **Up next suppression.** Hide the Now strip when its first item key starts `review:` on this page.
    Page-local via `UI.nextItems` + a body class, or (better) a shared rule. Risk: low.
13. **Cleanup.** Dead CSS (F), 27 inline styles to classes with gaps, chips to 8px corners, the 40px split
    pill back to `.pill` 42px. Risk: low.
14. Sub-page heads: back link inline with the h1 as a `.quiet` (sheet:68, walk:42, print:78); sheet at
    1280+ puts count + Minutes + Submit in a sticky side column. Risk: low.

## Shared asks (lead only)

- `--st-*` tokens for mistake statuses: open, half, relapsed, stuck, sure, unchecked, due, held, dismissed
  (replaces index.html:150-154).
- `.k`, `.stat-k`, `.meta` off mono and uppercase (fixes most of G here at once).
- `.split` wide-aside variant if the lead picks shape (b) in D.
- `.reveal` (DIRECTION 5, not built yet): P1 depends on it for row meta and row actions.
- Now strip: skip when Up next points at the current page (`review:*` on /review/).
- FOLD_SEL: no new class needed if P4 uses page-local `<details>`; else a `.fold-card` class.
- filterBar: an option to keep the collapsed "Filters · n" sheet at all widths with chosen `keep` keys.
- Contract to keep: `#start`, `#rhtabs`/`.rh-tabs`, `#list` (tour.js:50-53), `.rh-pane` (runner.css:1195-1198).
