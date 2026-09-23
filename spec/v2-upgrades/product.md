# v2 upgrades: the product as a whole

Written 2026-09-23 for `spec/rebuild-v2.md` Part 1, Part 2 (lines 1–648) and Part 4–5 (lines
10970–11183). It merges the three designers' product proposals (outcomes, experience, unfair
advantage: 36 proposals and 46 parity gaps in `spec/v2-upgrades/_proposals/product.json`, cited
as "outcomes #1" and so on, counting from 1) into one build-ready list. It is checked against
`spec/toptierprep-teardown.md`, `ttp-notes.md`, the live walk in `ttp-live.md`, and all nine
section upgrade files (`shell-me.md` U1–U28, `today.md` T1–T20, `practice.md` P1–P25,
`tests.md` X1–X23, `reports.md` SR1–SR24, `plan.md` L1–L20, `compete.md` C1–C27, `review.md`
V1–V19, `words.md` W1–W22).

* **What this file is.** The section files make each section way better. This file owns what no
  section owns: the signature features that cross every section, and the seams where the
  section files disagree. It adds 16 upgrades (G1–G16) and 22 resolutions (R39–R60, numbered
  after Part 2's R1–R38 so every file can cite them).
* **Precedence.** `spec/v2-decisions.md` wins over everything. Then this file's resolutions
  (R39–R60) and G-upgrades, on the seams they name. Then each `spec/v2-upgrades/<section>.md`,
  which wins over its Part 3 section. Then Part 2 (R1–R38 hold except where a section file or
  R39–R60 names a line). §3 of this file lists every line that changes, in the plan and in the
  sibling files.
* **No classes** (decision 5). Nothing here has teacher or student roles, classes, homework,
  assignments, class codes, `/class/` or `/join/`. Friends compete through Compete's private
  contests, an invite code or link that Compete owns (C18, C19).
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
    again" 8, …) and the exact replay, the fix and the parallel sitting in 7 more. `review.md`
    adds "Fresh one like this", "See one solved", "Learn it", "Redo these 5", "Keep warm · 3";
    `words.md` adds "Same word, new text" and "Same trap, new word" as two direct keys, and
    "Drill it".
  * **Four launchers for one day.** U1's time box (`source:'next', box`), T2's `Do them in
    order`, L8's `Start today` (plan tasks only, chained from `plan.next`) and V1's `Start
    review · 10 min` (source `due`, made the primary of Today's `#mist` card) each start the day
    with their own chain rule. T3's Warm-up row and V1's list both count check-ins, so two "due"
    numbers on Today disagree. The plan's Words task (L4) and T2's Words row would show the same
    words twice. v2 §3.6's task status ticks `fix` and `recheck` only from a session tagged with
    that task, so a time box that fixes three mistakes leaves the plan's Fix task `todo`.
  * **R&W items already exist.** `words.md` W1–W2 build `server/rw_items.py`: unlimited Words in
    Context and Transitions items in the bank's Item shape, a named trap on every wrong option,
    exact regeneration. As drafted they live only inside Words (`word_reviews`), outside drill,
    Review, traps and `/api/types`.
  * **Keys that change meaning.** Details is `D` in the runner (Part 2 §2.8), `I` in players;
    `I` is "I'm guessing" in the runner and Guess in word quizzes; `Q` is the global quick
    sheet; `Shift+T` is a menu in the runner and a direct action in Words; `V` is "see one
    solved" in Review's pane.
  * **Clashes between the upgrade files.** `D` chooses option D and opens Details in the
    practice runner (Part 2 §2.8; `tests.md` fixed it in exam mode only). `source:'warmup'` is
    T3's spaced warm-up and also Compete's contest-lobby drill (`compete.md` §3.2). The cause
    chips differ: `practice.md` P8 keeps `misread` as its own cause, `reports.md` SR8 folds it
    into slip and adds "Rushed" and "Ran long". `plan.md` cites a `type_memory` table and
    "optional chips" that `practice.md` rejected.

---

## 1. Scorecard

One row per TopTierPrep feature of the product as a whole. Section-level inventories are in
each section file's scorecard; rows 38–46 point there. "v2 spec" is `spec/rebuild-v2.md` as
written. "After these upgrades" includes the sibling files and this file.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Price, tiers, quotas | Free: 1 exam attempt, 0 questions from their own bank, 5 new words a day, 1 AI plan a cycle. Pro $13.99, Elite $23.99 a month; usage meters on Subscription and Profile | Everything free; no plans, quotas, paywalls or upgrade prompts; the selling slots show the student's day | The slots they sell from start work: Up next in the sidebar (U1), readiness on Me (U8) | **WAY BETTER.** Everything they meter is unlimited, and nothing on screen sells. |
| 2 | Sign-in | A Google sign-in wall before any page | No wall: anonymous-first, then an email code, pairing or the device code; Google is open question 5 | **Google sign-in** (G15, R58) as well as passkeys (U19), both one tap, both linking to the same learner and carrying the anonymous work over; a shared computer approved from the phone (U20); **Continue on your phone** carries the open page to a phone by QR (G12) | v2 BELOW for a returning student on a new device (no Google; email needs SMTP). **G15 → WAY BETTER:** their one method with no wall in front of it, plus passkeys, phone approval and the page carried across. |
| 3 | First visit | Wall, then empty cards: "Complete a full-length test to start tracking your score" (134 minutes) | New-student card frames; Up next offers the 20-question diagnostic, whose result waits behind a name-and-email step (R38) | **Start with 8** on Today, question 1 answered in place with no sign-up; afterwards every Today card is about the student; a live sample report (SR24) (G10) | v2 PARITY: the first useful result still cost 20 questions and a form. **G10 → WAY BETTER.** |
| 4 | The one next action | None: plan CTA, QOTD, countdown and score compete | Today §3a's first-match Up next and the Today list | One queue on every page with `G N` (U1); a time box with question 1 on the page (T1); **Start today** over the whole Due list, where Review's due list is one row (G1, R56). Today shows two starts, named apart (`Start today`, `Study 15 min`); every other start on the page is a row of the same list | **WAY BETTER.** One list, one count per fact (G6 checks `due today`). |
| 5 | Doing the day across sections | Dashboard → Full Plan → Start task → a QBank session that never ends → back → Mark done: about 12 clicks, 4 loads, 4 ticks for a 4-task day | Tasks tick from tagged sessions; summaries; finish responses carry `plan.next` | As drafted: 4 launchers with 4 chain rules, check-ins counted in two rows, the words twice, and Fix and Warm-up ticked only by their own tagged session. **G1 + R56**: one Start today over every Due row (plan, review, words, the day's questions, tests, private contests closing today), one chain on every finish screen, and plan tasks tick from whatever did the work (R40, R41) | v2 WAY BETTER than theirs but inconsistent across files. **G1 → one loop:** 1 tap, then Enter between parts. |
| 6 | Question sources | College Board Question Bank (1,921 Math) plus their own (3,867 Math): fixed pools that repeat; Free gets none of theirs | Unlimited questions from 386 verified templates; no official items (open question 17) | **Official questions on our answer pad** (G16, R59): a list of 1,039 official IDs we hold keys for, filtered by skill, tier and not yet done; each opens on College Board, is answered here, the wrong pick is named (92% of official wrong options resolve), the mistake opens and a trap-true Twin follows. Plus an official question by ID or pasted text becomes its type and unlimited twins (U2, P13); readiness weighted by College Board's own mix (U8); each type's page lists its official IDs (G7) | **WAY BETTER.** Their official workflow is kept, with a Solved filter, and every official miss gets a name, a mistake with check-ins and endless twins. Their own pool runs out and repeats; ours never does. |
| 7 | Reading & Writing | R&W bank (1,848 official + 1,315 theirs; Words in Context 261 + 102, Transitions 194 + 10), 4-module tests, an R&W question of the day | Math only; Words is R&W vocabulary (decision 2); optional R&W score fields | **G11 + R57**: `rw_items` is the first `rw` bank. Words in Context and Transitions are unlimited, drillable from Practice (`/api/drill {subject:'rw'}`), listed in `/api/types?subject=rw`, and their misses are ordinary mistakes (Review, Fix n, check-ins, Twin). Also: Word Sprint (C14), logged Bluebook R&W scores and misses on those two skills, R&W minutes and tasks in the plan and streak, the 1600 total | **WAY BETTER on the two R&W skills we generate** (theirs: 567 fixed items with prose; ours: unlimited, every wrong option named). The other R&W skills wait for the bank (decisions 2 and 3) and land in the same routes with no rewrite. |
| 8 | Explanation | AI prose "Justification … Distractor Analysis", unverified, after answering only; the QOTD doesn't highlight the key | The key highlighted, a one-sentence rationale (median 21 words), every wrong option's named misconception | Steps on this question's numbers, checked against the key, with the step where your answer left the path (P1); a hint ladder (P2); Learn this type (T4, P2); the same verdict on every surface (G4); steps written in one audited pass, **on every served template before launch** (G14's launch gate) | v2 BELOW on the key's explanation. **P1 + P2 + G4 + G14 → WAY BETTER** on every question at launch, not half of them. |
| 9 | Another question like this | None: retry the same item, or "More practice" to a list | "Another like this" on every surface under about 11 names; the repair is the same template on the next fresh seed | **Twin** (one verb, one key `T`, its menu `Shift+T`, on every surface including Review and Words, G2) that keeps your trap: a 60-seed walk offers it 98.4% of the time instead of about 56% (G3); axes easier, harder, grid-in, same setup (P18); same trap in other types (G3); in Words, same word or same trap as menu items. A visible sublabel says what Twin means on touch screens and the first 3 uses | v2 WAY BETTER in kind, but its signature promise failed about 2 times in 5 and had 11 names. **G2 + G3 → the promise holds, under one name that explains itself.** |
| 10 | Mistake loop | toggleRedo exists in their API with no button; "Redo Questions 0"; nothing re-checked | Review: named mistakes, 2 clean answers close, check-ins at 3, 10 and 30 days | A named mistake closes only on questions that offered its trap; unsure, slip and unnamed grid-in mistakes close on clean answers to their template, so every kind can reach Fixed; the 10-day check-in comes on another type with the same trap where one exists (G3) | **WAY BETTER**; G3 makes "Fixed" true for every kind. |
| 11 | Score estimate | Only after a full 4-module test; floor sections dropped; red LOW CONFIDENCE with no way to raise it | R16: bands from sittings, confidence with its reason, trend | Points on the table (U4), projection (U9), practice delta (T10), what moves the band (X15, SR21) | **WAY BETTER** (siblings); R48 keeps one pricing rule. |
| 12 | Pricing time | No point value anywhere; "Weakest first" | Mastery bars and accuracy | Every skill, mistake, habit and Up next row priced by one function in one chip, its arithmetic one tap away (U4, G5) | v2 PARITY. **U4 + G5 → WAY BETTER.** |
| 13 | Numbers that agree | Profile streak 0 while the QOTD says 1; wizard target 1400, dashboard 0; gauge "25 Wrong" beside "0 Incorrect / 45 Unanswered"; "13% · 1-8 questions" | Rule 5: one source per fact | Levers on Me (U13); **G6**: every number on every page carries a visible ⓘ on every device and opens its working, with what was left out, and a gate proves each fact (the due count included) reads the same on every endpoint | v2 PARITY in practice: a rule nobody checks, working shown only on Me. **G6 → WAY BETTER.** |
| 14 | Search | None | Palette: pages, skills, 386 types, misconceptions, actions, parsed sets | Paste a question or an official ID (U2); change anything by typing (U24); open any type's page (G7) | **WAY BETTER.** |
| 15 | Quick add | Draggable "Add your own word" button that covers Next | Quick sheet: quick question, log a mistake, add a word; never floats | Log a mistake by ID, pasted text or a Bluebook test (U2) | **WAY BETTER.** |
| 16 | Report a problem | Modal (title, category, details, 10 × 50 MB images); the student never hears back | One modal, replies, bounded disputes, admin page | Key disputes answered by an independent solver in about a second, quarantine, one fix corrects everyone (U3); Report on every question surface, key `R` (G4, G2) | **WAY BETTER.** |
| 17 | Share and export | `navigator.share` froze the page; shared sessions; "Share / Export Report" has no handler | Sets, progress link, calendar feed, print | Links send twins by default (U28, P22); repair packs (SR20) | **WAY BETTER.** |
| 18 | Speed | Client-routed SPA; cards skeleton-load each visit; a fake plan-building screen | 14+ static pages, each reloading and fetching behind skeletons | Prerender and paint from cache (U23), one round trip per question (P23), and **G9**: the next question pre-rendered, view transitions, budgets measured before merge | v2 BELOW. **G9 → WAY BETTER, measured.** |
| 19 | Phone | Desktop layout squeezed; tools at the top; the vocab button covers Next | 390 px rules, bottom sheets, 5 tabs | Chrome that fits (U26); one thumb-first runner for practice and tests (X6, R50) with every tool a visible labelled button in a wrapping tools row, none in a menu | **WAY BETTER.** |
| 20 | Keyboard | Arrows in the report player; the overview ignores Esc | One registry and map, but `D` both chooses D and opens Details in the practice runner | One key per action across runner, players and Words: `T` Twin, `Shift+T` its menu, `V` Details, `I` Guess, `E` again exactly (eliminate in a running set), `R` report, `Z` undo; a `/dev/` check that throws when a key means two actions in two scopes (G2, R43) | v2 PARITY with clashes. **G2 → WAY BETTER.** |
| 21 | Accessibility | Figures are images with no text alternative, floated beside the text | Charts carry hidden tables; the bank's figures are unnamed `role="img"` SVGs | Figure descriptions generated from each item's numbers and checked on every figure template before launch, table headers, MathML kept, Read aloud as a visible tool (G8) | v2 PARITY (both silent on figures). **G8 → WAY BETTER.** |
| 22 | Theme, text size, motion | None | Dark theme, three text sizes, reduced motion | Unchanged | **WAY BETTER.** |
| 23 | Time zone | Calendar in UTC, so an evening's work lands on the wrong day | The learner's local day everywhere (X-Tz, R13) | Unchanged | **WAY BETTER.** |
| 24 | Preferred study time | "Evening", used by nothing | Calendar download or feed with alarms | Reminders that say what is due, at the chosen time (U18) | **WAY BETTER.** |
| 25 | Private play with people you know | Hidden `/my-classes` and `/teacher` routes; their only private play is inside those hidden pages | v2's groups (R4) | Dropped by decision 5: a separate platform covers group teaching, so nothing here has roles, codes or homework. Friends race through Compete's private contests: one invite code or link, a series board, rounds built from their open traps (C18, C19) | **WAY BETTER** for friends (a link, free, with a reason to come back every round). Group teaching is out of scope (decision 5). |
| 26 | Contests and leaderboards | Tier-gated; empty on the days seen | Free Compete | `compete.md` C1–C25 | **WAY BETTER.** |
| 27 | Achievements | 4 hard-coded tiles; View All has no handler | 43 tiered rules with progress | Go on every badge (U13, C23); the Fixed moment in every verdict (G4) | **WAY BETTER.** |
| 28 | Streak | Two streaks that disagree | One study streak (R13) | Spare days (U16) | **WAY BETTER.** |
| 29 | Desmos | Embedded empty panel | Dock, float, per-sitting state | This question loaded after answering, with the point to read (P3) | **WAY BETTER.** |
| 30 | Reference sheet | Modal | Modal | Which formula this used, and the ones not given (P24) | **WAY BETTER.** |
| 31 | Timer and pace | Stopwatch that resets on reload; Timed or Untimed | Survives reload; 95 s pace | Budgets per tier and type, two passes (P16), a personal pace guide (X3) | **WAY BETTER.** |
| 32 | Question details | ID, domain, skill, difficulty | Template, level, why, permalink | Plus **About this type**: the type's own page (G7) | **WAY BETTER.** |
| 33 | Single-question page `/question/:key` | A route per item (seen in their bundle) | Permalink `?q=TEMPLATE:SEED` as a one-question drill | Links send twins (U28); a public page for each of the 386 types (G7) | **WAY BETTER.** |
| 34 | Content trust | AI prose; keys unchecked; their plan generator failed 3 of 3 | Audited bank with a second solver; plan built on the server | Every new bank field audited before it ships (G14); disputes checked by the solver (U3); **the Words content audited too**: every definition and part of speech checked against WordNet, every frame's key and traps re-solved by a second method, mismatches in a human queue that must be empty before Words ships (G14) | **WAY BETTER** for Math and R&W alike. |
| 35 | Help and FAQ | Six billing questions | `/help/` with search and anchors | A visible ⓘ beside every number, on every device, opening its working (U13, G6) | **WAY BETTER.** |
| 36 | Toasts and undo | Generic toasts ("Task skipped") | Toasts with actions | An inbox and Undo on every reversible action (U25); `Z` undoes from any page (G2) | **WAY BETTER.** |
| 37 | Empty and loading states | "No completed tests yet."; skeletons on every visit | A frame, a sentence and the filling action; static skeletons | Paint from cache (U23); **G12**: one dimmed sample row of what will appear, and the smallest filling action with its cost, run inside the card, through one `UI.empty` on every card, Review's included (V16): `Start with 8` for a learner with no answers, an inline Twin otherwise | v2 PARITY. **G12 → WAY BETTER.** |
| 38 | Dashboard (section) | Hero, QOTD, study time, plan CTA, score, countdown, recent tests | §3.2 | `today.md` T1–T20 | See `today.md` §1. |
| 39 | Question Bank (section) | Builder with counts and filters; session with retries, Attempts, overview | §3.3 | `practice.md` P1–P25 | See `practice.md` §1. |
| 40 | Practice tests and the runner (section) | Paper grid, start wizard, Bluebook-clone runner, Check Your Work | §3.4 | `tests.md` X1–X23 | See `tests.md` §1. |
| 41 | Results and the score report (section) | Ring gauges, tiles, domain cards, question grid, review modal | §3.5 | `reports.md` SR1–SR24 | See `reports.md` §1. |
| 42 | Study plan (section) | Four-step wizard; plan view recovered from their bundle | §3.6 | `plan.md` L1–L20 | See `plan.md` §1. |
| 43 | Contests, rankings, leaderboards (section) | Contest list, rankings grid, leaderboard | §3.7 | `compete.md` C1–C25 | See `compete.md` §1. |
| 44 | Vocabulary (section) | Library, flashcards, quizzes, My Words; 5 new words a day on Free | §3.8 | `words.md` W1–W22. Reconciled here: W1–W2's items are the `rw` bank (R57), so their misses are Review mistakes and their twins go through `UI.twin` (W1's two axes are menu items, R42, R43); W11's run is G1's Words part, one row with the plan's Words task (R56); W21's items are T14's two R&W slots; the Words content joins G14's audit | See `words.md` §1. |
| 45 | Profile and account (section) | Profile cards, usage meters | §3.1 | `shell-me.md` U1–U28 | See `shell-me.md` §1. |
| 46 | Redo, saved and marked (section) | A Redo toggle with no button; "Redo Questions 0" | §3.9 | `review.md` V1–V19. Reconciled here: V1's due list is one Due row (R56); its labels map to `UI.VERBS` (R42); "See one solved" is how `Learn this type` opens from a miss, freeing `V` (R43); V16 renders through `UI.empty` (G12); V19's sheet is G13's section 1 (R60) | See `review.md` §1. |

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
| unfair-advantage #11 paper versions with QR answer entry | Rejected (§4; its class use is void by decision 5) | none |
| unfair-advantage #12 figures a screen reader can use | **G8**, G14 | none |
| the Google sign-in gaps (outcomes, unfair-advantage) | **G15** | R58 |
| the official-question gap (unfair-advantage) | **G16**: official IDs on our answer pad | R59 |
| the R&W gaps (all three) | **G11**: `rw_items` as the first `rw` bank | R51, R57 |
| parity gaps (all three) | mapped in the scorecard rows above, or listed in §4 | |

### A. The seams: one decision where the upgrade files disagree (R39–R60)

These rows are appended to Part 2 §2.2 (§3.1 item 12). "Wins" names the text that is canonical.

| # | topic | what disagreed | decision | owner |
|---|---|---|---|---|
| R39 | Precedence | Nine upgrade files each win over their own section, and some specify the same seam | `v2-decisions.md` > R39–R60 and G1–G16 of `product.md` (on the seams they name) > `v2-upgrades/<section>.md` > Part 3 > Part 2. A later upgrade file that needs a seam changed adds a row here in the same commit | I1 |
| R40 | Starting the day | U1/T1 time box, T2 `Do them in order`, L8 `Start today` (plan tasks only, chained from `plan.next`, rail from `GET /api/plan/day`), V1 `Start review · 10 min` (Today's `#mist` primary) | **Two starts, named apart.** `Start today` walks the Due list (`next.due`, T2's rows with R56's review row) in its order, one ordinary sitting per row, chained on the client by `UI.run` (G1); the rail reads `/api/today.due`. `Study N min` is U1's box, one mixed session; after the day is done it reads `Keep going · N min`, and `Keep going` means the box and nothing else. T2's button and L8's pill are both `Start today`; T1's pill `Start · 15 min` is `Study 15 min`. V1's `Start review` is the review row's own start (R56), not a third launcher. The challenge and contests are never started by the run | F2 (`UI.run`), S3, S7, S10 |
| R41 | Plan task done | v2 §3.6 ticks `fix` and `recheck` only from a session tagged with that task | A task is done by the work, from any source that day: `fix` when answers on its trap templates ≥ its count; `recheck` when every check-in due that day has been answered once (the review row's check-in items, R56); `focus` unchanged (attempts on its topics ≥ count); `words` by T2's words rule (due = 0, or a words run finished today). Tagged sessions still tick as before | S7 |
| R42 | Action names | About 11 names for a twin, 7 for the other three ideas; `review.md` and `words.md` add more | **Six labels for four ideas** (G2): `Twin` (`Twin ×n`, `Twin this set`), `Twin test`, `Again, exactly`, `Fix n`, `Learn this type`. `UI.VERBS` holds each label, helper, sublabel, glyph and key; the sublabel shows under the button on coarse pointers and on the first 3 uses. §3.2 maps every `review.md` and `words.md` label (Fresh one like this, Try one now, Fresh versions, Redo these, Learn it, See one solved, Drill it, Same word, new text, …). `Rematch` (P19, C2) stays its own feature | F1, every page owner |
| R43 | Keys | `D` chooses and opens Details in the practice runner; Details is `I` in players; `I` is Guess in the runner and in word quizzes; `Q` is the global quick sheet; `U` is undo on Plan; `Shift+T` is a menu in the runner and a direct action in Words; `V` is "see one solved" in Review's pane | **One key per action across scopes** (G2): `D` only chooses; **Details `V`** in the runner and every player; **Guess `I`** in the runner and word quizzes, unbound in players; **Report `R`** everywhere a question shows; `T` Twin and `Shift+T` its menu after a verdict in the runner, every player and Words; `Q` stays the global quick sheet; **`Z` undo** globally (Plan's `U` becomes `Z`). `UI.KEYS` declares each question action's key once; in `/dev/`, `UI.keys.register` throws when a scope binds a key twice, and when runner, player, pane or words scopes bind one key to two different actions, except the listed `E` (eliminate in a running set, Again elsewhere) and `O` (Note; Open word in Words, which has no note) | F2, F3, S7, S9, S10 |
| R44 | The twin control | T5's `UI.twinSheet`, P18's split button and `/more {axis}`, W1's two direct twin keys, each consumed by S3, S6, S8, S9, S10 | **One component `UI.twin(anchor, ctx)`** (F3): P18's split button and menu. Inside a running set it appends through `POST /api/drill/{id}/more` (in a Words run, `POST /api/words/run/{id}/another`); everywhere else it opens T5's `UI.twinSheet` inline (R24). Its menu lists only the axes the item supports: for Words in Context `Same word, new text` and `Same trap, new word`, for Transitions `Same logic, new text` and `Same mix-up, new text`. Consumers never build their own twin button | F3, S9 |
| R45 | Which twin | The repair and every "like this" path serve the next fresh seed, which drops the trap about 2 times in 5; any right answer on the template closes every trap on it | **Trap-true** (G3): every twin that follows a miss on a named trap carries `want` from the trap's norm (§2.6, 60 seeds, grid-in `spr_reasons` too, an R&W item's trap ids). For traps of kind misconception, and grid-in traps whose template has `spr_mistakes`, a clean answer lowers `owed` only when `attempts.offered` holds the norm (or the grid-in's `spr_reasons` do). Unsure, slip and unnamed grid-in traps (norm `~unsure`, a filler slip, or `''`) keep v2's rule: any clean answer on the template counts, and their twins are plain. R9's 10-day check-in uses another template with the same norm when `progress.related(norm)` has one | F5, F4 |
| R46 | Drill source names | `warmup` is T3's spaced warm-up and also Compete's lobby drill | `warmup` means T3's warm-up only, which R56 makes the head of V1's `due` session: `{source:'warmup'}` is accepted as `{source:'due', count:5}` so U1's segment 1 and old bodies keep working. Compete's lobby drill (C7) is `source:'prep'` (UI label stays "Warm up"). New: `start` (G10), `due` (V1), `official` (G16). `learn` (T4), `twin` and `try` (R24) unchanged | F5, S8, S10 |
| R47 | Causes of a miss | P8: six chips with `misread` its own cause; SR8: different labels, misread folded into slip, "Rushed" and "Ran long" added; X: `changed` | **Causes:** `trap`, `slip`, `misread`, `clock`, `entry`, `changed` (tests, automatic), `gap`, first match in T7's order with `changed` first on tests and a student-set `miss_kind` winning. **Chips (P8's six, exactly):** Fell for a trap · Slip: I knew it · Misread the question · Ran out of time · Entered it wrong (grid-ins) · Didn't know how to start. **Letters** for Colour by Cause: T S R C E A G. **R9 kinds:** trap → misconception; slip, misread, clock, entry, changed → slip; gap → unsure | F4, S4, S6 |
| R48 | Pricing | Several proposals add a second points model | **Two functions, two looks.** Practice points on skills, mistakes and habits come only from U4's `estimate.gains`, shown as `≈ +6 pts` (never a range, never a score). A sitting's points come only from exact re-marking (`estimate.rescore`, `estimate.ledger`), shown without `≈` ("+12 on this section"). Nothing else prices points | F4, F1 |
| R49 | The actions on a revealed question | P1, P2, P3, P18, P21, T5, U3, R23, SR16 each add actions on their own surfaces | **One row `UI.questionActions(host, q, ctx)`** (G4) in the verdict slot of every surface that reveals a question, with one order, one set of keys and one access rule | F3 |
| R50 | The runner on a phone | X6 specifies gestures, footer Mark and the answer pad for the test window; a draft put Hint, Eliminate, Calculator, Desmos way and Read aloud in a `⋯` sheet | X6 is `runner.js`, so it applies to the practice session too, with one guard: in instant feedback no swipe moves on before Check. **No tool is in a menu** (decision 4, §2.1 rule 9): under 760 px the tools (Calculator, Reference, Eliminate, Hint, Desmos way, Read aloud, each where allowed) wrap into a visible **tools row** between the question and the footer, each a 44 px button with its icon and its text label; the row wraps to a second line rather than scroll or collapse | F3 |
| R51 | Subject | Each file says "payloads carry `subject`" in its own way | One axis (G11): `subject` is `math` or `rw`, derived template → topic → subject (no subject column), default `math`, `?subject=` on every section endpoint, 422 for an unknown subject. `rw` has a bank for the skills `rw_items` generates (R57); a request for any other R&W skill, or an R&W test, returns `available:false` or 409 `no_bank` | F4, every owner |
| R52 | Type states | outcomes: New/Learning/Learned/Kept/Proven; unfair-advantage: Proven; U8 and P14: unmet/met/ready | U8's **unmet · met · ready**, with the overlays open mistake, being fixed and due (P14), are the only type states. R37's words stay for skills | F1, S1, S4 |
| R53 | Spaced returns | Proposals add `type_state`, `boxes`, `skill_memory`; `plan.md` cites a `type_memory` that `practice.md` rejected | T3's derived `progress.warmup_candidates` is the only schedule for types, R9's check-ins the only one for mistakes. No schedule table is added | F4 |
| R54 | Confidence in practice | `plan.md` cites "P7's optional chips"; `practice.md` rejected chips | P7's split Check (`Enter` Sure, `Shift+Enter` Unsure, `I` Guess, a second tap = Sure) is the only practice input; nothing asks an extra tap | F3 |
| R55 | A brand-new student | U1: "Take the diagnostic · 20 q"; T1: the coach's box; proposals: 8 or 12 placement questions; V16: "Try one now", then "Take the diagnostic" | Up next row 0 for a learner with 0 answers is **Start with 8** (G10); the diagnostic is row 2. Every empty state for a learner with 0 answers offers `Start with 8 · about 10 min` as its action (G12), Review's included. No practice score or band is shown from it (U4, T10) | F2, F5, S3, S4, S10 |
| R56 | One Due list | V1's capped Due list (check-ins, relapsed, sure and wrong, half fixed, saved, marked, mistakes) and T3's Warm-up row both count check-ins; V1's `Start review` is a third primary on Today; the plan's Words task (L4) and T2's Words row list the same words; `Keep going` means U1's box in G1 and the coach's quick set in V1 | **V1's list is one Due row, kind `review`**, in place of T2's Warm-up row. `review.due` absorbs T3's candidates: its kinds are check-in, relapsed, sure, half, **fading** (T3's fading types), saved, marked, mistake, **keep_warm**, under V1's cap. `next.due` builds the row from `review.due`, so Up next's `checks` row, the Due list, Start today, Review's Due tab, Today's `#mist` card, the badge and the plan's recheck task read one list and one count. The plan's `recheck` task renders as that row and the plan's `words` task as the words row (each carries `task_id`, sits in PLAN and counts toward its `N of M`), never twice. Review's page pill and `#mist` start that row; while a run is on they read `Start review · part n of m` and start it with `run`. `Keep going` is the box only | F2 (`next.due`), S10 (`review.due`), S3, S7, S9 |
| R57 | R&W items | `words.md` keeps `rw_items` inside Words (answers in `word_reviews`, not in attempts, drill, Review or `/api/types`); G11 said R&W had no bank; §4 rejected logging R&W mistakes | **`rw_items` is the first `rw` bank** (G11). Its templates (`rw.wic.*`, `rw.nearly.*`, `rw.tr.*`) are registered in the catalogue under topics `words-in-context` and `transitions`, subject `rw`. Every answer to a generated R&W item, from a Words run, a word sheet sample, T14's slots or a drill, is filed by `progress.record` as an ordinary attempt (new nullable `attempts.word`); a miss opens a trap of kind misconception with norm = W1's trap id (W2's `wrong_logic` pair for transitions). `word_reviews` keeps the word's schedule and links the attempt (`word_reviews.attempt`). `words.rw_answers` reads attempts. So Review, Fix n, check-ins, `UI.twin`, `UI.questionActions`, the type page and Results' R&W row work unchanged | F4, F5, S9 |
| R58 | Sign-in | U19 passkeys only; Google left as open question 5 and rejected for now in §4 | **Google sign-in as well** (G15): Google Identity Services on `/signin/` and in the save nudge, one more method on the same learner as passkeys and email codes. The first link keeps the anonymous learner; signing in to an existing account carries the anonymous work over through the pairing `carry`. Passkeys stay first where a platform authenticator exists. Open question 5 is answered yes by default | S1 |
| R59 | Official questions | P13 sends students to College Board's bank and back with a paste; §4 and open question 17 drop in-app official practice | **An official-questions session on our answer pad** (G16): IDs from `material/keys`, opened on College Board, answered here, the pick named through U2's map, a trap opened (source `outside`, origin `cb_qbank`) and a trap-true Twin next. No College Board text is ever served | S4, F5, U2's `types.py` |
| R60 | Test-week sheets | G13's `/plan/?print=sheet`, V19's `/review/print.html?sheet=traps` and `/plan/?print=traps`, and V19's exam-week card with its own `Final check · 10` beside T13's final stretch and L19's eve task | **One sheet, one URL** (G13): V19's trap entries are its section 1; the two trap URLs redirect to `/plan/?print=sheet`. V19's Final check is a Due row (kind `final_check`) in T13's final stretch, not a card. V19's error log (`?sheet=log`) stays, as a different list | S7, S10, S3 |

### B. The day and the loop

#### G1. Start today: one run through the whole Due list, and the plan ticks from whatever did the work

*From: experience #1, unfair-advantage #3, outcomes #2; reconciles U1, T1, T2, T3, L4, L8, L9,
V1, W11. Effort M. Builders: F2 (`UI.run` in `ui.js`, `next.due`), S3 (the Due list header,
`/api/today.due`, `#mist`), S10 (`review.due` with T3's kinds, Review's pill), S7 (the DayPanel
pill, R41's done rules), S4 (session summary), S6 (report footer), S9 (the words run's
`then=run`), S5 (the lobby's `run`).*

**Why.** A 4-task day costs about 12 clicks, 4 page loads and 4 manual ticks on theirs, and
their QBank session never ends. As drafted, ours had four launchers that chained differently:
L8's walked plan tasks only, so Start today skipped the warm-up, the words and the day's
questions; V1's `Start review` was a third pill on Today; check-ins were counted in both the
Warm-up row and Review's list, so the counts disagreed; the plan's Words task and the Words row
listed the same words twice; and a Study-15-minutes box that fixed three mistakes left the
plan's Fix task `todo`. One run over one list, one count per fact and one done rule make the
whole site one loop.

**Two starts, named apart (R40).**

| start | label | what it does | where |
|---|---|---|---|
| The day | `Start today · 5 parts · 38 min`; mid-run `Continue today · part 2 of 5` | walks the undone Due rows in order, each its own ordinary sitting, chained | Today's Due list header (replaces `Do them in order`); Plan's DayPanel (L8); the sidebar Today card; the phone thumb bar (L8); palette "start today"; `/?run=1` |
| Some minutes | `Study 15 min` with chips 5 · 15 · 30 · 45 · 60; once the day is done, `Keep going · 15 min` | one mixed session sized to the time (U1's `box`, T1's blocks) | Today's `#next` (T1, region primary); the Up next popover chips (U1); Review's pill when nothing is due or open; palette "study 20" |

* Today has exactly these two pills. Every other start on Today (`#mist`, a Due row's action,
  a card's action) is a `.btn` that starts one Due row or one card's own set.
* Start today is hidden when no row is undone; the Due header then reads `Day done · 42 of 40
  min` and the pill is `Keep going · 15 min` (the box). `Keep going` never names anything else.
* On a rest day the pill reads `Practice anyway · 3 parts`.

**One Due list (R56).** `next.due(learner, tz)` (F2) returns the rows, in T2's order without its
class rows (decision 5):
1. A running or out-of-time test.
2. Plan tasks from `plan.today_summary` (fix, focus, test, custom, extra). The plan's `recheck`
   task is the review row and the plan's `words` task is the words row, in this group, each with
   its `task_id`, counted once in PLAN's `N of M`.
3. **Review** (kind `review`, replaces T3's Warm-up row): `Review · 12 due · ~16 min · 3
   check-ins · 2 fading · 2 sure and wrong`. Built from `review.due` (S10), whose kinds, in
   order, are V1's check-in, relapsed, sure, half, then T3's **fading** types, then V1's saved,
   marked, mistake, then T3's **keep_warm**, cut at V1's cap. `progress: {have: done, of:
   today's list}`, `minutes` = V1's minutes. Its start is `{source:'due', box:
   prefs.review_minutes}` (V1's session, which keeps T3's `hide_skill` and interleaving).
4. Sweep (T13, final stretch) and **Final check** (R60, exam week).
5. Words: `Words · 12 due · 5 new · ~6 min` (the plan task's label when one backs it), starting
   W11's run; one row whether or not a plan exists.
6. The day's questions (T14).
7. The challenge.
8. Private contests closing today (`compete.due_today`): `Friday five · 10 q · closes 9:00 PM`.

**Review's pill and `#mist` start the review row.** Review's `Start review · 10 min` (V1) and
Today's `#mist` card (a `.btn`, not a region primary) start row 3 with its own body. While a run
is on (`/api/today.due.run.on`), both read `Start review · part 2 of 5` and start the row with
`run`, so finishing it hands on to part 3. When nothing is due and nothing is open, Review's
pill is the box, `Keep going · 10 min`; when the list is done but mistakes are open, it is
`Fix 6 · 10 min` (V4's order).

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
* The day's questions: the run opens Today at `#qotd`; once every slot shown is answered, a
  `Continue today` bar appears under them.
* The end: T19's receipt (`/api/today.receipt`), with `Today's challenge · 10 q` when it is
  open (ranked starts keep their own lobby) and `Keep going · 15 min`.

**R41: the plan ticks from any path (S7, §3.6 Task status).** `fix` is done when that day's
answers on its trap templates, from any source, reach its count; `recheck` (shown as the review
row) when every check-in due that day has been answered once; `words` by T2's words rule; `focus`
as v2 (attempts on its topics from any source). So the box, a Review session, a twin sheet on
Today and the run all tick the same plan.

**Data.** No new endpoint or column. `cfg.run` already exists (L8, §2.6). `/api/today.due.rows`
already carries `start`, `progress`, `status` and `task_id` (T2); it adds `run: {on, part,
parts}` (on when a session today has `cfg.run == <today>` and undone rows remain). S9's run page
accepts `then=run`; S5's lobby passes `run` into the sitting's cfg. `review.due` (S10) takes
T3's `progress.warmup_candidates` (F4) for its fading and keep-warm kinds; `/api/today.warmup`
stays for T3's held rate and forecast.

**Acceptance.**
1. Learner `a:v2revprodrun` with a plan day (fix 4, focus 10, recheck, words), 2 check-ins
   due, 2 fading types, `prefs.words_goal = 10`, 12 words due and the QOTD unanswered:
   `/api/today.due.rows | map(.kind)` is `["plan","plan","review","words","qotd",…]`, with
   exactly one `review`, no `warmup` and exactly one `words`; the review and words rows carry
   the plan's recheck and words `task_id`s. Start today creates a session with
   `cfg.run == <today>` and `cfg.task` equal to the fix task's id.
2. `GET /api/review/due` → `len(items)` equals the review row's `progress.of`, `left` equals
   `of - have`, and `/api/me.review.due_left` equals `left`.
3. Finishing part 1 shows the interstitial naming "Focus"; after the focus part it names
   "Review"; after the review part the run opens `/words/run/?…&then=run`; the words run's end
   shows the interstitial naming "Day's questions".
4. A `Study 15 min` session that answers 4 questions on the fix task's trap templates:
   `GET /api/plan` shows that fix task `done`, with no session tagged with it. Answering both
   check-ins in it ticks the recheck task and the review row's two check-in items.
5. The challenge row is never started by `UI.run.start()`; the receipt offers it.
6. After part 1 on desktop, `/?run=1` on a second device paired to the learner starts part 2.
7. Playwright at 1280 on `/`: exactly two `.pill` elements, one starting "Start today" and one
   starting "Study"; `#mist`'s action is a `.btn`. With a run on and the review row next,
   `/review/`'s pill reads "Start review · part 2 of".
8. `grep -rn "Do them in order" web/` is empty; `grep -rn "Keep going" web/` matches only
   `UI.run` and U1's box code.

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
`UI.verb`, `UI.KEYS`), F2 (`UI.keys` checks, `Z`), F3 (runner and player maps), S9 (Words
verdicts), S10 (Review's labels), every page owner (copy), I1 (the copy gate).*

**Why.** Our signature is "the same kind of question with new numbers, whenever you want". With
about 11 names for it and 7 more for its neighbours, plus Review's and Words' own, a student
never learns it as a habit. Theirs has two generic actions because a fixed bank can't do more.
One vocabulary and one key make ours the reflex: `T` after any question, on any page, Words
included. "Twin" is a short coined word, so it always explains itself where a tooltip can't.

**The verbs (`UI.VERBS`, F1 `kit.js`).**

| id | label | means | sublabel (visible, R42) | helper (tooltip, `?` sheet) | key | glyph |
|---|---|---|---|---|---|---|
| `twin` | `Twin` · `Twin ×n` · `Twin ▾` | the same kind of question, new numbers, with your trap when you missed (G3); in Words, a new text | `same kind, new numbers` (R&W: `same kind, new text`) | "Same kind of question, new numbers. Counts toward mastery." | `T`, menu `Shift+T` | two offset squares |
| `twin_set` | `Twin this set` | a set of the same types, new numbers | `same types, new numbers` | "The same question types, new numbers." | none | two offset squares |
| `twin_test` | `Twin test` | a sitting with the same slots, new numbers, scored like any test (T16, X20) | `same slots, new numbers` | "Same question types in the same places, new numbers, scored like any test." | none | two offset squares + clock |
| `again` | `Again, exactly` | the same question | `the very same question` | "The same question again. Doesn't move mastery." | `E` (players, lists; never in a running set, where `E` eliminates) | ↺ |
| `fix` | `Fix n` | a set on open mistakes, each a twin that keeps its trap | `your open mistakes` | "Two clean answers on questions with that trap close each mistake." | `F` on report and Review pages | ↻ (the Repaired mark, §2.3) |
| `learn` | `Learn this type` | a worked example on reserved numbers, then three of your own (T4, P2); opened from a miss, the example sits beside your miss with your trap outlined (V11's sheet) | `one solved, then three` | "See one solved, then try three yourself. Counts toward mastery." | in the Twin menu | open book |

* `UI.verb(id, {count, onClick, href})` renders a `.btn` (or the region's pill) with the glyph,
  the label, a `title` that names the key, and the sublabel as a second line
  (`.verb-sub`, 12 px `--soft`, inside the 44 px target) when
  `matchMedia('(pointer: coarse)').matches`, or when the learner has used that verb fewer than
  3 times on this device (`localStorage satf.verbs.seen {id: n}`, +1 per click, try/catch; blocked
  storage shows the sublabel). The `?` sheet lists every verb with its sublabel and helper.
* Retired phrases (every surface, every file): "Another like this", "Another one like this",
  "Another" (as a twin button), "Try one like this", "Try one now", "Try one", "Fresh one like
  this", "New one like this", "N more like this", "Fresh versions", "Again · new questions",
  "Practice again", "Retake as a test", "Retake as twin", "Redo these", "Fix these", "Drill it",
  "Learn it", "See one solved", "Now you: a new one", "Keep warm · n", "Another 10 min". A set
  of the same **topics** (not types) reads plainly, `10 more · Circles`; a quiz of two
  confusable words reads `Quiz the pair · 6`.
* Words' axes are items in the Twin menu, not their own buttons (R44): `Same word, new text`,
  `Same trap, new word`, and for Transitions `Same logic, new text`, `Same mix-up, new text`.
  After a miss, plain `Twin` in Words is the same word in a new text with the picked trap on
  offer (`another {like:'word', want_trap}`); after a right answer, the same word in a new text.

**Keys (R43).** One table, `UI.KEYS` (F1), declares the key of every question action:
`twin T`, `twin_menu Shift+T`, `details V`, `guess I`, `report R`, `save B`, `mark M`,
`note O`, `history Y`, `desmos Shift+G`, `again E`, `fix F`.
* Runner (practice session and test window): `D` only chooses D; **`V` Details** (practice);
  **`I` I'm guessing** (practice); **`R` Report** (both modes; in exam mode R17's live
  categories); `T` / `Shift+T` Twin and its menu after a verdict (practice, P18).
* Players (report review, Review pane, challenge and contest review): `T` Twin, `Shift+T` its
  menu, **`V` Details** (was `I`); `I` is unbound; Review's `U` next not yet seen stays. V11's
  "see one solved" is `Learn this type` in the Twin menu (from a miss it opens V11's
  side-by-side sheet), so `V` is free for Details.
* Words (flashcards and word quizzes): `I` guess, `T` Twin, `Shift+T` the Twin menu, `R`
  Report, `O` open word, `W` hint.
* Global (pages with the shell): `Q` stays the quick sheet everywhere, the runner included.
  **`Z`** presses the Undo of the most recent reversible toast while it shows (U25). Plan's page
  `U` becomes `Z`.
* **Checks** (`UI.keys.register(scope, map)`, F2), in `/dev/` pages only (production logs
  once):
  * a scope that binds one key twice throws `Error('key T already in runner')`;
  * **across scopes**: for scopes `runner`, `player`, `pane` and `words`, a key bound to a
    `UI.KEYS` action must be that action's declared key, and a declared key must not be bound to
    a different action, else it throws `Error('V is details in player but hint in words')`. The
    exceptions are listed in `UI.KEYS.except`: `E` (eliminate in a running set) and `O` (Open
    word in `words`, which has no note).

**Acceptance.**
1. The copy gate (`tools/product_gates.py copy`, I1) runs
   `grep -rniE "another (one )?like this|\btry one\b|(fresh|new) one like this|[0-9]+ more like this|fresh versions|again · new questions|practice again|retake as (a test|twin)|redo these|fix these|drill it|learn it\b|see one solved|now you: a new one|keep warm ·|another 10 min"`
   over `web/` and over the change column of every §3.2 table in `spec/v2-upgrades/*.md`, and
   both are empty.
2. `UI.VERBS` has `twin, twin_set, twin_test, again, fix, learn`, each with `label`, `sub`,
   `helper`, `icon`; every rendered `.verb` with a key has a `title` containing it.
3. Playwright with `hasTouch` at 390: every `.verb` on `/`, `/review/` and a Words quiz verdict
   shows a visible `.verb-sub`. At 1280 with a mouse, a fresh profile shows it on the first 3
   Twin clicks and not on the 4th.
4. Practice runner at 1280: `D` selects option D and opens nothing; `V` opens Details; `I`
   toggles I'm guessing; `Q` opens the quick sheet; `R` opens `UI.report` with
   `ctx.question_id` set. In the report player, `V` opens Details.
5. A Words quiz verdict: `T` loads a new item with the same `word`; `Shift+T` opens the Twin
   menu with `Same word, new text` and `Same trap, new word`, and loads nothing by itself.
6. Unsave a question, then press `Z` while the toast shows: `GET /api/saved` contains it again.
   On `/plan/`, `Z` undoes a skip; `U` does nothing.
7. On `/dev/workspace.html`: registering `T` twice in scope `runner` throws; registering
   Details on `Q` in `runner` while `player` has it on `V` throws; registering `E` as eliminate
   in `runner` and Again in `player` does not.

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
2. **Every twin of a miss on a named trap sets it.** With `want = {template: '^' +
   re.escape(norm) + '$'}` from the trap: the repair after a miss (`drill._pick`'s `rep`), pools
   `redo` and `checks`, `from_session` twins (T5, SR, X16), `like` (a missed day's question),
   `/more {axis:'same'}` (P18), U28 links when the sender missed, the start set's repairs (G10),
   the official pad's twin (G16), Words' `another` (as `want_trap`, R57), and `UI.twin` from any
   surface. Compete's `rematch scope:'misses'` already does it (C2). After a right answer, and
   for a trap with no named norm (rule 4's second group), there is no `want`: a plain twin.
3. **Fallback.** Nothing in 60 seeds → the plain next seed, `feedback.trap_true = false`, and
   one line above the stem: `This type didn't offer that trap again; here's the closest.`
4. **Close rule** (F4, `progress.record`, R9), by the trap's kind:
   * **Named traps**: kind misconception (an MC reason, an R&W trap id), and grid-in traps
     whose template has `spr_mistakes`. A clean answer lowers `owed` only when
     `attempts.offered` (P6) contains the trap's norm, or the grid-in item's `spr_reasons` do.
     Other clean answers on the template count for mastery and nothing else. The verdict's next
     step (P9) reads `This one didn't offer "used the diameter" · 1 still to close it` in that
     case.
   * **Unnamed traps**: kind unsure (norm `~unsure`, including outside-logged ones from
     `POST /api/mistakes/add`, U2), kind slip (a filler "near-miss arithmetic slip", or R47's
     slip causes), and grid-in misses with no named value (norm `''`). These can never appear in
     `offered`, so v2's rule holds: any clean answer on the template lowers `owed` (an unsure
     owes 1, the others 2, R9).
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
7. Every kind reaches Fixed (`server/checks/f4.py`): a flagged-right unsure trap closes after
   one clean answer on its template (Part 3 Review acceptance 7); an outside-logged `~unsure`
   trap closes after one; an unnamed grid-in trap (norm `''`) closes after two; a filler slip
   trap closes after two, whatever `offered` holds. A misconception trap does not close on two
   clean answers whose `offered` lacks its norm.
8. An R&W miss picking a `too_strong` option opens a trap with norm `too_strong`; a twin of it
   offers a `too_strong` option; a clean answer on an item with no `too_strong` option leaves
   `owed` unchanged.

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
question (F2), the verdict of a generated R&W item in a Words run or word sheet (S9, R57; the
row adds W1's `Open word`, and Desmos way is absent), and the official pad's verdict (G16, S4;
Save, Mark, Note and History are absent there, since the question is College Board's).

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
or a tutor sees what the type asks, one solved, every trap it sets, your record and the way in.

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
1. For all 386 Math templates and every registered R&W template (R57), `GET /api/types/{t}` is
   200 and has `name`, `about`, `subject` and `weight`.
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
`readiness`, `accuracy:<topic>:<days>`, `minutes:<today|week|month>`, `due_today` (from
`review.due`, R56). Each calls the function the
page's own payload uses. `excluded` names what was left out: `14 exact repeats · 3 disputed · 4
right guesses count half`.

**Client.** `UI.fact(el, key)` (F1): a button that shows its cue on every pointer type, so a
student on a phone sees which numbers open: the value keeps a persistent 1 px dotted underline
(`--soft`), and a small ⓘ glyph (DM Mono 11 px, `--soft`, `aria-hidden`) follows it. On
`pointer: coarse` the button's hit area is at least 44 × 44 px (padding plus a `::after` hit
box, no layout shift). It opens a `UI.pop` (a bottom sheet under 760 px) with How · Your
numbers · Left out · What moves it · `Same number on: Today · Me · Results`. Its accessible name
is `<label>: <value>, show how it's worked out`. F1's kit specifies the cue once; F2 delegates:
any element with `data-fact="<key>"` gets the cue and opens on click or Enter, so pages only add
the attribute. Used on every stat tile, chip and meta: Today's hero chips, Me's tiles, nav-meta
tooltips, score cards, skill rows, report tiles, Plan's stat tiles, the Due header and the
review row's count, Review's stat strip, your Compete row.

**The gate (I1, `tools/product_gates.py facts`).** For three seeded learners (new, mid, heavy)
it fetches `/api/shell`, `/api/today`, `/api/today/insights`, `/api/me`, `/api/me/summary`,
`/api/plan`, `/api/review/counts`, `/api/review/due`, `/api/stats`, `/api/next` and compares a
table of (fact, endpoint, JSON path): study streak, open mistakes, **due today** (the review
row's `progress.of` and `of - have`, `/api/review/due` `total` and `left`,
`/api/review/counts.due_left`, `/api/me.review.due_left`, and Up next's `checks` count against
the review row's check-in items), minutes today, target, exam date, points total, the top
skill's points, one trap's points, the estimate band, active days. It exits non-zero naming the
fact and both values. It runs in I1's walk.

**Acceptance.**
1. `GET /api/levers?keys=streak,open_mistakes,due_today` → each key with `how` and non-empty
   `inputs`.
2. On `/`, `/results/`, `/plan/`, `/review/` and `/compete/`, every `[data-fact]` opens a
   popover on Enter; Esc closes it and returns focus.
3. Playwright with `hasTouch` at 390 on the same pages: every `[data-fact]` renders its ⓘ cue
   and a dotted underline with no hover, and its bounding box (with the hit box) is at least
   44 px tall.
4. `accuracy:<topic>:30`'s `excluded` lists repeats and disputed answers with counts for a
   learner who has both.
5. The gate passes on the seeded learners; with the shell's streak patched to +1, it fails and
   names `streak`; with `/api/review/due` returning one extra item, it fails and names
   `due today`.

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
* **Read aloud.** A visible, labelled tool in the question strip (icon plus `Read aloud`), on
  every screen size, wherever it is allowed: practice, review players, the Review pane, type
  pages, Words items and the official pad's list. Under 760 px it sits in R50's tools row, never
  in a menu. It reads the plain stem, then the figure's alt, then `A, …` through `UI.speak`
  (speechSynthesis), with a small spoken-math map (π "pi", ² "squared", √ "the square root of",
  a/b "a over b", ≤ "is at most", − "minus"); while it speaks the button reads `Stop` (`aria-
  pressed`). In the test window it appears only with `test_timing` x1.5 or x2, as Bluebook
  offers text-to-speech only as an accommodation. Where `speechSynthesis` is missing the button
  is absent. `ponytail:` a 12-rule replacer, not MathSpeak; move to Speech Rule Engine if
  students report misreads.
* **Phone tools row (R50, F3).** Under 760 px the runner renders `.tools-row` between the
  question and the footer: Calculator, Reference, Eliminate, Hint, Desmos way and Read aloud,
  each present only where its mode allows it, each a 44 px button with icon and text, wrapping to
  a second line. The footer keeps Mark, Back and Check/Next (X6).

**Acceptance.**
1. `tools/bank_coverage.py` prints a `figure_alt` line (`n of 76 figure templates`), the audit
   passes for every topic committed, and G14's launch gate requires 76 of 76.
2. Playwright on a figure question: `.q-figure[role=img]` has a non-empty `aria-label`; a table
   question has as many `th` as columns; a KaTeX stem contains a `math` element.
3. With `speechSynthesis.speak` stubbed, Read aloud on a π stem passes text containing "pi".
4. On `/test/` with `test_timing: 'official'`, no Read aloud control exists; with x1.5 it is a
   visible button.
5. Practice runner at 390 with no menu or sheet open: Calculator, Eliminate, Hint, Desmos way
   (on a type with a route) and Read aloud each match a visible `button` whose text contains its
   label, each at least 44 px tall, and `document.documentElement.scrollWidth === 390`. No
   `⋯` control exists in the runner footer.

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
* **The action follows the learner (R55).** With 0 answers, every empty state's action is
  `Start with 8 · about 10 min` (`{source:'start'}`, G10), never "Take the diagnostic". With
  answers, it is the card's own smallest set, labelled with `UI.VERBS` (usually `Twin`, inline).
* Used by every card's empty state (Today, Me, Review's page and tabs, Results, Plan Progress,
  Compete history, Words). No card builds its own empty panel.
* **Review (V16) through `UI.empty`.** A new learner's Review: `sample` is V16's Example row
  (a real reserved item from `GET /api/types/{t}/example`, tagged `Example`, opening the pane
  read-only with every option's reason); `text` is `Your mistakes appear here, each named, with
  what fixes it`; `action` is `Start with 8 · about 10 min`. A returning learner with nothing
  open: the action is `Twin` inline on the coach's pick (V16's live row: a wrong answer makes the
  first real Redo row appear without a reload). Empty Marked, Saved and History tabs use the same
  call; an empty History modal offers `Twin` on its template.

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
4. A new code at 1280 on `/review/`: one `.empty-sample` tagged `Example`, and the action's label
   starts "Start with 8"; no element's text contains "Take the diagnostic" or "Try one now". For a
   learner with 5 answers and nothing open, the action is a `.verb` Twin that runs inline.

#### G15. Sign-in in one tap on any device: Google as well as passkeys

*From: the outcomes and unfair-advantage sign-in gaps; answers open question 5 (R58). Effort S.
Builders: S1 (`server/api_account.py` route, `/signin/`, the save nudge, Settings), F4
(`users.google_sub`).*

**Why.** Theirs is Google in 2–3 taps on any device already signed in to Google. A passkey only
helps once it is saved and synced; a student switching between a school Chromebook and an iPhone
meets the browser's QR walk or an email code that needs SMTP. Google as one more method keeps
their fastest path, without their wall, on top of everything ours adds.

* **Where.** `/signin/`, the save nudge (U19's `Save your progress`), and Settings → Sign-in
  methods. Order: `Use your passkey` first where
  `PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()` is true, then `Continue
  with Google`, then `Email me a code`, then `Pair with a device`.
* **Client.** Google Identity Services (`https://accounts.google.com/gsi/client`, free), the
  standard button, `ux_mode: 'popup'`, One Tap off (nothing appears unasked). It posts the ID
  token credential to the server. Hidden when `GOOGLE_CLIENT_ID` is not configured.
* **Server (S1).** `POST /api/auth/google {credential}`: verifies the token with Google's
  `tokeninfo` endpoint (stdlib `urllib`), checks `aud == GOOGLE_CLIENT_ID`, `iss`, `exp` and
  `email_verified`, then:
  * the `sub` is new and this device's learner has no account: link it to this learner
    (`users.google_sub`, and `users.email` when empty), so the anonymous work is the account;
  * the `sub` belongs to an account: sign this device in to it, and carry this device's
    anonymous learner into it with the pairing claim's `carry` when that learner has rows and
    no account;
  * a signed-in learner linking from Settings: attach the `sub`, 409 when another account has it.
  * `ponytail:` one `tokeninfo` round trip per sign-in; verify locally against Google's keys if
    sign-in volume grows.
* **Data.** `users.google_sub TEXT UNIQUE` (§2.5). Export lists `google: true`; delete removes it.

**Acceptance.**
1. With `tokeninfo` stubbed to a valid payload for a new `sub`: `POST /api/auth/google` on an
   anonymous learner with 12 attempts returns that learner, and `users.google_sub` is set.
2. A second device, anonymous with 3 attempts, signing in with the same `sub`: afterwards the
   account has 15 attempts.
3. A payload with the wrong `aud`, `email_verified: false` or a past `exp` → 401, nothing linked.
4. `/signin/` with `GOOGLE_CLIENT_ID` unset renders no Google button and no error; set, it
   renders it after the passkey button on a device with a platform authenticator.

### F. The whole SAT and the bank

#### G11. The subject axis: the full SAT is additive, and R&W starts with a real bank

*From: the Reading & Writing gaps of all three designers, decisions 2 and 3; reconciles
`words.md` W1, W2, W5, W19, W21 (R51, R57). Effort M. Builders: F4 (`deps.subject_of`,
validation, `attempts.word`, `progress.record` for R&W), F5 (the catalogue registration, drill
and `want` for `rw.*`), S9 (`rw_items` behind the catalogue, Words runs filing attempts,
`words.rw_answers`), every owner (their payloads and endpoints), S6 (the R&W row), S7 (R&W
tasks).*

**Why.** Decision 3: Math-first now, the full SAT later, built so the expansion is additive.
Every upgrade file says its payloads "carry `subject`", each in its own way; one contract now
costs little, seven dialects would have to be torn out. And `words.md` already builds an R&W
generator in the bank's Item shape. Kept inside Words, it would be a second question system
(its own mistake rows, twins and schedule) to tear out when the R&W bank lands, which decision
3 rules out. Put behind the same catalogue, its items get everything a Math item gets today.

**Contract (R51).**
* `subject` is `math` or `rw`. `deps.subject_of(topic)` (F4) maps the 19 Math topics to `math`
  and `words-in-context` and `transitions` to `rw`; later R&W topics join the same map.
* No subject column: a row's subject is template → topic → subject. Sessions carry
  `cfg.subject` (default `math`). Words runs, word reviews, R&W own tasks (L11), `rw_now` /
  `rw_target`, `outside_scores.rw` and `contests.subject` (C14) are `rw`.
* Every section endpoint takes `?subject=`, default `math`; an unknown value → 422. Math readers
  (mastery, U8 readiness, the estimate, boards, the Math coverage) filter to `math`, so R&W
  attempts never move a Math number.
* Where no bank exists: `/api/bank?subject=rw` lists the two generated skills with
  `available: true` and every other R&W skill with `available: false`; `POST /api/drill
  {subject:'rw', topics:['boundaries']}` and `POST /api/mock/new {subject:'rw'}` → 409
  `{reason:'no_bank'}`.
* Shared components take labels from data (`UI.SUBJECT[subject].label`), never a literal "Math";
  the runner keeps its empty passage region and renders an R&W item's `text` in it (tests.md).
  P15's subject switch shows once `rw` has a bank, so it shows now, with the two skills.

**The first `rw` bank (R57).**
* **Catalogue (F5).** `rw_items` templates register as catalogue entries: `rw.wic.<frame>` and
  `rw.nearly.<entry>.<n>` under topic `words-in-context`, `rw.tr.<family>` under `transitions`,
  skill and domain as College Board names them (Craft and Structure, Expression of Ideas), tiers
  from each frame's `difficulty`. `catalogue.generate(template, seed, word=None)` dispatches
  `rw.*` to `rw_items.item` or `rw_items.transition`; everything that serves questions calls it.
* **Served like any question.** `GET /api/types?subject=rw` lists them with `available: true`
  and their trap ids as reasons; `POST /api/drill {subject:'rw', topics:['words-in-context']}`
  serves them in the practice runner (instant feedback, repairs, `want` over `traps[]`); the
  type page (G7), Details and `UI.questionActions` work unchanged. A drill serves `word=None`,
  so `(template, seed)` is the address; a Words run keyed on a word adds `word`.
* **One answer record (F4).** Every answer to a generated R&W item (a Words run, a word sheet
  sample, T14's two R&W slots, a drill) goes through `progress.record` into `attempts`, with new
  nullable `attempts.word TEXT` (NULL for Math). `offered` holds the item's trap ids. A miss
  opens a trap of kind misconception, norm = the picked option's W1 trap id (W2: `wrong_logic`
  or `reversed_direction`), label from `traps.json`'s name, `subject` from the topic. So Review
  lists it, `Fix n` and check-ins serve twins with `want_trap`, `progress.related(norm)` finds
  the same trap across frames (`Same trap, new word`), and it closes by G3's rule 4.
* **Words keeps its schedule.** `word_reviews` still holds the word's box and due date; a row
  made from a generated item carries `attempt INTEGER` (the attempt's id) and its minutes count
  once, through the attempt (R13). `words.rw_answers` (W1's one accessor) reads `attempts`, so
  W5's trap profile, W7's proof ladder and W13 read the same rows as Review. W1's planned
  INSERT…SELECT move is not needed: the rows are there from the first answer.
* **Logging an R&W miss** (U2, W19): `POST /api/mistakes/log {template: 'rw.wic.<frame>' |
  'rw.tr.<family>', reason: <trap id>, origin: 'bluebook' | 'cb_qbank'}` opens the same trap.
  An R&W official ID resolves through P11's index to its skill; when the skill is one of the two,
  it logs and serves 3 twins; otherwise it reads `Logged for the R&W bank`.

**What students see now.**
* Practice: a Reading & Writing seg with **Words in Context · unlimited** and **Transitions ·
  unlimited**, each with its traps, a builder like Math's and the same runner.
* Review: R&W mistakes beside Math ones, with a subject chip and a subject filter.
* Results gains a **Reading & Writing** row: the two skills' accuracy and open traps from
  `attempts`, Words (known, due, Word Sprint rating, C14), logged Bluebook or official R&W scores
  (`outside_scores`), and the 1600 total when both sections have a score (R16's combined). No
  R&W score is estimated from two skills (R48).
* Today's study time and the streak count Words and R&W practice (R13); Plan's R&W own tasks and
  the Words task count toward the day (L11, L4).

**Acceptance.**
1. `GET /api/bank?subject=rw` → 200, `words-in-context` and `transitions` with
   `available == true`, and any other listed R&W skill `available == false`; `?subject=xx` →
   422.
2. `GET /api/types?subject=rw` lists every `rw.*` template with `subject == 'rw'`;
   `POST /api/drill {subject:'rw', topics:['words-in-context'], count:5}` serves 5 items whose
   `text` contains `____`; `POST /api/drill {subject:'rw', topics:['boundaries']}` → 409
   `no_bank`.
3. A wrong answer in a Words run on a generated item writes one `attempts` row (template `rw.*`,
   `word` set) and one `word_reviews` row whose `attempt` is its id; `GET /api/review/redo`
   lists a trap with `subject == 'rw'` and the trap's name as its label; `/api/today.study.today`
   rose by the attempt's minutes once.
4. After that miss, the learner's Math mastery, readiness and estimate payloads are unchanged.
5. `GET /api/next`, `/api/today/insights` and `/api/plan` items carry `subject`.
6. `grep -n "'Math'\|\"Math\"" web/assets/ui.js web/assets/kit.js web/assets/question.js web/assets/runner.js`
   returns only the `UI.SUBJECT` table.
7. A learner with a logged R&W 610 and a Math band: Results shows the R&W row and a 1600 total.

#### G13. One sheet before the test, and one final check

*From: unfair-advantage #9; reconciles `review.md` V19, `plan.md` L19 and `today.md` T13 (R60).
Effort S. Builders: S7 (the page and `GET /api/plan/sheet`), S10 (`review.trapsheet`, the
redirect, the Due tab link), S3 and F2 (the Final check row), with data from P21, P16, P3, T7,
T13.*

**Why.** The last week's advice was spread over five places, and the drafts gave it three print
URLs (`/plan/?print=sheet`, `/plan/?print=traps`, `/review/print.html?sheet=traps`) and two
final-week flows (V19's exam-week card with its own `Final check · 10`, and T13's final stretch
with L19's eve task). One printable page of your own traps, rules, skips, Desmos types and
grid-in slips, and one final check in the Due list, is what a tutor would hand a student on the
eve.

* **Your test-day sheet**, at `/plan/?print=sheet` only (it works without a plan), readable on a
  phone and printable (A4 or Letter, 11 pt; a second page when long; nothing cut, ordered by
  value):
  1. Your traps: `review.trapsheet(learner, n=10)` (V19's entries: U6's top habits, then the top
     open or relapsed traps by points, each with label, hits and tell, a reserved example walked
     for the trap with `Your trap` marked, the key and the rationale's first sentence, your rule
     when one exists, and `dodged 4 of the last 5`). L19's `GET /api/plan/{id}/trapsheet`
     returns the same list.
  2. Your rules (P21's type rules, by domain).
  3. Skip first: types whose median is over 1.5× the budget and first-try accuracy under 50%,
     top 5 by U8 weight (P16).
  4. Use Desmos on: types with a verified route where your hand median is over 60 s (P3).
  5. Grid-in rules you broke (T7's `entry` items, grouped by rule).
  6. The test-day checklist (T13).
* **One URL.** `/plan/?print=traps` and `/review/print.html?sheet=traps` answer with a redirect
  to `/plan/?print=sheet#traps` (a 302 from the server, or `location.replace` where the page is
  static). V19's error log (`/review/print.html?sheet=log`) stays: it is every open mistake, a
  different list.
* **Final check** (was V19's exam-week card): from 7 days before `exam_date`, a Due row of kind
  `final_check` in T13's final stretch, `Final check · one fresh question per trap on your sheet
  · 10 · ~16 min`, starting `{templates: the sheet's templates, count: 10, timing:'pace',
  order:'mixed', source:'mistakes'}` with `want` per trap (G3). It is done once finished in the
  last 7 days; the run walks it like any row. Review's Due tab shows one line `Your test-day
  sheet` (a link) in the same week instead of a card.
* Linked from T13's final stretch, L19's eve task (`Read your test-day sheet · 5 min`), Review's
  Due tab, Me, and SR17's lobby briefing.

**Acceptance.**
1. `GET /api/plan/sheet` for a seeded learner returns six sections, each a list (empty lists
   allowed) and no answer keys other than reserved-seed examples; section 1's templates equal
   `GET /api/review/trapsheet`'s in order.
2. `/plan/?print=sheet` renders for a learner with no plan.
3. `/plan/?print=traps` and `/review/print.html?sheet=traps` end on `/plan/?print=sheet`.
4. With `exam_date` 5 days away: `/api/today.due.rows` has one `final_check` row, and
   `/review/` has no exam-week card; 9 days away, no such row.

#### G14. One pass through the bank: every new field per family, audited, one coverage report, and a launch gate

*From: experience #2, unfair-advantage #4, #12; the T-bank asks of P1, P3, P4, P18 and G8; the
Words content review (open question 2). Effort L. Builders: T-bank (the Math pass), S9 (the
Words audit), I1 (the gate).*

**Why.** Four upgrade files each ask T-bank for a field (grid-in mistakes, steps with the step
each mistake breaks, the Desmos route, `ask` in params, figure descriptions). All of them live in
the same 386 family files, so four tasks would collide, and a field that is not audited could
teach a wrong step. One pass, topic by topic, adds every field to a family at once and proves it.
Steps are what makes our explanation beat their prose, so they are not allowed to ship partial:
at launch every question has them, or the explanation is a one-sentence rationale and we are at
parity. The Words content (about 1,090 definitions, about 300 frames, sense features, trap tags)
had no check beyond a verifier that re-derives from the same features, so a wrong feature
passed.

* **Fields**: `spr_mistakes` (spec), `steps` and `step_of_reason` (P1), `desmos` and
  `desmos_read` (P3), `ask` recorded in params (P18), `figure_alt` (G8).
* **Launch fields**: `steps` with `step_of_reason` on every template (386 of 386, which is
  100% of U8 weight), and `figure_alt` on every figure template (76 of 76). `spr_mistakes`,
  `desmos` and `ask` ship partial and grow; the site never says those are missing (P1's rule).
* **Order**: one commit per topic, heaviest first by attempt volume × U8 weight, each touching
  only that topic's files and landing that topic's launch fields for all its templates (the
  other fields in the same commit where ready, else a later commit for the same topic). T-bank
  runs from wave 1a through wave 2. At the middle of wave 2, if `bank_coverage.py` shows under
  60% of U8 weight with steps, T-bank splits into T-bank-a (Algebra, Advanced Math) and
  T-bank-b (Problem-Solving & Data Analysis, Geometry & Trigonometry), each owning its topics'
  family files; commits stay topic-scoped, so they never collide.
* **Audit checks** (in `satbank/audit.py`, run by `python3 -m satbank check`, per field): no
  `spr_mistakes` value equals the key; the last step's value equals the key (numeral or
  `norm_text`) and each step's numbers come from params; `step_of_reason` indices are valid;
  the Desmos route, solved numerically from the same expressions, lands on the key;
  `figure_alt` names every drawn label and given number.
* **Coverage**: `tools/bank_coverage.py` (replaces `tools/spr_coverage.py`) prints `n of N` per
  field, per topic and as a share of U8 weight. `--gate` exits 1 unless the launch fields are
  complete and the audit passes. `tools/product_gates.py bank` runs it; I1 does not sign off
  below it.
* **The Words audit** (S9, `tools/words_audit.py`, stdlib, run by I1 before Words ships):
  * **Definitions**: each entry's part of speech must be one WordNet gives the lemma, and its
    definition must share at least one content lemma with a WordNet gloss or synonym of that
    lemma (stop words removed). WordNet 3.1's database files (`material/wordnet/`, the WordNet
    licence allows reuse with its notice) are parsed directly.
  * **Frames, by a second method**: W1's verifier re-derives from the sense features, so this
    check ignores them and uses WordNet relations. `classes.json` gains `seeds` (3–5 WordNet
    lemmas per class, set by hand). For 20 seeds of every frame, the key must reach a seed of
    the frame's class within 2 synonym, similar-to or hypernym hops; no distractor may share the
    key's synset unless its trap is `too_strong`, `too_weak` or `connotation`; a `reversed`
    distractor must reach an antonym of a seed within 2 hops. Transitions: each family's key and
    distractors are checked against `logic` by a hand table of 70 transitions → logic,
    independent of `logic_reasons`.
  * **Queue**: every mismatch is written to `server/words/review_queue.json` (`{kind, id,
    field, ours, wordnet}`). A reviewer either fixes the content or clears the item, signed in
    `server/words/review_log.json` (`{id, verdict, reviewer, date}`). Words ships only with an
    empty queue. The reviewer is named in open question 2 (default: the site owner).
  * `ponytail:` WordNet overlap is a heuristic and flags some good entries; the human queue is
    the check, the script only aims it.

**Acceptance.**
1. `python3 tools/bank_coverage.py` prints one line per field with its share of U8 weight and
   exits 0; `--gate` exits 1 while any template lacks `steps` or `step_of_reason`, or any figure
   template lacks `figure_alt`.
2. `python3 -m satbank check --topic <topic>` passes after every topic commit.
3. `git log --stat` on the T-bank branches: each commit's files are under one topic.
4. I1's walk: `tools/product_gates.py bank` exits 0 before sign-off.
5. `python3 tools/words_audit.py` exits 0 on the shipped content with an empty queue. In a temp
   copy where one entry's part of speech is changed to one WordNet lacks, or a frame's key is
   swapped for a word in another class, it writes that item to the queue and exits 1.

#### G16. Official questions on our answer pad

*From: the unfair-advantage official gap; reconciles P13, U2 and open question 17 (R59). Effort
M. Builders: S4 (`web/practice/official/**`, `api_practice.py`), F5 (the twin, through P13's
search), F4 (`official_done`), U2's `types.py` (the map and reasons).*

**Why.** A free TopTierPrep student's core practice is College Board's 1,921 official Math items
in filtered QBank sessions with a Solved filter. We can't serve College Board text (content
terms), and P13 only helps after the fact, with a paste. The pad keeps their whole workflow and
adds what their QBank can't: the wrong pick named (2,186 of 2,367 official wrong options
resolve, 92%), a mistake with check-ins, and a trap-true twin at once.

**The list** (`/practice/official/`, linked from the builder's "Questions from", each SkillRow's
`Official questions on College Board · 142`, the palette `official`, and P13's result list).
* Rows are the 1,039 official IDs in `material/keys` (the ones we hold keys for): `84664a7c ·
  Circles · Medium · MC` with the status `Not done` · `Solved` · `Missed · used the diameter` ·
  `Missed, then twin right`.
* Filters (a sticky bar): domain, skill, tier, format, status (`Not yet done` default · Missed ·
  Solved · All), and `Only types built from official questions`. The header counts: `142 in
  Circles · 38 done · 9 missed`.
* `Start · 10` walks the filtered list in order, one ID at a time; progress per ID is kept, so
  `Not yet done` resumes where the student stopped. Any row also opens on its own.

**The pad** (one ID at a time, one column 760 px):
* The ID in DM Mono 20 px with `Copy ID`, and `Open on College Board ↗`: a new tab on College
  Board's free question bank, at the question where its URL accepts an ID, else at the bank with
  the ID copied for its ID search. The page says `The question opens on College Board. Answer it
  here.`
* The answer pad, from the key file's format: `A · B · C · D` (44 px) for MC, or a grid-in field
  with R34's entry rules; `Enter` checks. A quiet `Skip`.
* The verdict, through `UI.questionActions` (G4): right → `Solved`; wrong → the key's letter or
  value, and U2's `POST /api/types/match/pick {cb_id, letter | value}` → the named reason when
  one resolves (`You picked C: used the diameter as the radius`), else `Not named yet` with U2's
  paste-or-pick; the mistake opens (U2's log path, `source 'outside'`, `origin 'cb_qbank'`); the
  primary is **Twin** (P13's search at the official tier, with `want` from the reason, G3),
  answered inline before `Next ID`.
* After a right answer on an ID with an exact map, `Twin` is a `.btn` for more on that type.

**Server (S4, F4).**
* `GET /api/official?domain=&skill=&tier=&status=&limit=&after=` → `{total, done, missed,
  rows:[{cb_id, topic, skill, tier, format, status, reason?, template?}]}`, from
  `material/keys` joined with U2's map and the learner's `official_done`.
* `POST /api/official/answer {cb_id, pick, ms}` → `{right, key, reason, trap_id, twin:{body}}`.
  The key is read from the key file and returned only after the pick. 404 for an ID not in
  `material/keys`.
* New learner table `official_done(learner, cb_id, pick, right, ms, at)`, PK `(learner, cb_id,
  at)`, in `LEARNER_TABLES` and `carry`. Its `ms` (capped at 10 min) counts toward study time and
  the study day (R13); it never counts toward mastery or the estimate, which read our own
  questions. The twin's answers are ordinary attempts.
* No response carries official stem, choice or explanation text (U2's rule and check).

**Acceptance.**
1. `GET /api/official?skill=<circles skill>` → `total` equals the circles IDs in
   `material/keys`; no row contains a `stem`, `choices` or `text` key.
2. `POST /api/official/answer` with a wrong letter on an ID whose wrong option resolves →
   `reason` non-empty and a trap with `source == 'outside'`; the returned twin body served
   offers that reason (G3).
3. Afterwards `status == 'missed'` for that ID, `Not yet done` no longer lists it, and
   `/api/today.study.today` rose by the answer's minutes.
4. `POST /api/official/answer` for an ID outside `material/keys` → 404.
5. At 390, the pad's four letter buttons, `Open on College Board` and `Copy ID` are on screen
   without scrolling.

---

## 3. Spec overrides

### 3.1 Inside `spec/rebuild-v2.md` lines 1–648 and 10970–11183

Each entry quotes the current text, then gives the replacement or addition.

1. **Header (lines 3–6).**
   * Quote: "Written 2026-09-23. This file replaces `spec/rebuild.md` as the plan and the state
     for the site. `spec/rebuild.md` stays as the record of the first rebuild."
   * Append: "The upgrades that take each section past parity are in
     `spec/v2-upgrades/<section>.md`; the rules where sections meet are in
     `spec/v2-upgrades/product.md` (G1–G16, R39–R60). `spec/v2-decisions.md` wins over all of
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
   * Add after that bullet: "* Where two upgrade files disagree, **R39–R60** (from
     `v2-upgrades/product.md`, appended to §2.2) win. Order: `v2-decisions.md`, then R39–R60 and
     `product.md`'s G-upgrades on the seams they name, then each `v2-upgrades/<section>.md`,
     then Part 3, then Part 2."

6. **§2.1 rule 1 (lines 92–95).**
   * Quote: "Every empty state says what will appear there and offers the action that fills it."
   * Replace with: "Every empty state shows one dimmed sample row of what will appear, says what
     it is, and offers the smallest action that fills it with its cost, runnable in place
     (`UI.empty`, G12)."

7. **§2.1 rule 5 (lines 108–110).**
   * Quote: "each comes from one server function and reads the same on every screen."
   * Replace with: "each comes from one server function, reads the same on every screen, shows
     a visible ⓘ on every device and opens its working (`UI.fact`, `GET /api/levers`, G6). I1's
     facts gate checks it on every endpoint, the due count included."

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
      exactly, Fix n, Learn this type (R42, G2), each with its visible sublabel on touch screens
      and its first 3 uses; the retired phrases in G2 never appear."

11. **§2.1, new rules after rule 12.**
    * Add: "13. **Speed is measured.** Check → verdict ≤ 100 ms p95; Next → next stem ≤ 50 ms with
      no request; a revisited page paints cached content within 150 ms; Today's first visit
      LCP ≤ 2.5 s under mobile throttling (150 ms RTT, 1.6 Mbps, 4× CPU); CLS ≤ 0.02 (G9's gate)."
    * Add: "14. **One question, one row.** Every surface that reveals a question uses
      `UI.questionActions` and the shared verdict slot (R49, G4)."
    * Add: "15. **Readable without sight.** Figures carry generated descriptions, tables real
      headers, math MathML; Read aloud is a visible tool wherever it is allowed (G8)."

12. **§2.2 (after R38, line 174).**
    * Append rows R39–R60 exactly as in §2 A of `v2-upgrades/product.md`.
    * In R4, replace the decision with: "Void (decision 5). There are no classes; Compete's
      private contests are an invite code or link that Compete owns (C18)."
    * In R10, quote: "`word` and `confusion` (S9, `words.resolve_drill`), `assignment` (S2,
      `classes.resolve_drill`)" → replace with: "`due` (S10, `review.resolve_drill`, V1, R56);
      `rw.*` templates are served by F5 through the catalogue (R57), so Words needs no resolver"

13. **§2.4, `kit.js` row (line 230).**
    * Quote: "`UI.ics(event)` (one event, or a daily repeating reminder) |"
    * Replace with: "`UI.ics(event)` (one event, or a daily repeating reminder). Product:
      `UI.VERBS`, `UI.verb(id, opts)` and `UI.KEYS` (G2), `UI.pts(el, pts, key)` (G5), `UI.fact(el,
      key)` with its visible cue (G6), `UI.empty(host, {sample, text, action})` (G12),
      `UI.SUBJECT` (G11) |"

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
      (G9); X6's phone footer, gestures and answer pad for both modes, and the visible tools row
      under 760 px (R50) |"

16. **§2.4, `ui.js` row (line 225).**
    * Quote: "`UI.SAT_DATES`, `UI.chip`, `UI.ref`, `NAV`, `SECTION`, `TOPICS` + aliases |"
    * Replace with: "`UI.SAT_DATES`, `UI.chip`, `UI.ref`, `NAV`, `SECTION`, `TOPICS` + aliases;
      `UI.run` (`start`, `between`, `rail`, G1); `[data-fact]` delegation (G6); `Z` undo, the
      duplicate-key check and the cross-scope key check (R43); optimistic toggles (G9) |"

17. **§2.5, "Not added" (lines 296–302).**
    * Quote: "Dashboard's `plan_marks` (its own shape) and `learners.plan_started`."
    * Append: "Nor, from the upgrade proposals: `type_state`, `type_memory`, `boxes`,
      `skill_memory` (R53), `estimate_log` (no practice score, R48), offline-pack tables (§4 of
      `product.md`). `traps.closed_how` gains the value `transfer` (G3). Added from `product.md`:
      `attempts.word TEXT` and `word_reviews.attempt INTEGER` (R57), `users.google_sub TEXT
      UNIQUE` (G15), the learner table `official_done(learner, cb_id, pick, right, ms, at)` (G16).
      Removed by decision 5: every class, membership, assignment and class-code table."

18. **§2.6, `want` row (line 328).**
    * Quote: "| `want` | {template: regex} | walk up to 40 seeds for an item where some option's
      reason matches (a mix-up drill, same-mistake-elsewhere) |"
    * Replace with: "| `want` | {template: regex} | walk up to 60 unseen seeds for an item where
      some option's `progress.norm(reason)`, a grid-in's `spr_reasons` value, or an R&W item's trap
      id matches. Set by the server from the trap's norm on every twin of a miss on a named trap:
      the repair, pools `redo` and `checks`, `from_session` twins, `like`, `/more {axis:'same'}`,
      twin links and the official pad's twin (R45, G3); unsure, slip and unnamed grid-in traps
      get none; a miss in 60 seeds serves the plain next seed with `trap_true: false` |"

19. **§2.6, `source` row (line 347).**
    * Quote: "| `source` | map, coach, plan, today, mistakes, review, quick, palette, assignment,
      outside, twin, try, word-example, words, worksheet, shared, qotd, spot |"
    * Replace with: "| `source` | map, coach, plan, today, mistakes, review, quick, palette,
      outside, twin, try, words, worksheet, shared, qotd, spot, and from the upgrade files:
      next, due (V1, R56; resolved by `review.resolve_drill` through R10's registry), warmup
      (T3's warm-up, an alias of `due` with count 5, R46), learn, start (G10), prep (Compete's
      lobby drill, R46), probe, habit, gauntlet, bluebook, official (P13, G16), sprint,
      rematch, finish, gain, pace, fix, confirm, rush |". `assignment` is gone (decision 5);
      `word-example` is gone (decision 2, `words.md`).

20. **§2.6, drill feedback (lines 366–369).**
    * Quote: "trap ids opened or closed,"
    * Replace with: "trap ids opened or closed, with `closed: [{id, label, hits, since, days,
      questions}]` for the Fixed line (G4), `trap_true` (G3),"

21. **§2.8, runner row (line 422).**
    * Quote: "`D` details"
    * Replace with: "`V` details (practice; `D` only chooses) · `R` report · `T` / `Shift+T`
      twin and its menu after a verdict (practice)"; `I` I'm guessing stays.

22. **§2.8, player row (line 423).**
    * Quote: "`T` try one like this"
    * Replace with: "`T` twin · `Shift+T` twin menu"
    * Quote: "`I` details"
    * Replace with: "`V` details"
    * In the "Flashcards and word quizzes" row, append: "`I` guess · `T` twin · `Shift+T` twin
      menu (after the verdict) · `R` report · `W` hint"

23. **§2.8, global row (line 421).**
    * Quote: "`[` collapse the sidebar. `?` shortcuts"
    * Replace with: "`[` collapse the sidebar. `Z` undo the last reversible change (while its
      toast shows). `?` shortcuts. A scope that registers a key twice, or a question action on a
      key other than its `UI.KEYS` key, throws in `/dev/` (R43)"
    * Quote: "`K` Class · "
    * Delete it (decision 5).

24. **§2.9, new provider rows (after the T-bank row, line 449).**
    * Add:
      * "| F1 | `UI.VERBS`, `UI.verb`, `UI.KEYS`, `UI.pts`, `UI.fact`, `UI.empty`, `UI.SUBJECT` | every page |"
      * "| F2 | `UI.run` (G1), `next.due` with R56's review row, `[data-fact]` delegation, `Z`, the key checks, `next.queue` kind `start` (G10) | S3, S4, S6, S7, S9, S10 |"
      * "| F3 | `UI.questionActions`, `UI.twin`, the verdict slot, figure/table/MathML markup, the phone tools row (R50) | S3, S4, S6, S8, S9, S10, the type page, the official pad |"
      * "| F4 | R45's close rule by kind and transfer check-in, `deps.subject_of` (G11), `attempts.word` and R&W answers through `progress.record` (R57), `official_done` (G16) | S10, S6, S9, S4, every owner |"
      * "| F5 | `want` from the trap on every twin path (G3), `rw.*` templates through the catalogue (R57), `source:'start'` (G10), `GET /api/types/{t}` (G7) | S3, S4, S6, S8, S9, S10, U28 |"
      * "| S1 | `GET /api/levers` (G6), `go` on `/pair/` (G12), `POST /api/auth/google` (G15) | every page, F2 |"
      * "| S4 | `/types/?t=` (G7), `/practice/official/` and `/api/official` (G16) | every question surface, palette, S6, S10, S7 |"
      * "| S7 | R41's done rules, `GET /api/plan/sheet` (G13) | S3, F2 |"
      * "| S9 | `rw_items` behind the catalogue, `words.rw_answers` over attempts (R57), `tools/words_audit.py` (G14) | F5, F4, S6, S10, I1 |"
      * "| S10 | `review.due` with T3's kinds (R56), `review.trapsheet` for G13's section 1 | F2, S3, S7 |"
      * "| T-bank | G14's fields: `spr_mistakes`, `steps`, `step_of_reason`, `desmos`, `desmos_read`, `ask`, `figure_alt` | F5, F3 |"
      * "| I1 | `tools/product_gates.py` (`perf`, `facts`, `copy`, `a11y`, `bank`) and the Words audit's empty queue | every merge in wave 3 |"

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
    * Add: "| 3.1, 3.2, 3.3, 3.5, 3.9 | "two clean answers close it" | for a named trap, two
      clean answers on questions that offered it; for unsure, slip and unnamed grid-in traps,
      clean answers on the template, as before | R45 |"
    * Add: "| 3.1, 3.2, 3.9 | the Warm-up row and Review's Due list, each with its own count | one
      Due row, kind `review`, from `review.due` | R56 |"
    * Add: "| every section | a button or link reading a retired phrase (G2) | the `UI.VERBS` label
      for the same action | R42 |"

30. **§4.1 waves (lines 974–985).**
    * Quote: "wave 1a  F1 design system      F4 data layer      T-bank grid-in mistakes (runs on
      its own until done)"
    * Replace with: "wave 1a  F1 design system      F4 data layer      T-bank one pass (G14: runs
      topic by topic through wave 2; splits into T-bank-a and T-bank-b at mid wave 2 when under
      60% of U8 weight has steps)"
    * Quote: "wave 3   I1 integration and the full walk"
    * Replace with: "wave 3   I1 integration, the full walk and the product gates (perf, facts,
      copy, a11y, bank) and the Words audit"

31. **§4.2, T-bank entry (lines 11026–11033).**
    * Quote: "**T-bank · Named grid-in mistakes in the bank** (wave 1a, port 8017)."
    * Replace the entry with: "**T-bank · One pass through the bank** (wave 1a to wave 2, port
      8017). Builds G14: `spr_mistakes`, `steps`, `step_of_reason`, `desmos`, `desmos_read`, `ask`
      in params and `figure_alt`, one topic per commit, heaviest first, with the audit checks;
      `practice.to_question` carries `spr_reasons`, `steps`, `step_of`, `desmos` and `figure_alt`
      (T-bank sends the change to the file's owner). Owns `satbank/item.py`, `satbank/audit.py`,
      `satbank/figures.py`, `satbank/plot.py`, `satbank/shapes.py`,
      `satbank/topics/*/families/*.py`, `tools/bank_coverage.py`. Needs F0. The launch fields
      (`steps` with `step_of_reason` on all 386 templates, `figure_alt` on all 76 figure
      templates) are complete before I1 signs off; the others ship partial and grow (open
      question 11)."

32. **§4.2, S4 entry (lines 11084–11089).**
    * Quote: "`api_practice.py` (adds `/api/bank`, the session endpoints, `GET /api/drill`),
      `server/checks/s4.py`."
    * Replace with: "`api_practice.py` (adds `/api/bank`, the session endpoints, `GET /api/drill`,
      `/api/official`), `web/types/**` (G7), `web/practice/official/**` (G16),
      `server/checks/s4.py`."

33. **§4.2, I1 entry (lines 11129–11133).**
    * Quote: "checks that every nav link lands on a real page; finishes README and this file's
      State lines."
    * Replace with: "checks that every nav link lands on a real page; runs
      `tools/product_gates.py` (`perf` G9, `facts` G6, `copy` G2, `a11y` G8, `bank` G14) and owns
      it; runs `tools/words_audit.py` and holds Words until its queue is empty (G14); applies
      the §3.2 lines of every `v2-upgrades` file with their owners; finishes README and this
      file's State lines."

34. **§4.3 ownership (after line 11147).**
    * Add: "* New server modules from the upgrade files, one owner each: `server/next.py` and
      `web/sw.js` (F2, U1, U18), `server/habits.py` and `server/types.py` (F5, U2, U6),
      `server/ratings.py` (F4, P11), `server/push.py` and `web/link/**` (S1, U18, U20),
      `server/today.py` (S3), `web/types/**` and `web/practice/official/**` (S4, G7, G16),
      `tools/words_audit.py` (S9, G14), `tools/product_gates.py` (I1)."
    * Add: "* `v2-upgrades/product.md`'s R39–R60 table is shared by convention: a task that needs a
      new seam decision adds a row there and in §2.2 in the same commit."

35. **Part 5 (lines 11165–11183).**
    * Quote: "2. **Words.** Ship about 750 SAT words and 70 transitions now,"
    * Replace the item with: "2. **Words.** Answered (decision 2): R&W vocabulary only. The
      definitions and frames go through G14's Words audit; a person clears its queue before
      Words ships. Who? Default: the site owner, signing each item in
      `server/words/review_log.json`."
    * Quote: "3. **Daily Challenge.** Each student gets twin questions"
    * Replace the item with: "3. **Daily Challenge.** Answered (decision 1): twins."
    * Quote: "5. **Sign-in.** Email codes need SMTP in production;"
    * Replace the item with: "5. **Sign-in.** Answered yes by default (G15, R58): Google sign-in
      as one more method beside passkeys (U19), email codes and pairing. It needs a free Google
      OAuth client id (`GOOGLE_CLIENT_ID`); without one the button is hidden."
    * Quote: "8. **Diagnostic gate.** Keep the name-and-email step before its result (default for
      now), or show it directly like every other sitting?"
    * Append: "G10 puts an 8-question start before the diagnostic, so the gate no longer meets a
      new student first; the product proposals and `tests.md`'s gap all favour showing the result
      directly."
    * Quote: "11. **Grid-in mistakes.** Naming grid-in mistakes needs edits to up to 133 templates.
      Ship with partial coverage and grow (default)?"
    * Replace with: "11. **Bank fields.** G14 adds grid-in mistakes, steps, Desmos routes and
      figure descriptions in one audited pass, topic by topic. Steps and figure descriptions are
      complete at launch (G14's gate); grid-in mistakes, Desmos routes and `ask` ship partial and
      grow (default)?"
    * Quote: "17. **Official replicas.**"
    * Replace the item with: "17. **Official questions.** No College Board text is served. G16
      lists the official IDs we hold keys for; the student opens each on College Board and
      answers on our pad, and a miss becomes a named mistake and twins (R59)."
    * Add: "20. **Type pages in search engines.** `/types/?t=` pages are public (G7). Let search
      engines index them (default), or `noindex`?"
    * Add: "21. **Read aloud in tests.** Only with extended time (x1.5 or x2), as Bluebook treats
      text-to-speech as an accommodation (G8, default). OK?"

### 3.2 In the sibling upgrade files (I1 applies them with the owners)

`review.md` and `words.md` were being revised while this was written, so their rows quote the
label and apply to **every occurrence** of it in that file, whatever sentence carries it.

| file | quote | change | why |
|---|---|---|---|
| `today.md` T1 | "* **The pill** `Start · 15 min` (the region's primary)" | "* **The pill** `Study 15 min` (the region's primary)" | R40 |
| `today.md` T2 | "A `.btn Do them in order` (shown with 2 or more undone rows) starts the first undone row." | "The header's primary `Start today · n parts · m min` (G1) starts the run over the undone rows." | R40 |
| `today.md` T2 rows | "4. **Warm-up** (T3): `Warm-up · 5 questions · ~6 min · 3 check-ins due · 2 fading`" | "4. **Review** (kind `review`, R56): `Review · 12 due · ~16 min · 3 check-ins · 2 fading`, from `review.due` (V1's list with T3's fading and keep-warm kinds), started with `{source:'due', box: prefs.review_minutes}`; the plan's recheck task is this row" | R56 |
| `today.md` T2 rows | "6. Words due: `12 words due · ~3 min` (`words.today_summary`), starting S9's review run." | "6. Words: `Words · 12 due · 5 new · ~6 min`, starting W11's run; the plan's `words` task (L4) is this row, with its `task_id`, never a second row" | R56 |
| `today.md` T2 rows | rows 2 (class assignments) and 9 (group contests) | Already applied in today.md: row 2 is removed (decision 5); row 9 reads "Private contests closing today (`compete.due_today`): `Friday five · 10 q · closes 9:00 PM`" | decision 5 |
| `today.md` T2 acceptance | "starts `[\"plan\",\"warmup\"]`" and "(`map(.kind)` has one `warmup`)" | "starts `[\"plan\",\"review\"]`" and "(`map(.kind)` has one `review` and no `warmup`); with a plan words task and `words_goal` 10, one `words`" | R56 |
| `today.md` T3 | "* **The Due row**: `Warm-up · 5 questions · ~6 min · 3 check-ins due · 2 fading`" | "* **In the Due list**: T3's candidates are the check-in, fading and keep-warm kinds of the review row (R56); `{source:'warmup'}` is accepted as `{source:'due', count:5}`" | R56, R46 |
| `today.md` T9 (and `review.md` §3.2 row "today T9 / R30") | "`#mist`'s primary is **Start review · 10 min**" | "`#mist`'s action is a `.btn` **Start review · 10 min** that starts the review row, with `12 due today`; while a run is on it reads `Start review · part n of m` (R56). Today's two pills are Start today and Study 15 min" | R40, R56 |
| `today.md` T13 | the final stretch's Due rows | Add the **Final check** row (kind `final_check`) from 7 days out (G13, R60) | R60 |
| `today.md` T5 | "**Component.** `UI.twinSheet({body, recall, onDone})` (F3, `question.js`)." | Append: "Callers reach it through `UI.twin(anchor, ctx)` (R44); every twin body carries `want` from the trap when the source was a miss on a named trap (R45)." | R44, R45 |
| `today.md` T16 | "**`Retake as twin`**" | "**`Twin test`**" | R42 |
| `shell-me.md` U1 | "* Brand-new student: "Take the diagnostic · 20 q", with a quiet "or one quick question"." | "* Brand-new student: row 0 `Start with 8 questions` (G10), row 2 the diagnostic." | R55 |
| `shell-me.md` U13 | "* **Data.** `/api/me/summary.levers: {key: {how, help, inputs: [...], next, start?}}`." | Append: "The same function serves `GET /api/levers?keys=` to every page, with `excluded` and `same_on` (G6)." | G6 |
| `shell-me.md` U19 | the sign-in methods | Add Google sign-in after passkeys (G15) on `/signin/`, the save nudge and Settings | R58 |
| `plan.md` L4 | the `words` task row | Append: "It is shown as Today's words row, not a second row (R56)." | R56 |
| `plan.md` L8 | "* It starts the first undone counted question task with `run: '<today>'`." | "* It is G1's `Start today`: the first undone Due row (plan tasks first, then the review row, words and the day's questions) with `run: '<today>'`." | R40, R56 |
| `plan.md` L8 | "Chaining is on the client, from the finish response's existing `plan.next`. The rail reads `GET /api/plan/day/{run}` (tasks with answered/total)." | "Chaining is on the client through `UI.run` over `/api/today.due` (G1); the rail reads the same rows." | R40 |
| `plan.md` L12 | "* `X` done or not done; `S` skip or undo; `U` undo the last action;" | "* `X` done or not done; `S` skip or undo; `Z` undo the last action (global, R43);" | R43 |
| `plan.md` L19 | the trap sheet and `/plan/?print=traps` | Section 1 of G13's sheet; `/plan/?print=traps` redirects to `/plan/?print=sheet#traps` | R60 |
| `plan.md` §4 | "T3's warm-up and P12's `type_memory` already schedule retrieval." | "T3's warm-up already schedules retrieval (R53)." | R53 |
| `plan.md` §4 | "P7's optional chips feed Fix's order (L4)." | "P7's split Check feeds Fix's order (L4, R54)." | R54 |
| `practice.md` P18 | "* **Another like this** (`T`): the same trap with new numbers." | "* **Twin** (`T`): the same trap with new numbers, through `want` (R45)." | R42, R45 |
| `practice.md` §3.2 §2.8 row | "`T` / `Shift+T` another like this and its axes" | "`T` / `Shift+T` Twin and its menu; `V` Details; `I` I'm guessing; `R` Report" | R43 |
| `practice.md` P15 | the Reading & Writing seg | It lists Words in Context and Transitions as available skills with unlimited counts, served by `POST /api/drill {subject:'rw'}` (R57) | R57 |
| `tests.md` §3.1 item 49 | "In exam mode `D` only chooses D: Details isn't offered" | Append: "In practice mode too `D` only chooses; Details is `V` (R43)." | R43 |
| `reports.md` SR8 | "(Fell for it · Misread the question · Slip in the arithmetic · Didn't know how to start · Rushed · Ran long, then guessed)" | "(P8's six: Fell for a trap · Slip: I knew it · Misread the question · Ran out of time · Entered it wrong · Didn't know how to start)" | R47 |
| `reports.md` SR8 | "fell for it → trap; misread, slip, rushed → slip; didn't know → gap; ran long → clock" | "each chip maps to its own cause (`misread` stays a cause, shown when non-zero); letters T S R C E A G" | R47 |
| `compete.md` §3.2 §2.6 row | "Sources `rematch`, `warmup`, `confirm`, `rush`" | "Sources `rematch`, `prep`, `confirm`, `rush`" (C7's lobby drill; UI label stays "Warm up") | R46 |
| `review.md` V1 | the Due list and its `Start review` pill | The list is Today's review row (R56): `review.due` adds T3's `fading` (after half fixed) and `keep_warm` (last) kinds under the same cap; the pill starts that row, and reads `Start review · part n of m` while a run is on | R56 |
| `review.md` V1 | "**Keep going · 10 min** (the coach's set," | "**Keep going · 10 min** (U1's box, `{source:'next', box:10}`; `Keep going` means the box only)" | R40, R56 |
| `review.md` V1 | "**Another 10 min**" | "**Fix n · 10 min**" (V4's order) when mistakes are open, else the box `Keep going · 10 min` | R42 |
| `review.md` every occurrence | "Fresh one like this", "Another like this", "Try one", "Try one now", "Now you: a new one" | `Twin` (`T`), inline where the source was inline; in an empty state for a learner with 0 answers, `Start with 8 · about 10 min` | R42, R55 |
| `review.md` every occurrence | "Fresh versions" (and "Fresh versions of selected · n", "Fresh versions · all n") | `Twin this set` (`Twin this set · 6 selected`, `Twin this set · all 14`) | R42 |
| `review.md` every occurrence | "Redo these 5", "Fix these", "Fix on new numbers · n q" | `Fix n` (e.g. `Fix 5 · about +18 pts`) | R42 |
| `review.md` every occurrence | "Learn it", "Keep warm · 3" | `Learn this type`; `Twin ×3` | R42 |
| `review.md` V11 | "See one solved" (key `V`) | `Learn this type` (Twin menu, and a `.btn` in the pane after a miss) opens V11's side-by-side sheet: your miss beside a worked twin with your trap outlined, then T4's three; `V` is Details (R43) | R42, R43 |
| `review.md` §3.2 §2.8 row | "`V` see one solved" | "`V` Details (as in every player, R43)" | R43 |
| `review.md` V16 | the new-student panel and empty tabs | Rendered by `UI.empty(host, {sample, text, action})` (G12): the Example row is `sample`; the action is `Start with 8 · about 10 min` for 0 answers and an inline `Twin` otherwise; "Take the diagnostic" is not offered | R55, G12 |
| `review.md` V19 | "print one list:" and "**Exam week** (from 7 days before `exam_date`): a card at the top of Due" | The trap sheet is section 1 of G13's `/plan/?print=sheet`; `/review/print.html?sheet=traps` redirects there. The exam-week card goes: Final check is Today's `final_check` Due row, and the Due tab shows one `Your test-day sheet` link | R60 |
| `words.md` intro, W1 Data | "They are not in `attempts`, Practice, Tests, the estimate or Compete yet." | "They are the first `rw` bank (R57): registered in the catalogue, served by drill, filed in `attempts` (with `attempts.word`) by `progress.record`, a miss opening a trap with norm = the trap id; `word_reviews` keeps the word's schedule and links the attempt. They stay out of Tests and the estimate." | R57 |
| `words.md` W1, W2 | "**Same word, new text** (`T`), **Same trap, new word** (`Shift+T`)" and "`T` gives the same logic in a new text; `Shift+T` the same pair of" | "**Twin** (`T`) through `UI.twin`, with `Same word, new text` and `Same trap, new word` (W2: `Same logic, new text`, `Same mix-up, new text`) in its menu (`Shift+T`)" | R42, R43, R44 |
| `words.md` every occurrence | "another like this", "**Another**" (the sheet sample), "**Practise 10 in context**" | `Twin`; `Twin`; `Twin ×10` | R42 |
| `words.md` every occurrence | "Drill it" on a trap (W5: "**Drill it · 10**"); "Drill it" on a pair | `Twin ×10`; `Quiz the pair · 6` | R42 |
| `words.md` §3.2 §2.8 keys row | "`T` / `Shift+T` another like this (after the verdict)" | "`T` Twin · `Shift+T` the Twin menu (after the verdict) · `R` Report" | R43 |
| `words.md` W1 | the content-review `ponytail:` note | "The content passes G14's Words audit (WordNet check, a second-method frame check, a human queue that is empty before Words ships)." | G14 |
| `words.md` W19 | logging a missed official R&W question | Through `POST /api/mistakes/log {template: 'rw.*', reason: <trap id>}` into the same traps (R57) | R57 |


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
* **Paper versions with QR answer entry** (unfair-advantage #11): its class use is void
  (decision 5), and the rest is covered: the worksheet prints with its key, and V18 files a
  printed worksheet's answers at `/review/sheet/?id=`.
* **A words interstitial every 10 minutes inside the Math session** (unfair-advantage #3):
  `today.md` rejected folding words into the Math runner; G1's run chains the words run as its
  own part.
* **A per-question countdown in Autopilot and a separate `pool:'auto'`** (unfair-advantage #3):
  U1's `box` with segments is that session.
* **Swipe-up on the tab bar and swipe to Next before Check** (experience #10): `shell-me.md`
  rejected the tab-bar gesture; R50 forbids moving on before Check in instant feedback.
* **Haptics on every verdict** (experience #10): X6 keeps `vibrate(8)` for the long-press strike
  only; a buzz on every answer is noise in a quiet room.
* **A `twin_tell` preference that shows the trap before the twin** (unfair-advantage #1, point
  6): T5's recall header already names it; one more switch for the same line.
* **A 14-class habit taxonomy** (unfair-advantage #7): U6's 11 regex families tag every reason;
  `practice.md` and `reports.md` rejected a second taxonomy.
* **Logging R&W mistakes in skills we don't generate yet** (the unfair-advantage R&W gap): for
  Words in Context and Transitions it is built (R57, G11), with twins, Fix and check-ins. For
  the other R&W skills there is no twin, fix or check-in yet, so it would be a notepad; their
  IDs read `Logged for the R&W bank` and join the same routes when the bank lands.
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
* **Showing the diagnostic result without its gate** (experience and unfair-advantage gaps): open
  question 8 is the user's; G10 means a new student meets the gate later, and §3.1 item 35
  records the recommendation.
* **An `official` pool serving College Board text** (the unfair-advantage official gap): content
  terms (open question 17). G16 lists the IDs, opens each on College Board's free bank and does
  the answering, naming and twins here.
