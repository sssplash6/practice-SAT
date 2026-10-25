# Pass: Practice builder, quick sheet, palette

Files: `web/practice/index.html` (style block and markup rewritten), `web/practice/builder.js`, `web/assets/quick.js`,
`web/assets/palette.js`. Audit: `audit/practice.md`.

## First screen

**Practice, 1440x900.** Leads with the skill tree. Main column (728px): one header row (Practice, the subject switch,
the points line on the right), the search box, the Presets fold (one line, says which preset is on), the tree head,
then the domains as two always-open columns; the whole tree ends around 760px, so every skill is on the first screen.
The sticky right column holds "Your set": the count and time, the picked skills and settings in one line, and
Start practice, the page's one orange button. Under it: the set in progress (when there is one), Ready to start rows,
and the Mistakes / Saved / Your sets links. Moved out of the way: the 72px fixed bottom bar (now the aside card),
the four Ready cards with orange Starts (now quiet rows in the aside, Up next's first item left to the sidebar), the
17px search label (screen readers only), Your sets (its own fold under the tree, not inside Presets).

**Practice, 390x844.** Header (title and subject on one row, points under), then the set in progress, Ready rows and
the list links, then the search, Presets, the tree head and the 2x2 domain tiles, which now start around 600px instead
of about 890px. The bottom bar is one row (the count and Start; the reason line only when Start is disabled), about
55px shorter, and the page keeps exactly the bar's height plus the tabs and the safe area free at the bottom.

**Quick sheet and palette.** Unchanged in what they lead with. The quick sheet's Log a mistake form folds "Where was it?"
behind "Add where (optional)"; the palette's empty list is now about 25 rows instead of about 60.

## Big changes

1. From 1280px wide the Start bar is a card at the top of a sticky right column, with the set in progress, Ready rows
   and the list links under it. Below 1280 the bar is the fixed bottom bar, as before.
2. The skill tree lays itself out by its own width: two open columns in the main column, four when it has 1000px,
   tiles when narrower than 560px. At 1440 the whole tree is on the first screen.
3. Your sets left the Presets fold: it is its own folded section under the tree, remembered; the Your sets link opens it.
4. One Start: only Start practice is orange. Ready rows and Resume use quiet or secondary buttons, and Up next's
   first item is no longer repeated in Ready (the sidebar or the Now strip shows it; Enter on the empty search still
   starts it).
5. A set in progress shows once on the page (the resume card); the Your sets link no longer repeats "n in progress".
6. Finished sets show Review; Rematch, Retake exact, Same settings, Share and Print are in a More menu on the row.
7. Presets are the shared chips. Save as preset, Copy link and "My defaults" (was Reset) are in one Options menu, which
   also renames and deletes your own presets.
8. The skill window opens on Check my level and the question types; the record and the skill's facts are one folded
   "Your record" list (remembered). The "In {domain}" block went: those facts are the domain header's tooltip and the
   domain window's line.
9. Type rows' Try one / Learn / More show on hover or focus with a mouse, always on touch.
10. Quick sheet: no inline styles left (a `qk-` class block in quick.js); type and "Not sure" rows are hairline rows,
    not boxes; "Where was it?" folds.
11. Palette, empty query: five skills then "All 19 skills", six actions then "More actions".

## Bugs fixed

- I1 checkbox hit areas overlapped in 38px rows: rows are 40px, hit area 40px tall and only 4 to 6px towards the name.
- I2 phone: the last rows sat under the bar on home-indicator phones. Bottom space is now the measured bar height
  (ResizeObserver, `--abar-h`) plus the tabs plus `env(safe-area-inset-bottom)`.
- I3 R&W hid the bar but kept 120/190px of bottom padding: the measured height is 0 then.
- I4 Your sets' 7-column row broke from 760 to 1039px: it collapses by its own width (container query, 700px).
- I5 viewport breakpoints against a 68/248px sidebar: the tree uses its own width (container query plus a
  ResizeObserver for the tiles/columns switch in JS).
- I6 a dimmed row's reason was only a `title` in the wide tree: on touch screens it shows under the name.
- I7 Ready titles were focusable but not keyboard operable: no more clamp or tap-to-expand; titles wrap in full.
- I8 the parsed search chips looked clickable: they are `.badge.soft`.
- I9 the search glow repainted forever: it pauses off screen (IntersectionObserver) and while typing.
- I10 the map's cell row used the quick sheet's `.quick` class: now `.mcells`.
- Found here: Ready's Start posted the Up next item's `{path, body}` wrapper to `/drill` (and `undefined` for link
  items). Ready rows now start through `UI.start` like the shell.
- Found here: Your sets' filters used the shared `.filters` class, which hides its children under 760px, so they
  vanished on phones. Now `.pr-filt`.
- Found here: the quick sheet re-showed an empty note field while still sending the earlier note; the field now keeps it.
- Em dash null placeholders (seven) are the en dash; the trophy emoji is a "Challenge" badge; the `⋯` and `▾` glyph
  buttons are words ("More", "Try one").

## Not done

- Proposal 5, the search as a plain field in the tree head: the animated box is the user's recorded call. Kept; made
  48px (was 56, the shared field height), its label screen-reader only, its icon a token-coloured mask (no hex).
- The `.tri` tree checkbox stays a page element (kept per the audit); its look is close to `UI.triCheck`, not identical.
- The Start window's "Saved as your defaults" status line stays (it says where changes go).
- Preset voice: only "Your top habit" became "Top habit"; the rest already read as the student's own ("My mistakes",
  "Check my level").
- Tree head Select all / Clear stay visible (not `.reveal`): they are the tree's main bulk actions.
- `.k`, `.meta`, `.badge`, `.palette-group`, `.palette-foot` look: shared, the lead's.

## Shared asks

- `.quiet` on coarse pointers: a 44px hit area (like `.btn.sm::before`). Practice keeps three phone `min-height: 44px`
  rules on `.quiet` until then (`.trow .tacts .quiet`, `.pset .sfoot`, `.pset .sheet-foot`).
- `.twocol-side` (ui.css 322): `overflow-y: auto` clips focus rings of full-width controls at its edges; suggest
  `padding: 4px; margin: -4px` on it.
- A body class for "the sidebar shows the Now block" (today `(min-width: 1100px) and (min-height: 700px)` with
  `body.has-side:not(.no-now)`); practice copies that query for `.pr-row[data-upnext]`.
- Export `nextMeta` (ui.js 1622) as `UI.nextMeta`; builder.js repeats its formatting for Ready rows.
- The Now strip's Start is a `.pill`: below 1100px it is a second orange button above the page's Start. Consider
  `.btn.sm` there on pages without `now: false`.
- `.palette [role="option"][aria-selected="true"]` (ui.css 2254): drop the amber inset stripe, keep the wash.
- Optional: move quick.js's `qk-` block and palette.js's `.pal-meta` / `.pal-status` into ui.css.

## For the user

- Keep the animated orange search box, or replace it with a plain field in the tree head (saves about 60px more)?
- Ready rows: titles now wrap in full instead of clamping with tap-to-expand. OK?
- Resume (set in progress) is now a grey button; only Start practice is orange. OK, or should Resume lead when a set is
  in progress?
- Your sets starts closed (as it effectively was inside Presets), and remembers. Open by default instead?

## Polish round

Files: `web/practice/index.html`, `web/practice/builder.js`. `web/assets/quick.js` and `palette.js` unchanged (see Not done).

### First screen

**Practice, 1440x900.** Main column: header row, the animated search box (kept), then the presets as one chip row (was
a closed "Presets" fold), the tree head and the domain columns. The presets row is the same height the closed fold
was, so the tree starts where it did, and the preset that is on shows as its pressed chip instead of a line in a fold
summary. The aside is one column: the Start card (the only box and the only orange button), then plain sections split
by hairlines: the set in progress (was a second box), Ready to start, and the lists. Mistakes, Saved and Your sets
are now quiet 36px rows with the count right-aligned at 12.5 `--soft`, like the sidebar's nav (was a wrapped line with
"· 4" after each word). In the tree, each skill row's open-mistakes badge now sits before the mastery bar, so every
bar ends on one right edge; the domain head's "+9 pts" and "n of m selected" are 11.5/500 `--soft` (were 12.5/400).
Rows stay 40 with hairlines (44 in the phone's domain window).

**Practice, 390x844.** The presets chip row takes the full width and scrolls sideways with soft edges; All presets
and Options sit under it. The aside content keeps its boxes and the lists keep their inline line here (the aside
leads main below 1280, and rows stretched across the phone looked empty). The Start window's tabs scroll sideways
with soft edges.

**Start window (all widths).** "Questions from" and "Answers shown" are `.choice-row` rows (the label left, the count
right, wash-2 and the amber inset when chosen) instead of radio circles on hairlines. The two Pace switches' `?` is
`UI.why`. "Practice more to unlock." (For me) now has a `UI.why` beside it with the skills still to place; it was a
`title` only, which touch screens never showed.

### New components added

- `UI.edgeFade(chips, true)` on the presets row (new: the row scrolls instead of wrapping); a repaint keeps the row's
  scroll position and brings the pressed chip into view; All presets scrolls to the first chip it adds.
- `UI.edgeFade(tablist, true)` on the Start window's tabs (they scroll sideways under 760px).
- `.choice-row` for the pool and feedback rows (replaces `.radio-row`). The radios are still real radios inside the
  labels (arrow keys, form semantics); an empty pool's row gets `aria-disabled` as well as its disabled radio.
- `UI.why` for the Pace switches (replaces the local `.ibtn` + `UI.pop(.info-pop)`) and for For me's unlock line.
- `UI.nextMeta` for Ready rows' meta line (replaces builder.js's copy of its formatting).
- `UI.NONE` for the missing-value glyph (replaces the local `'–'`).
- The palette keeps the lead's `UI.edgeFade(list)`.

### Removed local copies

- CSS: `.radio-row` (and its `input`, `.rl`, `.rn`, `.off` rules), `.pr-swrow .ibtn`, `.info-pop p`,
  `.pr-fold > summary .meta`, `.pr-chips > .chips { display: contents }`, and the three phone `min-height: 44px` rules on
  `.quiet` (`.trow .tacts .quiet`, `.pset .sfoot`, `.pset .sheet-foot`) now that `.quiet` has the 44px hit area on touch.
- Markup: the `#presetFold` details with `#presetTog`, `#presetNow`, `#presetBody` (no other file uses them; tour.js
  targets `#presetSec`, which stays).
- JS: the Presets fold's remembered state (`satf.pr.presets` is still read once as Your sets' first-time default),
  the fold summary's "· Mentor's pick" text, the local Ready meta formatter.

### Not done

- Tree counts as 11.5 `--soft` numbers: the open-mistakes count stays the orange `.badge.n` (it flags open mistakes, and
  the brief keeps orange marks; DIRECTION keeps `.badge.n` orange). The other counts in the tree went to 11.5.
- Row and card titles stay 600 (DIRECTION section 9, INSPO-VISUAL 6.1 not taken).
- builder.js's own tap tip (`tapTip`) stays: it shows a tip after a tap on a control that also acts (a chip, a seg
  option, a Ready row); the shared tap fallback only covers triggers with no action, and defers to it.
- quick.js: its tab row (`.qk-seg`) wraps rather than scrolls, so an edge fade would never show; nothing else in the
  sheet is a row toggle or a `?`. palette.js: its look is the lead's; the markup needed nothing.
- The shared set banner keeps its `.pill.sm` "Start this set" (a second orange in the aside while a shared link is
  open): it is that visit's task.
- The search box stays the animated one (the user's call).

### Shared asks

- tour.js step `#presetSec` says "Open this to pick one, or save your own": presets are a visible row now. Suggest
  "Ready-made starting points: pick one, or save your own under Options."
- `.choice-row` hover (ui.css ~373) excludes `[aria-pressed|checked|current]` but not `label.choice-row:has(input:checked)`,
  so a chosen label row turns grey on hover (the amber inset stays). Add `:not(:has(input:checked))`. It also skips
  `:disabled` but not `[aria-disabled="true"]`, so an empty pool row still darkens on hover.
- Still open from round one: a body class for "the sidebar shows the Now block" (practice copies the media query for
  `.pr-row[data-upnext]`).

### For the user

- Presets are always shown now, as one sideways-scrolling row of chips (was a fold you had to open). Same height as the
  closed fold. OK, or back behind a fold?
- The Start window's "Questions from" and "Answers shown" are row buttons now (orange edge on the chosen one), not
  radio circles.
- Checks: `check-ui.py` ok; `node --check` ok on builder.js, quick.js, palette.js and the inline script; no em dashes
  in the four files. The official smoke run (`page.js`, 1440 and 390) stops at `bank.domains` before and after these
  edits (its fixtures have no `/bank`); a private copy with a bank fixture (/private/tmp/claude-501/-Users-workingmyassof-freshbot-satbank/11932fea-c5c4-475d-bd5f-041033f1446a/scratchpad/practice-pass/) renders the
  tree, presets, aside, domain window and the Start window's tabs with no errors at both widths.

## Premium build (part 1)

Files: `web/practice/index.html`, `web/practice/builder.js`, `web/assets/quick.js`, `web/assets/palette.js`. Brief:
premium/PAGE-BUILD-BRIEF.md part 1 (calm first screen, hero, open bugs, Per page and More items with no new shared JS).

### First screen

**1440x900, the audited case (new student, Math, Mentor's pick, no answers).** Before: 4 bands of controls above the first
skill (header; search; presets row of 4-6 chips plus All presets, Options, Diagnostic; tree head with a 3-way seg, Select
all, Clear and an 8-way sort), about 65 targets, 23 checkboxes, 23 empty grey bars, 6 boxes (search, 4 domain cards, the
Start card), about 12 orange marks. After: 3 bands (header with the subject switch at the right and the points line under
the title; the search alone; one tree-head line: master box, "Skills", "3 of 19 selected", Clear while something is
picked, one View trigger). About 14 controls outside the rows (subject 2, search, master box, View, the preset trigger,
Start, the Diagnostic line, the Ready fold and its 1-2 Starts, the 3 lists) plus the 23 rows (4 domain heads, 19 skills),
0 empty bars (a bar only once a skill or domain has answers), 2 surfaces (the search and the hero), orange only on the
search's edge, Start, the picked boxes and the open-mistake badges. Domains are plain titled lists: two columns reading
down in test order (four from a 1000px tree), one hairline under each head, 28px between domains, no rules between rows,
a hover band and a warm band on picked rows. Space: header to body 24, search to tree 32, main groups 32, aside sections
24 with no rules.

**390x844.** Before: no skill on the first screen (tiles from about y 760, 600 with no Ready rows), two orange Starts.
After: the aside dissolves below 1280 (`display: contents`): the set in progress (when there is one) leads, then the
header, the search, the tree head on one line and the 2x2 tiles from about y 330; Ready rows and the lists follow the
tree. The fixed bar is the preset as a quiet line over "10 questions · ~14 min", with Start at the right. Tiles are white
with a soft edge, no border or shadow. The shell's Now strip Start is still a second orange (shared ask).

### Hero

`#abar` is `.card.hero` from 1280px (the only raised thing on the page): "Your set" with the preset trigger at its head,
the set as a figure ("10" at 28/600 in `--ink-strong`, "questions · ~14 min" on its baseline), up to 3 topic glyph chips
then "+2", the line under it (types, difficulty, format, "works on ≈ +n"), Start practice full width, the reason under it
when disabled, and the Diagnostic foot line for a new student. Below 1280 the same element is the docked bar; the page
overrides the card's look there by id (the page tone, a warm upward shadow, no radius or padding). ui.css (A1) now gives
the aside 8px of room, so the hero's shadow and focus rings are not clipped; the sticky column's top is 8px locally.

### What moved behind which control

- Presets row (chips, All presets, Options) -> one preset menu (`#presets`, a `.btn.sm.dd` in `#presetSec`, tour.js still
  finds it): groups Suggested, From your history, Yours; a preset that can't run yet is listed dimmed with its reason as
  the item's second line (was a tooltip); Plan focus with no focus links to Plan; Save as preset, Copy link, My defaults,
  Rename and Delete at its foot. The trigger reads the preset that is on ("Custom" after an edit).
- Diagnostic (presets row) -> a quiet foot line of Your set, only with no answers and when Up next does not already offer
  it; it waits for Up next to answer, so it never flashes.
- Skills / Map / Habits switch and the sort select (`#sort`) -> one View menu (`#view`): Show (Habits listed with "After
  about 30 answers" until it has rows, so its empty state stays reachable) and Order skills (picking one shows Skills).
  The trigger reads the order, or Map or Habits.
- Select all and Clear -> the master box (`#treeAll`, all / some / none) and Clear (`#treeClear`) while something is picked.
- Your sets, Finished: the three filters show once something is finished.
- Quick sheet: "Got time?" time boxes -> under the verdict's actions (hidden until each answer).

### Motion and feedback

- BUILD rule 13: the search's orange edge sweeps once round on load (1.6s, after 0.2s) and then rests lit (55% amber, 75%
  on hover, full on focus with the shared halo). Registered `--sa`, `--arc`, `--arc-hi`; the base values are the lit ring,
  so reduced motion shows it without the sweep. The IntersectionObserver and `.still` are gone (nothing loops).
- Small: picked and hover bands fade in 160ms, the box edge 120ms. Everything else (preset cascade, figure swap, menus,
  drawn check) is part 2.

### Icons

None moved yet (part 2). The local `icon()` no longer falls back to the orange dot.

### Bugs fixed

- SUGGESTIONS bug 3 (builder.js): an unknown icon name drew the orange dot; it now draws nothing.
- Map view: a cell click left the tree head's count stale; the head's box and count repaint after every view.
- "Check 1 skills I haven't tried" -> "Check 1 skill I haven't tried".
- Bug 4 for Practice's own chips: the hero's glyph chips set `--gb` to the chip's well, so no pale box.
- Calm empties: Habits and Your sets' Finished and Shared by me show one dimmed sample row under their line on first use
  (`.pr-sample`, inert, aria-hidden). The palette and the tree draw no mastery bar for a skill with no answers.
- Start no longer reads "Loading…": disabled "Start practice" until the first preview, a skeleton line for the set.
- Quick sheet: the skill showed twice (the row's chip and the workspace's head). With the workspace the row keeps only what
  its head lacks; without it (ui.js's renderer drops its line) the row is unchanged. An empty chip row collapses
  (`:empty`), so the live tally stays in the tree.
- A server error left the set's skeleton line in the hero; it is cleared and the reason says why.

### A1 follow-ups (the lead's note after ui.css landed)

- Page-level `var(--tile)` boxes: none left in the page. The domain tiles (narrow) are white `--raised` with the soft
  `--edge`, no shadow; the domain lists (wide) have no box at all; the set-in-progress and shared-set boxes are `.card`
  (plain inside the 1280+ column). The quick sheet's example and chosen-type boxes stay `--tile` wells inside the sheet.
- Side stripes and ink focus rings: none in the four files.
- Gaps: the 2x2 tiles and the shared-results tiles use 12px (one group), not the new `--card-gap` 32.
- The docked bar (below 1280) paints `--page`, a sticky bar's tone; the skill window's sticky types head paints its
  sheet's `--surface`, not `--paper` (dark mode matched the wrong layer).
- Search hits in the tree and the skill window are 600 and underlined amber, the palette's look (was a wash band).

### Inventory diff (smoke/inventory.js with a /bank fixture, 1440 and 390, before and after)

The official `smoke/page.js` and `inventory.js` still stop at `bank.domains` (no `/bank` fixture), before and after, the
same error; the real comparison used copies with a bank fixture in
/private/tmp/claude-501/-Users-workingmyassof-freshbot-satbank/11932fea-c5c4-475d-bd5f-041033f1446a/scratchpad/prem-practice/
(page.js, inventory.js, fixtures.js, run.js, run-new.js, run-quick.js, run-pal.js), all NO ERRORS at 1440 and 390, a new
student, the quick sheet's question tab and the palette's empty list included.
- Gone: All presets, Options and the 11 visible preset chips (Mentor's pick, Weakest 3, Full section mix, Biggest gains,
  Solve first, Check 1 skill, My mistakes, Missed, Marked, Saved, Due for review): all in the preset menu ("Preset:
  Mentor's pick"). Skills, Map, Habits and `#sort` / Sort: the View menu ("View and order: ..."). Select all: the master
  box ("Select every skill"). "Loading…": "Start practice" (disabled).
- New: ids `treeAll`, `treeClear`, `view`, `glyphs`, `diag`; href `/diagnostic/` (the foot line, hidden unless new).
- Every other link, button, id and field is unchanged.

### Not done (part 1)

- The points line stays a meta link under the title (it carries the score range and links to Results); the hero's
  "works on ≈ +n" is only the picked skills' share, so merging would lose figures.
- The `.tri` rest edge is 58% ink (about 3.2:1 on white), not `--faint` as the audit and demo show (2:1, under WCAG 1.4.11).
- Habits is listed, not disabled, in the View menu (zero loss: its empty state stays reachable).
- Quick sheet: not `head: false` as AUDIT §12 says; that drops the type, difficulty and Grid-in mark. The poorer copy went.
- Part 2: the search icon on `UI.ICON.search`, list icons, `∞` as a drawn mark, the drawn check, menu and figure motion,
  the details chevron on hover, the palette's matched-letter underline, the pill's busy and done states.

### Shared asks

- tour.js:30 text: "Ready-made sets. Open this to pick one, or save your own." (Options is gone.)
- The Now strip's Start is a `.pill` below 1100 (bug 10): a second orange on Practice's phone screen.
- Still open: a body class for "the sidebar shows the Now block".

### For the user

- Presets are one menu at the head of Your set now (was a row of chips); every preset is listed, and one that can't run
  yet says why. OK?
- The search's orange edge sweeps round once when the page opens and then stays softly lit; it no longer loops.
- Checks: `check-ui.py` ok; `node --check` ok on builder.js, quick.js, palette.js and the inline script; no em dashes.

## Premium build (part 2)

Files: `web/practice/index.html`, `web/practice/builder.js`, `web/assets/quick.js`, `web/assets/palette.js`. On the merged
phase A (BUILD.md "## Integration") and the critic's list (DEMO.md "## Visual review").

### Shared controls adopted (step 3)

- `UI.shell({ page: 'practice', ownPrimary: true })`: the Now strip's and the sidebar's Up next Start are `.btn`, so
  Start practice is the page's one orange button at every width (bug 10 for Practice; the smoke finds one `.pill`).
- The tree's tick box (`.tri`, a role=checkbox button) wears ui.css's drawn checkbox: 18px, 5px corners, the 3.6:1
  `--off-fg` edge (part 1's 58% ink stand-in is gone), amber with the `--check-ink` check growing in, an ink bar for some.
- Hover bands are `--hover`; a picked row stays the `--wash` band (E1, which the critic passed); the phone domain window's
  list lost its box and its rules (bands, no hairlines between banded rows).
- Open-mistake counts are neutral (`.badge.n.soft`), per the critic (E1: orange counts competed with the checks and
  Start); the Mistakes list row lost its amber dot (its count says it).
- The lists are icon rows (`.pr-li`: icon soft to ink, `--hover` band, focus ring inset, count neutral at the end).
- A set's More and a type's More are `.ibtn` quiet icon menus (`more`), ghost until hover; names unchanged.
- Start practice and the shared set's Start keep their label while they build: the pill's own spinner after 300ms at
  the same width (a quiet button still says "Building…", and gets its arrow back on an error).
- Save as preset turns the new preset on: the trigger reads its name (feedback in place, no toast); deleting the preset
  that is on falls back to Custom, and later ones keep their place.
- The hero's chips: two and "+3" on one line (the critic, B4 and E1), glyphs at their 20px floor, the full name as a title.

### Motion (step 4)

- Page entry: `data-m="stagger"` on the main column (search, skills, Your sets) and on the aside, `data-m-now` on Your set,
  so the hero never waits; kit plays it once per visit.
- The preset cascade: a pointer pick of a preset, a domain box or the master box fills the newly picked rows in tree
  order, 20ms apart, capped at 240ms (`.pr-pre` holds each row's unpicked look until its turn); keys and reduced motion
  fill at once. Checked in a wide-tree jsdom run: after a pointer pick of Full section mix, 4 rows held `.pr-pre` and
  all were released by 300ms.
- The hero's figure rolls on a change of number (`UI.roll`: only the digits that changed, up on a rise); a word swaps;
  never on the first paint. The Start window's footer copies the set's text (`B.l1Text`), never the rolling copy.
- Ready and Your sets glide (`UI.glide`, rows keyed): Up next changing, a Your sets tab, a filter, Show more, Stop
  sharing and a new share move rows instead of swapping them. The first paint just shows. Both lists are `position: relative` in
  the page CSS, so kit never has to set it (a fast second change cannot restore a stale value).
- Folds open and close in height: Ready, Your sets and the skill window's Your record are `details.fold`.
- The skills fade in over their skeleton (load and a subject switch). Menus grow from their trigger (kit, by itself).
- Quick sheet: the verdict's actions, then the time boxes, step in 4px under the verdict.

### Icons and drawings (step 5)

- `icon()` in builder.js is `UI.icon` (no dot fallback, nothing for an unknown name); quick.js and palette.js the same.
- The search's local data-URI mask is the shared magnifying glass (`.pr-sicon`, soft, amber-deep while focused).
- The row's details chevron is `caret_right` and shows on the row's hover or focus in the wide tree (always on touch).
- Lists: `review` (Mistakes, the page it opens), `bookmark` (Saved), `history` (Your sets). Ready's Start is `.quiet.go`
  with the `arrow` that nudges on hover.
- The `∞` stand-ins went: the Length seg's option reads "Endless", and an endless set in progress reads "3 answered".
- Habits' first use: `UI.spotArt('start')` over its line (kit's `UI.empty`); part 1's dimmed habit row went (a drawing,
  a line and a ghost row was one thing too many). Your sets' first-use empties are kit's `UI.empty` with the sample row
  and its "Example" badge (part 1's local `.pr-sample` went).
- Palette: the letters typed are wrapped in `<b>` on each row's label, which ui.css underlines in amber (A1 styled it;
  the markup was missing).
- No filled twins on Practice: none of its controls is an on/off toggle with an icon (the quick sheet's Save, an
  `aria-pressed` bookmark, gets the twin from ui.css as it is).

### Bugs fixed

- Finished filters that left nothing said "Sets you finish show up here": now "No finished set matches these filters."
  with Clear filters (no drawing, no sample).
- The dimmed sample on first-use Your sets tabs was a local copy of kit's empty state; it is kit's now.

### Checks

`check-ui.py` ok; `node --check` ok on builder.js, quick.js, palette.js and the inline script; no em dashes. Smoke with
the official harness (`FIX=practice` page.js) at 1440 and 390: NO ERRORS, identical to the run before part 2. Inventory
(`FIX=practice` inventory.js) at 1440 and 390: no link, button, id or field gone or added against part 1. The bank-fixture
copies in /private/tmp/claude-501/-Users-workingmyassof-freshbot-satbank/11932fea-c5c4-475d-bd5f-041033f1446a/scratchpad/prem-practice/
(menus, master box, View, Habits, a new student, the quick sheet's question tab, the palette's empty list): NO ERRORS;
one `.pill` on screen (Start practice), the icons, the stagger hooks and the keyed rows are where they should be.

### Not done

- `{ mark: 'clip' }` on the subject seg and the Start window's tabs: opt-in, and a second orange copy on a calm page.
- The glyph chips' entry and the preset label's crossfade (the audit's blur swap): blur is reserved (rule 5) and the
  chips change on every pick; the roll on the figure carries the change.
- First pick halo on Start (audit 7.3): no halos (rule 4).

### Shared asks

- tour.js:30 text still says "from Options" (from part 1).
- A shared dropdown chevron (`caret_down` on `.dd`) is on the lead's checklist; Practice's two `.dd` triggers use the
  ui.css one meanwhile.

### For the user

- On a phone the Now strip's Start is quiet now; the bottom bar's Start practice is the one orange button.
- Picking a preset lights its skills one after another down the tree; the hero's number rolls when the length changes.

## Visual review

Phase C, two rounds in Chromium at 1440 (light, dark), 390 (light, dark), as the learner with the most answers
(`a:v2revresults01`) and a fresh one. Shots: `spec/redesign-2026-10-19/premium/shots/app-review/practice-r0-*` (before),
`practice-r1-*`, `practice-r2-*` (after). Files: `web/practice/index.html`, `web/practice/builder.js`, `web/assets/quick.js`,
`web/assets/palette.js`.

### Per screen

- **First screen, 1440 (the "clustered" one).** Before: tree names wrapped to two and three lines in a 202px cell (8
  ragged rows), domain heads wrapped and "+5 pts8" collided, five amber "some picked" boxes, hero chips cut to
  "Linear Equatio…" (a fresh learner saw "Linear Equ…" twice), Mistakes and Your sets drew the same clock icon. After:
  every row and domain head is one line (the app's short names from `UI.TOPIC`, as the palette and sidebar say them;
  the full name stays the tooltip, the accessible name and the skill window's title); the domain head's open-mistake
  sum is gone in the wide tree (its rows show theirs; a tile keeps it); "some picked" is a quiet ink bar on a white box,
  so amber marks only picked skills, the search edge and Start; the hero shows as many whole chips as fit, then "+n",
  never an ellipsis; Your sets uses `list`. A shortened name's tooltip carries the full name and, on a dimmed row, the
  reason too (the name's title wins over the row's, so the reason would otherwise hide on hover screens). The aside: Ready titles 500/14 (were 600/14.5), short skill names in Ready,
  the set in progress and Your sets, balanced meta lines (no "so far" or "q" alone on a line). Verdict: the hero reads
  as the one raised thing with the one orange button; the tree breathes on a 40px rhythm.
- **390.** Tiles in a row match heights; a tile says "1 of 5" (" selected" for screen readers) so no word wraps alone;
  domain tiles use the short domain names. Your sets' four tabs stay one row and scroll sideways with soft edges (was
  "Official questions" wrapped onto a second line). Verdict: calm; the Now strip's condensed Start is the shell's (below).
- **Start window.** Panel top 20px (the group label sat on the tab rule), groups 16px apart, "Questions from" and
  "Answers shown" are one plain list (no grey well per row; a hover band; the chosen row keeps wash-2 and the amber
  inset; disabled pools are faint text only), height 680 (the tallest tab measured 506 of 564), Print PDF never wraps on
  a phone. Verdict: reads as a settings sheet, not a stack of grey boxes.
- **View and preset menus.** Both grow from their trigger's end (`align: 'end'`), so View stays over the tree and the
  preset menu inside the aside's edge; Mentor's pick's line is one clause ("Open mistakes: Linear equations 4, ...", two
  lines, was three). Verdict: fine, apart from the radio circles (shared ask 2).
- **Habits.** "Drill it" is the quiet way forward with its arrow at the row's end (was ten white buttons ragged after
  each line). First use (fresh learner) unchanged: the start drawing and its line.
- **Your sets.** A set in progress with no tally printed "null right · 0%": now the en dash.
- **Quick sheet (Q).** The check row (Sure, Not sure, Guessing) is sticky at the foot of the sheet's scroll, so a long
  question no longer hides how to answer it; after the answer the verdict and its actions scroll into view (smooth,
  instant after a key or with motion off). Verdict: good.
- **Palette (Mod+K).** Open-mistake counts are the tree's neutral badge (were an amber dot and number per row).

### Checks

`check-ui.py` ok; `node --check` on builder.js, quick.js, palette.js and the inline script; no em dashes in the four
files. Smoke `FIX=practice page.js` 1440 and 390: NO ERRORS (same as before). In Chromium the console shows only the
kit.js roll error (shared ask 1); Reading & Writing's tree (no `UI.TOPIC` short names) falls back to its own names. Inventory 1440 and 390 against the run
before the edits: one button renamed, "Geometry1 skill" -> "Geometry & Trig1 skill" (the tile's short domain name);
nothing gone or added.

### Shared asks

1. **kit.js:2057, a live bug.** `UI.roll` declares `off = from.length - text.length`, shadowing the motion `off()`, then
   calls `off()` at 2073: `TypeError: off is not a function` on every roll that moves a digit. On Practice: changing the
   length in the Start window throws inside `paintBar` (the hero and the window's footer keep "10 questions" while the
   set is 30; `paintAvail`/`paintSel` are skipped), and picking a preset with another count (Full section mix, 44)
   throws inside `applyPreset`, so the preset menu stays open and the hero keeps the old figure. ui.js `carry` (sidebar
   streak) throws the same. Fix: rename the local (`const shift = from.length - text.length`, and `from[i + shift]`).
2. Menu radios (ui.css 2489-2497): every unchecked `menuitemradio` draws an empty circle; the View menu shows 11 and
   the preset menu 15. Draw only the checked item's mark.
3. `--seg-thumb`'s amber ring: the Start window's Set tab shows five orange rings (four seg thumbs and the chosen row)
   plus the tab underline and Start. A raised white thumb without the ring would leave orange to the chosen row and Start.
4. question.js: the picked option before Check draws a 2px amber border inside a second ring (a double box); the
   "Sure, but wrong" note is an ink-bordered box (the boxed look the user called out).
5. The phone top bar's condensed "Up next ... Start" (after scrolling) is an orange pill on Practice; `ownPrimary` covers
   the Now strip and the sidebar but not this one.
6. The "Your progress is only in this browser" banner's Save progress is a second orange pill above the page's Start;
   the sidebar's Tests "Resume" chip is amber too.
7. Map view: every ready cell is a solid amber square (a wall of orange on a learner with history); consider the
   ink or amber-200 fill for "ready".

### For the user

- The skill tree uses the short skill names the palette already uses ("Two-variable equations", "Ratios & rates",
  "Geometry & Trig"); hover a row for the full College Board name. OK, or back to the full names (rows wrap again)?
- "Some skills picked" is now a quiet dash in a white box; only picked skills are orange.
