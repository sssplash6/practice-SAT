# Check brief for S6: Results and score report pages

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

**S6 · Results and the score report** (wave 2, port 8026). Builds Part 3.5 in full (the
player from F3, the report dialog from F6), R26, R35, the report's parts of Tests
(`?q=`, peers, notes, confidence, away, changes), Words (redirect), Compete (contest rows,
Ranked pill) and Review (Flagged filter). Owns `web/results/**`,
`server/api_results.py`, `web/assets/results-ui.js`, `server/checks/s6.py`.
State: not started.


## The section's acceptance list

### 3.5.8 Acceptance checks

1. curl -s -H 'X-Learner: a:v2revresults01' localhost:8000/api/session/3gGTd2b44bXqmkY-2Y4hRg/results | jq checks:
   - summary.correct + summary.incorrect + summary.unanswered == asked
   - modules | length == 2, and modules[0].asked == 22
   - every review item has n in 1..22, module in [1,2], status set and ref non-empty
   - every mcq item has reasons | length == 4, with '' at index 'ABCD'.indexOf(answer)
   - mine == true, and seq >= 1
2. The same curl with 'X-Learner: a:v2revsomeoneelse' returns mine == false and the same review. For today's challenge session 0_vHIyVpr8ubxI2bFAqj1A it returns 403 with detail.need == 'owner'.
3. Results for drill bcZjxCZ4bKZZNlcwnv8yAw:
   - domains and topics are non-empty
   - topics[].before and topics[].after are numbers
   - review[].ms is non-null for answered items
   - repair is true for repair questions
   - a drill ended with a question on screen has exactly one review item with status 'not_reached', and summary counts equal asked
4. Start a mock and POST /api/session/{sid}/flag {question_id: first, on: true}. GET /api/session/{sid} includes it in flags. After both modules, results.review for that qid has flagged == true and summary.flagged == 1.
5. Start a mock. POST answers B, then D, then clear, then D for one question. After finishing, its review item has changes == [1, 3, null, 3], and summary.changed.total >= 1.
6. Start a mock and POST /api/session/{sid}/time {times: {qid: 90000}} for several questions, then answer and finish. Attempts rows for that session have ms not null, and GET /api/me days.recent[-1].minutes > 0 for a learner who only sat that test.
7. POST /api/drill {from_session: <mock>, only: [<a correct qid>], scope: 'all'} returns total 1, and its served template equals the original's key with a different seed. {from_session, each: 2} returns total == 2 × misses. {only: ['nope']} returns 409.
8. POST /api/drill {from_session: <mock>, only: [qid], each: 5, source: 'twin'}, then answer one: GET /api/history does not list it, and the parent's results.twins.n == 1.
9. POST /api/mock/new {like: <finished mock>} returns a module 1 whose sorted template keys equal the source's module-1 keys, and every seed differs.
10. GET /api/history?kind=mock&limit=1:
   - returns 1 session with modules[].wrong and modules[].blank arrays
   - an unfinished expired mock shows in in_progress with expired == true
   - two sittings finished in the same second come back newest-inserted first
11. GET /api/stats has estimate.confidence.level in [high, medium, low], days14 of length 14 and domains_over_time. GET /api/skill/linear_functions has recent and sittings. GET /api/skill/bogus is 404.
12. rank.ranked is true on a learner's first mock and false on their second. rank.pct is null while n < 20.
13. For a mock with at least one easy miss, whatif.tier == 'easy' and whatif.estimate.high >= estimate.high.
14. GET results on an unfinished drill returns 409 with detail.kind == 'drill', and the report page redirects to /practice/session/?id=.
15. Browser 1280 on the report:
   - eight tiles whose numbers match summary
   - the legend is visible
   - clicking 'Incorrect' leaves exactly summary.incorrect cells at full opacity
   - the Module 2 select leaves only M2 cells
   - Mistakes refs such as 'M2 Q4' match the grid labels, and all 13 miss rows are in the DOM with no 'Show all' needed
   - cells carry ✓/✕/– glyphs
16. Browser player:
   - clicking a cell sets location.hash to '#q=m1-N'
   - ArrowRight moves within the filter
   - H hides the key, boxes, reasons and explanation, shows 'Answers hidden', and it stays hidden after ArrowRight
   - Esc closes and document.activeElement is the originating cell
   - report/?id=..#q=m2-4 opens at M2 Q4
   - every wrong option shows its misconception without any click
17. Browser: 'Try one like this' renders a second question in the player without navigation. Answering it shows a verdict, and GET /api/map shows one more answered in that topic.
18. Browser: the Report dialog shows the 'Sent with your report' box with the question ID. Sending with category 'key' returns ok, and the question then shows a 'Reported' tag.
19. Browser 390 on the report and the overview:
   - document.documentElement.scrollWidth <= 390
   - grid cells >= 44px
   - the filter chips wrap, with no element whose scrollWidth > clientWidth in the toolbar
   - the player's bottom bar is not covered by #tabs
20. Browser, a new learner (a:v2revempty02) on /results/:
   - no '—' in the estimate card
   - the 'Full section · 70 min' button is visible
   - the 14-day chart renders 14 baseline ticks
   - the sittings empty text shows with a Practise pill
21. Browser: /results/report/?id=nope shows 'That sitting does not exist.' with links to /results/ and /tests/, and no 'QUESTIONS' heading.
22. Browser: the practice session summary contains a link to /results/report/?id=<that set>.
23. Browser: the sittings card for a mock shows 'M1 ✕' chips whose count equals modules[0].asked - modules[0].right - blank count. Clicking a chip opens that question in the report.
24. Browser, page.emulate_media(media='print') on the report: .bar, .tabs and buttons are display:none, and the table of all questions is visible.
25. Challenge: after two learners sit a day's challenge and the day has passed, results.review[i].crowd.n == 2 and crowd.options sums to about 100. The player shows 'x% of 2 students got this right'.
26. POST /api/me/share {on: true} returns a token. /results/?share=<token> in a fresh browser renders the overview read-only, with no Fix or Resume buttons. After {on: false}, the same URL shows a 404 message.
27. PYTHONPATH=. python3 server/test_flow.py passes with the new assertions.


## The upgrades' acceptance items (spec/v2-upgrades/reports.md)

**Acceptance.**
1. `curl -s -H 'X-Learner: a:v2revrep01' localhost:8026/api/session/<finished mock>/results |
   jq '[.ledger.by_cause[].pts]|add - .ledger.total|fabs < 1'` is true, and the same holds for
   `by_tier`, `by_domain` and `incorrect_pts + blank_pts`. Every `.ledger.per_q[].pts >= 0`.
   It holds too for a lower-route mock at the 580 cap (a fixture with Module 1 at 13 of 22 and
   most of Module 2 missed), where each domain alone could otherwise claim most of the gap.
2. `python3 server/estimate.py` passes asserts: an all-right sitting has `total == 0` and no
   rows; flipping any miss never lowers `mid`; every bucket set (cause, tier, domain,
   incorrect/blank) sums to `all_right.mid − mid`; an empty bucket gets 0; relabelling the
   buckets permutes their points and changes nothing else (order-free).
3. A lower-route mock with 13 of 22 right in Module 1: `ledger.route.short_by == 1`, `savers`
   has one qid, and the page contains "1 more right would have earned the harder Module 2".
4. Browser 1280: clicking the Slips segment leaves exactly `by_cause[slip].n` cells at full
   opacity, and the URL gains `cause=slip`.
5. A drill's report has `ledger == null` and a `WHY YOU MISSED` region with counts and no "pts".


**Acceptance.**
1. Target 700 and a sitting whose path has 4 qids: `rescore(right = path).mid ≥ 700`, and
   `rescore(right = path[:-1]).mid < 700` (a check in `server/checks/s6.py`).
2. The Fix primary's POST body has `only` in descending `pts ÷ budget` order and
   `order:'given'`. The served session's templates follow that order (F5 check).
3. `POST whatif {right: [two misses]}` returns the same `mid` as `estimate.rescore`;
   `{right: ['nope']}` → 422; an unfinished sitting → 409.
4. Browser: What if on, click two miss cells → an element `[data-layer=whatif]` appears in the
   gauge and the line contains "+"; Reset removes it.
5. With a plan, Put in my plan creates a task whose `start.only` equals the row's qids, and
   `/api/today.plan` lists it on the next study day.


**Acceptance.**
1. Finish a mock with 3 misses as `a:v2revrep03`. GET results: `second.state == null`,
   `second.unseen|length == 3`, and for every unseen qid a jq check finds none of `answer`,
   `reasons`, `rationale`, `mistake`, `accepted`, `steps`, `diverge`, `wrong_step`,
   `option_steps`, `diagnosis`, `crowd.option_share`; `.judgement.crossed_key` contains no
   unseen qid; no unseen item's `cause.evidence` has the struck-key line (a fixture strikes the
   key on one of them); and no unseen grid-in miss has `cause == 'entry'`. The same checks pass
   for another learner reading the sitting (`mine:false`), on the compare payload, and on the
   CSV (`correct` reads `Hidden`).
2. `POST second` with the key → `correct == true`; the new attempts row has `repeat == 1`, and
   the trap's `owed` is unchanged. The same POST again → 409.
3. `POST seen {qids:[q]}`, then `POST second` for q → 409 `answers already shown`.
4. After a right non-guess second look on a named miss:
   `progress.causes(..., session=sid).per_q[q].cause == 'slip'`, and `second.with.mid >
   ledger.mid`.
5. Browser: the banner shows. Start opens the player with no `.opt.ok` mark and no explanation.
   After Enter the key shows. `Show answers now` removes the banner, and misconception labels
   appear in Mistakes.
6. With `prefs.second_look = false` there is no banner and every key shows.
7. Print repair pack while the offer stands: the confirm sheet appears; Print anyway sets
   `seen_key` on those qids and `second.unseen` becomes empty.


**Acceptance.**
1. `/results/report/?id=<sid>&fresh=1`: the gauge gets `data-animate`, the delta chip is
   present, and the URL no longer has `fresh`. A reload shows no `data-animate`.
2. `PUT /api/me {rw_now: 610}`, then results: `total.low == estimate.low + 610`,
   `total.parts[1].source == 'self'`, and `total.pct.low_pct` equals the total table's value at
   `total.low`. Saving from the inline field adds one `outside_scores` row with `math` null, and
   `/api/stats.estimate` is unchanged.
3. With `prefers-reduced-motion` emulated, the gauge renders its final state with no animation.
4. The first sitting routed up stores an `earned` row for that milestone; the second does not
   show the stamp again.
5. With `rw_target: 700` and `target: 700`, `total.gap.math_path` equals SR2's path and the
   hero shows both split rows.


**Acceptance.**
1. `python3 server/checks/f4.py` validates the data file as above (61 / 61 / 121 keys).
2. Results for a standard mock: `rank.national.low_pct <= rank.national.high_pct`, and both
   equal the table's values at the band's low and high.
3. With 19 first sittings, `rank.hist == null` and no histogram renders; with 20 the SVG has
   at least 20 circles.


**Acceptance.**
1. A mock with a miss on template t; then two clean right answers on t in a later drill:
   `recovery.recovered` contains the qid, `recovery.now.mid > ledger.mid`, and
   `points_recovered + points_open` equals `ledger.total` within 1.
2. Then a clean wrong answer on t: the qid moves to `slipping`.
3. A right second look (a repeat) on t leaves the qid in `open`.
4. Prove it posts `{kind:'custom', custom:{source:'misses', from_session}}`; the new sitting's
   templates equal the misses' templates, every seed differs, and its report contains
   "Proved".


**Acceptance.**
1. A twin of a finished section: `compare.paired == 44` (22 when the routes differ, with
   `module2 == 'different_route'`), and `slots[i].then.qid` is the source's slot i with an equal
   template.
2. The `counts` of fixed + slipped + still_missing + held equal `paired`.
3. `?vs=` with a sitting that shares 5 templates: `paired == 5`.
4. The compare endpoint for another learner's sitting → 403.
5. Browser: clicking a pair opens two question bodies (`.qbody` count 2); Esc returns focus to
   the pair cell.

---


**Acceptance.**
1. A timed mock finished with 3 blanks at time-up: those qids have `per_q[q].cause == 'clock'`.
2. `POST why {question_id: q, kind: 'misread'}` → `per_q[q] == {cause: 'slip', auto: false}`,
   and `attempts.miss_kind == 'misread'` for that row.
3. The `per_q` count equals `summary.incorrect + summary.unanswered`, and the counts per cause
   equal `ledger.by_cause[].n`.


**Acceptance.**
1. A test with `conf:'sure'` on a wrong answer: `judgement.conf.sure.wrong == 1`, and the
   report's first Mistakes group is "Sure and wrong · 1".
2. `judgement.without_guesses.high <= estimate.high`.
3. `qstate.struck` containing the key's index on 2 questions → `crossed_key|length == 2`.
4. Tags off: clicking the toggle makes `GET /api/prefs` return `confidence: 'ask'`.


**Acceptance.** Asserts in `server/checks/f4.py`: `('0.66', '2/3') → short`; `('1 1/2', '3/2')
→ form`; `('-7', '7') → sign`; `('45', '0.45') → percent`; `('12', '8') → None`. The results
review for a grid-in miss typed "0.66" to "2/3" carries `diagnosis.kind == 'short'`.


**Acceptance.** A sitting with 2 misses whose reasons tag `whole_part` in 2 topics:
`habits[0].id == 'whole_part'` with 2 topics, and its button posts `{source:'habit', habit:
'whole_part', count:8}`. A norm with 3 hits all time shows a row whose Trap drill posts
`pool:'related'`.


**Acceptance.**
1. On the shipped db, a finished mock with a miss on a (template, tier) where the learner's
   stored `result.odds[q] >= 0.75` (a fixture sets that topic's `skill_ratings` to 1300 against
   an item rating of 1000, E ≈ 0.85): the Should-have-had chip is enabled with a count ≥ 1, and
   choosing it leaves that cell at full opacity.
2. `result.odds` is written at finish and does not change when later practice moves the
   ratings; a sitting without it returns `odds.at == 'now'`.
3. With 19 first tries on (t, medium), `crowd == {n: 19, level, rough: true}` and the player
   header contains "(estimated)". With 20, 16 of them right, `crowd.rate == 0.8` and the header
   reads "80% of 20 students".
4. A challenge item's crowd has no letter-keyed field, and its norm shares sum to at most 100.


**Acceptance.**
1. A mock whose runner posted visits: `pace.visits_recorded == true` and each module's `visits`
   is non-empty.
2. `behind_at` is the first question where elapsed time exceeds the summed budgets by more than
   60 s (an assert in `server/checks/s6.py`).
3. On a fresh db a medium question's `budget_ms == 95000`.
4. An older sitting without visits renders "Visit order was not recorded for this sitting." and
   its bars.


**Acceptance.**
1. The report's regions appear in the DOM in the order above.
2. `results.debrief` has at most 3 items, each with `action`; each card renders one button.
3. Pressing `3` scrolls `#mistakes` into view; `N` opens the player at the first miss.
4. After opening 2 misses in the player, the heading reads "Reviewed 2 of".


**Acceptance.**
1. Shift-clicking 4 cells shows "4 selected", and Fix these 4 posts `only` with exactly those 4
   qids.
2. Colour by Points sets `data-colour="points"` on the grid, and the legend lists the steps.
3. Sorting the table by Worth, descending, puts the largest `worth` first.
4. At 390, the Act-on chips wrap and no toolbar element has `scrollWidth > clientWidth`.
5. At 1280 in the table view: `document.documentElement.scrollWidth <= innerWidth`, the
   `.table-wrap` has `scrollWidth > clientWidth`, `#` and `Skill` keep their `left` offset after
   scrolling the wrap to its end, and tabbing from the wrap through the headers focuses all 18
   (each scrolled into view). The same holds at 390.
6. Print emulation of the table view: two `<table>` elements, the first with exactly the 8
   headers above.


**Acceptance.**
1. Touch-swipe left on the question column moves from item n to n + 1; the same swipe starting
   on a table does not.
2. `See one solved first` renders an item with seed ≥ 900000, an option tagged "Your mistake
   gives", and creates no attempts row.
3. After Finish with the network set offline, the report still paints from the prefetched
   copy.
4. For a type with 4 attempts before this sitting and 1 after it, the trajectory renders 6
   glyphs, with this sitting's marked as current.
5. `python3 tools/steps_coverage.py --section` exits 0 and prints "of N section templates have
   worked steps" with the two numbers equal; `PYTHONPATH=. python3 -m satbank` fails on a
   fixture template with neither steps nor a 3-sentence `METHOD`.
6. For any finished mock, every review item's explanation has non-empty `steps` (a jq check
   over `.review[]` after the key is seen); a practice item on a template without steps
   renders a `.method` block of 3 or more sentences above the rationale.
7. `/results/report/?id=<sid>#q=math-m1-7` and `#q=m1-7` open the same question, and the
   header reads "M1 Q7" (one subject).

---


**Acceptance.**
1. Saving a rule creates a `notes` row with `seed = −1` for the question's template.
2. The briefing returns at most 5 rules and 2 pace facts.
3. For that learner, `/test/?s=<new sitting>`'s lobby contains "Your briefing from".


**Acceptance.**
1. A `timing:'x1.5'` section's report shows "1.5× time" and "Practice only", and its delta
   names a non-standard sitting or reads "First at these conditions".
2. `POST note {note:'tired'}` → `/api/history` lists `note == 'tired'` on that item.


**Acceptance.**
1. A U3 `broken` fixture on a mock question: that sitting's `result.rescored` has 1 entry with
   `how == 'removed'`, the question's review status is `removed` (its cell carries ⊖, not ⊘),
   and `ledger.all_right` is computed over 43 questions.
2. A `remarked` grid-in counts right, and the estimate's `mid` rises or stays.
3. A dispute left open leaves the estimate unchanged.


**Acceptance.**
1. Emulating print on the repair pack page: 2 fresh items per miss, and every fresh seed
   differs from the originals.
2. `GET /api/review/worksheet?session=<live test>&qids=…` → 409.
3. The worksheet's `/s/` code opens as an end-mode set whose answers file.
4. With a second look offered, `P` opens the confirm sheet, and until Print anyway is chosen
   the print DOM holds no unseen miss's key or misconception.


**Acceptance.**
1. A learner with an outside score: the chart SVG has a diamond whose aria-label names its
   source. A learner with two R&W entries: the R&W lane has 2 points.
2. Two standard sittings 14 days apart: the SVG has a cone path, and the estimate card contains
   "At this pace".
3. The tooltip on the gap between two points contains "questions".


**Acceptance.**
1. A learner with 3 scored sittings: `/api/stats.gap.by_cause` exists and every `pts >= 0`.
2. For each `why[i]`, the counts sum to that sitting's misses.
3. The Types met tile's number equals U8's count for the learner.


**Acceptance.**
1. `/api/history?kind=tests&sort=points_open` is ordered by `recovery.points_open`, descending.
2. Space on a focused card expands `.peek` containing a gauge; Enter opens the report.
3. `X` on two cards shows the Compare bar with a link containing `vs=`.


**Acceptance.**
1. Results for `sample-section` as any learner: `mine == false`, `ledger` non-null, 13 misses.
2. The page contains "Sample report", and the Fix button is disabled.
3. Any POST to that sitting (`second`, `why`, `note`, drill `from_session`) → 403, and any
   write with `X-Learner: sample:x` → 403.
4. On a db, record `rank.n` of a standard mock, `crowd.n` of an item, every `item_ratings` row
   and the daily board; delete and recreate the sample (`init()`): all are unchanged.
5. The sample's `recovery.timeline` days are all after its `finished`, and two rebuilds give
   byte-equal results payloads.


**Acceptance.**
1. A retry-mode drill with one question wrong then right: its review status is `mixed`, its
   cell carries `~`, its `tries|length == 2`, and the player shows two try rows.
2. A daily with one skip and one void: the report's hero and tiles show the same `right`,
   `wrong`, `skipped`, `voided`, `points` and `points_parts` as `GET /api/contest/daily`'s
   `.me.result`, and the Skipped and Voided chips read 1.
3. A question removed by a correction has `data-status="removed"` and ⊖; no cell outside a
   contest sitting carries ⊘.

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
| R15 | Goals and SAT dates | Target/exam date edited on Today, Me and Plan; R&W fields; three copies of SAT_DATES | `target, exam_date, current, minutes, days, tests, focus, rw_now, rw_target` live on `learners`; the active plan mirrors them both ways (Plan §5, `plan.mirror()`), so one edit shows everywhere. Dashboard's `plan_started` is `plans.start`. Upcoming official dates: one constant in `server/satdates.py`, served in `/api/shell.dates`, read by the date pickers on Today, Me, Plan and Compete's seasons. Past dates are never offered. A new `exam_date` must be today or later in the learner's zone. | F4 |
| R16 | Estimate, confidence, percentile, drift | Report, Tests, Today and Plan each define an estimate or percentile; Compete adds a report percentile | **One module `server/estimate.py`:** `estimate(learner)` returns latest, previous, best, range, `mean3` (mean midpoint of the last up to 3 scored sittings within 45 days, added outside Math scores included), combined (≥2 standard sections: mean ± 70/√n), confidence `{level, reason}` with **Tests §2.2's rules and wording**, trend (±20 = steady), routed_up and counted. `percentile(sid)` ranks a sitting among **each learner's first standard sitting of the same kind** (a paper: of that paper), shown only when n ≥ 20; standard = timed official, adaptive, standard module 1, not fixed-route or extended. The Report hero, Tests cards, Results, Today's score card and the report's Ranked pill all use it; Compete's "last 90 days" variant is not built. **Drift** is Plan's rule (mean3 vs the plan's start, ≥ 40 either way; target reached) and Today's drift line shows Plan's `suggest`. | F4 |
| R17 | Report a problem | Shell (10 images downscaled, disputes, admin), QBank (3 × 5 MB BLOBs), Tests (R-#### ids, tools), Report (3 screenshots), Words (10 images) | **One system:** Shell §2.10 and §10 are canonical: one modal `UI.report(ctx)`, up to 10 images (PNG, JPEG, WebP, GIF), stills downscaled in the browser to 2000px, 10 MB server cap, files on disk under `server/reports/{id}/` (git-ignored), bounded disputes (5 open), Your reports with replies in Settings, `/admin/reports` behind `SATF_ADMIN_TOKEN`. Categories per context are the union: Shell's lists, plus Tests' "More than one right answer" and "No right answer", plus Words' "Wrong or unclear definition" (word context). Mid-test reports never show marking and hide key disputes. Rate limit: 10 an hour and 20 a day per learner (429). Ids are integers. `tools/reports.py` is an optional CLI over the same table. | F6 |
| R18 | Sharing | Five specs define share tokens with colliding routes | **Three kinds, one each.** (a) **Progress link** for a parent or tutor: `links(kind='progress')`, view `/share/?t=`; it shows Me's cards, the Results overview and the plan read-only. Report's `learners.share` and Plan's `view_token` are this token (`/results/?share=` and `/plan/?view=` accept it). (b) **Calendar feed:** `links(kind='cal')`, one server `.ics` builder in `plan.py`, served at `/api/cal/{token}.ics`; the download is `GET /api/plan/ics`. Shell's client-side `UI.ics(plan)` is not built; a single-event helper `UI.ics(event)` (SAT date, a contest, the daily reminder) is in kit. (c) **Question sets:** `sets(code, owner, kind 'set' \| 'test' \| 'items', session, items, cfg, title, show_score, show_name, created, revoked)` for QBank shared sets, Tests shared tests and Review shares; `POST /api/sets`, `GET /api/sets/{code}` (public summary, no stems), `GET /api/sets/{code}/results` (owner only), `DELETE`; landing `/s/?c=CODE` forwards to `/practice/?share=` or `/tests/?shared=`. `navigator.share` is only ever called from a tap on "More ways to share". | F6 (sets), F4 (links table), S1 (progress view), S7 (cal) |
| R19 | Access to keys and re-serving | Review defines `access()`; others re-serve items ad hoc | **One rule, `deps.access(learner, template, seed)` → `reveal` \| `kept` \| None** (Review §server). Everything that returns a key or re-serves an exact (template, seed) goes through it: review endpoints, sets, worksheets, the report, the challenge review, permalinks, Words examples. Live-test items and unanswered or same-day challenge items never leak. The permalink `/practice/session/?q=TEMPLATE:SEED` (QBank; Shell's `/q/` is the same route) serves any catalogue item that is not in today's challenge as a fresh one-question drill; the key shows after answering, as always. | F4 |
| R20 | Status colours and glyphs | Report flips nothing; QBank uses wash for correct; Compete/Review differ | **The practice session's semantics, with glyphs everywhere** (§2.3): right = orange, wrong = graphite, plus Mixed (right on a retry) and Repaired (right on the repair after a miss) as two states, skipped, blank, voided, repeat, not reached, answered (exam), flagged, saved, has note, current. One legend component. | F1 |
| R21 | One question format | QBank `UI.workspace`, Tests runner shell, Today confirm mode, Words quiz mode | **One component `UI.workspace` (question.js) and one runner shell (runner.js/css).** Modes: `practice` (feedback instant / retry / end), `exam`, `review` (read-only, Hide answers, re-answer files a repeat), `quiz` (Words), `inline` (quick sheet, Today's Try one, sheets). The practice session and the exam runner use the same runner shell: sticky top bar, progress rail, question strip, footer (Back · "Question N of M ⌃" · Check/Next), navigator, Check your work, timer, calculator dock, highlights. The exam runner's look is the practice session's (Tests §1). `UI.question` stays as a thin alias. | F3 |
| R22 | Keyboard | QBank uses C for calculator and S for skip; Review S for save; clashes with choosing C | **One registry `UI.keys` (F2) and one map (§2.8).** Calculator G, reference F, save B, skip S, history Y, highlights L, confidence K. Shortcuts are ignored while typing (Enter and Esc aside) and when `prefs.keys` is off. | F2, F3 |
| R23 | Review player, pane and history | Report's `UI.review` player, Review's `UI.questionReview` pane, QBank's review sheet | **One component `UI.review(host, items, opts)`** with `mode: 'dialog'` (Report §1.13 layout) and `mode: 'pane'` (Review §8), plus **`UI.history`** (Review §9 attempt history for the whole question type), used by the session, the report, Review and the challenge review. Report's "Try one like this" tile and Review's inline mini-session are the same inline drill. | F3 |
| R24 | Drills that are not sittings | twin, try, word-example, review pane, spot, quick each have their own list rule | `cfg.inline = true` for sources `twin, try, word-example, review, spot`: never listed as a sitting, never in history, In progress or Resume; their answers file normally (a twin counts on its parent). `quick` sittings are listed in history as "Quick questions", never offered as Resume, and deleted when finished with 0 answers. Any set finished with 0 answered is never listed. | F5 (flag), S6 (history), S4 (drill list) |
| R25 | Achievements | Shell 43 tiered rules and `earned`; Compete 18 badges and `badges`; Words rules | **One engine `server/achievements.py`** and table `earned(learner, id, tier, at)`. Shell's tiered rules are the base. Compete adds only its unique badges (pace-setter, top-ten, weekly-4, sprinter, dress-rehearsal, season-top-10, level-5, level-8, all-rounder); Words adds 50 / 250 / 1,000 known, a collection complete, a 7-day review streak. Overlaps take Shell's tiered rule. Compete's and Words' rules are declared in their own modules (`ACHIEVEMENTS = [...]` in `compete.py`, `words.py`) and imported when present. | S1 |
| R26 | The sittings list | Tests, Report, Words, Review, Today each extend `/api/history` or add a list | **One endpoint `/api/history`** (S6) with every field in Report §server plus Tests' statuses, `all=1`, modules, blanks vs wrong, twin and paper labels, Words' `kind=words` filter and counts. Today's "Recent tests" reads `/api/history?kind=tests&all=1&limit=6`; Dashboard's separate `/api/tests/recent` is not built. The report page redirects a words-run id to `/words/run/?id=`. | S6 |
| R35 | Blank vs wrong | Report says blanks are never Incorrect; Tests shows blank chips | One bucket set everywhere: Correct / Incorrect / Unanswered; Incorrect never includes blanks; blanks are dashed-outline chips. | F1, S6 |
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
| S1 | `/signin/`, `/pair/`, account endpoints; `/api/me/summary`, `/feed`, `/activity`, `/achievements`, `/seen`; the progress-link view `/share/?t=` | F2 (menu links, toasts); S6 and S7 (their pages accept the progress token) |
| S3 | `/api/qotd?day=`, the "like" drill route, `/api/scores` | S8 (contest page QOTD panel), S6 and S7 (added scores on charts and the plan's test day) |
| S6 | `/api/history` (R26), `/api/stats`, `/api/skill/{topic}`, `UI.sittingCard`, `?q=M1-3` on the report | S3, S5, S9 (words filter), S1 (recent activity links) |
| S9 | `words.of_reason`, `words.minutes_today`, `words.today_summary`, `words.me_stats`, `/api/words/today`, `UI.gloss`, `UI.addWord`, `UI.addWordFromSelection` | F5 (feedback words), S7 (Words task), S3 (Words tile), S1 (Me stats), F2 (quick sheet tab), S4, S3, S6, S8 (gloss and add-from-selection hooks) |
| S10 | `/api/review/counts`, `/api/review/item`, `/api/review/family`, flag endpoints (`POST /api/session/{sid}/flag`, `POST /api/flags`) | S3 (Review card), S1 (Saved & in progress), F3 (`UI.review` pane, `UI.history`), S4 and S5 (Mark), S6 (flagged in results reads `flags`) |
### 2.13 Acceptance checks changed by the resolutions
| section | the check says | read it as | why |
| 3.5 Report | `POST /api/me/share {on:true}` returns a token for `/results/?share=` | `POST /api/share` (the progress link, S1) returns a token that `/results/?share=` and `/share/?t=` both accept | R18(a) |
| 3.5 Report | `POST /api/session/{sid}/time {times}` | answers carry `ms`, or `POST /api/session/{sid}/state {question_id, ms}`; the attempts then carry ms | R7 |
