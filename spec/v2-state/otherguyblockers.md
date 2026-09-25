# Blockers in the other agent's servers

Found by the independent checks on 2026-09-25. Fix every blocker below on the branch named, then run that server's
`server/checks/*.py` and `PYTHONPATH=. python3 server/test_flow.py` (both must pass) and tell the user "<server> fixes done".
Use the branches `v2/s7s`, `v2/s8s`, `v2/s9s` (not the old `-server` ones). `v2/s7s` has a fixer checkpoint (909e603): keep it.
Follow-ups (non-blockers) are in `spec/v2-state/next/<id>-verify1-issues.json`; fix them only if small.

## Compete server (S8) — branch `v2/s8s` — 4 blockers

### 1. server/api_compete.py list_contests, _meta/get_contest, contest_board, contest_grid, contest_traps, contest_pacer (and compete.board/series_board)

**Problem:** Non-members can see private contests. /api/contests?status=live|upcoming lists every learner's private contest, including all future series rounds, to everyone. For a non-member, GET /api/contest/{cid} and /api/contest/{cid}/board return 200 with the title, the entrants' names and their scores (probe: a stranger found the contest in the live list, got board 200 with 2 entrant names and lobby 200). After a private contest closes, a non-member can also open /grid. This breaks the invite-only privacy of friends' contests under decision 5.

**Fix:** Leave kind='private' rows out of the live, upcoming and finished lists unless the viewer is a member. Return 403 or 404 to non-members on /api/contest/{cid} (keep a minimal Join preview reachable only through ?code=), /board (including view=series), /grid, /traps, /review, /compare and /pacer of a private contest. Add an s8.py assertion that a stranger cannot list or read a private contest.

### 2. server/compete.py rush_next / rush_answer (cfg['last_rating'] vs q['item_rating'])

**Problem:** The directional filter compares an unrounded candidate rating (value > previous) with the rounded rating stored as last_rating. After a right answer the next Rush item can show the same rounded rating (794 then 794), so the difficulty does not strictly climb. s8.py failed on this ('five clean Rush answers climb through fresh item ratings') in 1 of my 5 runs, and 2 of 25 repeated runs failed. test_flow runs s8.py against the accumulating server/s8.db, so it will fail intermittently.

**Fix:** Store the unrounded rating (for example cfg['last_rating'] = item_rating before rounding, or q['item_rating_raw']) and compare against it. Alternatively require round(value) > previous. Keep the rounded value only for display.

### 3. server/compete.py _identity, follow, rivals

**Problem:** The anon board mode does not follow R12. _identity treats board='anon' like 'hidden' and shows 'Anonymous' on public boards and leaderboards. R12 says anon lists the default handle ('Student 4F2A') and only hidden reads 'Anonymous' (probe: anon row name 'Anonymous', expected 'Student 4739'). follow() also refuses anon targets and rivals() drops them, but compete.md's R12 row says name and anon rows are raceable and followable. The acceptance names 'boards with R12's names'.

**Fix:** In _identity, when board='anon' and the row is not the viewer's, return challenge.handle(learner, None) ('Student XXXX') with anon:true. Keep 'Anonymous' for hidden, and for anon or hidden on private-contest entrant lists (C18). Allow follow() and rivals() for anon, and refuse only hidden.

### 4. server/compete.py create_private

**Problem:** Acceptance #18 (as amended by compete.md) fails as written. POST /api/contests {count:10, topics:[...], open_for:24, twin:true} returns 422 'title must be 3–60 characters'. Spec §7 gives the title a default of "{name}'s challenge" and a length of 3–40 characters. The server requires a title and allows 60.

**Fix:** When no title is sent, default it to f"{board name or handle}'s challenge" using the owner's handle via challenge.handle. Validate 3–40 characters. Add the spec's exact body to s8.py.

## Plan server (S7) — branch `v2/s7s` — 5 blockers

### 1. server/checks/s7.py:152 (check_tasks_days) and :437

**Problem:** The check depends on the weekday. It takes today's first focus/map task, but on a 1111100 plan today is the weekly test day on Fridays and a rest day on Sat/Sun. It raises StopIteration today (Fri 2026-09-25), so both s7.py and test_flow fail. Shifting plan.today confirms it fails Fri/Sat/Sun and passes Mon-Thu.

**Fix:** Pick the first future practice day with a focus/map task (as study_after does) instead of payload['today']. Or create that section's plan with test_day and start chosen so the day is a practice day.

### 2. server/checks/s7.py:57

**Problem:** The check hardcodes `bank.templates == 386`. Master now has 388 templates after the bank-supply merge, so test_flow fails on master plus S7 before any plan check runs.

**Fix:** Compare against the live catalogue: sum(map(len, practice.catalogue()['by_topic'].values())), or assert only that it is >= 386.

### 3. server/plan.py:2088 shell_part

**Problem:** The shell_part contract (§2.10: /api/shell merges part keys at the root and plan provides the `plan` key) is broken. shell_part returns flat keys {id, day, done, total, minutes_left, next}, so for every learner with a plan /api/shell gains root id/day/done/total/minutes_left and its `next` queue list becomes a string. Probe: next went from [] to "Module test". web/assets/ui.js:1058 then calls `(shellData.next || []).filter(...)` on a string and throws a TypeError.

**Fix:** Return {'plan': {...}} so it merges one level down into shell.plan (keeping the shell's existing plan fields). Add a check that /api/shell.next stays a list with a plan active.

### 4. server/api_plan.py:521-555 (links, token_ics, shared); server/plan.py:41-55 init (plans.cal_token/view_token)

**Problem:** The R18/§2.13 sharing contract is not met. The progress-link token from links(kind='progress') that S1's /share/?t= and /plan/?view= use gets 404 from GET /api/plan/shared/<token>. The calendar feed ignores links(kind='cal') rows (a token inserted there gives 404 at /api/cal/<t>.ics). Tokens live in new plans.cal_token/view_token columns that F4's schema deliberately leaves out. S1, now in wave 2, needs the shared plan view keyed by the progress link.

**Fix:** Look up /api/plan/shared/{token} in links WHERE kind='progress' AND revoked IS NULL, serving that learner's active plan. Mint and revoke cal tokens as links(kind='cal') rows and serve /api/cal/{token}.ics from them. Keep the plans.* columns only as a fallback, or drop them.

### 5. server/checks/s7.py

**Problem:** The check does not cover items the task's accept list names: PATCH {swap}, plan.mirror from learner to plan (PUT /api/me with target/minutes/exam_date reaching the plan cfg), and GET /api/plan/ics (only /api/plan/{pid}/ics is tested). My probes show all three work, but the accept says s7.py covers them.

**Fix:** Add asserts: a swap PATCH changes the day's topics; PUT /api/me {target, minutes} shows in GET /api/plan active.cfg; GET /api/plan/ics equals /api/plan/{pid}/ics and the token feed.

## Words server (S9) — branch `v2/s9s` — 3 blockers

### 1. server/api_words.py _card_kind (lines 133-139) and _make_item (lines 88-104)

**Problem:** Due words at box 3 or higher (and placed=2 words) are always served as in-context items. frames.json has 0 of 5376 frames reviewed and pairs.json 0 of 153, so _make_item raises 409 and the whole run fails. Probe: bolster self-graded to box 3 and due; POST /api/words/run {mode:'mix',deck:{source:'today'}} returned 409 'no reviewed frame is available for this word', and {mode:'cards',deck:{source:'due'}} also returned 409. That mix body is exactly what today_summary.start sends, and S3 Today, S7 Plan and F2 Up next launch it. s9.py hides this because it runs with SATF_WORDS_UNREVIEWED=1.

**Fix:** When no servable frame exists, serve a self-graded card that reschedules at the current box ('Prove it') or a meaning2word check instead of failing, and skip an item rather than abort the run. Add an s9 check with SATF_WORDS_UNREVIEWED unset: a mix run and a due-cards run holding a due box-3 word both return 200.

### 2. server/api_words.py grade_sheet (lines 1358-1362)

**Problem:** The same-day 'replace the first grade' path undoes any latest review whose mode is 'sheet', but answer_sample also files mode 'sheet' (kind incontext). Probe: box-3 mitigate, sheet sample answered right gave box 3→4 with proven set; then POST /api/words/mitigate/grade {ok:true} deleted the in-context row and left box 3 with proven=None. That is data loss of a proof, and the covered sheet shows the sample and Know/Don't know together.

**Fix:** Replace only a previous covered-sheet grade: require last.kind == 'card' as well as mode 'sheet' and same day (or give sheet grades their own mode). Add an s9 check that a sample proof followed by a sheet grade keeps the incontext row and proven.

### 3. server/words.py library() (lines 482-524); server/checks/s9.py test_library (line 129)

**Problem:** Spec check 5 (as amended by words.md override 53) requires counts trapped, stubborn and atrisk; override 50 adds probable. GET /api/words lacks trapped, atrisk and probable, and its rows lack at_risk, trap, family, roots and value. s9.py asserts only a subset, so a Words server acceptance item is neither covered nor passing. The S9 pages' My words tiles (Fell for a trap, At risk, Probably known) need these fields.

**Fix:** Add counts.trapped (last in-context miss named a trap), counts.atrisk (retention < .8 to exam_date), counts.probable (placed == 2), and the row fields at_risk, trap, family (class), roots and value. Extend the test_library key assertion to the full amended list.
