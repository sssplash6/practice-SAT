# Resume here

## Now: RUNNING (updated 2026-09-24 10:30)

**Check policy changed (the user agreed):** one independent check, one fix, merge. Leftovers go to
`spec/v2-state/followups/<task>.json` for the section that uses them or I1. Only content tasks (`rounds: 2`) get two rounds.
build.js implements it (blocker vs followup severity; pass = no blockers).

- Merged into master: `v2/bank` (bank flaws), `v2/f4` (data layer; its leftovers in `followups/F4.json`), and the F4 swap
  middleware in app.py (7eafbe9). Dev DB backed up as `server/satfreshman.db.bak-20260924-1020` before the F4 merge.
- **F1**: check r1 found 17 defects; fix r1 running in run `wf_d6bde851-f95` (task wlzjrhc30). Under the new policy F1 merges
  after this fix: a background waiter (b5l21n742) reports when it ends; then stop that run before it starts check r2, run
  test_flow and the page-load check, save the leftovers to `followups/F1.json`, and merge `v2/f1`.
- **Then wave 1b**: F2 and F3 and F6 through build.js (add their TASKS entries from Part 4.2 and §2.12). F5 is the user's
  other agent's (branch `v2/f5`, now to be rebased on master).
- **Words**: words2.js run `wf_609b5aa4-27c` (task wf5hy4nl6): frames 2-4 done, frames1 finishing, then fold and check.
- Checkpoint loop running (task b2bucxp7g).
- **F5 drill engine: the user's other agent** (worktree `.claude/worktrees/f5`, branch `v2/f5`). Do not build it. When the user
  says "F5 done": add F5 to TASKS, run `from:'verify'`, merge. Their next backend-only job: F6's server half.
If cut off: F1 `[{id:'F1', from:'fix', issues:<saved r1 defects>}]` then merge; words2 `{from:'author', only:['frames1']}`.

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
