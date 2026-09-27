# Resume here

**Dev server:** started from the moved repo, `cd /Users/workingmyassof/freshbot/satbank && PYTHONPATH=. python3 -m uvicorn server.app:app
--port 8000 --log-level warning --reload --reload-dir server` (background task bkhbftu1e since 2026-09-27; the old one ran from the
deleted path and served 500s).

**One page at a time (the user, 2026-09-27):** build.js runs WORKERS = 1. After S4Q finishes, the user allowed ONE more
workflow: pages in the order S3 Today, S5 Tests, S6 Results, S10 Review, S7 Plan, S9 Words, S8 Compete, S1 Me, F2B, one
fully finished (built, checked, fixed, merged after a branch check, opened for the user) before the next starts.

**Standing rule (the user, 2026-09-27): my builds are PAGES ONLY. Any backend part becomes a HELPER-TASKS.md task and I ask
the user to give it to the other agent.**

## Now: PAUSED for usage limits (2026-09-24, evening). Nothing is running; all work is committed.

Policy: features get one independent check + one fix; content two rounds; small or data-only tasks (and the other
agent's non-feature jobs) get my inline check. Fixers fix only the listed defects. See memory check-policy.

Merged into master so far: planning and upgrades, v2/f0, v2/t-bank-all, v2/bank, v2/f4 (+ swap middleware), v2/f1,
v2/satdates, v2/bank-lint, v2/f5, v2/words-content, v2/bank-lint-fix group 6 (dfe3544).

### Status after the resume (2026-09-24 evening)
- MERGED: `v2/bank-lint-fix` groups 1-5 (ced6514; inline check: 21,800 items keep their numbers, 111 dead seeds
  revived, gate 19/19; the lint now reports 16 findings: 11 low-yield templates, 5 filler-majority notes) and `v2/f6`
  (33b1627; the test_flow label-threshold failure was a test-isolation bug, fixed by the other agent). F6's fixer left
  a drill.py change for S4 (use sets.serve for pool 'set'): in `followups/F6.json`.
- **ALL FOUNDATIONS MERGED** (2026-09-25): F2 (e9cf9f6) and F3 (1344fd9) passed their checks with no blockers;
  follow-ups in `followups/F2.json`, `followups/F3.json`. checks/f5.py's local-date bug fixed (45a2a33); moving
  check-ins to learners' local days is a follow-up in `followups/F5.json`.
- **Merged 2026-09-25 (helper, inline-checked):** spr-grow (6c9b8e2: grid-in named mistakes 204/204), freq (1bd58bc),
  sec-audit report. **When wave 2 resumes, its builders must fix these audit findings in their files:** SEC-01 (S1,
  api_account signup), SEC-02 (S3 qotd and S8 challenge: disposable codes farm the daily key), SEC-03 (S5/S6: session
  ID alone authorizes test writes and results). Add them to each task's unit prompts. SEC-04-07, 09 are the helper's
  Task 9; SEC-08 goes with his S8 fixes.
- **REPO MOVED 2026-09-26** to /Users/workingmyassof/freshbot/satbank (worktrees repaired). Scripts with the old absolute
  path (spec/v2-state/next/*.js REPO, HELPER-TASKS, memory) need updating if the move is permanent.
- **2026-09-26:** the helper finished Task 0 (v2/s7s, v2/s8s, v2/s9s) and Task 9 (v2/sec-fix). Each passes alone; merged
  together s7.py and s8.py assert and test_flow fails a timing check, so NOTHING was merged. The helper integrates them
  on v2/helper-integ (Task 10); then I merge that branch. The user asked for no further double-checking.
- **2026-09-27:** helper Tasks 10-11 done on `v2/helper-integ` (checks pass 3 runs); the user said don't merge it yet. Task 12
  waits for that merge. Helper now on Tasks 13 (local-day check-ins, v2/localday) and 14 (backups + load test, v2/ops), both
  from v2/helper-integ. Merge order later: v2/helper-integ, then v2/localday and v2/ops.
- **2026-09-27 (the 04:02 job, per the user):** the check-only pause is OVER. Merged: v2/helper-integ (4549610), v2/localday
  (304aa62), v2/ops (6b010a2), v2/bank-gaps (ddd545d, gate 19/19), v2/cb-data (eec25b0); test_flow all good after each.
  RUNNING:
  * Task 12 PAUSED 2026-09-27 to save tokens for the frontend: the tool and gate plan are done (v2/words-gate 8306599: 827 frames
    cover 1,218 of 1,244 senses; 26 senses are a key in no frame); the verdict passes were stopped early (v2/words-gate-a/-b).
    Resume later with a lighter first pass (1 seed per frame x key instead of 5): `{from:'verdicts'}` after editing the pass prompt.
    Found on the way: server/checks/s9.py fails with "OverflowError: Python int too large to convert to SQLite INTEGER" in
    test_daily_print_offline (words.grade), on master too: a real Words server bug for S9 or the helper.
  * The frontend (3 workers at a time since 2026-09-27, the user's request): build.js run `wf_9d9dbc9e-5dc` (task wc7l1f3i5), args `[{id:'S4'},{id:'S5'},{id:'S3'},{id:'S6'},{id:'S10'},
    {id:'S1'},{id:'F2B'},{id:'S7'},{id:'S8'},{id:'S9'}]` (sections 3 units; S7/S8/S9 pages-only 2 units; builders rebase old
    branches onto master first).
  * Checkpoint loop: task bgbqcunjk.
  * BRIEFS (2026-09-27, the user: "one section shouldnt be taking 4m tokens"): each remaining task reads only
    spec/v2-state/briefs/<id>.md (80-110k tokens) instead of the whole plan. The frontend was relaunched on them: run
    `wf_3f139f0b-f7c` (task w64p2zb82), same args, 3 workers, effort HIGH for every agent (the user's call). Briefs come from
    spec/v2-state/next/make_briefs.py (about 70k tokens each: the real requirements; 14-19k check briefs). Every agent follows
    the EFFICIENCY rules in build.js (cut output, read by line range, write files once, test per group).
  * STOPPED 2026-09-27 12:15 at the user's 90% usage limit ("stop new builds, also before getting to build confirm with me").
    DO NOT LAUNCH ANY BUILD WITHOUT ASKING THE USER FIRST.
    - CORRECTION: the run's builders, checkers and fixers ANSWERED THE USER'S MID-RUN QUESTIONS ("how much is S3 done?") instead
      of building: user messages sent while agents run are relayed to them. S3 Today and S5 Tests pages were NOT built (no web/
      commits); their "check" and "fix" did nothing. build.js now has an IGNORE CHAT rule. S3 and S5 pages need building again.
    - S4 Practice: MERGED 2026-09-27 (b2e4aaf): builder + session pages and the Practice server work so far (the helper's
      Task 25 continues the server on v2/s4-server: rebase it on master first). Leftovers in followups/S4-pages.json.
    - S4Q MERGED after the user approved the preview ("good job with practice"); leftovers in followups/S4Q.json.
    - 2026-09-28: the user reviewed the Today preview live (13 basic visual findings, all fixed on v2/s3 and v2/calm-shared).
      RUNNING: today-hygiene run `wf_da1586d8-318` (task w0342biml): 4 lens auditors, one fixer (commits on v2/s3 and
      v2/calm-shared), one re-check (the user: stop the workflow once the fix is done; watcher task b6bs40lyi). Every future
      page gets ONE hygiene agent (visual + calm, measured, looks at screenshots) whose findings join the one fix (build.js).
      Plan, Words, Compete (built): run build.js `[{id:'S7',from:'hygiene'},{id:'S9',from:'hygiene'},{id:'S8',from:'hygiene'}]`
      when the user says go, then preview.
    - 2026-09-28: run wf_52a6cb52-1a2 DONE. S3 Today, S7 Plan, S9 Words and S8 Compete pages are built, checked and fixed on
      their branches (verified web diffs: ~2,300 / 3,400 / 3,800 / 3,500 lines); leftovers in followups/<id>-pages.json.
      PREVIEW of all four together on port 8061 (task b8vcjsxuq, worktree scratchpad/prev4, test_flow all good). MERGE EACH
      ONLY AFTER THE USER LOOKS AND SAYS GOOD; then stop the preview and remove prev4.
    - The user (2026-09-27, going out): "only pick up sections in which server was done by another guy". So only S7, S9, S8 (their
      servers are merged), plus S3, which was already running (the user: "i never told you to stop the current one"). RUNNING one
      at a time: `[{id:'S3'},{id:'S7'},{id:'S9'},{id:'S8'}]` (S3 continues from its checkpoint on v2/s3). S5, S6,
      S10, S1 and F2B wait for Tasks 26, 20, 21, 22, 23. Do NOT merge any page before the user previews it.
    - (history) queue S3, S5, S6, S10, S7, S9, S8, S1, F2B
      (WORKERS = 1). For each finished page: verify its web/ diff on the branch, preview it for the user, merge on their OK.
    - (history) DECISION 7 (calm, quiet UI) added 2026-09-27; briefs regenerated. S4Q (the Practice pages made calm, no feature
      lost): run `wf_9e14b5f3-2c4` (task wgluczzch), `[{id:'S4Q'}]`, 2 units + one check + one fix, branch v2/s4q. Verify its
      web/ diff on the branch before merging.
    - Words gate MERGED (93fc62c): 797 frames approved over 1,159 senses; 30 blocked in review-queue.json; 26 senses no frame.
    - Also merged: v2/perf (helper Task 17: zero errors at 10/50/200 learners), v2/words-seed-sqlite (Task 18's crash fix;
      master already had it). Words gate pass A done on v2/words-gate-a (1,263 items: 1,235 one, 28 more); waiting for pass B.
    - S4 Practice pages: built, checked (3 blockers, next/S4-pages-verify1-issues.json); the fix is the ONLY thing running:
      run `wf_b6e107a2-030` (task wzcyt7kom), `[{id:'S4', from:'fix', issues:...}]`, from checkpoint on v2/s4. Then ready to merge.
    - S6 Results: page part 1 in progress, checkpointed on v2/s6. S10 Review: page part 1 had written nothing yet.
    - Not started: S1, F2B, S7, S8, S9 (all pages-only, 2 units).
    - To continue, after the user confirms: build.js with `[{id:'S3'},{id:'S5'},{id:'S6'},{id:'S10'},{id:'S1'},{id:'F2B'},{id:'S7'},{id:'S8'},{id:'S9'}]`
      (and S4 only if its fixer did not finish the pages).
    - Merging S3/S5/S4 pages: their server halves are helper Tasks 24-26 on v2/<id>-server (branched from these branches), so
      merge each pages branch, then its server branch when the helper finishes; test_flow after each.
    Check results and fix reports: followups/S3-pages.json, S4-pages.json, S5-pages.json.
  * (history) run `wf_d97948f9-1df` (task wi11d1s10). ALL TEN tasks are pages-only (2 units each). Server halves are
    the helper's: Tasks 20-23 (S6, S10, S1, F2B) and 24-26 (S3, S4, S5, continuing the main build's commits), on
    v2/<id>-server. Merge each server branch together with its pages branch. The previous run crashed because my shell sat in
    a non-git folder when agents needed worktrees: never cd outside the repo while a workflow runs.
  * Helper queue: Task 17 perf (the load test fails at 10 learners), 18 words grading fix + gate pass A (1 seed),
    19 gate pass B in a separate instance. After 18+19: merge v2/words-gate-a/-b into v2/words-gate, run the gate step
    (words-gate.js {from:'gate'}), merge.
  The Workflow tool can't open scripts under the moved repo: launch copies from
  ~/.claude/projects/-Users-workingmyassof-freshbot-satbank/9030c288-6222-49fa-a25a-6e6802e22cd3/workflows/scripts/ (copy
  spec/v2-state/next/*.js there first). As each task returns ready: leftovers to followups/<id>.json, test_flow, merge.
  Then I1, the integration walk, which now includes the "nothing dropped" audit (the user, 2026-09-27): once every section
  is merged, run spec/v2-state/next/i1-audit.js (copy in the workflow scripts folder): per section an auditor lists every
  spec and upgrade requirement as built / missing / weaker / contradicts against the full texts, and an independent refuter
  keeps only the gaps it can't disprove. Save the confirmed gaps to followups/audit-<id>.json, turn them into build.js
  tasks (one per section with gaps; one check + one fix), and build them before launch. Then the full walk.
- **Server checks done 2026-09-25 (run wf_efc641bf-0d1, stopped during the fixes):** blockers S7S 6, S8S 5, S9S 4 (each
  includes my branch-naming bug: build.js used v2/<id> = v2/s7s etc.). The fixers created v2/s7s, v2/s8s and v2/s9s from
  the helper's branches (S7 and S8 rebased on master), so those are now the canonical branches; v2/s7s has a fixer
  checkpoint 909e603. Defects are saved in next/<id>-verify1-issues.json. Check-only mode, so the helper fixes them
  (HELPER-TASKS Task 0); then I re-check lean (run the checks, confirm each blocker) and merge.
- **Helper tasks 1-5 DONE 2026-09-25**: habits (79c4f73) and bank supply (3513836) merged after my inline check; the S9, S7
  and S8 servers are in one check + one fix: build.js run `wf_efc641bf-0d1` (task wp60i0yv8, relaunched 19:30),
  `[{id:'S9S',from:'verify'},{id:'S7S',from:'verify'},{id:'S8S',from:'verify'}]`; merge each when ready, then add
  pages-only tasks S7, S8, S9. The helper's next jobs are HELPER-TASKS.md Tasks 6-8 (spr coverage, security audit,
  frequency corpus): inline-check 6 and 8 and merge; 7 is findings only.
- **S8 server (helper) 2026-09-25:** 12 commits, s8.py and test_flow pass, blocked on others' contracts. Told to mark
  them PENDING (like F4) and report done; its habits.py dependency (an unbuilt F5 item) and the C26 bank supply are
  HELPER-TASKS 4 and 5; S4/S5/S1 hooks come from wave 2.
- **The other agent has HELPER-TASKS.md** (the user gave it to him 2026-09-25) and works through it: s9-server 6 commits,
  s7-server 3, s8-server 5 as of 02:00. Wait for "<task> done" before checking; then add S9S/S7S/S8S TASKS entries,
  run `from:'verify'`, merge; then add pages-only tasks S7, S8, S9 (web/plan/** + plan-ui.js; web/compete/**,
  web/challenge/** + compete-ui.js; web/words/**, web/vocabulary/** + words-ui.js).
- **S9 server** (`v2/s9-server`, worktree `.claude/worktrees/s9-server`, the other agent's): parts 1-2 done (content
  index + proof-based review core; gated item generation), part 3 (api_words.py) checkpointed at 91021b1, part 4
  (checks/s9.py) not started; ~2,400 lines. **The other agent finishes it** (the user, 2026-09-24): do not build it here. When the user
  says "S9 server done": add an S9S TASKS entry (owns words.py, api_words.py, checks/s9.py, build_words.py index)
  and run it `from:'verify'` (a feature: one check + one fix), then merge.
- NEXT after F2 and F3 merge: wave 2 (S1, S3-S10), TASKS entries from Part 4.2; S9's pages build on v2/s9-server.
- **The other agent's queue** is in `spec/v2-state/HELPER-TASKS.md` (paste-ready): 1. finish the S9 Words server,
  2. the S7 Plan server, 3. the S8 Compete server. Server halves he takes are NOT built here; my wave-2 tasks for
  those sections build only the pages. When he reports one done: TASKS entry, `from:'verify'`, merge.

### On "continue"

1. `python3 tools/v2_checkpoint.py --quiet`, then restart the loop (Bash, run_in_background):
   `while true; do python3 tools/v2_checkpoint.py --quiet 2>>/tmp/v2-checkpoint.log; sleep 300; done`
2. Remove stale workflow worktrees first (`git worktree list`; the `wf_*` ones are clean; `git worktree remove --force`
   each, after checking `git -C <path> status --short` is empty). They hold branches (`v2/f1`) that new agents must switch to.
3. Relaunch these three, each as its own Workflow call (never from a run ID):
   - **F1** (design system): units 1-3 done on `v2/f1` (ui.css foundations, ui.css components, kit.js). Charts not started.
     `Workflow({scriptPath: ".../spec/v2-state/next/build.js", args: [{id: "F1", unit: 3}]})` (unit is 0-based: 3 = charts,
     then 404 + kit page, then verify and fix rounds).
   - **F4** (data layer, built by the user's other agent): verify r1 failed (19 defects) -> fix r1 done -> verify r2
     failed (17 defects, saved in `next/F4-verify2-issues.json`) -> fix r2 cut off, its edits committed as e837e82.
     `args: [{id: "F4", from: "fix", round: 2, issues: "/Users/workingmyassof/satbank/spec/v2-state/next/F4-verify2-issues.json"}]`
     That leaves one more fix round after verify r3. When it passes: rebase `v2/f4` on master, test_flow, merge.
   - **Words content** (`next/words.js`, branch `v2/words-content`, worktree `.claude/worktrees/words`): the core agent
     finished (sat.json normalized, classes consolidated, 400 core, `server/words/_plan.json`). Authors when stopped:
     adv1 110 of ~200 committed, adv3 110 of ~200, roots 118 (check foils.json and collections.json, which it also owns),
     adv2, second and transitions had committed nothing. `Workflow({scriptPath: ".../spec/v2-state/next/words.js",
     args: {skipCore: true}})`: each author continues from its own committed file.
     Still to do after it: confusions (~700), fills + frames (~1,500; literature cut from real Gutenberg texts, never
     from memory), fold `parts/` into the final files, delete `_plan.json`, an independent accuracy check, merge.
4. Bank flaws seen 2026-09-24 (fix in satbank/topics, gate must stay PASS, MCQ output unchanged):
   `rr.repeated_factor` reason reads "counted 1 years"; `pct.table_share` grid-in stem mentions a table it does not show;
   `lat.triangle_sum` names "subtracted from 100 instead of from 90" and "assumed both acute angles are 45", both doubtful.
5. Then wave 1b: F2, F3, F5 (after F4), F6 (after F1 and F4); then S1, S3-S10 (S2 dropped); then I1.

The build runs from `next/build.js` (args `[{id, from?, unit?, round?, issues?}]`): unit builders on `v2/<task>` ->
independent verifier -> up to 3 fix rounds. I merge each passing task into master (Part 4.4).

## Resumed 2026-09-23: second check dropped

The user: "remember that we are dropping check2". The way-better pass now applies each section's saved verdict once, with no
further skeptic rounds (`next/continue.js`). today had its fix already. After it returns: the class-cleanup check, merge `v2/f0`
then `v2/t-bank-all` into master, then the build (step 4 c-d below).

## Grid-in review completed 2026-09-23

The user narrowed this continuation to checking whether named grid-in mistakes
describe wrong answers a student could actually produce. That review is complete.
All ten topic fix branches were independently checked and merged into
`v2/t-bank-all` at `f4bf864`. Doubtful templates now use the existing skill-level
fallback instead of naming an unsupported mistake. The integrated bank has named
mistakes on 146 of 202 grid-in templates.

The full bank gate passes all 19 topics; `server/test_flow.py` says "all good".
Across seeds 0-30, 14,988 generated MCQ items match `master` byte for byte;
73 attempts fail identically in both trees (including unsupported forced formats).
The old grid-in task list and merge instructions below are historical and must
not be run again. The way-better pass, repo prep merge and site build have not
resumed. The repository has no Git remote, so these commits could not be pushed.

Paused on purpose by the user on 2026-09-23 ("save everything... make sure when i say continue, you can pick it up
smoothly"). Nothing was running at the pause: every workflow and background waiter was stopped, every finished agent result
is saved, and every partial edit is committed or on disk.

## When the user says "continue"

1. `cd /Users/workingmyassof/satbank && python3 tools/v2_checkpoint.py --quiet` (refresh `STATE.md`).
2. Restart the background checkpoint loop (Bash, `run_in_background`):
   `while true; do python3 tools/v2_checkpoint.py --quiet 2>>/tmp/v2-checkpoint.log; sleep 300; done`
3. Launch the continuation: `Workflow({scriptPath: "/Users/workingmyassof/satbank/spec/v2-state/next/continue.js"})`.
   It re-runs nothing finished. It reads the saved verdicts in `spec/v2-state/next/` and does only this:
   - **Way-better pass** (loop: fix → skeptic, up to round 3, then one final skeptic; fixers also strip class material):
     | section | next step | from |
     |---|---|---|
     | shell-me | fix, round 2 (an earlier round-2 fixer was cut off part way; continue from the file as it is) | `shell-me-skeptic2-issues.json` (18) |
     | today | skeptic, round 2 (its round-1 fix finished) | -- |
     | tests, plan | fix, round 1 (a fixer was cut off part way; continue) | `<id>-skeptic1-issues.json` (15, 16) |
     | practice, reports, compete, words, review, product | fix, round 1 | `<id>-skeptic1-issues.json` (17, 10, 15, 12, 18, 13) |
   - **Grid-in mistakes** (capped, agreed with the user: no more fix rounds; what still fails loses its named mistakes):
     | topic | next step |
     |---|---|
     | linear_inequalities | done, passed (`v2/t-bank-fix-linear_inequalities`) |
     | equivalent_expressions, linear_equations_in_two_variables, nonlinear_equations_and_systems, two_variable_data | one final recheck; if it fails, drop the failing templates |
     | area_and_volume, linear_equations_in_one_variable, linear_functions, systems_of_linear_equations | drop the templates named in `<topic>-recheck2-issues.json` |
     | right_triangles_and_trigonometry | finish the interrupted fix (checkpoint commit d7a76c3 on its branch), recheck, drop what still fails |
     The 9 topics not listed passed their first verification and need nothing (their branches are merged in `v2/t-bank-all`).
4. When it returns:
   a. **Grid-in merge** (in the `.claude/worktrees/t-bank-all` worktree): merge each `v2/t-bank-fix-<topic>` into
      `v2/t-bank-all`; run `PYTHONPATH=. python3 -m satbank check` (all 19 PASS), `PYTHONPATH=. python3 server/test_flow.py`
      ("all good"), `PYTHONPATH=. python3 tools/spr_coverage.py`, and the MCQ-identity dump against master
      (`python3 <scratchpad>/mcqdump.py` in both trees, then `cmp`; recreate the script from the grid-in commit messages if the
      scratchpad is gone: it dumps generate(template, seed) for seeds 0-30, default and fmt="mcq", MCQ items only).
   b. **Class cleanup check**: `grep -ciE "teacher|homework|assignment|/class/|class code" spec/v2-upgrades/*.md` should be ~0;
      strip leftovers (decision 5).
   c. **Merge into master**, in order: `v2/f0` (repo prep, verified: identical routes and responses), then `v2/t-bank-all`.
      Re-run test_flow after each. Commit the upgrade files and state.
   d. **Build**, per `spec/rebuild-v2.md` Part 4, minus S2 (classes, dropped) -- foundations F1 + F4, then F2, F3, F5, F6, then
      the nine sections S1, S3-S10 in parallel, then I1 integration. Each task: builder in its own worktree and branch → an
      independent verifier → up to 3 fix rounds → merge. Builders read `spec/rebuild-v2.md`, `spec/v2-upgrades/<section>.md`
      and `spec/v2-decisions.md` (decisions win). Apply the checkpoint rules (memory: interruption-proof-workflows): small
      committed units, continue from predecessors' partial work, continuation scripts from saved results -- never resume a
      pipelined run from its run ID.

## Where everything is

- Plan: `spec/rebuild-v2.md` (11,183 lines). Upgrades: `spec/v2-upgrades/*.md` (+ `_proposals/`). Decisions: `spec/v2-decisions.md` (1-5).
- State: `spec/v2-state/STATE.md` (branches, worktrees, runs), `runs/<run>/` (every finished agent result), `next/` (verdicts
  and `items.json`: each item's rounds), `wip/` (uncommitted worktree snapshots, git-ignored).
- Branches: `v2/f0` (repo prep, built + verified, not merged); `v2/t-bank-all` (grid-in base + 19 topics + global rule a6bc1b6);
  `v2/t-bank-fix-<topic>` (per-topic fixes); `v2/t-bank-<topic>` (the original topic work, already merged into `v2/t-bank-all`).
- Checkpoint tool: `tools/v2_checkpoint.py`. The dev server (uvicorn on :8000 with --reload) may no longer be running; start it
  with `PYTHONPATH=. python3 -m uvicorn server.app:app --port 8000 --reload --reload-dir server` if a step needs it.

## Progress at the pause

About 23% of v2: review and spec done; way-better pass about 60% (all proposals and judges done, skeptic/fix rounds under way);
repo prep done; grid-in mistakes about 85%. Foundations, the nine sections and integration have not started.
