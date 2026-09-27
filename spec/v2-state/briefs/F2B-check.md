# Check brief for F2B: Shell follow-ups (Part 3.1 §2 is the part that matters)

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

(see the task prompt)

## The section's acceptance list

### 3.1.8 Acceptance checks

1. At 1280x900, every page except /practice/session/ and /test/ shows a 248px left sidebar listing, in order: Search, Quick, Today, Practice, Mistakes, Tests, Plan, Results, Challenge, the Today card, Help & FAQ, Send feedback, the user card. Class is absent for a learner in no class. Exactly one nav link has aria-current="page" and it matches the page: /results/report/ → Results, /diagnostic/ → Tests, /mistakes/ → Mistakes, /challenge/ → Challenge.
2. Clicking the collapse button (or pressing [) makes the sidebar 68px (getBoundingClientRect().width === 68), and a reload keeps it collapsed (localStorage satf.rail). Focusing a rail item shows a role=tooltip containing its name.
3. At 900px wide the rail is the default. The toggle opens the full sidebar over a scrim, and Esc closes it.
4. At 390x844, document.documentElement.scrollWidth <= 390 on /, /me/, /me/settings/, /help/, /signin/, /class/ and /share/?t=…. The bottom tabs read exactly Today, Practice, Tests, Plan, Results. Tapping the avatar opens a sheet listing Mistakes, Challenge, Profile, Settings, Sign in (unsaved learner), Pair a device, Join or teach a class, Help & FAQ, Send feedback and Leave this device.
5. For a learner with 14 open traps, the sidebar Mistakes item and the phone top-bar chip both show 14. After all traps close, both are hidden.
6. The Today nav meta reads '12/28' for a learner with a 45-minute plan (per_session 28) who answered 12 today.
7. curl -s -H 'X-Learner: a:v2revshellA' localhost:8000/api/shell returns JSON with keys me, streak, best_streak, today, plan, tested_today, mistakes, saved, challenge, resume, newest_report, assignments, report_replies, new, prefs.
8. One streak: for a learner with plan days '1111100' and answers on Mon–Fri of last week and on today (a Monday), /api/shell streak, /api/me days.streak and /api/today days.streak all equal 6.
9. Study time: after finishing a module sitting that ran 20 minutes, /api/me/activity's today minutes rises by at least 19, although its attempts have ms NULL.
10. The account menu opens on Enter on the user card; ArrowDown moves focus through its items; Esc closes it and document.activeElement is the user card again.
11. Ctrl+K, then typing 'circles hard 5' and Enter, navigates to /practice/session/?id=X, and GET /api/drill/X shows topics ['circles'], count 5, difficulty ['hard']. Typing 'central angle' lists a Question types row; Enter starts a drill whose questions all carry that template.
12. Pressing Q on / opens the quick sheet with a question; answering shows the verdict, and Another (Enter) loads a new one. Closing with 0 answers leaves no sessions row with source 'quick'. Closing after 1 answer puts 'Quick questions' in /api/history, and /api/shell resume stays null. On /practice/session/ and /test/ there is no Quick button and Q does nothing.
13. Log a mistake: POST /api/mistakes/log {template: <a circles template>, reason: <one of GET /api/types?topic=circles reasons>, origin: 'bluebook'} → /api/mistakes lists it with source 'outside'. The attempts count is unchanged. An unknown template → 422.
14. Send feedback with category Bug and details 'x' → POST /api/report returns {id}, and sqlite shows a reports row with kind 'page'. Reporting a drill question, the question of the day and a challenge question each stores context.template and context.seed equal to the stored question, although the client never sent them.
15. POST /api/report with 11 files → 400; with one 11 MB PNG → 413; with one GIF → 200. With category key_wrong for a question in an unfinished mock → 409. In the test window, the report modal's 'Sent with this' box contains no 'marked' text.
16. A dispute (key_wrong, dispute true) on a finished drill miss sets that attempt's disputed = 1. The topic's mastery in /api/map ignores it, and today's minutes in /api/me/activity are unchanged. A 6th open dispute → 409.
17. Admin: with SATF_ADMIN_TOKEN unset, GET /api/admin/reports → 404. With it set, PUT {status:'no_change', reply:'Key checked', dispute_outcome:'key_right'} sets the attempt's disputed back to 0 and reopens the trap. The student's GET /api/reports shows the reply as unread, and /api/shell report_replies is 1.
18. Pairing: POST /api/pair as A → {code}. POST /api/pair/request as B → {pending:true} with no name in the body. A allows. B's status shows A's name. POST /api/pair/claim as B → {learner: A}, and B's attempts now carry learner A. Claiming again → 410. 11 wrong codes from one IP within 10 minutes → 429.
19. Email: POST /api/account/link as A writes a mail to server/outbox/ holding a 6-digit code and a /signin/?t= link; POST /api/account/verify {code} as A binds it. Then learner C links the same email. POST verify {token} with X-Learner D returns {other_device: true} and C is not signed in. POST verify {code} as C returns {learner: A}. Five wrong codes → 410.
20. POST /api/account/rotate as A → {learner: A2}. A PUT /api/me with header A → 401 with detail.retired true, and /api/shell with A → {retired: true}.
21. PUT /api/me {prefs:{set_length:22, difficulty:'hard', format:'grid'}} → 200, and /practice/ then opens with 22, only Hard and Grid-in selected. PUT /api/me {prefs:{colour:'x'}} → 422 naming 'colour'.
22. Theme: a fresh learner's page has no data-theme and getComputedStyle(document.body).backgroundColor is rgb(255, 255, 255). After Settings › Theme › Dark, it is rgb(26, 25, 23), and a reload has no light flash. grep -E '#[0-9A-Fa-f]{3,6}\b' on web/test/index.html, web/me/index.html and web/results/report/index.html finds nothing.
23. New learner a:v2revnew on /me/:
   - The H1 is 'Student XXXX'; the stat tiles show 0 / —.
   - Snapshot shows 'Take the diagnostic', 'Start a module' and 'Answer a question this week to be ranked.'
   - Goals shows 'Build my plan'; Learning preferences shows Questions per set 10 selected.
   - The feed shows 'Start today's set', and all 43 achievements are locked.
   - There are no console errors.
24. Seeded learner a:v2revshellhist on /me/: ANSWERED equals SELECT COUNT(*) FROM attempts WHERE learner=…, and ACCURACY equals round(100*SUM(correct)/COUNT(*)) over rows with disputed=0. The heatmap cell for today has a tooltip with today's questions and minutes.
25. The target quick edit on /me/ saves 700 (PUT /api/me {target:700}). /api/today profile.target and the Plan wizard's step 2 then both show 700. The exam-date popover lists no date earlier than today.
26. Practice rank: two learners with the same exam_date, where the first has more right answers in the last 7 days. The first is #1 of 2 in the 'Sitting …' line. After the second sets board 'hidden', the first's line reads #1 of 1, and the second still sees their own rank.
27. After a learner's 50th answer, the next shell page shows a toast containing 'Questions answered'. After POST /api/me/achievements/seen, the next load shows none. GET /api/me/achievements has answered.earned[0].at equal to the 50th attempt's at.
28. Board privacy: with board 'hidden', GET /api/challenge/board omits the learner from entries and players, but `you` still has a rank.
29. POST /api/share → token. GET /api/shared/{token} with no X-Learner returns stats, and its body contains neither the email nor the learner code. After DELETE /api/share/{token}, GET /api/shared/{token} → 404, and /share/?t= shows 'This link was turned off.'
30. GET /api/me/export returns Content-Disposition: attachment, and its attempts array length equals the DB count. DELETE /api/me {confirm:'DELETE'} leaves 0 rows for that learner in every listed table, and the players count of a challenge board they played is unchanged. Without confirm → 422.
31. A fresh browser whose first page is /test/?s=… ends up with localStorage satf.learner matching ^a:[0-9a-z]{24}$.
32. With /api blocked in the browser, pages show the offline banner 'Can't reach SAT Freshman' with Retry now, and the nav links still work.
33. Classes:
   - POST /api/classes as an unsaved learner → 403 {need:'save'}; as a saved one → {id, code}.
   - Two students join with display names.
   - A fresh 5-question set assignment gives the two students different stems.
   - same:true gives both identical (template, seed) lists.
   - After one student misses a question with a named reason, GET /api/classes/{id}/assignments/{aid} lists that label with members 1.
   - No teacher response contains an email or an 'a:' learner code.
34. GET /api/cal/{token}.ics contains 'RRULE:FREQ=WEEKLY;BYDAY=' and 'BEGIN:VALARM', and matches UI.ics() for the same learner. After DELETE /api/cal it returns 404.
35. /manifest.webmanifest is served and linked from every page, with 192 and 512 icons.
36. Every icon-only button in the shell has an aria-label. The skip link is the first Tab stop and moves focus to main. Every dialog closes on Esc and returns focus to its trigger.
37. PYTHONPATH=. python3 server/test_flow.py passes.


## The upgrades' acceptance items (spec/v2-upgrades/shell-me.md)

**Acceptance.**
1. A learner with one trap due for a check-in today and one open trap: `GET /api/next`
   `items[0].kind == 'checks'` and `items[1].kind == 'redo'`. With an unfinished module that
   has time left, `items[0].kind == 'resume'`.
2. `curl -s -H 'X-Learner: a:v2revnextA' :PORT/api/shell` has `next`, an array of 3 or fewer
   items, each with `title`, `minutes` and `start` or `href`.
3. On `/me/` at 1280, `G` then `N` navigates to `/practice/session/?id=X`, and
   `GET /api/drill/X` has `cfg.pool == 'checks'`. On `/practice/session/` and `/test/`,
   `G N` does nothing.
4. `POST /api/drill {source:'next', box:15}` returns a session with `cfg.box == 15` and
   `count == null`. For a learner with traps in 2 topics, no two consecutive served questions
   share a topic.
5. "Not today" on item 1 hides it on reload for that local day. The next day it is back.
6. A learner whose exam is tomorrow gets one item whose title starts with "Rest".
7. A learner with `gains.skills.probability.gain == 20` and 10 wrong first-try Probability
   attempts in 60 days, 3 of them on one open trap: that trap's `redo` item has `pts == 6`.
   A `checks` item has `pts == null`, and its rendered meta contains no "pts".
8. A learner whose plan today holds a check-ins task, with 2 check-ins due: `GET /api/next`
   has exactly one item whose start body has `pool == 'checks'`, and its reason contains
   "also in today's plan".
9. A brand-new learner: `items[0].title` starts with "Take a module", and no item before the
   diagnostic ends in a sign-up form. With `deps.part('compete','closing_soon')` absent,
   `GET /api/next` still returns 200 and has no `contest` item.


**Acceptance.**
1. `GET /api/types/match?id=23c5fcce` → `rows[0].via == 'id'`, `topic == 'circles'`, and a
   template in `GET /api/types`.
2. `POST /api/types/match/pick {cb_id:'23c5fcce', letter:'C'}` returns a non-empty reason
   equal to one of that template's surveyed reasons.
3. A check in `server/checks/f5.py` walks every key: at least 900 IDs resolve with
   `via:'id'` onto a served template.
4. No `/api/types/match` response contains any 40-character substring of an official stem
   (a check in `server/checks/f5.py`).
5. Logging from an ID opens a trap with `source 'outside'` and `origin 'cb_qbank'`, and the
   attempts count is unchanged.
6. A whole-test log with misses in 3 skills creates a set of 6 questions over those 3
   topics, and `/api/scores` lists the outside score.
7. `GET /api/types/match?id=ffff0000` (not in the keys) → 200 with
   `[{via: 'none', cb_id: 'ffff0000'}]`, never `[]`, and `cb_unknown.n` for that ID is 1.
   The sheet shows "We don't have ffff0000 yet", the text box has focus, and the skill chips
   are visible.
8. `GET /api/types` → `cb.known` equals the number of distinct IDs in `material/keys`
   (1,039 today), and the helper text prints that number.
9. `POST /api/mistakes/import` with 2 known IDs and 1 unknown → 3 rows, one with
   `matched: false`. Picking a skill for it adds that skill's 2 questions to the follow-up
   set.


**Acceptance.**
1. A finished drill miss on an MC question whose option C has a reason, on a template seeded
   with 20 Strong learners' first-try answers (1 of them on C's norm) and 100 others (15 on
   it). `POST /api/report {category:'key_wrong', answer:'C'}` → `check.outcome ==
   'explained'`, `check.reason` equals that item's `reasons[2]`, and `check.text` contains
   "numbers check out" and not "Checked:". The attempt's `disputed` stays 0. After
   `/accept`, GET /api/reports shows status `no_change`, and a 6th key report is still
   allowed.
2. A seed that `check_item` fails (a fixture that monkeypatches the check) → `broken`,
   `disputed = 1`, and `POST /api/drill {templates:[t], count:50}` never serves that seed.
3. Two learners report the same (template, seed). The second modal's `GET
   /api/reports/similar?session=&qid=` returns `{open: 1}`. Add me to it stores a row with
   `parent` set.
4. Admin "Key was wrong · every seed since" on a template with attempts from 2 learners sets
   `disputed = 1` on all of them, and each learner's feed has a `correction` item.
5. A report from a live mock returns no `check` and no key. After finishing, an inbox item
   "Report #n checked" exists.
6. `GET /api/reports/fixed` contains no learner id, name or email.
7. A fixture whose stem text contradicts its params (the stem asks for the diameter; the
   params compute the radius), with no answers on file → `check.outcome == 'unsure'` (thin),
   never `explained`, and the report is status `new` in admin.
8. The same fixture with 20 Strong learners of whom 12 picked C's norm, against a base rate
   of 15% → `unsure` with `check.signal.strong == 0.6`, and the attempt has `disputed = 1`.
9. `category: 'figure'` on any question → no lesson text in the response, and status `new`.
10. A report with a 40 MB GIF → 200, and the file is on disk at its full size. A 20 MB
    `video/webm` → 200. A 60 MB GIF → 413 naming the 50 MB limit. A `application/zip` → 415.


**Acceptance.**
1. A seeded learner: circles 10 answers at 30% right, linear_functions 20 at 90%, and 30 more
   spread over other skills. `gains.skills` has circles' gain > linear_functions' gain, and
   /me/ lists Circles above Linear functions under "By points".
2. `python3 server/estimate.py` passes asserts:
   * raising any single skill's accuracy never lowers S;
   * `gains` for a learner at 100% everywhere is all zeros;
   * `need(700).m1_min == 14` and `need(560).m1_min is None`;
   * `need(800).reachable is False` and `need(800).ceiling == 780`;
   * for every target from 200 to 780 in tens, `scoring._interpolate(right_of_44 / 44) >=
     target`, and `(right_of_44 − 1) / 44` falls short of it;
   * `scoring.route_after(m1_min, 22) == 'upper'` and `route_after(m1_min − 1, 22) ==
     'lower'`.
3. A learner with 12 answers: `gains == null`, and the card shows "Answer 30 questions".
4. The target popover for 700 contains "of 44" with an integer from 0 to 44, and "14 of 22 in
   module 1". For 560 it has no "module 1" text. For 800 it names 780.
5. `PUT /api/me {target:700, rw_target:700}` → `summary.goals.total.target == 1400`, and
   `/`, `/plan/` and `/me/` all render "1400".


**Acceptance.**
1. A learner with 6 circles answers: the circles row contains "rough · 6 answers". With 4 it
   contains "Not measured yet · try 5" and no gain. With 0 it reads "Not started". With 26
   it contains "measured".
2. `POST /api/drill {source:'probe', count:12}` for a learner with 6 rough skills → 12
   questions over 4 to 6 topics, all rough ones.
3. A skill at mastery ≥ 0.8 whose last answer is 11 days old shows "Fading" and a Keep warm
   link that posts `{pool:'review', topics:[t], count:3}`.


**Acceptance.**
1. `python3 server/habits.py` exits 0 and prints 11 families, each spanning ≥ 3 topics.
2. A learner with 3 traps whose reasons tag `whole_part` across 2 topics →
   `summary.habits[0].id == 'whole_part'` and `skills` has 2 entries.
3. `POST /api/drill {source:'habit', habit:'whole_part', count:8}` → 8 questions. A check in
   `server/checks/f5.py` regenerates each and finds an option reason matching the family.
4. `POST /api/drill {source:'gauntlet', count:10}` for a learner with traps on 2 templates →
   at least one served template is not a trap template, and has an option whose norm equals
   a trap norm.


**Acceptance.**
1. A learner with 6 timed right answers in circles at a median of 150 s and 90% accuracy:
   `pace.skills.circles.quadrant == 'slow_right'`, and the card offers "Speed drill".
2. `forecast.seconds` equals the sum of the per-slot medians (a unit assert in
   `server/checks/f4.py`).
3. A learner with 25 guess-tagged answers, 7 right → the line reads "28%".


**Acceptance.**
1. `GET /api/types`: the weights sum to 1 (±1e-6). The circles weights sum to
   7/44 × 67/348 (±1e-6).
2. A learner with 2 first-try rights on the heaviest circles template has
   `readiness == that weight` (rounded to 3 places).
3. At 390px the atlas has no horizontal scroll (`scrollWidth <= 390`).


**Acceptance.**
1. Sittings at midpoints 500 (Sep 1) and 560 (Sep 15), exam Nov 7 → `projection == null`,
   and the chart reads "Three modules over three weeks start a projection."
2. Add a third at 600 (Sep 22), which is a raw slope of about +33 a week. Then
   `projection.mid < 700` (the formula gives about 683), the SVG has a cone path, and the
   hidden table has a "Projected" row. An unshrunk line would have said about 790.
3. Sittings 500 (Sep 1), 530 (Sep 11), 560 (Sep 22), exam Nov 7 → `mid` about 611 and
   `half == 60`. The Nov 7 chip reads "~610".
4. Sittings 500 (Sep 1), 560 (Sep 15), 540 (Sep 29) → `half > 80`, and no exam-date chip
   carries a "~" figure.
5. `python3 server/estimate.py` asserts that a flat series projects its own mean, and that
   no projection moves more than 20 a week after week 4.


**Acceptance.** For a learner with 84 answers in the last 7 days and 0 in the 7 before, the
ANSWERED tile's delta reads "▲ 84", and its sparkline has 14 points.


**Acceptance.**
1. 20 seeded learners with first midpoints within ±40 and varied gains: `ranks.climb.of == 21`
   for a 21st, `window == 40`, and its rank is ordered by gain.
2. With 14 within ±40 and 8 more within ±80 → `window == 80`, `of == 23`, and the line reads
   "Started" followed by the ±80 range.
3. With 19 learners holding a first sitting in all, `ranks.climb == null`.
4. The gap line's number equals the next row's `right` minus yours, plus 1.
5. With `country = 'US'` set → `ranks.country` exists and its `of` equals the US practice
   board's size. With it blank → the "Add your country" line, and choosing a country in its
   popover sends `PUT /api/me {country}` and renders `#n of m` without a reload.
   `PUT /api/me {country:'XX'}` → 422. Settings › Account & devices has the same select.
6. A learner with 8 days of history → `ranks.self.days == 8`, and the line reads "You, 8
   days ago". With 7 days → `ranks.self == null`.


**Acceptance.** A practice set that moved circles from 0.35 to 0.45 shows the row "Circles:
Learning → Getting there". Its Follow up posts a drill whose questions are the set's
still-open templates with fresh seeds.


**Acceptance.**
1. A learner at circles mastery 0.7 with 12 answers: `levers['skill:circles'].next` matches
   `^\d+ more right`. Applying that many right answers (at medium) through
   `progress.mastery_of` reaches ≥ 0.8.
2. Every tile on /me/ is focusable and opens a popover on Enter. Esc closes it and returns
   focus.
3. `/api/me/achievements` rows with `have < next` all carry `go`.


**Acceptance.**
1. `PUT /api/me/week/goals {week, goals:[{kind:'fix_traps', params:{topic:'circles'}, target:4}]}`
   → `/api/shell.goals[0] == {…, have:0, target:4, done:false}`.
2. Closing 4 circles traps → `done: true`, and the feed has a goal item.
3. A 4th goal → 422.
4. The sheet opens once per week per device, and never on `/practice/session/` or `/test/`,
   nor on a load with a query or a hash (U25 acceptance 4).


**Acceptance.**
1. A learner with `exam_date` = today + 30 and no stored prefs: `GET /api/me` has
   `prefs.clock == 'pace'`, `pref_source.clock == 'stage'` and `stage.name == 'build'`.
2. `PUT {prefs:{clock:'off'}}` → `pref_source.clock == 'yours'`. `PUT {prefs:{clock:null}}`
   → back to `'stage'`.
3. With `exam_date` = today + 10 → `prefs.feedback == 'end'`.
4. `PUT {prefs:{mode:'x'}}` → 422 naming `mode`.
5. With `exam_date` = today + 10: `POST /api/drill {pool:'redo', ids:[x]}` → `cfg.feedback ==
   'instant'` and `cfg.repairs == 'next'`, and the first answer's response carries the key
   and the verdict. `POST /api/drill {topics:['circles']}` from the builder → `cfg.feedback
   == 'end'`. The same holds for `checks`, `habit`, `gauntlet` and `quick`.
6. On /me/, Learning preferences has a "Words a day" row that writes `words_goal`, and a
   "Test timing" row that writes `test_timing` (§3.1 override 22).


**Acceptance.** A learner who answers on 7 consecutive study days, misses day 8 (a study day)
and answers on day 9: `/api/shell.streak == 8`, `spares == 0`, and day 8 has
`spare_used: true`. With the day-8 miss before any 7-day run, the streak breaks.


**Acceptance.**
1. With `exam_date` = a date whose `register_by` is 5 days away and `registered` null, the
   banner text contains "5 days left".
2. `PUT {prefs:{registered: exam_date}}` hides it.
3. The `.ics` feed contains a `SUMMARY` starting "Register for".


**Acceptance.**
1. (a) For a learner with 3 check-ins due tomorrow, tomorrow's VEVENT SUMMARY is "SAT Math ·
   Up next · 25 min" (no count), and its DESCRIPTION contains "/?next=1".
2. (a) The Google button's URL contains `action=TEMPLATE`, `ctz=` and
   `recur=RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR` for a Mon–Fri plan. The downloaded `.ics` has
   one VEVENT with an RRULE and a VALARM.
3. (b) With the VAPID env unset, the first start writes `server/vapid.pem`, and
   `GET /api/push/key` returns a public key. With `SATF_PUSH=off`, `/api/push/*` → 404 and
   Settings shows no row.
4. (b) A subscription row is created, and `POST /api/push/next` returns text naming the
   first Up next item. After that item is done, the next call names the new first item.
5. (b) No page calls `Notification.requestPermission()` outside a click handler (a check
   greps `web/**` for the call and asserts each one sits in a listener).
6. (b) With `study_time` 22:30, `remind` 10 and the default quiet hours, the scheduler (a
   test clock) sends the study reminder at 22:20. The streak nudge due at 20:30 with quiet
   hours `{from:'20:00', to:'07:00'}` is not sent inside the window.
   `PUT /api/me {prefs:{quiet:{from:'23:00', to:'06:30'}}}` → 200, and `{from:'25:00'}` → 422.


**Acceptance.**
1. `server/checks/s1.py` registers a credential made with `cryptography`'s P-256 key, using a
   hand-built `authData` and `clientDataJSON`, then logs in with a valid signature →
   `{learner}`.
2. The same login with a wrong origin → 400, a reused challenge → 400, and a bad signature
   → 401.
3. After registering, `GET /api/account` shows `saved: true` without an email. That
   passkey-only learner finishes a diagnostic, and its results endpoint → 200 with no sign-up
   form rendered. An unsaved learner's → 403 `{need: 'signup'}`.
4. The `/signin/` field has `autocomplete` containing `webauthn`. In Chrome with a CDP
   virtual authenticator (`WebAuthn.addVirtualAuthenticator`, internal, resident key, user
   verification) holding a registered credential, loading `/signin/` sends one
   `/api/passkey/login/options` with `conditional: true`, and completing the conditional
   request signs in (`satf.learner` starts `d:`). With `SATF_WEBAUTHN_TTL=10`, a second
   options call is sent before 10 s have passed.
5. A sign-in with "This is a shared computer" ticked, on a device whose learner has 24
   answers, leaves the account's attempt count unchanged (`/api/me/summary` before and
   after), offers no Add, and leaves `localStorage satf.learner` unchanged.
6. A non-shared sign-in whose newest local answer is 30 h old focuses **Don't add them**.
   Choosing Add raises the account's attempt count by 24. `POST /api/passkey/login` with no
   `carry` field moves nothing.
7. After an email-code sign-in, a fresh visit to `/signin/` (no hash) opens on the Email
   tab.
8. `GET /api/health` has `mail`. With `SATF_SMTP_HOST` unset it is `'outbox'`, and the Email
   tab shows the "aren't switched on" text with a Passkey button and no code form.


**Acceptance.**
1. With `SATF_GOOGLE_CLIENT_ID` unset: `/api/google` → 404, and `/signin/` has no Google
   button.
2. `server/checks/s1.py` signs an ID token with a test RSA key and points the JWKS fetch at
   it: a valid token → 200 with a credential starting `d:`. A wrong `aud` → 401, an expired
   token → 401, `email_verified: false` → 401, and a reused nonce → 400.
3. A token whose email matches an existing saved user signs in to that learner, with no
   answers moved when `carry` is missing. A token with a new email saves this device's
   learner: `account.saved` is then true, and a second sign-in with the same `sub` but a
   changed email reaches the same learner.


**Acceptance.**
1. As B: `POST /api/link/request` → `{token, code}`. As A: `POST /api/link/code {code}` → the
   request, with B's label and no name.
2. A approves. B's `GET /api/link/{token}` → `{credential}` starting `d:`, and answers B
   records with it are stored under A's learner. A second approve → 410.
3. Deny → B reads `{state:'denied'}`.
4. 11 wrong codes from one IP within 10 minutes → 429.
5. A `session_only` request approved for a learner with 500 attempts, from a computer whose
   anonymous learner has 24: the owner still has 500 afterwards.


**Acceptance.**
1. A passkey or email sign-in returns a `d:` token. `GET /api/devices` as the owner lists it.
   `DELETE /api/devices/{id}` → that token's next PUT gets 401 with `detail.retired == true`.
2. A `session_only` token idle for 16 minutes → 401 `{retired: true}` (a test sets
   `last_seen` back), and one used within 15 minutes but created 12 h ago → 401. After
   `/leaving` with no ping for 61 s → 401; a ping within 60 s keeps it working. Two page
   loads in a row in one tab (with the `pagehide` between them) keep the session. A tab
   restored after the token died shows the "session has ended" banner and paints no cached
   card.
3. No response to a `d:` device contains the learner's `a:` code (a check greps every
   endpoint body in `server/checks/s1.py`).
4. Browser A holds `a:X` and registers a passkey. Then A's `satf.learner` starts with `d:`,
   and `GET /api/devices` lists A. Browser B, which also holds `a:X`, calls `GET /api/shell`
   → 200 with an `X-Learner-Swap` header starting `d:`, B's next call uses it, and the
   devices list shows B. After **End the old code now**, `X-Learner: a:X` → 401
   `{retired: true}`.
5. `POST /api/transfer` → `{code}`. Redeeming it on B gives a `d:` token that
   `GET /api/devices` lists. A second redeem → 410, and a redeem after 10 minutes → 410.
6. Sign out on a saved device, then fire `pagehide` within 8 s: a keepalive DELETE is sent,
   and the token then gets 401. Undo within 8 s instead → the token still works, and no
   DELETE was sent.
7. After Sign out, `satf.profiles` has no entry with that token. A shared-computer Sign out
   sends the DELETE at once and shows no Undo.
8. With `satf.family` unset, Students on this device is not rendered, unless a parked
   unsaved code exists.
9. On a family device with two profiles, switching changes `X-Learner` on the next
   `/api/shell` call.
10. The diagnostic's confirmation link, opened with no `X-Learner`, verifies the email:
    `account.saved` becomes true, and the laptop's next request with `a:X` → 200 with a swap
    header, never 401.


**Acceptance.**
1. `/api/shell.me.domains` has 4 numbers from 0 to 1.
2. `PUT /api/me {avatar:'circles'}` for a brand-new learner → 200. After the circles badge is
   earned, `/api/shell.me.avatar.ring == true`.
3. The avatar SVG's aria-label names all four domains.
4. No board payload contains domain mastery: a check in `server/checks/s8.py` fetches every
   board endpoint (`/api/compete/*` boards, the challenge board, practice ranks) for a board
   holding a learner whose avatar is the living mark, and finds no `domains` key and no
   mastery figure. That learner's row shows the initial.
5. Choosing a 3 MB JPEG as the photo: the user card and Me show an `<img>` with a `blob:` URL
   no larger than 256×256, the network log shows no request carrying image data, and a board
   still shows the glyph or initial. Remove shows "Your … will be shown instead", and after
   it IndexedDB `photo` has no entry for the learner. On a shared-computer sign-in the photo
   tile is absent.


**Acceptance.**
1. `PUT /api/me {name:'José'}` → 200, and `{name:'李明'}` → 200. `{name:'Dana2'}` → 422
   naming `name`.
2. Two learners both `PUT {name:'Emma'}` → 200 each. Both `PUT {handle:'Emma'}` → the second
   gets 409 naming `handle`.
3. No board payload (the `server/checks/s8.py` sweep of U22) contains a learner's `name`;
   rows show `handle` or "Student 4F2A".
4. `/me/`'s H1 shows the name, and its "On boards" line shows the handle.


**Acceptance.**
1. Chrome at 1280: after a 200 ms hover, clicking a nav item paints a real card (not a
   `.skel`) within 100 ms of `performance.getEntriesByType('navigation')[0].activationStart`.
2. Safari and Firefox, on a second visit: cached content is painted within 50 ms of
   DOMContentLoaded.
3. A prerendered `/me/` sends no POST before activation (checked through the network log).
4. Prerendering `/results/` without activating it (a hover, then moving away) leaves
   `localStorage satf.seen.report` unchanged, and the sidebar's Results "New" dot is still
   shown. Activating it then updates `satf.seen.report`.
5. A prerendered `/` on the first load of the week opens no sheet and writes no shown-once
   flag. On activation the week sheet opens.


**Acceptance.**
1. ⌘K, type "target 700", Enter → `PUT /api/me {target:700}`. The toast has Undo; Undo sends
   the previous target.
2. "calculator" lists `calc_button` with its current value.
3. `GET /api/prefs` contains every key of §2.7, each with a label.
4. "why band" lists the Help answer on bands.


**Acceptance.**
1. A new achievement shows in `GET /api/me/feed?unread=1`. After `POST /api/me/feed/seen` it
   does not.
2. A learner without a plan whose last attempt is 3 days old sees the welcome-back sheet
   once. A reload does not show it again.
3. Unsave → Undo → `GET /api/saved` contains the question again.
4. A Mon–Fri learner (an active plan, rest on Sat and Sun) whose last answer was on Friday:
   the first clean load on Monday opens exactly one sheet, the week sheet, with no
   welcome-back block. `/?next=1` on Monday before that opens the session with no sheet,
   and the week sheet then opens on the day's next clean load.
5. The same learner inactive since the previous Wednesday: Monday's first clean load opens
   one sheet, the week sheet, with the welcome-back block at its top.
6. With 20 unread items, the account menu renders 3 inbox rows and "See all (20)".


**Acceptance.**
1. **Height budget.** With all 9 nav items, at 1366×657, 1440×790, 1280×900 and 1280×500:
   every nav item's `getBoundingClientRect()` lies inside the viewport, and the sidebar's
   `scrollHeight == clientHeight`. At 1366×470 the nav region scrolls and the active item is
   in view. At 1920×1100 the full Up next block and the full Today card are in the sidebar,
   and no Now strip is drawn.
1a. **Nothing behind a hover.** At 1366×657 on `/me/`, with a Today card that has every line
   (spares, minutes, registration, a contest closing, the exam footer): the Now strip is in
   the viewport, and the Up next reason, its meta and every Today card line are visible
   text nodes (no `title` attribute or popover needed). After scrolling 1,000px, the section
   bar shows "Up next:" and a Start button, and `G N` still starts item 1.
2. With a plan, the Today card contains no "of 28 questions" text while the Today item reads
   "12/28", and the Plan item's meta never matches `^\d+ q$`.
3. At 1280 on /me/: the Profile item has `aria-current="page"`, and the section bar has 16
   chips. Scrolling to Skills sets `aria-current` on the Skills chip. At 390 the same 16 chips
   render.
4. On /help/ at 1366×657, the section bar lists Help's groups, and acceptance 1 still holds.
5. **Phone.** At 390×844 and at 360×740, with a Review count of 114: tapping the grip opens
   the menu sheet. The Review cell lies inside the viewport without scrolling the sheet.
   `document.documentElement.scrollWidth <= innerWidth`, and the top bar's
   `scrollWidth <= clientWidth`. Holding Practice for 500 ms lists "Log a mistake".
6. **Menu.** For a saved learner with 20 unread items, `End` from any item focuses Sign out,
   and ArrowDown from the first item reaches it in 12 presses. Dark theme has
   `role="menuitemcheckbox"` and toggles with Space while the menu stays open. Keyboard
   shortcuts is a `menuitem` in the Display group, and activating it opens the `?` sheet.
   The header has no focusable descendants.
7. Collapsing Skills on /me/ survives a reload.
8. At 390, `scrollWidth <= 390` on /me/ with every card collapsed and expanded.


**Acceptance.** Two learners open the same twin code and get the same template with different
seeds. The owner's results list both, with time and right.

---

## 3. Spec overrides


## Contracts and amended checks

| # | topic | what disagreed | decision | owner |
| R1 | Navigation | Shell keeps 5 phone tabs; Compete, Words and Review each add a 6th tab | **Desktop sidebar (Shell §2.2), final items.** STUDY: Today, Practice, **Review** (badge: open mistakes; replaces "Mistakes"), **Words**, Tests, Plan, Class (only when in or teaching one). PROGRESS: Results, **Compete** (replaces "Challenge"). **Phone: 5 tabs stay** Today · Practice · Tests · Plan · Results. Review, Words, Compete, Class, Profile, Settings and Help sit in the avatar menu sheet, each at most two taps away; the phone top bar's count chip is Review's. The 6-tab bars in Compete §2, Words §1 and Review §1 are not built. G-keys: G M Review, G W Words, G C Compete (see §2.8). Nav metas: Review "● 14"; Words "12 due"; Compete as Shell's Challenge meta (New / Resume / #4). | F2 |
| R2 | Mistakes page | Shell and Today link `/mistakes/`; Review replaces it | `/review/` is the page (Review spec). `/mistakes/` redirects (307, served by `api_review.py`) to `/review/?tab=redo`, keeping the query. Every "Mistakes" reference in other specs means Review. Mistakes logged from outside (Shell §2.7) appear in Review's Redo tab with a "Logged by you · Bluebook" chip and their note. | S10 |
| R3 | Challenge | Shell keeps `/challenge/` and a practice-rank board at `/challenge/#practice`; Compete replaces it | Compete owns all competition. `/challenge/` redirects (307, served by `api_compete.py`, as Compete §2 says) to `/compete/contest/?id=daily`. Shell's **practice rank** (right answers, rolling 7 days, scopes everyone / same exam date / each class) is Compete's leaderboard metric `right` with period `7d` and a new scope `exam`; the Me snapshot reads it from Compete. `/challenge/#practice` links become `/compete/leaderboard/?metric=right&period=7d`. | S8 |
| R4 | Classes vs groups | Shell has classes/members/assignments; Compete has groups/group_members | **One concept: Class** (Shell §7 tables and `/api/classes`). Compete's groups are classes: the Group board scope is a class's current members; a group contest is a private contest with `grp` = class id and a due time; Me's "Groups" list is the classes list. Creating a class needs a saved email (Shell rule, also for Compete's "Create a group"). Joining needs nothing. One code alphabet and namespace for class codes and contest codes (`^[A-HJ-NP-Z2-9]{6}$`, `db.new_code()`), and `/join/?c=` resolves either. `/api/groups` is not built. | S2 (Compete reads `members`) |
| R5 | Mark vs Save | QBank merges marking into saving (as TopTierPrep does); Review keeps them apart | **Two things everywhere** (Review model). *Mark for review* = a flag on one question in one sitting (`flags` table, flag icon, per sitting). *Save* = keep a question for good (`saved` table, bookmark icon). QBank's "rename Saved to Marked for review" is not done; its builder gets two pools, Marked and Saved. QBank's "a right replay removes it from Marked" is not built; Review has Unmark / Unsave with Undo. The Report button's icon is a speech bubble with "!", never a flag. | F4 (tables), S10 (endpoints) |
| R7 | Per-question time, trail, strikes in tests | Report adds `sessions.times` and `sessions.trail`; Review adds `sessions.times`; Tests adds `sessions.qstate` | **One column `sessions.qstate`** (JSON): per qid `{ms, struck, conf, trail, first, changes}` and `_session {away_ms, away_n, late}`. Flags are not in it (R5). The runner sends `ms` (dwell delta) and `made_left` with each answer save and other deltas with `POST /api/session/{sid}/state`. `record_paper` passes `qstate[qid].ms` into `attempts.ms`, so tests count as study time and per-question time. Report's `/flag` and `/time` endpoints are served by Review (flags) and Tests (`/state`). | F4 (column, record_paper), S5 (endpoints) |
| R8 | Attempts columns and what counts | Review adds norm/repeat/repair/flagged/stem; QBank guess; Shell disputed; Compete sms/void | **One set of new `attempts` columns:** `norm, repeat, repair, flagged, guess, disputed, sms, void, stem`. Mastery, accuracy, boards and ranks leave out rows with `repeat=1`, `disputed=1` or `void` set; a right answer with `guess=1` counts half. Study time and question counts keep every row. A **clean answer** (closes a mistake, counts as a check-in) is right, not a repeat, not flagged and not a guess. `progress.record` computes `repeat` itself for every caller. | F4 |
| R9 | Traps and check-ins | Review rebuilds traps (id, norm, kinds, relapses) with check-ins at 7/21 days; Plan wants rechecks at 3/10/30 via stage/due; Shell adds source/note/origin | **One `traps` table:** Review's rebuild (integer `id`, `norm`, `reason` = latest concrete text, `closed_how`, `relapses`, `seed`, `session`) plus Shell's `source` ('outside'), `note`, `origin`, plus **one check-in schedule: 3, 10 and 30 days after fixing** (Plan's), stored as `due` + `checks` (0 to 3). A miss on a due check reopens it as Relapsed. Plan's Rechecks task is the drill pool `checks` (R10); Review's "Check these now" and "CHECK-INS DUE" use the same. Kinds: misconception, gridin (named when the template has `spr_mistakes`), slip, unsure. | F4 |
| R10 | Drill body | Nine sections add their own fields to `POST /api/drill` | **One body contract (§2.6)**, validated in one place and built by F5. Section field names map onto it (table in §2.6). Fields that need another section's data stay on `POST /api/drill` and are resolved by the owner's module through a registry: `like` (S3, `daily.resolve_drill`), `word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2, `classes.resolve_drill`); contests are started by S8's own routes. `list` is accepted as an alias of `pool`, so Review's bodies work unchanged. | F5 |
| R11 | Preferences | Shell prefs, QBank prefs, Tests `learners.test_prefs`, Words `words_goal/words_from/gloss` columns, Shell `study_time` column | **One `learners.prefs` JSON and one registry `server/prefs.py`** with every key in §2.7. The separate columns are not added. Settings (S1) renders every key; the Practice builder, the test start sheet, Plan step 4, Me and the session's More menu write the same keys. Unknown key or bad value → 422 naming the key; only non-default values are stored; GET returns defaults merged. | F4 |
| R12 | Board identity and names | Shell `learners.board` name/anon/hidden and NAME_OK (no digits); Compete `learners.public`, `country`, HANDLE_OK, uniqueness | `learners.board` = `name` \| `anon` \| `hidden` plus `learners.country` (ISO alpha-2, blank by default). `anon` lists the handle ("Student 4F2A"); `hidden` keeps the row at its real rank with the name "Anonymous" and no row menu, so nobody else's rank moves (Compete's fix). A student always sees their own rank. **Board names follow Compete's rule:** 3 to 24 characters (letters, digits, space, `_ . -`), unique case-insensitively (409), reserved and default-looking names refused (422). NAME_OK stays for the diagnostic sign-up; class display names are 1 to 40 characters. Deleted learners' challenge rows are keyed `gone:…` and show as a handle. | F4 (validation), S8 (boards) |
| R13 | Streak and study time | Shell, Today, Plan and Words each define a streak or minutes rule | **One function `progress.days(learner, tz, weeks)`**, used by the shell, Today, Me, Plan, Results and Words. A day is the learner's local day (X-Tz). A study day has at least one answer, or at least 10 word reviews, or a finished sitting. Rest days of the **active plan** (a weekday off, a day off, the exam's eve) neither break nor extend the streak; a rest day with practice extends it. Minutes = attempt ms (each capped at 10 min) + each finished sitting's elapsed time **only when its attempts carry no ms** (capped per module at its clock + 60s; untimed 90 min) + word reviews (each ≤ 60 s) + minutes of the student's own plan tasks marked done. Returns streak, best, active days, minutes and per-day rows for up to 53 weeks. Today's three labelled streaks are three facts: study (this), day's questions (`daily.qotd_streak`), challenge (`compete.challenge_streak`). The 60-minute after-midnight grace applies to the question of the day only. | F4 |
| R14 | Plan arithmetic | Shell and Today compute plan days on the client (`UI.plan.dayOf/doneOf`) and add `plan_marks`; Plan puts all of it on the server | **Server only, `server/plan.py`** (Plan spec). `UI.plan.dayOf/testOf/doneOf` are deleted. Today's plan list, the shell's Today and Plan metas, the Today card and Me's week dots read `/api/today.plan` and `/api/shell.plan` (Plan provides `plan.today_summary()`). Today's Skip / Move use Plan's `PATCH /api/plan/{id}/tasks/{task}` (any study day up to the eve, not only this week). Dashboard's `plan_marks` table and `POST /api/plan/mark` are not built. | S7 |
| R15 | Goals and SAT dates | Target/exam date edited on Today, Me and Plan; R&W fields; three copies of SAT_DATES | `target, exam_date, current, minutes, days, tests, focus, rw_now, rw_target` live on `learners`; the active plan mirrors them both ways (Plan §5, `plan.mirror()`), so one edit shows everywhere. Dashboard's `plan_started` is `plans.start`. Upcoming official dates: one constant in `server/satdates.py`, served in `/api/shell.dates`, read by the date pickers on Today, Me, Plan and Compete's seasons. Past dates are never offered. A new `exam_date` must be today or later in the learner's zone. | F4 |
| R16 | Estimate, confidence, percentile, drift | Report, Tests, Today and Plan each define an estimate or percentile; Compete adds a report percentile | **One module `server/estimate.py`:** `estimate(learner)` returns latest, previous, best, range, `mean3` (mean midpoint of the last up to 3 scored sittings within 45 days, added outside Math scores included), combined (≥2 standard sections: mean ± 70/√n), confidence `{level, reason}` with **Tests §2.2's rules and wording**, trend (±20 = steady), routed_up and counted. `percentile(sid)` ranks a sitting among **each learner's first standard sitting of the same kind** (a paper: of that paper), shown only when n ≥ 20; standard = timed official, adaptive, standard module 1, not fixed-route or extended. The Report hero, Tests cards, Results, Today's score card and the report's Ranked pill all use it; Compete's "last 90 days" variant is not built. **Drift** is Plan's rule (mean3 vs the plan's start, ≥ 40 either way; target reached) and Today's drift line shows Plan's `suggest`. | F4 |
| R17 | Report a problem | Shell (10 images downscaled, disputes, admin), QBank (3 × 5 MB BLOBs), Tests (R-#### ids, tools), Report (3 screenshots), Words (10 images) | **One system:** Shell §2.10 and §10 are canonical: one modal `UI.report(ctx)`, up to 10 images (PNG, JPEG, WebP, GIF), stills downscaled in the browser to 2000px, 10 MB server cap, files on disk under `server/reports/{id}/` (git-ignored), bounded disputes (5 open), Your reports with replies in Settings, `/admin/reports` behind `SATF_ADMIN_TOKEN`. Categories per context are the union: Shell's lists, plus Tests' "More than one right answer" and "No right answer", plus Words' "Wrong or unclear definition" (word context). Mid-test reports never show marking and hide key disputes. Rate limit: 10 an hour and 20 a day per learner (429). Ids are integers. `tools/reports.py` is an optional CLI over the same table. | F6 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
| R19 | Access to keys and re-serving | Review defines `access()`; others re-serve items ad hoc | **One rule, `deps.access(learner, template, seed)` → `reveal` \| `kept` \| None** (Review §server). Everything that returns a key or re-serves an exact (template, seed) goes through it: review endpoints, sets, worksheets, the report, the challenge review, permalinks, Words examples. Live-test items and unanswered or same-day challenge items never leak. The permalink `/practice/session/?q=TEMPLATE:SEED` (QBank; Shell's `/q/` is the same route) serves any catalogue item that is not in today's challenge as a fresh one-question drill; the key shows after answering, as always. | F4 |
| R20 | Status colours and glyphs | Report flips nothing; QBank uses wash for correct; Compete/Review differ | **The practice session's semantics, with glyphs everywhere** (§2.3): right = orange, wrong = graphite, plus Mixed (right on a retry) and Repaired (right on the repair after a miss) as two states, skipped, blank, voided, repeat, not reached, answered (exam), flagged, saved, has note, current. One legend component. | F1 |
| R22 | Keyboard | QBank uses C for calculator and S for skip; Review S for save; clashes with choosing C | **One registry `UI.keys` (F2) and one map (§2.8).** Calculator G, reference F, save B, skip S, history Y, highlights L, confidence K. Shortcuts are ignored while typing (Enter and Esc aside) and when `prefs.keys` is off. | F2, F3 |
| R24 | Drills that are not sittings | twin, try, word-example, review pane, spot, quick each have their own list rule | `cfg.inline = true` for sources `twin, try, word-example, review, spot`: never listed as a sitting, never in history, In progress or Resume; their answers file normally (a twin counts on its parent). `quick` sittings are listed in history as "Quick questions", never offered as Resume, and deleted when finished with 0 answers. Any set finished with 0 answered is never listed. | F5 (flag), S6 (history), S4 (drill list) |
| R25 | Achievements | Shell 43 tiered rules and `earned`; Compete 18 badges and `badges`; Words rules | **One engine `server/achievements.py`** and table `earned(learner, id, tier, at)`. Shell's tiered rules are the base. Compete adds only its unique badges (pace-setter, top-ten, weekly-4, sprinter, dress-rehearsal, season-top-10, level-5, level-8, all-rounder); Words adds 50 / 250 / 1,000 known, a collection complete, a 7-day review streak. Overlaps take Shell's tiered rule. Compete's and Words' rules are declared in their own modules (`ACHIEVEMENTS = [...]` in `compete.py`, `words.py`) and imported when present. | S1 |
| R29 | The quick sheet | Shell's floating-button equivalent has Quick question and Log a mistake; Words adds a "+ word" bar button | **One quick sheet (Q key, bolt in the sidebar and phone bar) with three tabs:** Quick question · Log a mistake · Add a word. The third calls `UI.addWord()` from `words-ui.js`. This is their add-your-own-word button, done without covering anything. Words' "+ word" bar button is not built; Words keeps Add to my words on selected text and N on its pages. | F2 (sheet), S9 (`UI.addWord`) |
| R31 | Me's tiles | Shell's 2×3 stat grid; Words and Compete want stats on Me | Me's identity grid becomes **2×4**: Streak, Answered, Accuracy, Study time, Tests, Mistakes fixed (Shell), plus **Words** ("31 known · 12 due") and **Rating** ("Level 3 · 1,084"). Me's Snapshot reads ranks from Compete; Saved & in progress reads Review's counts; Test defaults appear under Learning preferences. | S1 |
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
### 2.13 Acceptance checks changed by the resolutions
| section | the check says | read it as | why |
| 3.1 Shell | the sidebar lists "Search, Quick, Today, Practice, Mistakes, Tests, Plan, Results, Challenge, …" | "Search, Quick, Today, Practice, Review, Words, Tests, Plan, Results, Compete, the Today card, Help & FAQ, Send feedback, the user card" (Class only when in one); `/mistakes/` and `/challenge/` land on Review and Compete, which are then current | R1, R2, R3 |
| 3.1 Shell | the phone menu sheet lists "Mistakes, Challenge, …" | "Review, Words, Compete, Profile, Settings, Sign in, Pair a device, Join or teach a class, Help & FAQ, Send feedback, Leave this device" | R1 |
| 3.1 Shell | "the sidebar Mistakes item and the phone top-bar chip both show 14" | the sidebar Review item and the phone top-bar chip | R1 |
| 3.1 Shell | `PUT /api/me {prefs:{set_length:22, difficulty:'hard', format:'grid'}}` | `{prefs:{set_length:22, tiers:['hard'], formats:['spr']}}` | R11 |
| 3.1 Shell | "GET /api/cal/{token}.ics … matches UI.ics() for the same learner" | "… matches GET /api/plan/ics for the same learner" | R18(b) |
| 3.1 Shell | practice rank: "after the second sets board 'hidden', the first's line reads #1 of 1" | reads "#1 of 2", and the second is listed as "Anonymous" at #2 and still sees their own rank | R12 |
| 3.1 Shell | "with board 'hidden', GET /api/challenge/board omits the learner from entries and players" | the contest board keeps the row at its rank named "Anonymous"; `players` is unchanged | R12 |
