# R&W parity map: plan, progress, profile, reports, parent, admin, achievements, habits, shell

Scope: server/plan.py, api_plan.py, progress.py, progress_pdf.py, api_profile.py, reports.py, parent_mail.py,
api_parent.py, api_admin.py, achievements.py, ratings.py, habits.py, api_me.py, api_shell.py, mail.py,
satdates.py, estimate.py (as consumed). Web: web/plan, web/me, web/parent, web/admin, plan-ui.js, charts.js,
palette.js, subject parts of kit.js and ui.js. Compete: see section 7 (from compete.md).

All line numbers are as of 2026-10-22, working tree (uncommitted changes present).

---------------------------------------------------------------------------------------------------

## 0. Verdict table

| Feature | R&W today | Server evidence | Page evidence | Natural UI |
|---|---|---|---|---|
| Plan wizard | partial: R&W score/target/minutes/domain focus are typed, never measured | plan.py:108-206 (validate, rw_* keys), plan.py:1821-1859 (propose: Math only) | wizard.js:390-403, 437-469, 609-612, 661-765 | scores and targets side by side + Total; focus already a Math/R&W switch (wizard.js:664) |
| Weekly plan generation | partial: R&W = off-site "custom" rows + Words deck; no bank items, no R&W tests | plan.py:667-701 (_rw_tasks, start=None), 787-983 (build_day), 387-466 (allocate over Math TOPICS) | plan.js, plan-ui.js:173,184 | one day list holding both subjects' tasks |
| Plan targets | partial: Math measured, R&W self-reported | plan.py:100-105, 182-185, 202-205; api_plan.py:30-37, 483-493 | plan.js:301-303, 374-383, 480-511, 1014-1029 | side by side + Total |
| Progress (plan Progress tab) | partial: R&W only as a domain list from logged Bluebook misses | plan.py:1396-1410, payload 2019-2058 | progress.js:291-299 ("No R&W results yet") | subject switch for skills/domains/coverage; total trajectory shared |
| Skill mastery / ratings | server computes for R&W, nothing in scope asks | progress.py:259-298 (board(subject)), progress.py:543-545 (ratings.update for every topic) | me.js skills/domains = Math only | subject switch |
| Predicted score (outside tests) | math-only (R&W = a typed point) | estimate.py:142-178, 689-706, 709-744; plan.py:1761-1775, 2033 | plan.js:484-514, progress.js:60-93, me.js:466-505, 664-680, 990-1005 | side by side + Total |
| Profile targets | partial: rw_now/rw_target exist, self-reported, select boxes | api_me.py:146-202, deps.py:28 | me.js:466-505, 583-650 | side by side + Total |
| Problem reports (reports.py) and admin inbox | partial: works mechanically for rw_* items; Math copy; passage hidden from reviewer | reports.py:369-470, 1238-1264 | admin/reports/index.html:265-291 | n/a |
| Progress PDF | math-only (counts mix both subjects) | progress_pdf.py:35-36, 135-166, 263-327 | download via api_results.py:972-984 | side by side |
| Parent page | partial: totals mix subjects, no subject labels, Math target shown as "Target score" | api_parent.py:152-170 (on api_admin.detail) | parent.js:133-139 | side by side |
| Parent weekly email + alerts | partial: same data, "score range" without subject | parent_mail.py:57-97 | n/a | side by side lines |
| Admin student board | partial: mixed totals, R&W topics as raw slug, no R&W goals, sittings unlabeled | api_admin.py:39-74, 86-169 | admin/students/index.html, admin/student/index.html:60-85 | side by side |
| Compete | see section 7 | | | |
| Achievements | partial: volume/habit badges count R&W; skill/domain/explorer/climb are Math | achievements.py:89-94, 146-148, 177-187 | me.js badges | add R&W rules |
| Streaks (progress.days) | works | progress.py:960-1078 counts every attempt, word review, test | me, shell, plan | n/a |
| Habits (misconception families) | none by design | habits.py:81-83 returns [] for rw; api_profile.py:312; progress.py:98-103 | me.js:1058 | R&W families only if wanted |
| Week goals | partial: fix_traps / reach_word 422 on rw_* topics; suggestions Math | api_profile.py:799-855, 858-897 | me/week.js | both |
| Shell / nav | partial: domains, avatar mark, plan target, pace are Math | api_shell.py:59-66, 158-166; api_me.py:73-82 | ui.js:2187-2191, kit.js:2638-2650 | side by side (two marks or 8 segments) |
| Levers ("how is this computed" facts) | math-only | api_profile.py:129-215 | facts popovers on me/today/results | per subject keys |

---------------------------------------------------------------------------------------------------

## 1. Roots (most findings below are one of these)

R1. `subject="math"` defaults, and every in-scope caller passes nothing.
- progress.py:188 `topics(subject="math")`, :259 `board`, :807 `coach`, :1119 `warmup_candidates`, :1295 `blind`,
  :1319 `causes`, :1396 `pace`, :1453 `fluency`, :1557 `types_met`. :246 `open_traps(subject=None)` is the only
  neutral one and plan.py:885, api_plan.py:583, api_profile.py:873 force `subject="math"`.
- estimate.py:114 `_sittings`, :142 `estimate`, :435 `_rows`, :489 `gains` (and `gains` returns None for
  any subject but math, estimate.py:493), :593 `route`, :648 `practice_delta`. No subject parameter at all:
  :563 `need` (44 questions, module-1 route), :616 `time_cost`, :689 `projection`, :709 `total`, :765
  `growth` (filters math, :774), :796 `calibration` (outside_scores.math only, :801-809).

R2. The score and allocation models are Math tables.
- estimate.py:39-61 `SKILL_WEIGHT` / `DOMAIN_OF` (19 Math skills), :62 `SPR_SHARE`, :73-80 `shares()` from
  blueprint.DOMAIN_SPLIT. No R&W skill weights exist anywhere; only domain shares:
  progress.py:58-59 `RW_BLUEPRINT` and a duplicate plan.py:35 `RW_SHARES`.
- plan.py:23-24 `DOMAINS = progress.DOMAINS`, `TOPICS = estimate.DOMAIN_OF` (Math).
- scoring.py:59 `ANCHORS`, :74 `ROUTE_UP_AT`, :82 `LOWER_ROUTE_CEILING=580`, :61/:87 band halves: Math curve.

R3. learners schema is asymmetric.
- `current`/`target` (Math, measured or set from a diagnostic, plan.py:1934-1947) vs `rw_now`/`rw_target`
  (self-reported). `focus` holds Math domains only (api_me.py:185-192). Plan cfg mirrors the same split:
  `current/target/focus/skills` vs `rw_current/rw_target/rw_focus/rw_minutes` (plan.py:113-205).
- deps.py:28 `TARGETS = range(200, 810, 10)`; api_me.py:165-177 messages say "target is a Math score".

R4. There is no R&W sitting.
- api_tests.py:1504-1514 `_insert(..., subject="math")`: no caller passes subject; api_tests.py:1585 "tests
  stay Math for now". So `estimate(learner, "rw")` only ever sees outside_scores rows (estimate.py:128-132),
  each with low == high (zero width), source bluebook/official/other.

R5. Math pace constants.
- deps.py:21 `SECONDS_PER_QUESTION = 95`; progress.py:1450 `TIER_BUDGET_MS` (65/95/126 s, "Math tier
  defaults"); plan.py:399, 409 (`* 60 / 95`), :547 `_seconds` default 95, :635 `1.3 * 95_000`, :641
  `count * 95`; plan.js:915 `m * 60 / 95`; api_me.py:73-82 `per_session`; api_profile.py:207 "SAT question
  budget 95000". R&W real pace: 32 min / 27 questions, about 71 s.

R6. Math module shapes.
- 22 / 44 questions, 35 / 70 minutes: plan.py:293, 329-334 (kind_of), :846, 855-857 (test task count 20/44/22,
  minutes 30/70/35), :1032 (`len != 22` in checkpoints_of), estimate.py:563-590 (`need`: right_of_44,
  `m1_min` of 22), plan.py:369 / :604 (route gate, "Math tops out at 580 until module 1 reaches 14 of 22"),
  :609-616 (_tiers keyed on Math target vs 550/580/680/690). R&W module: 27 questions, 32 minutes; section 54 /
  64 min (plan.py:1420 already validates `of <= 54`).

R7. R&W evidence is display-only.
- `rw_log` is written by plan.py:1413-1428 (`log_rw`) and read only by plan.py:1397 (`rw_domains`). It does not
  feed allocation, estimate, mastery, or the R&W task split (`_rw_tasks` uses fixed `RW_SHARES` and the
  student's focus states only).
- outside_scores.rw is read by estimate.py:128-132 (`_sittings("rw")`, which nothing in scope calls),
  estimate.py:709-744 (`total`, SR4, used by api_results/api_tests), plan.py:2025 (payload score.rw.sittings),
  and drawn by charts.js:664-676 as a hatched "R&W (yours)" lane.

R8. Frontend topic tables are Math.
- ui.js:652-679 `UI.DOMAINS` (4 Math) and `UI.TOPICS` (19 Math, with glyphs and short names); ui.js:681-687
  `UI.RW_SKILL` has names only (no domain, no glyph, no short name).
- wizard.js:39-42 `DOMAINS`, `DSHORT`, `WEIGHT` (Math), `RW` (domain, share, copy); progress.js:21 `DOMAINS`.
- kit.js:2638-2650 living mark: four quadrants = four Math domains; api_shell.py:59-66 returns
  `{"math": [4 masteries]}` only.

Already subject-neutral (works for R&W today, keep it that way):
- progress.py:960-1078 `days()`: questions, minutes, words, tests, streaks count every attempt and sitting.
- progress.py:543-545: `ratings.update` runs for every clean first try with a tier, so `skill_ratings` rows
  for `rw_*` topics exist today. ratings.py:113-125 is topic-keyed and neutral.
- api_profile.py:257-283 `_practice_rank` (right answers in 7 days, all subjects).
- achievements: answered, hard_right, hours, streak, on_target, consistency, fixed, clean_set, never_twice,
  qotd, first_module/first_section/sections, challenge/podium/first_place/perfect count all subjects.
- week goals `pass_checks`, `take_module`, `minutes`; the feed (api_profile.py:533-627).

---------------------------------------------------------------------------------------------------

## 2. Study plan

### 2.1 Plan wizard (web/plan/wizard.js, server plan.validate / propose / preview)
1. Partial.
   - Step 1 starting score: Math slider or "Let the plan measure it" (20-question diagnostic on day 1,
     wizard.js:380-393, plan.py:836-861); R&W is a second slider only after "Add my R&W score"
     (wizard.js:395-403). R&W cannot be measured.
   - Step 2 targets: Math target slider with route notes (wizard.js:437-454: "14 of 22 right in module 1",
     "A perfect section reads 710-800 here", 780 cap); R&W target slider (wizard.js:465-469); Total line
     (wizard.js:462, 277).
   - Step 3: "R&W time a study day" chips 0/15/30/45/60 "On top of your Math time" (wizard.js:609-612).
   - Step 4 focus: a Section seg Math | Reading and Writing already exists (wizard.js:661-665). Math side
     shows points to gain, domain/skill focus with gains, practice-week split bar (wizard.js:669-750). R&W
     side shows 4 domain focus rows with logged misses only (wizard.js:751-765).
   - Server: plan.py:108-206 validates both; plan.py:1821-1859 `propose` fills only Math (`current` from
     Math sittings mean3, Math target default +100, plan.py:1844-1851); rw_* come from the profile.
     plan.py:1862-1914 `preview` returns `points: {"math": ...}`, `split_points: {"math": ...}`,
     `target_note` (Math route), `split` over Math domains.
2. Math-specific: ticks layer "The average Math score is 505" (wizard.js:409-419); quick targets and route
   notes (wizard.js:441-453); Math `measure` diagnostic only; `RW` copy table (wizard.js:42) names
   Words for Craft and Structure; `bar()` split uses Math DOMAINS only (wizard.js:798-802).
3. Parity needs: R&W `measure` path (an R&W diagnostic or first R&W module on day 1); R&W ticks layer with
   R&W national mean and the learner's R&W sittings; R&W target notes (R&W has its own module-1 route);
   `preview.points.rw` and `split_points.rw` once an R&W gains model exists; R&W skill focus (10 skills), not
   only 4 domains; replace `rw_minutes` (a fixed top-up) with one budget split across subjects. Keep the
   side-by-side score/target steps; keep the section switch on step 4.

### 2.2 Weekly plan generation (plan.py build_day / allocate / day_view / freeze / calendar)
1. Partial. Every in-app task is Math:
   - test task path `/api/mock/new` with `{full, timed, pause}` and no subject (plan.py:568-569, 846-863);
     Math diagnostic when measuring (plan.py:836-861).
   - warm-up `progress.warmup_candidates(learner, tz)` default math (plan.py:873); fix
     `open_traps(subject="math")` (plan.py:885); learn/check/map/focus over Math `TOPICS` from
     `allocate` (plan.py:387-466); sweep over all closed traps (plan.py:742-760, subject-neutral count).
   - R&W appears as `custom` rows "R&W · <domains> · N min", detail "On your own · Bluebook or official SAT
     practice", `start = None`, `type = "rw"` (plan.py:667-701). The only R&W thing served in-app is the
     Words task (`kind="words"`, `subject="rw"`, plan.py:959-972) from the legacy words deck, with
     `in_context`/`transitions` tweaks when Craft and Structure / Expression of Ideas are on Focus. The bank's
     `rw_*` items are never served by the plan.
   - After an R&W row is done, plan.js:1375-1395 asks for misses per domain (rw_log); ticking a Bluebook
     task asks for Math and R&W scores (plan.js:1397-1420 -> /api/scores + rwlog).
2. Math-specific: R5/R6 constants; `_why` copy ("of 44 a section", "Below the route: Math tops out at 580",
   plan.py:580-607); `_tiers` keyed on the Math target (plan.py:609-616); grid-in tilt (plan.py:645-651);
   `_check_for` before/after checks on Math topics (plan.py:704-734); `checks_of` hard-codes
   `"subject": "math"` (plan.py:1473, 1480); `checkpoints_of` twin module-1 compare needs 22 items and returns
   `"subject": "math"` (plan.py:1020-1061); `_coverage` cells over Math TOPICS and `19` (plan.py:1324-1361);
   payload `map.of = 19` (plan.py:2035-2037); week theme fallback "Math practice" (plan.py:1213); ICS
   "SAT Math · ..." (plan.py:2134) and settings.js:270, 309 "SAT Math · Up next"; `_bank` filters Math "the plan
   is Math" (plan.py:1666). `_task_status` marks a test task done by ANY finished test-kind sitting that day
   (plan.py:1111-1119), so a future R&W sitting would tick a Math test task.
3. Parity needs: an R&W allocation (R&W skill values from an R&W gains/mastery model, R&W `TOPICS`, R&W
   domain shares) dealt into the same day budget; R&W focus/learn/check/fix/warm-up tasks that start drills
   with `rw_*` topics (needs drill support, outside this scope); test tasks carrying `subject` (module/section
   per subject, and a full 2-section mock on rehearsal days); `_task_status` same-day match by subject;
   R&W pace (71 s) for counts and clocks; `checks_of`/`checkpoints_of`/`_coverage` per subject. Natural UI:
   one day list with both subjects (subject chip per task row; plan-ui.js:173 already labels "R&W").

### 2.3 Plan targets and score tile
1. Partial. Plan cfg holds `current/target` and `rw_current/rw_target` (plan.py:113-205). `api_plan._mirror`
   writes both back to learners (api_plan.py:30-37). Result logging takes `math` (required) and `rw`
   (optional) (api_plan.py:483-493; plan.js:1014-1029). Duplicate copies result math/rw into the next plan
   (api_plan.py:457-459).
2. Math-specific: score tile is Math: "Score start -> target" on a 200-800 track (plan.js:484-495), pace
   badge (plan.py:1288-1305, `_pace_suggest` over Math sittings, 780 cap), projection line (plan.js:501-502),
   needs/makes per week (plan.py:1761-1775 `verdict = {"math": ...}`), levers (plan.py:1777-1818,
   `estimate.need` path). R&W is one text line "R&W a -> b · Total x -> y" (plan.js:510-511). Plan list names
   use total target when R&W set (plan.js:301-303, 1823-1824; plan.py:1657-1658), else Math.
   `drift` banner and `measure` auto-set Math `current` only (plan.py:1934-1947, 2015-2020).
3. Parity needs: `verdict`, `pace`, `projection`, `points`, `suggest` keyed `{"math", "rw", "total"}`
   (payload already uses dict keys `math` for these, plan.py:2031-2033, so adding `rw` is the shape the page
   expects); a total tile (400-1600) with the two section tracks under it.

### 2.4 Progress (plan Progress tab, web/plan/progress.js; GET /api/plan/progress, api_plan.py:93-99)
1. Partial. Score path chart: `UI.bandChart` over `d.sittings` (Math sittings + Math outside scores),
   projection band, aims, "Math score path" (progress.js:60-93). Domains card: Math domains table (accuracy,
   time share, points share, gain) then an R&W sub-list from `rw_domains` (logged misses, minutes) with "No R&W
   results yet. Log them after a Bluebook test." (progress.js:274-299). Coverage, checks, checkpoints, bought,
   causes, calibration, skill pace: all Math (plan.py:1324-1361, 1461-1496, 1020-1061, 1695-1758).
2. Math-specific: `_progress_extra` bought over Math TOPICS, `"subject": "math"` (plan.py:1709-1727);
   `progress.causes(learner, tz, days)` default math (plan.py:1729); `progress.pace(learner)` default math
   (plan.py:1756); split_domain over Math DOMAINS (plan.py:1735-1752).
3. Parity needs: per-subject versions of domains/skills/coverage/bought/causes/pace/checks; a subject switch
   on this tab (Math | R&W), with the score path either per subject or a total path. The R&W domain card
   should read mastery from `progress.board(learner, "rw")` (works server-side today) instead of rw_log only.

---------------------------------------------------------------------------------------------------

## 3. Progress, skills, ratings

### 3.1 progress.py
1. The module is mostly subject-aware: `board`, `topics`, `warmup_candidates`, `causes`, `pace`, `fluency`,
   `types_met`, `blind`, `coach`, `_clean_rights` all take `subject` (progress.py:188, 259, 807, 1084, 1119,
   1295, 1319, 1396, 1453, 1557). `board(learner, "rw")` returns the 10 R&W skills with mastery, trend, last5,
   traps (topics come from practice.catalogue, `deps.subject_of(s) == "rw"`). R&W misses file as unnamed traps
   closed by clean answers in the skill (progress.py:98-103, 385, 490).
2. Math-specific: defaults (R1); `TIER_BUDGET_MS` (progress.py:1450); `BLUEPRINT`/`DOMAINS` are Math
   (progress.py:55-57) while `RW_BLUEPRINT` (58-59) is used only via `DOMAIN_WEIGHT`; `due_rechecks` and
   `rechecks_passed` are subject-neutral (progress.py:1098-1116).
3. Parity needs: callers pass subject (R1). Nothing to build in progress.py itself except R&W pace budgets
   and an `RW_DOMAINS` tuple next to `DOMAINS`.

### 3.2 ratings.py
1. Works mechanically: `skill_ratings` per (learner, topic), updated for R&W answers (progress.py:543-545).
2. Math-specific: `_seed_rating` seeds every topic, including `rw_*`, from `learners.current`, a Math score
   (ratings.py:76-80). `structural_priors` scores +50 grid-in, +25 figure/table, +25 rationale sentence
   (ratings.py:142-165); R&W items are all MCQ with no figure, so R&W item priors rank on rationale length
   only and are close to arbitrary within a tier. `SURVEY_SEEDS = 18` and R&W templates cycle `seed % n`
   over a few fixed items (satbank/topics/rw.py:4-5, 55-56), so an R&W (template, tier) is a handful of
   fixed items, not a generator.
3. Parity needs: seed `rw_*` ratings from `rw_now`/`rw_current`; an R&W structural prior (passage length,
   question type) or measured priors only. Single compete `learners.rating` is in section 7.

### 3.3 Skill mastery shown to the student
- Me page skills/domains: api_profile.py:355-511 builds `domains` from `progress.board(learner)` (Math) and
  `progress.DOMAINS` (api_profile.py:429-444); `catching` filters Math traps (api_profile.py:446-448);
  readiness/coverage weights only Math kinds (api_profile.py:416-428). me.js:805-968 renders them with
  `UI.DOMAINS` / `UI.TOPICS`. R&W mastery is never shown on Me.
- Parity: `subjects.rw` gets the same `domains`, `coverage`, `gains` (when a model exists), `habits`; me.js
  gets a subject switch on Skills/Readiness, side by side on Snapshot/Goals.

---------------------------------------------------------------------------------------------------

## 4. Predicted score outside tests (consumers in scope)

1. Math-only. The Math band is the latest sitting's own band (`estimate.estimate().latest`), the plan's
   pace mean, `combined` (2-3 standard sections), and the U9 projection. R&W is only what the student typed
   (outside_scores.rw or learners.rw_now).
   - Me Snapshot "Math score" band + Best + "SAT total low-high · R&W n (yours)" (me.js:664-680) from
     api_profile.py:450-466 (`total.now_low/now_high = math latest band + rw_now`).
   - Me Goals bar (me.js:466-505), "Since you started" (me.js:351-359), trend chart "Math score over time"
     (me.js:990-1005).
   - Plan tile and Progress chart (section 2.3, 2.4).
   - Levers `band`: "The latest scored sitting's Math score range" (api_profile.py:142-151).
   - PDF hero (section 5.2).
2. Math-specific: R2, R4. estimate.total (SR4, estimate.py:709-744) already models "Math measured + R&W typed",
   placed on the national total table; it is used by api_results.py:769 and api_tests.py:2473, not by Me
   (api_profile builds its own sum, api_profile.py:463-466).
3. Parity needs: R&W bands from R&W sittings, then one total estimator (both sections from sittings, a typed
   R&W only as fallback) used by Me, Plan, PDF, parent, admin. Side by side (Math, R&W) with the Total on
   top.

---------------------------------------------------------------------------------------------------

## 5. Profile, reports, PDF, parent, admin

### 5.1 Profile / me (api_me.py, api_profile.py, web/me)
1. Partial. `PUT /api/me` takes `target`, `current` (Math) and `rw_now`, `rw_target` (api_me.py:112-205),
   mirrored into the active plan (plan.py:2061-2075). Me target popover: Math slider + chips, R&W now/target as
   selects, "R&W is your own estimate." (me.js:583-650). Goals row shows "Total = Math t + R&W r (your R&W
   estimate)" (me.js:478-481).
2. Math-specific: avatar must be a Math topic slug (api_me.py:180-181, `progress.topics()`); focus domains Math
   (api_me.py:185-192); messages "target is a Math score" (api_me.py:166, 172); levers "points",
   "readiness" (Math catalogue), "pace" (95 s), `skill:`/`accuracy:`/`pace:` keys reject rw topics
   (api_profile.py:129-215, `progress.topics()` at :185, :200); `need` = Math (api_profile.py:471);
   `_self_rank` delta from Math sittings and Math board (api_profile.py:329-352); `_habits` Math only
   (api_profile.py:301-326). Week goals `fix_traps`/`reach_word` validate topics against Math topics
   (api_profile.py:805, 818) and suggestions use Math traps and Math board (api_profile.py:873-889).
3. Parity needs: R&W target/now as measured fields (or a `rw_current` measured like `current`); avatar and
   goals accept `rw_*`; levers per subject. Side by side (both targets and a Total), one Edit popover.

### 5.2 Progress PDF (progress_pdf.py)
1. Math-only. Title "SAT Math · prepared {date}", "Estimated Math score" (progress_pdf.py:35-36, and uz/ru at
   45-56). Hero scale 200-800 with band and Math target tick (progress_pdf.py:135-166). Data: api_results.stats
   (api_results.py:930-970): `answered`/`accuracy`/`by_difficulty` count both subjects, `estimate` is Math,
   `top_traps` Math; trend points from `api_results.history(kind="tests")` (progress_pdf.py:309-311), which
   lists all test sittings regardless of subject.
2. Math-specific: band = `estimate.combined` (2-3 standard sections) else `estimate.range` (min mid to max
   mid of all sittings) (progress_pdf.py:275-277); target = `profile.target` (Math).
3. Parity needs: two section heroes (or one total hero 400-1600 with two section bars), trend per subject,
   tiles split by subject.

### 5.3 Problem reports (reports.py) and admin inbox (web/admin/reports)
1. Partial. A question report on an `rw_*` item works: `_context` sets `subject = deps.subject_of(t)`
   (reports.py:555); `instant_check` regenerates via `registry.generate` (R&W topics register through
   satbank/topics/rw.py) and audits.
2. Math-specific: outcome texts "Our solver gets X from the numbers", "The numbers check out with our
   independent solver" (reports.py:448-466) and the grid-in forms branch (reports.py:420-427); `pick_rate`
   keyed by norm, and R&W misses are unnamed (progress.py:98-103), so the "signal" path never fires for R&W.
   `question()` returns `text` (the passage) (reports.py:1258) but the admin view never renders it
   (admin/reports/index.html:265-291 shows stem, choices, rationale only). Sitting reports quote
   `est low-high` (reports.py:576-581).
3. Parity needs: R&W wording for instant check (no "numbers"), passage shown in qView. No score work.

### 5.4 Parent page and emails (api_parent.py, parent_mail.py, web/parent)
1. Partial. `summary` reads `api_admin.detail` (api_parent.py:152-170): totals/week/last14 count all attempts
   (both subjects); `focus`/`strong` from per-topic accuracy, all subjects, names from Math topics only (so an
   R&W skill shows its raw slug, api_admin.py:121-127); `tests` = last 5 sittings with low/high and no
   subject; `goal.target` = Math target only.
2. Math-specific: parent.js:139 shows `goal.target` as "Target score" (reads as total); parent.js:137-138
   lists tests "low to high" (English "to" in all three languages) without subject; parent_mail.py:29, 35, 41
   "score range {low} to {high}"; no R&W target, no total.
3. Parity needs: goal = Math, R&W, Total; tests labeled by subject (and full-SAT mocks as total); strong/weak
   skills with proper R&W names. Side by side.

### 5.5 Admin student board (api_admin.py, web/admin/students, web/admin/student)
1. Partial. List: answers/accuracy/minutes/tests/open mistakes/rating over all subjects (api_admin.py:39-74),
   `target` = Math. Detail: activity mixed; skills grouped by domain with names from `progress.topics()` (Math)
   so R&W rows show slug and empty domain, grouped under "Other" (api_admin.py:121-130,
   admin/student/index.html:60); sittings with low/high, no subject (api_admin.py:132-144,
   admin/student/index.html:67); profile has `target`, `current`, no `rw_now`/`rw_target` (api_admin.py:92-96,
   admin/student/index.html:85 "Target score").
2. Parity needs: names/domains from `progress.topics("math") | progress.topics("rw")`; subject column on
   sittings; R&W goal fields; per-subject accuracy. Side by side.

---------------------------------------------------------------------------------------------------

## 6. Achievements, streaks, habits, shell

### 6.1 Achievements (achievements.py)
1. Partial. Neutral counters listed in section 1 already count R&W.
2. Math-specific: `skill:<topic>` and `domain:<domain>` rules from `progress.topics()` / `progress.DOMAINS`
   (achievements.py:89-94, 183-187, board at :120 default math); `explorer` tiers end at 386 = Math type count,
   value from `types_met(learner)` default math (achievements.py:24, 177); `climbing` = latest minus earliest
   Math sitting mid (achievements.py:146-148); `upper_route` counts any sitting route (:179).
3. Parity needs: `skill:rw_*` and `domain:<R&W domain>` rules (adventure names "Tamed: ...", "Ruler of ..."
   work as is), an R&W explorer (or combined), climb per subject or on total.

### 6.2 Streaks
- Works: progress.py:960-1078 and plan.py:1222-1242 `streak_of` count any activity. Nothing to do.

### 6.3 Habits (habits.py)
- None for R&W by design: habits.py:1 "families over SAT Math reason norms", habits.py:81-83 `families("rw")`
  returns `[]`, `family_of` stamps `subject="math"` (:86-93); api_profile.py:312 filters Math. Consistent with
  R&W misses being unnamed (progress.py:98-103). Parity only if R&W families are wanted (e.g. too broad,
  half right, off-topic, opposite, punctuation rule), which needs named R&W distractor reasons first.

### 6.4 Shell / nav (api_shell.py, ui.js, kit.js)
1. Partial. Streak, today minutes, review, words are neutral.
2. Math-specific: `me.domains = {"math": [...]}` (api_shell.py:59-66); avatar glyph only for Math topics
   (api_shell.py:69-76, api_me.py:180); living mark = 4 Math quadrants (kit.js:2638-2650; ui.js:2191 passes
   `me.domains.math`); `plan.target` = Math target (api_shell.py:166); `per_session` at 95 s (api_me.py:73-82);
   `CB_BANK = 1921` "College Board's Math question bank size" (api_shell.py:323-325). Palette "target N" sets
   the Math target and refuses 800-1600 as "a total: type the Math part" (palette.js:363-369).
3. Parity needs: `domains.rw`, an 8-part or two-ring mark, palette target for rw and total, CB bank count per
   subject.

---------------------------------------------------------------------------------------------------

## 7. Compete

Full detail with every file:line: compete.md in this folder (cp = server/compete.py, ac = server/api_compete.py,
cui = web/assets/compete-ui.js, ov = web/compete/overview.js, ct = web/compete/contest/contest.js,
lb = web/compete/leaderboard/leaderboard.js, rk = web/compete/rankings/rankings.js). Summary:

| Mode / board | R&W today | Key evidence | Natural UI |
|---|---|---|---|
| Daily Challenge `daily-<day>` | math-only | cp:388-405, `_daily_slots` cp:194-205 on challenge.MIX (Math 3/3/2/2), SPR slots, 950 s = 10 x 95 | two Daily cards side by side |
| Legacy /api/challenge | math-only | ac:28-74, ac:35 uses 95 s | keep for old links |
| Sprint `sprint-<week>` | math-only | cp:208-227 rotates challenge.MIX; 60 fresh items per run, repeat runs | per-subject sprint |
| Rush `rush-<week>` | math UI, leaky API | domain validated against `blueprint.by_domain()` which includes R&W domains (cp:519-521); session always stored 'math' (cp:549-551); `rush_next` has no subject guard (cp:576-578) | subject per Rush |
| Word Sprint `words-<week>` | partial, dormant | only R&W contest (cp:419-424, 698-850), legacy vocabulary deck (`rw.wic.*`, `rw.tr.*`), never the `rw_*` bank; unrated; not inserted unless Transitions pairs are reviewed (words.py:1104-1107) | keep as vocab game or replace |
| Weekly Module | math-only | Math blueprint 22 q, 2100 s (cp:361-369, 440); 200-wide band, "section": "Math" | R&W module 27 q / 1920 s |
| Season Final | math-only | Math M1 + routed M2, 4200 s (cp:432-440); 140-wide band; ov:334 "full Math section" | full SAT: both sections + total |
| Trap of the week | math-only | `habits.families()` Math only (cp:249-293) | needs R&W families |
| Private contests / series | math UI, leaky API | subject hard-coded "math" (cp:2319); `from_session` and `topics` accept rw templates (cp:2275-2287); sheet uses UI.TOPICS, "Grid-in" format, "95 s a question" (cui:802-968) | subject choice in the sheet |
| Leaderboard | partial | `?subject=math|rw` exists server and client (ac:305-312, cp:1909, lb:13/74/162/258) but switch hidden (lb:117); `skill` silently Math (cp:1950-1958), `test`, `climb`, `rating` ignore subject (cp:1945-1949, 2060-2078, 1969-1990); only `points`, `net`, `right` honour it | expose the switch: Math / R&W / Total |
| Contest rating / levels | single, subject-blind | `learners.rating` (cp:936-966); two inconsistent level ladders (ratings.py:47 vs cui:338-340) | per-subject rating |
| Champions / seasons | math-only | `close_champions` cp:1824-1878 never passes subject; `champions` table has no subject column | subject column |
| Records, history, badges, streak, rivals, share card | mostly subject-blind | pace-setter badge = 95,000 ms (cp:2103); challenge streak any `daily-%` (cp:2124-2161); share text has no subject (cui:277-287) | per-subject bests and pace |

Compete blockers specific to fixed R&W items (cross-cutting, also matter for mocks and the plan):
- Twin supply: `pool()` needs >= 100 distinct items per (template, tier) (cp:157-172); the R&W bank's best pair has
  68 (server/cache/twin_supply.json), so every twin contest kind would 409 for R&W. Needs a sibling-by-(skill, tier)
  or one-identical-form model.
- Leak protection is keyed (template, seed) (deps.py:223-247, `contest_items`), but R&W seeds cycle fixed items
  (`seed % n`, satbank/topics/rw.py:50-56), so the same R&W item under another seed is unprotected during a live
  contest. Needs item id (source_id) keys.
- Pacing: replace hard-coded 65/95/126 and 95 with `drill.TIER_BUDGET[subject]` / `drill.budget_ms` (drill.py:103-104,
  1273-1277), which are already subject-aware.

Compete bands (all wider than 20; none is a 400-1600 total):
- Weekly Module estimate 200 wide (scoring.py:61, set at api_tests.py:1336), shown ct:306.
- Season Final estimate 140 wide (scoring.py:87, api_tests.py:1372), shown ct:300-305, ct:507, ac:355, `final_focus` cp:1370.
- Leaderboard `test` = midpoint of the best mock band (cp:1945-1948, lb:20 "Band middle").
- Climb cohort windows +-40/80/160 (cp:2072) and `climb()` "Started lo-hi" = start +- window (cp:2090-2092): 80, 160
  or 320 wide, shown me.js:703-709 and rk:233.
- Contest "Band" column ct:597 is dead (no data sent).

---------------------------------------------------------------------------------------------------

## 8. Every score range / band / predicted score in scope

Width-setting constants (the model, not the display). Narrowing to 20 is a model decision: these are
documented as uncalibrated (scoring.py:84-86 "not as narrow as the real test's 20 points, because none of these
items are calibrated on real test-takers"; estimate.py:663-664 projection is a `ponytail:` placeholder).

| Where | What | Current width | Scale |
|---|---|---|---|
| scoring.py:61, 377-378 | `HALF_BAND = 100`: module, diagnostic, custom, any non-mock sitting | 200 | section 200-800 |
| scoring.py:87, 101-106 | `MOCK_HALF_BAND = 70`: mock / two-module section / paper; lower route caps high at 580 | 140 (less when capped) | section |
| estimate.py:274-275 | `_half`: rescoring uses 70 for SECTION_KINDS else 100 | 140 / 200 | section |
| estimate.py:151-155 | `combined`: last 2-3 standard sections, half = 70/sqrt(n), round 10 | 100 (n=2), 80 (n=3) | section |
| estimate.py:174-175 | `range`: min mid to max mid of all sittings (history spread) | variable | section |
| estimate.py:130-131 | outside score row low = high | 0 | section |
| estimate.py:158-165 | confidence copy "One full section narrows it to about 140 points", "within 100 points" | copy | section |
| estimate.py:661-686 | `project`: half = clamp(60, 150, latest half + err) | 120-300 | section |
| estimate.py:729-744 | `total`: Math band + one R&W value | = Math band (140/200) | total 400-1600 |
| plan.py:1295-1301 | `_pace_suggest`: "On pace" if within 35 of expected | tolerance 70 | section |
| plan.py:1007-1010 | `_test_band`: test task result low/high and beat/under/within the aim | sitting band | section |

Display sites in scope:

| File:line | Shows | Width today | Scale |
|---|---|---|---|
| plan.py:1283-1285 -> progress.js:60-93 | sittings as bands in "Math score path"; copy "±70 for a module or section, ±100 for the diagnostic" (progress.js:93; module is actually ±100, api_tests.py:1369-1372 keeps scoring.score's band for single modules) | 140 / 200 | section |
| progress.js:68, 77 | projection band "At this pace" | 120-300 | section |
| plan.js:490-495 | score track 200-800, pace band drawn as mean ±35 | 70 | section |
| plan.js:501-502 | "At this pace L-H on <date>" | 120-300 | section |
| plan.js:510-511 | "R&W a -> b · Total x -> y" | points | R&W section + total |
| plan.js:301-303, 374-383, 1823-1824 | plan name/target: total if R&W set else Math | point | total or section |
| plan-ui.js:224 | test task verdict "within the band" | sitting band | section |
| plan.py:1617-1659 `_summary` / plan.js:1014-1029 | plan result: Math (+R&W) typed, total sum | point | section + total |
| wizard.js:366-373 | "Latest · kind · date · low-high" | 140 / 200 | section |
| wizard.js:409-419 | your sittings as bands on the 200-800 slider | 140 / 200 | section |
| wizard.js:277, 399-400, 462 | Total = Math + R&W | point | total |
| wizard.js:453 | "A perfect section reads 710-800 here" | 90 | section |
| api_profile.py:142-151 | lever `band`: latest Math range | 140 / 200 | section |
| api_profile.py:450-455 | `score.points`: every Math sitting band + outside points | 140 / 200 / 0 | section |
| api_profile.py:463-466 | `goals.total.now_low/now_high` = Math latest band + rw_now | 140 / 200 | total |
| api_profile.py:467 | `goals.subjects.math.band` | 140 / 200 | section |
| me.js:351-359 | "Since you started" band -> band | 140 / 200 | section |
| me.js:484-493 | Goals bar 200-800 with latest band and target tick | 140 / 200 | section |
| me.js:503 | "a 780 puts 800 inside your band" | copy | section |
| me.js:669-677, 731 | Snapshot "Math score" band, Best band, "SAT total low-high" | 140 / 200 | section + total |
| me.js:995-1005 | trend bandChart "Math score over time" (+ projection when sent) | 140 / 200 | section |
| progress_pdf.py:275-277, 135-166 | PDF hero band = combined or range, on 200-800 | 80-100 or variable | section |
| progress_pdf.py:223-260, 309-311 | PDF trend: per test low/high | 140 / 200 | section (mixes subjects) |
| api_parent.py:160 -> parent.js:137-138 | recent tests "low to high" | 140 / 200 | section, unlabeled |
| parent_mail.py:89, 29/35/41 | alert "score range {low} to {high}" | 140 / 200 | section, unlabeled |
| api_admin.py:137-144 -> admin/student/index.html:67 | sittings "low to high" | 140 / 200 | section, unlabeled |
| reports.py:576-581 | sitting report context "low-high" | 140 / 200 | section |
| achievements.py:146-148 | climb = latest mid - earliest mid | point | section |
| api_profile.py:329-352 | `_self_rank.estimate` = mid delta over 30 days | point | section |
| compete.py:2072, 2090-2092 -> me.js:703-709 | climb "Started lo-hi" cohort window | 80 / 160 / 320 | section |
| compete (ct:300-306, ct:507, ac:355, lb:20) | contest module / Final bands | 200 / 140 | section |
| charts.js:434-790 | `bandChart`: draws whatever widths come in; `est` zone (:561), projection, R&W lane 200-800 (:664-676) | as given | default 200-800 |
| charts.js:800-811 | `gauge` default 200-800 | as given | section |
| kit.js:1874, 2933-2936 | `scoreSlider` default 200-800; `UI.SUBJECT` math/rw min 200 max 800 | n/a | section |
| palette.js:363-369 | "target N" 200-800 Math; 800-1600 refused as total | n/a | section |

Notes for the 20-point goal:
- Every band in scope is a sitting's stored `result.estimate` (set at finish by scoring.py) or a sum of it with
  a typed R&W. Display code reads `low`/`high` and needs no change to draw a 20-wide band, except fixed visual
  widths: plan.js:494 (mean ±35), progress.js:93 copy, wizard.js:453 copy, me.js:503 copy, estimate.py:158-165
  copy.
- Total bands (400-1600) are only ever a Math band plus a point. A 20-wide total needs both sections from
  sittings (R4), or a total model; adding two 20-wide section bands gives 40, so the total needs its own width.
- Stored history: finished sittings keep their old 140/200 bands in `sessions.result`; `estimate._sittings`,
  `percentile`, `growth` read those as stored (estimate.py:120-127, 195-206). Decide whether to re-band history.
- Scales: every chart/track/slider in scope is 200-800 (plan.js:490-491, me.js:486, wizard.js:409, 456,
  progress_pdf.py:149-151, charts.js:506-512, 666, kit.js:1874). A total view needs 400-1600.
