# Pass: Results and the score report

Files: `web/results/index.html`, `web/results/page.js`, `web/results/report/index.html`, `web/results/report/page.js`,
`web/assets/results-ui.js`, `web/assets/report.js`, `web/assets/charts.js`.

## First screen

**Results, 1440x900.** Leads with the header: "Results" and one orange `.pill`, "Practise the top 3 · ≈ +40" (or
"Fix all open · n" when there is no gain to show; none for a read-only link or a student with no scored test). Below
it two columns. Main: "Score over time" (Range and Kinds controls now sit in the card head, the legend folds behind
"Key"), then Sittings. Right column (300px, sticky under the section chips): the estimate card ("Math 520–600" as
its title, confidence and trend badges, the target track, Best / To target / Exam rows), Totals as rows, and one
Share row. Moved out of the way: the Share button and `⋯` left the header for the right column; the kicker over
every card is gone; the Totals tile grid (2 rows of 4) became 8 rows of about 36px beside the chart.

**Results, 390x844.** Header with the primary pill beside the title, then the estimate card, the chart, Sittings,
Totals, Share, Trends, Mistakes, Skills: the old reading order (the two columns dissolve below 1280px). Sitting rows
are two lines (name and score, then the day and Fix / Peek) instead of four. Skills are 44px rows instead of 120px
tiles (about 3800px of skills down to about 1300px).

**Report, 1440x900.** Leads with "← Results", the sitting's name as the h1 ("Full section #3") with the actions on
the same row (orange "Win back ≈ 60 pts" split button, Review mistakes, Retake as a test, `⋯`), and one meta line
(date · 64 min · Timed · Adaptive · Form 2.1 · conditions · the note). Main: Points, then Mistakes. Right column:
the gauge and its facts, Recovery as four steps, the Summary rows, Takeaways, Best value, Up next, sticky while the
question grid scrolls (so What if moves the gauge in view). Moved out of the way: the uppercase eyebrow, the date
as h1, the separate condition-chip row and the "Add a note" row (into `⋯`), the recovery status strip, the tiles
row, the three takeaway cards.

**Report, 390x844.** Back link, h1, actions (still wrapping to two rows), meta line, then the score card, Recovery,
Points, Then vs now, Mistakes, Best value, Takeaways, Summary, Questions, Breakdown, Judgement, Time, Up next: the
old order, minus the Habits and Modules cards (merged). The phone's sticky Fix / Jump to / Review strip is unchanged.

## Big changes

- Results has a right column: the estimate, Totals as rows, and Share live there; the chart, sittings, trends,
  mistakes and skills have the main column. Below 1280px everything is one column in the old order.
- Results' header carries the page's one primary: "Practise the top 3" or "Fix all open". The same button inside
  Trends > Gap or Mistakes now shows only when the header does not have it.
- Share moved from the header to the right column ("Share progress" plus `⋯` with CSV, Print, read-only link).
- Every skill is a 40px row (glyph, name, mastery bar, right/answered, open mistakes), two columns where they fit.
  The mastery word and counts are the row's tooltip and label, and the panel a tap opens.
- Sitting rows (Results and Today's Recent tests) are hairline rows. The Review button is gone (the title is the
  same link); Fix and Peek show on hover or keyboard focus on a laptop and always on touch.
- Mistakes on Results: 5 rows, "Show all 10" expands; Fix per row on hover; "All mistakes" link in the card head.
- The Report header: the h1 is the sitting's name; date, minutes, timing, form, conditions and note are one meta
  line; "Add a note" / "Edit note" moved into `⋯`.
- The Report has a right column: score, Recovery (four steps with ticks), Summary rows (were tiles), Takeaways (rows,
  were three cards), Best value, Up next.
- The Report's Modules card is gone: each module's result, route, time against 35:00 and flags are now the question
  grid's module heads (and a line per module above the table view).
- The Report's Habits card is gone: habits are a group inside Mistakes, with the same Drill buttons.
- Up next on the Report no longer repeats the shell's Up next item; its rows are "name, size, Start".
- "Win back ≈ 60 pts" is the whole label now; the question count and minutes are its tooltip and the first line of
  its `⌄` menu.
- The target is named once per page: Results on the estimate track; the Report on the gauge dial (the facts say
  "3 questions from your target", the Correct row lost "need 31 for 650", the gauge key lost its band and target rows).
- Breakdown's Domains: "By points / SAT order" is a small select in the panel; the domain tiles lost their fills.
- Colour by time / cause / points uses ink steps from tokens, so dark mode shows dark cells, not pale ones.
- charts.js gained two opt-ins any page can use: `ctlHost` (put the Range / Kinds controls in a card head) and
  `legend: 'fold'` (the key behind a "Key" toggle, the shared fold look).

## Bugs fixed

- report.js styles beat the Report page's after any Feedback or Report a problem (`.rp-acts` stacked the header
  actions, `.rp-row` changed gaps, the page's `.rp { gap: 24px }` hit the modal). Every report.js rule is scoped under
  `dialog.sheet.rp` (`.rp-rec` stays global); the page styles `#root.rp` and `#head .rp-acts` only.
- report.js's click breadcrumb skipped every click on the Report page (it excluded `.closest('.rp')`, which is the
  page root there); it now excludes only `dialog.rp`.
- `.sc-side` was declared twice (grid, then flex): now one grid, Fix and Peek in fixed columns, rows line up.
- Colour-by shades were hardcoded light browns (pale in dark mode, white text at 2.6:1): `--sh-0..3` from
  `color-mix` on `--ink` and `--surface`, legend swatches read the same vars.
- "Math 520–600" overflowed its span-4 card from 1100 to 1440px: the card now lives in the 300px column at 28px,
  or full width below 1280, and may wrap.
- The Sittings filter row was `nowrap` from 760px and overflowed up to 1280px (and in the new main column): it wraps.
- A flagged route-saver cell lost its flag corner (`::before` reused): the saver is its own `.rp-saver` mark.
- `.rp-table table { min-width: 1180px }` forced a sideways scroll at every width: `min-width: 100%`.
- `border-radius` on collapsed table cells (no effect) removed; `.sc-chip` double `box-shadow` tidied.
- charts.js `textW` comment said DM Mono: corrected (Geist Mono 0.6em; 0.62 errs wide for Geist figures).
- `Oʻzbekcha` (U+02BB, missing in Geist) is `O’zbekcha`.
- Em dashes as empty values (results-ui.js, charts.js x3, report.js) are en dashes.
- FOLD_OFF no longer matches the Report, so its `.rp-helper` and the gauge caption fold. The sample / shared /
  re-scored strips and the "Misconceptions show once…" line carry `data-nofold`; nothing else long is must-read.

## Not done

- Proposal 12, dropping Results' Exam and Streak: kept as one row each. The shell shows the streak everywhere, but
  the exam date is not in the phone shell, so dropping it would lose it on a phone.
- Chart svg labels stay Geist Mono 10.5 / 11px: their font lives in ui.css (`figure.chart svg text`, lead-owned). See
  Shared asks; `textW` needs no change unless the size changes.
- One shared component for `.rs-strip/.rp-strip`, `.rs-line/.rp-line`, `.rs-row/.rp-row`, `.rs-helper/.rp-helper`,
  `.rs-bar/.rp-bar`: restyled identically per page, not merged (only the info button and key/value rows moved into
  results-ui.js as `UI.rx.info` and `UI.rx.kv`). Merging means renames across both pages for no visual gain.
- Takeaway buttons still repeat Pace's Careful set and Judgement's changes chip: they are the actionable summary.
- The Module 1 result still shows in three places (score facts, the Points route line when 3 or fewer short, the grid
  head); the fourth (Modules card) is gone.
- The `.rp-split` split pill still squares one side of two `.pill`s: it is the one split button on the site.
- The Report's phone header still wraps its actions to two rows (see For the user).
- The total line under Details still repeats the band ("Math 520–600 measured here · R&W 600"): it explains the sum.
- No browser check (pass rules); geometry is reasoned from the CSS.

## Shared asks

- `ui.css:1518-1524` `figure.chart svg text`: Geist with `tabular-nums` at the micro step (11.5px) per DIRECTION 1.
  When it lands, tell the Results owner: charts.js passes 10.5 / 11 to `textW` at lines ~571, 582, 592, 995, 1086,
  1509, 1543, 1552, 1555, 1651, 1690; they become 11.5 (the 0.62 factor can stay).
- `ui.css:1147` `.card-head > h2, .card-head > h3`: still 700 18px; DIRECTION's section step is 16/600.
- `ui.css:1215` `.badge`: 999px corners and `.badge.n` mono 11px; DIRECTION says 6px and Geist micro. Results and the
  Report now use `.badge` for every tag (the delta, "First section", compare counts, "Practice only").
- `ui.css:1465` `.legend b`: mono. `ui.css:1616` `.gauge-s`: 13px, off the scale (12.5).
- `ui.css:1526` `.chart-ctl`: `margin-bottom: 12px` is wrong when it sits in a card head (`ctlHost`); this pass
  overrides it as `.card-head .rs-headr .chart-ctl { margin: 0 }`. A shared `.card-head .chart-ctl { margin: 0 }`
  would let Today and Plan use `ctlHost` too.
- kit.js: a shared `UI.info(text, label)` (the quiet `?` with its tooltip); results-ui.js has it as `UI.rx.info` and
  `.rx-info`. Same for key/value rows: `UI.rx.kv` / `.rx-kv` (used on both pages) could be kit's.
- `.twocol` below 1280: both pages use `.rs-main, #side { display: contents }` plus `order` to keep the old one-column
  reading order (main and aside interleaved). If other pages want that, a shared `.twocol.interleave` would do it.
- `.reveal` needs to be a direct child of the hovered row (`:hover > .reveal`); worth a line in the ui.css comment.
- FOLD_SEL: no new info-box classes from this pass.

## For the user

- Sitting rows lost their Review button (the name is the same link), on Results and on Today's Recent tests. Fix and
  Peek appear on hover on a laptop. Keep it that way, or bring Review back as a visible button?
- The Report's summary numbers no longer count up on the first view after Finish (they are rows now, and DIRECTION
  says nothing animates on load). Fine?
- Results keeps Exam and Streak rows (see Not done). Drop them once the exam date is in the phone shell?
- The Report's phone header has four actions in two rows. Move "Retake as a test" into `⋯` on phones?
- The gauge's "Math measured here…" caption folds behind its first words instead of becoming a `?` tooltip. OK?

## Polish round

Files: `web/results/index.html`, `web/results/page.js`, `web/results/report/index.html`, `web/results/report/page.js`,
`web/assets/results-ui.js`, `web/assets/charts.js`, `web/assets/report.js`.

### First screen

**Results, 1440x900.** Header unchanged ("Results" and the one orange pill). The main column now opens on the
estimate as the hero: a small "Math estimate" label with its `?`, then "520–600" at 44/600 with "/800" at 14.5
`--soft` on the same baseline and the change since the sitting before as a badge ("↑ +40 since Oct 7"); Range and
Kinds sit top right of that card head; the chart under it has 4 dashed gridlines (200, 400, 600, 800), no axis line.
The right column is one surface split by hairlines instead of two cards and a loose row: Estimate (Confidence with
its reason behind `?`, "Target 650 · 50 to go" with a 4px track under it, Best, Exam, the quiet "Sit a full
section" link), Totals (8 rows), Share. Moved out of the way: the band left the right column (said once, as the
hero), the confidence and trend chips became a row and the hero's delta, the 8px track with its floating "Target"
label became a 4px meter under its row.

**Results, 390x844.** Header, then the hero card first (figure, then Range on its own line, then the chart), then
the Estimate facts card, Sittings, Totals, Share, Trends, Mistakes, Skills. A student with no scored test still
gets "Sit your first test" first.

**Trends panels** lead with their number: "86 questions in the last two weeks", "12 misses in the last 14 days, by
cause", "70% right of 640, all time" (28/600, the unit 14.5 `--soft` on its baseline). Gap and Domains keep words
(Gap's figure is the header pill's, said once; Domains has no single figure).

**Report, 1440x900.** Header unchanged. Main: Points now leads with "≈ 60" at 28 and "pts below all right on this
route (620–700)" beside it, By cause / By difficulty top right; Mistakes leads with "7 misses" and keeps the rest
("1 named · 1 not answered", Reviewed n of m, the sort) in its head. The right column is one surface: the gauge
and its facts, Recovery, Summary, Takeaways, Best value, Up next, split by hairlines.

**Report, 390x844.** As round one, with the same number-first heads.

### New components added

- `UI.why` everywhere the pages had `rx.info`: the card-head `?`s (Recovery, Points, Best value, Gap, Domains,
  Mistakes), the percentile line, the Domains note, the hero's "About this estimate", and a new `why` on kv rows
  (the Confidence row). Touch now opens them (they were hover only).
- `UI.roll`: the Report's What if band rolls from the last re-score to the new one as cells flip; the Report's
  Questions count ("6 of 44 shown") rolls when a Show chip or a filter changes it; Results' "Showing 5 of 11" rolls
  when Show more adds rows. Never on load: a redrawn card starts plain.
- `UI.saving`: the read-only link's Copy (Copying, Copied; "Copy it from the box" when the browser refuses, and kit
  opens its "Copy this" sheet as before). It replaced the "Link copied · read-only" toast.
- `.choice-row`: the Share sheet's three language tiles (O’zbekcha / English / Русский, 16px padded tiles over 48px
  tall) are three choice rows, the English name as the right-hand meta.
- Number-first card heads (INSPO 5.12): `head({fig: [figure, unit]})` on both pages.
- Quick-stats rows of one surface (INSPO 5.11): the right column on both pages, CSS only (`#side` children at
  1280px+: one hairline between parts, corners only at the two ends; `[hidden]` parts skipped).
- Heatmap readout (INSPO 5.3) now lives in charts.js: `UI.heatmap`'s `draw()` adds `p.heat-readout` after the grid,
  fills it (the latest active day's label) and owns the hover, focus, pointer-leave and blur updates on the grid.
  kit's observer sees the line already there and skips it, so nothing shows twice. Smoke of `dev/kit.html` gives the
  same text as before ("Mon, Oct 19 · 24 questions · 34 min · 15 right").
  With kit's document listeners blocked, charts.js's own listeners alone update it on hover, mouse leave, focus and
  blur (jsdom).
- charts.js gridlines: one dashed group (`stroke-dasharray: 3 3`, a presentation attribute, so a ui.css rule would
  win) in the band, bar, line and quadrant charts; the full bar chart's solid axis line is gone (its dashed 0
  gridline is the baseline; mini bars keep theirs), the time axis's month tick marks are gone (labels stay), the dot
  strip's axis line is gone. Labels were already 11.5 (ui.css, `textW`). This is shared: Today's trend and bars,
  Plan, Tests, Profile and the Report's Time bars change the same way.
- `--shadow-float` on the two floating bars: Results' Compare bar (`.rs-cmp`) and report.js's recording pill (`.rp-rec`).

### Removed local copies

- `.rx-info` (its CSS block and the button builder in results-ui.js). `UI.rx.info(text, label)` stays as a one-line
  wrapper over `UI.why` (label "About X" becomes about "X"; nothing outside these two pages calls it).
- `.rs-lang` tiles (four rules and the 420px media rule): `.choice-row`.
- `.card-head .rs-headr .chart-ctl { margin: 0 }`: ui.css has `.card-head .chart-ctl`.
- `.rs-big-row`, `.rs-chips`, the 8px `.rs-track` with `.tl` labels, `#estimate .rx-kv` margin: replaced by the hero
  and the 4px track.
- `.sc-score[data-acc]` fills (orange tints by accuracy on sitting scores) and the `data-acc` attribute: the score
  is plain ink, right-aligned (one accent per screen; the number already says it).
- Skills' orange `.badge.n` "3 open": a quiet `.rs-open` line with the amber dot used by every other "open" mark.
- Grep of `web/` for every removed class: no references left.

### Not done

- "/1600" (INSPO section 4): the Results figure is the Math band on 200 to 800 and R&W is not measured here, so it
  says "/800". The 400 to 1600 total exists only on a Report, under Details, once the student enters an R&W score.
- `UI.roll` on Results' estimate: it never changes while the page is open (a new sitting means a new page load,
  and rolling on arrival is "on load"). Recovery's counts after the player closes are not rolled: `refresh()`
  repaints the whole report, so there is no old element to roll from. The "Win back ≈ N pts" label fills in from
  /whatif just after load, so it does not roll either. The FRESH gauge sweep after Finish is unchanged.
- `UI.saving` on the note Save and the R&W Save: both redraw their own row on success (the button is gone at once),
  so there is no Saved to show; they keep their toasts.
- Report Time, Questions and Breakdown keep word titles: no single number answers them.
- The clock lane's vertical 5-minute lines stay: they are a lane chart's time scale, not x/y gridlines. The mini
  trend's single baseline is now dashed (it sits in the grid group).
- `.rp-chip` stays: a 28px question chip inside sentences; the shared `.chip` is 36px with a glyph.
- No browser check (pass rules). Smoke: a scratch copy of `page.js` with Results and Report stubs (stats, history,
  map, a 44-question report, whatif, share) at 1440 and 390, plus clicks on Show more, the hero `?`, Share, a skill
  row, Show chips, What if flips and Copy: no errors; the standard smoke on results, report, index, me, plan, tests,
  practice: the same output as before the edits (me and practice fail the same way on their missing fixtures).

### Shared asks

- kit.js: drop the heatmap readout block now that charts.js owns it: `HEAT_C`, `latest`, `heatRead`,
  `heatReadouts`, `heatCell`, `heatFig`, the four document listeners (pointerover, focusin, pointerout, focusout) and
  the `heatReadouts(n)` call in the MutationObserver; the top comment's line ~99 should point at charts.js. The
  PROGRESS kit section's "Better long-term home" note is done.
- ui.css: `.ch-tick` is now unused; `.ch-base` is used only by mini bar charts. `.ch-grid line` could take
  `stroke-dasharray: 3 3` itself (charts.js's attribute then becomes a fallback).
- A shared one-surface aside: both Results pages carry the same four `#side` rules (1280px+: gap 0, hairline
  between visible parts, corners at the ends). Today's "at a glance" aside wants the same; a `.twocol-side.one`
  class in ui.css would let all three drop their copies.
- `UI.saving` could take a `keep` option for a button whose work redraws it, or pages should not call it there
  (see Not done); nothing needed today.

### For the user

- The Math estimate is now the big figure at the top of Results ("520–600 /800" with the change since last time);
  the right column holds its facts. It reads "/800", not "/1600", because it is the Math section only.
- The right column on Results and on a Report is one panel split by thin lines instead of a stack of cards.
- Chart gridlines are dashed with no axis line everywhere charts appear (Today, Plan, Tests, Profile too).
- Sitting scores lost their orange tint by accuracy, and a skill's "3 open" is grey text with a small orange dot
  instead of an orange badge, so the orange that is left points at actions and progress. Keep it that way? The
  sitting rows are shared (`UI.sittingCard`), so Today's Recent tests and the Tests page lose the tint too.
- A Report's Mistakes card is now headed by its count ("7 misses"); the word "Mistakes" stays in the jump list and
  the section chips. Fine, or bring the word back as the title?
- The Share languages are three rows instead of three big tiles; Copy on the read-only link says Copied in place
  instead of a toast.

## Premium build (part 1)

Files: `web/results/index.html`, `web/results/page.js`, `web/results/report/index.html`, `web/results/report/page.js`,
`web/assets/results-ui.js`, `web/assets/charts.js` (`report.js` untouched in part 1).

### First screen, before and after

**Results, 1440x900 (a student with scored sittings).** Before: section chips (5 links), "Results" + pill, the hero
with Range (3) and Kinds (2-4) segs, Key, Sittings with seg (4) + kind select + "Has open mistakes" chip + sort
select, the aside with Estimate and 8 Totals rows. About 19 buttons, 11 links, 2 selects, 3 control rows before
the first sitting. After: no chips until the header has scrolled away; "Results" + pill; the hero card (`.card.hero`)
with its label and `?` left, one "All sittings" button right, the band as the hero number (`.hero-num`, 56-64, /800
beside it), the chart and Key; Sittings with the seg and one "Sort and filter" button; aside: Estimate, Totals as 4
rows + "4 more", Share. About 14 buttons, 4 links, 0 selects, 1 control row before the hero.

**Results, 390x844.** Before: Now strip, 5 chips, header, hero label, Range + Kinds (5-7 buttons), chart: 5 control
rows before the chart. After: Now strip, header, hero label, the figure, one "All sittings" button: 3 rows.

**Report, 1440x900.** Before: 7 chips, "← Results" row, h1 + split pill + Review mistakes + Retake as a test + `⋯`,
meta; main opened on "≈ 60 pts below" with the score a 300px widget in the aside (figure clamped to 34-44px).
About 21 buttons, 4 header rows before content. After: no chips until scrolled; one row "Results / Full section #3"
with the split pill, Review mistakes and `⋯`; meta; then the score leads main as the page's one hero (`.card.hero`:
gauge in a 360px column so its figure reaches 44, the facts beside it); Points under it; the aside opens on
Recovery. About 12 buttons in view, 2 header rows before content.

**Report, 390x844.** Before: actions wrapped to 2 rows (split, Review, Retake, `⋯`). After: one row (split and `⋯`;
Review mistakes is the first line of `⋯` on a phone and stays in the sticky strip and the Mistakes card).

### Hero

- Results: `#overview` is `.card.hero` while it carries the band; the band is `h2.hero-num` with `<small>/800</small>`
  (the local `.rs-big` is gone). With no scored test the "Sit your first test" card is the hero instead, and it now
  opens on a dimmed example chart (`UI.empty` sample: three sittings climbing into an estimate, inert, "Example").
- Report: `#hero` moved from the aside to the top of main as `.card.hero`, gauge beside its facts from 760px. A practice
  set's and a challenge's count ("35 / 44") is `.hero-num` (the local `.rp-big` is gone). The gauge figure stays at
  A1's gauge step (44).

### What moved behind which control

- Results Range (Last 10, 30 days, All) and Kinds (Sections, Modules, Diagnostic, Added): one `.btn.sm.dd` named for
  what it shows ("All sittings", "Last 10 · Sections"), `.on` when it narrows, over a menu: Range radios, Kinds
  checkboxes with each band's swatch and count; the last kind left on cannot be turned off. This is charts.js's
  `filters` option, so it is the same anywhere a page asks for filters (only Results and `dev/kit.html` do).
- Results Sittings: kind of test, "Has open mistakes" and the sort live in one "Sort and filter · n" menu button
  (`#sitfilt`, n = filters on); a pick redraws the list and focus returns to the button.
- Results Totals: Questions, Accuracy, Study time, Tests in view; Streak, Mistakes, Types met, Recovered behind
  "4 more" (a fold only when 2 or more would hide).
- Section chips on both pages: hidden and taking no room until the page header is under the sticky bar
  (`UI.rx.deferSections`, see Shared asks). The Report keeps keys 1-9 and the phone's Jump to.
- Report header: Retake as a test is the first line of `⋯`, its tooltip text as the line's sub (disabled with "Sit
  your own section to use this." on the sample). On a phone Review mistakes leads `⋯`.
- Report Questions: three tool rows became one: Show chips left; Filters (Focus is now the first group of its sheet,
  same `act` URL key), View and Reset right. The key moved under the grid at meta size (`#rvlegend`).
- Report Mistakes: "Reviewed 3 of 7" joined the head's meta line; the sort select is the shared sort dropdown
  ("Sort: Most points"). The gauge's folded caption is a `?` beside the change badge ("About this score").
- Every other select on these pages that sorted (Results Skills, the Report's domain order) is the same sort dropdown.

### Copy and counts

- Results Skills head: "1 of 3 strong" (before any is Strong: "n of m started").
- Trends > Difficulty and format leads with "448 of 640 right, all time" instead of "70%" (the rows keep theirs).
- "No sittings match." now carries a Clear that resets the kind and open filters.

### Bugs fixed

- Bug 13 (dead hook): `data-animate` on the Report gauge had no CSS. The page's extra `setAttribute` and charts.js's
  set and remove are gone; the sweep on `?fresh=1` runs as before (it never needed the attribute).

### New motion and feedback moments, icons

None in part 1 (the brief's part 2).

### Inventory diff accounted for

Run on the stock smoke (Today fixtures, no band; the Report there is "not found") and on a richer local fixture
(a band, six sittings, a 44-question section report, a practice set, the sample, a challenge):
- Results buttons gone: "Last 10", "30 days", "All" and "Sections n", "Modules n": inside "All sittings" (aria
  "Showing All sittings. Range and kinds"). "Has open mistakes": inside "Sort and filter". Fields gone: "Sort
  sittings" (the menu's Sort group), "Sort skills" ("Sort: By domain"). New id `sitfilt`. With no band, the first-test
  sample adds three inert, aria-hidden chart points.
- Report buttons gone: "Retake as a test" (first line of `⋯`). Fields gone: "Sort mistakes" ("Sort: Most points"),
  "Order the domains" ("Order: By points"). New: "About this score". "← Results" became the crumb's "Results" (same
  href). Ids `rvreset`, `rvlegend`, `reviewed`, `fixmore`, `hero` kept.
- Removed selectors (`.rs-big`, `.rp-big`, `.rp-row.lab`, `#sittings .rs-headr .field`, `.rp-domtools .field`,
  `data-animate`): no references left in web/.

### Checks

`tools/check-ui.py` ok; `node --check` on the five JS files (the two pages have no inline scripts); no em dashes;
stock smoke on results and report at 1440 and 390: no errors (Report "not found" as before); the rich fixture with
clicks (both menus, a kind filter to an empty list and Clear, the Filters sheet's Focus and Reset, the sort
dropdowns, `⋯` at both widths, sample, practice set, challenge): no errors; Today, Tests, Plan and dev/kit smoke
unchanged (Me fails the same way before and after on its fixture gap).

### Not done (part 1)

- Gauge as an instrument, the amber fade under the trend, the zone's edges and the newest point's halo: charts.js can
  draw the shapes, but their look lives in ui.css; with the chart draw-in they go to part 2 (see Shared asks).
- "New best" badge (shown once), hover readout in the hero figure, Recovery and fixed-row moments: part 2.
- Unicode marks (`⋯ ⌄ ← ↑ ↓ ▲ ▼ ✓ ✕ ⚑ ✎ ↺`), the one-shape split button, the "Every question right" medallion: part 2.
- Show stays chips, not a 5-way seg: five counted options would scroll sideways on a phone; chips wrap.

### Shared asks

- ui.js: `UI.shell({sections, defer: true})` (or `UI.sections(list, {defer})`) so the bar sits after the page head
  until it sticks. Until then `UI.rx.deferSections(head)` does it page-side: an IntersectionObserver on the page
  header (top margin 44px, 100px on a phone: the bar's bottom edge) toggles `html.rx-past`; `html.rx-defer .sections`
  gets `margin-bottom: calc(-1 * var(--rx-sec, 44px)) !important` (the bar's measured height; `paintBarNext` writes
  an inline margin) and `visibility: hidden` until `.rx-past`. Today, Practice and Plan could use the same.
- ui.css for part 2's chart depth: `.g-groove` (16px groove in `--track` with a 1px inner `--line` edge), a band
  gradient and a needle with a `--surface` halo for the gauge; `.ch-area` (the amber fade under `.ch-trend`), 1px
  amber edges on `.ch-zone`, a halo on `.ch-mid.now`. charts.js will emit those classes.
- A shared breadcrumb look (`.rp-crumb`: the parent in `--soft` at the h1 step, a `--faint` slash) if other detail
  pages want "Parent / name".

### For the user

- Retake as a test moved into the Report's `⋯` (first line, with its one-line explanation). On a phone, Review
  mistakes is there too, so the header is one row. OK?
- The section chips on Results and the Report now appear only once you scroll past the page title.
- Results Totals shows four rows; "4 more" opens Streak, Mistakes, Types met and Recovered.
- Range and Kinds on the score chart are one button now ("All sittings"); Sittings' kind, open-mistakes and sort are
  one "Sort and filter" button.

## Premium build (part 2)

Files: `web/results/index.html`, `web/results/page.js`, `web/results/report/index.html`, `web/results/report/page.js`,
`web/assets/results-ui.js`, `web/assets/charts.js`, `web/assets/report.js`.

### Shared pieces adopted

- `rx.deferSections` and its CSS are gone: the shell defers the section chips on every page now.
- The Report's Fix split is `.split-btn` (was `.rp-split`, two pills joined by hand with a 3px seam under A1's
  borders): "Win back ≈ 60 pts" plus a menu half with `aria-expanded` and a drawn caret that turns while open.
- The right column on both pages is one raised card (`.rx-side` wrapper inside `#side`: white, `--shadow-1`, parts
  split by hairlines; flat in print). Before, Results painted it `--tile` (now the page tone) and the Report drew inset lines with no
  elevation. Below 1280 the wrapper is `display: contents`, so the one-column reading order is unchanged.
- States per the visual review: hover bands are `--hover` (sitting rows, which had none, mistake rows, breakdown
  skill rows, skill rows, kv links); focus on rows is the amber-deep ring inset 2px (was ink); a picked sitting is
  a `--sel-bg` band without the ring (hover leaves it alone); the question chips (`.rp-chip`) get a hover, a press and the `--sel-*` pressed
  look; page-level strips (shared, sample, re-scored) are `--mat`; the phone's sticky Fix strip sits on `--page` with
  the scroll shadow; report.js's wells inside its sheet are `--well`.

### Motion and feedback

- Page entry: `data-m="stagger"` on both main columns and both asides (the header, with the primary, never waits).
- Charts draw in once, the first time each is seen (charts.js `firstView` in `sized()`, calling `UI.motion.draw`):
  the trend line draws, bands and their middles rise, the amber fade wipes in; bar charts' bars rise; line charts'
  lines draw. A chart below the fold or in a closed Trends tab waits until it is seen. Resizes and filter changes
  redraw plainly. This is in charts.js, so Today's, Tests', Plan's and Profile's charts draw in the same way. Dashed
  series (the test window's pace guide) are left out of the draw-in: the stroke draw writes its own dash pattern.
- The amber fade under trend lines: a `.ch-area` path with its `.ch-fade` gradient under `.ch-trend` (band charts)
  and under your line (`.ch-line.you`, line charts).
- Hovering or focusing a sitting on the Results chart shows its band in the hero figure, with its name and day in
  place of the change badge; leaving restores the estimate (`bandChart` `onFocus`). The other bands dim to 55% while
  one is hovered on every band chart (Today, Tests, Plan, Profile too), not only on Results.
- The Report on a fresh hand-in (`?fresh=1`): the gauge sweeps with its figure as before (now once: a cached paint
  followed by the network's no longer replays it), the change chip lands last (after 1.2s, once), and the mark fills
  to the four domains' mastery (`UI.spotArt('done')`) beside it.
- What if: the dashed band glides 240ms from the last answer (or from the sitting's band) to the new one (it starts
  at the old band before the first frame).
- Recovery: a step that turns done on a refresh draws its check (`UI.fx.check`); the step marks are drawn checks.
- "New best": when the latest sitting is your best and beat the one before, a "New best" badge pops beside the
  estimate the first time Results is seen after it (remembered per sitting on the device).
- The Compare bar rises in when the second sitting is picked and leaves on Clear.
- report.js: the sent state leads with a drawn check and "Report #n is in" at section size; the recording pill
  fades in.

### Icons and illustrations

- `⋯` -> `UI.icon('more', 18)` (Results Share, the Report header, every mistake row). `⌄` on the split -> a drawn
  caret. The Peek button's inline chevron (results-ui.js) -> `caret_down`, which turns by itself while open (its local
  rotate rule is gone). The calendar's month steppers `‹ ›` -> `caret_left` / `caret_right` (charts.js). "← Back to
  your plan" -> `caret_left` and the label. report.js's attachment `×` -> `x`. The Results delta's `↑ ↓` -> carets.
- `▲ ▼` (not in Geist or Marks) -> Marks' `▴ ▾`: the domain table's change marks, the sitting rows' "vs last", the
  route-saver mark in question cells and its legend line. `✓ ✕ ⚑ ✎ ↺` stay (Marks draws them).
- Spot drawings: the mark filling on a fresh hand-in (`done`), all clear on the Report's "Every question right." and
  on Results' Mistakes when every one is fixed (`clear`). No drawing on filtered empties.

### Inventory diff accounted for (whole renovation, original files vs now, rich fixture and stock smoke)

As part 1, plus: new id `sidecard` (the Results aside's card), generated gradient ids (`chf1`...) for the amber
fade. No other link, button, id or field changed in part 2.

### Checks

`tools/check-ui.py` ok; `node --check` on the five JS files; no em dashes; stock smoke on Results and the Report at
1440 and 390: no errors; the rich fixture with clicks (hover readout and restore, New best, the draw-in firing once
per chart and not on a redraw, Compare in and out, the fresh hand-in, What if flips, all right): no errors; A/B
smoke (original files vs now) on Today, Tests, Plan, Practice, Review, Words, Compete, Help and dev/kit at 1440 and
390: identical output (Me fails the same way in both on its fixture gap).

### Not done

- Bands sliding to their new place when Range or Kinds change, and new sitting rows rising on "Show 5 more": both
  redraw from scratch (a new svg, a new list), so there is nothing to glide from; the "Showing n" count still rolls.
- Stack bars (Points, Why you miss) and the 14-day bars on the Trends tab grow left to right: stack bars are not svg
  (no `[data-m]` hook); the 14-day bars do draw in.
- Meters and rings sweeping on change: nothing on these pages changes in place (a refresh repaints the report);
  What if and Recovery got their own moments above.
- A Report "New best": the report payload has the previous sitting, not the best one.

### Shared asks

- ui.css: `.split-btn > [aria-haspopup][aria-expanded="true"] > svg { transform: rotate(180deg) }` and icons.css's
  `[aria-expanded="true"] > svg:has(> g.ph-turn) { rotate: 180deg }` both apply to `UI.icon('caret_down')`, so a
  split's caret turns 360 and looks still. The Report uses `UI.icon('down')` (no `ph-turn`) to dodge it; drop one of
  the two rules (then any caret works).
- `UI.motion.enter(el, 'nudge')` replaces `transform`, so an element centred with `translateX(-50%)` (report.js's
  `.rp-rec`) would jump sideways; it fades instead. An `enter` that composes (`composite: 'add'`) would fix it.
- The lead's open item: a shared `caret_down` on `.dd` triggers (Results and the Report now use `.dd` buttons for
  every sort and filter, still with the CSS chevron).

### For the user

- Hover a sitting on the Results chart: the big number shows that sitting; move off and it is the estimate again.
- After a new best, Results shows "New best" once, the first time you open it.
- Every chart draws itself in the first time you see it, on every page, never again on a resize.

## Visual review

Real app at http://127.0.0.1:8071 on the DB copy, learner `a:v2revresults01` (most attempts; 2 sections, 1 module,
drills), the Report on its Full section #2 (`?id=3gGTd2b44bXqmkY-2Y4hRg`, also `&fresh=1`), and a fresh learner.
Own headless Chromium (scratchpad `rv-results/`). Shots: `premium/shots/app-review/results-*` and `report-*`
(`r0` before, `r1`, `r2`, `r3` after each round; `-dark`, `-390`, `-full-*-pN` page slices, hover, focus, press,
menus, sheets, peek, the fresh sweep mid-flight and settled). Files: `web/results/index.html`, `web/results/page.js`,
`web/results/report/index.html`, `web/results/report/page.js`, `web/assets/results-ui.js`, `web/assets/report.js`,
`web/assets/charts.js`.

### Verdicts and what changed

- **Report hero (gauge).** r0: broken. The gauge drew at 145px inside its 360px column, so the 44px figure sat on top
  of a thumbnail arc and half the hero card was empty. Cause: `.rp-gauge { justify-items: center }` shrink-wrapped the
  figure to its widest child (the "Section #1" key), and the gauge svg has no width of its own (charts.js strips it).
  Now `stretch`: the dial is 360 wide at 1440 (figure 44px) and 326 at 390, the groove, band and needle read as an
  instrument in both themes. The `?fresh=1` sweep checked mid-flight (490 to 630 on its way to 520 to 660), the
  change chip lands after it, the mark fills beside it. Premium now.
- **Results hero (estimate and chart).** Good at r0 (56-64px figure, /800, change badge, New best once, the amber fade
  under the trend). Hover had three readouts at once: the hero figure swap, a dark tooltip saying the same, and a grey
  column 600px tall. Now one: the hero figure (its line also carries the right/asked detail, on the baseline where the
  badge was), the other bands dim, no tooltip (charts.js: a point the page shows itself via `onFocus` is `quiet`), no
  grey column (page CSS). Draw-in and the fade were already right.
- **Sitting rows (Results, and Today and Tests through `UI.sittingCard`).** r0: every Full section row printed a literal
  "null" as its subtitle (results-ui.js passed `null` to the native `append`, which prints it). Fixed. Peek's "Where
  the points went" read "Clock ≈ 35.4 pts" and lost the unlabelled segment: now the printed (rounded) points, and the
  key shows only the parts whose label does not fit in the bar.
- **Orange count.** Both pages carry their own orange primary (Practise the top 3 / Fix all open / a first test's Full
  section; Win back) and the shell's Up next Start was orange too (two or three oranges per first screen, three at
  390). Both pages now pass `UI.shell({ ownPrimary })` when their pill is on screen, so Up next's Start is the white
  `.btn` in the sidebar and the Now strip.
- **Right column card (both pages).** Calm, one raised card split by hairlines; no change.
- **Trends > Gap and Difficulty and format, the Report's Difficulty and Format.** Names wrapped to two lines in a 150px
  column and every track ended at a different x. The rows now share one grid (`subgrid`, max-content names), figures
  and Practise end on one edge (checked on all four tabs at 1440 and 390, `report-r4-*`, `results-r4-*`). Floor:
  subgrid needs Chrome 117, Safari 16, Firefox 71; below that a row stacks its label, track and figure.
- **Skills (Results).** At 1440 the main column is about 710px, so two columns left 124px per name: "Two-variable
  eq...", "Systems of equa...", six names cut. Two columns now only where 420px each fit (one column at 1440 and at
  1024, where the list is 836px); no name is cut.
- **Report Breakdown > Domain.** Four domains in 3 + 1 (Geometry alone on a row, the note glued under it): now 2 by 2
  (one column on a phone), the note 16px clear.
- **Question grid.** At 390 seven across left Q22 alone on a row in each module: now six across at 48px, rows of six
  ending on four. The amber "correct" fill is the shared status vocabulary (left, see asks).
- **Mistake rows (both pages).** At 390 the amber dot stayed at a line's end while "Open, 2 to close" wrapped below:
  the status no longer breaks, the dot travels with it.
- **Judgement.** "Ask how sure I am on my next test" stretched to half the card: it hugs its label.
- **Report a problem sheet.** Good structure; "21/200" and "0/5,000" counters under empty fields were noise: in this
  sheet a count shows from 90% (kit's `.near`) or past the limit. The recording pill enters with `nudge` again.
- **First test (fresh learner).** The hero with the dimmed example chart reads well. At 390 "One module · 35 min"
  wrapped onto its own row: the buttons are "Full section" and "One module", the minutes moved into the line under them
  ("A full section (70 min) is the most accurate. A module (35 min) is the quick way in.").
- Share sheet, skill drawer, menus (All sittings, Sort, the Win back split, More), focus ring on rows (amber-deep,
  inset), the pill press, dark mode on both pages: premium as they were.

### Lead's round 3 items (done)

- `UI.calendar` (charts.js): `nav: false` (no previous, next or Today), `legend: 'why'` (the key behind a "?" after the
  title; the summary stays in the data table), `tasks: false` (no done/of chip per day). Defaults unchanged; checked in
  the browser (default: 2 navs, 3 task chips, the key; with the options: none, none, the key in the why pop).
  `nav: false` hides the head's buttons only: PageUp / PageDown and T in the grid still change the month, so Plan
  should pass `min` / `max` (the same month) if the month must stay put.
- report.js `.rp-rec` enters with `'nudge'`; Results' read-only link Copy is `UI.copyText(url, { button, fail })`;
  `#sitfilt` (`.dd`) shows the shared drawn caret once.

### Band chart fixes from the Tests and Today reviewers (charts.js, every page)

- Sittings on one day printed the same date under each ("Sep 23 | Sep 23"): labels now go from the newest leftwards,
  a day's run is labelled once (under its newest), and a label never runs into the one to its right.
- A short chart (Tests' aside, 110px) stacked seven y labels 12px apart: without a page-set `grid`, the step doubles
  until labels are 18px apart (200 to 800 by 200 there; Results, which sets `grid: 200`, and the 160px+ charts are
  unchanged).
- The empty note ("Your first test puts a point here.") sat over the y scale: it centres on the drawing, clear of
  the scale, the ghost band and the x labels (`emptyNote(..., {l, b})`, band chart only).
- The key wrapped onto a second row in a 260 to 300px aside: shorter names ("Trend", "Estimate", "Added" for "Trend
  of the middles", "Current estimate", "A score you added"), and under 360px a key of three or more folds behind
  "Key" as Results' hero does. Shots `results-t1-tests-chart-*`, `results-t1-chart-empty-260`, `-five-260`.
- Today's "null" under Recent tests is the `UI.sittingCard` fix above (0 of 3 rows on Today now).
- The calendar's heavy today box is ui.css, not charts.js (charts.js only sets `data-today` and selects today by
  default, which Today's readout under the calendar relies on): see the shared ask.

### Not changed

- The chart's three identical "Sep 23 11:15" labels and the trend falling while the hero says "+60 / New best": every
  sitting in this fixture shares one timestamp. Real sittings differ; no change.
- A band chart keeps its minimum of six slots, so three sittings sit in the right half ("newest right" by design).

### Checks

`tools/check-ui.py` ok; `node --check` on the five JS files (the pages have no inline scripts); no em dash in the
seven files; smoke page.js on /results/ and /results/report/ at 1440 and 390 NO ERRORS (the Report is "not found" in
the fixture, as before), Today's five states, /tests/, /plan/, dev/kit NO ERRORS, /me/ its known fixture error;
inventory diff (a copy of web/ with the old labels vs now, both pages, both widths): only "Full section · 70 min" and
"One module · 35 min" became "Full section" and "One module".

### Shared asks

- ui.css `.chart-hit:hover` (ink 6% column): every band chart now dims the other sittings on hover, so the grey
  column says it twice. Drop it for `.band-chart .chart-hit:hover` (then results/index.html's
  `#overview .chart-hit:hover` rule can go).
- ui.css `[data-status="correct"]` (solid amber): on a Report the 31 correct cells of 44 are the loudest thing on the
  page, louder than the one primary. A lead call: correct as an amber wash (`--amber-200` fill, ink-deep glyph),
  incorrect stays ink, site-wide so the vocabulary stays one.
- ui.css `.ch-zone` in dark: 18% amber over near-black with a 45% edge reads as a brown slab; about 10% fill and a 30%
  edge would match the light weight.
- ui.css calendar today (the Today reviewer's "heavy 2px ink box"): today is also the default selection, so it wears
  `.cal-d[data-today] { box-shadow: 0 0 0 1.5px var(--ink) }` (2027) plus `.cal-d[aria-selected="true"] { outline: 2px
  solid var(--ink); outline-offset: 1px }` (2029), a double ink frame; the plan look has `inset 0 0 0 2px var(--ink)`
  (2067). Proposed: `.cal-d[data-today] { box-shadow: inset 0 0 0 1px var(--amber-deep) }`, the same at 2067, and the
  heat look's picked day on the one selected look as the plan look already does (`.cal-d[aria-selected="true"] {
  outline: 0; background: var(--sel-bg); box-shadow: var(--sel-edge) }`). Plan's own today chip
  (plan/index.html:162-164) is unaffected.
- kit.js `UI.counter`: consider showing the count from `.near` by default (report.js now hides it until then inside
  its sheet only).

### Round 5

The lead's read of the Results hero for `a:v2revresults01` ("500–590 /800 · +60 since Sep 23 · New best", the aside's
"Best 550–750", a trend line falling to the orange point): three claims about three different things.

- **What the numbers are** (server/estimate.py): the figure is `combined`, the last up to 3 full sections sat under
  test conditions (here the two sections, middles 500 and 590, so 500–590). `latest`, `previous` and `best` are
  sittings of any scored kind, sorted by finished then id, descending: latest the module (550–750, middle 650),
  previous a section (520–660, 590), best the module. `trend.delta` is latest middle minus previous middle (+60), a
  sitting against a sitting, never the estimate's own change; "New best" was the latest sitting being the best
  sitting. The chart plots every scored sitting with its trend through the middles; it ran oldest to newest from
  /history's order, which breaks a tie in `finished` the other way (all three sittings in this copy finished in the
  same second), so its orange "newest" was a different sitting from `latest` and the line fell.
- **One story now** (web/results/page.js, web/results/index.html): the figure stays the estimate, and its "?" says
  what it is ("From your last 2 full sections sat under test conditions. Modules, the diagnostic and added scores
  are on the chart, not in this band.", or for a range "The spread of your scored sittings so far..."). The old text
  ("Sections count double; sittings from the last 60 days") matched no code. One chip beside it is about the last
  sitting and says what it compares: "Last sitting +60 vs the one before" (soft and "−" when lower, none within 20),
  or once, when that sitting is the best yet, "Best sitting yet, +60 vs the one before" (it pops; remembered per
  sitting, and an old "New best" seen counts). The aside's row is "Best sitting". The chart sorts its points by
  finished then id, as estimate.py does, so its orange band is that last sitting and the line rises to it (550–750
  above the estimate zone, which the "?" explains). The hero takes the room left of All sittings, so a long chip
  wraps under the figure instead of pushing the control onto its own row.
- Shots: `results-r5-1440-first.png` (first view: Best sitting yet), `results-r5-1440.png` (seen), `-1440-dark`,
  `-390`, `results-r5-hover-1440.png`, `results-r5-why-1440.png`.

Also from the lead (charts.js): the calendar key behind `legend: 'why'` drew its swatches outside the figure, so the
plan look's swatch rules (`.cal.plan .cal-sw...`) no longer applied and Practice showed a filled dot beside hollow
rings on the grid. The key now renders inside a wrapper carrying the figure's look classes, so every swatch takes the
same style as the mark it explains (checked on /plan/ with `a:s790a6684c9aed61f5`: `results-r5-plan-key-0.png`,
`results-r5-plan-cal-0.png`). Results draws no calendar.

Checks: check-ui ok; node --check on the five JS files; no em dash; smoke NO ERRORS on /results/, /results/report/,
/plan/, /tests/, dev/kit at 1440 and 390 and Today's five states; inventory diff unchanged from round 4 (only the two
first-test labels).
