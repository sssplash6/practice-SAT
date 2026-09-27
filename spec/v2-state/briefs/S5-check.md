# Check brief for S5: Tests and the test window pages

## Decisions

# v2: the user's decisions

Answers to the open questions in `spec/rebuild-v2.md` Part 5. Where this file and the plan
disagree, this file wins. Builders read it alongside the plan and `spec/v2-upgrades/`.

## 2026-09-23

1. **Daily Challenge: twins.** Every student gets the same ten question types in the same
   order, each with their own numbers, so answers cannot be passed around. (Open question 3,
   the default.)
2. **Words: SAT Reading & Writing (EBRW) vocabulary only, for now.** Ship the SAT word list
   and transitions -- no "Math language" deck. (Open question 2.) The reason is the roadmap
   below: Words is the first piece of EBRW on the site.
3. **Roadmap: the full SAT, later.** The site stays Math-first while the Reading & Writing
   question bank is built. When there are thousands of EBRW items, the platform expands to
   the full SAT (both sections, 1600 scale, R&W practice, tests and reports). Build v2 so that
   expansion is additive: subject-aware data and routes where it costs little, no Math-only
   assumptions baked into shared components that would have to be torn out.
4. **No visual budget.** "We are not limiting ourselves visually to miss on functionality...
   as long as we have useful functionality, we can use however much elements, space, and
   whatnot." A useful feature, stat, control, filter, panel or explanation is never cut,
   collapsed away or hidden to save space or look lighter. Pages may be as long and as dense
   as the functionality needs; organise it (sections, tabs, sticky bars, tables) rather than
   remove it. Something belongs if it helps a student study, OR if it makes the site clearer,
   more straightforward or more convenient to use (the user, same day: "not only if it helps to
   study, but even if it makes things clear, straightforward, and very convenient to use") --
   shortcuts, previews, confirmations of what will happen, visible state, counts, legends,
   explanations of a number, one-tap ways to the next step. The only reason to leave something
   out is that it does none of these.
5. **No classes.** "We have a separate platform for classes, drop it." Task S2 (Classes and
   homework, Shell spec §7) is removed: no teacher or student roles, classes, homework,
   assignments, class codes, `/class/` or `/join/` pages, class leaderboards or teacher views,
   and no data or endpoints for them. Anything elsewhere in the plan or the upgrades that
   depends on classes goes too. Compete keeps private contests, but not through classes: a
   private contest is an invite code or link that Compete owns (friends competing together),
   with no teacher or homework features. Resolution R4 of the plan ("Compete's groups are the
   same thing as classes") is void.

6. **No College Board Student-bank features (2026-09-27).** The public Question Bank index in `material/cb/cb_index.json`
   (3,770 questions with subject, domain, skill, difficulty and band) covers what we need: day-one levels and mapping official
   questions to our types. Do not build the two nice-to-haves that would need the signed-in Student Question Bank: resolving a
   Student-bank question ID when a student logs a missed official question (public-index IDs still work), and per-question
   "open on College Board" deep links. A plain link to College Board's Question Bank home is fine.


## Task entry

**S5 · Tests and the test window** (wave 2, port 8025). Builds Part 3.4 in full (runner
components from F3), Compete §8 for the test window, the Weekly Module and Season Final
starts, Review's flags in the runner, Shell's `UI.learner` and token rules for
`web/test/` (R32), QBank's "shelf sections and diagnostic forms remember what they serve".
Owns `web/tests/**`, `web/test/**`, `web/diagnostic/index.html`, `server/api_tests.py`,
`server/papers.py`, `blueprint.py`, `mocks.json`, `forms.json`, `tools/moderate.py`,
`server/checks/s5.py`.
State: not started.


## The section's acceptance list

### 3.4.8 Acceptance checks

1. curl -s -X POST localhost:8000/api/mock/new -H 'X-Learner: a:v2revacc01' -H 'content-type: application/json' -d '{"kind":"section"}' returns begun:false, questions:[], question_count:22 and seconds:2100. A GET 3 s later still reports seconds 2100.
2. The old body {"full":false} still returns a module sitting (Today and Plan keep working), and it lands on the lobby with begun:false.
3. POST /api/session/{id}/answer before /begin returns 409. After POST /begin, GET returns 22 questions and seconds starts to fall.
4. POST /cfg {timing:'x1.5'} before begin changes seconds to 3150. After begin, the same call returns 409.
5. POST /pause, wait 4 s, then GET: seconds unchanged (±1), questions:[], paused:true. /answer returns 409. POST /begin resumes, and the clock falls again from the same value.
6. POST /state {question_id:'m1q01', marked:true, struck:[0,2], ms:12000, conf:'guess'}, then the ms part again, then GET: qstate.m1q01 shows marked true, struck [0,2], ms 24000, conf 'guess'.
7. A recursive key scan of the GET /api/session/{id} JSON (including qstate) finds none of: answer, rationale, reasons, key, seed.
8. GET /api/session/{id} with X-Learner a:v2revother returns 403. With no X-Learner header at all it also returns 403.
9. After finishing module 1: the response has next_module 2 and a summary where answered+unanswered == 22. GET shows begun:false and seconds 2100 for module 2, unchanged 3 s later, until /begin.
10. In test_flow: move module_started back 36 min in the DB. /answer then returns 409 'time is up'. The same answer with made_left:5 is accepted, and result.late is 1 after finish.
11. {"kind":"section","m1":"upper"}: module 1 difficulties count easy 3 / medium 8 / hard 11. After hand-in the results have estimate null and scored false. {"kind":"module","module":"m2u"} also finishes with scored false.
12. {"kind":"section","timing":"x1.5"} gives seconds 3150 after begin; x2 gives 4200; untimed gives null.
13. {"kind":"twin","twin_of":<finished section>}: slot by slot, module 1's stored template and difficulty equal the source's, every seed differs, and the grid-in positions are equal.
14. GET /api/tests lists papers with n 1..7 (label 'Launch set') and this ISO week's paper. Two learners starting {"kind":"paper","paper":1} and beginning get identical module 1 stems.
15. After a learner sits paper 1 twice, the paper's sat_by counts them once, and history marks the second sitting retake:2.
16. GET /api/papers/1/posts before any finished sitting of paper 1 returns gated:true and no text. After one it returns threads. POST without a profile name returns 422. A third report from different codes hides the post.
17. POST /api/session/{finished}/share returns a code. GET /api/shared/{code} contains no stems or keys. {"kind":"shared","shared":code} gives a module 1 whose template and seed equal the source's, slot by slot.
18. GET /api/history?all=1 lists an unfinished sitting with status in_progress and left_seconds. A finished section has modules[0].asked == 22 and separate missed and blank lists.
19. POST /api/session/{id}/discard, then: /api/history?all=1 no longer lists it, /api/tests.in_progress is empty, the row's finished is still NULL, and /api/today tested stays false.
20. Opening http://localhost:8000/test/ with no ?s= creates no row (sqlite3 server/satfreshman.db "SELECT count(*) FROM sessions" unchanged) and lands on /tests/ with the start sheet open at Diagnostic.
21. With the server returning 404 for a made-up id, /test/?s=nope shows 'This test doesn't exist.' and no sample questions.
22. POST /api/report with a question context returns an id, and sqlite3 server/satfreshman.db "SELECT template, seed FROM reports WHERE id='…'" is non-null. A 201-character title gets 422, the 21st report in a day gets 429, and GET /api/reports lists it with status 'open'.
23. Browser 1280, /test/?s=ID: the lobby shows 'Enter fullscreen and begin', 'Begin without fullscreen' and a Change link on Timing. 'Begin without fullscreen' reveals question 1 with the Directions sheet open.
24. Browser: press M. #markBtn gets aria-pressed=true, and strip segment 1 shows the amber dot. After a reload, both are still there.
25. Browser: press C on a multiple-choice question. Option C gets aria-checked=true and the calculator stays closed. Press G: the calculator opens.
26. Browser: turn Eliminate on and click the strike on B. B's text has a line-through and 'Undo' shows. Shift+C strikes C. A reload keeps both.
27. Browser: on question 22 the Next label is 'Review'. Clicking it shows 'Check your work', and the three tile numbers add up to 22. Switching Show to Time prints a time under each cell. Clicking cell 5 opens question 5, and the browser's Back from #review returns to the question.
28. Browser: N opens the navigator. Esc closes it, and document.activeElement is #navBtn.
29. Browser grid-in at 1280: the 'Entering your answer' rail is visible beside the column with the examples table. Typing '1/2/3' leaves '1/2', and the preview renders a KaTeX fraction. '-12345' is accepted; '123456' is refused with the hint shown.
30. Browser: with DevTools offline, choosing an answer shows 'Offline · 1 answer waiting' in #saved. Back online, it shows 'Saved', and the server's answers include it.
31. Browser: Save and exit lands on /tests/. The In progress card shows 'Paused · mm:ss left', matching the seconds from GET.
32. Browser: at 300 s left or less (use a custom test with minutes:6), the hidden clock unhides and the '5 minutes left' toast shows.
33. Browser /tests/ at 390: document.documentElement.scrollWidth === 390. At 1280, #kinds and #papers each compute 3 grid columns, and the section nav shows counts.
34. Browser /tests/ for a new learner a:v2revacc99: the score card shows 'No estimate yet' with the 'No data' chip, the sittings list shows 'Nothing sat yet', Up next recommends the diagnostic, Papers lists at least 7 cards each reading 'Not sat', and there are no page errors.
35. Browser /tests/ with scored sittings: the score card shows a confidence chip with a reason line, 'Routed up N of M sections' and 'Counted: …'.
36. Browser /tests/: setting Kind to Modules removes the section rows, and the URL gains ?kind=module. The filter survives a reload. Export CSV downloads a file whose row count equals the number of visible rows.
37. Browser: a sitting with blanks shows outlined chips for blanks and filled chips for wrong answers, and each chip links to /results/report/?id=…&q=M1-n.
38. Browser start sheet: choosing Full section with Module 1 'Harder' shows 'Harder or easier module 1 is practice, not a score estimate', and the summary line updates. Ticking 'Save these as my defaults' updates GET /api/me profile.test_prefs.
39. The runner at 390 shows no Bluebook dashed rule (.rule elements absent). Every option is a .opt tile from ui.css, and the × Save and exit button is visible in the top bar.
40. PYTHONPATH=. python3 server/test_flow.py passes, including the new checks.


## The upgrades' acceptance items (spec/v2-upgrades/tests.md)

**Acceptance.**
1. `curl -s -X POST localhost:PORT/api/mock/new -H 'X-Learner: a:v2revtests01' -H
   'content-type: application/json' -d '{"kind":"section"}'` returns `conditions:"test_day"` and no
   `pace` key.
2. `{"kind":"section","timing":"x0.85"}` returns 422 naming `timing`. With `"conditions":"training"`
   it returns `seconds:1785` after `/begin`.
3. A Test-day section paused once, then finished: `SELECT ranked, unranked_why FROM sessions WHERE
   id=…` gives `0|paused once`; `GET /api/tests` still shows its band in `estimate.latest`, and
   `estimate.combined` leaves it out.
4. In test_flow: a Test-day sitting whose queued calls flush 3 minutes late with one `pid`, `hid`
   0 and `off` 180000 → after finish `ranked == 1` and `_session.offline_ms >= 180000`. The same
   sitting with a last `hid` of 190000 → `unranked_why == 'away 3:10'`. Two page loads whose `el`
   stamps are 200000 ms apart (the page was closed) → `unranked_why` starts `away`.
5. Browser 1280: with Test-day chosen, the Tools step shows "Pace guide" disabled with "Training
   only"; the lobby shows "this sitting ranks"; the runner shows the `Ranked` chip; Save and exit
   shows exactly [Keep going] and [Pause and exit].
6. The `Like test day` chip lands on `/test/?s=…#lobby` in one click with Timing official and
   Conditions Test-day.
7. A seeded learner whose last 2 sections each had 3 blanks at time-up: the orange preset chip is
   "Pacing practice" and its reason line contains "blanks".


**Acceptance.**
1. In `server/checks/s5.py`, with a seeded Builder: a learner with 40 attempts on Algebra template A
   and none on B (both able to make the slot's tier and format) gets B in the first Algebra slot of a
   Training section, for every builder seed 0–199.
2. Two fresh sections for a new learner keep domain counts 8/7/4/3, tiers 7/8/7 and grid-ins at
   `SPR_AT`.
3. An unbegun section's payload has `holds.subject == 'math'`, `holds.domains` summing to 22 and an
   integer `holds.new_types`, and a recursive scan finds no `key` or `template` values.
4. The Test-day key, over builder seeds 0–199, ranks each template of an Algebra slot's pool first at
   least once, and never reads exposure (the alphabetical lean is gone, and so is the personal one).


**Acceptance.**
1. In `server/checks/s5.py`: `sum(pace_plan(l, 'module1', 1).budget_s) == 2100 − 180` (±1), and
   `== 3150 − 270` at x1.5.
2. A Test-day payload has no `pace`. A Training payload with pace on has `pace.budget_s` of
   length 22.
3. A learner with 20 first-try rights per tier at medians 50 / 80 / 140 s gets `source:'you'`.
4. With `reveal_route` false, module 2's `budget_s` is identical after an upper and a lower route.
5. Browser, Training: staying on Q1 past its budget makes the delta line read "behind".


**Acceptance.**
1. Browser, Training, a custom test with `minutes:2`: at 60 s left with blanks the banner shows, and
   Next blank opens an unanswered question without filling it.
2. On a grid-in, typing `.66` shows the warning; `.45`, `.64`, `.6666` and `0.5` don't. Clearing
   and retyping `.66` in the same sitting doesn't show it again.
3. `repeatingCut` returns true for exactly 15 of the strings `.01` … `.99`.
4. In a Test-day sitting none of these banners exist in the DOM at any point.


**Acceptance.**
1. Browser 1280 with 5 unanswered and 3 marked: `#review` shows "Go through 8". Enter opens the
   lowest unanswered position; the footer reads "Going through · 1 of 8"; after the last queued
   question the view is `#review` and the toast contains "Done".
2. From Q1, `U` opens the first unanswered question after it; `Shift+M` the next marked.
3. An answer posted after `end_at` has `qstate[qid].pass == 2`, and `result.pass2.answered` counts it.


**Acceptance.**
1. At 390: `#markFoot` is in the footer with `aria-pressed`; a 450ms pointer hold on option B gives
   it `.out`; a 100px left swipe on the column opens Q2.
2. At 390 with Highlights & Notes on: a 450ms hold on option B's text leaves B without `.out`, and
   `getComputedStyle(optB).userSelect` is not `none` (the OS selection can start).
3. On a grid-in at 390 the pad shows 15 keys and the field has `inputmode="none"`; tapping `−`, `2`,
   `/`, `3` renders −2/3 in the preview.
4. At 1280, a `contextmenu` event on an option is `defaultPrevented` and the option is struck (with
   Highlights & Notes on, the native menu is left alone).


**Acceptance.** Browser, Training with cover on: `.opts.covered` exists on a multiple-choice
question, `V` removes it, and `GET /api/session/{id}` then has `qstate[qid].reveal_ms > 0`. In a
Test-day sitting the Cover control and `V` do nothing.


**Acceptance.**
1. `POST /api/session/{id}/state {question_id, scratch:{…25 KB…}}` → 422; 10 KB → 200 and returned in
   `GET` qstate.
2. Browser: draw a stroke on Q3, reload: the stroke is there at the same place.
3. Type `y=2x+1` in Desmos on Q4, move to Q5: `qstate.m1q04.calc.exprs` contains it. After finish,
   `SELECT calc FROM attempts WHERE session=… AND qid='m1q04'` is 1.


**Acceptance.**
1. At 1280 with the calculator docked, the Reference tab open and a grid-in question: the question
   column's bounding box is at least 560px wide and fully inside the viewport, neither panel overlaps
   it, and typing `cyl` leaves only the cylinder entry.
2. At 1180 with the calculator docked, opening the reference makes the right slot float
   (`#rightSlot.float`), and the column stays at least 560px wide.
3. After opening the reference twice on Q2, `qstate.m1q02.ref_n == 2`.
4. `Z` on Q3, then `GET /api/saved` lists it with the sitting id; the review item for it has no
   key until the sitting is finished. `B` on Q3 in the same sitting selects option B and saves
   nothing.
5. A learner with a type note on template T: a Training sitting's payload for a T question carries
   `type_note`; a Test-day sitting's payload has no `type_note` at any depth.


**Acceptance.**
1. `POST /state {report_later:'m1q05'}` → `GET` shows it in `qstate._session.report_later`.
2. With a resolved `wrong key` report on m1q05's (template, seed) in `$DB`, `GET
   /api/session/{id}/results` has `removed:['m1q05']` and `modules[0].asked == 21`.


**Acceptance.**
1. After module 1 is handed in, `POST /state {question_id:'m1q03', predict:'miss'}` → 200, while
   `{question_id:'m1q03', marked:true}` → 409. After the final finish, the results'
   `predicted.spotted + predicted.silent` equals the number of wrong answers.
2. Browser, Test-day: after handing in module 1, `#between` shows a countdown under 1:00; with
   nothing pressed, module 2's first question is on screen within 62 s and its clock is running.
3. In test_flow: a Test-day section whose module 2 `/begin` comes from a new `pid` 10 minutes after
   module 1's finish → after the final finish `ranked == 0` and `unranked_why` starts `break`. The
   same with `between_ms` 55000 → `ranked == 1`.
4. Browser, Training: `#between` has no countdown, and module 2 waits for Begin.


**Acceptance.** Finishing a section returns `done.estimate.low` and `.high`; the browser stays on
`#done` (no redirect) and shows "See your report", plus "Pressure check" when there were misses; with
`prefers-reduced-motion` the band has no animation class.


**Acceptance.**
1. A section finished with 3 wrong and 2 blank: `POST /api/drill {pressure:sid}` gives a session of
   at least 5 items whose template and difficulty equal the originals' and whose seeds all differ;
   `GET /api/history` doesn't list it.
2. Answering a twin wrong with the original pick's reason puts that qid in `knowledge`; a blank
   original whose twin is right in 40 s goes to `pressure`; `ceiling` midpoint ≥ the band's midpoint.
3. After the report's review has been opened, `POST /api/drill {pressure:sid}` → 409 `answers already
   seen`.
4. `progress.causes(session=sid)` gives `slip` for the `pressure` qids and `trap` for `knowledge`.


**Acceptance.**
1. A module 1 with 13 right: `result.gate == {right:13, needed:14, margin:-1, …}`.
2. Three trainer sittings that route up in a row → `GET /api/tests` `kinds` row `trainer` has
   `streak:3`.
3. The Protect the gate body's templates are all easy or medium misses from module-1 positions.


**Acceptance.**
1. A seeded learner with 2 sections, 4 named-trap misses and 3 blanks at time-up: `levers.causes` has
   `trap` with `n:4, pts>0` and `clock` with `n:3`, and the trap action body has `pool:'redo'`.
2. `growth` is null with fewer than 20 peers.
3. An outside Bluebook score 610 dated 3 days after a section banded 560–700 → `calibration.inside ==
   true`.
4. With `rw_now` 620, `total` is present and the card shows "Total".


**Acceptance.**
1. After a section with 3 named traps, fixing them (2 clean answers each) gives `GET
   /api/tests.cycle.prove.due` = the closing date + 3 days.
2. `{"kind":"custom","custom":{"source":"traps","from_session":ID,"neutral":0.25}}` builds at least 6
   questions; each trap slot has an option whose stored reason's norm equals its trap's norm; the neutral
   slots offer none of the learner's trap norms.
3. Choosing the trap option reopens that trap with `relapses + 1`; a right non-guess answer adds 1 to
   `checks`.
4. The Trap test's results have `estimate: null`, and `/api/history` labels it `Trap test`.


**Acceptance.** A seeded learner with 3 timed sections whose qstate gives 5 right→wrong and 2
wrong→right: the `changes` row has `verdict:'costs'` and evidence containing "5" and "2"; with 1
sitting the section shows the empty state; with data, at least 8 rows render and no "Show all" control
exists.


**Acceptance.** A twin against its source returns `by:'slot'` and summary counts that add up to the
slots asked; two unrelated sections return `by:'template'`; another learner's code gets 403; ticking
two rows shows the bar; `?compare=a,b` opens the sheet.


**Acceptance.** A test question where the key's index was struck and unstruck and the pick is wrong:
`qstate[qid].struck_ever` contains the key index, and after finish `attempts.struck` for that qid holds
the final strikes.


**Acceptance.**
1. Two learners start and begin `{"kind":"paper","paper":1}`: slot by slot their module 1s have equal
   `(key, difficulty, type)`, and at least 20 of 22 seeds differ.
2. `SELECT questions FROM papers WHERE n=1` has `sections[0].subject == 'math'` and no `stem`.
3. A learner whose `linear_functions` skill rating is 300 below their other Algebra topics, and two
   papers where one has 5 more module 1 Algebra slots on linear functions at the same tiers: in `GET
   /api/tests`, that paper's `rating.you.expect_m1` is at least 1 lower than the other's. A learner
   with no answers gets `rating.you.source == 'types'`.
4. With fewer than 20 ranked first sittings, `rating.everyone.source == 'predicted'`; the code path
   reads `item_ratings` and has no tier-default constants.
5. A paper with 3 first sittings, 1 ranked: its card reads `Sat by 3 · 1 ranked`.
6. Selecting a filter option shows as many cards as its count said.
7. A Retake's seeds are all different from the learner's first sitting's; `Again, exactly` gives equal
   seeds and history marks it `exact`.
8. After a Season Final with 25 ranked sittings closes, the next Monday build adds a paper with
   `source` starting `final-`, and its card shows `Sat by 25` and a percentile line.


**Acceptance.**
1. Before sitting: `gated:true` and no `slots` key. After: 44 or more slot rows.
2. With fewer than 20 first ranked sittings and a slot whose (template, tier) has 30 first tries
   site-wide: that slot has `source:'site'`, `n:30` and a numeric `right`.
3. A slot with 3 answers in total has `spread == []` and a non-empty `designed`.
4. Spread shares add up to at most 1. `cheapest` lists only your misses and blanks.
5. A learner code with no finished sitting of paper 8 → `POST /api/papers/8/posts` 403.


**Acceptance.** Two learners on one twin share get equal templates and tiers per slot with different
seeds; `GET /api/sets/{code}` has no stems; a finished pair's peers carry labels and no `given` key.
`Race friends` on a finished section → `POST /api/contests {from_session, count:22, minutes:35,
twin:true, open_for:72}` returns a code matching `^[A-HJ-NP-Z2-9]{6}$`; a second learner joining with it
gets module 1's templates and tiers slot by slot with different seeds. Nothing in `web/tests/` or
`web/test/` calls `/api/classes` or links to `/class/` or `/join/`.


**Acceptance.** On `/tests/`, `J` focuses the first card; `Enter` on a paused row opens its lobby; `GET
/api/shell` for a learner with a paused test has `next.items[0].kind == 'resume'` and "Paused" in its
title; the downloaded `.ics` has a SUMMARY starting "Finish".

---

## 3. Spec overrides


## Contracts and amended checks

| # | topic | what disagreed | decision | owner |
| R5 | Mark vs Save | QBank merges marking into saving (as TopTierPrep does); Review keeps them apart | **Two things everywhere** (Review model). *Mark for review* = a flag on one question in one sitting (`flags` table, flag icon, per sitting). *Save* = keep a question for good (`saved` table, bookmark icon). QBank's "rename Saved to Marked for review" is not done; its builder gets two pools, Marked and Saved. QBank's "a right replay removes it from Marked" is not built; Review has Unmark / Unsave with Undo. The Report button's icon is a speech bubble with "!", never a flag. | F4 (tables), S10 (endpoints) |
| R6 | Highlights and notes | QBank stores notes per (template, seed); Tests stores marks per sitting in `qstate`; Review stores a note on `saved` | **One store:** `notes(learner, template, seed, note ≤1000, marks JSON ≤50)`. Written with `POST /api/notes {session, question_id, note?, marks?}` from any sitting kind; the server resolves (template, seed) and never trusts the client for them. Mark styles are Tests' seven: highlight, strong, underline, dashed, dotted, box, strike (each mark may carry a note ≤500). A saved question's note (Review §5) is the same note. Notes come back wherever that exact question appears: replay, retake, review, report, Saved. | F4 (`api_notes.py`), F3 (`UI.annotate`) |
| R7 | Per-question time, trail, strikes in tests | Report adds `sessions.times` and `sessions.trail`; Review adds `sessions.times`; Tests adds `sessions.qstate` | **One column `sessions.qstate`** (JSON): per qid `{ms, struck, conf, trail, first, changes}` and `_session {away_ms, away_n, late}`. Flags are not in it (R5). The runner sends `ms` (dwell delta) and `made_left` with each answer save and other deltas with `POST /api/session/{sid}/state`. `record_paper` passes `qstate[qid].ms` into `attempts.ms`, so tests count as study time and per-question time. Report's `/flag` and `/time` endpoints are served by Review (flags) and Tests (`/state`). | F4 (column, record_paper), S5 (endpoints) |
| R8 | Attempts columns and what counts | Review adds norm/repeat/repair/flagged/stem; QBank guess; Shell disputed; Compete sms/void | **One set of new `attempts` columns:** `norm, repeat, repair, flagged, guess, disputed, sms, void, stem`. Mastery, accuracy, boards and ranks leave out rows with `repeat=1`, `disputed=1` or `void` set; a right answer with `guess=1` counts half. Study time and question counts keep every row. A **clean answer** (closes a mistake, counts as a check-in) is right, not a repeat, not flagged and not a guess. `progress.record` computes `repeat` itself for every caller. | F4 |
| R9 | Traps and check-ins | Review rebuilds traps (id, norm, kinds, relapses) with check-ins at 7/21 days; Plan wants rechecks at 3/10/30 via stage/due; Shell adds source/note/origin | **One `traps` table:** Review's rebuild (integer `id`, `norm`, `reason` = latest concrete text, `closed_how`, `relapses`, `seed`, `session`) plus Shell's `source` ('outside'), `note`, `origin`, plus **one check-in schedule: 3, 10 and 30 days after fixing** (Plan's), stored as `due` + `checks` (0 to 3). A miss on a due check reopens it as Relapsed. Plan's Rechecks task is the drill pool `checks` (R10); Review's "Check these now" and "CHECK-INS DUE" use the same. Kinds: misconception, gridin (named when the template has `spr_mistakes`), slip, unsure. | F4 |
| R10 | Drill body | Nine sections add their own fields to `POST /api/drill` | **One body contract (§2.6)**, validated in one place and built by F5. Section field names map onto it (table in §2.6). Fields that need another section's data stay on `POST /api/drill` and are resolved by the owner's module through a registry: `like` (S3, `daily.resolve_drill`), `word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2, `classes.resolve_drill`); contests are started by S8's own routes. `list` is accepted as an alias of `pool`, so Review's bodies work unchanged. | F5 |
| R11 | Preferences | Shell prefs, QBank prefs, Tests `learners.test_prefs`, Words `words_goal/words_from/gloss` columns, Shell `study_time` column | **One `learners.prefs` JSON and one registry `server/prefs.py`** with every key in §2.7. The separate columns are not added. Settings (S1) renders every key; the Practice builder, the test start sheet, Plan step 4, Me and the session's More menu write the same keys. Unknown key or bad value → 422 naming the key; only non-default values are stored; GET returns defaults merged. | F4 |
| R15 | Goals and SAT dates | Target/exam date edited on Today, Me and Plan; R&W fields; three copies of SAT_DATES | `target, exam_date, current, minutes, days, tests, focus, rw_now, rw_target` live on `learners`; the active plan mirrors them both ways (Plan §5, `plan.mirror()`), so one edit shows everywhere. Dashboard's `plan_started` is `plans.start`. Upcoming official dates: one constant in `server/satdates.py`, served in `/api/shell.dates`, read by the date pickers on Today, Me, Plan and Compete's seasons. Past dates are never offered. A new `exam_date` must be today or later in the learner's zone. | F4 |
| R16 | Estimate, confidence, percentile, drift | Report, Tests, Today and Plan each define an estimate or percentile; Compete adds a report percentile | **One module `server/estimate.py`:** `estimate(learner)` returns latest, previous, best, range, `mean3` (mean midpoint of the last up to 3 scored sittings within 45 days, added outside Math scores included), combined (≥2 standard sections: mean ± 70/√n), confidence `{level, reason}` with **Tests §2.2's rules and wording**, trend (±20 = steady), routed_up and counted. `percentile(sid)` ranks a sitting among **each learner's first standard sitting of the same kind** (a paper: of that paper), shown only when n ≥ 20; standard = timed official, adaptive, standard module 1, not fixed-route or extended. The Report hero, Tests cards, Results, Today's score card and the report's Ranked pill all use it; Compete's "last 90 days" variant is not built. **Drift** is Plan's rule (mean3 vs the plan's start, ≥ 40 either way; target reached) and Today's drift line shows Plan's `suggest`. | F4 |
| R17 | Report a problem | Shell (10 images downscaled, disputes, admin), QBank (3 × 5 MB BLOBs), Tests (R-#### ids, tools), Report (3 screenshots), Words (10 images) | **One system:** Shell §2.10 and §10 are canonical: one modal `UI.report(ctx)`, up to 10 images (PNG, JPEG, WebP, GIF), stills downscaled in the browser to 2000px, 10 MB server cap, files on disk under `server/reports/{id}/` (git-ignored), bounded disputes (5 open), Your reports with replies in Settings, `/admin/reports` behind `SATF_ADMIN_TOKEN`. Categories per context are the union: Shell's lists, plus Tests' "More than one right answer" and "No right answer", plus Words' "Wrong or unclear definition" (word context). Mid-test reports never show marking and hide key disputes. Rate limit: 10 an hour and 20 a day per learner (429). Ids are integers. `tools/reports.py` is an optional CLI over the same table. | F6 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
| R19 | Access to keys and re-serving | Review defines `access()`; others re-serve items ad hoc | **One rule, `deps.access(learner, template, seed)` → `reveal` \| `kept` \| None** (Review §server). Everything that returns a key or re-serves an exact (template, seed) goes through it: review endpoints, sets, worksheets, the report, the challenge review, permalinks, Words examples. Live-test items and unanswered or same-day challenge items never leak. The permalink `/practice/session/?q=TEMPLATE:SEED` (QBank; Shell's `/q/` is the same route) serves any catalogue item that is not in today's challenge as a fresh one-question drill; the key shows after answering, as always. | F4 |
| R21 | One question format | QBank `UI.workspace`, Tests runner shell, Today confirm mode, Words quiz mode | **One component `UI.workspace` (question.js) and one runner shell (runner.js/css).** Modes: `practice` (feedback instant / retry / end), `exam`, `review` (read-only, Hide answers, re-answer files a repeat), `quiz` (Words), `inline` (quick sheet, Today's Try one, sheets). The practice session and the exam runner use the same runner shell: sticky top bar, progress rail, question strip, footer (Back · "Question N of M ⌃" · Check/Next), navigator, Check your work, timer, calculator dock, highlights. The exam runner's look is the practice session's (Tests §1). `UI.question` stays as a thin alias. | F3 |
| R22 | Keyboard | QBank uses C for calculator and S for skip; Review S for save; clashes with choosing C | **One registry `UI.keys` (F2) and one map (§2.8).** Calculator G, reference F, save B, skip S, history Y, highlights L, confidence K. Shortcuts are ignored while typing (Enter and Esc aside) and when `prefs.keys` is off. | F2, F3 |
| R24 | Drills that are not sittings | twin, try, word-example, review pane, spot, quick each have their own list rule | `cfg.inline = true` for sources `twin, try, word-example, review, spot`: never listed as a sitting, never in history, In progress or Resume; their answers file normally (a twin counts on its parent). `quick` sittings are listed in history as "Quick questions", never offered as Resume, and deleted when finished with 0 answers. Any set finished with 0 answered is never listed. | F5 (flag), S6 (history), S4 (drill list) |
| R28 | Contest sittings inside the runners | Compete specifies changes to the practice session and the test window, which S4 and S5 own | S4 and S5 build Compete §8 on their pages and in `drill.py` / `api_tests.py`, through hooks that Compete provides: `compete.clock(row)` (the answer clock), `compete.twin_questions(learner, cid, slots)`, `compete.finish_contest(row)` (points, secs, ranked), `compete.state_extra(row)` (ranked chip, field line). Skip, voiding, reveal-at-end, sprint mode and the leave sheet are generic runner features any sitting can switch on. | S4, S5 (hooks), S8 (functions) |
| R32 | Theme tokens in the test window | Shell tokenises `web/test/`; Tests rewrites it | The Tests rewrite ends with no hard-coded colours in `web/test/` (Shell's grep acceptance applies to S5). Me and the report page are tokenised by their owners (S1, S6). | S5, S1, S6 |
| R36 | Session kinds | new kinds from Tests and Words | New `sessions.kind` values: `custom` (Tests' custom test), `words` (Words runs), `spot` (Review). `UI.KIND` (kit) holds every label; `/api/history` lists `words` only with `?kind=words` and never lists `spot`. | F1, S6 |
| R38 | Diagnostic gate | Today and Report respect the sign-up gate | Kept as today until the user decides (open question 8). Today, Report, Tests and Fix all respect it. | S3, S5, S6 |
| state | fill / edge | glyph | meaning |
| Correct | `--amber` fill, `--ink-deep` number | ✓ top-right | right on the first try |
| Incorrect | `--ink` fill, white number | ✕ | wrong |
| Mixed | diagonal split `--amber` / paper, 1.5px `--amber-deep` edge | ~ | right on try 2 or 3 in retry mode (only the first try counts) |
| Repaired | `--amber` fill with an ink ↻ corner | ↻ | right on the repair question that followed a miss |
| Fixed since | paper, 1.5px `--ink` edge, ink number | ✕ + small amber ✓ badge | wrong then, and the mistake has closed since (report) |
| Unanswered / Blank | paper, 1.5px dashed `--faint` edge, `--soft` number | – | not answered (a blank is never "Incorrect", R35) |
| Skipped | 1.5px dashed `--soft` edge | » | skipped, can still be answered before Finish |
| Voided | paper with a diagonal ink slash | ⊘ | a contest question voided by leaving or copying |
| Repeat | 1.5px ink outline, no fill | = | an exact re-attempt; left out of mastery |
| Not reached | dotted `--faint` edge | · | a set ended with this question on screen; left out of counts |
| Answered (exam, end mode) | `--ink` fill, white number | – | answered, no verdict shown |
| Flagged (overlay) | amber flag notch, top-right, 9px | flag | marked for review in that sitting |
| Saved (overlay, lists only) | bookmark | bookmark | kept |
| Has note (overlay) | 7px note glyph, bottom-left | note | a note or highlight exists |
| Current (overlay) | 2px ink ring, 2px paper gap | – | the question on screen |
| Filtered out | 30% opacity, skipped by Tab | – | outside the active filter |
| file | owner | components (signature, then who uses it) |
| `web/assets/head.js` | F0 → F2 | the theme / text size / motion snippet of Shell §2.13, run before first paint |
| `web/assets/ui.js` | F2 | `UI.learner()`, `UI.useLearner(code)`, `UI.api(path, opts)` (sends X-Learner and X-Tz; network error → offline banner; 401 retired → banner), `UI.shell(pageOverride?)` (sidebar 248 / rail 68 / phone bar + 5 tabs + menu sheet, skip link), `UI.refresh()` (alias `UI.me`), `UI.prefs()` (defaults merged), `UI.prefRow(host, key)`, `UI.keys.register(scope, map)` + the `?` shortcuts sheet, `UI.SAT_DATES`, `UI.chip`, `UI.ref`, `NAV`, `SECTION`, `TOPICS` + aliases |
| `web/assets/quick.js` | F2 | `UI.quick(tab?)`: Quick question · Log a mistake · Add a word (R29) |
| `web/assets/palette.js` | F2 | `UI.palette()`: pages, skills, 386 question types, named misconceptions, actions, "circles hard 5 timed" parsing |
| `web/assets/qr.js` | F2 | vendored MIT QR encoder, loaded by Settings (pairing) and Class (join code) |
| `web/assets/ui.css` | F1 | tokens (light + dark), status and level tokens, every shared class: `.card .card-head .card-err .skel .btn .quiet .pill .seg .switch .chips .field .counter .otp .stat .meter .badge .kbd .table .thumbs .legend .cell .strip .pips .dbars .menu .popover .tip .toast .banner .sheet .side .side-item .side-meta .side-day .rail .pbar .tabs` + print styles; the new header comment of §2.1 |
| `web/assets/kit.js` | F1 | overlays: `UI.sheet({title, body, actions, size})` (native `<dialog>`; a bottom sheet under 760px; Esc; focus returns), `UI.confirm({title, text, confirm, cancel, input}) → Promise`, `UI.pop(anchor \| rect, content, {role})` (anchored popover or listbox; Esc and outside click close; can anchor to a text selection), `UI.menu(trigger, items)`, `UI.tooltip(el, text)`, `UI.toast(text, {action, href, undo, ms})` (3 stacked, polite), `UI.banner(kind, text, actions)`. Controls: `UI.seg(host, options, {value, multi, onChange})`, `UI.tabs(host, tabs, {counts})`, `UI.switch`, `UI.chips`, `UI.dropdown(host, {label, options, groups, multi, counts})`, `UI.filterBar(host, filters, {url, store, sheet})` (URL sync, "Filters · n" bottom sheet on a phone, Clear), `UI.triCheck`, `UI.otp(host, onComplete)`, `UI.counter(field, max)`, `UI.scoreSlider(host, {min, max, step, value, onChange})` (range + number field + bubble), `UI.images(host, {max, maxBytes, maxEdge})` (the downscaling picker; paste and drop), `UI.examDate(anchor, {value, onSave})` (upcoming official dates with "in N days", Another date, No date yet). Data: `UI.tile(host, {label, value, sub, href, filter})` (count-up), `UI.meter`, `UI.skel(host, shape)`, `UI.cardError(host, retry)`, `UI.table(host, cols, rows, {sort})`, `UI.pips(owed, of)`, `UI.dbars(tier)`, `UI.cell(state, n, overlays)`, `UI.legend(host, states, counts)`, `UI.strip(host, marks, {onPick})`, `UI.masteryWord`, `UI.skillRow(host, skill, {practise})`, `UI.avatar(profile, size)`, `UI.countdown(el, iso)`. Formatters: `UI.dur`, `UI.mmss`, `UI.num`, `UI.date(d, 'long' \| 'short' \| 'eyebrow')`, `UI.relTime`, `UI.KIND` (every session kind and label, R36), `UI.copyText(text)` (clipboard, else select in a field), `UI.ics(event)` (one event, or a daily repeating reminder) |
| `web/assets/charts.js` | F1 | each with `role=img`, an aria summary and a visually hidden data table: `UI.bandChart(host, points, {height, target, exam, estimate, outside, onPick})` (Results, Today, Tests, Me, share view), `UI.gauge(host, {band, target, previous})` (Report), `UI.scale(host, {band, target, start})` (Today, Tests cards), `UI.barChart(host, rows, {planned, stacked, pace})` (study time, forecast, pace per question), `UI.calendar(host, {month, days, plan, marks, onPick, min, max})` (one Monday-first month grid with heat, plan marks, exam mark, roving tabindex; Today and Plan), `UI.heatmap(host, days, {weeks})` (Me, share view), `UI.lineChart(host, series, {bands})` (Compete rating / top %), `UI.spread(host, options)` (option or misconception spread; QOTD, contest review, class results) |
| `web/assets/question.js` | F3 | `UI.workspace(host, q, opts)` (R21; `UI.question` alias): modes practice (instant / retry / end), exam, review, quiz, inline; select-then-Check (prefs.first_tap restores one tap); strike with Undo; auto 2x2; the grid-in field with keystroke filter, rule line, stacked-fraction preview with its decimal, "All entry rules" popover, accepted forms; every option's misconception after the reveal (prefs.option_reasons); crowd bars; I'm guessing; the actions-row slot; Hide answers; `UI.annotate(host, marks, {editable, onChange})` (7 styles, notes, notes rail, read-only render) |
| `web/assets/runner.js` + `runner.css` | F3 | `UI.runner(host, {mode, top, footer})` (the shell shared by the session and the test window: sticky top bar, progress rail, question strip with labelled tools, footer Back · "Question N of M ⌃" · Check/Next), `UI.navigator(host, cells, {views})` (Status / Difficulty / Skill / Time, legend with counts, filters; popover or bottom sheet), `UI.checkYourWork(host, cells, opts)` (tiles, grid, Time view, warning, pacing line), `UI.timer(el, {secondsLeft, elapsed, hideKey, pause})`, `UI.calc(opts)` (float, dock at ≥1100px, resize, phone sheet, Desmos state per sitting), `UI.saveQueue(sid, send)` (ordered, retried, localStorage mirror, `made_left`, status callback), `UI.review(host, items, {mode: 'dialog' \| 'pane', filters, actions})` (R23), `UI.history({template} \| {session, question_id})` (attempt history modal), runner key maps (§2.8) |
| `web/assets/report.js` | F6 | `UI.report(ctx)` (R17): ctx `{kind: 'question' \| 'sitting' \| 'page' \| 'word' \| 'paper' \| 'catalog', source, session, question_id, day, word, paper, revealed}` |
| `web/assets/results-ui.js` | S6 | `UI.sittingCard(host, row, {actions})` (Tests T6 row design: band, route chips, M1/M2, time, wrong vs blank chips per module linking to `?q=`, actions line, note; In progress / Time's up / gated states), `UI.skillPanel(topic)` |
| `web/assets/plan-ui.js` | S7 | `UI.taskRow(host, task, {actions, compact})` (status circle or checkbox, title, type tag, meta, Start / Resume / Review, Why this?, ⋯ menu) |
| `web/assets/compete-ui.js` | S8 | `UI.board(host, data, {columns, onMore, youBar, rowMenu})`, `UI.level(rating, provisional, size)`, `UI.podium(host, top3)` |
| `web/assets/words-ui.js` | S9 | `UI.word.open(slug, {list})`, `UI.gloss(el)`, `UI.addWord(prefill)`, `UI.addWordFromSelection(root)`, `UI.speak(text)` |
| table | columns | written by |
| `flags` | learner, session, qid, template, seed, topic, at; PK (learner, session, qid) | S10 endpoints, S5 runner through them |
| `notes` | learner, template, seed, note, marks JSON, at; PK (learner, template, seed) | F4 `api_notes.py` |
| `links` | token PK, learner, kind ('progress' \| 'cal'), created, revoked, views INTEGER DEFAULT 0, last_view | S1 (progress), S7 (cal) |
| `pairs` | code PK, learner, created, expires, used, req_learner, req_device, req_answers INTEGER, state DEFAULT 'open' | S1 |
| `retired` | code PK, into, at | S1 (read by `deps.learner_of`, F4) |
| `reports` | id INTEGER PK AUTOINCREMENT, learner, kind, source, session, qid, paper, word, template, seed, category, title, answer, given, details, context JSON, device JSON, email, files JSON, dispute INTEGER DEFAULT 0, at, status DEFAULT 'new', reply, replied, seen | F6 |
| `sets` | code PK, owner, kind ('set' \| 'test' \| 'items'), session, items JSON, cfg JSON, title, show_score INTEGER DEFAULT 1, created, revoked | F6 |
| `earned` | learner, id, tier INTEGER, at; PK (learner, id, tier) | S1 |
| `classes` | id PK, name, code UNIQUE, owner, created, archived | S2 |
| `members` | class, learner, display, joined, left; PK (class, learner) | S2 |
| `assignments` | id PK, class, title, kind ('set' \| 'module' \| 'section'), cfg JSON, questions JSON, who JSON, due, created | S2 |
| `attachments` | assignment, learner, files JSON, at; PK (assignment, learner) | S2 |
| `tries` | learner, session, qid, n INTEGER, given, correct INTEGER, reason, ms INTEGER, at | S4 |
| `outside_scores` | id PK, learner, day, math, rw, source ('bluebook' \| 'official' \| 'other'), at | S3 (S7 records the exam result through S3's `add_outside_score()`) |
| `plans` | id PK, learner, name, cfg JSON, start, tz INTEGER, start_mastery JSON, created, updated, archived, result JSON, drift_seen | S7 |
| `plan_days` | plan, day, kind, minutes, test, phase, tasks JSON; PK (plan, day) | S7 |
| `plan_overrides` | plan, day, minutes, off INTEGER DEFAULT 0, test, topics JSON; PK (plan, day) | S7 |
| `plan_tasks` | id PK, plan, day, repeat, title, minutes INTEGER, created, removed | S7 |
| `plan_marks` | plan, day, task, status, to_day, at; PK (plan, day, task) | S7 |
| `papers` | n INTEGER PK, week UNIQUE, label, built, questions JSON | S5 |
| `posts` | id INTEGER PK, paper INTEGER, learner, name, at, edited, parent INTEGER, about, text, helpful INTEGER DEFAULT 0, reports INTEGER DEFAULT 0, hidden INTEGER DEFAULT 0 | S5 |
| `post_votes` | post, learner, kind ('helpful' \| 'report'); PK (post, learner, kind) | S5 |
| `contests` | id PK, kind, title, owner, code UNIQUE, grp, opens, closes, count INTEGER, seconds INTEGER, spec JSON, questions JSON, created | S8 |
| `contest_items` | contest, template, seed; PK | S8 |
| `contest_members` | contest, learner, joined; PK | S8 |
| `item_ratings` | template, tier, rating REAL, n INTEGER; PK (template, tier) | S8 |
| `name_reports` | target, reporter, at; PK | S8 |
| `seasons` | id PK, opens, closes, standings JSON, closed | S8 |
| `kv` | k PK, v | S8 (the HMAC secret for board ids) |
| `word_state` | learner, word, box INTEGER DEFAULT 0, due, reps, lapses, right, wrong, saved INTEGER DEFAULT 0, first, last, lastday, lastwrong; PK (learner, word) | S9 |
| `word_reviews` | id PK, learner, word, session, mode, kind, correct, given, confusion, box_before, due_before, ms, at | S9 |
| `my_words` | id PK, learner, word, meaning, pos, example, same JSON, opposite JSON, notes, list, source, created, updated | S9 |
| field | values | meaning |
| `topics` | [slug] | skills |
| `templates` | [template], ≤ 120, each in the catalogue | only these question types, round-robin |
| `exclude` | [[template, seed]] | never serve these (the day's own question for a "like" drill) |
| `want` | {template: regex} | walk up to 40 seeds for an item where some option's reason matches (a mix-up drill, same-mistake-elsewhere) |
| `count` | 1–120 or null | null = endless |
| `tiers` | subset of easy, medium, hard | legacy `difficulty` maps here; `'adaptive'` in it means `adaptive: true` |
| `levels`, `unmeasured` | [1..7], bool (default true) | measured levels (QBank) |
| `formats` | subset of mcq, spr | legacy `format`/`fmt`: both, mcq, grid, spr; `mix` = both with `spr_share: 0.5` |
| `spr_share` | 0–1 | share of grid-ins in the set (Plan's format tilt) |
| `adaptive` | bool | step up after 2 first-try rights in a skill, down after a miss (R33) |
| `order`, `mix` | mixed \| grouped \| ramp; even \| blueprint | QBank |
| `pool` | `new` (default) · `redo` (open mistakes) · `checks` (fixed mistakes due a check-in) · `review` (types right ≥ 10 days ago, no open trap) · `untried` (never answered; falls back to least answered) · `seen` (exact replays of past attempts) · `saved` · `marked` (flags) · `history` (attempt ids) · `items` ([[template, seed]]) · `set` (a sets code) · `related` (a norm) | where the questions come from |
| `ids` | selection within the pool | trap ids, [session, qid] pairs, [template, seed] pairs, attempt ids, a set code, a norm; null = all matching |
| `exact` | bool | serve those exact (template, seed) (each checked by `deps.access`, R19) instead of fresh seeds on their templates |
| `each` | 1–5 | fresh questions per template |
| `level` | as_missed \| any \| harder | tier for redo and checks |
| `result`, `marked`, `from` | any \| missed \| right \| guessed; bool; both \| practice \| tests | filters for `seen` |
| `from_session`, `only`, `scope`, `still_open` | sid; [qid]; misses \| all; bool | Fix these (Report); a diagnostic before sign-up → 403 |
| `retake`, `again`, `item` | sid; sid; 'template:seed' | exact retake; same settings new questions; permalink |
| `timed`, `minutes` / `timing` | bool, 1–180 / off \| pace \| custom | the clock (pace = 95 s a question) |
| `feedback` | instant \| retry \| end | stored in cfg; S4 implements retry and end |
| `repairs` | next \| end \| off | when the repair after a miss comes |
| `source` | map, coach, plan, today, mistakes, review, quick, palette, assignment, outside, twin, try, word-example, words, worksheet, shared, qotd, spot | a label; `twin, try, word-example, review, spot` set `cfg.inline` (R24); `quick` with no topics takes the coach's pick |
| `task` | `YYYY-MM-DD:(fix\|recheck\|focus\|extra\|test)` | Plan's tag |
| `parent` | sid | a twin drill's parent sitting |
| `like`, `word`, `confusion`, `assignment` | as in the owner's spec | resolved by the owner module's `resolve_drill(learner, body)` through `deps.part` into the fields above; 501 until that module exists |
| `contest` | set only by S8's server code, never from the client | |
| spec | its field | canonical |
| Shell | `unseen`, `trap {template, reason}`, `format`, `difficulty:'adaptive'`, `templates` | `pool:'untried'`, `pool:'redo', ids:[trap id]`, `formats`, `adaptive:true`, `templates` |
| Today | `like {day, slot}`; `mistakes:true, templates, count` | kept on the body; `daily.resolve_drill` (S3) turns it into `templates`, `exclude` (and the 409 "answer it first"); `pool:'redo', templates, count` |
| QBank | `pool:'mistakes'`, `saved:true`, `share`, `difficulty` | `pool:'redo'`, `pool:'saved', exact:true`, `pool:'set', ids:code`, `tiers` |
| Plan | `recheck:true`, `fmt`, `task` | `pool:'checks'`, `formats` / `spr_share`, `task` |
| Words | `word`, `confusion` | kept on the body; `words.resolve_drill` (S9) turns them into `templates`, `want` (409 for a bankless mix-up) |
| Review | `list`, `ids`, `exact`, `each`, `level` | `list` is an alias of `pool` (fixed → `checks`, templates → `templates`, share → `set`); same names otherwise |
| Report | `only`, `each`, `scope`, `still_open`, `source:'twin'` | same names; `parent` = the report's sitting |
| Compete | `templates` ("another like this") | same |
| key | values | default | also edited in |
| `set_length` | 0–120 (0 = endless) | 10 | builder, Me, quick sheet, palette |
| `clock`, `clock_minutes` | off \| pace \| custom; 1–180 | off; 16 | builder, Me |
| `tiers` | non-empty subset of easy, medium, hard | all | builder |
| `adaptive` | bool | false | builder, Me ("Adaptive" option) |
| `levels`, `unmeasured` | [1..7]; bool | all; true | builder |
| `formats` | non-empty subset of mcq, spr | both | builder |
| `feedback` | instant \| retry \| end | instant | builder, session More |
| `repairs` | next \| end \| off | next | builder |
| `rationale` | miss \| always \| tap | miss | Me, session More |
| `option_reasons` | bool | true | session More |
| `first_tap` | bool | false | session More |
| `order`, `mix` | mixed \| grouped \| ramp; even \| blueprint | mixed; even | builder |
| `pool` | new \| redo \| checks \| review \| untried \| seen \| saved \| marked | new | builder |
| `keep_warm` | bool | true | Settings (coach revisits strong skills after 10 days) |
| `confirm_end`, `keys` | bool | true | Settings |
| `show_timer`, `show_stopwatch`, `pace_alert` | bool | true | Settings, session More |
| `calc_button`, `calc_mode`, `ref_button` | bool; closed \| dock \| float; bool | true; closed; true | Settings, session More |
| `theme` | light \| dark \| system | light | Settings, palette (mirrored to localStorage `satf.look`) |
| `text` | small \| normal \| large | normal | Settings, runner More (A− A A+) |
| `motion` | system \| reduce | system | Settings |
| `week_start` | mon \| sun | mon | Settings |
| `gloss` | bool | true | Settings, Me (underline math words in questions) |
| `study_time`, `remind` | HH:MM or null; 0 \| 10 \| 30 | null; 10 | Settings, Plan step 3 |
| `test_timing` | official \| x1.5 \| x2 \| untimed | official | test start sheet, lobby, Me |
| `test_calculator`, `test_pace`, `test_confidence`, `test_reveal_route`, `test_fullscreen` | bool | true, true, false, false, true | test start sheet, lobby, Me |
| `words_goal` | 0 \| 5 \| 10 \| 20 (0 = no words in the plan) | 10 | Plan step 4, Me, Words |
| `words_from` | non-empty subset of math, sat, transitions | [math] | Plan step 4, Me |
| scope | keys |
| Global (pages with the shell) | `G` then `T` Today · `P` Practice · `M` Review · `W` Words · `E` Tests · `L` Plan · `K` Class · `R` Results · `C` Compete · `U` Profile · `S` Settings · `H` Help. `Q` quick sheet. ⌘K / Ctrl K palette (`/` too, except on pages where `/` focuses that page's search: Words, Review). `[` collapse the sidebar. `?` shortcuts |
| Runner: practice session and test window | `A–D` / `1–4` choose · `Shift+A–D` strike / undo · `Enter` Check, Next or Save & next · `←` `→` back / next · `E` eliminate mode · `M` mark for review · `B` save (practice) · `L` highlights & notes · `O` my note · `K` confidence (exam, when on) · `I` I'm guessing (practice) · `S` skip (practice) · `D` details · `N` navigator · `Y` attempt history (after answering) · `G` calculator · `F` reference (formula sheet) · `H` hide / show timer · `P` pause (practice) · `Shift+R` check your work · `?` · `Esc` |
| Player: report review, Review pane, challenge review | `←` `→` or `J` `K` move · `N` next miss · `H` hide / show answers · `T` try one like this · `E` again, exactly · `B` save · `M` mark · `Y` history · `I` details · `R` report · `A–D` / `1–4` pick while answers are hidden · `Esc` |
| Lists (Review, Words) | `J` `K` or `↑` `↓` move · `Enter` open · `X` select · `/` search · `N` add a word (Words) |
| Flashcards and word quizzes | `Space` flip · `1` / `2` grade · `←` `→` · `B` save (after the verdict in a quiz) · `P` speak · `O` open word · `A–D` / `1–4` |
### 2.9 Contracts: who provides what to whom
| F6 | `UI.report`, `POST /api/report`, `GET /api/reports`; `sets` endpoints and `/s/` | every page with a question; S4, S5, S10 (share); S6 (peers) |
| S5 | the lobby at `/test/?s=`; `POST /api/mock/new` (old body still works) | S3 and S7 start tests there, never on a running clock |
| S6 | `/api/history` (R26), `/api/stats`, `/api/skill/{topic}`, `UI.sittingCard`, `?q=M1-3` on the report | S3, S5, S9 (words filter), S1 (recent activity links) |
| S8 | `compete.clock`, `twin_questions`, `finish_contest`, `state_extra`, `rate`, `challenge_streak`, `rank_snapshot`, `/api/contest/daily`, `UI.board`, `UI.level` | S4 and S5 (contest sittings, R28), F4 (`record` rating hook), S3 (challenge card), S1 (snapshot, Boards block) |
| S10 | `/api/review/counts`, `/api/review/item`, `/api/review/family`, flag endpoints (`POST /api/session/{sid}/flag`, `POST /api/flags`) | S3 (Review card), S1 (Saved & in progress), F3 (`UI.review` pane, `UI.history`), S4 and S5 (Mark), S6 (flagged in results reads `flags`) |
### 2.13 Acceptance checks changed by the resolutions
| section | the check says | read it as | why |
| 3.4 Tests | `POST /api/session/{finished}/share`, `GET /api/shared/{code}` | `POST /api/sets {session}`, `GET /api/sets/{code}` | R18(c) |
| 3.4 Tests | a report row `WHERE id='…'`; "the 21st report in a day gets 429" | integer ids; the 11th report within an hour gets 429 | R17 |
| 3.4 Tests | "Save these as my defaults updates GET /api/me profile.test_prefs" | updates the `test_*` keys of `profile.prefs` | R11 |
