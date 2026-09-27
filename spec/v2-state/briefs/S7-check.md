# Check brief for S7: Plan pages (the server is merged)

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

**S7 · Plan** (wave 2, port 8027). Builds Part 3.6 in full, R14, the calendar feed of R18(b),
Words' Plan step 4 and Words task. Owns `web/plan/**`, `server/plan.py`,
`server/api_plan.py`, `web/assets/plan-ui.js`, `server/checks/s7.py`.
State: not started.


## The section's acceptance list

### 3.6.8 Acceptance checks

1. curl -s localhost:8000/api/plan -H 'X-Learner: a:v2revplanacc1' -H 'X-Tz: 0' returns active=null, bank.topics=19, bank.templates=386 and a non-empty bank.example.label.
2. time curl -s -X POST localhost:8000/api/plan -H 'X-Learner: a:v2revplanacc1' -H 'X-Tz: 0' -H 'content-type: application/json' -d '{"current":520,"target":700,"exam_date":"2026-11-07","minutes":45,"days":"1111100","tests":"weekly","test_size":"module","focus":{"Geometry and Trigonometry":"focus","Algebra":"strong"}}' returns 200 in under 1 s with active.id set. In days: 2026-11-07 is 'exam', 2026-11-06 is 'eve', every Saturday and Sunday is 'rest', each full Mon-Sun week before Nov 2 has exactly one 'test' on its Friday, and the week of Nov 2 has its test on Thursday 2026-11-05.
3. POST /api/plan/preview with that body gives split['Geometry and Trigonometry'] > 0.15 and split['Algebra'] < 0.35, the shares sum to 1 ± 0.01, target_note.points_pct is 88 and route_right is 14, and preview for target 800 has target_note.capped true.
4. Across GET /api/plan/day/{d} for the next 20 practice days, Geometry and Trigonometry topics fill more slots than Problem-Solving and Data Analysis topics, and no topic appears on 3 practice days in a row. With Advanced Math on focus and minutes 120, all 20 days return focus tasks (the fallback holds).
5. POST /api/plan returns 422 for each of: target 190; target 500 with current 520; exam_date yesterday; exam_date '2026-02-30'; days '0000000'; three domains on focus; tests 'hourly'; off [['2026-10-10','2026-10-01']]; a custom task titled with 61 characters.
6. PUT /api/plan/draft {step:3, fields:{minutes:90}}, then GET /api/plan, gives draft.step == 3, and the landing (shot.py at 1280) shows 'Continue' and 'step 3 of 4'. A POST /api/plan that returns 422 leaves the draft unchanged.
7. Take today.tasks' focus task and POST its start.path with start.body: GET /api/plan shows it 'active' with answered/total. Answer its full planned count without calling finish, and GET shows it 'done'. Call finish and the response carries plan.next.
8. After a learner finishes a whole module test with no ms sent, /api/me days.recent[-1].minutes >= 1.
9. In test_flow: backdate a plan's start by 3 days in sqlite and GET /api/plan: plan_days has rows for those 3 days. PATCH {minutes:90} leaves those rows' minutes unchanged, and today's Day.minutes becomes 90.
10. A past planned day with no study has status 'missed'. Starting its catch-up task (task=<that date>:focus) and finishing it turns that day 'made_up', and stats.made_up is 1.
11. POST /api/plan/{id}/tasks {day: today, title: 'Reading & Writing', minutes: 30} shows the task in today.tasks with kind 'custom'. PATCH it {day: today, status: 'done'} raises today's minutes_done by 30. PATCH {status: 'todo'} undoes it. DELETE removes it.
12. A repeating custom task {repeat: 'study_days', title: 'R&W', minutes: 30} appears on every study day in the next 14 days and on no rest day, and each such Day.minutes grows by 30.
13. PATCH today's focus task {day: today, status: 'skipped'} gives status 'skipped', and the page row has opacity 0.55 and the text 'Skipped'. PATCH {status: 'todo'} restores it.
14. PATCH today's focus task {day: today, to: <next study day>} marks today's row 'moved' with moved_to set, and that day's planned minutes grow by the task's minutes.
15. PUT /api/plan/{id}/day/{today} {off: true} makes today 'off', and the next practice day's focus topics include today's former topics. DELETE the override and today returns to 'practice'.
16. A plan whose start is backdated 8 days, with no study, returns behind.suggest_minutes >= 15. PATCH {minutes: behind.suggest_minutes} then changes Day.minutes for today onward only.
17. A learner on a '1111100' plan who studied on Friday and Monday, with nothing on Saturday and Sunday, has stats.streak == 2, and /api/today days.streak == 2.
18. curl GET /api/plan/{id}/ics with the learner header returns text/calendar containing 'BEGIN:VCALENDAR', one 'BEGIN:VEVENT' per study day from today plus the exam and eve, 'DTSTART;VALUE=DATE:20261107' with 'SUMMARY:SAT', and at least one 'BEGIN:VALARM'. After POST /links {cal:true}, /cal/<token>.ics returns the same events with no header; after {cal:false} it returns 404.
19. After POST /links {view:true}, GET /api/plan/shared/<token> with no X-Learner returns days and stats, and the body contains neither the learner code nor any start body. After {view:false} it returns 404.
20. After a module sitting whose band midpoint is 60 above the plan's current, GET /api/plan returns suggest.kind 'up'. POST /drift {dismiss} clears it. Two sittings averaging above the target give suggest.kind 'target'.
21. At 390px, document.documentElement.scrollWidth <= 390 on the landing, on each wizard step (?setup=1&step=1..4), and on each tab (?tab=plan|progress|plans), for learners a:v2revplanacc1 (new) and a:v2revshellhist (history).
22. At 390px the wizard shows 'Step 2 of 4 · Where you're going' as text. The WeekdayTiles read 'Mon'...'Sun', each with STUDY or REST, and every study tile contains a select. Calendar cells show their minutes text.
23. In step 4 with two domains on Focus, the page contains the visible text '2 focus areas at most' (not only a title attribute), and the third domain's Focus button is disabled.
24. Toggling Geometry & Trig to Focus in step 4 grows its SplitBar segment within 400ms, with no reload.
25. ?tab=progress renders an svg in the StudyTimeChart and a table inside it. The DomainCard rows are in ascending order of % right, and 'All 19 skills' expands to 19 rows.
26. With the exam date backdated to yesterday, GET /api/plan gives state 'after', the page shows the result form, and POST /api/plan/{id}/result {math:690} makes the Plans tab tag 'Finished · 690'.
27. With a plan active, Today (/) shows the first undone task's title from /api/today.plan, and its 'N of M done' equals the Plan tab's.
28. In the calendar, focus today's cell and press ArrowRight: the next day's cell gets aria-pressed=true and the DayPanel kicker changes to that date.
29. Create a second plan: the first shows under Plans as Archived. POST /api/plan/{first}/activate makes it active again, GET /api/me profile.exam_date equals its exam_date, and ?id=<second> shows the 'You are viewing an older plan' banner with both buttons.
30. Setting sessionStorage satf.return to '//evil.example' and opening a report shows no 'Back to your plan'. '/plan/?setup=1&step=1' shows it.
31. PYTHONPATH=. python3 server/test_flow.py passes, and python3 -m server.plan (the __main__ self-check) passes.


## The upgrades' acceptance items (spec/v2-upgrades/plan.md)

**Acceptance.**
1. U4's seeded learner (circles 10 answers at 30%, linear_functions 20 at 90%, 30 more
   elsewhere) with a plan and no focus: over `GET /api/plan/day/{d}` for the next 20 practice
   days, circles fills more focus slots than linear_functions.
2. v2 acceptance 3 passes unchanged for `a:v2revplanacc1` (gains null).
3. A learner with per-tier first tries giving `route.m1 == 0.5` and target 650: `route.gate ==
   true`, and every Build focus body has `tiers ⊆ {easy, medium}`. The same learner at m1 0.62
   the next day stays gated; at 0.66 it is not.
4. At 1280, step 4 for the seeded learner shows `Where your points are` with 6 rows; the first
   row's topic is `points.skills` sorted by `v` descending, first.
5. With gains non-null, every focus task's `why[0].text` contains `≈ +`.
6. `python3 -m server.plan` asserts that a skill with gain 20 and 90 minutes gets a larger `w_t`
   than a skill with gain 0 at the same state, for minutes 0 to 300 on the second skill.
7. The same self-check asserts that no body dealt on a gated day carries `hard` in `tiers` or
   in `pins`.


**Acceptance.**
1. `python3 -m server.plan` asserts guarantees 1 and 2 (pins ≤ 1 a practice day, pins ≤ 30% of
   pre-Final slots, pins sorted by gain, the `W` window held, `counts.unplanned` equal to the
   needed cells with fewer than 2 pins) on three synthetic plans: 60 days over all 19 topics at
   45 × 5; a 45-day new student with about 50 needed cells; and 15 minutes × 2 days a week.
2. A learner with circles hard first tries ✓✓✗✓ (newest last) has that cell `proven`; ✓✗✗✓ is
   `shaky`.
3. `POST /api/drill {topics:['ratios'], pins:[{topic:'circles', tier:'hard', count:2}],
   count:6}` serves exactly 2 hard circles items and 4 ratios items (a check in
   `server/checks/f5.py`).
4. A new learner with 3 answers: the plan's first practice days' focus tasks are kind `map`
   with `body.source == 'probe'`, and the Plan tab shows `Map · ` with a count.
5. At 390, the coverage card has no horizontal page scroll (`scrollWidth <= 390`).


**Acceptance.**
1. A plan with circles on Focus: the first practice day of the week that deals circles has a
   `check` task ordered before the focus task, with `body.count == 4` and `topics ==
   ['circles']`.
2. That week's last practice day has a `check` whose `body.rematch` is the before session's id.
3. The after scores 4/4 in less total ms, and 10 of circles' last 12 clean first tries at
   medium or hard are right: `GET /api/plan` shows circles `{state:'strong', by:'auto'}`, a new
   Focus skill with `by:'auto'`, and a `changes.today` line containing "passed". `PATCH` with the
   old skills restores it and sets `pin: true`.
4. The same 4/4 with 7 of the last 12 right: circles stays on Focus, and the check's `result ==
   'again'`.
5. With `prefs.plan_auto_focus == false`, nothing changes and `banners` has kind `graduated`.
6. A Strong skill with 7 of its last 12 right reads `normal` with a `since` 7 days ahead, and
   its next focus Why contains "slipping".
7. An auto-promoted Strong skill has a `pins` item with `why == 'keep'` and `count == 2` in some
   focus body of every plan week after its promotion.


**Acceptance.**
1. A learner with 2 check-ins due: today's tasks have one kind `recheck` titled "Warm-up" with
   `body.source == 'warmup'`, and no other task carries check-ins.
2. A learner with one trap opened on a `conf='sure'` answer and one ordinary trap: the fix
   body's `ids[0]` is the sure one.
3. A Focus skill with 3 answers in Build: a `learn` task that day with `body.example == true`.
4. `prefs.words_goal = 10` with 12 due on a 45-minute day: a `words` task whose `minutes ==
   min(words.minutes_today(), 9)` and whose `body.box` equals it, `subject == 'rw'`, and
   `budget.q == floor((45 − w) × 60 / s)`, with the focus count equal to `q` minus the other
   question kinds.
5. `jq '[.today.tasks[].subject] | all'` is true.
6. `python3 -m server.plan` asserts, for every minutes value in {10, 15, 30, 45, 60, 90} × `s`
   in 60–150 by 5 × Words on and off × Build, Sharpen and Final × test day or not: the counted
   minutes (question rows at `s`, Words `w`, own tasks kept, the test) are at most `m`, and a
   test lands only on a day whose `g` is at least its minutes.


**Acceptance.**
1. A Build focus body has `zone == 'stretch'`. A Final body has no `zone`, `adaptive == false`
   and `tiers` equal to v2's Final row for the target.
2. A Sharpen focus body has `timing == 'pace'`.
3. A Build skill whose median is 1.4× its budget: its focus body has `timing == 'pace'`, and its
   Why contains "budget".

---


**Acceptance.**
1. A learner with 2 sittings (midpoints 560 and 580), 4 weeks of Mon/Wed/Thu at about 30 min,
   and no profile target: `proposal.cfg` has `current 570`, `target 670`, `days '1011000'`,
   `minutes 30`.
2. At 1280 the landing shows "Use this plan". One click sends exactly one `POST /api/plan`, the
   URL becomes `/plan/`, and `document.activeElement` text starts "Start today".
3. The `30 min × …` chip → 45 → `PATCH {minutes:45}`; its Undo toast sends `PATCH {minutes:30}`.
4. In the wizard, picking the 1h chip changes week 1's cells to `1h` within 400 ms, without a
   reload.
5. ⌘Enter on step 2 with a valid date sends `POST /api/plan`, with steps 3–4 defaults in the
   body.
6. A new learner (no sitting, `measure: true`): `preview.sample_day.tasks[0].kind == 'test'`
   with a title starting "Diagnostic", the next is kind `map`, and `preview.first.question` has
   no `answer`, `rationale` or `reasons`. `POST /api/drill {source:'plan_preview', count:1,
   first:{token, answer:0, ms:20000}}` returns an id whose session has 1 answered and
   `cfg.source == 'plan_preview'`; re-posting the token gives 409.
7. At 390, on each wizard step, the Live plan's month grid is in the page flow (not inside a
   `[role=dialog]`) and above the footer.


**Acceptance.**
1. A learner with 2 sittings: step 1's RangeBar SVG has 2 band rects and one mean tick.
2. `POST /api/plan {current:null, measure:true, …}` → today's first task has kind `test` and
   a start path to the diagnostic. After a diagnostic with midpoint 540, `GET` shows
   `active.cfg.current == 540` and a change line containing "540".
3. A learner averaging 110 min a week who picks 45 × 5 sees the text "You've averaged". Ramp
   from 25 gives week 1 days of 25 and week 5 days of 45 in `preview.calendar`.
4. `cfg.place = 'the library'` → the `.ics` VEVENTs carry `LOCATION:the library`.
5. Daily tests at 45 min → the tests-share line shows, and its button sets `tests: 'weekly'`.
6. The Words row's 20 chip sends `PUT /api/me {prefs:{words_goal:20}}`.
7. Step 2's TargetNote for target 700 contains "88%" and no text matching `of 44 right`.
8. Step 4 at 1280 shows 19 SkillRows on load with no click.

---


**Acceptance.**
1. Clicking Start today → `/practice/session/?id=X`, and `GET /api/drill/X` has `cfg.run ==
   today` and `cfg.task` equal to the first undone counted task's id.
2. Finishing that block shows "Continue" and the next task's title; Enter creates a session with
   the same `run` and the next task's `task`.
3. After the last block the page contains "TODAY'S WORK", and `GET /api/plan` shows today
   `done` (or `partial` by the rules).
4. On a test day the first block opens `/test/?s=`; the report page contains "Continue today".
5. With Words on and no own tasks: the last interstitial's next pane starts "Words", Continue
   lands on `/words/run/` with `run` = today, the Words finish reply has `plan.next == null`,
   and afterwards `GET /api/plan` shows today `done`.
6. With a repeating own task: the rail has a segment labelled "on your own", the receipt shows
   its checkbox, and ticking it there sends `PATCH {status:'done'}` for that task.


**Acceptance.**
1. A learner with `s = 95`, Words on (12 due), 2 check-ins due and 6 open traps: `PUT day
   {minutes:10, trim:true}` on a 45-minute day leaves exactly Words (`body.box == 3`) and a
   warm-up of 4, 9.3 counted minutes, and `budget.cut` lists fix and focus. At 15 it leaves
   Words 3, warm-up 3 and fix 4 (14.1 min).
2. All of them done → today's status is `partial`, and `stats.streak` grew by 1.
3. The next practice day's focus topics include the topics cut today.
4. `DELETE` the override → today's minutes are 45 again.
5. On a test day, `GET /api/plan/day/{d}?minutes=30` returns no `test` task, a `cut` item
   `{kind:'test', to:<next study day with 35+ min>}`, and the preview text contains "moves to".
6. The L4 self-check (L4 acceptance 6) covers every chip value.


**Acceptance.**
1. Every `why` item on a focus task has `text`, and those naming a trap have
   `href ^= '/review/?open=trap:'`.
2. `PATCH {status:'skipped', reason:'no_time'}` → the task is `moved`, with `moved_to` = the
   next study day.
3. `reason:'too_hard'` on a circles focus task → the next day that deals circles has a `learn`
   task before its focus task.
4. `PATCH {status:'done', minutes:20, where:'khan'}` on a focus task → today's `minutes_done`
   grows by 20, and `stats.questions` is unchanged.
5. A done set with 3 misses shows "Again · the 3 you missed"; its body has `rematch` and
   `scope:'misses'`.
6. At 1280 and 390, every undone question row has visible `Skip` and `Mark done` buttons and a
   `[role=checkbox]` status circle; the ⋯ menu contains no Skip, Mark done or Again item.
7. Every row's why lines are visible on load (no `details`, no `aria-expanded=false` around
   them).
8. `I know this` sends a body with `count == 8`; 7 right passes the skill, 6 reads "Not yet".


**Acceptance.**
1. `POST /api/plan/{id}/tasks {type:'bluebook', day}` creates a task with `minutes == 134`.
2. Ticking it and saving Math 610 → `/api/scores` lists an outside score of 610 on that day,
   and `GET /api/plan.sittings` includes it.
3. Three missed cells in 2 skills → tomorrow's tasks include a `fix` whose detail contains
   "Bluebook follow-up".
4. Saving R&W 560 with Standard English Conventions 5 missed of 26 → `GET /api/plan.score.rw`
   includes the 560 sitting, and `GET /api/plan/progress.rw_domains` has that domain with
   `missed == 5`.


**Acceptance.**
1. Playwright at 1280: drag today's focus row onto Thursday's column; while hovering, the column
   shows "→"; the drop sends one `PATCH` with `to` = Thursday.
2. Dragging over a rest day shows the rest-day reason, and a drop there sends nothing.
3. Keys: select a task, `M`, `→`, `Enter` → `PATCH` to the next study day. `U` → `PATCH
   {status:'todo'}`.
4. Second visit in the same context: the DayPanel shows real rows, not `.skel`, within 50 ms of
   DOMContentLoaded.
5. `PATCH` intercepted to 500 → the row reverts and shows "Couldn't move. Try again."

---


**Acceptance.**
1. Sittings with midpoints 500 (Sep 1) and 560 (Sep 15), exam Nov 7, target 700: `projection`
   is non-null, `verdict.made_per_week > 0`, and the Score tile shows "At this pace".
2. A plan whose workload is short: the Days tile shows "short by", and its Set button's body is
   `{minutes: workload.suggest_minutes}`.
3. A test task 3 weeks into a 560 → 700 plan over 7 weeks has `aim == 620` (560 + 140 × 3/7,
   rounded to 10). A sitting at midpoint 700 (630–770) has `verdict == 'beat'` and a ✓ in the
   WeekStrip; at 650 (580–720) `within` and no ✓; at 540 (470–610) `under`.
4. `levers` has at most 3 items; each `patch` applied through preview changes `effect` as
   stated. No lever label contains a score range.


**Acceptance.**
1. A plan with a module baseline and `checkpoints:'every2'`: the second test task's start body
   has `kind:'twin'` and `twin_of` = baseline A; the first and third are fresh. Once baseline B
   exists, the next checkpoint's `twin_of` is B, then A again.
2. After the checkpoint, `GET /api/plan/progress.checkpoints[0]` has `subject == 'math'`, 22
   slots, each `change` in {fixed, held, slipped, still_missed} with a boolean `practised`, and
   the counts sum to 22.
3. `Fix these` sends `only` with exactly the slipped and still-missed qids and `sibling:true`;
   the session serves no template that appears in the checkpoint, except fallback slots.
4. At 390 the slot strip wraps to 2 rows of 11 with no page scroll.


**Acceptance.**
1. Day 1 GET, then a new trap on circles, then day 2 GET: `changes.today` has a line naming the
   trap's label with `cause == 'mistakes'`.
2. `PUT day {off:true}` for Monday, then the next day's first GET: a line "Mon off" with
   `cause == 'edit'`.
3. A second GET on the same day adds no snapshot row.
4. `GET /api/today` first on a day, then `GET /api/plan`: exactly one snapshot row for that day,
   `made_on` the local date.
5. `PATCH {minutes:25}` writes one `plan_events` row with `kind 'edit'`, `field 'minutes'`,
   `from_v 45`, `to_v 25`.
6. With the previous snapshot 3 days old, `changes.since` is that date, and the kicker text
   starts "Since".


**Acceptance.**
1. `PUT …/week/<next Monday> {days:[{date:<Tue>, off:true}, {date:<Thu>, minutes:15}]}` →
   Tuesday is `off`, and Thursday's minutes are 15.
2. With an active plan, U14's sheet contains "Next week's plan" and 7 tiles.
3. A `pass_check` goal on circles turns `done` when the circles After passes.


**Acceptance.**
1. A learner who missed 3 of the last 4 Tuesdays: `behind.fixes` has a `weekday` item naming
   Tuesday; applying it sets `day_minutes[1] == 15`.
2. The drift banner's preview text contains "needs +" and a number.
3. `PUT /api/me {prefs:{registered:'2026-11-07'}}` with that exam date → the registration
   banner is gone, and `GET /api/plan.active.cfg.booked == true`.


**Acceptance.**
1. A skill with 70 minutes in 14 days, 10/20 right in its 20 clean first tries before the plan
   and 11/20 in its last 20: its row has `not_moving: true`, and the card shows "Not moving".
   With 13/20 in the last 20 (+15) it is false; with only 15 answers since the start it is
   false.
2. `causes.total` equals the plan period's R8-counted first-try misses.
3. DomainCard By points orders rows by summed gain, descending.
4. Clicking Thursday's bar in StudyTimeChart → the URL has `?tab=plan&day=<Thu>`, and the
   DayPanel kicker shows that date.
5. `?tab=progress` shows 19 rows in the All 19 skills table on load, with no click.

---


**Acceptance.**
1. Exam Sat Nov 7, plan from Sep 23 (a 10-day Final): Oct 31 is a test day with `rehearsal:
   true` and a section body with `pause: false`, and it is the only rehearsal. A plan from Aug 1
   (a 15-day Final) has two, Oct 24 and Oct 31. No rehearsal falls within 6 days of the exam.
2. A learner with 12 closed traps: Final's practice days carry `sweep` tasks whose counts sum
   to 12 (±1 per day).
3. The last 5 study days before the eve have minutes = round(0.6 × base), no `learn` task and no
   `test` task, and each one's counted minutes are at most its minutes (`python3 -m
   server.plan` asserts no test on a taper day).
6. The v2 plan of §3.6.8 acceptance 2 (Mon–Fri, weekly module, exam Nov 7, made Sep 23): the week
   of Oct 26 has one test, the rehearsal on Sat Oct 31, and no test on Fri Oct 30; the week of
   Nov 2 has no test; the focus task 2 days before the exam has `timing == 'pace'` and `count
   <= 10`.
4. `GET …/trapsheet` returns ≤ 10 entries, each example with `seed >= 900000`, and no entry
   without a tell.
5. The eve has no counted task, one extra titled "Read your trap sheet", and `kind == 'eve'`.


**Acceptance.**
1. A finished plan: `plans[i].record.by_dow` has 7 numbers from 0 to 100, and the row shows the
   strip.
2. `Plan the next one` on a plan whose Tuesday adherence was 30% → the draft has
   `day_minutes[1] == 15`.
3. A learner with 25 plans: the Plans tab shows 20 rows and "Show 20 more · 5 left"; with 12
   plans it shows 12 rows and no pager.
4. A finished plan with 4 edits shows its last 3 event lines under the row without a click.

---


**Acceptance.**
1. `POST /api/plan` with `sections: {math: {current: 560, target: 700}, rw: {current: 500,
   target: 650, minutes: 30, focus: {'Standard English Conventions': 'focus'}}}` and v2's other
   fields: today's tasks have one type `rw` task titled `R&W · Standard English Conventions · …`
   and one shared R&W row, all with `subject == 'rw'`, their minutes summing to 30.
2. `GET /api/plan.score.total` has `start == 1060` and `target == 1350`; the Score tile contains
   "Total 1060 → 1350", and `document.title` contains "1350".
3. Craft and Structure on Focus with `prefs.words_goal == 10` → `prefs.words_goal == 15`, a
   toast with Undo, and the day's `words` body has `in_context == 2`. Expression of Ideas on
   Focus → the body has `transitions == 6`.
4. A third R&W domain on Focus → 422 whose message starts with "rw:".
5. The landing's BankStats has 4 tiles, and the fourth contains "Words".
6. With R&W unset: step 1 shows the R&W slider, step 2 shows the disabled R&W target with "Set
   your R&W score first", and the Plan tab shows no Total.
7. A ticked R&W task's `Log misses` with `{domain:'Craft and Structure', missed:3, of:13}` →
   `progress.rw_domains` shows that domain with `missed == 3`.

---

## 3. Spec overrides


## Contracts and amended checks

| # | topic | what disagreed | decision | owner |
| R8 | Attempts columns and what counts | Review adds norm/repeat/repair/flagged/stem; QBank guess; Shell disputed; Compete sms/void | **One set of new `attempts` columns:** `norm, repeat, repair, flagged, guess, disputed, sms, void, stem`. Mastery, accuracy, boards and ranks leave out rows with `repeat=1`, `disputed=1` or `void` set; a right answer with `guess=1` counts half. Study time and question counts keep every row. A **clean answer** (closes a mistake, counts as a check-in) is right, not a repeat, not flagged and not a guess. `progress.record` computes `repeat` itself for every caller. | F4 |
| R9 | Traps and check-ins | Review rebuilds traps (id, norm, kinds, relapses) with check-ins at 7/21 days; Plan wants rechecks at 3/10/30 via stage/due; Shell adds source/note/origin | **One `traps` table:** Review's rebuild (integer `id`, `norm`, `reason` = latest concrete text, `closed_how`, `relapses`, `seed`, `session`) plus Shell's `source` ('outside'), `note`, `origin`, plus **one check-in schedule: 3, 10 and 30 days after fixing** (Plan's), stored as `due` + `checks` (0 to 3). A miss on a due check reopens it as Relapsed. Plan's Rechecks task is the drill pool `checks` (R10); Review's "Check these now" and "CHECK-INS DUE" use the same. Kinds: misconception, gridin (named when the template has `spr_mistakes`), slip, unsure. | F4 |
| R10 | Drill body | Nine sections add their own fields to `POST /api/drill` | **One body contract (§2.6)**, validated in one place and built by F5. Section field names map onto it (table in §2.6). Fields that need another section's data stay on `POST /api/drill` and are resolved by the owner's module through a registry: `like` (S3, `daily.resolve_drill`), `word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2, `classes.resolve_drill`); contests are started by S8's own routes. `list` is accepted as an alias of `pool`, so Review's bodies work unchanged. | F5 |
| R11 | Preferences | Shell prefs, QBank prefs, Tests `learners.test_prefs`, Words `words_goal/words_from/gloss` columns, Shell `study_time` column | **One `learners.prefs` JSON and one registry `server/prefs.py`** with every key in §2.7. The separate columns are not added. Settings (S1) renders every key; the Practice builder, the test start sheet, Plan step 4, Me and the session's More menu write the same keys. Unknown key or bad value → 422 naming the key; only non-default values are stored; GET returns defaults merged. | F4 |
| R13 | Streak and study time | Shell, Today, Plan and Words each define a streak or minutes rule | **One function `progress.days(learner, tz, weeks)`**, used by the shell, Today, Me, Plan, Results and Words. A day is the learner's local day (X-Tz). A study day has at least one answer, or at least 10 word reviews, or a finished sitting. Rest days of the **active plan** (a weekday off, a day off, the exam's eve) neither break nor extend the streak; a rest day with practice extends it. Minutes = attempt ms (each capped at 10 min) + each finished sitting's elapsed time **only when its attempts carry no ms** (capped per module at its clock + 60s; untimed 90 min) + word reviews (each ≤ 60 s) + minutes of the student's own plan tasks marked done. Returns streak, best, active days, minutes and per-day rows for up to 53 weeks. Today's three labelled streaks are three facts: study (this), day's questions (`daily.qotd_streak`), challenge (`compete.challenge_streak`). The 60-minute after-midnight grace applies to the question of the day only. | F4 |
| R14 | Plan arithmetic | Shell and Today compute plan days on the client (`UI.plan.dayOf/doneOf`) and add `plan_marks`; Plan puts all of it on the server | **Server only, `server/plan.py`** (Plan spec). `UI.plan.dayOf/testOf/doneOf` are deleted. Today's plan list, the shell's Today and Plan metas, the Today card and Me's week dots read `/api/today.plan` and `/api/shell.plan` (Plan provides `plan.today_summary()`). Today's Skip / Move use Plan's `PATCH /api/plan/{id}/tasks/{task}` (any study day up to the eve, not only this week). Dashboard's `plan_marks` table and `POST /api/plan/mark` are not built. | S7 |
| R15 | Goals and SAT dates | Target/exam date edited on Today, Me and Plan; R&W fields; three copies of SAT_DATES | `target, exam_date, current, minutes, days, tests, focus, rw_now, rw_target` live on `learners`; the active plan mirrors them both ways (Plan §5, `plan.mirror()`), so one edit shows everywhere. Dashboard's `plan_started` is `plans.start`. Upcoming official dates: one constant in `server/satdates.py`, served in `/api/shell.dates`, read by the date pickers on Today, Me, Plan and Compete's seasons. Past dates are never offered. A new `exam_date` must be today or later in the learner's zone. | F4 |
| R16 | Estimate, confidence, percentile, drift | Report, Tests, Today and Plan each define an estimate or percentile; Compete adds a report percentile | **One module `server/estimate.py`:** `estimate(learner)` returns latest, previous, best, range, `mean3` (mean midpoint of the last up to 3 scored sittings within 45 days, added outside Math scores included), combined (≥2 standard sections: mean ± 70/√n), confidence `{level, reason}` with **Tests §2.2's rules and wording**, trend (±20 = steady), routed_up and counted. `percentile(sid)` ranks a sitting among **each learner's first standard sitting of the same kind** (a paper: of that paper), shown only when n ≥ 20; standard = timed official, adaptive, standard module 1, not fixed-route or extended. The Report hero, Tests cards, Results, Today's score card and the report's Ranked pill all use it; Compete's "last 90 days" variant is not built. **Drift** is Plan's rule (mean3 vs the plan's start, ≥ 40 either way; target reached) and Today's drift line shows Plan's `suggest`. | F4 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
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
| S1 | `/signin/`, `/pair/`, account endpoints; `/api/me/summary`, `/feed`, `/activity`, `/achievements`, `/seen`; the progress-link view `/share/?t=` | F2 (menu links, toasts); S6 and S7 (their pages accept the progress token) |
| S2 | `/api/classes`, `/api/assignments`, `members` | F2 (Class nav item), S3 (due assignments first), S7 (assignment minutes), S8 (class scope) |
| S3 | `/api/qotd?day=`, the "like" drill route, `/api/scores` | S8 (contest page QOTD panel), S6 and S7 (added scores on charts and the plan's test day) |
| S5 | the lobby at `/test/?s=`; `POST /api/mock/new` (old body still works) | S3 and S7 start tests there, never on a running clock |
| S7 | `plan.today_summary(learner, tz)`, `plan.mirror(learner, fields)`, `PATCH /api/plan/{id}/tasks/{task}`, `GET /api/plan/ics` and the cal feed, `UI.taskRow` | S3 (plan card, Today list), F2 (metas), F4 (`PUT /api/me` mirror), S1 (goals card, Settings calendar), S4 (next in plan) |
| S9 | `words.of_reason`, `words.minutes_today`, `words.today_summary`, `words.me_stats`, `/api/words/today`, `UI.gloss`, `UI.addWord`, `UI.addWordFromSelection` | F5 (feedback words), S7 (Words task), S3 (Words tile), S1 (Me stats), F2 (quick sheet tab), S4, S3, S6, S8 (gloss and add-from-selection hooks) |
### 2.13 Acceptance checks changed by the resolutions
| section | the check says | read it as | why |
| 3.6 Plan | `/cal/<token>.ics`; `POST /links {view:true}` | `/api/cal/<token>.ics`; `POST /api/share` (progress link), then `GET /api/plan/shared/<token>` | R18 |
