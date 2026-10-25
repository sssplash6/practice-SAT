# Contracts between the build agents

Each owner writes its section as soon as the shape is decided (before finishing the code), then keeps
it current. Readers: build against what is written here; if it is missing, do the independent parts first.

## A: scoring and estimate (owner A)

Status: built 2026-10-22 (scoring.py, estimate.py, the db.py migration), in the shapes below.
Every `subject` below is `"math" | "rw"` and defaults to `"math"`, so today's calls keep working.

### Bands (server/scoring.py): the only places a width is made

- `HALF = 10`. `HALF_BAND` and `MOCK_HALF_BAND` stay as aliases of it (api_tests `_up_to` reads one).
- `band(centre, scale=(200, 800)) -> {low, high, mid}`: `low`/`high` ints on tens, always 20 apart (at an
  edge it slides inside: 800 -> 780-800); `mid` = the unrounded centre (1 decimal).
- `total_band(rw_mid, math_mid) -> {low, high, mid}` on 400-1600: the summed centres +- 10. Pass `mid`s,
  never add two ranges.
- `section_band(centre, route, subject="math") -> {low, high, mid, capped}`: `band` plus the lower route's
  ceiling (`CEILING[subject]`, 580 both). Capped = `ceiling-20..ceiling`, `mid = min(centre, ceiling)`.
- `section_score(result, route, subject=None)`: subject from `result["subject"]` when not passed. Returns
  `{low, high, mid, capped, section, scale, route}`; `score()`'s estimate is `{low, high, mid, scale, section}`.
- Reading a stored band: use `estimate["mid"]` when present, else `(low + high) / 2` (rows stored before
  the migration below have no `mid`).

### Stored history (server/db.py, once, kv flag `reband:20`)

Every finished sitting's `result.estimate` is re-marked to 20 wide from its centre (from `result.domains`
when present, else the old midpoint), capped again on a lower route, with `mid` added and the old ends
kept as `estimate.was = {low, high}`. `result.rescored[].before/after` and `result.pressure.ceiling` get
the same treatment. Helper for readers: `estimate._mid(band)` (stored `mid`, else the middle of the ends).

### server/estimate.py

- Sitting item (from `_sittings(learner, subject)`, and in `estimate()`'s latest/previous/best):
  `{id, kind, low, high, mid, at, capped, route, standard, outside, why | source}`. A logged outside score
  is `low == high == mid` (`kind: "outside"`, `source` bluebook/official/other).
- `current(learner, subject="math") -> None | {low, high, mid, capped, n, source, at, id}`: "your current
  score" in a subject, the ONE rule every page uses (Tests, Results, Me, plan tile, Today, parent, admin,
  PDF, totals). The latest up to 3 scored sittings and logged scores (`n` of them): 2-3 = `band(mean of
  their mids)`, held under the lower route's ceiling (`section_band(mean, "lower")`) only when every one
  of them was capped; 1 = that sitting's own stored band (a logged point gets `band(point)`). None of
  them: the typed score (`learners.rw_now` for R&W, `learners.current` for Math), `n: 0`, `source:
  "self"`; else None. `source` = `"measured"` when an in-app sitting is among them (`id` = the newest
  one), else the logged score's source. `at` = the newest one's full ISO timestamp (format it in local
  time). No age window.
- `estimate(learner, subject) -> {subject, latest, previous, best, range, mean3, combined, confidence,
  trend, routed_up, counted}`, everything from that subject's sittings and logged scores only.
  `combined` = `band(mean mid of the last 2-3 ranked sections)` + `n` (None under 2).
  `range` = `current(learner, subject)` exactly (same shape; None with nothing at all). It is no longer
  a spread of sittings; copy that calls it "the spread of your sittings" must change.
- `total(learner, sid=None) -> None | {low, high, mid, pct, parts, gap, rw_history}`: `total_band` of an
  R&W centre and a Math centre. Without `sid` each side is `current(learner, subject)`. With `sid`, the
  `sid` sitting (and, for a full SAT part, its partner) for its own subject, `current()` for the other.
  None when either side is missing (two typed scores do make a total; check `parts[].source`).
  `parts = [{subject: "rw", low, high, mid, capped, n, source, at, id, value}, {subject: "math", ...same}]`
  (R&W first); a `sid` part is `n: 1, source: "measured", at: <finished ISO>`; `value` = mid on tens.
  `pct = national(low, high, "total")`.
  `gap = {target, above_high, math_path, rw_to_target} | None` (target = Math + R&W targets).
- `projection(learner, to_day=None, subject) -> None | {mid, low, high, half: 10, slope, slope_used, n,
  to, label}`; low/high = `band(mid)`. `project(points, to_day, half_latest=None)`: `half_latest` is
  ignored (kept for api_today's call).
- `growth(learner, subject) -> None | {since_first, first, n, pct}` (peers of the same subject only).
- `calibration(learner, subject) -> {pairs, latest, inside, checked}`: that subject's logged
  Bluebook/official scores against that subject's sections.
- `gains(learner, subject)`, `route(learner, subject)`, `practice_delta(learner, since, subject)`: as
  before, now real for R&W (skills = `blueprint.RW_SKILL_WEIGHT`, domains = `scoring.RW_DOMAINS`; R&W has
  no grid-in extra). `skills[].per_test` is out of the section size (44 Math, 54 R&W).
- `need(target, learner=None, subject) -> {target, reachable, ceiling, right_of_44, now_of_44, of, m1_min,
  m1_of, where, path}`: the key names stay; for R&W `right_of_44` / `now_of_44` are out of `of` = 54 and
  `m1_min` out of `m1_of` = 27.
- `time_cost(learner, pace=None, subject)`: points the clock costs at that subject's pace.
- `shares(subject)`, `model(rows, subject)`, `domain_of(subject)` (`DOMAIN_OF` stays the Math map).
- `percentile(sid)`: peers are first ranked sittings of the same kind AND subject.
- `national(low, high, subject)`: subject `"math" | "rw" | "total"` (College Board's tables).
- `rescore` / `ledger` / `rescore_sitting`: unchanged shapes; the band is `section_band`, `mid` is the
  centre held at the ceiling, `ledger.route.cap_cost` = all-right centre minus the ceiling.

## B: tests server (owner B)

Status: written 2026-10-22 before the code; fields marked (later) may land after the rest.

### Making a sitting

- `POST /api/mock/new` body gains `subject: "math" | "rw"` and `kind: "full"`.
  - `kind` section / module (m1, m2u, m2l, harder / easier module 1) / paper: `subject` from the body,
    default `"math"`. A paper is one section of one subject (R&W papers are their own paper numbers, see
    Papers below); asking for paper n with the other subject is 422.
  - custom: `subject` from the body, else inferred from `custom.topics` (R&W skills are `rw_<skill>`,
    e.g. `rw_words_in_context`), else from `custom.from_session`'s sitting, else math. Every topic must
    be of that one subject (422 otherwise). `custom.topics` now allows up to 29. R&W custom tests are
    multiple choice only (`formats` is ignored for R&W). Default count = module size (22 Math, 27 R&W).
    `saved` / `mistakes` / `traps` sources keep only that subject's items.
  - twin: always the twinned sitting's subject. shared: the set's items' subject.
  - `kind: "full"` = the full SAT (Reading and Writing, break, Math). `subject` is ignored. The response
    is the R&W sitting's payload (a normal two-module section in its lobby).
  - Legacy, unchanged: the old body `{"full": true}` still means "a Math section" and `{"full": false}`
    "Math module 1". Never send `full: true` to mean a full SAT; send `kind: "full"`.
- `POST /api/session` (diagnostic) body gains `subject` (default math). R&W: 20 questions, 5 per domain
  (1 easy, 2 medium, 2 hard), drawn from fixed forms (ids 101+), Bluebook order (domain by domain).

### The sitting payload (GET /api/session/{sid}, begin, cfg, pause, mock/new)

- `subject`: the row's subject. `modules`: `[{subject, n, questions}]` with 27 per R&W module, 22 Math.
- `duration` / `seconds`: R&W modules 32:00 (1920 s), Math 35:00; a diagnostic or custom test is
  `n x 71 s` R&W, `n x 95 s` Math (times the timing factor).
- `calculator`: always `false` for R&W. Questions carry `text` (the passage) as before.
- `section`: for a full SAT part `"Section 1, Module 2: Reading and Writing"` (Bluebook's header);
  otherwise as before with the right subject name.
- `kind`: `"full"` for both parts of a full SAT; `kind_label` `"Full SAT"`.
- `full` (only on a full SAT part, and on its `in_progress` row): `{id, part, of: 2, number}`; `number` is
  the learner's full SAT count, the same on both parts (the Math half of the first one is #1). `id` is the R&W sitting's id (the full SAT's
  id). On part 2 (Math) also `break`: before Begin `{since: <R&W hand-in ISO>, seconds: 600,
  limit_seconds: 660}`, after Begin `{ms, long}`.
- `ranked` / `why` (live chip): a part-2 lobby already shows `why: "long break"` once 11:00 have passed.
- Highlights: `marks[].at` now also accepts `"p"` (a mark on the passage `text`).

### Handing in (POST /api/session/{sid}/finish, the last module)

`done` as before, with `subject` and `estimate` of this sitting's subject (previous / best / headline
compare with the same subject only). On a full SAT part:
- part 1 (R&W): `done.next = {id, subject: "math", part: 2, href: "/test/?s=<id>", break_seconds: 600}`.
  The Math sitting is created at this moment, in its lobby, with the R&W sitting's options. A repeated
  finish (`already: true`) returns the same `done` (with `next`). `done.full = {id, part: 1}`.
- part 2 (Math): `done.full = {id, part: 2, total: {low, high, mid} | null, rw: {low, high} | null,
  math: {low, high} | null, previous: {low, high} | null, best: {low, high} | null,
  href: "/results/full/?id=<id>"}`. `total` = `scoring.total_band(rw mid, math mid)` (20 wide, 400-1600).
- The break (the client's 10:00 countdown, "Resume testing" = Begin on the Math sitting) is measured
  server side at the Math sitting's first Begin: `Begin - R&W hand-in`. Over 11:00 (10:00 + 60 s slack)
  both sections stay scored and the Math sitting is unranked, `unranked_why: "long break"`. The 75 s
  between-modules rule does not apply to it.
- Stopping after R&W: the R&W section is complete and scored on its own. The Math sitting waits in
  `in_progress` (a normal lobby); discarding it (`POST /api/session/{sid}/discard`) leaves the R&W section.

### GET /api/full/{id} (a full SAT's result; `id` = either part's sitting id)

```
{id, kind: "full", number, status: "rw" | "break" | "math" | "done" | "stopped" (Math discarded), started, finished,
 ms: int | null,                          // both finished sections' times summed
 previous: {low, high, mid} | null,       // the learner's last earlier full SAT's total (the latest while this one runs)
 total: {low, high, mid} | null,          // both sections scored
 national: {low_pct, high_pct, ...} | null,   // CB total percentiles
 ranked: bool, unranked_why: str | null,  // ranked only when both sections rank
 break: {ms, limit_ms: 660000, long: bool} | null,
 sections: [{subject: "rw", id, status, finished, estimate: {low, high, mid, ...} | null, right, asked,
             route, ranked, unranked_why, href: "/results/report/?id=<sid>"},
            {subject: "math", ...same, or id: null before the break ends}]}
```
Owner-only (403 for another learner). Sections are always R&W then Math.

### Results list, tests overview, report

- `GET /api/history` gains `subject=both|math|rw` (default both). With `both`, the two parts of a full SAT
  fold into one entry `{id: <full id>, kind: "full", label: "Full SAT", subject: "both", estimate: total
  band (scale 400-1600), parts: [<rw entry>, <math entry>], finished, delta}`; with `math` or `rw` each
  part is listed as its own section entry. Every section entry of a full SAT carries `full: {id, part, number}` (a folded entry `{id, part: null, number}`).
  `delta` compares with the previous entry of the same kind and subject (full with full).
  A full SAT's section entries (and their reports) carry `label: "Full SAT"`; `counts` stay per section
  (a full SAT adds 2 to `counts.tests`, 1 to `total` when folded). History `modules[]` carry `missed`
  (= `wrong`) as the sittings list does. Server callers of `api_results.history()` (progress_pdf)
  get the folded shape too.
  The list rule (R24, folded in from the old shadow route in api_practice.py): no inline set
  (`cfg.inline` or an inline source), nothing whose `result.asked` is 0; a `source: "quick"` set is
  labelled "Quick questions". This route (api_results.history) is the only GET /api/history.
- `GET /api/stats` `tests` is `{mock, module, diagnostic, custom, full}` over both subjects, by the history
  list rule (no discarded or empty sittings): a full SAT counts once under `full`, never also as two
  `mock` sections. Clients summing tests add all five keys (results/page.js drawTotals sums three).
- "Your current score" is `estimate.current(learner, subject)` everywhere B serves one: `/api/tests`
  `estimate.current` and `estimate.headline_parts.low/high`, `/api/stats` `current`; totals are
  `estimate.total(learner)`. A sitting's own result (done, report, history, kinds last/best) stays its own.
- Dates: the client gets ISO moments (`done.since`, `levers.route.at`, `recommended.at`, `finished`); copy
  that names a day (`done.headline`, `recommended.reason`, `levers.route.day`, `cycle` dates, history
  `weeks`) uses the learner's day from `X-Tz`, not the UTC day.
- `GET /api/stats` gains `total` (`estimate.total(learner)`, A's shape) and `subject` (default math): `estimate`, `latest` / `previous` / `best`, traps,
  `why`, `gap`, `types_met` and `domains_over_time` are that subject's; answer and day counts are both.
- `GET /api/tests?subject=math|rw` (default math; top-level `subject` echoes it): `estimate`, `levers`, `gate`, `habits`, `recommended`,
  `cycle`, `twin`, `papers`, `kinds` are that subject's. `in_progress` lists every subject (rows carry
  `subject` and `full`). `kinds` gains `{id: "full", everyone, yours, last, best, percentile, last_id}`
  over finished full SATs (last / best = total mid, 400-1600), the same in both subject views; a full
  SAT's parts are not counted under "section".
- `GET /api/session/{sid}/results`: `full: {id, part, href}` on a part; `route_rule` =
  `{cut, lower_ceiling: 580, half_band: 10}` for either subject; `clock_ms` and `summary.pace_ms` per
  subject (71 s R&W); `previous` is the previous sitting of the same kind, subject and full-ness.
- Papers: `GET /api/tests` `papers` and `GET /api/papers/{n}` cards carry `subject`; R&W papers are
  separate numbers (one weekly R&W paper beside the Math one, built on first ask); posts' `about` takes
  `m1:1`-`m1:27`.

## D: practice (owner D)

Status: written 2026-10-22; the drill / review / bank parts are built (server), Today / Up next / daily
land behind them in these shapes.

### POST /api/drill and /api/drill/preview

- `subject: "math" | "rw"` is optional. When absent, `drill.resolve` infers it (`drill._subject_of`):
  1. the first topic or template the body names (`topics`, `templates`, `segments[].template`, `want`
     keys, `item` "template:seed", `trap.template`), via `deps.infer_subject`;
  2. else the larger part of its `[template, seed]` pairs (`ids` for items / saved / marked / set);
  3. else the parent sitting's subject (`again`, `rematch`, `retake`, `from_session`; `again` also
     copies `subject` from the old cfg);
  4. else what its ids point at: a shared set's code (`share`, `pool: set`: its items, else its sitting),
     College Board ids (`pool: official`, R&W ids now twin through the
     index), trap ids (`pool: redo | checks`, `mistakes`, `recheck`), attempt ids (`pool: history`),
     the larger part when mixed;
  5. else math.
  An explicit `subject` wins; topics or templates of the other subject are still a 422. A mixed id
  list keeps its larger subject and drops the rest (to practise both, send two sets).
- So callers that name something need not send `subject`. Callers MUST send it when the body names
  nothing: `{pool: 'redo'}` / `{mistakes: true}` (Fix all), `{pool: 'saved' | 'marked' | 'review' |
  'untried' | 'checks'}` with no ids, and `{source: 'due' | 'warmup' | 'quick' | 'coach' | 'today' |
  'next' | 'start' | 'probe' | 'gain' | 'sprint'}` with no topics. Without it they get Math.
- Reasons gone: `no_bank` and `rw_bank_pending` (an empty R&W pick is `no_templates` like Math's).
- Written items (R&W types hold 1 to 110 fixed items): every "one more like this" path serves an
  unseen item of another type of the same skill, same tier first, when the type is spent: /more
  (Twin, Another like this), repairs, final round, rematch slots, and a set on chosen types (twin
  body, Prove it, again, worksheet, Saved "a fresh one") goes on with the skill's other types rather
  than ending. Such a question's `why` is `{kind: "sibling", detail: "Another type of this skill: ..."}`.
- Worked examples (worked-first, Learn, the hint's "example" rung): an R&W example is an item the
  learner has not seen, never the question on screen or queued, and is remembered as seen. The hint's
  `example` now carries `text`, `table_title`, `figure_alt`, `type_name`. The hint's "strike" text for
  R&W is the option's own reason ("Struck B: ...").
- `GET /api/drill/{sid}` (`state`) carries `subject`: the session page and the runner read it for tools
  (no calculator, reference sheet, Desmos, grid-in or "same setup" axes, word cards when `rw`).
- Legacy `drill.create(learner, sid, topics, ...)` (challenge, /s items) now writes `subject` (inferred
  from its topics / items) into cfg and `sessions.subject`; a timed set's default clock is
  `count x deps.PACE[subject]`.
- `task` (a plan task's id): `YYYY-MM-DD:<kind>` with an optional `:<suffix>` of `[a-z0-9_]` (`:rw`, a
  skill slug); kinds `drill.TASK_KINDS` (fix, recheck, focus, map, learn, check, sweep, extra, test, pace,
  habit). A Review walk's drill state carries `walk` ({items, i, step}).
- Tier mixes (`tier_mix`) plan on the subject's own module mixes (`blueprint.SPEC[subject]["tiers"]`).
- An R&W type's name is its authored name (`drill.type_name`, `progress.rw_label`, `/api/types` `name`);
  `progress.open_traps` labels R&W rows with it, rows stored before included.

### The runner (web/assets/runner.js) for C

- `UI.runner(host, {subject: 'rw', ...})`: no calculator or reference sheet, pace 71 s a question
  (navigator and budgets), checkpoints after Q9 and Q18 of 27 (Math Q7 and Q14), R&W directions. In
  practice a passage question (`q.text`) hides the calculator and reference whatever the set.
  `UI.directions({subject})`. The review player hides both tools on a passage question; its question
  fields keep `text` and `table_title`.

### Other endpoints

- `GET /api/map?subject=` (default math): that subject's board and coach.
- `GET /api/types/{template}/example?tier=` with X-Learner: an R&W example is an unseen item (the tier's
  when one is left, else another type of the skill), remembered as seen; 409 `no_example` when the skill
  is spent. Without X-Learner it is the old reserved-seed pick. Python callers: `api_bank.example(t,
  want, tier, learner)`.
- `GET /api/types/match?id=`: R&W College Board ids now map (through `drill.cb_index`) to a type of the
  skill. `/api/types/match/pick` and `/api/mistakes/log` file an R&W type unnamed (no reason), labelled
  by the type.
- `GET /api/review/*` keep `?subject=math|rw` (default math): counts, due, snooze, redo, marked, saved,
  fixed, history, history.csv, ledger, calibration, trapsheet. The pages now send it.
  `POST /api/review/walk` body takes `subject` (else the larger part of the misses); a walk is one subject.
- Mistake rows: an R&W miss has `kind: "misconception"` (never "gridin"), and `label` = its question
  type (`progress.rw_label(template)`), the same on every passage. Old rows converge on the next miss.
- `progress` for A and E: `coach(learner, k, count, subject)`, `open_traps(learner, topic, subject)`,
  `due_rechecks(learner, day=None, subject=None)` (None = both), `board(learner, subject)`,
  `warmup_candidates(learner, tz, subject)`, `trap_kind(norm, miss_kind, spr, topic=None)`,
  `rw_label(template)`. Ask D for anything else inside progress.py.
- Prefs: the Learn / Build / Test mode now sets `practice.rw.*` as it sets `practice.math.*`; the builder
  saves each subject's settings under `practice.math` / `practice.rw` (presets too).

### Today, Up next, the day's questions (both subjects by design)

- `GET /api/today` takes no subject: its queue, Due rows, Mistakes card and calendar hold both
  subjects. Every row / item carries `subject` (null for a row about neither: the day's questions, Words),
  and every drill body in it carries `subject`. Review is one Due row a section with work due (`key`
  `review:math` / `review:rw`, title "Review · Math" when both show). `traps.top[]` rows carry `subject`;
  `traps.fixes = [{subject, n, body: {mistakes: true, subject}}]` (one Fix all a section; `traps.now` /
  `traps.rare` groups carry `fixes` too). `coach.subject` and `next.subject` = the Study box's subject
  (`next.box_subject(learner, tz)`: more review due plus open mistakes, Math on a tie); the page's Size
  menu can switch it. Score: `total` = `estimate.total(learner)` (or null), `sections = {rw, math}` (each
  section's latest sitting or logged score, `estimate._sittings` items), `score` / `scores` (Math sittings,
  as before), `score_rw` / `scores_rw`, `current_band` = `scoring.band(profile.current)`; no width is made
  on Today. `domains[]` lists both sections' domains, each with `subject`. `warmup` / `review` sum both
  sections and carry `by_subject`. `GET /api/calendar` days add `missed_by_subject` (a redo set a
  section) and `subject` on sittings and opened / closed traps.
- `GET /api/today/insights?subject=` (gain, pace, causes, estimate) is per subject; `answers` counts that
  subject's answers; `time_split` covers both sections' domains. Today asks for both and merges them.
- `GET /api/next`: items of both subjects (each kind lists `box_subject`'s first), each with `subject` and
  a body that carries it; per-subject singleton keys end `:math` / `:rw`. A new learner (under 8 answers)
  still gets one Math start item. `next.resolve_drill` (the Study time box) takes the body's `subject`,
  else `box_subject`, and returns it in the body.
- `GET /api/qotd`: `slots: [{slot, subject, fmt, label, bank, question, mine, saved}]`. Four slots from
  `daily.BANK_FROM` (2026-10-22): `math:mcq`, `math:spr`, `rw:bank` (an R&W bank passage item picked by
  the date, `daily.rw_question`; a learner who already met it gets an unseen item of the same type, else
  of another type of the skill, `daily.rw_for`), `rw:wic` (Words, when it can make one); days before it
  keep `rw:wic` / `rw:transition`. `bank: true` slots (math:mcq, math:spr, rw:bank) answer through
  `POST /api/qotd {slot, answer, day, ms}` -> `progress.record` and `daily.feedback` (subject and
  `sat_pace_ms` from the slot: 71111 for R&W), twin and "5 more" through `POST /api/drill {like: {day,
  slot}, count, source}` (the body gets the slot's `subject`), save through `POST /api/qotd/save`. The
  crowd of `rw:bank` counts answers on the day's own item only. `past[].marks` keys are each day's own
  slots.

## F: compete (owner F)

Status: built 2026-10-22 (compete.py, api_compete.py, challenge.py, web/compete, compete-ui.js, s8.py).

- Every contest row has a real `subject`. Ids: Math Daily `daily-YYYY-MM-DD`, R&W Daily `daily-YYYY-MM-DD-rw`
  (read the day as `id[6:16]`; `/api/contest/daily-rw` is today's), Rush `rush-<week>` and `rush-<week>-rw`,
  Weekly Module `weekly-<week>` (odd ISO weeks R&W, 27 questions, 1920 s), Final/Sprint/Trap Math only.
- R&W slots are `[template, tier, "mcq"]`; each entrant gets an unseen item of that skill and tier (the slot's
  template first). `contest_items.qhash` identifies an R&W item; `compete.live_item(template, seed)` says
  whether it is in a live contest under any seed (for `deps._protected`).
- `?subject=math|rw` (default math) on `/api/compete`, `/api/compete/me`, `/api/compete/rivals`,
  `/api/leaderboard`; `/api/contests` and `/api/compete/history` filter by it when given (history rows carry
  `subject`). `POST /api/contests` takes `subject`, else infers it from `topics`/`templates`.
- Contest rating is per subject: Math in `learners.rating/rated`, R&W in `learners.rw_rating/rw_rated` (db.py
  LATER_COLUMNS). Contest payloads (`/api/contest/{id}`, the join preview, `state_extra`) carry `subject`. `compete.rank_snapshot(learner, tz, subject)`,
  `compete.climb(learner, subject)` (lo/hi = `scoring.band` of the start), `compete.records(learner, subject)`.
- Champions: R&W podium boards are named `rw:points`, `rw:net`, `rw:change`, `rw:band`.
