# Pass report: Tests (web/tests/**)

Files: `web/tests/index.html` (page CSS and markup), `tests.js`, `start.js`, `talk.js`, `compare.js`.
Checks run: `python3 tools/check-ui.py` (ok), `node --check` on all four JS files (ok; the page has no inline script),
em dash grep on the five files (none), removed selectors grepped across `web/` (none used elsewhere).

## First screen

**Tests, 1440x900** (sidebar 248, main about 1040 wide, `.twocol` main plus a 300px sticky aside).
- Leads with: the title, then the **Next test** card: its name, one meta line ("Next test · your last was 3 days ago")
  and the page's one 42px orange **Start** at the right end (about y 130 to 172). In progress sits right under it as
  40px rows in one card, then Test, fix, prove, then New test as rows.
- Right column, from the top: the estimate (band at the 28px figure, confidence badge with its reason one tap away,
  the target line, the chart, Best / Target / Exam), then What moves this band. The aside sticks under the section
  bar (`--twocol-top: 60px`) and scrolls inside itself.
- Moved out of the way: the 980px score card that led the page (now the aside); the four score lines (total,
  projection, growth, calibration) folded under "Total, pace and growth" (remembered); Habits merged into What moves;
  "How scoring works" to the foot of the aside; the 550px empty column beside the score card is gone.

**Tests, 390x844.**
- Leads with: the title, a one-line estimate under it ("520–600 · Mixed · 60 points below your 650 target", a link to
  the estimate card), then the Next test card with Start first in its actions. Start lands at about y 280 to 320
  (it was near y 1480, two screens down).
- Then In progress, Test, fix, prove, New test (rows), Papers (rows), Your sittings; the estimate and What moves this
  band come after the task (the aside stacks below main under 1280px). The section bar gets Estimate and Habits chips
  under 1280px so both are one tap away.

**Start sheet.** Leads with the steps and "Start now" (the one-tap presets), then the kinds. The stacked h3 "What do
you want to sit?" is gone; the foot (Back, the summary, Start / Next) is the dialog's own `.sheet-foot`, always in
view outside the scroll. Long helps moved behind `?`.

**Paper sheet, share sheet, compare sheet.** Unchanged in order; the composer no longer bleeds past the sheet's
padding, Send is a square `.btn.icon`, the share sheet has one help line instead of two.

## Big changes

1. Tests is now two columns: the task on the left (next test and its Start, In progress, New test, Papers, Your
   sittings), the estimate and what moves it on the right. On a phone the Start is in the first screen.
2. The next test is the header's card with the page's only big orange button; it is called "Next test" now, so it
   reads differently from the sidebar's Up next.
3. New test and Papers are one card each, a row per test, not 3x3 card grids. What used to hide in a hover tooltip
   (a kind's tags and what it is for; a paper's set, your mistake types, new types, sat by, average, your band and how
   its rating was worked out) is the row's second line: on hover or focus with a mouse, always on a phone.
4. Only the next test's own row keeps a small orange Start; every other Start is grey (about 20 orange buttons down to
   2). In progress's Resume is grey too, since the Next test card carries the resume.
5. Habits is no longer its own card: What moves this band has a "Where points went | Habits" switch, remembered.
6. The estimate's extra lines (total, pace, growth, calibration) fold under one toggle; "How scoring works" sits under
   the estimate.
7. Sittings show everything on a phone: the date, minutes and module scores were hidden there before.
8. The filters' values now show at every width as removable chips, and the sort stays visible beside Filters.
9. Start sheet: no second heading, "Start now" for the one-tap presets, the tool and aid explanations and two long
   notes behind `?`, the foot always in view.
10. One button size set: no 38px pills, no round Send button; one tag (`.badge`) everywhere.
11. Empty states are one line each: What moves ("Sit a full section to see where your points went.") and Habits
    (two pips and what it will measure) lost their own orange "Full section" buttons, and the five blank habit cells
    went; the Next test card and the Full section row carry that Start. With no estimate, the "No data" chip and the
    band-width sentence became "No estimate yet" with a `?`. Your sittings' empty state keeps a quiet "Start a full
    section".

## Bugs fixed

- **Compare ticks** (I-1): the checkbox now sits in `label.sr-cmp`, which is what the X key, the compare bar's Clear and
  the dropped third pick look for. Ticking a third row now unticks the first; Clear unticks every box; X works.
- **Filters invisible on desktop** (I-2): the `.fchip.dup` rule that hid the active-filter chips at 760px+ is gone, and
  the sort dropdown is kept out beside "Filters · n" (`filters-keep`), so the current sort shows at every width.
- **O key** (I-3): calls the start sheet for the focused kind or paper directly (`options(card)`), and the ⋯ menu's
  Options uses the same function.
- **Round Send** (`.tk-send` 50%): now `.btn.icon` (10px corners).
- **Section chips out of order** (I-4): In progress, Test fix prove, New test, Papers, Your sittings in page order;
  Estimate and Habits added under 1280px (where they sit below); the Habits chip switches the seg before it scrolls.
- **Phone data loss** (I-5): a sitting row on a phone is tick / name / band and module scores, then date and minutes,
  then actions; nothing is `display: none`. At 760-999 the band stays.
- **Sheet bleeds** (I-6): the start sheet's foot is a real `.sheet-foot` outside the scroll; the composer sticks inside
  the sheet's padding instead of hardcoding -24 / -22.
- **Dead JS** (I-7): `icon`, `sourceLine`, the empty `n`, `est`, the unused `pips()` removed; `ls` and `rec` are used now.
- **Dead CSS**: `.stat.sm`, `.sc-gate`, `.sc-spark`, `.tc-goal`, `.tc-stats`, `.tc-tags`, `.tc-hist`, `.tc-rep`, `.tag`,
  `.conf`, `.pips-row`, `.hb-what/.hb-cell/.hb-ck/.hb-cv`, `.st-subj`, `.st-swh` (and its `!important`), the 38px pill
  rules, the five negative-margin patches, the quiet-button margin override, the `.sections a .n` mono count.
- **F key** focused a hidden dropdown (every dropdown sits behind Filters): it now focuses the Filters button.
- **Habits "Why"** was a tooltip only (nothing on tap or click): it opens its text in a popover now.
- **The confidence reason** was a `title` on a non-focusable span: it is a `?` that opens on tap, click or Enter.
- **Em dash placeholders**: `tests.js` and the nine in `compare.js` are gone; compare uses `UI.NONE` for its
  placeholders and for the filter that drops empty rows (the lead's request).

## Not done

- **The estimate card "after #live" under 1280px** (audit proposal 1): the aside stacks after the main column instead.
  Putting it between In progress and New test needs `.twocol.side-first` (which would also put it above the Next test
  card) or reordering that breaks DOM order against visual order (focus order). The one-line estimate under the title
  and the Estimate chip cover the jump.
- **Folding inside the start and share sheets** (`dialog[data-fold]`): not turned on. The start sheet redraws its pane
  on every choice, so the delayed auto-fold would fold each new help line 180ms after it paints (a jump on every tap);
  the share sheet's help changes text with its seg after it folds (a stale summary). Instead: the long helps went
  behind `?` popovers (fixed module 2, neutral questions, the six tools and aids), the module cards' help became
  their meta line, the traps help was shortened, the share sheet's two helps became one line, and the conditions help
  stays visible (`data-nofold`) because it sets ranking.
- **`?` tooltips on hover**: the `?`s open a popover on click, tap or Enter; they do not also show a hover tooltip (one
  behaviour everywhere, and a tooltip alone never reached touch).
- **Dead hash links into Tests** (outside the audit): `/tests/#history` (me.js:345), `/tests/#module` and
  `/tests/#section` (ui.js:1996, the quick menu) point at ids that do not exist on this page. Not changed: the sources
  are other passes' files. Suggest `#sittings`, and `?start=module1` / `?start=section`.

## Shared asks

- `UI.why(text, {label, text})` in kit.js: a `?` (or a word) that opens its text in `UI.pop` on click, tap or Enter.
  Built here as `TestStart.why` (start.js) with `.ts-q` (soft colour) in the page CSS; other pages will need it.
- `.skill-row` collapses only under `@media (max-width: 759px)`; in a 300px aside its `minmax(150px…)` columns
  overflow. Tests overrides it inside `#levers` with `@container (max-width: 520px)`. A container query in ui.css
  (`.twocol-side .skill-row` or a container on `.card`) would serve every aside.
- `UI.filterBar` with `pop: true`: an option to keep the sort out beside Filters (Tests marks the last `.dd`
  `filters-keep` by hand, `keepSort()` in tests.js). The `.filters-pop` rules also live in this page's CSS only.
- `UI.sheet({ foot: el })`: a sheet foot built by the page (start.js appends its own `.sheet-foot` to `sh.el`).
- A synchronous `UI.fold(el, label)` so a pane that redraws can fold without the 180ms auto-fold jump (would let the
  start sheet opt into `data-fold`).
- `check-ui.py`: flag `border-radius: 50%` on `.pill` and `.btn` (the audit's ask; `.tk-send` is fixed here).
- Section bar scroll-spy: a section inside a sticky aside always intersects; Tests gives aside sections chips only under
  1280px. A shared rule (skip `.twocol-side` descendants when the aside is sticky) would let pages stop checking width.

## For the user

- **Orange Starts** (audit proposal 5, a reversal of the earlier "one orange Start on every card" decision): the header's
  Start is the one 42px orange button; the row of the test it recommends (in New test or Papers) keeps a small orange
  Start; every other Start, including In progress's Resume, is grey. Revert in tests.js: `kindsCard` (`id === rec`),
  `paperCard` (`recommended`) and `liveRow` (`btn sm`).
- **Where the estimate lives**: the right column from 1280px wide; below that, after Your sittings, with a one-line
  summary under the title that links to it. Say if you would rather it come right after In progress on a phone.
- **Renamed chips** on sittings: "Gate +2" is "Route line +2" and "2nd pass +20" is "Second pass +20", each with a
  tooltip that explains it. "Sit this week's Paper #8 instead" is "Paper #8 instead"; "One more section makes this
  Consistent · Start" is "Sit one more section".
- **A sitting's note** is in Geist now, not serif italic (serif is for question text).
- **Not seen in a browser** (worth a look): the band chart at about 268px wide with 8 points; the aside's height at
  1440x900 (it scrolls inside itself when taller); the hover-only second line of New test and Paper rows leaves a
  blank line under each title on desktop until the row is hovered or focused.

## Polish round

Files: `web/tests/index.html`, `tests.js`, `start.js` (`talk.js`, `compare.js` unchanged: every `.seg` there is `UI.seg`, so
the sliding thumb comes with no edit). Checks: `python3 tools/check-ui.py` ok; `node --check` on the four JS files ok (the
page has no inline script); no em dash in the five files; removed selectors (`.ts-q`, `.lv-state`, `keepSort`,
`#cycle > .sc-line`, the `.st-card/.st-mod/.st-radio/.st-trap` looks, `.mv-skills .skill-row`) unreferenced in `web/`;
smoke at 1440 and 390: NO ERRORS before and after. A scratchpad run with a full `/api/tests` fixture also opened the start
sheet through all four steps, the trap pick list, a `?`, and a Discard (both counts rolled): no errors.

### First screen

**Tests, 1440x900.** The title, then the **Next test** card, the only card of its own in the main column, with the page's
one 42px orange Start. Under it In progress, Test fix prove, New test, Papers and Your sittings are sections of **one
surface** (one card, a hairline between sections) instead of five cards. The aside is one surface too: the estimate, a
hairline, What moves this band, with "How scoring works" as the quiet line under it.
- The estimate leads with its number: the title with the move ("Up 20 points since 10 Oct") directly under it, the
  confidence badge and its `?` top right, then **520–600** at 28/600 (-0.03em) with "of 800" small on the same baseline,
  then the distance to the target. Before: title, band, target line, move line in a stack.
- In progress rows: the state and "12 of 22 answered" over a 22-block tick meter (ink), then module and start time.
- Papers: tiles (preview with a hairline, text under it, no box): the preview is what you should get right in module 1
  as 22 blocks with the route line at 14; then Paper #n, New, how it should go for you, your state, Start and ⋯.

**Tests, 390x844.** Same order as round one (title, one-line estimate, Next test with Start in the first screen). The
sections share one surface; a paper is a row again (name, badges, Start and ⋯; the preview meter under it, out of its box).

**Start sheet.** The kinds, modules, timings and traps are `.choice-row` toggles (well rows, wash-2 and the amber inset
when chosen), timings with their clock at the right; the trap list fades at its scroll edges.

### New components added

- `UI.why` for every `?`: the first-estimate note, the confidence reason, Habits "Why" (a word, named "Why: <habit>"), the
  fixed module 2 note, neutral questions, the nine tool and aid switches. Replaces `TestStart.why` + `.ts-q`.
- `.choice-row`: `.st-card`, `.st-mod`, `.st-radio` (buttons with role radio / checkbox, as before) and `.st-trap`
  (`label.choice-row` with its checkbox). Replaces the page's tile-choice look.
- Tick meter (`UI.meter` with `ticks`): In progress answered of total; Test fix prove "Proved 2 of 6" (was a text line);
  each paper's expected module-1 score against the route line (was the "· expect 11 of 22" part of its badge).
- `UI.roll`: after Discard, the In progress count and the Your sittings count roll to their new figure (never on load).
- Number-first estimate head (item 12), as above.
- `UI.edgeFade` on the start sheet's trap list. Sliding `.seg` thumb: automatic on all 16 `UI.seg` calls.

### Removed local copies

- `TestStart.why` body and `.ts-q` (start.js, index.html). `TestStart.why` stays as a one-line pass-through to `UI.why`.
- `keepSort()`: filterBar `keep: ['p.sort']` / `keep: ['sort']` now keeps each sort beside Filters.
- `.st-card/.st-mod/.st-radio` fill, padding, radius and checked state; `.st-trap` grid, hairlines and checkbox styling.
- `#levers { container-type }` and the two `.mv-skills .skill-row` lines (ui.css stacks skill rows in `.twocol-side`).

### Bugs fixed

- Paper rows said "average NaN": `average` is `{value, n, basis}` from the server; the value is read now.
- "1 types new to you": pluralised.

### Not done

- **New test and Your sittings stay rows.** The preview pattern needs something to preview: papers have per-paper data
  (the expected module-1 score), kinds would only get a drawing of their module shape, which their facts line already
  says (decoration, the slop list), and sittings are a sortable, filterable, comparable list where rows scan better.
- **Types met as a tick meter** (New test head): left as the quiet head line; a meter there competes with the list.
- **Rolling the band**: the estimate never changes on screen except cached copy to fresh copy while the page loads,
  which is a load.
- **First and last axis labels on the band chart**: the chart is `UI.bandChart` in charts.js (shared).

### Shared asks

- `UI.why(text, {label, about})`: with `label` the button's name is the word alone, so a list of "Why" buttons all read
  "Why". Tests sets `aria-label` "Why: <habit>" after the call; `about` could name a word button too ("Why: <about>").
- `.filters-pop` (filterBar `pop: true`) still has its rules only in this page's CSS; it belongs in ui.css.
- `UI.sheet({ foot })`: start.js still appends its own `.sheet-foot`.
- A taller tick variant for previews (bencho's 3x20): `.meter.lg.ticks` gives 8px blocks, which reads small in a well.

### For the user

- **Papers are tiles now** (a round-one reversal: round one made them rows). Each tile leads with a preview: your
  expected module-1 score as 22 blocks with the route line at 14. On a phone each paper is still a row. Revert in
  tests.js `papersCard` (drop `ts-tiles`) and `paperCard` (drop `paperPreview`, put "· expect n of 22" back in the badge).
- **One surface instead of five cards** under the Next test, and one in the aside, with hairlines between sections.
- **The `?` buttons** also show their text on mouse hover now (the shared behaviour), and open on tap, click or Enter.
- **Copy**: Untimed's line in the start sheet is "Counts up" (was "The clock counts up, so you still see your time"); a
  paper's badge is "Harder for you" with the expected score in its preview.
- **Not seen in a browser**: the tile grid at 760-1279px (2 to 3 columns), the 8px tick blocks in the paper preview,
  and a paper tile's last line, which (as in round one) shows on hover or focus with a mouse and leaves its space blank
  until then.

## Premium build (part 1)

Files: `web/tests/index.html`, `tests.js`, `start.js` (`talk.js`, `compare.js` unchanged in part 1: their marks are icon
work for part 2). Checks: `python3 tools/check-ui.py` ok; `node --check` on the four JS files ok (no inline script); no em
dash in the five files; removed selectors (`.ts-sub` rule, `.ts-card > .reveal`, `.mv-skh`, `.hs-arrow`, the "more" grid
area) unreferenced in `web/` apart from `.ts-sub` in ui.js `FOLD_SEL` (harmless, see Shared asks); smoke 1440 and 390:
NO ERRORS before and after. A scratchpad run with a full `/api/tests` fixture (up next = paper, resume, section,
module; an empty learner; `#section`, `#module`, `#history`, `?start=section`; the ⋯ menu, "n more kinds", How
scoring works, the start sheet's More presets across a redraw): no errors.

### First screen, before and after

**1440x900, main column** (sidebar unchanged):
- Before: 3 section chips above the title; the hero (1 orange Start); New test with 9 rows, each 2 lines with a blank
  reserved line, 9 Starts (1 orange) and 9 ⋯; a "Which ones?" link; Papers head with Filters, Sort and a folded help
  line. About 26 targets, 2 orange fills, 9 blank lines.
- After: the title (chips wait until the bar sticks); the raised hero with its shape strip and the one orange Start;
  New test as 4 one-line rows (only the next test's row shows Start and ⋯; the others reveal theirs on hover or focus)
  and "5 more kinds"; Papers head with `?`, Filters and Sort. About 9 targets, 1 orange fill, no blank lines.
- Aside: the band at the hero step; "Sit one more section" is quiet text, not a boxed button; cause rows read name,
  count, points (actions on hover or focus); "Skills worth the most" folded.

**390x844:** the chip row stays (phone); the estimate line leads with the band at 16/600; the hero's two module strips
stack; New test 4 one-line rows (was 9 rows of 2 lines plus a tags line each), 8 buttons (was 18).

### Hero

`#next` is `.card.hero` (A1's surface, shadow and `--hero-wash`; no local depth). A `.k` "Next test" over the title,
one facts line ("44 questions · 70 min · your last was 9 days ago"; the "Next test ·" prefix went), Start at the right.
Its figure is the test's shape: module 1 as 22 blocks with the route line at 14, lit to your last module 1 ("Last time
15 of 22") or, for a paper, what you should get ("Expect 15 of 22"); module 2 beside it; a module or trainer shows module
1 alone; a resume shows the sitting's answered blocks. Diagnostic, traps, custom, pressure and contest have no strip.
The page's number, the estimate band, is `.hero-num` at `--fs-hero` in `--ink-strong` (56px inside the 300px aside, by
container query, so "520–600" never touches its edge).

Decision: the page audit (section 3) kept the band at 28px; SUGGESTIONS #8 lists Tests for a big hero number and BUILD
rule 9 made `--fs-hero` for it, so the band takes the hero step and the hero card's title stays 16/600 (the audit's
point, that nothing ties the h1, still holds).

### What moved behind which control

- A kind's tags and what it is for: the first line of its ⋯ menu (was a hover-only second line, blank until then).
- A paper tile's set, mistake types, crowd, average, your band and the rating's working: the first line of its ⋯ menu
  (was the blank-until-hover last line). The rating badge keeps its tooltip.
- Kinds 5 to 9 (Module 2 harder and easier, Custom, Diagnostic, Twin, Route-up trainer, whichever are not in the four):
  behind "n more kinds", remembered (`satf.tests.moreKinds`). J/K skip them while folded.
- The four kinds shown: the next test's kind, Full section, Module 1, Trap test, filled from the usual order.
- Papers help: the `?` beside "Papers" (was a folded help line).
- "Skills worth the most" and "All skills": a fold, remembered (`satf.tests.skillsMore`).
- What moves cause actions: `.reveal` (on hover or focus with a mouse, always on touch).
- The first-estimate `?` text: the empty state's line.
- Start sheet presets: one in view (the recommended one, else Like test day) and "More presets" for the other five;
  the kinds are one column.
- Section chips at 1100px+: hidden until the bar sticks (page CSS); the phone keeps them.

### Bugs fixed

- Open bug 11: when the next test resumes a sitting, In progress no longer lists it (and its chip counts the rest).
  Its Hand in and Discard moved into the hero so nothing is lost.
- Dead links into Tests from other pages: `/tests/#history` opens Your sittings, `/tests/#section` and `/tests/#module`
  open the start sheet on a full section and module 1 (handled here, the sources unchanged).

### Per page and More items done

- Next test card shows the test's module shape as a tick strip; kind rows one line each.
- One orange fill in main: the next test's row (kind or paper) is `.btn.sm` with a "Next" badge; a kind row keeps its
  Start and ⋯ in view. No side stripe (the user's rule, from the lead's A1 note).
- The lead's A1 follow-ups: the rows' ink focus box (`.ts-card`, `.sr-row`, which also set `outline: none`) is gone,
  so the shared amber-deep ring shows, rounded; page-tone `var(--tile)` boxes inside the white sheets are `var(--well)`
  (`.tk-top`, `.hs-box`) and the crowd rows' hover is `var(--hover)`; tile grids keep their own gaps (papers 20/16,
  talk tops 12), only groups take the 32px `--card-gap`.
- Phone: the hero's Start is full width with its quiet links under it. The hero rule is `.card.ts-next`, so its grid
  wins over `.card.hero` on a tie.
- Air: sections in the main and aside surfaces 24 + 24 around their hairline (was 16 + 16); groups take `--card-gap`.
- Sample rows: "No estimate yet" shows a dimmed band and chart, What moves two dimmed cause rows, Your sittings a dimmed
  sitting row (all `UI.empty`, the action appended as before, so `UI.empty` never swaps in "Start with 8"); "Not rated
  for you yet" is the 22 blocks and route line, unlit.
- Route drawing: How scoring works draws module 1 forking to the harder module 2 (amber) or the easier one, replacing
  the "14 of 22 →" text.
- New test head: "14 of 61 types met" as one link (tooltip and label keep "under the clock").

### Inventory diff (1440 and 390, smoke fixture)

- Gone: "About the first estimate" (its text is the empty state's line).
- New: "4 more kinds" (the fold), "About papers" (the help), three point buttons of the dimmed sample chart (inert,
  aria-hidden), meter ids `kmk*`. `kclip*` ids are generated and only renumbered.
- Unchanged: every Start, every "More for …", every filter and id. Hidden kinds stay in the DOM.

### Not done (part 2 or shared)

- Play icon on Start, `⋯`, `×`, `!`/`✓`, talk and compare marks: icon work, part 2.
- Busy, done, saved-in-place, motion, quiet menus, drawn checkbox: part 2.
- One "Best for me" button holding Sort and Filters: needs filterBar (shared).
- Sidebar Up next Start as `.btn.sm` when it is the hero's test: shell.

### Shared asks

- `UI.sections(list, { until: 'stuck' })`, then drop the page's 44px rule.
- Drop `.ts-sub` from `FOLD_SEL` (ui.js): Tests no longer uses it.
- filterBar: a sort-labelled trigger that holds the filters ("Best for me · 2").
- Sidebar Up next Start quiet when the page's hero carries the same test.

### For the user

- **Recommended row Start is grey now** (round one kept a small orange one): one orange in main; a "Next" badge marks
  the row. Revert in tests.js `kindsCard` and `paperCard` (`cls: 'btn sm'`).
- **Start sheet**: one preset shows, as a grey button (round one made the recommended one orange); five behind "More
  presets". Revert in start.js `stepTest`.
- **"Sit one more section"** is quiet text under the target line, not a boxed button.
- **Not seen in a browser**: the hero strips at 760-1279px, the 56px band in the aside, the fork drawing on a phone,
  and the chip bar appearing when it sticks at 1100px+.

## Premium build (part 2)

Files: `web/tests/index.html`, `tests.js`, `start.js`, `talk.js`; `web/test/test.js` line 31 only (the lead's ask: the
dot fallback). `compare.js` unchanged (its ✓ ✕ – marks are text, which Marks now draws). Checks: `python3 tools/check-ui.py`
ok; `node --check` on the five JS files ok (no inline script); no em dash; smoke 1440 and 390 NO ERRORS; the scratchpad
fixture runs (up next = paper, resume, section; an empty learner with the start sheet open; a stored older band) NO
ERRORS. Inventory, part 1 to part 2, 1440 and 390: nothing gone; one new generated chart id (`chf2`, charts.js).

### Shared pieces adopted

- `UI.shell({ ..., ownPrimary: true })`: the sidebar's and Now strip's Up next Start is a `.btn`, so the hero keeps
  the one orange button. The page's -44px section-chip shim is gone (the shell defers the chips now).
- Busy and done: the start sheet's `go()` no longer swaps the label to "Building…" (the width jumped); `aria-busy`
  shows A1's spinner after 300ms at the same width, and a built `.pill` takes `.done` (the drawn check, in place of
  the hero's play mark) while the lobby loads.
- Saved in place (UI.saving): a sitting's note Save (Saving, Saved with the check, then the editor closes; no toast),
  the board name Save in a paper's discussion (no "Name saved" toast), the share sheet's Copy, the race's Copy and
  Copy code ("Copying", "Copied"; no toasts). Copy still makes the link the first time.
- Quiet menus: every ⋯ (kind rows, paper tiles, sittings) is a ghost `.ibtn` with `UI.icon('more')` (was a grey
  `.btn.sm.icon` with a ⋯ character); the sitting row reuses the page's `moreBtn`.
- Drawn checkbox: the page's 16px ink `accent-color` override on the compare tick is gone, so A1's 18px box shows.
- Hover band: a kind row and a sitting row show a warm `--hover` band 8px past their text, under their content.
- Focus, surfaces and wells: done in part 1 for the lead's A1 note.

### Motion and feedback

- Page entry: `data-m="stagger"` on the main column (title, hero, the list surface; `data-m-now` on the hero so Start
  is never delayed) and on the aside (the estimate card, How scoring works).
- The estimate band rolls (`UI.roll`) when it differs from the band last seen on this device (`satf.tests.band`), in
  the aside and in the one-line estimate under the title; never on a first visit. A repaint with the same band keeps
  the same node, so a roll in flight carries on.
- The hero's strips fill once a tab (`satf.tests.strips` in session storage): drawn empty until the sittings behind
  them are in, then lit left to right 240ms later, for every hero kind (section, paper, module, trainer, resume). A
  repaint of the same hero keeps its nodes, so the fill carries on; later visits in the tab paint them full.
- List glide (`UI.glide`): Papers and Your sittings glide on a filter, sort, chip removal, Show all / Show more and
  "Only: …" (tiles keyed `p<n>`, rows by sitting id); never on the first paint.
- "5 more kinds": the revealed rows rise 4px, 30ms apart.
- Where points went | Habits: the pane fades in on a switch (not on load).
- Start sheet: Next, Back and a step label slide the pane 12px from the side it travels from (a choice that redraws
  the same step does not move); keys stay instant.
- Folds (Total, pace and growth; Skills worth the most), sheets, menus, toasts, the seg thumb: shared, nothing to call.

### Icons and illustrations

- ⋯ to `UI.icon('more')` (3 call sites into 1 helper); the filter chips' "×" `::after` to `UI.icon('x', 12)`; the
  hero Start leads with `UI.icon('play', 16)`.
- Row menus carry icons: Options (settings), Race friends (compete), Report a problem (report), Questions & discussion
  (chat), Again exactly and Retake (again), Twin (twin), Try the harder module 2 (up), Share (link), Note (note).
- `UI.spotArt('start')` above the line of Your sittings' first-use empty (with its dimmed sample row); no drawing on
  the filtered empties or in sheets.
- test.js: an unknown icon name draws nothing (was the orange dot that hid typos).
- The paper sheet's Send stays a square `.btn.icon` with the arrow.

### Not done

- Filled twins: none of this page's toggles carries an icon (Helpful, the domain and difficulty toggles are words), so
  there is no twin to show.
- Carets: no disclosure control in these files draws one (the dropdowns are kit's); the crowd rows in a paper's sheet
  expand on their whole head, which has no room for a caret in its four columns.
- The stepper bar filling by scaleX: the stepper is rebuilt on every draw, so a transition has nothing to run from.
- Band chart draw-in and the amber fade under it: charts.js.
- The habit row marks (! and ✓ in a ring) stay text (Marks draws ✓).

### Shared asks

- **kit.js `meter()` tick count is off by one** when `ticks === max`: `Math.floor(v / max * t)` gives 14 for 15 of
  22 (15 / 22 * 22 = 14.999…). "Last time 15 of 22" lights 14 blocks, and every paper preview and In progress meter
  can show one block short. Fix: `Math.floor(v * t / max + 1e-9)`.
- A caret slot in kit's expandable rows (or a `UI.disclosure` helper) for heads like the paper sheet's crowd rows.

### For the user

- **Row ⋯ buttons** are bare icons now, darker on hover; the Start beside them is unchanged.
- **Copy and Save** say "Copied" or "Saved" with a check in the button instead of a toast.
- **Not seen in a browser**: the band's roll (it needs a band different from your last visit), the strips filling,
  the start sheet's slide, the hover band under a sitting row's checkbox.

## Visual review

Shots: `spec/redesign-2026-10-19/premium/shots/app-review/tests-*` (`r0` before, `r1`/`r2` after the fixes, `r3` after
the lead's round-3 pieces). Browsed as `a:v2revresults01` (most attempts; other reviewers started five sections on it
during the session, so later shots show a resume hero and In progress), `a:s7fdfaa02e3cd2ab96` (next test = a paper),
`a:iy33gerjmudak47b` (a resume) and a fresh learner; 1440 light and dark, 390; hover, Tab focus, the hero pill's hover
and press, the ⋯ menu, "4 more kinds" opened by keyboard, the start sheet (light and dark), the share sheet's Copy,
the Filters popover, two sittings ticked (the compare bar), the Habits half.
Files: `web/tests/index.html`, `tests.js`. Checks: `tools/check-ui.py` ok; `node --check` on the four JS files; no em
dash; smoke (page.js tests 1440 and 390, and the scratchpad's rich `/api/tests` fixture with its sheet walk) NO ERRORS,
output identical to a copy with my tests.js edits reverted; inventory (every button, link, field and meter by name,
rich fixture, 1440 and 390) identical: 106 and 109 controls, nothing gone, nothing new.

### Per screen

- **Estimate (aside).** Verdict before: two bugs and a lonely badge. Fixed: the "Example" tag of the empty estimate sat
  on the 480–620 figure (the shared `.empty-sample > .badge` corner); it now takes the confidence's place beside "of
  800" (`tag: false` and the page draws it). The same corner tag covered the points of What moves' sample rows and the
  ⋯ of Your sittings' sample row: those samples now give the tag its own strip above the dimmed rows (page CSS). A
  literal "null" printed under the band when there was no target (`host.append(..., null)`: native append prints
  null). The confidence badge and its `?` sat alone on a line (the title is too long to share a line with it in
  300px); they now sit beside "of 800". Best / Target / Exam no longer wrap "Set a target" (auto columns, spaced).
  "Where points went" overflowed its half of the full-width seg by 11px; the seg is content-width now.
- **Next test hero.** Good: one raised card, one orange button, the module strips give it depth; focus ring and press
  read well. Changed: a resume hero showed four actions (Plan your test days, Discard, Hand in, Continue); Plan your
  test days now shows only beside a fresh test (Plan is in the nav).
- **New test rows and "4 more kinds".** Rows good at 1440. "4 more kinds" floated centred in 600 weight between the
  list and Papers; it is a left-aligned disclosure with a caret that turns (`caret_down`, `aria-expanded` as before),
  and "Show all n" / "Show n more" sit on the list's left edge too. On a phone "You ≈500 · Best ≈590" floated mid-row
  (margin-left auto in a wrapped line); it now flows after the facts.
- **Papers tiles.** Verdict before: the identical-card-grid look: every tile had a hairline box saying "Expected in
  module 1 · n of 22", "About your level" on 9 of 10, and a white Start plus ⋯ (20 controls). Now: the preview is a
  quiet well with the 22 blocks and the route line alone (the meter keeps its words for screen readers), then the name
  and one line "Expect 13 of 22 in module 1" with Start and ⋯ to their right, shown on hover or focus with a mouse
  (always on touch) like the kind rows; the next test's tile keeps them out. A rating badge shows only when a paper is
  harder or easier for you (its tooltip and the ⋯ menu's first line keep the working). The `?` beside Papers says what
  the blocks are. Ten tiles before Show all (five rows of two; it said "Show all 10" for one hidden paper). Tiles are 300px at least, so at 1024 (`tests-r3-1024-*`) two columns keep the line and Start side by side (three 270px tiles wrapped the line). A tile gets
  the warm hover band. Phone: a row (name, line, Start and ⋯, the blocks under).
- **Start sheet.** Steps, presets and the foot good in both themes. The segs (Module 2, Module 1, the share sheet's)
  stretched their track to the sheet's width with the options bunched left; they are as wide as their options now.
  The seven kind rows are the shared `.choice-row` wells; left as they are.
- **Compare bar.** Good; its label read "Compare Full section and Full section" for two unnumbered sittings; now
  "Compare these 2 sittings (full section)".
- **Habits.** The action "Hard-end practice · 10 hard at 95 s" ran past the 300px aside (a button never wraps): the
  verb is the button, the terms sit beside it as a meta (aria-label keeps the whole label).
- **Lead's round 3.** `.filters-pop` rules gone from the page (shared now); the share sheet's and the race's Copy
  buttons use `UI.copyText(text, { button })` (the share link is made on the first Copy, the button busy meanwhile).

### Shared asks

- ui.css `.empty-sample > .badge` (absolute, top right) lands on whatever sits at a sample's top right; give it a
  reserved strip (`.empty-sample:has(> .badge) { padding-top: 28px }`, badge at `top: 0; right: 0`) or place it in
  flow. Tests does this in page CSS (`.ts .empty-sample…`); other pages with a figure at the sample's corner will hit it.
- charts.js `bandChart`: two sittings on the same day print the same x label twice ("Sep 23 · Sep 23"); its empty
  text "Your first test puts a point here." overlaps the y-axis labels (paper learner, 300px aside); the legend wraps
  to two lines at 300px.
- Server: `GET /api/history?all=1` returns 500 for `a:iy33gerjmudak47b` and `a:s7fdfaa02e3cd2ab96` (the page shows
  "Your sittings 0" with a sample although the learner has an estimate).

### For the user

- **Paper tiles** show Start and ⋯ on hover (always on a phone), and "About your level" is gone (Harder / Easier stay).
  Revert in tests.js `paperCard` (drop `' reveal'`) and `ratingTip` (put back `about: 'About your level'`).
- **The confidence** (Consistent, Mixed, Rough) sits beside "of 800" under the band, not top right.

### Round 4 (the lead's two asks, fresh learner)

Shots: `tests-r4-fresh-1440-*` (light and dark, hero hover, the Trap test row hovered), `tests-r4-fresh-390-*`.
- **Plan your test days** (hero) was a bold `.quiet` beside Start and read as a label: it is a `.link` now (the shared
  link look, 500 weight, an underline at rest that turns amber on hover), so it reads as a secondary action.
- **No traps ready yet** floated mid-row in the results column; it now sits at the row's end where the other rows'
  Start sits, right-aligned and muted, with ⋯ beside it on hover or focus (`.reveal-host` on the row). The disabled
  Start it stood next to is gone (it did nothing; the words say why). On a phone the words go under the facts like
  the other rows' results, ⋯ at the row's end.
- Checks: check-ui ok, `node --check` ok, no em dash, smoke NO ERRORS (plain and rich fixtures, 1440 and 390).
  Inventory: the rich fixture (traps ready) is identical; the plain fixture (no traps) loses only the disabled
  "Start Trap test" button.
