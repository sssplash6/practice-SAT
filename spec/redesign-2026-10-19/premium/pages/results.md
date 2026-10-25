# Premium audit: Results and the score Report

Files: `web/results/index.html`, `web/results/page.js`, `web/results/report/index.html`, `web/results/report/page.js`,
`web/assets/results-ui.js`, `charts.js`, `report.js`. Code-level only. "page.js" alone is Results; "report" is the
Report's page.js; "index.html" is Results' page, "report.html" the Report's.
Geometry from CSS: border-box (ui.css:242), `.page` 1120 max with 40px gutters, sidebar 248 from 1100px, `.twocol`
main 728 + 12 + aside 300 from 1280px (ui.css:324-335), card pad 16.
Marks: (D3/D6/D7) = crosses DIRECTION section 3, 6 or 7; the brief opens it, the lead decides.

## 1. First screen inventory

**Results 1440x900** (student with scored sittings), top to bottom: section bar, 5 chips (page.js:116); "Results" +
pill "Practise the top 3 · ≈ +40" (page.js:127); hero card: "Math estimate ?", 44px band, "/800", delta badge
(page.js:245-255), Range seg 3 + Kinds seg 2-4 top right (charts.js:428-435), 200px chart, "Key" fold; Sittings
head: h2 + seg 4 + kind select (Tests only) + "Has open mistakes" chip + sort select (page.js:437-458), two rows at
696px inner width; a week head; about 3 rows. Aside, one surface, fully visible (~680px): Estimate (4 kv rows, `?`,
quiet "Sit a full section..."), Totals (8 rows), Share + `⋯`.
- Buttons ~19 visible (pill 1, `?` 2, Range 3, Kinds 3, Key 1, Sittings seg 4, chip 1, quiet 1, Share 1, `⋯` 1),
  plus Fix + Peek on every row on hover. Links 11 (5 chips, ~4 sitting titles, 2 kv links). Inputs 1-2 selects.
  Chips/badges 1 delta + 7 seg counts. Boxes 3 surfaces. Bars: 1 chart, 1 target track. Labels ~14. Helper lines 0.
- Control rows before content: (1) section chips, (2) h1 + pill, (3) Range + Kinds in the hero head; Sittings adds
  (4)-(5) seg + chip + selects before its first row.

**Results 390x844**: top bar 56, Now strip (title, Start, `⋯`), chips scrolling sideways (5), h1 + pill (fits one
row), hero: label + `?`, 44px figure, delta badge on its own line, Range + Kinds full width (index.html:126-128),
160px chart, Key. Estimate facts start at the fold. Buttons ~15, links 5, badges 1, boxes 1.5, bars 1.
Control rows before the chart: 5 (Now strip, chips, header, hero label, Range/Kinds).

**Report 1440x900** (fresh full section, 7 misses): 7 chips (report:463-466); "← Results" (+ "← Back to your plan");
h1 "Full section #3" + split pill (2 buttons) + Review mistakes + Retake as a test + `⋯` (report:338-390); meta line
(date, minutes, Timed, Adaptive, Form, badge, note). Main 728: Points ("≈ 60 pts below all right...", `?`, seg 2,
stack bar, route line with 1-3 qchips + helper, report:689-707); Mistakes head (fig, meta, Reviewed, sort select),
~4 rows. Aside 300: gauge in ~260px so the figure clamps to 34px (ui.css:1678), key, caption fold, facts (delta
badge, "3 questions from your target" + 3 qchips, percentile + `?`, Module 1 line, Details), Recovery (4 steps,
Start second look, Show answers now, Check-ins link).
- Buttons ~21 visible (split 2, Review, Retake, `⋯`, `?` 3, seg 2, qchips ~5, Details, caption fold, 2 Recovery),
  6 row titles that are buttons, 6 row `⋯` on hover, 5 invisible stack hits. Links 9-10. Inputs 1. Badges 1-2.
  Boxes 3 surfaces. Bars: stack bar + gauge. Helper lines 2-3 (route helper, gauge caption, held-answers line).
- Rows before content: (1) 7 chips, (2) back link, (3) h1 + 5 actions, (4) meta. The score is not in main at all:
  main opens on a loss ("≈ 60 pts below"), the score is a 300px widget beside it (report.html:270-271).

**Report 390x844**: no chips (report.html:217); Now strip, back, h1, actions wrap to 2 rows, meta wraps to 2 lines,
then the gauge (~326px, figure ~42px) at about y 330; facts reach the fold. Rows before the score: 5. The sticky
strip (Fix pill, Jump select, Review) appears once the hero leaves (report:447-461).
Before the fold: buttons ~12 (Now strip Start + `⋯`, split 2, Review, Retake, `⋯`, caption fold, 3 target qchips, `?`),
links 1-2 (back), badges 1-2 (delta, "Practice only"), inputs 0, boxes 1 hero card, bars 1 gauge, labels ~7 (meta bits,
gauge sub, ticks), helper lines 1-2 (meta wraps, folded caption).

## 2. Clutter fixes

Results
- Range + Kinds: one `.btn.sm` "All sittings ⌄" (label = current range and kinds) opening `UI.menu` with Range radios
  and Kinds checks, the pattern of the Report's View menu (report:1039-1044). 5-7 buttons become 1.
- Sittings head: keep the 4-way seg; kind select, "Has open mistakes" and sort go into one "Sort and filter · n"
  menu button (n = active filters). Phone: seg + that button, one row.
- Totals: 4 rows (Questions, Accuracy, Study time, Tests) + a "4 more" `details.fold` (Streak, Mistakes, Types met,
  Recovered), the fold look charts.js:710 already uses.
- Section chips: hidden until the bar sticks (shared ask: `UI.shell({sections, defer: true})`, ui.js:2262-2292 already
  tracks `.stuck`). On a 5-card page they repeat the card titles above the title.
- Space: header to hero 12 → 24; hero card padding 16 → 24; everything else keeps 12.
- Calm first screen: "Results" + pill; 24px; the hero card alone in the eye line: label + `?` left, one menu button
  right, the figure, the chart; Sittings below with one control row; aside: Estimate 4 rows, Totals 4 rows, Share.

Report
- Header: "Results / Full section #3" as one breadcrumb line (the back link in `--soft` before a slash), then split
  pill + Review mistakes + `⋯`; Retake as a test moves to the top of `⋯` (its tooltip text as the item meta). Phone:
  split + `⋯`, Review mistakes first in `⋯` (it is also in the sticky strip and the Mistakes card). One action row.
- 7 chips deferred until stuck (same shared ask).
- Questions tools (report:997-1061): 3 rows (Show chips 5; Filters, Focus, View, Reset; legend) become 1: Show as a
  5-way `.seg` left, "Filters · n" (Focus joins the sheet as its first group) and "View ⌄" right, Reset inside the
  sheet, legend under the grid at meta size.
- Mistakes head: "Reviewed 3 of 7" joins the meta string; the sort select becomes a "Sort ⌄" menu button.
- Gauge caption: a `?` beside "Math · middle 580" instead of a folding caption under the dial.
- Calm first screen: breadcrumb + 3 actions; meta; 24px; the score hero across main; Points under it; aside opens on
  Recovery.

## 3. Depth and hero

- The hero of both pages is the score. On the Report it moves to the top of main at 1280+: `#hero` leaves `#side`,
  `.rp-hero` takes its 760-1279 two-column grid (report.html:89) as `340px 1fr`; the figure reaches 44 at a 344px
  container (12.8cqw, ui.css:1678), so the gauge column is 344 or the factor rises to 13cqw. The aside starts at
  Recovery. Size M, no loss: the order rules for <1280 stay.
- Hero surface, one recipe for the Results overview card and the Report hero only (`.card.hero`, shared ask): paper,
  not tile; `radial-gradient(120% 90% at 15% 0%, color-mix(in srgb, var(--wash) 70%, var(--paper)), var(--paper) 60%)`;
  hairline kept; warm layered shadow `0 1px 2px rgb(63 48 25 / .06), 0 14px 32px -18px rgb(63 48 25 / .22)`;
  inner top highlight `inset 0 1px 0 rgb(255 255 255 / .7)`. Dark: tint at 10%, shadow black 50%. (D3/D6)
- Gauge as an instrument (charts.js:735-863): `.g-track` is a 2px line (ui.css:1683) under a 16px band, so the band
  floats on a hairline. Make the track a 16px groove in `--track` with a 1px `--line` inner edge, round ends; the band
  a `linearGradient` along the arc (amber to amber-deep at its high end); the mid tick a graphite needle with a 2px
  `--surface` halo; the previous band stays a mat ghost inside the groove; figure `tabular-nums` so it never jitters.
- Results chart depth: area fill under `.ch-trend` (amber 14% to 0, vertical; D6 allows chart fills); `.ch-zone`
  (flat 18%, ui.css:1620) gets 1px amber 40% edges at its low and high so it reads as a band; the newest mid
  (`.ch-mid.now`, ui.css:1634) gets a 7px amber 20% halo: the one lit point.
- No elevation anywhere else: Sittings, Trends, Mistakes, Skills, Points and the aside stay flat tiles with hairlines.
  Floating things keep `--shadow-float` (Compare bar index.html:121, menus, tips).

## 4. Buttons, controls, highlights

- `.pill` (header primary; ui.css:855-875): amber, hover 8% darker, press .97, busy = opacity .6. Should: inner top
  highlight + amber-tinted drop `0 6px 14px -8px rgb(217 119 5 / .55)`; hover lifts 1px and the shadow grows; press
  drops to 0 and .97 (120ms); busy keeps the label and a 2px bar fills along the bottom edge to 90% over 1.2s and holds (no
  loop, ui.css rule 10); success is the navigation itself. Shared.
- Split pill (`.rp-split`, report.html:77-79): two pills with a 1px gap and a unicode `⌄`. Should: one shape, a 1px
  `--ink-deep` 15% divider, a 16px chevron icon that turns 180 when its menu is open (`aria-expanded`).
- `.btn` (Review mistakes, Share; ui.css:880-905): hover 7% darker. Add a 1px top inset highlight for a pressed-key
  feel; press .97 exists. `.quiet` underline hover is right.
- Segs (Range, By cause, Breakdown, Show): selected = wash-2 + amber ring per button. Should: one sliding thumb
  under the options (transform, 200ms `--ease`), the label weight change only. Shared (`UI.seg`).
- Sitting rows `.sc` (results-ui.js:88-91): no hover at all (skills and mistake rows have one: index.html:109,
  report.html:129). Add `--well` row fill + title underline on hover; selected keeps wash + ring.
- `.rp-chip` qchips (report.html:52-54): no hover, no press. Add `--mat` on hover, .97 on press, focus ring.
- Chart hits (ui.css:1600-1607): hover is a 6% ink column and a tooltip after 60ms (charts.js:263). Should drive the
  readout (5.3) and a 1px guide line; focus shows the same readout.
- Loading: static `.skel` (ui.css:1232) then a hard `replaceChildren`. Fade content in 160ms over the skeleton's
  footprint; no shimmer. Saves (note, R&W, report:282, 626) toast "Saved": an inline check that draws in 240ms.

## 5. Motion moments

Exists: gauge sweep 1200ms on `?fresh=1` only (charts.js:847-861, report:555); `[data-animate]` (report:557) has no
CSS anywhere, so it is inert; `.scale-band.grow` 600ms; `UI.roll` 220ms on the What if band (report:1309), the
Questions count (report:1115) and "Showing n" (page.js:498); `.reveal` 160ms; tips fade 120ms. Every new item below:
first paint only, never on a `sized()` width redraw (charts.js:236-248), off under `still()`.
1. Hand-in arrival (FRESH; test.js:697 lands here) (D7): hero surface rises 8px + fades 240ms; groove draws, band
   sweeps 900ms from the previous band (else from 200) with the figure rolling in tabular digits; on landing the
   delta chip rises 4px in 160ms and the target line appears; band over target = target tick pulses once (1 to 1.4
   to 1, 400ms) and the line says "Target reached"; then cards stagger 40ms each, 6 at most. Under 1.6s; any scroll,
   click or key finishes it at once.
2. Results chart draw-in when first seen (IntersectionObserver) (D7): gridlines fade 160ms, bands rise from their low
   end (scaleY, 30ms stagger, 320ms), the trend draws by `stroke-dashoffset` 600ms, the newest mid pops last
   (.6 to 1, 200ms).
3. Hover readout: bandChart passes `onFocus` to `hitLayer` (charts.js:251-268; it does not today) and the hero figure
   shows the hovered sitting's band, kind and date in place via `UI.roll`, back on leave; a 1px guide; other bands
   dim to 55% (150ms). Same idea as the heatmap readout (charts.js:1488-1506), no new widget.
4. Stack bars (Points, Why you miss; charts.js:1811-1816): grow left to right once (scaleX, 40ms stagger, 400ms);
   hover dims siblings to 60%; a picked segment keeps a 2px ink underline while the grid filter is on.
5. Last 14 days bars rise from the baseline once, 20ms stagger.
6. Range or Kinds change: bands slide to their new x (FLIP on transform, 240ms) instead of a cut redraw.
7. Trends tabs and Breakdown seg: panel crossfade 160ms with a 4px slide toward the chosen tab.
8. Peek: opens via grid rows 0fr to 1fr 200ms; its chevron rotate (results-ui.js:126) gets a transition.
9. Show 5 more sittings: new rows rise 6px + fade 160ms, 30ms stagger; the count rolls (exists).
10. What if: a flipped cell turns over (rotateY, 200ms); the dashed band glides from the last answer using the
    gauge's own interpolation (`paint`, charts.js:841-846), not a jump.

## 6. Icons and imagery

- Unicode stand-ins: `⋯` (page.js:134; report:387, 915), `⌄` (report:361), `←` (report:248), `↑ ↓` in the delta
  (page.js:254), `▲ ▼` (page.js:404, results-ui.js:217), `✓ ✕` (results-ui.js:114, 235, 422; report:484, 903),
  `⚑ ✎ ↺` table heads (report:1233-1235), `▲` route saver (report:1190), `→` (report:440), `×` (page.js:539).
- kit `ICON` (kit.js:180) and ui.js `ICON` (ui.js:438) have check, x, chev, arrow, filter, copy, clock, trophy.
  Missing: more, chevron-down, arrow-left, trend-up, trend-down, flag, note, changed, share, download, print. Shared
  ask: those 11 at the same stroke and grid; then swap every glyph above (status glyphs in cells stay, they are marks).
- Kinds options carry no swatch: put each band's `keySwatch` (charts.js:301) inside its option, so the filter shows
  what it hides and the Key fold is needed less.
- Empty states: "Sit your first test" (page.js:207-219) is text and buttons: add a faint line-art gauge (the real
  `UI.gauge` with no band, 140px, dotted "your band lands here"). "Every question right." (report:850): a check
  medallion (amber ring, check icon) over the line. "No sittings match." (page.js:474): filter icon + Reset.

## 7. Delight and feedback

- Target reached at hand-in: the tick pulse and an amber-filled "Target reached" badge (orange = progress).
- New best: when the band beats `E.best` (page.js:236) or the previous best, a small "New best" badge beside the
  figure on both pages, once per sitting.
- Delta chip with direction: up = wash with trend-up icon, down = soft with trend-down, none = "Held" (page.js:254,
  report:563).
- Recovery: a step that completes on `refresh()` (report:129-131) draws its check (dashoffset 240ms).
- A mistake that turns fixed on refresh: the strike-through (report.html:136) draws across in 200ms.
- Compare bar (`#cmpbar`, page.js:502-513) slides up 200ms instead of appearing; Clear slides it down 150ms.
- Share PDF: the language row shows "Making the PDF", then a check and "Downloaded" in place (page.js:157-161).
- Report a problem (report.js): the sent state (report.js:716-729) is a paragraph; lead it with a drawn check and
  "Report #n is in" at section size, links under it. The recording pill (report.js:146) slides up 200ms.

## 8. Ranked top 10

1. Report score hero leads main at 1280+ (gauge 344, figure 44), aside opens on Recovery: the test-score moment is
   the page's focal point, not a sidebar widget. M, slop low.
2. Hand-in arrival sequence (rise, groove + sweep with rolling figure, delta and target landing, stagger,
   skippable): one earned celebration. M, slop med (D7).
3. Gauge as an instrument: 16px groove, gradient band, needle with halo, tabular figure. S, slop low.
4. `.card.hero` surface (warm radial tint, hairline, layered warm shadow, top highlight) on the two heroes only: one
   lifted thing per page. S, slop med (D3/D6).
5. bandChart hover readout in the hero figure + guide line + dimmed siblings, via `hitLayer` onFocus: number and
   chart become one instrument. M, slop low.
6. Questions tools from 3 rows to 1 (Show seg, Filters · n with Focus, View ⌄): the grid is the content. M, slop low.
7. Results control merges: Range + Kinds into "All sittings ⌄", Sittings filters into "Sort and filter · n",
   Totals 4 + fold, chips deferred until stuck: about 10 fewer controls on the first screen. S, slop low.
8. Data draws in once per view (bands rise, trend draws, newest pops; stack and day bars grow), never on resize:
   data arriving reads as data. M, slop med (D7).
9. Tactile controls: pill highlight + tinted shadow + 1px lift, one-shape split pill with a chevron icon, `.sc` row
   hover, `.rp-chip` hover and press, sliding seg thumb. M (shared), slop low.
10. Icon set for the 11 missing marks plus the directional delta chip, and the one-row Report header (breadcrumb,
    Retake into `⋯`): polished marks and a calmer header. S, slop low.
