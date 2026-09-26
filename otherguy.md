# Helper work report

**Snapshot:** 2026-09-26, repository `/Users/workingmyassof/satbank` at `master` commit `31f8ae8`.

This is the work I completed or fixed while serving the delegated backend and bank tasks. I committed each finished unit on its own branch. I did not push or merge those branches. The main build merged the earlier branches listed below; the four server branches in the handoff table still need its independent verification and merge. The modified `spec/v2-state/STATE.md` in the main checkout belongs to another session and was left untouched.

## Already merged to master

| Work | Branch / commits | Result |
| --- | --- | --- |
| F5 drill engine and bank catalogue | `v2/f5`, `514f2be` through `6e3d219` | Unified pool and filter validation, preview counts and 409 reasons, adaptive selection with measured levels and pace, named-trap repairs that keep the misconception on offer, inline feedback, type catalogue and examples, outside mistake logging, and `server/checks/f5.py`. The R45 repair and fix-drill assertions were restored in `server/test_flow.py`. |
| SAT dates | `v2/satdates`, `141f815` | `server/satdates.py` records the published dates, registration and late deadlines, score releases, test-day arrival guidance and checklist, with College Board source URLs and check dates. March 2027 was settled as **March 6**, not March 13. Unpublished spring 2027 score releases and anticipated 2027–28 deadlines remain `None`. Standard Saturday doors **open 7:45 a.m. and close 8:00 a.m.** |
| Read-only bank lint | `v2/bank-lint`, `f168c9f` | Added `tools/lint_bank.py` and its saved table, `tools/lint_bank.out.txt`, without modifying bank questions. The initial scan reported 1,969 findings, including 55 generation errors, 15 plurals, 65 missing tables, 7 missing figures, 936 missing graphs, 390 rationale endings and 501 repeated reasons. The triage separated true defects from lint false positives. |
| Bank lint group 6 | `v2/bank-lint-fix`, `549df45` | Corrected reasons so they produce their option values, rejected only degenerate draws, and fixed named grammar. The full 0–49 seed comparison is in `spec/v2-state/followups/bank-lint-group6-diff.md`: 394 generated items unchanged; 102 changed seed outcomes, including 27 degenerate draws whose quantities legitimately changed. |
| Bank lint groups 1–5 | `v2/bank-lint-fix`, `b38dc12`, `d4f7cb4`, `ce3f2a9`, `d4639f6`, `033fa1a` | Fixed singular units, references to missing visuals, rationale conclusions, and seeds that exhausted the normal 60 draws; tightened the linter and saved the new output. `spec/v2-state/followups/bank-lint-groups1-5-proof.md` and `tools/bank_lint_seed_dump.jsonl.gz` compare 7,800 template/seed cases: zero changes to numeric answers, ordered option values or numbers for the 7,549 seeds that already generated; 251 formerly dead seeds now generate. Final lint output has 16 review findings: 11 `low_yield` and 5 `filler_majority`; every originally requested correctness check is at zero. |
| Habits helper (Task 4) | `v2/habits`, `84845cf` | Added `server/habits.py` with ordered misconception families and a bank coverage audit. |
| Bank supply (Task 5) | `v2/bank-supply`, `14cf283` | Added easy Advanced Math grid-in supply for the twin challenge's C26 requirement. |
| Named grid-in mistakes (Task 6) | `v2/spr-grow`, 13 commits `d1e53ea` through `62e7df5` | Added named mistakes to the 56 previously uncovered grid-in templates. The branch's coverage audit reached 204/204; the 19-topic bank check and serving flow passed. Comparison showed unrelated generated fields stayed byte-identical. A separate later bank-label review is owned by the main build, so use its current coverage when integrating other bank branches. |
| Security audit (Task 7) | `v2/sec-audit`, `21fa6b9` | Wrote the read-only `spec/v2-state/followups/security-audit.md` with nine reproducible findings: two high, six medium and one low. It used temporary SQLite and report storage, never the production database. |
| Word-frequency corpus (Task 8) | `v2/freq`, `baddd02` | Added `tools/count_freq.py`, the pinned source list and `tools/data/freq.txt`: 450 Gutenberg books plus 196 US federal texts, 57,028,573 counted tokens and 74,989 words retained at a minimum count of five. The file is under 5 MB. |

The main build's merge commits for these units include `197b54a`, `3ad7b8e`, `22b1532`, `dfe3544`, `ced6514`, `79c4f73`, `3513836`, `6c9b8e2`, `b6d3b5b`, and `1bd58bc`.

## Completed server branches awaiting the main build

Use the **new** branches here. `v2/s7-server`, `v2/s8-server` and `v2/s9-server` are superseded and should not be merged in their place.

| Area | Branch, worktree and commits | What is complete | Gate |
| --- | --- | --- | --- |
| S7 Plan | `v2/s7s` at `.claude/worktrees/s7s`; initial server commits rebased as `635ed4b`–`0707a46`, preserved fixer checkpoint `bdaa0c8`, then `14174d3` | Plan scheduling and status, API, token sharing and calendar feeds, Shell and Today hooks. Fixed weekday-dependent tests, live catalogue count, Shell shape, active/revocable share links and missing mirror/swap checks. | `server/checks/s7.py` passes; `server/test_flow.py` prints `all good`. |
| S8 Compete | `v2/s8s` at `.claude/worktrees/s8s`; server implementation `444acf3`–`f498844`, fixes `7ec57b9` and `3be6463` | Twin daily contest, private series, boards, records, Rush, Trap of the Week, Word Sprint paths, Final focus, supply survey and simulation. Fixed private-contest access, anonymity, Rush rating comparisons and create validation. `3be6463` fixes SEC-08: an indexed SQL top-100 legacy challenge board with the caller's true rank, bounded row fetching and date validation. | `server/checks/s8.py` passes, including a 1,000-finisher SEC-08 reproduction; `server/test_flow.py` prints `all good`. External-section checks still print `PENDING` until their owners land. |
| S9 Words | `v2/s9s` at `.claude/worktrees/s9s`; server implementation `2a3c9c9`–`7d686ac`, fixes `53cb7b6` and `c60500b` | Content index, per-sense state and spaced review, proof ladder, gated item generation, Words runs and API, list sharing, Today/Me helpers, and Word Sprint hooks. Fixed no-reviewed-frame fallback, protection of in-context proof on same-day sheet regrades, and library counts/fields (`probable`, `trapped`, `stubborn`, `atrisk`, family, roots, value, trap). | `server/checks/s9.py` passes; `server/test_flow.py` prints `all good`. Until reviewed frames are published, the fallback review cannot promote a word to Known. |
| Security fixes (Task 9) | `v2/sec-fix` at `.claude/worktrees/sec-fix`; `86e94b5`, `70922a2`, `3e089bd`, `5414988` | SEC-04 outside-log requests counted once each in an atomic transaction, even when opening a trap writes two events; SEC-05 streamed report byte cap before multipart parsing, including chunked uploads; SEC-06 eight-hex-character College Board IDs and bounded unknown-ID telemetry; SEC-07 `writer_of` on body and header codes in legacy practice and mock creation; SEC-09 sample learner block at the route and in `progress.record_trap`. The mock creation route is in `server/api_tests.py`, so that file has the narrow SEC-07 change. | `server/checks/security.py` passes its reproductions, including concurrent quota requests; `server/test_flow.py` prints `all good`. |

The S7, S8, S9 and security worktrees are clean. None of these four branch tips is an ancestor of `master` at this snapshot. Their tests used scratch or dedicated databases, not `server/satfreshman.db`; no server was run on port 8000.

## What the main build still owns

1. Independently verify and merge `v2/s7s`, `v2/s8s`, `v2/s9s` and `v2/sec-fix`. Follow the one-check/one-fix policy in `spec/v2-state/HELPER-TASKS.md`. Their old `*-server` branches are superseded.
2. Resolve security findings SEC-01, SEC-02 and SEC-03 in the wave-2 sections that own account, daily identity and test/session authorization. SEC-04–09 are addressed in the helper branches above, with SEC-08 on `v2/s8s`.
3. Recheck S8's external `PENDING` contracts after the S1, S4, S5 and S9 changes are integrated. The S8-owned assertions already pass.
4. Publish reviewed Words frames/pairs to unlock fully in-context reviews and Word Sprint promotion. The server's fallback intentionally cannot certify Known without that proof.
5. Keep the unrelated main-checkout change to `spec/v2-state/STATE.md` separate from these commits.

No further helper task is assigned after Task 9 in `spec/v2-state/HELPER-TASKS.md`. The one-shot S8 resume heartbeat fired after S8 was already complete; it targets the obsolete `v2/s8-server` branch and has no further scheduled run.
