# v2 upgrades: the product as a whole

Written 2026-09-23 for `spec/rebuild-v2.md` Part 1, Part 2 (lines 1–648) and Part 4–5 (lines
10970–11183). It merges the three designers' product proposals (outcomes, experience, unfair
advantage: 36 proposals and 46 parity gaps in `spec/v2-upgrades/_proposals/product.json`, cited
as "outcomes #1" and so on, counting from 1) into one build-ready list. It is checked against
`spec/toptierprep-teardown.md`, `ttp-notes.md`, the live walk in `ttp-live.md`, and the seven
section upgrade files already written (`shell-me.md` U1–U28, `today.md` T1–T20, `practice.md`
P1–P25, `tests.md` X1–X23, `reports.md` SR1–SR24, `plan.md` L1–L20, `compete.md` C1–C25).

* **What this file is.** The section files make each section way better. This file owns what no
  section owns: the signature features that cross every section, and the seams where the
  section files disagree. It adds 14 upgrades (G1–G14) and 17 resolutions (R39–R55, numbered
  after Part 2's R1–R38 so every file can cite them).
* **Precedence.** `spec/v2-decisions.md` wins over everything. Then this file's resolutions
  (R39–R55) and G-upgrades, on the seams they name. Then each `spec/v2-upgrades/<section>.md`,
  which wins over its Part 3 section. Then Part 2 (R1–R38 hold except where a section file or
  R39–R55 names a line). §3 of this file lists every line that changes, in the plan and in the
  sibling files.
* **Never re-specified.** Where a sibling file already specifies a piece (Up next U1, points U4,
  levers U13, steps P1, the Desmos way P3, twins' axes P18, the instant check U3, causes T7),
  this file names it and only adds the cross-section rule.
* **The bar.** A student who uses TopTierPrep today opens ours and wants to switch: the day
  starts in one tap and flows across sections without a menu, every question teaches and leads
  to its twin, every number agrees with itself and says how it was worked out, and it is faster
  than their single-page app. Parity is failure.
* **Subject-aware** (decision 3). G11 defines the `subject` axis once; every payload the
  siblings mark "carries `subject`" follows it.
* **Facts measured for this file** (current bank and code, 2026-09-23):
  * **Twins drop the trap.** Over 386 templates, seeds 0–11, 10,916 (item, named-trap) pairs:
    the next seed of the same template does **not** offer the same misconception 44.1% of the
    time with a digits-stripped normaliser (unfair-advantage #1 measured 40.8% with its own).
    Walking up to 60 fresh seeds finds it 98.4% of the time; median walk 1 seed, 90th
    percentile 7; the whole survey regenerates in 2.4 s. Today `drill._pick` repairs with
    `_fresh(b, template, None)` (the next unseen seed, ≤ 12 tried, difficulty only), and
    `progress.record` lowers `owed` on **every** open trap of a template on **any** right
    answer (`server/progress.py` `record`). So a mistake can close on questions that never
    offered it.
  * **Shared traps.** Sampling 8 seeds per template gives 2,246 distinct normalised reasons; 72
    recur in 2 or more templates and 13 across 2 or more topics (the designers counted 79 and
    12 with a finer normaliser).
  * **Figures.** At seed 1, 76 of 386 templates draw a figure and 39 a table. Every figure SVG
    in `satbank/figures.py` and `plot.py` is `role="img"` with no accessible name.
  * **Names.** The plan and the upgrade files name the one idea "same kind of question, new
    numbers" in at least 11 ways ("Another like this" 12, "Another one like this" 11, "Try one
    like this" 10, "Fresh versions" 15, "Try one now" 14, "New one like this" 8, "Practice
    again" 8, …) and the exact replay, the fix and the parallel sitting in 7 more.
  * **Three launchers for one day.** U1's time box (`source:'next', box`), T2's `Do them in
    order`, and L8's `Start today` (plan tasks only, chained from `plan.next`) each start the
    day with their own chain rule. v2 §3.6's task status ticks `fix` and `recheck` only from a
    session tagged with that task, so a time box that fixes three mistakes leaves the plan's
    Fix task `todo`.
  * **Clashes between the upgrade files.** `D` chooses option D and opens Details in the
    practice runner (Part 2 §2.8; `tests.md` fixed it in exam mode only). `source:'warmup'` is
    T3's spaced warm-up and also Compete's contest-lobby drill (`compete.md` §3.2). The cause
    chips differ: `practice.md` P8 keeps `misread` as its own cause, `reports.md` SR8 folds it
    into slip and adds "Rushed" and "Ran long". `plan.md` cites a `type_memory` table and
    "optional chips" that `practice.md` rejected.

---

## 1. Scorecard

One row per TopTierPrep feature of the product as a whole. Section-level inventories are in
each section file's scorecard; rows 38–44 point there. "v2 spec" is `spec/rebuild-v2.md` as
written. "After these upgrades" includes the sibling files and this file.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Price, tiers, quotas | Free: 1 exam attempt, 0 questions from their own bank, 5 new words a day, 1 AI plan a cycle. Pro $13.99, Elite $23.99 a month; usage meters on Subscription and Profile | Everything free; no plans, quotas, paywalls or upgrade prompts; the selling slots show the student's day | The slots they sell from start work: Up next in the sidebar (U1), readiness on Me (U8) | **WAY BETTER.** Everything they meter is unlimited, and nothing on screen sells. |
| 2 | Sign-in | A Google sign-in wall before any page | No wall: anonymous-first, then an email code, pairing or the device code; Google is open question 5 | Passkeys in one tap (U19); a shared computer approved from the phone (U20); **Continue on your phone** carries the open page to a phone by QR (G12) | v2 PARITY for a returning student on a new device (slower than Google; email needs SMTP). **U19 + G12 → WAY BETTER.** |
| 3 | First visit | Wall, then empty cards: "Complete a full-length test to start tracking your score" (134 minutes) | New-student card frames; Up next offers the 20-question diagnostic, whose result waits behind a name-and-email step (R38) | **Start with 8** on Today, question 1 answered in place with no sign-up; afterwards every Today card is about the student; a live sample report (SR24) (G10) | v2 PARITY: the first useful result still cost 20 questions and a form. **G10 → WAY BETTER.** |
| 4 | The one next action | None: plan CTA, QOTD, countdown and score compete | Today §3a's first-match Up next and the Today list | One queue on every page with `G N` (U1); a time box with question 1 on the page (T1); **Start today** over the whole Due list (G1) | **WAY BETTER.** |
| 5 | Doing the day across sections | Dashboard → Full Plan → Start task → a QBank session that never ends → back → Mark done: about 12 clicks, 4 loads, 4 ticks for a 4-task day | Tasks tick from tagged sessions; summaries; finish responses carry `plan.next` | As drafted: 3 launchers with 3 chain rules, and Fix and Warm-up ticked only by their own tagged session. **G1**: one Start today over every Due row (plan, warm-up, words, day's questions, tests), one chain on every finish screen, and plan tasks tick from whatever did the work (R40, R41) | v2 WAY BETTER than theirs but inconsistent across files. **G1 → one loop:** 1 tap, then Enter between parts. |
| 6 | Question sources | College Board Question Bank (1,921 Math) plus their own (3,867 Math): fixed pools that repeat; Free gets none of theirs | Unlimited questions from 386 verified templates; no official items (open question 17) | An official question, by ID or pasted text, becomes its type, named mistake and unlimited twins (U2, P13); readiness weighted by College Board's own mix (U8); each type's page lists the official IDs it was learned from (G7) | **WAY BETTER.** Their pool runs out and repeats; ours never does, and an official question is the way in, not the ceiling. |
| 7 | Reading & Writing | R&W bank (1,848 official + 1,315 theirs), 4-module tests, an R&W question of the day | Math only; Words is R&W vocabulary (decision 2); optional R&W score fields | **G11**: one subject axis, so R&W is additive. Now: R&W vocabulary (Words, Word Sprint C14), Bluebook R&W sittings logged, R&W minutes and own tasks in the plan and streak, the 1600 total | **BELOW parity for R&W practice, by decision 3.** G11 closes what can be closed without a bank, and makes the bank a drop-in: no shared component assumes Math. |
| 8 | Explanation | AI prose "Justification … Distractor Analysis", unverified, after answering only; the QOTD doesn't highlight the key | The key highlighted, a one-sentence rationale (median 21 words), every wrong option's named misconception | Steps on this question's numbers, checked against the key, with the step where your answer left the path (P1); a hint ladder (P2); Learn this type (T4, P2); the same verdict on every surface (G4); steps written in one audited pass (G14) | v2 BELOW on the key's explanation. **P1 + P2 + G4 + G14 → WAY BETTER.** |
| 9 | Another question like this | None: retry the same item, or "More practice" to a list | "Another like this" on every surface under about 11 names; the repair is the same template on the next fresh seed | **Twin** (one verb, one key `T`, G2) that keeps your trap: a 60-seed walk offers it 98.4% of the time instead of about 56% (G3); axes easier, harder, grid-in, same setup (P18); same trap in other types (G3) | v2 WAY BETTER in kind, but its signature promise failed about 2 times in 5 and had 11 names. **G2 + G3 → the promise holds, under one name.** |
| 10 | Mistake loop | toggleRedo exists in their API with no button; "Redo Questions 0"; nothing re-checked | Review: named mistakes, 2 clean answers close, check-ins at 3, 10 and 30 days | A mistake closes only on questions that offered its trap; the 10-day check-in comes on another type with the same trap where one exists (G3) | **WAY BETTER**; G3 makes "Fixed" true. |
| 11 | Score estimate | Only after a full 4-module test; floor sections dropped; red LOW CONFIDENCE with no way to raise it | R16: bands from sittings, confidence with its reason, trend | Points on the table (U4), projection (U9), practice delta (T10), what moves the band (X15, SR21) | **WAY BETTER** (siblings); R48 keeps one pricing rule. |
| 12 | Pricing time | No point value anywhere; "Weakest first" | Mastery bars and accuracy | Every skill, mistake, habit and Up next row priced by one function in one chip, its arithmetic one tap away (U4, G5) | v2 PARITY. **U4 + G5 → WAY BETTER.** |
| 13 | Numbers that agree | Profile streak 0 while the QOTD says 1; wizard target 1400, dashboard 0; gauge "25 Wrong" beside "0 Incorrect / 45 Unanswered"; "13% · 1-8 questions" | Rule 5: one source per fact | Levers on Me (U13); **G6**: every number on every page opens its working, with what was left out, and a gate proves each fact reads the same on every endpoint | v2 PARITY in practice: a rule nobody checks, working shown only on Me. **G6 → WAY BETTER.** |
| 14 | Search | None | Palette: pages, skills, 386 types, misconceptions, actions, parsed sets | Paste a question or an official ID (U2); change anything by typing (U24); open any type's page (G7) | **WAY BETTER.** |
| 15 | Quick add | Draggable "Add your own word" button that covers Next | Quick sheet: quick question, log a mistake, add a word; never floats | Log a mistake by ID, pasted text or a Bluebook test (U2) | **WAY BETTER.** |
| 16 | Report a problem | Modal (title, category, details, 10 × 50 MB images); the student never hears back | One modal, replies, bounded disputes, admin page | Key disputes answered by an independent solver in about a second, quarantine, one fix corrects everyone (U3); Report on every question surface, key `R` (G4, G2) | **WAY BETTER.** |
| 17 | Share and export | `navigator.share` froze the page; shared sessions; "Share / Export Report" has no handler | Sets, progress link, calendar feed, print | Links send twins by default (U28, P22); repair packs (SR20) | **WAY BETTER.** |
| 18 | Speed | Client-routed SPA; cards skeleton-load each visit; a fake plan-building screen | 14+ static pages, each reloading and fetching behind skeletons | Prerender and paint from cache (U23), one round trip per question (P23), and **G9**: the next question pre-rendered, view transitions, budgets measured before merge | v2 BELOW. **G9 → WAY BETTER, measured.** |
| 19 | Phone | Desktop layout squeezed; tools at the top; the vocab button covers Next | 390 px rules, bottom sheets, 5 tabs | Chrome that fits (U26); one thumb-first runner for practice and tests (X6, R50) | **WAY BETTER.** |
| 20 | Keyboard | Arrows in the report player; the overview ignores Esc | One registry and map, but `D` both chooses D and opens Details in the practice runner | One key per verb (`T` twin, `E` again exactly, `R` report on every question), Details on `Q`, `Z` undo, and a registry that refuses a duplicate key (G2, R43) | v2 PARITY with a clash. **G2 → WAY BETTER.** |
| 21 | Accessibility | Figures are images with no text alternative, floated beside the text | Charts carry hidden tables; the bank's figures are unnamed `role="img"` SVGs | Figure descriptions generated from each item's numbers and checked, table headers, MathML kept, Read aloud (G8) | v2 PARITY (both silent on figures). **G8 → WAY BETTER.** |
| 22 | Theme, text size, motion | None | Dark theme, three text sizes, reduced motion | Unchanged | **WAY BETTER.** |
| 23 | Time zone | Calendar in UTC, so an evening's work lands on the wrong day | The learner's local day everywhere (X-Tz, R13) | Unchanged | **WAY BETTER.** |
| 24 | Preferred study time | "Evening", used by nothing | Calendar download or feed with alarms | Reminders that say what is due, at the chosen time (U18) | **WAY BETTER.** |
| 25 | Classes and homework | Hidden `/my-classes` and `/teacher` | `/class/` with codes and assignments | Reach-a-level homework, tailored questions (U27), class twins (X22), class contests (C18, C19) | **WAY BETTER.** |
| 26 | Contests and leaderboards | Tier-gated; empty on the days seen | Free Compete | `compete.md` C1–C25 | **WAY BETTER.** |
| 27 | Achievements | 4 hard-coded tiles; View All has no handler | 43 tiered rules with progress | Go on every badge (U13, C23); the Fixed moment in every verdict (G4) | **WAY BETTER.** |
| 28 | Streak | Two streaks that disagree | One study streak (R13) | Spare days (U16) | **WAY BETTER.** |
| 29 | Desmos | Embedded empty panel | Dock, float, per-sitting state | This question loaded after answering, with the point to read (P3) | **WAY BETTER.** |
| 30 | Reference sheet | Modal | Modal | Which formula this used, and the ones not given (P24) | **WAY BETTER.** |
| 31 | Timer and pace | Stopwatch that resets on reload; Timed or Untimed | Survives reload; 95 s pace | Budgets per tier and type, two passes (P16), a personal pace guide (X3) | **WAY BETTER.** |
| 32 | Question details | ID, domain, skill, difficulty | Template, level, why, permalink | Plus **About this type**: the type's own page (G7) | **WAY BETTER.** |
| 33 | Single-question page `/question/:key` | A route per item (seen in their bundle) | Permalink `?q=TEMPLATE:SEED` as a one-question drill | Links send twins (U28); a public page for each of the 386 types (G7) | **WAY BETTER.** |
| 34 | Content trust | AI prose; keys unchecked; their plan generator failed 3 of 3 | Audited bank with a second solver; plan built on the server | Every new bank field audited before it ships (G14); disputes checked by the solver (U3) | **WAY BETTER.** |
| 35 | Help and FAQ | Six billing questions | `/help/` with search and anchors | A "?" and a working popover beside every number (U13, G6) | **WAY BETTER.** |
| 36 | Toasts and undo | Generic toasts ("Task skipped") | Toasts with actions | An inbox and Undo on every reversible action (U25); `Z` undoes from any page (G2) | **WAY BETTER.** |
| 37 | Empty and loading states | "No completed tests yet."; skeletons on every visit | A frame, a sentence and the filling action; static skeletons | Paint from cache (U23); **G12**: one dimmed sample row of what will appear, and the smallest filling action with its cost, run inside the card | v2 PARITY. **G12 → WAY BETTER.** |
| 38 | Dashboard (section) | Hero, QOTD, study time, plan CTA, score, countdown, recent tests | §3.2 | `today.md` T1–T20 | See `today.md` §1. |
| 39 | Question Bank (section) | Builder with counts and filters; session with retries, Attempts, overview | §3.3 | `practice.md` P1–P25 | See `practice.md` §1. |
| 40 | Practice tests and the runner (section) | Paper grid, start wizard, Bluebook-clone runner, Check Your Work | §3.4 | `tests.md` X1–X23 | See `tests.md` §1. |
| 41 | Results and the score report (section) | Ring gauges, tiles, domain cards, question grid, review modal | §3.5 | `reports.md` SR1–SR24 | See `reports.md` §1. |
| 42 | Study plan (section) | Four-step wizard; plan view recovered from their bundle | §3.6 | `plan.md` L1–L20 | See `plan.md` §1. |
| 43 | Contests, rankings, leaderboards (section) | Contest list, rankings grid, leaderboard | §3.7 | `compete.md` C1–C25 | See `compete.md` §1. |
| 44 | Vocabulary; profile and account (sections) | Library, flashcards, quizzes, My Words; profile cards | §3.8; §3.1 | Words upgrades when merged; `shell-me.md` U1–U28 | See those files. |

---

## 2. Accepted upgrades

### Where each proposal went

Accepted in a sibling means the sibling's version is built and this file adds only the
cross-section rule named in the last column.

| proposal | where | cross-section rule here |
|---|---|---|
| outcomes #1 score engine, practice estimate | points: U4; route line: P10 `estimate.route`; the absolute practice score and predicted-vs-actual: Rejected | R48 |
| outcomes #2 one "what next" engine | U1 `next.queue`, T2 `next.due` | G1, R40 |
| outcomes #3 cause and cure | T7, P8, SR8 | R47 |
| outcomes #4 spaced review of types | T3 warm-up (derived) | R53 |
| outcomes #5 worked example, hints, contrast line | P1, P2, T4 | G4 |
| outcomes #6 pacing trained | P16, U7, X3, T8 | none |
| outcomes #7 fix that transfers and lasts, your rule | transfer check-in: **G3**; your rule: P21 | G3 |
| outcomes #8 skill map with certainty, placement | U5, P11; placement band: Rejected | none |
| outcomes #9 Desmos loaded with the question | P3 | G4 |
| outcomes #10 confidence on every answer | P7 (split Check) | R54 |
| outcomes #11 proof of progress | P9, U14, T19, SR4, SR7; the Fixed moment: **G4** | G4 |
| outcomes #12 reminders | U18 | none |
| experience #1 play today | **G1** | R40, R41 |
| experience #2 worked steps, hint ladder | P1, P2, G14 (bank pass) | G14 |
| experience #3 points on the table | U4 | G5, R48 |
| experience #4 learn any type in a minute | T4, P2; entry from every question: **G4**, **G7** | G4 |
| experience #5 instant by default | U23, P23; budgets and the missing mechanisms: **G9** | G9 |
| experience #6 re-check now | U3 | G4 |
| experience #7 every number explains itself | U13 on Me; everywhere: **G6** | G6 |
| experience #8 the first ten minutes | **G10** | R55 |
| experience #9 one study vocabulary | **G2** | R42, R43 |
| experience #10 thumb-first runner | X6 for both runner modes | R50 |
| experience #11 earned moments | the Fixed moment: **G4**; weekly proof: U14; personal bests: Rejected | G4 |
| experience #12 offline pack | Rejected | none |
| unfair-advantage #1 trap-true twins, one Twin control | **G3**, **G2**, `UI.twin` | R44, R45 |
| unfair-advantage #2 points forecast | U4 | R48 |
| unfair-advantage #3 autopilot | U1's box (5–60 min) and **G1**; the words interstitial: Rejected | R40 |
| unfair-advantage #4 Desmos route | P3, G14 | none |
| unfair-advantage #5 386-type map and a page per type | map: P14, U8; page: **G7** | R52 |
| unfair-advantage #6 paste any question | U2, P13 | none |
| unfair-advantage #7 habit profile | U6 (11 families) | none |
| unfair-advantage #8 first visit, 12 questions | **G10** (8 questions, no band) | R55 |
| unfair-advantage #9 playbook and final week | T13, L19; one sheet: **G13** | none |
| unfair-advantage #10 offline pack | Rejected | none |
| unfair-advantage #11 paper versions for classes | Rejected | none |
| unfair-advantage #12 figures a screen reader can use | **G8**, G14 | none |
| parity gaps (all three) | mapped in the scorecard rows above, or listed in §4 | |

### A. The seams: one decision where the upgrade files disagree (R39–R55)

These rows are appended to Part 2 §2.2 (§3.1 item 12). "Wins" names the text that is canonical.

| # | topic | what disagreed | decision | owner |
|---|---|---|---|---|
| R39 | Precedence | Seven upgrade files each win over their own section, and some specify the same seam | `v2-decisions.md` > R39–R55 and G1–G14 of `product.md` (on the seams they name) > `v2-upgrades/<section>.md` > Part 3 > Part 2. A later upgrade file that needs a seam changed adds a row here in the same commit | I1 |
| R40 | Starting the day | U1/T1 time box, T2 `Do them in order`, L8 `Start today` (plan tasks only, chained from `plan.next`, rail from `GET /api/plan/day`) | **Two starts, named apart.** `Start today` walks the Due list (`next.due`, T2's rows) in its order, one ordinary sitting per row, chained on the client by `UI.run` (G1); the rail reads `/api/today.due`. `Study N min` is U1's box, one mixed session. T2's button and L8's pill are both `Start today`; T1's pill `Start · 15 min` is `Study 15 min`. The challenge and contests are never started by the run | F2 (`UI.run`), S3, S7 |
| R41 | Plan task done | v2 §3.6 ticks `fix` and `recheck` only from a session tagged with that task | A task is done by the work, from any source that day: `fix` when answers on its trap templates ≥ its count; `recheck` when every check-in due that day has been answered once (T2's warm-up rule); `focus` unchanged (attempts on its topics ≥ count). Tagged sessions still tick as before | S7 |
| R42 | Action names | About 11 names for a twin, 7 for the other three ideas | **Six labels for four ideas** (G2): `Twin` (`Twin ×5`, `Twin this set`), `Twin test`, `Again, exactly`, `Fix n`, `Learn this type`. `UI.VERBS` holds each label, helper, glyph and key. `Rematch` (P19, C2) stays its own feature | F1, every page owner |
| R43 | Keys | `D` chooses and opens Details in the practice runner; `U` is undo on Plan and "next unanswered" in the runner; players' `T` is "try one like this" | Runner: `D` only chooses; **Details `Q`**; **Report `R`** (both modes). Players and runner after a verdict: `T` Twin, `Shift+T` its menu. Global (pages with the shell): **`Z` undo** the last reversible change; Plan's `U` becomes `Z`. `UI.keys.register` throws in dev when a scope registers a key twice | F2, F3, S7 |
| R44 | The twin control | T5's `UI.twinSheet`, P18's split button and `/more {axis}`, each consumed by S3, S6, S8, S10 | **One component `UI.twin(anchor, ctx)`** (F3): P18's split button and menu. Inside a running set it appends through `POST /api/drill/{id}/more`; everywhere else it opens T5's `UI.twinSheet` inline (R24). Consumers never build their own twin button | F3 |
| R45 | Which twin | The repair and every "like this" path serve the next fresh seed, which drops the trap about 2 times in 5; any right answer on the template closes every trap on it | **Trap-true** (G3): every twin that follows a miss or a mistake carries `want` from the trap's norm (§2.6, 60 seeds, grid-in `spr_reasons` too). A clean answer lowers a trap's `owed` only when `attempts.offered` holds its norm (or the grid-in's `spr_reasons` do). R9's 10-day check-in uses another template with the same norm when `progress.related(norm)` has one | F5, F4 |
| R46 | Drill source names | `warmup` is T3's spaced warm-up and also Compete's lobby drill | `warmup` means T3 only. Compete's lobby drill (C7) is `source:'prep'` (UI label stays "Warm up"). New: `start` (G10). `learn` (T4), `twin` and `try` (R24) unchanged | F5, S8 |
| R47 | Causes of a miss | P8: six chips with `misread` its own cause; SR8: different labels, misread folded into slip, "Rushed" and "Ran long" added; X: `changed` | **Causes:** `trap`, `slip`, `misread`, `clock`, `entry`, `changed` (tests, automatic), `gap`, first match in T7's order with `changed` first on tests and a student-set `miss_kind` winning. **Chips (P8's six, exactly):** Fell for a trap · Slip: I knew it · Misread the question · Ran out of time · Entered it wrong (grid-ins) · Didn't know how to start. **Letters** for Colour by Cause: T S R C E A G. **R9 kinds:** trap → misconception; slip, misread, clock, entry, changed → slip; gap → unsure | F4, S4, S6 |
| R48 | Pricing | Several proposals add a second points model | **Two functions, two looks.** Practice points on skills, mistakes and habits come only from U4's `estimate.gains`, shown as `≈ +6 pts` (never a range, never a score). A sitting's points come only from exact re-marking (`estimate.rescore`, `estimate.ledger`), shown without `≈` ("+12 on this section"). Nothing else prices points | F4, F1 |
| R49 | The actions on a revealed question | P1, P2, P3, P18, P21, T5, U3, R23, SR16 each add actions on their own surfaces | **One row `UI.questionActions(host, q, ctx)`** (G4) in the verdict slot of every surface that reveals a question, with one order, one set of keys and one access rule | F3 |
| R50 | The runner on a phone | X6 specifies gestures, footer Mark and the answer pad for the test window | X6 is `runner.js`, so it applies to the practice session too, with one guard: in instant feedback no swipe moves on before Check. The practice-only tools (Hint, Eliminate, Calculator, Desmos way, Read aloud) sit in the footer's `⋯` sheet under 760 px | F3 |
| R51 | Subject | Each file says "payloads carry `subject`" in its own way | One axis (G11): `subject` is `math` or `rw`, derived template → topic → subject (no attempts column), default `math`, `?subject=` on every section endpoint, 422 for an unknown subject, `available:false` where no bank exists | F4, every owner |
| R52 | Type states | outcomes: New/Learning/Learned/Kept/Proven; unfair-advantage: Proven; U8 and P14: unmet/met/ready | U8's **unmet · met · ready**, with the overlays open mistake, being fixed and due (P14), are the only type states. R37's words stay for skills | F1, S1, S4 |
| R53 | Spaced returns | Proposals add `type_state`, `boxes`, `skill_memory`; `plan.md` cites a `type_memory` that `practice.md` rejected | T3's derived `progress.warmup_candidates` is the only schedule for types, R9's check-ins the only one for mistakes. No schedule table is added | F4 |
| R54 | Confidence in practice | `plan.md` cites "P7's optional chips"; `practice.md` rejected chips | P7's split Check (`Enter` Sure, `Shift+Enter` Unsure, `I` Guess, a second tap = Sure) is the only practice input; nothing asks an extra tap | F3 |
| R55 | A brand-new student | U1: "Take the diagnostic · 20 q"; T1: the coach's box; proposals: 8 or 12 placement questions | Up next row 0 for a learner with 0 answers is **Start with 8** (G10); the diagnostic is row 2. No practice score or band is shown from it (U4, T10) | F2, F5, S3, S4 |

### B. The day and the loop

#### G1. Start today: one run through the whole Due list, and the plan ticks from whatever did the work

*From: experience #1, unfair-advantage #3, outcomes #2; reconciles U1, T1, T2, L8, L9. Effort M.
Builders: F2 (`UI.run` in `ui.js`), S3 (the Due list header, `/api/today.due`), S7 (the
DayPanel pill, R41's done rules), S4 (session summary), S6 (report footer), S9 (the words run's
`then=run`), S5 (the lobby's `run`).*

**Why.** A 4-task day costs about 12 clicks, 4 page loads and 4 manual ticks on theirs, and
their QBank session never ends. As drafted, ours had three launchers that chained differently:
L8's walked plan tasks only, so Start today skipped the warm-up, the words and the day's
questions; and a Study-15-minutes box that fixed three mistakes left the plan's Fix task
`todo`. One run over the one list, and one done rule, make the whole site one loop.

**Two starts, named apart (R40).**

| start | label | what it does | where |
|---|---|---|---|
| The day | `Start today · 5 parts · 38 min`; mid-run `Continue today · part 2 of 5` | walks the undone Due rows (T2) in order, each its own ordinary sitting, chained | Today's Due list header (replaces `Do them in order`); Plan's DayPanel (L8); the sidebar Today card; the phone thumb bar (L8); palette "start today"; `/?run=1` |
| Some minutes | `Study 15 min` with chips 5 · 15 · 30 · 45 · 60 | one mixed session sized to the time (U1's `box`, T1's blocks) | Today's `#next` (T1, region primary); the Up next popover chips (U1); palette "study 20" |

* Start today is hidden when no row is undone; the Due header then reads `Day done · 42 of 40
  min` and the pill is `Keep going · 15 min` (the box).
* On a rest day the pill reads `Practice anyway · 3 parts`.

**The run (`UI.run`, F2, `ui.js`).**
* `UI.run.start()`: reads `/api/today.due` (fresh), takes the first undone row whose kind is
  not `challenge` or `contest`, and starts it with `run: <local day>`: added to a drill body,
  or as `&run=<day>` on an href (`/test/?s=`, `/words/run/?id=…&then=run`, `/?run=1#qotd`).
* `UI.run.between(host, done, next)`: L8's two-pane interstitial (done part's result on the
  left, the next part on the right), with `Continue ↵`, `.quiet Skip this part` (`S`) and
  `.quiet Stop for now` (`Esc`). Rendered by the S4 session summary, the S6 report footer and
  the S9 words run end, whenever the finished sitting's `cfg.run` (or the page's `run`
  parameter) is today.
* `UI.run.rail(host)`: L8's day rail, one segment per Due row (answered/total from
  `/api/today.due.rows[].progress`), labelled `Today 18 of 38 min`. Shown in the session header
  and the words run header while a run is on.
* State: the server's rows are the truth, so any device continues the same run. Only "Skip this
  part" is local: `sessionStorage satf.run = {day, skipped:[row key]}` (try/catch). Skipping
  moves on without marking the row; it stays undone on Today.
* The day's questions: the run opens Today at `#qotd`; once both are answered, a `Continue
  today` bar appears under them.
* The end: T19's receipt (`/api/today.receipt`), with `Today's challenge · 10 q` when it is
  open (ranked starts keep their own lobby) and `Keep going · 15 min`.

**R41: the plan ticks from any path (S7, §3.6 Task status).** `fix` is done when that day's
answers on its trap templates, from any source, reach its count; `recheck` (shown as Warm-up)
when every check-in due that day has been answered once; `focus` as v2 (attempts on its topics
from any source). So the box, a Review mini-session, a twin sheet on Today and the run all tick
the same plan.

**Data.** No new endpoint or column. `cfg.run` already exists (L8, §2.6). `/api/today.due.rows`
already carries `start`, `progress` and `status` (T2). S9's run page accepts `then=run`; S5's
lobby passes `run` into the sitting's cfg.

**Acceptance.**
1. Learner `a:v2revprodrun` with a plan day (fix 4, focus 10), 2 check-ins due, 12 words due
   and the QOTD unanswered: `/api/today.due.rows | map(.kind)` begins with two `plan` rows,
   then `warmup`, then `words`, then the day's-questions row. Start today creates a session with `cfg.run == <today>` and
   `cfg.task` equal to the fix task's id.
2. Finishing it shows the interstitial naming "Focus"; after the focus part it names
   "Warm-up"; after the warm-up the run opens `/words/run/?…&then=run`; the words run's end
   shows the interstitial naming "Day's questions".
3. A `Study 15 min` session that answers 4 questions on the fix task's trap templates:
   `GET /api/plan` shows that fix task `done`, with no session tagged with it.
4. The challenge row is never started by `UI.run.start()`; the receipt offers it.
5. After part 1 on desktop, `/?run=1` on a second device paired to the learner starts part 2.
6. `grep -rn "Do them in order" web/` is empty, and `#next`'s pill text starts "Study".

#### G10. The first ten minutes fill the whole product

*From: experience #8, unfair-advantage #8; resolves U1's brand-new row (R55). Effort S.
Builders: F5 (`source:'start'`), F2 (`next.queue` kind `start`), S3 (T1's block for a new
learner), S4 (the summary variant), S7 (the SourceNote), S6 (the sample report link, SR24).*

**Why.** Theirs opens with a Google wall, then empty cards that ask for a 134-minute test. The
v2 start was a 20-question diagnostic whose result sits behind a form. Eight questions on the
first screen, with the first answered in place, make every card on Today about the student in
ten minutes, without an account and without inventing a score.

**Up next (F2).** For a learner with 0 answers, `next.queue` row 0 is kind `start`: title
`Start with 8 questions`, detail `One from each part of SAT Math, then four that adapt to you ·
about 10 min · no sign-up`, start `{source:'start'}`. Row 2 is the diagnostic (`Take the
diagnostic · 20 q · a score range`). Once the start set is finished, or 8 answers exist, the
row is gone; an unfinished one reads `Resume · 3 of 8`.

**On Today (S3, T1's mechanism).** The box shows one block, `1  Start with 8 · one from each
part of SAT Math · 8 q · ~10 min`, and question 1 inline (T1's preview token, with
`source:'start'`), so the first Check creates the session. The time seg is hidden for this
block. F5 accepts T1's `first {token, answer, ms}` with `source:'start'`.

**The set (F5).** `POST /api/drill {source:'start'}`: `count` 8, untimed, instant feedback,
repairs next.
* Questions 1–4: one **medium** question per domain, in the order Algebra, Advanced Math,
  Problem-Solving & Data Analysis, Geometry & Trigonometry, each from the domain's
  highest-weight skill (U8's weight), a random template of it.
* Questions 5–8: R33's step (up after a right, down after a miss, `blueprint.siblings` where a
  template has one tier), drawn by blueprint domain weight (15 / 15 / 7 / 7), the domain of the
  first miss first.
* A miss's repair is a trap-true twin (G3), so the first mistake is already being fixed.

**Summary variant (S4, `cfg.source == 'start'`).**
* `Where you are after 8 · rough`: four domain rows, each with R37's word, "2 of 2" and U5's
  rough rung. No score, band or percentile.
* The named mistakes opened, with `Fix now · n` (pool redo, trap-true).
* The primary: `Next: {U1 item}`.
* `Want a score range? One module · 22 q · 35 min` (the lobby) and `See what a test report
  shows` (SR24's sample).
* A quiet, non-blocking `Save your progress` (U19).

**Afterwards.** Today's Review card lists the mistakes, the study card shows the minutes, the
streak reads `Day 1`, and Plan's SourceNote reads `8 practice answers · take a module for a
real start` (S7).

**Acceptance.**
1. New learner `a:v2revprodnew`: `GET /api/next` → `items[0].kind == 'start'`, and
   `items[1]` starts the diagnostic.
2. `POST /api/drill {source:'start'}`: the first 4 served questions are `medium` and map to 4
   distinct domains; after two rights in a row, question 7's tier is above question 6's or its
   template is a harder sibling.
3. The finish payload has no `band`, `score` or `percentile` key.
4. After finishing with one miss: `/api/today` shows that trap in the Review card,
   `study.today > 0` and `streak == 1`; `GET /api/next` has no `start` row.
5. Playwright at 390 on `/` for a new learner: the first option and Check are on screen without
   scrolling; Check sends one `POST /api/drill` whose `cfg.source == 'start'`.

### C. One question, everywhere

#### G2. One study vocabulary: six labels for four ideas, one glyph and one key each

*From: experience #9, unfair-advantage #1 (point 4). Effort S. Builders: F1 (`UI.VERBS`,
`UI.verb`), F2 (`UI.keys` duplicate check, `Z`), F3 (runner and player maps), every page owner
(copy), I1 (the copy gate).*

**Why.** Our signature is "the same kind of question with new numbers, whenever you want". With
about 11 names for it and 7 more for its neighbours, a student never learns it as a habit.
Theirs has two generic actions because a fixed bank can't do more. One vocabulary and one key
make ours the reflex: `T` after any question, on any page.

**The verbs (`UI.VERBS`, F1 `kit.js`).**

| id | label | means | helper (tooltip, `?` sheet, first use on a page) | key | glyph |
|---|---|---|---|---|---|
| `twin` | `Twin` · `Twin ×5` · `Twin ▾` | the same kind of question, new numbers, with your trap when you missed (G3) | "Same kind of question, new numbers. Counts toward mastery." | `T`, menu `Shift+T` | two offset squares |
| `twin_set` | `Twin this set` | a set of the same types, new numbers | "The same question types, new numbers." | none | two offset squares |
| `twin_test` | `Twin test` | a sitting with the same slots, new numbers, scored like any test (T16, X20) | "Same question types in the same places, new numbers, scored like any test." | none | two offset squares + clock |
| `again` | `Again, exactly` | the same question | "The same question again. Doesn't move mastery." | `E` (players, lists; never in a running set, where `E` eliminates) | ↺ |
| `fix` | `Fix n` | a set on open mistakes, each a twin that keeps its trap | "Two clean answers on questions with that trap close each mistake." | `F` on report and Review pages | ↻ (the Repaired mark, §2.3) |
| `learn` | `Learn this type` | a worked example on reserved numbers, then three of your own (T4, P2) | "See one solved, then try three yourself. Counts toward mastery." | in the Twin menu | open book |

* `UI.verb(id, {count, onClick, href})` renders a `.btn` (or the region's pill) with the glyph,
  the label and a `title` that names the key.
* Retired phrases (every surface, every file): "Another like this", "Another one like this",
  "Try one like this", "Try one now", "Fresh one like this", "New one like this", "N more like
  this", "Fresh versions", "Again · new questions", "Practice again", "Retake as a test",
  "Retake as twin", "Redo these", "Fix these", "Drill it". A set of the same **topics** (not
  types) reads plainly, `10 more · Circles`.

**Keys (R43).**
* Runner (practice session and test window): `D` only chooses D; **`Q` Details** (practice);
  **`R` Report** (both modes; in exam mode R17's live categories); `T` / `Shift+T` Twin after a
  verdict (practice, P18).
* Players (report review, Review pane, challenge and contest review): `T` Twin, `Shift+T` its
  menu; the rest of §2.8's player row stays.
* Global (pages with the shell): **`Z`** presses the Undo of the most recent reversible toast
  while it shows (U25). Plan's page `U` becomes `Z`.
* `UI.keys.register(scope, map)` throws `Error('key T already in runner')` when `location.
  pathname` starts `/dev/` and a scope registers a key twice; in production it logs once.

**Acceptance.**
1. `grep -rniE "another (one )?like this|try one (like this|now)|(fresh|new) one like this|[0-9]+ more like this|fresh versions|again · new questions|practice again|retake as (a test|twin)|redo these|fix these|drill it" web/`
   is empty.
2. `UI.VERBS` has `twin, twin_set, twin_test, again, fix, learn`, each with `label`, `helper`,
   `icon`; every rendered `.verb` with a key has a `title` containing it.
3. Practice runner at 1280: `D` selects option D and opens nothing; `Q` opens Details; `R`
   opens `UI.report` with `ctx.question_id` set.
4. Unsave a question, then press `Z` while the toast shows: `GET /api/saved` contains it again.
5. On `/plan/`, `Z` undoes a skip; `U` does nothing.
6. On `/dev/workspace.html`, registering `T` twice in scope `runner` throws.

#### G3. Twins that keep your trap, and a mistake that closes only on questions that offered it

*From: unfair-advantage #1, outcomes #7 (transfer). Effort M. Builders: F5 (`want` walk, every
twin path), F4 (`progress.record`'s close rule, R9's transfer check-in), F3 (the fallback line),
S10 (Fixed row copy), T-bank (`spr_reasons`, G14).*

**Why.** "Another one like this, with your trap" is the promise no fixed bank can make. Measured
today, the next fresh seed drops the student's trap 44.1% of the time, and a mistake closes on
any right answer to its template, trap on offer or not. So the promise fails about 2 times in 5,
and "Fixed" can mean the student never met the trap again. A 60-seed walk finds it 98.4% of the
time (median 1 seed, 90th percentile 7), at about 0.26 ms a seed.

**Rules (R45).**
1. **One mechanism: `want`** (§2.6). F5 raises its walk from 40 to 60 seeds, matches
   `progress.norm(reason)` of each MC option and each grid-in `spr_reasons` value, skips seeds
   the learner has attempts on, and starts from the learner's cursor for that template.
2. **Every twin of a miss sets it.** With `want = {template: '^' + re.escape(norm) + '$'}` from
   the trap: the repair after a miss (`drill._pick`'s `rep`), pools `redo` and `checks`,
   `from_session` twins (T5, SR, X16), `like` (a missed day's question), `/more {axis:'same'}`
   (P18), U28 links when the sender missed, the start set's repairs (G10), and `UI.twin` from
   any surface. Compete's `rematch scope:'misses'` already does it (C2). After a right answer
   there is no `want`: a plain twin.
3. **Fallback.** Nothing in 60 seeds → the plain next seed, `feedback.trap_true = false`, and
   one line above the stem: `This type didn't offer that trap again; here's the closest.`
4. **Close rule** (F4, `progress.record`, R9). A clean answer lowers a trap's `owed` only when
   `attempts.offered` (P6) contains the trap's norm, or the grid-in item's `spr_reasons` do.
   Other clean answers on the template count for mastery and nothing else. The verdict's next
   step (P9) reads `This one didn't offer "used the diameter" · 1 still to close it` in that
   case.
5. **Transfer check-in** (R9). The 10-day check-in is served from another template whose items
   offer the same norm when `progress.related(norm)` has one (about 72 norms recur across
   templates, 13 across topics), with `want` on it; otherwise the trap's own template. Passing
   both remaining check-ins then sets `closed_how = 'transfer'`, and Review's Fixed row reads
   `Held on another type: {type name}`. A miss there reopens it as Relapsed: `It came back on
   {type name}`.
6. **Same trap, other types.** When `progress.related(norm)` has other templates, `UI.twin`'s
   menu shows `Same trap, other types · n`: `POST /api/drill {templates:[…], want:{t: re, …},
   count:5, source:'twin'}` (inline, R24).

**Acceptance.**
1. `server/checks/f5.py`: for 200 random (template, seed, reason) with a named reason, a drill
   whose first answer picks that reason serves a repair whose options' norms contain it in at
   least 95% of cases, each found within 60 seeds.
2. A learner misses template t picking reason r (trap owed 2), then answers right a fresh t item
   whose `offered` lacks norm(r): the trap's `owed` is still 2. A right answer on an item
   offering r → `owed == 1`.
3. `POST /api/drill/{id}/more {question_id, axis:'same'}` after that miss → the next item's
   `offered` contains norm(r).
4. A trap whose norm recurs on template u: the 10-day check-in's template is u and its
   `offered` contains the norm; passing the remaining check-ins → `traps.closed_how ==
   'transfer'`.
5. With `spr_reasons` present on a grid-in template, a typed wrong value naming r → the
   repair's `spr_reasons` contain r.
6. A forced fallback (monkeypatched walk of 0) → `feedback.trap_true == false`, and the stem
   line is shown.

#### G4. One question, one action row, on every surface

*From: experience #4, #6, #11; outcomes #5, #9, #11; unfair-advantage #1 and the explanation
gaps. Effort M. Builders: F3 (`UI.questionActions`, the verdict slot, `UI.twin`), F5 (feedback
`closed` detail), F2 (the nav count tick), every surface owner (one call each).*

**Why.** The upgrades give a revealed question about ten actions (twin and its axes, learn,
steps, the Desmos way, save, mark, history, your rule, report, about this type), specified in
eight places for eight surfaces. Built separately, the same question would offer different
actions in a different order on Today, in the report and in Review. One row, one order and one
set of keys make every surface feel like one product, and the moment a mistake closes shows the
same way wherever it happens.

**The verdict slot (F3, `question.js`), top to bottom**, in every mode that reveals:
1. Verdict and key (R20 glyphs); your answer and the key.
2. **Fixed**, when `feedback.closed` has a trap: `Fixed · used the diameter as the radius ·
   caught you 3× since Sep 12 · 6 days, 5 questions`, with one 200 ms scale-in (none under
   reduced motion). The sidebar Review meta and the phone chip decrement in place
   (`UI.refresh()`).
3. The named mistake of your pick; P6's traps on offer; P8's cause chips (R47).
4. P9's next step or then-vs-now line.
5. Steps (P1), open on a miss; the rationale.
6. **The action row** (`UI.questionActions`).

**The row, in order** (wraps on a phone; an action is absent, not disabled, when not allowed):

| # | action | key | notes |
|---|---|---|---|
| 1 | `Twin ▾` (`UI.twin`, R44) | `T`, `Shift+T` | the region's primary after a miss; `.btn` after a right answer, where Next is primary in the runner. Menu: Twin · Easier · Harder · As a grid-in · Same setup, a different question (P18, only supported axes) · Same trap, other types · n (G3) · Twin ×5 · Learn this type (T4) · Print 10 with key (a `source:'worksheet'` drill, then `?print=1`) |
| 2 | `Desmos way` (P3) | `Shift+G` | only when the type has a verified route |
| 3 | `Save` | `B` | |
| 4 | `Mark` | `M` | only inside a sitting |
| 5 | `Note` / `My rule` (P21) | `O` | |
| 6 | `History` (`UI.history`) | `Y` | |
| 7 | `Again, exactly` | `E` | players and lists only |
| 8 | `About this type` | none | the type's page (G7) |
| 9 | `Report` (U3's instant check) | `R` | |

**Context.** `ctx = {surface: 'runner'|'player'|'pane'|'inline'|'type', session, question_id,
template, seed, trap_id, live, revealed}`. `ctx.live` (a test or contest in progress): only
Mark, Note and Report ("Remind me after the test") render; an unanswered challenge item renders
none (R19).

**Surfaces and owners** (each calls `UI.questionActions` once): the practice verdict (S4), the
report player (S6), the Review pane (S10), Today's twin sheet and questions of the day (S3), the
challenge and contest review (S8), the type page example (G7, S4), the quick sheet's quick
question (F2).

**Acceptance.**
1. `web/dev/workspace.html`: an MC miss revealed in practice, review, inline and pane modes gives
   identical button labels in identical order.
2. In a live test at 1280, the question strip's DOM has no Twin, Desmos or History control.
3. A right answer that closes a trap shows a line starting "Fixed ·", and the sidebar Review
   meta drops by 1 without a reload.
4. `grep -rln "twinSheet(" web/` lists only `web/assets/question.js` (callers go through
   `UI.twin`).

#### G7. A home for every question type: `/types/?t=`

*From: unfair-advantage #5, experience #4. Effort M. Builders: F5 (`GET /api/types/{t}` in
`api_bank.py`), S4 (`web/types/**`), every surface (links: G4's About this type, the palette,
P14's map, S6's skill panel, S10's family strip, S7's Why, U2's match results).*

**Why.** Everything we know about a question type is spread over a map popover, the Details
popover, Learn it, the traps sheet, the history modal and the official-ID match. Theirs stops at
29 skills with no lessons. One page per type, public and linkable, is where a student, a parent
or a teacher sees what the type asks, one solved, every trap it sets, your record and the way in.

**Page** (`/types/?t=circles.arc`, S4, one column 760 px; wide screens add a right
column for "You"):
* **Header**: the type's name and about line (the docstring's first sentence); skill → domain;
  formats and tiers; weight (`about 1 in 30 questions on SAT Math`, U8's weight); `Learned from
  9 College Board questions` with their IDs (U2's map; IDs only, never text).
* **Worked example** (`GET /api/types/{t}/example`, reserved seeds ≥ 900000): stem and figure,
  the key, every wrong option with its misconception, steps (P1) and the Desmos way (P3) when
  present; `.quiet Another example`.
* **Actions**: `Learn this type` (T4's body, primary), `Twin ×5` (inline), `Practise timed · 10`
  (P16 budgets), `Print 10 with key`, `Copy link`.
* **The traps it sets**: every reason the type produces (`/api/types` reasons), each with the
  field's share of misses on this type (shown when n ≥ 20, else "not enough answers yet"), your
  caught and dodged counts (P6), and `Spot it` (S10's spot pool, called defensively).
* **You** (only with a learner): U8 state and due, R23's history with P9's trend line, your
  median against the budget (P16), your rule (P21, editable), open mistakes on this type with
  `Fix n`.
* **Related**: easier and harder siblings (`blueprint.siblings`), and types with the same traps
  (`progress.related`).

**Endpoint (F5).** `GET /api/types/{t}` → `{template, name, about, topic, domain, subject,
formats, tiers, weight, official:[cb_id], reasons:[{norm, label, crowd_share}], has:{steps,
desmos}, siblings:{easier, harder}, related:[t]}`, public and cached per deploy; with
`X-Learner` it adds `you:{state, due, median_ms, budget_ms, rule, open:[trap id], caught,
dodged}` (read from the existing functions). History stays `GET /api/types/{t}/history` (P9).

**Entry.** G4's About this type; the palette's type rows (Enter runs a set, `Shift+Enter` opens
the page); P14's map cell popover; the Log-a-mistake type rows; S6's skill panel type list; S10's
family strip; S7's task Why; U2's match cards.

**Acceptance.**
1. For all 386 templates, `GET /api/types/{t}` is 200 and has `name`, `about` and `weight`.
2. No public payload contains `answer` except the example, whose `seed >= 900000`.
3. Without `X-Learner` there is no `you` key; with one there is.
4. Details → About this type on a practice question opens `/types/?t=<its template>`.
5. At 390, `document.documentElement.scrollWidth === 390`.

### D. Numbers you can trust

#### G5. One points number, one chip

*From: experience #3, unfair-advantage #2, outcomes #1. Effort S. Builders: F1 (`UI.pts`), every
page that shows points.*

**Why.** Points on the table (U4) are the unit students think in. Three proposals added their own
model, and a sitting's exact re-score (SR1) is a second, different number. Two looks keep them
apart, and one chip keeps each identical everywhere (R48).

* `UI.pts(el, pts, key)` (F1 `kit.js`): DM Mono 12 px, `--soft`, `≈ +6 pts`; never orange;
  nothing when `pts` is null; a button that opens `UI.fact(key)` (G6) with the arithmetic.
  `key` is `skill:<topic>`, `trap:<id>` or `habit:<id>`.
* A sitting's exact figures render without `≈`: `+12 on this section` (SR1's ledger).
* Users: Up next metas (U1), Today `#gain` and Due Why (T6, T2), the Review card and Redo's
  `Most points` sort (S10), Results skills (S6), the builder (P10), Plan's Why (L1), the palette.

**Acceptance.**
1. For a seeded learner with an open trap id X: its `pts` is equal in `GET /api/next`, the Review
   list payload and `/api/today`'s Review card (G6's gate covers it).
2. On a seeded report, no `.ledger` element contains `≈`, and every `.pts` chip does.

#### G6. Every number opens its working, on every page, and reads the same everywhere

*From: experience #7; extends U13. Effort M. Builders: S1 (`GET /api/levers`), F1 (`UI.fact`),
F2 (delegation), every page owner (`data-fact`), I1 (the gate).*

**Why.** Their numbers contradict each other on the same page. Ours come from one function each
(rule 5), but nothing proves it, and U13's working is only on Me. A student who can open any
number and see the rows behind it trusts the advice built on it.

**Server (S1, `api_profile.py`).** `GET /api/levers?keys=streak,open_mistakes,skill:circles` (up
to 20 keys) serves U13's `levers(learner, tz, keys)` to any page. Each lever: `{value, how, help,
inputs:[…], excluded:[{label, n}], next, start?, same_on:[page]}`. Keys beyond U13's: `points`,
`open_mistakes`, `band`, `percentile:<sid>`, `rank:<metric>:<period>` (from S8), `pace:<topic>`,
`readiness`, `accuracy:<topic>:<days>`, `minutes:<today|week|month>`. Each calls the function the
page's own payload uses. `excluded` names what was left out: `14 exact repeats · 3 disputed · 4
right guesses count half`.

**Client.** `UI.fact(el, key)` (F1): a button with a dotted underline on hover-capable pointers
(nothing on touch), opening a `UI.pop` (a bottom sheet under 760 px) with How · Your numbers ·
Left out · What moves it · `Same number on: Today · Me · Results`. F2 delegates: any element
with `data-fact="<key>"` opens it on click or Enter, so pages only add the attribute. Used on
every stat tile, chip and meta: Today's hero chips, Me's tiles, nav-meta tooltips, score cards,
skill rows, report tiles, Plan's stat tiles, your Compete row.

**The gate (I1, `tools/product_gates.py facts`).** For three seeded learners (new, mid, heavy)
it fetches `/api/shell`, `/api/today`, `/api/today/insights`, `/api/me/summary`, `/api/plan`,
`/api/review/counts`, `/api/stats`, `/api/next` and compares a table of (fact, endpoint, JSON
path): study streak, open mistakes, minutes today, target, exam date, points total, the top
skill's points, one trap's points, the estimate band, active days. It exits non-zero naming the
fact and both values. It runs in I1's walk.

**Acceptance.**
1. `GET /api/levers?keys=streak,open_mistakes` → both keys with `how` and non-empty `inputs`.
2. On `/`, `/results/`, `/plan/` and `/compete/`, every `[data-fact]` opens a popover on Enter;
   Esc closes it and returns focus.
3. `accuracy:<topic>:30`'s `excluded` lists repeats and disputed answers with counts for a
   learner who has both.
4. The gate passes on the seeded learners; with the shell's streak patched to +1, it fails and
   names `streak`.

### E. Reach and speed

#### G8. Figures, tables and math that a screen reader can use, and Read aloud

*From: unfair-advantage #12. Effort M. Builders: T-bank (`Item.figure_alt`, in G14's pass), F5
(`to_question` passes it), F3 (figure, table and math markup; the Read aloud tool), S9
(`UI.speak`, called defensively).*

**Why.** Their figures are images with no text alternative. Ours are drawn from known numbers,
so each can say exactly what it shows, which serves students with low vision and anyone studying
by ear. Today 76 of 386 templates draw a figure, all unnamed.

* **Figures.** Each figure builder (`satbank/figures.py`, `plot.py`, `shapes.py`) returns
  `figure_alt` from its own params, e.g. `Circle with center O. Points A, G and P lie on the
  circle. Arc AGP measures 108 degrees.` The audit (G14) fails a family whose alt misses a drawn
  label or a given number. F3 renders `<figure role="img" aria-label="{figure_alt}">` with the
  inner SVG `aria-hidden="true"`; a missing alt reads `Figure for this question` and is counted
  by the coverage script.
* **Tables.** Row 0 becomes `<th scope="col">`; a visually hidden `<caption>` reads `Table for
  question N`.
* **Math.** Every KaTeX call keeps `output: 'htmlAndMathml'` (KaTeX's default), so screen
  readers read MathML. F3's one render helper is the only caller.
* **Read aloud.** A tool in the strip's `⋯` (practice, review, type pages) reads the plain stem,
  then the figure's alt, then `A, …` through `UI.speak` (speechSynthesis), with a small spoken-
  math map (π "pi", ² "squared", √ "the square root of", a/b "a over b", ≤ "is at most", −
  "minus"). In the test window it appears only with `test_timing` x1.5 or x2, as Bluebook
  offers text-to-speech only as an accommodation. `ponytail:` a 12-rule replacer, not MathSpeak;
  move to Speech Rule Engine if students report misreads.

**Acceptance.**
1. `tools/bank_coverage.py` prints a `figure_alt` line (`n of 76 figure templates`), and the
   audit passes for every topic committed.
2. Playwright on a figure question: `.q-figure[role=img]` has a non-empty `aria-label`; a table
   question has as many `th` as columns; a KaTeX stem contains a `math` element.
3. With `speechSynthesis.speak` stubbed, Read aloud on a π stem passes text containing "pi".
4. On `/test/` with `test_timing: 'official'`, no Read aloud control exists.

#### G9. Speed budgets, measured before merge

*From: experience #5. Effort M. Builders: F3 (pre-render), F1 (view transitions), F2 (optimistic
toggles), I1 (`tools/product_gates.py perf`).*

**Why.** Theirs is a single-page app, so its route changes are quick after the first load. Ours
is 14+ pages that reload. U23 (prerender, paint from cache) and P23 (one round trip per question)
cover most of it; three mechanisms are missing, and nothing measures any of it.

**Mechanisms added.**
* **Next with no wait (F3).** While the verdict shows, the `next` that P23's answer returns is
  rendered (KaTeX, figure) into a hidden node; Next swaps nodes.
* **View transitions (F1, `ui.css`).** `@view-transition { navigation: auto; }`, a 120 ms fade of
  `main` only, the sidebar pinned with `view-transition-name: side`. Off under
  `prefers-reduced-motion` and `html[data-motion="reduce"]`. Browsers without support ignore it.
* **Optimistic toggles (F2, `UI.api`).** Save, Mark, Unsave, Unmark and prefs switches flip at
  once and revert with a toast on failure.

**Budgets** (added to §2.1 as rule 13):

| moment | budget | measured as |
|---|---|---|
| Check → verdict painted | ≤ 100 ms p95 over 20 answers, local | click to the verdict node's first paint |
| Next → next stem painted | ≤ 50 ms p95, no request before paint | click to paint; network log |
| Revisit of a shell page | cached content ≤ 150 ms from navigation start (U23) | first non-skeleton card paint |
| Today, first visit, mobile throttling (150 ms RTT, 1.6 Mbps, 4× CPU) | LCP ≤ 2.5 s | PerformanceObserver `largest-contentful-paint` under DevTools throttling |
| Layout shift as data arrives | CLS ≤ 0.02 | PerformanceObserver `layout-shift` |

**The gate.** `tools/product_gates.py perf` runs Playwright (as `shot.py` does) against a local
server with a seeded heavy learner, three runs, median; it fails when a budget is missed on two
consecutive runs.

**Acceptance.**
1. The gate passes at I1.
2. With a 200 ms sleep injected into the answer route, it fails on "Check → verdict".
3. After Check in the practice runner, the network log shows no request between the Next click
   and the next stem's paint.

#### G12. Conveniences everywhere: empty states that show what will appear, and Continue on your phone

*From: the experience empty-state and sign-in gaps. Effort S. Builders: F1 (`UI.empty`), every
card owner, S1 (`go` on the pair page), F2 (the account-menu row and palette command).*

**Why.** Decision 4: whatever makes the site clearer or more convenient belongs. An empty card
that shows one row of exactly what will appear, and fills itself in four minutes without leaving
the page, is clearer than a sentence. A student mid-set on a school laptop who has to leave
should be able to carry the open page to a phone in one scan.

**Empty states (`UI.empty(host, {sample, text, action})`, F1 `kit.js`).**
* `sample`: one row built with the real row component and fixture data (a mistake row with its
  pips and pts chip, a sitting card, a word row), at 55% opacity, `aria-hidden`.
* `text`: what will appear here (rule 1).
* `action`: the smallest filling action with its cost, `{label, cost, body | href, inline}`, e.g.
  `Answer 3 questions · about 4 min`. `inline: true` runs it inside the card (`UI.twinSheet` or an
  inline drill) and re-renders the card when done.
* Used by every card's empty state (Today, Me, Review tabs, Results, Plan Progress, Compete
  history, Words).

**Continue on your phone.** An account-menu row and the palette command `continue on phone`
open a sheet that calls the existing `POST /api/pair` (Shell §5) and shows a QR (`qr.js`) of
`/pair/?c=<code>&go=<current path and query>`. The phone opens it and sends
`POST /api/pair/request`; the laptop's open sheet shows the request with one `Allow`; the phone
claims and lands on `go`: a practice set reopens at its question, a test through its lobby. A
phone that already holds this learner skips pairing and goes straight to `go`. The pair page
follows `go` only when it starts with a single `/` and not `/admin/`, `/api/` or `/signin/`;
otherwise it lands on `/`. No server change beyond the page.

**Acceptance.**
1. A new learner's Review card renders one `.empty-sample` with `aria-hidden="true"` and an action
   whose label contains "min".
2. Its inline action answers 3 questions in the card and the card then lists the mistakes made.
3. After pairing, `/pair/?c=…&go=/practice/session/?id=X` lands on that session; `go=//evil.example`
   and `go=/admin/reports/` land on `/`.

### F. The whole SAT and the bank

#### G11. The subject axis: the full SAT is additive

*From: the Reading & Writing gaps of all three designers, decision 3. Effort S. Builders: F4
(`deps.subject_of`, validation), every owner (their payloads and endpoints), S6 (the R&W row),
S9 (Words skill tags), S7 (R&W tasks).*

**Why.** Decision 3: Math-first now, the full SAT later, built so the expansion is additive.
Every upgrade file says its payloads "carry `subject`", each in its own way. One contract now
costs little; seven dialects would have to be torn out.

**Contract (R51).**
* `subject` is `math` or `rw`. `deps.subject_of(topic)` (F4) maps the 19 Math topics to `math`;
  R&W topics join the same map with the R&W bank.
* No `attempts.subject` column: a row's subject is template → topic → subject. Sessions carry
  `cfg.subject` (default `math`). Words runs, word reviews, R&W own tasks (L11), `rw_now` /
  `rw_target`, `outside_scores.rw` and `contests.subject` (C14) are `rw`.
* Every section endpoint takes `?subject=`, default `math`; an unknown value → 422. Where no bank
  exists: `/api/bank?subject=rw` and `/api/types?subject=rw` → 200 `{subject:'rw', available:
  false}`; `POST /api/drill {subject:'rw'}` and `POST /api/mock/new {subject:'rw'}` → 409
  `{reason:'no_bank'}`.
* Shared components take labels from data (`UI.SUBJECT[subject].label`), never a literal "Math";
  the runner keeps its empty passage region (tests.md); P15's subject switch stays hidden while
  one subject has a bank.

**What students see now.**
* Results gains a **Reading & Writing** row: Words (known, due, Word Sprint rating, C14), the
  R&W skills Words practises (Words in Context, Transitions), logged Bluebook or official R&W
  scores (`outside_scores`), and the 1600 total when both sections have a score (R16's
  combined).
* Today's study time and the streak already count Words (R13); Plan's R&W own tasks count toward
  the day (L11).

**Acceptance.**
1. `GET /api/bank?subject=rw` → 200 with `available == false`; `?subject=xx` → 422.
2. `POST /api/drill {subject:'rw'}` → 409 `no_bank`.
3. `GET /api/next`, `/api/today/insights` and `/api/plan` items carry `subject`.
4. `grep -n "'Math'\|\"Math\"" web/assets/ui.js web/assets/kit.js web/assets/question.js web/assets/runner.js`
   returns only the `UI.SUBJECT` table.
5. A learner with a logged R&W 610 and a Math band: Results shows the R&W row and a 1600 total.

#### G13. One sheet before the test

*From: unfair-advantage #9. Effort S. Builders: S7 (the page, from L19's trap sheet), with data
from P21, P16, P3, T7, T13.*

**Why.** The last week's advice is spread over five places. One printable page of your own traps,
rules, skips, Desmos types and grid-in slips is what a tutor would hand a student on the eve.

* L19's trap sheet becomes **Your test-day sheet**, at `/plan/?print=sheet` (it works without a
  plan), readable on a phone and printable (A4 or Letter, 11 pt; a second page when long; nothing
  cut, ordered by value):
  1. Your traps (L19's up to 10 entries, each with its worked example).
  2. Your rules (P21's type rules, by domain).
  3. Skip first: types whose median is over 1.5× the budget and first-try accuracy under 50%,
     top 5 by U8 weight (P16).
  4. Use Desmos on: types with a verified route where your hand median is over 60 s (P3).
  5. Grid-in rules you broke (T7's `entry` items, grouped by rule).
  6. The test-day checklist (T13).
* Linked from T13's final stretch, L19's eve task (`Read your test-day sheet · 5 min`), Me, and
  SR17's lobby briefing.

**Acceptance.**
1. `GET /api/plan/sheet` for a seeded learner returns six sections, each a list (empty lists
   allowed) and no answer keys other than reserved-seed examples.
2. `/plan/?print=sheet` renders for a learner with no plan.

#### G14. One pass through the bank: every new field per family, audited, one coverage report

*From: experience #2, unfair-advantage #4, #12; the T-bank asks of P1, P3, P4, P18 and G8. Effort
L (it grows). Builder: T-bank.*

**Why.** Four upgrade files each ask T-bank for a field (grid-in mistakes, steps with the step
each mistake breaks, the Desmos route, `ask` in params, figure descriptions). All of them live in
the same 386 family files, so four tasks would collide, and a field that is not audited could
teach a wrong step. One pass, topic by topic, adds every field to a family at once and proves it.

* **Fields**: `spr_mistakes` (spec), `steps` and `step_of_reason` (P1), `desmos` and
  `desmos_read` (P3), `ask` recorded in params (P18), `figure_alt` (G8).
* **Order**: 19 commits, one per topic, by attempt volume × U8 weight (the heaviest first). Each
  commit touches only that topic's files.
* **Audit checks** (in `satbank/audit.py`, run by `python3 -m satbank check`, per field): no `spr_mistakes` value equals the key;
  the last step's value equals the key (numeral or `norm_text`) and each step's numbers come from
  params; `step_of_reason` indices are valid; the Desmos route, solved numerically from the same
  expressions, lands on the key; `figure_alt` names every drawn label and given number.
* **Coverage**: `tools/bank_coverage.py` (replaces `tools/spr_coverage.py`) prints `n of N` per
  field and per topic. The site never says a field is missing (P1's rule).

**Acceptance.**
1. `python3 tools/bank_coverage.py` prints one line per field and exits 0.
2. `python3 -m satbank check --topic <topic>` passes after every topic commit.
3. `git log --stat` on the T-bank branch: each commit's files are under one topic.

---

## 3. Spec overrides

### 3.1 Inside `spec/rebuild-v2.md` lines 1–648 and 10970–11183

Each entry quotes the current text, then gives the replacement or addition.

1. **Header (lines 3–6).**
   * Quote: "Written 2026-09-23. This file replaces `spec/rebuild.md` as the plan and the state
     for the site. `spec/rebuild.md` stays as the record of the first rebuild."
   * Append: "The upgrades that take each section past parity are in
     `spec/v2-upgrades/<section>.md`; the rules where sections meet are in
     `spec/v2-upgrades/product.md` (G1–G14, R39–R55). `spec/v2-decisions.md` wins over all of
     them."

2. **§1, the bar (lines 42–46).**
   * Quote: "* **Parity first.** Every feature, filter, stat, control, step, state and page they
     have gets an equivalent here that is at least as capable and clearly better to use."
   * Replace with: "* **Parity is failure.** Every feature, filter, stat, control, step, state
     and page they have gets an equivalent here that is way better to use, and the upgrade
     files say how. A student who uses TopTierPrep today opens ours and wants to switch."

3. **§1, what they missed (lines 47–51).**
   * Quote: "and an exact address `(template, seed)` for every question, so "another one like
     this" never runs out, a question can be regenerated exactly, and a fresh version is always
     possible."
   * Replace with: "and an exact address `(template, seed)` for every question, so a **twin**
     (same kind, new numbers) never runs out and keeps the student's trap (G3), a question can be
     regenerated exactly, and every question type has its own page (G7)."

4. **§1, scope (lines 68–70).**
   * Quote: "The Math bank is the only bank; Reading & Writing appears only where a section needs
     it without a bank (the Words section and optional R&W score fields)."
   * Replace with: "The Math bank is the only bank today. Every section is keyed by `subject`
     (G11), so the Reading & Writing bank lands additively; until then R&W appears as Words (R&W
     vocabulary, decision 2), logged R&W scores and sittings, and R&W minutes and tasks."

5. **How to read this document (lines 81–82).**
   * Quote: "* Where two section specs disagree, **§2.2 Resolutions wins**."
   * Add after that bullet: "* Where two upgrade files disagree, **R39–R55** (from
     `v2-upgrades/product.md`, appended to §2.2) win. Order: `v2-decisions.md`, then R39–R55 and
     `product.md`'s G-upgrades on the seams they name, then each `v2-upgrades/<section>.md`,
     then Part 3, then Part 2."

6. **§2.1 rule 1 (lines 92–95).**
   * Quote: "Every empty state says what will appear there and offers the action that fills it."
   * Replace with: "Every empty state shows one dimmed sample row of what will appear, says what
     it is, and offers the smallest action that fills it with its cost, runnable in place
     (`UI.empty`, G12)."

7. **§2.1 rule 5 (lines 108–110).**
   * Quote: "each comes from one server function and reads the same on every screen."
   * Replace with: "each comes from one server function, reads the same on every screen, and
     opens its working (`UI.fact`, `GET /api/levers`, G6). I1's facts gate checks it on every
     endpoint."

8. **§2.1 rule 8 (lines 116–119).**
   * Quote: "loading (static skeletons at final size, no looping shimmer)"
   * Replace with: "loading (the last copy painted from cache, U23; static skeletons at final size
     only on a first view, no looping shimmer)"

9. **§2.1 rule 10 (line 123).**
   * Quote: "10. **Motion is entry only.** Nothing loops. `prefers-reduced-motion` turns it off."
   * Replace with: "10. **Motion is entry only.** Nothing loops. Page changes fade `main` for
     120 ms (view transitions, G9); the Fixed line scales in once for 200 ms (G4).
     `prefers-reduced-motion` and `prefs.motion = reduce` turn all of it off."

10. **§2.1 rule 12 (lines 127–128).**
    * Quote: "12. **Copy:** no emoji; the flame, trophy and marks are our icons."
    * Append to the rule: "Actions use `UI.VERBS` only: Twin, Twin this set, Twin test, Again,
      exactly, Fix n, Learn this type (R42, G2); the retired phrases in G2 never appear."

11. **§2.1, new rules after rule 12.**
    * Add: "13. **Speed is measured.** Check → verdict ≤ 100 ms p95; Next → next stem ≤ 50 ms with
      no request; a revisited page paints cached content within 150 ms; Today's first visit
      LCP ≤ 2.5 s under mobile throttling (150 ms RTT, 1.6 Mbps, 4× CPU); CLS ≤ 0.02 (G9's gate)."
    * Add: "14. **One question, one row.** Every surface that reveals a question uses
      `UI.questionActions` and the shared verdict slot (R49, G4)."
    * Add: "15. **Readable without sight.** Figures carry generated descriptions, tables real
      headers, math MathML (G8)."

12. **§2.2 (after R38, line 174).**
    * Append rows R39–R55 exactly as in §2 A of `v2-upgrades/product.md`.

13. **§2.4, `kit.js` row (line 230).**
    * Quote: "`UI.ics(event)` (one event, or a daily repeating reminder) |"
    * Replace with: "`UI.ics(event)` (one event, or a daily repeating reminder). Product:
      `UI.VERBS` and `UI.verb(id, opts)` (G2), `UI.pts(el, pts, key)` (G5), `UI.fact(el, key)`
      (G6), `UI.empty(host, {sample, text, action})` (G12), `UI.SUBJECT` (G11) |"

14. **§2.4, `question.js` row (line 232).**
    * Quote: "`UI.annotate(host, marks, {editable, onChange})` (7 styles, notes, notes rail,
      read-only render) |"
    * Replace with: "`UI.annotate(host, marks, {editable, onChange})` (7 styles, notes, notes
      rail, read-only render); the shared verdict slot with the Fixed line, and
      `UI.questionActions(host, q, ctx)` (R49, G4); `UI.twin(anchor, ctx)` (R44), which opens
      `UI.twinSheet` outside a running set; figure, table and MathML markup and Read aloud (G8) |"

15. **§2.4, `runner.js` row (line 233).**
    * Quote: "runner key maps (§2.8) |"
    * Replace with: "runner key maps (§2.8); the next question pre-rendered while the verdict shows
      (G9); X6's phone footer, gestures and answer pad for both modes (R50) |"

16. **§2.4, `ui.js` row (line 225).**
    * Quote: "`UI.SAT_DATES`, `UI.chip`, `UI.ref`, `NAV`, `SECTION`, `TOPICS` + aliases |"
    * Replace with: "`UI.SAT_DATES`, `UI.chip`, `UI.ref`, `NAV`, `SECTION`, `TOPICS` + aliases;
      `UI.run` (`start`, `between`, `rail`, G1); `[data-fact]` delegation (G6); `Z` undo and the
      duplicate-key check (R43); optimistic toggles (G9) |"

17. **§2.5, "Not added" (lines 296–302).**
    * Quote: "Dashboard's `plan_marks` (its own shape) and `learners.plan_started`."
    * Append: "Nor, from the upgrade proposals: `type_state`, `type_memory`, `boxes`,
      `skill_memory` (R53), `estimate_log` (no practice score, R48), offline-pack tables (§4 of
      `product.md`). `traps.closed_how` gains the value `transfer` (G3)."

18. **§2.6, `want` row (line 328).**
    * Quote: "| `want` | {template: regex} | walk up to 40 seeds for an item where some option's
      reason matches (a mix-up drill, same-mistake-elsewhere) |"
    * Replace with: "| `want` | {template: regex} | walk up to 60 unseen seeds for an item where
      some option's `progress.norm(reason)`, or a grid-in's `spr_reasons` value, matches. Set by
      the server from the trap's norm on every twin of a miss: the repair, pools `redo` and
      `checks`, `from_session` twins, `like`, `/more {axis:'same'}` and twin links (R45, G3); a
      miss in 60 seeds serves the plain next seed with `trap_true: false` |"

19. **§2.6, `source` row (line 347).**
    * Quote: "| `source` | map, coach, plan, today, mistakes, review, quick, palette, assignment,
      outside, twin, try, word-example, words, worksheet, shared, qotd, spot |"
    * Replace with: "| `source` | map, coach, plan, today, mistakes, review, quick, palette,
      assignment, outside, twin, try, word-example, words, worksheet, shared, qotd, spot, and
      from the upgrade files: next, warmup (T3 only), learn, start (G10), prep (Compete's lobby
      drill, R46), probe, habit, gauntlet, bluebook, official, sprint, rematch, finish, gain,
      pace, fix, confirm, rush |"

20. **§2.6, drill feedback (lines 366–369).**
    * Quote: "trap ids opened or closed,"
    * Replace with: "trap ids opened or closed, with `closed: [{id, label, hits, since, days,
      questions}]` for the Fixed line (G4), `trap_true` (G3),"

21. **§2.8, runner row (line 422).**
    * Quote: "`D` details"
    * Replace with: "`Q` details (practice; `D` only chooses) · `R` report · `T` / `Shift+T`
      twin and its menu after a verdict (practice)"

22. **§2.8, player row (line 423).**
    * Quote: "`T` try one like this"
    * Replace with: "`T` twin · `Shift+T` twin menu"

23. **§2.8, global row (line 421).**
    * Quote: "`[` collapse the sidebar. `?` shortcuts"
    * Replace with: "`[` collapse the sidebar. `Z` undo the last reversible change (while its
      toast shows). `?` shortcuts. A scope that registers a key twice throws in `/dev/` (R43)"

24. **§2.9, new provider rows (after the T-bank row, line 449).**
    * Add:
      * "| F1 | `UI.VERBS`, `UI.verb`, `UI.pts`, `UI.fact`, `UI.empty`, `UI.SUBJECT` | every page |"
      * "| F2 | `UI.run` (G1), `[data-fact]` delegation, `Z`, `next.queue` kind `start` (G10) | S3, S4, S6, S7, S9 |"
      * "| F3 | `UI.questionActions`, `UI.twin`, the verdict slot, figure/table/MathML markup | S3, S4, S6, S8, S10, the type page |"
      * "| F4 | R45's close rule and transfer check-in, `deps.subject_of` (G11) | S10, S6, every owner |"
      * "| F5 | `want` from the trap on every twin path (G3), `source:'start'` (G10), `GET /api/types/{t}` (G7) | S3, S4, S6, S8, S10, U28 |"
      * "| S1 | `GET /api/levers` (G6), `go` on `/pair/` (G12) | every page, F2 |"
      * "| S4 | `/types/?t=` (G7) | every question surface, palette, S6, S10, S7 |"
      * "| S7 | R41's done rules, `GET /api/plan/sheet` (G13) | S3, F2 |"
      * "| T-bank | G14's fields: `spr_mistakes`, `steps`, `step_of_reason`, `desmos`, `desmos_read`, `ask`, `figure_alt` | F5, F3 |"
      * "| I1 | `tools/product_gates.py` (`perf`, `facts`, `copy`, `a11y`) | every merge in wave 3 |"

25. **§2.12 F1 acceptance (lines 548–551).**
    * Quote: "every chart renders its hidden table; `/nope/` shows the 404 page."
    * Append: "`web/dev/kit.html` also shows `UI.verb` for each of the six verbs, `UI.pts` with a
      value and with null, `UI.fact` opening on Enter, and `UI.empty` with a sample row."

26. **§2.12 F3 acceptance (lines 570–574).**
    * Quote: "the review player's Hide answers persisting across Next, and the key map of §2.8."
    * Append: "`UI.questionActions` giving the same row in every mode (G4 check 1), a figure with
      its `aria-label`, and the next question pre-rendered before Next."

27. **§2.12 F4 acceptance (lines 587–590).**
    * Quote: "access() on a live test item and today's challenge item, carry of every table."
    * Append: "a right answer on an item that did not offer a trap's norm leaving `owed`
      unchanged (G3 check 2); the transfer check-in (G3 check 4)."

28. **§2.12 F5 acceptance (lines 600–603).**
    * Quote: "and QBank's "templates", "tiers" and "levels" acceptance items."
    * Append: "the trap-true survey (G3 check 1), `source:'start'` (G10 check 2), and
      `GET /api/types/{t}` for all 386 templates (G7 check 1)."

29. **§2.13, new rows.**
    * Add: "| 3.3 Practice | "After a miss, the same template on a fresh seed" (repair) | the same
      template on the first unseen seed that offers the missed trap, within 60 (R45) | R45 |"
    * Add: "| 3.1, 3.2, 3.3, 3.5, 3.9 | "two clean answers close it" | two clean answers on
      questions that offered that trap | R45 |"
    * Add: "| every section | a button or link reading a retired phrase (G2) | the `UI.VERBS` label
      for the same action | R42 |"

30. **§4.1 waves (lines 974–985).**
    * Quote: "wave 1a  F1 design system      F4 data layer      T-bank grid-in mistakes (runs on
      its own until done)"
    * Replace with: "wave 1a  F1 design system      F4 data layer      T-bank one pass (G14: runs
      topic by topic until done, through wave 2)"
    * Quote: "wave 3   I1 integration and the full walk"
    * Replace with: "wave 3   I1 integration, the full walk and the product gates (perf, facts,
      copy, a11y)"

31. **§4.2, T-bank entry (lines 11026–11033).**
    * Quote: "**T-bank · Named grid-in mistakes in the bank** (wave 1a, port 8017)."
    * Replace the entry with: "**T-bank · One pass through the bank** (wave 1a to wave 2, port
      8017). Builds G14: `spr_mistakes`, `steps`, `step_of_reason`, `desmos`, `desmos_read`, `ask`
      in params and `figure_alt`, one topic per commit, heaviest first, with the audit checks;
      `practice.to_question` carries `spr_reasons`, `steps`, `step_of`, `desmos` and `figure_alt`
      (T-bank sends the change to the file's owner). Owns `satbank/item.py`, `satbank/audit.py`,
      `satbank/figures.py`, `satbank/plot.py`, `satbank/shapes.py`,
      `satbank/topics/*/families/*.py`, `tools/bank_coverage.py`. Needs F0. Ships partial and
      grows (open question 11)."

32. **§4.2, S4 entry (lines 11084–11089).**
    * Quote: "`api_practice.py` (adds `/api/bank`, the session endpoints, `GET /api/drill`),
      `server/checks/s4.py`."
    * Replace with: "`api_practice.py` (adds `/api/bank`, the session endpoints, `GET /api/drill`),
      `web/types/**` (G7), `server/checks/s4.py`."

33. **§4.2, I1 entry (lines 11129–11133).**
    * Quote: "checks that every nav link lands on a real page; finishes README and this file's
      State lines."
    * Replace with: "checks that every nav link lands on a real page; runs
      `tools/product_gates.py` (`perf` G9, `facts` G6, `copy` G2, `a11y` G8) and owns it; applies
      the §3.2 lines of every `v2-upgrades` file with their owners; finishes README and this
      file's State lines."

34. **§4.3 ownership (after line 11147).**
    * Add: "* New server modules from the upgrade files, one owner each: `server/next.py` and
      `web/sw.js` (F2, U1, U18), `server/habits.py` and `server/types.py` (F5, U2, U6),
      `server/ratings.py` (F4, P11), `server/push.py` and `web/link/**` (S1, U18, U20),
      `server/today.py` (S3), `web/types/**` (S4, G7), `tools/product_gates.py` (I1)."
    * Add: "* `v2-upgrades/product.md`'s R39–R55 table is shared by convention: a task that needs a
      new seam decision adds a row there and in §2.2 in the same commit."

35. **Part 5 (lines 11165–11183).**
    * Quote: "2. **Words.** Ship about 750 SAT words and 70 transitions now,"
    * Replace the item with: "2. **Words.** Answered (decision 2): R&W vocabulary only. Still
      open: who reads the definitions before launch?"
    * Quote: "3. **Daily Challenge.** Each student gets twin questions"
    * Replace the item with: "3. **Daily Challenge.** Answered (decision 1): twins."
    * Quote: "5. **Sign-in.** Email codes need SMTP in production;"
    * Replace the item with: "5. **Sign-in.** Passkeys (U19) give one-tap return without SMTP or
      Google. Add Google sign-in as well?"
    * Quote: "8. **Diagnostic gate.** Keep the name-and-email step before its result (default for
      now), or show it directly like every other sitting?"
    * Append: "G10 puts an 8-question start before the diagnostic, so the gate no longer meets a
      new student first; the product proposals and `tests.md`'s gap all favour showing the result
      directly."
    * Quote: "11. **Grid-in mistakes.** Naming grid-in mistakes needs edits to up to 133 templates.
      Ship with partial coverage and grow (default)?"
    * Replace with: "11. **Bank fields.** G14 adds grid-in mistakes, steps, Desmos routes and
      figure descriptions in one audited pass, topic by topic. Ship with partial coverage and
      grow (default)?"
    * Add: "20. **Type pages in search engines.** `/types/?t=` pages are public (G7). Let search
      engines index them (default), or `noindex`?"
    * Add: "21. **Read aloud in tests.** Only with extended time (x1.5 or x2), as Bluebook treats
      text-to-speech as an accommodation (G8, default). OK?"

### 3.2 In the sibling upgrade files (I1 applies them with the owners)

| file | quote | change | why |
|---|---|---|---|
| `today.md` T1 | "* **The pill** `Start · 15 min` (the region's primary)" | "* **The pill** `Study 15 min` (the region's primary)" | R40 |
| `today.md` T2 | "A `.btn Do them in order` (shown with 2 or more undone rows) starts the first undone row." | "The header's primary `Start today · n parts · m min` (G1) starts the run over the undone rows." | R40 |
| `today.md` T5 | "**Component.** `UI.twinSheet({body, recall, onDone})` (F3, `question.js`)." | Append: "Callers reach it through `UI.twin(anchor, ctx)` (R44); every twin body carries `want` from the trap when the source was a miss (R45)." | R44, R45 |
| `today.md` T16 | "**`Retake as twin`**" | "**`Twin test`**" | R42 |
| `shell-me.md` U1 | "* Brand-new student: "Take the diagnostic · 20 q", with a quiet "or one quick question"." | "* Brand-new student: row 0 `Start with 8 questions` (G10), row 2 the diagnostic." | R55 |
| `shell-me.md` U13 | "* **Data.** `/api/me/summary.levers: {key: {how, help, inputs: [...], next, start?}}`." | Append: "The same function serves `GET /api/levers?keys=` to every page, with `excluded` and `same_on` (G6)." | G6 |
| `plan.md` L8 | "* It starts the first undone counted question task with `run: '<today>'`." | "* It is G1's `Start today`: the first undone Due row (plan tasks first, then the warm-up, words and the day's questions) with `run: '<today>'`." | R40 |
| `plan.md` L8 | "Chaining is on the client, from the finish response's existing `plan.next`. The rail reads `GET /api/plan/day/{run}` (tasks with answered/total)." | "Chaining is on the client through `UI.run` over `/api/today.due` (G1); the rail reads the same rows." | R40 |
| `plan.md` L12 | "* `X` done or not done; `S` skip or undo; `U` undo the last action;" | "* `X` done or not done; `S` skip or undo; `Z` undo the last action (global, R43);" | R43 |
| `plan.md` §4 | "T3's warm-up and P12's `type_memory` already schedule retrieval." | "T3's warm-up already schedules retrieval (R53)." | R53 |
| `plan.md` §4 | "P7's optional chips feed Fix's order (L4)." | "P7's split Check feeds Fix's order (L4, R54)." | R54 |
| `practice.md` P18 | "* **Another like this** (`T`): the same trap with new numbers." | "* **Twin** (`T`): the same trap with new numbers, through `want` (R45)." | R42, R45 |
| `practice.md` §3.2 §2.8 row | "`T` / `Shift+T` another like this and its axes" | "`T` / `Shift+T` Twin and its menu; `Q` Details; `R` Report" | R43 |
| `tests.md` §3.1 item 49 | "In exam mode `D` only chooses D: Details isn't offered" | Append: "In practice mode too `D` only chooses; Details is `Q` (R43)." | R43 |
| `reports.md` SR8 | "(Fell for it · Misread the question · Slip in the arithmetic · Didn't know how to start · Rushed · Ran long, then guessed)" | "(P8's six: Fell for a trap · Slip: I knew it · Misread the question · Ran out of time · Entered it wrong · Didn't know how to start)" | R47 |
| `reports.md` SR8 | "fell for it → trap; misread, slip, rushed → slip; didn't know → gap; ran long → clock" | "each chip maps to its own cause (`misread` stays a cause, shown when non-zero); letters T S R C E A G" | R47 |
| `compete.md` §3.2 §2.6 row | "Sources `rematch`, `warmup`, `confirm`, `rush`" | "Sources `rematch`, `prep`, `confirm`, `rush`" (C7's lobby drill; UI label stays "Warm up") | R46 |

---

## 4. Rejected

* **An absolute practice score and a predicted-vs-actual log** (outcomes #1, the outcomes
  estimate and countdown gaps): U4, T10 and `tests.md` never show the practice model as a score;
  R48 keeps practice points as `≈` gains and sitting points as exact re-scores.
* **A second or third points model** (outcomes #1's simulated sittings, unfair-advantage #2's
  `points.py`, experience #3's `estimate.points`): U4's `estimate.gains` is the one source (R48).
* **A `type_state` / Leitner box table and the stages New · Learning · Learned · Kept · Proven**
  (outcomes #4), **"Proven" types** (unfair-advantage #5): T3 derives the schedule and U8's
  unmet · met · ready are the type words (R52, R53).
* **A pre-Check "Quick one. Re-read what it asks?" nudge on fast easy answers** (outcomes #3): it
  interrupts before Check; P8's slip chip and its fix come after the verdict.
* **Owing 3 clean answers after a Sure miss** (outcomes #10): `practice.md` rejected it; P7 ranks
  such traps first instead.
* **A 12- or 15-question placement with its own band** (outcomes #8, unfair-advantage #8's band):
  `plan.md` rejected a new score source; G10 measures by domain and says "rough".
* **Personal-best lines and records** (experience #11): `today.md` and `reports.md` rejected them
  as novelty. The Fixed line (G4) marks the moment that moves a score.
* **Offline pack with a caching service worker** (experience #12, unfair-advantage #10): shipping
  keys to the client lets anyone read them in devtools and farm the practice board (R3), and it
  needs back-dated answers; `shell-me.md` and `practice.md` rejected it. `UI.saveQueue` rides out
  brief drops.
* **Paper versions for classes with QR answer entry** (unfair-advantage #11): rejected in
  `shell-me.md`, `practice.md`, `plan.md` and `compete.md` until a teacher asks; the worksheet
  prints and X22 gives each student a twin online.
* **A words interstitial every 10 minutes inside the Math session** (unfair-advantage #3):
  `today.md` rejected folding words into the Math runner; G1's run chains the words run as its
  own part.
* **A per-question countdown in Autopilot and a separate `pool:'auto'`** (unfair-advantage #3):
  U1's `box` with segments is that session.
* **Swipe-up on the tab bar and swipe to Next before Check** (experience #10): `shell-me.md`
  rejected the tab-bar gesture; R50 forbids moving on before Check in instant feedback.
* **Haptics on every verdict** (experience #10): X6 keeps `vibrate(8)` for the long-press strike
  only; a buzz on every answer is noise in class.
* **A `twin_tell` preference that shows the trap before the twin** (unfair-advantage #1, point
  6): T5's recall header already names it; one more switch for the same line.
* **A 14-class habit taxonomy** (unfair-advantage #7): U6's 11 regex families tag every reason;
  `practice.md` and `reports.md` rejected a second taxonomy.
* **Logging Reading & Writing mistakes before the R&W bank** (the unfair-advantage R&W gap): with
  no bank there is no twin, fix or check-in, so it would be a notepad. G11 makes it additive for
  when the bank lands.
* **A "Stretch zone" chance-of-success default from this file** (the outcomes Question Score
  gap): P11's zones already do it in the builder.
* **"On track for 700?" as Me's opening verdict** (the experience profile gap): U10's outcome
  strip and U9's projection say it with their stated limits; a Yes/Close/Behind word from a
  minutes-to-points model has no defensible basis (`shell-me.md`, `plan.md`).
* **"Minimum day" that keeps the streak on partial work** (the outcomes behind-banner gap): U16's
  spare days and T1's 5-minute box cover a bad day without a second streak rule (R13).
* **Goal days in place of the study streak** (the outcomes streak gap): `today.md` rejected a
  second meaning for one streak.
* **Study-unit countdown with seconds only on exam morning** (the experience countdown gap): T12
  already states capacity under the clock; the live clock is kept as their feature, with motion
  off under reduced motion.
* **Starting a test straight from a card into the lobby only** (the experience test-start gap):
  `tests.md` X1–X2 decide the start and lobby; this file doesn't re-specify a section's flow.
* **Google sign-in now** (outcomes and unfair-advantage gaps): passkeys (U19) answer the one-tap
  need; Google stays open question 5.
* **Showing the diagnostic result without its gate** (experience and unfair-advantage gaps): open
  question 8 is the user's; G10 means a new student meets the gate later, and §3.1 item 35
  records the recommendation.
* **An `official` pool serving College Board text** (the unfair-advantage official gap): content
  terms (open question 17). IDs link to College Board's free source; twins do the practice.
