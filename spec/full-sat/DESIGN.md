# Full SAT: every feature for both subjects, full mocks, 20-point ranges

The owner's ask (2026-10-22): "every part of the website should be not math only, but full sat. If a
function exists for SAT Math, the same function should exist for English (Reading and Writing). We can
now have full mocks with both English and Math. Narrow the score calculation to a range of at most 20,
e.g. 1490-1510. Take your time: quality and consistency."

Maps of what is Math-only today (read the one for your area before you start):
- tests, mocks, scoring, results, every score range: `MAP/tests.md`
- practice, drills, review, Today, Up next, daily, challenge: `MAP/practice.md` (+ review-notes.md, today-notes.md)
- plan, progress, profile, parent, admin, PDF, achievements, shell, compete: `MAP/plan.md` (+ compete.md)

`MAP` = spec/full-sat/MAP (line numbers there were taken before the build started; re-read before editing)

## 0. House rules (all agents)

- Read the repo's CLAUDE.md files: no em dashes anywhere (code, comments, UI, docs); buttons use `.pill` /
  `.btn` / `.quiet` only, run `python3 tools/check-ui.py` after UI changes; long helper text folds
  automatically (`FOLD_SEL` in ui.js), use `data-nofold` for text that must always show.
- Match the surrounding code: its comment density, naming, idiom. Comments say why, briefly.
- Several agents edit this one working tree at the same time. Edit files only with the Edit tool (exact
  replacements); never rewrite a whole file, never `git checkout`/`stash`/`reset`, never format a file.
  If an Edit fails because the file changed, re-read and retry. Stay inside your ownership list (section 7);
  if you need a change in a file another agent owns, write the request in your report instead.
- Do not commit, do not deploy. Never touch prod or `server/satfreshman.db`.
- Run servers only on your own port with a scratch DB copy and `SATF_EMAIL_ONLY=0`.
- Baseline: every check passes today (`SATF_EMAIL_ONLY=0 PYTHONPATH=. python3 server/test_flow.py` and each
  `server/checks/*.py`; s1/s6/s7/s8/s10 need `SATF_DB=<dir named server>/sN.db` copies). Keep them passing;
  when a check asserts the old behaviour (a band at least 100 wide, "Math sets stay Math", subject defaults),
  update the check to the new rule, never delete it.

## 1. Subjects

- `"math"` and `"rw"`. Labels: "Math", "Reading and Writing" (short "R&W" only where space is tight).
- Server: an endpoint that serves or filters by subject takes `subject` (query or body). When absent it is
  INFERRED from what the request names (topics, templates, question ids, trap ids, the parent session for
  again / rematch / retake / twin / from_session); Math only when nothing tells. One helper does this:
  `deps.infer_subject(*names, parent=None, default="math")` (built by the lead, see section 8).
- Never mix subjects inside one set, test, estimate, percentile, median or leaderboard unless the thing is
  explicitly "both" (Today's queue, a full SAT, totals, streaks, volume counts).
- Client: one shared choice. `UI.subject.get()` returns `?subject=` when present, else the remembered
  choice (`localStorage satf.subject`), else "math"; `UI.subject.set(s)` remembers it.
  `UI.subjectSeg(host, {value, onChange, both})` draws the Math | Reading and Writing segmented control
  (`both: true` adds "Both" first, for lists). Every page with per-subject content puts it in the same place
  (top of the page content, under the title) and keeps it in the URL (`?subject=rw`) so links and reloads
  agree.
- Per-subject pages (a switch): Practice (exists), Review and Mistakes, Tests, Results list (Both | Math |
  R&W), the plan's Progress tab and skills, Compete boards, the bank browser.
- Side-by-side pages (no switch): Me / profile scores and targets, the plan's score tile, Today's header
  score, parent page and emails, admin student page, progress PDF: Total, then R&W, then Math (College
  Board's order).
- Mixed by design: Today and Up next queues hold both subjects' items; streaks and volume count both.

## 2. Tests

Real digital SAT: R&W first (2 modules x 27 questions, 32 minutes each, module 2 routed), a 10-minute
break, then Math (2 x 22, 35 minutes each). Calculator and reference sheet are Math only. R&W has no
grid-ins; every R&W item has a passage (`text`), sometimes a table or figure.

- Every test kind takes a subject: section, single module (m1 / m2 upper / m2 lower, harder / easier
  module 1), custom, twin, diagnostic, paper, shared test, archive. The row's `subject` column is set from
  it (no more hard-coded "math").
- R&W module blueprint: domains per module, module 1 / module 2: Information and Ideas 7/7, Craft and
  Structure 8/7, Expression of Ideas 5/6, Standard English Conventions 7/7 (54 total: 14 / 15 / 11 / 14,
  College Board's published shares 26 / 28 / 20 / 26 per cent, material/cb/specs.json). Skills inside a
  domain follow `R&W SKILL_WEIGHT` (College Board Question Bank proportions, the 5k bank plan): Command of
  Evidence 649, Inferences 328, Central Ideas and Details 323 | Words in Context 776, Text Structure and
  Purpose 443, Cross-Text Connections 181 | Rhetorical Synthesis 513, Transitions 487 | Boundaries 658,
  Form, Structure, and Sense 642. So a module carries about one Cross-Text item, three to four Words in
  Context. Tier mixes: Math's mixes scaled
  to 27 (module 1 9/9/9; module 2 lower 13/10/4; upper 4/10/13; harder / easier module 1 like upper /
  lower). Order inside a module is Bluebook's: Craft and Structure (Words in Context, Text Structure and
  Purpose, Cross-Text Connections), Information and Ideas (Central Ideas and Details, Command of Evidence,
  Inferences), Standard English Conventions (Boundaries, Form, Structure, and Sense), Expression of Ideas
  (Transitions, Rhetorical Synthesis); easiest to hardest inside each skill. No question is repeated
  inside a sitting and none the learner has already seen when an unseen one exists.
- R&W diagnostic: 20 questions, 5 per domain (1 easy, 2 medium, 2 hard), several fixed forms like Math's.
- R&W twins and paper / pressure re-draws: a written item has no "new numbers" version, so the twin of an
  R&W item is an unseen item of the same skill and tier (same template first when one is left).
- Full SAT (new kind `full`): two linked sittings, one per section, each a normal section sitting
  (`cfg.full = {id, part}`: part 1 R&W, part 2 Math). Handing in R&W creates the Math sitting and returns
  it in `done.next`; the client shows Bluebook's break (10:00 countdown, "Resume testing" ends it early),
  then the Math lobby begins. The break is not a gap between modules (the 75 s rule does not apply to it);
  a break longer than 10 minutes plus 60 s slack leaves both sections scored but marks the Math section
  unranked with the reason "long break", like the other timing rules. Stopping after R&W leaves a complete, scored R&W section. Results group the two
  by `full.id`: one "Full SAT" row with the total, a full result page (total, then each section with its
  report link). Tests overview, history, percentiles and "previous best" compare like with like
  (full with full, R&W section with R&W section).

## 3. Scores (the 20-point rule)

- Every score range shown anywhere is at most 20 points wide: a section 200-800 range is centre +- 10
  (e.g. 740-760), a total 400-1600 range is (R&W centre + Math centre) +- 10 (e.g. 1490-1510), rounded to
  10, clamped to the scale. A total is never the sum of two section ranges.
- One function makes every band: `scoring.band(centre, scale=(200, 800))` and
  `scoring.total_band(rw_centre, math_centre)` (built by the lead). No other file computes a width;
  `HALF_BAND`, `MOCK_HALF_BAND`, projection clamps, plan.js's +-35 track band, index.html's +-30, compete's
  climb ranges all go through it. Copy that quotes a width ("+-70", "200-point band") is updated.
- R&W section score: the same weighted heuristic as Math (`WEIGHT`, `ANCHORS`), the same routing rule, and
  a lower-route ceiling of 580 (College Board publishes 580 for Math; for R&W there is no published number,
  so 580 is a stated choice, said so in the comment).
- Stored history: finished sittings keep their old 140 / 200-wide bands in `sessions.result`. A one-time,
  idempotent migration in `db.py` re-marks each scored sitting through the new band function (from its
  centre, keeping a capped high), keeps the original as `estimate.was = {low, high}`, and records that it
  ran; the lead backs up prod before deploy.
- The scoring.py docstring and any page text that argued for wide bands is rewritten: the range is an
  estimate from uncalibrated items, shown to +-10 by the owner's choice; it is not a College Board score.

## 4. Estimates, plan, progress (summary; details in MAP/plan.md)

- R&W is measured from R&W sittings and R&W answers exactly as Math is (estimate, projection, growth,
  calibration, gains / need, pace at 71 s a question). A logged Bluebook result still counts as evidence
  for its subject. The total comes from `estimate.total(learner)` everywhere it is shown.
- The plan schedules in-app R&W work (R&W practice on the R&W bank, R&W modules and sections, full SATs
  near the exam) the way it schedules Math; the "On your own · Bluebook" R&W rows go where an in-app
  version now exists. Targets: R&W and Math targets; a total target is their sum.

## 5. Practice, review, Today (summary; details in MAP/practice.md)

- Fix subject inference once (`drill.resolve` and every caller), `again` keeps the subject, the fallback
  coach pick takes the subject.
- Fixed items: every "one more like this" path (twin, repair, final round, prove, again, print, examples)
  falls back to an unseen same-skill same-tier item for R&W; never show an item's key twice; never serve
  the question on screen as its own example.
- R&W misses are not "grid-in" misses; R&W trap labels are stable per skill / template.
- Math tools (calculator, reference sheet, grid / ask axes, Desmos, word cards) do not appear in R&W sets.
- Today and Up next include R&W items; Review, Mistakes, walk, sheet and print take the subject switch.
- Stale "R&W bank is coming" code paths are removed.

## 6. Compete (summary; details in MAP/compete.md)

- Contests, Rush, private contests, the daily challenge and leaderboards take a subject. R&W per-player
  questions are unseen same-skill same-tier items (the bank has no 100-item templates). R&W items never
  leak into Math boards. The leaderboard's subject switch is shown.

## 7. Ownership (one agent per area; the lead owns the shared files in section 8)

- A scoring-estimate: server/scoring.py, server/estimate.py, server/db.py (migration only), the width
  assertions in server/checks/*.py other than the files another agent owns (send those owners the rule).
- B tests-server: server/api_tests.py, server/blueprint.py, server/test_flow.py, server/papers.py,
  server/sets.py, server/forms.json (+ new R&W forms file), server/mocks.json, server/api_results.py,
  tools/build_mocks.py, server/checks/s5.py, s6.py, f5.py.
- C tests-web: web/test/, web/tests/, web/results/, web/diagnostic/, web/assets/results-ui.js,
  web/assets/report.js. runner.js / runner.css belong to D: send D what the exam mode needs (or, for an
  exam-only branch D agrees to, make the one Edit and say so in both reports).
- D practice: server/drill.py, server/practice.py, server/api_practice.py, server/review.py,
  server/api_review.py, server/api_today.py, server/next.py, server/daily.py, server/api_bank.py,
  server/prefs.py, server/progress.py (all of it: E and A call it with an explicit subject and send D any
  change they need inside it), web/practice/, web/review/, web/mistakes/, web/index.html, web/s/,
  web/assets/quick.js, web/assets/question.js, web/assets/runner.js, web/assets/runner.css,
  server/checks/rw_bank.py, s3.py, s4.py, s10.py.
- E plan-profile: server/plan.py, server/api_plan.py, server/api_profile.py, server/api_me.py,
  server/progress_pdf.py, server/parent_mail.py, server/api_parent.py, server/api_admin.py,
  server/achievements.py, server/ratings.py, server/api_shell.py, server/habits.py, web/plan/, web/me/,
  web/parent/, web/admin/, web/assets/plan-ui.js, web/assets/charts.js, web/assets/palette.js,
  server/checks/s7.py, f4.py.
- F compete: server/compete.py, server/api_compete.py, server/challenge.py, web/compete/, web/challenge/,
  web/assets/compete-ui.js, server/checks/s8.py.

## 8. Shared contracts the lead builds first

- `deps.infer_subject(*names, parent=None, default="math") -> "math" | "rw"`.
- `scoring.band(centre, scale=(200, 800)) -> {"low", "high", "mid"}`; `scoring.total_band(rw_mid, math_mid)`;
  `scoring.HALF = 10`; `scoring.section_score(result, route, subject="math")`.
- `blueprint.SPEC[subject]` = {module_size, module_seconds, domain_split, tiers, order} and
  `deps.SECONDS_PER_QUESTION` per subject (`deps.PACE = {"math": 95, "rw": 71}`).
- Client: `UI.SUBJECTS`, `UI.subjectLabel(s, short)`, `UI.subject.get/set`, `UI.subjectSeg(...)`,
  `UI.RW_DOMAINS`, `UI.RW_SKILL` (exists), `UI.topicName(topic)` for any subject.
