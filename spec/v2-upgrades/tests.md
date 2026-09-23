# v2 upgrades: Practice tests and the test window

Written 2026-09-23 for `spec/rebuild-v2.md` §3.4 (lines 4780–6054). It merges three designers'
proposals (outcomes, experience, unfair advantage: 33 proposals and 62 parity gaps in
`spec/v2-upgrades/_proposals/tests.json`) into one build-ready list, checked against the
TopTierPrep inventory in §3.4.1, `spec/toptierprep-teardown.md`, `ttp-notes.md` and the live walk
in `ttp-live.md`.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.4 where they
  differ, and §3 lists every change. Part 2 resolutions (R1–R38) still hold, except the lines
  named in §3.2 "Outside the section".
* **Siblings, reused and not re-specified.** `practice.md` (P1–P25), `shell-me.md` (U1–U28) and
  `today.md` (T1–T20) already own several pieces this section shows. This file calls them by
  name: P3 (the Desmos way, `Item.desmos`, `attempts.calc`), P5 (cover the choices), P6
  (`attempts.offered` / `struck`), P7 (Sure / Unsure / Guess), P11 (`ratings.odds`, zone), P16
  (budgets 65 / 95 / 126 s), P19 and P22 (rematch and fresh-slot sets), P20 (the `U` key), P21
  (type notes, `notes.seed = −1`), P24 (the formula a question used), U1 (`next.queue`), U3
  (reports answered by the solver, quarantine), U4 (`estimate.gains`), U7 (`progress.pace`), U8
  (the type atlas), U9 (`estimate.projection`), T7 (`progress.causes`), T10 (verdict line), T16
  (`estimate.rescore`, the compare endpoint, Retake as twin). Where one of them has to change,
  the change is in §3.2.
* **The bar.** A student who sits TopTierPrep's papers today opens ours and wants to switch,
  because every test is fresh and fair, the window helps them in training and stays out of the
  way on test day, and every sitting ends with a diagnosis and a next step that moves the score.
  Parity is failure.
* **Names.** Upgrades are X1–X23. Builders are Part 4's tasks (F1–F6, S1 and S3–S10, T-bank; S2
  Classes is removed by decision 5). S5 owns `web/tests/`, `web/test/`, `server/api_tests.py` and
  `server/blueprint.py` (from F5 in wave 2).
* **No classes** (v2-decisions 5). Nothing here has a teacher, class, homework, assignment or class
  code. Friends sit together through a twin share link (X22) or a Compete private contest by invite
  code, which Compete owns.
* **Subject-aware** (v2-decisions 3). `sessions.subject TEXT NOT NULL DEFAULT 'math'`. Every payload
  that describes a section carries `subject` (`math` now): `pace_plan`, `crowd` and each of its slots,
  `levers`, `habits`, `result.gate`, `done`, `holds`, and each section of `papers.questions`, which is
  `{sections:[{subject:'math', module1, module2_lower, module2_upper}]}`. The session payload's
  `modules` is a list `[{subject, n, questions}]`, not "1 or 2"; the header label, "Module n of N" and
  the sittings CSV's module columns are all derived from that list (§3.1 items 71–72). The runner
  keeps an empty `passage` region. A full SAT (R&W 27 + 27, the break, then Math 22 + 22) is then
  more sections in the same shapes, not a rewrite.
* **Facts this file relies on** (code as of 2026-09-23):
  * `blueprint.MODULE_SIZE` 22, `MODULE_SECONDS` 2,100, `TIERS['module1']` 7 / 8 / 7,
    `SPR_AT` (6, 7, 13, 14, 21, 22). `blueprint.fill` sorts a slot's pool by `(uses in this module,
    name)` and tries the first `practice.CANDIDATES` (7) of them, so today the choice inside a domain
    leans to templates early in the alphabet. X2 replaces the name key.
  * `scoring.ROUTE_UP_AT` 0.60, so 14 of 22 routes up. `LOWER_ROUTE_CEILING` 580.
    `MOCK_HALF_BAND` 70, `HALF_BAND` 100. Module weights 44 / 52 (upper) / 36 (lower); one medium
    question is worth about 12 points mid-scale (today.md).
  * `server/mocks.json` holds 7 forms, each `module1`, `module2_lower`, `module2_upper` of stored
    questions with `key`, `seed`, `difficulty` and `type`, so their slot lists already exist.
  * P16's tier budgets 65 / 95 / 126 s add up to 2,097 s on 7 / 8 / 7.
  * `sessions.ranked` and `sessions.unranked_why` are already in §2.5 (added for contests).
    X1 reuses them for tests.
  * Compete (§3.7) already runs a Weekly Module (22 questions, twins, in the test window) and a
    Season Final (a full adaptive section, the weekend a week before each SAT date).
  * The db holds 287 attempts from 13 learners, and no (template, tier) has 20. So every number
    here that could be empty at launch has a fallback that works on day one (the viewer's own odds,
    site-wide data per type), switches to the crowd at R16's single threshold, n ≥ 20, and says
    which source and how many it has. No share of a crowd is shown below n 5.

---

## 1. Scorecard

The "v2 spec" column is §3.4 as written. The verdict says why ours is way better. Where v2 was at
parity or below, the verdict names the upgrade that fixes it.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Estimated Score card | "Math 200-280", a red LOW CONFIDENCE chip, a trend; drops a section at the 200 floor | Band, confidence with reason, headline, band chart, Best / Combined / Range / Routed up / Target / Exam, "Counted"; floor sittings count | Where the points went in the last 3 sections, priced by re-marking; the route lever; the top 3 skills; confidence as a button; total with R&W; projection cone; calibration against Bluebook scores; growth percentile (X15) | v2 PARITY: more facts, all about the past. **X15 → WAY BETTER.** It says which points can be won back, what each is worth and starts that work in one tap. |
| 2 | Section tab bar | One tab "Full-Length Tests"; a hidden /practice/diagnostic route nothing links to | A sticky section nav with counts; the diagnostic is a card | Adds Habits and the Cycle card (X16, X17) | **WAY BETTER already in v2.** Everything is reachable and counted. |
| 3 | Difficulty filter | Editorial Easy / Medium / Hard label, the same for everyone | Measured from 20 first sittings; "Not rated yet" before that (for months on a new site) | Rated for you from your first answer with P11's odds over the paper's slots: `Harder for you · expect 14 of 22 in module 1 · 16 on most papers`; filter Harder for me / About my level / Easier for me; beside it everyone's rating from P11's item ratings, measured at 20 ranked first sittings (X20) | v2 BELOW at launch. **X20 → WAY BETTER.** Theirs says how hard a paper is for nobody in particular; ours says how many you should get, on day one, from the one difficulty model the site already has. |
| 4 | Type filter (Adaptive / Non-adaptive) | A label over a fixed shelf | Module 2 Adaptive / Always harder / Always easier in the start sheet | Route-up trainer with a streak goal, the harder-module gauntlet, route margin everywhere, presets "Routing check" and "700+ finisher" (X14, X1) | v2 PARITY (the same switch, moved). **X14 → WAY BETTER.** It trains the one jump in the score, the 580 wall. |
| 5 | Status filter | All / Not Attempted / In Progress / Completed | All / Not sat / In progress / Completed | Adds "Misses to fix"; every option shows its count; active filters as removable chips (X20) | v2 PARITY. **X20 → WAY BETTER.** It ties the shelf to repair. |
| 6 | Access filter | All / Free / Paid | Replaced by "New to you" | "For me": Has my open mistake types / Types I haven't met under the clock (X20) | **WAY BETTER:** nothing is paid, and the slot means something to the student. |
| 7 | Sort By | Newest / Oldest / Hardest / Easiest | Adds Most sat | "Best for me" (default): the papers holding your open traps and unmet types first; Hardest / Easiest for me by your expected score (X20) | v2 PARITY. **X20 → WAY BETTER.** |
| 8 | Paper grid | 29–31 fixed papers, the same questions for everyone, mostly paywalled; free tier gets 1 attempt | 7 launch papers plus one every Monday, the same questions for everyone | Twin papers: the same types in the same slots for everyone, each sitter's own numbers; every paper can be retaken fresh forever; beside it, unlimited fresh sections (X20) | v2 BELOW in shelf count, and identical questions can be passed around. **X20 → WAY BETTER.** A fair crowd comparison that can't be copied and never runs out. |
| 9 | Card: Report | Flag "Report" → a form into silence | Labelled Report on cards (R17) | Reports answered by the solver (U3); a wrong key leaves your score (X10) | **WAY BETTER** (U3). |
| 10 | Card: tags | Free / Adaptive / Standard | Adaptive · Official timing · rating chip | `Harder for you · expect 14 of 22` plus `Everyone: typical · predicted` or `· measured from 34 sittings`; "Has 3 of your open mistake types"; a `Season Final` tag on Road-to papers (X20) | v2 PARITY. **X20 → WAY BETTER.** |
| 11 | Card: stat tiles | People took 1.6k · Your last score ("Not taken" after a 2-module sitting) | Sat by · Average · You; percentile after 30 | `Sat by 41 · 12 ranked` over every first sitting; Average from 5 sittings, ranked-only at 20; at 20 ranked a distribution strip and the percentile (R16's one threshold); `Hardest: M2 Q19 · 18% right · you got it`; closed Season Finals join the shelf as `Road to Oct 3` papers that start with the contest's crowd; T4 cards keep `Everyone: N sittings` (X20, X21) | v2 BELOW at launch (every card "Sat by 0"). **X20 → WAY BETTER.** Counts from the first sitting, and a pre-exam paper that is never empty. |
| 12 | Card: Comments N | Grey button, count | "Discussion 12 · opens after you sit it" | "Questions & discussion": a per-slot board with each type's result and traps from day one, site-wide until the paper has its own 20 (X21) | v2 PARITY. **X21 → WAY BETTER.** |
| 13 | Card: Start Exam | Opens a 3-step wizard | One tap to the lobby with your defaults | Presets and a recommended setup with its reason (X1) | **WAY BETTER already in v2.** |
| 14 | Paid lock and limits | Blurred card, "Unlock it with Pro or Elite"; 1 attempt free, 20–30 plus retakes a month paid | Everything free | Unchanged | **WAY BETTER:** unlimited and free. |
| 15 | Comments modal | Threaded, unmoderated, spoilers, no question reference | Gated until you sit it, tagged by question, Helpful, report-to-hide, moderation; Part 5 q7 left it maybe behind a flag | Questions tab first: % right per slot, the named-trap spread, median time vs yours, your cheapest points, the top Helpful post; site-wide data per (template, tier) until 20 first sittings, no share below n 5. Discussion launches on, with its moderation owner named (X21, §3.1 item 73) | v2 PARITY, and possibly switched off. **X21 → WAY BETTER.** Data first, anchored to questions, never empty, and it ships. |
| 16 | Report modal | Exam id, category, 5,000 chars, 10 images, no reply | R17 form, (template, seed) attached, status in Me | Solver verdict in a second (U3); "Remind me after the test" costs no clock; a confirmed bad key is removed from the score (X10) | v2 PARITY in form. **X10 + U3 → WAY BETTER.** |
| 17 | Wizard step 1 | Full Test / Select Modules | Radio cards: section, choose modules, paper, custom, diagnostic, twin, shared | Adds Trap test and Route-up trainer; a presets row with one recommended (X1, X14, X16) | **WAY BETTER already in v2** (more kinds). X1 makes it one tap. |
| 18 | Wizard step 2 | 2×2 checkable module cards, Select all / Clear, "N of 4 selected" | The same cards and counter | Each card shows your last result on it and what it yields; one-tap module presets (X1) | v2 PARITY. **X1 → WAY BETTER.** |
| 19 | Wizard step 3 | Timed / Untimed | Official / 1.5x / 2x / Untimed / own minutes | Conditions (Test-day · Training) plus Tight clock (−15%) for training; each option says what it trains (X1) | **WAY BETTER already in v2** (extended time). X1 adds what they have no concept of. |
| 20 | Learning preferences for tests | Profile: Practice Mode Timed/Untimed, Show Desmos | `test_*` prefs on the server, edited in the sheet, lobby and Me | Adds `test_conditions`, `test_nudges`, `test_cover`, `test_predict` (X1) | **WAY BETTER already in v2:** they follow the code and are editable until Begin. |
| 21 | Fullscreen gate | Dark page, "Enter Fullscreen", no word on what the test is | Lobby: facts, every setting with Change, no questions sent before Begin | States whether it ranks and why, what it holds by domain, how many types are new to you (X1, X2) | **WAY BETTER already in v2.** X1 and X2 add what the student needs to decide. |
| 22 | Runner chrome | Bluebook trade dress, no sidebar | Practice session look, Bluebook behaviour | Test-day conditions: exactly Bluebook's behaviour, on purpose, with no type notes or other aids. Training: pace, nudges, cover, confidence, type notes (X1, X3–X7, X9) | Behaviour PARITY on purpose, so test day holds no surprises. **X1 → WAY BETTER:** the same window becomes a coach when the student chooses Training. |
| 23 | Header title + Directions | "Section 1, Module 1: Reading and Writing" | "Math · Module 1 of 2"; Directions opens at the start | A Ranked / Training chip beside the title (X1) | v2 PARITY. **X1 → WAY BETTER:** the student always knows what this sitting counts for. |
| 24 | Timer with hide | Countdown, eye toggle | Server-derived, hide kept, 5-minute unhide, count-up when untimed | Training: ahead/behind against a per-position budget from the student's own speed, checkpoints at Q8 and Q15 (X3) | **WAY BETTER already in v2** (reload isn't free time). X3 adds pace. |
| 25 | Highlights & Notes toggle | Pen icon | Labelled tool, key L | Scratch layer beside it (X8) | v2 PARITY. **X8 → WAY BETTER.** |
| 26 | More → Save and Exit | One item; no time left shown on return | Save and exit pauses the clock; In progress shows time left | The sheet says what a pause costs (the rank) before it happens; "Remind me tonight" (X1, X23) | **WAY BETTER already in v2.** |
| 27 | Calculator | Floating Desmos, resizable, forgets its state | Dock, resize, state per sitting, phone sheet, no-calculator mode; on the public trial key | Your expressions kept per question and shown in review beside the Desmos way (X8, P3). The production Desmos key is a launch blocker with an owner; if it is refused, a built-in scientific calculator fills the same dock, so the runner never ships without one (§3.1 item 74) | v2 PARITY in capability, at risk on the key. **X8 → WAY BETTER**, and never worse than theirs. |
| 28 | Reference | Modal image | The drawn sheet in a dialog | Docked in one 300px right-hand slot beside the question (tabs with Notes and Entering your answer), with search; the column never drops under 560px; opens counted per question (X9); the formula used highlighted in review (P24) | v2 PARITY. **X9 → WAY BETTER.** |
| 29 | Layout | R&W split pane; math column; SPR directions pane | Math column; "Entering your answer" rail on every grid-in | One layout rule for every panel: calculator dock left, one tabbed right-hand slot, a column of 560–700px, the later panel floats only when both can't fit; answer pad on phones; the passage region kept for R&W (X6, X9, §3 override 56) | **Math: WAY BETTER** (rail everywhere, pad, nothing covers the question). R&W: below by scope until the EBRW bank, built additively (decision 3). |
| 30 | Question strip | Number, Mark (yellow), Report, ABC toggle | Q badge, Mark, confidence, Eliminate, Report, all labelled | Strike by long-press (when no text tool is on) or right-click, Save (`Z`, practice.md's one save key, so `A–D` only choose), Scratch, Mark in thumb reach on phones (X6, X9) | v2 PARITY. **X6 → WAY BETTER.** |
| 31 | Choices | 2px rows, blue selection | Orange selection, KaTeX, text size | Solve first: cover the choices in Training (X7) | v2 PARITY. **X7 → WAY BETTER.** |
| 32 | Highlights and notes | 4 colours, 3 underlines, Note; no list of notes | 7 styles, notes rail, kept into review | "Asked for · Given · Ignore" names on the first three styles; your type notes under later questions of that type in Training, and in every review (X9) | v2 PARITY. **X9 + X8 → WAY BETTER.** |
| 33 | SPR input + preview | Placeholder, KaTeX preview, accepts any character | Keystroke filter, KaTeX preview, rail with the examples table | Training: a warning only on the 15 two-digit cuts of thirds, sixths and ninths (`.66`, `.33`, `.83` …) and their longer cuts, once per value, so it never fires on `.45`; after hand-in "Right value, wrong form" (X4, T7) | v2 PARITY in preview. **X4 → WAY BETTER:** the one grid-in mistake that costs right answers, caught without crying wolf. |
| 34 | Footer | Name, "Question 1 of 27", Back / Next | Name, save status, "Question 7 of 22 ⌃" | "Going through · 3 of 8" queue mode (X5) | **WAY BETTER already in v2** (save status, offline queue). |
| 35 | Module navigator | Legend without counts, Esc ignored | Counts, filters, Esc, arrow keys | "Go through 8"; Time view in Training (X5) | v2 PARITY. **X5 → WAY BETTER.** |
| 36 | Check Your Work | 3 tiles, grid, "26 unanswered" warning | Tiles as filters, Time view, no-penalty tip, pacing line | One pill walks every blank and marked question in order; pass 2 is measured (X5) | v2 PARITY (it lists, it doesn't lead). **X5 → WAY BETTER.** |
| 37 | Module sequence | No break, no way back | The same; module 2's clock starts on Begin, and a Test-day student could rest for days between modules and still rank | Test-day: a visible 60 s countdown with "Which ones do you think you missed?" inside it, then module 2 starts itself, as Bluebook; a longer break keeps the score but unranks (`break 12:40`). Training: the open step with the module 1 pace trace and gate margin (X11, X3, X14) | v2 BELOW (a hole in the rank). **X11 → WAY BETTER.** Bluebook's pacing, plus calibration that costs no test time. |
| 38 | Resume | Save and Exit + an In Progress filter; no time left | In progress card, paused lobby, time left | Paused tests lead Up next on every page (X23, U1) | **WAY BETTER already in v2.** |
| 39 | Retakes | 10–20 a month (paid), the same paper again | Retake re-serves the same paper | Retake gets new numbers on the same slots; compare slot by slot (X18, X20) | v2 PARITY (measures memory). **X18 → WAY BETTER.** |
| 40 | Share | QBank-only shared session; navigator.share froze the page | A finished sitting's exact questions by link; both scores | Twins by default (P22), peers compared slot by slot by named mistake; or a race with a deadline and a board through a Compete private contest by invite code (X22) | v2 PARITY in mechanism. **X22 → WAY BETTER.** |
| 41 | Classes and homework (hidden) | Teacher can assign a timed test with a due date | Classes in Shell §7 | Not built: decision 5 (a separate platform has classes). Friends race the same test through X22's twin share or a Compete private contest by invite code, with a due time and a board | **Out of scope by decision.** For friends: **WAY BETTER** than their hidden teacher area (X22). |
| 42 | Score report handoff | Straight to /results with count-up rings | Straight to the report | The hand-in moment: the band against last time, earned firsts, then the pressure check before any key (X12, X13) | v2 PARITY. **X12 + X13 → WAY BETTER.** |
| 43 | Percentile | "N% at or below you on their first attempt", ranked sittings only | First standard sittings, n ≥ 20 | Ranked stated before Begin with the reason; away time measured from the client's own stamps, so a Wi-Fi drop never unranks (`offline 3:10` is shown, not counted); a growth percentile for the improving student (X1, X15) | v2 PARITY (their rule). **X1 + X15 → WAY BETTER.** |
| 44 | Diagnostic | Hidden route, empty | A 20-question card | The pressure check confirms or clears each misconception from the first sitting (X13) | **WAY BETTER already in v2** (visible). X13 adds depth. |
| 45 | Eliminations | Saved to their server (bundle), shown nowhere | Persisted on our server | Read against each option's named trap: "you crossed out the right answer", survivor traps (X19) | v2 PARITY. **X19 → WAY BETTER.** |
| 46 | Results list (their /results) | Wrong and blank chips mixed, no score, dead Export | Your sittings: filters, blanks apart, Fix, Twin, Export CSV, notes | Compare any two, chips for rank, margin and pressure (X18) | **WAY BETTER already in v2.** |
| 47 | Time analysis | Contest rankings "average seconds per answered question, by difficulty", empty | Time view on Check your work | How you take tests: end of module, finish margin, changes, marks, pass 2, calibration, calculator (X17) | v2 PARITY. **X17 → WAY BETTER.** |

---

## 2. Accepted upgrades

Grouped by where they act. Each gives why, screens and components, controls and states, data
and endpoints, how it uses the rest of the site, and acceptance checks. Learner codes in the
checks start `a:v2revtests`; `:PORT` is S5's own port; `$DB` is the worktree's `SATF_DB`.

Shared rules for every upgrade:
* **Nothing leaks from a live module.** No key, rationale, reason, template name or seed is sent
  before the module is handed in (§3.4.5 payload rule). Budgets and odds sent in Training carry
  only numbers. The one exception is the student's own type notes, sent in Training only (X9): the
  note's text, never the template name.
* **Test-day stays Bluebook.** Any aid marked *Training* is absent, not just hidden, under
  Test-day conditions (X1).
* **Pricing is re-marking.** Every "≈ +N" on this page comes from `estimate.rescore(sid,
  positions)` (T16) over the student's own sittings, rounded to 10, route held as taken, with
  "up to +N with the harder module 2" when the flip crosses 14 of 22. No second score model.

### A. The conditions and the start

#### X1. Test-day or Training: one choice decides the aids, the pause and whether the sitting ranks

*From: outcomes "Timer mode" and "Start sheet" gaps, unfair-advantage "Fullscreen gate" and "Start
sheet" gaps and proposal 4's coach flag, experience "not ranked" and "Choose modules" gaps. Effort S.
Builders: S5 (sheet, lobby, finish), F4 (prefs keys, R16 `ranked`), F3 (the runner reads
`cfg.conditions`).*

**Why.** v2 has loose toggles (the pace guide is on by default, plus confidence, reveal route and
pause) that quietly make a sitting un-Bluebook and blur which sittings are measurements. The
student learns afterwards that it didn't rank, exactly as on theirs ("Practice test — not
ranked"). One choice fixes both: **Test-day** is exactly Bluebook and the only thing that ranks;
**Training** turns every aid on.

**The two conditions** (`cfg.conditions`, pref `test_conditions`, default `test_day`):

| | Test-day | Training |
|---|---|---|
| Pace guide (X3) | absent | `test_pace` (on) |
| Coaching nudges (X4) | absent | `test_nudges` (on) |
| Confidence tags (P7) | absent | `test_confidence` (off) |
| Cover the choices (X7) | absent | `test_cover` (off) |
| Tell me my module 2 | absent | `test_reveal_route` (off) |
| Your type notes under the stem (X9) | absent | `test_type_notes` (on) |
| Tight clock timing | not offered | offered |
| Navigator Time view, "Best value first" order (X5) | absent | on |
| Calculator, reference, highlights, scratch, eliminate, mark, Save, Go through, answer pad, keys, prediction (X11) | yes | yes |
| Pause (Save and exit) | allowed; the sitting keeps its score but stops ranking | allowed |
| Between modules (X11) | a 60 s countdown, then module 2 begins by itself; a longer break keeps the score but unranks | open-ended, Begin when ready |
| Fullscreen | the lobby leads with "Enter fullscreen and begin" | per `test_fullscreen` |

**Ranked.** At the final finish S5 sets `sessions.ranked` and `sessions.unranked_why` (columns from
§2.5). A sitting ranks when all hold: Test-day; official timing; adaptive route; standard module 1;
kind section, paper, twin, shared, diagnostic or module 1; 0 pauses; a break of at most 75 s between
modules (X11); at most 120 s away from the window in total. The reason is the first failing rule:
`training`, `paused once`, `time and a half`, `untimed`, `fixed route`, `harder module 1`, `break
12:40`, `away 3:10`. Combined, paper stats and every percentile read `ranked = 1` (R16, §3.2). The
estimate still counts every scored sitting, with the reason as a chip.

**Away is measured from the client's stamps, never from gaps in what reached the server.** The v2
save queue survives a Wi-Fi drop ("Nothing a student does is lost"), so a gap between saves proves
nothing. Every queued answer, `/state`, `/begin` and `/finish` call carries:
* `pid`: a random id for this page load (a reload or a second tab gets a new one);
* `el`: the module clock's elapsed ms when the event happened (not when it was sent);
* `hid`: this page load's running total of `document.hidden` ms while the clock ran;
* `off`: its running total of ms with the queue failing while the page was visible.

A page load also queues a bare stamp every 30 s while the clock runs and sends one with
`navigator.sendBeacon` on `pagehide`, so an idle student is never mistaken for a closed page and a
closed page's gap is known to within 30 s.

When the queue flushes, the server reads the stamps, not the arrival times. Away = the sum of each
page load's last `hid`, plus the clock time between one page load's last `el` and the next page
load's first `el` (the page was closed while the clock ran). Offline time goes to
`_session.offline_ms` and shows as a chip and a report line (`offline 3:10 · this doesn't affect
your rank`); it never unranks. A stamp later than the server clock allows (el beyond now − begin)
is capped there, so stamps can't buy time. `qstate._session.last_ping` is not built.

**Start sheet.**
* **Presets row** above step 1, and in each card's Options: chips `Like test day` · `Same as last
  time` · `Pacing practice` · `Routing check` · `700+ finisher` · `Accommodations 1.5x` (the label
  follows `test_timing` when it is x2). Each chip opens the lobby in one tap. Its tooltip is the
  summary line it will produce.
  * Like test day: section, Test-day, official, adaptive, fullscreen.
  * Same as last time: the last sitting's `cfg`, shown only when one exists.
  * Pacing practice: module 1, Training, Tight clock, pace guide and nudges on.
  * Routing check: a Route-up trainer sitting (X14).
  * 700+ finisher: the harder module 2 alone, Test-day (the gauntlet, X14).
  * Accommodations: section, Test-day, x1.5 (or x2).
* **Recommended.** One chip is orange with a reason line under the row, from X15's levers: the
  biggest cause is clock → `Pacing practice · your last 2 sections left 3 blanks each at
  time-up`; a lower route within 2 of the cut → `Routing check · Sep 12 missed the harder module 2
  by 1`; otherwise `Like test day`.
* **Stepper** labels become `Test · Modules · Conditions · Tools`.
* **Step 2 module cards** each show your last result and what they yield: `Module 1 alone · ±100
  estimate · last 17/22`; `Module 2 · harder · practice · last 12/22`.
* **"Trains:" lines.** Under each module, route and timing option, one line, with a personal
  clause when there is data: `Always harder · Trains the 700s: hard questions late in a module ·
  your last: 15/22`; `Tight clock · 29:45 a module · Trains pace: your modules average 37:10`.
* **Step 3 Conditions** is a `.seg` `Test-day · Training`, with helpers:
  * Test-day: `Exactly the SAT: no aids. Ranks among first sittings. A pause keeps your score but
    drops the rank.`
  * Training: `Pace guide, nudges and the rest. Keeps its score, never ranks.`
  * Under it, the timing radio cards: Official, Time and a half, Double time, Untimed, **Tight
    clock (−15%) · Training** ("29:45 a module"), and My own minutes (custom tests).
* **Step 4 Tools** lists both-condition tools first. Training aids follow under a `k` "Training
  aids" (Pace guide, Coaching nudges, Confidence tags, Cover the choices, Tell me my module 2, Your
  type notes); under Test-day each shows disabled with `Training only`.

**Lobby.** A first settings row: `Conditions: Test-day · this sitting ranks among first sittings`
or `Training · keeps its score, doesn't rank`, with Change (before Begin only, `POST /cfg
{conditions}`). A helper line under it: `Pausing, extended time, a fixed route, a break between
modules or more than 2 minutes away keeps your score but drops the rank. Losing Wi-Fi doesn't.`

**Runner header.** After the title, a 24px chip: `Ranked` (paper, 1px ink edge) or `Training`
(`--wash`), with an `aria-label` that states the rule. A Test-day sitting that loses its rank
mid-module (a pause, or the away limit) changes the chip to `Unranked · paused once`.

**Save and exit sheet.**
* Test-day: "Save and exit? The clock stops until you come back. This sitting keeps its score but
  won't rank." [Keep going] [Pause and exit].
* Training: v2's text, [Keep going] [Save and exit].
* Both add a quiet "Remind me tonight" (X23).

**Sittings list.** A `Conditions: All / Test-day / Training` filter; the chip `Unranked · paused
once` beside the band.

**Data.** `POST /api/mock/new` and `/cfg` accept `conditions`; `timing:'x0.85'` under Test-day →
422 `tight clock is a training timing`. The payload carries `conditions` and, only in Training, the
aids' data (X3, X5). `/api/history` rows add `conditions, ranked, unranked_why`. Durations multiply
by 0.85 for Tight clock.

**Uses the rest of the site.** R16 (`ranked` replaces "standard" for Combined and percentiles),
X20 (paper stats), T13 (the dress rehearsal starts `Like test day`), U15 (in the Test-like stage
Up next's test rows use `Like test day`), X15 (the recommended preset).

**Acceptance.**
1. `curl -s -X POST localhost:PORT/api/mock/new -H 'X-Learner: a:v2revtests01' -H
   'content-type: application/json' -d '{"kind":"section"}'` returns `conditions:"test_day"` and no
   `pace` key.
2. `{"kind":"section","timing":"x0.85"}` returns 422 naming `timing`. With `"conditions":"training"`
   it returns `seconds:1785` after `/begin`.
3. A Test-day section paused once, then finished: `SELECT ranked, unranked_why FROM sessions WHERE
   id=…` gives `0|paused once`; `GET /api/tests` still shows its band in `estimate.latest`, and
   `estimate.combined` leaves it out.
4. In test_flow: a Test-day sitting whose queued calls flush 3 minutes late with one `pid`, `hid`
   0 and `off` 180000 → after finish `ranked == 1` and `_session.offline_ms >= 180000`. The same
   sitting with a last `hid` of 190000 → `unranked_why == 'away 3:10'`. Two page loads whose `el`
   stamps are 200000 ms apart (the page was closed) → `unranked_why` starts `away`.
5. Browser 1280: with Test-day chosen, the Tools step shows "Pace guide" disabled with "Training
   only"; the lobby shows "this sitting ranks"; the runner shows the `Ranked` chip; Save and exit
   shows exactly [Keep going] and [Pause and exit].
6. The `Like test day` chip lands on `/test/?s=…#lobby` in one click with Timing official and
   Conditions Test-day.
7. A seeded learner whose last 2 sections each had 3 blanks at time-up: the orange preset chip is
   "Pacing practice" and its reason line contains "blanks".

#### X2. Training sections that bring the types you've met least, fair Test-day sections, and a lobby that says what it holds

*From: unfair-advantage #8. Effort S. Builders: S5 (`blueprint.fill`), F4 (`progress.types_met`),
S6 (the report line).*

**Why.** Which kinds of question a TopTierPrep student meets under the clock depends on their fixed
shelf, so some kinds turn up for the first time on test day. Within the official blueprint, ours can
pick, in each slot, the type this student has met least, when the student is training. A ranked
sitting is a measurement, so it must draw types the way test day does, not the ones this student is
weakest on.

**Server.** `blueprint.fill(..., order)` replaces the `name` sort key, which today favours templates
early in the alphabet (only the first `practice.CANDIDATES` = 7 by name are ever tried):
* **Test-day sittings** (ranked or not), papers' weekly slot build and Compete's forms: `order =
  'shuffle'`, the key is `(uses in this module, sha1(builder_seed + t))`. Every template in the domain
  that can make the slot's tier and format is equally likely; exposure plays no part.
* **Training sittings and custom tests from skills**: `order = 'exposure'`, the key is `(uses in this
  module, exposure.get(t, 0), sha1(builder_seed + t))`. `exposure` = the learner's attempts plus
  `practice_seen` rows per template. It applies at build and to module 2 at routing.
* Papers, twins and shares keep their slots. The domain split, tier ladder and grid-in positions are
  untouched in both orders, so the estimate stays valid.

**Lobby.** Two fact rows (public facts and counts only; no names before hand-in):
* `What it holds: Algebra 8 · Advanced Math 7 · Problem-Solving and Data 4 · Geometry and
  Trigonometry 3 · 6 grid-ins` (module 1's split and `SPR_AT`).
* `9 question types you haven't met under the clock · 4 you've never met at all`.

**Report** (S6 renders `result.new_types {n, right, templates}`): `New types this test: 9 · right on
5`, each with Practise.

**Tests page.** Under T4: `Question types met under the clock: 142 of 386`, with a quiet `Which
ones?` → `/me/#atlas?met=tests` (U8's atlas, not a new sheet). `progress.types_met(learner)` → `{tests,
practice, never}` is the one count that Me and Tests read.

**Acceptance.**
1. In `server/checks/s5.py`, with a seeded Builder: a learner with 40 attempts on Algebra template A
   and none on B (both able to make the slot's tier and format) gets B in the first Algebra slot of a
   Training section, for every builder seed 0–199.
2. Two fresh sections for a new learner keep domain counts 8/7/4/3, tiers 7/8/7 and grid-ins at
   `SPR_AT`.
3. An unbegun section's payload has `holds.subject == 'math'`, `holds.domains` summing to 22 and an
   integer `holds.new_types`, and a recursive scan finds no `key` or `template` values.
4. The Test-day key, over builder seeds 0–199, ranks each template of an Algebra slot's pool first at
   least once, and never reads exposure (the alphabetical lean is gone, and so is the personal one).

### B. In the module

#### X3. A pace guide built from your own speed (Training)

*From: outcomes #4, experience #5, unfair-advantage #4, the clock gaps of all three. Effort S.
Builders: S5 (`api_tests.pace_plan`), F3 (the strip tick, the delta line), F1 (`UI.lineChart` at
64px).*

**Why.** An even 95 s pace is wrong on a module that runs easy to hard: it calls every hard question
late. Theirs, and Bluebook's, is a bare countdown. We keep time per answer (R7), so the guide can be
the student's own.

**Budget per position.** `api_tests.pace_plan(learner, form, factor)` → `{subject, budget_s[n],
reserve_s, source: 'you'|'default', n_answers}` (n = the form's length, 22 for Math).
* Each position's tier comes from the form's public ladder (`blueprint.slots(form)`), never from the
  items served.
* The tier base is the student's median seconds on first-try right answers per tier over 60 days in
  timed contexts (tests and `clock: pace` practice), when each tier has at least 15. Otherwise P16's
  defaults: 65 / 95 / 126 s.
* The budgets are scaled to `duration − reserve`, where the reserve is 180 s × the timing factor.
* With `reveal_route` off, module 2 uses the mean of the two module 2 ladders, so the budgets can't
  reveal the route.

**Screens** (Training, `test_pace` on):
* **Strip.** The amber tick sits at the question you should be on (the first position whose
  cumulative budget passes the elapsed time). Checkpoint ticks after Q7 and Q14; hover or focus
  shows `By Q8: 24:10 left`.
* **Clock.** A DM Mono 12px line under the digits: `+1:20 ahead` or `0:45 behind`, ink, never red,
  updated every 5 s, hidden with the clock.
* **Checkpoint toast**, once each, when more than 2:00 behind: `2:10 behind at Q8. Mark anything past
  2:00 and come back.`
* **Check your work.** The pacing line becomes `6:12 left · keep 3:00 for checking · about 46 s for
  each unanswered question`.
* **Between modules.** `Module 1 pace`: `UI.lineChart` at 64px, cumulative plan against you, with
  `At Q11 you were 2:10 behind`.
* **Lobby row.** `Pace guide · paced to your speed (212 timed answers)`, or `· SAT tier pace (65 /
  95 / 126 s)`.

**Uses the rest of the site.** P16's tier defaults, U7's medians (the same attempts), T8's pace card
(one medians function), X17's Pace tile.

**Acceptance.**
1. In `server/checks/s5.py`: `sum(pace_plan(l, 'module1', 1).budget_s) == 2100 − 180` (±1), and
   `== 3150 − 270` at x1.5.
2. A Test-day payload has no `pace`. A Training payload with pace on has `pace.budget_s` of
   length 22.
3. A learner with 20 first-try rights per tier at medians 50 / 80 / 140 s gets `source:'you'`.
4. With `reveal_route` false, module 2's `budget_s` is identical after an upper and a lower route.
5. Browser, Training: staying on Q1 past its budget makes the delta line read "behind".

#### X4. Coaching nudges: the time sink, the last-minute blanks and the grid-in form (Training)

*From: outcomes #3 (nudge), unfair-advantage #4 (nudge) and the "Time's up" and grid-in gaps,
experience grid-in gap. Effort S. Builders: F3 (banners, the field warning), S5 (budgets in the
payload).*

**Why.** One stuck question eats the time three easier ones needed; blanks at the bell are free
points given away; `.66` for 2/3 is marked wrong. None of this needs the key to warn about.

**Nudges** (Training, `test_nudges` on). Each is a 40px `--wash` banner under the question header,
announced in the live region, never a modal:
* **Time sink.** Time on an unanswered question passes `max(2 × budget[i], 150 s)`: `3:10 on this
  one. Your budget for it is 1:35. Mark it and come back?` [Mark and next] [Keep going]. At most once
  per question.
* **Last minute.** At 60 s left with blanks: `3 unanswered. A guess can't cost you.` [Next blank]. It
  cycles through the blanks and never fills anything in. Once per module.
* **Grid-in form**, under the field for 6 s, key-blind. It fires only when the entry's fractional part
  has d ≥ 2 digits, the entry doesn't fill the grid (5 characters, 6 with a minus), and those d digits
  are exactly the d-digit truncation or rounding of j/n for n in {3, 6, 9} with j/n non-terminating.
  At d = 2 that is 15 values of the 99 from .01 to .99: `.11 .16 .17 .22 .33 .44 .55 .56 .66 .67 .77
  .78 .83 .88 .89`; at d = 3 the same cuts one digit longer (`.333`, `.667`, `.833` …). Integer parts
  pass through (`1.33` for 4/3 warns). Sevenths, elevenths and twelfths are left out: their cuts
  cover half of all two-digit decimals, and a warning that fires on `.45` teaches students to ignore
  it. Text: `If it repeats, fill the grid: .6666 or .6667, or enter 2/3. A short repeating decimal is
  marked wrong.` It shows once per value per sitting (`.66` twice warns once). The rule lives in
  `question.js` as `repeatingCut(str)` with a `__test` table, and a fixture on
  `web/dev/workspace.html`: `.66`, `.33`, `1.33`, `.667` warn; `.45`, `.64`, `.15`, `.85`, `.6666`,
  `.6667`, `0.5`, `.142` don't.
* Each firing is logged in `qstate._session.nudges [{kind, qid, at, took}]` for X17.

**After hand-in**, in both conditions: T7's `entry` cause labels a right value in a wrong form
"Right value, wrong form" in the report.

**Acceptance.**
1. Browser, Training, a custom test with `minutes:2`: at 60 s left with blanks the banner shows, and
   Next blank opens an unanswered question without filling it.
2. On a grid-in, typing `.66` shows the warning; `.45`, `.64`, `.6666` and `0.5` don't. Clearing
   and retyping `.66` in the same sitting doesn't show it again.
3. `repeatingCut` returns true for exactly 15 of the strings `.01` … `.99`.
4. In a Test-day sitting none of these banners exist in the DOM at any point.

#### X5. Check your work that walks you through: one queue, jump keys, and the second pass measured

*From: experience #4, outcomes #3 (the ordered pass and its measure), unfair-advantage #4 (triage)
and the navigator gap. Effort S. Builders: F3 (`UI.navigator` queue mode, `UI.checkYourWork`), F2
(keys), S5 (`pass`, `end_at`).*

**Why.** On theirs, revisiting 8 questions costs about 24 extra taps (cell, answer, navigator, Go to
Review Page, each time). A queue does it in one pill and Nexts, in the order that earns most.

**Check your work.**
* Above the grid, toggle chips with counts: `Unanswered 5 · For review 3 · Guesses 2` (Guesses when
  confidence tags are on). Default: Unanswered and For review.
* The pill `Go through 8` (Enter). Order: unanswered by position (modules run easy to hard, so early
  blanks are the cheapest points), then marked, then guesses.
* Training adds `Order: By position · Best value first`. Best value = p(right) ÷ expected seconds,
  where p = `ratings.odds(learner, template, tier)` (P11) and the seconds come from X3. Rows then
  read `Q18 · unanswered · about 1:10 · you get 80% of these`. The payload carries `odds` per qid in
  Training only (numbers, no names).

**Queue mode.** The footer centre reads `Going through · 3 of 8 · Q14 ⌃`. Next and → go to the next
queued question, Back to the previous. Queued strip segments get a ring. A quiet `Stop` returns to
`#review`. Answering a blank or unmarking updates the chips live. After the last one the student is
back on `#review` with the toast `Done: 5 answered, 2 unmarked`. The navigator's footer gets the same
`Go through 8` beside `Go to review page`. On a phone the pill is full width in the footer.

**Keys** (both conditions): `U` next unanswered (P20's key), `Shift+M` next marked, both wrapping.

**Pass 2.** `qstate._session.end_at` = the elapsed ms when the student first reaches the last question
or opens `#review`. The server sets `qstate[qid].pass = 2` for an answer that arrives after it. The
finish stores `result.pass2 {answered, right}`; the report (S6) shows `Pass 2: 3 answered, 2 right
(≈ +20)`, and the sittings row gets a `2nd pass +20` chip.

**Training navigator.** A `Time` view prints each cell's time and rings cells over twice their budget.

**Acceptance.**
1. Browser 1280 with 5 unanswered and 3 marked: `#review` shows "Go through 8". Enter opens the
   lowest unanswered position; the footer reads "Going through · 1 of 8"; after the last queued
   question the view is `#review` and the toast contains "Done".
2. From Q1, `U` opens the first unanswered question after it; `Shift+M` the next marked.
3. An answer posted after `end_at` has `qstate[qid].pass == 2`, and `result.pass2.answered` counts it.

#### X6. Thumb-first test window on phones, and one-gesture eliminate everywhere

*From: experience #9 and the question-strip gap. Effort M. Builders: F3 (`runner.js` gestures, footer,
`UI.pad`).*

**Why.** Their runner is a desktop Bluebook clone: eliminating takes the ABC toggle plus a small
circle, Mark sits at the top, and the phone keyboard covers the stem on grid-ins.

**Under 760px.**
* **Swipe** the question column left or right (at least 64px, angle under 30°) for Next or Back,
  with a 160ms slide. Never while text is selected, while Highlights & Notes or Scratch is on, or
  inside a `.q-table` scroller. No slide with reduced motion.
* **Long-press** an option for 450ms to strike or unstrike it without Eliminate mode, **only while
  Highlights & Notes and Scratch are both off**. A ring fills to show progress; `navigator.vibrate(8)`
  where supported; `-webkit-touch-callout: none` and `user-select: none` are set on `.opt` only in
  that state. With Highlights & Notes on, a long-press selects text as the OS does, so options can be
  highlighted (`o:i` marks), and striking uses Eliminate mode or `Shift+A–D`. With Scratch on, the
  pen owns the touch. The long-press hint in the More sheet says so: `Hold an option to cross it out
  (not while highlighting)`.
* **Footer** `[‹ Back 44] [Mark 44, bookmark, aria-pressed] [M1 · 7 of 22 ⌃] [Next]`. Mark leaves
  the question header on phones.
* **Answer pad** (`UI.pad`) for grid-ins, pinned above the footer: 0–9, `.`, `/`, `−`, ⌫, in 4 rows
  of 44px keys, with the field at `inputmode="none"`. The OS keyboard no longer covers the stem, and
  the minus a decimal pad lacks is there. A `Use the answer pad` switch in More; on by default where
  `matchMedia('(pointer: coarse)')` matches; stored in localStorage `satf.pad` (try/catch).
* Swiping up on the footer button opens the navigator sheet.

**Desktop.** Right-click on an option strikes it; the context menu is suppressed on `.opt` only.

**Acceptance.**
1. At 390: `#markFoot` is in the footer with `aria-pressed`; a 450ms pointer hold on option B gives
   it `.out`; a 100px left swipe on the column opens Q2.
2. At 390 with Highlights & Notes on: a 450ms hold on option B's text leaves B without `.out`, and
   `getComputedStyle(optB).userSelect` is not `none` (the OS selection can start).
3. On a grid-in at 390 the pad shows 15 keys and the field has `inputmode="none"`; tapping `−`, `2`,
   `/`, `3` renders −2/3 in the preview.
4. At 1280, a `contextmenu` event on an option is `defaultPrevented` and the option is struck (with
   Highlights & Notes on, the native menu is left alone).

#### X7. Solve first: cover the choices, in Training

*From: experience #6. Effort S (P5 is the mechanism). Builders: F3 (P5's covered state in exam
mode), S6 (the report line).*

**Why.** Solving before looking is the habit that beats trap answers, and only a bank whose wrong
options are named can count how many trap picks it prevented.

**What changes from P5.** In a Training sitting with `test_cover` on, P5's cover applies to every
multiple-choice question: one `--tile-2` block at the options' final height, `Choices covered ·
work it out, then reveal (V)`, and P5's optional "Your answer" field. Revealed stays revealed.
`qstate[qid]` stores `covered`, `reveal_ms` and `own` (the typed value). Scoring is unchanged.

**Report** (S6): `Solved first on 18 of 22 · 86% right · 1 trap pick, against 4 where you looked
first`, and per question `Revealed after 1:05 · your worked answer 12 matched "used the diameter"`.

**Acceptance.** Browser, Training with cover on: `.opts.covered` exists on a multiple-choice
question, `V` removes it, and `GET /api/session/{id}` then has `qstate[qid].reveal_ms > 0`. In a
Test-day sitting the Cover control and `V` do nothing.

#### X8. Your working, kept: a scratch layer and the calculator log per question, shown in review

*From: unfair-advantage #12 and #11, experience #10, outcomes #7 (capture) and the Highlights gap.
Effort M. Builders: F3 (`UI.scratch`, `UI.calc` capture), S5 (`/state` fields and caps), F4
(`record_paper` writes P3's `attempts.calc`), S6 (the review renders it).*

**Why.** Neither theirs nor Bluebook keeps a student's working, so a review can only show the key
and prose. Ours can show the step where your method went wrong, next to the misconception your pick
named.

**Scratch** (tool `Scratch` in the top-bar tools, key `Shift+L`, beside `L` for Highlights &
Notes, since `X` is Details in the shared runner map; both conditions, since the SAT gives
scratch paper):
* A transparent canvas over the question column: Pen, Marker, Eraser, Clear; touch, stylus or mouse;
  graphite only. On a phone two fingers scroll while the pen is on, and `Done` closes it.
* A `Typed scratch` box under the options (DM Mono, 0/1000) for keyboard users.
* Strokes are simplified (Ramer–Douglas–Peucker at 1px) and saved as `qstate[qid].scratch {w,
  text, strokes, typed}` (w = column width, text = text size, so the overlay lines up again),
  through the save queue. At most 20 KB a question (422 `scratch too large`) and 256 KB of qstate a
  sitting.

**Calculator log.** On each question change, if Desmos changed, the runner diffs
`getState().expressions` and stores what was added or edited as `qstate[qid].calc {open_ms, exprs
[≤20 LaTeX strings, ≤200 characters each]}`. It opens a Desmos folder named `Q8` for the next
question so the list stays readable. `record_paper` sets P3's `attempts.calc = 1` when `exprs` is
non-empty.

**Review** (S6, after hand-in): a `Your working` block under the question: the ink over the stem where
it was drawn, the typed scratch, a read-only Desmos with your expressions, and P3's "The Desmos way"
beside it when the template has one.

**Acceptance.**
1. `POST /api/session/{id}/state {question_id, scratch:{…25 KB…}}` → 422; 10 KB → 200 and returned in
   `GET` qstate.
2. Browser: draw a stroke on Q3, reload: the stroke is there at the same place.
3. Type `y=2x+1` in Desmos on Q4, move to Q5: `qstate.m1q04.calc.exprs` contains it. After finish,
   `SELECT calc FROM attempts WHERE session=… AND qid='m1q04'` is 1.

#### X9. Tools beside the question: one right-hand slot with a searchable reference, math-named marks, Save, and type notes in Training

*From: experience reference and highlight gaps, outcomes reference gap, unfair-advantage
question-strip gap. Effort S. Builders: F3 (`UI.runner` slots, `UI.ref` dock, `UI.annotate`
labels), S10 (Save through the saved endpoints).*

**Why.** Their reference is a modal image that covers the question, so students flip back and forth.
Their highlighter is general-purpose and rarely used on math.

* **One layout rule for every panel** (`UI.runner` owns it, so the calculator, reference, notes and
  grid-in rail never compete):
  * **Left dock**: the calculator (`UI.calc`, 420px default, resizable 320–560px).
  * **Right slot**: one 300px panel with tabs `Reference · Notes · Entering your answer` (the last
    only on grid-ins). The v2 notes rail (300px) and grid-in rail (260px) stop being separate rails
    and become these tabs; the grid-in rail no longer moves when the calculator docks. On a grid-in,
    the slot opens on `Entering your answer` unless the student closed it in this sitting. `F`
    opens the slot on Reference (again closes it); `O` (my note) opens it on Notes.
  * **Question column**: 560px minimum, 700px maximum, centred in what is left, 16px from each panel.
  * **Fitting**: column = viewport − open panels − 16px gutters. When that is under 560px, the
    calculator narrows first (to 320px). If it is still under 560px, the panel opened later floats:
    the calculator as v2's floating window, the right slot as a 300px overlay from the right edge with
    a shadow and ×, over the page margin first. Both dock at 1212px and wider (320 + 16 + 560 + 16 +
    300); at 1280 with both open the calculator sits at 388px and the column at 560px. Under 1180px
    the right slot is a half-height sheet, as v2's phone sheets.
* **Reference** (the Reference tab, `UI.ref({mode:'dock'})`). A search field filters entries (`cyl`,
  `30-60-90`); each formula group collapses on its own. The runner counts `qstate[qid].ref_n` and
  `ref_ms`. In review, the formula the question used is highlighted (P24).
* **Math-named marks.** The first three toolbar styles carry names as their labels and tooltips:
  **Asked for** (box), **Given** (highlight), **Ignore** (strike). The other four are unchanged. The
  Notes tab lists each question's "Asked for" text.
* **Save** (`Z`, both runner modes, the one save key practice.md sets, §3.2 §2.8) keeps the question
  in Review › Saved (R5), with `From Full section #12 · key after you hand in` until the sitting
  finishes (R19 withholds it). `B` is never Save in the runner: in exam mode it always chooses B,
  and in practice it chooses B before Check (practice acceptance 29).
* **Type notes** (P21's `notes.seed = −1`). A note on a question can follow its type. **In Training
  only** (`test_type_notes`, on, listed under "Training aids"), `Your note on this kind, Sep 12:
  square the radius first` shows under the stem of a later question of that template; the payload
  carries only the note's text for that qid. Under Test-day the note is absent from the payload and
  the DOM, because it is a method hint that marks the type, and ranked sittings must be sat without
  aids. After hand-in, in both conditions, the review shows the note beside the question.

**Acceptance.**
1. At 1280 with the calculator docked, the Reference tab open and a grid-in question: the question
   column's bounding box is at least 560px wide and fully inside the viewport, neither panel overlaps
   it, and typing `cyl` leaves only the cylinder entry.
2. At 1180 with the calculator docked, opening the reference makes the right slot float
   (`#rightSlot.float`), and the column stays at least 560px wide.
3. After opening the reference twice on Q2, `qstate.m1q02.ref_n == 2`.
4. `Z` on Q3, then `GET /api/saved` lists it with the sitting id; the review item for it has no
   key until the sitting is finished. `B` on Q3 in the same sitting selects option B and saves
   nothing.
5. A learner with a type note on template T: a Training sitting's payload for a T question carries
   `type_note`; a Test-day sitting's payload has no `type_note` at any depth.

#### X10. Report after the test, and a question with a bad key leaves your score

*From: outcomes, experience and unfair-advantage report gaps. Effort S (U3 is the mechanism).
Builders: F6 (`UI.report` `ctx.live`), S5 (removal at finish), S6 (the line).*

**Why.** Filling in a form mid-test burns the clock, and on theirs a bad question still counts
against you.

* **Mid-test.** `UI.report(ctx)` with `ctx.live = true` opens with a primary row `Remind me after the
  test` (one tap: adds the qid to `qstate._session.report_later` and toasts `We'll ask after you hand
  in`). U3's one-tap category chips sit under it with `The clock keeps running`. Marking and key
  disputes stay hidden mid-test (R17).
* **After hand-in.** The hand-in moment (X12) lists `You flagged Q7 to report` with `Report now`,
  which opens the sheet prefilled with `include_answer` on.
* **Removal.** At finish and on every results read, a position whose (template, seed) has a report
  resolved `wrong key` or `no right answer` (U3's solver disagreed, or an admin confirmed), or whose
  template is quarantined, leaves both right and asked. The estimate is recomputed and the route
  stands as taken. `result.removed [qid]`; the report reads `Q7 was removed from your score after
  your report. The solver disagreed with the key.`

**Acceptance.**
1. `POST /state {report_later:'m1q05'}` → `GET` shows it in `qstate._session.report_later`.
2. With a resolved `wrong key` report on m1q05's (template, seed) in `$DB`, `GET
   /api/session/{id}/results` has `removed:['m1q05']` and `modules[0].asked == 21`.

### C. The hand-in

#### X11. Between modules: Bluebook's 60-second step under Test-day, and "Which ones do you think you missed?" inside it

*From: outcomes #6, and the module-sequence gap (a break that still ranks). Effort S. Builders: S5
(the break stamps, `predict` accepted after the module, the ranked rule), F3 (`#between` countdown,
the grid sheet), F4 (T9's rule), S6 (the report split).*

**Why.** A miss you didn't see coming repeats on test day, and it is the one to fix first. Under
Test-day conditions confidence tags are off, so this is the only calibration a strict sitting gets,
and it costs no test time. And in v2, module 2's clock starts only on Begin, so a Test-day sitting
could rest for hours between modules with 0 pauses and still rank, which Bluebook never allows and
which mixes rested and unrested sittings in every percentile.

* **Test-day `#between`.** Bluebook goes straight into module 2, so ours gives one short step: a
  visible countdown `Module 2 starts in 0:48` (DM Mono, the 60 s bar draining under it, announced at
  0:30 and 0:10), the prediction sheet inside it, and `.btn Begin module 2 now` (Enter when the sheet
  is closed). At 0:00 module 2 begins by itself (the same `/begin` call). The countdown starts when
  module 2's payload has arrived, so a slow hand-in never eats it.
* **Leaving it counts as a break.** `/begin` for module 2 carries X1's stamps plus `between_ms`
  (payload arrival → Begin on the page's clock). Break = `between_ms`, or, when Begin comes from a
  new page load (the page was closed or Save and exit was used), the server time since module 1's
  finish. A break over 75 s (the 60 s plus slack for a slow device) keeps the score and unranks with
  `unranked_why 'break 12:40'`; Save and exit on `#between` under Test-day says so first: `Leave now?
  Module 2 would start when you're back, and this sitting won't rank.` Hidden time inside the 60 s
  counts toward X1's away total. A Begin queued offline carries its stamp, and module 2's clock
  starts at that stamp's time, so offline time is neither free time nor a break.
* **Training `#between`** keeps v2's open step: no countdown, Begin when ready, with the module 1
  pace trace (X3) and, with Tell me my module 2 on, the gate margin (X14).
* **Where the prediction shows.** On `#between`, above Begin (inside the countdown under Test-day),
  and after the final `Hand in`, before the hand-in moment (no clock is left then). Pref
  `test_predict` (default on).
* **Sheet.** `Which do you think you missed? (optional)`, the module's grid at 44px, each cell with
  its number and a two-word skill label. A tap toggles a dashed graphite ring, `Think I missed`.
  [Done] (Enter) and quiet [Skip]. It takes about 20 s.
* **Data.** `POST /state {question_id, predict:'miss'|null}` is accepted for a handed-in module's
  qids until 15 minutes after the final finish; every other field still gets 409. Unanswered cells
  can't be ticked. `result.between {ms, source:'stamp'|'server'}` is stored at the final finish.
* **Report and habits.** A miss is **Spotted** (predicted, or tagged Unsure or Guess) or **Silent**;
  a right answer predicted as a miss is **Underconfident**. Silent misses go first in Fix and join
  T9's blind spots (§3.2).

**Acceptance.**
1. After module 1 is handed in, `POST /state {question_id:'m1q03', predict:'miss'}` → 200, while
   `{question_id:'m1q03', marked:true}` → 409. After the final finish, the results'
   `predicted.spotted + predicted.silent` equals the number of wrong answers.
2. Browser, Test-day: after handing in module 1, `#between` shows a countdown under 1:00; with
   nothing pressed, module 2's first question is on screen within 62 s and its clock is running.
3. In test_flow: a Test-day section whose module 2 `/begin` comes from a new `pid` 10 minutes after
   module 1's finish → after the final finish `ranked == 0` and `unranked_why` starts `break`. The
   same with `between_ms` 55000 → `ranked == 1`.
4. Browser, Training: `#between` has no countdown, and module 2 waits for Begin.

#### X12. The hand-in moment: the band against last time, what was earned, the next step

*From: experience #8. Effort S. Builders: S5 (the finish response, `api_tests.moments`), F1
(`UI.scale`), S1 (achievements rules, optional).*

**Why.** Theirs drops you on rings with no comparison and no next step. The moment right after a test
is when a student will take the next useful action, so it gets one screen.

**Screen `#done`** (replaces the redirect after "Marking your test…"):
* `k` `Full section #12 · handed in`, and the chip `Ranked` or `Unranked · paused once`.
* The band on `UI.scale` (200–800) with the previous band as a ghost outline and the target tick. The
  numbers count up once over 600ms; static with reduced motion.
* The headline: `Up 40 since Sep 12` / `Level with Sep 12` / `Your first estimate`.
* The route chip (`Harder module 2`), now that the test is over, with the gate margin (X14).
* Up to 2 earned moments from a fixed list, each one line with our trophy or marks icon: first route
  to the harder module 2, a new best band, no blanks, beat this paper's average, every module finished
  with 3:00 or more left, a twin 30 or more above its original, first High confidence. Nothing shows
  when nothing is earned.
* The report-later list (X10).
* Actions: the pill `Pressure check · 9 questions · ~12 min` when eligible (X13), else `See your
  report`; `.btn See your report`; quiet `Fix 7 now`; quiet `Back to Tests`.
* Unscored kinds read `17 of 22 right · practice, no estimate`. The diagnostic shows no band: its
  pressure check (if any) runs, then its sign-up gate (R38). Offline keeps v2's `Handing in when you
  reconnect` state.

**Data.** The final `POST /finish` adds `done {subject, estimate {low, high, previous, best, target},
route, gate, moments[], misses, blanks, report_later[], pressure {eligible, n, minutes}}`, with one
`done.sections[]` entry per section once a paper has more than one (decision 3).

**Acceptance.** Finishing a section returns `done.estimate.low` and `.high`; the browser stays on
`#done` (no redirect) and shows "See your report", plus "Pressure check" when there were misses; with
`prefers-reduced-motion` the band has no animation class.

#### X13. Pressure check: an untimed round of twins that splits what you don't know from what the clock took

*From: unfair-advantage #1, experience #1, outcomes #1 (the confirm step). Effort M. Builders: S5
(`api_tests.resolve_drill`, `on_drill_finish`), F5 (the `pressure` field, `cfg.inline`), S6 (the
report block), F4 (`estimate.rescore`).*

**Why.** Their report splits Correct / Incorrect / Unanswered (and contradicts itself). It can't say
why a question was lost. A slip, a question the clock took and a real gap need opposite fixes, and
only a bank that can serve the same question type at the same difficulty with new numbers, before the
key is seen, can tell them apart.

**Eligible.** Any finished timed sitting (section, paper, twin, shared, module, custom, diagnostic)
with at least one qualifying question, until the report's question review is first opened (S6 sets
`qstate._session.keys_seen`) or 7 days pass. Trap tests are already retests and aren't eligible.

**Which questions.** Every qid that was wrong, blank, tagged Guess (right or wrong), or took more than
2 × its budget (P16) × the timing factor. At most 15, wrong and blank first, then in position order.
The screen doesn't say which is which: `9 questions like ones you missed, left blank, guessed or spent
long on. Same kind, same difficulty, new numbers, no clock.`

**Build.** `POST /api/drill {pressure: sid}`. S5's resolver (§3.2, the R10 registry) turns it into
`{pool:'items', ids:[[template, seed]], exact:true, feedback:'end', timing:'off', source:'pressure',
parent: sid}`, with each seed from `blueprint.draw_matching` on the learner's Builder (same template,
tier and format) and `cfg.pressure_of {new_qid: old_qid}`. It is inline (R24): never listed, counted
on the parent. It runs in the practice session in end mode: nothing revealed, a count-up clock, ms
per question. Finishing goes to `/results/report/?id=PARENT#pressure`.

**Classify** (`api_tests.on_drill_finish(row)`, called from `drill.finish` when `cfg.pressure_of` is
set), one verdict per original question:
* **Knowledge**: the twin is wrong with the same norm as the test pick (R9). `Real gap: <label>`.
* **Shaky**: the twin is wrong another way.
* **Speed**: the twin is right but over 2 × budget. `You can do it, not yet at test speed.`
* **Pressure**: wrong or blank in the test, twin right within 2 × budget.
* **Lucky**: right in the test with Guess (or slow), twin wrong.
* **Confirmed**: right in the test with Guess (or slow), twin right.

**Stored** on the parent: `result.pressure {buckets:{knowledge:[qid], shaky, speed, pressure, lucky,
confirmed}, ceiling, routes_up, drill}`. `ceiling` = `estimate.rescore(sid, pressure positions)`;
`routes_up` when those flips cross 14 of 22 in module 1. The twins' answers file as normal attempts
(fresh items) and count toward mastery; the sitting's band, percentile and paper stats never change.
Knowledge verdicts sort that trap first in Fix and Review, like a sure miss (§3.2).

**Report block** (S6): a stacked bar with counts and glyphs, `Knowledge 3 · Speed 1 · Pressure 3 ·
Lucky 1`, and `Your band today 540–680. Without the 3 pressure losses: 580–720.` Each bucket lists its
`M1 Q7` chips and one fix:
* Knowledge → `Fix these 3` (`pool:'redo'`, those traps).
* Speed → `Timed sprint · 6 at 95 s` (`{templates, count:6, timing:'pace'}`).
* Pressure → `Next test in Training with the pace guide` (the start sheet at `Pacing practice`).
* Lucky → `Practise 5 like it` (`{templates, count:5}`).

**Elsewhere.** T7's causes use the verdicts for these questions (§3.2). The sittings row gets
`Pressure 3 · Knowledge 3`, and the Status filter gains `Pressure losses`. X17 has a Pressure tile.

**Acceptance.**
1. A section finished with 3 wrong and 2 blank: `POST /api/drill {pressure:sid}` gives a session of
   at least 5 items whose template and difficulty equal the originals' and whose seeds all differ;
   `GET /api/history` doesn't list it.
2. Answering a twin wrong with the original pick's reason puts that qid in `knowledge`; a blank
   original whose twin is right in 40 s goes to `pressure`; `ceiling` midpoint ≥ the band's midpoint.
3. After the report's review has been opened, `POST /api/drill {pressure:sid}` → 409 `answers already
   seen`.
4. `progress.causes(session=sid)` gives `slip` for the `pressure` qids and `trap` for `knowledge`.

### D. After the test

#### X14. The route gate: your margin to the harder module 2, a Route-up trainer, and the gauntlet

*From: outcomes #5, unfair-advantage #5, experience #2 (the route row), unfair-advantage
between-modules gap. Effort S. Builders: S5 (`result.gate`, trainer kinds), S6 (report line), F5
(drill `templates`).*

**Why.** The route is the one sudden jump in the score: the easier module 2 caps Math at 580, and the
gate is won or lost on module 1's easy and medium questions. Theirs shows "Adaptive" as a label and
never says how close you came. A free student there gets one attempt; only a generator can serve a
fresh module 1 every time.

* **Data.** Every sitting with a standard module 1 stores `result.gate {subject, right, needed:
  ceil(0.60 × asked), margin, cheap_misses:[positions of easy or medium misses]}` (one per section).
* **Lines.** Report and `#done`: `Routed up with 2 to spare` / `1 short of the harder module 2 · 2 of
  your misses were easy or medium`. The sittings row gets the margin chip. `#between` shows it only in
  Training with `reveal_route` on.
* **T1 Gate row** (replaces "Routed up"): `Gate · routed up 4 of 6`, plus a DM Mono strip of the last
  6 margins around a zero line, orange above it. When 2 of the last 3 sections routed lower: `Your
  last sections routed lower, so they top out at 580. One more right in module 1 lifts the cap.` with
  `.btn Protect the gate · 12` → `POST /api/drill {templates: the cheap misses' templates, count:12,
  timing:'pace', source:'gate'}`.
* **Route-up trainer** (T4 card 8; shown while fewer than 4 of the last 5 sections routed up, or before
  any section). Tags `Module 1 · Official timing · Test-day`; facts `22 questions · 35 min`; goal
  `Route up 3 times in a row` with pips for the last 5 trainer sittings and `Best streak 2`. Start →
  `{kind:'module', module:'m1', trainer:'route', conditions:'test_day'}`. Lobby fact `The line: 14 of
  22 right routes you up`. On `#done`: a 22-cell strip marking where the 14th right answer would be;
  `These cost the route: Q2 (easy), Q5 (easy)` each with `Try a twin` (R24); pill `Fix what cost the
  route` (`{from_session, only:[those], each:2}`); quiet `Next module 1`. Streaks count Test-day,
  official timing only.
* **Gauntlet.** Card 3 (Module 2 · harder) adds, when the target is 620 or more or after 2 upper
  routes, the goal `18 of 22 on the harder module 2` and pips for the last 5 (`trainer:'gauntlet'`).
* **How scoring works** gets a diagram: M1 → 14 of 22 → harder module 2 (up to 800) / easier module 2
  (up to 580).
* The sittings Kind filter adds `Trainer`.

**Acceptance.**
1. A module 1 with 13 right: `result.gate == {right:13, needed:14, margin:-1, …}`.
2. Three trainer sittings that route up in a row → `GET /api/tests` `kinds` row `trainer` has
   `streak:3`.
3. The Protect the gate body's templates are all easy or medium misses from module-1 positions.

#### X15. What moves this band: the score card that prescribes

*From: outcomes #1 and #10, experience #2 and the score gap, unfair-advantage #2 (its gains part) and
the empty-state gap, outcomes growth-percentile gap. Effort M. Builders: F4 (`estimate.growth`,
`estimate.calibration`), S5 (`levers` in `/api/tests`), S3 (Add a score), `tools/calibrate.py`.*

**Why.** Theirs is "Math 200-280 · LOW CONFIDENCE", and v2 adds more facts about the past. The card
should say which points can be won back, what each is worth, and start that work.

**T1 additions.**
* **Confidence reason as a button.** `Low: one module so far. One full section narrows it to about 140
  points.` with `.btn Full section · 70 min`, or `One more section makes this High · Start`.
* **Total.** With `rw_now`: `Total 1180–1320 · with your R&W 620 (entered Sep 12)`. Without it: an
  inline `Add your R&W score` (S3's Add a score, R15). The only R&W number on the page, and additive
  (decision 3).
* **Projection.** U9's cone to the exam date on the band chart, and T10's verdict line (`On pace:
  about 640–700 on Oct 3 · target 700`).
* **Growth percentile** (n ≥ 20): `Since your first section: +80 · more than 72% of students who
  started near 480 (41 students)`. `estimate.growth(learner)` compares the first ranked section's
  midpoint with `mean3`, among learners whose first ranked section was within ±40 and who have 2 or
  more ranked sections.
* **Calibration.** `Your Bluebook test: 610 (Sep 20) · our estimate then: 560–700 · inside`, from
  `outside_scores` (Bluebook or official) within 10 days of a ranked section. How scoring works says
  `Checked against 312 Bluebook and official scores` at 50 or more pairs, else `Not yet checked against
  real scores`. `tools/calibrate.py` prints the pairs, a least-squares fit of `scoring.ANCHORS`, and
  the residual spread; a person commits any change.
* **"What moves this band"** (full width in the card, under the facts):
  * **Where the points went · last 3 sections**: one row per T7 cause (plus `changed`, §3.2) over
    those sittings: `Traps · 6 questions · ≈ +40`. Points = the mean over the sittings of the rescore
    with that cause's positions right. Each row has one action: Traps → `Fix 6` (`pool:'redo'`, those
    traps); Clock → `Pacing practice` (X1); Slips → `See your 4 slips` and `Careful set · 8`; Entry →
    `Grid-in entry drill · 5`; Gaps → `Learn it` (T4) on the top gap topic; Changed → `See the changes`
    (report `?filter=changed`).
  * **The route lever** (X14), when a lower route fell within 2 of the cut: `1 more right in module 1
    on Sep 12 would have lifted the 580 cap · up to +70`.
  * **Skills worth the most**: the top 3 of U4's `estimate.gains` as `UI.skillRow`, with a quiet `All
    skills` → Today's `#gain`.
  * A sum line: `Traps and slips together ≈ +60 · your 700 target is inside`, one rescore of both.
  * Helper: `Worked out by re-marking your own sittings with those questions right.`
  * Empty: `Sit a full section to see where your points went.` with the section pill.

**Data.** `GET /api/tests` adds `total`, `projection`, `growth|null`, `calibration|null` and `levers
{subject, causes:[{cause, n, pts, route_pts, action}], route|null, skills:[top 3], both {pts,
band}}`.

**Acceptance.**
1. A seeded learner with 2 sections, 4 named-trap misses and 3 blanks at time-up: `levers.causes` has
   `trap` with `n:4, pts>0` and `clock` with `n:3`, and the trap action body has `pool:'redo'`.
2. `growth` is null with fewer than 20 peers.
3. An outside Bluebook score 610 dated 3 days after a section banded 560–700 → `calibration.inside ==
   true`.
4. With `rw_now` 620, `total` is present and the card shows "Total".

#### X16. Test → Fix → Prove: a repair, then a timed, spaced retest of every missed type, with a verdict

*From: outcomes #2, unfair-advantage #3. Effort M. Builders: S5 (the Cycle card, the Trap test kind in
`blueprint.custom`), F5 (the `want` walk, pool `related`), F4 (R9 check-ins), S6 (verdict block), S7
(the Prove task, optional).*

**Why.** Their loop is test → report → nothing, and a retake shows the same questions again. A fix
made in untimed practice often fails under the clock. A retest that is timed, spaced and offers the
exact trap you fell for is the proof, and only a bank that can walk a template to a seed offering a
named wrong answer can build it.

**Cycle card** (`#cycle`, above In progress; for the latest scored sitting with 3 or more misses in the
last 21 days). A 3-segment stepper, each with its state and date:
* **Fix 7**: `POST /api/drill {from_session, scope:'misses', source:'fix'}`; silent misses (X11) and
  Knowledge verdicts (X13) first; P2's worked example first per `worked_first`.
* **Prove (due Sat)**: due on R9's first check-in date (fix + 3 days). It starts a Trap test from the
  sitting (below). Verdict per misconception: `Held ✓` / `Held, but slow (2:40)` / `Relapsed ✕`.
* **Twin (from Sep 30)**: T16's `Retake as twin`, 7 or more days after the original.
* A line: `Proved 5 of 7 · worth ≈ +40 on Section #12` (the rescore with the proved positions).

**Trap test** (T4 card 9, step 1 option). Tags `Your traps · Test rules`; facts `6–22 questions · 95 s
each`; helper `Every question offers a wrong answer you've fallen for before. Do you still take it?`;
stats `Traps ready 14` (open, check-ins due, and closed within 60 days) and `Last trap test: took 3 of
12`.
* **Step 2**: `Which traps`: All ready 14 / Open 9 / Check-ins due 5 / From a sitting (dropdown) / Pick
  (a checklist of trap labels with topic glyph and `hit 3×`); Length 10 / 22 / all; `Neutral questions
  mixed in`: 1 in 4 (default) / none.
* **Build**: `POST /api/mock/new {kind:'custom', custom:{source:'traps', traps:'all'|'open'|'due'|[ids],
  from_session?, count, neutral:0.25|0}}`. `blueprint.custom(queue=[(template, norm)])` walks each
  template for a seed that offers the norm (the drill body's `want` walk, §2.6), else pool `related`
  (a sibling template with the same norm). Neutral slots come from the same skills with none of the
  learner's trap norms on offer, so the test isn't transparent. At least 6 questions, ladder order, 95 s
  each, no reveal until hand-in. Not scored; `UI.KIND` `Trap test`.
* **Marking** per question: trap taken / other wrong / right / blank. A right, non-guess answer with the
  trap on offer is a clean check-in (R9 `checks + 1`); taking the trap reopens it as Relapsed.
* **Result** (S6): `Your traps were on offer 14 times. You took them 3 times.` and `Last time: 7 of 12
  (Sep 2)`; one row per trap with `offered 2 · taken 0` and `Check-in passed / Still open / Relapsed`.

**Up next (T2).** Prove due comes second, after Resume. A Trap test is offered when 5 or more check-ins
are due or 8 or more traps are open and none was sat in 7 days. Plan can place `Prove Section #12 · 9 q
· 15 min` on its due day.

**Acceptance.**
1. After a section with 3 named traps, fixing them (2 clean answers each) gives `GET
   /api/tests.cycle.prove.due` = the closing date + 3 days.
2. `{"kind":"custom","custom":{"source":"traps","from_session":ID,"neutral":0.25}}` builds at least 6
   questions; each trap slot has an option whose stored reason's norm equals its trap's norm; the neutral
   slots offer none of the learner's trap norms.
3. Choosing the trap option reopens that trap with `relapses + 1`; a right non-guess answer adds 1 to
   `checks`.
4. The Trap test's results have `estimate: null`, and `/api/history` labels it `Trap test`.

#### X17. How you take tests: your test-taking habits across sittings, each with one fix

*From: experience #3, unfair-advantage #10, outcomes #3 and #6 (their measures), the "time analysis"
gap. Effort M. Builders: S5 (`api_tests.habits`), F1 (`UI.spark`), S6 (drill-down targets).*

**Why.** Theirs records nothing about how a student sits a test (no time per question, a stopwatch
that resets on reload, an empty contest Time Analysis). Our qstate (ms, first answer, changes, marks,
passes, confidence, calculator, reference, away, predictions) turns into coaching on test-taking
itself.

**Section `#habits`** on `/tests/`, after T1–T3, with a nav item that carries its row count (`Habits 15`). Shown after 2 finished
timed test sittings; before that `Sit 2 timed tests to see how you take them: pacing, blanks, answer
changes, marking and confidence.` with the Up next pill.
* **Filters**: `Last 5 · 10 · All` and `Sections and papers · All timed`.
* **Rows**, all shown (decision 4), those that cost points first by points, then the good ones. Each: a
  glyph (✓ good, ! costs; ink), a title (600 15px), an evidence line (DM Mono 13px), the trend against
  the previous 3 sittings, a 60×20 `UI.spark` per sitting, one action, and a `Why` popover with its
  rule. `Which sittings?` sets the T6 filter.
  1. **End of module**: `Q17–22: 38% right · Q1–16: 71%` → `Hard-end practice · 10 hard at 95 s`.
  2. **Finish margin**: `4 of 12 modules ran to 0:00`, or `You kept 4:10 on average to check` →
     `Pacing practice`.
  3. **Pace by position**: `You reach Q16 with 9:10 left on average` (X3's budgets).
  4. **Blanks**: `1.2 a module · ≈ −10 against guessing` (blanks × 0.25 × a question's worth).
  5. **Answer changes**: `7 right→wrong, 3 wrong→right · ≈ −40` (qstate first vs final) → `See the
     changes`; or the good `Your changes pay: +5 net`.
  6. **Mark for review**: `Marked 18 · went back to 15 · changed 6 · gained 4`.
  7. **Second pass**: `Pass 2: 3 answered a module, 2 right` (X5).
  8. **Calibration**: `Spotted 4 of 7 misses · 40% → 57%` (X11).
  9. **Confidence**, when used: `Sure 91% · Unsure 62% · Guess 30%`.
  10. **Calculator**: `Open on 40% of questions · right 78% with it, 64% without`.
  11. **Reference**: `Opened 4 times a module (1:50)`.
  12. **Away**: `Left the window 3 times in 5 tests`.
  13. **Pressure**: `Pressure losses 3 a test, down from 5` (X13).
  14. **Eliminations**: `Crossed out the right answer 2 times` (X19).
  15. **Nudges** (Training): `Took 2 of 3 time-sink nudges`.
* Rows from sittings without qstate are counted out, and the header says `from 4 of 7 tests`.

**Data.** `GET /api/tests.habits {subject, n, from_n, rows:[{id, verdict, title, evidence, series,
points, action, why}]}` from finished, timed, non-abandoned test sittings. It reads T7's `changes`, so
the counts match Today.

**Acceptance.** A seeded learner with 3 timed sections whose qstate gives 5 right→wrong and 2
wrong→right: the `changes` row has `verdict:'costs'` and evidence containing "5" and "2"; with 1
sitting the section shows the empty state; with data, at least 8 rows render and no "Show all" control
exists.

#### X18. Compare any two sittings, with a slot-by-slot diff for twins and retakes

*From: experience #11, unfair-advantage #6 (the diff and chains), outcomes retake gap. Effort M.
Builders: S6 (the compare endpoint, extended), S5 (the sheet, the checkboxes).*

**Why.** Their results list can't compare sittings, and a fixed paper can't be re-sat fresh. Our twins
make the comparison fair (same types, same positions), so "did I improve?" gets a real answer.

* **Rows.** Each T6 row gets a `Compare` checkbox (`X` on the focused row). With two ticked, a sticky
  bar: `Compare #11 and #14` [Compare] [Clear].
* **Compare sheet** (720px; full height on a phone). Two columns: band, M1, M2, route and margin, time
  used, blanks, away, pauses, conditions; the 4 domains' bars side by side; a `Question types` table.
  * When one sitting is a twin, rematch or paper retake of the other (the same root), it is slot by
    slot (M1 Q1 …) with ✓/✕ per side and `Fixed 5 · Still missed 2 · New 1 · Held 36 · +60`. Each
    still-missed slot says `Same trap both times: <label>` or `A different mistake`.
  * Otherwise it joins by template in three groups, `Missed both times`, `Fixed`, `New misses`, each
    with Fix.
* **Deep link** `/tests/?compare=11,14`. A twin's row carries `vs #11: +60 · fixed 5`, and a chain
  reads `3rd sitting of this form` (`cfg.twin_of` holds the root, as P19's `rematch_of`).
* **Retakes.** A paper's Retake is a twin (X20). `Again, exactly · tests memory` stays as a quiet
  option.

**Data.** S6's `GET /api/session/{id}/compare?with=` (T16) accepts any two of the owner's sittings (403
otherwise) and returns `{by:'slot'|'template', a, b, rows, summary}`.

**Acceptance.** A twin against its source returns `by:'slot'` and summary counts that add up to the
slots asked; two unrelated sections return `by:'template'`; another learner's code gets 403; ticking
two rows shows the bar; `?compare=a,b` opens the sheet.

#### X19. Eliminations read against the traps

*From: outcomes #8, unfair-advantage question-strip gap. Effort S. Builders: F4 (`record_paper`
writes P6's columns), F3 (`struck_ever` in the trail), S6 (the lines).*

**Why.** They save eliminations and show nothing from them. Every one of our options names its
misconception, so a strike can be graded.

* `record_paper` writes P6's `attempts.offered` and `attempts.struck` for test answers, so P6's dodged
  and caught counts, and U6's habits, include tests.
* `qstate[qid].struck_ever` records every index ever struck.
* Report (S6): `You crossed out A and C, then chose D: added the exponents of y but left z alone.`
  and `You crossed out the right answer (B), then undid it.`
* X17's Eliminations row; the survivor trap (picked after striking others, and wrong) joins U6's habit
  list.

**Acceptance.** A test question where the key's index was struck and unstruck and the pick is wrong:
`qstate[qid].struck_ever` contains the key index, and after finish `attempts.struck` for that qid holds
the final strikes.

### E. Papers and sharing

#### X20. Twin papers: the same question types in the same slots for everyone, each with their own numbers

*From: experience paper-forms gap (with v2-decisions 1's reasoning), unfair-advantage shelf,
difficulty and card gaps, experience filter, status, card-stats and "Everyone" gaps, outcomes grid,
filter and retake gaps. Effort M. Builders: S5 (papers, stats, filters), F1 (`UI.scale` histogram,
`UI.filterBar` chips and counts).*

**Why.** Identical questions let answers be passed around, which inflates the percentile a paper
exists to give. That is why the Daily Challenge is twins (decision 1). A paper can do the same: the
same type, tier and format in every slot keeps Sat by, the rating and the percentile comparable, while
a discussion becomes about method, not "(C) is 12". Every retake is fresh too, which theirs can never
be.

**Data.**
* `papers.questions` holds **slots**, by section: `{sections:[{subject:'math', module1:[[template,
  tier, fmt]], module2_lower, module2_upper}]}`, never stems. A full-SAT paper later is two sections
  in the same shape.
* Papers #1–#7 take their slots from `server/mocks.json`'s stored `key`, `difficulty` and `type`.
* The weekly paper's slots come from one `blueprint.fill(order='shuffle')` on a Builder seeded
  `paper:{week}` (the template choice only).
* **Road-to papers.** When a Compete Season Final closes (Mon 12:00 UTC after its weekend), S5's
  Monday build also inserts a paper from it: `label 'Road to Oct 3'`, `source 'final-2026-10-03'`,
  `questions` = the Final's slot lists (it is twins per route, so they exist). Its crowd starts with
  the Final's ranked first sittings: they count as first sittings of the paper for Sat by, Average,
  the rating, the strip, the percentile and X21's board. The card carries the tag `Season Final ·
  412 sat it live` and the sub `The last full rehearsal before Oct 3, any time you like`. It is the
  anytime pre-exam paper: Up next offers it from the Final's close to the exam (§3.1 item 11).
* A paper sitting draws its own questions with `blueprint.twin_slots(slots, b)` (v2's `twin()` over
  slot triples, same fallback) at begin and at routing, stored in the sitting like any section.
* **Counts.** `Sat by` counts every learner's first finished sitting of the paper, in any
  conditions. Average, the rating, the strip, the percentile and per-slot aggregates use **first
  ranked sittings** (X1), at R16's one threshold, n ≥ 20.

**Rating: one model, P11's, for you from the first answer.** X20 adds no difficulty model and no tier
defaults. It sums P11's `ratings.odds(learner, template, tier)` (skill ratings against
`item_ratings`, which every clean first try anywhere on the site moves) over the paper's slots.
* **For you** (every viewer, day one): `expect_m1` = Σ odds over module 1's slots; `expect_m2` the
  same over the module 2 the viewer would reach (upper when `expect_m1 ≥ 14`). `typical_m1` = the
  median of `expect_m1` over the shelf's papers for this viewer. Chip:
  * `Harder for you · expect 14 of 22 in module 1 · 16 on most papers` when `expect_m1 ≤ typical_m1 −
    1`;
  * `Easier for you · expect 17 of 22 · 15 on most papers` when `≥ typical_m1 + 1`;
  * otherwise `About your level · expect 15 of 22`.
  A learner with no answers has default skill ratings, so papers still differ by how hard their types
  have been for everyone (item ratings), and the chip says `· from how hard its types have been`
  (`source:'types'`; `'you'` once the viewer has a skill rating with n ≥ 1).
  The tooltip names the paper's 3 hardest slots for you by topic, never by template.
* **For everyone.** Before 20 first ranked sittings: the same sum with every skill rating at the
  crowd median for that topic (1000 where fewer than 10 learners have one), against the shelf's
  median: `Everyone: harder than most · predicted from its types`. From 20: the mean share of weight
  earned by first ranked sittings against the shelf's mean (±0.05 is Typical): `Everyone: harder than
  most · measured from 34 sittings`. Both read the same `item_ratings`, so the predicted and the
  measured rating can't disagree by construction, only by evidence.

**Card.**
* The header, sub and tags as v2, with the two rating chips above (yours first, orange-free: ink on
  `--wash`).
* Stats: `Sat by 41 · 12 ranked` · `Average 590` (from 5 first sittings, labelled `· 7 sittings`;
  ranked-only from 20, labelled `· ranked`) · `You`. At 20 ranked, a 32px distribution strip of first
  ranked midpoints (`UI.scale` with `hist`) marks the average, your band and your target, and the
  percentile line shows.
* Line: `Has 3 of your open mistake types · 4 types you haven't met under the clock`.
* After you sit it: `Hardest: M2 harder Q19 · 18% right · you got it` (X21, from site-wide data
  until the paper has its own 20).
* Actions: Start / Resume / Retake (new numbers), Options, `Questions & discussion 12`, and `Race
  friends` (X22).

**Filters.**
* Difficulty: All / Harder for me / About my level / Easier for me (the "for you" chip; counts are
  per viewer, so they are never all zero once papers differ in types).
* Status: All / Not sat / In progress / Completed / `Misses to fix` (completed papers whose missed slots
  have open traps).
* **For me**: All / Has my open mistake types / Types I haven't met.
* Source: All / Weekly / Launch / Road to (Season Final papers).
* Sort: **Best for me** (the default once you have an estimate or open traps: unsat first, then 3 × the
  slots holding your open-trap templates + the slots you haven't met, ties newest) / Newest / Oldest /
  Hardest for me / Easiest for me (by `expect_m1`) / Hardest for everyone (the everyone rating) / Most
  sat.
* Every option shows its count (`Harder for me (3)`). Options with 0 are disabled but visible.
  Active filters also show as removable chips under the bar. T6's filter bar does the same.

**New test cards (T4).** Tiles: `You` (last), `Best`, `Adds` (`+1 section → High confidence`, or
`Keeps it High`), and `Everyone: 1,284 sittings` beside Adds (decision 4: a count that tells a student
the kind is well used stays). The percentile line (`Your last beats 62% of fresh sections`) shows at
n ≥ 20 ranked, R16's threshold, not 30.

**Acceptance.**
1. Two learners start and begin `{"kind":"paper","paper":1}`: slot by slot their module 1s have equal
   `(key, difficulty, type)`, and at least 20 of 22 seeds differ.
2. `SELECT questions FROM papers WHERE n=1` has `sections[0].subject == 'math'` and no `stem`.
3. A learner whose `linear_functions` skill rating is 300 below their other Algebra topics, and two
   papers where one has 5 more module 1 Algebra slots on linear functions at the same tiers: in `GET
   /api/tests`, that paper's `rating.you.expect_m1` is at least 1 lower than the other's. A learner
   with no answers gets `rating.you.source == 'types'`.
4. With fewer than 20 ranked first sittings, `rating.everyone.source == 'predicted'`; the code path
   reads `item_ratings` and has no tier-default constants.
5. A paper with 3 first sittings, 1 ranked: its card reads `Sat by 3 · 1 ranked`.
6. Selecting a filter option shows as many cards as its count said.
7. A Retake's seeds are all different from the learner's first sitting's; `Again, exactly` gives equal
   seeds and history marks it `exact`.
8. After a Season Final with 25 ranked sittings closes, the next Monday build adds a paper with
   `source` starting `final-`, and its card shows `Sat by 25` and a percentile line.

#### X21. Paper question boards: every slot with the crowd's result, the trap that caught most people, and your cheapest points

*From: experience #7, unfair-advantage #7, outcomes #9, and the discussion gaps of all three. Effort M.
Builders: S5 (`GET /api/papers/{n}/crowd`), F1 (`UI.spread`), F3 (`UI.review`), F5 (the inline twin,
R24).*

**Why.** Their comments are one flat, unmoderated thread per paper, full of spoilers and tied to no
question, with "People took N" as the only crowd number. Ours puts data first. Because every wrong
option names its misconception, the spread comes labelled, and it works across twins, since it
aggregates by slot and by misconception, not by letter.

**Sheet.** `Paper #8`, with tabs `Questions · Discussion 12`, both gated as v2's discussion: nothing is
sent before you've finished the paper.

**Two sources, always labelled.** A paper's slots are (template, tier, fmt) triples, and twin papers
share templates with the bank, so every slot has site-wide data from day one:
* **Site-wide** (`source:'site'`), while the paper has fewer than 20 first ranked sittings: from every
  clean first try (R8) on that (template, tier) in practice, tests and contests. `34% right on this type
  · 1,240 answers site-wide`, the median right time from timed contexts, and the spread of named
  wrong answers.
* **This paper** (`source:'paper'`), from 20 first ranked sittings (R16's threshold): `18% right · 214
  first sittings`.
* **Designed traps.** Below 5 answers from either source, a slot's trap line lists the misconceptions
  its options are built to catch, from the item's stored option reasons (the labels only, after
  hand-in): `Built to catch: added the exponents · forgot to halve c`. No crowd share is ever shown
  below n 5, so one other sitter's pick can't be read off the board.

**Questions tab.**
* Header `From 214 first sittings`, or `Site-wide data for each type until this paper has 20 first
  sittings · 12 so far` (your own rows always list).
* Top blocks: `Traps of this paper` (the 3 misconceptions with the largest share over the paper's
  slots, from whichever source each slot uses, each from n ≥ 5) and `Your cheapest points: 3 questions
  80% or more got right` (your misses and blanks whose slot's right share is 0.8 or more, from either
  source, each chip saying which).
* Sort: Hardest for everyone / Your misses / Where the crowd beat you / Where you beat the crowd / In
  order / Most discussed. Filter: Module, Source.
* **Row**: the `M1 Q17` chip, skill glyph and name, tier glyph; `18% right` with a bar, n and its
  source; your glyph; `Median right 1:50 · you 3:10`; the top trap `24% · added the exponents instead
  of multiplying` (n ≥ 5) or the designed traps; the post count and the top Helpful post's first 120
  characters.
* **Expanded**: `UI.spread` by misconception (grid-ins: the top 3 named wrong answers), n ≥ 5, and
  actions `Try one like this` (inline twin, R24), `Discuss` (Discussion with About set to that slot,
  the composer prefilled), `Open my review` (`/results/report/?id=MYSID&q=M1-17`).
* Module 2 slots not on your route form their own labelled group, `Not on your route`, listed in full.
* A slot with no data from either source reads `No answers on this type yet · built to catch: …`.

**Discussion ships on** (settles Part 5 question 7 for this section, §3.1 item 73): the v2 gate (you
must have finished the paper), report-to-hide at 3 reports, 20 posts a day, edit or delete for 15
minutes, and `tools/moderate.py` (list reported, hide, restore, mute a code). A post from a code with
no finished sitting of the paper is refused (403), which is the gate against minted codes. The owner
is named in Part 4: S5 builds and tests the tools; the site operator who reads `SATF_REPORTS_TO`
moderates, and I1's launch checklist is not done until that address is set and `tools/moderate.py
--pending` runs clean on the launch db.

**Server.** `GET /api/papers/{n}/crowd` → `{gated:true, count}` before a finished sitting, otherwise
`{subject, n_first, source, traps, cheapest, slots:[{slot:'m1:17', topic, tier, fmt, source:'paper'|
'site', n, right|null, median_right_ms, spread:[{norm, label, share}], designed:[label], spr_top,
posts, top_post}]}`. Paper data comes from the first ranked sittings' attempts (session, qid, norm,
ms); site data from `attempts` grouped by (template, tier), first tries only. Cached 10 minutes per
paper. Labels are the latest reason text for each norm. `right` is null only when both sources have
n 0; `spread` is `[]` below n 5.

**Acceptance.**
1. Before sitting: `gated:true` and no `slots` key. After: 44 or more slot rows.
2. With fewer than 20 first ranked sittings and a slot whose (template, tier) has 30 first tries
   site-wide: that slot has `source:'site'`, `n:30` and a numeric `right`.
3. A slot with 3 answers in total has `spread == []` and a non-empty `designed`.
4. Spread shares add up to at most 1. `cheapest` lists only your misses and blanks.
5. A learner code with no finished sitting of paper 8 → `POST /api/papers/8/posts` 403.

#### X22. Shares send twins, peers compared slot by slot, and a race with friends by invite code

*From: unfair-advantage #6 (twin shares), the share gaps of all three. Effort S (P22 and Compete's
private contests carry the mechanisms). Builders: F6 (`sets` `cfg.fresh`), S5 (the share sheet), S6
(peers), S8 (the contest from a sitting).*

**Why.** An exact share lets a friend copy answers, and their share exists only for QBank (and froze
the page). Friends who want to sit the same test together get nothing on theirs. Classes, homework
and teacher views are not built here (decision 5: a separate platform has them).

* **Share sheet** adds a seg `What they sit`: **Twins** (default): `The same kinds of question in the
  same order, with their own numbers. Answers can't be passed around, and you still compare question
  by question.` / **Exactly these questions**: `The same questions as yours.` Twins → `POST /api/sets
  {kind:'test', session, cfg:{slots, fresh:true}}` (P22's mechanism). The landing reads `Module 1 has
  the same question types in the same order as Ana's, with your own numbers.`
* **Peers** (S6), after both have finished: a slot grid, `Q7 · a line touching a parabola: you ✓ · Ana
  ✕ · she picked: forgot to halve c`. Only misconception labels, never a raw answer.
* **Race friends.** A second seg on the share sheet, `How: Any time (a link) · A race with a deadline`,
  and the quiet `Race friends` on each paper card and T4 section card. A race opens Compete's own
  Create a private contest sheet (§3.7 §7), preset: `from_session` (this finished sitting, or the
  paper's slots), 22 questions (module 1's slots), 35 minutes, twins on, open 3 days; Compete's Repeat
  turns it into a weekly series. Compete owns the rest: the invite code and its contest link
  (`/compete/contest/?code=…`, C18), who joined, the board, the due time and voiding. No roles, no
  homework, no class, no owner view: anyone with the code sits it. The share sheet shows the returned
  code and link with Copy, and `Races you made` links to Compete.

**Acceptance.** Two learners on one twin share get equal templates and tiers per slot with different
seeds; `GET /api/sets/{code}` has no stems; a finished pair's peers carry labels and no `given` key.
`Race friends` on a finished section → `POST /api/contests {from_session, count:22, minutes:35,
twin:true, open_for:72}` returns a code matching `^[A-HJ-NP-Z2-9]{6}$`; a second learner joining with it
gets module 1's templates and tiers slot by slot with different seeds. Nothing in `web/tests/` or
`web/test/` calls `/api/classes` or links to `/class/` or `/join/`.

#### X23. Catalog keys, and a paused test that follows you

*From: experience keyboard and resume gaps, experience #11 (X on a row). Effort S. Builders: F2
(`UI.keys` scope `tests`, U1), S5.*

* **Page scope `tests`**: `J` / `K` move through cards and rows (roving focus), `Enter` starts, or
  resumes a paused row, `O` Options, `D` Questions & discussion (papers), `X` Compare (rows), `F`
  focuses the first filter. All listed in `?`.
* **Resume everywhere.** U1's row 1 `resume` includes paused test sittings: `Paused · Full section #12
  · 21:40 left` (not urgent; a running clock stays urgent). Every page's Up next shows it.
* **Remind me tonight** on the Save and exit sheet: `UI.ics(event)` at `prefs.study_time` or 19:00,
  titled `Finish Full section #12 · 21:40 left`, with the lobby URL.

**Acceptance.** On `/tests/`, `J` focuses the first card; `Enter` on a paused row opens its lobby; `GET
/api/shell` for a learner with a paused test has `next.items[0].kind == 'resume'` and "Paused" in its
title; the downloaded `.ics` has a SUMMARY starting "Finish".

---

## 3. Spec overrides

### 3.1 Inside §3.4 (spec/rebuild-v2.md lines 4780–6054)

Each item quotes the spec, then gives the replacement.

**§3.4.3 Review changes and ground rules**

1. "The 7 fixed sections already in `server/mocks.json` become **Papers #1–#7**." → "The 7 fixed
   sections in `server/mocks.json` become the **slot lists** of Papers #1–#7: every sitter gets the
   same question type, tier and format in each slot, with their own numbers (X20)."
2. "The server builds **one new paper every Monday**, the way the daily challenge is built: once, from a
   seed, the same for everyone." → "… once, from a seed: the same slots for everyone, each sitter's own
   seeds, as the Daily Challenge's twins (decision 1)."
3. "**Access** (paid) has nothing to filter, so it is replaced by **New to you**, which counts the
   paper's questions you have already met." → "… replaced by **For me**: Has my open mistake types /
   Types I haven't met under the clock (X20)."
4. "It opens only after you've sat the paper. That prevents spoilers and keeps out drive-by chatter." →
   append: "Its first tab is the Questions board (X21)."
5. "**Behaviour is Bluebook's**, so test day holds no surprises:" → "**Behaviour is Bluebook's under
   Test-day conditions**, so test day holds no surprises. Training conditions add the aids of X3–X7
   (X1):"

**§1 runner shell table**

6. The `top-centre` test cell "clock `34:57` + Hide; progress strip under it (answered / unanswered /
   marked / current)" → append "; in Training the ahead/behind line (X3)". The `top-left` test cell "×
   Save and exit · title "Math · Module 1 of 2" · Directions ⌄" → append "· the Ranked / Training chip
   (X1)". The `top-right` test cell "Highlights & Notes · Calculator · Reference · More" → "Highlights &
   Notes · Scratch · Calculator · Reference · More". The `question header` test cell "`Q7` badge · Mark
   for review · (Sure/Unsure/Guess) · Eliminate · Report" → "`Q7` badge · Mark for review ·
   (Sure/Unsure/Guess, Training) · Save · Eliminate · Report".

**§2 `/tests/`**

7. The layout line "[sticky section nav]  New test 7 · Papers 8 · In progress 1 · Your sittings 12" →
   "[sticky section nav]  Habits 15 · New test 9 · Papers 8 · In progress 1 · Your sittings 12". Insert
   `┌ T3b Cycle (full width, when any) ┐` above T3 and `┌ T7 How you take tests (full width) ┐` after
   T2 (X16, X17).
8. §2.2 "**Routed up** **(extra)**: "4 of 6 sections". It tells a student how often module 1 earns the
   harder module 2, which is the gate to the 600s." → "**Gate**: "routed up 4 of 6", with the margin
   strip, the 580 line and Protect the gate (X14)."
9. §2.2 "**Confidence reason** (12.5px soft). It is one of:" → "**Confidence reason**, followed by the
   action that raises it as a `.btn` (X15). It is one of:"
10. §2.2 "Under the grid (meta): "Counted: 6 sittings · 4 sections, 1 module, 1 diagnostic". A sitting
    at the 200 floor still counts." → append "· 3 ranked". Then add, in order: Total (with R&W),
    projection and verdict, growth percentile, calibration, and "What moves this band" (X15).
11. §2.3 "What it recommends, in this order:" → the order becomes: 1 unfinished sitting (Resume); 2 a
    pressure check still open on a sitting finished in the last 24 h (X13); 3 Prove due (X16); 4 a plan
    test day (with T16's twin when the last same-kind sitting is 7 or more days old, and T13's dress
    rehearsal on its Saturday, both `Like test day`); 5 brand-new learner (diagnostic); 6 Compete's Season
    Final while it is open, then, from its close to the exam, its Road-to paper (X20); 7 a Trap test
    (X16's rule); 8 the Route-up trainer when 2 of the last 3
    sections routed lower (X14); 9 this week's paper; 10 otherwise, from X15's biggest cause (`Your points
    leak to time: sit Pacing practice`), else Full section.
12. §2.4 ""Paused · 21:40 left"" → append ", with "· won't rank" for a Test-day sitting (X1)".
13. §2.5 ""Everyone": "1,284 sittings". Once there are 30 or more scored sittings of that kind, a second
    line appears: "Your last beats 62% of fresh sections"." → "The "Everyone" tile stays, and "Adds":
    "+1 section → High confidence" (or "Keeps it High") joins it. The percentile line "Your last beats
    62% of fresh sections" shows at 20 or more ranked sittings of that kind, R16's threshold (X20)."
14. §2.5 "The cards, in order:" → add **8. Route-up trainer** and **9. Trap test** (X14, X16). Card 3
    (Module 2 · harder) adds the gauntlet goal and pips (X14).
15. §2.6 helper "The same questions for everyone who sits them, so your score compares directly. A new
    paper every Monday." → "The same question types in the same order for everyone, each with their own
    numbers, so scores compare and answers can't be passed around. A new paper every Monday."
16. §2.6 "**Difficulty:** All / Easier than most / Typical / Harder than most / Not rated yet. The rating
    is measured from everyone's first standard sittings, once a paper has at least 20." → "**Difficulty:**
    All / Harder for me / About my level / Easier for me, from P11's odds for the viewer over the paper's
    slots, from the first answer. Everyone's rating is a second chip: predicted from P11's item ratings,
    measured from 20 first ranked sittings (X20). **Source:** All / Weekly / Launch / Road to."
17. §2.6 "**New to you:** All / Mostly new to me (90% or more of its questions unseen)." → "**For me:** All
    / Has my open mistake types / Types I haven't met under the clock."
18. §2.6 "**Status:** All / Not sat / In progress / Completed." → append "/ Misses to fix". "**Sort:**
    Newest / Oldest / Hardest / Easiest / Most sat." → "**Sort:** Best for me (default once there is an
    estimate or open traps) / Newest / Oldest / Hardest for me / Easiest for me / Hardest for everyone /
    Most sat." Add: every option shows its
    count, zero options are disabled but visible, and active filters show as removable chips (X20).
19. §2.6 "**Line (meta):** "New to you: 63 of 66", plus, once you've sat it and it has at least 30 first
    sittings, "· your first sitting beats 62%"." → "**Line (meta):** "Has 3 of your open mistake types · 4
    types you haven't met under the clock", plus the percentile and the distribution strip at 20 first
    ranked sittings, and after sitting "Hardest: M2 harder Q19 · 18% right · you got it" (X20, X21)."
    The stat tiles: "Sat by 41 · 12 ranked" over every first sitting, Average from 5 first sittings
    (ranked-only from 20), You.
20. §2.6 "Quiet "Discussion 12"." → "Quiet "Questions & discussion 12"." The gated suffix stays.
21. §2.6 "**Retakes:** allowed at any time." → append "A retake gets new numbers on the same slots. A
    quiet "Again, exactly · tests memory" re-serves your first sitting's items (X18)."
22. §2.7 "**Header:** "Discussion · Paper #8" with the count, and ×." → "**Header:** "Paper #8", tabs
    "Questions · Discussion 12", and ×. The Questions tab is X21." And ""Sit Paper #8 first. The
    discussion talks about its answers."" → ""Sit Paper #8 first. The questions and discussion talk about
    its traps.""
23. §2.8 "**Kind:** All / Full sections / Papers / Modules / Custom / Diagnostics / Twins / Shared." →
    append "/ Trap tests / Trainer". "**Status:** All / Completed / In progress / Timed out." → append "/
    Pressure losses". Add "**Conditions:** All / Test-day / Training" (X1). The score chips add "Unranked
    · paused once" (or "· break 12:40"), "offline 3:10" (never unranking), the gate margin, "Pressure 3 · Knowledge 3" and "2nd pass +20". Line 2 of a row starts
    with the Compare checkbox (X18).
24. §2.9 ""Anyone with the link sits these exact questions. They see no answers until they finish, and
    you'll see how they did."" → ""Anyone with the link sits the same question types in the same order
    with their own numbers (or these exact questions, if you chose that). They see no answers until they
    finish, and you'll see how they did."", with the `What they sit` seg above it (X22).
25. §2.9 ""Module 1 is the same as Ana's. Module 2 matches hers when you earn the same route."" →
    ""Module 1 has the same question types in the same order as Ana's, with your own numbers. Module 2
    matches hers when you earn the same route.""
26. §2.10 "- That floor-score sittings count." → append bullets: Test-day and Training, and what makes a
    sitting rank (X1); the route diagram (X14); pressure checks never change a band (X13); removed
    questions (X10); calibration status (X15).

**§3 The start sheet**

27. "a stepper of 4 segments (4px bars, amber when done or current) with labels under them: Test ·
    Modules · Timing · Tools." → "… labels: Test · Modules · Conditions · Tools", with the presets row and
    the recommended chip above step 1 (X1).
28. Step 1 list: add "Trap test" and "Route-up trainer" (X14, X16).
29. Step 2 Choose modules: ""Module 1 · 22 questions · 35 min · mixed"" → append to each card its last
    result and what it yields (X1). Each Module 2 and Module 1 option gets its "Trains:" line.
30. Custom test "**Difficulty:** Easy / Medium / Hard toggles, at least one." → append "or **For me**
    (P11's zone per skill)".
31. "**Step 3 · Timing**" → "**Step 3 · Conditions and timing**": the Test-day · Training seg first,
    then the timing cards, adding "**Tight clock (−15%) · Training:** "29:45 a module"" (X1).
32. "**Step 4 · Tools** (defaults shown)" list → two groups. Both conditions: Fullscreen, Calculator,
    "Ask which I missed" (on, X11), Save these as my defaults. **Training aids**: Pace guide (on), Coaching
    nudges (on), Confidence tags (off), Cover the choices (off), Tell me which module 2 I got (off), Your
    type notes (on), each disabled with "Training only" under Test-day.

**§4 The test window**

33. §4.2 settings rows: insert first "Conditions: "Test-day · this sitting ranks among first sittings" /
    "Training · keeps its score, doesn't rank"" with Change and the helper line (X1).
34. §4.2 "- "Every question is new to you". For a paper or shared test: "63 of its 66 questions are new to
    you"." → "- "Every question is new to you" (true for every kind now), then "What it holds: Algebra 8 ·
    …" and "9 question types you haven't met under the clock" (X2)."
35. §4.3 "It opens a confirm sheet: "Save and exit? The clock stops until you come back, and this test
    waits under In progress on Tests." with [Keep going] [Save and exit]." → Training keeps this;
    Test-day reads "Save and exit? The clock stops until you come back. This sitting keeps its score but
    won't rank." with [Keep going] [Pause and exit]; both add quiet "Remind me tonight" (X1, X23).
36. §4.3 "- Untimed: the clock counts up, with an "Elapsed" label (`k`) above it." → append "- Training
    with Pace guide: the ahead/behind line under the digits (X3)."
37. §4.3 "- **Pace tick (extra):** a 2×10px `--amber-deep` tick at the question you'd reach at the test's
    pace (elapsed ÷ (seconds per question × timing factor)). It shows when Pace guide is on and the test is
    timed" → "… at the question you should be on by X3's per-position budgets, plus checkpoint ticks after
    Q7 and Q14. It shows in Training with Pace guide on and the test timed".
38. §4.3 "**Confidence (when on) (extra):**" → "**Confidence (Training, when on) (extra):**". Add
    **Save** (bookmark plus "Save", `Z`) before Eliminate (X9). Under 760px Mark moves to the footer
    (X6).
39. §4.3 Grid-in "Enter moves to the next question." → append "In Training, the repeating-decimal warning
    (X4). On touch devices, the answer pad (X6)."
40. §4.3 "**Question note (extra):**" → add after it "**Scratch (extra):** the pen layer and typed scratch
    of X8, kept per question."
41. §4.4 "- **Filters** (`.choices`): All / Unanswered / For review / Guesses (shown when Confidence tags
    are on)." → append ". In Training, a Time view." and "- **Footer:** quiet "Go to review page →"." →
    "- **Footer:** the pill "Go through 8" and quiet "Go to review page →" (X5)."
42. §4.5 "- **Grid:** the navigator cells at 44px, 11 per row. A click goes to that question." → insert
    before it the queue chips and the "Go through N" pill, and in Training the Order control (X5).
    "- **Pacing line**, when timed (extra): "6:12 left · about 46 s for each unanswered question"." →
    "… "6:12 left · keep 3:00 for checking · about 46 s for each unanswered question" in Training (X3)."
43. §4.6 "- h1 "Module 1 is in"." → under Test-day, add under the h1 the countdown "Module 2 starts in
    0:48" with "Begin module 2 now"; at 0:00 module 2 begins by itself, and a break over 75 s unranks
    (X11). After the stat tiles add the prediction block (X11), and in Training (no countdown) the module
    1 pace trace (X3) and, with "Tell me my module 2" on, the gate margin (X14).
44. §4.7 "- **Handing in:** the column shows "Marking your test…" with the bar skeleton, then redirects to
    `/results/report/?id=ID`. A diagnostic goes to signup, as today." → "- **Handing in:** the prediction
    sheet (X11), then "Marking your test…", then the hand-in moment `#done` (X12), which offers the
    pressure check (X13) before the report. A diagnostic shows no band: pressure check, then sign-up
    (R38)."
45. §4.8 "- **Reference:** the existing `UI.ref`." → "- **Reference:** `UI.ref`, a tab of the 300px
    right-hand slot (with Notes and Entering your answer) at ≥1180px, with search, and counted per
    question (X9)." The calculator's dock and the notes and grid-in rails follow X9's one layout rule:
    calculator left (320–560px), one right slot, a 560–700px column, the later panel floats when both
    can't fit.
46. §4.8 the Highlights styles list: the first three are labelled "Asked for" (box), "Given" (highlight)
    and "Ignore" (strike), and placed first on the toolbar (X9).
47. §4.8 More items "- Pace guide [toggle]" and "- Confidence tags [toggle]" → shown only in Training.
    Add "- Scratch" and "- Use the answer pad [toggle]" (touch devices).
48. §4.8 Report "- In a timed test, a footer note: "The clock keeps running."" → "- In a live test, the
    first row is "Remind me after the test" (one tap), then the category chips with "The clock keeps
    running" (X10)."
49. §4.10 table: add rows `U` next unanswered · `Shift+M` next marked · `Z` save · `Shift+L` scratch ·
    `V` cover the choices (Training). Add under the table: "In exam mode `D` only chooses D (Details
    isn't offered during a test) and `B` only chooses B (Save is `Z`)."
50. §4.12 "- **Footer:** [‹ 44px Back icon] [the "M1 · 7 of 22 ⌃" button] [Next pill, 44px tall]." →
    "- **Footer:** [‹ Back 44] [Mark 44] [M1 · 7 of 22 ⌃] [Next pill]. Swipe the column for Back and Next;
    long-press an option to strike it while no text tool is on; the answer pad on grid-ins (X6)." And "- **Question header:**
    `Q7`, Mark (icon plus "Mark"), …" → drop Mark from the phone header.

**§5 Flows**

51. After "11. **Shared.**" add: "12. **Pressure check.** `#done` → `POST /api/drill {pressure: sid}` →
    the practice session in end mode → finish → `api_tests.on_drill_finish` → `/results/report/?id=SID#pressure`.
    13. **Compare.** Two checkboxes → `GET /api/session/{a}/compare?with={b}`. 14. **Questions board.**
    `GET /api/papers/{n}/crowd`. 15. **Trap test.** `POST /api/mock/new {kind:'custom',
    custom:{source:'traps', …}}`."

**§3.4.4 Extras**

52. "- **Papers that never run out: a new shared paper every Monday**:" → read with twin papers: "…
    Everyone gets the same question types in the same slots with their own numbers, so Sat by, Average,
    rank and discussion are fair and answers can't be passed around." Append X1–X23 as extras.

**§3.4.5 Server changes**

53. POST /api/mock/new body: add `conditions?: 'test_day'|'training'`, `trainer?: 'route'|'gauntlet'`,
    `timing` value `'x0.85'` (Training only; 422 otherwise), and `custom.source` value `'traps'` with
    `traps`, `neutral` (X1, X14, X16).
54. "New table papers (n INTEGER PRIMARY KEY, week TEXT UNIQUE, label TEXT, built TEXT, questions TEXT
    {module1, module2_lower, module2_upper})." → "… source TEXT ('launch', 'weekly' or a Season Final's
    contest id), questions TEXT holding `{sections:[{subject, module1, module2_lower, module2_upper}]}`
    with slot lists of [template, tier, fmt]." And "A paper sitting is sessions.kind='mock',
    mock_id='P{n}'. mock_module() reads 'P…' from the papers table (lru-cached) the way it reads the MOCKS
    shelf today." → "A paper sitting is sessions.kind='mock', cfg.paper = n. Its modules are drawn with
    `blueprint.twin_slots` at begin and at routing and stored in the sitting, like any section."
55. Stats: "- first sittings = each learner's earliest finished, non-abandoned sitting of that paper at
    official timing, adaptive, with the whole paper;" → "- sat_by = learners with a finished sitting of
    the paper (any conditions), with ranked_n beside it; first sittings (for average, rating, strip,
    percentile and the board) = each learner's earliest finished, ranked (X1) sitting of that paper, plus,
    for a Road-to paper, the Season Final's ranked sittings;". "- new_to_you = 66 − |paper items ∩ practice_seen|." →
    "- types_new = slot templates the learner hasn't met under the clock; open_traps = slots whose
    template has an open trap of this learner; predicted and measured ratings (X20)."
56. "- **Per-question state (POST /api/session/{sid}/state)**" body: add `predict?: 'miss'|null` (accepted
    for handed-in modules until 15 min after the final finish), `scratch?` (≤20 KB), `calc?: {open_ms,
    exprs}`, `ref_n?`, `ref_ms?`, `covered?`, `reveal_ms?`, `own?`, `report_later?`, `struck_ever` (kept
    by the server from `struck`), and `_session` keys `end_at`, `nudges`, `keys_seen`, `offline_ms`, `pids {pid: {first_el, last_el,
    hid, off}}`. Every call (this one, `/answer`, `/begin`, `/finish`) carries X1's stamps `pid, el, hid,
    off`. qstate is capped at 256 KB a sitting.
57. "- **Module hand-in (POST /api/session/{sid}/finish)**" → the final finish also stores `ranked`,
    `unranked_why` (X1, measured from stamps), `result.between` (X11), `result.gate` (X14), `result.pass2` (X5), `result.new_types` (X2),
    `result.removed` (X10), and returns `done` (X12).
58. "Both are excluded from Combined, paper stats and every percentile." → "Every unranked sitting (X1),
    these included, is excluded from Combined, paper stats and every percentile."
59. Durations "multiplied by 1.5 or 2 for extended timing." → "multiplied by 1.5 or 2 for extended
    timing, or 0.85 for Tight clock."
60. "- **Session payload additions (GET /api/session/{sid})**" → add `subject`, `conditions`, `ranked`
    (live state), `holds` (X2), and in Training only `pace` (X3), `odds` (X5) and `type_note` per qid
    (X9). "modules (1 or 2)" → "modules: a list of `{subject, n, questions}`, one per module of the
    sitting" (decision 3).
61. "- **Tests overview (GET /api/tests)**" → add `levers`, `total`, `projection`, `growth`,
    `calibration` (X15), `habits` (X17), `cycle` (X16), `gate` (X14), `types_met` (X2), and in `kinds`
    rows for `trainer` and `traps` with `streak` and `ready`.
62. After Discussion: add "`GET /api/papers/{n}/crowd`, gated like posts, cached 10 minutes, each slot
    from this paper's first ranked sittings at n ≥ 20 and from site-wide first tries on its (template,
    tier) before that, no share below n 5 (X21)."
63. test_flow checks: "two learners get identical module 1 stems on P1" → "two learners get equal
    (template, difficulty, type) slot by slot on P1, with different seeds". Add: X1 ranked and unranked
    reasons, including a flushed offline queue that stays ranked and a closed page that doesn't; X11 a
    10-minute break between modules unranks; X3 budget sums; X11 predict after hand-in; X13 pressure build and classify; X14 gate; X16
    trap slots offer their norms; X10 removal.

**§3.4.7 Shared needs**

64. Add: `UI.spark` and `UI.scale` `hist` (F1); `UI.pad`, `UI.scratch`, `UI.ref` dock mode, the
    `UI.runner` left dock and tabbed right slot with X9's fitting rule, `UI.calc` engine `scientific`
    (item 74), `UI.navigator` queue mode, `UI.checkYourWork` chips and order (F3); `UI.report`
    `ctx.live` (F6).

**§3.4.8 Acceptance checks**

65. #14 "Two learners starting {"kind":"paper","paper":1} and beginning get identical module 1 stems." →
    "… get module 1s whose (template, difficulty, type) are equal slot by slot, with different seeds."
66. #17 "{"kind":"shared","shared":code} gives a module 1 whose template and seed equal the source's,
    slot by slot." → "A twin share gives a module 1 whose template and difficulty equal the source's slot
    by slot with different seeds; an exact share (`cfg.fresh:false`) gives equal template and seed."
67. #23 "the lobby shows 'Enter fullscreen and begin', 'Begin without fullscreen' and a Change link on
    Timing." → append "and the Conditions row with its rank line".

**§3.4.9 Open questions**

68. "Save and exit pauses the clock on a timed sitting, and the number of pauses is shown on the report
    and flagged. Is pausing acceptable, …" → settled by X1: pausing is always allowed; under Test-day it
    keeps the score, drops the rank, and says so before it happens.
69. "When a Reading and Writing bank exists: 4 modules, a 10-minute break between sections, and the split
    pane. The shell keeps a passage-pane slot for it. Build that now, or leave it until the bank exists?"
    → settled by decision 3: `UI.runner` keeps an empty `passage` region and the payloads carry `subject`;
    nothing else is built until the bank exists.
70. "The weekly paper: Monday 00:00 UTC is proposed. Should its first week double as a 'this week' board
    …" → settled: papers stay percentile-only. Compete's Weekly Module is the ranked weekend event, and
    Up next shows Compete's Season Final as the dress rehearsal. When a Final closes it joins the shelf
    as a Road-to paper, the anytime rehearsal until the exam (X20).

**Added: subject-aware labels, and the two launch questions this section can't ship without**

71. §3.4.5 "section_label(): - mock → 'Math · Module {n} of 2'; - paper → 'Paper #{n} · Module {m} of
    2'; …" → "section_label() is derived from the payload's `modules` list: `{subject label} · Module
    {m} of {modules of that subject}` for a section, `Paper #{n} · {subject label} · Module {m} of {k}`
    for a paper, and the module, custom and diagnostic labels as v2 with the subject label first.
    Subject labels come from one map (`math` → `Math`, later `rw` → `Reading and Writing`)." Nothing
    in the runner or the report hard-codes `of 2`.
72. §2.8 Your sittings, Export CSV: "The columns are: number, date, kind, band, M1, M2, route, timing, minutes, misses, blanks and
    note." → "… band, then one column per module of the sittings shown, named from `modules`
    (`Math M1`, `Math M2`; later `R&W M1`, `R&W M2`), then route, conditions, ranked, timing, minutes,
    misses, blanks and note." The row grid on screen reads the same list.
73. §3.4.9 "Discussion on papers: … Launch it as specified, or keep it behind a flag until someone is
    assigned to moderate?" → settled for this section: it launches on, with the gate (a post needs a
    finished sitting of that paper, which is the defence against minted codes), report-to-hide at 3,
    20 posts a day and `tools/moderate.py`. S5 owns the tools; the site operator who reads
    `SATF_REPORTS_TO` moderates; I1's launch checklist holds it (§3.2 row "Part 4"). The Questions
    tab needs no moderation and is never empty (X21), so the sheet is useful even on a quiet day.
74. §3.4.9 "Desmos: the key is the public trial key (DESMOS_KEY in ui.js and test.js). A production key
    is needed before launch." → settled as a **launch blocker with a fallback**:
    * One constant, `UI.DESMOS_KEY` in `ui.js` (test.js reads it, no second copy).
    * The operator requests the production key; I1 cannot close while the constant is the trial key,
      unless the fallback below is switched on by setting it to `''`.
    * **Fallback** (F3, built either way): `UI.calc` falls back to engine `scientific` when the key is
      empty, the Desmos script fails to load, or `window.Desmos` is missing 8 s after the calculator is
      first opened. It fills the same dock, float and phone sheet: digits, + − × ÷, ( ), ^, √, x², 1/x,
      π, e, sin cos tan and their inverses with a Deg/Rad toggle, `ans`, and a history of lines that
      can be copied; typed input works. A shunting-yard evaluator in `runner.js` (about 150 lines, no
      `eval`, a `__test` table). X8 logs its lines as `calc.exprs`. P3's Desmos way hides with `Needs
      the graphing calculator`. The lobby's Calculator row reads `Calculator: scientific · the graphing
      calculator is unavailable`. The no-calculator mode stays.
    * Acceptance: with `UI.DESMOS_KEY = ''`, `G` opens the dock with the scientific engine; typing
      `2^10` Enter shows 1024 and `sin(30)` in Deg shows 0.5; no console error; the runner never
      shows an empty dock.

### 3.2 Outside the section (Part 2 and sibling lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| R7 | `qstate` per qid adds `predict, scratch, calc, ref_n, ref_ms, covered, reveal_ms, own, pass, struck_ever`; `_session` adds `end_at, nudges, report_later, keys_seen, offline_ms, pids`. Every runner call carries the client stamps `pid, el, hid, off`, and away, breaks and offline time are measured from them, never from arrival gaps (no `last_ping`). Cap 256 KB a sitting, 20 KB of scratch a question | X1, X3–X11 |
| R8 / P3 / P6 | `record_paper` writes `attempts.calc`, `offered` and `struck` for test answers | X8, X19 |
| R9 | A Knowledge verdict (X13) and a silent miss (X11) sort that trap first in Fix and Review, like a sure miss. Trap-test answers are check-ins (clean → `checks + 1`, trap taken → Relapsed) | X11, X13, X16 |
| R10 / §2.6 | Body field `pressure: sid`, resolved by `api_tests.resolve_drill(learner, body)` through the registry beside `like`, `word`, `confusion` (no `assignment`: decision 5). Sources `pressure`, `gate`, `fix` | X13, X14, X16 |
| R16 | `ranked = 1` replaces "standard" for Combined, paper stats and every percentile. R16's n ≥ 20 is the only crowd threshold in Tests (§3.4's 30s go). Adds `estimate.growth` and `estimate.calibration`. `estimate.rescore` (T16) prices levers, pressure ceilings and the cycle | X1, X13, X15, X16, X20 |
| P11 (practice.md) | `ratings.odds` is also read per paper slot for the "for you" rating, and at crowd-median skill ratings for "everyone"; no second difficulty model | X20 |
| R17 / U3 | `UI.report` `ctx.live` puts "Remind me after the test" first. A report resolved `wrong key` or `no right answer`, or a quarantined template, removes the position from that sitting's score | X10 |
| R18(c) / P22 | Test sets default to `cfg:{slots, fresh:true}`; `exact` is the option | X22 |
| R24 | Source `pressure` joins the inline list | X13 |
| §2.4 | F1: `UI.spark(host, series)`, `UI.scale` option `hist`. F3: `UI.pad`, `UI.scratch(host, {editable, strokes})`, `UI.ref` mode `dock`, the `UI.runner` left dock and tabbed right slot with X9's fitting rule (column 560–700px), `UI.calc` engine `scientific`, `UI.navigator` queue mode, `UI.checkYourWork` chips and order, the save queue's `pid, el, hid, off` stamps. F6: `UI.report` `ctx.live` | X1, X5, X6, X8, X9, X10, X17, X20 |
| §2.5 | No new tables. `sessions.subject TEXT NOT NULL DEFAULT 'math'`. `papers.source TEXT` ('launch', 'weekly', a Final's contest id); `papers.questions` is `{sections:[{subject, module1, module2_lower, module2_upper}]}` of slot lists. `sessions.ranked` and `unranked_why` are used for tests too | X1, X20, decision 3 |
| §2.7 | Keys `test_conditions` (test_day \| training, default test_day), `test_nudges` (true), `test_cover` (false), `test_predict` (true), `test_type_notes` (true, Training only); `test_timing` adds `x0.85` (Training only). `test_pace` acts only in Training | X1, X3, X4, X7, X9, X11 |
| §2.8 | Runner, both modes: practice.md's row already moves Save from `B` to `Z` and Details from `D` to `X`, one save key everywhere; the test window uses the same map, so in exam mode `A–D` only choose (`B` would otherwise both choose and save) and `X` is unused (no Details during a test). Tests adds `U` next unanswered, `Shift+M` next marked, `Shift+L` scratch, `V` cover in Training. In exam mode `D` only chooses (fixes the D clash in the runner row). Page scope `tests`: `J K Enter O D X F` | X5, X8, X9, X23 |
| §2.9 | Providers: S5 `api_tests.resolve_drill`, `on_drill_finish`, `habits`, `pace_plan`, `GET /api/papers/{n}/crowd` → F5, S6, S3; F4 `estimate.growth`, `estimate.calibration`, `progress.types_met` → S5, S1; S6 compare endpoint (any two sittings) → S5, S3 | X2, X13, X15, X17, X18, X21 |
| §2.10 | `drill.finish` calls `api_tests.on_drill_finish(row)` when `cfg.pressure_of` is set | X13 |
| today.md T7 | `progress.causes` adds cause `changed` (on tests: `qstate.first` was the key and the final answer is wrong), checked before `trap`. For questions with a pressure verdict, the verdict decides: knowledge → trap, shaky → gap, speed → clock, pressure → slip | X13, X15 |
| today.md T9 | Blind spots also include test misses that weren't predicted (X11) when the student made predictions in that sitting | X11 |
| today.md T16 | "Retake as twin" and Tests' Twin are one build (`{kind:'twin', twin_of}`); the compare endpoint serves any two own sittings | X18 |
| shell-me U1 | Row 1 `resume` includes paused test sittings (not urgent). A `prove` row for a due Prove (X16) | X16, X23 |
| §3.5 Report | `POST /api/mock/new {like: sid, full}` is an alias of `{kind:'twin', twin_of: sid}`. The report renders `result.pressure`, `predicted`, `gate`, `removed`, `pass2`, `new_types`, `between`, the offline line (`offline 3:10 · doesn't affect your rank`), type notes beside their questions, Your working, the elimination lines, cover lines, and per-slot crowd bars for papers; its first question-review GET sets `qstate._session.keys_seen` | X2, X5, X7, X8, X10–X14, X19, X21 |
| §3.7 Compete | The Season Final is the dress rehearsal Tests' Up next shows while it is open. When it closes, S5 reads its slot lists from `contests.spec` and adds a Road-to paper whose crowd starts with the Final's ranked sittings. `POST /api/contests` accepts `from_session` (a finished sitting of the owner) or `paper` (n): module 1's slots as twins, count 22, minutes 35; the invite code, board and results stay Compete's. The weekly paper and the Weekly Module stay two events: an anytime shared form, and a weekend contest. No groups or classes (decision 5) | X16 (Up next), X20, X22, §3.1 item 70 |
| §3.6 Plan | A Prove task on its due day (optional); T13's rehearsal and plan test days start `Like test day` | X1, X16 |
| Part 4 (I1, F3, S5) | Launch blockers with owners: the production Desmos key (the operator requests it; F3 ships the scientific fallback either way; I1 does not close on the trial key, §3.1 item 74), and Discussion's moderator (the operator reading `SATF_REPORTS_TO`; S5 ships `tools/moderate.py`; I1 does not close until that address is set, §3.1 item 73). Settles Part 5 questions 7 (for Discussion) and 15 | X21, X8 |
| Shell §7 Classes (S2) | Removed by decision 5. Nothing in Tests assigns, lists a class or links to `/class/` or `/join/` | X22 |

---

## 4. Rejected

* **30 papers at launch** (unfair-advantage shelf gap): a paper's only edge over a fresh section is its
  crowd, and 30 papers split a small crowd 30 ways, so every card would read "Not rated" and every board
  would be empty. Twin papers, ratings for the viewer from the first answer, site-wide boards, Road-to
  papers from each Season Final and unlimited fresh sections answer the shelf.
* **Pre-building the next 4 weeks of papers** (same gap): a twin paper is a slot list, one `fill` of
  about 0.2 s, so a cold build is invisible.
* **"From practice: 570–650" and "Predicted for you: 540–620" on paper cards** (unfair-advantage #2 and
  difficulty gap): U4 and T10 never show the practice model as a score, and today.md rejected the same
  line. The practice delta and the projection cover it.
* **A Monte Carlo slot model for skill gains** (unfair-advantage #2): a second score model beside U4's
  `estimate.gains` (today.md rejected the same).
* **A separate "Skip for now / Later" state** (outcomes #3): unanswered plus Mark already say it, the
  queue orders them (X5), pass 2 is measured without it, and Bluebook has only Mark.
* **"Predict your score" in the lobby** (outcomes #6): a novelty. Per-question predictions (X11) give
  calibration that can be acted on.
* **A per-student "adjusted" band from one Bluebook pair** (outcomes #10): one pair sits inside the ±70
  noise. The comparison line and the global refit cover it.
* **An automatic nightly refit of `scoring.ANCHORS`** (outcomes #10): a scoring change needs a person.
  The tool proposes; someone commits.
* **"Tightening pace" from 1.25x down to official** (unfair-advantage timing gap): one more mode. Tight
  clock, extended timings and U15's stages cover the progression.
* **An Even / Front-loaded / Mine pace choice** (outcomes #4, experience #5): even pace is wrong advice
  on a module that runs easy to hard. One pace line, personal when the data allows (X3).
* **A "Coached" flag separate from the conditions** (unfair-advantage #4): Training is that flag (X1).
* **Pencil-and-paper tests with a bubble sheet and proctor clock** (unfair-advantage #9): the digital
  SAT is taken on screen, Review's worksheet already prints any set, and classrooms belong to the
  separate classes platform (decision 5).
* **A Calculator-first module card** (outcomes #7): it is a practice set, not a test. P3's builder filter
  "Has a Desmos way" builds it.
* **A 10-card formula recall set after tests** (outcomes reference gap): P24's "Not on the sheet: know
  it" covers formulas, and a flashcard deck is Words' job, which is EBRW only (decision 2).
* **Exam-date cohort percentiles** (unfair-advantage percentile gap): Compete owns the exam scope (R3),
  and a cohort of one exam date splits a small crowd again. The exam-week rehearsal paper is built
  (experience prediction-papers gap): each closed Season Final joins the shelf as a Road-to paper (X20),
  and T13 schedules the Final itself.
* **A pinned rationale as each question thread's first post** (experience discussion gap): with twin
  papers each sitter has their own numbers. "Open my review" shows their own rationale.
* **An "Another way to solve it" post type** (same gap): Helpful sorting and the top post on each
  question row do it without a second post type.
* **Choosing warning points (10 / 5 / 1 minutes)** (experience clock gap): Bluebook's 5:00 and the 1:00
  pulse stay, and X3's checkpoints warn earlier in Training.
* **A pace dot on a hidden clock** (same gap): hiding the clock is the student's choice not to see time.
* **An adaptive diagnostic with follow-up questions** (outcomes diagnostic gap): the scoring heuristic
  assumes a fixed form. The pressure check (X13) confirms misconceptions from the first sitting instead.
* **Showing the diagnostic result without the sign-up gate** (unfair-advantage diagnostic gap): open
  question 8 awaits the user, so R38 holds.
* **A hard-questions-by-skill table on the gauntlet card** (unfair-advantage #5): the report's skill
  panel already shows it per sitting.
* **A band chart per twin chain** (unfair-advantage #6): the sittings chart and the compare sheet (X18)
  cover it.
* **A separate "Question types met" sheet on Tests** (unfair-advantage #8): U8's atlas in Me is that
  sheet; Tests links to it.
* **"All of it: 560–700 → 650–760"** (outcomes #1): flipping every miss is a perfect score, which says
  nothing. The sum line prices the fixable causes instead.
* **Collapsing habits rows to 4 behind "Show all"** (experience #3): decision 4. All rows show.
* **"Assign to a class" on cards, class twins and class grids** (the earlier X22): decision 5 removes
  classes, homework and assignments. Friends race through X22's share or a Compete invite code.
* **Tier defaults for a paper's crowd rating** (the earlier X20: easy 0.80, medium 0.60, hard 0.35):
  a second difficulty model beside P11 that rated every launch paper "Typical". X20 reads P11's odds.
* **Exposure-first templates in ranked sittings** (the earlier X2): it served each student their
  least-met types on the sittings that rank, pushing their estimate and percentile below test day.
  Exposure-first is Training's; Test-day draws a seeded shuffle.
* **A gap between state saves as "away"** (the earlier X1): a Wi-Fi drop looked like leaving the
  window. Away is `document.hidden` time and closed-page time from the client's stamps.
* **`B` as Save in the runner** (the earlier X9 and §3.1 item 49): `B` chooses option B. Save is
  `Z`, practice.md's one save key; scratch is `Shift+L`, since `X` is Details there.
