# Check brief for S3: Today pages

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

7. **A calm, quiet interface: show only what the student needs (2026-09-27).** The user: "lets show students stuff that they
   only really indeed need to know ... make it easy and less tiring for eyes. convinience matters". Every page follows this:
   - Show what the student needs to decide or act on now. Hide zeros and defaults ("0 open", "Not practised", "0 of 107
     types ready", "Easy Medium Hard" when all are on); show a count only when it says something.
   - One number per idea, said once. Never repeat a fact in two places on the same screen (a selection shown by checkmarks is
     not also listed as chips; "Not started" is not beside "Not practised").
   - Details on demand, one tap away: expand a row, hover or focus for a tooltip, or open a Details / Settings sheet. Settings
     summaries collapse into one control; explanatory sentences become tooltips or help, not permanent text.
   - Easy on the eyes: generous spacing, few text sizes and weights, the primary fact in normal ink, secondary facts muted, mono
     only for numbers that matter, orange only for the one action or state that needs attention.
   - No feature is removed (this is not minimalism; decision 4 still holds): everything stays reachable and fast to use.


## Task entry

**S3 · Today** (wave 2, port 8023). Builds Part 3.2 in full, R27 (QOTD), R30 (Review card,
Words tile), and the Today items of Review §10, Words §11 and Compete §9. Owns
`web/index.html`, `server/api_today.py` (`/api/today`, `/api/calendar`, `/api/scores`,
`/api/qotd`, the like-drill route), `server/daily.py`, `server/checks/s3.py`.
State: not started.


## The section's acceptance list

### 3.2.8 Acceptance checks

1. curl -s -H 'X-Learner: a:v2revacc1' -H 'X-Tz: 0' localhost:8000/api/today | jq '.study, .days.best, .scores, .open, .traps.open, .week.this' shows zeros, 0, [], {drill:null, drills:0, test:null}, 0 and zeroed week figures for a fresh code.
2. curl -s -H 'X-Tz: 0' localhost:8000/api/qotd | jq '.slots|map(.slot, .question.type)' gives ["mcq","mcq","spr","spr"]. The same call as a:v2revacc2 returns identical stems. jq '[.slots[].question|has("answer","rationale","reasons","key")]|flatten|any' gives false.
3. POST /api/qotd {answer:'999', day:<today>, slot:'spr', ms:40000} as a:v2revacc1 returns correct:false with answer and crowd.answered ≥ 1. A second identical POST returns the same given. GET /api/today then shows study.today ≥ 1, and /api/me days.streak equals /api/today days.streak.
4. POST /api/qotd {answer:0, day:<today-3>, slot:'mcq'} returns late:true. GET /api/qotd?day=<today-3> shows mine set while crowd.answered is unchanged, and .streak does not count that day.
5. POST /api/qotd with day=<tomorrow> gives 422. GET /api/qotd?day=<today-40> gives 422.
6. POST /api/drill {like:{day:<today>, slot:'mcq'}} before answering gives 409. After answering, count:5 gives a session whose served items in sqlite (sessions.questions) are all the QOTD's template and none has its seed.
7. With 2 open traps on different templates in one topic, POST /api/drill {mistakes:true, templates:[t1]} serves only t1 (twice).
8. After POST /api/mock/new {full:false} and /api/session/{id}/finish: GET /api/today .study.today includes the elapsed minutes; GET /api/tests/recent .recent[0].modules[0].wrong + blank equals the incorrect positions in /api/session/{id}/results .review; GET /api/calendar?month=<YYYY-MM> lists the sitting under today.
9. A finished mock's tests/recent modules[1] positions start at 1 and modules[0].asked equals len(module 1) from the results review.
10. A diagnostic finished with no signup: /api/today .scores excludes it, tests/recent shows gated:true without estimate, and POST /api/drill {from_session} gives 403.
11. GET /api/calendar?month=2026-13 gives 422. GET /api/calendar?month=2026-09 has 30 entries in days.
12. PUT /api/me {exam_date:'2020-01-01'} gives 422. PUT /api/me {exam_date:'2026-11-07', minutes:60, days:'1111100'} returns 200 with plan_started = today. PUT /api/me {rw_now:610, rw_target:700} returns 200, and profile carries both.
13. POST /api/scores {day:<today>, math:610, rw:600, source:'bluebook'} returns 201-ish with an id; GET lists it; DELETE removes it; as another learner, DELETE of that id gives 404.
14. POST /api/plan/mark {day:<today>, task:'practice', state:'skipped'} returns the mark; GET /api/today .plan_marks includes it; state:null removes it; a day before today − 13 gives 422.
15. shot.py a:v2revacc3 1280 … http://localhost:8000/ for a new code: every card shows its empty state with an action (Add your name, the Diagnostic link, Today list 0 of 3, When is your SAT?, No score yet with doors, No tests yet with doors, the Plan CTA). No page errors, and no card shows a bare dash.
16. At 1280 the two day's questions are side by side and both show their stems. At 390 they are tabs with status marks. At 390 the cards stack in the order hero, next, qotd, exam, score, mist, study, plan, chal, tests; document.documentElement.scrollWidth === 390; the last card clears the tab bar.
17. With a plan and a practice set of 5 answered out of 38: the Today list reads PLAN · 0 of 1 done with '5 of 38 questions', and the hero chip reads Plan · 0 of 1 done. After 38 answers the row shows a filled check and the header reads All done for today.
18. Plan rest day: Up next shows Rest day and an orange pill Practice anyway.
19. A timed module started and left: Up next shows Resume with the time left, counting down. With seconds_left 0 on module 1 of a section it shows Continue to module 2.
20. In the browser the SEC box changes within 1.1s, and with exam_date = today+10 at 07:00 local the DAYS box reads 10. With Playwright timezoneId 'Asia/Tashkent' at 00:30 local, the ringed calendar cell and the hero date are the local date.
21. Clicking Target ✎ opens dialog#targetSheet with Save disabled. Typing 650 enables Save; Save sends PUT /api/me {target:650}, and the score tick, gap line and plan stat row show 650 without a reload; /plan/ step 2 opens at 650. Esc closes without a request.
22. The exam trigger lists only official dates after today. Choosing Nov 7 updates the countdown, the hero chip and the plan line. Esc closes the popover and focus returns to the trigger.
23. MC day's question: the first tap only selects (no request in the network log); Check sends POST /api/qotd. After the reveal, every option row shows a percentage and each distractor shows its misconception line under it. 5 more like this opens /practice/session/?id=.
24. Start a drill from Up next, answer 2, return to / (pageshow): Up next shows Continue · 2 of N answered and links to the same session id.
25. Try one now opens dialog#tryOne with a question of the top trap's template. Answering it right fills one owed pip after Done.
26. Tapping a calendar day with activity shows 'Mon, Sep 21 · N min · N questions · N% right' and its sittings as links. A future plan day shows 'Planned · …'.
27. Aborting /api/challenge with Playwright route interception leaves every other card rendered, and the challenge card shows Couldn't load the challenge. with Retry. Aborting /api/today shows Couldn't load this. on next, mist, score, plan and exam, and one Retry repaints all of them.
28. PYTHONPATH=. python3 server/test_flow.py passes.


## The upgrades' acceptance items (spec/v2-upgrades/today.md)

**Acceptance.**
1. `curl -s -H 'X-Learner: a:v2revtoday1' -H 'X-Tz: 0' :PORT/api/today | jq '.next.preview.blocks
   | length > 0'` gives `true`, and `jq '[.next.preview.first.question | has("answer"),
   has("rationale"), has("reasons")] | any'` gives `false`. `sqlite3 server/v2.db "select count(*) from practice_seen where learner='a:v2revtoday1'"`
   is unchanged by the call.
2. Two GETs of `/api/today` on the same local day return the same `first.question.stem`.
3. `POST /api/drill {source:'next', box:15, first:{token, answer:0, ms:30000}}` returns an id
   whose `GET /api/drill/{id}` has 1 answered, `cfg.box == 15`, and question 1 equal to the
   previewed stem. Re-posting the same token gives 409 `preview_stale`.
4. `POST /api/drill/preview {source:'next', box:15, drop:['redo:<id>']}` has no block with
   that key, and its `minutes` is within 15 ± 3.
5. Playwright at 1280 on `/`: selecting option B sends no request; Check sends one
   `POST /api/drill`; the feedback shows in `#next`; Enter lands on `/practice/session/?id=`
   with "Question 2 of".
6. At 390, `#next` is the second card, the Check button's top is within 24 px of the last
   option's bottom, and `document.documentElement.scrollWidth === 390`.
7. On first paint at 1280, with nothing clicked, `#next` shows 10 size chips (5 Time, 5 Count),
   the `.clock` toggle and `More options`, and has no `Count instead` control. Picking Count 22
   leaves no Time chip selected and sends a preview with `count:22` and no `box`.
8. With today's minutes at or past the goal: the selected Time chip is 15 and the pill reads
   `Keep going · 15 min`. Timed on a 15-min box: `GET /api/drill/{id}` has `cfg.timed == true`
   and `cfg.minutes == 15`.


**Acceptance.**
1. A learner with a plan practice day and 2 check-ins due:
   `/api/today.due.rows|map(.kind)` starts `["plan","warmup"]`,
   and `minutes_left` equals the sum of the undone rows' `minutes`.
2. The plan's recheck task never appears as its own row (`map(.kind)` has one `warmup`).
3. Finishing the plan's practice session turns its row `done` without any tick, and the S4
   summary shows "Next due: Warm-up".
4. A practice task that opened 1 trap: its done row has `.result.opened == 1` and the Fix
   button's body has `still_open: true`.
5. Words module absent: no `words` row and no error; present with 12 due: the row reads
   "12 words due".
6. A plan with a custom task `R&W reading · 30 min` today: its row's status box is an
   `input[type=checkbox]` labelled "Mark as done". Ticking it sends one
   `PATCH /api/plan/{id}/tasks/{task_id}` with `{day:<today>, status:'done'}`. After it,
   `GET /api/plan` has that task at `status:'marked'`, /plan/ shows it done,
   `/api/today.study.today` rose by 30, and PLAN's `N of M` rose by 1. Undo sends
   `status:'todo'` and restores all three.
7. With the plan's qotd and challenge extras on: PLAN's header `N of M` equals
   `/api/today.plan.tasks_done` of `tasks_counted`, it equals /plan/'s day line, and no row of
   kind `qotd` or `challenge` sits in the PLAN group.


**Acceptance.**
1. A learner with one trap closed 3 days ago and two templates in different domains answered
   right once 3 days ago: `POST /api/drill {source:'warmup', count:5}` serves 3 questions,
   the check-in's template first, with no two consecutive questions from one domain.
2. `GET /api/drill/{id}` has `cfg.hide_skill == true`. At 1280 the session's skill line reads
   "Mixed warm-up" before Check and the real skill after.
3. An assert in `server/checks/f4.py`: k = 1…5 gives intervals 2, 5, 12, 30, 30 days, and a
   clean right 10 hours after the previous counted one doesn't raise k.
4. `/api/calendar?month=<this month>` future days carry `due.checks`, equal to the number of
   traps whose `due` is that day.


**Acceptance.**
1. `POST /api/drill {source:'learn', templates:['<t>'], example:true, count:3}` →
   `GET /api/drill/{id}` has `cfg.example.seed >= 900000` and 3 questions, none with a seed
   ≥ 900000.
2. After 3 answers, `select count(*) from attempts where session='<id>'` is 3.
3. An answer posted with `guess:true` stores `attempts.guess = 1`.
4. For a template that makes 2 tiers, question 3's difficulty is above question 1's.


**Acceptance.**
1. After a wrong MC day's question, the twin body returns a session with `cfg.inline == true`,
   the QOTD's template and a different seed. `/api/history` doesn't list it.
2. `{from_session: <unfinished module>, only:['q3'], source:'twin'}` → 409.
3. At 390, the sheet is a bottom sheet; Esc closes it and focus returns to the chip.
4. A right twin after a wrong day's question gives the slot mark the ↻ corner without a reload.

---


**Acceptance.**
1. U4's seeded learner (circles 10 answers at 30%, linear_functions 20 at 90%, 30 more
   elsewhere): `#gain` lists Circles above Linear functions.
2. A learner with 12 grid-in first tries at 25% and 30 MC at 70%: `insights.gains.extras` has
   a `spr` entry with `gain > 0`, and the card shows "Grid-in answers".
3. `By domain` shows 4 rows whose `answered` equals `/api/today.domains[].answered`.
4. With 12 answers the card reads "Answer 30 questions" and "12 of 30".
5. A learner with 40 answers: `#gain` renders 19 skill rows under the sub-headers `TOP 6` and
   `THE OTHER 13`, and has no `Show all` or other expand control. At 1280, after scrolling to
   the last row, the seg is still inside the viewport.
6. An assert in `server/checks/f4.py` for U7's seeded learner with 2 forecast blanks:
   `gains.extras[kind=='pace'].gain == insights.pace.pts_lost`, and `#gain`'s Pace row and
   `#pace`'s cost line print the same number.


**Acceptance.** In `server/checks/f4.py`, one seeded learner:
1. `scoring.entry_error` asserts in `server/checks/f4.py`:
   * `('.66','2/3')`, `('0.66','2/3')` and `('.67','2/3')` → `'early'`; `('1.2','1.25')` →
     `'early'`;
   * `('1 1/2','3/2')` → `'form'`;
   * `('455','460')`, `('154','150')`, `('.7','2/3')` and `('3','3.5')` → None;
   * `('.6667','2/3')` is right (`grid_equal`), so it is no miss at all.
   A seeded learner with a grid-in "0.66" to the key "2/3" has `by.entry == 1`, and one with
   "455" to "460" has `by.entry == 0`.
2. A timed module finished with 3 blanks → `by.clock == 3`.
3. A named wrong answer on a template the learner got right 4 of the previous 5 → trap, never
   slip. An unnamed grid-in miss on that template → slip. The named answer on a new template →
   trap. An unnamed grid-in miss answered in 3 minutes on a new template → gap. A fast named
   pick on an easy question → trap, and T9 lists the same attempt's trap.
4. `sum(by.values()) == total`, and each `items[cause]` has ids only of that learner.
5. On `/` at 1280, clicking the Entry segment shows a button whose drill body has
   `formats:['spr']`.


**Acceptance.**
1. U7's seeded learner (6 timed rights in circles at a median 150 s): `slow_right[0].topic ==
   'circles'`, and the button's body has `timing:'pace'`.
2. `runs_out_at` equals the first index where the cumulative strip ms passes 2,100,000 (an
   assert in `server/checks/f4.py`).
3. Asserts in `server/checks/f4.py`:
   * `pts_lost == estimate.time_cost(learner, pace)`, and it equals `gains.extras` pace gain;
   * with no blanks it is 0;
   * for a learner with ā = 1 at every tier, routed up, with 2 medium blanks a module, it
     equals `round5(S − _interpolate(F − 8/96))`.
4. A `source:'pace'` session with accuracy 20 points below the topic's usual → the summary
   contains "accuracy first", and `/api/today/insights.pace.guard` contains the topic.


**Acceptance.**
1. A learner with 3 traps whose reasons tag `whole_part` over 2 topics: `By habit` shows one
   row naming both skills; its button posts `{source:'habit', habit:'whole_part', count:8}`.
2. Five right answers in a `habit` session on 2 templates → `broken_at` is set; a later wrong
   pick in the family clears it.
3. A trap whose missed attempt was a medium question with `ms` under 0.6 × the medium median
   and `guess = 0` is in `blind` and is the first row. The same on an easy question is not in
   `blind`. A test miss with `qstate.conf == 'sure'` on an easy question is in `blind`.
4. For every id in `blind`, T7's per-attempt rule (`progress.cause_of`, which
   `progress.causes` maps over the window) gives its latest missed attempt `trap`.

---


**Acceptance.**
1. A learner with a module on Sep 21 and 40 practice answers since, at higher accuracy:
   `practice_delta.pts > 0` and the card shows "Practice since".
2. Sittings with midpoints 500 (Sep 1) and 560 (Sep 15), exam Nov 7, target 700: `verdict`
   starts "On pace" or "Behind", and the SVG has a cone path.
3. An outside official score dated after the exam date → `calibration` is non-null, and the
   line contains "We projected".
4. A learner with 9 geometry answers → `thin` contains Geometry and Trigonometry, and the
   Sharpen button posts `{source:'probe', count:12}`.


**Acceptance.**
1. Opening the dialog at 700 shows text matching `\d+ of 44 right`.
2. At 650 the dialog contains "14 of 22"; at 560 it doesn't.
3. With an exam date, each quick chip has a tag from {Steady, Ambitious, Very ambitious}, and
   the Dec 5 chip's Save sends `PUT /api/me {target, exam_date}`.


**Acceptance.**
1. Exam today + 10, Mon–Fri, 45 min, 10 open traps, median 100 s: `workload.need.traps ==
   2000` (s), and `fits` matches `capacity >= Σ need`.
2. `short_by > 0` → the Set button's body is `{minutes: suggest_minutes}`, a chip value.
3. The popover's rows each contain "study days" and a tag; with `satdates` deadlines present,
   "register by".
4. The SEC box still ticks within 1.1 s (v2 check 20).
5. A learner with 40 answers, no open traps, no sittings, exam today + 30 and a target 200
   points above `_interpolate(F)`: `need.target.minutes > 0`, `need.target.skills` is
   non-empty and in gain order, the line contains "reach 700", and `fits` is true only when
   `capacity ≥ Σ need` including the target term.
6. With 12 answers: `sized == false` and `unsized == 'answers'`, the card shows "Answer 30
   questions to size the work · 12 of 30", and neither "fits" nor "Suggested" appears on `/`.
   With 40 answers and no target: `unsized == 'target'` and the card shows "Set a target".
7. An assert in `server/checks/s3.py`: `suggest_minutes` is null or ≥ 15, for a sweep of
   need and capacity values that includes a need of 5 minutes.


**Acceptance.**
1. Exam today + 12: `stage.mode == 'stretch'`; `/api/next` items contain no kind `untried` or
   `probe`; the Up next reason never reads "New skills".
2. Three traps closed 20 days ago → a Due row of kind `sweep`; the body has `sweep:true`.
3. On the rehearsal Saturday, `/api/today.next.items[0].title` starts "Dress rehearsal".
4. Exam today + 1 → Up next's title starts "Light warm-up"; the checklist shows the 3 Night
   before items, and its heading reads "of 10".
5. Exam today, 07:00 local: `#exam` is the second card in DOM order, and all other cards are
   present and expanded.
6. Exam today + 6: `#exam` contains the checklist with no closed `<details>` (none at all), its
   7 checkboxes are visible, and the heading reads "Test-day checklist · 0 of 7". At today + 8
   there is no checklist.
7. Exam today + 12 with 3 traps on 2+-a-test skills and 2 on rare ones: `#mist` shows both
   group headings and all 5 rows without a click. The rare group's Fix body has exactly those
   2 trap ids.
8. The rehearsal line contains "after R&W and the break" and no clock time, and its `.ics` time
   field is empty until the student picks one.

---


**Acceptance.**
1. With Words merged: `GET /api/qotd | jq '.slots|map(.slot)'` gives
   `["math:mcq","math:spr","rw:wic","rw:transition"]`, and `jq '[.slots[].question |
   has("answer","answer_index","reasons","traps","key","seed","word")] | flatten | any'` gives
   `false`. Without Words: `["math:mcq","math:spr"]`.
2. `POST /api/qotd {slot:'mcq', …}` is filed as `math:mcq` in session `qotd:{day}`.
   `{slot:'rw:wic', …}` files one `word_reviews` row in session `qotd:rw:wic:{day}`, and a
   second identical POST returns the first answer.
3. **Key hidden.** Learner B answers `rw:wic` and reads `key_word`. Then fresh learner A loads
   `/` at 1280 and waits for `#qotd`. For A:
   * no text outside the `rw:wic` slot's option buttons contains `key_word` (whole word, any
     case), and no option carries a key marker;
   * `/api/words/today.wic.word` is null.
   After A answers, the verdict names `key_word`.
4. `POST /api/qotd {slot:'math:spr', answer:'1 1/2'}` for a key of 3/2 → `correct:false`,
   `entry.kind == 'form'`. `'.66'` for 2/3 → `'early'`. `'455'` for 460 → `entry == null`.
5. With 5 or more on-time answers, feedback has `crowd.median_ms` as an integer.
6. Twins in the column at 1280:
   * After a wrong MC, `Now its twin` renders a new stem inside `#qotd` without opening a
     dialog.
   * After a wrong `rw:wic`, `POST /api/qotd/another {like:'word'}` returns an item whose
     server-side key is the same word, in a different frame.
   * Before the slot is answered, the call gives 409.
7. After a **right** answer in each slot, the rationale (Math) or all four reasons (R&W) are
   visible with no click.
8. The Due row reads `N of 4`. It is done only after all four are answered, and its Why reads
   "The same 4 for everyone, one try each".


**Acceptance.** After finishing the day's challenge: `#chal` has 10 elements with the slot
role and a field % each. Before finishing, none are rendered and no review call is made.

---


**Acceptance.**
1. A finished module with 3 wrong named answers and 2 blanks at time-up: the card's cause line
   sums to 5, and `estimate.rescore(sid, [those 3])` gives a midpoint above the original.
2. `Retake as twin` posts `{kind:'twin', twin_of}`, and the new sitting's slots match the
   source's templates and tiers (S5's check 13).
3. After the twin finishes, its card shows "Twin of" and "Fixed N of M".
4. A tap on a miss chip shows a menu with exactly "Review Q…" and "Twin".


**Acceptance.**
1. A day with 5 wrong first tries: its Redo button's body has 5 attempt ids, and the session it
   creates serves 5 templates matching those attempts, each on a new seed.
2. The Accuracy heat draws a hollow cell for a day with 1 answer.
3. `time_split.domains` sums to the week's practice minutes (± 1).
4. With `exam_date` and a target set and 40 answers, the goal popover shows "Suggested" with
   a chip value of at least 15, its arithmetic contains "reach", and each chip has the meta
   "≈ N q". With 12 answers it shows "Answer 30 questions to size the work · 12 of 30" and no
   "Suggested".


**Acceptance.**
1. A learner with 2 module sittings (midpoints 620 and 680, within 45 days) and no plan:
   `Build with these` shows 4 controls, the Start from reads "average 650", and there are 7 day
   rows. `Use this plan` sends one `POST /api/plan` with `current:650`, after which
   `/api/today.plan` is non-null and its start is today.
1b. **No sitting.** A learner with 40 practice answers and no sitting: Start from shows the
   `Your best guess` slider with no value and `Take a module · 35 min`, the target chip is
   visible, and `Use this plan` is disabled. After the slider is set to 520, the target chip
   reads 620 (start + 100) and `Use this plan` sends `{current:520, target:620}`.
1c. **New student.** A fresh code: Start from shows `Diagnostic · 20 q` and the slider.
   Clicking the diagnostic saves the draft and sets `sessionStorage satf.return` to
   `/plan/?setup=1&step=1`. With neither done, `Use this plan` stays disabled.
2. With a plan: the stat row has "On time" and no "days to the SAT".
3. A missed past study day: its `Make up` starts a drill with `task` equal to
   `<that date>:focus`. After finishing, the day reads made up.
4. Behind with 2 missed days: two Apply buttons. Applying the first sends
   `PATCH {minutes}`, and Undo sends the old value.
5. With a plan: the week header's text equals `Week {n} of {N} · {tasks_done} of
   {tasks_planned} tasks · {pct}%` from `GET /api/plan`'s `weeks[n]`, and its theme line
   equals that row's `theme`. Both match /plan/'s week header for the same week, including
   after paging to the previous week.

---


**Acceptance.**
1. A learner who studied yesterday and closed 3 traps: `brief` contains a fact starting
   "Yesterday" with "3 mistakes fixed".
2. Playwright with the clock at 19:00 local, a 6-day streak and nothing today: the first
   hero fact contains "keeps your 6-day streak", and its button opens `dialog` with a question.
   At 17:00 it doesn't appear.
3. After the goal's minutes are reached, `receipt` is non-null, and `#next` shows "TODAY'S
   WORK" with every receipt line. A reload shows the same full receipt, with no `.rise`
   animation, and no `Show` control exists.
4. `receipt.claimed == estimate.practice_delta(learner, local midnight)` (an assert in
   `server/checks/s3.py`). A seeded day whose answers lower `S` gives a negative `claimed`, and
   the line reads "≈ −".


**Acceptance.**
1. Second visit (Playwright, same context): `#next` shows real content, not `.skel`, within
   50 ms of DOMContentLoaded.
2. `PATCH /api/plan/...` intercepted to 500: the skipped row reverts and shows "Not saved. Try
   again."
3. Pressing `J` twice from the top moves focus to the third card's heading.
4. At 390, a 70px left swipe on the MC question shows the grid-in tab.

---

## 3. Spec overrides


## Contracts and amended checks

| # | topic | what disagreed | decision | owner |
| R2 | Mistakes page | Shell and Today link `/mistakes/`; Review replaces it | `/review/` is the page (Review spec). `/mistakes/` redirects (307, served by `api_review.py`) to `/review/?tab=redo`, keeping the query. Every "Mistakes" reference in other specs means Review. Mistakes logged from outside (Shell §2.7) appear in Review's Redo tab with a "Logged by you · Bluebook" chip and their note. | S10 |
| R3 | Challenge | Shell keeps `/challenge/` and a practice-rank board at `/challenge/#practice`; Compete replaces it | Compete owns all competition. `/challenge/` redirects (307, served by `api_compete.py`, as Compete §2 says) to `/compete/contest/?id=daily`. Shell's **practice rank** (right answers, rolling 7 days, scopes everyone / same exam date / each class) is Compete's leaderboard metric `right` with period `7d` and a new scope `exam`; the Me snapshot reads it from Compete. `/challenge/#practice` links become `/compete/leaderboard/?metric=right&period=7d`. | S8 |
| R7 | Per-question time, trail, strikes in tests | Report adds `sessions.times` and `sessions.trail`; Review adds `sessions.times`; Tests adds `sessions.qstate` | **One column `sessions.qstate`** (JSON): per qid `{ms, struck, conf, trail, first, changes}` and `_session {away_ms, away_n, late}`. Flags are not in it (R5). The runner sends `ms` (dwell delta) and `made_left` with each answer save and other deltas with `POST /api/session/{sid}/state`. `record_paper` passes `qstate[qid].ms` into `attempts.ms`, so tests count as study time and per-question time. Report's `/flag` and `/time` endpoints are served by Review (flags) and Tests (`/state`). | F4 (column, record_paper), S5 (endpoints) |
| R8 | Attempts columns and what counts | Review adds norm/repeat/repair/flagged/stem; QBank guess; Shell disputed; Compete sms/void | **One set of new `attempts` columns:** `norm, repeat, repair, flagged, guess, disputed, sms, void, stem`. Mastery, accuracy, boards and ranks leave out rows with `repeat=1`, `disputed=1` or `void` set; a right answer with `guess=1` counts half. Study time and question counts keep every row. A **clean answer** (closes a mistake, counts as a check-in) is right, not a repeat, not flagged and not a guess. `progress.record` computes `repeat` itself for every caller. | F4 |
| R9 | Traps and check-ins | Review rebuilds traps (id, norm, kinds, relapses) with check-ins at 7/21 days; Plan wants rechecks at 3/10/30 via stage/due; Shell adds source/note/origin | **One `traps` table:** Review's rebuild (integer `id`, `norm`, `reason` = latest concrete text, `closed_how`, `relapses`, `seed`, `session`) plus Shell's `source` ('outside'), `note`, `origin`, plus **one check-in schedule: 3, 10 and 30 days after fixing** (Plan's), stored as `due` + `checks` (0 to 3). A miss on a due check reopens it as Relapsed. Plan's Rechecks task is the drill pool `checks` (R10); Review's "Check these now" and "CHECK-INS DUE" use the same. Kinds: misconception, gridin (named when the template has `spr_mistakes`), slip, unsure. | F4 |
| R10 | Drill body | Nine sections add their own fields to `POST /api/drill` | **One body contract (§2.6)**, validated in one place and built by F5. Section field names map onto it (table in §2.6). Fields that need another section's data stay on `POST /api/drill` and are resolved by the owner's module through a registry: `like` (S3, `daily.resolve_drill`), `word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2, `classes.resolve_drill`); contests are started by S8's own routes. `list` is accepted as an alias of `pool`, so Review's bodies work unchanged. | F5 |
| R13 | Streak and study time | Shell, Today, Plan and Words each define a streak or minutes rule | **One function `progress.days(learner, tz, weeks)`**, used by the shell, Today, Me, Plan, Results and Words. A day is the learner's local day (X-Tz). A study day has at least one answer, or at least 10 word reviews, or a finished sitting. Rest days of the **active plan** (a weekday off, a day off, the exam's eve) neither break nor extend the streak; a rest day with practice extends it. Minutes = attempt ms (each capped at 10 min) + each finished sitting's elapsed time **only when its attempts carry no ms** (capped per module at its clock + 60s; untimed 90 min) + word reviews (each ≤ 60 s) + minutes of the student's own plan tasks marked done. Returns streak, best, active days, minutes and per-day rows for up to 53 weeks. Today's three labelled streaks are three facts: study (this), day's questions (`daily.qotd_streak`), challenge (`compete.challenge_streak`). The 60-minute after-midnight grace applies to the question of the day only. | F4 |
| R14 | Plan arithmetic | Shell and Today compute plan days on the client (`UI.plan.dayOf/doneOf`) and add `plan_marks`; Plan puts all of it on the server | **Server only, `server/plan.py`** (Plan spec). `UI.plan.dayOf/testOf/doneOf` are deleted. Today's plan list, the shell's Today and Plan metas, the Today card and Me's week dots read `/api/today.plan` and `/api/shell.plan` (Plan provides `plan.today_summary()`). Today's Skip / Move use Plan's `PATCH /api/plan/{id}/tasks/{task}` (any study day up to the eve, not only this week). Dashboard's `plan_marks` table and `POST /api/plan/mark` are not built. | S7 |
| R15 | Goals and SAT dates | Target/exam date edited on Today, Me and Plan; R&W fields; three copies of SAT_DATES | `target, exam_date, current, minutes, days, tests, focus, rw_now, rw_target` live on `learners`; the active plan mirrors them both ways (Plan §5, `plan.mirror()`), so one edit shows everywhere. Dashboard's `plan_started` is `plans.start`. Upcoming official dates: one constant in `server/satdates.py`, served in `/api/shell.dates`, read by the date pickers on Today, Me, Plan and Compete's seasons. Past dates are never offered. A new `exam_date` must be today or later in the learner's zone. | F4 |
| R16 | Estimate, confidence, percentile, drift | Report, Tests, Today and Plan each define an estimate or percentile; Compete adds a report percentile | **One module `server/estimate.py`:** `estimate(learner)` returns latest, previous, best, range, `mean3` (mean midpoint of the last up to 3 scored sittings within 45 days, added outside Math scores included), combined (≥2 standard sections: mean ± 70/√n), confidence `{level, reason}` with **Tests §2.2's rules and wording**, trend (±20 = steady), routed_up and counted. `percentile(sid)` ranks a sitting among **each learner's first standard sitting of the same kind** (a paper: of that paper), shown only when n ≥ 20; standard = timed official, adaptive, standard module 1, not fixed-route or extended. The Report hero, Tests cards, Results, Today's score card and the report's Ranked pill all use it; Compete's "last 90 days" variant is not built. **Drift** is Plan's rule (mean3 vs the plan's start, ≥ 40 either way; target reached) and Today's drift line shows Plan's `suggest`. | F4 |
| R17 | Report a problem | Shell (10 images downscaled, disputes, admin), QBank (3 × 5 MB BLOBs), Tests (R-#### ids, tools), Report (3 screenshots), Words (10 images) | **One system:** Shell §2.10 and §10 are canonical: one modal `UI.report(ctx)`, up to 10 images (PNG, JPEG, WebP, GIF), stills downscaled in the browser to 2000px, 10 MB server cap, files on disk under `server/reports/{id}/` (git-ignored), bounded disputes (5 open), Your reports with replies in Settings, `/admin/reports` behind `SATF_ADMIN_TOKEN`. Categories per context are the union: Shell's lists, plus Tests' "More than one right answer" and "No right answer", plus Words' "Wrong or unclear definition" (word context). Mid-test reports never show marking and hide key disputes. Rate limit: 10 an hour and 20 a day per learner (429). Ids are integers. `tools/reports.py` is an optional CLI over the same table. | F6 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
| R19 | Access to keys and re-serving | Review defines `access()`; others re-serve items ad hoc | **One rule, `deps.access(learner, template, seed)` → `reveal` \| `kept` \| None** (Review §server). Everything that returns a key or re-serves an exact (template, seed) goes through it: review endpoints, sets, worksheets, the report, the challenge review, permalinks, Words examples. Live-test items and unanswered or same-day challenge items never leak. The permalink `/practice/session/?q=TEMPLATE:SEED` (QBank; Shell's `/q/` is the same route) serves any catalogue item that is not in today's challenge as a fresh one-question drill; the key shows after answering, as always. | F4 |
| R20 | Status colours and glyphs | Report flips nothing; QBank uses wash for correct; Compete/Review differ | **The practice session's semantics, with glyphs everywhere** (§2.3): right = orange, wrong = graphite, plus Mixed (right on a retry) and Repaired (right on the repair after a miss) as two states, skipped, blank, voided, repeat, not reached, answered (exam), flagged, saved, has note, current. One legend component. | F1 |
| R24 | Drills that are not sittings | twin, try, word-example, review pane, spot, quick each have their own list rule | `cfg.inline = true` for sources `twin, try, word-example, review, spot`: never listed as a sitting, never in history, In progress or Resume; their answers file normally (a twin counts on its parent). `quick` sittings are listed in history as "Quick questions", never offered as Resume, and deleted when finished with 0 answers. Any set finished with 0 answered is never listed. | F5 (flag), S6 (history), S4 (drill list) |
| R26 | The sittings list | Tests, Report, Words, Review, Today each extend `/api/history` or add a list | **One endpoint `/api/history`** (S6) with every field in Report §server plus Tests' statuses, `all=1`, modules, blanks vs wrong, twin and paper labels, Words' `kind=words` filter and counts. Today's "Recent tests" reads `/api/history?kind=tests&all=1&limit=6`; Dashboard's separate `/api/tests/recent` is not built. The report page redirects a words-run id to `/words/run/?id=`. | S6 |
| R27 | Question of the day | Today reshapes QOTD (two slots, crowd, past days); Compete wants the spread, a streak and past days | **Today owns QOTD** (`daily.py`), and its API covers Compete's needs: the option spread with misconceptions, the day's-questions streak, 30 past days, graced answers. Compete's contest-page QOTD panel reads `/api/qotd?day=`. | S3 |
| R30 | Today's cards | Today has a Mistakes card; Review wants a Review card; Words wants a Words tile | Today's `#mist` card **is** the Review card: Review's counts (open, half fixed, check-ins due, marked) plus Today's top 5, Fix and Try one now. A **Words tile** joins the grid: desktop `plan ×8 · words ×4` (the plan card spans 8, the Words tile 4); phone after the challenge card. | S3 |
| R34 | Test pace | several pace numbers | 95 seconds a question everywhere (2100 s ÷ 22, as `MODULE_SECONDS // MODULE_SIZE`). A 10-question challenge is 950 s. | F5 |
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
| F5 | the drill body; `GET /api/types`, `GET /api/types/{t}/example`, `POST /api/mistakes/log`; `drill.levels()`, `blueprint.kinds()` | F2 (palette, Log a mistake), S2 (assignment type search), S3, S4, S7, S8, S9, S10 |
| S2 | `/api/classes`, `/api/assignments`, `members` | F2 (Class nav item), S3 (due assignments first), S7 (assignment minutes), S8 (class scope) |
| S3 | `/api/qotd?day=`, the "like" drill route, `/api/scores` | S8 (contest page QOTD panel), S6 and S7 (added scores on charts and the plan's test day) |
| S4 | `/api/bank`, `/api/drill` list (Your sets), permalink `?q=` | S1 (question types met), S3 (Continue), palette |
| S5 | the lobby at `/test/?s=`; `POST /api/mock/new` (old body still works) | S3 and S7 start tests there, never on a running clock |
| S6 | `/api/history` (R26), `/api/stats`, `/api/skill/{topic}`, `UI.sittingCard`, `?q=M1-3` on the report | S3, S5, S9 (words filter), S1 (recent activity links) |
| S7 | `plan.today_summary(learner, tz)`, `plan.mirror(learner, fields)`, `PATCH /api/plan/{id}/tasks/{task}`, `GET /api/plan/ics` and the cal feed, `UI.taskRow` | S3 (plan card, Today list), F2 (metas), F4 (`PUT /api/me` mirror), S1 (goals card, Settings calendar), S4 (next in plan) |
| S8 | `compete.clock`, `twin_questions`, `finish_contest`, `state_extra`, `rate`, `challenge_streak`, `rank_snapshot`, `/api/contest/daily`, `UI.board`, `UI.level` | S4 and S5 (contest sittings, R28), F4 (`record` rating hook), S3 (challenge card), S1 (snapshot, Boards block) |
| S9 | `words.of_reason`, `words.minutes_today`, `words.today_summary`, `words.me_stats`, `/api/words/today`, `UI.gloss`, `UI.addWord`, `UI.addWordFromSelection` | F5 (feedback words), S7 (Words task), S3 (Words tile), S1 (Me stats), F2 (quick sheet tab), S4, S3, S6, S8 (gloss and add-from-selection hooks) |
| S10 | `/api/review/counts`, `/api/review/item`, `/api/review/family`, flag endpoints (`POST /api/session/{sid}/flag`, `POST /api/flags`) | S3 (Review card), S1 (Saved & in progress), F3 (`UI.review` pane, `UI.history`), S4 and S5 (Mark), S6 (flagged in results reads `flags`) |
### 2.13 Acceptance checks changed by the resolutions
| section | the check says | read it as | why |
| 3.2 Today | `POST /api/plan/mark {day, task, state:'skipped'}` | `PATCH /api/plan/{id}/tasks/{task_id} {day, status:'skipped'}`; `/api/today.plan` shows it; `{status:'todo'}` removes it | R14 |
| 3.2 Today | `GET /api/tests/recent` (fields and module split) | the same fields in `GET /api/history?kind=tests&all=1` | R26 |
| 3.2 Today | "PUT /api/me {exam_date, minutes, days} returns 200 with plan_started = today" | returns 200; a plan's start day comes from `POST /api/plan` (`plans.start`) | R14, R15 |
