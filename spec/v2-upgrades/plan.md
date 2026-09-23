# v2 upgrades: Study plan

Written 2026-09-23 for `spec/rebuild-v2.md` §3.6 (lines 7046–8096). It merges three designers'
proposals (outcomes, experience, unfair advantage) into one build-ready list, L1–L21, against
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
* **Names.** Upgrades are L1–L21 (L for the Plan key, `G L`). Builders are Part 4's tasks. S7
  owns `web/plan/**`, `server/plan.py`, `server/api_plan.py`, `web/assets/plan-ui.js`,
  `server/checks/s7.py`; every other file is met through §2.9.
* **No classes** (decision 5). The plan has no homework, assignment, class or teacher element,
  and reads nothing from classes.
* **Subject-aware** (decision 3). Built keyed by subject now, so adding the R&W bank later adds
  keys and consumers never change shape:
  * Every task carries `subject` (`math`; `rw` for Words and R&W tasks, L21).
  * Every per-section payload is a map keyed by subject: `points: {math: {…}}`, `coverage:
    {math: {…}}`, `score: {math, rw?, total?}`, `projection: {math}`, `verdict: {math}`,
    `pace: {math}`, `route` inside `points.math`. List payloads (`checks`, `checkpoints`,
    `causes`) carry `subject` on every item.
  * `cfg.sections: {math: {current, target, focus, skills}, rw?: {current, target, focus,
    minutes}}` is the store. `PlanIn` still accepts top-level `current`, `target`, `focus` and
    `skills` as aliases of `sections.math` (so v2's acceptance bodies pass), and the top level is
    written back only for the `learners` mirror (profile target).
  * Focus caps are per subject: `math` 2 domains and 6 skills, `rw` 2 of its 4 domains. A 422
    names the subject (`rw: 2 focus areas at most`). Domains are validated against that
    subject's list, so an unknown or other-subject domain is a 422.
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
| 2 | Landing stat cards | 10 tests · 6,933 questions · 1,002 words | ∞ sections · 386 types / 19 skills · one real named mistake | Adds a **Your numbers** row above: ≈ points on the table with the top 3 skills, the route check, open mistakes by name (L1). BankStats gains a fourth tile, **Words**: the SAT words and transitions counts with spaced review (L21) | v2 better (a real mistake) but still about the bank, and it dropped their vocabulary stat. **L1 + L21 → WAY BETTER.** The first numbers are about the student's score, and nothing of theirs is missing. |
| 3 | How it works | 3 numbered cards | 3 tiles that describe real behaviour | The example day's first question is answerable in place, served by the preview's token and filed to a one-question session. A new student on the measure path sees their real day 1 (the diagnostic, then Map) (L6) | v2 PARITY in form. **L6 → WAY BETTER.** A new student meets a named mistake before committing, on the day they will really get. |
| 4 | Plans list on the landing | List; empty state | Same component as the Plans tab, collapsed to 5 | Every plan listed (paged by 20 only past 20 rows); each finished plan shows what it achieved, what worked and its last changes (L20) | v2 PARITY, and below it once collapsed. **L20 → WAY BETTER.** |
| 5 | Plan quota | 1 per billing cycle; failed plans hidden | Free, unlimited | Same | **WAY BETTER already.** |
| 6 | Dashboard plan CTA (no plan) | "Build Your Adaptive DSAT Study Plan", 3 bullets, Build My Plan | Today's `Build with these` (T18) | `Build with these` and the landing read one `plan.propose` (L6) | **WAY BETTER** (T18 + L6): one rule, one tap, both places. |
| 7 | Wizard header, Exit setup | Title, "draft saves as you go", Exit setup pill | Same, Exit keeps the draft | `⌘/Ctrl Enter` creates from any step once a date is set; later steps take defaults (L6) | v2 PARITY. **L6 → WAY BETTER.** |
| 8 | Stepper | Four cards, no forward jump | Forward once valid, red dot for a server error | A live plan beside every step (L6) | **WAY BETTER.** The student watches the plan change instead of reading a summary. |
| 9 | Draft autosave | Resets on a failed build | Server draft + local fallback, never reset | Same | **WAY BETTER already.** |
| 10 | Step 1: where you are | Two sliders, "best estimate", prefilled when tests exist | Math slider + number, SourceNote, optional R&W number, a link out to the diagnostic | The last 3 sittings drawn as bands with their mean; a new student picks **Let the plan measure it**: the diagnostic is day 1's first task and week 1 a Map week (L7, L2). R&W is a slider + number beside Math, prefilled from Bluebook, with the Total (L21) | v2 PARITY for a new student (a guess, or a trip out), and below theirs on R&W (a hidden optional field). **L7 + L2 + L21 → WAY BETTER.** The plan starts on evidence for both sections and nobody leaves the wizard. |
| 11 | Step 2: target, NOW → TARGET | Target sliders, +400 card, range bar, screen-reader line | GainCard, TargetNote (88% of points, 14 of 22, the 780 cap); an R&W target field only once R&W is filled | "700 is about 88% of the section's points · the points you're most likely missing are in Circles, Probability, Nonlinear functions", and the route check from the student's own first tries (L1, L7). R&W target slider + number and `Total 1060 → 1350` on a 400–1600 track (L21) | v2 better (honest) on Math, below on R&W. **L1 + L21 → WAY BETTER.** The target names skills and a route, and the total is always in view. No question count that contradicts the points line. |
| 12 | Step 2: exam date and pace | Free calendar; "about 60 points per week", never judged | Official-date chips with pace, PaceTag, later-date suggestion | `UI.examDate` rows: study days, pace and tag, register-by, projected score, Recommended; "you make +9 a week; this date needs +22" (L7) | **WAY BETTER.** A date chosen against the student's own rate and deadlines. |
| 13 | Step 3: daily time | 30m–4h chips | 15m–4h, 2.5h added, per-day minutes | The student's real rhythm beside the chips, an overreach warning, and **Ramp** (L7) | v2 PARITY: a number the student guesses. **L7 → WAY BETTER.** The plan starts at what the student really does and grows. |
| 14 | Step 3: days a week, STUDY/REST tiles | Slider, tiles, study/rest counts | Same, plus a minutes select per tile and days off | Each tile shows "studied 3 of last 4 · ~35m" (L7) | **WAY BETTER.** |
| 15 | "Solve a practice exam every day" | Toggle, locked below 150 min | None / Weekly / Twice / Every study day; module or section; test day | Checkpoints: every second test is a twin of one of two alternating baselines, with each slot marked when its type was practised in between (L14); a warning when tests take over 30% of the time (L7) | v2 PARITY: a frequency. **L14 → WAY BETTER.** Two tests in the plan are finally comparable, slot by slot, and the card says how much was rehearsal. |
| 16 | Step 4: focus areas | 8 domains (4 R&W + 4 Math), Focus / Normal / Strong, 4 cap, tints | 4 Math domains + 19 skills (behind chevrons), caps 2 / 6, suggestions, live SplitBar | **Where your points are** panel, ≈ points on every row, suggestions by points per minute, a points bar under the split, coverage per domain, Auto focus, SkillRows always open (L1, L2, L3, L7). The 4 R&W domains with Focus / Normal / Strong, each Focus changing Words and the day's R&W tasks (L21) | v2 PARITY in kind, below on R&W (none). **L1 + L3 + L21 → WAY BETTER.** |
| 17 | Include vocabulary practice | Toggle; Vocabulary and Flashcards tasks | Extras (rechecks, QOTD, challenge) called the equivalent; no words task in the Task model | A Words row in step 4 (SAT words + transitions, decision 2) and a counted **Words** task inside the day's minutes, counted as R&W time (L4) | v2 BELOW. **L4 → WAY BETTER.** Spaced EBRW words sized to the real due queue. |
| 18 | Plan at a glance | A text summary that rounds up | GlancePanel rows from preview; a bottom sheet on phones | Plus the **live plan**: compact month, week 1, day 1's rows, inline on every step at every width (L6) | **WAY BETTER.** |
| 19 | Build screen, error card | Fake one-minute progress; FAILED in 0.3 s; draft reset | Synchronous create, no build screen | Create lands with keyboard focus on **Start today** (L6, L8) | **WAY BETTER already.** |
| 20 | Plan adaptation (`regenerate`, `adapt`; weakAreas fixed at build) | AI regeneration behind a paid quota; focus never moves by itself | Daily re-deal, drift, behind | Focus moves on when a skill passes a before/after check (L3); a changelog says what changed this morning and why (L15) | v2 PARITY in what the student sees. **L3 + L15 → WAY BETTER.** Adaptivity the student can check. |
| 21 | Page tabs | Plan · Progress · History | Plan · Progress · Plans | Plus the changelog lines, always open, under the tabs, each with its cause (L15) | **WAY BETTER.** |
| 22 | Four stat tiles | Days to exam, Streak, Plan complete %, Score gap "1000 now, 1400 target" | Days, Score with status chip (Math only), Plan done, This week with streak | Days adds capacity against need; Score adds the projection, made vs needed a week, the route and ≈ points claimed, and `Total 1060 → 1350` with R&W set; Plan done reads against the schedule; Week carries goals; each tile opens its detail (L13, L16, L21) | v2 PARITY, below on the total. **L13 + L21 → WAY BETTER.** Four tiles that say whether the plan is working, for the whole score. |
| 23 | Today card on the plan page | "N of M done · X min left · Y min planned", empty states | DayPanel progress line and footer states | **Start today** runs the day in one go and ends in a receipt; **Today I have** trims the day by value (L8, L9) | v2 PARITY. **L8 + L9 → WAY BETTER.** 1 tap plus Enter between blocks, against their ~12 taps. |
| 24 | Task types | Practice test, Question set, Vocabulary, Reading, Practice game, Flashcards, Custom | Fix, Rechecks, Focus, Test, Your own, Extra | Warm-up, Fix, Learn it, Before/After check, Habit, Pace, Focus, Map, Test / Checkpoint / Rehearsal, Sweep, Words, R&W by domain, Your own, Extras (L4, L21) | v2 PARITY: a set, a test, your own. **L4 + L21 → WAY BETTER.** Each kind is a different teaching move with a reason. |
| 25 | "Why this task?" | AI `aiReason`, "Hide AI rationale" | Fact lines the scheduler used, behind a `Why this?` disclosure | Value first (≈ +15), always shown under the detail line, every line linking to its evidence (L10) | v2 better (facts), below in reach (a disclosure). **L10 → WAY BETTER.** Always visible and checkable in one tap. |
| 26 | Task actions | Skip, Mark done and launch as visible buttons; ✓ Done, Practice again, Undo; a checkbox on every week row | Skip/Undo, Mark done, Move, Swap, Make it a section, Again, all inside the ⋯ menu; checkboxes on own tasks only | Skip and Mark done are visible buttons beside Start on every row; the status circle is a real checkbox on every task; done rows show Again · the N you missed, Again · 10 more and Undo as buttons. Skip asks why and acts on it; Mark done logs minutes done elsewhere; every done row reports what it fixed (L10) | v2 BELOW (one-tap actions hidden in a menu). **L10 → WAY BETTER.** Every action theirs shows is in view, and each one teaches the plan something. |
| 27 | Custom tasks | CUSTOM with Mark done | Own tasks with repeat rules | Typed own tasks: a Bluebook test asks for the scores and misses, which feed the trajectory and tomorrow's Fix (L11) | v2 PARITY. **L11 → WAY BETTER.** A ticked official test teaches the plan something. |
| 28 | Week view | Week N, X of Y · %, AI theme, pager, day tiles | Same, plus server theme, kinds, minutes, bars | Week goals in the header with a live result, Review week, and next week shaped in one sheet (L16) | v2 PARITY. **L16 → WAY BETTER.** |
| 29 | Selected day, empty day | Header; "Nothing scheduled" | DayPanel for any past or future day | Plus each day is a drop target showing its new load (L12) | **WAY BETTER.** |
| 30 | Rescheduling | Move to a later day of the same week only | Any study day to the eve, swap, day off, change a day | One drag or two keys, with the target day's new load shown before the drop (L12) | **WAY BETTER already**; L12 makes it fast. |
| 31 | Behind banner | ≥ 4 tasks and < 60% done in 7 days; Rebalance my plan | Real average minutes, Fit to 25 min with a preview | What it cost, **Catch up · 15 min**, the weekday pattern, Ramp and a later date, each previewed in hours and pace (L17) | v2 PARITY: one fix. **L17 → WAY BETTER.** |
| 32 | Score drift banner | Upward only, ≥ 60, snoozed 3 h | mean3 ± 40 both ways, target reached, remembered on the server | Evidence chips, what moved, the effect before applying, optional auto-apply (L17) | v2 PARITY. **L17 → WAY BETTER.** |
| 33 | Progress: accuracy by domain | Bars, weakest first, RW/MATH legend | DomainCard (Math only), 19-skill table behind an expander | By points by default, points claimed since the start, the 19 × 3 coverage map, what the time bought, the 19-skill table open (L1, L2, L18); an R&W section from Bluebook and logged misses with a Math · R&W legend (L21) | v2 PARITY, below on R&W. **L18 + L21 → WAY BETTER.** It ranks by value, shows what is paying, and covers both sections. |
| 34 | Progress: study time per day | Studied vs planned | Bars, tests hatched, range, tooltip | First-try accuracy line; a bar opens its day (L18) | v2 PARITY. **L18 → WAY BETTER.** |
| 35 | Progress: how the plan splits time | Planned minutes by task type | Planned and done by task type | Plus by domain against where the points are (L18) | v2 PARITY. **L18 → WAY BETTER.** A misallocation shows at a glance. |
| 36 | History tab | List, make active, older-plan banner | Plans tab, plus duplicate and remove | A record of what worked, the last changes inline from a stored event log, and the next plan seeded from it (L20, L15) | v2 PARITY. **L20 → WAY BETTER.** |
| 37 | Toasts | Generic | With Undo where one exists | Every automatic change also toasts with Undo (L3, L15) | **WAY BETTER already.** |
| 38 | Dashboard card with a plan | Today's Plan, N of M, min left, Full Plan, checkboxes | Today's plan card (T2, T18) | Start today and Today I have there too (L8, L9) | **WAY BETTER** (T2, T18, L8). |
| 39 | Profile study goals | Target unsynced, countdown, Daily 2 h / Weekly 12 h, preferred time unused | One value across Me, Today and Plan; preferred time → calendar | A **Where** beside the time (an implementation intention) in every event; registration deadlines (L7, L17, U17) | **WAY BETTER.** |
| 40 | Dashboard countdown, study-time calendar | DD:HH:MM:SS ticker; calendar marked in UTC | Local-time month grid; Today's capacity line (T12) | The Days tile states capacity against the work left (L13) | **WAY BETTER.** |
| 41 | Classes and homework | Hidden `/my-classes`, a second to-do list | Today lists assignments | **Not built** (decision 5: classes live on a separate platform). The plan has no homework or assignment task | Out of scope by decision 5. |
| 42 | The last weeks | Nothing changes; "Exam day has arrived" | Final phase: full sections and open mistakes; the eve and a checklist; an exam-week test inside the taper | Dress rehearsals at the real hour replace Final's weekly tests, the sweep with a still-fixed scoreboard, a taper with no test on it, and a personal trap sheet for the eve (L19) | v2 PARITY in effect. **L19 → WAY BETTER.** |
| 43 | Both sections in one plan | R&W and Math sliders, 4 R&W domains, Reading and Vocabulary tasks, a total-score tile, RW/MATH accuracy | Math plan; R&W as an optional number and a free-text own task | R&W current and target sliders, the 4 R&W domains with Focus / Normal / Strong, typed R&W tasks per focus domain, Words steered by the R&W focus, R&W misses logged per domain from Bluebook, and the Total in the title, Score tile, drift and Plans rows (L21) | v2 BELOW (half a plan). **L21 → WAY BETTER.** Their R&W is sliders and a label; ours is fed by the student's Bluebook misses and the spaced Words queue. |

---

## 2. Accepted upgrades

Each gives why, screens and components, controls and states, data and endpoints, how it uses
the rest of the site, and acceptance checks. Learner codes start `a:v2revplan`; `:8027` is
S7's port. Every figure that comes from a model says "about" or "≈".

### Layout after these upgrades

**Plan tab, desktop (≥1080px)**, under the title row and the 4 stat tiles:
```
banners ×12
tabs ×12 (sticky)  ·  changelog lines under them, always open (L15)
day ×7.5  (DayPanel: head with Start today and Today I have, progress, rows, footer)
          | side ×4.5 (ComingUp · Map progress (Map days) · Your habits · Sweep (Final))
week ×7.5 (WeekStrip with goals)
phase ×12
month ×12
```
**Phone (<760px)**: title, tiles (Days full width, then a 3-up row), banners, tabs, changelog
lines, DayPanel, WeekStrip, ComingUp, Map, habits, sweep, phase, month. A **thumb bar** sits
above the tab bar on `/plan/`: `Next · Fix mistakes · 8 q · Start` (L8). Nothing is folded away
(decision 4): why lines, row actions, the changelog, SkillRows, the 19-skill table and every
plan in the Plans list render open, and only the ⋯ menu and the Move sheet are overlays.

**Progress tab**, desktop 2 columns:
```
checkpoint ×12 (when one exists)
progress ×6   | trajectory ×6
bought ×12    (What your time bought)
causes ×6     | coverage ×6
domains ×6    | split ×6      (domains: Math rows, then the R&W section, L21)
skills ×12    (All 19 skills, open)
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
* Value per minute, for a skill with `gain_t ≥ 5`: `v_t = gain_t / max(minutes_t, 10)`. The
  10-minute floor stops a nearly-done skill from looking infinitely cheap.
* Every other skill (gain under 5, including mastered ones at 0) gets a fixed floor value
  `v_t = 0.1 × median(v over the gain ≥ 5 skills)`, only so it stays in the deal. It can never
  outrank a skill with real points: a skill at +20 needing 90 minutes (v ≈ 0.22) always outweighs
  a skill at 0.
* With no skill at gain ≥ 5, §4's formula applies (as with gains null).
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
* **Precedence over coverage (L2) and difficulty (L5).** While gated, hard is not a needed
  tier: L2 counts hard as needed only when `target > 580` and the gate is off, so no focus
  body's `tiers` and no `pins` segment carries hard. (Fix still serves the student's own hard
  traps, after the easy and medium ones.) The coverage card's hard column and step 4's
  coverage line read `Hard tiers wait until your first modules reach 60%`.
* When the gate turns off, the hard cells become needed and their pins go into the remaining
  Sharpen days first (L2's order). If Sharpen is too short to place them, the rest ride as
  2-question hard segments in Final's focus sets.
* Final is unchanged: the rehearsals need every tier.

**Screens.**
* **Step 4 › Where your points are** (a panel above the DomainRows): the top 6 skills by
  `v_t`, each a `UI.skillRow` (U4's row):
  * `Nonlinear functions · ≈ +20 · about 6 of 44 questions · 58% right · 3 open mistakes · 6
    more right to Strong · ~9 min` (`per_test`, `accuracy`, `to_strong`, `minutes`);
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

**Data.** `GET /api/plan` adds `points: {math: {total, top3, claimed, skills: [{topic, gain,
per_test, accuracy, to_strong, minutes, v, floor}], route: {m1, route, margin, gate}} | null}`
(`floor: true` marks a floor-valued skill). `POST /api/plan/preview` adds `points` and
`split_points: {math: {domain: share}}`.

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

#### L2. Coverage: every skill and every tier the target needs, planned and proven

*From: experience #10, outcomes #8 (Map week), unfair-advantage #5 (reworked), the
unfair-advantage difficulty gap. Effort M. Builders: S7 (allocator guarantees, Map mode, card),
F5 (`pins`), U5's probe (exists).*

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
  hard questions) and Gate mode is off (L1's precedence).

**Pins.** A pin is a 2-question segment for one cell, riding inside that day's focus set: the
drill field `pins: [{topic, tier, count}]` makes the picker serve `count` items of that topic at
that tier inside the set's `count`, whether or not the topic is in `topics`; the rest of the set
follows `topics` and its difficulty. A pin never takes a slot, so L1's points allocation and the
student's Focus keep every slot.

**Allocator guarantees** (plan.py, each with an assert in `__main__`):
1. Every skill gets at least one focus slot in every `W` days, where `W = max(14, ceil(19 ÷
   slots per week) × 7)` and slots per week is the sum of v2's slots (3 / 2 / 1 by focus
   questions) over the plan's practice days in a week. Strong skills proven on every needed tier
   are exempt (the warm-up keeps those). A 45-minute, 5-day plan has `W = 14`; a 15-minute,
   2-day plan with 1 slot a day has `W = 70`, and the coverage card says so (`Every skill at
   least once in 70 days at this time`).
2. Needed untested or shaky cells get pins, at most 1 a practice day and at most 30% of the
   pre-Final slots in total. Pins are ordered by the skill's gain (L1; with gains null, untested
   before shaky, then by the blueprint weight), and a cell counts as **planned** once it has 2
   pins before Final. Cells that cannot get 2 are **not planned before Final**, counted in the
   coverage header and marked on their cell, never silently dropped.
3. In Build, an untested needed cell takes priority over a shaky one for its skill's pin.

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
* Header: `Proven 31 of 57 · shaky 14 · untested 12 · 9 not planned before Final`, and the line
  `Every skill at least once in 14 days` (guarantee 1's `W`). While gated: `Hard tiers wait
  until your first modules reach 60%`.
* 19 rows under 4 domain headers, 3 cells each, with glyph and text for the state (never colour
  alone), a `needed` tick, and the next planned pin date in mono (`Oct 14`), or `not planned
  before Final`, or `—` when not needed.
* A cell opens a 5-question drill: `Try hard Circles now` → `{topics:['circles'], tiers:['hard'],
  count:5, source:'plan'}`.
* `role=grid`, arrow keys, a hidden table.
* Step 4's DomainRow shows its line: `Algebra · 9 of 15 proven`.

**Data.** `GET /api/plan/progress.coverage = {math: {cells: [{topic, tier, state, right, n,
needed, next, planned}], counts: {proven, shaky, untested, unplanned}, window_days}}`, computed
from attempts. `GET /api/plan.map = {on, measured, of: 19, done_at} | null`.

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

**Rules.** A 4-question sitting is noise on its own (a student with a true 55% scores 3/4 about
39% of the time), so no verdict rests on one sitting.
* **Passed**, one of two ways:
  * **with a check**: the After at 3/4 or better, in no more total time than the Before, **and**
    at least 9 of the skill's last 12 clean first tries at medium or hard right (the After's
    included). A true-55% student passes about 5% of the time, against 39% on 3/4 alone;
  * **without one**: 11 of the last 12 clean first tries at medium or hard right and no open
    trap.
  * Either way the skill leaves Focus for Strong (`by: 'auto'`), and the next skill by `v_t`
    (L1), not on Focus and not Strong, takes its place (`by: 'auto'`), within the caps.
* **Again**: the After at 3/4 without the 9 of 12 (`Again · 3/4 today, 7 of your last 12 · one
  more week`), or at 2/4. It stays on Focus; 2/4 also adds a Learn it task (L4) on the next
  practice day.
* **Learn first**: 1/4 or less keeps it, with Learn it before the next focus set.
* **Keep-warm**: every Strong skill with `by: 'auto'` gets a 2-question segment a week at medium
  or hard (L2's `pins` with `why: 'keep'`, outside the 30% pin cap), so its last 12 answers keep
  arriving. The warm-up (T3) serves its check-ins as usual.
* **Slipping**: a Strong skill (set by the student or by auto) at 7 or fewer of its last 12
  clean first tries, or with both keep-warm items of a week missed, goes to Normal for 7 days.
  Why line: `Circles is slipping · 7 of 12 · back to Normal until Oct 9`.

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
* `GET /api/plan.checks = [{subject, topic, week, before:{sid, right, of, ms}, after:{sid,
  right, of, ms}|null, recent: {right, of: 12}, result: 'passed'|'again'|'learn'|null}]` and
  `focus_history: [{subject, topic, state, from, to, why}]`. Both are found from sessions tagged
  `:check:<topic>` and `cfg.rematch_of`, so there is no new table.

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

#### L4. The day, rebuilt: warm-up first, then the teaching move each skill needs

*From: outcomes #2, #5, #6, #9, unfair-advantage #4, #10, #11, the Words gaps of all three.
Effort M. Builders: S7 (kinds, budget, order), S9 (Words task), T3 / T4 / T8 / U6 bodies
(exist).*

**Why.** Theirs has one move, "a question set". A student who fails ten cold questions on a
new skill needed a worked example; one who knows it slowly needs the clock; one habit across
skills needs one drill, not eleven. And a plan that ignores vocabulary is lying about the
minutes in the day.

**Order and bodies for a practice day** (replaces §4 "Tasks for a practice budget"):

| # | kind | when | row (example) | body |
|---|---|---|---|---|
| 1 | `test` | a test day (checkpoint L14, rehearsal L19) | `Module test · 22 q · 35 min` | §4 / L14 / L19 |
| 2 | `recheck`, shown as **Warm-up** | anything due in `progress.warmup_candidates` (T3) | `Warm-up · 5 questions · ~6 min · 3 check-ins due · 2 fading` | `{source:'warmup', count, task:'<d>:recheck'}`, count from the fill (up to 5; up to 8 in Final) |
| 3 | `fix` | open traps | `Fix mistakes · 8 q · "used the diameter as the radius" +5` | v2's count rule; ids ordered: confident misses first (P7 `conf='sure'`, T9 blind spots), then U4 gain × hits; Gate mode puts easy and medium first |
| 4 | `learn` | a Focus skill with fewer than 5 answers or mastery under 0.35 (Build); an After at 2/4 or less (L3); a skip "Too hard" (L10); 2+ `stuck` misses (P8) in 14 days; T7's `top_gap_topic` | `Learn it · Circles · a worked example + 3 · ~6 min` | T4: `{source:'learn', topics:[t], example:true, count:3, task:'<d>:learn'}` |
| 5 | `check` | L3 | `Before · Circles · 4 questions` | L3 |
| 6 | `habit` | once a week (the second practice day), when one habit is 25%+ of the last 20 misses (U1 row 6) | `Habit · answered a different quantity · 8 across 5 skills` | U6: `{source:'habit', habit, count:8, task:'<d>:habit'}` |
| 7 | `pace` | a Focus skill in U7's slow-and-right quadrant, from Sharpen on (or any phase when its median is over 1.3× its budget), at most 2 a week; or fast-and-wrong ("rushing") | `Speed drill · Systems · 8 in 12:40` or `Careful set · Percentages · 8` | T8: `{topics:[t], count:8, timing:'pace', source:'pace', task:'<d>:pace:<t>'}`; careful: `timing:'off'` |
| 8 | `map` / `focus` | the rest of the budget, at least 3 (the fill below; Map days: L2) | `Focus set · Circles, Percentages · 18 q · 28 min` | §4 plus L1 / L2 / L5 fields |
| 9 | `sweep` | Final (L19) | `Sweep · 9 of 44 old mistakes · new numbers` | L19 |
| 10 | `words` | `prefs.words_goal > 0`, or anything due | `Words · 12 due · 5 new · ~6 min` | S9's today run: `{mode:'mix', deck:{source:'today'}, box: w, run?, task:'<d>:words'}`; `Review cards`, `Learn 5`, `Quiz` beside it |
| 11 | `custom` (typed own tasks, L11; R&W tasks, L21), then extras `qotd`, `challenge` | as v2 | as v2 | as v2 |

**The day's budget** (replaces §4 "Questions for m minutes" and v2's 60% rule). One rule builds
every day, the base day and every Today I have chip (L9) alike, so no day runs longer than its
minutes.
* **Inputs.** `m` = the day's minutes (after ramp, taper and overrides). `s` = the learner's
  median seconds per question over 60 days, clamped to 60–150 (95 with no data). Own tasks
  (L11, L21) keep their minutes while at least 10 minutes are left for the rest; otherwise the
  longest is marked `skip today` (a repeating one) or `moved to <next study day>` (a one-off),
  one at a time, in the preview and the row. `g` = `m` − own minutes kept.
* **Test first.** On a test day the test takes 35 minutes (module) or 70 (section) off `g`.
  With `g` under 70 a section becomes a module (as v2). With `g` under 35 the test moves to the
  next study day with at least 35 minutes that is not the eve or a taper day, and the day's row
  and the L9 preview say `Module test moves to Thu · it needs 35 min`. With no such day that
  week, the week's test is dropped with the line `No day left this week with 35 min`.
* **Words.** `w = min(words.minutes_today(), max(3, round(0.2 × g)))` when Words is on and
  anything is due or new, else 0. The run's `box` is `w`, and the Words run order (Fix cards,
  due, proofs, …, new last) makes a short box due-first by itself: `Words · 12 due · 3 min ·
  due first`.
* **Questions.** `q = min(120, floor((g − w) × 60 / s))`. Floored, never rounded up, and with no
  minimum of 5: a day holds only what fits.
* **Fill.** A focus reserve `r = ceil(0.4 q)` when `q ≥ 20` (`ceil(0.3 q)` in Final), else 0.
  Then each kind that applies that day (the table's `when` column) takes `min(target, left)`,
  in this priority order, and is cut when that is under its minimum (the rows still show in
  the table's order above):

  | kind | target | minimum |
  |---|---|---|
  | warm-up | `min(5, max(2, ceil(0.4 q)))`; Final `min(8, max(2, ceil(0.3 q)))` | 2 |
  | fix | v2's count rule | 4 |
  | check | 4 | 4 (whole) |
  | learn | 4 (the example + 3) | 4 (whole) |
  | sweep | `ceil(to go ÷ Final days left)` | 3 |
  | habit | 8 | 8 (whole) |
  | pace | 8 | 8 (whole) |
  | focus / map | `r` + whatever is left | 3 |

  A focus remainder under 3 goes back to the warm-up (up to 5, or 8 in Final), then to the fix,
  and is otherwise left unspent.
* **Where a cut kind goes**: fix → its traps stay open, first in the next day's Fix; check → the
  next practice day that deals the skill; learn, habit, pace → the next practice day; sweep →
  its count re-spreads over the remaining Final days; focus → its topics keep their deficit
  (§4), so the re-deal brings them back sooner.
* **Worked figures at `s = 95` with Words on**: 10 min → Words 3 + warm-up 4 (9.3 min); 15 min
  → Words 3 + warm-up 3 + fix 4 (14.1 min); 45 min with check-ins due and 6 open traps → Words
  9, warm-up 5, fix 8, focus 9 (43.8 min). At `s = 150`, 10 min → Words 3 + warm-up 2 (8 min).
* **Minutes shown** on every row are count × `s`, the same rule as U1 and T2, so the plan and
  Today agree; the budget adds exact seconds, and the rows round for display.
* **Cause routing** (T7's `progress.causes` over 14 days picks what gets scheduled):

  | cause | the plan adds |
  |---|---|
  | trap | Fix (and Habit when a family is 40%+ of the traps) |
  | slip | focus sets for that skill carry `feedback:'instant'`, and P8's "re-check the last step" line stays on |
  | clock | a Pace task |
  | entry | the day's focus set gets `spr_share: 0.5` (as v2's format tilt) |
  | gap | Learn it on `top_gap_topic` |

  Each is named in the task's Why (`3 of your last 10 misses were slips`).
* **Words** (decision 2: SAT words and transitions only). The row's primary is `Start` (S9's
  today run with `box: w`); `Review cards`, `Learn 5` and `Quiz` stay beside it. It completes
  itself from `words.today_summary().done`, or when its box run finishes. It carries
  `subject:'rw'`, and its minutes count as R&W time in stats, the week theme and the split.
  L21's R&W focus steers its mix.
* **Side card "Your habits"** (Plan tab, under ComingUp): U6's top 3 with the tell and
  `Drill · 8`, plus `Next habit task Thu`.

**Data.** `Task.kind` gains `learn, check, habit, pace, map, sweep, words`; every task gains
`subject`. The drill `task` regex widens (§3.2). `GET /api/plan.habits` = U6's top 3. Each day
carries `budget: {m, g, w, q, s, cut: [{kind, count, to}]}`, so the preview line and the rows
read one computation.

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
* **Gate mode** (L1) overrides Build and Sharpen with `tiers:['easy','medium']`, and L2's pins
  with it: while gated, no `pins` item carries hard (L1's precedence).

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

**Landing, new student.** v2's hero, and the example day's first question row carries a live
question (`UI.workspace(host, q, {mode:'inline'})`, T1's inline mode: select, Check, the named
mistake).
* **The example day is the real day 1.** For a learner on the measure path (no sitting, L7's
  default), `sample_day` is what `POST /api/plan` would create: `Diagnostic · 20 questions · ~30
  min`, then `Map · 6 skills you haven't shown yet` (L2). With an estimate, it is that plan's
  day 1. v2 §6's "focus starts on Algebra and Advanced Math" no longer applies to measure plans
  (§3.1).
* **Where the question comes from.** `POST /api/plan/preview` returns `first: {token,
  question} | null` for `sample_day`'s first question row, built on T1's F5 preview path: the
  seed from `drill.preview_seed(learner, template, day)`, `question` as `drill.public()` output,
  and the HMAC token over `learner|template|seed|local day|task id`. On the measure path the
  item is the first item U5's probe would serve (a Map day's body), since the diagnostic itself
  is a sitting.
* **Answering it.** `POST /api/drill {source:'plan_preview', count:1, first:{token, answer,
  ms}}` recomputes the item, checks the token (same learner, same local day, same item), creates
  a one-question session with `source:'plan_preview'`, and files the answer through
  `drill.answer`, so the feedback is the usual named mistake, recorded like every answer. A
  stale token gives 409 `preview_stale`, and the row shows `Load a fresh question`.

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
  * At 390 the Live plan (compact month, week 1, day 1's rows) and the Glance rows render
    inline on every step, above the sticky footer, not in a bottom sheet (decision 4). v2's
    Glance bar and sheet are replaced (§3.1).
* **⌘/Ctrl Enter** creates from any step once step 2 is valid (later steps take the defaults);
  the footer shows the hint `⌘↵ create now`.

**Data.** `GET /api/plan` returns `proposal: {cfg, why, preview}` when there is no active plan.
`POST /api/plan/preview` adds `calendar: [{date, kind, minutes, phase, test}]`, `week` (T18's
7 days of `{date, kind, minutes, topics}`), `sample_day: {date, tasks}` and `first: {token,
question} | null`. Drill `source` gains `plan_preview` (§3.2).

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
* **Reading & Writing** sits beside Math as a slider with a number field (L21), not a hidden
  optional input.

**Step 2.**
* **TargetNote** adds U4's need and P10's route:
  * `700 is about 88% of the section's points · the points you're most likely missing are in
    Circles, Probability and Nonlinear functions` (v2's points line, with U4 `need`'s top 3
    skills by gain);
  * above 580: `Your first modules: about 54% · 14 of 22 routes up`.
  * v2's 780-cap line stays.
  * No "N of 44 right" count. Scoring is difficulty-weighted, so a count read off the points
    share (44 × 0.88 ≈ 39) contradicts any count from U4's `right_of_44` (37), and v2's review
    already removed it.
* **R&W target** slider + number and `Total 1060 → 1350 (+290)` on a 400–1600 track (L21).
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
  L14). Helper: `A checkpoint is a twin of one of your baseline tests: the same question types
  with new numbers, so the two compare slot by slot.`
* **R&W time** chips `0 · 15 · 30 · 45 · 60 min a study day` (L21).

**Step 4.**
* L1's points panel and row figures, L2's coverage line per domain, L3's Auto focus switch.
* **SkillRows are always open** under their DomainRow (decision 4): all 19, each with its
  segmented control, `≈ +15` and gap tags. The chevron becomes a plain count label (`2 skills on
  focus`).
* **The R&W group**: its 4 domains with Focus / Normal / Strong (L21), under a `Reading &
  Writing` header with its own `1/2 focus` counter.
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
7. Step 2's TargetNote for target 700 contains "88%" and no text matching `of 44 right`.
8. Step 4 at 1280 shows 19 SkillRows on load with no click.

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
* **The run's order** is L4's: test → warm-up → fix → learn / check → habit / pace → focus (or
  map, sweep) → **Words**. Every counted task of the day is a block of the run except own tasks:
  * **Words is a block.** The interstitial's next pane reads `Words · 12 due · ~6 min · due
    first`, and Continue opens `/words/run/?today=1&run=<today>`, which starts S9's today run
    with `{box: w, run, task:'<d>:words'}`. Its finish reply carries `plan: {tasks, next}` like a
    drill's (§3.2), so its summary becomes the next interstitial, or the end of the run.
  * **Own tasks** (L11, L21) are not launched: the rail shows them as segments marked `on your
    own`, and the final receipt lists them as live checkboxes.
* **Mid-run**, the pill reads `Resume today · block 2 of 3 · 6 of 20` everywhere.
* **The day rail** (S4 on sessions, S5 in the test page, S9 in the Words runner; shown when
  `run` is set) is a thin strip under the header: one segment per counted task of the day,
  filled by answered/total (Words by its box minutes; own tasks hatched with `on your own`),
  labelled `Today 18 of 45 min`.
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
else. The Words today run and the mock test accept and echo `run` the same way. Chaining is on
the client, from the finish response's `plan.next` (drills and tests have it; the Words run
finish gains it, §3.2). The rail reads `GET /api/plan/day/{run}` (tasks with answered/total,
Words with its minutes). The end reads `/api/today.receipt` (T19).

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

#### L9. Today I have: time chips that trim the day by value

*From: outcomes #4 (time box, minimum day), the experience DayPanel gap, unfair-advantage #7.
Effort S. Builders: S7, S3 (the same chips on Today's plan card).*

**Why.** A plan that only offers "skip" on a bad day gets abandoned. Ten minutes of the
highest-value work keeps the spacing, the streak and the habit. Theirs has fixed durations and a
Behind banner that fires a week too late.

**Screens.**
* A chip row in the DayPanel head: `Today I have: 10 · 15 · 30 · [45] · 60 · 90 min`, with the
  planned minutes selected.
* Choosing a chip shows a preview line in place before applying, read from the day's
  `budget.cut`: `Fits: Words 3 · Warm-up 3 · Fix 4 · 14 min · Left for later: Focus 10 q (its
  topics come back sooner) · Before · Circles → Thu` with `.btn Apply` (Enter) and `Cancel`. On
  a test day under 35 minutes it adds `Module test moves to Thu · it needs 35 min`.
* Apply → `PUT /api/plan/{id}/day/{today} {minutes, trim:true}`, with Undo.
* The same chips replace `Practice anyway` on a rest day (they start that many minutes from the
  next allocation), and sit on Today's plan card.

**Rules.**
* A chip re-runs L4's budget with `m` = the chip, the same fill, floors and cut destinations,
  so every kind is covered: own tasks, the test, Words, warm-up, fix, check, learn, sweep,
  habit, pace and focus. In effect, shrinking cuts focus first, then pace, habit, sweep, learn
  and check, then fix, and keeps Words (due first, at least 3 min) and the warm-up (at least 2)
  longest. **Growing** adds focus questions.
* By chip at `s = 95` with Words on: 10 min → Words 3 + warm-up 4; 15 → Words 3 + warm-up 3 +
  fix 4; 30 → Words 6 + warm-up 5 + fix 4 + focus 6 (with 6 open traps; 29.8 min).
* Cut kinds go where L4 says. Undone focus topics keep their deficit (§4) and the re-deal brings
  them back sooner.
* A trimmed day below 60% of its base minutes can be at best `partial` (a half-ring "short day"
  glyph on the calendar and week strip). A partial day keeps the streak.

**Data.** `GET /api/plan/day/{date}?minutes=m` returns the trimmed preview `{tasks, budget,
cut:[{kind, count, topics, to}]}` (L4's `budget`). `plan_overrides.trim INTEGER DEFAULT 0`.

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

#### L10. Rows that say what they're worth, show their evidence and report what they did

*From: the Why, task-action and Again gaps of all three, outcomes #9 (fix order), the open
question on Mark done. Effort S. Builders: S7 (`UI.taskRow`, PATCH), P18 (rematch misses), T2
(the result shape).*

**Why.** Their aiReason can't be checked, and a ticked task records nothing. Ours should prove
each claim in one tap, act on why a student skipped, and say after every task what it
changed.

**Row additions.**
* **Meta**: minutes at the learner's pace (L4) and the skill's `≈ +15` (L1).
* **Actions in view** (theirs shows Skip, Mark done and Practice again as buttons; so does ours,
  on every row):
  * beside `Start` / `Resume`: quiet `Skip` and `Mark done` buttons; once Skip is tapped, its
    reason chips appear inline in the row;
  * the status circle is a real checkbox on every task (`role=checkbox`, 24 px target). On a
    question task it opens the `Did it elsewhere?` form below, inline; on an own task it ticks;
  * a done row shows `Again · the 3 you missed`, `Again · 10 more` (and `Again · harder` when it
    applies) and `Undo` as visible buttons; a skipped or moved row shows `Undo`;
  * the ⋯ TaskMenu keeps only Move, Swap topics, Make it a section / module, Edit and Remove.
  * At 390 the buttons wrap under the title (v2's 340 px rule); none moves into the menu.
* **Why lines, always shown**: under each row's detail line, every `why` line in full with its
  evidence link, no disclosure (decision 4; theirs shows aiReason on the row). They carry
  evidence (`why: [{text, href}]`):
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
  * **I know this** → an 8-question test-out now: `{topics, count:8, tiers:['medium','hard'],
    timing:'pace', task:'<d>:check:<t>'}`. 7/8 or better passes the skill (L3's Passed, with
    `by:'auto'` and keep-warm); a true-60% student passes about 11% of the time, against 34% on
    4/5. Less reads `Not yet · 5 of 8`, and the task returns to todo.
* **Mark done on a question task** (the button or the checkbox) opens `Did it elsewhere? [20]
  min · Bluebook · Khan Academy · A book · A tutor · Other`. The minutes count toward the day's minutes and status (R13's own-task
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
6. At 1280 and 390, every undone question row has visible `Skip` and `Mark done` buttons and a
   `[role=checkbox]` status circle; the ⋯ menu contains no Skip, Mark done or Again item.
7. Every row's why lines are visible on load (no `details`, no `aria-expanded=false` around
   them).
8. `I know this` sends a body with `count == 8`; 7 right passes the skill, 6 reads "Not yet".

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
  * the Math score and the R&W score go to `add_outside_score(source:'bluebook')`, so they feed
    mean3, the trajectory, drift and the projection (R&W's in `score.rw` and the Total, L21);
  * **R&W misses per domain**: four number fields, `Information and Ideas · Craft and
    Structure · Expression of Ideas · Standard English Conventions · [ ] missed of [ ]`
    (Bluebook's own report groups them this way), saved through `plan.log_rw` (L21) and shown in
    the DomainCard's R&W section;
  * the missed cells build U2's follow-up set, which becomes tomorrow's Fix (`Bluebook
    follow-up · 2 per missed skill`).
  * `Add the score later` leaves a plain tick, and a link stays on the done row.
* **Tutor**: the done row offers `Log a mistake from it` (U2, one question) repeatedly and counts
  them (`3 logged`).
* **R&W**: counted as R&W minutes; when Words is on, the detail links `Words · 12 due`. L21's
  R&W domain tasks are this type, generated from `sections.rw`.

**Data.** `plan_tasks` gains `type TEXT DEFAULT 'other'` and `subject TEXT DEFAULT 'math'`.
Ticking a bluebook task returns `{next:'score_sheet'}`.

**Acceptance.**
1. `POST /api/plan/{id}/tasks {type:'bluebook', day}` creates a task with `minutes == 134`.
2. Ticking it and saving Math 610 → `/api/scores` lists an outside score of 610 on that day,
   and `GET /api/plan.sittings` includes it.
3. Three missed cells in 2 skills → tomorrow's tasks include a `fix` whose detail contains
   "Bluebook follow-up".
4. Saving R&W 560 with Standard English Conventions 5 missed of 26 → `GET /api/plan.score.rw`
   includes the 560 sitting, and `GET /api/plan/progress.rw_domains` has that domain with
   `missed == 5`.

#### L12. Drag, keys and instant

*From: experience #8, the experience loading gap, U23 / T20. Effort M. Builders: S7, F2
(`UI.keys` scope `plan`, `UI.cached`), F1 (`UI.sheet`).*

**Why.** Their only reschedule is three taps to a later day of the same week. A plan is edited
every day; each edit should be one gesture that shows its consequence first.

* **Drag (desktop, pointer events, no library)**: each task row has a handle. While dragging:
  * every valid WeekStrip column and MonthCalendar cell shows its new load in mono
    (`45 → 73m`);
  * invalid ones are dimmed, with the reason as visible text in the cell and in
    `aria-describedby`: rest day, the eve, a test on a day under 35 minutes.
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
  * with R&W set, `R&W 500 → 650 · Total 1060 → 1350 · last Bluebook 1120` (L21);
  * `What changes it ›` opens the levers.
* **Plan done** reads against the schedule: `27% · 12 of 44 study days · on schedule`, or
  `2 behind · make up Thu? [Do it now]` (starts the missed day's catch-up task).
* **This week** adds U14's goal pips (L16).
* Each tile is a button: Days → the calendar, Score → the trajectory, Plan done → the missed
  days, Week → the week review.

**Checkpoints on every test day.**
* Each test task shows `Checkpoint 2 · aim 610+`: the pace line (start → target on the exam
  date) at that date, rounded to 10.
* After the sitting, the verdict reads the sitting's band (±70, `MOCK_HALF_BAND`), never its
  midpoint alone:
  * **beat** only when the band's low end clears the aim: `680 mid · 610–750 · beat, even at the
    low end`;
  * **under** only when the band's high end is below it: `530 mid · 460–600 · under`;
  * **within the band** otherwise: `590 mid · 520–660 · within the band · one sitting can't
    tell`.
* The WeekStrip marks a test day ✓ only on **beat**; **under** gets a hollow ring with `!`, and
  **within** gets nothing. The TrajectoryChart draws the aims as ticks on the pace line, filled
  only when beaten.

**Levers** (`What changes it`, the Behind banner, and the Score tile's `Short` state). The top
3 by improvement, each previewed and applied with one tap and Undo:
* `+15 min a day · fits with 6 h to spare`;
* `Add Saturday · 38 study days · fits with 3 h to spare`;
* `Move to Dec 5 · needs +11 a week (you make +9)` (only when not booked);
* `Ramp from 25 · 20 h to the exam · fits with 1 h to spare`.

**TrajectoryChart** gains U9's cone (a `--mat` area from now to the exam) beside the pace line,
with its hidden-table rows.

**Data.** `GET /api/plan` adds `projection: {math}` (U9), `verdict: {math: {kind,
made_per_week, needs_per_week}}`, `score: {math, rw?, total?}` (L21), `workload` (T12, through
`deps.part('today', 'workload')`), `levers: [{kind, label, patch, effect: {needs_per_week, fits,
spare_h, short_h, study_days}}]`, and `test.aim` / `test.result: {mid, low, high, verdict:
'beat'|'within'|'under'}` per test task. Preview computes the levers.

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

#### L14. Checkpoint twins: the same 22 question types as your baseline, slot by slot

*From: unfair-advantage #3, the unfair-advantage test-rhythm gap. Effort M. Builders: S7 (the
rhythm, the task, the card), S5 (twin kind with `task`, exists), S6 (`GET
/api/session/{id}/compare?with=`, from T16).*

**Why.** Their plan draws on 10 fixed papers, and a retake repeats questions whose keys the
student has seen, so the second score is contaminated. A parallel form on demand needs a
generator. With one, two tests two weeks apart compare like with like, slot by slot. The same
types asked again are still partly rehearsal, so ours keeps that small and says how much.

**Two baselines, alternating** (`cfg.baselines: [a, b]`, each set once found):
* **A**: the first scored module or section finished inside the plan window, else the most
  recent in the 14 days before the start.
* **B**: the first fresh (non-twin) module finished from week 3 of the plan.
* A diagnostic baseline gives fresh sections until a module or section exists.
* Checkpoints alternate A, B, A, … (only A until B exists), so on a weekly rhythm with every 2nd
  test a 12-week plan re-asks each baseline's 22 types about 3 times, not 6. Each checkpoint
  compares with its own baseline.

**Checkpoint tests**: with `cfg.checkpoints` `every` or `every2`, those test tasks start `POST
/api/mock/new {kind:'twin', twin_of: <its baseline>, task:'<d>:test'}`.
* Row: `Checkpoint 2 · twin of your Oct 7 module · same 22 question types, new numbers · 35
  min`.
* The other test days stay fresh adaptive sections.

**CheckpointCard** (top of the Progress tab; also in the report when the sitting's task is a
checkpoint):
* `Baseline A 11/22 · 470–610 → Checkpoint 2 16/22 · 560–700 · +90`. When the two bands
  overlap: `The bands overlap: part of +90 may be the sitting, not the skill.`
* A 22-cell slot strip for module 1. Each cell has a glyph and text: fixed ✗→✓, held ✓→✓,
  slipped ✓→✗, still missed ✗→✗, and a small `p` mark when that slot's template was served to
  the student in any session between the baseline and the checkpoint (`practised`). Counts
  under it: `fixed 7 (2 practised) · held 9 · slipped 2 · still missed 4`.
* Tapping a cell names the skill, the tier, the trap chosen, and `practised 3 times since Sep
  23` when it was.
* Pill `Fix these 6` → `{from_session: <checkpoint>, only: [the slipped and still-missed qids],
  each:2, sibling:true, source:'twin', task:'<today>:extra'}`. `sibling:true` serves other
  templates of the same skill at the same tier (`blueprint.siblings(t, 0)`, P18's rule at step
  0), never the checkpoint's own templates, so the next checkpoint is not a rehearsal of this
  one. A slot whose topic has no other template at that tier falls back to its own template
  on a fresh seed, and that slot is marked practised.
* A series line per baseline, labelled `same question types`: `Baseline A 11 → CP1 14 → CP3 16
  of 22 · same question types each time, so some of the gain is familiarity with them`.
* On the TrajectoryChart, checkpoints are filled squares and fresh tests dots.

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

#### L15. What changed this morning, and why

*From: experience #6. Effort M. Builders: S7 (`plan_snapshots`, `plan_events`), S3 (calls
`plan.today_summary`, which snapshots).*

**Why.** Theirs markets "dynamic score drift adjustments" through a black-box regenerate. Ours
re-deals every day, which is only trusted if the student can see what moved and which answer
moved it.

**The event log.** `plan_events(id INTEGER PK, plan, at, kind, field, from_v, to_v, text,
day)`, with `kind` one of `edit | auto | sitting | mistake | phase`. The causes live here, not
in the snapshot:
* **edit**: every `PATCH /api/plan`, day and week override (`PUT …/day`, `PUT …/week`), task
  mark, move, skip and own-task change writes one row, named from its field (`field:'minutes',
  from_v:45, to_v:25, text:'fitted to 25 min'`).
* **auto**: every automatic change writes one row: L3's focus moves, L7's re-base from the
  diagnostic, L17's auto-drift, L2's Map done.
* **sitting** and **mistake**: written by the snapshot step from the scored sessions and the
  traps opened or closed since the previous snapshot (one row each, with the label).
* **phase**: written by the first re-deal in a new phase (`Final starts`).

**Snapshots.**
* On the first of `plan.today_summary()` (which Today's plan card and `/api/today.plan` call) or
  `GET /api/plan` in each local day, whichever comes first, plan.py stores the next 14 days
  (date, kind, minutes, test, topics, task kinds and counts) in `plan_snapshots`, kept 60 days.
  A student who works only from Today still gets one snapshot a day.
* A diff against the previous snapshot gives change lines. Each line takes its cause from
  `plan_events` between the two snapshots, matched by day and field, first match: edit, sitting,
  auto (a focus move), mistake, phase. A line with no matching event says `re-dealt from your
  answers`.
* Examples: `Circles added Thu · 2 new mistakes yesterday` · `Fix set 8 → 12 · 4 new mistakes` ·
  `Fri module → section · Final starts` · `Mon off · you took it off` · `Circles → Strong ·
  passed its check 4/4 and 10 of 12`.

**Screens.**
* **Changelog lines** under the tabs, always open (decision 4): a kicker `Since this morning ·
  3 changes`, or `Since Tue · 5 changes` when the previous snapshot is older than yesterday,
  then every line in full with its cause. Each line selects its day. Changed WeekStrip cells
  carry a small dot until that day is selected (localStorage, try/catch). With no changes the
  kicker reads `No changes today`, and nothing else shows.
* **Progress › Changes**: `Your plan changed 23 times · 17 from your answers · 4 from your edits
  · 2 from tests` (counted from `plan_events`: mistake and auto, edit, sitting), then the dated
  list, paged by 20.

**Data.** `plan_snapshots(plan, made_on, days JSON; PK(plan, made_on))`; `plan_events` as above,
indexed on `(plan, at)`. `GET /api/plan.changes = {since, today: [{text, day, cause, event}],
counts}`. `GET /api/plan/{id}/changes?before=` pages `plan_events` with their lines.

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

#### L16. The week: review, goals in the header, and next week shaped in one sheet

*From: outcomes #4 (weekly reset), experience #7, unfair-advantage #8, the week-view gaps of all
three. Effort M. Builders: S1 (U14's sheet hosts it), S7 (`UI.weekPlanner`, the week endpoint),
F4 (U14's `week_goals`).*

**Why.** Their week is a theme sentence and a percentage. A week should end with its real
results, set up to three checked goals, and let the student reshape next week in a minute, short
of rebuilding the plan.

* **The review is U14's Monday sheet** (S1). With an active plan, its receipts add the plan's
  facts (`Days 4 of 5 · 3h 10m of 3h 45m · Circles before 1/4 → after 4/4, passed · Checkpoint
  aim 610 · 680 mid, 610–750 · beat`).
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
  * the sittings as dated chips linking to their reports; with R&W set, Bluebook R&W sittings
    drift `sections.rw.current` by the same mean3 rule, and the preview adds the Total (`Start
    from 1120 total`, L21);
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
  * Sorted by minutes.
  * **Not moving**, defined on two windows of 20 clean first tries (R8):
    * *before*: the skill's 20 before the plan start; with fewer than 20 there, the first 20 in
      the plan;
    * *after*: its last 20, none of them in *before*;
    * flagged when the skill had 60+ minutes in the last 14 days, both windows are full, and
      *after* − *before* is under 10 points of first-try accuracy (for example 10/20 → 11/20,
      +5). 20 answers move in 5-point steps, so 10 points is two answers.
    * A flagged row offers `Learn it · untimed` (T4) and `See its misses` (T7 items for that
      topic), and reads `Not moving · 50% → 55% over 20 answers each · 72 min in 14 days`.
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
  each row adds `≈ +40 on the table · ≈ +12 claimed since Sep 23`. A `Math · R&W` legend (glyph
  and text) heads it, and the **R&W section** follows the Math rows (L21).
* **All 19 skills**: the table is open on the tab (decision 4), all 19 rows sorted by points
  (or weakest first with `By accuracy`), with v2's columns plus `≈ +` and coverage cells; its
  header sorts, and it scrolls inside its card only past 19 rows (never, today).
* **SplitCard**: a third bar, minutes by domain over the plan against the share of points on the
  table (T17's `time_split`): `Algebra · 35% of your time · 12% of your points`, with
  `.btn Rebalance to the points`, which puts the domain with the largest gap on Focus (PATCH,
  Undo).
* **StudyTimeChart**: a first-try accuracy line on a right axis (a hollow dot under 5 answers);
  clicking a bar opens that day on the Plan tab (`?day=`).

**Data.** `GET /api/plan/progress = {bought, causes, coverage, checks, weeks, checkpoints,
calibration, pace, split_domain, changes_counts, rw_domains}`; each `bought` row carries
`{topic, minutes, minutes_14d, before: {right, of}, after: {right, of}, not_moving, fixed,
check, claimed}`, and per-section parts are keyed by subject.

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
* **They replace Final's weekly tests.** From Final's first day, no weekly module or section is
  dealt: a Final week with a rehearsal has that test only, and the exam week has none (its days
  are taper days). This replaces v2's "the exam-week test moves to Thursday" (§3.1).
* The day becomes a test day, even if it was a rest day; the student can move it (not onto a
  taper day).
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
* minutes × 0.6 (an override shown as `Taper · 27 of 45 min`; day status rules as normal), filled
  by L4's budget, so every taper day fits its minutes;
* no test, and no Learn, Map or Habit;
* the warm-up up to 8 (L4's Final target, which scales with `q`);
* focus only on skills with 2 or more questions a test (U4 `per_test`);
* **the last timed set, 2 days out**: that day's focus set is a timed set (`timing:'pace'`) of up
  to 10 questions, reserved before the other kinds (`r = min(10, q − 2)`), so the warm-up and
  fix shrink around it. At 27 minutes, `s = 95` and Words 5: Words 5 + timed set 10 + warm-up 3
  (25.6 min). Row: `Last timed set · 10 in 15:50 · like the real pace`.
* A **Trap gauntlet · 10** (U6) as a counted task 3 days out, inside the same budget (it takes
  the focus reserve that day).

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

#### L20. Plans that remember what worked

*From: the Plans/History gaps of all three. Effort S. Builders: S7.*

**Why.** Students retake. The first plan's evidence (which weekdays held, which skills
relapsed, what an hour bought) should make the second plan better, not start from scratch.

* **PlanSummary** gains `record: {hours, days_pct, by_dow: [pct × 7], start_mid, end_mid,
  result, fixed, relapsed, checks_passed, best_weekday, changes}` and `recent_events` (the last
  3 `plan_events` texts with dates, L15), and `result` / `target` gain `total` when R&W is set.
* **Every plan is listed** (decision 4; v2 collapsed to 5): the list pages by 20 only past 20
  rows (`Show 20 more · 12 left`).
* **Plans rows** for finished and archived plans: `Sep 1 → Oct 3 · 82% of days · 31 h · 560 →
  650 (+90) · 44 fixed · 3 relapsed`, with a 7-cell weekday adherence strip (glyph and percentage
  per day). With R&W set the target and result read as totals: `target 1350 (Math 700) · 1290 →
  1380`.
* Under each row, its last 3 `plan_events` lines, always shown: `Oct 2 fitted to 25 min · Oct 9
  target 750 · Oct 12 Circles → Strong`, then `All 23 changes ›`, which opens that plan's
  Progress › Changes (`?id=…&tab=progress#changes`).
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
3. A learner with 25 plans: the Plans tab shows 20 rows and "Show 20 more · 5 left"; with 12
   plans it shows 12 rows and no pager.
4. A finished plan with 4 edits shows its last 3 event lines under the row without a click.

---

### F. Both sections

#### L21. Reading & Writing in the plan, and the Total everywhere

*From: the skeptic review of the R&W half of theirs, decision 3. Effort M. Builders: S7
(`sections.rw`, the R&W tasks, the Total, the DomainCard section, `rw_log`), S9 (the today run's
`goal`, `transitions` and `in_context`; `bank.words`), U2's sheet (the R&W domain fields, L11),
F1 (the 400–1600 track).*

**Why.** Their plan covers both sections: R&W current and target sliders, 4 R&W domains with
Focus / Normal / Strong, Reading and Vocabulary tasks, a total-score tile (`1000 now, 1400
target`) and RW / MATH accuracy. Decision 3 keeps the site Math-first while the R&W bank is
built. It does not let the plan ignore half the score. A student aiming for 1400 has to see the
total, and their R&W time has to be planned and fed by real evidence. We do that with what we
have: the spaced Words queue (decision 2), Bluebook's R&W results by domain (L11), and typed R&W
tasks per domain. When the R&W bank arrives, `sections.rw` gains an allocator, and nothing
changes shape.

**Wizard.**
* **Step 1**: `Reading & Writing`, a 200–800 slider with a number field beside Math's (not
  hidden, not a switch). Its SourceNote reads `From your Oct 3 Bluebook test` (the latest
  outside R&W score), or `Not set · your Total needs it`. Leaving it unset keeps a Math-only
  plan: the R&W parts below still show and read `Not set`. `Total 1060` sits under both.
* **Step 2**: an R&W target slider + number field (minimum = R&W current), always shown, and
  disabled with the visible reason `Set your R&W score first` while current is unset. The NOW →
  TARGET card adds `R&W 500 → 650 (+150)` and `Total 1060 → 1350 (+290)` on a 400–1600 track,
  with the screen-reader sentence for the total. The Glance and the page title read `Nov 7 ·
  1350`, with `Math 700` under it.
* **Step 3**: `R&W time` chips `0 · 15 · 30 · 45 · 60 min a study day` (`sections.rw.minutes`;
  30 once R&W is set, else 0), with the line `On top of your Math time · 3h 45m + 2h 30m a
  week`. v2's quick-add chip `+ Reading & Writing · 30 min · every study day` sets this same
  field, so there is never a second R&W task.
* **Step 4**: the R&W group, 4 DomainRows under a `Reading & Writing` header with its own
  `1/2 focus` counter. Each row has the `↑ Focus / — Normal / ✓ Strong` control (at most 2 on
  Focus), a weight tag, an evidence line from `rw_log` (`5 missed of 26 in 2 Bluebook tests`, or
  `No R&W results yet · log them after a Bluebook test`), and what Focus does, as visible text:

  | domain | about of the R&W section | Focus does |
  |---|---|---|
  | Information and Ideas | 26% | its own daily R&W task |
  | Craft and Structure | 28% | its own task; Words' new-word goal up one chip (10 → 15, at most 20), and 2 in-context items a run instead of 1 |
  | Expression of Ideas | 20% | its own task; Words' transition items 2–3 → 6 a run |
  | Standard English Conventions | 26% | its own task |

  * **Suggestion**: Focus the 1–2 domains with the highest missed share in `rw_log` (missed ÷
    of, with at least 8 answered); Strong under 10% missed. With no results, no suggestion.
  * The Words goal change is written to `prefs.words_goal` with a toast and Undo
    (`Words: 15 new a day while Craft and Structure is on Focus · Undo`), and the step 4 Words
    row shows the new value at once.

**The R&W tasks** (kind `custom`, type `rw`, subject `rw`, made each study day from
`sections.rw`):
* The day's R&W minutes split over the 4 domains by share × `{focus 2, normal 1, strong 0.4}`,
  rounded to 5 minutes.
* Each Focus domain gets its own row: `R&W · Standard English Conventions · 15 min`. The Normal
  and Strong domains share one row: `R&W · Information and Ideas, Craft and Structure,
  Expression of Ideas · 15 min`. A share under 5 minutes joins the shared row.
* Detail: `On your own · Bluebook practice or Khan Academy's official SAT practice`, with both
  links. Craft and Structure and Expression of Ideas rows add `Words covers the vocabulary and
  transitions`.
* Actions: the checkbox (ticked = done, by R13's own-task rule), then an inline `Log misses ·
  [ ] missed of [ ]` for the row's domain (one pair per domain on the shared row), which writes
  `rw_log` with `source:'task'`.
* In the rest of the plan they are own tasks: kept by L4's budget while 10+ minutes are left for
  the rest, shown in L8's run as `on your own`, and moved like own tasks (L12).

**The Total, wherever the score shows** (when R&W current and target are set):
* The page title (`Nov 7 · 1350`); the Score tile's `R&W 500 → 650 · Total 1060 → 1350 · last
  Bluebook 1120` (L13); drift on R&W Bluebook sittings with R16's mean3 rule, previewing the
  Total (L17); the Plans rows (L20); and the result form, whose R&W field fills
  `result.total`.
* Projections stay per section: `At this pace: 640–700 Math on Nov 7`. R&W gets no projection
  (there is no model for it), only its sittings.

**Progress.**
* The DomainCard's **R&W section**, after the Math rows under the `Math · R&W` legend: 4 rows
  with the state tag, `missed 5 of 26 · 19% · from 2 Bluebook tests and 3 logged sets`, R&W
  minutes planned against done, and `Log misses` inline.
* The SplitCard shows R&W minutes (R&W tasks + Words) as their own segment beside Math's.

**Landing.** BankStats gains a fourth tile, **Words**: W17's live count (`1,180 words · 60
transitions · you know about 540`), with the line *Spaced review that measures itself: the first
part of Reading & Writing here*. It comes from `bank.words`, filled by S9.

**Data.**
* `cfg.sections.rw: {current, target, focus: {domain: state}, minutes} | null` (the
  Subject-aware bullet at the top). `PlanIn` validates rw domains against `plan.RW_DOMAINS` (the
  4 names and shares, a constant until the R&W bank owns them), with at most 2 on Focus.
* New table `rw_log(id, learner, at, source 'bluebook'|'task', ref, domain, missed, of)`,
  written through `plan.log_rw(learner, rows)` by U2's sheet (L11) and by the R&W task's `Log
  misses`: `POST /api/plan/{id}/rwlog {day, task?, rows: [{domain, missed, of}]}`.
* `GET /api/plan` adds `score.rw: {start, target, sittings}` and `score.total: {start, target,
  latest}` (only when set) and `bank.words: {words, transitions, known}`. `GET
  /api/plan/progress.rw_domains = [{domain, state, missed, of, sources, minutes_planned,
  minutes_done}]`. The day's `words` body gains `goal`, `transitions` and `in_context` when an
  R&W domain on Focus sets them (§3.2).

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

### 3.1 Inside §3.6 (spec/rebuild-v2.md lines 7046–8096)

Each entry quotes the current text, then gives the replacement or addition.

1. **Box.**
   * Quote: "> **Read with resolutions:** R9, R10, R11, R13, R14, R15, R16, R18 (§2.2). Where
     this spec disagrees with them, they win."
   * Append: "Read with `spec/v2-upgrades/plan.md` (L1–L21), which wins over this section, and
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
   * Add as tile 4: "4. **Words**: W17's live count of SAT words and transitions with `you know
     about N`, and the line *Spaced review that measures itself* (`bank.words`, L21)."

4. **1d ExampleDay.**
   * Quote: "- A new student sees the blueprint-weighted focus set only."
   * Replace with: "- A new student on the measure path sees their real day 1 (`Diagnostic ·
     20 questions`, then `Map · 6 skills`); with an estimate, that plan's day 1. The first
     question row holds a live question from the preview's `first` token (`UI.workspace`
     inline), answered into a one-question `plan_preview` session (L6). With data, the example
     day is the proposal's day 1."

5. **2a GlancePanel.**
   * Quote: "- **GlancePanel**: recomputed by `POST /api/plan/preview`, debounced 250ms. Stale
     rows dim to 60% while the call is in flight. Rows:"
   * Add before the rows: "It opens with the **Live plan** (L6): the compact month, week 1's
     columns and day 1's rows, each changed cell ringed once."
   * Quote: "  - At 390: the Glance becomes a bar above the footer, e.g. `560 → 700 · Nov 7 · 3h
     45m/wk ⌃`. Tapping it opens a bottom sheet."
   * Replace with: "  - At 390: the Live plan and the Glance rows render inline on every step,
     above the sticky footer, with no bottom sheet (decision 4, L6)."

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
   * Add to its points line: "`· the points you're most likely missing are in Circles,
     Probability and Nonlinear functions`" (U4 `need`'s top 3 by gain), and, above 580, the line
     "`Your first modules: about 54% · 14 of 22 routes up`" (P10 `route`). No "N of 44 right"
     count (L7).

9a. **2b and 2c Reading & Writing.**
   * Quote the "- **Reading & Writing** row, always visible:" item with its sub-bullets, and
     "  - With R&W filled in, an optional `R&W target` number field appears."
   * Replace with L21's step 1 and step 2: an R&W slider + number with its SourceNote and the
     Total; an R&W target slider + number, always shown, disabled with `Set your R&W score
     first` while unset; `R&W 500 → 650 (+150)` and `Total 1060 → 1350 (+290)` on a 400–1600
     track.

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
      (`cfg.ramp`) (L7), then the `R&W time` chips `0 · 15 · 30 · 45 · 60` (L21).

13. **2d WeekdayTiles.**
    * Quote: "- **WeekdayTiles**: seven tiles, Mon–Sun, with 3-letter names. Each tile is 72px
      wide at desktop."
    * Append: "Each tile also shows `studied 3 of last 4 · ~35m` (L7)."

14. **2d TestRhythm.**
    * Quote: "- **TestRhythm** `Practice tests`: segmented `None · Weekly · Twice a week · Every
      study day`."
    * Add under it: "  - **Checkpoints**: `Every test · Every 2nd test · Off` (default Every
      2nd; L14), twins of two alternating baselines. A tests-share warning above 30% of the
      planned minutes, with `Weekly instead` (L7)."

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
    * Quote: "  - **Chevron**: shows a count, e.g. `2 skills on focus` or `4 skills`. It expands
      **SkillRows**:"
    * Replace with: "  - **Count label**: `2 skills on focus` or `4 skills`, over its **SkillRows**,
      which are always shown (decision 4, L7):"
    * Add after the Math DomainRows: "- **Reading & Writing** group: 4 DomainRows with Focus /
      Normal / Strong (2 at most), evidence from `rw_log`, and what Focus does (L21)."

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
      `bluebook`, 134 min), `+ Reading & Writing · 30 min · every study day` (sets
      `sections.rw.minutes` to 30, which makes the typed R&W tasks, L21), `+ Tutor session`
      (type `tutor`), `+ Other…` (L11)."

21. **2f Create.**
    * Quote: "  - a toast (`role=status`) reads `Plan made · 31 study days to Nov 7`."
    * Add: "  - keyboard focus moves to `Start today` (L8); after a one-tap create, the `Built
      from your results` chip banner shows (L6)."

22. **3b StatTiles.**
    * Quote: "###### 3b. StatTiles (4 in a row at desktop; one full-width tile plus a 3-up row at
      390)"
    * Add under the heading: "Each tile is a button that opens its detail. Days adds capacity
      against the work left; Score adds the projection, made vs needed a week, ≈ claimed, the
      route and, with R&W set, the Total; Plan done reads against the schedule; This week adds
      the goal pips (L13, L16, L21)."

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
    * Add: "- Under the tabs, the changelog lines, always open: `Since this morning · 3
      changes` and every line with its cause, or `No changes today` (L15)."

25. **3f DayPanel head.**
    * Quote: "  - Right-aligned mono: `45 min planned`."
    * Add: "  - The pill `Start today · 3 tasks · 45 min` (L8) and the chip row `Today I have: 10
      · 15 · 30 · 45 · 60 · 90 min` (L9). With `cfg.place`: `16:00 · the library`."

26. **3f Type tags.**
    * Quote: "  - **Title**, a **type tag** and one **detail line**. Type tags: `Mistakes`,
      `Rechecks`, `Focus`, `Test`, `Your own`, `Extra`."
    * Replace the tag list with: "`Warm-up`, `Mistakes`, `Learn it`, `Check`, `Habit`,
      `Pace`, `Map`, `Focus`, `Test`, `Checkpoint`, `Rehearsal`, `Sweep`, `Words`, `R&W`,
      `Your own`, `Extra` (L4, L21)."

27. **3f Why this?**
    * Quote: "  - **`Why this?`** is a disclosure listing the server's `why` lines, e.g.:"
    * Replace with: "  - **Why lines**, always shown under the detail line (no disclosure,
      decision 4): the server's `why` lines in full, value first, each a link to its evidence
      (L1, L10), e.g.:"

28. **3f TaskMenu.**
    * Quote: "    - `Again · new questions` (done tasks): starts 10 more on the same topics,
      tagged `:extra`."
    * Remove `Skip` / `Undo skip`, `Mark done` / `Mark not done` and `Again` from the menu:
      they become visible buttons on the row (L10): `Skip` with its reason chips inline, `Mark
      done` with the "Did it elsewhere?" form, the status circle as a real checkbox on every
      task, and on done rows `Again · the N you missed`, `Again · 10 more`, `Again · harder`
      and `Undo`. The menu keeps `Move to…`, `Swap topics`, `Make it a section` / `Make it a
      module`, `Edit` and `Remove`. Add drag and long-press moves (L12).

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
    * Add: "  - `Goals 2/3` pips and `.quiet Review week` (L16). A test day gets ✓ only when its
      verdict is `beat`, meaning the band's low end clears the aim (L13)."

34. **3j Progress tab.**
    * Quote: "- Every chart has a visually hidden `<table>` with the same numbers."
    * Add before it: L18's cards (What your time bought, Why you lose points, Coverage, Checks,
      Weeks, Changes, Pace and calibration, CheckpointCard) and the changed DomainCard (with
      L21's R&W section and `Math · R&W` legend), SplitCard and StudyTimeChart. The tab reads
      `GET /api/plan/progress`.
    * Quote: "  - **`All 19 skills`** expands in place into a table sorted weakest first."
    * Replace with: "  - **`All 19 skills`** is a table shown open on the tab (decision 4), sorted
      by points (weakest first under `By accuracy`) (L18)."

35. **3k Plans rows.**
    * Quote: "  - mono `Built Sep 23 · Sep 23 → Nov 7 · target 700 · 45 days left · 31 tasks
      done · 80% of days`."
    * Add: "Finished and archived rows add the record line, the weekday strip and their last 3
      change lines, always shown, with `All 23 changes ›` (L20)."
    * Quote: "- More than 5 plans collapse to 5, plus `Show all 12`."
    * Replace with: "- Every plan is listed. Past 20 rows the list pages by 20 (`Show 20 more · 12
      left`) (L20)."

36. **3l Calendar events.**
    * Quote: "    - One event per study day from today, at the preferred time, lasting its
      minutes: `SAT Math · 45 min · Circles, Percentages`, or `SAT Math · Module test`."
    * Replace with: "    - One event per study day from today, at the preferred time, lasting its
      minutes, titled from the day's tasks and the check-ins due (U18a): `SAT Math · 3 check-ins
      + Circles · 45 min`, with `LOCATION` from `cfg.place` and the link `/?next=1` in
      DESCRIPTION. Rehearsals at `cfg.rehearsal_at` (L19); registration deadlines (U17)."

37. **§4 Questions for m minutes.**
    * Quote: "**Questions for m minutes**: `clamp(round(m*60/95), 5, 120)`."
    * Replace with: "**The day's budget**: L4's rule. Own tasks kept, the test first (moved when
      the day is under 35 minutes), Words `w = min(words.minutes_today(), max(3, round(0.2 ×
      g)))`, then `q = min(120, floor((g − w) × 60 / s))` with no minimum, where `s` is the
      learner's median seconds per question over 60 days, clamped to 60–150 (95 with no data),
      filled in L4's order with its targets, minimums and focus reserve."

38. **§4 Difficulty.**
    * Quote the "**Difficulty** (the drill `difficulty` list):" heading and its table.
    * Replace with L5's rules: Build `zone:'stretch'` within the needed tiers, plus L2's pins;
      Sharpen `stretch` without easy above 580; Final Standard with v2's Final row and
      `adaptive:false`; Gate mode easy and medium, with no hard pins (L1's precedence).

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
    * Add after it: L2's pins (2-question `pins` segments inside focus sets, at most 1 a
      practice day and 30% of pre-Final slots, by gain) and its three guarantees with the
      scaled window `W`, Map mode, L1's Gate mode with `plan_days.gate` hysteresis and its
      precedence over hard pins, and L3's checks (at most 2 skills a week) and keep-warm
      segments.

42. **§4 Tasks for a budget.**
    * Quote the "**Tasks for a practice budget of q questions**" list (items 1–7).
    * Replace with L4's table, budget (fill order, targets, minimums, where cut kinds go) and
      cause routing. Items 5–7 (custom, extras, why lines) stay; v2's fix count rule stays as
      the fix target.

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
    * Quote: "  - Day 1 has no fix task, and focus starts on Algebra and Advanced Math."
    * Replace with: "  - Day 1 has no fix task. On the measure path day 1 is the diagnostic and the
      next practice days are Map days (L2, L7); with an estimate, focus starts on Algebra and
      Advanced Math."
    * Quote (Lots of history): "  - Plans collapse at 5."
    * Replace with: "  - Every plan is listed; the Plans list pages by 20 past 20 rows (L20)."
    * Quote (phones): "  - The Glance is a bottom sheet."
    * Replace with: "  - The Live plan and the Glance render inline above the sticky footer on
      every step (L6)."
    * Add under Loading: "A second visit paints from `UI.cached` under `Updating…` (L12)."

48. **§3.6.4 Extras.**
    * Quote: "- **Focus that really changes time, with a live split bar**:"
    * Add at the end of the list: "- **L1–L21** (`spec/v2-upgrades/plan.md`): points decide the
      week; coverage; checks that move focus on; the rebuilt day; a plan in one tap; Start
      today; the changelog; checkpoint twins; the final phase; plans that remember; both
      sections with the Total."

49. **§3.6.5 Server changes.**
    * Quote: "- **New table plans**: plans(id TEXT PK, …"
    * Add columns: `plans.start_points JSON`; `plan_days.gate INTEGER DEFAULT 0`;
      `plan_overrides.trim INTEGER DEFAULT 0`; `plan_marks.minutes INTEGER`, `plan_marks.note
      TEXT`; `plan_tasks.type TEXT DEFAULT 'other'`, `plan_tasks.subject TEXT DEFAULT 'math'`;
      new tables `plan_snapshots(plan, made_on, days JSON; PK(plan, made_on))` and
      `plan_events(id, plan, at, kind, field, from_v, to_v, text, day)` (L15), and `rw_log(id,
      learner, at, source, ref, domain, missed, of)` (L21).
    * cfg fields add: `current: null` with `measure`, `ramp {from}`, `place`, `checkpoints
      every|every2|off`, `baselines [a, b]`, `rehearsal_at HH:MM`, `sections: {math: {current,
      target, focus, skills}, rw?: {current, target, focus, minutes}}` with top-level Math
      aliases; `skills` entries `{state, by, since, pin?}`. Focus caps per subject (math 2 / 6,
      rw 2).
    * Quote: "- **GET /api/plan**: Freezes past days first. Returns {active, …"
    * Add fields, per-section ones keyed by subject: `proposal` (no active plan), `points`,
      `map`, `checks`, `focus_history`, `habits`, `changes`, `projection`, `verdict`,
      `workload`, `levers`, `rhythm`, `sweep`; `score` becomes `{math, rw?, total?}`; `bank`
      adds `words`; Day adds `budget`; Task adds `subject`, `why: [{text, href}]`,
      `result.fixed/opened/moved/to_strong`, `aim`, `result.verdict`; PlanSummary adds `record`
      and `recent_events`.
    * Quote (plan.py's self-check list): "the exam-week test moving to Thursday"
    * Replace with: "no weekly test in Final (the rehearsals replace them), no test on a taper
      day, and L4's budget never over the day's minutes".
    * Add endpoints: `GET /api/plan/progress` (L18); `GET /api/plan/day/{date}?minutes=` (L9);
      `PUT /api/plan/{id}/week/{monday}` (L16); `GET /api/plan/{id}/changes?before=` (L15);
      `GET /api/plan/{id}/trapsheet` (L19); `POST /api/plan/{id}/rwlog` (L21). `PUT
      …/day/{date}` accepts `trim`. `PATCH …/tasks/{task}` accepts `reason`, `minutes`,
      `where`. `POST …/tasks` accepts `type`.
    * Quote: "- **POST /api/drill: task, recheck, fmt, count cap for mistakes**: task (str up to
      40, matching ^\d{4}-\d{2}-\d{2}:(fix|recheck|focus|extra)$) is stored in cfg."
    * Replace the regex with
      `^\d{4}-\d{2}-\d{2}:(fix|recheck|focus|extra|learn|check|habit|pace|map|sweep|test)(:[a-z0-9_]+)?$`,
      and add the fields `run`, `pins` and `sibling`, and the source `plan_preview` with
      `first` (§3.2).

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
    * Quote in item 2: "each full Mon-Sun week before Nov 2 has exactly one 'test' on its
      Friday, and the week of Nov 2 has its test on Thursday 2026-11-05."
    * Replace with: "each full Mon-Sun week before Oct 26 has exactly one 'test' on its Friday;
      the week of Oct 26 has one test, the dress rehearsal on Sat Oct 31, and none on Fri Oct 30
      (a taper day); the week of Nov 2 has no module test (L19)."
    * Quote in item 25: "and 'All 19 skills' expands to 19 rows."
    * Replace with: "and the 'All 19 skills' table shows 19 rows on load (L18)."
    * Append L1–L21's acceptance lists as items 32 onward.

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
      * "Check thresholds (the After at 3 of 4 with less time and 9 of the last 12 medium/hard;
        11 of 12 without a check; the 7-of-8 test-out) and the 2-a-week cap are stated choices,
        sized so a true-55–60% student passes about 5–11% of the time; revisit once check
        results exist."
      * "L4's budget targets (warm-up `ceil(0.4 q)` up to 5, the 40% focus reserve from 20
        questions, Words at 20% of the day) and L2's pin caps (1 a day, 30% of slots) are stated
        choices."
      * "The R&W domain shares in `plan.RW_DOMAINS` (26 / 28 / 20 / 26) follow College Board's
        published ranges; confirm before shipping."
      * "The 60% trimmed-day line and the 0.6 taper are stated choices."
      * "The rehearsal default 08:30 follows T13; with 'R&W first' the Math start is 09:45.
        Verify both against College Board's test-day timing."

### 3.2 Outside the section (Part 2 and sibling lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| §2.5 | `plans.start_points JSON`; `plan_days.gate INTEGER DEFAULT 0`; `plan_overrides.trim INTEGER DEFAULT 0`; `plan_marks.minutes INTEGER`, `plan_marks.note TEXT`; `plan_tasks.type TEXT DEFAULT 'other'`, `plan_tasks.subject TEXT DEFAULT 'math'`; new `plan_snapshots(plan, made_on, days JSON; PK(plan, made_on))`, `plan_events(id, plan, at, kind, field, from_v, to_v, text, day)` and `rw_log(id, learner, at, source, ref, domain, missed, of)`, written by S7. `progress.carry` moves `plan_snapshots`, `plan_events` and `rw_log` with plans and the learner | L1, L9, L10, L11, L15, L21 |
| §2.6 | `task` regex: `^\d{4}-\d{2}-\d{2}:(fix\|recheck\|focus\|extra\|learn\|check\|habit\|pace\|map\|sweep\|test)(:[a-z0-9_]+)?$`. New fields: `run` (YYYY-MM-DD, stored and echoed only); `pins` ([{topic, tier, count 1–4, why?}]; the picker serves those items inside `count`, whether or not the topic is in `topics`); `sibling` (bool, with `from_session` + `only`: serve another template of the same topic and tier, `blueprint.siblings(t, 0)`). Source `plan_preview` with `first {token, answer, ms}` and `count:1` (T1's token check). `rematch` (P18) accepts `task` and `timing` | L2, L3, L6, L8, L10, L14 |
| §2.7 | `plan_auto_focus` bool, default true (Plan step 4, Settings); `plan_auto_drift` bool, default false (Plan, Settings). `words_from` default becomes `[sat, transitions]`, and `math` leaves its values (decision 2; Words owns the change) | L3, L7, L17 |
| §2.8 | Page scope `plan`: `J` `K` `↑` `↓` `Enter` `X` `S` `M` `U` `←` `→` `Shift+←` `Shift+→` `T` `1` `2` `3` `Shift+Enter` | L12 |
| §2.9 | S7 consumes F4 `estimate.gains`, `estimate.route`, `estimate.projection`, `progress.causes`, `progress.warmup_candidates`, `progress.pace`; F5 `habits` (U6); S3 `today.workload`, `today.receipt`; S9 `words.today_summary`, `words.minutes_today`, `bank.words`; S6 `GET /api/session/{id}/compare?with=`. S7 provides `plan.propose` → S3; `plan.today_summary` (which snapshots) → S3; `plan.log_rw` → U2's sheet; `UI.weekPlanner` → S1; `run` and the day's tasks with answered/total → S4, S5, S9 | all |
| shell-me U14 | With an active plan, the sheet hosts S7's `UI.weekPlanner`, and its receipts add the plan's facts. Goal kind `pass_check {topic}` | L16 |
| shell-me U16 | A spare is spent on a missed study day only once the next study day ends with it still missed. A planned day that becomes `made_up` counts as a study day for the streak | L17 |
| shell-me U17 | `prefs.registered == exam_date` and the plan's `cfg.booked` are one fact; setting either sets both | L17 |
| shell-me U18 | Event LOCATION from `cfg.place`; rehearsal events at `cfg.rehearsal_at` | L7, L19 |
| today T2 | `Do them in order` becomes `Start today` (L8) when a plan is active. Today's plan card reads `plan.today_summary()` | L8, L15 |
| today T18 | `Build with these` reads `plan.propose` (L6): its own target and minutes rules are replaced by propose's. The card carries L9's chips | L6, L9 |
| today T13 | The rehearsal option "Bluebook R&W first" moves the Math start to 09:45 | L19 |
| practice P18 | `rematch` bodies may carry `task` and `timing:'pace'`; `scope:'misses'` is used by the plan's Again. `blueprint.siblings(t, 0)`: other templates of the same topic at the same tier (P18's label-then-norms rule at step 0), for the checkpoint's `Fix these` | L3, L10, L14 |
| shell-me U2 | The whole-test sheet adds four optional `missed of` pairs for the R&W domains, saved through `plan.log_rw` with `source:'bluebook'` | L11, L21 |
| §3.3 S4 session | When `cfg.run` is set: the day rail and the in-place interstitial at each block's end; the run's last block ends on T19's receipt | L8 |
| §3.4 S5 | `POST /api/mock/new` twin accepts `task` and `run` (echoed); the day rail in the test page when `run` is set; a per-sitting `pause:false` for rehearsals | L8, L14, L19 |
| §3.5 S6 | The report footer's `Continue today`; the CheckpointCard when the sitting's task is a checkpoint; rehearsal lines (pace by quarter, the last 5 questions) | L8, L14, L19 |
| §3.8 Words | The Plan's Words task is kind `words` with `subject:'rw'` in the Plan's Task model; `words_from` defaults to SAT words and transitions. The today run (`mode:'mix', deck:{source:'today'}`) accepts `box` as any integer 3–60 (the Plan's `w`), `run` and `task` (echoed), and optional `goal` (new words), `transitions` (items, default 2–3) and `in_context` (items, default 1) from L21's R&W focus. With `run` set, its finish reply carries `plan: {tasks, next}` and the runner shows the day rail. `bank.words: {words, transitions, known}` (W17's live count) for the Plan landing | L4, L8, L21 |

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
* **Anything from classes** (experience #13's and unfair-advantage #12's homework task and
  adherence column): decision 5. Classes live on a separate platform.
* **A question count in the TargetNote** (`700 ≈ 37 of 44 right`, U4's `right_of_44`): scoring
  is difficulty-weighted, so the count contradicts the points share beside it (39 of 44), and
  v2's review removed it. The note names the points share and the skills instead (L7).
* **One-sitting verdicts** (a 3/4 After alone, a 4/5 test-out, a checkpoint "beat by 70" on its
  midpoint): the ±70 band and a 4-question sample make them flip on noise. L3, L10 and L13 need
  more evidence or read the band.
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
