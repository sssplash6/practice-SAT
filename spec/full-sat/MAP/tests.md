# Tests, mocks, diagnostic, papers, results and scoring: Math-only inventory

Read-only map of /Users/workingmyassof/freshbot/satbank as of 2026-10-22 (uncommitted working tree).
Line numbers are from the current files. "API" = server/api_tests.py unless named.

## 0. Headline facts

1. Not one test kind can be R&W today. Every sitting is created with subject "math": `_new` cfg
   `"subject": "math"` (API:1675) and `_insert(..., subject="math")` default (API:1505); nothing ever
   passes another subject. The `/api/mock/new` body (`NewMock`, API:1479) has no subject field.
   The custom builder filters R&W out on purpose (API:1585, 1593, 1600, "tests stay Math for now").
2. The plumbing is half there: `sessions.subject` column (db.py:196), payload `subject` and `section`
   (API:419-424), `SUBJECT_LABEL` (API:53), `modules_list` of `{subject, n, questions}` (API:248),
   papers stored as `{sections:[{subject, module1, module2_lower, module2_upper}]}` (papers.py:4-6),
   `estimate.estimate(learner, subject)` filtering rows by subject (estimate.py:110-133),
   `progress.*(subject=...)` everywhere, `drill.TIER_BUDGET["rw"]` (drill.py:103-104),
   `practice.to_question` carries `text` (passage) and `band` (practice.py:377-379), and
   `PUBLIC_FIELDS` already ships `text` (API:39-40). `cb_percentiles.json` has `math`, `rw` and
   `total` tables (61/61/121 rows), so `estimate.national(..., "rw")` and `"total"` already work.
3. R&W supply for twins/papers/pressure (all of which redraw "the same template at the same tier"):
   152 R&W template codes, median 18.5 items per code (min 1, max 110). Per tier: easy has 0 items
   in 58 codes and exactly 1 in 2; medium 0 in 43; hard 0 in 44 and 1 in 4; median 4-5 items per
   (code, tier). Items are fixed (`seed % n`) and practice dedupe never shows one twice, so a learner
   exhausts a (code, tier) after about 5 draws. Twins (`blueprint.twin` -> `twin_slots` ->
   `draw_matching(tries=40)` then `_fallback` within the topic, blueprint.py:343-368), papers
   (`twin_slots` per learner) and the pressure check (`draw_matching(..., tries=40)`, API:1831) will
   fall back to sibling templates early and fail sooner than Math. Plan for "same skill, same tier"
   twins for R&W, not "same template".
4. Existing bugs found on the way (not just parity gaps):
   * `_tier_bases` (API:514-531) reads every timed attempt with no subject filter, so R&W practice
     attempts made under `timing: pace` already leak into Math pace-plan medians.
   * `blueprint.custom` with `formats="both"` (the default) puts `spr` slots at SPR_AT positions
     (blueprint.py:392-394) and then `draw_matching(..., "spr")` (blueprint.py:435) can never match an
     R&W template, so those slots are silently skipped (`continue`, blueprint.py:440-441). An R&W
     custom test of 22 would come out about 16 long, and each failed slot also `b.keep`s up to 10
     non-matching draws (blueprint.py:227), burning finite R&W items. R&W must force `formats="mcq"`.
   * `estimate.percentile` peers by `(kind, mock_id)` only (estimate.py:181-185, 200-206): once R&W
     sections exist, Math and R&W sections are ranked against each other. Same pooling in
     `kinds_rows` crowd (API:2046-2054), `gate_summary` (API:2104), `levers` (API:2138),
     `recommended` (API:2424), `habits` (API:2202), `_moments` "first_upper" (API:1229-1232).
   * `papers.ratings_for` hard-codes `m1 >= 14` (papers.py:290) instead of
     `ceil(ROUTE_UP_AT * len(module1))`. `_route`/`gate_of` are proportional and fine.
   * `_done` calls `estimate.estimate(learner)` with no subject (API:1296), so an R&W hand-in would
     show Math's previous/best band and a Math "Up 30 since" headline.
   * Passage highlights: the runner tags passage marks `at: 'p'` (web/assets/question.js:432) and
     web/test/test.js `marksOut` (85-91) sends it through, but `Mark.at` (API:691) only accepts
     `stem|t:r:c|o:0-3`, so the first passage highlight in a test makes the whole `/state` POST 422.
     Latent until R&W items reach tests; fix by adding `p` to the pattern.
   * R&W practice already shows the Math calculator and reference sheet (practice/session/session.js
     passes neither `calc` nor `ref`; runner defaults them on). Outside this scope, same fix shape.

## 1. Shared Math constants (the fan-out, listed once)

| Where | What | R&W value |
|---|---|---|
| blueprint.py:19 | `MODULE_SIZE = 22` (asserted in `slots`, :88) | 27 |
| blueprint.py:20 | `MODULE_SECONDS = 35*60` | 32*60 |
| blueprint.py:24-29 | `DOMAIN_SPLIT` (4 Math domains, 15/15/7/7) | 4 R&W domains, about 26/28/20/26% of 54 (material/cb/specs.json) e.g. 7/8/5/7 per module |
| blueprint.py:33-40 | `TIERS` (sum 22) | sum 27 |
| blueprint.py:47 | `SPR_AT` grid-in positions | none |
| blueprint.py:51-62, 75-89 | `spread`: domains spread across an easiest-to-hardest ladder | R&W modules run in domain blocks (question-type order), easiest-to-hardest within each block; needs a separate `slots` for R&W |
| blueprint.py:371-376 | `holds` keeps only `DOMAIN_SPLIT[1]` domains | returns empty `domains` for R&W |
| blueprint.py:392 | `custom_slots` SPR positions scaled to 22 | mcq only |
| API:36 | `MOCK_MODULE_SECONDS = 35*60` (used by `duration`, :177-178) | 32*60 |
| API:511 | `TIER_DEFAULT_S` 65/95/126 (pace plan, pressure 1268, 1887) | reuse `drill.TIER_BUDGET["rw"]` 49/71/94 (drill.py:104) |
| API:253 | `modules_list` literal `22` for module 2 | per-subject size |
| API:565 | `pace_plan` returns `"subject": "math"`, uses `blueprint.MODULE_SECONDS` and Math ladders | subject param |
| API:2086-2091 | gauntlet: 18 of 22, shown from target 620 | per subject |
| API:2285, 2294, 2321-2325 | habits: `q_worth = 12`, "Q17-22 / Q1-16" copy, Calculator row, Reference row | R&W: no calculator/reference rows; position copy from module size |
| API:2172 | lever action "Grid-in entry drill" | Math only |
| deps.py:21 | `SECONDS_PER_QUESTION = 95` (diagnostic/custom clock API:182, plan, pace quadrants) | 71 |
| scoring.py:59 | `ANCHORS` (invented Math curve) | can reuse or own curve |
| scoring.py:76 | `ROUTE_UP_AT = 0.60` (justified by Math median 520) | stated choice for R&W |
| scoring.py:82 | `LOWER_ROUTE_CEILING = 580` (CB Technical Manual, Math) | needs an R&W figure; none in repo |
| scoring.py:108, 386 | estimate dict `"section": "Math"` | subject |
| scoring.py:61, 87 | `HALF_BAND = 100`, `MOCK_HALF_BAND = 70` | see section 5 |
| estimate.py:39-61 | `SKILL_WEIGHT`, `DOMAIN_OF` Math skills only (`shares`, `model`) | R&W skill weights (cb_index has per-skill counts) |
| estimate.py:62 | `SPR_SHARE = 12/44` | n/a |
| estimate.py:493 | `gains` returns None when subject != "math" | R&W model |
| estimate.py:563-590 | `need`: 44, 22 hard-coded | 54, 27 |
| estimate.py:382 | `ledger` route block: `m1 = questions[:22]` | `len(module1)` |
| estimate.py:378 | `by_domain` default label "Math" | subject |
| estimate.py:616-645 | `time_cost` Math module ladders | per subject |
| api_results.py:42-43 | `PACE_MS`, `MODULE_MS` from blueprint (Math) | per subject |
| api_results.py:327-338 | `clock_ms` sections = 2 x 35 min, module 35 min, else 95 s/q | per subject |
| api_results.py:777 | `route_rule.half_band` 70/100 | see section 5 |
| api_results.py:1047-1049 | `WhatIf` lists max 44 ids | 54 |
| api_results.py:1280 | compare: `len(slots) > 22` means module 2 paired | module 1 size |
| api_results.py:1302-1310 | briefing: "Aim for about 95 seconds", "14 of 22" | per subject |
| papers.py:48 | `ABOUT_OK` positions 1-22 | 1-27 |
| papers.py:95-100 | `_build` weekly paper: one Math section | add R&W section |
| papers.py:159, 288, 346, 377-380, 456-457, 525 | every reader uses `sections[0]` | pick by subject |
| papers.py:290 | `m1 >= 14` | proportional |
| sets.py:66, 537-539 | `MODULE_MIN = 35` | per subject |

Every "math" default in API (subject falls back to math when a row has none, harmless for old
rows, but each is a place that must read the row's subject instead of assuming):
250, 390, 419, 565, 1139, 1314, 1343, 1353, 1505, 1675, 1804-1805 (start_mock, via `_insert`),
1906, 1955, 1977, 2140, 2195, 2206, 2344, 2462 (`"subject": "Math"` literal). Also API:1131
calls `gate_of(m1, answers)` without the subject.

Runner-facing session fields that are Math tools: `payload.calculator` defaults True (API:437);
`options` test_calculator pref (API:937); `State.calc`, `ref_n`, `ref_ms` (API:720-722);
`Nudge.kind "grid"` (API:702); `GRID_OK`/`_checked_answer` spr branch (API:64, 612-619; harmless
for R&W). `Mark.at` (API:691) accepts `stem`, table cell `t:r:c` and option `o:0-3` but no passage
target, so test-mode highlights on an R&W passage (`text`) have nowhere to be stored.

## 2. Feature by feature

Status: works / partial / math-only, for R&W today.

### Diagnostic (POST /api/session, API:576-592)
* Status: math-only.
* Evidence: `form_id = random.choice(list(FORMS))` (API:584); FORMS are server/forms.json, 10 forms x
  20 Math questions, 4 Math domains x (1 easy, 2 medium, 2 hard) (tools/build_diagnostics.py:33-40,
  app.py:52-59); `_insert(..., "diagnostic", ...)` default subject math (API:587); clock 20 x 95 s
  (API:182); marked by `scoring.score` with `HALF_BAND` and `"section": "Math"` (scoring.py:375-386);
  test_flow.py:47-63 and 148 assert the 4 Math domains.
* R&W needs: R&W forms (build_diagnostics.py DOMAINS/PER_DOMAIN are Math; R&W items are fixed so a
  form is a pick of item ids), a subject on the session, 71 s per question, subject-aware estimate
  label. A full-SAT diagnostic = two linked rows (R&W form then Math form), see section 4; the anon
  signup gate (api_account.py:38) must release both rows.

### Section mock (kind "section" -> row kind "mock", API:1684-1687)
* Status: math-only.
* Evidence: `fresh_module(learner, form)` -> `blueprint.module(form, ...)` built from Math
  `DOMAIN_SPLIT`/`TIERS`/`SPR_AT` (blueprint.py:317-321, 75-89); `duration` 35 min (API:173-183);
  routing `scoring.route_after` at 60% (API:1103-1104, proportional, fine); `_module2` builds
  `module2_<route>` Math (API:1095); final estimate `scoring.section_score` (API:1372) with Math label
  and the Math 580 cap (scoring.py:95-109); `modules_list` literal 22 (API:253).
* Note: `blueprint.by_domain()` (blueprint.py:201-208) already includes R&W domains and
  `abilities()` already surveys R&W templates (app.py startup), so filling R&W slots needs only an
  R&W `slots` (domain-block order, no SPR) and size/tier tables.
* R&W needs: per-subject blueprint tables; `duration` per subject; R&W route cut and lower-route cap;
  `section_score(result, route, subject)`; payload `calculator` False for R&W.

### Single module (kind "module", API:1688-1699; route trainer, gauntlet)
* Status: math-only (same builders as the section).
* Math-specific: `MODULE_FORM`/`M1_FORM` forms are Math blueprint keys (API:51-52); gauntlet 18/22
  and 620 target (API:2086-2091); trainer copy.
* R&W needs: same blueprint parameterisation; gauntlet goal scaled to 27.

### Custom test (kind "custom", API:1700-1706, `_custom` API:1581-1663)
* Status: math-only by explicit filter.
* Evidence: skills filter `deps.subject_of(t) != "math"` -> 422 (API:1585); saved (API:1593) and
  mistakes (API:1600) filtered to Math; `topics` `max_length=19` = the 19 Math topics (API:1469);
  default count 22 (API:1588, 1594, 1603); clock 95 s/q (API:182); `formats` default "both" puts
  grid-in slots that R&W cannot fill (bug in section 0.4).
* R&W needs: drop the filters (or filter by a requested subject), one subject per custom test (the
  session row has one subject), raise the topics cap, force mcq, 71 s per question.

### Twin (kind "twin", API:1707-1719, `_module2` API:1077-1080)
* Status: partial. A twin of an R&W sitting would build (generic `blueprint.twin`) but be stored as
  subject math (API:1675, 1718 does not pass `src["subject"]`), and R&W item supply runs thin
  (section 0.3).
* R&W needs: copy `src["subject"]` into `_insert`; same-skill fallback for R&W.

### Paper (kind "paper", API:1720-1733, server/papers.py)
* Status: math-only.
* Evidence: launch papers #1-#7 from mocks.json as `{"subject": "math"}` (papers.py:82-90); weekly
  `_build` one Math section (papers.py:93-100); `slots(n, form)` returns `sections[0][form]`
  (papers.py:155-159); `card`, `_hardest`, `_crowd`, `crowd`, `ratings_for` all read `sections[0]`;
  `ABOUT_OK` 1-22 (papers.py:48); `m1 >= 14` (papers.py:290); `card.questions` counts module1 +
  module2_upper (papers.py:370).
* R&W needs: pick section by subject (or an R&W paper); a full-SAT paper is two sections in the
  existing `sections` list, sat as two linked rows (section 4); about-regex to 27.

### Shared test (kind "shared", API:1734-1750, server/sets.py)
* Status: partial. Sharing a finished R&W sitting would work generically (`sets._paper`
  sets.py:163-177, items carry module 1/2), but the taker's sitting is created with subject math
  (API:1675 via `_insert`), `sets.MODULE_MIN = 35` (sets.py:66, 537-539) sets the advertised minutes,
  and `single = not m2_pairs and not route` decides module vs mock (API:1746).
* R&W needs: carry subject (derive from item templates via `deps.subject_of`), minutes per subject.

### Archive shelf mock (GET /api/mocks, POST /api/mock/{num}, API:1767-1809)
* Status: math-only.
* Evidence: MOCKS = server/mocks.json, 7 Math shelf sections (tools/build_mocks.py; asserted in
  test_flow.py:222-249: 22 questions, 15/15/7/7, grid-ins at 6/7/13/14/21/22); `start_mock` cfg has no
  subject (API:1804-1805); score on the spine is the band middle (API:1778).
* R&W needs: build R&W shelf sections (tools/build_mocks.py is Math-shaped) or leave the shelf Math
  and label it. Low priority: papers already cover "same form for everyone".

### Results page (GET /api/session/{sid}/results, api_results.report :622-778)
* Status: partial. Generic per row: `core` uses the row subject for addresses (`{subject}-m{n}-{k}`,
  api_results.py:285), `scoring.score` domain order already lists the 4 R&W domains
  (scoring.py:380-382), `estimate.national(..., c["subject"])` works for rw.
* Math-specific: `groups` reads only `module1`/`module2` (api_results.py:204-224); `clock_ms`
  (327-338); `route_rule` (776-777: Math cap and 70/100 half bands); `by_format` mcq/spr (699) is
  harmless; `estimate.total(learner, sid)` adds self-reported R&W to the Math band (769,
  estimate.py:709-744); `ledger` m1 = first 22 (estimate.py:382); briefing (1302-1310); compare
  (1280); WhatIf caps (1047-1049); `stats` traps filtered to Math (937); `init` sample section is a
  Math shelf mock (1189-1215); progress `recovery` fine.
* R&W needs: per-subject constants above; a full-test reader that shows both linked rows and the
  total (section 4).

### Report page (same endpoint; web/results/report)
* Server side as above. `_report_insight.conditions.calculator` (api_results.py:579) is a Math
  concept; `causes` uses the row subject (665) which is correct.

### Pressure, pacing, causes analytics (API:1256-1310, 1814-1921, 2134-2336)
* Status: math-only.
* `pressure_questions` slow test uses Math `TIER_DEFAULT_S` (API:1268); `resolve_drill` draws twins
  with an spr flag (API:1831, fine) but R&W supply is thin; `on_drill_finish` budget Math (API:1887),
  result `"subject": parent["subject"] or "math"` (API:1906) fine.
* `levers`: sections = any `kind == "mock"` regardless of subject (API:2138-2139);
  `progress.causes(learner, session=...)` without subject (API:2146) so an R&W sitting yields no
  per-question causes (progress.py:1326, 1356 filter by subject); `_up_to` Math band constants
  (API:2121-2131); route block uses `LOWER_ROUTE_CEILING` (API:2187); returns `"subject": "math"`
  (2140, 2195).
* `habits`: all finished timed sittings, any subject (API:2202); Math copy and rows (2285-2325);
  `progress.causes(learner, days=365)` Math only (2284).
* `progress.pace` forecast strip uses Math `blueprint.slots("module1", 1)` and `MODULE_SECONDS`
  (progress.py:1428-1442); `estimate.time_cost` Math ladders (estimate.py:616-645).
* `_tier_bases` subject leak (API:514-531, section 0.4).
* R&W needs: subject filter on every list of sittings, subject passed to `progress.causes`/`pace`,
  per-subject budgets.

### Gate / route (API:1098-1146, 2102-2118)
* Status: partial. `route_after`/`gate_of` are proportional to module length (fine for 27);
  `gate_of` subject param exists but `_route` drops it (API:1131); `gate_summary` pools subjects
  (API:2104); `recommended` pools subjects (API:2424-2432); `LOWER_ROUTE_CEILING` Math only; payload
  `reveal_route` fine.
* R&W needs: subject filters and an R&W cap.

### Score estimate (estimate.py, scoring.py, /api/tests)
* Status: partial. `estimate.estimate(learner, subject)` already filters rows by subject
  (estimate.py:110-133) and reads `outside_scores.rw`; but `tests_overview` calls it for Math only
  and labels `"subject": "Math"` (API:2445, 2461-2464); `projection` (estimate.py:699), `growth`
  (774), `calibration` (801) are Math only; `total` (709-744) = measured Math band + a single R&W
  number (self `rw_now` or an outside score), so a measured R&W section is never used;
  `gains`/`need`/`route`/`time_cost` Math models (sections above); `_done` subject bug (API:1296).
* R&W needs: subject on every call; `total` from the latest measured R&W row and Math row (or the
  linked pair) with the total band computed from summed centres (section 5).

### Shared session-row consumers outside api_tests
`sets._paper` (sets.py:163-177), `deps.paper_of` (deps.py:212-220), `estimate._paper`
(estimate.py:252-256, generic over dict values), `progress.record_paper` (progress.py:559-596,
per question, subject-agnostic), `papers._slot_questions` (papers.py:416-427, `m1`/`m2u`/`m2l`).

## 3. Checks that pin Math numbers (will fail or need R&W twins)

* server/test_flow.py: 38-39 DOMAINS; 47-63 forms; 71-73 `20 * 95`; 151 `hi - lo >= 100` (diagnostic
  band width); 223-249 shelf (22, 15/15/7/7, SPR at 6/7/13/14/21/22); 257, 273 `seconds > 2000`;
  272, 490, 507 22-question modules; 286, 525 `high <= 580`; 350 `19` topics; 498 fresh grid-ins;
  783-786 DOMAIN_SPLIT; 801 76 questions for 2 hours (95 s).
* server/checks/s5.py: 167, 170, 175, 193, 201, 203 (22 questions, 2100 s); 422 holds subject math
  and 22; 467 `2100 - 180`; 475, 477 22 budgets; 511-512 paper section subject math and 22; 525 label
  "Paper #1 · Math · Module 1 of 2"; 600-601 contest 44 / 4200; 688 >= 44 slots; 761 gate 14 of 22.
* server/checks/s6.py: 42 sample asked 44; 81 whatif high.

## 4. Full two-section mock: fit with the session model, and the recommendation

### What the session row assumes (one section per row)
* One `subject` column (db.py:196) read by `_subject`/`subject` everywhere.
* `module` in {1, 2} (db.py:141): `two_modules` routes only at module 1 (API:107-109, 1434-1436);
  `_route` sets `module=2` with `WHERE COALESCE(module,1)=1` (API:1121-1125).
* One `route` (db.py:142) and one `module1` JSON (db.py:143, API:1107-1108).
* `questions` = `{"module1": [...], "module2": [...]}` (API:117-119, 1110-1114); readers that only
  know those two keys: `mock_module`, `marked_questions`, `_modules`, `_handed_in_ids`
  (API:112-159, 731-737), `api_results.groups` (204-213), `sets._paper` (163-177),
  `papers._slot_questions` (416-427).
* One clock: `module_started`, `paused_ms`, `paused_at` reset per module (API:1121-1123);
  `duration` one value for the live module (API:173-183).
* The between-module step is judged by `BREAK_MAX_MS = 75_000` (API:59, 1205-1208): any gap over
  75 s unranks the sitting. A 10-minute section break in one row would unrank every full test
  unless special-cased.
* `_final` marks everything with one `scoring.score` (API:1336), which would merge R&W and Math
  domains into one band; one `result.estimate` per row, which `estimate._sittings` reads as one
  band of one subject (estimate.py:114-127); `ledger` assumes the first 22 are module 1.
* Stamps keyed `m{module}:{pid}` (API:328), `away_of` groups by module (API:1165-1185).
* Review addresses `{subject}-m{module}-{n}` (api_results.py:285).

### Recommendation: two linked rows, one per section (R&W row, then Math row)
Each row stays exactly what the code already handles (one subject, two routed modules); the only
new code is the link, the break and the total. A four-module row would break every reader listed
above; two rows break none of them, and a learner who stops after R&W keeps a complete, scored R&W
section instead of a half-marked test.

Concrete glue:
1. `NewMock.kind` gains `"full"` (API:1481). `_new` builds the R&W section exactly like "section"
   with `subject="rw"` and `cfg["full"] = {"id": <group id>, "part": 1}`.
2. In `_final` (API:1330), after the R&W row is marked and filed, if `cfg.full.part == 1`: insert the
   Math section row in its lobby (`fresh_module(..., "module1")`, `subject="math"`,
   `cfg["full"] = {"id": ..., "part": 2, "after": rw_sid}`) and return `next: {sid}` inside `done`.
   Creating it at hand-in (not at start) keeps an unstarted Math section out of `open_sittings`.
3. Break: the Math row's lobby is the 10-minute break screen. On its `begin` (API:836-879), store
   `_session.section_break = {"ms": module_started - rw.finished}` (the same pattern as `between`,
   API:867-876) and judge it in `rank_of` against its own limit (10 min plus slack), separate from
   `BREAK_MAX_MS`.
4. Total: computed when the Math row finishes (or read lazily) from both rows' estimates:
   `result.full = {rw: sid, rw_band, math_band, total}`; `estimate.total` (estimate.py:709) prefers
   this measured pair over `rw_now`/`outside_scores`. Ranked as full only when both rows rank.
5. Readers: history/tests list group rows by `json_extract(cfg,'$.full.id')` (the codebase already
   queries cfg this way, e.g. API:1972, api_results.py:740); results page shows both rows plus total.
   No schema change is needed; a `full_of` column via the ADD COLUMN list (db.py:196) is optional for
   indexing.
6. Side effects to handle: `_insert` numbers each row (API:1509-1510) so one full test takes two
   numbers; `_rate` counts two sittings (API:1496-1501); `kinds_rows` needs a "full" key; papers and
   shares of a full test are two sections (the `sections` list already allows it); pause/discard
   stay per row (discarding the Math row leaves the R&W section standing).

The same pattern covers a full-SAT diagnostic (R&W 20, then Math 20) and a full paper.

### Web side of the one-section assumption (detail in section 6)
* test.js decides everything per module from the payload: `two()`/`lastModule()` (56-57), lobby
  "Module m of N" (234), `between()` with `seconds: 60` and Math tools copy (630-682), "Continue to
  module 2" (619-623), `done()` with one 200-800 estimate (691-761), `report_later` qid regex
  `/^m(\d)q0?(\d+)$/` with no subject (739). With two linked rows each row is a normal 2-module
  section, so test.js only needs: tools from `S.subject` (test.js:452), and at the R&W `done()` a
  hop to the Math row's lobby, which shows a 10-minute `UI.between` (runner.js:2943-2996 already
  takes `seconds` and `title`; its "Module 2" strings at 2959-2995 must become parameters).
* The passage two-pane already works in exam mode (runner.js:1757-1772 has no mode check; test.js:427
  passes `text` through), so R&W in the runner costs tool gating and copy, not layout work.

## 5. Score ranges: every place a width is computed or shown

Full table from a repo-wide sweep follows (5.0 onward, copied from scratchpad/map/ranges/ranges.md,
spot-checked: api_today.py:1262, web/index.html:2149, web/plan/plan.js:494, web/tests/tests.js:1059).

Notes for the "at most 20 wide" change:
* Roots: `scoring.HALF_BAND` (scoring.py:61, 200 wide) and `MOCK_HALF_BAND` (scoring.py:87, 140 wide)
  feed `score()` (376-378), `section_score()` (101-102) and `estimate._half` (estimate.py:274-275)
  -> `mid()` (240-249) -> rescore/ledger/whatif/path/recovery/second-look/pass2/levers. Setting both
  to 10 gives exactly 20 wide, because each end is rounded to 10 separately and both move together.
  Exceptions: clamps at 200/800 (narrower, fine) and the lower-route cap `low = min(low, high - 10)`
  (scoring.py:106, estimate.py:248) which gives 570-580 (10 wide, fine).
* Hard-coded widths that do not read the constants: `combined` `70 / sqrt(n)` (estimate.py:153),
  `project` half `max(60, min(150, ...))` (estimate.py:683; floor makes 120 wide minimum),
  `api_today.early_projection` same clamp (api_today.py:1262), `route_rule.half_band` 70/100
  (api_results.py:777), client mean +/-35 (web/plan/plan.js:494), client current +/-30
  (web/index.html:2149). `estimate().range` (estimate.py:174-175) is a min-max of sitting midpoints,
  not a band, and is the Results/PDF hero fallback (web/results/page.js:74, progress_pdf.py:275-277).
* Totals: there is no total band today; every total adds one R&W number to both Math ends
  (estimate.py:731, api_profile.py:465-466, web/index.html:2143, 2902). For a full SAT, adding two
  20-wide section bands gives 40 wide, so the total must be built from the summed centres:
  `c = rw_centre + math_centre`, `low = round10(c - 10)`, `high = round10(c + 10)`, clamped to
  400/1600. `estimate.mid()` already returns the unrounded `centre`; store it in `result.estimate`
  so the total never re-derives from rounded ends. `national(low, high, "total")` already works.
* Behaviour that changes when bands narrow (reads low/high, not the middle): plan.py:1009,
  api_today.py:484, 1300, 1322, estimate.py:393, 809, api_tests.py:2130 (`_up_to` rebuilds the centre
  as `low + MOCK_HALF_BAND`; old stored bands will not match a new constant), web report
  page.js:587, 979, results/page.js:241, index.html:2277, me.js:503.
* Rationale text that contradicts a 20-wide band: scoring.py:16-20 ("narrower than 200 points would
  be pretending", SE near 45), :61, :84-86; estimate.py:158-165 confidence copy (140, 100);
  web/tests/tests.js:98, 1059; start.js:362; plan/progress.js:93; plan/wizard.js:453 ("710-800");
  diagnostic/index.html:47, 61, 65.
* Existing inconsistency: a Season Final is row kind `module`, stored at 140 wide by `section_score`
  but re-marked at 200 wide by `estimate._half` (only mock/section/paper get MOCK_HALF_BAND).
* Checks to update: test_flow.py:151 (`hi - lo >= 100`), estimate.py:851-863 self-test, f4.py:733-856,
  s3.py:893, s5.py:606, s7.py:381-410, s8.py:542, f6.py:186-189.

Scale key: S = section 200-800, T = total 400-1600. C/D/X = computed / displayed / copy text.
"r10" = each end rounded to 10 separately. "clamp" = max(200)/min(800) unless stated.
All R&W sittings go through the same scoring.score/section_score (label "Math" hardcoded), so every section constant applies to R&W too.

### 5.0 Root constants and functions (change these first)

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

### 5.1 Server: where a band is COMPUTED

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

### 5.2 Server: band CONSUMERS (pass through, or logic on low/high)

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

### 5.3 Totals (section band combined into a total)

No separate total band exists. All three add a single R&W value to both math ends, so total width = math band width.

| file:line | how |
|---|---|
| server/estimate.py:731 | total(): low = math.low + rw.value, high = math.high + rw.value; rw from outside score (60 days) or learners.rw_now |
| server/api_profile.py:465-466 | goals.total now_low/now_high = latest.low/high + rw_now |
| web/index.html:2143 | client: `SAT total ${sc.low + p.rw_now}–${sc.high + p.rw_now}` |
| web/index.html:2902 | client: `≈ ${r.estimate.low + rw}–${r.estimate.high + rw} with your R&W` |
| Point-only totals (no range) | web/plan/plan.js:301,511; web/plan/wizard.js:277,462; web/me/me.js:479-481,586; web/index.html:2287; server/plan.py:2026-2027 (start/target sums) |

### 5.4 Single point scores (no range)

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

### 5.5 Web: display of server low/high

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

### 5.6 Copy and static text that states a width or range

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

### 5.7 Width-dependent logic (reads low or high, not mid): behaviour changes when bands narrow

- server/plan.py:1009 verdict beat/under/within.
- server/api_today.py:1300 at_target if latest.low >= target.
- server/api_today.py:484 default target from band high + 50.
- server/api_today.py:1322, server/estimate.py:809 calibration `inside` (low <= score <= high).
- server/estimate.py:393 cap_cost from uncapped high.
- server/api_tests.py:2130 _up_to centre from low + MOCK_HALF_BAND.
- server/scoring.py:106, server/estimate.py:248 `low=min(low, high-10)` on capped bands.
- server/estimate.py:234 national percentiles at each end.
- web/results/report/page.js:587, 979; web/results/page.js:241; web/tests/tests.js:235; web/index.html:2277.

### 5.8 Tests / checks that encode widths (will break or need fixture updates)

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

### 5.9 Not score estimates (considered, excluded)

- web/me/me.js:705-707 "Started lo–hi": compete climb cohort window around first mid, half = 40/80/160 (server/compete.py:2072, lo/hi at 2091-2092). A score range, but a cohort filter, not an estimate.
- web/words/run/index.html:1011 vocabulary "±(hi-n)" (server/words.py:735-743): word count.
- server/drill.py:442 BAND_MID: College Board 1-7 item difficulty bands mapped to item ratings.
- tools/cb_data.py, tools/cb_rw_fetch.py: CB score_band_range_cd 1-7.
- server/compete.py:1815-1894 champions `band` = level bands.
- server/api_words.py, server/words.py freq/sprint bands.
- web/assets/compete-ui.js:314 rank range "#lo–#hi".
- server/ratings.py: Elo-style ratings (400 divisor), no score band.

### 5.10 Checked, no range logic

server/mail.py, server/challenge.py, server/daily.py, server/api_shell.py, server/api_me.py (200-800 in tens validation only, :166-177), server/ratings.py, server/next.py (copy only), server/api_compete.py (passthrough at :355), server/api_plan.py (passthrough), tools/*.py (no score bands; cb_data builds percentiles json only), web/welcome/*, web/share/index.html (loads me.js read-only, so me.js rows apply), web/assets/kit.js, web/assets/runner.js, web/assets/quick.js (200–800 placeholder only), web/practice/*, web/review/*.

## 6. Web map (detail)

Copied from scratchpad/map/web/web.md (web agent, all files read in full).

Read 2026-10-22, READ-ONLY. Line numbers are against the working tree (uncommitted edits included).
All paths relative to /Users/workingmyassof/freshbot/satbank. Raw per-file notes sit beside this file (raw-*.md).

### 6.0 Headline findings

1. test.js builds a fresh `UI.runner` for every module: `start()` calls `destroyRun()` (test.js:433) then `UI.runner(runHost, {...})` (test.js:446-500). Every tool flag is read once per module from the session payload `S`. So gating the calculator, reference sheet and Math directions for R&W is a test.js change at test.js:452 (`calc: S.calculator !== false, ref: true, annotate: true, scratch: true, directions: true`), driven by a per-module `S.subject`. runner.js needs no subject logic for that.
2. The two-pane passage layout already works in exam mode. runner.js `placePassage` (1764-1772) has no mode check: `if (it.q.text && !phone() && fitsPassage())` moves `ws.passageNodes` into the `.rn-passage` pane; `runner.css` `.rn.has-passage` rules (529-551) are mode-agnostic; `annotate(bodyEl, ...)` (1794) anchors marks on the pane or inline. test.js passes each question object through untouched (test.js:427 `Object.assign({}, q, { number: i + 1 })`), so if the server's session payload includes `text`, R&W renders like practice. Practice proves it: practice/session/session.js:176-215 uses the same runner and passes neither `calc` nor `ref`, so R&W practice currently shows the calculator and reference too.
3. Highlights on the passage use addr `'p'` (question.js:432). test.js `marksOut` (85-91) maps only `'s'` to `'stem'` and passes every other addr through, so passage marks reach `POST /session/{id}/state` as `at: 'p'`; `marksIn` (92-93) maps back. Server must accept `at: 'p'`.
4. Subject-aware plumbing already exists and should be reused: kit.js `SUBJECT` + `qlabel` + `qlabel.addr` (2933-2949), report `?q=` parser (report/page.js:37-47), runner `rvAt` (3075-3084), results-ui chips grouped per (subject, module) (results-ui.js:200-244), gauge `subject` option (charts.js:824).
5. Almost every score surface is hard-coded to one 200-800 Math scale; the "total" today is Math band + a self-entered R&W number.

### 6.1 Feature by feature

#### Diagnostic
- Entry: diagnostic/index.html:40 ("20 questions · 32 min · all four domains evenly"), :42 Start, :70-75 `TestStart.go({kind:'diagnostic'})`; :47 "about 200 points wide"; :65 `UI.scale(... min: 200, max: 800)`.
- start.js:80-82 diagnostic is `POST /api/session` (not `/mock/new`); start.js:40 KIND diagnostic n 20; start.js:218 steps Test/Conditions only.
- tests.js:272 next card text; tests.js:521 INFO "All four domains evenly", "20 questions · 32 min".
- test.js:63 `baseSeconds` fallback `(question_count || 22) * 95` for custom/diagnostic (20 x 95 = 31:40). test.js:174 and :699 finished diagnostic goes to `/diagnostic/signup.html`; :265 no "Start over" for diagnostic; :720-723 "The diagnostic is in".
- signup.html (whole file) and verified.html: subject-neutral. signup.html:55 "once the last module is handed in"; gate polls `GET /session/{sid}/results` (79-82).

#### Section mock (2-module routed)
- tests.js:516 INFO section "Adaptive", "8/7/4/3 each module" (Math domain counts), "44 questions · 70 min · 2 modules"; :257 default next card "44 questions · 70 min"; :288 plan variant.
- start.js:36 KIND section n 44 mods 2; :137 body `{kind:'section', route, m1}`; :342-357 Module 2 seg adaptive/upper/lower, Module 1 standard/harder/easier, "tops out at 580".
- test.js:215-218 lobby "N modules · X questions each" (uses `S.modules[0].questions`), "Module 2 is fixed / chosen by how module 1 goes"; :283 startOver to `?start=section`.
- No subject is ever sent: start.js `body()` 131-165 builds no `subject`; `go()` 74-95 posts to `/mock/new`.

#### Single module
- tests.js:517-519 module1 / module2u / module2l "22 questions · 35 min", "580"; :284 next card; :914 "Try the harder module 2".
- start.js:37 KIND modules n 22; :113 `count = mods * 22`; :143-147 m1+m2 becomes a section with fixed route; :359-379 cards "22 questions · 35 min", "14 of 22", "n of 2 modules · n*22 questions · n*35 min".
- test.js:219 single module lobby shows "N questions"; kit.js KIND.label "Module m".

#### Custom test builder
- start.js:402-442 `stepCustom`: skill picker iterates `UI.DOMAINS` + `UI.TOPICS` (412-420), which are Math-only (ui.js:652-680). R&W skills cannot be picked. Formats seg Both / MC only / "Grid-in only" (434). Length seg 10/22/44 (427). "mmss(n*95) at test pace" (441).
- start.js:39 KIND custom; :114 count; :127-128 seconds `n * 95`; :148-155 body; :498-502 timing "95 s a question".
- test.js:74 "95 s a question"; :335-339 "My own minutes" for custom.
- tests.js:520 INFO custom "5–60 questions"; :524 traps "6–22 questions · 95 s each".

#### Twin
- tests.js:522 INFO; :551/579 `D.twin`; :912 sitting menu Twin for section/mock/module/paper/twin/shared; :371-372 cycle twin.
- start.js:41 KIND twin n 44 mods 2; :139 body; :383-387 step text.
- report/page.js:384-388 `retake()` posts `{kind:'twin', twin_of, full: kind !== 'module', timed}`; :393-396 offered for mock/module/diagnostic/paper.
- compare.js slot-by-slot table (95-114) labels come from server `slot_label`.

#### Paper (weekly Papers) and printable output
- Papers (same slots for everyone): tests.js:649-695 papers card; :656 "line at 14"; :699-709 rating "Expect e1 of 22 in module 1, where 14 routes you up"; :712-718 preview meter `max 22, ticks 22, tick 14`; :741 "of 22"; :739 race `count 22, minutes 35`; :277 "44 questions · 70 min".
- start.js:38 KIND paper n 44; :138 body; :325-334 paper picker.
- talk.js (paper sheet): :22-25 `SHORT`/`MODULE` maps only m1/m2u/m2l, `slotName('m1:5')`; :196 qid fallback `m1q${pos}`; :163 and :187-188 grid-in spread.
- Printable: no printable full test exists. Report prints: repair pack / retry sheet / tutor packet (report/page.js:1695-1756) render with `UI.workspace` (1724) and an "A–D" key (1749); `@media print` table (index.html:246-264, page.js:1083-1096). Practice worksheets use `/practice/session/?id=..&print=1` (review/review.js:1784, review/sheet/sheet.js:184-206). Results page Print (results/page.js:140).

#### Shared test
- tests.js:983-1038 Share sheet: `POST /sets {kind:'test', session, show_score, cfg:{fresh}}`; race `{from_session, count 22, minutes 35, twin, open_for 72}` (1018-1022).
- tests.js:1169-1170 `?shared=CODE` opens start sheet. start.js:237-245 `loadShared` (minutes fallback `count/22*35`), :393-400 text "Module 1 ... Module 2 matches when you earn the same route", :44 KIND shared n 44 mods 2.

#### Archive shelf mock
- No served web client. The shelf page is archive/site-v1/web/mock/index.html (not mounted: server/app.py:33 `WEB = .../web`), it calls `GET /api/mocks` and `POST /api/mock/{num}` then opens `../test/?s=ID` (archive mock/index.html:304-317). Sittings it creates are kind `mock` and flow through test.js, Tests, Results and the report like any section (kit.js KIND mock "Full section"; results-ui.js:367 "Module n" for kind mock in progress).

#### Results page (results/page.js)
- :62-66 `startTest` posts legacy `{full, timed}` to `/mock/new`; :218-219 "Full section" / "One module" (70 / 35 min); :244 "(70 min)".
- :231-234 target track on a 200-800 scale (`pos = (v - 200) / 6`).
- :258-273 hero: :263 "Math is measured here; Reading and Writing is your own score until SAT Freshman has R&W questions."; :270 "Math estimate"; :272 "/800".
- :316 chart detail "harder M2 / easier M2"; :323-326 `bandChart` (default 200-800, grid 200).
- :432 Domains tip "one full SAT Math section: two modules, 44 questions ... (22 questions)"; :437-438 column names/tips 22/20/44; :433 and :640 domain order from `UI.DOMAINS` (Math).
- :515 sitting score fallback `right/asked*800`.
- :607 Skills card filters `(t.subject || 'math') === 'math'`: R&W skills are excluded.
- :40 FORMAT Grid-in; :405 why-you-miss keys include `entry`.

#### Report page (results/report/page.js)
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

#### Pressure, pacing, causes analytics
- Pressure: test.js:697-698 stores `satf.pressure.{sid}`, :748-757 Pressure check button, :798-802 `POST /session/{sid}/pressure`; tests.js:262-266 next card, :777 filter, :886-887 chip "Pressure n · Knowledge n"; report/page.js:1583-1589 Up next.
- Pacing: runner pace guide ticks with checkpoints `[7, 14]` (runner.js:1983, :2674-2680 toast "behind at Q8/Q15"); `pace_ms: 95000` to navigator and Check your work (runner.js:2241, :2292), `overBudget` default 95000 (:343), `budgetAt` fallback 95000 (:2641), odds value fallback 95 s (:2293). test.js:651-663 "Module 1 pace" chart in between. tests.js:439-492 Habits rows are server-built. report drawPace/clockReplay above.
- Causes: tests.js:70 CAUSE map, :203-247 "Where points went" (server `levers`), :232 fallback "lifted the 580 cap"; results/page.js:399-408; report :62 CAUSES (includes `entry` = grid-in), :323-331 fix menu; results-ui.js:40-44; runner.js:3541 `entry` cause offered only for spr.

#### Gate / route display
- test.js:645-648 between route text; :683-688 `gateLine` "harder module 2"; :725-731 done chip "Harder/Easier module 2"; :763-792 trainer strip, :231 "The line: 0.6*n".
- tests.js:333-335 Module 1 meter `max 22, ticks 22, tick 14` "14 of 22 right routes you up", Module 2 meter; :326 `lastM1` requires `modules[0].asked === 22`; :715-716 paper preview tick 14; :870-885 chips "Harder M2", "Easier M2", "580 cap", "Route line +g"; :1054-1080 How scoring works (14 of 22, 580, up to 800, 75 s break rule).
- compare.js:28-29 gate/route; results-ui.js:189 subtitle "harder M2 / easier M2".

#### Score estimate display
- test.js:714-715 done card `UI.scale(... min: 200, max: 800)`.
- tests.js:92 "Estimated Math score"; :98 empty text; :113 and :184 "of 800"; :130 and :180 `bandChart min 200 max 800`; :144 "Total low–high · with your R&W ..." from `D.total`; :152 calibration `x.math ?? x.score`.
- results/page.js:231-234, :263, :270-272 (see above). report :566-571, :627-648.
- charts.js: `bandChart` y defaults `opts.min ?? 200, opts.max ?? 800` (506), auto-thinned grid (516), R&W self-entered lane hard-coded 200-800 (664-677), `normPoint` reads `p.math ?? p.score` (398-408); `gauge` `min ?? 200, max ?? 800` (811), ticks at thirds (840) work for 400-1600, label from `UI.SUBJECT[subject]` default "Math" (824, 874, 880); `scale` `min ?? 200, max ?? 800` (954); `dotStrip` min 200 bin 20 (2068). kit.js SUBJECT has math and rw only (2933-2936), no total entry.
- results-ui.js:301 Peek gauge `subject: 'math'` hard-coded.

#### Timers and break screen
- runner.js:119-220 `timer` is generic (warnings 300/60 s, unhides at 5:00).
- test.js:61-64 `baseSeconds`: `S.duration / factor`, else 95 s/question for custom and diagnostic, else 2100 (35 min). :66-76 `timingText` (" for each module", "95 s a question").
- start.js:123-130 `seconds()` = `2100 * modules` or `n * 95`; :498-502 timing rows "35:00 a module".
- Between modules: test.js:630-682 builds `UI.between(b, {conditions, seconds: 60, stats, next, route, cells, ...})`. runner.js:2943-2996 `between`: `o.seconds` already a parameter and `o.title` overrides the h1 (2950), but "Module 2 starts in" (2959, 2989), "Begin module 2 now" / "Begin module 2" (2963, 2995), "Getting module 2 ready…" (2978) are hard-coded. There is no section break screen; a 10-minute break can reuse `UI.between` with `seconds: 600` once those strings are parameters. Training mode has no countdown (2944-2945, 2970).
- Time's up: test.js:607-627; runner.js:2610-2624 (closes calculator).

#### Calculator (Desmos) and reference sheet
- test.js:452 `calc: S.calculator !== false, ref: true` (reference always on); :290-296 settings line "calculator / no calculator / scientific calculator"; :341-343 Settings Calculator switch; :363-366 keys G Calculator, F Reference; :643 between "calculator and reference sheet on every question".
- start.js:108 tools.calculator default; :185 summary "calculator on / no calculator"; :524 Calculator switch.
- runner.js:1291-1296 `cfg.calc`, `cfg.ref` per runner; :1349-1358 tool buttons; :1709 passed to `UI.workspace`; :2163-2168 per-question calculator expressions saved; :2361-2366 `toggleCalc`; :2810-2817 keys G/F; :2906 auto-open calculator from prefs; :2522-2525 practice "Calculator opens" menu.
- runner.js:1117-1194 `REF` Math formula sheet, `refDock`, `refSheet`; :1550 slot tabs include Reference when `cfg.ref`.
- runner.js:1197-1215 `DIRECTIONS` is the Math section text (calculator permitted, SPR rules); :1217-1234 appends `UI.spr.directions()` table. Shown on first begin (test.js:503) and the lobby Directions link (test.js:260).
- Review player always shows Calculator and Reference (runner.js:3160-3165, 3179-3191).
- question.js:1670-1671 tools honour `o.calc`, `o.ref`.

#### Grid-in (SPR) input
- test.js:428 spr items use `value`, MC use `selected`; :479 nudge kind `grid`; :38 aid text "the grid-in form".
- runner.js:1309 `isMc`; :1550 "Entry rules" slot tab only for spr; :1819-1832 `sprHelp` only for spr; :1866 Eliminate hidden for spr; :1850 practice "Grid-in" badge; :2452 Details Format; :2492 answer pad note.
- All of these are per item, so an all-MC R&W module never triggers them. Only the copy (DIRECTIONS, AIDS text) is Math-specific.

#### Passage rendering
- question.js:429-445 `passage(q)`: `<div class="q-passage" data-addr="p" data-nofold>`, paragraphs, "Text 1/Text 2" labels, `<u>`, blanks; :570-576 rendered inline; :640 R&W options are prose (no TeX) with `data-addr o:i`; :1754 `ws.passageNodes`; :399-401 R&W speech.
- runner.js:1424-1430 pane; :1472-1505 `layout()` (passage and docked calculator share the left column, passage wins 1481-1483); :1531-1539 resize, `satf.passage.w`; :1599-1604 `detailsFit` counts the passage; :1757-1772 `fitsPassage`/`placePassage`; :1754-1755 cleared on destroy. Phone and narrow screens keep it inline (runner.css:1216 hides the pane under the phone breakpoint).
- Review player: question rendered inline via `UI.workspace` (runner.js:3440-3455), no two-pane; works because `playerItem` includes `text` (report/page.js:1603). Note runner.js:3050 `QF` (flat review rows) lacks `text`, so a flat row without `q` would drop its passage.

#### Annotation / highlight tools
- runner.js:785-961 `annotate` works on any `[data-addr]` node: addrs `s`, `t:r:c`, `o:i`, and the passage `p`. Attached to `bodyEl` (1794) so pane marks work. Exam tool "Highlights & Notes" (1349).
- test.js:85-93 style and addr mapping (see headline 3). practice session.js:80-81 keeps addr unchanged.
- Read-only marks in the review player (runner.js:3454).

#### Question counts and durations hard-coded
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

#### Domain names hard-coded
- ui.js:652-657 `DOMAINS` (Algebra, Advanced Math, Problem-Solving and Data Analysis, Geometry and Trigonometry) and :658-680 `TOPICS` (19 Math); `RW_SKILL` (681-686) maps the 10 rw slugs to names but has no domain grouping and is not in `TOPICS`/`TOPIC`.
- Consumers: start.js:412-420 (custom picker), results/page.js:42, :433, :640-645, report/page.js:67, :1041, :1358, results-ui.js:191 and :390-391 (skill names via `UI.TOPIC`), runner.js:407-410 and fillHead :3496-3503 (fall back to `topic_name` for rw), test.js:547-554 `shortOf` (falls back to first words of `topic_name`).
- compare.js:24 `DOMAIN` keys algebra/advanced/psda/geometry; report/page.js:625 `doneMs`; tests.js:516 "8/7/4/3 each module"; "all four domains evenly" (tests.js:272, :521; start.js:40; diagnostic/index.html:40).

#### Score axes 200-800 vs 400-1600
- 200-800 hard-coded: test.js:715; tests.js:113, :130, :180, :184; results/page.js:232-233, :272; report/page.js:637-641 (R&W input range, correct for a section); diagnostic/index.html:65; charts.js:506, :666, :811, :954, :2068 (defaults, overridable by `min`/`max` except the R&W lane).
- No 400-1600 anywhere. The gauge, scale and bandChart accept `min`/`max`, so a total only needs callers to pass 400/1600 (and the bandChart's grid step thins itself, 516).

### 6.2 Runner: what branches on subject, and what would need to

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

### 6.3 Already subject-aware (reuse)

- kit.js:2933-2949 `UI.SUBJECT` {math, rw}, `UI.qlabel(item, sitting)` ("R&W M1 Q5" when two subjects), `UI.qlabel.addr` (`rw-m1-5`).
- report/page.js:37-47 `?q=` parse with subject; :219 `UI.review.at` with subject; runner.js:3074-3084 `rvAddr`/`rvAt` match subject+module+n.
- results-ui.js:200-244 miss chips one group per (subject, module), links via `qlabel.addr`.
- charts.js:824 gauge `subject` label; report/page.js:566-567 passes `R.subject`.
- report/page.js:1603/1618 `playerItem` carries `text` and `subject`.
- question.js passage, prose options, R&W speech; test.js marks round-trip `p`.

### 6.4 One-section assumptions in the web flow

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
