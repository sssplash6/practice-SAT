# Score range inventory (satbank, read-only pass 2026-10-22)

Scale key: S = section 200-800, T = total 400-1600. C/D/X = computed / displayed / copy text.
"r10" = each end rounded to 10 separately. "clamp" = max(200)/min(800) unless stated.
All R&W sittings go through the same scoring.score/section_score (label "Math" hardcoded), so every section constant applies to R&W too.

## 0. Root constants and functions (change these first)

| Root | Where | Current | Feeds |
|---|---|---|---|
| `HALF_BAND = 100` | server/scoring.py:61 | 200 wide | diagnostic, single module, custom, drill-scored sittings at finish (scoring.score:377-378); estimate._half for non-section kinds (estimate.py:274-275) -> all rescore/ledger/whatif/path/flip/recovery/second-look bands for those kinds |
| `MOCK_HALF_BAND = 70` | server/scoring.py:87 | 140 wide | mock + Season Final at finish (section_score:101-102); estimate._half for kinds mock/section/paper; api_tests._up_to:2130 |
| `scoring.section_score` | server/scoring.py:95-108 | centre +/-70, r10, clamp, lower route caps high=580 and `low=min(low, high-10)` | stored `result.estimate` for two-module sittings |
| `scoring.score` band | server/scoring.py:375-386 | centre +/-100, r10, clamp | stored `result.estimate` for all other kinds (overwritten by section_score for mocks/finals) |
| `estimate.mid()` | server/estimate.py:240-249 | duplicate of the two above, unrounded floats, same 580 cap and `min(low, high-10)` | rescore, ledger, whatif, path, flip_easy, recovery.now, second.with, pass2 pts, levers, rescore_sitting |
| `estimate._printed` | server/estimate.py:288-291 | r10 of mid() low/high | rescore() output |
| `estimate.estimate().combined` | server/estimate.py:150-155 | literal `70 / sqrt(n)` (n=2 -> ~100 wide, n=3 -> ~80), r10, clamp; NOT tied to MOCK_HALF_BAND | Results hero, PDF hero |
| `estimate.estimate().range` | server/estimate.py:174-175 | min/max of sitting MIDPOINTS, not a band; width = data spread (0 with one sitting, can be 300+) | Results hero fallback, PDF hero fallback |
| `estimate.project` half | server/estimate.py:683 | `max(60, min(150, _round10(half_latest + err)))` -> 120 to 300 wide, floor 60 | U9 projection everywhere |
| `api_today.early_projection` half | server/api_today.py:1262 | duplicate clamp `max(60, min(150, _round10(half_latest)))` | Today projection when U9 has <3 sittings, calibration |
| `api_results route_rule.half_band` | server/api_results.py:777 | literal `70 if kind in SECTIONS else 100` (duplicate, unused by web) | report payload only |
| client ±35 | web/plan/plan.js:494 | mean-35..mean+35 (70 wide) | plan Score tile track |
| client ±30 | web/index.html:2149 | p.current-30..+30 (60 wide) | Today scale for self-entered score |

Widths come out exactly 2*half only when half is a multiple of 10 (each end r10). Clamps at 200/800 shrink the band near the edges (e.g. HALF 100 all-right centre 780 -> 680-800; mock 710-800). Lower-route cap can collapse a mock band to 10 wide (centre >= 650 on lower route -> low=min(low,570), high=580 -> 570-580).

## 1. Server: where a band is COMPUTED

| file:line | kind | name | width now | scale | source of width | clamp / round |
|---|---|---|---|---|---|---|
| server/scoring.py:16-20 | X (docstring) | module doc | "narrower than 200 points would be pretending" | S | rationale for HALF_BAND | - |
| server/scoring.py:59 | C | ANCHORS | top anchor 780, bottom 200 | S | curve, caps centre at 780 | - |
| server/scoring.py:61 | C | HALF_BAND | 100 -> 200 wide | S | constant | - |
| server/scoring.py:82 | C | LOWER_ROUTE_CEILING | 580 cap on high | S | constant | - |
| server/scoring.py:84-87 | C + X comment | MOCK_HALF_BAND | 70 -> 140 wide | S | constant | - |
| server/scoring.py:101-102 | C | section_score low/high | 140 | S | MOCK_HALF_BAND | clamp 200/800, r10 |
| server/scoring.py:104-107 | C | section_score cap | high=580, low=min(low,570) | S | LOWER_ROUTE_CEILING | width shrinks, can be 10 |
| server/scoring.py:340 | X | score() docstring "one wide band" | - | S | - | - |
| server/scoring.py:376-378 | C | score() low/high | 200 | S | HALF_BAND | clamp, r10 |
| server/scoring.py:386 | C | score() `estimate` dict | {low,high,section,scale:[200,800]} | S | above | - |
| server/api_tests.py:1336,1369-1374 | C | _final: score() then section_score() if mock or two_modules (Season Final, kind module) else score() band | 140 or 200 | S | scoring constants | - |
| server/api_results.py:1206-1208 | C | sample-section seed | 140 | S | section_score | - |
| server/estimate.py:240-249 | C | mid(earned,possible,route,half) | 2*half, unrounded floats | S | arg `half` | clamp 200.0/800.0, 580 cap, `low=min(low,high-10)` |
| server/estimate.py:274-275 | C | _half(row) | MOCK_HALF_BAND for mock/section/paper else HALF_BAND | S | constants by kind. NOTE: Season Final (kind module) is stored at 140 but rescored at 200 here | - |
| server/estimate.py:288-291 | C | _printed | r10 of mid() | S | - | r10 |
| server/estimate.py:294-303 | C | rescore() | 2*half | S | _half | r10 |
| server/estimate.py:349-351,395 | C | ledger base/everything; `all_right` {low,high,mid} | 2*half, UNROUNDED | S | _half | clamp, cap |
| server/estimate.py:388-393 | C | ledger route.cap_cost = uncapped.high - 580 | depends on half | S | _half | - |
| server/estimate.py:421-428 | C | rescore_sitting after/before (written back into result.estimate and result.rescored) | 2*half | S | _half | r10 |
| server/estimate.py:150-155 | C | estimate().combined | 70/sqrt(n): ~100 (n=2), ~80 (n=3) | S | literal 70 | clamp, r10 via _round10 |
| server/estimate.py:174-175 | C | estimate().range | spread of mids | S | data | none |
| server/estimate.py:124-125 | C | _sittings low/high/mid per sitting | stored band | S | stored | - |
| server/estimate.py:129-132 | C | _sittings outside score | low=high=point (0 wide) | S | user-entered | - |
| server/estimate.py:661-686 | C | project() low/high/half | 120..300 | S | `max(60,min(150,_round10(half_latest+err)))`, err = regression prediction SE | mid clamp 200/800, ends clamp, ends NOT r10 (round only), half r10 |
| server/estimate.py:703-704 | C | projection() passes half_latest = (latest.high-latest.low)/2 | inherits latest band | S | stored band | - |
| server/api_today.py:1243-1265 | C | early_projection (fallback) | 120..300 | S | `max(60,min(150,_round10(half_latest)))` | clamp |
| server/api_today.py:1268-1273 | C | _points half = newest sitting (high-low)/2 | inherits | S | stored | - |
| server/estimate.py:709-744 | C | total() low/high = math band + rw scalar | = math band width | T | sum of math low/high + one rw value (no own total band) | none |
| server/estimate.py:742 | C | total pct = national(low,high,"total") | - | T | percentile table | table key clamp 400/1600, r10 |
| server/estimate.py:226-235 | C | national(low,high,subject) | percentile at each end | S or T | cb_percentiles.json | step clamps to table min/max, r10 |
| server/api_tests.py:2121-2131 | C | _up_to centre = min(800-MOCK_HALF_BAND, low+MOCK_HALF_BAND) | assumes stored half == MOCK_HALF_BAND | S | constant | r10 of result |

## 2. Server: band CONSUMERS (pass through, or logic on low/high)

| file:line | kind | name | what it does with the band | scale |
|---|---|---|---|---|
| server/api_results.py:115-121 | C | _band/_mid | validates band, mid = (low+high)/2 | S |
| server/api_results.py:379 | C | second_block `with` | estimate.rescore(right=slips) band | S |
| server/api_results.py:600-618 | C | _value path.estimate (out_of_reach = ledger.all_right, unrounded; reachable = rescore) and flip_easy.estimate (rescore) | bands | S |
| server/api_results.py:664,761 | C | report `ledger` (all_right unrounded) | band | S |
| server/api_results.py:731 | C | report previous.estimate | stored band | S |
| server/api_results.py:737-738 | C | rank.national at low and high | percentile pair | S |
| server/api_results.py:762 | C | report recovery (progress.recovery `now` = rescore) | band | S |
| server/api_results.py:769 | C | report total (estimate.total) | math band + rw | T |
| server/api_results.py:776-777 | C | route_rule half_band literal 70/100 | duplicate width, unused by web | S |
| server/api_results.py:825-826,872 | C | history delta / sort by mid | point | S |
| server/api_results.py:859 | C | history entry `estimate` | stored band | S |
| server/api_results.py:935,965 | C | stats `estimate` = estimate.estimate() (latest/previous/best/combined/range) | bands | S |
| server/api_results.py:1059-1064 | C | POST whatif -> rescore + delta | band | S |
| server/api_results.py:1268-1275 | C | compare band then/now + delta(mid) | stored bands | S |
| server/api_tests.py:1228-1234 | C | _moments "A new best band" (best by mid) | - | S |
| server/api_tests.py:1247 | C | "Up N on the original" mid delta r10 | point | S |
| server/api_tests.py:1296-1320 | C | _done hand-in: estimate {low,high,previous,best,target} + headline Up/Down mid delta r10 | stored bands | S |
| server/api_tests.py:1400-1407 | C | pass2 pts = rescore mid diff r10 | point | S |
| server/api_tests.py:1898 | C | pressure ceiling = rescore band (stored in result.pressure, not shown in web) | band | S |
| server/api_tests.py:1975,1986 | C | sitting_row `estimate` + capped | stored band | S |
| server/api_tests.py:2016-2018 | C | _mid | point | S |
| server/api_tests.py:2147-2164,2193-2194 | C | levers pts (rescore mid diffs) r10 | point | S |
| server/api_tests.py:2461-2463 | C | /api/tests estimate + headline_parts low/high | latest band | S |
| server/api_tests.py:2473 | C | /api/tests total, projection, calibration | see roots | S/T |
| server/api_today.py:119-136 | C | scores() low/high/mid/capped | stored band | S |
| server/api_today.py:886-891 | X+C | brief fact text `{low}–{high}` + mid delta | stored band | S |
| server/api_today.py:1300 | C | verdict at_target if latest.low >= target | width-dependent | S |
| server/api_today.py:1305-1313 | X+C | verdict text "On pace: about {low}–{high}", "Behind: on pace for {low}–{high}", "If this pace held: about {low}–{high}" | projection band | S |
| server/api_today.py:1318-1324 | C+X | calibration projected low/high, inside test, text "We projected {low}–{high}" | early_projection band | S |
| server/api_today.py:1438-1439 | C | /api/calendar sitting estimate low/high | stored band | S |
| server/api_today.py:483-485 | C | plan_draft default target = min(800, round10(band_high + 50)) | width-dependent (uses high) | S |
| server/plan.py:1002-1010 | C | _test_band verdict beat (low>=aim) / under (high<aim) / within | width-dependent | S |
| server/plan.py:1053-1057 | C | checkpoints baseline_band / band (not rendered in web) | stored | S |
| server/plan.py:1283-1285 | C | plan _sittings low/high | stored | S |
| server/plan.py:1766-1774,2033 | C | verdict.projection / payload projection = estimate.projection | 120..300 | S |
| server/api_profile.py:140-149 | C+X | fact `band`: latest low/high; text "the range tightens with more sections" | stored | S |
| server/api_profile.py:451-454 | C | score.points low/high per sitting | stored | S |
| server/api_profile.py:456,467 | C | math.band / goals.subjects.math.band = estimate latest | stored | S |
| server/api_profile.py:463-466 | C | goals.total now_low/now_high = latest low/high + rw_now | math width | T |
| server/progress_pdf.py:275-277 | C | PDF band = est.combined or est.range | combined (80-100) or spread of mids | S |
| server/progress_pdf.py:139-141 | D | hero big text r10 `lo–hi` (single number if lo==hi) | - | S |
| server/progress_pdf.py:150-157 | D | hero scale 200-800, band bar | clamp 200/800 | S |
| server/progress_pdf.py:309-311 | C | trend pts (history low/high/mid) | stored | S |
| server/progress_pdf.py:223-262 | D | trend: band bars, y-axis floor50(lo-30)..ceil50(hi+30) min 100 span, mid label r10 | - | S |
| server/parent_mail.py:29,35,41 | X | "score range {low} to {high}" (EN/UZ/RU) | - | S |
| server/parent_mail.py:89 | D | alert uses t.low/t.high | from api_parent | S |
| server/api_parent.py:160 | C | tests low/high passthrough | from api_admin | S |
| server/api_admin.py:137,144 | C | sittings low/high | stored | S |
| server/reports.py:577-580 | X | sitting ctx band string `{low}–{high}` | stored | S |
| server/compete.py:1370 | C | final_focus band = result.estimate | stored | S |
| server/api_compete.py:355 | C | test-day card band passthrough | stored | S |
| server/progress.py:1508-1513 | C | recovery now = rescore(recovered); points_recovered/open from mids | band + points | S |

## 3. Totals (section band combined into a total)

No separate total band exists. All three add a single R&W value to both math ends, so total width = math band width.

| file:line | how |
|---|---|
| server/estimate.py:731 | total(): low = math.low + rw.value, high = math.high + rw.value; rw from outside score (60 days) or learners.rw_now |
| server/api_profile.py:465-466 | goals.total now_low/now_high = latest.low/high + rw_now |
| web/index.html:2143 | client: `SAT total ${sc.low + p.rw_now}–${sc.high + p.rw_now}` |
| web/index.html:2902 | client: `≈ ${r.estimate.low + rw}–${r.estimate.high + rw} with your R&W` |
| Point-only totals (no range) | web/plan/plan.js:301,511; web/plan/wizard.js:277,462; web/me/me.js:479-481,586; web/index.html:2287; server/plan.py:2026-2027 (start/target sums) |

## 4. Single point scores (no range)

| file:line | what |
|---|---|
| server/estimate.py:136-139 | _mean3 = r10 mean of last 3 mids (45 days) |
| server/estimate.py:166 | trend delta (mid diff) |
| server/estimate.py:213-214 | percentile uses mid |
| server/estimate.py:765-793 | growth uses mids |
| server/api_tests.py:1775-1778 | /api/mocks cassette score = r10 mid |
| server/papers.py:188,332-334,363 | paper mid, average r10, `last` mid |
| server/plan.py:1293 | pace mean r10 |
| server/plan.py:1826,1845,1938 | propose current/target, measured current r10 |
| server/api_today.py:470-475 | plan_draft source value r10 (also passes latest low/high) |
| server/api_profile.py:351 | _self_rank estimate delta from mids |
| server/achievements.py:146-148 | climb = latest.mid - earliest.mid |
| server/compete.py:1946-1948,2053-2057 | leaderboards use band midpoint |
| server/estimate.py:130 | outside scores stored as low=high |
| web/me/me.js:23 | mid() = round of (low+high)/2 |
| web/results/page.js:515 | score = mid or right/asked*800 |
| web/tests/tests.js:75-81 | headline mid deltas r10 |
| web/tests/tests.js:730-732 | paper "average N", "you N" (y.last is a number, band() returns null) |
| web/tests/tests.js:573 | "You ≈N" |
| web/index.html:2129-2130 | added score / "≈ current" |
| web/index.html:2361 | current = r10 mid |
| web/plan/wizard.js:366-374 | "Use {mid}" r10 |
| web/compete/leaderboard/leaderboard.js:20 | copy: "by the middle of its estimate band" |

## 5. Web: display of server low/high

All of these show server low/high; recompute only where noted.

| file:line | kind | name | recompute? |
|---|---|---|---|
| web/assets/charts.js:186-190 | D | fband(lo,hi): "lo–hi" or single if equal | no |
| web/assets/charts.js:398-408 | D | normPoint: low/high from p.estimate/p.band/p; point -> low=high | mid=(low+high)/2 |
| web/assets/charts.js:417,431 | D | tooltip / gap text bands | no |
| web/assets/charts.js:506-512 | D | bandChart y-axis fit: floor((min-50)/step)*step .. ceil((max+50)/step)*step, clamp opts.min/max (200/800) | axis only |
| web/assets/charts.js:560-561 | D | estimate zone rect | no |
| web/assets/charts.js:563-568 | D | projection cone + label "if this pace held, lo–hi" | no |
| web/assets/charts.js:605-609 | D | sitting band rects | no |
| web/assets/charts.js:664-666 | D | R&W lane clamp 200-800 | - |
| web/assets/charts.js:683-685,740-744,770 | D | aria summary / data table / legend bands | mid round |
| web/assets/charts.js:811-812,822-898 | D | gauge: clamp 200/800, layers band/previous/today/second/whatif | mid round |
| web/assets/charts.js:907 | D | gauge paint big text r10 of each end | r10 |
| web/assets/charts.js:913-944 | D | gauge sweep / what-if glide | interpolation |
| web/assets/charts.js:954-1034 | D | UI.scale band/previous/estimate, label fband, count-up r10 (1034), clamp 200/800 | r10 on animate |
| web/assets/charts.js:2066-2102 | D | dotStrip band zone (no caller outside dev) | no |
| web/assets/results-ui.js:56 | D | rx.band(e) "low–high" | no |
| web/assets/results-ui.js:206,216 | D | sitting card score | no |
| web/assets/results-ui.js:301 | D | sitting card gauge | no |
| web/results/report/page.js:203 | C | `scored` = estimate.low present | - |
| web/results/report/page.js:427 | D | other sittings meta band | no |
| web/results/report/page.js:445 | D | "re-scored: before → after" | no |
| web/results/report/page.js:556-567 | D | hero gauge: band, previous, today (recovery.now), second (second.with); `differs()` rounds | mid round |
| web/results/report/page.js:574-575 | D | chip mid delta | point |
| web/results/report/page.js:585 | D | out_of_reach "reaches {round(path.estimate.high)}" (all_right.high unrounded) | Math.round |
| web/results/report/page.js:587 | D+C | "N to your target from the high end" / Target reached if e.high >= tgt | width-dependent |
| web/results/report/page.js:593-597 | D+X | national "low_pct–high_pct percentile"; info "Your band ... Our band is an estimate" | no |
| web/results/report/page.js:609 | X | route copy "tops out at 580", "Capped at 580" | - |
| web/results/report/page.js:613 | D | flip_easy band | no |
| web/results/report/page.js:629-633 | D | "Total ≈ low–high" + total pct + "Math lo–hi measured here · R&W n" | no |
| web/results/report/page.js:706 | D | ledger all_right band, Math.round (not r10) | round |
| web/results/report/page.js:723 | D | "all right here would have been {round(all_right.high + cap_cost)}" | point |
| web/results/report/page.js:738 | D | compare then → now (delta) | no |
| web/results/report/page.js:957,978-979 | D+C | "Fix the top 3: re-scores at lo–hi", "target falls inside" (low<=tgt<=high) | width-dependent |
| web/results/report/page.js:1314-1327 | D | what-if band + gauge whatif | mid delta |
| web/results/page.js:74-75 | C | bandOf(E) = E (if has low) else E.combined else E.range | picks source |
| web/results/page.js:229-245 | D+C | sidecard: track (clamp 200-800), "Target N: Reached / N to go" uses heroBand high (width-dependent), Best sitting band | round |
| web/results/page.js:254 | C | heroBand r10 of combined/range | r10 |
| web/results/page.js:259-265 | D+X | hero band (single if low==high); copy "From your last N full sections..." / "The spread of your scored sittings so far. Two full sections ... firmer band." | no |
| web/results/page.js:293 | D | heroShow hovered sitting band | round |
| web/results/page.js:314-324 | D | bandChart pts + estimate zone (combined/range) | no |
| web/results/page.js:663-664 | D | CSV band_low/band_high | no |
| web/tests/tests.js:25 | D | band(e) round each end | round |
| web/tests/tests.js:111-120 | D | hero band (latest) + rolls from last seen | no |
| web/tests/tests.js:125-130 | D | chart last 8 sittings | no |
| web/tests/tests.js:135 | D | Best band | no |
| web/tests/tests.js:143-146 | D | "Total lo–hi" (server total), projection verdict or "On pace: about lo–hi" | no |
| web/tests/tests.js:149-153 | D | calibration "our estimate then: band(x.estimate || x)" BUG: server sends `x.band`, prints null | no |
| web/tests/tests.js:234-235 | D+C | L.both.band (server sends only pts: dead) | - |
| web/tests/tests.js:571 | D | D.twin.band (server twin has no band: dead) | - |
| web/tests/tests.js:763,782,895,926 | D | sitting rows band / sort by mid | mid |
| web/tests/tests.js:1044-1045 | D | CSV band column | no |
| web/tests/compare.js:19,34 | D | band rounded | round |
| web/test/test.js:707-716 | D | hand-in UI.scale band, previous, target, label "lo–hi" | no |
| web/index.html:2141-2142 | D | Today score band + "Capped at {high}" | no |
| web/index.html:2149 | C+D | UI.scale: band = latest; estimate = current±30 (client 60-wide) | yes, ±30 |
| web/index.html:2153 | C | gap = target - mid | point |
| web/index.html:2174-2178 | D | bandChart scores + outside points + projection | no |
| web/index.html:2187 | D | calibration text (server) | no |
| web/index.html:2201 | D | folded row "lo–hi" | no |
| web/index.html:2211 | D | drift chips "date · lo–hi" | no |
| web/index.html:2265 | C | target default = ceil10(mid + 60) | point |
| web/index.html:2277,2303 | D+C | "Below your latest band" (v < sc.low), "Latest lo–hi" | width-dependent |
| web/index.html:2709 | D | calendar day sitting "lo–hi" | no |
| web/index.html:2876,2894,2906 | D | recent tests fold/card band + UI.scale | no |
| web/me/me.js:22 | D | band(b) "low–high" | no |
| web/me/me.js:352-358 | D | outcomes "band(first) → band(latest)" + mid delta | mid |
| web/me/me.js:474,486-492 | D | goals gbar band + "lo–hi now · target · +N to go" (mid) | mid |
| web/me/me.js:503 | X | "a {ceiling} puts 800 inside your band" (true only while half >= 20) | width-dependent copy |
| web/me/me.js:638 | D | "+N from your latest band" (mid) | mid |
| web/me/me.js:672-677 | D | snapshot band, Best band, "SAT total now_low–now_high" | no |
| web/me/me.js:731 | D | said snapshot band | no |
| web/me/me.js:995 | D | trend chart points | no |
| web/plan/plan.js:494 | C+D | track band mean±35 (client 70 wide) | yes |
| web/plan/plan.js:502 | D | "At this pace lo–hi" r10 of projection | r10 |
| web/plan/progress.js:60-77 | D | score path chart sittings + projection; y-axis floor50(low-60)..ceil50(high+60) clamp 200/800 | axis |
| web/plan/wizard.js:373 | D | "Latest · kind · date · lo–hi" | no |
| web/plan/wizard.js:410-412 | D | slider ticks: sitting bands as bars, clamp 200-800 | no |
| web/assets/plan-ui.js:224 | X | test task verdict "within the band" (plan._test_band) | - |
| web/compete/contest/contest.js:298-306 | D | Final "Section estimate lo–hi", weekly "Module estimate lo–hi" | no |
| web/compete/contest/contest.js:507 | D | test-day card "Season Final: lo–hi" | no |
| web/compete/contest/contest.js:597 | D | board column Band (entries carry no band server-side, likely empty) | no |
| web/parent/parent.js:138 | D | "low to high" | no |
| web/admin/student/index.html:67 | D | "low to high" | no |
| web/assets/report.js:516 | D | report sheet st.band (server string reports.py:580) | no |
| web/s/index.html:277 | D | set Score column r.band (server sets.py:509 only accepts a number, so always null) | dead |
| web/assets/ui.js:906,3249 | D | UI.band helper exported, no caller | dead |
| web/results/report/page.js:1419 | D | J.without_guesses band: no server field | dead |

## 6. Copy and static text that states a width or range

| file:line | text (abridged) | implies |
|---|---|---|
| server/scoring.py:16-20 | "a band narrower than 200 points would be pretending" | 200 |
| server/scoring.py:61 | comment "a 200-point band" | 200 |
| server/scoring.py:84-86 | mock band narrower by sqrt ratio, "not as narrow as the real test's 20 points" | 140 |
| server/estimate.py:158 | "One full section narrows it to about 140 points." | 140 |
| server/estimate.py:160 | "landed within 100 points of each other" (consistency threshold, also logic at :159) | 100 spread rule |
| server/estimate.py:162 | "A second within 100 points would firm it up." | 100 |
| server/estimate.py:164-165 | "your last two sections are {gap} points apart" | data |
| server/api_profile.py:144 | "the range tightens with more sections" | - |
| server/next.py:138 | "20 q · a score range", "Your starting band in 20 questions" | - |
| server/parent_mail.py:29,35,41 | "score range {low} to {high}" | - |
| web/tests/tests.js:98 | "A full section gives a band about 140 points wide; one module or the diagnostic, about 200." | 140/200 |
| web/tests/tests.js:1059 | "Bands: about ±70 for a section or paper, ±100 for a module or the diagnostic." | 70/100 |
| web/tests/start.js:362 | Module 1 card "±100 estimate" | 100 |
| web/plan/progress.js:93 | "A test reads as a band: ±70 for a module or section, ±100 for the diagnostic." (wrong today: module is ±100) | 70/100 |
| web/plan/wizard.js:453 | "A perfect section reads 710–800 here" | 780±70 |
| web/me/me.js:503 | "a {ceiling} puts 800 inside your band" | half >= 20 |
| web/diagnostic/index.html:47 | "A first band, about 200 points wide" | 200 |
| web/diagnostic/index.html:61 | comment "a band about 200 points wide" | 200 |
| web/help/answers.json:109 | "shown as a band ... More sittings narrow it." | - |
| web/assets/tour.js:35 | "A range based on your recent tests ... narrower and more reliable" | - |
| web/assets/palette.js:271 | "placement score band" | - |
| web/results/page.js:261-262 | combined / "spread of your scored sittings" copy | - |
| web/results/report/page.js:597 | "Our band is an estimate..." | - |
| web/index.html:2168 | "Tightens your score band where the evidence is thin" | - |
| web/compete/leaderboard/leaderboard.js:20 | "by the middle of its estimate band" | - |
| web/assets/plan-ui.js:224 | "within the band" | - |

Sample / example bands (hardcoded):

| file:line | sample | width |
|---|---|---|
| web/diagnostic/index.html:65 | 480-680 | 200 |
| web/tests/tests.js:179 | sittings 440-600, 470-610, 480-620 | 160/140/140 |
| web/tests/tests.js:184 | "480–620" | 140 |
| web/tests/tests.js:813 | 520-600 | 80 |
| web/tests/index.html:105 | CSS comment "520–600" | 80 |
| web/results/page.js:250-251 | 470-550, 510-590, 550-630, estimate 550-630 | 80 |
| web/assets/results-ui.js:26 | doc comment "520–660" | 140 |
| web/dev/kit.html:755-817, web/dev/premium.js:341,549,720,830,842 | dev-only samples (50-80 wide) | - |

## 7. Width-dependent logic (reads low or high, not mid): behaviour changes when bands narrow

- server/plan.py:1009 verdict beat/under/within.
- server/api_today.py:1300 at_target if latest.low >= target.
- server/api_today.py:484 default target from band high + 50.
- server/api_today.py:1322, server/estimate.py:809 calibration `inside` (low <= score <= high).
- server/estimate.py:393 cap_cost from uncapped high.
- server/api_tests.py:2130 _up_to centre from low + MOCK_HALF_BAND.
- server/scoring.py:106, server/estimate.py:248 `low=min(low, high-10)` on capped bands.
- server/estimate.py:234 national percentiles at each end.
- web/results/report/page.js:587, 979; web/results/page.js:241; web/tests/tests.js:235; web/index.html:2277.

## 8. Tests / checks that encode widths (will break or need fixture updates)

- server/test_flow.py:151 asserts `hi - lo >= 100`.
- server/test_flow.py:281-291, 525 route cap assertions (high <= 580, high < top).
- server/estimate.py:851-863 self-test project(..., 70) half inputs.
- server/checks/f4.py:733-856 fixtures 140/200 wide bands, :737 combined, :803 total, :842-845 project half 70.
- server/checks/s3.py:893 fake_sitting half=40; :935 projection low<high.
- server/checks/s5.py:335 combined n; :606 140-wide fixtures; :862-863, :970-973 ceiling/mid.
- server/checks/s6.py:81 whatif high >= report high.
- server/checks/s7.py:381-410 _test_band fixtures (140 wide, beat/within/under).
- server/checks/s8.py:542 fixture 610-750.
- server/checks/f6.py:186-189 "520–600" band string; :427,:448 rescore.

## 9. Not score estimates (considered, excluded)

- web/me/me.js:705-707 "Started lo–hi": compete climb cohort window around first mid, half = 40/80/160 (server/compete.py:2072, lo/hi at 2091-2092). A score range, but a cohort filter, not an estimate.
- web/words/run/index.html:1011 vocabulary "±(hi-n)" (server/words.py:735-743): word count.
- server/drill.py:442 BAND_MID: College Board 1-7 item difficulty bands mapped to item ratings.
- tools/cb_data.py, tools/cb_rw_fetch.py: CB score_band_range_cd 1-7.
- server/compete.py:1815-1894 champions `band` = level bands.
- server/api_words.py, server/words.py freq/sprint bands.
- web/assets/compete-ui.js:314 rank range "#lo–#hi".
- server/ratings.py: Elo-style ratings (400 divisor), no score band.

## 10. Checked, no range logic

server/mail.py, server/challenge.py, server/daily.py, server/api_shell.py, server/api_me.py (200-800 in tens validation only, :166-177), server/ratings.py, server/next.py (copy only), server/api_compete.py (passthrough at :355), server/api_plan.py (passthrough), tools/*.py (no score bands; cb_data builds percentiles json only), web/welcome/*, web/share/index.html (loads me.js read-only, so me.js rows apply), web/assets/kit.js, web/assets/runner.js, web/assets/quick.js (200–800 placeholder only), web/practice/*, web/review/*.
