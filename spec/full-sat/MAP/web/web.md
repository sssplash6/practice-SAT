# Web side map for the full-SAT test (R&W 2x27 then break then Math 2x22)

Read 2026-10-22, READ-ONLY. Line numbers are against the working tree (uncommitted edits included).
All paths relative to /Users/workingmyassof/freshbot/satbank. Raw per-file notes sit beside this file (raw-*.md).

## 0. Headline findings

1. test.js builds a fresh `UI.runner` for every module: `start()` calls `destroyRun()` (test.js:433) then `UI.runner(runHost, {...})` (test.js:446-500). Every tool flag is read once per module from the session payload `S`. So gating the calculator, reference sheet and Math directions for R&W is a test.js change at test.js:452 (`calc: S.calculator !== false, ref: true, annotate: true, scratch: true, directions: true`), driven by a per-module `S.subject`. runner.js needs no subject logic for that.
2. The two-pane passage layout already works in exam mode. runner.js `placePassage` (1764-1772) has no mode check: `if (it.q.text && !phone() && fitsPassage())` moves `ws.passageNodes` into the `.rn-passage` pane; `runner.css` `.rn.has-passage` rules (529-551) are mode-agnostic; `annotate(bodyEl, ...)` (1794) anchors marks on the pane or inline. test.js passes each question object through untouched (test.js:427 `Object.assign({}, q, { number: i + 1 })`), so if the server's session payload includes `text`, R&W renders like practice. Practice proves it: practice/session/session.js:176-215 uses the same runner and passes neither `calc` nor `ref`, so R&W practice currently shows the calculator and reference too.
3. Highlights on the passage use addr `'p'` (question.js:432). test.js `marksOut` (85-91) maps only `'s'` to `'stem'` and passes every other addr through, so passage marks reach `POST /session/{id}/state` as `at: 'p'`; `marksIn` (92-93) maps back. Server must accept `at: 'p'`.
4. Subject-aware plumbing already exists and should be reused: kit.js `SUBJECT` + `qlabel` + `qlabel.addr` (2933-2949), report `?q=` parser (report/page.js:37-47), runner `rvAt` (3075-3084), results-ui chips grouped per (subject, module) (results-ui.js:200-244), gauge `subject` option (charts.js:824).
5. Almost every score surface is hard-coded to one 200-800 Math scale; the "total" today is Math band + a self-entered R&W number.

## 1. Feature by feature

### Diagnostic
- Entry: diagnostic/index.html:40 ("20 questions · 32 min · all four domains evenly"), :42 Start, :70-75 `TestStart.go({kind:'diagnostic'})`; :47 "about 200 points wide"; :65 `UI.scale(... min: 200, max: 800)`.
- start.js:80-82 diagnostic is `POST /api/session` (not `/mock/new`); start.js:40 KIND diagnostic n 20; start.js:218 steps Test/Conditions only.
- tests.js:272 next card text; tests.js:521 INFO "All four domains evenly", "20 questions · 32 min".
- test.js:63 `baseSeconds` fallback `(question_count || 22) * 95` for custom/diagnostic (20 x 95 = 31:40). test.js:174 and :699 finished diagnostic goes to `/diagnostic/signup.html`; :265 no "Start over" for diagnostic; :720-723 "The diagnostic is in".
- signup.html (whole file) and verified.html: subject-neutral. signup.html:55 "once the last module is handed in"; gate polls `GET /session/{sid}/results` (79-82).

### Section mock (2-module routed)
- tests.js:516 INFO section "Adaptive", "8/7/4/3 each module" (Math domain counts), "44 questions · 70 min · 2 modules"; :257 default next card "44 questions · 70 min"; :288 plan variant.
- start.js:36 KIND section n 44 mods 2; :137 body `{kind:'section', route, m1}`; :342-357 Module 2 seg adaptive/upper/lower, Module 1 standard/harder/easier, "tops out at 580".
- test.js:215-218 lobby "N modules · X questions each" (uses `S.modules[0].questions`), "Module 2 is fixed / chosen by how module 1 goes"; :283 startOver to `?start=section`.
- No subject is ever sent: start.js `body()` 131-165 builds no `subject`; `go()` 74-95 posts to `/mock/new`.

### Single module
- tests.js:517-519 module1 / module2u / module2l "22 questions · 35 min", "580"; :284 next card; :914 "Try the harder module 2".
- start.js:37 KIND modules n 22; :113 `count = mods * 22`; :143-147 m1+m2 becomes a section with fixed route; :359-379 cards "22 questions · 35 min", "14 of 22", "n of 2 modules · n*22 questions · n*35 min".
- test.js:219 single module lobby shows "N questions"; kit.js KIND.label "Module m".

### Custom test builder
- start.js:402-442 `stepCustom`: skill picker iterates `UI.DOMAINS` + `UI.TOPICS` (412-420), which are Math-only (ui.js:652-680). R&W skills cannot be picked. Formats seg Both / MC only / "Grid-in only" (434). Length seg 10/22/44 (427). "mmss(n*95) at test pace" (441).
- start.js:39 KIND custom; :114 count; :127-128 seconds `n * 95`; :148-155 body; :498-502 timing "95 s a question".
- test.js:74 "95 s a question"; :335-339 "My own minutes" for custom.
- tests.js:520 INFO custom "5–60 questions"; :524 traps "6–22 questions · 95 s each".

### Twin
- tests.js:522 INFO; :551/579 `D.twin`; :912 sitting menu Twin for section/mock/module/paper/twin/shared; :371-372 cycle twin.
- start.js:41 KIND twin n 44 mods 2; :139 body; :383-387 step text.
- report/page.js:384-388 `retake()` posts `{kind:'twin', twin_of, full: kind !== 'module', timed}`; :393-396 offered for mock/module/diagnostic/paper.
- compare.js slot-by-slot table (95-114) labels come from server `slot_label`.

### Paper (weekly Papers) and printable output
- Papers (same slots for everyone): tests.js:649-695 papers card; :656 "line at 14"; :699-709 rating "Expect e1 of 22 in module 1, where 14 routes you up"; :712-718 preview meter `max 22, ticks 22, tick 14`; :741 "of 22"; :739 race `count 22, minutes 35`; :277 "44 questions · 70 min".
- start.js:38 KIND paper n 44; :138 body; :325-334 paper picker.
- talk.js (paper sheet): :22-25 `SHORT`/`MODULE` maps only m1/m2u/m2l, `slotName('m1:5')`; :196 qid fallback `m1q${pos}`; :163 and :187-188 grid-in spread.
- Printable: no printable full test exists. Report prints: repair pack / retry sheet / tutor packet (report/page.js:1695-1756) render with `UI.workspace` (1724) and an "A–D" key (1749); `@media print` table (index.html:246-264, page.js:1083-1096). Practice worksheets use `/practice/session/?id=..&print=1` (review/review.js:1784, review/sheet/sheet.js:184-206). Results page Print (results/page.js:140).

### Shared test
- tests.js:983-1038 Share sheet: `POST /sets {kind:'test', session, show_score, cfg:{fresh}}`; race `{from_session, count 22, minutes 35, twin, open_for 72}` (1018-1022).
- tests.js:1169-1170 `?shared=CODE` opens start sheet. start.js:237-245 `loadShared` (minutes fallback `count/22*35`), :393-400 text "Module 1 ... Module 2 matches when you earn the same route", :44 KIND shared n 44 mods 2.

### Archive shelf mock
- No served web client. The shelf page is archive/site-v1/web/mock/index.html (not mounted: server/app.py:33 `WEB = .../web`), it calls `GET /api/mocks` and `POST /api/mock/{num}` then opens `../test/?s=ID` (archive mock/index.html:304-317). Sittings it creates are kind `mock` and flow through test.js, Tests, Results and the report like any section (kit.js KIND mock "Full section"; results-ui.js:367 "Module n" for kind mock in progress).

### Results page (results/page.js)
- :62-66 `startTest` posts legacy `{full, timed}` to `/mock/new`; :218-219 "Full section" / "One module" (70 / 35 min); :244 "(70 min)".
- :231-234 target track on a 200-800 scale (`pos = (v - 200) / 6`).
- :258-273 hero: :263 "Math is measured here; Reading and Writing is your own score until SAT Freshman has R&W questions."; :270 "Math estimate"; :272 "/800".
- :316 chart detail "harder M2 / easier M2"; :323-326 `bandChart` (default 200-800, grid 200).
- :432 Domains tip "one full SAT Math section: two modules, 44 questions ... (22 questions)"; :437-438 column names/tips 22/20/44; :433 and :640 domain order from `UI.DOMAINS` (Math).
- :515 sitting score fallback `right/asked*800`.
- :607 Skills card filters `(t.subject || 'math') === 'math'`: R&W skills are excluded.
- :40 FORMAT Grid-in; :405 why-you-miss keys include `entry`.

### Report page (results/report/page.js)
- :37-47 `?q=` accepts `(math|rw)` prefix and module: `q=rw-m1-7` style hash; default `math`.
- :207 `sectioned = modules.length > 1`; :219 `UI.review.at(IT.map({n, module, subject}))`.
- :226-236 names "Full section" / "One module"; :240 "Adaptive", "Form x"; :265 "Calculator off" meta.
- :297 and :1595 budget fallback 95455 ms (35 min / 22); :1512 pace line default 95455.
- :328 "Entry: grid-in rules"; :922 "Missed grid-in"; :1052/:1244 Format Grid-in/MC; :1529 blank advice MC vs grid-in.
- :354 "Harder next · New section" posts `{full:true, timed:true}`.
- Hero :550-623: :566-567 `UI.gauge({..., subject: R.subject || 'math', sub: SUBJECT label · middle})`; :571 "Math is measured here. Reading and Writing is your own score ..."; :576 "First section"; :585 "needs the harder Module 2"; :605-610 route line only when `R.kind === 'mock'`, `rule.lower_ceiling || 580`.
- :625 `doneMs` reads the four Math domains by name prefix (Algebra, Advanced Math, Problem-Solving, Geometry) for `UI.spotArt('done')`.
- :627-648 `totalBlock`: `R.total.parts` with `subject === 'rw'`; owner R&W input 200-800 `PUT /me {rw_now, rw_source}` (637-645).
- :689-725 ledger by cause/tier; :718-724 route savers "harder Module 2", 580; :1148 legend "routed you up".
- :751-759 then-vs-now slots grouped by `s.module` only.
- Questions grid :1170-1204: `modLine` name `Module ${m}`, route only for `mod.n === 2`, `' of 35:00'` hard-coded (1178); `modGroups` keyed by `x.module` only (1180-1184).
- Filters :1000 and :1048 module filter by number only. :1153/:1160 time shading thresholds 30/95/190 s.
- :1336-1381 domains from server, ordered by `UI.DOMAINS`; :1377 "% of the section".
- Pace :1498-1538 groups by `x.module` only (1505-1506); clock replay :1542-1571 finds `pace.modules` by `Number(p.n) === (m || 1)` (1543) and `dur = clock_ms / modules.length` (1551).
- :1598 "New section" link.
- Player :1602-1625 `playerItem` includes `text` and `subject` (1603, 1618); :1662-1663 `UI.review(..., sitting: { subjects: 1 })` hard-coded.
- CSV :1680-1693 columns question,module,n (no subject).

### Pressure, pacing, causes analytics
- Pressure: test.js:697-698 stores `satf.pressure.{sid}`, :748-757 Pressure check button, :798-802 `POST /session/{sid}/pressure`; tests.js:262-266 next card, :777 filter, :886-887 chip "Pressure n · Knowledge n"; report/page.js:1583-1589 Up next.
- Pacing: runner pace guide ticks with checkpoints `[7, 14]` (runner.js:1983, :2674-2680 toast "behind at Q8/Q15"); `pace_ms: 95000` to navigator and Check your work (runner.js:2241, :2292), `overBudget` default 95000 (:343), `budgetAt` fallback 95000 (:2641), odds value fallback 95 s (:2293). test.js:651-663 "Module 1 pace" chart in between. tests.js:439-492 Habits rows are server-built. report drawPace/clockReplay above.
- Causes: tests.js:70 CAUSE map, :203-247 "Where points went" (server `levers`), :232 fallback "lifted the 580 cap"; results/page.js:399-408; report :62 CAUSES (includes `entry` = grid-in), :323-331 fix menu; results-ui.js:40-44; runner.js:3541 `entry` cause offered only for spr.

### Gate / route display
- test.js:645-648 between route text; :683-688 `gateLine` "harder module 2"; :725-731 done chip "Harder/Easier module 2"; :763-792 trainer strip, :231 "The line: 0.6*n".
- tests.js:333-335 Module 1 meter `max 22, ticks 22, tick 14` "14 of 22 right routes you up", Module 2 meter; :326 `lastM1` requires `modules[0].asked === 22`; :715-716 paper preview tick 14; :870-885 chips "Harder M2", "Easier M2", "580 cap", "Route line +g"; :1054-1080 How scoring works (14 of 22, 580, up to 800, 75 s break rule).
- compare.js:28-29 gate/route; results-ui.js:189 subtitle "harder M2 / easier M2".

### Score estimate display
- test.js:714-715 done card `UI.scale(... min: 200, max: 800)`.
- tests.js:92 "Estimated Math score"; :98 empty text; :113 and :184 "of 800"; :130 and :180 `bandChart min 200 max 800`; :144 "Total low–high · with your R&W ..." from `D.total`; :152 calibration `x.math ?? x.score`.
- results/page.js:231-234, :263, :270-272 (see above). report :566-571, :627-648.
- charts.js: `bandChart` y defaults `opts.min ?? 200, opts.max ?? 800` (506), auto-thinned grid (516), R&W self-entered lane hard-coded 200-800 (664-677), `normPoint` reads `p.math ?? p.score` (398-408); `gauge` `min ?? 200, max ?? 800` (811), ticks at thirds (840) work for 400-1600, label from `UI.SUBJECT[subject]` default "Math" (824, 874, 880); `scale` `min ?? 200, max ?? 800` (954); `dotStrip` min 200 bin 20 (2068). kit.js SUBJECT has math and rw only (2933-2936), no total entry.
- results-ui.js:301 Peek gauge `subject: 'math'` hard-coded.

### Timers and break screen
- runner.js:119-220 `timer` is generic (warnings 300/60 s, unhides at 5:00).
- test.js:61-64 `baseSeconds`: `S.duration / factor`, else 95 s/question for custom and diagnostic, else 2100 (35 min). :66-76 `timingText` (" for each module", "95 s a question").
- start.js:123-130 `seconds()` = `2100 * modules` or `n * 95`; :498-502 timing rows "35:00 a module".
- Between modules: test.js:630-682 builds `UI.between(b, {conditions, seconds: 60, stats, next, route, cells, ...})`. runner.js:2943-2996 `between`: `o.seconds` already a parameter and `o.title` overrides the h1 (2950), but "Module 2 starts in" (2959, 2989), "Begin module 2 now" / "Begin module 2" (2963, 2995), "Getting module 2 ready…" (2978) are hard-coded. There is no section break screen; a 10-minute break can reuse `UI.between` with `seconds: 600` once those strings are parameters. Training mode has no countdown (2944-2945, 2970).
- Time's up: test.js:607-627; runner.js:2610-2624 (closes calculator).

### Calculator (Desmos) and reference sheet
- test.js:452 `calc: S.calculator !== false, ref: true` (reference always on); :290-296 settings line "calculator / no calculator / scientific calculator"; :341-343 Settings Calculator switch; :363-366 keys G Calculator, F Reference; :643 between "calculator and reference sheet on every question".
- start.js:108 tools.calculator default; :185 summary "calculator on / no calculator"; :524 Calculator switch.
- runner.js:1291-1296 `cfg.calc`, `cfg.ref` per runner; :1349-1358 tool buttons; :1709 passed to `UI.workspace`; :2163-2168 per-question calculator expressions saved; :2361-2366 `toggleCalc`; :2810-2817 keys G/F; :2906 auto-open calculator from prefs; :2522-2525 practice "Calculator opens" menu.
- runner.js:1117-1194 `REF` Math formula sheet, `refDock`, `refSheet`; :1550 slot tabs include Reference when `cfg.ref`.
- runner.js:1197-1215 `DIRECTIONS` is the Math section text (calculator permitted, SPR rules); :1217-1234 appends `UI.spr.directions()` table. Shown on first begin (test.js:503) and the lobby Directions link (test.js:260).
- Review player always shows Calculator and Reference (runner.js:3160-3165, 3179-3191).
- question.js:1670-1671 tools honour `o.calc`, `o.ref`.

### Grid-in (SPR) input
- test.js:428 spr items use `value`, MC use `selected`; :479 nudge kind `grid`; :38 aid text "the grid-in form".
- runner.js:1309 `isMc`; :1550 "Entry rules" slot tab only for spr; :1819-1832 `sprHelp` only for spr; :1866 Eliminate hidden for spr; :1850 practice "Grid-in" badge; :2452 Details Format; :2492 answer pad note.
- All of these are per item, so an all-MC R&W module never triggers them. Only the copy (DIRECTIONS, AIDS text) is Math-specific.

### Passage rendering
- question.js:429-445 `passage(q)`: `<div class="q-passage" data-addr="p" data-nofold>`, paragraphs, "Text 1/Text 2" labels, `<u>`, blanks; :570-576 rendered inline; :640 R&W options are prose (no TeX) with `data-addr o:i`; :1754 `ws.passageNodes`; :399-401 R&W speech.
- runner.js:1424-1430 pane; :1472-1505 `layout()` (passage and docked calculator share the left column, passage wins 1481-1483); :1531-1539 resize, `satf.passage.w`; :1599-1604 `detailsFit` counts the passage; :1757-1772 `fitsPassage`/`placePassage`; :1754-1755 cleared on destroy. Phone and narrow screens keep it inline (runner.css:1216 hides the pane under the phone breakpoint).
- Review player: question rendered inline via `UI.workspace` (runner.js:3440-3455), no two-pane; works because `playerItem` includes `text` (report/page.js:1603). Note runner.js:3050 `QF` (flat review rows) lacks `text`, so a flat row without `q` would drop its passage.

### Annotation / highlight tools
- runner.js:785-961 `annotate` works on any `[data-addr]` node: addrs `s`, `t:r:c`, `o:i`, and the passage `p`. Attached to `bodyEl` (1794) so pane marks work. Exam tool "Highlights & Notes" (1349).
- test.js:85-93 style and addr mapping (see headline 3). practice session.js:80-81 keeps addr unchanged.
- Read-only marks in the review player (runner.js:3454).

### Question counts and durations hard-coded
- 22: tests.js:326, :333-337, :406-407, :411, :565, :704, :715-716, :739, :741, :1018-1022; start.js:113, :242, :362-375, :427; test.js:63, :642; talk.js m1 slots; report/page.js:1178 ("of 35:00").
- 20 / 32 min: tests.js:272, :337, :407, :521; start.js:40; diagnostic/index.html:40.
- 44 / 70 min: tests.js:116, :257, :277, :288, :516; start.js:36, :38, :41, :44, :116; results/page.js:218-219, :244, :432, :437-438.
- 35 min / 2100 s: test.js:63; start.js:128, :242, :375, :498; tests.js:281, :284, :517-519, :523, :565, :739, :1018-1022; report/page.js:1178.
- 95 s per question: test.js:63, :74; start.js:128, :441, :502; tests.js:524; runner.js:343, :566, :665, :2241, :2292-2293, :2641; report/page.js:297, :1512, :1595, :1153/:1160.
- 14 of 22 route line, 580 cap: tests.js:232, :333-335, :519, :656, :704, :715-716, :872, :1060, :1075-1077; start.js:57, :346, :362-364, :390; report/page.js:609, :723.
- Pace checkpoints after Q7 and Q14: runner.js:1983, :2674.
- No 27, 32-minute module, 54, 98, 134 or 10-minute break appears anywhere in the web side.

### "Math" strings
- tests.js:92 "Estimated Math score", :1044 CSV columns "Math M1..".
- results/page.js:263, :270, :272, :432.
- report/page.js:571 (and :567 falls back to "Math").
- runner.js:1197-1198 directions ("important math skills ... calculator is permitted"), :1241 doc comment "Math · Module 1 of 2".
- charts.js:824 gauge label default "Math"; compare.js:24 DOMAIN map.
- Subject defaults to `math`: report/page.js:42, :567, :1618; runner.js:3074, :3077; kit.js:2938; results-ui.js:231-234, :301, :317; results/page.js:607; practice session.js:66, :87; charts.js:824.

### Domain names hard-coded
- ui.js:652-657 `DOMAINS` (Algebra, Advanced Math, Problem-Solving and Data Analysis, Geometry and Trigonometry) and :658-680 `TOPICS` (19 Math); `RW_SKILL` (681-686) maps the 10 rw slugs to names but has no domain grouping and is not in `TOPICS`/`TOPIC`.
- Consumers: start.js:412-420 (custom picker), results/page.js:42, :433, :640-645, report/page.js:67, :1041, :1358, results-ui.js:191 and :390-391 (skill names via `UI.TOPIC`), runner.js:407-410 and fillHead :3496-3503 (fall back to `topic_name` for rw), test.js:547-554 `shortOf` (falls back to first words of `topic_name`).
- compare.js:24 `DOMAIN` keys algebra/advanced/psda/geometry; report/page.js:625 `doneMs`; tests.js:516 "8/7/4/3 each module"; "all four domains evenly" (tests.js:272, :521; start.js:40; diagnostic/index.html:40).

### Score axes 200-800 vs 400-1600
- 200-800 hard-coded: test.js:715; tests.js:113, :130, :180, :184; results/page.js:232-233, :272; report/page.js:637-641 (R&W input range, correct for a section); diagnostic/index.html:65; charts.js:506, :666, :811, :954, :2068 (defaults, overridable by `min`/`max` except the R&W lane).
- No 400-1600 anywhere. The gauge, scale and bandChart accept `min`/`max`, so a total only needs callers to pass 400/1600 (and the bandChart's grid step thins itself, 516).

## 2. Runner: what branches on subject, and what would need to

| Concern | Today | Where |
|---|---|---|
| Calculator button, G key, auto-open, Desmos exprs | runner-level `cfg.calc` from caller; test.js passes `S.calculator !== false` | runner.js:1292, :1351, :2361, :2810, :2906, :2163; test.js:452 |
| Reference sheet, F key, slot tab | runner-level `cfg.ref`; test.js passes `true` | runner.js:1292, :1352, :1550, :2811; test.js:452 |
| Directions text | Math only, `cfg.dirs` | runner.js:1197-1234, :1336, :2481; test.js:452, :503 |
| SPR input, Entry rules, Eliminate hidden | per item (`q.type`) | runner.js:1309, :1550, :1819-1832, :1866 |
| Passage pane | per item (`q.text`), any mode | runner.js:1757-1772 |
| Pace budget defaults | 95000 ms constants | runner.js:343, :2241, :2292, :2641 |
| Pace checkpoints | `[7, 14]` | runner.js:1983, :2674 |
| Phone footer label | `${o.short || 'M1'} · n of total` | runner.js:1998; test.js:448 `short: M${module}` |
| Check your work copy | "can't come back to this module" | runner.js:645 |
| Between screen copy | "Module 2" strings | runner.js:2950-2995 |
| Review player tools | Calculator and Reference always shown | runner.js:3160-3165 |
| Review labels | `UI.qlabel(it, o.sitting)`; subject prefix only if `sitting.subjects > 1` | runner.js:3274; kit.js:2937-2948; report passes 1 at page.js:1663 |
| Review nav | flat strip up to 24 items, else a pill + navigator; no module grouping | runner.js:3231-3268 |

Practice reuse: practice/session/session.js:176-215 drives the same `UI.runner` in `mode: 'practice'`; R&W items already render with the passage pane there. Test mode can reuse it as is; the only exam-mode differences are tool flags and copy.

## 3. Already subject-aware (reuse)

- kit.js:2933-2949 `UI.SUBJECT` {math, rw}, `UI.qlabel(item, sitting)` ("R&W M1 Q5" when two subjects), `UI.qlabel.addr` (`rw-m1-5`).
- report/page.js:37-47 `?q=` parse with subject; :219 `UI.review.at` with subject; runner.js:3074-3084 `rvAddr`/`rvAt` match subject+module+n.
- results-ui.js:200-244 miss chips one group per (subject, module), links via `qlabel.addr`.
- charts.js:824 gauge `subject` label; report/page.js:566-567 passes `R.subject`.
- report/page.js:1603/1618 `playerItem` carries `text` and `subject`.
- question.js passage, prose options, R&W speech; test.js marks round-trip `p`.

## 4. One-section assumptions in the web flow

- test.js module numbering: `two()`/`lastModule()` (56-57) from `S.modules`; boot sends `module > 1 && !begun` to `between()` (196); lobby "Module m of N" (234) and "Module 2 is ..." (217), "N modules · X questions each" from `modules[0]` (216); `between()` uses `m = S.module || 2`, `n2 = S.modules[m - 1].questions || 22`, Math tools line (632, 642-643); `timeUpScreen` `m = final ? module : 1` and "Continue to module 2" (619, 623); `handIn` "Handing in module 1…" (581-582); `snapshotM1` names and `cellsM1`/`paceM1` (539-556, 651-663).
- test.js position key: `satf.posmod.{sid}` compares `S.module` numbers to reset position (443-447); a module index that restarts per section would not reset.
- test.js report label `Module m · Qi` (489) and `report_later` qid regex `/^m(\d)q0?(\d+)$/` (739): no subject in qids.
- test.js `done()` (691-761): one estimate on `UI.scale` 200-800 (714-715), one route chip, one gate line.
- test.js runner title is `S.section`, short `M${module}` (448); finish label "Move on to module N+1" (455) is generic.
- `UI.between` (runner.js:2943-2996): module-2-only copy, 60 s from test.js:665, no section break.
- tests.js: "Module X of 2" (338, 406), counts default 20/22 (337, 407), `lastM1` needs `asked === 22` (326), sitting row `M1 x/y · M2 x/y` from `modules[0..1]` (919), miss chips keyed `M${m.n}` and report link `q=M${n}-${p}` (855-859), CSV "Math M1.." (1044), next-card meters (333-335).
- start.js: `count`/`seconds` per kind (112-130), KIND table (35-45), no subject in any body.
- compare.js: `m1`/`m2` from `modules[0]`/`modules[1]` (35-36), LABELS Module 1/Module 2 (46-47).
- talk.js: slots m1/m2u/m2l only (22-25), qid `m1q` (196).
- results-ui.js: Peek strips grouped by `it.module` only, with a mock fallback that splits by `module1.asked` (310-323); Peek gauge `subject: 'math'` (301); in-progress "Module n" for mock (367); player opened without `sitting` (340).
- report/page.js: `modGroups` (1180-1184), `drawPace` (1505-1506), `clockReplay` (1543) keyed by module only; `dur = clock_ms / modules.length` (1551) assumes equal modules; `modLine` "of 35:00" and route only for module 2 (1176-1178); module filter by number (1000, 1048); `sitting: { subjects: 1 }` (1663); route line only for `kind === 'mock'` (606); CSV has no subject (1682).
- results/page.js: one "Math estimate" hero on /800 (258-273), Skills filtered to math (607), domain table assumes Math sections (432-438).
- Total score: tests.js:144, report/page.js:627-648, results/page.js:263, charts.js:664-677 all treat R&W as a self-entered number beside the measured Math band.
