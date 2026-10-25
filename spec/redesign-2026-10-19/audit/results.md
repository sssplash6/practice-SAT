# Audit: Results and the score report

Scope: `web/results/index.html` + `page.js` (Results), `web/results/report/index.html` + `page.js` (Report),
`assets/results-ui.js` (sitting row, skill drawer, `UI.rx`), `assets/report.js` (Report a problem / Feedback
modal, every page), `assets/charts.js` (styling and density only). Code-level; numbers are computed from the CSS.

Geometry used below. 1440x900: sidebar 248, main 1192, `.page` max 1120 with 40px gutters, so content is
**1040px**; a card's inner width is 996 (22px pad). 390x844: gutter 16, content 358, card inner 326.

## What the student sees

**Results, 1440x900.** Now strip (Up next, ~50px), section chips (~52px), 27px top pad, `h1` "Results" with
Share + `⋯`, then a 12-col grid at 24px gaps: Estimate (span 4, 331px) beside Score over time (span 8, 685px).
Estimate is ~320px tall: kicker, "Math 520-600", chips, target track (66px of margin around an 8px bar),
Best / Target / Exam stats, a confidence button. The chart card is ~360px (kicker, Range + Kinds segs row,
200px plot, legend). The first screen ends at the top of Sittings. No `.pill` in it.
Below: Sittings (filters, In progress, week groups, 5 rows, Show 5 more), Totals (up to 8 `.stat` tiles, 2 rows),
Trends (one card, 5 tabs), Top misconceptions (up to 10 rows of ~80px), Every skill (~30 tiles of ~120px in
4 columns, about 1330px tall).

**Results, 390x844.** Same order, one column. Each sitting row stacks into four lines (~150px). Skills become
one 120px tile per row: about 3800px of skills. Compare bar floats above the tabs.

**Report, 1440x900.** Now strip, chips, then a header of four rows: "← Results", an uppercase mono eyebrow
("PRACTICE TEST · FULL MATH SECTION #3 · ADAPTIVE · FORM 2.1"), an `h1` that is only the date ("October 3,
2026 · 64 min · Timed"), then the actions. Title (flex 1 1 340px) plus split pill "Win back ≈ 60 pts · 7
questions · 12 min", Review mistakes, Retake as a test and `⋯` need ~1094px, so the actions wrap to their
own row. Then condition chips and "Add a note". The score card starts ~385px down; gauge (401px wide, ~345px
tall with key and caption) beside the facts. Recovery line at ~800px. Then 15 regions: Points, Compare,
Mistakes + Best value (8/4), Takeaways (3 cards), Tiles, Habits, Questions, Modules, Breakdown, Judgement,
Time, Up next. Folding never runs here (see I3).

**Report, 390x844.** Eyebrow wraps to 2 lines, actions wrap to 2 rows, gauge full width; the sticky
`.rp-stick` (Fix, Jump to, Review) replaces the chips once the hero scrolls away. Question grid 7x44px.

## A. Purpose and primary action

- Results answers "where do I stand" well (estimate first) but has no next action in the first screen.
  Its real primaries are buried: "Practise the top 3 · ≈ +40" sits in Trends > Gap (page.js:273, behind
  a tab, ~1300px down) and "Fix all open · n" in Top misconceptions (page.js:487). Header primary is Share.
- Report: the primary is right (Win back split pill, report/page.js:351-360) but it sits on the third
  header row and its label is ~40 characters. Two first steps compete when a second look is offered:
  "Start second look" (`.btn sm` in the recovery line, page.js:481) versus the header pill.
- Results empty state: two `.pill sm` side by side (page.js:187); one should be `.btn`.
- Report `#next` can show two pills (Pressure check and Start: topic, page.js:1552, 1562).

## B. Whitespace (concrete)

| Where | Now | Note |
|---|---|---|
| `.rs`, `.rp`, `.rp-hero`, `.rp-mist-wrap` gap | 24 (16 phone) | index.html:20, report:22/82/105; 12 per DIRECTION |
| `.rs-track` margin | 40 0 26 | index.html:110; 66px around an 8px bar |
| `.rs-stats` | margin-top 8 + padding-top 20 + rule | index.html:114 |
| `.rs-chips` margin-top | 16 | index.html:109 |
| `.rs-group > h3` margin | 18 0 10 | index.html:61 |
| `#skills .rs-dom-h` | margin-top 18 + 8 pad + rule | index.html:77 |
| `.rs-skill` | padding 14, gap 8, ~120px tall | index.html:70 |
| `.rs-trap` | 12px 0 per row, 3 text lines | index.html:63 |
| `.rs-list` gap / `.sc` pad | 10 / 8px 14px | index.html:60, results-ui.js:68 |
| inline margins | 10, 14, 18, 8 | page.js:188, 189, 273, 502 |
| `#trendtabs` + panel `.card-head` | 16 + 16 | index.html:83 |
| report `#head` | 4 rows at gap 12 | report:58 |
| `.rp-group` margin-top / `.rp-mrow` pad | 16 / 12px 14px | report:110, 112 |
| `.rp-card`, `.rp-mod`, `.rp-dom` pad | 16 | report:98, 161, 163 |
| `#next` padding-top | 24 | report:188 |
| `.rp-judge` gap | 16px 24px | report:185 |
| `.rp-big` | clamp(44, 7vw, 64) 800 | report:85 |

Every card also pays a kicker line above its title (`.card-head > .k` takes 100% width, ui.css:1124): about
22px per card, 7 cards on Results, 11 on the Report.

## C. Always-on, non-essential content

FOLD_SEL (ui.js:2792) on Results catches almost nothing: every `.rs-helper` string is under 70 characters
or inside a dialog (skipped), and the band chart only writes `.chart-note` when `projection === null`
(Results never passes it). On the Report nothing folds at all: `FOLD_OFF = /\/(print|report|help)\b/`
(ui.js:2795) matches `/results/report/`, so `.rp-helper` in FOLD_SEL is dead.

| Item | Where | Do |
|---|---|---|
| Kicker above every card title | page.js:47, report/page.js:82, 1460, 1546 | delete (title says it) |
| Panel kicker + h3 inside Trends, under a tab of the same name | page.js:265, 308, 322, 332, 347 | delete kicker, h3 to one line |
| Chart Range + Kinds segs (own 52px row) | charts.js:418-433 | move into the card head row |
| Chart legend (6-10 items) | charts.js:688-705 | fold behind "Key" |
| Gauge key (repeats the band and target) | charts.js:807-814 | drop band and target rows |
| Gauge caption "Math measured here..." | report/page.js:548 | ⓘ beside the band, as Results does |
| Totals (8 tiles) | page.js:277-299 | side column, key/value rows |
| Report tiles | report/page.js:760-803 | side column, key/value rows |
| Takeaways (3 cards) | report/page.js:738-757 | 3 one-line rows in the side column |
| Condition chips + note row | report/page.js:254-263 | one meta line under the h1; note edit in `⋯` |
| Sitting row Fix and Peek | results-ui.js:238-252 | `.reveal` (always on coarse) |
| Mistake row meta (6 bits) | report/page.js:897 | keep 3 visible, rest in the row tooltip |
| Modules card | report/page.js:1284-1300 | merge into the question grid group heads |
| "Misconceptions show once..." / "Every miss you make lands here..." | report/page.js:882, page.js:480 | `?` tooltip |

## D. Sidebar use

- Left nav: nothing page-specific belongs there; the Report maps to Results (ui.js:1430). Fine.
- Right column (`.split`, 1280+), Results: Estimate card (sticky), Totals as rows, Share / CSV / Print.
  Main keeps the chart, Sittings, Trends, Mistakes, Skills. Main width at 1440: 1112 - 300 - 12 = 800px.
- Right column, Report: score summary (band, delta chip, target line, percentile), the recovery steps as a
  4-row checklist (Second look, Fix, Check-ins, Prove it), the tiles as rows, takeaways, Best value, Up next.
  Main: Points, Mistakes, Questions, Breakdown, Judgement, Time. The gauge fits 268px (`.gauge-v` is cqw).
- Below 1280 the aside stacks first (summary is what the student came for), as today's order.

## E. Redundancy (page and shell)

- Shell Up next shows 3 times on the Report: Now strip, `.sections-next` when stuck, and `#next`'s
  `UI.nextItems()[0]` button (report/page.js:1566). Drop the `#next` copy.
- Streak tile (page.js:291) repeats the shell's streak; Exam stat (page.js:219) repeats the countdown;
  "Study time · this week" overlaps Today progress.
- Target on Results: track label, Target stat, chart line, chart legend. On the Report: gauge label, gauge
  key, facts line, Correct tile sub "need n for 650", Best value line. Keep one per view.
- Band on the Report: gauge centre, gauge key "This sitting", `gauge-s` "Math · middle 560". The user's own
  rule is "one number said twice" (report/page.js:19).
- Time away and pauses: header chips (page.js:258-259) and Judgement (page.js:1415-1416), same words.
- Module 1 result: hero facts (page.js:585), Ledger route line (696), Modules card, grid group head.
- Takeaway actions duplicate Pace's Careful set and Judgement's changed chip (page.js:751-752).
- Results: "Mistakes · n open" tile, "Fix all open · n", and the Mistakes chip; Tests tile vs Sittings seg counts.
- Sitting row: the title link and the Review button go to the same URL (results-ui.js:180, 238).

## F. Local overrides, colours, sizes, inline styles

- Hard-coded shades, light theme only: report/index.html:142-145 (#F4EFE8, #DDD3C6, #A89A88, #5B5046,
  #fff) and the legend swatches inline in page.js:1120. Dark theme shows pale cells. Use tokens.
- 999px: `.rp-chip` (report:29, buttons: qchips, pace chips, changes chip); `.rp-rec` (report.js:147).
- Uppercase letter-spaced: `.rs-group > h3` (index:61), `.rs-dom-h` week heads (index:75), `.rp-group > h3`
  (report:111), `.rp-judge h3, .rp-sub` (report:187), `.skp h3` (results-ui.js:133), `.rp-file .th`
  (report.js:129), plus shared `.k` and `.stat-k`.
- Mono for words: `.sc-when` "Today" (results-ui.js:82), `.sc-peek-strips p` (114), `.rs-dt` body
  (index:56), `.rp-steps-key` "under 0:30" (report:148), `.rp-box` context lines (report.js:108), all `.meta`.
- Off-scale sizes: Results 11, 11.5, 12, 13, 13.5, 15, 16, 17, clamp(30-38) 800; Report 8, 8.5, 10.5, 11,
  13, 13.5, 15, 15.5, 18, 28, clamp(22-30) 800, clamp(44-64) 800; results-ui 8, 9, 10, 15.5.
- Inline styles: page.js:183/195 (gridColumn), 188, 189, 273, 502; report/page.js:941, 1120;
  results-ui.js:296.
- Copies of one component: `.rs-info`/`.rp-info`, `.rs-strip`/`.rp-strip`/`.rp-status`, `.rs-bar(s)`/`.rp-bar(s)`
  (identical 150px | 1fr | auto rows), `.rs-row`/`.rp-row`, `.rs-line`/`.rp-line`, `.rs-helper`/`.rp-helper`.
- `.rp-chip` re-invents kit chips; `.rp-split` cuts `.pill` corners (report:67-69).
- Filled boxes inside a card: `.rs-skill`, `.rp-card`, `.rp-mod`, `.rp-dom` (tile-2), `.rp-mrow` (paper).

## G. AI-slop tells

- A kicker over every title, and formula titles: "Every sitting", "Every skill", "Every question", "Every
  miss, named"; cute subtitles: "Cheapest points first", "Where the minutes went", "How you decided", "What to
  do about this sitting", "The same slip in more than one place", "Where the points leak, all time".
- Takeaways: three equal tile-2 cards in a row (report:97).
- Decorative orange tick before domain heads (index:78); ⓘ glyph buttons; "→" in labels ("All mistakes →",
  "A full section → Medium"); `·` chains of 3-4 facts in one button label.

## H. Copy

- Report h1 is a date. Make the h1 the sitting ("Full section #3"), the date, minutes, timing and form a
  meta line. Eyebrow goes.
- "A full section → Medium · 70 min" (page.js:222): "Sit a full section for a firmer estimate · 70 min".
- "Win back ≈ 60 pts · 7 questions · 12 min": keep "Win back ≈ 60 pts"; the count and minutes to `title`.
- Sections chip "Mistakes" vs card "Top misconceptions / The mistakes you make most": one name, "Mistakes".
- Em dash as an empty value: results-ui.js:380, charts.js:175, 224, 839, report.js:229. Use "none" or "-".
- "Open the sample report", "Shared progress · read-only": fine. "Practice only: Untimed": fine.

## I. CSS and layout bugs

1. **report.js styles break the Report header.** `UI.report` lazy-loads report.js (ui.js:2376) and appends
   its `<style>` after the page's, so `.rp-acts { display: grid; justify-items: start }` (report.js:144)
   beats report/index.html:66: after any Feedback or "Report a problem" the header actions stack in a
   column. `.rp-row` gap also changes (report.js:136). And the page's `.rp { gap: 24px }` (report:22) hits
   the modal (`dialog.sheet.rp`, report.js:432): 24px between its head, body and foot on this page only.
2. `.sc-side` is declared twice (results-ui.js:76 grid, 104 flex). Flex wins, the 78/66/34 columns are dead,
   so Review / Fix / Peek and the score cell shift per row (rows without Fix are offset).
3. FOLD_OFF matches `/results/report/`; `.rp-helper` in FOLD_SEL never folds. Decide which is intended.
4. "Math 520-600" (`.rs-big`, nowrap, index:42) plus the ⓘ needs ~290px at 38px; the span-4 card gives 286
   at 1440 and ~197 at 1100 (font 32): it likely overflows the card from 1100 to ~1440.
5. `#sittings .rs-headr` is `nowrap` from 760px (index:41): seg (4 options + counts) + kind select + "Has open
   mistakes" + sort select is ~810px; at 760-1280 the card inner is ~690-730, so it overflows when Tests is
   picked.
6. `.rp-cells .cell[data-saver]::before` (report:135) replaces `.cell[data-flag]::before`: a flagged
   route-saver cell loses its flag corner.
7. `.rs-dt td[data-s] { border-radius: 6px }` (index:58) does nothing under `border-collapse: collapse`.
8. `.rp-table table { min-width: 1180px }` (report:152): always scrolls sideways at 996px inner.
9. `.sc-chip[data-status="blank"]` sets `box-shadow` twice (results-ui.js:94). Harmless, tidy.
10. charts.js:131 comment still sizes labels for DM Mono; Geist Mono is close (0.6em), fine, fix the comment.

## Redesign proposals (ranked)

1. **Fix I1 (collision), no rename.** Scope every report.js rule under `dialog.sheet.rp` (report.js:100-145;
   leave `.rp-rec`, it lives on body), and scope the page grid as `#root.rp` (report:22-24, 208, 234).
   Risk: low. Small diff, real bug on every Report visit that opens Feedback.
2. **Fix I2.** Delete the flex `.sc-side` (results-ui.js:104) or the grid one; with Fix and Peek moving to
   `.reveal`, keep the grid so columns line up. `.sc` is also used by Today (index.html:2936). Risk: low.
3. **Kickers out, one title per card** (both `head()` helpers, page.js:47 and report/page.js:82; Breakdown
   1460; `#next` 1546). Card titles become the short noun: Score over time, Sittings, Totals, Trends,
   Mistakes, Skills; Report: Points, Mistakes, Best value, Questions, Breakdown, Judgement, Time. Trends
   panels keep only their sentence as a 14.5/600 line. Risk: low; tour titles (tour.js:62-68) still match.
4. **Results header gets the primary** (page.js:108-118): `.pill` "Practise the top 3 · ≈ +40" when
   `ST.gap.top3` exists, else "Fix all open · n" when traps are open, else none. Share becomes `.btn`.
   The Gap panel's own pill (page.js:273) goes (same action). Read-only: unchanged. Risk: low.
5. **BIG: Results right column.** `.split` with `aside`: Estimate (sticky), Totals as a key/value list
   (Questions, Accuracy, Study time, Tests, Streak, Mistakes, Types met, Recovered: 8 x 32px rows, links
   kept), Share / CSV / Print. Main: chart (now 800px wide), Sittings, Trends, Mistakes, Skills. `#estimate`
   and `#overview` stop sharing a row (index:23-24 go). Below 1280: Estimate, Totals, then main, as today.
   Ids stay (tour.js, section chips). Risk: medium (needs the lead's `.split`).
6. **BIG: Report header and side column.** Header: back link, `h1` = sitting name, one meta line (date ·
   min · timing · form · condition chips · note), actions on the same row as the h1 at 1280+. Side column:
   score summary, recovery checklist (moves `#recovery`, page.js:468-497), tiles as rows (page.js:760-803),
   takeaways as rows, Best value (page.js:916-952), Up next minus the shell item. The gauge keeps its What
   if layer (`gaugeApi.set`) in the aside, visible while the grid scrolls: a gain, What if is used from the
   grid. Risk: medium-high (print pack clones `#hero`, `#ledger`, `#value` by id, page.js:1702; keep ids).
7. **Skills as rows** (page.js:518-541, index:69-79): `button.rs-skill` becomes a 40px row: glyph, name,
   72px mastery bar + word, "n · 72%", open badge; 2 columns from 1100px, 1 on a phone (44px rows).
   Domain heads 14.5/600 with a hairline, no orange tick. Height ~1330 to ~770px desktop, ~3800 to ~1450
   phone. Same button, same `UI.skillPanel`. Risk: low.
8. **Sittings rows tighter** (results-ui.js:68-104): hairline rows (no tile fill), 44-52px, `.sc-when` in
   Geist, Fix + Peek behind `.reveal` (Review button can go: the title is the same link; keep it on coarse
   pointers if wanted). Week heads (page.js:450) sentence case 12.5/500. Shared with Today and Tests: check
   both. Risk: medium.
9. **Mistakes rows** (Results page.js:494-499, Report 892-913, index:63, report:110-124): 44px rows, label +
   one meta line, status as dot + short text, Fix / menu on `.reveal`. Report rows lose the paper fill
   (hairlines instead). Group heads sentence case. Results shows 5, "Show all 10" expands. Risk: low.
10. **Merge the Report's Modules card into the question grid** (page.js:1284-1300 into 1150): group head
    becomes "Module 2 · harder · 31/44 · 70% · 31:20 of 35:00 · 2 flagged". The strips there duplicate the
    grid (same `openPlayer`). Drop `modules` from jumpList. **BIG** (a card goes). Risk: low.
11. **Habits into Mistakes** as a "Habits" group with the same Drill buttons (page.js:806-824 into 841).
    **BIG.** Risk: low.
12. **Dedupe** (E): drop `#next`'s `nextItems()` button (page.js:1566-1567); drop the gauge key's band and
    target rows (charts.js:808, 813; keep previous / second look / what if / today); drop away and pause
    lines from Judgement (page.js:1415-1416; header keeps them); drop the Exam stat (page.js:219) and the
    Streak tile (page.js:291) once the shell Now block shows them at 700px+ and on the phone menu.
13. **Dark-safe shades** (report:142-145, page.js:1120): `--sh-0..3` from `color-mix` on `--ink` and
    `--paper` (as `.sb-warm` does, ui.css:1845-1853); legend swatches use the same vars. Risk: low.
14. **Chart density** (charts.js:418-433, 688-705): an option to render `chart-ctl` into a given host (the
    card head) and a folded legend ("Key"). Saves ~60px per band chart; affects Today and Plan too (opt-in).
15. **Breakdown**: one seg row only; move Domains' "By points / SAT order" into a small sort select beside
    it (page.js:1309-1311); `.rp-dom` tiles to rows of 4 columns without fills (report:162-165). Risk: low.
16. **Copy and slop** (H, G): em dash placeholders, ⓘ to `?` per DIRECTION, "→" out of labels, cute
    subtitles out, h1 fix. Risk: none.
17. **Sizes to the scale**: `.rs-big`, `.rp-big`, `.rp-title h1` to figure 32 / page 22; `.rp-dom .v` 28 to
    figure; 8 / 8.5 / 9 / 10 / 10.5 to micro 11.5 (cell corner labels may stay 9 inside 40px cells).
18. **Fix I4-I8.** `.rs-big` drops `nowrap` and the ⓘ wraps (or figure 32 solves it); `#sittings .rs-headr`
    wraps above the seg (index:41); saver uses `::after` on `.n` or a data attr not on `::before`;
    `.rp-table` `min-width: 100%`, sticky first 2 columns already handle overflow.

## Shared asks (lead)

- `.k`, `.stat-k`: sentence case Geist 12 (DIRECTION). `.meta` is mono (ui.css:767): words in every meta
  line render mono; make it Geist with `tabular-nums`.
- Decide FOLD_OFF vs `.rp-helper` (I3). If the Report should fold, narrow FOLD_OFF to `/print|/help`.
- `.split` + `.reveal` primitives (proposals 5, 6, 8, 9).
- One shared info button (`.rs-info`/`.rp-info`) and one note strip (`.rs-strip`/`.rp-strip`/`.rp-status`);
  until then results-ui.js (loaded by both pages) can hold the shared copies without renames.
- `.card-head > h3` is styled as an h2 (ui.css:1123): nested heads in Trends read as two equal titles.
- charts.js and report.js are used site-wide: proposals 1, 12 (gauge key), 14 touch every page using them.
