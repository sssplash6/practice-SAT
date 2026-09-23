# v2 upgrades: Today (the dashboard)

Written 2026-09-23 for `spec/rebuild-v2.md` §3.2 (lines 2295–3347). It merges three designers'
proposals (outcomes, experience, unfair advantage) into one build-ready list, T1–T20.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.2 where
  they differ: §3 of this file lists every place that changes. Part 2 resolutions (R1–R38)
  still hold, except the lines named in §3.2 "Outside the section".
* **Shared with the shell file.** `spec/v2-upgrades/shell-me.md` already specifies the pieces
  Today also shows: Up next's queue and time box (U1, `server/next.py`), points on the table
  (U4, `estimate.gains` / `estimate.need`), rough skills and Sharpen (U5), habits and the trap
  gauntlet (U6, `server/habits.py`), pace (U7, `progress.pace`), the projection (U9), every
  number explaining itself (U13), week goals (U14), stages (U15), spare days (U16),
  registration deadlines (U17), paint from cache (U23) and Undo (U25). Today reads those same
  functions, so one fact reads the same on Today, in the chrome and on Me. Where this file
  needs one of them to change, the change is listed in §3.2, never re-specified here.
* **The bar.** A student who uses TopTierPrep today opens ours and wants to switch, because
  this page does more for their score and is nicer and faster to use. Parity is failure.
* **Names.** Upgrades are T1–T20. Builders are Part 4's tasks (F1–F6, S1–S10). S3 owns
  `web/index.html`, `server/api_today.py`, `server/daily.py` and the new `server/today.py`.
* **Subject-aware.** Per v2-decisions item 3, every new payload about a section (points,
  causes, pace, readiness, the warm-up) carries `subject` (`math` now), so R&W is additive.
* **Facts this file relies on** (from the code as of 2026-09-23):
  * `scoring.ANCHORS` = (0, 200), (0.25, 300), (0.5, 480), (0.75, 620), (1.0, 780). Mid-scale
    the curve rises 560 points per unit of weighted fraction.
  * Module weights (`scoring.WEIGHT` easy 1 / medium 2 / hard 3 over `blueprint.TIERS`):
    module 1 carries 44, the upper module 2 carries 52 and the lower one 36. So one medium
    question in a routed-up section is worth about 2/96 × 560 ≈ 12 points mid-scale.
  * `scoring.ROUTE_UP_AT` = 0.60 of module 1's questions right (14 of 22).
    `LOWER_ROUTE_CEILING` = 580, so any target above 580 needs the harder module 2.
  * Grid-ins sit at 6 of 22 positions per module (`blueprint.SPR_AT`), 12 of 44 a section.
    153 of 386 templates make grid-ins. 59 of 386 make more than one tier.
  * `GET /api/types/{t}/example` serves a reserved seed (900000+) that is never served in
    practice (F5), so a worked example costs no real question.

---

## 1. Scorecard

"v2 spec" is §3.2 as written. The verdict says why ours is way better. Where v2 was only at
parity (or below), the verdict names the upgrade that fixes it. Shell items around the
dashboard (sidebar, Upgrade card, user card, floating word button) are scored in
`shell-me.md`.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Hero banner | Blue banner: date eyebrow, time-of-day greeting with the full name, a decorative illustration. No facts, no action | Date eyebrow, greeting, `Add your name`, 4 chips (streak, minutes today, SAT in N days, plan N of M), each linking to its card | Adds a briefing line (yesterday's result, what came due, new homework or score, a skill that moved), a streak-at-risk line with a one-question action after 18:00, and a Final stretch chip (T19, T13) | v2 PARITY: the chips repeat numbers the cards show. **T19 → WAY BETTER.** The first line a returning student reads says what changed and what is owed, and each fact is one tap from its action. |
| 2 | Single next action | None: the plan CTA, QOTD, countdown and score compete | Up next: running test, unfinished set, plan test day, or the coach's set with count and clock chips | "I have 15 minutes" builds a points-ordered session and lists its blocks before Start. Any block can be dropped. Question 1 is already on the page (T1). A new skill starts with a worked example (T4) | Better than theirs already, but v2's chooser is their QBank builder's count and timer. **T1 → WAY BETTER.** The student states their time and gets the best session that fits. The first answer is 2 taps from landing (theirs: 6–8 taps and a page change). |
| 3 | Today's Plan card | N of M completed, X min left (Y total), All Done badge, Full Plan, a checkbox per task, "Could not start task" toast | Today list: auto-ticked from real work, progress per row, Why, Skip / Undo, Move to… | **Due today**: homework, plan tasks, warm-up, words, the day's questions, the challenge and group contests in one list with one minute total. Done rows say what they achieved and offer the repair. Every finish screen hands you the next row (T2) | v2 PARITY plus auto-tick. **T2 → WAY BETTER.** Everything owed today is in one place, with zero ticks and zero trips back to the dashboard between items. |
| 4 | "Why this task?" | Expands one `aiReason` sentence | A `Why` toggle with one line (the coach's reason) | Why gives numbers: open mistakes, recent accuracy, questions a section, ≈ points, minutes at your pace, and `See the evidence` (T2) | v2 PARITY. **T2 → WAY BETTER.** A claim the student can check, not a sentence. |
| 5 | Skip / Undo / Move a task | Skip, Mark done, Undo, Move to a later day in the same week only | Skip / Undo skip, Move to any study day up to the eve (R14), automatic completion | Adds `Swap for: Circles` (the plan's alternatives). Every edit applies at once with Undo (T2, T20) | **WAY BETTER already** (wider range, no manual done). T20 makes it instant. |
| 6 | Two questions of the day | R&W left, Math right, the same for everyone | One MC and one grid-in Math, side by side | Adds a third slot, **Word in context** (the SAT's R&W item type, from Words), with a crowd spread and why each wrong word fails (T14) | v2 BELOW theirs for a student who thinks in 1600: no R&W at all. **T14 → WAY BETTER.** An R&W item, plus both Math formats. |
| 7 | Answering the QOTD | A modal: select, Check, one attempt, key never highlighted, Show explanation, More practice, Done | Inline confirm mode. The key is highlighted, every option shows its misconception and crowd bar. 5 more like this, Harder, Save, Share, Report, 30 past days | After a miss, its twin is answered in place and the slot turns Repaired. A pace line: you, everyone, the SAT. A grid-in entry error is named as entry, not as a wrong idea (T14, T5) | **WAY BETTER already** in feedback. T14 means a miss ends on a right answer. |
| 8 | QOTD streak | A "1 day" pill; the profile says 0 | A labelled day's-questions streak from one source | Adds the best streak and the month's record against the crowd (T14) | **WAY BETTER** (one source, labelled, with a record). |
| 9 | Study time today / this month | Two figures: 1m / 1h 13m | Four figures (today, week, month, active days) with goal bars, one local-day function | Each day also counts clean answers and mistakes fixed. **Where the time went**: minutes by domain against the test's share and against where the points are, with Rebalance (T17) | v2 PARITY: still only "how long". **T17 → WAY BETTER.** It says whether the minutes went where the points are, and fixes it in one tap. |
| 10 | Month calendar | Round cells, today black, activity blue, cells do nothing, no navigation, drawn in UTC | Goal-relative heat, plan marks, exam mark, month nav, a day detail, keyboard | Heat by Minutes, Questions, Accuracy or Fixed. Future cells show check-ins due. The day detail names the mistakes opened and closed and has **Redo this day's misses** as fresh questions (T17) | v2 PARITY in kind (a better grid). **T17 → WAY BETTER.** Any past day becomes a set; the days ahead show the spacing. |
| 11 | Daily / weekly goal | On the profile: "Daily 2 Hours / Weekly 12 Hours", no effect | Minute chips on Today, the same field as the plan, weekly goal = minutes × study days | A suggested goal worked out from the real workload to the exam, with its arithmetic; each chip shows its question count; "58 min a day for the 3 days left" (T17) | v2 PARITY: a number the student guesses. **T17 → WAY BETTER.** |
| 12 | Streaks | QOTD says 1, profile says 0 | Three labelled streaks (study, day's questions, challenge), one source each, with the best | Spare days (U16), "goal met 9 of the last 14 days", rest days shielded on the calendar and week strip, and an at-risk warning with a one-question action (T17, T19) | **WAY BETTER.** It can't disagree with itself, can't be broken by one sick day, and warns before it breaks. |
| 13 | Study plan CTA (no plan) | "Build Your Adaptive DSAT Study Plan", 3 bullets, Build My Plan, 1 plan a cycle; the generator failed 3 of 3 times | 4 step links, a personal preview, 3 bullets, `Build my plan →` into the 4-step wizard | **Build with these**: the SAT date, daily minutes and days, prefilled from the student's data, with the first week drawn inline. One tap creates the plan and fills Due today (T18) | v2 PARITY: a button into a wizard. **T18 → WAY BETTER.** A working plan in one tap, free and unlimited. |
| 14 | Plan stat tiles | Days to exam, Streak, Plan complete %, Score gap "1000 now, 1400 target" | Day 12 of 45, 20% done, 10 days to the SAT, +140 to target | Adherence ("on time 9 of 10 study days") and pace status ("Behind · making +9 a week, needs +18") replace the two tiles that repeat other cards (T18) | v2 PARITY: a one-for-one copy. **T18 → WAY BETTER.** It says whether the plan is working. |
| 15 | Week pager and day tiles | "3 / 7" pager, This week, 7 tiles with done/total or rest | The same, plus partial, missed and skipped states and the planned load | Each day shows studied-vs-planned minutes, its topics, and what it fixed and held. `Make up` on a missed day, `Work ahead` on a future one (T18) | v2 PARITY. **T18 → WAY BETTER.** |
| 16 | Behind banner | "You have fallen behind" with Rebalance my plan (one tap) | A line and `Change daily time`, which opens the wizard | Says what the missed days cost (check-ins overdue, mistakes aging). `Catch up · 15 min` starts the fix; two previewed plan fixes apply in one tap with Undo (T18) | v2 BELOW theirs (a trip to the wizard). **T18 → WAY BETTER.** |
| 17 | Score drift banner | Upward only, ≥ 60, Not now (3 h) / Rebuild with these scores | Plan's `suggest` (R16, ±40), Update the plan's start / Not now | The 3 sittings as dated chips, the skills that moved since the plan started, and the effect before applying ("pace needed drops from +18 to +12 a week"). Downward drift gets its own fix (T10) | v2 PARITY. **T10 → WAY BETTER.** |
| 18 | Score progress | Current and target; stayed 0 after a 420 sitting ("Complete a full-length test…") | A band from any sitting, the scale with target and start, gap and pace, an 8-point trend, 4 domain rows | "Practice since Sep 21: ≈ +15". Evidence per domain with Sharpen. A projection cone to the exam date with an On pace / Behind verdict and made-vs-needed per week. After the SAT, the forecast against the real score (T10). **Where your points went** (T7) | v2 PARITY: it still moves only after a test. **T10 + T7 → WAY BETTER.** It moves every day, looks forward, and says why points are lost. |
| 19 | Accuracy by domain, weakest first (their plan's Progress tab) | 4 raw-accuracy bars: "This is where your remaining time pays off most" | 4 domain rows on the Score card, with `Most points to fix` | **Points on the table**: 19 skills priced in scaled points and in the student's own minutes, one tap each. Grid-in entry and pace get their own rows when they cost points (T6) | v2 PARITY: ranked by weakness, not value. **T6 → WAY BETTER.** A skill on every test outranks a rare one at the same accuracy. |
| 20 | Target editor | Wrong "current score", number input, 400–1600 bar, Save disabled until you type; targets not synced | Number + slider, quick chips, optional R&W, one target shared everywhere | **What it takes**: "700 ≈ 37 of 44 right; you're near 31", where the missing ones are, "needs the harder module 2: 14 of 22 in module 1", a pace tag on every chip, and a later date that makes it Steady (T11) | v2 PARITY: the same dialog, done right. **T11 → WAY BETTER.** The target becomes a count of questions and a route. |
| 21 | Exam date picker | A select of 8 official dates, two already past | Upcoming official dates, Another date, Remove date | Each date shows its study days, the pace it needs with a tag, a projected score, and the registration and late deadlines. The first Steady date is marked Recommended (T12, U17) | v2 PARITY: their control without their bugs. **T12 → WAY BETTER.** Choosing a date is a decision made with data. |
| 22 | Exam countdown | Live DD : HH : MM : SS to an unstated time | The same ticker to doors-close, a plan line, a checklist in the final week | The main figure is capacity against need: "7 study days · 5h 15m · needed: 23 mistakes, 2 sections, warm-ups · fits with 1h to spare", or "short by 1h: add 10 min a day". The ticker stays, smaller (T12) | v2 PARITY: seconds are decoration. **T12 → WAY BETTER.** It says whether the time left is enough. |
| 23 | The last weeks | Nothing changes as the date nears; "Exam day has arrived" | A checklist from 7 days out; exam-day and passed states | **Final stretch** from 14 days: dress rehearsals, a relapse sweep of every fixed mistake, readiness per domain, no new low-value topics, a taper, the eve, a test-morning order, and after the test the scores date and the official score (T13) | v2 PARITY. **T13 → WAY BETTER.** The page changes what it asks for when it matters most. |
| 24 | Recent tests | Total, date, R&W and Math rows, Review | Band, route tag, wrong-vs-blank chips per module linking to the question, Review, Fix N, New one like this | Why the points went (traps, slips, clock, entry, gaps), what fixing them is worth on this paper (exact re-score), time used per module and blanks at time-up, delta, percentile, total with R&W. **Retake as twin** with fixed-vs-still-wrong. Any miss chip opens its twin (T16, T5) | v2 better on misses; the score half was PARITY. **T16 → WAY BETTER.** |
| 25 | Resume a test or a set | Nothing to resume | Up next resumes a running test (clock shown) and unfinished sets | Also a Due today row; the page paints from the last visit at once (T2, T20) | **WAY BETTER already.** |
| 26 | Mistakes on the dashboard | None (their Redo list exists only in their API) | Mistakes card: named misconceptions, hits, owed pips, Fix, Try one now | By habit across skills with Drill this habit and the gauntlet; **blind spots** (sure and wrong) first; a relapse offers Learn it; one twin sheet (T9, T5, T4) | **WAY BETTER already.** T9 fixes the habit, not the question. |
| 27 | Spaced review | Only vocab "Due Today" (stayed 0 after grading) | Check-ins at 3/10/30 days live in Review | **Warm-up**: 5 spaced, mixed, unlabelled retrievals every day on fresh numbers, with a forecast on the calendar and a held rate (T3) | **WAY BETTER.** Theirs cannot re-test a Math question without showing the same numbers. |
| 28 | Time insight | "Time Analysis" on Contest Rankings, empty; the QBank stopwatch resets on reload | Nothing on Today | **Pace**: a module at your pace against 35:00, the strip showing where the clock runs out, points lost to time, slow-but-right skills with a speed drill (T8) | v2 BELOW (nothing). **T8 → WAY BETTER.** |
| 29 | Homework | `/my-classes` exists but is hidden from the sidebar and dashboard | §2.9 says Today shows assignments due first, but §3a/§3b never list them | A Due today row with its due time; overdue rows at the top; Up next leads with homework due within 24 h (T2) | v2 missed it. **T2 → WAY BETTER.** |
| 30 | Vocab due | A separate "Due Today N" card on My Words | Words tile (R30) | Words due is a row in Due today with its minutes, chained after the Math session (T2) | v2 PARITY. **T2 → WAY BETTER.** One list, one total. |
| 31 | Daily challenge | Contests empty, answers revealed only after a contest ends | Card with top 5, time left, challenge streak, yesterday | After finishing: 10 slot squares against the field's % right, the field's top trap per slot, and a twin of each miss (T15) | **WAY BETTER.** |
| 32 | Practice estimate | Practice page: "Math 200-280 · LOW CONFIDENCE" with no way to improve it | A band from any sitting | Evidence per domain and **Sharpen · 12 questions** where it's thin; the practice delta moves daily (T10) | **WAY BETTER.** Low confidence becomes a 19-minute action. |
| 33 | Loading and errors | Generic toast "Could not start task. Please try again." | Skeletons at final height, per-card errors with Retry | Paint from the last visit, then update; optimistic edits with Undo; J / K between cards (T20) | **WAY BETTER.** |

---

## 2. Accepted upgrades

Grouped by how directly they move the score. Each gives why, screens and components,
controls and states, data and endpoints, how it uses the rest of the site, and acceptance
checks. Learner codes in the checks start `a:v2revtoday`; `:PORT` is S3's own.

### Layout after these upgrades

**Desktop (≥1080px)**, 12 columns:
```
hero  ×12
next  ×8   | mist  ×4
gain  ×8   | exam  ×4
qotd  ×12             (MC + grid-in side by side, 6 + 6; Word in context full width under them)
score ×6   | pace  ×6
study ×8   | chal  ×4
plan  ×8   | words ×4
tests ×12
```
In the final stretch (T13): `hero / exam ×12 / next ×8 | mist ×4 / gain ×12 / …` (the rest
unchanged). On exam day before 13:00: `hero / exam ×12 / next ×12 / …`.

**Tablet (760–1079px)**, 2 columns: `hero hero / next next / qotd qotd / gain gain / mist exam
/ score pace / study study / chal words / plan plan / tests tests`. The questions of the day
use tabs.

**Phone (<760px)**: hero, next, qotd, gain, mist, exam, score, pace, study, plan, chal, words,
tests.

**Calls.** `/api/today` stays the one call for the core cards (hero, next, mist, exam, plan,
the Due list). A new `GET /api/today/insights` feeds `#gain`, `#pace` and the forward-looking
parts of `#score` (T6–T10). It runs in parallel, has its own error and Retry, and a failure
leaves the core cards untouched. Both are computed from one read of the learner's attempts
over the last 60 days, passed into pure functions.
`ponytail:` recomputed per call; memo per (learner, last attempt id) if profiles show it.

---

### A. The day's work

#### T1. Up next: sized to your time, with question 1 already on the page

*From: outcomes #5, experience #1, unfair-advantage #2, U1's time box. Effort M. Builders: S3
(the card), F5 (`first`, `drop`, preview blocks, the token), F2 (`next.py` composition), F3
(`UI.workspace` inline mode).*

**Why.** A student plans by time ("I have 15 minutes before the bus"), not by count. Theirs
fixes daily time once in a wizard, and starting a QBank set takes 6–8 taps and a page change.
Listing the blocks before Start shows the session is worth the minutes, and answering the first
question on Today removes the last reason not to start.

**Screens and components** (inside `#next`, after v2 §3a items 1–3, which still come first:
running test, unfinished drill, plan test day; `next.queue` supplies them, see §3.2).
* **Time seg** (`UI.seg`) under the header: `Time today: 5 · 15 · 30 · 45 · 60 min`.
  * Default: the plan's minutes left today (`plan.today_summary`). Otherwise the daily goal
    minus today's minutes. Otherwise 15. Rounded to the nearest option, at least 5.
  * Helper under the 5 chip when it is selected: `Short on time? 5 minutes keeps your streak
    and your check-ins.`
* **The plan of the session**: numbered block rows from `POST /api/drill/preview`. For example:
  ```
  1  Warm-up · 2 check-ins, 1 fading          3 q · 4 min
  2  Fix "Added the percentages"              2 q · 3 min · ≈ +5
  3  Linear functions                         3 q · 5 min · ≈ +20
  4  Keep warm: Circles                       1 q · 2 min
     Then more Linear functions until 15:00
  =  15 min
  ```
  * Each row: its number, label, `count q · minutes` in DM Mono, the U4 points when known, and
    an `×` button (`aria-label="Drop Fix Added the percentages"`). Dropping re-runs the
    preview with that block key in `drop`, and the next candidate takes its place.
  * At 60 min with no module or section finished this week, one extra row:
    `Or a timed module · 22 q · 35 min · no test yet this week` with a `.btn Start module`.
  * With a plan, when the box is shorter than today's task: `The other 28 questions stay in
    today's task. If they're not done, the plan redraws the days ahead.`
* **The reason line** keeps v2's wording and leads with value when U4 has it:
  `Worth about +20 · Linear functions: 58% right, about 4 of 44 on every test`.
* **Question 1, on the page.** Under the blocks, `UI.workspace(host, q, {mode:'inline'})`
  renders the first block's first question: the skill line, the stem in Source Serif 4 at
  `--q-size`, then the options or the grid-in field, then Check.
  * A tap selects, and Check (or Enter) files it. That call creates the session with this item
    as question 1.
  * Feedback appears in place: the key, the named mistake, the rationale.
  * Then the pill `Continue · 2 of ~9` (Enter) opens `/practice/session/?id=` at question 2.
    A `.quiet` `Stop here` finishes a one-question session, which still counts toward today.
  * When block 1 is the warm-up, the skill line reads `Mixed warm-up` until Check (T3).
  * Phone: the question is full width, option rows are 56px, and Check sits directly under the
    options.
* **The pill** `Start · 15 min` (the region's primary) starts the same session without
  answering in place.
* **Kept, behind `.quiet Count instead`**: v2's count chips `5 · 10 · 22 · {coach} · Endless`,
  the Timed/Untimed `.clock` and `More options`. Choosing a count replaces the box with a
  count set, as in v2.
* **Learn it** (T4): a `.btn Learn it · example + 3` beside the pill when the box's first skill
  block is new to the student (fewer than 5 answers).

**Controls and states.**
* Loading: skeletons of 3 block rows and a 4-line question.
* Preview fails: v2's coach set with its count chips and the note `Couldn't size the set.
  Here is the usual one.`
* Rest day: the blocks and the question show, and the pill reads `Practice anyway`.
* Goal met or Due list all done: the receipt (T19) sits above the blocks, and the pill reads
  `Keep going · 15 min`.
* Changing the box re-fetches the preview (debounced 200 ms). Stale rows dim to 60% until it
  returns. The inline question is replaced only if block 1's first item changed.
* A stale preview item (409 `preview_stale`): the client refetches and shows `That question
  was used elsewhere. Here's a fresh one.`

**Data and endpoints.**
* `POST /api/drill/preview {source:'next', box, drop:[key]}` (§2.6's preview, F5) returns
  `{box, blocks:[{key, kind:'warmup'|'redo'|'skill'|'warm'|'then', label, detail, count,
  minutes, pts}], minutes, alt:{kind:'module'}|null, plan_note|null, first:{token,
  question}|null}`.
  * Block keys are stable: `warmup`, `redo:{trap id}`, `skill:{topic}`, `warm:{topic}`,
    `then:{topic}`.
  * `minutes` per block = count × the learner's median seconds for that topic over 60 days
    (95 by default), the same rule as U1.
* `/api/today.next` carries `{items, box:{default, options}, preview}` for the default box,
  so the first paint needs no second call.
* **The first question** is chosen without writing anything. Its seed comes from
  `drill.preview_seed(learner, template, day)`: a walk from `sha256(learner:template:day)` that
  skips `practice_seen` and passes `deps.access`. `question` is `drill.public()` output (no
  key, rationale or reasons). Loading the page marks nothing seen and creates no session.
* **The token** is an HMAC-SHA256 over `learner|template|seed|local day|sorted block keys`,
  with a secret F5 creates once in `kv` (`preview_secret`), base64url, 22 characters.
* `POST /api/drill {source:'next', box, drop, first:{token, answer, ms}}`:
  * F5 recomputes block 1's first item from the same body and checks the token (same learner,
    same local day, same item).
  * It creates the session with that item as `served[0]` and files the answer through
    `drill.answer`, so the feedback shape is the usual one.
  * It returns `{id, feedback, next_url}`.
  * A mismatch, another day, or an item served elsewhere since → 409 `{reason:'preview_stale'}`.

**Uses the rest of the site.** The composition is U1's `box` (`next.resolve_drill`), with the
warm-up (T3) as segment 1, so the sidebar's Up next, the palette's "15 min" and this card build
the same session. The session page shows U1's box clock (`12:40 left of your 15`). Its
summary's "Next" comes from `GET /api/next` (U1 chaining).

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

#### T2. Due today: one list, one minute total, and each finish hands you the next

*From: experience #2, outcomes Today-list gap, unfair-advantage Why and All-done gaps, the
§2.9 assignment contract. Effort M. Builders: S3 (the list), F2 (`next.due`), S7
(`plan.today_summary`, PATCH), S2 (`classes.due_soon`), S9 (`words.today_summary`), S8
(`compete.due_today`), S4 / S6 / S9 / S8 / S2 (finish-screen chaining).*

**Why.** A student's day holds homework, plan tasks, reviews, words and the daily items.
Theirs lists plan tasks only, ticked by hand, with vocab on another page and homework hidden.
One list with one time total answers "what do I still owe today, and how long will it take?",
and chaining the finish screens removes the trip back to the dashboard.

**Screens and components** (the v2 §3b list, renamed and extended, under Up next).
* **Header**: `DUE TODAY · 3 of 7 done · about 34 min left`, and on the right
  `fits in your 45-min goal` or `11 min over your goal`. A `.btn Do them in order` (shown with
  2 or more undone rows) starts the first undone row.
* **Groups**: with a plan, `PLAN · 1 of 2 · 22 min left of 60` (the plan's own figures, as v2),
  then `ALSO DUE`. Without a plan, one group.
* **Rows, in this order**:
  1. A running or out-of-time test (v2's rules).
  2. Class assignments due within 24 h, by due time: `Period 3 · Circles · 10 q · due 5:00 PM`.
     Overdue ones (up to 7 days late) read `Overdue since Tue` in ink-bold and sit at the top.
  3. Plan tasks (fix, focus, test, custom, extra), from `plan.today_summary`. The plan's
     recheck task is rendered as the Warm-up row (T3), not twice.
  4. **Warm-up** (T3): `Warm-up · 5 questions · ~6 min · 3 check-ins due · 2 fading`. Shown
     with or without a plan whenever anything is due.
  5. **Sweep** (T13, final stretch only).
  6. Words due: `12 words due · ~3 min` (`words.today_summary`), starting S9's review run.
  7. The day's questions: `1 of 3`.
  8. The challenge.
  9. Group contests closing today: `Period 3 contest · 10 q · closes 9:00 PM`.
* **A row** keeps v2's status box, title with type tag, meta, action and ⋯ menu, plus:
  * the minute estimate in DM Mono: a practice or assignment count × the learner's median
    seconds, a word review 15 s (`words.minutes_today`), a test its clock, the challenge 16 min;
  * the due time when there is one;
  * **Why** (the `.quiet` toggle) with evidence: `Probability · 2 open mistakes · 48% right of
    your last 25 · about 3 of 44 a section · ≈ +15 · ~22 min at your pace`, from the plan
    task's `why[]` and U4. A `.quiet See the evidence` opens `/review/?tab=redo&topic=probability`;
  * `Swap for: Circles` in the ⋯ menu when the plan task has `alternatives`;
  * **once done**, its result: `15 of 15 · 12 right · 2 fixed · 1 new mistake`. When it opened
    mistakes, a `.btn Fix the 1 it opened · 2 q` sends
    `POST /api/drill {from_session: sid, still_open: true, scope: 'misses'}`.
* Undone rows come first and done rows after them, each with its result. Nothing is folded
  away.
* **Every finish screen offers the next row**: the practice summary (S4), the report (S6), the
  words run end (S9), the contest result (S8) and the assignment finish (S2) show
  `Next due: Warm-up · 5 · ~6 min [Start]` and `Back to Today`. Enter starts it. The item comes
  from `GET /api/next` with the just-finished key excluded (U1), so there is one rule.

**Completion rules** (v2's, plus):
* Homework: its assignment session is finished.
* Warm-up: today's warm-up session is finished, or every check-in due today has been answered
  once.
* Sweep: today's share answered.
* Words: due = 0, or a words run finished today.
* A contest: finished.

**Data and endpoints.**
* `next.due(learner, tz)` (F2, `server/next.py`) returns the rows. `next.queue` takes its
  first kinds from the same rows, so Up next and the list can't disagree.
* `/api/today.due = {rows:[{key, kind, title, tag, minutes, progress:{have, of}, due_at,
  status, why:[str], evidence_href, start:{path, body}|href, result:{answered, right, fixed,
  opened, session}|null, alternatives, task_id}], minutes_left, goal_minutes, done, total}`.
* Sources are read through `deps.part`, so a missing module drops its rows quietly:
  `classes.due_soon(learner, tz)`, `plan.today_summary`, `words.today_summary`,
  `compete.due_today(learner, tz)`.

**Uses the rest of the site.** Skip, Move and Swap use S7's `PATCH /api/plan/{id}/tasks/{task}`
(R14), applied at once with Undo (T20). The sidebar's Today card (F2) shows the same
`done / total` and minutes left.

**Acceptance.**
1. A learner in a class with an assignment due in 3 hours, a plan practice day and 2
   check-ins due: `/api/today.due.rows|map(.kind)` starts `["assignment","plan","warmup"]`,
   and `minutes_left` equals the sum of the undone rows' `minutes`.
2. The plan's recheck task never appears as its own row (`map(.kind)` has one `warmup`).
3. Finishing the assignment session turns its row `done` without any tick, and the S4 summary
   shows "Next due: Plan".
4. A practice task that opened 1 trap: its done row has `.result.opened == 1` and the Fix
   button's body has `still_open: true`.
5. Words module absent: no `words` row and no error; present with 12 due: the row reads
   "12 words due".

#### T3. Warm-up: spaced, mixed, unlabelled retrieval every day

*From: outcomes #2, U1's checks and keep-warm rows, R9. Effort M. Builders: F4
(`progress.warmup_candidates`, `progress.due_forecast`), F5 (source `warmup`, `cfg.hide_skill`),
F3 (the hidden skill line), S3 (the row, the forecast, the held rate), S7 (the recheck task's
body).*

**Why.** Retrieval spaced just before forgetting, mixed across domains, and without a label
saying which method to use is what makes a fix hold on test day. Theirs has spaced review only
for vocab, and their Redo list has no UI. A fixed bank would show the same numbers again; each
of our returns has new numbers, so the schedule never runs dry.

**What is due** (`progress.warmup_candidates(learner, tz)`, F4), in this priority:
1. **Check-ins due** (R9: 3, 10 and 30 days after a fix), most overdue first.
2. **Fading types**: templates with no open trap whose last counted clean right is older than
   their interval. A clean right counts if it came at least 20 hours after the previous counted
   one. Intervals by counted rights k: 1 → 2 days, 2 → 5, 3 → 12, 4 or more → 30. Ranked by
   age ÷ interval. Derived from attempts, so no new table.
3. **Keep warm**: one Strong topic untouched for 10+ days (`prefs.keep_warm`).

**The session.** `POST /api/drill {source:'warmup', count:5}` (8 in the final stretch, T13).
* F5 fills it from the candidates in order.
* Interleaved: never two in a row from one domain when two or more domains are present, and one
  grid-in when any candidate template makes one.
* Fresh seeds, untimed, instant feedback, `repairs:'next'`.
* `cfg.hide_skill = true`: the skill line reads `Mixed warm-up` until Check, and the session
  header and navigator hide skill names until each item is answered. The difficulty pips stay.
  The student has to recognise which method a question needs.
* A held item (clean right) extends its interval by the rule above. A miss opens or reopens a
  trap by R9's normal rule; a missed check-in reopens as Relapsed.

**Screens.**
* **The Due row**: `Warm-up · 5 questions · ~6 min · 3 check-ins due · 2 fading`. Why:
  `Questions you got right before, back just as you start to forget them.`
* **Done**: `4 of 5 held · Circles slipped: it's in your mistakes now`.
* **Up next**: it is U1's segment 1 of every box (up to 3), and U1's `checks` row starts this
  session (§3.2).
* **Calendar** (T17): future cells show `3 due` in mono 9px from the check-in forecast. The
  day detail reads `Planned · warm-up · 3 check-ins · about 4 fading`.
* **Study card footer**: `Held 82% of 40 warm-up answers this month`.
* **Empty**: `Nothing to review yet · first check-ins come 3 days after a fix.`

**Data.**
* `/api/today.warmup = {checks, fading, keep_warm, size, today:{held, of, slipped:[topic]}|null,
  month:{held, of}}`.
* `progress.due_forecast(learner, tz, days=14) → [{day, checks, fading}]`: check-ins from
  `traps.due` and the R9 schedule; fading from the intervals, assuming no practice in between.
  It is returned in `/api/calendar` for future days.

**Uses the rest of the site.** Plan's recheck task starts `{source:'warmup', task:'YYYY-MM-DD:recheck'}`
(§3.2). Review's "Check these now" uses the same pool.

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

#### T4. Learn it: a worked example, then a twin with the example one tap away, then two on your own

*From: outcomes #7. Effort M. Builders: F5 (`example`, source `learn`), F3 (the example card),
S4 (the session order and summary), S3 (where it is offered).*

**Why.** For a new or repeatedly broken skill, studying a solved problem first, then solving
with the support fading, beats guessing again (the worked-example and fading effects). A
relapse means the method is missing, not the numbers. Theirs shows an explanation only after a
failed try. A fixed bank can't give a matched worked example without using up one of its own
questions; ours uses the reserved example range.

**Where it is offered.**
* Up next: `.btn Learn it · example + 3` when the box's main skill has fewer than 5 answers.
* The Mistakes card: on a row with `relapses ≥ 1` or `hits ≥ 3`, with the tag
  `Relapsed · learn it again`.
* Where your points went (T7): the Gaps fix.
* Points on the table (T6): on a `Not measured yet` row, beside `Measure · 5`.

**The session.** `POST /api/drill {source:'learn', templates:[t] | topics:[t], example:true,
count:3}`.
* With `topics`, F5 picks the topic's template with the largest U8 weight that the student
  hasn't met, else the most-missed one.
* **Card 0, `Worked example`**: `GET /api/types/{t}/example` (seed 900000+). It shows the
  question with the key highlighted, every option's misconception line and the rationale open.
  Its only button is `Your turn`. It files no attempt.
* **Question 1, `Your turn · the example is one tap away`**: a fresh seed of the same template.
  `.quiet Show the example` re-opens card 0 beside the question (a side panel at ≥1080px, a
  sheet below). Opening it sends that answer with `guess:true`, so it counts half (R8).
* **Questions 2 and 3, on your own**: fresh seeds. Question 3 is one tier up when the template
  makes one (59 of 386 do), else the same tier.
* **Summary** (S4): `Example, then 3 on your own: 2 right · 1 with the example open`. Clean
  answers close the template's trap by the normal rule.

**Acceptance.**
1. `POST /api/drill {source:'learn', templates:['<t>'], example:true, count:3}` →
   `GET /api/drill/{id}` has `cfg.example.seed >= 900000` and 3 questions, none with a seed
   ≥ 900000.
2. After 3 answers, `select count(*) from attempts where session='<id>'` is 3.
3. An answer posted with `guess:true` stores `attempts.guess = 1`.
4. For a template that makes 2 tiers, question 3's difficulty is above question 1's.

#### T5. Twin anywhere: every miss on Today has a same-trap twin, answered in place

*From: unfair-advantage #3, the experience and outcomes QOTD gaps. Effort M. Builders: F3
(`UI.twinSheet`), F5 (existing fields), S3 (the call sites).*

**Why.** A miss followed at once by a new question of the exact same kind, answered right,
turns an error into a lesson while it is fresh. Theirs allows one QOTD attempt, hides the key,
and their test chips do nothing. Retrying a finite bank's item tests memory; a twin tests the
skill.

**Component.** `UI.twinSheet({body, recall, onDone})` (F3, `question.js`). It is a `UI.sheet`
(a bottom sheet under 760px) running `UI.workspace` in inline mode.
* A collapsed header recalls the original: `Sep 21 · Module · Q13 · you picked B · added the
  percentages`. It expands to the original question read-only.
* The twin, then the full feedback (key, misconception, rationale).
* `Another twin` and `Done`. On Done the source mark takes the Repaired state (R20: amber with
  an ink ↻ corner) when the twin was right, and `/api/today` is refetched.

**Where it appears, and the body each sends** (all existing §2.6 fields, `cfg.inline` by R24):
| from | body |
|---|---|
| Try one now (v2 §4, now this sheet) | `{pool:'redo', ids:[trap id], count:1, source:'try'}` |
| A wrong day's question (T14, in the column itself on desktop) | `{like:{day, slot}, count:1, source:'twin'}` |
| A miss chip on a test card (T16) | `{from_session: sid, only:[qid], each:1, source:'twin', parent: sid}` |
| The calendar day detail (T17) | `{pool:'history', ids:[attempt ids], exact:false, each:1, source:'twin'}` |
| The finished challenge (T15) | `{from_session: sid, only:[qid], each:1, source:'twin'}` |

* A live test's item → 409 from `deps.access` (R19). The sheet reads `Finish the test first:
  its questions stay closed until then.`
* A twin is filed for mastery and counts on its parent (R24). It never counts in a crowd, a
  streak or a board.

**Acceptance.**
1. After a wrong MC day's question, the twin body returns a session with `cfg.inline == true`,
   the QOTD's template and a different seed. `/api/history` doesn't list it.
2. `{from_session: <unfinished module>, only:['q3'], source:'twin'}` → 409.
3. At 390, the sheet is a bottom sheet; Esc closes it and focus returns to the chip.
4. A right twin after a wrong day's question gives the slot mark the ↻ corner without a reload.

---

### B. Where the points are

#### T6. Points on the table: every skill priced in points and minutes, one tap each

*From: outcomes #1, experience #3, unfair-advantage #1, U4. Effort M. Builders: F4
(`estimate.gains` extras and tiers), S3 (the card), F1 (`UI.skillRow` with the track).*

**Why.** A skill at 40% that appears half a question a test is worth less than a 70% skill that
appears four times. Ranking by weakness alone (theirs: "Accuracy by domain, weakest first")
sends time to the wrong place. Pricing each skill in scaled points and in the student's own
minutes makes the trade-off plain, and one tap starts it.

**Card `#gain`** (desktop `gain ×8` under Up next; phone after the day's questions).
* **Header**: `POINTS ON THE TABLE` on the left. On the right, `from 312 answers · updated
  after every answer` and a `.seg By points · By minutes · By domain`.
* **Header line**: `About +60 on the table · your top 3 together ≈ +34`. With a target:
  `Target 700 needs about 37 of 44 right; you're near 31` (U4 `need`), which opens the target
  dialog (T11).
* **Rows** (6, then `.quiet Show all 19`, which expands in place), each `UI.skillRow`:
  * glyph and skill name;
  * `≈ +20` in DM Mono 18px 600, or `under 5`;
  * a 0–100 track: an ink tick at the student's accuracy and an amber tick at 80% (the level
    U4's gain assumes), with `52% → 80%` in mono 11px;
  * meta: `about 4 of 44 · at least 6 right · ~9 min`;
  * first-try accuracy by tier in mono 11px: `E 9/10 · M 6/11 · H 1/5`;
  * the open-mistake dots (up to 3) with a count;
  * `rough · 4 answers` when evidence is under 10 (U5);
  * `.btn Practise · 10`: `POST /api/drill {topics:[t], count: prefs.set_length, adaptive:true,
    source:'gain'}`.
* **Extra rows**, placed by their points, only when they apply:
  * `Grid-in answers · ≈ +15`, when grid-in first-try accuracy trails multiple choice by 15
    points or more over at least 10 of each. Meta `grid-ins 45% · multiple choice 71% · 12 of
    44 are grid-ins`. `.btn Practise · 10` → `{formats:['spr'], count:10, source:'gain'}`.
  * `Pace · ≈ +10`, when U7's forecast leaves questions blank. Meta `a module takes 38:40 of
    35:00`. `.btn See pace` scrolls to `#pace`.
* **By minutes** sorts by gain ÷ minutes and prints `≈ +2 a minute`.
* **By domain** is v2's Score-card domain block, moved here: 4 rows with the mastery bar,
  `71% right of 120`, the trap dot, and `Most points to fix` on the domain with the largest
  summed gain. Each links to `/practice/?domain=`.
* **Footer**: `.btn Practise the top 3 · 15` (U4's set) and the helper `Estimated with our
  score model: how far your Math band would move if this skill reached 80%.` with
  `.quiet How this works` → `/help/#points`.
* **Under 30 answers**: `Answer 30 questions and this shows where your points are · 12 of 30`,
  with the coach's set.
* A skill with fewer than 5 answers: `Not measured yet · about 4 of 44`, with `Measure · 5`
  and `Learn it` (T4).

**Data.** `/api/today/insights.gains` = `estimate.gains(learner)` (U4) plus:
* `tiers: {topic: {easy:[right, n], medium:[…], hard:[…]}}`, first tries, R8 counting;
* `extras: [{kind:'spr'|'pace', gain, detail}]`. The grid-in gain is U4's formula applied to
  the grid-in share of the section (12/44), raising its accuracy to the MC accuracy. The pace
  gain is `S − _interpolate(F × (22 − blanks) / 22)` with U7's forecast blanks;
* `by_domain: [{domain, gain, mastery, answered, right, traps}]`.

**Uses the rest of the site.** Up next's reason line, the Due list's Why and T11 read the same
function. Me's Skills card (U4) and Results render the same rows. Plan's `skills[].gap` should
call it too, so the plan and Today agree (§3.2).

**Acceptance.**
1. U4's seeded learner (circles 10 answers at 30%, linear_functions 20 at 90%, 30 more
   elsewhere): `#gain` lists Circles above Linear functions.
2. A learner with 12 grid-in first tries at 25% and 30 MC at 70%: `insights.gains.extras` has
   a `spr` entry with `gain > 0`, and the card shows "Grid-in answers".
3. `By domain` shows 4 rows whose `answered` equals `/api/today.domains[].answered`.
4. With 12 answers the card reads "Answer 30 questions" and "12 of 30".

#### T7. Where your points went: every miss sorted into trap, slip, clock, entry or gap, each with its fix

*From: outcomes #3, outcomes #8 (answer changes). Effort M. Builders: F4 (`progress.causes`,
`estimate.per_question`), S3 (the block), F3 (`UI.review` pane for slips).*

**Why.** "Study more" is the wrong fix for most misses. A careless student needs to check, a
slow one needs pace, a misconception needs fixing, and a grid-in entry error is learned in one
drill. Theirs shows Correct / Incorrect / Unanswered, counts blanks as wrong on one card, and
has no skill, difficulty or time per question, so they can't tell these apart.

**The rule** (`progress.causes(learner, tz, days=14, session=None)`, F4). Every wrong or blank
first try that R8 counts (not a repeat, not disputed, not void) gets one cause, first match
wins:
1. **clock**: blank in a timed sitting, or answered in the sitting's last 90 s after under 25 s
   on the question (`qstate` ms and `made_left`, R7).
2. **entry**: a grid-in whose value matches the key at 2 significant figures but not by
   `scoring.grid_equal`, or equals the key in a form the grid rejects (a mixed number, more
   than 5 characters for a positive answer or 6 for a negative one; `scoring.accepted_forms`).
3. **slip**: the student got this template right on at least 4 of their last 5 first tries
   before this one, or the question is easy and was answered in under half their median time
   for easy questions.
4. **trap**: the picked option names a misconception, or the grid-in mistake is named
   (`spr_mistakes`).
5. **gap**: everything else, usually a slow miss with nothing named.

It returns `{subject, days, total, by:{clock, entry, slip, trap, gap}, items:{cause: [attempt
ids ≤ 40]}, lever, top_gap_topic, changes:{right_to_wrong, wrong_to_right, sittings}}`.
* Over 14 days of practice the causes are counts, not points: practice misses are not a test's
  score. Points appear only for one sitting (T16), by exact re-marking.
* `changes` counts answer changes on tests over 30 days from `qstate.trail` (R7).

**Block** in `#score`, `WHERE POINTS WENT · LAST 14 DAYS`.
* One stacked bar with 5 labelled segments and counts: `Traps 11 · Slips 4 · Clock 3 · Entry 2
  · Gaps 6`. Segments are ink shades; the largest is orange; each carries its text label (never
  colour alone). A hidden table lists them.
* The helper names the biggest lever: `Most of your misses are traps (11 of 26): fixing them is
  your fastest gain.`
* Each segment is a button that opens its fix in a row under the bar:
  * Traps → `.btn Fix all · 22` (pool redo), or `Drill this habit · 8` (U6) when one habit is
    40% or more of the traps.
  * Slips → `.btn See your 4 slips` (the `UI.review` pane over those attempts) with the helper
    `You know these. Reread the last line of the question before Check.` and
    `.btn Careful set · 8` (untimed, those templates).
  * Clock → `#pace`'s speed drill (T8).
  * Entry → `.btn Grid-in entry drill · 5` (`{templates: those, formats:['spr'], count:5}`) and
    the Grid-in rules popover.
  * Gaps → `Learn it` (T4) on `top_gap_topic`.
* **Answer changes**, shown when `changes` total 5 or more:
  * more right-to-wrong: `On tests you changed 5 right answers to wrong and 2 wrong to right:
    keep your first answer unless you find an error.`
  * otherwise: `Your changes help: 6 wrong to right, 1 right to wrong. Keep checking.`
* Empty (fewer than 5 misses in 14 days): `Fewer than 5 misses in 14 days: nothing to sort
  yet.`
* The test cards (T16) print the same rule for one sitting.

**Acceptance.** In `server/checks/f4.py`, one seeded learner:
1. A grid-in "0.66" to the key "2/3" → `by.entry == 1`. "1 1/2" to "3/2" → entry.
2. A timed module finished with 3 blanks → `by.clock == 3`.
3. A named wrong answer on a template the learner got right 4 of the previous 5 → slip; the
   same answer on a new template → trap; an unnamed grid-in miss answered in 3 minutes → gap.
4. `sum(by.values()) == total`, and each `items[cause]` has ids only of that learner.
5. On `/` at 1280, clicking the Entry segment shows a button whose drill body has
   `formats:['spr']`.

#### T8. Pace: a module at your pace, where the clock runs out, and the drill that fixes it

*From: outcomes #4, experience #4, unfair-advantage #8, U7. Effort S. Builders: F4
(`progress.pace` extras), S3 (the card), F1 (`UI.strip` with a marker), S4 (the summary's
guard line).*

**Why.** A slow but accurate student loses points to the clock, not to knowledge, and usually
finds out on test day. Theirs has no time per question anywhere; their only time view is an
empty contest page. Ours records ms on every answer in every mode (R7).

**Card `#pace`** (desktop `pace ×6` beside Score).
* **Figure**: `38:40` in `.num` 44px, meta `a module at your pace · the SAT gives 35:00`.
* **Module strip**: 22 cells (`UI.strip`) in `blueprint.slots('module1', 1)` order, each with
  its tier pips. An orange vertical marker sits where the running total passes 2,100 s. Cells
  after it are dashed (the Unanswered token) with `~2 left blank`.
* **Cost**: `≈ −25 points from time alone` (blanks × `estimate.per_question`).
* With time to spare instead: `4:50 to spare · use it to check your last 5.`
* **Slow but right**, up to 3 rows: `Systems of equations · 2:40 a question · 88% right`, each
  with `.btn Speed drill · 8 in 12:40` → `{topics:[t], count:8, timing:'pace', source:'pace'}`
  (95 s a question, the runner's pace alert on).
* **Rushing**, when it applies: `6 wrong answers under 20 s this week · 4 in Percentages` with
  `.btn Careful set · 8` (untimed).
* **Tests**, from `qstate`: `Ran out of time in 3 of your last 4 modules · 5 blank at time-up`
  with `.btn Timed module · 22 · 35 min`.
* **Weekly delta**: `Module pace 43:30 → 38:40 since last week`.
* `.quiet Every skill` → `/me/#pace` (U7's quadrant chart).
* **Accuracy guard** (S4 summary of a `source:'pace'` session): `6 of 8 under 1:35 · median
  1:22 (was 2:40)`. If accuracy fell 15 points or more below the topic's usual, it reads
  `Slow down: accuracy first`, and for 3 days that topic's Speed drill on Today becomes
  `Careful set · 8`.
* **Empty** (fewer than 20 timed answers): `Your pace shows after 20 answers with the clock on ·
  12 so far`, with `.btn Timed set · 10` (`clock: pace`).

**Data.** `estimate.per_question(learner)` (F4) is the curve's slope at the student's weighted
fraction × a medium question's weight ÷ the section's weight (≈ 12 points mid-scale).
`/api/today/insights.pace` = U7's `progress.pace` plus
`{strip:[{slot, tier, ms}], runs_out_at, blanks, pts_lost, slow_right:[…], rushing:{n, topic,
n_topic}, tests:{modules, ran_out, blanks}, week_before_ms, guard:[topic]}`.

**Acceptance.**
1. U7's seeded learner (6 timed rights in circles at a median 150 s): `slow_right[0].topic ==
   'circles'`, and the button's body has `timing:'pace'`.
2. `runs_out_at` equals the first index where the cumulative strip ms passes 2,100,000 (an
   assert in `server/checks/f4.py`).
3. `pts_lost` equals `blanks × per_question` rounded to 5.
4. A `source:'pace'` session with accuracy 20 points below the topic's usual → the summary
   contains "accuracy first", and `/api/today/insights.pace.guard` contains the topic.

#### T9. The Mistakes card: habits across skills, blind spots first, relapses to Learn it

*From: outcomes #10, unfair-advantage #4, outcomes #8 (the inferred part), U6. Effort S.
Builders: F5 (`habits.py` avoided/broken), F4 (the sure rule), S3 (the card), S10 (spot).*

**Why.** Re-fixing one habit skill by skill is slow; fixing it once, across skills, transfers.
And a confident mistake is the costliest one, because it is never flagged or rechecked. Theirs
names no misconceptions at all.

**Additions to `#mist`** (R30's Review card: Review's counts, top 5, Fix, Try one now).
* A `.seg By question type · By habit` under the header.
* **By habit** lists U6's families from the student's open and last-30-day traps, only those
  spanning 2 or more templates. Each row:
  * the name (600 15): `Answered a different quantity than asked`;
  * `5 misses · Percentages, Rates, Scatterplots` with the skill glyphs;
  * the tell in italics;
  * progress: `avoided 2 of the last 5`, or `Broken · Sep 30` (the habit's name struck through
    in ink);
  * `.btn Drill this habit · 8` (U6's `source:'habit'`) and `.quiet Spot it · 3` (S10's spot on
    the habit's top trap).
  * The header carries U6's `Trap gauntlet · 10`.
  * Empty: `No habit shows up in more than one skill yet.`
* **Broken** (computed, no table): 5 avoidances in a row across at least 2 templates in
  `habit` or `gauntlet` sessions, where every item carries the trap, so a right answer is an
  avoidance. A later miss in the family reopens it.
* **Blind spots.** A trap whose latest miss was *sure* gets an ink `Sure` tag and sorts first,
  under the sub-header `BLIND SPOTS · 3` with the helper `You were sure and wrong: these never
  get double-checked.` Sure means not a guess (R8) and either the test's `qstate.conf` said sure
  or the answer came faster than 0.6 × the student's median for its tier. There is no new tap
  (see Rejected).
* **Relapsed** traps carry `Relapsed · learn it again`, which starts T4.
* **Try one now** opens T5's sheet.

**Data.** `/api/today.traps` adds `blind:[trap id]` and `habits:[{id, name, tell, misses,
skills, templates, avoided:{n, of}, broken_at}]` (from `habits.of_learner`, shared with Me's
card).

**Acceptance.**
1. A learner with 3 traps whose reasons tag `whole_part` over 2 topics: `By habit` shows one
   row naming both skills; its button posts `{source:'habit', habit:'whole_part', count:8}`.
2. Five right answers in a `habit` session on 2 templates → `broken_at` is set; a later wrong
   pick in the family clears it.
3. A trap whose missed attempt had `ms` under 0.6 × the tier median and `guess = 0` is in
   `blind` and is the first row.

---

### C. Score, target and date

#### T10. A score card that moves every day and looks forward

*From: outcomes #6, experience #5, the unfair-advantage score-gap gap, U5, U9. Effort M.
Builders: F4 (`estimate.practice_delta`, U9 `projection`), F1 (`UI.bandChart` cone), S3, S7
(drift preview).*

**Why.** Theirs stayed 0 after a 420 sitting, and their practice estimate says "LOW
CONFIDENCE" with no way to fix it. A student should see today's practice move the number,
know which domains are measured, and know whether they'll make it by the date.

**Additions to `#score`** (v2's band, SAT total, scale, gap, trend and Add a score stay).
* **Practice since the last test**, under the band: `Practice since Sep 21: ≈ +15 · from 84
  answers`, with `.quiet How` (U13's popover: our model's change, not a test score). It is the
  change in U4's `S` from the latest sitting's finish time to now (U4 allows differences of
  `S`, never `S` itself). Shown when |Δ| ≥ 5 and at least 20 answers since.
* **Evidence**, one line: `Evidence: Algebra 120 · Advanced Math 64 · Data 22 · Geometry 9
  (thin)` (first tries in 60 days). When any domain has fewer than 15: `.btn Sharpen · 12
  questions · ~19 min` (U5's probe). S4's summary then says what changed.
* **Trend** (`UI.bandChart`) gains U9's projection cone to the exam date, the exam tick, the
  plan's pace line and the target line.
* **Verdict**, one line under the chart:
  * `On pace: about 640–700 on Oct 3 · target 700`;
  * `Behind: on pace for 600–660 · 700 needs +18 a week, you're making +9`;
  * `At your target ✓`;
  * `Not enough to project yet · 2 scored sittings in 60 days start it`, with
    `.btn Module · 22 q · 35 min`.
  Two mono figures follow it: `Made +9 / wk · needs +18 / wk`.
* **Calibration**, once an official score is added after the exam date: `We projected
  600–660 for Oct 3 · you scored 640`, in either direction. The projection is recomputed from
  the sittings before the exam date, so nothing is stored.
* **Where points went** (T7) sits under the verdict.
* **Drift** (Plan's `suggest`, R16):
  * the evidence: the 3 sittings as dated band chips linking to their reports;
  * what moved: `Percentages +0.18 · Circles +0.12 since the plan started` (mastery now
    against `plans.start_mastery`);
  * the effect before applying: `New start 610 · the pace needed drops from +18 to +12 a week`
    (`POST /api/plan/preview {current: 610}`);
  * downward: `Tests are running below the plan's start (560 → 520)` with
    `.btn Update the start to 520` and `.btn Sharpen · 12`.
* The domain rows move to `#gain` By domain (T6).

**Data.** `/api/today/insights.estimate = {latest, practice_delta:{pts, answers, since},
evidence:{domain: n}, thin:[domain], projection (U9), verdict, made_per_week, needs_per_week,
calibration|null}`. `estimate.practice_delta(learner)` recomputes U4's `S` over the attempts up
to the latest sitting's `finished`, and now.

**Acceptance.**
1. A learner with a module on Sep 21 and 40 practice answers since, at higher accuracy:
   `practice_delta.pts > 0` and the card shows "Practice since".
2. Sittings with midpoints 500 (Sep 1) and 560 (Sep 15), exam Nov 7, target 700: `verdict`
   starts "On pace" or "Behind", and the SVG has a cone path.
3. An outside official score dated after the exam date → `calibration` is non-null, and the
   line contains "We projected".
4. A learner with 9 geometry answers → `thin` contains Geometry and Trigonometry, and the
   Sharpen button posts `{source:'probe', count:12}`.

#### T11. The target dialog: what it takes

*From: all three target gaps, U4 `need`, Plan's `target_note` and pace tags. Effort S.
Builders: S3 (the dialog), F4 (`estimate.need`), S7 (`POST /api/plan/preview`).*

**Why.** "700" means nothing until it is a number of questions, a route and a weekly pace.
Theirs states a wrong current score.

**Additions to `dialog.sheet#targetSheet`** (v2's number, slider, chips, R&W and buttons stay).
* **`WHAT IT TAKES`**, recomputed as the slider moves (debounced 250 ms):
  * `700 ≈ 37 of 44 right · you're near 31` (U4 `need`);
  * `The 6 you're most likely missing are in Circles, Probability and Nonlinear functions`;
  * above 580: `Needs the harder module 2: at least 14 of 22 right in module 1 · your best
    module 1: 12 of 22` (Plan preview `target_note`, and the best module 1 from the student's
    sittings);
  * with an exam date: `45 days · 31 study days · about 22 a week · Ambitious` (the preview's
    `pace_per_week` and `pace_tag`). When Very ambitious, a chip `Dec 5 makes it Steady`, which
    adds that exam date to the same Save.
* **Quick chips** carry their tag: `650 · Steady`, `700 · Ambitious`.
* Once the band's low end reaches the target: `You're at 700 · Raise to 750?`.
* It is the same function as Me's target popover (U4), so the numbers match.

**Acceptance.**
1. Opening the dialog at 700 shows text matching `\d+ of 44 right`.
2. At 650 the dialog contains "14 of 22"; at 560 it doesn't.
3. With an exam date, each quick chip has a tag from {Steady, Ambitious, Very ambitious}, and
   the Dec 5 chip's Save sends `PUT /api/me {target, exam_date}`.

#### T12. The countdown as capacity, and exam dates that show their consequences

*From: all three countdown and date-picker gaps, U17. Effort S. Builders: S3 (the card,
`today.workload`), F1 (`UI.examDate`), S7 (preview `per_date`), F4 (`satdates` deadlines).*

**Why.** Seconds tell a student nothing about how to study. Whether the time left covers the
work left is the question that matters, and a date chosen with its pace and deadlines visible
is a better decision.

**`#exam` card.**
* **Main figure**, capacity: `7 study days · ~5h 15m at your goal · 2 tests left`.
* **Need against capacity**, one line:
  * `Needed: 23 open mistakes (~1h) · 2 sections (2h 20m) · warm-ups (~40m) · fits, with
    1h 15m to spare`;
  * or `Short by 1h: add 10 min a day [Set 55 min]`, which sends `PUT /api/me {minutes:55}`
    with Undo.
* **The ticker** (v2's `DD : HH : MM : SS` to doors-close) stays under it at `.num` 28px, with
  its caption.
* **Registration** (U17): `Register for Nov 7 by Oct 23 · 5 days left`, with `I've registered`
  and `College Board ↗`, whenever `prefs.registered != exam_date` before `late_by`.
* v2's plan line, `.ics` and checklist stay.

**The date popover** uses `UI.examDate` (F1). Each upcoming official date reads
`Nov 7 · Sat · in 45 days · 32 study days · +11 a week · Steady · register by Oct 23`, plus
`~690` when U9 projects. The first Steady date after the current choice is tagged
`Recommended`. `Another date…` and `Remove date` stay.

**Data.** `today.workload(learner, tz)` (S3, `server/today.py`), shared by T12 and T17:
* capacity = the remaining study days' planned minutes before the eve (the plan's days, else
  `profile.minutes` × the study days, else the 7-day average × the days);
* need = open traps × 2 × median seconds + check-ins due before the exam × median + the tests
  left (the plan's, else T13's rehearsals) × their clocks + warm-ups (size × median × study days);
* `{study_days, capacity, need:{traps, checks, tests, warmups}, fits, short_by, add_per_day,
  suggest_minutes}`. All of it is workload at the student's own pace; nothing is converted into
  points.
* The popover reads `POST /api/plan/preview` `per_date` (with or without a plan: the preview
  takes the profile as a draft).

**Acceptance.**
1. Exam today + 10, Mon–Fri, 45 min, 10 open traps, median 100 s: `workload.need.traps ==
   2000` (s), and `fits` matches `capacity >= Σ need`.
2. `short_by > 0` → the Set button's body is `{minutes: suggest_minutes}`, a chip value.
3. The popover's rows each contain "study days" and a tag; with `satdates` deadlines present,
   "register by".
4. The SEC box still ticks within 1.1 s (v2 check 20).

#### T13. Final stretch: from 14 days out, Today changes what it asks for

*From: outcomes #9, experience #6, unfair-advantage #6, U15's stages. Effort M. Builders: F2
(`next.stage`, queue rules), F5 (`sweep`), S3 (the card changes), S7 (the Final phase agrees),
F1 (`UI.ics(event)`).*

**Why.** The last two weeks protect the score: rehearsals under real timing, retaining what is
known, fixing what repeats, and rest before the test, instead of cramming a rare topic the night
before. Theirs ticks seconds and nothing else changes.

**Modes** (`next.stage(learner, tz)`, keyed off `exam_date`, with or without a plan):
`stretch` (14–8 days), `taper` (7–2), `eve` (1), `exam` (0), `after` (the exam has passed and
no new date is set). With a plan, the plan's Final phase and its test days win: its tests are
the rehearsals, and no second schedule is made.

* **Hero**: the chip `Final stretch · 12 days` and the line `Rehearse, keep what you have, fix
  what repeats.`
* **Layout**: `#exam` moves to full width under the hero.
* **Dress rehearsal**, on each Saturday before the exam that leaves at least 6 days (at most
  2). That morning Up next leads with `Dress rehearsal · full Math section · 44 q · 70 min ·
  start around 8:30, like the real day`, pill `Start section` (`POST /api/mock/new
  {kind:'section', timing:'official'}` → the lobby). `.btn Add to calendar` downloads
  `UI.ics(event)` for that Saturday at a time the student picks (default 08:30, 90 min with the
  break). Without a plan, Due today lists it that day.
* **Relapse sweep**: every trap closed in the last 90 days (not dismissed) gets one fresh twin,
  spread evenly over the study days left before the eve. The Due row reads `Sweep · 5 of 34
  fixed mistakes today · ~8 min` → `{pool:'checks', sweep:true, count:5}`. A trap counts as
  swept once any attempt on its template comes after the stretch began. A miss reopens it as
  Relapsed.
* **Warm-up** grows to 8.
* **Fix** lists only traps on skills with 2 or more questions a test (U4 `per_test`), by gain.
  The rest: `11 mistakes on rare skills are parked until after Nov 7 · Show`.
* **No new rare skills**: the coach's `new` pick is suppressed with the line `Not starting
  Evaluating statistical claims: about 0.5 of 44 a test, 12 days left.` and `.quiet Practise
  anyway`.
* **Readiness per domain** in `#exam`: 4 rows, each with `.btn 10 min` (a box of 10 on that
  domain):
  * `Ready`: mastery ≥ STRONG, no open trap on a skill with 2+ a test, answered in the last 7
    days;
  * `Shaky · 3 open mistakes` (or mastery under 0.6);
  * `Untested for 14 days`.
* **The countdown adds** `2 rehearsals left · 9 check-ins due · 12 mistakes worth ≈ +60`.
* **Taper** (7–2 days): boxes draw only from the warm-up, the sweep and open traps (U1's final
  week drops probe and untried). The time seg's default caps at 30.
* **Eve**: Up next is `Light warm-up · 5 from your strongest skills · ~8 min`, then `Done for
  today. Sleep does more than cramming now.` The checklist opens with a `Night before` group:
  `Bluebook opened and updated today`, `Admission ticket saved`, `Alarm set` (wording to verify,
  open question 10).
* **Exam day before 13:00**: the order becomes hero, exam (the countdown to doors and the open
  checklist), next (`Warm-up · 5 easy · untimed · ~7 min` from the strongest skills), then every
  other card in its usual order. Nothing is collapsed (decision 4).
* **After** (13:00 on exam day onward): `How did it go? Scores come out around Oct 16
  [Remind me]` (U17 `scores_by`, `UI.ics(event)`), `.btn Add your official score`, and
  `Pick your next date`. Once the score is added, T10's calibration line shows and the plan CTA
  returns.

**Data.** `/api/today.next.stage = {mode, days, rehearsals:[{day, done}], sweep:{total, today,
done}, parked}`.

**Acceptance.**
1. Exam today + 12: `stage.mode == 'stretch'`; `/api/next` items contain no kind `untried` or
   `probe`; the Up next reason never reads "New skills".
2. Three traps closed 20 days ago → a Due row of kind `sweep`; the body has `sweep:true`.
3. On the rehearsal Saturday, `/api/today.next.items[0].title` starts "Dress rehearsal".
4. Exam today + 1 → Up next's title starts "Light warm-up"; the checklist `<details>` is open
   with 3 more items.
5. Exam today, 07:00 local: `#exam` is the second card in DOM order, and all other cards are
   present and expanded.

---

### D. The daily items

#### T14. The day's questions: pace, a twin in place, entry errors named, and a word in context

*From: the QOTD gaps of all three designers, unfair-advantage #3. Effort M. Builders: S3
(`daily.py`, the card), S9 (the word item and its grading), F3 (the in-column twin), F4
(`scoring.accepted_forms`).*

**Why.** Theirs gives an R&W question beside the Math one; ours had none. A miss should end on
a right answer. A grid-in entry mistake is a different fix from a wrong idea. Knowing your time
against everyone's builds pace.

**Changes to `#qotd`.**
* **Third slot, `WORD IN CONTEXT`**: the day's SAT word as an In-context item from Words (S9):
  a 2–3 sentence text with a blank, "Which choice completes the text with the most logical and
  precise word?", 4 words of the same part of speech. It is the same for everyone.
  * Desktop: under the two Math columns, full width, choices in a 2×2 grid. Below 1080px: a
    third tab.
  * After answering: the key, why each wrong word fails, the crowd spread (`UI.spread`, F1),
    `Add to my words` and `3 more like this` (a Words In-context quiz on that word's group).
  * It counts toward `N of 3` and the Due row. The day's-questions streak rule (one on-time
    answer) is unchanged.
  * Until S9 ships `words.daily_item`, the slot is absent and the card keeps 2 slots.
  * Only the SAT word appears; the math word of the day from the Words spec is dropped
    (decision 2).
* **Pace line** after the reveal (when the crowd has 5 or more): `You 1:12 · everyone 0:58 ·
  SAT pace 1:35`.
* **After a miss**: the first action becomes `Now its twin`, answered in the same column (T5).
  A right twin gives the slot mark the ↻ corner. It never counts in the crowd or the streak.
* **Entry errors**, for a grid-in: `Right value, rejected form: you entered 1 1/2. The grid
  takes 3/2 or 1.5.` or `Stopped too early: .66 for 2/3 needs 4 characters (.666 or .667).`
  The answer is still wrong, as the SAT marks it.
* **Header meta**: `3 in a row · best 11 · 19 of 23 right this month · crowd 61%`.
* The past-days strip carries a third mark per day.

**Data.**
* `GET /api/qotd` slots add `{slot:'word', question}` when `deps.part('words', 'daily_item')`
  exists; `question` has no key or reasons.
* `POST /api/qotd {slot:'word', answer, day, ms}` is filed through `words.record_daily` (S9,
  a `word_reviews` row with session `qotd-word:{day}`), once per day, with the same grace and
  late rules.
* Feedback adds `crowd.median_ms` (on-time answers), and for grid-ins
  `entry:{kind:'form'|'early', text}|null` from `scoring.accepted_forms` and the grid rule.
* `GET /api/qotd` adds `month:{right, of, crowd_pct}` and `best`.

**Acceptance.**
1. With the Words module present: `GET /api/qotd | jq '.slots|map(.slot)'` gives
   `["mcq","spr","word"]` and the word slot has no key. Without it: `["mcq","spr"]`.
2. `POST /api/qotd {slot:'spr', answer:'1 1/2'}` for a key of 3/2 returns `correct:false` and
   `entry.kind == 'form'`.
3. With 5 or more on-time answers, feedback has `crowd.median_ms` as an integer.
4. After a wrong MC, `Now its twin` renders a new stem inside `#qotd` without opening a
   dialog at 1280.

#### T15. The challenge card after you finish: your ten slots against the field

*From: unfair-advantage #10. Effort S. Builders: S3 (the card), S8 (the existing
`/api/contest/daily/review`).*

**Why.** Seeing which slot beat the field, and why, turns a rank into a lesson. Theirs reveals
nothing until a contest ends. Because ours are twins (decision 1), the pattern and the
misconception can be shown the same day without leaking anyone's key.

**Additions to `#chal`, once the student has finished:**
* 10 slot squares (R20 tokens) of the student's result, each with the field's % right under it
  in mono 10px.
* Tapping a square: `Slot 7 · Circles · 18% of 124 right · most picked: used the diameter as
  the radius`, with `.btn Twin slot 7` (T5).
* `You beat the field on 3 slots · hardest for the field: 7`.
* `.btn Twin your 2 misses` (T5, one after another in the sheet).
* The copy follows decision 1: `10 question types · the same for everyone, your own numbers ·
  ranked by right answers, then time`.

**Acceptance.** After finishing the day's challenge: `#chal` has 10 elements with the slot
role and a field % each. Before finishing, none are rendered and no review call is made.

---

### E. History and plan

#### T16. Test cards: why the points went, what fixing them is worth, and a retake as a twin

*From: the recent-tests gaps of all three designers, unfair-advantage #5. Effort M. Builders:
S6 (`UI.sittingCard` slots, the compare endpoint), S5 (the twin kind), F4 (`estimate.rescore`,
`progress.causes`), S3.*

**Why.** Their card offers only Review. A student needs to know why the points went, what
fixing them would have been worth on this paper, and, after work, whether the same paper with
new numbers now goes better. A fixed paper retaken measures memory.

**Additions to each finished card** (the shared sitting card):
* **Delta**: `+40 vs Sep 14` (the previous sitting of the same kind).
* **Causes**: `Lost 13: 6 traps · 3 clock · 2 slips · 1 entry · 1 gap` (T7's rule, one
  sitting).
* **Worth**: `Fixing the 6 traps ≈ +60 on this test`. This is exact: the sitting is re-marked
  with those positions right (`estimate.rescore(sid, positions)`, route held as taken). When
  the change would have routed module 1 up, it adds `and it would have sent you to the harder
  module 2`.
* **Time per module**: `M1 35:00 used · ran out at Q19 · 3 blank at time-up` (from `qstate`).
* **Percentile**, when n ≥ 20 (R16).
* **Total**, when `rw_now` is set: `≈ 1130–1210 with your R&W 610`.
* **Miss chips**: a tap opens a menu, `Review Q13` / `Twin` (T5).
* **Actions**: `Review`, `Fix 13`, and **`Retake as twin`** (`POST /api/mock/new {kind:'twin',
  twin_of: id}`), placed first when the sitting is 3 or more days old or has 5 or more misses.
  `New one like this` stays, as a `.quiet`.
* **A twin's card**: `Twin of Sep 21 · Fixed 9 of 13 · 2 new misses · 520–600 → 580–660
  (+60)`, from S6's `GET /api/session/{id}/compare?with={source}`.
* **Plan test day**: Up next's default is `Twin of your last test · measures what changed`
  when the last same-kind sitting is 7 or more days old, with a `Fresh test` toggle.

**Acceptance.**
1. A finished module with 3 wrong named answers and 2 blanks at time-up: the card's cause line
   sums to 5, and `estimate.rescore(sid, [those 3])` gives a midpoint above the original.
2. `Retake as twin` posts `{kind:'twin', twin_of}`, and the new sitting's slots match the
   source's templates and tiers (S5's check 13).
3. After the twin finishes, its card shows "Twin of" and "Fixed N of M".
4. A tap on a miss chip shows a menu with exactly "Review Q…" and "Twin".

#### T17. The study card: where the time went, any day redone, and a goal worked out from the work

*From: experience #8, the study, calendar, goal and streak gaps of all three designers. Effort
M. Builders: S3, F4 (the calendar rows, `due_forecast`), F1 (`UI.calendar` metric option).*

**Why.** Minutes alone reward sitting. A student should see whether the time went where the
points are, turn any past day into a set, and get a daily goal worked out from the work left,
not guessed.

**Additions to `#study`.**
* **Figures**: each sub-line adds fixes: `38m Today · 31 questions · 71% right · 3 fixed`.
* **Where the time went** (this week): one stacked bar of minutes by domain, with two reference
  bars under it, the test's share (35 / 35 / 15 / 15) and the share of points on the table
  (T6). Line: `62% of your time on Algebra · 35% of the test · 18% of your points`.
  `.btn Rebalance · 10 in Advanced Math` → `{topics: that domain's top-gain skills, count:10,
  source:'gain'}`. A second line splits the minutes into new, fixing, review and tests.
* **Daily goal popover**: each chip shows `≈ 30 q` (minutes × 60 ÷ median seconds). With an
  exam date, `Suggested: 35 min` and its arithmetic from `today.workload`: `(23 open mistakes ×
  2 + 18 check-ins + 2 sections) at 1:40 each ÷ 28 study days`. The weekly line reads
  `2h 5m of 5h · 58 min a day for the 3 days left`.
* **Footer**: `4-day study streak · best 9 · 1 spare` (U16) · `goal met 9 of the last 14 days`
  · `held 82% of 40 warm-up answers this month` (T3).
* **Calendar**:
  * `.seg Minutes · Questions · Accuracy · Fixed` recolours the heat with the same 3 levels.
    Accuracy draws a hollow cell under 5 answers, so a 1/1 day doesn't read as perfect.
  * Future cells show `3 due` (check-ins, T3) and the plan's load.
  * Plan rest days carry a small shield glyph (`aria-label` "rest day, streak safe"), and a
    spent spare day a hollow ring (U16), on the calendar and the week strip.
* **Day detail**, for a past day, adds:
  * `Mistakes that day: 3 opened · 2 closed`, each label linking to
    `/review/?open=trap:{id}`;
  * the topics as chips with right/asked (`Percentages 4/7`);
  * `9:12 AM – 10:05 AM` (first and last answer);
  * `.btn Redo this day's misses · 5` → `{pool:'history', ids:[that day's wrong first-try
    attempt ids], exact:false, each:1, source:'today'}`, hidden when there were none.
  * For a future day: `Planned · Practice · 38 q · warm-up: 3 check-ins, about 4 fading`.
* **Calendar export**: when `prefs.study_time` is null, the Add to calendar sheet offers
  `You usually start around 20:30 · Use it` (the median local start of sittings over 30 days),
  which writes `prefs.study_time`.

**Data.** `/api/calendar` day rows add `fixed, opened:[{id, label}], closed:[{id, label}],
topics:[{topic, right, asked}], first_at, last_at, missed:[attempt id], due:{checks, fading}`.
`/api/today/insights.time_split = {domains:{d: minutes}, kinds:{new, fix, review, test},
test_share, points_share}`. `/api/today.goal_suggest = {minutes, arithmetic}`.

**Acceptance.**
1. A day with 5 wrong first tries: its Redo button's body has 5 attempt ids, and the session it
   creates serves 5 templates matching those attempts, each on a new seed.
2. The Accuracy heat draws a hollow cell for a day with 1 answer.
3. `time_split.domains` sums to the week's practice minutes (± 1).
4. With `exam_date` set, the goal popover shows "Suggested" with a chip value, and the chip
   meta "≈ N q".

#### T18. The plan card: adherence, pace, make-ups, previewed fixes, and a plan in one tap

*From: the plan gaps of all three designers. Effort M. Builders: S3 (the card), S7
(`POST /api/plan/preview` week sample, PATCH, stats), U25's Undo.*

**Why.** Theirs copies four tiles and sends a behind student to rebalance; their generator
failed 3 of 3. A student needs to know if the plan is working, fix a missed day in one tap, and
get a plan without a wizard.

**No plan: `Build with these`** (above v2's CTA, which stays under it).
* Three inline controls, prefilled:
  * `SAT date [Nov 7 ▾]`: the profile's date, else the next official date;
  * `Daily [45 min ▾]`: `profile.minutes`, else the 7-day average rounded to 15 (at least 20);
  * `Days [Mon–Fri]`: the weekdays actually studied over 28 days, else Mon–Fri.
* The target is `profile.target`, else the band's high end + 50. The start is the latest band's
  midpoint.
* Under them, the first 7 days drawn read-only with `UI.taskRow` from `POST /api/plan/preview`
  (`week`), plus its pace tag.
* Pill `Use this plan` → `POST /api/plan` with that draft. Today repaints with the plan and Due
  today fills. `.quiet Adjust…` → `/plan/?step=1` with the draft saved.

**Plan set.**
* **Stat row**: `Day 12 of 45` · `20% done · 9 of 45 study days` · `On time 9 of 10 study days`
  (adherence, replacing `10 days to the SAT`, which the countdown shows) · `Behind · making +9
  a week, needs +18` or `On pace` (Plan's pace status with U9's slope, replacing `+140 to
  target`, which the Score card's gap line shows).
* **Week strip**: each day column adds a 4px studied-vs-planned bar, its topic glyphs, and for
  past days `2 fixed · 1 held` in mono 10px. A missed day gets `.quiet Make up` (starts its
  catch-up task, `task=<date>:focus`, which Plan marks `made_up`). A future day gets
  `.quiet Work ahead` (starts that day's set now).
* **Behind**:
  * what it cost: `2 study days missed · 4 check-ins now overdue · 2 mistakes older than 10
    days`;
  * the region's primary: `Catch up · 15 min` (a box of 15, T1);
  * two previewed fixes, each `.btn Apply` with Undo: `Shorter days: 30 min × 6 days · still
    Steady` (`PATCH {minutes: behind.suggest_minutes}`) and `Later date: Nov 7 · +11 a week`
    (`PATCH {exam_date: preview.later_date}`);
  * `.quiet Change daily time` stays.

**Acceptance.**
1. A learner with 40 answers and no plan: `Build with these` shows 3 controls and 7 day rows.
   `Use this plan` sends one `POST /api/plan`, after which `/api/today.plan` is non-null.
2. With a plan: the stat row has "On time" and no "days to the SAT".
3. A missed past study day: its `Make up` starts a drill with `task` equal to
   `<that date>:focus`. After finishing, the day reads made up.
4. Behind with 2 missed days: two Apply buttons. Applying the first sends
   `PATCH {minutes}`, and Undo sends the old value.

---

### F. Motivation and speed

#### T19. The hero's briefing, the streak at risk, and the day's receipt

*From: outcomes #11, experience #7, the hero gaps of all three designers. Effort S. Builders:
S3 (`today.brief`, `today.receipt`), F4 (`progress.days`).*

**Why.** Seeing what yesterday's work changed, and what came due, is what brings a student back
tomorrow. Theirs shows a greeting and an illustration, a streak that disagrees with itself, and
an "All Done" badge that marks completion, not outcome.

* **Briefing line** under the heading (Archivo 15, ink-soft): up to 3 facts, most urgent first,
  each a link to its place:
  * `Period 3's Circles set is due at 5:00 PM`;
  * `2 mistakes you fixed 10 days ago are due a check-in`;
  * `Module on Sep 21: 520–600 · +40` (a sitting or outside score since the last study day);
  * `Yesterday: 42 of 45 min · 3 mistakes fixed · challenge #4 of 30` (or `Since Mon: …` when
    the last study day was earlier), shown when the last study day isn't today;
  * `Percentages is now Strong` (a mastery word that changed on the last study day).
* **Streak at risk**: after 18:00 local, with nothing done today, a study streak of 2 or more,
  and today not a plan rest day, the first fact becomes `One answer keeps your 6-day streak ·
  5h 12m left today` with an inline `.btn 1 question` (T5's sheet on a due check-in, else the
  coach's pick, `source:'try'`). With a spare banked (U16) it adds `· or a spare covers it`.
* **The day's receipt**: the first time today that the Due list is all done or the minutes
  reach the goal, Up next opens with `TODAY'S WORK`, entering with a `.rise` that never loops:
  * `48 min · 38 questions · 74% right`;
  * `Moved: Percentages Learning → Getting there`;
  * `Fixed: Added the percentages instead of multiplying them (+2 more)`;
  * `Check-ins held 3 of 3 · 1 relapse caught`;
  * `≈ +8 claimed from your points on the table` (U4's total at local midnight minus now);
  * the flame: `7 days · best 9`.
  Then the pill `Keep going · 15 min` and `.quiet See today in the calendar`. On later visits
  the same day, the receipt is one line at the top of Up next with its `Show`.
  `localStorage satf.done.{day}` (try/catch) remembers the first showing; without storage it can
  show again, which is harmless. `prefers-reduced-motion` turns off the rise.

**Data.** `/api/today.brief = [{kind, text, href}]` (≤ 3), `.at_risk = {streak, left_ms,
start:{body}, spare}|null`, `.receipt = {minutes, questions, right, moved, fixed, checks,
relapses, claimed, streak, best}|null`. "Since" is the start of the last study day from
`progress.days`, so no new column is written on every GET.

**Acceptance.**
1. A learner who studied yesterday and closed 3 traps: `brief` contains a fact starting
   "Yesterday" with "3 mistakes fixed".
2. Playwright with the clock at 19:00 local, a 6-day streak and nothing today: the first
   hero fact contains "keeps your 6-day streak", and its button opens `dialog` with a question.
   At 17:00 it doesn't appear.
3. After the goal's minutes are reached, `receipt` is non-null, and `#next` shows "TODAY'S
   WORK" once. A reload shows the one-line form.

#### T20. Instant and keyboard-first

*From: experience #9, U23, U25. Effort S. Builders: F2 (`UI.cached` day option, `UI.keys`), S3.*

**Why.** Today is opened many times a day. Every visit should paint the real page at once, every
edit should feel instant, and a keyboard user should never need the mouse.

* **Paint from the last visit**: `/api/today`, `/api/today/insights`, `/api/qotd`,
  `/api/contest/daily` and `/api/history` go through `UI.cached(path, {store:'local',
  until:'day'})` (U23 with a day-scoped localStorage option), so a new tab paints too. A mono
  11px `Updating…` shows on a `--line` top rule until the live response arrives. A card
  repaints only when its part of the JSON changed. A first visit uses the skeletons.
* **Optimistic edits**: skip, move, swap, dropping a box block, the daily goal, the target and
  the exam date apply at once, show U25's Undo toast for 6 s, and revert with `Not saved. Try
  again.` on failure.
* **Page keys** (`UI.keys` scope `today`, listed in `?`): `J` / `K` next / previous card (focus
  moves to its heading and scrolls it into view), `T` Try one now, `Enter` on a focused card
  heading runs that card's primary. `G N` (U1) starts Up next. The inline question takes A–D /
  1–4 and Enter while it has focus (F3). Palette entries: "Start today's set", "Warm-up",
  "Fix top mistake", "Question of the day".
* **Phone**: the day's-question tabs also switch with a horizontal swipe on the question body
  (pointer events, 60px, off while an input has focus). Each card's primary sits at its bottom.
  Pointer-down on Start adds `<link rel=prefetch href=/practice/session/>`.

**Acceptance.**
1. Second visit (Playwright, same context): `#next` shows real content, not `.skel`, within
   50 ms of DOMContentLoaded.
2. `PATCH /api/plan/...` intercepted to 500: the skipped row reverts and shows "Not saved. Try
   again."
3. Pressing `J` twice from the top moves focus to the third card's heading.
4. At 390, a 70px left swipe on the MC question shows the grid-in tab.

---

## 3. Spec overrides

### 3.1 Inside §3.2 (spec/rebuild-v2.md lines 2295–3347)

Each entry quotes the current text, then gives the replacement or addition.

1. **Box at the top.**
   * Quote: "> **Read with resolutions:** R2, R10, R13, R14, R15, R16, R17, R26, R27, R30, R38
     (§2.2). Where this spec disagrees with them, they win."
   * Append: "Read with `spec/v2-upgrades/today.md` (T1–T20), which wins over this section, and
     with `shell-me.md` U1, U4–U7, U9, U13, U15–U17, U23 and U25, whose functions Today reads."

2. **§0 Rules for this page.**
   * Quote: "- Every feature of their dashboard has an equivalent here that does more, and
     nothing is cut or hidden for looks."
   * Add after it:
     * "- **One source per fact.** Up next and Due today (`next.queue`, `next.due`), points on
       the table (`estimate.gains`), pace (`progress.pace`), causes (`progress.causes`), the
       warm-up (`progress.warmup_candidates`) and the workload (`today.workload`) each come
       from one function and read the same on every screen."
     * "- **Every figure explains itself** (U13), and **every end leads on**: each finish
       screen offers the next Due row."

3. **§1 Layout, desktop.**
   * Quote the block from "hero  ×12" through "tests ×12".
   * Replace with T1's layout block ("Layout after these upgrades"), including the final-stretch
     and exam-day variants.

4. **§1 Layout, tablet.**
   * Quote: "**Tablet (760–1079px)**, 2 columns: `hero hero / next next / qotd qotd / score exam
     / study study / mist chal / plan plan / tests tests`. The questions of the day use tabs."
   * Replace with: "**Tablet (760–1079px)**, 2 columns: `hero hero / next next / qotd qotd /
     gain gain / mist exam / score pace / study study / chal words / plan plan / tests tests`.
     The questions of the day use tabs (3 with the word slot)."

5. **§1 Layout, phone.**
   * Quote: "**Phone (<760px, designed at 390px)**, one column: hero, next, qotd, exam, score,
     mist, study, plan, chal, tests."
   * Replace with: "**Phone (<760px, designed at 390px)**, one column: hero, next, qotd, gain,
     mist, exam, score, pace, study, plan, chal, words, tests."

6. **§1 Cards.**
   * Quote: "- Each card is a `<section aria-label>` with an id that the other cards link to:
     `#next #qotd #exam #score #study #plan #mist #chal #tests`."
   * Replace the id list with: "`#next #qotd #gain #exam #score #pace #study #plan #mist #chal
     #words #tests`."

7. **§1 Errors.**
   * Quote: "- The QOTD, calendar, challenge and tests cards have their own calls, errors and
     Retry."
   * Replace with: "- The QOTD, calendar, challenge and tests cards have their own calls, errors
     and Retry. `#gain`, `#pace` and the forward parts of `#score` (practice delta, evidence,
     projection, verdict, where points went) read `GET /api/today/insights`; if it fails they
     show `Couldn't load this.` with one Retry, and the band, scale and trend still paint from
     `/api/today`."

8. **§2 Hero.**
   * Quote: "**Heading** (`h1.h1`): `Good morning, Aziz`."
   * Add after the heading bullets: "**Briefing line** and **streak at risk**: T19."
   * Quote: "- **Plan** (only with a plan): `Plan · 1 of 2 done`, or `Plan · rest day`. Links to
     `#next`."
   * Add after it: "- **Final stretch** (exam ≤ 14 days, T13): `Final stretch · 12 days`, links
     to `#exam`."
   * Quote: "**Better than theirs**: the same greeting and date, with the decorative
     illustration replaced by four live facts that each lead somewhere."
   * Replace with: "**Better than theirs**: the same greeting and date, then a line that says
     what changed and what is owed, and live chips that each lead somewhere."

9. **§3 header.**
   * Quote: "**Header**: `UP NEXT` on the left. On the right, when a plan is set: `Today in your
     plan · 60 min`, `Test day in your plan · 70 min` or `Rest day in your plan`."
   * Add: "Under it, the time seg `Time today: 5 · 15 · 30 · 45 · 60 min` (T1). Items 1–3 of §3a
     come from `next.queue` (`resume`, `assignment`, `plan` test)."

10. **§3a item 4.**
    * Quote the block from "**4. The coach's set**" through "- **Start**: the pill. It sends
      `POST /api/drill {topics, count, timed, minutes: timed ? minutesFor(count) : null,
      source:'coach'}`, then goes to `/practice/session/?id=`."
    * Replace with: "**4. The time box** (T1): the reason line (value first), the numbered
      blocks from `POST /api/drill/preview {source:'next', box, drop}` with × to drop, question
      1 inline (`first` token), and the pill `Start · {box} min`. v2's topic chips, count
      choices, clock, estimate and More options stay behind `.quiet Count instead`, unchanged."

11. **§3a Goal met.**
    * Quote: "- A line with a check: `Today's goal done · 64 of 60 min`."
    * Replace with: "- The day's receipt (T19), then the box with the pill `Keep going · 15 min`."

12. **§3a New student.**
    * Quote: "- The coach's `new` pick."
    * Replace with: "- The coach's `new` pick as a box, with `.btn Learn it · example + 3` (T4)."

13. **§3b The Today list.**
    * Quote from "**With a plan**, two groups:" through "- A `.quiet` at the end: `Build a plan to
      set a daily goal`."
    * Replace with T2's header, groups (`PLAN` and `ALSO DUE`) and rows 1–9. Keep the `.quiet`
      `Build a plan to set a daily goal` at the end without a plan.
    * Quote: "- **`Why`**: a `.quiet` toggle that opens one line of reason, and turns into `Hide`
      while open."
    * Replace with: "- **`Why`**: a `.quiet` toggle that opens the evidence line (T2: mistakes,
      recent accuracy, questions a section, ≈ points, minutes) and `See the evidence`; it turns
      into `Hide` while open."
    * Quote: "- **Action** (`.btn`): `Start`, `Continue`, `Resume`, or `Practice again` once done
      (a fresh coach set)."
    * Add after it: "- **Result** once done (T2), and `Fix the N it opened` when it opened
      mistakes. ⋯ adds `Swap for: {topic}` when the plan task has alternatives."
    * Quote: "- **Challenge**: finished."
    * Add after it the completion rules of T2 (homework, warm-up, sweep, words, contest).
    * Quote: "- If a mark fails, the row reverts and shows `Not saved. Try again.`"
    * Replace with: "- Every edit applies at once with an Undo toast (U25). If it fails, the row
      reverts and shows `Not saved. Try again.`"

14. **§4 Mistakes.**
    * Quote: "**Top 5 open traps** (`today.traps.top`, ordered by hits, then by most recent).
      Each row shows:"
    * Add before it: "A `.seg By question type · By habit` (T9). Blind spots (T9) sort first
      under `BLIND SPOTS · N`."
    * Quote: "- The first row also has a `.btn` **`Try one now`**, which opens
      `dialog.sheet#tryOne`:"
    * Replace with: "- The first row also has a `.btn` **`Try one now`**, which opens
      `UI.twinSheet` (T5) with `{pool:'redo', ids:[trap id], count:1, source:'try'}`:" (the
      sub-bullets stay).
    * Add at the end of the row list: "- A relapsed row carries `Relapsed · learn it again`
      (T4)."

15. **§5 Questions of the day, intro.**
    * Quote: "Theirs gives one R&W and one Math. We have no R&W bank, so ours are **one
      multiple-choice and one grid-in Math question**. That covers both SAT Math formats, and
      grid-in entry rules are where points leak unnoticed. Both are the same for every student
      on the same local date."
    * Replace with: "Theirs gives one R&W and one Math. Ours are **one multiple-choice and one
      grid-in Math question, and one Word in context** (the SAT R&W item type, from Words; T14).
      All three are the same for every student on the same local date."
    * Quote: "###### Desktop (≥1080px): two columns, both visible"
    * Add under its bullets: "- The Word in context slot runs full width under the two columns."
    * Quote: "- Right: the day's-question streak, a flame with `3 days in a row`, or `Start a
      streak`. The `aria-label` reads `Day's questions streak, 3 days`."
    * Append: "Meta after it: `best 11 · 19 of 23 right this month · crowd 61%` (T14)."
    * Quote: "4. **Actions row** (`.btn`s):"
    * Add before it: "3b. **Pace line** (crowd ≥ 5): `You 1:12 · everyone 0:58 · SAT pace 1:35`.
      **Entry line** for a grid-in entry error (T14)."
    * Add as the first action: "- After a miss: `Now its twin`, answered in the column (T5)."
    * Quote: "- `PAST DAYS`, then 7 buttons for the 7 days before today. Each shows a weekday
      letter and two mini marks (MC, grid-in):"
    * Replace "two mini marks (MC, grid-in)" with "a mini mark per slot (MC, grid-in, word)".

16. **§6 Study time.**
    * Quote: "- `38m` **Today**, then `31 questions · 71% right`. With a goal, `of 60m` and a 4px
      amber goal bar. On a plan rest day it reads `Rest day`."
    * Replace `31 questions · 71% right` with `31 questions · 71% right · 3 fixed`.
    * Quote: "- The helper line: `Your plan uses this as a study day's length.`"
    * Add after it: "- Each chip shows `≈ N q`. With an exam date: `Suggested: 35 min` and its
      arithmetic (T17). The weekly line says what is left per remaining study day."
    * Quote: "**Heat**, from that day's minutes:"
    * Replace with: "**Heat**, from the metric chosen in `.seg Minutes · Questions · Accuracy ·
      Fixed` (default Minutes; Accuracy is hollow under 5 answers):"
    * Quote: "- **A past day or today**: `Mon, Sep 21 · 42 min · 31 questions · 71% right`, then
      that day's sittings as links."
    * Add after it: T17's day-detail lines (mistakes opened and closed, topic chips, first and
      last times, `Redo this day's misses · N`).
    * Quote: "- **A future plan day**: `Planned · Practice · 38 questions` or `Planned · Module
      test`, plus `Open in plan` (`/plan/?day=`)."
    * Append: "It adds `warm-up: 3 check-ins, about 4 fading` (T3). Future cells show `3 due`."
    * Quote: "**Footer**: `4-day study streak · best 9`."
    * Replace with: "**Footer**: `4-day study streak · best 9 · 1 spare` · `goal met 9 of the
      last 14 days` · `held 82% of 40 warm-up answers this month`."
    * Add a new sub-section before "###### This week vs last": "###### Where the time went"
      (T17).

17. **§7 Daily challenge.**
    * Quote: "- `10 questions · 16 min · the same for everyone · ranked by right answers, then
      time`."
    * Replace with: "- `10 questions · 16 min · 10 question types, the same for everyone, your own
      numbers · ranked by right answers, then time`."
    * Quote: "- **Finished**: a big `#12`, meta `of 124 · 8/10 · 11:32`, and a `.quiet` `Full
      board` to `/challenge/`."
    * Append: "Then the 10 slot squares against the field, and `Twin your N misses` (T15)."

18. **§8 Plan.**
    * Quote: "- `.btn` `Build my plan →`."
    * Add before the CTA's title: "**Build with these** (T18): 3 prefilled controls, the first 7
      days drawn from the preview, the pill `Use this plan`, and `.quiet Adjust…`." The CTA
      keeps its steps, preview, bullets and helper; `Build my plan →` becomes a `.quiet`.
    * Quote: "- `10 days to the SAT`"
      → "- `On time 9 of 10 study days`"
    * Quote: "- `+140 to target`, with `560 → 700` under it"
      → "- `On pace`, or `Behind · making +9 a week, needs +18`"
    * Quote: "- the planned load: `38q` or `Module`."
    * Add after it: "- a 4px studied-vs-planned bar, the day's topic glyphs, and for past days
      `2 fixed · 1 held`; `Make up` on a missed day and `Work ahead` on a future one (T18)."
    * Quote: "**Behind**: shown when 2 or more of the last 7 study days were missed (skipped days
      don't count). It reads `2 study days missed this week. Nothing piles up: each day is
      redrawn from your results. If the days are too long, shorten them.` with the `.btn`
      `Change daily time` (`/plan/?step=2`)."
    * Replace with T18's Behind: the cost line, `Catch up · 15 min`, two previewed fixes with
      Apply and Undo, and `.quiet Change daily time`.

19. **§9 Score.**
    * Quote: "**Gap**"
    * Add before it: T10's "Practice since the last test" and "Evidence" lines.
    * Quote: "**Trend** (`UI.bandChart`, lifted from the /results/ chart)"
    * Add to its bullets: "- U9's projection cone to the exam date, the exam tick and the plan's
      pace line; the verdict line and `Made / needs` figures; calibration after an official
      score (T10)." Then add the block `WHERE POINTS WENT · LAST 14 DAYS` (T7).
    * Quote the block from "**Domains**" through "- The domain with the most traps gets the tag
      `Most points to fix`."
    * Replace with: "**Domains**: moved to `#gain`, By domain (T6), with `Most points to fix` on
      the domain with the largest summed gain."
    * Quote: "- `Your last 3 tests average 610; your plan started from 560.`"
    * Add after it T10's drift evidence (sitting chips), what moved, the effect preview and the
      downward form.

20. **§9 Target dialog.**
    * Quote: "- The reference line `Latest 520–600 · Plan start 560`."
    * Add after it: "- **What it takes** (T11): of-44, where the misses are, the route note above
      580, the pace tag, the later-date chip; each quick chip carries its tag; `Raise to 750?`
      once reached."

21. **§10 SAT countdown.**
    * Quote: "###### Live countdown"
    * Add before it: "###### Capacity (T12): the main figure `7 study days · ~5h 15m at your goal
      · 2 tests left`, the need-against-capacity line, and the registration line (U17)."
    * Quote: "- Four boxes, `DD : HH : MM : SS` (`.num` 56px, 40px at phone, tabular), labelled
      `DAYS HOURS MIN SEC` in `.k`. Days use 3 digits at 100 or more."
    * Replace `.num` 56px, 40px at phone with `.num` 28px at every width.
    * Quote: "- Only the **upcoming** official dates from `UI.SAT_DATES` (moved out of /plan/).
      Each reads `Oct 3, 2026 · Sat · in 10 days`, with a check on the current one."
    * Replace with: "- Only the **upcoming** official dates (`/api/shell.dates`, R15), through
      `UI.examDate`. Each reads `Nov 7 · Sat · in 45 days · 32 study days · +11 a week · Steady
      · register by Oct 23` (plus `~690` when projected), with a check on the current one and
      `Recommended` on the first Steady date (T12)."
    * Quote: "- `Calculator, optional: Desmos is built in`"
    * Add after it: "- On the eve, a `Night before` group: `Bluebook opened and updated
      today`, `Admission ticket saved`, `Alarm set` (T13)."
    * Quote the "- **Exam day**:" and "- **Passed**:" state blocks.
    * Replace with T13's `exam` and `after` modes, and add T13's `stretch`, `taper` and `eve`
      modes, readiness rows and the countdown additions.

22. **§11 Recent tests.**
    * Quote: "- **Meta**: `31/44 right · 64 min`."
    * Add after it: T16's delta, causes, worth, time per module, percentile and total lines.
    * Quote: "- Each chip links to `/results/report/?id=…&q=M1-3`."
    * Replace with: "- A tap on a chip opens a menu: `Review Q3` (`/results/report/?id=…&q=M1-3`)
      and `Twin` (T5)."
    * Quote: "- `.btn` `New one like this`: `POST /api/mock/new {full: kind==='mock'}`, a
      never-seen test of the same shape."
    * Replace with: "- `.btn` `Retake as twin`: `POST /api/mock/new {kind:'twin', twin_of: id}`,
      first when the sitting is 3+ days old or has 5+ misses. `.quiet` `New one like this`
      stays. A twin's card shows `Twin of {date} · Fixed N of M · …` (T16)."

23. **§12 Data and refresh.**
    * Quote: "- `/api/tests/recent?limit=6`"
    * Replace with: "- `/api/history?kind=tests&all=1&limit=6` (R26)" and add "- `/api/today/insights`".
    * Quote: "Each card paints when its own call resolves. The hero's date and greeting paint from
      the client clock before any call returns."
    * Append: "Every card first paints from `UI.cached` (T20) when a copy from today exists."

24. **§13 States matrix.** Add rows:
    * `final stretch (≤ 14 days)` → hero chip; `#exam` full width with readiness; rehearsal on
      Saturdays; Sweep row; Fix parked; no new rare skills.
    * `exam eve` → Up next `Light warm-up`; checklist open with Night before.
    * `exam day, before 13:00` → order hero, exam, next; nothing collapsed.
    * `after the exam` → scores date with Remind me; Add your official score; calibration once
      added.
    * `streak at risk (after 18:00)` → first hero fact and `1 question`.
    * `day done` → the receipt once, then its one-line form.
    * `/today/insights fails` → gain, pace and score's forward parts show `Couldn't load this.`
      + Retry; the rest renders.
    * `under 30 answers` → `#gain` shows "Answer 30 questions · N of 30".
    * `Words module absent` → 2 day's-question slots; no words row.

25. **§14 Accessibility and motion.**
    * Quote: "- Motion is entry only (`.rise`, staggered by row), and nothing loops.
      `prefers-reduced-motion` turns off the rises and the count-up."
    * Append: "The receipt enters once a day. Page keys `J` / `K` / `T` (T20). The causes bar,
      the pace strip, the where-the-time-went bar and the points tracks each have a hidden data
      table and text labels."

26. **§3.2.4 Extras.** Append one line per upgrade T1–T20, using each upgrade's "Why".

27. **§3.2.5 Server changes.**
    * Quote: "- **GET /api/today: new fields**"
    * Add to its list: `next` (T1), `due` (T2), `warmup` (T3), `traps.blind`, `traps.habits`
      (T9), `brief`, `at_risk`, `receipt` (T19), `goal_suggest` and `workload` (T12, T17),
      `next.stage` (T13).
    * Add a new item: "- **GET /api/today/insights (new)**: `{subject, gains, causes, pace,
      estimate, time_split}` (T6–T10, T17)."
    * Quote: "- **POST /api/qotd: slot, ms, grace, late answers, richer feedback**"
    * Add: "`slot:'word'` (T14); feedback `crowd.median_ms`, `entry`; GET adds `month`, `best`."
    * Quote: "- **POST /api/drill: like, templates, count in mistakes mode**"
    * Add: "`first`, `drop`, `box` preview blocks (T1); `source:'warmup'` with `cfg.hide_skill`
      (T3); `source:'learn'` with `example` (T4); `sweep` on pool `checks` (T13); sources `gain`,
      `pace`, `today`. All through F5's one contract (§2.6)."
    * Quote: "- **GET /api/calendar?month=YYYY-MM (new)**"
      Add to its response: T17's day-row fields and `due` for future days (T3).
    * Add: "- **server/today.py (new, S3)**: `brief`, `receipt`, `workload`, and the insights
      assembly."
    * Quote: "- **server/test_flow.py**"
      Add: "Checks in `server/checks/s3.py` cover T1–T20's server acceptance items."

28. **§3.2.6 Files.** Add rows: `server/today.py` S3; `server/next.py` F2 (`due`, `stage`);
    `server/habits.py` F5; `server/estimate.py` F4 (`practice_delta`, `per_question`,
    `rescore`); `server/checks/s3.py` S3.

29. **§3.2.7 Shared needs.** Add:
    * "`UI.twinSheet` and the in-column twin, `hideSkill`, the worked-example card → F3."
    * "`UI.cached(path, {store:'local', until:'day'})` → F2."
    * "`UI.bandChart` projection cone and pace line (U9); `UI.strip` with a marker; `UI.calendar`
      metric option and `due` marks; `UI.skillRow` track with two ticks → F1."
    * "`UI.examDate` rows with per-date pace, projection and deadlines → F1 (U17)."

30. **§3.2.8 Acceptance.**
    * Quote: "16. At 1280 the two day's questions are side by side and both show their stems. At
      390 they are tabs with status marks. At 390 the cards stack in the order hero, next, qotd,
      exam, score, mist, study, plan, chal, tests; …"
    * Replace the order with: "hero, next, qotd, gain, mist, exam, score, pace, study, plan,
      chal, words, tests". With the Words module present, the tabs are three.
    * Quote: "17. With a plan and a practice set of 5 answered out of 38: the Today list reads
      PLAN · 0 of 1 done with '5 of 38 questions', …"
    * Replace "the Today list" with "the Due today list's PLAN group".
    * Quote: "15. shot.py a:v2revacc3 1280 … http://localhost:8000/ for a new code: every card
      shows its empty state with an action (…)"
    * Add to its list: "`#gain` 'Answer 30 questions', `#pace` 'Your pace shows after 20
      answers', Warm-up empty line, the box with question 1".
    * Append T1–T20's acceptance lists as items 29 onward.

31. **§3.2.9 Open questions.** Add:
    * "Rehearsal start time: the default 08:30 and '70 min + break' should match when the Math
      section really starts on SAT day (after R&W and the break); verify with College Board."
    * "The warm-up intervals (2, 5, 12, 30 days) are a stated choice, not a measurement; revisit
      them once held rates exist."
    * "The word-in-context slot depends on S9 shipping `words.daily_item`; until then Today
      keeps two slots."

### 3.2 Outside the section (Part 2 and shell-me lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| shell-me U1 `next.queue` | Adds kind `resume` for an unfinished drill (v2 §3a item 2) and a plan test day as `plan` with `test`. Row 4 `checks` starts `{source:'warmup'}`. `next.due(learner, tz)` is the source of rows 1–4 and of Today's Due list. `next.stage` holds T13's modes (stretch, taper, eve, exam, after) and drops `new` for rare skills in the stretch | T2, T3, T13 |
| shell-me U1 box | Segment 1 is `progress.warmup_candidates` (check-ins due, then fading), up to 3. The preview returns `blocks` with stable keys, and the body takes `drop` and `first`. The box options are 5–60 (Today offers 5, 15, 30, 45, 60) | T1, T3 |
| shell-me U1 chaining | Add the words run end (S9), the contest result (S8) and the assignment finish (S2) to the finish screens that show "Next: {title}" | T2 |
| shell-me U23 | `UI.cached(path, {store:'local', until:'day'})`: localStorage keyed to the local date, dropped when it changes, same 200 KB cap and sign-out clearing | T20 |
| R9 | Check-ins also feed `progress.due_forecast`; in the final stretch, pool `checks` with `sweep:true` selects traps closed in the last 90 days and not yet swept | T3, T13 |
| R16 | `estimate.py` adds `practice_delta`, `per_question`, `rescore(sid, positions)`; `gains` adds `tiers`, `extras`, `by_domain` | T6, T7, T10, T16 |
| R19 | Twins from a live test's positions are refused (409), as for any exact item | T5 |
| R24 | Sources `twin` and `try` from Today stay inline; `warmup`, `learn`, `pace`, `gain` and `today` are ordinary sittings | T3–T5 |
| §2.5 | No new tables. The warm-up, causes, habits' broken state and sweep are computed from existing rows. `kv` holds `preview_secret`, which F5 writes once at init | T1, T3, T7, T9, T13 |
| §2.6 | Fields: `first {token, answer, ms}`, `drop [key]`, `example` (bool), `sweep` (bool, pool checks). Sources: `warmup` (sets `cfg.hide_skill`), `learn`, `gain`, `pace`, `today`. The preview returns `blocks` and `first` for `source:'next'` | T1, T3, T4, T6, T8, T13, T17 |
| §2.8 | Page scope `today`: `J`, `K`, `T` | T20 |
| §2.9 | Providers: F4 `progress.causes`, `progress.warmup_candidates`, `progress.due_forecast` → S3, S7, S10; F2 `next.due`, `next.stage` → S3, S7; F3 `UI.twinSheet` → S3, S6, S8; S8 `compete.due_today` → S3; S2 `classes.due_soon` → S3 (already in U1); S9 `words.daily_item`, `words.record_daily` → S3; S6 `GET /api/session/{id}/compare?with=` → S3, S5; S7 preview `week` (7 days of `{date, kind, minutes, topics}`) → S3 | all |
| S7 Plan | The recheck task's start body is `{source:'warmup', task:'YYYY-MM-DD:recheck'}`. The Final phase's test days are Today's rehearsals. `skills[].gap` reads `estimate.gains`. `POST /api/plan/preview` returns `week` | T3, T6, T13, T18 |
| S9 Words | The Words spec's math word of the day is not shown on Today (decision 2); the SAT word becomes the Word in context slot | T14 |
| S6 Results | `UI.sittingCard` takes extra lines (delta, causes, worth, time per module, total) and a chip menu; the compare endpoint | T16 |

---

## 4. Rejected

* **A `Sure · Not sure` tap before every Check** (outcomes #8, the experience QOTD gap): most
  students won't tap it, and `shell-me.md` rejected the same tap. Blind spots are inferred from
  speed, guess flags and test confidence instead (T9).
* **An absolute practice score ("From practice: ~560 ±50") and a hero `Est. ~560` chip**
  (outcomes #6): U4 never shows `S` as a score. The practice delta shows the movement, and the
  band stays R16's.
* **Traps ahead, predicted from the crowd at your band** (unfair-advantage #7): it needs crowd
  volume we don't have, and it falls back to generic distractors. The gauntlet (U6) and Learn
  it (T4) cover prevention from the student's own data.
* **Print today's pack with a QR code to enter answers later** (unfair-advantage #9): a niche
  need. Review's worksheet already prints any set.
* **"What if I study 60 min a day?" and "+15 min a day → 630–690"** (experience #5,
  unfair-advantage score gap): there is no defensible model from minutes to points
  (`shell-me.md` rejected the same).
* **A daily goal recommended from the score pace ("50 min to be on pace for 700")**
  (experience goal gap): same reason. The workload-based suggestion (T17) replaces it.
* **Personal-best lines ("Best week for fixing: 14, was 11")** (outcomes #11): novelty. Me's
  week history names the best week (U14).
* **Solid days inside the streak ("12-day streak · 9 solid")** (outcomes streak gap): a second
  meaning for one streak. "Goal met 9 of the last 14 days" says the same plainly.
* **A per-tier model of points from simulated blueprint fills** (unfair-advantage #1): a second
  score model beside U4's. U4 plus the tier accuracies on each row covers it.
* **Splitting each skill's gain into "open mistakes" and "general misses"** (experience #3):
  there is no defensible way to split it.
* **The adaptive tier and next step on each topic chip** (unfair-advantage chips gap): R33's
  step lives inside a session, so no state exists before Start.
* **Letter shortcuts for every card (N, C, P, E, D)** (experience #9): bare `N` clashes with
  Words, the players and the runner (`shell-me.md` rejected it). `J` / `K`, `G N` and the palette
  cover it.
* **Collapsing every other card on exam day** (outcomes #9, experience #6): decision 4. The
  cards are reordered instead.
* **Dragging a test mark in the week strip, and Swap with tomorrow** (unfair-advantage Skip
  gap): `Move to…` does both and works from the keyboard.
* **Words reviews folded into the same session as the Math questions** (outcomes Words gap):
  they run in different runners. The words row is chained after the session instead (T2).
* **A hero headline sentence with its own Start** (outcomes hero gap): it duplicates Up next,
  which sits directly under it.
* **A questions-a-day or mistakes-a-day goal unit** (experience and unfair-advantage goal gaps):
  U14's week goals hold outcome goals. The chips show the question equivalent.
* **Hints cut from the rationale's first clause** (outcomes #7): the cut would often be
  nonsense or give the answer away. The worked example itself is the hint (T4).
* **Sparklines on the plan stat tiles** (experience plan gap): four more charts for a trend the
  week strip already shows.
* **A `learners.seen_at` column written on every GET** (outcomes #11): the last study day from
  `progress.days` gives the same briefing with no write.
* **A goal level set from the target for the points map** (outcomes #1): U4's fixed 80%
  reference keeps one number across Today and Me. The target's need is in the card's header
  line and in the dialog.
* **A new `from_day` drill field** (experience #8): `pool:'history'` with the day's attempt ids
  does it.
* **A 2 h 20 m dress-rehearsal event** (outcomes #9): that is the full SAT. Our section is 70
  minutes, so the event is 90 minutes with the break.
