# v2 upgrades: Study plan

Written 2026-09-23 for `spec/rebuild-v2.md` §3.6 (lines 7046–8096). It merges three designers'
proposals (outcomes, experience, unfair advantage) into one build-ready list, L1–L20, against
the TopTierPrep inventory in §3.6.1, `spec/toptierprep-teardown.md`, `ttp-notes.md` and the live
walk in `ttp-live.md` (their plan view recovered from the bundle; their generator failed 3 of 3).

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.6 where
  they differ: §3 lists every place that changes. Part 2 resolutions (R1–R38) still hold,
  except the lines named in §3.2 "Outside the section".
* **Siblings, reused and never re-specified.** `shell-me.md`: Up next and the time box (U1,
  `server/next.py`), Bluebook and ID import (U2), points on the table (U4, `estimate.gains`,
  `estimate.need`), rough skills and the 12-question Sharpen probe (U5), habits and the trap
  gauntlet (U6, `server/habits.py`), pace (U7, `progress.pace`), the projection (U9,
  `estimate.projection`), levers (U13), the Monday week sheet and goals (U14), stages (U15),
  spare days (U16), registration deadlines (U17), reminders (U18), paint from cache (U23),
  Undo (U25). `today.md`: the time-box preview (T1), Due today (T2), the warm-up (T3), Learn it
  (T4), twins (T5), causes (T7, `progress.causes`), pace card (T8), the score verdict (T10),
  what it takes (T11), capacity (T12, `today.workload`), final stretch (T13), the receipt
  (T19). `practice.md`: the learn ladder (P2), Sure · Unsure · Guess (P7), why you missed (P8),
  the route check (P10, `estimate.route`), zones (P11), type reviews (P12), budgets and two
  passes (P16), rematch (P18). The plan decides **when** each of these happens and **how much
  of the day** it gets; the siblings own **what** it is.
* **The bar.** A student using TopTierPrep's plan today opens ours and wants to switch: it
  exists in one tap, it spends each minute where the points are, it proves each week what the
  work fixed, and it changes itself in view. Parity is failure.
* **Names.** Upgrades are L1–L20 (L for the Plan key, `G L`). Builders are Part 4's tasks. S7
  owns `web/plan/**`, `server/plan.py`, `server/api_plan.py`, `web/assets/plan-ui.js`,
  `server/checks/s7.py`; every other file is met through §2.9.
* **Subject-aware** (decision 3). Every task carries `subject` (`math` now; `rw` for Words and
  R&W own tasks). Points, coverage and causes payloads carry `subject`. `cfg` keeps Math fields
  at top level and an empty `sections: ['math']`, so an R&W allocator is additive.
* **Facts this file relies on** (code as of 2026-09-23):
  * `blueprint.DOMAIN_SPLIT`: module 1 is 8 / 7 / 4 / 3 and module 2 is 7 / 8 / 3 / 4
    (Algebra / Advanced Math / PSDA / Geometry), 15 / 15 / 7 / 7 of 44. `TIERS`: module 1
    7 / 8 / 7, lower module 2 11 / 8 / 3, upper 3 / 8 / 11. `MODULE_SECONDS` 2,100.
  * `scoring.ROUTE_UP_AT` 0.60 (14 of 22), `LOWER_ROUTE_CEILING` 580, `ANCHORS` top out at
    780, `MOCK_HALF_BAND` 70, `HALF_BAND` 100. `progress.STRONG` 0.8.
  * Topics per domain: Algebra 5, Advanced Math 3, PSDA 7, Geometry 4 (19). 386 templates.
  * `POST /api/mock/new {kind:'twin', twin_of}` exists in §3.4: module 1 keeps every slot's
    template and difficulty on new seeds.
  * P16's tier budgets: easy 65 s, medium 95 s, hard 126 s (2,097 s on module 1's mix).

---

## 1. Scorecard

"v2 spec" is §3.6 as written. The verdict says why ours is way better; where v2 was only at
parity (or below), it names the upgrade that fixes it.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Landing hero and CTA | Blue hero, "Your path to the score you want", Create my plan, "Takes about a minute · 1 plan left this cycle" | Wash hero, Create my plan, "free · as many plans as you like", HeroPreview (Math now, Next SAT, Open mistakes), draft banner | With data: **Your plan, ready**: the proposal's line, a compact month, day 1's real tasks, `Use this plan` in one tap, `Adjust…` (L6). New student: the example day's first question answerable in place, and "let the plan measure it" (L6, L7) | v2 PARITY: a better hero in front of the same four screens. **L6 → WAY BETTER.** A working plan and a startable first task in one tap; theirs is four screens and a fake build that failed 3 of 3. |
| 2 | Landing stat cards | 10 tests · 6,933 questions · 1,002 words | ∞ sections · 386 types / 19 skills · one real named mistake | Adds a **Your numbers** row above: ≈ points on the table with the top 3 skills, the route check, open mistakes by name (L1) | v2 better (a real mistake) but still about the bank. **L1 → WAY BETTER.** The first numbers are about the student's score. |
| 3 | How it works | 3 numbered cards | 3 tiles that describe real behaviour | The example day's first row is a live question (L6) | v2 PARITY in form. **L6 → WAY BETTER.** A new student meets a named mistake before committing. |
| 4 | Plans list on the landing | List; empty state | Same component as the Plans tab | Each finished plan shows what it achieved and what worked (L20) | v2 PARITY. **L20 → WAY BETTER.** |
| 5 | Plan quota | 1 per billing cycle; failed plans hidden | Free, unlimited | Same | **WAY BETTER already.** |
| 6 | Dashboard plan CTA (no plan) | "Build Your Adaptive DSAT Study Plan", 3 bullets, Build My Plan | Today's `Build with these` (T18) | `Build with these` and the landing read one `plan.propose` (L6) | **WAY BETTER** (T18 + L6): one rule, one tap, both places. |
| 7 | Wizard header, Exit setup | Title, "draft saves as you go", Exit setup pill | Same, Exit keeps the draft | `⌘/Ctrl Enter` creates from any step once a date is set; later steps take defaults (L6) | v2 PARITY. **L6 → WAY BETTER.** |
| 8 | Stepper | Four cards, no forward jump | Forward once valid, red dot for a server error | A live plan beside every step (L6) | **WAY BETTER.** The student watches the plan change instead of reading a summary. |
| 9 | Draft autosave | Resets on a failed build | Server draft + local fallback, never reset | Same | **WAY BETTER already.** |
| 10 | Step 1: where you are | Two sliders, "best estimate", prefilled when tests exist | Math slider + number, SourceNote, optional R&W, a link out to the diagnostic | The last 3 sittings drawn as bands with their mean; a new student picks **Let the plan measure it**: the diagnostic is day 1's first task and week 1 a Map week (L7, L2) | v2 PARITY for a new student (a guess, or a trip out). **L7 + L2 → WAY BETTER.** The plan starts on evidence and nobody leaves the wizard. |
| 11 | Step 2: target, NOW → TARGET | Target sliders, +400 card, range bar, screen-reader line | GainCard, TargetNote (88% of points, 14 of 22, the 780 cap) | "700 ≈ 37 of 44 right · you're near 31 · the 6 you're most likely missing are in …", and the route check from the student's own first tries (L1, L7) | v2 better (honest); **L1 → WAY BETTER.** The target becomes a count of questions, named skills and a route. |
| 12 | Step 2: exam date and pace | Free calendar; "about 60 points per week", never judged | Official-date chips with pace, PaceTag, later-date suggestion | `UI.examDate` rows: study days, pace and tag, register-by, projected score, Recommended; "you make +9 a week; this date needs +22" (L7) | **WAY BETTER.** A date chosen against the student's own rate and deadlines. |
| 13 | Step 3: daily time | 30m–4h chips | 15m–4h, 2.5h added, per-day minutes | The student's real rhythm beside the chips, an overreach warning, and **Ramp** (L7) | v2 PARITY: a number the student guesses. **L7 → WAY BETTER.** The plan starts at what the student really does and grows. |
| 14 | Step 3: days a week, STUDY/REST tiles | Slider, tiles, study/rest counts | Same, plus a minutes select per tile and days off | Each tile shows "studied 3 of last 4 · ~35m" (L7) | **WAY BETTER.** |
| 15 | "Solve a practice exam every day" | Toggle, locked below 150 min | None / Weekly / Twice / Every study day; module or section; test day | Checkpoints: every second test is a twin of the baseline (L14); a warning when tests take over 30% of the time (L7) | v2 PARITY: a frequency. **L14 → WAY BETTER.** Two tests in the plan are finally comparable, slot by slot. |
| 16 | Step 4: focus areas | 8 domains, Focus / Normal / Strong, 4 cap, tints | 4 domains + 19 skills, caps 2 / 6, suggestions, live SplitBar | **Where your points are** panel, ≈ points on every row, suggestions by points per minute, a points bar under the split, coverage per domain, Auto focus (L1, L2, L3) | v2 PARITY in kind: chosen once, ranked by weakness. **L1 + L3 → WAY BETTER.** |
| 17 | Include vocabulary practice | Toggle; Vocabulary and Flashcards tasks | Extras (rechecks, QOTD, challenge) called the equivalent; no words task in the Task model | A Words row in step 4 (SAT words + transitions, decision 2) and a counted **Words** task inside the day's minutes, counted as R&W time (L4) | v2 BELOW. **L4 → WAY BETTER.** Spaced EBRW words sized to the real due queue. |
| 18 | Plan at a glance | A text summary that rounds up | GlancePanel rows from preview | Plus the **live plan**: compact month, week 1, day 1's rows (L6) | **WAY BETTER.** |
| 19 | Build screen, error card | Fake one-minute progress; FAILED in 0.3 s; draft reset | Synchronous create, no build screen | Create lands with keyboard focus on **Start today** (L6, L8) | **WAY BETTER already.** |
| 20 | Plan adaptation (`regenerate`, `adapt`; weakAreas fixed at build) | AI regeneration behind a paid quota; focus never moves by itself | Daily re-deal, drift, behind | Focus moves on when a skill passes a before/after check (L3); a changelog says what changed this morning and why (L15) | v2 PARITY in what the student sees. **L3 + L15 → WAY BETTER.** Adaptivity the student can check. |
| 21 | Page tabs | Plan · Progress · History | Plan · Progress · Plans | Plus the changelog strip under the tabs (L15) | **WAY BETTER.** |
| 22 | Four stat tiles | Days to exam, Streak, Plan complete %, Score gap "1000 now, 1400 target" | Days, Score with status chip, Plan done, This week with streak | Days adds capacity against need; Score adds the projection, made vs needed a week, the route and ≈ points claimed; Plan done reads against the schedule; Week carries goals; each tile opens its detail (L13, L16) | v2 PARITY. **L13 → WAY BETTER.** Four tiles that say whether the plan is working. |
| 23 | Today card on the plan page | "N of M done · X min left · Y min planned", empty states | DayPanel progress line and footer states | **Start today** runs the day in one go and ends in a receipt; **Today I have** trims the day by value (L8, L9) | v2 PARITY. **L8 + L9 → WAY BETTER.** 1 tap plus Enter between blocks, against their ~12 taps. |
| 24 | Task types | Practice test, Question set, Vocabulary, Reading, Practice game, Flashcards, Custom | Fix, Rechecks, Focus, Test, Your own, Extra | Warm-up, Fix, Learn it, Before/After check, Habit, Pace, Focus, Map, Test / Checkpoint / Rehearsal, Sweep, Words, Homework, Your own, Extras (L4) | v2 PARITY: a set, a test, your own. **L4 → WAY BETTER.** Each kind is a different teaching move with a reason. |
| 25 | "Why this task?" | AI `aiReason`, "Hide AI rationale" | Fact lines the scheduler used | Value first (≈ +15), and every line links to its evidence (L10) | v2 better (facts). **L10 → WAY BETTER.** Checkable in one tap. |
| 26 | Task actions | Skip, Mark done, launch, ✓ Done, Practice again, Undo | Skip/Undo, Mark done, Move, Swap, Make it a section, Again · new questions | Skip asks why and acts on it; Mark done logs minutes done elsewhere; Again · the ones you missed; every done row reports what it fixed (L10) | v2 PARITY in kind. **L10 → WAY BETTER.** |
| 27 | Custom tasks | CUSTOM with Mark done | Own tasks with repeat rules | Typed own tasks: a Bluebook test asks for the scores and misses, which feed the trajectory and tomorrow's Fix (L11) | v2 PARITY. **L11 → WAY BETTER.** A ticked official test teaches the plan something. |
| 28 | Week view | Week N, X of Y · %, AI theme, pager, day tiles | Same, plus server theme, kinds, minutes, bars | Week goals in the header with a live result, Review week, and next week shaped in one sheet (L16) | v2 PARITY. **L16 → WAY BETTER.** |
| 29 | Selected day, empty day | Header; "Nothing scheduled" | DayPanel for any past or future day | Plus each day is a drop target showing its new load (L12) | **WAY BETTER.** |
| 30 | Rescheduling | Move to a later day of the same week only | Any study day to the eve, swap, day off, change a day | One drag or two keys, with the target day's new load shown before the drop (L12) | **WAY BETTER already**; L12 makes it fast. |
| 31 | Behind banner | ≥ 4 tasks and < 60% done in 7 days; Rebalance my plan | Real average minutes, Fit to 25 min with a preview | What it cost, **Catch up · 15 min**, the weekday pattern, Ramp and a later date, each previewed in hours and pace (L17) | v2 PARITY: one fix. **L17 → WAY BETTER.** |
| 32 | Score drift banner | Upward only, ≥ 60, snoozed 3 h | mean3 ± 40 both ways, target reached, remembered on the server | Evidence chips, what moved, the effect before applying, optional auto-apply (L17) | v2 PARITY. **L17 → WAY BETTER.** |
| 33 | Progress: accuracy by domain | Bars, weakest first | DomainCard, 19-skill table | By points by default, points claimed since the start, the 19 × 3 coverage map, what the time bought (L1, L2, L18) | v2 PARITY. **L18 → WAY BETTER.** It ranks by value and shows what is paying. |
| 34 | Progress: study time per day | Studied vs planned | Bars, tests hatched, range, tooltip | First-try accuracy line; a bar opens its day (L18) | v2 PARITY. **L18 → WAY BETTER.** |
| 35 | Progress: how the plan splits time | Planned minutes by task type | Planned and done by task type | Plus by domain against where the points are (L18) | v2 PARITY. **L18 → WAY BETTER.** A misallocation shows at a glance. |
| 36 | History tab | List, make active, older-plan banner | Plans tab, plus duplicate and remove | A record of what worked, a timeline of changes, and the next plan seeded from it (L20) | v2 PARITY. **L20 → WAY BETTER.** |
| 37 | Toasts | Generic | With Undo where one exists | Every automatic change also toasts with Undo (L3, L15) | **WAY BETTER already.** |
| 38 | Dashboard card with a plan | Today's Plan, N of M, min left, Full Plan, checkboxes | Today's plan card (T2, T18) | Start today and Today I have there too (L8, L9) | **WAY BETTER** (T2, T18, L8). |
| 39 | Profile study goals | Target unsynced, countdown, Daily 2 h / Weekly 12 h, preferred time unused | One value across Me, Today and Plan; preferred time → calendar | A **Where** beside the time (an implementation intention) in every event; registration deadlines (L7, L17, U17) | **WAY BETTER.** |
| 40 | Dashboard countdown, study-time calendar | DD:HH:MM:SS ticker; calendar marked in UTC | Local-time month grid; Today's capacity line (T12) | The Days tile states capacity against the work left (L13) | **WAY BETTER.** |
| 41 | Classes and homework | Hidden `/my-classes`, a second to-do list | Today lists assignments; the plan ignores them | Homework lands in the plan as a counted task before its due date (L4) | v2 PARITY (two lists). **L4 → WAY BETTER.** One list, honest minutes. |
| 42 | The last weeks | Nothing changes; "Exam day has arrived" | Final phase: full sections and open mistakes; the eve and a checklist | Dress rehearsals at the real hour, the sweep with a still-fixed scoreboard, a taper, and a personal trap sheet for the eve (L19) | v2 PARITY in effect. **L19 → WAY BETTER.** |

---

## 2. Accepted upgrades

Each gives why, screens and components, controls and states, data and endpoints, how it uses
the rest of the site, and acceptance checks. Learner codes start `a:v2revplan`; `:8027` is
S7's port. Every figure that comes from a model says "about" or "≈".

### Layout after these upgrades

**Plan tab, desktop (≥1080px)**, under the title row and the 4 stat tiles:
```
banners ×12
tabs ×12 (sticky)  ·  changelog strip under them (L15)
day ×7.5  (DayPanel: head with Start today and Today I have, progress, rows, footer)
          | side ×4.5 (ComingUp · Map progress (Map days) · Your habits · Sweep (Final))
week ×7.5 (WeekStrip with goals)
phase ×12
month ×12
```
**Phone (<760px)**: title, tiles (Days full width, then a 3-up row), banners, tabs, changelog
strip, DayPanel, WeekStrip, ComingUp, Map, habits, sweep, phase, month. A **thumb bar** sits
above the tab bar on `/plan/`: `Next · Fix mistakes · 8 q · Start` (L8). Nothing is folded away
(decision 4).

**Progress tab**, desktop 2 columns:
```
checkpoint ×12 (when one exists)
progress ×6   | trajectory ×6
bought ×12    (What your time bought)
causes ×6     | coverage ×6
domains ×6    | split ×6
studytime ×12
checks ×6     | weeks ×6
pace ×6       | gaps ×6
changes ×12
```
Phone: the same order, one column.

**Calls.** `GET /api/plan` stays the one call for the Plan tab. A new `GET /api/plan/progress`
feeds the Progress-only cards (L18); it loads when the tab opens (or on idle after the Plan tab
paints), has its own error and Retry, and one read of the learner's attempts feeds all its pure
functions. `ponytail:` recomputed per call; memo per (learner, last attempt id) if profiles
show it.

---

### A. Where the time goes

#### L1. Points decide the week, and the route check

*From: outcomes #1, experience #3, unfair-advantage #1, the step-4, SplitBar, Why and DomainCard
gaps of all three. Effort M. Builders: S7 (allocator, step 4, cards), F4 (`estimate.gains`,
`estimate.route` exist in U4 / P10; `plans.start_points`).*

**Why.** A skill that is 6 questions a section at 58% is worth far more than one that is half
a question at 30%. §4's `(1.5 − m)` weight ranks weakness, not value, and theirs ranks 8
self-marked domains. Spending each slot where the most points are per minute is the fastest
route to a higher scaled score, and above 580 nothing matters more than reaching the harder
module 2.

**The model is U4's.** `estimate.gains(learner, subject)` per skill: `{gain, per_test,
accuracy, to_strong, minutes}`, null under 30 answers. The plan never recomputes it
(`shell-me.md` and `practice.md` rejected a second model).

**Allocation** (replaces §4 "Domain shares"; the slot walk, caps and fallback are unchanged):
* Value per minute: `v_t = max(gain_t, 2) / max(minutes_t, 5)`. The floor of 2 keeps every
  skill in the deal.
* Weight: `w_t = v_t × {focus 2, normal 1, strong 0.4}[state]`, where state is the skill's own
  state, else its domain's.
* A domain's share is `Σ w_t` over its topics, normalised. The topic weight inside the domain is
  `w_t` (replacing "the coach score × {2, 1, 0.4}").
* `gains == null` (under 30 answers): §4's formula, unchanged. So v2 acceptance 3 still holds
  for a new learner.

**The route check** (P10's `estimate.route`: `{m1, route, margin}`, first-module accuracy from
the learner's per-tier first tries).
* **Gate mode** is on when `target > 580` and `m1 < 0.60`, and off once `m1 ≥ 0.65`. In between
  it keeps the last frozen day's value (`plan_days.gate`), so it doesn't flicker.
* While on, in Build and Sharpen:
  * focus sets use `tiers: ['easy', 'medium']`;
  * Fix takes easy and medium traps first;
  * the week theme leads with `Route: about 54% of a first module → 60% (14 of 22) opens the
    harder module 2`;
  * the focus Why adds `Below the route: Math tops out at 580 until module 1 reaches 14 of 22`.
* Final is unchanged: the rehearsals need every tier.

**Screens.**
* **Step 4 › Where your points are** (a panel above the DomainRows): the top 6 skills by
  `v_t`, each a `UI.skillRow` (U4's row):
  * `Nonlinear functions · ≈ +20 · about 6 of 44 · 58% right · 3 open mistakes · at least 6
    right · ~9 min`;
  * a `↑ Focus` toggle per row, which writes that skill's state.
  * Header: `About +60 on the table · your top 3 together ≈ +34`, plus the route line when
    `target > 580`: `First modules about 54% · 14 of 22 routes up`.
  * Under 30 answers: `Answer 30 questions and this shows where your points are · 12 of 30`.
* **DomainRow** adds `≈ +40 on the table`; **SkillRow** adds `≈ +15`, or `Not measured yet`
  under 5 answers.
* **Suggestion rule** (replaces §2e's):
  * Focus the top 3 skills by `v_t` whose gain is +10 or more.
  * Focus a domain whose summed gain is 40% or more of the total.
  * Strong on skills with gain under 5 and mastery ≥ 0.8.
  * Under 30 answers, §2e's rule.
* **SplitBar** gets a second bar under `Your practice week`: `Where your points are`, the share
  of the total gain by domain, with labels such as `Advanced Math · 38% of time · 45% of
  points`.
* **Why lines lead with value**: `Nonlinear functions ≈ +20 on the table · about 6 of 44 a
  section · 58% right`. Task meta adds `≈ +20` after the minutes. There is no task-level
  "worth": the figure is always the skill's.
* **Landing › Your numbers** (a row above BankStats, with 30+ answers): `≈ +60 on the table ·
  Nonlinear functions, Circles, Percentages`, the route line, and the open-mistake count with
  the top label.
* **Claimed**: `plans.start_points` stores `{total, skills: {topic: gain}}` at create (or on the
  first day gains exists). The Score tile and DomainCard show `≈ +18 claimed since Sep 23` =
  start total − now (signed).

**Data.** `GET /api/plan` adds `points: {subject, total, top3, claimed, skills: [{topic, gain,
per_test, accuracy, to_strong, minutes, v, claimed}], route: {m1, route, margin, gate}} | null`.
`POST /api/plan/preview` adds `points` and `split_points: {domain: share}`.

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

#### L2. Coverage: every skill and every tier the target needs, planned and proven

*From: experience #10, outcomes #8 (Map week), unfair-advantage #5 (reworked), the
unfair-advantage difficulty gap. Effort M. Builders: S7 (allocator guarantees, Map mode, card),
F5 (`tiers_by_topic`), U5's probe (exists).*

**Why.** A plan that never deals hard Circles leaves the student meeting it cold on test day.
Theirs cannot even see skill × difficulty (their report has neither). And a plan built on a
guessed score spends its first weeks on the wrong skills: the diagnostic is ±100, and a
handful of answers per skill is noise.

**The grid.** 19 skills × 3 tiers. A cell is:
* **proven**: at least 3 of the last 4 clean first tries (R8) at that tier right;
* **shaky**: answered, not proven;
* **untested**: none;
* **n/a**: the skill has no template at that tier (`blueprint.kinds()`).
* **Needed** tiers: easy and medium always; hard when `target > 580` (the upper module holds 11
  hard questions).

**Allocator guarantees** (plan.py, each with an assert in `__main__`):
1. Every skill gets at least one focus slot in every 14 days, unless it is Strong and proven on
   every needed tier (the warm-up keeps those).
2. Every needed untested or shaky cell is pinned at least twice before Final starts. A pinned
   slot sends that skill's questions at that tier through the new drill field
   `tiers_by_topic: {topic: [tier]}`.
3. In Build, an untested needed cell takes priority over a shaky one for its skill's slot.

**Map mode** (new students).
* Trigger: at create, or at any re-deal in the plan's first 14 days, more than 5 skills have
  fewer than 6 clean first tries.
* Up to the first 5 practice days are Map days. Their focus task is kind `map`:
  `{source:'probe', count, task:'<d>:map'}` (U5's probe: rough skills first, adaptive, mixed,
  repairs at the end, so the answers measure).
* Row: `Map · 20 questions · 6 skills you haven't shown yet`.
* A side tile: `Map · 11 of 19 skills measured`, with a 19-cell strip (measured: ink with ✓;
  rough: dashed).
* **Map done** (5 or fewer skills rough) shows one card at the top of the Plan tab:
  `Map done · 17 of 19 measured · strongest Linear equations in one variable 86% · most points:
  Nonlinear functions ≈ +20 · first modules about 54%`, with `Use the suggested focus`
  (a PATCH of focus and skills, with Undo) and `Keep mine`.

**Progress › "Ready on every skill?"** (the coverage card).
* Header: `Proven 31 of 57 · shaky 14 · untested 12 · 0 needed and unplanned`.
* 19 rows under 4 domain headers, 3 cells each, with glyph and text for the state (never colour
  alone), a `needed` tick, and the next planned date in mono (`Oct 14`) or `—`.
* A cell opens a 5-question drill: `Try hard Circles now` → `{topics:['circles'], tiers:['hard'],
  count:5, source:'plan'}`.
* `role=grid`, arrow keys, a hidden table.
* Step 4's DomainRow shows its line: `Algebra · 9 of 15 proven`.

**Data.** `GET /api/plan/progress.coverage = {subject, cells: [{topic, tier, state, right, n,
needed, next}], counts}`, computed from attempts. `GET /api/plan.map = {on, measured,
of: 19, done_at} | null`.

**Acceptance.**
1. `python3 -m server.plan` asserts guarantees 1 and 2 on a synthetic 60-day plan over all 19
   topics.
2. A learner with circles hard first tries ✓✓✗✓ (newest last) has that cell `proven`; ✓✗✗✓ is
   `shaky`.
3. `POST /api/drill {topics:['circles','ratios'], tiers_by_topic:{circles:['hard']}, count:6}`
   serves only hard circles items and any-tier ratios items (a check in `server/checks/f5.py`).
4. A new learner with 3 answers: the plan's first practice days' focus tasks are kind `map`
   with `body.source == 'probe'`, and the Plan tab shows `Map · ` with a count.
5. At 390, the coverage card has no horizontal page scroll (`scrollWidth <= 390`).

#### L3. Focus that moves on: a before and an after on the same question types

*From: outcomes #3, experience #9, the outcomes skill-drift and step-4 gaps, unfair-advantage #10
(the demotion rule). Effort M. Builders: S7 (checks, rules, banners), P18's rematch (F5, exists),
S4 (the check's summary line).*

**Why.** Theirs keeps the focus chosen in the wizard until it goes stale. A week of work on
Circles should end with proof that it worked, and the time should move to the next skill the
moment it does. A fixed bank cannot re-ask the same four question types with new numbers; our
(template, seed) addressing makes an exact before/after trivial.

**The checks** (kind `check`, counted, ~6 min each; at most 2 skills a week: the focus skills
with the largest gain and no passed check):
* **Before**: on the first practice day of the week that deals the skill, a task before its
  focus set: `Before · Circles · 4 questions · ~6 min`, detail `The same 4 question types come
  back Fri with new numbers`. Body: `{topics:['circles'], count:4, order:'mixed', feedback:'end',
  repairs:'end', task:'<d>:check:circles'}`. The drill picks 4 distinct templates at the zone's
  tier (P11).
* **After**: on the week's last practice day, or once 30 focus answers on the skill have come
  since the before: `After · Circles · the same 4 types, new numbers · timed`. Body:
  `{rematch: <before sid>, timing:'pace', task:'<d>:check:circles'}` (P18: same templates, tiers
  and formats in order, fresh seeds, then → now per slot).
* **Result row** (the done After row, the week review, the Progress Checks table):
  `Circles · before 1/4 → after 4/4 on the same question types · 6:10 → 4:05`.

**Rules.**
* **Passed**: after ≥ 3/4 and total time ≤ the before's, or 11 of the last 12 clean first tries
  at medium or hard right with no open trap. The skill leaves Focus for Strong (`by: 'auto'`),
  joins the warm-up's keep-warm, and the next skill by `v_t` (L1), not on Focus and not Strong,
  takes its place (`by: 'auto'`), within the caps.
* **Again**: 2/4 keeps it on Focus and adds a Learn it task (L4) on the next practice day.
* **Learn first**: 1/4 or less keeps it, with Learn it before the next focus set.
* **Slipping**: a Strong skill (set by the student or by auto) at 7 or fewer of its last 12
  clean first tries, or with a missed keep-warm item, goes to Normal for 7 days. Why line:
  `Circles is slipping · 7 of 12 · back to Normal until Oct 9`.

**Auto or ask** (pref `plan_auto_focus`, default on; step 4 switch "Move a skill off Focus when
it passes its check"):
* **On**: applied at the re-deal, with the toast `Circles passed · 1/4 → 4/4 · next week's
  focus: Percentages (≈ +20) · Undo` and a changelog line (L15). Undo reverts and pins the skill
  (`pin: true`), and auto leaves pinned skills alone.
* **Off**: a banner (L17): `Circles passed its check · 4/4 · Move it to Strong and put
  Percentages (≈ +20) on Focus?` with `Move` and `Keep on Focus`.

**Data.**
* `cfg.skills` entries become `{state, by: 'you'|'auto', since, pin?}`. A bare string state is
  still accepted (`by: 'you'`).
* `GET /api/plan.checks = [{topic, week, before:{sid, right, of, ms}, after:{sid, right, of,
  ms}|null, result: 'passed'|'again'|'learn'|null}]` and `focus_history: [{topic, state, from,
  to, why}]`. Both are found from sessions tagged `:check:<topic>` and `cfg.rematch_of`, so
  there is no new table.

**Acceptance.**
1. A plan with circles on Focus: the first practice day of the week that deals circles has a
   `check` task ordered before the focus task, with `body.count == 4` and `topics ==
   ['circles']`.
2. That week's last practice day has a `check` whose `body.rematch` is the before session's id.
3. The after scores 4/4 in less total ms: `GET /api/plan` shows circles `{state:'strong',
   by:'auto'}`, a new Focus skill with `by:'auto'`, and a `changes.today` line containing
   "passed". `PATCH` with the old skills restores it and sets `pin: true`.
4. With `prefs.plan_auto_focus == false`, nothing changes and `banners` has kind `graduated`.
5. A Strong skill with 7 of its last 12 right reads `normal` with a `since` 7 days ahead, and
   its next focus Why contains "slipping".

#### L4. The day, rebuilt: warm-up first, then the teaching move each skill needs

*From: outcomes #2, #5, #6, #9, unfair-advantage #4, #10, #11, experience #13, unfair-advantage
#12, the Words gaps of all three. Effort M. Builders: S7 (kinds, budget, order), S9 (Words
task), S2 (`classes.due_soon` with due dates), T3 / T4 / T8 / U6 bodies (exist).*

**Why.** Theirs has one move, "a question set". A student who fails ten cold questions on a
new skill needed a worked example; one who knows it slowly needs the clock; one habit across
skills needs one drill, not eleven. And a plan that ignores homework and vocabulary is lying
about the minutes in the day.

**Order and bodies for a practice day** (replaces §4 "Tasks for a practice budget"):

| # | kind | when | row (example) | body |
|---|---|---|---|---|
| 1 | `test` | a test day (checkpoint L14, rehearsal L19) | `Module test · 22 q · 35 min` | §4 / L14 / L19 |
| 2 | `recheck`, shown as **Warm-up** | anything due in `progress.warmup_candidates` (T3) | `Warm-up · 5 questions · ~6 min · 3 check-ins due · 2 fading` | `{source:'warmup', count:5, task:'<d>:recheck'}` (8 in Final) |
| 3 | `fix` | open traps | `Fix mistakes · 8 q · "used the diameter as the radius" +5` | v2's count rule; ids ordered: confident misses first (P7 `conf='sure'`, T9 blind spots), then U4 gain × hits; Gate mode puts easy and medium first |
| 4 | `learn` | a Focus skill with fewer than 5 answers or mastery under 0.35 (Build); an After at 2/4 or less (L3); a skip "Too hard" (L10); 2+ `stuck` misses (P8) in 14 days; T7's `top_gap_topic` | `Learn it · Circles · a worked example + 3 · ~6 min` | T4: `{source:'learn', topics:[t], example:true, count:3, task:'<d>:learn'}` |
| 5 | `check` | L3 | `Before · Circles · 4 questions` | L3 |
| 6 | `habit` | once a week (the second practice day), when one habit is 25%+ of the last 20 misses (U1 row 6) | `Habit · answered a different quantity · 8 across 5 skills` | U6: `{source:'habit', habit, count:8, task:'<d>:habit'}` |
| 7 | `pace` | a Focus skill in U7's slow-and-right quadrant, from Sharpen on (or any phase when its median is over 1.3× its budget), at most 2 a week; or fast-and-wrong ("rushing") | `Speed drill · Systems · 8 in 12:40` or `Careful set · Percentages · 8` | T8: `{topics:[t], count:8, timing:'pace', source:'pace', task:'<d>:pace:<t>'}`; careful: `timing:'off'` |
| 8 | `map` / `focus` | the rest of the budget, at least 5 (Map days: L2) | `Focus set · Circles, Percentages · 18 q · 28 min` | §4 plus L1 / L2 / L5 fields |
| 9 | `sweep` | Final (L19) | `Sweep · 9 of 44 old mistakes · new numbers` | L19 |
| 10 | `words` | `prefs.words_goal > 0` | `Words · 12 due · 5 new · ~6 min` | S9's run: `Review cards`, `Learn 5`, `Quiz` |
| 11 | `assigned` | a class assignment with a due date, not done | `Homework · Period 3 · Circles · 15 q · due Fri` | `{assignment}` (`classes.resolve_drill`) |
| 12 | `custom`, then extras `qotd`, `challenge` | as v2 | as v2 | as v2 |

* **Budget.** The day's questions are `q = clamp(round((m − words_min) × 60 / s), 5, 120)`, where
  `s` is the learner's median seconds per question over 60 days, clamped to 60–150 (default 95;
  §3 override), and `words_min = words.minutes_today()` when Words is on (the Words spec's
  rule).
* Assigned questions come out of the focus count.
* Kinds 2–7 together take at most 60% of `q`. Past that, trim in reverse order: pace, habit,
  learn, then the fix count down to 4.
* **Minutes shown** on every row are count × `s`, the same rule as U1 and T2, so the plan and
  Today agree.
* **Cause routing** (T7's `progress.causes` over 14 days picks what gets scheduled):

  | cause | the plan adds |
  |---|---|
  | trap | Fix (and Habit when a family is 40%+ of the traps) |
  | slip | focus sets for that skill carry `feedback:'instant'`, and P8's "re-check the last step" line stays on |
  | clock | a Pace task |
  | entry | the day's focus set gets `spr_share: 0.5` (as v2's format tilt) |
  | gap | Learn it on `top_gap_topic` |

  Each is named in the task's Why (`3 of your last 10 misses were slips`).
* **Words** (decision 2: SAT words and transitions only). The row has S9's three launch
  buttons and completes itself from `words.today_summary().done`. It carries `subject:'rw'`,
  and its minutes count as R&W time in stats, the week theme and the split.
* **Homework** goes on the last study day before the due date that has room, else the due day.
  Its minutes count; Move is limited to the due date (targets after it are dimmed, with the
  reason "due Fri"); after the due date it reads `Late · due Fri` (a ring with `!`, not colour
  alone). Done follows the assignment's own completion. It appears once, in the plan group of
  Today's Due list (§3.2).
* **Side card "Your habits"** (Plan tab, under ComingUp): U6's top 3 with the tell and
  `Drill · 8`, plus `Next habit task Thu`.

**Data.** `Task.kind` gains `learn, check, habit, pace, map, sweep, words, assigned`; every
task gains `subject`. The drill `task` regex widens (§3.2). `GET /api/plan.habits` = U6's top 3.

**Acceptance.**
1. A learner with 2 check-ins due: today's tasks have one kind `recheck` titled "Warm-up" with
   `body.source == 'warmup'`, and no other task carries check-ins.
2. A learner with one trap opened on a `conf='sure'` answer and one ordinary trap: the fix
   body's `ids[0]` is the sure one.
3. A Focus skill with 3 answers in Build: a `learn` task that day with `body.example == true`.
4. `prefs.words_goal = 10` with 12 due: a `words` task whose `minutes == words.minutes_today()`,
   `subject == 'rw'`, and the focus count equals `q − (kinds 2–7)` with `q` from `m − words_min`.
5. An assignment of 15 questions due Friday: a task kind `assigned` on Thursday. `PATCH … {to:
   <Saturday>}` → 422 naming the due date.
6. `jq '[.today.tasks[].subject] | all'` is true.

#### L5. Difficulty and clock per skill

*From: unfair-advantage #5 (difficulty that climbs per skill), outcomes #7, the
unfair-advantage difficulty gap. Effort S. Builders: S7 (bodies), P11 zones and P16 budgets
(F4 / F5, exist).*

**Why.** §4's phase × target table is one tier list for every student and every skill, and
its "slow" rule is a flat 120 s. P11 already aims each question at the student's odds per skill,
and P16 gives every question type a fair budget; the plan should drive them, not override them.

**Focus-set difficulty** (replaces §4 "Difficulty"):
* **Build**: `zone:'stretch'` (P11, about 70% odds), within the needed tiers (L2), plus L2's
  pins.
* **Sharpen**: `zone:'stretch'`, with easy left out when `target > 580`.
* **Final**: Standard (no zone), `tiers` from v2's Final row, `adaptive:false`: test-like, as
  U15's Test-like bundle.
* **Gate mode** (L1) overrides Build and Sharpen with `tiers:['easy','medium']`.

**Clock** (replaces §4 "Clock" auto):
* **Auto**: `timing:'pace'` (the sum of P16's per-question budgets) in Sharpen and Final. In
  Build, a skill is timed when its median over its last 20 answers is above 1.3× its budget.
* Two passes (P16's pref) apply to every timed plan set.
* **Test tasks from Sharpen on** carry the pass plan in their detail: `Two passes: answer, or
  mark anything past 1:30 and come back`. Their report shows P16 / T16's time sinks.
* The ClockMode helper reads `Each question gets its own budget: easy 1:05 · medium 1:35 ·
  hard 2:06`.

**Acceptance.**
1. A Build focus body has `zone == 'stretch'`. A Final body has no `zone`, `adaptive == false`
   and `tiers` equal to v2's Final row for the target.
2. A Sharpen focus body has `timing == 'pace'`.
3. A Build skill whose median is 1.4× its budget: its focus body has `timing == 'pace'`, and its
   Why contains "budget".

---

### B. Getting a plan

#### L6. A plan in one tap, and a wizard that shows the real plan as you change it

*From: experience #2, unfair-advantage #6, the outcomes wizard gap, the experience build-moment
and landing gaps. Effort M. Builders: S7 (`plan.propose`, landing, wizard, banner), F1
(`UI.monthGrid` compact, `UI.pop`), S3 (T18 reads `propose`).*

**Why.** Theirs is landing → Create → four steps → a fake one-minute build, and it failed 3 of 3,
resetting the draft. A student who already has results should get a real plan in one tap and
tune it only if they want to. When they tune, they should watch the calendar and day 1 change,
not read a summary.

**`plan.propose(learner, tz)`** (one function; Today's `Build with these` reads it too, §3.2):
* `current`: `estimate.mean3` (R16) → the latest sitting's midpoint → null (the measure path,
  L7).
* `target`: the profile target → `min(round10(current + 100), 780)` → 600 with current null.
* `exam_date`: the profile date → the first `SAT_DATES` entry at least 28 days away, with
  `booked: false`.
* `days`: each weekday studied in at least 2 of the last 4 weeks (`progress.days`); if that
  gives fewer than 3, Mon–Fri.
* `minutes`: the profile minutes → the median minutes on study days over 28 days, snapped down
  to a chip, at least 15 → 45.
* `tests`: weekly module, auto test day, `checkpoints:'every2'`; `clock:'auto'`; focus from
  L1's suggestions; extras and Words at their defaults.
* It returns `{cfg, why: {field: 'tests'|'profile'|'rhythm'|'results'|'default'}}`.

**Landing, with data** (30+ answers or a sitting). The HeroPreview becomes **Your plan, ready**:
* the line `Nov 7 · 570 → 670 · 30 min × Mon, Wed, Thu · module Fri · Focus Nonlinear
  functions, Circles`;
* a compact month (`UI.monthGrid(host, {compact:true})`: 32 px cells, a phase band, test marks,
  the SAT);
* day 1's real task rows (read-only `UI.taskRow`).
* Pill **Use this plan** → `POST /api/plan` with the proposal, under 1 s. `.btn Adjust…` opens
  the wizard with the proposal as the draft.
* BankStats, HowItWorks and the example day stay below it (decision 4).

**Landing, new student.** v2's hero, and the example day's first row carries a live question
(`UI.workspace(host, q, {mode:'inline'})`, T1's inline mode: select, Check, the named mistake).

**After a one-tap create.**
* The Plan tab opens with keyboard focus on **Start today** (L8).
* The month grid's study days fill in phase order once (at most 400 ms, entry only, none under
  reduced motion).
* A **Built from your results** banner lists the assumptions as editable chips: `Start 570 ·
  from 2 tests ✎`, `Target 670 ✎`, `Nov 7 · not booked ✎`, `30 min × Mon, Wed, Thu ✎`,
  `Weekly module · Fri ✎`, `Focus Nonlinear functions, Circles ✎`.
  * Each chip opens a `UI.pop` holding the wizard's own control for that field, and saves with
    `PATCH` and Undo. No wizard.
  * The banner stays 3 days or until dismissed.

**Wizard.**
* The GlancePanel keeps its rows and adds a **Live plan** block on top, re-rendered from
  `POST /api/plan/preview`:
  * the compact month;
  * week 1's seven columns with minutes and topics;
  * day 1's task rows.
  * A cell that changed gets a single orange ring as it enters (600 ms; none under reduced
    motion).
  * At 390 it is the top of the Glance bottom sheet.
* **⌘/Ctrl Enter** creates from any step once step 2 is valid (later steps take the defaults);
  the footer shows the hint `⌘↵ create now`.

**Data.** `GET /api/plan` returns `proposal: {cfg, why, preview}` when there is no active plan.
`POST /api/plan/preview` adds `calendar: [{date, kind, minutes, phase, test}]` and `week` (T18's
7 days of `{date, kind, minutes, topics}`).

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

#### L7. Four steps that start from evidence

*From: the step 1–4 gaps of all three, outcomes #4 (where), the outcomes test-share gap,
experience #11 (reworked as the measure path). Effort M. Builders: S7, F1 (`UI.examDate`), F4
(`progress.days` rhythm), S9 (the Words row writes its prefs).*

**Why.** Theirs asks the student to guess three numbers they usually overestimate (their own
Behind banner exists because of it). Ours shows what the student has actually done and makes
the plan start there.

**Step 1.**
* **RangeBar** draws the last 3 sittings as grey dated bands with an ink tick at their mean, so
  `Use 650` is visibly the middle of real evidence.
* **New student** (no sitting), two choices:
  * **Let the plan measure it** (default): current is left empty (`cfg.current: null,
    measure: true`). Day 1's first task is the diagnostic (20 questions, about 30 min, in
    `/test/`), then Map days (L2).
  * **I'll estimate**: the slider.
  * When a measured plan's first scored sitting finishes, the plan sets `current` to its
    midpoint (rounded to 10), with the toast `Starting score set to 540 from your diagnostic ·
    Undo` and a changelog line.
  * Until then, the Glance and tiles read `Score ? → 600 · measured on day 1`, and the pace
    waits.

**Step 2.**
* **TargetNote** adds U4's need and P10's route:
  * `700 ≈ 37 of 44 right · you're near 31 · the 6 you're most likely missing are in Circles,
    Probability and Nonlinear functions`;
  * above 580: `Your first modules: about 54% · 14 of 22 routes up`.
  * v2's lines (88% of the points, the 780 cap) stay.
* **DateChips** become `UI.examDate` rows (T12's): `Nov 7 · Sat · in 45 days · 32 study days ·
  +11 a week · Steady · register by Oct 23 · ~690`. The projection appears when U9 has one; the
  first Steady date is tagged `Recommended`. They scroll horizontally only at 390 (as v2).
* **PaceLine** adds, when U9 has a slope: `You're making +9 a week; this date needs +22.` The
  PaceTag stays a labelled heuristic (open question 12).

**Step 3.**
* **Rhythm line** above the chips: `Last 4 weeks: 3 days a week · median 32 min · 1h 50m a
  week` with `.btn Use that`. With under 7 active days in 28 it reads `No study rhythm yet ·
  the plan will learn yours`.
* **Each WeekdayTile** shows `studied 3 of last 4 · ~35m` under its STUDY/REST label.
* **Overreach warning** when the chosen week is over 1.5× the last 4 weeks' average (with 7+
  active days): `You've averaged 1h 50m a week; this asks 3h 45m.` It comes with
  `.btn Ramp up to it` (below).
* **Ramp** (`cfg.ramp: {from}`, a chip value under `minutes`): day minutes = `min(minutes, from
  + 5 × plan week)`. Preview and Glance: `Ramp: 25 → 45 min by week 5`. Behind and Plan done use
  the ramped value.
* **Where** (`cfg.place`, ≤ 30 characters, optional) beside PreferredTime:
  `Where: [the library]`. It goes into each calendar event's LOCATION, the DayPanel head
  (`16:00 · the library`) and Today's plan line.
* **Tests share**: when tests take over 30% of the planned minutes: `Tests take 42% of your
  time. Tests measure; practice raises the score.` with `.btn Weekly instead`.
* **Checkpoints** seg under TestRhythm: `Every test · Every 2nd test · Off` (default Every 2nd;
  L14). Helper: `A checkpoint is a twin of your first test: the same question types with new
  numbers, so the two compare slot by slot.`

**Step 4.**
* L1's points panel and row figures, L2's coverage line per domain, L3's Auto focus switch.
* **Words row**: `Words · SAT words and transitions · [0 · 5 · 10 · 20] new a day · about 6 min
  a day`. It writes `prefs.words_goal` and `prefs.words_from ⊆ {sat, transitions}`, the same
  fields as Words and Me.
* **Extras**: `Rechecks` becomes `Warm-up`: *Questions you got right before, back just as you
  start to forget them, mixed and unlabelled* (T3).

**Data.** `GET /api/plan` (and the draft boot) adds `rhythm: {weeks: 4, days_per_week,
median_min, weekly_min, by_dow: [{studied, of, median_min}], active_days}`. `PlanIn` gains
`current: null` with `measure: true`, `ramp`, `place`, `checkpoints`.

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

---

### C. Doing the day

#### L8. Start today: the whole day in one run, ending in a receipt

*From: experience #1, the experience Today-card and build-moment gaps. Effort M. Builders: S7
(the pill, the thumb bar, `run`), S4 (the day rail and the in-place interstitial), S6 (Continue
today on the report), S3 (the Today card pill), F5 (`run` echoed in cfg).*

**Why.** Their tasks each launch a separate page, and their QBank session doesn't even end with
a summary. A 3-task day costs about 12 taps and back-navigation. Ours is 1 tap and Enter between
blocks, ending in one summary that names what was fixed and what comes tomorrow.

**Screens.**
* **The pill** `Start today · 3 tasks · 45 min` is the DayPanel head's primary, and it is also on
  Today's plan card (§3.2) and in the phone thumb bar (`Next · Fix mistakes · 8 q · Start`).
  Shift+Enter starts it on `/plan/`.
* It starts the first undone counted question task with `run: '<today>'`. On a test day that is
  the test, in the lobby.
* **Mid-run**, the pill reads `Resume today · block 2 of 3 · 6 of 20` everywhere.
* **The day rail** (S4, shown when `cfg.run` is set) is a thin strip under the session header:
  one segment per counted task of the day, filled by answered/total, labelled `Today 18 of 45
  min`.
* **The interstitial.** When a block finishes, the summary's head becomes two panes, with no
  page load:
  * left, the done block's result (L10's receipt): `Fix mistakes · 7 of 8 · closed "used the
    diameter as the radius", "dropped the negative root"`;
  * right, the next block: `Focus set · Circles, Percentages · 20 q · 32 min · timed`;
  * pill `Continue ↵` and `.quiet Stop for now` (Esc returns to `/plan/`, progress kept).
  * The ordinary summary follows below, unchanged.
* **After a test block**, the report's footer (S6) shows `Continue today · Focus set · 10 q`.
* **The end of the run** is T19's receipt, rendered in the session page: minutes, questions,
  right, mastery words moved, mistakes fixed and new ones by name (`first in tomorrow's Fix`),
  check-ins held, `Streak 5 (+1)`.
  * Your own tasks follow as live checkboxes, then a one-line preview of tomorrow.
  * Actions: `Keep going · 10 more` and `Back to plan`.
  * "Day done" and the streak bump appear only when §4's day rule is met.

**Data.** The drill body's `run` (YYYY-MM-DD) is stored in cfg and echoed; it changes nothing
else. Chaining is on the client, from the finish response's existing `plan.next`. The rail reads
`GET /api/plan/day/{run}` (tasks with answered/total). The end reads `/api/today.receipt` (T19).

**Acceptance.**
1. Clicking Start today → `/practice/session/?id=X`, and `GET /api/drill/X` has `cfg.run ==
   today` and `cfg.task` equal to the first undone counted task's id.
2. Finishing that block shows "Continue" and the next task's title; Enter creates a session with
   the same `run` and the next task's `task`.
3. After the last block the page contains "TODAY'S WORK", and `GET /api/plan` shows today
   `done` (or `partial` by the rules).
4. On a test day the first block opens `/test/?s=`; the report page contains "Continue today".

#### L9. Today I have: time chips that trim the day by value

*From: outcomes #4 (time box, minimum day), the experience DayPanel gap, unfair-advantage #7.
Effort S. Builders: S7, S3 (the same chips on Today's plan card).*

**Why.** A plan that only offers "skip" on a bad day gets abandoned. Ten minutes of the
highest-value work keeps the spacing, the streak and the habit. Theirs has fixed durations and a
Behind banner that fires a week too late.

**Screens.**
* A chip row in the DayPanel head: `Today I have: 10 · 15 · 30 · [45] · 60 · 90 min`, with the
  planned minutes selected.
* Choosing a chip shows a preview line in place before applying:
  `Fits: Warm-up 3 · Fix 4 · Focus 8 · Left for later: Focus 10 q (its topics come back sooner)`
  with `.btn Apply` (Enter) and `Cancel`.
* Apply → `PUT /api/plan/{id}/day/{today} {minutes, trim:true}`, with Undo.
* The same chips replace `Practice anyway` on a rest day (they start that many minutes from the
  next allocation), and sit on Today's plan card.

**Rules.**
* **Shrinking**: focus first (down to 5), then pace, habit, learn and check drop, then fix down
  to 4, then the warm-up down to 3. The 10-minute day is warm-up 3 + fix 4.
* **Growing** adds focus questions.
* Nothing is moved: undone focus topics keep their deficit (§4) and the re-deal brings them back
  sooner.
* A trimmed day below 60% of its base minutes can be at best `partial` (a half-ring "short day"
  glyph on the calendar and week strip). A partial day keeps the streak.

**Data.** `GET /api/plan/day/{date}?minutes=m` returns the trimmed preview `{tasks, cut:[{kind,
count, topics}]}`. `plan_overrides.trim INTEGER DEFAULT 0`.

**Acceptance.**
1. `PUT day {minutes:10, trim:true}` on a 45-minute day: today's counted tasks total ≤ 10
   minutes, in the order warm-up, fix.
2. All of them done → today's status is `partial`, and `stats.streak` grew by 1.
3. The next practice day's focus topics include the topics cut today.
4. `DELETE` the override → today's minutes are 45 again.

#### L10. Rows that say what they're worth, show their evidence and report what they did

*From: the Why, task-action and Again gaps of all three, outcomes #9 (fix order), the open
question on Mark done. Effort S. Builders: S7 (`UI.taskRow`, PATCH), P18 (rematch misses), T2
(the result shape).*

**Why.** Their aiReason can't be checked, and a ticked task records nothing. Ours should prove
each claim in one tap, act on why a student skipped, and say after every task what it
changed.

**Row additions.**
* **Meta**: minutes at the learner's pace (L4) and the skill's `≈ +15` (L1).
* **Why lines carry evidence** (`why: [{text, href}]`):
  * open mistakes → `/review/?open=trap:{id}` (the `UI.review` pane);
  * `41% right on 17` → the skill's `UI.history`;
  * `last worked 9 days ago` → that session's review;
  * `≈ +15` → the skill's points row;
  * pace → `/me/#pace`;
  * a cause (`3 slips`) → T7's items.
* **Done receipt** (`result`): `15 of 15 · 12 right · 2 fixed · 1 new mistake · Circles 41% →
  58% · 12 min`, plus `Circles: 2 more right to Strong` (U4 `to_strong`). When it opened
  mistakes, `.btn Fix the 1 it opened · 2 q` (T2's body).
* **Skip asks why**, optional. After Skip, the row shows `Why? No time · Too hard · I know this`:
  * **No time** → moved to the next study day (`Moved to Thu · Undo`).
  * **Too hard** → a Learn it task (L4) comes before the skill's next focus set.
  * **I know this** → a 5-question test-out now: `{topics, count:5, tiers:['medium','hard'],
    timing:'pace', task:'<d>:check:<t>'}`. 4/5 or better passes the skill (L3's rule). Less
    reads `Not yet · 2 of 5`, and the task returns to todo.
* **Mark done on a question task** opens `Did it elsewhere? [20] min · Bluebook · Khan Academy ·
  A book · Class · Other`. The minutes count toward the day's minutes and status (R13's own-task
  rule), never toward question stats or mastery. The row reads `Marked done · 20 min in Khan
  Academy`. (This resolves §3.6.9's Mark done question.)
* **Again** on a done set:
  * `Again · the 3 you missed, new numbers` → `{rematch: sid, scope:'misses',
    task:'<d>:extra'}` (the primary, shown when there were misses);
  * `Again · 10 more like this` (v2);
  * `Again · harder` when the set was 90% or better and a tier above exists.

**Data.** `PATCH /api/plan/{id}/tasks/{task}` accepts `{status:'skipped', reason:
'no_time'|'too_hard'|'know'}` and `{status:'done', minutes 1–240, where}`. `plan_marks` gains
`minutes INTEGER` and `note TEXT` (the reason or where). `Task.result` gains `fixed:[label],
opened:[label], moved:[{topic, from, to}], to_strong`.

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

#### L11. Typed own tasks: an official test feeds the plan

*From: the custom-task gaps of all three. Effort S. Builders: S7, U2's quick sheet (F2 / F5),
S3 (`add_outside_score`).*

**Why.** A student's Bluebook practice test is the best evidence they have, and in theirs (and
v2) ticking it teaches the plan nothing.

* **Quick-add chips**: `+ Official Bluebook practice test · once` (type `bluebook`, default 134
  min), `+ Reading & Writing · 30 min · every study day` (type `rw`, subject `rw`),
  `+ Tutor session` (type `tutor`), `+ Other…`.
* **Ticking a bluebook task** opens U2's quick sheet on **A whole test**, prefilled with the
  task's day:
  * the Math score (and optional R&W) goes to `add_outside_score(source:'bluebook')`, so it feeds
    mean3, the trajectory, drift and the projection;
  * the missed cells build U2's follow-up set, which becomes tomorrow's Fix (`Bluebook
    follow-up · 2 per missed skill`).
  * `Add the score later` leaves a plain tick, and a link stays on the done row.
* **Tutor**: the done row offers `Log a mistake from it` (U2, one question) repeatedly and counts
  them (`3 logged`).
* **R&W**: counted as R&W minutes; when Words is on, the detail links `Words · 12 due`.

**Data.** `plan_tasks` gains `type TEXT DEFAULT 'other'` and `subject TEXT DEFAULT 'math'`.
Ticking a bluebook task returns `{next:'score_sheet'}`.

**Acceptance.**
1. `POST /api/plan/{id}/tasks {type:'bluebook', day}` creates a task with `minutes == 134`.
2. Ticking it and saving Math 610 → `/api/scores` lists an outside score of 610 on that day,
   and `GET /api/plan.sittings` includes it.
3. Three missed cells in 2 skills → tomorrow's tasks include a `fix` whose detail contains
   "Bluebook follow-up".

#### L12. Drag, keys and instant

*From: experience #8, the experience loading gap, U23 / T20. Effort M. Builders: S7, F2
(`UI.keys` scope `plan`, `UI.cached`), F1 (`UI.sheet`).*

**Why.** Their only reschedule is three taps to a later day of the same week. A plan is edited
every day; each edit should be one gesture that shows its consequence first.

* **Drag (desktop, pointer events, no library)**: each task row has a handle. While dragging:
  * every valid WeekStrip column and MonthCalendar cell shows its new load in mono
    (`45 → 73m`);
  * invalid ones are dimmed, with the reason in a tooltip and `aria-describedby`: rest day, the
    eve, a test on a day under 35 minutes, past the due date for homework.
  * The drop sends `PATCH {day, to}`, with the toast `Moved to Thu · Undo`.
* **Phone**: a long press (500 ms) opens the Move sheet: the next 7 study days with their loads,
  plus `Another date…`.
* **Keys** (`UI.keys` scope `plan`, listed under `?`, ignored while typing):
  * `J` / `K` or `↓` / `↑` select a task; `Enter` starts it;
  * `X` done or not done; `S` skip or undo; `U` undo the last action;
  * `M` move mode: `←` / `→` walk the days showing each new load, `Enter` confirms, `Esc`
    cancels;
  * with no task selected: `←` / `→` change the day, `Shift+←` / `Shift+→` the week, `T` today;
  * `1` / `2` / `3` switch tabs; `Shift+Enter` Start today.
* **Instant**: `/api/plan` goes through `UI.cached(path, {store:'local', until:'day'})` (U23 as
  T20 extends it), so a second visit paints at once under an `Updating…` rule. Every action is
  optimistic and rolls back in its row with `Couldn't move. Try again.` Offline, the plan stays
  readable, and Start reads `Starting needs a connection`.

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

### D. Is it working?

#### L13. Will I make it: the projection, a checkpoint on every test day, and levers priced in pace and hours

*From: outcomes #10, experience #4, unfair-advantage #2 (their honest parts), the tile gaps of
all three. Effort M. Builders: S7 (tiles, levers, checkpoints), F4 (U9 `estimate.projection`),
S3 (`today.workload`), F1 (`UI.bandChart` cone).*

**Why.** Their Score gap tile never changes, and their pace line never says whether it is
realistic. A student needs to know in week 2, not week 6, whether this plan reaches the target,
and which lever closes the gap. `shell-me.md` and `today.md` rejected any model from minutes to
points, so the levers here are priced in what we can defend: the pace needed against the pace
made, and hours of work against hours available.

**Stat tiles.**
* **Days to exam** adds capacity: `31 study days · 23 h planned · the work left is about 19 h ·
  fits with 4 h to spare`, or `short by 3 h · add 10 min a day [Set 55 min]` (`PATCH {minutes}`,
  Undo). From `today.workload` (T12).
* **Score** keeps v2's start → target, track and chip, and adds:
  * `At this pace: 640–700 on Nov 7` (U9's projection), or `Two scored sittings in 60 days start
    a projection` with `Take this week's test now`;
  * `Making +9 a week · needs +18` (made = U9's slope; needs = (min(target, 780) − mean3) ÷ weeks
    left);
  * `≈ +18 claimed since Sep 23 · from 412 answers` (L1);
  * `First modules about 54% · 14 of 22 routes up` when `target > 580`;
  * `What changes it ›` opens the levers.
* **Plan done** reads against the schedule: `27% · 12 of 44 study days · on schedule`, or
  `2 behind · make up Thu? [Do it now]` (starts the missed day's catch-up task).
* **This week** adds U14's goal pips (L16).
* Each tile is a button: Days → the calendar, Score → the trajectory, Plan done → the missed
  days, Week → the week review.

**Checkpoints on every test day.**
* Each test task shows `Checkpoint 2 · aim 610+`: the pace line (start → target on the exam
  date) at that date, rounded to 10.
* After the sitting: `680 mid · beat by 70` or `590 mid · 20 under`.
* The WeekStrip marks a beaten test day with ✓. The TrajectoryChart draws the aims as ticks on
  the pace line, filled when beaten.

**Levers** (`What changes it`, the Behind banner, and the Score tile's `Short` state). The top
3 by improvement, each previewed and applied with one tap and Undo:
* `+15 min a day · fits with 6 h to spare`;
* `Add Saturday · 38 study days · fits with 3 h to spare`;
* `Move to Dec 5 · needs +11 a week (you make +9)` (only when not booked);
* `Ramp from 25 · 20 h to the exam · fits with 1 h to spare`.

**TrajectoryChart** gains U9's cone (a `--mat` area from now to the exam) beside the pace line,
with its hidden-table rows.

**Data.** `GET /api/plan` adds `projection` (U9), `verdict: {kind, made_per_week,
needs_per_week}`, `workload` (T12, through `deps.part('today', 'workload')`), `levers:
[{kind, label, patch, effect: {needs_per_week, fits, spare_h, short_h, study_days}}]`, and
`test.aim` / `test.result` per test task. Preview computes the levers.

**Acceptance.**
1. Sittings with midpoints 500 (Sep 1) and 560 (Sep 15), exam Nov 7, target 700: `projection`
   is non-null, `verdict.made_per_week > 0`, and the Score tile shows "At this pace".
2. A plan whose workload is short: the Days tile shows "short by", and its Set button's body is
   `{minutes: workload.suggest_minutes}`.
3. A test task 3 weeks into a 560 → 700 plan over 7 weeks has `aim == 620` (560 + 140 × 3/7,
   rounded to 10). A sitting at midpoint 650 reads "beat by 30".
4. `levers` has at most 3 items; each `patch` applied through preview changes `effect` as
   stated. No lever label contains a score range.

#### L14. Checkpoint twins: the same 22 question types as your baseline, slot by slot

*From: unfair-advantage #3, the unfair-advantage test-rhythm gap. Effort M. Builders: S7 (the
rhythm, the task, the card), S5 (twin kind with `task`, exists), S6 (`GET
/api/session/{id}/compare?with=`, from T16).*

**Why.** Their plan draws on 10 fixed papers, and a retake repeats questions whose keys the
student has seen, so the second score is contaminated. A parallel form on demand needs a
generator. With one, two tests two weeks apart finally compare like with like, slot by slot.

**The baseline**: the first scored module or section finished inside the plan window, else the
most recent in the 14 days before the start (`cfg.baseline`, set once it is found). A
diagnostic baseline gives fresh sections until a module or section exists.

**Checkpoint tests**: with `cfg.checkpoints` `every` or `every2`, those test tasks start `POST
/api/mock/new {kind:'twin', twin_of: <baseline>, task:'<d>:test'}`.
* Row: `Checkpoint 2 · twin of your Sep 23 module · same 22 question types, new numbers · 35
  min`.
* The other test days stay fresh adaptive sections.

**CheckpointCard** (top of the Progress tab; also in the report when the sitting's task is a
checkpoint):
* `Baseline 11/22 · 470–610 → Checkpoint 2 16/22 · 560–700 · +90`.
* A 22-cell slot strip for module 1. Each cell has a glyph and text: fixed ✗→✓, held ✓→✓,
  slipped ✓→✗, still missed ✗→✗. Counts under it: `fixed 7 · held 9 · slipped 2 · still missed
  4`.
* Tapping a cell names the skill, the tier and the trap chosen.
* Pill `Fix these 6` → `{from_session: <checkpoint>, only: [the slipped and still-missed qids],
  each:2, source:'twin', task:'<today>:extra'}`.
* A series line: `Baseline 11 → CP1 14 → CP2 16 of 22`.
* On the TrajectoryChart, checkpoints are filled squares and fresh tests dots.

**Acceptance.**
1. A plan with a module baseline and `checkpoints:'every2'`: the second test task's start body
   has `kind:'twin'` and `twin_of` = the baseline; the first and third are fresh.
2. After the checkpoint, `GET /api/plan/progress.checkpoints[0]` has 22 slots, each `change` in
   {fixed, held, slipped, still_missed}, and the counts sum to 22.
3. `Fix these` sends `only` with exactly the slipped and still-missed qids.
4. At 390 the slot strip wraps to 2 rows of 11 with no page scroll.

#### L15. What changed this morning, and why

*From: experience #6. Effort M. Builders: S7, F4 (`plan_snapshots`).*

**Why.** Theirs markets "dynamic score drift adjustments" through a black-box regenerate. Ours
re-deals every day, which is only trusted if the student can see what moved and which answer
moved it.

* On the first `GET /api/plan` of each local day, plan.py stores the next 14 days (date, kind,
  minutes, test, topics, task kinds and counts) in `plan_snapshots`, kept 60 days.
* A diff against the previous snapshot gives change lines. Each takes its cause from the same
  facts the why lines use, first match:
  1. your edit, named;
  2. a sitting;
  3. a focus move (L3);
  4. mistakes opened or closed, with the label;
  5. a phase change.
* Examples: `Circles added Thu · 2 new mistakes yesterday` · `Fix set 8 → 12 · 4 new mistakes` ·
  `Fri module → section · Final starts` · `Mon off · you took it off` · `Circles → Strong ·
  passed its check 4/4`.
* **Strip** under the tabs: `Updated this morning · 3 changes ›`, which expands in place to the
  lines. Each line selects its day. Changed WeekStrip cells carry a small dot until that day is
  selected (localStorage, try/catch). With no changes the strip reads `No changes today`.
* **Progress › Changes**: `Your plan changed 23 times · 17 from your answers · 4 from your edits
  · 2 from tests`, then the dated list, paged by 20.
* Every automatic change (L3, L7's re-base, L17 auto-drift) writes a line.

**Data.** `plan_snapshots(plan, made_on, days JSON; PK(plan, made_on))`. `GET /api/plan.changes
= {today: [{text, day, cause}], counts}`. `GET /api/plan/{id}/changes?before=` pages the
history.

**Acceptance.**
1. Day 1 GET, then a new trap on circles, then day 2 GET: `changes.today` has a line naming the
   trap's label with `cause == 'mistakes'`.
2. `PUT day {off:true}` for Monday, then the next day's first GET: a line "Mon off" with
   `cause == 'edit'`.
3. A second GET on the same day adds no snapshot row.

#### L16. The week: review, goals in the header, and next week shaped in one sheet

*From: outcomes #4 (weekly reset), experience #7, unfair-advantage #8, the week-view gaps of all
three. Effort M. Builders: S1 (U14's sheet hosts it), S7 (`UI.weekPlanner`, the week endpoint),
F4 (U14's `week_goals`).*

**Why.** Their week is a theme sentence and a percentage. A week should end with its real
results, set up to three checked goals, and let the student reshape next week in a minute, short
of rebuilding the plan.

* **The review is U14's Monday sheet** (S1). With an active plan, its receipts add the plan's
  facts (`Days 4 of 5 · 3h 10m of 3h 45m · Circles before 1/4 → after 4/4 · Checkpoint 610+
  beaten by 40`).
* It gains **Next week's plan**, S7's `UI.weekPlanner(host, week)`:
  * 7 day tiles with their topics and test day, a minutes select (−15 · default · +15), and
    `Busy` (off) / `Short` (15 min) toggles;
  * `Swap a focus skill`, choices from L1's list with their points;
  * `Looks good` saves.
* U14's goal kinds add `pass_check {topic}` (L3).
* **WeekStrip header**: `Week 3 of 7 · Sep 21–27 · Goals 2/3`, with pips (met ✓, open ○,
  missed –) and `.quiet Review week`, which opens U14's sheet for that week. When goals exist,
  the theme line leads with them: `Goals: fix the 4 Circles mistakes · pass the Circles check ·
  module Fri 610+`.
* **Progress › Weeks**: one row per past week: days, minutes, questions, fixed, checks passed,
  checkpoint, goals met.

**Data.** `PUT /api/plan/{id}/week/{monday} {days: [{date, minutes?, off?}], swap?: {from, to}}`
writes `plan_overrides` for those dates (and `cfg.skills` for a swap). Only future dates;
returns the refreshed days.

**Acceptance.**
1. `PUT …/week/<next Monday> {days:[{date:<Tue>, off:true}, {date:<Thu>, minutes:15}]}` →
   Tuesday is `off`, and Thursday's minutes are 15.
2. With an active plan, U14's sheet contains "Next week's plan" and 7 tiles.
3. A `pass_check` goal on circles turns `done` when the circles After passes.

#### L17. Banners that price their fixes

*From: outcomes #4 (the weekday pattern), the Behind and drift gaps of all three, the experience
streak gap, U17. Effort S. Builders: S7.*

* **Behind** (v2's trigger):
  * what it cost (T18's line): `2 study days missed · 4 check-ins now overdue · 2 mistakes older
    than 10 days`;
  * primary `Catch up · 15 min` (U1's box of 15);
  * the fixes side by side, each previewed and applied with Undo:
    * `Shorter days: 25 min × 5 · fits · pace unchanged` (v2's fit);
    * `Ramp: start at 25, add 5 a week` (L7);
    * `You miss most Tuesdays and Thursdays. Make them 15-minute days?` (`PATCH {day_minutes}`),
      shown when a weekday was missed at least twice, and on at least half its planned days, in
      the last 28 days;
    * `Later date: Dec 5 · needs +11 a week` (when not booked).
  * v2's `Add days off` and `Dismiss` stay.
* **Drift** (v2's rule, T10's content):
  * the sittings as dated chips linking to their reports;
  * what moved: `Percentages +0.18 · Circles +0.12 since the plan started`;
  * the effect before applying: `Start from 650 · needs +11 a week instead of +22`;
  * `Raise to 750` with its needed pace.
  * Pref `plan_auto_drift` (default off) applies it at once, with a toast, Undo and a changelog
    line.
* **Missed** adds the streak: `Make it up to keep your 9-day streak`, and with a spare banked
  (U16) `· or a spare covers it`.
* **Registration** replaces BookedReminder: `Nov 7 isn't booked yet · register by Oct 23 · 5
  days left` with `I've registered` and `College Board ↗`. `cfg.booked` and U17's
  `prefs.registered == exam_date` are one fact.
* **Graduated / Slipping** (L3, when auto is off) and **Map done** (L2).

**Acceptance.**
1. A learner who missed 3 of the last 4 Tuesdays: `behind.fixes` has a `weekday` item naming
   Tuesday; applying it sets `day_minutes[1] == 15`.
2. The drift banner's preview text contains "needs +" and a number.
3. `PUT /api/me {prefs:{registered:'2026-11-07'}}` with that exam date → the registration
   banner is gone, and `GET /api/plan.active.cfg.booked == true`.

#### L18. Progress: what the time bought

*From: the Progress gaps of all three, outcomes #5 (causes), outcomes #9 (calibration),
experience #3 ("Not moving"), unfair-advantage #1 (time against points). Effort M. Builders: S7
(cards), F4 (`progress.causes`, `progress.pace`), P7's data.*

**Why.** Their three charts (accuracy weakest first, minutes, split by task type) don't tell a
student whether their time is paying. Ours says, per skill, what the minutes bought, why points
are lost, and where time and points disagree.

**New cards** (v2's stay):
* **What your time bought**: one row per skill with 10+ minutes since the start:
  * minutes;
  * first-try accuracy start → now (the 20 clean first tries before the start, or `new`,
    against the last 20);
  * mistakes fixed;
  * the check before → after (L3);
  * `≈` claimed (L1).
  * Sorted by minutes. A row is flagged **Not moving** after 60+ minutes in 14 days with under
    3 points of change over its last 20 answers. It then offers `Learn it · untimed` (T4) and
    `See its misses` (T7 items for that topic).
* **Why you lose points**: T7's causes over the plan's days (at most 60), the same bar and fix
  buttons, plus a 4-week trend per cause.
* **Coverage** (L2), **Checks** (L3), **Weeks** (L16), **Changes** (L15), **CheckpointCard**
  (L14).
* **Pace and calibration**:
  * U7's header line (`a module at your pace takes 38:40 of 35:00`) and the top 3 slow-but-right
    skills with T8's Speed drill;
  * with 20+ tagged answers since the start, P7's `Sure 88% right (212) · Unsure 51% (74) ·
    Guess 27% (19)` and its reading line;
  * `Every skill ›` → `/me/#pace`.

**Changed cards.**
* **DomainCard**: `.seg By points · By accuracy` (By points by default when gains is non-null);
  each row adds `≈ +40 on the table · ≈ +12 claimed since Sep 23`.
* **SplitCard**: a third bar, minutes by domain over the plan against the share of points on the
  table (T17's `time_split`): `Algebra · 35% of your time · 12% of your points`, with
  `.btn Rebalance to the points`, which puts the domain with the largest gap on Focus (PATCH,
  Undo).
* **StudyTimeChart**: a first-try accuracy line on a right axis (a hollow dot under 5 answers);
  clicking a bar opens that day on the Plan tab (`?day=`).

**Data.** `GET /api/plan/progress = {bought, causes, coverage, checks, weeks, checkpoints,
calibration, pace, split_domain, changes_counts}`.

**Acceptance.**
1. A skill with 70 minutes in 14 days and first-try accuracy 50% → 51% over its last 20 answers:
   its row has `not_moving: true`, and the card shows "Not moving".
2. `causes.total` equals the plan period's R8-counted first-try misses.
3. DomainCard By points orders rows by summed gain, descending.
4. Clicking Thursday's bar in StudyTimeChart → the URL has `?tab=plan&day=<Thu>`, and the
   DayPanel kicker shows that date.

---

### E. The last weeks, and after

#### L19. Final phase: dress rehearsals, the sweep, a taper and your trap sheet

*From: outcomes #11, experience #5, #12, unfair-advantage #9 (the trap sheet), T13. Effort M.
Builders: S7 (rules, tasks, sheet), S5 (the no-pause flag), S6 (rehearsal lines), T13 / U6
bodies.*

**Why.** The last two weeks protect the score: rehearse under real conditions, keep what is
known, re-test every old mistake, then rest. Theirs changes nothing as the date nears. T13
already defines this for Today; with a plan, the plan's Final phase is where it lives (T13: "its
tests are the rehearsals").

**Dress rehearsals** (T13's rule: each exam weekday in Final that leaves at least 6 days, at most
2):
* The day becomes a test day, even if it was a rest day; the student can move it.
* A full section, official timing, Desmos, and no pausing (S5's per-sitting flag, open question
  9).
* Row: `Dress rehearsal · like Nov 7 · Sat 8:30 · 2 modules · 70 min · no pausing`.
* A calendar event at `cfg.rehearsal_at` (default 08:30, 90 minutes with the break).
* Task menu option `Sit Bluebook R&W first, like the real morning`: it adds a bluebook own task
  `Bluebook R&W section · 64 min + 10 min break` at 08:30 and moves the Math start to 09:45.
* The rehearsal's report (S6) adds pace by quarter of each module and `Last 5 questions: 2:10 a
  question vs 1:25 average`, from `qstate` ms.

**The sweep** (task kind `sweep`, T13's pool rule):
* `{pool:'checks', sweep:true, count, task:'<d>:sweep'}`, spread over Final's practice days:
  count = ceil(to go ÷ days left), at most 40% of `q`. It needs 5 or more closed traps.
* **Scoreboard** (DayPanel side column and Progress): `Still fixed 31 · Back on the list 4 · To
  go 9`, one square per trap (right: orange with ✓; wrong: graphite with ✕; to go: outline),
  each with an aria-label.
* A miss reopens the trap as Relapsed (R9), first in the next day's Fix.

**Taper** (the last 5 study days before the eve):
* minutes × 0.6 (an override shown as `Taper · 27 of 45 min`; day status rules as normal);
* no Learn, Map or Habit;
* the warm-up at 8;
* focus only on skills with 2 or more questions a test (U4 `per_test`);
* the last timed set 2 days out.
* A **Trap gauntlet · 10** (U6) as a counted task 3 days out.

**Trap sheet.**
* `GET /api/plan/{id}/trapsheet` returns up to 10 entries: U6's top habits, then the top open or
  relapsed traps. Each has:
  * the name, hits and the tell;
  * one example from the type's reserved seeds (`/api/types/{t}/example`: never served, so no
    key the student has seen), walked up to 40 seeds for one that carries the trap;
  * the trap option marked `Your trap`, the key and the rationale.
* It renders at `/plan/?print=traps`, readable on a phone and printable (`@media print`, 2
  pages).
* The eve stays a rest day with no counted task (so R13's streak rule is untouched). Its one
  extra is `Read your trap sheet · 5 min` (tick), beside the checklist. The eve card adds `38 of
  44 still fixed · Rehearsal Oct 31: 680 mid · pace held`.

**Acceptance.**
1. Exam Sat Nov 7, plan from Sep 23 (a 10-day Final): Oct 31 is a test day with `rehearsal:
   true` and a section body with `pause: false`, and it is the only rehearsal. A plan from Aug 1
   (a 15-day Final) has two, Oct 24 and Oct 31. No rehearsal falls within 6 days of the exam.
2. A learner with 12 closed traps: Final's practice days carry `sweep` tasks whose counts sum
   to 12 (±1 per day).
3. The last 5 study days before the eve have minutes = round(0.6 × base) and no `learn` tasks.
4. `GET …/trapsheet` returns ≤ 10 entries, each example with `seed >= 900000`, and no entry
   without a tell.
5. The eve has no counted task, one extra titled "Read your trap sheet", and `kind == 'eve'`.

#### L20. Plans that remember what worked

*From: the Plans/History gaps of all three. Effort S. Builders: S7.*

**Why.** Students retake. The first plan's evidence (which weekdays held, which skills
relapsed, what an hour bought) should make the second plan better, not start from scratch.

* **PlanSummary** gains `record: {hours, days_pct, by_dow: [pct × 7], start_mid, end_mid,
  result, fixed, relapsed, checks_passed, best_weekday, changes}`.
* **Plans rows** for finished and archived plans: `Sep 1 → Oct 3 · 82% of days · 31 h · 560 →
  650 (+90) · 44 fixed · 3 relapsed`, with a 7-cell weekday adherence strip (glyph and percentage
  per day). Expanding a row shows its changelog timeline (L15): `Oct 2 fitted to 25 min · Oct 9
  target 750`.
* The ResultPanel summary adds `+2.9 points an hour on this plan (560 → 650 over 31 h)`. It is a
  record of what happened, never a forecast.
* **Plan the next one from this** carries:
  * the result as current;
  * the time settings, with weekdays under 50% adherence set to 15 minutes;
  * relapsed skills on Focus;
  * the Words and extras settings;
  * the same own tasks.

**Acceptance.**
1. A finished plan: `plans[i].record.by_dow` has 7 numbers from 0 to 100, and the row shows the
   strip.
2. `Plan the next one` on a plan whose Tuesday adherence was 30% → the draft has
   `day_minutes[1] == 15`.

---

## 3. Spec overrides

### 3.1 Inside §3.6 (spec/rebuild-v2.md lines 7046–8096)

Each entry quotes the current text, then gives the replacement or addition.

1. **Box.**
   * Quote: "> **Read with resolutions:** R9, R10, R11, R13, R14, R15, R16, R18 (§2.2). Where
     this spec disagrees with them, they win."
   * Append: "Read with `spec/v2-upgrades/plan.md` (L1–L20), which wins over this section, and
     with the sibling functions it names (U1, U2, U4–U7, U9, U13–U18, U23, U25; T1–T4, T7, T8,
     T10–T13, T19; P2, P7, P8, P10–P12, P16, P18)."

2. **1a Hero, the pill.**
   * Quote: "  - Pill `Create my plan`, which opens `?setup=1&step=1`."
   * Replace with: "  - With 30+ answers or a sitting, the right column is **Your plan, ready**
     (L6), and the pill is `Use this plan` (`POST /api/plan` with `proposal.cfg`), with
     `.btn Adjust…` → `?setup=1&step=1` holding the proposal as the draft. Otherwise the pill is
     `Create my plan`, which opens `?setup=1&step=1`."

3. **1b BankStats.**
   * Quote: "**1b. BankStats**: three `--tile` tiles, each a big DM Mono 40 number with a label
     and one line. The data comes from `GET /api/plan` → `bank`."
   * Add before it: "**1b′. Your numbers** (30+ answers): ≈ points on the table with the top 3
     skills, the route line, and open mistakes with the top label (L1)."

4. **1d ExampleDay.**
   * Quote: "- A new student sees the blueprint-weighted focus set only."
   * Replace with: "- A new student sees the blueprint-weighted focus set, and its first row
     holds a live question (`UI.workspace` inline, L6). With data, the example day is the
     proposal's day 1."

5. **2a GlancePanel.**
   * Quote: "- **GlancePanel**: recomputed by `POST /api/plan/preview`, debounced 250ms. Stale
     rows dim to 60% while the call is in flight. Rows:"
   * Add before the rows: "It opens with the **Live plan** (L6): the compact month, week 1's
     columns and day 1's rows, each changed cell ringed once."

6. **2a Footer.**
   * Quote: "  - Enter advances when focus is not in a text field."
   * Add: "  - ⌘/Ctrl Enter creates the plan from any step once step 2 is valid, with defaults
     for the rest (L6); the footer shows `⌘↵ create now`."

7. **2b New student.**
   * Quote the "  - **New student**: `Don't know? Take the diagnostic (20 questions, about 30
     min)`." item and its two sub-bullets.
   * Replace with: "  - **New student**: two choices, **Let the plan measure it** (default:
     `current: null, measure: true`; day 1 starts with the diagnostic, then Map days, and the
     first sitting sets `current` with Undo) and **I'll estimate** (the slider) (L7, L2). The
     `satf.return` path stays for a diagnostic started from this step."

8. **2b RangeBar.**
   * Quote: "- **RangeBar**: a 200–800 track with the ticks `200`, `avg 505` (`MATH_MEAN`, see
     open questions) and `800`, and an ink dot at the current value."
   * Append: "The last 3 sittings are drawn on it as grey dated bands, with an ink tick at their
     mean (L7)."

9. **2c TargetNote.**
   * Quote: "- **TargetNote** (mono 12.5, `--soft`), computed by the server from `scoring.py`:"
   * Add as its first two lines: "`700 ≈ 37 of 44 right · you're near 31 · the 6 you're most
     likely missing are in …` (U4 `need`)" and, above 580, "`Your first modules: about 54% · 14
     of 22 routes up`" (P10 `route`).

10. **2c DateChips.**
    * Quote: "  - Two lines per chip: `Oct 3`, and in mono `10 d · 98/wk`. The selected chip is
      orange."
    * Replace with: "  - Each date is a `UI.examDate` row (T12): `Nov 7 · Sat · in 45 days · 32
      study days · +11 a week · Steady · register by Oct 23 · ~690` (the projection when U9 has
      one); the first Steady date is tagged `Recommended`. The selected row is orange."

11. **2c PaceLine.**
    * Quote: "  - For `Very ambitious`, a line suggests a later date: *Nov 7 brings it to 22 a
      week.* The date is a button that selects that chip."
    * Add: "  - With a U9 slope: `You're making +9 a week; this date needs +22.`"

12. **2d MinutesChips.**
    * Quote: "- **MinutesChips** `A study day`: `15m 30m 45m 1h 1.5h 2h 2.5h 3h 4h`."
    * Add after it: the rhythm line with `Use that`, the overreach warning, and **Ramp**
      (`cfg.ramp`) (L7).

13. **2d WeekdayTiles.**
    * Quote: "- **WeekdayTiles**: seven tiles, Mon–Sun, with 3-letter names. Each tile is 72px
      wide at desktop."
    * Append: "Each tile also shows `studied 3 of last 4 · ~35m` (L7)."

14. **2d TestRhythm.**
    * Quote: "- **TestRhythm** `Practice tests`: segmented `None · Weekly · Twice a week · Every
      study day`."
    * Add under it: "  - **Checkpoints**: `Every test · Every 2nd test · Off` (default Every
      2nd; L14). A tests-share warning above 30% of the planned minutes, with `Weekly instead`
      (L7)."

15. **2d ClockMode helper.**
    * Quote: "  - Helper: `Test pace is 95 s a question`."
    * Replace with: "  - Helper: `Each question gets its own budget: easy 1:05 · medium 1:35 ·
      hard 2:06` (P16)."

16. **2d PreferredTime.**
    * Quote: "- **PreferredTime** `Usual time`, used for the calendar: chips `Morning 8:00 ·
      Afternoon 15:00 · Evening 18:00 · Other`, where `Other` opens a time input."
    * Add: "- **Where** (`cfg.place`, ≤ 30 characters, optional), used in event LOCATION, the
      DayPanel head and Today's plan line (L7)."

17. **2e Suggestion rule.**
    * Quote the "  - **Suggestion rule**:" item and its three sub-bullets.
    * Replace with L1's rule (top 3 skills by value per minute with gain +10 or more; a domain
      with 40%+ of the gain; Strong under 5 and mastery ≥ 0.8; §2e's old rule under 30
      answers).

18. **2e additions.**
    * Quote: "- **SplitBar** `Your practice week`:"
    * Add before it: "- **Where your points are** panel (L1), the coverage line on each
      DomainRow (L2), and the switch `Move a skill off Focus when it passes its check`
      (`prefs.plan_auto_focus`, L3)."
    * Add inside it: "a second bar, `Where your points are` (L1)."

19. **2e Extras.**
    * Quote: "  - `Rechecks`, default on: *Mistakes you fixed come back 3, 10 and 30 days later
      with new numbers.*"
    * Replace with: "  - `Warm-up`, default on: *Questions you got right before, back just as
      you start to forget them, mixed and unlabelled* (T3; task kind `recheck`)."
    * Add: "  - **Words** row: `SAT words and transitions · [0 · 5 · 10 · 20] new a day · about
      6 min a day`, writing `prefs.words_goal` and `prefs.words_from` (decision 2; L4, L7)."

20. **2e Your own tasks.**
    * Quote: "  - Quick-add chips: `+ Reading & Writing · 30 min · every study day`, `+ Official
      Bluebook practice test · once`, `+ Other…`."
    * Replace with: "  - Quick-add chips: `+ Official Bluebook practice test · once` (type
      `bluebook`, 134 min), `+ Reading & Writing · 30 min · every study day` (type `rw`),
      `+ Tutor session` (type `tutor`), `+ Other…` (L11)."

21. **2f Create.**
    * Quote: "  - a toast (`role=status`) reads `Plan made · 31 study days to Nov 7`."
    * Add: "  - keyboard focus moves to `Start today` (L8); after a one-tap create, the `Built
      from your results` chip banner shows (L6)."

22. **3b StatTiles.**
    * Quote: "###### 3b. StatTiles (4 in a row at desktop; one full-width tile plus a 3-up row at
      390)"
    * Add under the heading: "Each tile is a button that opens its detail. Days adds capacity
      against the work left; Score adds the projection, made vs needed a week, ≈ claimed and the
      route; Plan done reads against the schedule; This week adds the goal pips (L13, L16)."

23. **3c Banners.**
    * Quote: "  - Pill `Fit the plan to 25 min`. Under it, a preview line: `Same date and target
      · 870 → 480 questions to Nov 7 · pace unchanged`."
    * Replace with L17's Behind: what it cost, `Catch up · 15 min`, and the previewed fixes
      (shorter days, ramp, the weekday pattern, a later date).
    * Quote: "- **BookedReminder** (the date is provisional): `Nov 7 isn't booked yet` with
      `Booked it`."
    * Replace with L17's registration banner (`register by …`, `I've registered`, `College
      Board ↗`), where `cfg.booked` mirrors `prefs.registered`.
    * Add L17's drift preview, the Missed banner's streak line, Graduated / Slipping (L3) and
      Map done (L2).

24. **3d Tabs.**
    * Quote: "- The stat tiles stay above the tabs on every tab."
    * Add: "- Under the tabs, the changelog strip `Updated this morning · 3 changes ›` (L15)."

25. **3f DayPanel head.**
    * Quote: "  - Right-aligned mono: `45 min planned`."
    * Add: "  - The pill `Start today · 3 tasks · 45 min` (L8) and the chip row `Today I have: 10
      · 15 · 30 · 45 · 60 · 90 min` (L9). With `cfg.place`: `16:00 · the library`."

26. **3f Type tags.**
    * Quote: "  - **Title**, a **type tag** and one **detail line**. Type tags: `Mistakes`,
      `Rechecks`, `Focus`, `Test`, `Your own`, `Extra`."
    * Replace the tag list with: "`Warm-up`, `Mistakes`, `Learn it`, `Check`, `Habit`,
      `Pace`, `Map`, `Focus`, `Test`, `Checkpoint`, `Rehearsal`, `Sweep`, `Words`,
      `Homework`, `Your own`, `Extra` (L4)."

27. **3f Why this?**
    * Quote: "  - **`Why this?`** is a disclosure listing the server's `why` lines, e.g.:"
    * Replace with: "  - **`Why this?`** is a disclosure listing the server's `why` lines, value
      first, each a link to its evidence (L1, L10), e.g.:"

28. **3f TaskMenu.**
    * Quote: "    - `Again · new questions` (done tasks): starts 10 more on the same topics,
      tagged `:extra`."
    * Replace with L10's three Again actions. Add Skip's optional reasons and Mark done's
      "Did it elsewhere?" form (L10), and drag and long-press moves (L12).

29. **3f Still fixed?**
    * Quote: "  - **Still fixed?** (rechecks):" with its Detail and "    - Body: `{recheck:
      true, count, task}`."
    * Replace with: "  - **Warm-up** (kind `recheck`, T3): detail `3 check-ins due · 2 fading`;
      body `{source:'warmup', count:5, task:'<d>:recheck'}` (8 in Final)."

30. **3f Daily challenge** (decision 1).
    * Quote: "    - `10 questions, the same for everyone`, then `rank 14 of 203` once done."
    * Replace with: "    - `The same 10 question types for everyone, your own numbers`, then
      `rank 14 of 203` once done."

31. **3f Footer states.**
    * Quote: "  - All counted tasks done: `Day done ✓` with the quiet `Keep going · 10 more`
      (never runs out) and `Start tomorrow's focus set`."
    * Add: "The first time a day is done, T19's receipt shows above it (L8)."

32. **3f Eve.**
    * Quote: "- **Eve**: `Rest before the SAT`, plus the **Checklist** (checkboxes stored in
      localStorage per viewer):"
    * Add: "It stays a rest day with no counted task. Its one extra is `Read your trap sheet · 5
      min`, and the card shows the sweep count and the rehearsal result (L19)."

33. **3g WeekStrip header.**
    * Quote: "  - Right-aligned: `8 of 12 tasks · 67%`, with a bar."
    * Add: "  - `Goals 2/3` pips and `.quiet Review week` (L16). Beaten checkpoint days get ✓
      (L13)."

34. **3j Progress tab.**
    * Quote: "- Every chart has a visually hidden `<table>` with the same numbers."
    * Add before it: L18's cards (What your time bought, Why you lose points, Coverage, Checks,
      Weeks, Changes, Pace and calibration, CheckpointCard) and the changed DomainCard,
      SplitCard and StudyTimeChart. The tab reads `GET /api/plan/progress`.

35. **3k Plans rows.**
    * Quote: "  - mono `Built Sep 23 · Sep 23 → Nov 7 · target 700 · 45 days left · 31 tasks
      done · 80% of days`."
    * Add: "Finished and archived rows add the record line and the weekday strip, and expand to
      the changelog timeline (L20)."

36. **3l Calendar events.**
    * Quote: "    - One event per study day from today, at the preferred time, lasting its
      minutes: `SAT Math · 45 min · Circles, Percentages`, or `SAT Math · Module test`."
    * Replace with: "    - One event per study day from today, at the preferred time, lasting its
      minutes, titled from the day's tasks and the check-ins due (U18a): `SAT Math · 3 check-ins
      + Circles · 45 min`, with `LOCATION` from `cfg.place` and the link `/?next=1` in
      DESCRIPTION. Rehearsals at `cfg.rehearsal_at` (L19); registration deadlines (U17)."

37. **§4 Questions for m minutes.**
    * Quote: "**Questions for m minutes**: `clamp(round(m*60/95), 5, 120)`."
    * Replace with: "**Questions for m minutes**: `clamp(round((m − words_min) × 60 / s), 5,
      120)`, where `s` is the learner's median seconds per question over 60 days, clamped to
      60–150 (95 with no data), and `words_min` is `words.minutes_today()` when Words is on
      (L4)."

38. **§4 Difficulty.**
    * Quote the "**Difficulty** (the drill `difficulty` list):" heading and its table.
    * Replace with L5's rules: Build `zone:'stretch'` within the needed tiers, plus L2's pins;
      Sharpen `stretch` without easy above 580; Final Standard with v2's Final row and
      `adaptive:false`; Gate mode easy and medium.

39. **§4 Clock.**
    * Quote: "  - A skill whose median ms over its last 20 answers exceeds 120 s is timed in any
      phase." and "  - Timed means `timed: true, minutes: round(q*95/60)`."
    * Replace with: "  - In Build, a skill whose median over its last 20 answers is above 1.3×
      its P16 budget is timed." and "  - Timed means `timing: 'pace'` (the sum of the served
      budgets), with two passes on (L5)."

40. **§4 Domain shares.**
    * Quote the "**Domain shares**:" block (both bullets).
    * Replace with L1's allocation (`v_t`, `w_t`, the domain sum, and the §4 formula when gains
      is null).

41. **§4 Allocation.**
    * Quote: "- `alternatives` are the next two candidate sets under the same rules."
    * Add after it: L2's three guarantees (`tiers_by_topic` pins), Map mode, L1's Gate mode
      with `plan_days.gate` hysteresis, and L3's checks (at most 2 skills a week).

42. **§4 Tasks for a budget.**
    * Quote the "**Tasks for a practice budget of q questions**" list (items 1–7).
    * Replace with L4's table, budget, trim order and cause routing. Items 5–7 (custom, extras,
      why lines) stay.

43. **§4 Day status.**
    * Quote: "- `partial` when anything was done."
    * Add: "- A trimmed day (L9) below 60% of its base minutes is at best `partial`." Under
      `minutes_done`, add: "minutes marked done elsewhere on a generated task (L10)."

44. **§4 Behind.**
    * Quote: "- The banner's preview line comes from `POST /api/plan/preview` with that minutes
      value. Applying it is a `PATCH {minutes}`."
    * Add: "- `behind.fixes` also holds `ramp`, `weekday` (a weekday missed at least twice and
      on half its planned days in 28 days) and `date` (when not booked), each with its preview
      effect (L17)."

45. **§4 Week theme.**
    * Quote: "**Week theme**: the phase, the three topics with the most slots that week, the
      test day, and your own repeating tasks."
    * Add: "When U14 goals exist for the week, the theme leads with them. Gate mode leads with
      the route line (L1, L16)."

46. **§5 Other pages.**
    * Quote: "  - The first undone counted task is the main row with its pill; the other tasks
      are compact rows with status circles; your own tasks have checkboxes."
    * Add: "  - The card's primary is `Start today` (L8), with L9's chips."
    * Quote: "  - `Next in today's plan: Focus set · 18 questions` with `Start`."
    * Replace with: "  - With `cfg.run`: the day rail and the in-place interstitial (L8);
      otherwise `Next in today's plan: Focus set · 18 questions` with `Start`."
    * Quote: "  - When the sitting carries a `task`: `Back to plan`, plus the drift prompt if it
      applies."
    * Add: "  - With `cfg.run`: `Continue today · <next task>`. A checkpoint sitting shows the
      CheckpointCard (L14)."

47. **§6 States, new student.**
    * Quote: "  - Step 1 offers the diagnostic. Step 4 rows read `Not started`, with no
      suggestions."
    * Replace with: "  - Step 1 offers **Let the plan measure it** (default) or **I'll estimate**.
      Step 4 rows read `Not started`, with no suggestions. The first 5 practice days are Map days
      (L2)."
    * Add under Loading: "A second visit paints from `UI.cached` under `Updating…` (L12)."

48. **§3.6.4 Extras.**
    * Quote: "- **Focus that really changes time, with a live split bar**:"
    * Add at the end of the list: "- **L1–L20** (`spec/v2-upgrades/plan.md`): points decide the
      week; coverage; checks that move focus on; the rebuilt day; a plan in one tap; Start
      today; the changelog; checkpoint twins; the final phase; plans that remember."

49. **§3.6.5 Server changes.**
    * Quote: "- **New table plans**: plans(id TEXT PK, …"
    * Add columns: `plans.start_points JSON`; `plan_days.gate INTEGER DEFAULT 0`;
      `plan_overrides.trim INTEGER DEFAULT 0`; `plan_marks.minutes INTEGER`, `plan_marks.note
      TEXT`; `plan_tasks.type TEXT DEFAULT 'other'`, `plan_tasks.subject TEXT DEFAULT 'math'`;
      new table `plan_snapshots(plan, made_on, days JSON; PK(plan, made_on))` (L15).
    * cfg fields add: `current: null` with `measure`, `ramp {from}`, `place`, `checkpoints
      every|every2|off`, `baseline`, `rehearsal_at HH:MM`, `sections: ['math']`; `skills`
      entries `{state, by, since, pin?}`.
    * Quote: "- **GET /api/plan**: Freezes past days first. Returns {active, …"
    * Add fields: `proposal` (no active plan), `points`, `map`, `checks`, `focus_history`,
      `habits`, `changes`, `projection`, `verdict`, `workload`, `levers`, `rhythm`, `sweep`;
      Task adds `subject`, `why: [{text, href}]`, `result.fixed/opened/moved/to_strong`,
      `aim`; PlanSummary adds `record`.
    * Add endpoints: `GET /api/plan/progress` (L18); `GET /api/plan/day/{date}?minutes=` (L9);
      `PUT /api/plan/{id}/week/{monday}` (L16); `GET /api/plan/{id}/changes?before=` (L15);
      `GET /api/plan/{id}/trapsheet` (L19). `PUT …/day/{date}` accepts `trim`. `PATCH
      …/tasks/{task}` accepts `reason`, `minutes`, `where`. `POST …/tasks` accepts `type`.
    * Quote: "- **POST /api/drill: task, recheck, fmt, count cap for mistakes**: task (str up to
      40, matching ^\d{4}-\d{2}-\d{2}:(fix|recheck|focus|extra)$) is stored in cfg."
    * Replace the regex with
      `^\d{4}-\d{2}-\d{2}:(fix|recheck|focus|extra|learn|check|habit|pace|map|sweep|test)(:[a-z0-9_]+)?$`,
      and add the fields `run` and `tiers_by_topic` (§3.2).

50. **§3.6.7 Shared needs.** Add:
    * "`UI.weekPlanner(host, week)` (S7 plan-ui.js), hosted by U14's sheet (S1)."
    * "`plan.propose(learner, tz)`, read by Today's `Build with these` (S3)."
    * "The session day rail and interstitial when `cfg.run` is set (S4), and `Continue today`
      on the report (S6)."

51. **§3.6.8 Acceptance checks.**
    * Quote: "3. POST /api/plan/preview with that body gives split['Geometry and Trigonometry']
      > 0.15 …"
    * Append: "(For a new learner this holds through L1's fallback; L1's check 1 covers a
      seeded one.)"
    * Append L1–L20's acceptance lists as items 32 onward.

52. **§3.6.9 Open questions.**
    * Quote: "- Manual 'Mark done' on a generated task: proposed to count toward the day's
      status and minutes, but not toward question stats or mastery. Agree?"
    * Replace with: "- Resolved by L10: it counts toward the day's minutes and status, with the
      minutes and where recorded, never toward stats or mastery."
    * Quote: "- server/mail.py already sends signup verification. Should verified students get
      an optional daily email of today's tasks, beyond the calendar feed, or is that out of
      scope?"
    * Replace with: "- Out of scope: reminders are U18's titled calendar events and push (needs
      no SMTP)."
    * Add:
      * "Check thresholds (3 of 4 with less time; 11 of 12 medium/hard) and the 2-a-week cap are
        stated choices; revisit once check results exist."
      * "The 60% trimmed-day line and the 0.6 taper are stated choices."
      * "The rehearsal default 08:30 follows T13; with 'R&W first' the Math start is 09:45.
        Verify both against College Board's test-day timing."

### 3.2 Outside the section (Part 2 and sibling lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| §2.5 | `plans.start_points JSON`; `plan_days.gate INTEGER DEFAULT 0`; `plan_overrides.trim INTEGER DEFAULT 0`; `plan_marks.minutes INTEGER`, `plan_marks.note TEXT`; `plan_tasks.type TEXT DEFAULT 'other'`, `plan_tasks.subject TEXT DEFAULT 'math'`; new `plan_snapshots(plan, made_on, days JSON; PK(plan, made_on))`, written by S7. `progress.carry` moves `plan_snapshots` with plans | L1, L9, L10, L11, L15 |
| §2.6 | `task` regex: `^\d{4}-\d{2}-\d{2}:(fix\|recheck\|focus\|extra\|learn\|check\|habit\|pace\|map\|sweep\|test)(:[a-z0-9_]+)?$`. New fields: `run` (YYYY-MM-DD, stored and echoed only) and `tiers_by_topic` ({topic: [tier]}; the picker uses it for that topic in place of `tiers`). `rematch` (P18) accepts `task` and `timing` | L2, L3, L4, L8, L10 |
| §2.7 | `plan_auto_focus` bool, default true (Plan step 4, Settings); `plan_auto_drift` bool, default false (Plan, Settings). `words_from` default becomes `[sat, transitions]`, and `math` leaves its values (decision 2; Words owns the change) | L3, L7, L17 |
| §2.8 | Page scope `plan`: `J` `K` `↑` `↓` `Enter` `X` `S` `M` `U` `←` `→` `Shift+←` `Shift+→` `T` `1` `2` `3` `Shift+Enter` | L12 |
| §2.9 | S7 consumes F4 `estimate.gains`, `estimate.route`, `estimate.projection`, `progress.causes`, `progress.warmup_candidates`, `progress.pace`; F5 `habits` (U6); S3 `today.workload`, `today.receipt`; S9 `words.today_summary`, `words.minutes_today`; S2 `classes.due_soon` with due dates and `classes.resolve_drill`; S6 `GET /api/session/{id}/compare?with=`. S7 provides `plan.propose` → S3; `UI.weekPlanner` → S1; `run` and the day's tasks with answered/total → S4 | all |
| shell-me U14 | With an active plan, the sheet hosts S7's `UI.weekPlanner`, and its receipts add the plan's facts. Goal kind `pass_check {topic}` | L16 |
| shell-me U16 | A spare is spent on a missed study day only once the next study day ends with it still missed. A planned day that becomes `made_up` counts as a study day for the streak | L17 |
| shell-me U17 | `prefs.registered == exam_date` and the plan's `cfg.booked` are one fact; setting either sets both | L17 |
| shell-me U18 | Event LOCATION from `cfg.place`; rehearsal events at `cfg.rehearsal_at` | L7, L19 |
| today T2 | With a plan, a dated assignment appears once, as the plan's `assigned` task in the PLAN group, not again in ALSO DUE. `Do them in order` becomes `Start today` (L8) when a plan is active | L4, L8 |
| today T18 | `Build with these` reads `plan.propose` (L6): its own target and minutes rules are replaced by propose's. The card carries L9's chips | L6, L9 |
| today T13 | The rehearsal option "Bluebook R&W first" moves the Math start to 09:45 | L19 |
| practice P18 | `rematch` bodies may carry `task` and `timing:'pace'`; `scope:'misses'` is used by the plan's Again | L3, L10 |
| §3.3 S4 session | When `cfg.run` is set: the day rail and the in-place interstitial at each block's end; the run's last block ends on T19's receipt | L8 |
| §3.4 S5 | `POST /api/mock/new` twin accepts `task`; a per-sitting `pause:false` for rehearsals | L14, L19 |
| §3.5 S6 | The report footer's `Continue today`; the CheckpointCard when the sitting's task is a checkpoint; rehearsal lines (pace by quarter, the last 5 questions) | L8, L14, L19 |
| §3.8 Words | The Plan's Words task is kind `words` with `subject:'rw'` in the Plan's Task model; `words_from` defaults to SAT words and transitions | L4 |

---

## 4. Rejected

* **A second points model** (outcomes #1's lost questions per section, unfair-advantage #1's
  per-tier `expected_section`, experience #3's "90% on every tier"): U4's `estimate.gains` is
  the one source of points; `practice.md` and `today.md` rejected the same.
* **Minutes-to-points forecasts and levers** ("+15 min a day → 670–720", outcomes #10,
  experience #4, unfair-advantage #2), and the `plan_forecasts` table: there is no defensible
  model from minutes to points (`shell-me.md`, `today.md`). The levers are priced in pace and
  hours instead (L13).
* **Replacing the PaceTag with a forecast** (experience #4): the tag stays a labelled heuristic
  (open question 12), with the projection and made-vs-needed beside it.
* **The readiness grid with a required % per tier found by bisection** (unfair-advantage #5): a
  per-tier score model. The coverage grid (proven, shaky, untested) and P11's zones cover it.
* **An ~80-family misconception taxonomy file** (unfair-advantage #4): U6's 11 families are the
  one taxonomy; `practice.md` rejected authored tags.
* **A `skill_memory` table with its own intervals** (outcomes #2): T3's warm-up and P12's
  `type_memory` already schedule retrieval. A third schedule would disagree with them.
* **Per-skill pacing rungs stored per learner** (outcomes #7), and the 130 / 110 / 95 s speed
  ladder (unfair-advantage #11): P16's budgets, fluency and sprint plus U7's quadrants already
  are the pace rule. The plan schedules them (L4, L5).
* **A weekly error-review task with one tap per miss** (outcomes #5): P8 records the cause at
  answer time. The week review and Progress show causes with their fixes (L16, L18).
* **A confidence tap required on plan sets** (outcomes #9): `shell-me.md` and `today.md`
  rejected it. P7's optional chips feed Fix's order (L4).
* **A 12-question inline placement with its own band and a `placement` sitting kind**
  (experience #11, the unfair-advantage step-1 gap): a new score source with a new band rule.
  The diagnostic as day 1's task, plus Map days, measures without a new estimate (L7, L2).
* **Raising the Focus cap to 3 domains with visible dilution** (experience step-4 gap): with 4
  Math domains, 3 on Focus is everything but one. The points panel and the SplitBar already
  show where the time goes.
* **Swipe right or left on task rows** (experience #8): it fights vertical scroll and the
  system back swipe. The long-press sheet, the ⋯ menu and the keys cover it.
* **`[` and `]` for weeks** (experience #8): `[` is the global sidebar key. `Shift+←` / `→`
  are used instead.
* **"How you study best": accuracy by time of day and by minutes into a session, and split
  days** (experience #14, the unfair-advantage preferred-time gap): our own day order (warm-up
  and fixes first, harder focus sets later) confounds both. T17's median start time already
  suggests the usual time.
* **Email reminders through mail.py, the 10-minute nudge at the preferred time + 3 h, and a
  parent Sunday digest** (outcomes #4, the experience reminders gap): these need SMTP (open
  question 5). U18's titled events and push, T19's streak-at-risk line, and the 10-minute chip
  (L9) cover them. `shell-me.md` rejected the parent email.
* **A plan-adherence column in the teacher's class view** (experience #13, unfair-advantage
  #12): minors and consent (open question 6). The homework task lands in the plan without it.
* **A printable week of worksheets with codes and answer entry** (unfair-advantage #9):
  `shell-me.md` and `practice.md` rejected per-student packs and QR entry. Practice's worksheet
  prints any set, and the trap sheet is kept (L19).
* **A `plan_weeks` table and `plan.propose_goals`** (unfair-advantage #8): U14's `week_goals`
  holds the goals, and `plan_overrides` holds the week's days.
* **A `plan_checks` table** (outcomes #3): the before is a tagged session, and the after is P18's
  rematch of it.
* **Drift that prefers checkpoints, and two beaten checkpoints bringing the target prompt
  forward** (unfair-advantage #3, experience #4): R16's mean3 stays the one drift rule. The
  checkpoint series shows as evidence.
* **An "Exam-ready 7 of 19" tile with its own spaced-check rule** (outcomes tile gap): a third
  readiness measure next to U8 and coverage. The coverage counts say it.
* **A per-task "worth ~+6 pts", and the counterfactual "close these 2 traps and Circles leaves
  tomorrow's set"** (unfair-advantage Why gap): no defensible split of a skill's gain across
  tasks, and the re-deal is not a one-skill rule. The skill's ≈ gain and the changelog say what
  is true.
* **A separate `GET /api/plan/{id}/quick` set that counts as partial** (unfair-advantage #7):
  L9's trim does it inside the plan's own rules, with no second path.
* **Server-side chaining of the day's blocks** (experience #1's F5 option): the client chains
  from the existing `plan.next`; `run` is only echoed.
* **Collapsing BankStats and HowItWorks for students with data** (the experience landing gap):
  decision 4. They move below the ready plan instead.
* **A 2 h 20 min full-SAT rehearsal event by default** (outcomes #11): `today.md` rejected it.
  "R&W first" is the student's own Bluebook task, by choice (L19).
* **Gain per study hour as a forecast** (outcomes Plans gap): kept only as the record of a
  finished plan (L20).
