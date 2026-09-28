# The other agent's next tasks (backend only)

Tasks 1-5 are DONE (2026-09-25): S9, S7, S8 servers under one check each; habits.py and bank supply merged.
Tasks 6, 7 and 8 are DONE and merged (2026-09-25). Tasks 0 and 9 are DONE on branches (2026-09-26). Tasks 10 and 11 are DONE on v2/helper-integ (not merged yet, by the user's choice). Task 12 waits for that merge.
Next: Tasks 13, 14, 15 and 16 can run in parallel (separate instances): 13 and 14 branch from v2/helper-integ,
15 and 16 from master. They touch disjoint files. Never touch v2/s7-server, v2/s8-server, v2/s9-server or any wave-2 branch.

Written 2026-09-24 for the user's helper agent. Paste one task at a time. Each is a
**feature**, so when the helper reports it done, the main session runs one
independent check and one fix (build.js, `from: 'verify'`), then merges. The
helper never merges.

## Rules for every task

- Work only in your own worktree and branch, named in the task. Start with
  `git rebase master` if the branch already exists.
- Own only the files the task names. Call other sections' modules through
  `deps.part(module, name)`, so a missing one degrades quietly. Never edit `db.py`,
  `app.py`, `progress.py`, `drill.py`, or any `web/` file.
- A missing column goes in your module's `init()`: `app.py` runs each module's
  `init` at startup (§2.10 of `spec/rebuild-v2.md`).
- Run your own server on your port with its own database:
  `SATF_DB=$PWD/server/<task>.db`. Never use port 8000 or `server/satfreshman.db`.
- Commit after each part with a real message. Never commit on a detached HEAD.
  Leave nothing uncommitted when you stop. Never push or merge.
- `spec/v2-decisions.md` wins over the specs:
  - no classes, teachers, homework or assignments;
  - Words is Reading & Writing only;
  - the daily challenge is twins.
- **Done means** your `server/checks/<task>.py` passes and
  `PYTHONPATH=. python3 server/test_flow.py` prints "all good". Then tell the
  user "<task> done" with the commit list.

## Task 0 (DO FIRST): fix the blockers the checks found in your three servers

```
The independent checks of your S7, S8 and S9 servers found real blockers. Your work now lives on these branches
(the checker copied it; S7 and S8 are rebased on master): v2/s7s, v2/s8s, v2/s9s. Use those, NOT the old
v2/s7-server, v2/s8-server, v2/s9-server.
For each: git worktree add .claude/worktrees/<name> v2/<s7s|s8s|s9s>, then read the defects in
spec/v2-state/next/<S7S|S8S|S9S>-verify1-issues.json. Fix every "blocker" except the one about the branch name
(already resolved). Fix a "followup" only if it is small. v2/s7s has one checkpoint from a fixer that was stopped
(909e603, server/checks/s7.py): keep it and continue from it.
Highlights: S8, non-members can list private contests; anon mode must show the handle (R12); Rush's rating filter
compares rounded and unrounded ratings; the create-contest body in acceptance #18. S7, checks depend on the weekday
and hardcode 386 templates (the bank has 388 now); shell_part's shape (§2.10 root keys); progress-link tokens 404
on /api/plan/shared; missing checks for swap and mirror. S9, box-3+ reviews need in-context items but no frame is
reviewed yet (serve a meaning or recall item until frames pass the gate, and say so); a same-day regrade can undo
an in-context review; GET /api/words counts need trapped, stubborn, atrisk and probable.
Rules as above. DONE per server: its checks/*.py and test_flow pass. Tell the user "S7 fixes done" (S8, S9) with
the commits. The main agent then re-checks lean and merges.
```

---

## Task 1: finish the S9 Words server

```
Continue your S9 Words server task. Your worktree is .claude/worktrees/s9-server (branch v2/s9-server); it is clean
and your last commit is 91021b1 "Implement Words run and library API checkpoint". Parts 1-2 are done.
First: git rebase master (F6's sets are merged there now).
FINISH:
3. api_words.py: complete whatever the checkpoint left open: every run (today's words W11, learn, review, placement
   W10, sprint W16), grading, word of the day (W21), bring your words (W19), sharing a list via deps.part('sets', ...),
   and the helpers other sections call: words.today_summary, words.minutes_today, words.me_stats, words.of_reason.
4. server/checks/s9.py covering every server acceptance item in the Words spec (spec/rebuild-v2.md lines
   9134-10029) and spec/v2-upgrades/words.md W1-W22.
Own files: server/words.py, server/api_words.py, server/checks/s9.py, tools/build_words.py (the derived index only).
Port 8029 with SATF_DB=$PWD/server/s9.db. Rules as in spec/v2-state/HELPER-TASKS.md.
DONE: checks/s9.py passes and test_flow prints "all good". Tell the user "S9 server done" with the commit list.
```

## Task 2: the S7 Plan server

```
Build the SERVER half of section S7 "Plan" (backend only; the pages come later from the main build).
READ: spec/v2-decisions.md (wins), the Plan spec in spec/rebuild-v2.md Part 3.6 (lines 7046-8096; take its server
items, data and endpoints), Part 4.2 S7 (line 11107), resolutions R13 (rest days in progress.days), R14 (plan
arithmetic on the server), R15 (goals mirrored with the learner) and R18(b) (the calendar feed), the S7 contract row
in §2.9 (line 445), and spec/v2-upgrades/plan.md (every server/API part; skip page layout).
SETUP: git worktree add .claude/worktrees/s7-server -b v2/s7-server master
OWN ONLY: server/plan.py, server/api_plan.py, server/checks/s7.py.
BUILD, one commit per part:
1. plan.py: generating a plan from exam date, goal, minutes and days (the setup the spec's plan wizard collects),
   its days and tasks, rest days, drift and re-planning (Plan's rules), plan.mirror(learner, fields) (PUT /api/me
   calls it), plan.shell_part and plan.today_summary(learner, tz) for Today.
2. api_plan.py: POST /api/plan, GET the plan and its days, PATCH /api/plan/{id}/tasks/{task_id} {day, status |
   to | swap} applied at once (R14; Today and Plan both use it), the plan's Words task through
   deps.part('words', 'today_summary'), GET /api/plan/ics and the token feed /api/cal/{token}.ics (R18(b)), and the
   read-only shared view /api/plan/shared/{token}.
3. server/checks/s7.py covering every Plan server acceptance item (as amended by §2.13 and plan.md).
Port 8027 with SATF_DB=$PWD/server/s7.db. Rules as in spec/v2-state/HELPER-TASKS.md.
DONE: checks/s7.py passes and test_flow prints "all good". Tell the user "S7 server done" with the commit list.
```

## Task 3: the S8 Compete server

```
Build the SERVER half of section S8 "Compete" (backend only; the pages and the runner hooks' UI come later).
READ: spec/v2-decisions.md (wins: TWIN daily challenges, meaning each student gets the same question types with their
own numbers; private contests by invite code or link, no classes), the Compete spec in spec/rebuild-v2.md Part 3.7
(lines 8097-9133; server items, data, endpoints), Part 4.2 S8 (line 11112), resolutions R3 (practice rank), R12
(board names and hidden/anon rows), R25 (achievement lists), R28 (contest sittings run inside the practice session
and test window, built by S4/S5 on your hooks), the S8 contract row in §2.9 (line 446: compete.clock,
twin_questions, finish_contest, state_extra, rate, challenge_streak, rank_snapshot, /api/contest/daily), the
"Hooks inside write paths" rule in §2.10 (progress.record calls compete.rate; finishes call compete.finish_contest),
and spec/v2-upgrades/compete.md (every server/API part).
SETUP: git worktree add .claude/worktrees/s8-server -b v2/s8-server master
OWN ONLY: server/compete.py, server/challenge.py, server/api_compete.py, server/checks/s8.py.
BUILD, one commit per part:
1. compete.py core: the twin daily challenge (twin_questions, the day's clock, the twin daily streak
   challenge_streak), ratings and rate(), rank_snapshot, and the ACHIEVEMENTS list.
2. Contests: private contests by invite code or link (create, join, schedule, closing time, the finish_contest hook,
   voids for leaving or copying), compete.due_today for Today, and shell_part.
3. api_compete.py: /api/contest/daily, contest routes, boards (practice rank R3, challenge board, contest boards)
   with R12's names and hidden or anonymous rows, rank lines, and the challenge review through deps.access.
4. server/checks/s8.py covering every Compete server acceptance item (as amended by §2.13 and compete.md).
Port 8028 with SATF_DB=$PWD/server/s8.db. Rules as in spec/v2-state/HELPER-TASKS.md.
DONE: checks/s8.py passes and test_flow prints "all good". Tell the user "S8 server done" with the commit list.
```

## Task 4: server/habits.py (an F5 item nobody built)

```
Build server/habits.py, U6's mistake families, which F5 was assigned and never built.
READ: spec/v2-upgrades/shell-me.md U6 (around line 693: "Families (server/habits.py, owner F5)": 11 families
{id, name, tell, regex} applied to named mistakes' norms) plus the habits mentions in practice.md (line 520),
review.md (line 22), plan.md (line 14) and compete.md (lines 13 and 749).
SETUP: git worktree add .claude/worktrees/habits -b v2/habits master
OWN ONLY: server/habits.py. Provide the family catalogue and reason-to-family mapping that Trap of the Week (S8),
the Review habits view (S10), Plan's gauntlet (S7) and Practice's habit source need, for example families(),
family_of(norm) and members(family). Also `python3 server/habits.py` must assert that every family spans at least 3
topics and print coverage. Leave drill.py alone: its 'habit' and 'gauntlet' sources are S4's.
DONE: python3 server/habits.py passes and test_flow prints "all good". Tell the user "habits done".
```

## Task 5: bank supply for twin challenges (C26)

```
The S8 supply survey (s8.py --supply) finds only 2 qualifying Advanced Math / easy / grid-in templates, and C26
needs 3 at the 1,000-twin floor.
SETUP: git worktree add .claude/worktrees/bank-supply -b v2/bank-supply master
Add one new easy grid-in template (two for margin) in an Advanced Math topic (equivalent_expressions,
nonlinear_functions, or nonlinear_equations_and_systems), with named grid-in mistakes (spr_mistakes), a rationale
that ends on the answer, and the audit's rules. Existing templates' output must stay byte-identical: add, don't edit.
DONE: PYTHONPATH=. python3 -m satbank check PASS on all 19 topics, tools/lint_bank.py adds no finding for the new
template, s8.py --supply passes on master plus this branch, test_flow "all good". Tell the user "bank supply done".
```

## Task 6: named mistakes for more grid-in templates

```
56 of 202 grid-in templates still name no mistake: a wrong typed answer only says "Incorrect". Grow the coverage.
READ: satbank/item.py (Item.spr_mistakes, satbank.item.gridin_mistakes), satbank/audit.py, tools/spr_coverage.py
(it lists which grid-in templates name their mistakes), and how the multiple-choice Mis(reason, value) lists
already name mistakes in each template.
SETUP: git worktree add .claude/worktrees/spr-grow -b v2/spr-grow master
For each uncovered grid-in template, pass spr_mistakes built from the template's own mistake logic. Keep a mistake
ONLY if it is a real route a student takes to that exact value for that question; a false "you made this mistake"
is worse than none, so leave a template uncovered when you are unsure. Never change satbank/item.py or audit.py.
RULE: multiple-choice output of every template stays byte-identical; grid-ins may differ only in spr_mistakes.
Prove it with a dump of seeds 0-199 (as in the lint job).
One commit per topic. DONE: satbank check PASS 19/19, tools/lint_bank.py adds no finding, test_flow "all good",
and tools/spr_coverage.py shows the new count. Tell the user "spr-grow done: N of 202".
```

## Task 7: server security and abuse audit (read-only)

```
Audit the merged server for security and abuse problems. READ-ONLY: do not edit anything; write findings only.
SETUP: git worktree add --detach .claude/worktrees/sec-audit master
Go through every route in server/api_*.py and the modules they call (deps.py learner_of and access, reports.py,
sets.py, drill.py, progress.py, words.py when merged). Look for: identity (X-Learner codes, retired codes, device
tokens, the swap middleware), access to answer keys (deps.access: live tests, today's challenge, sets), injection
(SQL built from input, regex from input: F5 had a ReDoS), unbounded work (a request that loops, generates or sorts
without a cap), file uploads (reports: types, sizes, paths), rate limits, admin routes (SATF_ADMIN_TOKEN), error
messages that leak data, and CSRF-style writes from other sites. Reproduce each finding with a curl or a TestClient
script on your own port (8039, SATF_DB of your own).
Write spec/v2-state/followups/security-audit.md: each finding with severity (critical/high/medium/low), file:line,
a reproduction, and the fix. Commit only that file on a branch v2/sec-audit (git switch -c v2/sec-audit).
Tell the user "security audit done" with the counts by severity.
```

## Task 8: the word-frequency corpus (W17)

```
Build the objective word-frequency data W17 asks for (spec/v2-upgrades/words.md, W17 "Frequency band").
SETUP: git worktree add .claude/worktrees/freq -b v2/freq master
OWN ONLY: tools/count_freq.py, tools/data/freq_sources.txt, tools/data/freq.txt. Do not edit tools/build_words.py
(it is under review on another branch; it will read freq.txt later).
List a pinned public-domain corpus in freq_sources.txt: about 300 Project Gutenberg books from 1850-1928 plus modern
US federal public-domain texts (NSF award abstracts, NASA and NOAA articles, CRS reports), about 60 million words;
record each source's URL. count_freq.py downloads each source once into a cache outside the repo, strips headers and
licences, tokenizes, and writes tools/data/freq.txt as "word count" lines sorted by count (lowercased; keep only
words appearing at least 5 times). Then print, for every headword in server/words/sat.json, its rank and the band
W17 defines (1: top 3,000; 2: to 10,000; 3: to 25,000; 4: to 50,000; 5: rarer), and the count per band.
Commit the three files (freq.txt must stay under 5 MB; drop the tail if needed). Tell the user "freq done" with the
per-band counts.
```

## Task 9: fix the security findings in files no running task owns

```
Fix these findings from spec/v2-state/followups/security-audit.md (your audit), each with its reproduction turned
into a check that now passes:
- SEC-04 outside-mistake quota: count log requests per learner and day atomically (server/api_bank.py).
- SEC-05 report uploads: enforce the byte cap on the request stream before multipart parsing, chunked too
  (server/reports.py).
- SEC-06 /api/types/match: validate the College Board ID format and length, bound the cb_unknown writes
  (server/api_bank.py).
- SEC-07 legacy creation routes: POST /api/practice and /api/mock/{num} go through writer_of, body codes included
  (server/api_legacy.py; the /api/session part of it is S5's, leave it).
- SEC-09 sample learners: use writer_of in /api/mistakes/log and guard progress.record_trap against sample:
  learners (server/api_bank.py, server/progress.py; touch only record_trap in progress.py).
SETUP: git worktree add .claude/worktrees/sec-fix -b v2/sec-fix master
Put the checks in server/checks/security.py (new). DONE: security.py and test_flow pass. Tell the user
"security fixes done". Also fix SEC-08 (the challenge board's unbounded work) on v2/s8s as part of Task 0.
SEC-01, SEC-02 and SEC-03 are in files owned by paused wave-2 sections (S1, S3, S5, S6); the main build fixes those.
```

## Task 10 (DO FIRST): make your four branches pass together

```
Each of v2/s7s, v2/s8s, v2/s9s and v2/sec-fix passes alone, but merged together on master they fail: s7.py and
s8.py raise AssertionError, and test_flow fails "warm create must finish within one second".
SETUP: git worktree add .claude/worktrees/integ -b v2/helper-integ master, then git merge --no-ff each of v2/s9s,
v2/s7s, v2/s8s, v2/sec-fix (they merge without conflicts).
Find and fix every failure on v2/helper-integ, in the files those branches own, until ALL of these pass in the same
tree: server/checks/s7.py, s8.py, s9.py, security.py, and PYTHONPATH=. python3 server/test_flow.py three runs in a
row. If the one-second timing check only fails under load, make it robust (measure the warm path correctly); don't
just raise the limit. Commit on v2/helper-integ. Tell the user "integ done": the main agent merges that one branch.
```

## Task 11: wire the frequency bands into the Words build

```
On v2/helper-integ after Task 10: tools/build_words.py sets each entry's freq_band from tools/data/freq.txt (W17's
bands), replacing the estimated values; GET /api/words rows carry it (W17 acceptance 7: every non-own row has
freq_band 1-5). Keep python3 tools/build_words.py at exit 0 and checks/s9.py passing. Commit; tell the user "bands done".
```

## Task 12: start the Words review gate (no frame can be served yet)

```
No frame is reviewed, so Words has no in-context questions yet. Build the gate W1 describes and run its first pass.
READ: spec/v2-upgrades/words.md W1 "The review gate" (tools/build_words.py --review, server/words/adjudications.json,
two independent verdicts with different "by"; a frame is servable only with two "one" verdicts naming the key).
On a new branch v2/words-gate from master after Task 10 merges: implement --review (each frame x legal key x 5 seeds as
full items WITHOUT the key, and review-queue.json). Then adjudicate as "model:helper-a": for each item decide which
options fit, blind to the key, and record the verdict. Start with the frames that cover the most senses, until every
SAT sense has at least one judged frame. The second, independent verdict ("model:helper-b") must come from a fresh
session that never saw the first verdicts. Only then may a frame get reviewed set. Commit in batches of about 100
frames. Tell the user how many frames and senses are servable.
```

## Task 13: check-ins on the learner's own day (R13)

```
Check-in due dates, record()'s day and the drill's checks pool all use UTC dates, but R13 (spec/rebuild-v2.md Part 2,
line 149) says a day is the learner's local day from X-Tz. So a student in Asia gets check-ins a day late and one in
the US gets them early (logged in spec/v2-state/followups/F5.json, "later").
SETUP: git worktree add .claude/worktrees/localday -b v2/localday v2/helper-integ
Make every check-in date local to the learner: when a mistake closes, its 3/10/30-day due dates are set in the
learner's local day (store the tz the answer came with, or the learner's last tz); the checks pool and every "due
today" count (progress, drill's checks pool, Review's and Today's due counts through progress) compare against the
learner's local today. Keep UTC timestamps in the database; only the day boundaries change. Files: server/progress.py,
server/drill.py (the checks pool only), server/checks/f4.py and f5.py. Add checks: a learner at X-Tz -300 (UTC+5)
and one at X-Tz 300 (UTC-5) each see a check-in come due at their own local midnight, not UTC's.
DONE: f4.py, f5.py and test_flow pass (three runs, including one between 00:00 and 05:00 local if you can fake the
clock). Tell the user "localday done".
```

## Task 14: production readiness: database backups and a load test

```
SETUP: git worktree add .claude/worktrees/ops -b v2/ops v2/helper-integ
1. tools/backup_db.py: an online backup of the live SQLite database with sqlite3's backup API (safe while the server
   runs), written to a dated file outside the repo (a directory set by SATF_BACKUPS), keeping the last 14 daily and 8
   weekly copies, plus --verify (open the copy, run PRAGMA integrity_check, count rows per table) and --restore
   <file> <target> (refuses to overwrite a non-empty target without --force). Never touch server/satfreshman.db in
   tests: use a temp database.
2. tools/load_test.py: start the app on your own port with a temp SATF_DB, seed N learners, then hammer the hot
   routes concurrently (drill create/next/answer, /api/today, /api/shell, /api/me, /api/words, a test sitting) for a
   set time and report p50/p95/p99 latency, errors and throughput per route, and which routes break first at 10,
   50 and 200 concurrent learners. Write the findings to spec/v2-state/followups/load-test.md with the slowest routes
   and the likely cause of each (profile the worst one).
Commit both tools and the report on v2/ops. Tell the user "ops done" with the three slowest routes.
```

## Task 15: College Board data (permission granted by phone 2026-09-27)

```
The user has an official College Board partnership and called College Board on 2026-09-27: they are fine with agents
collecting this data. Record that in every output's "source" block as {permission: "College Board, by phone to the
user, 2026-09-27; written confirmation pending"}. Still: NEVER log in, enter credentials or automate an account.
Collect only what is reachable without signing in; if a piece is only behind a login, list it for the user (it will
come as a partner export) and move on. Be polite: cache every fetch outside the repo, 1 request a second at most.
SETUP: git worktree add .claude/worktrees/cb-data -b v2/cb-data master
Collect, each with its source URLs and fetch date, into material/cb/ (metadata only: never store question text,
answers or explanations):
1. cb_index.json: the Question Bank listing {cb_id: {subject, domain, skill, tier, band}}, band 1..7 (practice.md P11,
   lines 815-840; acceptance 9 near line 934), plus the public deep-link URL pattern for an item by ID.
2. percentiles.json: the current year's national and user percentiles for the total and both section scores
   (compare with server/data/cb_percentiles.json and list differences).
3. specs.json: the test specifications: domains and skills with each domain's share of questions, and how
   College Board defines easy / medium / hard.
4. dates.json: test dates, registration, late and score-release dates, checked against server/satdates.py
   (report any mismatch; do not edit satdates.py).
5. brand.md: the rules for using "SAT" and "Bluebook" in a product's name, copy and screenshots.
6. replicas.md: what College Board's terms say about building practice questions that mirror official ones in
   structure with original numbers and wording (open question 17), quoted with links.
OWN ONLY: tools/cb_data.py and material/cb/**. DONE: each file has its source block; counts printed for 1; test_flow
"all good". Tell the user "cb-data done" with the counts and any login-only pieces.
```

## Task 16: question-bank supply survey and gap filling (additive)

```
Find the thin cells of the bank and fill them with NEW templates. Adaptive practice, twin challenges and
per-skill tiers all need at least 3 templates per (skill, tier, format) cell.
SETUP: git worktree add .claude/worktrees/bank-gaps -b v2/bank-gaps master
1. tools/bank_supply.py (new): for every skill (19) x tier (easy/medium/hard) x format (mcq/spr), count the
   templates that generate items in that cell (seeds 0-99) and print the cells with fewer than 3.
2. For each thin cell (at most 12 cells in this task; the thinnest first), add a NEW template in a new family file,
   the way bank-supply's supply.py did: a real SAT-style item, named wrong options (Mis) and named grid-in mistakes
   (spr_mistakes) that are real routes to their values, a rationale ending on the answer, and a figure or table only
   if the item carries it. ADD, never edit: every existing template's output stays byte-identical.
One commit per topic. DONE: satbank check PASS 19/19; tools/lint_bank.py adds no finding; bank_supply.py shows each
filled cell at 3 or more; test_flow "all good". Tell the user "bank-gaps done" with the cells filled.
```

## Task 17 (DO FIRST): make the server survive real traffic

```
Your load test (spec/v2-state/followups/load-test.md) shows the site failing at 10 concurrent learners (drill create and
/api/shell time out), heavy latency at 50, and "sqlite3.OperationalError: database is locked" at 200.
SETUP: git worktree add .claude/worktrees/perf -b v2/perf master
OWN ONLY: server/db.py, server/compete.py, server/challenge.py, server/api_compete.py, server/words.py, server/api_words.py,
tools/load_test.py, and a new server/checks/perf.py. Do NOT edit api_shell.py, next.py, drill.py, practice.py, api_today.py,
api_tests.py or any web/ file: those belong to sections being built right now. For slowness inside them, profile it and
write the cause and the fix into spec/v2-state/followups/perf-for-sections.md for their builders.
Fix in your files:
1. SQLite contention: WAL mode, a busy_timeout, short write transactions (BEGIN IMMEDIATE only around the writes), and a
   bounded retry on "database is locked"; no request should hold a write lock while generating questions.
2. Anything slow or synchronous in Compete (contest/twin generation on the request path: precompute or cache per day)
   and Words (GET /api/words: cache the library and per-learner state reads).
3. Re-run the load test at 10, 50 and 200. Targets: 0 errors at 10 and 50, hot-route p95 under 1 s at 50, no
   "database is locked" at 200. Record before/after in load-test.md.
DONE: perf.py, the section checks you touched (s8.py, s9.py) and test_flow pass; tell the user "perf done" with the
before/after table.
```

## Task 18: fix the Words grading crash, then Words gate verdicts, pass A

```
1. server/checks/s9.py fails on master: "OverflowError: Python int too large to convert to SQLite INTEGER" in
   test_daily_print_offline (words.grade). Fix it in server/words.py on v2/perf's sibling branch v2/words-fix from master;
   commit; tell the user "words fix done".
2. Then the review gate's first verdict pass, LIGHT version: git worktree add .claude/worktrees/gate-a v2/words-gate-a.
   The tool and plan are on v2/words-gate (merge it into your branch first if missing): 827 frames in
   server/words/gate_plan.json. For each frame x legal key judge ONE generated item (seed 0), not five. You are
   "model:helper-a". Never look at the key and never open adjudications_b.json. Keep valid rows a stopped predecessor
   left in adjudications_a.json (skip items already judged). Commit every ~100 frames. Tell the user "gate A done"
   with the one / more / none counts.
```

## Task 19: Words gate verdicts, pass B (a SEPARATE, fresh instance)

```
Run this in a different instance from Task 18, one that has never seen pass A's verdicts.
git worktree add .claude/worktrees/gate-b v2/words-gate-b. Same job as Task 18 part 2, as "model:helper-b", writing
server/words/adjudications_b.json: ONE item (seed 0) per frame x legal key over server/words/gate_plan.json (merge
v2/words-gate into your branch first if missing). Never look at the key and never open adjudications_a.json. Commit every
~100 frames. Tell the user "gate B done" with the counts. The main agent then merges both and marks agreed frames reviewed.
```

## Task 20: the S6 Results server

```
SETUP: git worktree add .claude/worktrees/s6-server v2/s6-server   (the branch exists; git rebase master first)
OWN ONLY: server/api_results.py, server/checks/s6.py.
Build every server item of the Results section: the report, history, per-skill stats (a skill on Results opens its stats and
Practice starts on only that skill: the user asked for this), R26, R35, the Tests parts (?q=, peers, notes, confidence, away,
changes), contest rows and the Ranked pill, the Flagged filter. Also: SEC-03's results part (results only to the sitting's owner,
spec/v2-state/followups/security-audit.md) and F5's follow-up (move the R24 history filter into api_results.history so the shadow
GET /api/history in api_practice.py can be deleted; tell the user it can be).
Rules as above (own files only, own port and SATF_DB, commit per part, never push or merge, never touch a web/ file: the
main build is building this section's pages right now and codes against the endpoints your spec lists, so build exactly those
endpoints and shapes). The requirements are in spec/v2-state/briefs/S6.md (sections 2-5 and 7; the brief says pages-only for the main
build, but its server items are yours). The branch already has the section's early server commits: continue from them.
ALSO (from the Results pages, followups/S6-pages.json): the new owner-only check in api_results.py returns 403 without a
learner header and stops test_flow at line 212 ("practice results were gated behind signup"): make test_flow send the header
or narrow the rule; /whatif must work for any reader (the spec), so the sample and shared views get What if; a hidden miss
must not give away its misconception in cause.evidence.norm; the 403 carries `kind` so a live challenge can say so; share
links must open for the people they are shared with; the sample sitting should match its spec (misses, named mistakes,
a second look, recovered points); the first /api/stats after seeding took ~15 s.
ALSO (from the Tests pages): /api/history?all=1 rows through api_tests.sitting_row (number, M1/M2 scores, miss and blank chips,
conditions), and GET /api/session/{a}/compare?with={b} for Compare two sittings (slot by slot and by type).
DONE: checks/s6.py passes and test_flow "all good". Tell the user "S6 server done".
```

## Task 21: the S10 Review server

```
SETUP: git worktree add .claude/worktrees/s10-server v2/s10-server   (exists; git rebase master first)
OWN ONLY: server/api_review.py, server/checks/s10.py.
Build every server item of the Review section: redo, marked, saved, history and fixed lists, R2, R5's endpoints (flags vs saved),
notes on saved questions, shares through sets, the habits view (server/habits.py is merged), check-ins due (local days are merged).
Rules as above (own files only, own port and SATF_DB, commit per part, never push or merge, never touch a web/ file: the
main build is building this section's pages right now and codes against the endpoints your spec lists, so build exactly those
endpoints and shapes). The requirements are in spec/v2-state/briefs/S10.md (sections 2-5 and 7; the brief says pages-only for the main
build, but its server items are yours). The branch already has the section's early server commits: continue from them.
ALSO (from the Review pages, followups/S10-pages.json): GET /api/drill/{id} returns cfg.walk (items, i, step) so
/review/walk/ works; POST /api/drill/preview with source 'due' returns blocks and honours drop; /api/review/item's story is
filtered by the item's norm; /api/review/redo returns causes; History's by_difficulty gives {n, right}; Fixed takes
status/sort; Marked, Saved and History take sort; a GET for type rules (the Your rules view).
DONE: checks/s10.py passes and test_flow "all good". Tell the user "S10 server done".
```

## Task 22: the S1 Account and Me server

```
SETUP: git worktree add .claude/worktrees/s1-server v2/s1-server   (exists; git rebase master first)
OWN ONLY: server/account.py, server/api_account.py, server/api_profile.py, server/achievements.py, server/mail.py,
server/checks/s1.py.
Build every server item of Account, Me, Settings and Help: sign-in (email codes, passkeys, device pairing, rotate), /api/me/summary,
feed, activity, achievements (R25, reading ACHIEVEMENTS from compete and words), export and delete, progress links and the shared
view (R18a), the diagnostic sign-up joining an account, mail. Also SEC-01 (spec/v2-state/followups/security-audit.md): a signup
must never change a verified user's name, and the response must not reveal whether an email is registered.
Rules as above (own files only, own port and SATF_DB, commit per part, never push or merge, never touch a web/ file: the
main build is building this section's pages right now and codes against the endpoints your spec lists, so build exactly those
endpoints and shapes). The requirements are in spec/v2-state/briefs/S1.md (sections 2-5 and 7; the brief says pages-only for the main
build, but its server items are yours). The branch already has the section's early server commits: continue from them.
ALSO (from the Me pages, followups/S1-pages.json): the shell's `inbox` is an object, so the phone avatar badge reads "NaN"
(send the unread count in account.shell_part); /api/health needs mail, google and the Google client ID; endpoints for "End
the old code now", a target-needs estimate for any target, /api/push/*, /api/mistakes/import; /api/me/summary needs
subjects.math.pace, score.projection and score.gaps, check-ins passed and due, week history, skills[].last and the default
board name; /api/shared/{token} needs the name and activity days; PUT /api/me must accept avatar 'initial'; feed rows:
achievement names (not "Hard Right · Tier 10"), scores as "7 / 10", report links with ?id= (not ?s=), effect counts per
sitting; lever texts must use skill names, not raw ids ("Practise nonlinear_functions").
FIRST among them: GET /api/levers?keys= (G6 in spec/v2-upgrades/product.md): every page's "how it's worked out" popovers call
it, including the streak button in the phone top bar, and today they all show "Couldn't load".
DONE: checks/s1.py passes and test_flow "all good". Tell the user "S1 server done".
```

## Task 23: the shell's Up next server (F2B backend)

```
SETUP: git worktree add .claude/worktrees/f2b-server -b v2/f2b-server master
OWN ONLY: server/next.py, server/api_shell.py, server/checks/f2.py.
Build server/next.py (queue, due, stage and resolve_drill; GET /api/next; the 'start' kind for new learners, product.md G10;
sources read through deps.part so a missing section drops its rows) and wire /api/shell.next and /api/shell.has in api_shell.py.
Also profile /api/shell's cold start (your load test: 42.6M function calls for five calls) and make it fast. Extend checks/f2.py.
Requirements: spec/v2-state/briefs/F2B.md and spec/v2-state/followups/F2.json. The main build is doing the shell's frontend (ui.js,
palette.js, quick.js, sw.js) right now against GET /api/next and /api/shell.next: build exactly those shapes.
DONE: checks/f2.py passes and test_flow "all good". Tell the user "F2B server done".
```

## Task 24: finish the S3 Today server

```
SETUP: git worktree add .claude/worktrees/s3-server v2/s3-server   (exists; git rebase master first)
OWN ONLY: server/api_today.py, server/daily.py, server/checks/s3.py.
Finish every server item of Today (Part 3.2 in full, R27 the questions of the day, R30): api_today.py and daily.py are largely built
and checks/s3.py exists (1,121 lines). Also SEC-02 (spec/v2-state/followups/security-audit.md): throwaway learner codes must not farm
the day's answer key for a second code, and the audit's perf notes for api_today in spec/v2-state/followups/perf-for-sections.md.
Rules as above (own files only, own port and SATF_DB, commit per part, never push or merge, never touch a web/ file: the main build
is building this section's pages right now against the endpoints its spec lists, so build exactly those endpoints and shapes).
Requirements: spec/v2-state/briefs/S3.md (its server items are yours). The branch already has the section's server work from the main
build (13 commits): continue from it, do not redo it.
ALSO, what the Today page builder found missing (spec/v2-state/followups/S3-pages.json, "fixer_report" and the unit reports):
seconds_per_question must default to 95 until the learner has 20+ timed answers (one 2-second answer promised "450 questions");
an endpoint for estimate.need at any target (e.g. GET /api/today/need?target=) so the target slider's "700 ≈ N of 44 right" moves;
the pace card must not count a module finished with 0 answers as "ran out of time". The Today page is built and waiting on these. ALSO: server/checks/s3.py line ~200 fails (`got["accepted"] and got["sat_pace_ms"]
== 95_000`) depending on the day's grid-in (probably no other accepted answer forms that day, so `accepted` is empty): make the
check and the server handle a grid-in with a single accepted form.
DONE: checks/s3.py passes and test_flow "all good". Tell the user "S3 server done".
```

## Task 25: finish the S4 Practice server

```
SETUP: git worktree add .claude/worktrees/s4-server v2/s4-server   (exists; git rebase master first)
OWN ONLY: server/drill.py, server/practice.py, server/api_practice.py, server/checks/s4.py.
Finish every server item of the Practice builder and session (Part 3.3, R28 for the practice session): the session endpoints,
GET /api/drill, the builder's API. Also F6's follow-up (pool 'set' through sets.serve, spec/v2-state/followups/F6.json), deleting
the shadow GET /api/history once S6's server moves the R24 filter (Task 20), and the drill perf notes in perf-for-sections.md
(drill create timed out at 10 learners in your load test).
Rules as above (own files only, own port and SATF_DB, commit per part, never push or merge, never touch a web/ file: the main build
is building this section's pages right now against the endpoints its spec lists, so build exactly those endpoints and shapes).
Requirements: spec/v2-state/briefs/S4.md (its server items are yours). The branch already has the section's server work from the main
build (7 commits): continue from it, do not redo it.
DONE: checks/s4.py passes and test_flow "all good". Tell the user "S4 server done".
```

## Task 26: finish the S5 Tests server

```
SETUP: git worktree add .claude/worktrees/s5-server v2/s5-server   (exists; git rebase master first)
OWN ONLY: server/api_tests.py, server/papers.py, server/blueprint.py, server/mocks.json, server/forms.json, tools/moderate.py,
server/checks/s5.py.
Finish every server item of Tests and the test window (Part 3.4, R28 for the test window, the Weekly Module and Season Final starts,
R32's token rules). Also SEC-03 (security-audit.md): a sitting's ID alone must not let anyone read, answer, finish or sign up on it
(ownership through X-Learner, or a server-minted secret for anonymous diagnostics), and the /api/session part of SEC-07.
Rules as above (own files only, own port and SATF_DB, commit per part, never push or merge, never touch a web/ file: the main build
is building this section's pages right now against the endpoints its spec lists, so build exactly those endpoints and shapes).
Requirements: spec/v2-state/briefs/S5.md (its server items are yours). The branch already has the section's server work from the main
build (8 commits): continue from it, do not redo it.
ALSO (the Tests pages are built on v2/s5 and read these; followups/S5-pages.json): add `type_notes` to the session payload;
GET /api/tests reads habits_last and habits_scope and each habit row lists its sitting ids; the score card's total, projection,
growth and calibration fields (the pages found them null in every test: confirm the names in the payload); the cycle's
`proved {n, of, pts}`; the hand-in's gate data gives the positions answered right (the trainer's 22-cell strip);
/api/papers/{n}/crowd returns the learner's sitting id and each slot's question id; a paper card's "You" is a midpoint score;
the Custom test's "For me" difficulty in its request model.
Also send each question's `topic` slug with the test payload (PUBLIC_FIELDS has only topic_name; the break screen maps names
back to short names by guesswork).
DONE: checks/s5.py passes and test_flow "all good". Tell the user "S5 server done".
```

## Task 27: the Words gate step (combine passes A and B, approve the agreed frames)

```
Passes A and B are done (v2/words-gate-a, v2/words-gate-b; 1,263 seed-0 items over the 827 frames in gate_plan.json).
SETUP: git worktree add .claude/worktrees/gate -b v2/words-gate-final v2/words-gate, then git merge --no-ff v2/words-gate-a and
v2/words-gate-b (their files differ: adjudications_a.json and adjudications_b.json).
1. Combine both into server/words/adjudications.json in W1's format (spec/v2-upgrades/words.md, W1 "The review gate").
2. A frame is servable only when EVERY judged item of it has two verdicts "one" from different "by" (model:helper-a and
   model:helper-b) that BOTH name the key's option. Set that frame's reviewed {by: "model:helper-a+model:helper-b", date}.
3. Any "more", "none", or two verdicts that disagree (or disagree with the key) blocks the frame: list those frames with both
   verdicts in server/words/review-queue.json, for a person to resolve. Never mark a blocked frame reviewed.
4. Run python3 tools/build_words.py (exit 0) and PYTHONPATH=. python3 server/checks/s9.py, and confirm with SATF_WORDS_UNREVIEWED
   unset that Words now serves in-context items for the approved frames (box 3+ reviews stop falling back).
5. Report: frames approved, frames blocked (and why, by kind), SAT senses with at least one approved frame, and the 26 senses no
   frame covers (from gate_plan.json "uncovered").
Commit on v2/words-gate-final. Tell the user "gate done" with those counts. The main agent merges it.
```

## Task 28 (light): two small backend leftovers from the Practice pages

```
SETUP: git worktree add .claude/worktrees/light -b v2/light master
OWN ONLY: server/prefs.py, server/api_notes.py, server/checks/f4.py.
1. prefs: add "hide_timer" (bool, default false) and "open_explanations" (bool, default false) to the one prefs registry
   (spec/rebuild-v2.md §2.7, R11), with validation like the other keys (bad value: 422 naming the key). The Practice session
   stores them in localStorage until these exist.
2. notes: the question runner (web/assets/runner.js) and api_notes.py use different highlight style names, so every save got a
   422 until the Practice page added a translation. Make POST /api/notes accept the runner's style names (map them to the stored
   ones; keep accepting today's names), so the page's stopgap can be removed later.
Add a case for each to server/checks/f4.py. DONE: f4.py and test_flow "all good". Tell the user "light done".
```

## Task 29 (light): an operator's README section, and ignore the generated cache

```
SETUP: git worktree add .claude/worktrees/ops-docs -b v2/ops-docs master
OWN ONLY: README.md (add one new section, "Running and operating SAT Freshman"; do not rewrite the rest) and .gitignore.
1. .gitignore: add server/cache/ (generated files such as twin_supply.json keep getting committed by accident); if any file under
   server/cache/ is tracked, git rm --cached it.
2. The README section, short and exact, from what is really in the repo (check each command runs):
   - how to run the site locally (the uvicorn command, the port, PYTHONPATH), and the test commands (server/test_flow.py, every
     server/checks/*.py, python3 -m satbank check, tools/build_words.py, tools/lint_bank.py);
   - every environment variable the server reads (grep for os.environ / getenv: SATF_DB, SATF_ADMIN_TOKEN, SATF_REPORTS,
     SATF_BACKUPS, SATF_WORDS_UNREVIEWED, SATF_GOOGLE_CLIENT_ID, mail/SMTP settings and any others) with what each does and its default;
   - backups (tools/backup_db.py: daily/weekly rotation, --verify, --restore), the load test (tools/load_test.py) and the reports
     admin (tools/reports.py);
   - what launch still needs from outside: an SMTP server for email sign-in and a Desmos production key.
DONE: every command in the section runs as written. Tell the user "docs done".
```

## Task 30: what the new pages need from the merged servers (Plan, Words, Compete)

```
The Today, Plan, Words and Compete pages are built and waiting for review. Their builders and checkers listed server gaps.
READ: spec/v2-state/followups/S3-pages.json, S7-pages.json, S9-pages.json, S8-pages.json (each "verified_defects" and
"fixer_report"). Do every item that belongs to a server file you own here, and list the rest.
SETUP: git worktree add .claude/worktrees/page-asks -b v2/page-asks master
OWN ONLY: server/plan.py, server/api_plan.py, server/checks/s7.py, server/words.py, server/api_words.py, server/checks/s9.py,
server/compete.py, server/api_compete.py, server/checks/s8.py.
Known asks: /api/plan/preview's per_date is empty (the exam-date picker needs each date's study days, weekly pace, tag and
Recommended); words.daily_item is missing (Today's day's questions show only the two Math slots); anything else in those files.
ALSO READ followups/S7-hygiene.json, S9-hygiene.json, S8-hygiene.json ("fixer_report", the part for other owners). From them:
- FIRST: server/checks/s8.py ~517-519 is date-dependent and stops test_flow: it asks compete.contest("final-" + next SAT date),
  but compete.ensure only makes a Season Final in the week before an SAT, so on a fresh DB in other weeks (e.g. 2026-09-28)
  it is a 404. Make the check create or pick its Final itself.
  The page shows the same gap: on 2026-09-28 Compete's season card reads "Road to Oct 3 · 6 days left" with a Season
  Final dated Sat Sep 26 - Sun Sep 27, already past. Say what the SAT week holds instead.
- Words: /api/words must fill each word's `lists` from word_lists (a new list vanishes on reload); quiz_item must leave out
  the target's family, synonyms and "Same as" words (the worksheet's Q3 has two right answers: student-facing, fix first);
  "nearly" sample items keep the word in the text or are labelled in-context; _summary needs a "today" bucket (words due
  today are counted under tomorrow); add "meaning" to the traps catalogue.
- Plan: api_plan.py logs the student's own task marks under the settings-edit kind ("Changed 2026-09-28:fix"): give them
  their own kind, say what changed ("Skipped Fix mistakes", "Moved Warm-up to Tue") and put `field` in changes.today.
- Compete: GET /api/contest/{cid} returns owner: true and code to the owner; the join payload adds who invited, how many
  are in, the round and topics; send `rated` (the count of rated answers); the debrief marks unreached slots itself.
  POST /api/contests accepts a sitting or paper to build a race from (the Tests share sheet's "Race friends").
  Levels: ratings.level_of is a 7-level scale but spec/rating.md and the par rows use 10; list it for the owner of
  ratings.py (not in your files) unless compete.py can map it.
Do NOT change response shapes the pages already use; add fields. DONE: s7.py, s8.py, s9.py and test_flow pass. Tell the user
"page asks done" with what you did and the list of items for other owners.
```


## Task 31 (light): make test_flow pass on any date

```
test_flow never prints "all good" today, so no task can meet its DONE line. Two checks depend on the calendar, and one
test lacks a header. Fix only these; nothing else.
SETUP: git worktree add .claude/worktrees/flow-green -b v2/flow-green master
OWN ONLY: server/checks/s3.py, server/checks/s8.py, server/test_flow.py.
1. server/checks/s3.py ~line 200 (qotd_answer_and_crowd): `got["sat_pace_ms"] == 95_000` fails on some days (the day's
   grid-in has one accepted form). Make the check build or pick its own question so the assert holds on every date.
2. server/checks/s8.py ~517-519: compete.contest("final-" + next SAT date) is a 404 outside the week before an SAT
   (compete.ensure makes a Season Final only then). Create or pick the check's own Final so it works on any date.
3. server/test_flow.py line ~212 ("practice results were gated behind signup"): the Results server on v2/s6-server now
   answers 403 without an X-Learner header. Send the learner's header in that call (do not loosen the server rule).
Test each on at least three dates: today, the week before an SAT (e.g. 2026-09-28 for Oct 3), and an ordinary week, by
setting the clock the checks already use (or freezegun-style patching inside the check). Commit per fix, never push or merge.
DONE: on v2/flow-green (and with v2/s6-server merged into a scratch copy for item 3) test_flow prints "all good".
Tell the user "flow green". These fixes come out of Tasks 24 and 30: skip them there.
Also commit your Task 29 edits (README.md, .gitignore) on v2/ops-docs if they are finished.
```


## Task 32 (very light): four one-line server fixes the new pages found

```
Each is a line or two in a file you already own. Do each on the branch of the task that owns the file, one commit each.
1. v2/s10-server, server/checks/s10.py: check(c) calls main(), which asserts SATF_DB ends in s10.db, so test_flow fails
   under any other database. Let check(c) skip that assert (keep it for a direct run).
2. v2/s1-server, PUT /api/me: accept avatar 'initial' (the avatar picker's Initial tile is refused today).
3. v2/s5-server, server/api_tests.py PUBLIC_FIELDS: add "topic" (the slug), so the test window can name skills without
   guessing from topic_name.
4. v2/s10-server, /api/review/due: add each item's `seed`, so the page opens the exact question, not the template's
   latest miss.
DONE: each branch's own checks/sN.py still passes. Tell the user "task 32 done".
```

---

## For the main session

When the helper reports a task done:
1. Add a TASKS entry to `spec/v2-state/next/build.js`: id S9S, S7S or S8S, the owned files above, `units: []`, and
   an `accept` built from the task's DONE line.
2. Run it `from: 'verify'`.
3. Merge after its one fix.

The wave-2 page tasks S9, S7 and S8 then build only the pages, on top of these branches, rebased on master.
