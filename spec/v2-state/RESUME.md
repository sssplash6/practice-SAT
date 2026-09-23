# Resume here

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
