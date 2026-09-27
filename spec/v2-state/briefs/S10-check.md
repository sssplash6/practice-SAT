# Check brief for S10: Review pages

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


## Task entry

**S10 · Review** (wave 2, port 8030). Builds Part 3.9 in full (components from F3, traps
logic from F4, sets from F6), R2, R5's endpoints. Owns `web/review/**`, `web/mistakes/**`,
`server/api_review.py`, `server/checks/s10.py`.
State: not started.


## The section's acceptance list

### 3.9.8 Acceptance checks

1. curl -s -H 'X-Learner: a:v2revacc1' localhost:8000/api/review/counts returns all zeros for a new code, /api/me has review.open == 0, and /review/ shows the new-student panel with 'Start practice'.
2. After a drill in which an MC question is answered wrong, /api/review/redo has one item with an integer id, kind 'misconception', owed 2, status 'open', a seed and a given_label; /api/review/history has a row with result 'wrong', mistake set and ms set.
3. Two misses on context.container_percent seeds whose reasons differ only in the percent give ONE redo item with hits 2 (its norm contains '#'), and its label is the concrete text of the second miss.
4. A miss whose option is 'near-miss arithmetic slip' gives kind 'slip' with the label 'Arithmetic slip'.
5. A half-fixed trap (owed 1) makes redo_questions count 1 for its template, and POST /api/drill {list:'redo', ids:[that id]} returns total 1.
6. Save a question, answer it right, start {list:'saved', exact:true} and answer it right again: that attempts row has repeat=1, the trap's owed is unchanged, /api/map mastery for the topic is unchanged, and History shows result 'repeat'.
7. Answer a practice question right with flagged:true: /api/review/redo gains an item with kind 'unsure' and owed 1, and one clean fresh answer on that template moves it to /api/review/fixed.
8. Live test: POST /api/session/{sid}/flag {question_id, on:true}; GET /api/session/{sid} includes it in flags; after module 1 → 2 the module-1 flag is still in flags; after finish, results.review[].flagged is true for it and /api/review/marked lists it with during:true.
9. The same flag call with another learner's X-Learner returns 403.
10. Two sittings of the same diagnostic form with different questions flagged: each report's flagged count matches only its own flags.
11. GET /api/review/item for the (template, seed) of an unanswered daily-challenge question returns 404; the same call under another learner's code for an item this learner answered returns 404; GET /api/review/family?session=<live test>&question_id=… returns 409.
12. POST /api/shares with today's challenge (template, seed) returns 409; a share of an answered practice item returns an id, and POST /api/drill {list:'share', ids:id, exact:true} under a second code serves that exact stem.
13. POST /api/mistakes/dismiss moves the item from redo to fixed with closed_how 'dismissed'; /restore brings it back with relapses unchanged; a later miss on a dismissed trap reopens it with relapses unchanged.
14. GET /api/review/history?limit=50, then ?cursor=<next>, returns only ids smaller than the first page's smallest id; summary.answers equals counts.answers when no filter is set.
15. A test answer saved twice with ms 3000 and 2000 files attempts.ms 5000 for that question after finish.
16. POST /api/me/carry moves flags rows to the new code (GET /api/review/marked lists them under the new code and returns an empty list under the old one).
17. Browser: http://localhost:8000/mistakes/ lands on /review/?tab=redo; clicking the Saved tab changes the URL to tab=saved, and Back returns to Redo.
18. Browser 1280: clicking a redo row opens the pane on the right with the exact missed question, the pick and the key marked, a misconception line under every wrong option, the skill and difficulty visible without opening Details, and pips; 'Fresh one like this' answers inline, and a clean answer fills one pip without a reload.
19. Browser 1280: Hide answers hides the key and rationale, stays on after Next and after a reload, and Check re-answers and files a Repeat.
20. Browser 1280: History with Group by = Sitting shows sitting headers with 'Again, exactly'; selecting 3 rows and pressing Fresh versions starts a 3-question set on those templates with unseen stems.
21. Browser 390: document.documentElement.scrollWidth <= 390 on every tab; a row tap opens a full-screen dialog that both Esc and the Back button close; the action bar sits above the tab bar, its summary shows the chosen Level, and the last row is not covered.
22. Browser 390: the Filters sheet with Topic = Circles shows only circle rows, and the tab count reads 'n of 25'; Clear filters restores all rows.
23. Browser: in the practice session, the History button shows a count before answering and opens the modal with earlier attempts on that kind of question across seeds, with Open disabled until answered; Esc closes it and returns focus to the button.
24. Browser: in /test/, the Save and History strip buttons are present but aria-disabled while the test is live.
25. Browser: the report page shows a 'Flagged (n)' filter after a test with a flagged question, and the flagged cell carries the corner flag and a legend entry.
26. Browser: pressing S while typing in a grid-in input or a note textarea types 's' and does not toggle Save.
27. PYTHONPATH=. python3 server/test_flow.py passes with the new asserts.


## The upgrades' acceptance items (spec/v2-upgrades/review.md)

**Acceptance.**
1. A learner (`a:v2revreview1`) with no timed answers and `review_minutes` 10, seeded with one
   trap fixed 4 days ago (R9 due), one relapsed trap, one open trap whose latest miss has
   `conf='sure'`, one trap owed 1, one saved question saved 2 days ago with no answer since, and
   20 more open traps: `GET /api/review/due` has `items[0..4].kind ==
   ['check','relapsed','sure','half','saved']`, `cap == 6`, `total == 6` and `waiting` equal to
   the frozen keys minus 6.
2. `POST /api/drill {source:'due', box:10}` → `GET /api/drill/{id}` has `cfg.hide_skill ==
   true` and `cfg.box == 10`. Its first 5 served templates equal those five items' templates as a
   set (in any order), and no two consecutive served questions share a topic.
3. Answer the check-in item's question: a second `GET /api/review/due` shows it in the same
   position with `done == true`, `left` one lower and `total` unchanged. `GET /api/me` has
   `review.due_left == left`, and `/api/today.due`'s Review row has the same `left`.
4. Answer every item on today's list, missing two of them: `left == 0`, `done == cap` and
   `waiting > 0`, and `/review/` at 1280 shows Done for today. Then open a new trap in an
   ordinary practice set: today's `items` are unchanged, and the next local day's list includes
   it.
5. `review_minutes` 20 → `cap == 12`; 5 → `cap == 3`; 0 → `waiting == 0`. With nothing open and
   nothing due: `items == []`, and `/review/` at 1280 shows the pill "Keep going · 10 min".
6. `POST /api/review/snooze {key}` for one item: `left` and `/api/me.review.due_left` drop by one.
   In a second browser context with the same code, the row shows `Not today · Undo`, the badge
   reads the lower number, and U1's queue leaves the item out. `{key, undo:true}` restores it.
7. Browser 390: six tab segments fit with `document.documentElement.scrollWidth === 390`, each
   segment at least 44 px tall; the Due tab is selected when `left > 0`; the sidebar meta at 1280
   reads `6 due · 25 open` with no `title` tooltip needed to see either number.
8. `POST /api/drill/preview {source:'due', box:10, drop:['due:check:<t>']}` returns no block
   with that key, and its minutes stay within 10 ± 3.
9. `POST /api/drill {source:'warmup', count:5}` serves the first 5 items of today's list (as a
   set); `/api/today.due` has one Review row and no separate Warm-up row.


**Acceptance.**
1. A learner finishes a module with 3 wrong MC answers: `GET /api/review/redo?lens=new` lists 3
   items with `new == true`, and `/api/review/counts.new == 3`.
2. `POST /api/review/walk {session: <that sid>}` → `n == 3`; `GET /api/drill/{id}` has
   `cfg.inline == true` and `cfg.walk.items[0].try == true`. `/api/history` does not list it.
3. `POST /api/review/why {attempt_id, diag: <that attempt's norm>}` → `called == true`; a second
   call with another `diag` leaves `attempts.diag` unchanged. The item is no longer New.
4. `POST /api/review/why {attempt_id, diag:'misread'}` on another attempt sets `miss_kind ==
   'misread'`, and `progress.causes` counts it under `misread`.
5. Browser 1280: the walk's step 2 shows between 3 and 6 choices and no letters; pressing `2`
   selects the second; Enter reveals the key. A reload returns to the same mistake and step.
6. The Try again answer files `attempts.repeat == 1`; the trap's `owed` is unchanged.
7. A practice miss with instant feedback has `revealed_at` set at filing, and its walk item has
   `try == false`. A section miss opened in the report at 1280 shows What happened? first; after
   Just show me its `revealed_at` is set, and a walk over that sitting skips Try again for it.
8. Leave an item blank in a finished module, save it, re-serve it exactly (`{pool:'saved',
   exact:true}`) and answer it right: `attempts.repeat == 1`, and the trap's `owed` and
   `/api/map` topic mastery are unchanged. A fresh twin of it answered right has `repeat == 0`.
9. A module with 2 misses and 3 blanks: the walk has `n == 5` with 3 items `blank == true`;
   each blank starts at step 2 with the three blank choices.


**Acceptance.**
1. Save (t, s) on day 0: `saved_due` lists it on day 1 with `k == 0`. One clean right on a fresh
   t seed on day 1 → due on day 4. A second clean right 10 h later does not raise `k`.
2. Four counted clean rights on four days → the row is `learned: true` and never in `due`.
3. A wrong answer on t after `k == 2` → due tomorrow with `k == 0`, and a trap is open on t.
4. `POST /api/drill {pool:'saved', ids:[[t, s]], exact:false, each:1}` serves t with a seed
   other than s; after answering, the feedback has `saved_note` when a note exists.
5. `PUT /api/me {prefs:{saved_spaced:false}}` → `saved_due` returns `[]` and U1's queue has no
   `saved` row.
6. Browser: Save, then tap `Got lucky` in the toast → `/api/review/redo?kind=unsure` gains the
   item.
7. Browser 1280, Saved with 4 due: select 6 rows that are not due. The action bar shows
   **Fresh versions of selected · 6** as the primary and **Practise due · 4** beside it; with
   `2 each` the started drill serves 12 questions, none with a saved seed.

---


**Acceptance.**
1. The U1 acceptance learner (`gains.skills.probability.gain == 20`, 10 wrong first tries in 60
   days, 3 on one open trap): `/api/review/redo` has that trap with `pts == 6`, and its group
   `pts >= 6`.
2. A learner with 12 answers: every `pts` is null, and the AT STAKE tile reads "after 30
   answers".
3. `sort=worth` returns items in non-increasing `pts`.
4. Closing a trap worth 6: `select pts from trap_log where event='fixed' order by id desc
   limit 1` is 6, and `/api/review/fixed.stats.recovered_month >= 6`.


**Acceptance.**
1. Three wrong answers with `conf='sure'` and two right with `conf='unsure'`: `matrix.sure.wrong
   == 3`, `matrix.unsure.right == 2`, and each of the three traps has `blind == true`.
2. A wrong answer with `conf` null, `guess = 0`, `ms` under 0.6 × the tier median and at least
   25% of its budget (50 s on a medium question) is counted in `matrix.sure.assumed` and flagged
   `blind`; the pane reads `Fast answer · assumed sure`. A 20-second untagged miss on a medium
   question (budget 95 s) is in History's `result=rushed`, has `blind == false`, and is not in
   Due's `sure` kind.
3. A test with 4 flags, 2 of them shown only once: `flags.never == 2`; `GET /api/review/marked`
   rows for those carry `visits == 1`.
4. `changes.net` equals `wr − rw` over tests in range, and `pts == round(net ×
   per_question / 5) × 5`.
5. Browser: clicking the Sure × Wrong cell lands on History with `conf=sure&result=wrong` in the
   URL and only wrong rows.
6. A learner with 5 topics that each qualify for a reading: `readings` has 5 entries, ordered by
   points, and the card shows all 5.


**Acceptance.**
1. A learner with 2 misses corrected to `misread` and 3 traps: the bar's `misread == 2`, and
   `/api/review/redo?cause=misread` returns exactly those traps.
2. `POST /api/review/why {attempt_id, guess:true}` sets `attempts.guess == 1`; the trap is no
   longer `blind`.
3. `The label is wrong` creates a `reports` row with `category == 'Wrong mistake label'` and the
   attempt's template and seed.
4. Browser: clicking the Slips segment shows a row whose button body has `feedback:'instant'`
   and those templates.


**Acceptance.**
1. A learner with 3 traps tagging `whole_part` over 2 topics: `?group=habit` returns one group
   `whole_part` with 3 items, and its button body is `{source:'habit', habit:'whole_part',
   count:8}`.
2. A trap norm on offer and not chosen in 2 other templates (P6 rows): its item has
   `dodged_elsewhere == 2`.
3. `?habit=sign` returns only traps whose norm maps to `sign`.

---

**Acceptance.**
1. A trap missed, repaired, answered clean and fixed: `select event from trap_log where
   template='<t>' order by id` gives `open, miss, pip, pip, fixed` (the miss that opened it
   also logs `miss`).
2. `POST /api/me/carry` moves `trap_log` rows to the new code, and `/api/review/item?…` for the
   carried trap returns the same story length.
3. An attempt with the key struck: `path.struck` contains the key's index, and the pane shows
   "You crossed out the right answer".
4. `GET /api/review/family?template=<t>` for a learner whose last two misses on t share a norm
   has `verdict.kind == 'same_trap'`; `&norm=<n>` returns only rows with that norm.
5. Browser: clicking a timeline node loads that exact stem in the pane, and Back restores the
   timeline.
6. A retry-mode practice answer wrong on try 1 and right on try 2: its History item has
   `result == 'mixed'` and `tries.length == 2` with `tries[1].correct == true`; it is in
   `result=mixed`; `summary.mixed == 1`; the attempts row is still wrong (the first try counts).
   Browser: the row's `2 tries` toggle shows both picks with their times.


**Acceptance.**
1. A learner with 5 `open` and 3 `fixed` events this week and 2 `relapse`: this week's row has
   `opened == 5`, `fixed == 3`, `relapsed == 2`, and `open_end` equals the open count.
2. With net fixes ≤ 0 over 4 weeks: `forecast.zero_on == null` and no forecast line renders.
3. At 390, the chart shows 8 weeks and `scrollWidth === 390`; its hidden table has 8 rows.


**Acceptance.**
1. A trap fixed today: `/api/review/fixed` has it with `held == 0` and `checks == 0`; the row
   reads "Not checked yet". After one clean check-in: `held == 1`.
2. A trap on a two-tier template fixed with clean rights only at medium: `tiers_proven ==
   ['medium']`, `tiers_available == ['medium','hard']`; its check-in drill serves a medium seed.
   After a clean hard right, the check-in serves hard.
3. `counts.held + counts.unchecked == counts.fixed` (dismissed excluded).


**Acceptance.**
1. A trap with 3 hits: `/api/review/redo` item `status == 'stuck'`; its row button posts the T4
   body with `templates == [t]`.
2. `GET /api/types/<t>/example?want=<norm>` for a template and norm that appear in its survey
   returns `seed >= 900000` and a `trap_index` whose option reason normalises to the norm.
3. Browser 1280: See one solved opens a sheet with two columns and exactly one outlined option in
   the right one; Now you closes it and shows a new question in the pane with a different stem.
4. `server/checks/s10.py` computes the share of open traps on templates with P1 steps and fails
   below 80%; `tools/steps_queue.py` lists templates without steps in non-increasing demand.
5. The pane for a miss on a template without steps shows one value line per option plus the key's
   value line, and no Steps tab.


**Acceptance.**
1. A learner with a right answer at 150 s on a medium template with no crowd budget:
   `/api/review/history?result=slow` includes it; at 50 s it does not.
2. A wrong answer at 20 s on a medium question (budget 95 s) is in `result=rushed`.
3. `summary.slow.over_ms` equals the sum of `ms − budget_ms` over the slow rows.

---


**Acceptance.**
1. After a rematch of sid, `/api/review/history?group=sitting` returns sid with `children:
   [<rematch id>]` and `best` set; the child is not a top-level sitting.
2. `POST /api/drill {rematch: sid, scope:'weak'}` serves one fresh slot per first-try miss and
   per right answer over its budget, in the original order.
3. Browser: a sitting header shows one cell per question, blanks included and dashed; clicking
   cell 4 opens question 4 in the pane.
4. `POST /api/drill {rematch: sid, scope:'misses', until_fixed:true}` for a sitting with 2 misses:
   a slot answered wrong is served again on a new seed until its trap's `owed == 0` or 3 rounds
   pass. `POST /api/drill {from_session: sid}` creates the same body (`cfg.rematch == sid`,
   `cfg.scope == 'misses'`, `cfg.until_fixed == true`).
5. Browser 1280: the sitting header and the report each show exactly two miss actions, "Walk
   these misses · name each, then prove it" and "Fix on new numbers · n q · Then → Now";
   "Again, exactly (tests memory)" appears only in the overflow.
6. A finished module with 3 blanks: its sitting has `blanks.length == 3` and 3 `blank` cells; a
   blank cell opens its item with the key shown; `{rematch: sid, scope:'blanks'}` serves 3
   questions on unseen seeds, and right answers file `repeat == 0`.
7. A practice sitting with 12 answers that opened 2 traps (their only misses) and filled a pip on
   a third: after `/void`, every attempt of the session has `void == 'discarded'`, the 2 traps
   are in no Review list or count, the third's `owed` is one higher, `/api/map` mastery for the
   topic equals its value before the sitting, and History lists the 12 rows with `Discarded`.
   `/unvoid` restores the counts, the traps and the mastery exactly. `/void` on a challenge
   sitting → 409.

---


**Acceptance.**
1. Browser 1280, a list of 25: the pane header has 25 cells; clicking the 10th opens row 10; `U`
   from row 1 after opening rows 1–3 goes to row 4.
2. After opening row 5, the network log shows item requests for rows 3, 4, 6 and 7; moving to row
   6 makes no new item request.
3. Fresh one like this: the stem element is the same node before and after (not re-created), and
   at least one `mark.chg` exists when the numbers differ.
4. Browser 390: a left swipe on the pane moves to the next row; a long-press on a row shows the
   action bar with `1 selected`.
5. On Redo, every strip cell carries a status (`data-status` in `open|half|relapsed|stuck|sure`)
   drawn with pips; on Fixed, a check-in state; on History, an answer result. On Redo, `N` from
   row 1 after opening rows 1–3 goes to row 4.


**Acceptance.**
1. Marked with Volume 10 over 14 rows: the started drill has `count == 10`, taken in the tab's
   sort order. Volume 40 over 60 rows → `count == 40`; the number field with 17 → `count == 17`.
2. A one-tier medium template with a same-label hard sibling: `{pool:'redo', ids:[trap], level:
   'harder'}` serves the sibling at hard.
3. `?levels=4,5` returns only rows whose (template, tier) rates L4 or L5.
4. Browser 1280: the Redo, Due and Fixed bars have no Feedback control and read `Instant ·
   fixing set`; the drills they start have `feedback == 'instant'`. Marked's bar with At the end
   starts a drill with `feedback == 'end'`.
5. The Due bar has no Volume control; after the header seg changes from 10 to 20, the bar's
   summary reads `12 questions · 20 min`.
6. After `tools/seed_ratings.py`, each of L1–L7 holds at least 5% of (template, tier) types, and
   running it twice leaves `item_ratings` unchanged.


**Acceptance.**
1. A new code at 1280: `/review/` shows one row with the `Example` tag and a Try one now
   question. Answering it wrong makes `/api/review/redo` return one item, and the list shows it
   without a reload.
2. The example row's pane shows a reason under every wrong option and files no attempt.

---


**Acceptance.**
1. `POST /api/sets {kind:'items', items:[[t, s]], cfg:{context:true}}` for an item the sharer
   missed: `GET /api/sets/{code}` has no stem and no context; after a second learner answers
   through the landing, the landing's context has `pick` and `mistake` equal to the sharer's.
2. The same call with `note:false` never returns the note.
3. A twin share of 3 missed items: each taker's served items carry an option whose norm equals
   the sharer's picked norm on that item (when a seed within 40 has it).
4. `/share/?t=<token>` shows the Mistakes block with the same open count as `/api/review/counts`.


**Acceptance.**
1. Print worksheet from Saved with 3 selected and `each:2` → a drill with 6 questions,
   `cfg.feedback == 'end'`, `source == 'worksheet'`, not finished.
2. Submitting the answer sheet with one wrong MC answer files 6 attempts (`select count(*) from
   attempts where session='<sid>'`), finishes the set, and opens one trap.
3. `/review/` shows the waiting-worksheet line before submitting and not after.
4. The print view of a worksheet set has no answer-key page. Print the key now, then submit: every
   attempt of the set has `repeat == 1`, and no trap's `owed` falls. Without printing the key,
   the same submission files `repeat == 0` rights. After Submit, Print the key opens the key page
   and leaves the filed attempts unchanged.


**Acceptance.**
1. `GET /api/review/trapsheet` returns ≤ 10 entries, each example `seed >= 900000`, habits first;
   `GET /api/plan/{id}/trapsheet` for the same learner returns the same template list in the same
   order.
2. `POST /api/notes {attempt_id, scope:'type', note:'check the sign'}` stores a `notes` row with
   `seed == -1` and the attempt's template; another learner's attempt id → 404.
3. A trap closed in the pane shows the rule prompt once; closing another trap on the same
   template with a rule already written shows no prompt.
4. A learner with `exam_date` 5 days away sees the Exam week card; 9 days away, no card.
5. `/review/print.html?sheet=log` lists one row per open trap, and `@media print` hides the shell.

---
## 3. Spec overrides


## Contracts and amended checks

| # | topic | what disagreed | decision | owner |
| R1 | Navigation | Shell keeps 5 phone tabs; Compete, Words and Review each add a 6th tab | **Desktop sidebar (Shell §2.2), final items.** STUDY: Today, Practice, **Review** (badge: open mistakes; replaces "Mistakes"), **Words**, Tests, Plan, Class (only when in or teaching one). PROGRESS: Results, **Compete** (replaces "Challenge"). **Phone: 5 tabs stay** Today · Practice · Tests · Plan · Results. Review, Words, Compete, Class, Profile, Settings and Help sit in the avatar menu sheet, each at most two taps away; the phone top bar's count chip is Review's. The 6-tab bars in Compete §2, Words §1 and Review §1 are not built. G-keys: G M Review, G W Words, G C Compete (see §2.8). Nav metas: Review "● 14"; Words "12 due"; Compete as Shell's Challenge meta (New / Resume / #4). | F2 |
| R2 | Mistakes page | Shell and Today link `/mistakes/`; Review replaces it | `/review/` is the page (Review spec). `/mistakes/` redirects (307, served by `api_review.py`) to `/review/?tab=redo`, keeping the query. Every "Mistakes" reference in other specs means Review. Mistakes logged from outside (Shell §2.7) appear in Review's Redo tab with a "Logged by you · Bluebook" chip and their note. | S10 |
| R5 | Mark vs Save | QBank merges marking into saving (as TopTierPrep does); Review keeps them apart | **Two things everywhere** (Review model). *Mark for review* = a flag on one question in one sitting (`flags` table, flag icon, per sitting). *Save* = keep a question for good (`saved` table, bookmark icon). QBank's "rename Saved to Marked for review" is not done; its builder gets two pools, Marked and Saved. QBank's "a right replay removes it from Marked" is not built; Review has Unmark / Unsave with Undo. The Report button's icon is a speech bubble with "!", never a flag. | F4 (tables), S10 (endpoints) |
| R6 | Highlights and notes | QBank stores notes per (template, seed); Tests stores marks per sitting in `qstate`; Review stores a note on `saved` | **One store:** `notes(learner, template, seed, note ≤1000, marks JSON ≤50)`. Written with `POST /api/notes {session, question_id, note?, marks?}` from any sitting kind; the server resolves (template, seed) and never trusts the client for them. Mark styles are Tests' seven: highlight, strong, underline, dashed, dotted, box, strike (each mark may carry a note ≤500). A saved question's note (Review §5) is the same note. Notes come back wherever that exact question appears: replay, retake, review, report, Saved. | F4 (`api_notes.py`), F3 (`UI.annotate`) |
| R7 | Per-question time, trail, strikes in tests | Report adds `sessions.times` and `sessions.trail`; Review adds `sessions.times`; Tests adds `sessions.qstate` | **One column `sessions.qstate`** (JSON): per qid `{ms, struck, conf, trail, first, changes}` and `_session {away_ms, away_n, late}`. Flags are not in it (R5). The runner sends `ms` (dwell delta) and `made_left` with each answer save and other deltas with `POST /api/session/{sid}/state`. `record_paper` passes `qstate[qid].ms` into `attempts.ms`, so tests count as study time and per-question time. Report's `/flag` and `/time` endpoints are served by Review (flags) and Tests (`/state`). | F4 (column, record_paper), S5 (endpoints) |
| R8 | Attempts columns and what counts | Review adds norm/repeat/repair/flagged/stem; QBank guess; Shell disputed; Compete sms/void | **One set of new `attempts` columns:** `norm, repeat, repair, flagged, guess, disputed, sms, void, stem`. Mastery, accuracy, boards and ranks leave out rows with `repeat=1`, `disputed=1` or `void` set; a right answer with `guess=1` counts half. Study time and question counts keep every row. A **clean answer** (closes a mistake, counts as a check-in) is right, not a repeat, not flagged and not a guess. `progress.record` computes `repeat` itself for every caller. | F4 |
| R9 | Traps and check-ins | Review rebuilds traps (id, norm, kinds, relapses) with check-ins at 7/21 days; Plan wants rechecks at 3/10/30 via stage/due; Shell adds source/note/origin | **One `traps` table:** Review's rebuild (integer `id`, `norm`, `reason` = latest concrete text, `closed_how`, `relapses`, `seed`, `session`) plus Shell's `source` ('outside'), `note`, `origin`, plus **one check-in schedule: 3, 10 and 30 days after fixing** (Plan's), stored as `due` + `checks` (0 to 3). A miss on a due check reopens it as Relapsed. Plan's Rechecks task is the drill pool `checks` (R10); Review's "Check these now" and "CHECK-INS DUE" use the same. Kinds: misconception, gridin (named when the template has `spr_mistakes`), slip, unsure. | F4 |
| R10 | Drill body | Nine sections add their own fields to `POST /api/drill` | **One body contract (§2.6)**, validated in one place and built by F5. Section field names map onto it (table in §2.6). Fields that need another section's data stay on `POST /api/drill` and are resolved by the owner's module through a registry: `like` (S3, `daily.resolve_drill`), `word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2, `classes.resolve_drill`); contests are started by S8's own routes. `list` is accepted as an alias of `pool`, so Review's bodies work unchanged. | F5 |
| R15 | Goals and SAT dates | Target/exam date edited on Today, Me and Plan; R&W fields; three copies of SAT_DATES | `target, exam_date, current, minutes, days, tests, focus, rw_now, rw_target` live on `learners`; the active plan mirrors them both ways (Plan §5, `plan.mirror()`), so one edit shows everywhere. Dashboard's `plan_started` is `plans.start`. Upcoming official dates: one constant in `server/satdates.py`, served in `/api/shell.dates`, read by the date pickers on Today, Me, Plan and Compete's seasons. Past dates are never offered. A new `exam_date` must be today or later in the learner's zone. | F4 |
| R17 | Report a problem | Shell (10 images downscaled, disputes, admin), QBank (3 × 5 MB BLOBs), Tests (R-#### ids, tools), Report (3 screenshots), Words (10 images) | **One system:** Shell §2.10 and §10 are canonical: one modal `UI.report(ctx)`, up to 10 images (PNG, JPEG, WebP, GIF), stills downscaled in the browser to 2000px, 10 MB server cap, files on disk under `server/reports/{id}/` (git-ignored), bounded disputes (5 open), Your reports with replies in Settings, `/admin/reports` behind `SATF_ADMIN_TOKEN`. Categories per context are the union: Shell's lists, plus Tests' "More than one right answer" and "No right answer", plus Words' "Wrong or unclear definition" (word context). Mid-test reports never show marking and hide key disputes. Rate limit: 10 an hour and 20 a day per learner (429). Ids are integers. `tools/reports.py` is an optional CLI over the same table. | F6 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
| R19 | Access to keys and re-serving | Review defines `access()`; others re-serve items ad hoc | **One rule, `deps.access(learner, template, seed)` → `reveal` \| `kept` \| None** (Review §server). Everything that returns a key or re-serves an exact (template, seed) goes through it: review endpoints, sets, worksheets, the report, the challenge review, permalinks, Words examples. Live-test items and unanswered or same-day challenge items never leak. The permalink `/practice/session/?q=TEMPLATE:SEED` (QBank; Shell's `/q/` is the same route) serves any catalogue item that is not in today's challenge as a fresh one-question drill; the key shows after answering, as always. | F4 |
| R20 | Status colours and glyphs | Report flips nothing; QBank uses wash for correct; Compete/Review differ | **The practice session's semantics, with glyphs everywhere** (§2.3): right = orange, wrong = graphite, plus Mixed (right on a retry) and Repaired (right on the repair after a miss) as two states, skipped, blank, voided, repeat, not reached, answered (exam), flagged, saved, has note, current. One legend component. | F1 |
| R22 | Keyboard | QBank uses C for calculator and S for skip; Review S for save; clashes with choosing C | **One registry `UI.keys` (F2) and one map (§2.8).** Calculator G, reference F, save B, skip S, history Y, highlights L, confidence K. Shortcuts are ignored while typing (Enter and Esc aside) and when `prefs.keys` is off. | F2, F3 |
| R23 | Review player, pane and history | Report's `UI.review` player, Review's `UI.questionReview` pane, QBank's review sheet | **One component `UI.review(host, items, opts)`** with `mode: 'dialog'` (Report §1.13 layout) and `mode: 'pane'` (Review §8), plus **`UI.history`** (Review §9 attempt history for the whole question type), used by the session, the report, Review and the challenge review. Report's "Try one like this" tile and Review's inline mini-session are the same inline drill. | F3 |
| R24 | Drills that are not sittings | twin, try, word-example, review pane, spot, quick each have their own list rule | `cfg.inline = true` for sources `twin, try, word-example, review, spot`: never listed as a sitting, never in history, In progress or Resume; their answers file normally (a twin counts on its parent). `quick` sittings are listed in history as "Quick questions", never offered as Resume, and deleted when finished with 0 answers. Any set finished with 0 answered is never listed. | F5 (flag), S6 (history), S4 (drill list) |
| R30 | Today's cards | Today has a Mistakes card; Review wants a Review card; Words wants a Words tile | Today's `#mist` card **is** the Review card: Review's counts (open, half fixed, check-ins due, marked) plus Today's top 5, Fix and Try one now. A **Words tile** joins the grid: desktop `plan ×8 · words ×4` (the plan card spans 8, the Words tile 4); phone after the challenge card. | S3 |
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
| F5 | the drill body; `GET /api/types`, `GET /api/types/{t}/example`, `POST /api/mistakes/log`; `drill.levels()`, `blueprint.kinds()` | F2 (palette, Log a mistake), S2 (assignment type search), S3, S4, S7, S8, S9, S10 |
| F6 | `UI.report`, `POST /api/report`, `GET /api/reports`; `sets` endpoints and `/s/` | every page with a question; S4, S5, S10 (share); S6 (peers) |
| S10 | `/api/review/counts`, `/api/review/item`, `/api/review/family`, flag endpoints (`POST /api/session/{sid}/flag`, `POST /api/flags`) | S3 (Review card), S1 (Saved & in progress), F3 (`UI.review` pane, `UI.history`), S4 and S5 (Mark), S6 (flagged in results reads `flags`) |
### 2.13 Acceptance checks changed by the resolutions
| section | the check says | read it as | why |
| 3.9 Review | `POST /api/shares …`, `{list:'share', ids:id}` | `POST /api/sets …`; `list:'share'` stays valid as an alias of `pool:'set'` | R18(c), R10 |
