# R&W parity map: practice, drills, challenge, review, Today, Up next, daily

Read-only audit, 2026-10-22. Repo: /Users/workingmyassof/freshbot/satbank (working tree as found, uncommitted changes included).
Line numbers are from that working tree.

## 0. How this was measured

- `drill.preview` (writes nothing) was swept for every `source` in `drill.SOURCES` and every `pool` in `drill.POOLS`, for `subject: "rw"` and `"math"`, against a scratch SQLite (`SATF_DB` in scratchpad/map, fresh learner with no history). Raw output: `scratchpad/map/sweep.out`. Scripts: `sweep.py`, `probe2.py`, `probe3.py` (same folder).
- Bank facts (from `satbank/topics/rw.py` through `registry.generate`):
  - 10 R&W topics `rw_<skill>`, 152 templates, 3,433 items (all `mcq`, all with `text`). 46 items carry a figure, 142 a table.
  - Items per template: min 1, median 19, max 110. 3 templates have under 3 items, 12 under 5, 40 under 10.
  - Templates mix tiers (rw.py:79-81 interleaves easy/medium/hard). 102 of 152 lack at least one tier, 43 are single-tier, 44 have no hard, 58 no easy. `blueprint.kinds()` survey (18 seeds) matches the real tiers for all 152.
  - Per skill and tier: cross-text easy has only 22 items, inferences easy 35; words in context easy 253.
  - `blueprint.lookalikes` returns something for only 8 of 152 R&W templates (reasons are per-item `why_wrong` prose).
  - No R&W template has `steps`, `desmos`, `latex_choices`, `spr` form, `ask` axis or an official (material/keys) mapping.
  - `cb_count` keys line up: `_catalogue("rw")` gives every R&W skill its College Board count (boundaries 213 ... words in context 261).
- Dedupe is real across sessions: `Builder.signature` uses `question_hash` for any item with `text` (practice.py:249-253) and the drill stores the same hash (`drill._hash_of`, drill.py:1939-1941) in `practice_seen`. Once a learner has seen every item of a template, `_fresh` returns None for it.

## 1. Cross-cutting root causes (fix these first; most per-feature gaps reduce to them)

RC1. `drill.resolve` defaults `subject` to math and never infers it.
- drill.py:896 `subject = _choices(body.get("subject", "math"), ...)`; drill.py:908 and :914 then 422 any R&W topic/template; drill.py:1083-1084 silently drop R&W queue/items; drill.py:1122-1123 return `no_bank`.
- `again` copies topics/templates/etc. from the old cfg but not `subject` (drill.py:850-859).
- Verified (probe3): `{templates:[rw], source:"twin"}`, `{source:"learn", templates:[rw]}`, `{source:"worksheet", templates:[rw]}` all 422 "too many templates or wrong subject"; `{item:"rw_...:2"}` gives `filters_removed_all`. With `subject:"rw"` the twin body is servable.
- Callers that omit subject (break on an R&W item), in this map's own scope: question.js:1942 (Learn), :1943 (Print 10), :1944 (Twin fallback body `{templates:[t], source:'twin'}`); builder.js:420 "Your last set again" `{again, source:'builder'}`; builder.js:1605 and :1625 (Your sets: Same settings / Rematch / Retake send the TAB's subject, not the row's `r.subject`, so an R&W row on the Math tab fails, `no_bank` or 422); palette.js:188-274 (every body, no subject; palette reads `/api/map`, Math only). Sections 5 and 6 list the Today, Up next, Review, walk, sheet and quick callers.
- Shared fix (one place): in `resolve`, when `subject` is absent take it from `topics`/`templates`/`item`/`again`/`rematch`/`retake`/`from_session` cfg/`ids` (trap or attempt rows), else math. `deps.subject_of` already answers for a topic or template.

RC2. `progress.coach` called without subject inside `resolve`.
- drill.py:1110 (`source:"quick"`) and drill.py:1117 (`coach`, `today`, `next` with no topics) call `progress.coach(learner, ...)` with the math default. Sweep: `rw source=quick|coach|today|next` -> `no_bank`; the same for math -> servable.
- Fix: pass `subject=subject`.

RC3. Stale "R&W bank is coming" code paths.
- api_practice.py:104-124 `_rw_bank` and its call at :180-181: dead (`_catalogue("rw")["types"]` has 152). Note text "R&W practice questions come with the R&W bank".
- builder.js:280-328 `rwPanel` (and `#rw` toggling at :272-278): dead since `bank.bank` is true. Its "Log a missed R&W question" form posts `{subject, skill, letter, cb_id|text}` to `/api/mistakes/log`, whose model requires `template` (api_bank.py:250-258), so it would 422 anyway. Copy "waits in Review's Outside list for the R&W bank" (:322).
- builder.js:83 `REASON.no_bank: 'That subject's bank is coming'`; drill.py:907, :1121, :1123 still raise `no_bank` for R&W. These now fire for real R&W gaps (RC1, RC2) and tell the student the bank does not exist.
- drill.py:363-369: an R&W College Board id gives `rw_bank_pending` (verified). drill.py:467 `cb_index` sets `topic=None` for R&W, so `_index_twins` (drill.py:473-483) cannot twin an R&W id.
- drill.py:194-197 `_rw_serve` ponytail note "1 to 3 items a type" is stale (median 19).

RC4. Math-only modules that gate builder features.
- `estimate.gains` returns None for any subject but math (estimate.py:493). Effects on the R&W tab: "Biggest gains" preset always "Needs 30 answers" (builder.js:465), no "points on the table" (builder.js:243), no `gain`/`per_test` in skill rows and record, finish "What this set moved" has no gain (drill.py ~3487).
- Habits are Math's: api_practice.py:329 (`_habits` only for math), drill.py:662-665 `habits.families(subject)`; sweep `rw source=habit` -> 422 unknown habit family.
- Official twins and `has: official`: material/keys is Math only (drill.py:430-448, api_bank.py:37-45). Sweep: `rw has official` -> `no_official_types`; builder shows "Only types built from official questions (0 of 152)" on the R&W tab (builder.js:1307).
- Desmos: `has: desmos` and the Desmos preset (builder.js:478) can never serve R&W.
- `estimate.route_of` uses Math's module-1 tier mix (estimate.py:602-613); `blueprint.TIERS` tier mixes (`tier_mix`, "Like the test" plan) are Math's 22-question mixes, applied as-is to R&W (drill.py:762-768).

RC5. Copy says numbers everywhere (R&W items are passages, not numbers).
- Server: drill.py:1868 repair why "The same trap with new numbers"; drill.py:3170 hint text "Struck A: that's what you get if you {reason}" (R&W `why_wrong` is a full sentence, e.g. "A comma alone cannot join the two independent clauses", so this reads broken).
- Web: question.js:1924 twin menu "same kind, new numbers", :2048 "Same kind of question, new numbers", :2068/:2072 "Same question type, new numbers"; kit.js:2739 has `sub_rw: 'same kind, new text'` for the Twin verb only, other verbs (twin_set, twin_test, learn "on new numbers") have no R&W copy (kit.js:2740-2744). session.js:273, :306, :308, :322, :614; builder.js:1119-1122 pool rows "Fresh numbers on ...", :1124 "Generated for you now", :1137, :1276-1277, :1284 "never counted in Math", :1603, :1622-1623, :1631.

RC6. Fixed items: exhaustion and key leaks (R&W-only traps).
- A twin, repair, final round, review slot, Learn ladder, worked example, print, rematch slot: each consumes an unseen item of a template with 1 to 110 items. When `_fresh` finds none, `_pick` falls through; at the end `next_question` returns `{done:true, exhausted:true}` (drill.py ~2479-2480) and session.js:439 shows "We ran out of unseen questions for these settings". No R&W-specific fallback to a sibling template, except `_rw_serve` for redo/checks (drill.py:194-204).
- Hint ladder leak: `hint` rung "example" calls `_example(q["key"], 0)` with no `avoid` (drill.py:3174). For an R&W template that is a fixed item (`seed % n`), so with probability 1/n it is the question on screen, shown with its answer (3 templates have n under 3). The worked-first path does pass `avoid` (drill.py:1891) and marks the example seen (drill.py:1933-1937); the hint path does neither, so a hinted example can also be served later as a "new" question.
- The hint example payload omits `text` and `table_title` (drill.py:3176-3177 key list), so an R&W worked example in the hint shows a stem with no passage.
- `/api/types/{template}/example` (api_bank.py:180-206, used by runner.js:3898 "See one solved first" and quick.js:420) also picks a reserved-seed item without marking it seen and without avoiding the current item.
- Printing burns items: session print walks `/next` with `skip:true` until the set is full (session.js ~636-644), which commits (marks seen) every item; question.js "Print 10 with key" asks 10 of ONE template.

RC7. The subject choice exists only in the Practice builder, and is not remembered.
- builder.js:100 reads `?subject=rw`; builder.js:264-271 the Math / Reading & Writing seg rewrites the URL. No pref holds a chosen subject (prefs.py has none; `prefs.practice` is per-subject settings, not a choice). The builder keeps ONE settings object across tabs (`B.st`): fromPrefs reads only `practice.math` for zone, review_mix, review_from, cover, words_mix, final_round, hints, two_passes (builder.js:114-117) and only `worked_first` from `practice.rw` (:118-119); toPrefs writes the R&W tab's changes to `practice.math` (:126-129). Presets are stored and listed under `practice.math.presets` on both tabs (builder.js:481, :574-591); a Math preset loaded on the R&W tab selects nothing (loadBody filters unknown templates, builder.js:1489).
- Server side, `_prefs_defaults` reads `practice[subject]` (drill.py:390-411) and the Learn/Build/Test mode bundles apply to math only (prefs.py:369), so every R&W set started outside the builder (coach, plan, next, gain, probe, palette sources) runs on `practice.rw` server defaults (zone stretch, review_mix 20, ...) that no page lets the student edit.

## 2. Practice builder: modes and presets

Server side: R&W works when `subject:"rw"` is in the body (sweep: one skill, full mix 54 blueprint at 64.2 min, timed pace with R&W budgets 49/71/94 s, custom clock, sprint, tier_mix module2_upper, ramp, adaptive, zone For me, tiers hard only (12 of 16 boundaries types), probe, finish, learn, untried, review_mix, cover). Web: builder.js loads `/api/bank?subject=rw` and runs the same tree (builder.js:1699-1723).

| Feature | R&W today | What is Math-specific (file:line) | R&W parity needs |
|---|---|---|---|
| By skill / by type (tree, Try one, Practise this type) | works | Try one menu offers every tier the type has (builder.js:909); grid-in try hidden correctly (:910). Skill record shows "With/Without Desmos", "On the test about N of 44" (builder.js:862-865) but they stay empty for R&W (no calc, no gains). | Nothing blocking. "of 44" should read 54 (R&W section) when gains exist for R&W. |
| Learn (type row) | math-only in UI | builder.js:924 hides Learn on R&W; server works (`rw learn one template` servable, but `count` defaults to 10 slots, drill.py:722-733). In-set ladder (/more ladder, drill.py:3042-3051) runs for R&W from the twin menu. | Decide: show Learn for R&W (example is a bank item with its key, opt-in like worked_first) or hide the ladder too. Pass `count: 3`. Watch exhaustion on small templates. |
| Check my level (skill panel) | math-only in UI | builder.js:872 `if (B.subject === 'math')`. Server probe works for R&W (sweep). The preset "Check N skills I haven't tried" is offered on both tabs (builder.js:475), so the two disagree. | Show the button on R&W too. |
| Mentor's pick | works | `bank.coach` is subject-aware (api_practice.py:338). | none |
| Weakest 3, Plan focus, Probe untried | works | Plan focus matches `focus` domain names; R&W domains only match if Plan stores them (out of scope). | Check Plan stores R&W domains. |
| Biggest gains | math-only | estimate.py:493. | R&W gains model (RC4). |
| Full section mix | works | builder.js:552 sets 54 for R&W; tier plan uses Math module mixes (drill.py:762-768). | R&W module tier mix in `blueprint.TIERS`. |
| Harder module's mix (route) | partial | Route bar needs `route.text`/`line` which `route_of` never returns (estimate.py:612-613; builder.js:249-254), so it never shows for either subject; the tier mix is Math's. | R&W route numbers; module mix. |
| My mistakes / Fix (redo pool) | works | R&W misses are unnamed per type (`miss_norm` returns "" for `text`, progress.py:96-102); `_rw_serve` serves the type or another type of the skill (drill.py:194-204, 248-262). | Copy "Fresh numbers on my open mistakes" (builder.js:1119). |
| Missed / Marked / Saved (seen, marked, saved pools) | works | Fresh-twin default for Seen and Saved (drill.py:1006) means another item of that template, which can run out. | Copy "Fresh twins ... new numbers" (builder.js:1137). |
| Due for review (review pool), Check-ins (checks) | works | `warmup_candidates(subject=)` (drill.py:269, 1072). | none |
| Untried | works | sweep: count 120. | none |
| Solve first (preset) and "Solve before seeing choices" (cover) | partial | Preset hidden for R&W (builder.js:474) but the cover control shows (builder.js:1253-1256) and the server accepts it. For prose choices question.js covers without a typed field ("work it out, then reveal", question.js:768-779), which suits R&W (predict, then look). | Either show the preset on R&W with R&W copy or keep it hidden; make the two consistent. |
| Top habit | math-only | api_practice.py:329; drill.py:662-665. | R&W "habits" would be distractor families (spec decision, none in the bank today). |
| Desmos drills, has desmos/steps | math-only by nature | builder.js:478, :1306; drill.py:521-537. | Hide on R&W. |
| Only official types | math-only | builder.js:1307 shows "0 of 152". | Hide on R&W or map R&W CB ids (RC3). |
| Mix-up order, "Mix it up with look-alikes" | partial | Works only for the 8 R&W types with lookalikes; else `no_lookalikes` (sweep). builder.js:1290-1293 offers Mix-up for every R&W pick. | Hide when the pick has no lookalikes, or define R&W lookalikes by skill/subtype instead of shared reasons (blueprint.py:162-175). |
| Format (MC / grid-in) | works (hidden) | builder.js:1302 hides the seg; `fmts()` forces mcq (builder.js:169). paintFormatHelp still writes "0 of N selected types make grid-ins" on R&W (builder.js:1322-1326). | Hide the help line on R&W. |
| Timed: pace / custom / box; Speed drill | works | R&W budgets in `TIER_BUDGET["rw"]` (drill.py:103-104). Speed-drill entry points live on Today and Plan (fork B). | none here |
| Feedback: instant / retry / end (incl. "retry wrong") | works | subject-agnostic. | none |
| After a miss: repairs next/later/end, Final round | works, with traps | Repair = another item of the same template (`_fresh` with the R&W miss norm "" ). Copy (RC5). Exhaustion on small templates (RC6). | R&W copy; fall back to a sibling template of the same skill like `_rw_serve`. |
| Mix in reviews | works | drill.py:776-797. | none |
| Mix in due SAT words | math-only (inverted) | drill.py:799-813 adds word cards only when `cfg["subject"] == "math"`, yet the words are R&W vocabulary. Builder shows the control on R&W with copy "never counted in Math" (builder.js:1282-1284). | Allow for R&W (most natural home), or hide on R&W. |
| Worked examples (worked_first) | works (opt-in) | `practice.rw.worked_first` default False (prefs.py:157); drill passes `avoid` and marks seen (drill.py:1883-1892, 1933-1937). The hint "example" rung does not (RC6). | Fix the hint path; include `text`. |
| Hints before I answer | partial | Rung "strike" copy broken for R&W (drill.py:3170); rung "example" can leak the key and lacks the passage (RC6). | R&W strike copy ("Struck A: {why_wrong}"); fix example. |
| Calculator and reference sheet in a set | math-only tools shown | session.js:176-215 never passes `calc:false`/`ref:false`, and runner.js:1292 defaults both on, so an R&W set shows Desmos and the Math reference. Tests pass `S.calculator` (test.js:452). | Pass `calc: st.subject !== 'rw', ref: st.subject !== 'rw'` (or per question when `q.text`). |
| Twin axes inside a set | partial | session.js:190 always offers `['easier','harder','grid','ask']`; question.js:1922-1935 lists them unfiltered. For R&W `grid` and `ask` always 409 (drill.py:3071-3093); easier/harder use `blueprint.siblings` (works). | Send axes from the item (`q.subject`/type `axes`), drop grid/ask on R&W. |
| Rematch / Retake / New set same settings / Share / Print (session page) | works | session.js create() adds `st.subject` (session.js:66). Copy "new numbers" (RC5). Print walks the whole set (RC6). | Copy; print burns items. |
| Your sets (list) | partial | `/api/drill` listing has no subject filter (drill.py:3675-3732); rows carry `subject` (drill.py:3671). Builder row actions send the tab subject (builder.js:1605, :1625), so cross-subject rows fail. | Use `r.subject`, or filter the list by tab. |
| Ready rows / Up next in builder | math-only in UI | builder.js:274 and :439 hide `#ready` on R&W; "Your last set again" body has no subject (builder.js:420). | Show on R&W once Up next has R&W items (fork B: next.py is Math-only). |
| Search / command line (`UI.parseSet`) | works | Types come from the current bank (builder.js:621). | none |
| Deep links `?subject=&skills=...` | works | builder.js:1452 keeps `subject`; deepLink sets it (:1501). `?cb=` official ids for R&W hit `rw_bank_pending` (RC3). | RC3. |
| See the traps (type menu) | math-only | `UI.types()` reads `/api/shell/catalog`, built from `api_bank.types()` with the math default (api_shell.py:336; ui.js:820-833), so an R&W type finds no traps and says "Its wrong choices are near values, not named traps" (builder.js:930). | Include R&W in the catalog, or R&W copy. |

## 3. Drill server: per action (server/drill.py, server/api_practice.py)

| Action | R&W today | Evidence and Math-specific detail |
|---|---|---|
| POST /api/drill, /preview with subject rw | works | resolve (drill.py:817-1149); sweep. |
| ... without subject | broken | RC1. |
| source quick / coach / today / next with no topics | broken for R&W | RC2, drill.py:1110, :1117. |
| source start | works, no domain opener | drill.py:1113-1115 handles subject; drill.py:1653-1662 one-per-domain opener is math-only. |
| source probe, finish, learn, sprint, due/warmup, gain, palette, plan, skill, fix, result | works with subject and topics | sweep (most need topics/templates; with none they give `no_bank` for R&W vs `no_templates` for Math, a misleading reason). |
| source habit | math-only | drill.py:662-665. |
| pool official / `?cb=` | math-only | drill.py:353-373, 608-628, cb_index topic None (drill.py:467). |
| /more same (Another like this, Practise this trap) | works, runs out | drill.py:3052-3058; `want` for R&W is a per-item sentence, never offered by another item, so it falls back to a plain item (drill.py:1384-1390). |
| /more easier, harder | works | blueprint.siblings (blueprint.py:178-200). |
| /more grid, ask | always 409 on R&W | drill.py:3071-3093. |
| /more ladder (Learn this type) | works | drill.py:3042-3051. |
| /hint | partial | RC5 strike copy, RC6 example leak and missing passage. |
| /calc (Desmos log) | n/a | Math tool. |
| /word | math sets only | word cards only planned for math (drill.py:799-813). |
| /final (final round) | works, runs out | slot cards on fresh seeds (drill.py:1437-1477). |
| /finish -> next | works | api_practice.py:619-620 keeps the set's subject for Keep going; finish's gains are math-only (RC4). |
| GET /api/map | math-only | api_practice.py:38-44 `progress.board(learner)` and `coach` with math default; used by palette.js:76 and results/page.js:607. |
| GET /api/bank?subject=rw | works | api_practice.py:177-345; `words` attached for R&W (:345). |
| GET /api/drill (Your sets), /api/history | no subject filter | drill.py:3675; api_practice.py:408-429. |

## 4. Bank browser (server/api_bank.py)

| Endpoint | R&W today | Notes |
|---|---|---|
| GET /api/types?subject=rw | works | api_bank.py:82-87 (422 for other values). |
| GET /api/shell/catalog (palette, quick sheet, traps sheet) | math-only | api_shell.py:336 calls `types()` with the math default. |
| GET /api/types/{template} | works | `has` hard-coded `{steps:false, desmos:false}`; `related` = lookalikes (8 of 152 R&W). |
| GET /api/types/{template}/example | works, leaks | RC6: reserved seeds cycle onto real items, not marked seen. |
| GET/POST /api/types/match, /match/pick | math-only for ids | `_official()` is material/keys (Math); an R&W CB id returns `via: none`. Text match ranks all types (no subject filter). `match/pick` maps a letter to a reason by index `(ord(letter)-65) % len(reasons)` (api_bank.py:175), meaningless for R&W per-item reasons. |
| POST /api/mistakes/log (outside mistakes) | works only with a template | Requires `template` (api_bank.py:250-258); records an R&W trap with norm "" if `reason` empty. The dead builder form (RC3) does not send `template`. |
| A /types/ page | missing for both | palette.js:231 links `/types/?t=...`; no `web/types/` exists (404). |

No web page is a "bank browser" today beyond the builder tree; the builder tree is the browser, and it works for R&W.

## 5. Review, mistakes, walk, sheet, print (full notes: scratchpad/map/review-notes.md, probes probe_review*.py)

Picture: the Review SERVER is already subject-aware (`_subject`, api_review.py:343-346; `subject: str = "math"` on counts, due, snooze, redo, marked, saved, fixed, history, history.csv, ledger, calibration, trapsheet, api_review.py:379-1022; probe: `/api/review/redo?subject=rw` lists the R&W mistake, without subject it lists nothing). The PAGES never send `subject` (zero hits for "subject" in review.js, walk.js, sheet.js, print.html, item.js), and every drill body they post omits it (RC1). Net: Review is Math-only in practice.

| Feature | R&W today | Server | Page / Math-specific |
|---|---|---|---|
| Counts strip, tab counts | math-only (page) | api_review.py:378-381 ok | review.js:133 no subject. `recovered_month`, `open_week_delta`, `worksheets_waiting` are not subject-filtered at all (review.py:785-821). |
| Due today list, Snooze | math-only (page) | review.py:547 `due(subject)`, frozen per subject (review.py:489-499); api_review.py:395-403 | review.js:140, :862 no subject |
| Start review / All / Fix N | math-only | body `{source:'due', box}` -> drill.py:1071-1078 (math default). `review.resolve_drill` (review.py:644-717) is dead (no caller) and math-pinned. | review.js:165-175. "Fix N" never includes open mistakes (shared bug, both subjects). |
| Redo (Mistakes) list | math-only (page) | api_review.py:406-505 ok | review.js:494-510 `listPath` no subject |
| Fix / Fix these / Worth the most / blind spots | math-only | pool redo reads `open_traps(subject=math)` without body subject (drill.py:246) | review.js:1914-1920, :1735, :1420 |
| Twin this set / Same questions again / Retake (Marked, Saved, History) | math-only | items dropped (drill.py:1084) | review.js:1932-1945, :1744-1756, :1189 |
| Check these now (Fixed) | math-only | checks query unfiltered then dropped (drill.py:246-249, :1083) | review.js:1963 |
| Pane: Another like this, easier/harder | math-only | 422 wrong subject (probe) | review.js:2051-2057 `twinBody` |
| Pane: The very same question | math-only | 409 filters_removed_all (probe) | runner.js:3798 default `again` body |
| Walk (start, Try again, Prove it) | math-only, runs out | api_review.py:1092-1137 creates through `drill.create` with no subject (:1129); all-R&W walk 409 (probe) | walk.js:58, :64, :140, :156-162; a 409 shows as "Nothing to walk right now" (walk.js:69-72). Prove pins the miss tier; a 1-item type gives 409. |
| Walk step 2 "name it" | broken even with subject | `called = diag == norm` (api_review.py:1076) and an R&W norm is always "" (progress.py:96-102), so R&W is never "named" | "Arithmetic slip" choice (api_review.py:886, walk.js:34) |
| Spot the trap | math by design | 409 for UNNAMED norms (api_review.py:1231-1232) | review.js:1405-1408 |
| Habits, Trap gauntlet, Drill this habit | math by design | habits.families Math (habits.py:81-83) | review.js:905-907, :1371-1384 |
| Cause fixes: Speed drill, Careful set, Read the ask, Learn this type | math-only (no subject) | servable for R&W with subject | review.js:1394-1399; "Grid-in entry · 8" (:1397) Math by nature |
| Right but slow / Fluency sprint | math-only | history pace part subject-aware | review.js:1659-1666 |
| Final check (exam week) | math-only | trapsheet subject-aware | review.js:1521-1524 |
| Your rules card | math-only | `/api/bank` default math | review.js:1540 |
| Ledger, calibration | math-only (page) | review.py:918, :978 ok | review.js:416, :1434 |
| Print worksheet (Redo/Saved) | math-only | 409 without subject | review.js:1779-1786 |
| Worksheet sheet `/review/sheet/` | works once a sheet exists | `/drill/{sid}` | sheet.js:92-120 A-D sheet, key via `UI.workspace` renders the passage (sheet.js:243); "Print another version" `{again: sid}` (sheet.js:196) loses subject (`again` does not copy it, drill.py:855-857). |
| Print: trap sheet | math-only (page), leaks items | trapsheet calls `api_bank.example` (review.py:868-875): reserved seed lands on a real R&W item, printed with its key, not marked seen | print.html:164 no subject; example renders the passage (print.html:139) |
| Print: error log | math-only (page), wrong labels | `/review/redo` | print.html:200 no subject; print.html:110 "Grid-in: a wrong value" would label every R&W row (see below) |
| Item detail `/api/review/item` | works | passes `text` (api_tests.py:39-40) | renders via UI.workspace |
| Dismiss / restore / reopen / add | works | id-based (api_review.py:283-340) | |
| Legacy `/api/mistakes` | math-only | api_review.py:63-74 (Math topic names); used by tests/start.js:468 | |
| `/mistakes/` | redirect | api_review.py:55-60 307 to `/review/?tab=redo`, keeps the query (so `?subject=rw` would survive) | web/mistakes/index.html:18-19 static fallback |

Review-specific R&W traps (beyond the missing subject):
- R&W misses are typed "gridin": `progress.trap_kind("")` returns "gridin" (progress.py:92-93) and every R&W norm is "". Used at review.py:265-267, api_review.py:441, :645; shown as "grid-in entry" (review.js:952), Kind filter Grid-in (review.js:441), error log "Grid-in: a wrong value" (print.html:110). Probe: `kind: gridin` on an R&W Redo row.
- One R&W trap per template (norm ""), so a second miss on a type is `hits: 2` on the same trap; "group by mistake type" (api_review.py:486-490) puts all R&W traps in one group.
- R&W trap labels are item subtypes (`practice.skill_of(q)`, progress.py:385-386; rw.py:37 `subtype`): 1,724 distinct strings, some passage-specific (probe: "T1 link: a skeletal condition common among the crew ..."). An outside-logged R&W miss gets the blueprint majority label instead (api_bank.py:283), so one type reads two ways.
- Fixed tab "tiers proven" counts same-template clean answers only (api_review.py:638-641), but an R&W trap closes on clean answers anywhere in its skill (progress.py:490-493).
- Topic filter and short names come from `UI.TOPICS`/`UI.DOMAINS` (19 Math skills, ui.js:652-679; review.js:61-62, :421-424); `UI.RW_SKILL` exists (ui.js:681-687) but is unused here. Format filter MC/Grid-in (review.js:431), "MC" bit (review.js:947, :1010, :1029).
- Math empty-state samples (review.js:751-756, `/types/rr.partner/example`).
- Outside log: R&W CB ids never match (`_match_id` reads material/keys only, api_bank.py:36-45, 88-99); `/api/outside/misses` is advertised (api_shell.py:281, quick.js:673-674) but has no route.

## 6. Today, Unlocks, Up next, daily question, challenge, /s, quick sheet (full notes: scratchpad/map/today-notes.md)

Shared: nothing in this cluster injects `subject` (index.html:646-655 `drill()`/`go()`, ui.js:1289-1295 `UI.start`, question.js:1975-2090 twinRun), so RC1 and RC2 apply everywhere. `progress.due_rechecks` has no subject filter (progress.py:1098-1109). Legacy `drill.create(learner, sid, topics, ...)` used by the challenge and /s writes no subject (drill.py:2043-2065). Client topic names `UI.TOPICS/DOMAINS/TOPIC` are Math only (ui.js:652-679); Today's `TOP(slug)` prints an R&W topic as a raw slug (index.html:512). `UI.question` (ui.js:2940-2964, verified) has no passage; `UI.workspace` does.

GET /api/today (api_today.py:1121-1177) takes no subject and is Math or all-subject block by block: coach :1131; open traps `subject="math"` :1132; gains :1134 (None for R&W, estimate.py:493); domains Math only :204-219; warm-up :334; review counts `"math"` :512; readiness and final-stretch use "44" (:245-269, :1100-1118); stretch coach "of 44" (:643-660); receipt counts all subjects' topics (:965-972) and prints R&W slugs; time_split mixes (:1336-1353); at_risk may pick an R&W check-in and 409 (:945-946). The rw_bank check itself asserts "an R&W mistake never reaches Today" (server/checks/rw_bank.py:79-80), so excluding R&W from Today is current intent, not an accident.

| Today card | R&W today | Evidence |
|---|---|---|
| Up next lead / Study session builder | math-only | sessBody `{source:'next', ...}` (index.html:1034-1037); next.resolve_drill Math (next.py:340-403); "More options" `/practice/?topics=` (index.html:1255-1259) has no subject and the builder reads `skills`, not `topics` (builder.js:1452-1456) |
| See an example first | math-only | `{source:'learn', topics:[coach topic]}` (index.html:1251) |
| Due today: Review, Sweep | math-only | api_today.py:783-814, bodies without subject |
| Due today: Words | works (Words vocabulary) | api_today.py:815-830 |
| Due today: Day's questions | partial | section below |
| Due today: Challenge | math-only | api_today.py:844-846; page uses `/contest/daily` (index.html:656-659) |
| Plan rows | R&W tasks have no Start | plan.py:692-699 ("On your own · Bluebook") |
| Mistakes card (Fix all, row Fix, Twin, Learn it again) | math-only | open_traps math (api_today.py:1132); bodies index.html:1646, :1654, :1665-1666 without subject |
| Mistakes by habit, Trap gauntlet | dead for everyone | `habits.of_learner` missing (api_today.py:258); `gauntlet` has no server branch (only in SOURCES, drill.py:86) |
| Points on the table | math-only | `/today/insights` called without `?subject=` (index.html:740) though the server takes it (api_today.py:1361-1381); grid-in drill `formats:['spr']` (index.html:2043) |
| Pace (Speed drill · 8 in 12:40, Timed set · 10) | math-only | Math module 2100 s (index.html:2072), bodies index.html:2079, :2100 without subject; "Timed set · 10" has no topics and `gain` is not a coach-fallback source, so it likely 409s for everyone |
| Causes | math-only | api_today.py:1368; grid-in drill (index.html:2255) |
| Score / target | math-only by design | "We only test Math" (index.html:2305) |
| Study time split | partial | Math domains only (api_today.py:1333-1353; index.html:2640-2646) |
| Calendar "Redo this day's misses" | breaks on R&W | `{pool:'history', ids}` no subject (index.html:2727) |
| Tests card | math-only | index.html:2849-2930 |
| Words tile | works | index.html:2822-2840 |
| Unlocks strip | partial | `ins.answers` counts all subjects (api_today.py:1371) while gains are Math only, so an R&W-only student reaches "30 of 30" and Points never unlocks (index.html:869-903) |
| Q1 inline preview | dead for everyone | reads `p.first`/`p.blocks` (index.html:1339-1376), preview never returns them |

Up next (`/api/next`, api_shell.py:310-320, no subject; next.py:96-337). Keys already end in `:math` (next.py:111, :132, :137, :213, :226, :269), so per-subject keys were planned.

| Item | R&W today | Evidence |
|---|---|---|
| rest/warm-up, start/diagnostic | math-only | next.py:110-116, :132-137 |
| resume test/drill | works | next.py:118-130, :152-162 |
| plan tasks | Math bodies; R&W none | next.py:178-209 |
| review (due) | math-only | next.py:49-53, :211-218 (review.due default math) |
| checks fallback | breaks on R&W | due_rechecks all subjects, body without subject (next.py:54-66, :219-231) |
| redo (Fix) | math-only | `open_traps(subject="math")` next.py:145, :233-245 |
| habit | math-only, skewed | Math regexes; `_wrong()` counts R&W misses (next.py:75-82, :247-265) |
| probe, skill, warm, untried | math-only | next.py:267-280, :293-301, :307 explicit `== "math"` |
| saved "try a fresh one" | breaks on R&W | next.py:282-291 any-subject saved rows, body without subject |
| qotd | partial | checks the Math MC session only (next.py:318-321) |
| resolve_drill (time box) | math-only | next.py:340-403, :370, :383 |

Daily question: partial. Four slots, math:mcq and math:spr from the generated Math bank, rw:wic and rw:transition from Words vocabulary (daily.py:30-35, 102-104, 138-143; words.py:1355-1394). The written R&W bank never supplies a day's question. Math pick `deps.subject_of(k) == "math"` (daily.py:63-69); `feedback()` subject hard-coded math (daily.py:293-316); `like` twin resolver rejects non-Math slots (daily.py:449-470); save Math only (daily.py:473-485, api_today.py:1634-1656); R&W "5 more like this" links to /words (index.html:1850). Trap: a date-hashed seed on a fixed item can land on one the student already met; a 1-item template has no twin; past-days strip assumes math slot keys (daily.py:423-432).

Challenge: math-only. Legacy `/api/challenge` uses `MIX` (Math domains), `SPR_AT=(4,8)` grid-ins and Math seconds (challenge.py:18-58, api_compete.py:28-57), started by legacy `drill.create` with no subject. Today's card runs `/contest/daily` whose `compete._daily_slots` reuses the same MIX (compete.py:194-205). Parity: an R&W mix 3/3/2/2 from RW_BLUEPRINT (progress.py:58), no grid-ins, R&W budget, `subject` on the contest (`_insert` already takes it, compete.py:179-185). Trap: each entrant gets a fresh twin of each slot; thin R&W supply per template and tier trips "daily twin supply is too small" (compete.py:202-203). No subject switch on web/challenge.

/s shared set: partial. kind `set` redirects to `/practice/?share=` (s/index.html:123); kind `items` starts via `sets.start` -> legacy `drill.create` with no subject (sets.py:785-803), so budgets and Keep going treat it as Math; inline help renders with `UI.question` (s/index.html:308), no passage; topic links `/practice/?topic=` without subject (s/index.html:172, :325), which the builder ignores.

Quick sheet (quick.js): math-only. Quick question `{source:'quick'}` no subject (quick.js:176-180, RC2); "Practise {skill}" (quick.js:157, :472) without subject; Log a mistake uses the Math shell catalog (api_shell.py:335-340), copy "Math question IDs" (quick.js:330), Math `UI.TOPICS` picker (quick.js:426-436); text match can find an R&W type (api_bank.py:142-155) but the follow-up drills `{pool:'redo', ids, source:'outside'}` (quick.js:572, :582) carry no subject; `example()` and fallback use `UI.question` (quick.js:116, :212), no passage.

## 7. Subject picker inventory (all of web/, scope pages marked)

| Page | How the subject is chosen today |
|---|---|
| Practice builder `/practice/` (scope) | Seg Math / Reading & Writing (builder.js:264-271) plus `?subject=rw` (builder.js:100). Not remembered (URL only). |
| Practice session `/practice/session/` (scope) | Inherited from the set's cfg (`st.subject`, session.js:66, :87). No switch (correct). |
| Today `/` (scope) | none. Only the Day's questions tab strip splits Math and R&W slots (index.html:1708-1709). `/api/today/insights?subject=` exists server-side but the page never sends it (index.html:740). |
| Up next (shell, sidebar, Now strip) (scope) | none; `/api/next` takes no subject. |
| Challenge `/challenge/` (scope) | none. |
| Shared set `/s/` (scope) | none; follows the shared items but is not recorded. |
| Quick sheet (quick.js) (scope) | none. |
| Review hub, walk, sheet, print (scope) | none on the page, though nearly every `/api/review/*` GET takes `?subject=`. |
| Mistakes `/mistakes/` (scope) | redirect to Review, keeps the query string (api_review.py:59). |
| Palette (Ctrl+K, palette.js) | none: Math only via `/api/map`. |
| Results `/results/` | Math only: results/page.js:607 filters `topics` to math. |
| Results report `/results/report/` | per sitting (`R.subject`), no switch. |
| Me | Math and R&W targets shown side by side (me.js:472-473), no switch. |
| Compete leaderboard | `?subject=` link only, no control (leaderboard.js:13, :117). |
| Tests `/test/` | the sitting's section, no switch. |
| Words | its own R&W area, no subject concept. |

Consistency gap: one tab control on one page, URL-only, while the server already takes `?subject=` or `body.subject` almost everywhere. A remembered `subject` (pref or `localStorage satf.subject`) read by the builder, Today, Review and Mistakes would make the choice follow the student.

## 8. Parity checklist, in the order that removes the most breakage per line

1. `drill.resolve` infers `subject` when the body has none (RC1): from `topics`/`templates` (`deps.subject_of`), `item`, `ids` (item pairs, attempt ids, trap ids), `again`/`rematch`/`retake`/`from_session` parent cfg; add `subject` to the `again` copy list (drill.py:855-857); explicit `subject` still wins, a mixed body stays a 422. This alone fixes every Review, walk, pane, runner, sheet, Today, Up next, quick, palette and builder body listed in sections 2, 5, 6.
2. `progress.coach(..., subject=subject)` at drill.py:1110 and :1117 (RC2).
3. Replace stale `no_bank` / `rw_bank_pending` reasons (drill.py:907, :1121, :1123, :369; builder.js:83) with real reasons; delete `_rw_bank` (api_practice.py:104-124, :180-181) and `rwPanel` (builder.js:272-328) (RC3).
4. One remembered subject (pref or `satf.subject`) plus `?subject=` read by: builder (exists, builder.js:100), Review (send `subject` on every GET, review.js, walk.js, sheet.js, print.html), Today (`/api/today?subject=`, `/today/insights?subject=` already exists), Up next (`/api/next?subject=`, keys already end `:math`), quick sheet, challenge. Builder: keep per-subject settings (`practice.rw.*`, not one `B.st`), per-subject presets.
5. Fixed-item safety (RC6): hint example `avoid` + mark seen + include `text`/`table_title` (drill.py:3174-3177); `/api/types/{t}/example` and the trap sheet example must avoid the current item and mark what they show; twin / repair / final / prove / again fall back to another type of the same skill and tier when the template is spent (reuse `_rw_serve`, drill.py:194-204); print should not walk a whole set of one small template.
6. Math tools off in R&W sets: `calc:false, ref:false` in session.js:176 when `st.subject === 'rw'`; drop `grid` and `ask` axes (session.js:190) for R&W; hide Desmos, official, habit, solve-first/format help controls on the R&W tab; allow word cards in R&W sets (drill.py:804) or hide the control.
7. R&W copy: "new passage" / "new text" instead of "new numbers" (RC5 list, plus review/walk/sheet/runner lines in section 5); R&W strike-hint copy; "of 54" not "of 44".
8. R&W-specific models still missing (bigger work, decide scope): `estimate.gains` for R&W (estimate.py:493) which unlocks Biggest gains, points, Today's Points card and Unlocks; R&W tier mixes in `blueprint.TIERS`; R&W daily question slot from the bank; R&W challenge mix; R&W trap kind (not "gridin", progress.py:92-93) and one stable label per type; R&W lookalikes for Mix-up; R&W CB ids through `cb_index` (drill.py:467) for official twins and outside logging.
9. Client names: an R&W entry in `UI.TOPIC`/`UI.DOMAINS` (or use `UI.RW_SKILL`) so Today, Review filters and chips stop printing raw slugs; shell catalog (`api_shell.py:336`) includes R&W types so palette, quick sheet and "See the traps" know them.

## 9. Notes on this audit

- Trainers: the Route-up and 700+ gauntlet trainers live in Tests (web/tests/start.js:43-60, web/test/test.js:693-787), outside this map. The builder's only trainer-like control is the "Practise the harder module's mix" route preset (builder.js:249-254, :560), which is servable for R&W but uses Math tier mixes and never shows because `route_of` returns no text (section 2).
- Spot-checked fork claims against the code: `trap_kind("")` returns "gridin" (progress.py:92-93); `sets.start` calls legacy `drill.create` with no subject (sets.py:796); `habits.of_learner` is called (api_today.py:261) but not defined in server/habits.py; `UI.question` has no passage (ui.js:2940-2964).
- Read-only: all probes used scratch databases and outboxes under scratchpad/map. During the audit web/assets/runner.js (14:55), server/s9.db, server/satfreshman.db-shm and a server/outbox .eml changed; none came from these probes (another process). runner.js line numbers above were re-read after that edit.
