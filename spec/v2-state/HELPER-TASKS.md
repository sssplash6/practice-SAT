# The other agent's next tasks (backend only)

Order now: finish S8 (with PENDING markers), Task 1 (S9 incl. S8's two Words contracts), Task 4, Task 5.

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

---

## For the main session

When the helper reports a task done:
1. Add a TASKS entry to `spec/v2-state/next/build.js`: id S9S, S7S or S8S, the owned files above, `units: []`, and
   an `accept` built from the task's DONE line.
2. Run it `from: 'verify'`.
3. Merge after its one fix.

The wave-2 page tasks S9, S7 and S8 then build only the pages, on top of these branches, rebased on master.
