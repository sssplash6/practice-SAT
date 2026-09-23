# v2 upgrades: Practice, the builder and the session

Written 2026-09-23 for `spec/rebuild-v2.md` §3.3 (lines 3348–4779). It merges the three designers'
proposals in `spec/v2-upgrades/_proposals/practice.json` (outcomes, experience, unfair
advantage; cited below as "outcomes #1" and so on) into one build-ready list, P1–P25. The
TopTierPrep inventory is §3.3.1, checked against `spec/toptierprep-teardown.md`,
`ttp-notes.md` and the live walk in `ttp-live.md`.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.3 where
  they differ, and §3 lists every change. Part 2 resolutions (R1–R38) still hold, except the
  lines named in §3.2 "Outside the section".
* **Siblings.** `spec/v2-upgrades/shell-me.md` (U1–U28) and `spec/v2-upgrades/today.md`
  (T1–T20) are already written. Where they specify something Practice needs, the upgrade here
  names it and does not specify it again. Where a proposal would have built a second version
  of a sibling's model, this file uses the sibling's model:
  * spaced returns are T3's `progress.warmup_candidates` (no second schedule, no new table);
  * the cause of a miss is T7's `progress.causes` (no second taxonomy);
  * the Learn session is T4's body (`source:'learn', example:true`);
  * type readiness words are U8's (unmet · met · ready);
  * points are U4's `estimate.gains`, habits U6's families, pace U7's `progress.pace`;
  * key disputes are U3's instant check, and question links U28's twin.
* **The bar.** A student who uses TopTierPrep's Question Bank today opens ours and wants to
  switch, because each question teaches more, each set is aimed better, and the loop is
  faster. Parity is failure.
* **Names.** Upgrades are P1–P25. Builders are Part 4's tasks (F1–F6, S1–S10, T-bank). Every
  new server function has one owner.
* **Subject-aware.** Per v2-decisions item 3, new payloads that describe a section
  (`/api/bank`, points, budgets, the route check, look-alikes) carry `subject` (`math` now), so
  a second subject is additive. Concretely, and cheap now:
  * `blueprint.SECTION[subject] = {questions, module_seconds, tiers}` (Math: 44, 2,100,
    `TIERS`). Every "of 44" in this file prints `SECTION[subject].questions`, never a literal.
  * Tier budgets are keyed by subject and derived from that subject's `module_seconds`, its
    module-1 question count and tier mix, with the ratios 0.68 / 1.0 / 1.32 (Math: 65 / 95 /
    126 s). `budget_ms(template, tier)` reads the template's subject, and a set's pace comes from
    its own subject, never a literal 95.
  * `POST /api/drill`, `/preview` and the set's state carry `subject` (default `math`); so do
    the §1.10 deep links (`subject=math`) and `UI.parseSet`'s body.
  * Builder prefs live per subject: `prefs.practice[subject] = {zone, review_mix, review_from,
    final_round, cover, two_passes, hints, worked_first, words_mix, presets, …}`. Only keys that
    describe the student rather than the subject stay flat (`confidence`, `type_rules`, `keys`).
    U15's bundles write into `prefs.practice.math`.
  * Acceptance: `GET /api/drill/{id}` carries `subject: 'math'`; `PUT /api/me
    {prefs:{practice:{math:{zone:'warm'}}}}` round-trips through `GET /api/me`, and a flat
    `prefs.zone` is read once at startup and moved there.
* **Facts measured for this file** (current bank and db, 2026-09-23):
  * 386 templates. Rationales: median 21 words, at most 57. TopTierPrep's report explanation
    is a Justification paragraph plus one line per wrong option, so our explanation is
    **thinner** today.
  * Of sampled distractors, 2,801 carry a named reason and 10 are fillers (99.6% named).
  * In an 18-seed survey, 153 templates emit grid-ins (116 emit both formats) and 59 emit more
    than one tier. 181 templates take `fmt`.
  * Of 1,356 surveyed grid-in items, 675 (50%, on 87 of the 153 grid-in templates) have an MC
    version of the same seed with the same key and params, carrying 2,025 named wrong values.
  * With same-skill-label siblings at the adjacent tier, 156 of 386 types can offer an easier
    or a harder question (59 today).
  * Template kwargs: `wrongs` 195, `fmt` 181, `ask` 85, `ctx` 81, `mode` 43. Re-generating a
    seed with another `ask` keeps the setup on 29 templates today. Only 10 templates record
    two or more contexts in 18 seeds.
  * 412 of 937 sampled MC items (44%, on 172 templates) have four plain-number options.
    `satbank.expr.agree` can compare expression options.
  * The db holds 287 attempts from 13 learners, 166 of them with `ms`. No (template, tier)
    has more than 12, so §3.3's measured levels (20+ first tries) would ship empty.
  * `material/keys` holds 1,039 official Math IDs with a tier each (easy / medium / hard) and
    no 1–7 score band. College Board's Question Bank listing shows, for every question, its ID,
    section, domain, skill, difficulty and score band (1–7), without opening the question.
  * Every template is pinned to official items in `satbank/topics/*/sources.py`, and many
    parameter spaces are small, so an unguarded fresh seed can land on an official item's
    exact numbers.
  * Templates by topic, for the Desmos floor (P3): systems 20, linear functions 23, linear
    equations in two variables 22, nonlinear functions 36, nonlinear equations and systems
    32, linear inequalities 18, two-variable data 18, circle equations
    (`circles.families.equation`) 6: 175 in all.
  * `scoring.ROUTE_UP_AT = 0.60`, `LOWER_ROUTE_CEILING = 580`. `blueprint.TIERS` is
    module 1 7 / 8 / 7, harder module 2 3 / 8 / 11, lower module 2 11 / 8 / 3.
    `MODULE_SECONDS` is 2,100.

---

## 1. Scorecard

"v2 spec" is §3.3 as written. The verdict says why ours is way better. Where v2 was at parity
or below, the verdict names the accepted upgrade that fixes it.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | One-screen builder | One screen, no page scroll; the skill list scrolls in its card; a fixed bar. 5 to 7 controls every visit | A scrolling page: presets with reasons, search, a skill tree with stats, 11 settings, Your sets, a fixed Action bar | A Ready row of Up next's first 3 sets plus "Again", each one tap. A command line ("circles hard 10 timed", Enter). Saved presets. Time boxes. Enter in the empty line starts Ready card 1 (P15) | v2 PARITY for speed: more capable, but slower for "10 hard circles". **P15 → WAY BETTER:** one tap or one line, with the full builder still below. |
| 2 | Bank toggle (QB \| TTP) | 1,921 College Board Math items in the app, filtered and tracked, plus 3,867 of their own | No toggle; a line on where questions come from; replicas left out | Every College Board Math ID resolves: 911 exactly onto templates, the rest by skill, tier and band from the listing index. Paste IDs (or a whole list) and get unlimited twins at the official tier, with the same traps where the map is exact. Each SkillRow links to College Board's bank at that skill with a "Paste what you missed there" field. "Built from 11 official questions" chips, an official-only filter, an "Official questions you brought" tab. No practice question ever copies an official one (P13) | v2 BELOW. **P13 → WAY BETTER:** official practice starts and ends in our builder, and every official miss becomes endless practice at its tier. Theirs gives each item once, with no twin. |
| 3 | Live "N questions" count | An inventory count that froze when a domain was unchecked | Live types and questions, "unlimited", ≈ minutes | "Covers ~21 of 44 questions on a Math section · works on ≈ +30 · ≈ 17 min for you" (P10, P16) | v2 PARITY: an inventory number. **P10 + P16 → WAY BETTER:** it says what the set is worth to this student and how long it takes them. |
| 4 | Subject toggle | English and Writing \| Math | Math only; the eyebrow says SAT MATH | A "Math · Reading & Writing" seg. R&W lists the 10 R&W skills, each linked to College Board's official bank at that skill; a Log it form keeps R&W misses (ID or text, skill, letter) for the EBRW bank and Review; the Words drills (EBRW words and transitions) with their counts. The builder, prefs, budgets and deep links are keyed by subject (P15, header) | **Still BELOW for R&W questions until the EBRW bank exists** (decisions 2 and 3). P15 removes the dead end: an R&W student practises official questions, logs misses and reviews words from here, and nothing has to be torn out when the bank ships. |
| 5 | Domain accordions | Check circle, name, count, chevron; no indeterminate state | Tri-state box, weight chip "35% · ~15 of 44", mastery bar and word, answered · first-try %, open mistakes, selected count | Adds "≈ +40 on the table" (P10), reviews due (P12) and "14 of 23 types ready" (P14) | **WAY BETTER already in v2.** The upgrades rank domains by what they are worth. |
| 6 | Skill checkboxes with counts | A checkbox and an item count ("Linear functions 170 / 408") | Full name, types, tiers, grid-in count, mastery, record, open mistakes, last practised, SkillPanel stats, 386 TypeRows, but a skill over 12 types collapsed behind "Show all" | Every TypeRow shown, under sticky skill-label sub-headers with counts and select-all. Adds Worth, fluent types, reviews due, odds per type, Desmos and official chips, a College Board link, a Map view and Finish this skill (P10–P14, P16) | **WAY BETTER** (the type layer they lack), now with nothing hidden (decision 4). The upgrades make each row a priced to-do. |
| 7 | Bluebook Include \| Exclude | Filters out items that also appear in Bluebook, so a student's tests stay unspoiled | A fixed lock line: "Never repeats" | Every pool rejects a card with an official item's pinned numbers or wording, so no practice question copies a College Board question, and the Repeats line says so. A pool "Fresh numbers on mistakes I logged from outside": Bluebook and College Board misses (by ID, text or a whole test, U2) become twins (P13) | v2 BELOW: nothing stopped a random seed landing on an official item. **P13 → WAY BETTER:** their protection holds in every pool, and Bluebook misses drive practice instead of being filtered out. |
| 8 | Difficulty multi-select | Easy / Medium / Hard pills | Tier toggles with type counts, plus Adaptive (off by default) | "Standard · For me". For me offers Warm-up, Stretch or Challenge, aimed by the student's own odds on each type, from ratings seeded by their score or a probe. Until a skill is placed (8 clean answers or Check my level) it serves the test's 7 / 8 / 7 mix, so nobody gets a run of Easy. Standard adds test-shaped mixes: "Like module 1 (7/8/7)" and "Like the harder module 2 (3/8/11)" (P11) | v2 PARITY. **P11 → WAY BETTER:** each question is aimed at this student's odds from day one without a cold-start trap, and a 700-seeker can practise the tier mix of the module that decides their ceiling. |
| 9 | Question Score 1–7 | A dual-thumb slider; opaque, and missing from Details | Seven level cells measured from 20+ first tries per (template, tier); none measured at launch | Levels from item ratings whose priors are College Board's own 1–7 score bands for the official items each type maps to, moving with every clean first try. All seven levels hold types on day one; a level reads "rough" until 20; every type shows "your odds" (P11) | v2 BELOW at launch: 7 disabled cells. **P11 → WAY BETTER:** their scale on day one, then measured on our students, with how sure it is and the student's odds. |
| 10 | Solved filter | All / Solved only / Unsolved only | Pools: New, Open mistakes, Due, Never tried, Seen before (Result any / missed / right / guessed; Marked; From) | Seen pools give fresh twins or exact replays (P21). Due comes from the warm-up schedule (P12). Result adds "Sure but wrong" (P7) | **WAY BETTER already in v2.** P21 makes a replay test the skill, not memory of the item. |
| 11 | Marked for Review filter | All / Saved only (marking is saving) | Separate Marked and Saved pools (R5), but the builder only had a "Marked only" checkbox that read attempts, and no Saved row | Rows "Marked for review · 6" (default Exactly) and "Saved · 9" (default Fresh twins) in Questions from, each with an Exactly / Fresh twins seg; presets for both and a Saved header link (P21). A mark comes back as a fresh twin in the warm-up 2 days later (P12) | v2 BELOW: no way to start saved questions. **P21 + P12 → WAY BETTER:** both lists start in one tap, twins test the skill, and a mark does something even if the student never opens the list. |
| 12 | Redo list | `toggleRedo` in the API, no button; "Redo Questions 0" | Open-mistake pool with fresh numbers and named misconceptions; 2 clean answers close one | Confident misses first (P7); a final round re-asks every miss at the end of the set (P12); outside misses join (P13); any wrong option has "Practise this trap" (P1) | **WAY BETTER already in v2.** |
| 13 | Volume | 10 / 20 / 30 / 40 / 50 / All | 5–50, ∞, Other (1–120) | "15 min · 30 min" time boxes sized from the student's own budgets; "Fit to today's plan" (P15) | v2 PARITY. **P15 → WAY BETTER:** a set fits the time the student has. |
| 14 | Mode Timed \| Untimed | Timed allows 6 min a question (10 = 60:00) | Untimed / Test pace (flat 95 s) / Custom; pace alert at 1:35 | Per-type budgets (crowd median, or 65 / 95 / 126 s by tier). The clock is the sum of the planned slots' budgets, and every repair, twin or final-round question adds its own, shown as "+1:05 for the repair". "0:48 / 1:05" on the stopwatch, a pace delta, fluency, two passes, time sinks, new bests (P16) | v2 PARITY: a better flat number. **P16 → WAY BETTER:** the clock trains the real 35-minute trade-offs one question at a time and always matches the set. |
| 15 | Start Practice Session | The primary button | The disabled reason as text; "Building…"; a preview | Enter from the command line or a Ready card (P15). The Action bar states worth and minutes (P10, P16) | **WAY BETTER already in v2:** it says why it can't start. |
| 16 | Learning Preferences | Timed / Untimed, Adaptive / Fixed (no visible effect), AI Explanations, Show Desmos, Include Vocab Review | `learners.prefs` on the server, edited in the builder, More, Me and Settings; U15 modes | New keys: zone, review mix, final round, confidence, hints, solve first, worked first, two passes, presets (P2, P5, P7, P11, P12, P15, P16) | **WAY BETTER already in v2:** the settings work and follow the code. U15 moves them with the exam date. |
| 17 | Adaptive preference | No visible effect in QBank | R33: step a tier after 2 first-try rights, down after a miss (off by default) | Zone targeting per type from odds is the default (P11). R33's step reaches a sibling template when the type has one tier (P18) | v2 PARITY, and R33's step does nothing on 327 one-tier types. **P11 + P18 → WAY BETTER.** |
| 18 | Saved content counts | Profile counts: Saved Words / Redo / Saved Questions | Header links Mistakes · 4, Marked · 6, Your sets · 2 in progress | Adds Saved · 9 as a link that starts it (P21) and reviews due with a 14-day forecast (P12) | **WAY BETTER already in v2:** the links start the work. |
| 19 | Session route | Resumable only by its URL; the sidebar stays | Resume banner, Your sets (In progress / Finished / Shared), position restored on any device | Adds Rematch and "Rematch in 3 days" (P19) | **WAY BETTER already in v2.** |
| 20 | Go Back | A link back | Exit sheet: Keep for later / Pause / End and see summary | — | **WAY BETTER already in v2.** |
| 21 | Details popover | ID, domain, skill, difficulty; closes on outside click only | ID with copy, type and its about line, level with n, why, you and this type, everyone, permalink; Esc | Adds your odds (after answering), "Modeled on College Board 84664a7c", the Desmos way, the formula used, your rule for the type (P11, P13, P3, P24, P21) | **WAY BETTER already in v2.** |
| 22 | Explanation (and the AI Explanations switch) | Only after a check, replacing the card. The report version is a Justification plus one line per wrong option | Inline. A one-sentence rationale (median 21 words). Every option's misconception by default | Steps on this seed's numbers, with the step where the chosen answer left the path beside the right one, on at least 50% of the test by weight at launch (a gate). Every other template gets an audited Method paragraph of 40+ words. Option lines with values and "Practise this trap" (P1). A hint ladder that counts only the rungs the item has (P2). A Desmos-way tab (P3) | v2 BELOW in depth and at PARITY on per-option lines. **P1 + P2 + P3 → WAY BETTER:** never thinner than theirs anywhere, and on the common half it shows where *this* answer went wrong, in the student's numbers, and drills that trap. |
| 23 | Timer (Hide; Review page; Submit module) | A countdown pill with Hide | Countdown or stopwatch with a caption, Hide kept, Pause, toasts | A pace delta per answer with "3 Hard left"; budgets per question; the clock grows with every added question and says by how much (P16) | v2 PARITY in pacing. **P16 → WAY BETTER.** |
| 24 | Check Your Work | Timed sessions only | Every mode: tiles, grid, a note on skipped or unanswered | Triage in order: fill the blanks first (a blank scores like a wrong answer), then revisit Unsure answers, with the time left per question (P20) | v2 PARITY. **P20 → WAY BETTER:** it says what to do with the minutes left. |
| 25 | Clear Session | Removes answers, annotations and attempts, and serves the same items again | "Start over with these exact questions", which brought back the student's own notes and highlights | Rematch: the same types, tiers and order with new numbers, and a Then → Now table. The exact retake stays, labelled "tests memory". Both confirms carry "Start clean" (on for Retake), which hides highlights, notes, strikes and rules on the copy until Finish, keeping them on the server (P19) | v2 BELOW: the redo was spoiled. **P19 → WAY BETTER:** a clean redo like theirs without losing anything, and a rematch whose second score measures the skill. |
| 26 | Share | `navigator.share` froze the page; a shared-session landing | Set shares with the sharer's results (right rate per question, top named mistake), name opt-in | Each taker gets their own twins by default (P22, U28) | **WAY BETTER already in v2** (the results). P22 stops answers being passed around. |
| 27 | Calculator (and the Show Desmos switch) | Desmos in a floating panel, draggable and resizable | Dock, Float, phone sheet; state per set | "Show me in Desmos" loads this question's expressions after the verdict, on every one of the 175 templates in the six Desmos-heavy families at launch (a gate), on a production key. What the student typed is saved. Right with vs without Desmos, per skill (P3) | v2 PARITY in capability. **P3 → WAY BETTER** once its floor and production key are in; until both hold P3 ships dark and this row stays PARITY. |
| 28 | Reference | A modal with the formula-sheet image | The formula-sheet dialog | Every template names the formulas it uses (386 explicit entries), so the dialog opens at this question's formula. "Not on the sheet: know it", with a drill of the types that use it (P24) | v2 PARITY. **P24 → WAY BETTER:** on every question, never a skill heading. |
| 29 | Question number square | A blue square | Number, skill chip, type name, difficulty, Grid-in, Again | Adds zone, review, final-round and "Twin of CB …" chips (P11–P13) | **WAY BETTER already in v2.** |
| 30 | Mark for Review | A bookmark, which is also their save | A flag per sitting (R5), Save separate | Marked questions come back as twins (P12, P21) | v2 PARITY for the flag. **P12 + P21 → WAY BETTER.** |
| 31 | Eliminate | A mode toggle, ⊘ on each choice, saved to the server | Strike circles, Undo, Shift+A–D, saved, any device | Strikes are graded after the reveal ("You struck the key", "dodged: used the slope as the intercept"), strike accuracy in the summary, "You reliably rule out …" on the skill (P6) | v2 PARITY. **P6 → WAY BETTER:** only named distractors can grade an elimination. |
| 32 | Annotate / Highlights & Notes | Annotate on passages; H&N in the exam | Seven styles plus notes, stored per (template, seed) | A rule can follow the type onto every later practice question of that template, and prints as a "My rules" sheet (P21). A "Read the ask" underline after misreads (P8). Both are study aids: never in tests, the challenge, contests, end mode or Test-like mode, and the rule tip has its own switch | v2 PARITY: exact seeds rarely come back. **P21 + P8 → WAY BETTER**, and test-like sittings stay fair. |
| 33 | Report | 5,000 characters, 10 images, and no answer | `UI.report` (R17) | Key disputes answered inside the sheet by a second solver (U3). A broken question is voided in the rail and replaced in the set at once (P25) | v2 PARITY in form. **U3 + P25 → WAY BETTER.** |
| 34 | Attempts / Attempt History | #, result, option, time | Each try with its named mistake; the type's last 20 first tries, each with Open | A trend head per type: ✕ ✕ ✓ ✓ ✓, median time 2:10 → 0:58, "ready · next return Oct 2"; "then vs now" on the verdict (P9) | **WAY BETTER already in v2.** |
| 35 | Per-question stopwatch | Counts up; resets to 00:00 on reload | Survives reload, skip and leaving; pace alert at 1:35 | Measured against this question's budget, with your median tick and "New best on this type" (P16) | v2 PARITY in the alert. **P16 → WAY BETTER.** |
| 36 | Stem rendering | KaTeX; an image floats beside the text (a bug) | Figure on its own row; Source Serif 20 px | Adds the "Read the ask" underline (P8) and the type-rule tip (P21) | **WAY BETTER already in v2** (the bug is fixed). |
| 37 | MCQ layout | A 2×2 grid of cards | Rows; auto 2×2 for short choices | Cover the choices and solve first (P5) | v2 PARITY. **P5 → WAY BETTER:** a typed answer is diagnosed before the choices can sway it. |
| 38 | SPR input and Answer Preview | Placeholder with examples; KaTeX preview; green when right | Rule line, validation, stacked preview with its decimal, accepted forms; named grid-in mistakes grow template by template | Named grid-in mistakes on 87 templates (half of all grid-ins) at launch, borrowed from the same seed's MC version (P4) | v2 PARITY at launch: the named part is nearly empty. **P4 → WAY BETTER.** |
| 39 | Check | Green or red; the key never shown; unlimited retries; Mixed | Select then Check. Key, named mistake, repair. Retry names the mistake; first try counts | Check carries the confidence: `Check` · `Sure` · `Unsure` · `Guess` in the same one tap (P7). A plain Check or Enter files Unrated unless the student tags, so Sure always means Sure. The cause of each miss, pre-filled (P8). The next step (P9) | **WAY BETTER already in v2.** P7 tags answers at no extra cost without faking confidence. |
| 40 | Bottom bar | Previous · "Question N of 10" · Check · Next; a round trip each | The same, with keys | One round trip: the next question comes back with the verdict as a preview, committed only when shown. Tap the choice again to check; Enter, Enter. `A–D` only choose; save is `Z`, details `X` (P23, §2.10) | v2 PARITY. **P23 → WAY BETTER** (faster, and the set's counts stay exact). |
| 41 | Question Overview | Status \| Difficulty; ignores Esc | Status / Difficulty / Skill / Time, legends with counts, a current ring, Esc | Legend chips filter. Confidence and Traps views. "Twins of these". U jumps to the next unanswered (P20) | v2 PARITY: it only shows. **P20 → WAY BETTER.** |
| 42 | No end | No summary, score or review | Summary: tiles, by skill / type / difficulty, time per question, mistakes, review list, NextActions | Points moved, calibration, causes, traps dodged, time sinks and passes, reviews held, final round, and a next set built from all of it (P6–P10, P12, P16) | **WAY BETTER already in v2.** The upgrades make it prescribe the next set. |
| 43 | Reload | The stopwatch resets; a wrong pick shows as plain "selected" | Restores the verdict, stopwatch, strikes and notes | — | **WAY BETTER already in v2.** |
| 44 | Homework (hidden) | Class pages and QBank-session assignments, hidden in their app | Not built: no classes (decision 5, a separate platform has them) | Friends share a set by link; each taker gets their own twins, with results per slot and per named mistake (P22). Racing friends is Compete's invite-code private contest | **Out of scope (decision 5).** Sharing among friends is covered by P22. |
| 45 | Public single question (hidden) | `/question/:key` | Permalink `?q=TEMPLATE:SEED` | "Send a twin" by default, with both results (U28, P22) | v2 PARITY. **U28 → WAY BETTER.** |
| 46 | Floating vocab button | Covers Next | The quick sheet; nothing floats | — | **WAY BETTER already in v2** (R29). |
| 47 | Include Vocab Review (preference) | A switch that mixes vocab review into study | Words is its own section; §2.9 adds math-word chips to the verdict | No math-word chips (decision 2). "Mix in due SAT words: Off · 2 per set · All due" puts Words' due reviews into the set at breaks, filed to Words' schedule and kept out of Math numbers (P12). The summary offers "SAT words · 12 due" as a next action, and the R&W seg lists the Words drills (P15) | v2 PARITY. **P12 + P15 → WAY BETTER:** the same switch, with a chosen dose, reviews that move the real Words schedule, and a counted next step. |

---

## 2. Accepted upgrades

Grouped by where they act. Each gives why, screens and components, controls and states, data
and endpoints, how it uses the rest of the site, and acceptance checks. Learner codes in the
checks start `a:v2revpr`; `:PORT` is the task's own port.

Shared rules for every upgrade:
* **Revealing.** Anything that shows a key, steps, a Desmos solution, a formula or a trap is
  returned only when the feedback can be revealed: instant mode, retry mode once the question
  is final, or any mode once the set is finished. R19 still governs exact re-serving.
  Reserved seeds (900000 and up) are never served in practice (`_fresh` skips them), so their
  keys can always be shown.
* **Challenge** (§2.13). Hints, Learn this type, twin axes, review slots, the final round, zone
  targeting, Mix-up, word cards (P12) and the study aids below are off. Steps, the Desmos way,
  confidence, the cause chips and the next-step line are allowed after answering.
* **End mode.** Nothing on the verdict side shows before Finish. Confidence and Cover work
  while answering. Steps, causes and the Desmos way appear in the ReviewSheet after Finish.
* **Study aids stay out of anything test-like.** `UI.workspace` is shared with the exam
  runner, the Daily Challenge and contests (R21), so these four are gated in one place:
  the type-rule tip (P21), the Read-the-ask underline (P8), the "Last time: a slip" line and
  the "Check anyway?" prompts (P8, P16).
  * They show only in instant or retry practice, and in review (the ReviewSheet, Review's
    pane, the report player).
  * They never show in end mode before Finish, in tests, in the Daily Challenge, in contests,
    or in U15's Test-like mode.
  * The server enforces it: `/q` and `next` omit `type_note`, `ask_span`, `slip_note` and
    `check_anyway_ms` in those contexts, so nothing reaches the DOM.
  * Pref `type_rules` (flat, default on) turns the rule tip off everywhere.
  * Acceptance: with a type rule saved on t, a Daily Challenge twin of t has no
    `.type-rule` element in the DOM, and its `/q` payload has no `type_note`. The same
    question in an instant practice set shows the tip.
* **Help counting.** Any answer given with help (a hint, the example open) stores
  `attempts.hints > 0`. It counts half toward mastery and is not clean (R8 amendment, §3.2),
  the same rule as a guess, kept in its own column so calibration (P7) stays clean.

### A. The answer loop: what each question teaches

#### P1. Steps on this question's numbers, the step where your answer left the path, and a drill for every trap

*From: experience #2, the explanation parity gaps of all three designers (including
unfair-advantage's "Lock it in: 3 twins"). Effort L (content grows template by template).
Builders: T-bank (`Step`, `Mis.at / wrong`, audit, coverage), F5 (`practice.to_question`,
feedback fields, `/more {want}`), F3 (the explanation card), S4 (session wiring), S10 and S6
(the same card in Review and the report).*

**Why.** Our rationale is one sentence (median 21 words); their Justification is longer.
Neither tells a student where their own attempt went wrong. A generator knows every
intermediate value for this seed and which step each misconception gets wrong, so it can show
the right line and the student's line side by side. A fixed bank of prose can't. Steps are
also the second rung of the hint ladder (P2).

**Bank (T-bank, `satbank/item.py`, `satbank/audit.py`).**
* `@dataclass Step: text: str; value: Exact | None = None`. The text carries this seed's
  numbers ("Gather the m terms: 8m − 8m = 0").
* `Item.steps: list[Step] = []`.
* `Mis` gains `at: int | None = None` (the step index where this misconception departs) and
  `wrong: str | None = None` (that step done the mistaken way with these numbers: "3 ÷ 54 =
  1/18").
* `assemble` copies each picked Mis's `at` and `wrong` into `Item.step_of: list[dict | None]`,
  aligned with `choices`. The key and fillers get None. SPR `spr_mistakes` carry the same
  fields.
* **Audit**, whenever `steps` is non-empty:
  * 2 ≤ len(steps) ≤ 6;
  * when the key is a value, the last step's `value` equals the key;
  * each `at` is in range;
  * when a Mis value is numeric, `wrong` contains that option's printed value
    (`item.numeral` on the tokens).
* **Coverage is a launch gate.** `tools/steps_coverage.py` prints "n of 386 templates have
  worked steps · they cover x% of the test by U8 weight · m distractors point at a step · k
  templates use a Method paragraph". It **exits non-zero while x < 50%**, and P1 is not marked
  done until it exits 0. Work runs in U8 weight order (the most common official forms first),
  so the gate is met by roughly the most common third of the templates.
* **No fake steps.** A template without `steps` never shows its rationale cut into pieces
  (today.md rejected the same cut for hints: it is often nonsense or gives the answer away).
* **A floor for every other template: the Method paragraph.** Where `steps` is empty, the
  Short tab becomes **Method**, one paragraph of at least 40 words, built by
  `item.method(item)` (T-bank) from three audited parts:
  * the type's idea: the template docstring's first paragraph ("A line through two points:
    slope is rise over run, then substitute one point to get the intercept.");
  * this seed's rationale, with its numbers;
  * the key's value: "Here that gives 18."
  * The audit, on 200 seeds of every template without steps, asserts at least 40 words and
    that the key's printed value appears. A template that falls short gets a `METHOD:`
    paragraph in its docstring (T-bank authors it; about 3 sentences), which replaces the
    first part.
  * So no explanation of ours is thinner than their Justification plus Distractor Analysis:
    the Method paragraph plus a named, valued line per wrong option.

**Payload (F5).** `practice.to_question` stores `steps` (text list) and `step_of`. Feedback,
when it can be revealed, adds `steps`, `diverge` (the chosen option's `at`, or the matched
grid-in mistake's), `wrong_step` and `option_steps` (an `at` per option).

**The explanation card (F3, `UI.workspace`).**
* **Header**: the type's name and its about line (the docstring's first sentence), so every
  explanation opens with the idea of the type.
* **Tabs** (`UI.tabs`): **Steps** (the default when steps exist) · **Short** (the rationale) ·
  **Desmos way** (P3, when present). Without steps the first tab is **Method** (the paragraph
  above) and there is no Steps tab, never an empty one.
* **Steps**: numbered rows in Source Serif 17 px, with KaTeX, as a roving-tabindex list (↑ ↓
  move while it has focus; no letter keys, because `J` / `K` belong to the players and `K` to
  confidence in the runner, §2.8).
* **On a miss** with `diverge`:
  * rows before it get a small ✓ and "you likely had this";
  * row `diverge` gets a 1.5 px ink outline and a two-column compare: "**Right:** 54 ÷ 3 = 18 |
    **Your B:** 3 ÷ 54 = 1/18 · the ratio flipped", ending with the option's reason. On a phone
    the cells stack.
* **Option lines** (replacing §2.6's "C: used the slope as the intercept"): "C · 14 · used the
  slope as the intercept", then two quiet links:
  * **See where C comes from** outlines C's step; the chosen answer's outline stays;
  * **Practise this trap** calls `POST /api/drill/{id}/more {question_id, want: norm, n: 1}`
    and shows "Next: one with this trap". Up to 3 can be queued per question ("Lock it in").
  A filler still reads "a nearby value, not tied to a specific mistake" and has no drill link.

**Uses.** The ReviewSheet (§2.11), Review's pane (S10, R23), the report player (S6) and the
print key page (§2.12) render the same card. The option line's reason links to its habit (U6).

**Acceptance.**
1. `python3 tools/steps_coverage.py` prints "of 386 templates have worked steps" and exits 0
   only when steps cover at least 50% of U8 weight (a run on a bank below it exits 1).
   `PYTHONPATH=. python3 -m satbank` passes 200 seeds of every template with steps.
2. On a covered template, a wrong MC answer's feedback has non-empty `steps`, and `diverge`
   equals `option_steps[chosen]`. In end mode the answer response has no `steps`.
3. Browser: after that miss the Steps tab is selected, one row has the outline, and it
   contains "Your B:" (or the chosen letter).
4. "Practise this trap" on option C: the next served question has the same template, a new
   seed, and an option whose `progress.norm(reason)` equals C's norm.
5. On a template without steps the explanation shows no Steps tab.
6. For every template without steps, 200 seeds: `item.method(item)` has at least 40 words and
   contains the key's printed value, and the explanation's first tab reads "Method".

#### P2. Help before you give up, and Learn this type: rule out a trap, the first step, a worked twin, then the ladder

*From: outcomes #8 (the hint ladder), outcomes #3 (study one, solve one), unfair-advantage #13
(scout the type), experience #2 (hints in retry mode), and today.md T4, whose Learn session
this reuses. Effort M (on P1). Builders: F5 (`/hint`, example cards, `/more {ladder}`), F3
(workspace modes `example` and `guided`, the Hint row, the scout sheet), F4 (`attempts.hints`,
R8), S4 (entry points, summary), S10 (Review's entry).*

**Why.** A stuck student today guesses and then reads the key. Help given one rung at a time
keeps them solving. Their only in-question help is Eliminate, and their explanation appears
only after checking. Only named distractors let a hint strike a trap and say which mistake it
is, and only a generator can hand over a worked twin without spending a question.

**The hint ladder** (instant and retry modes; never end mode, the challenge, tests or
contests; pref `hints`, default on).
* A quiet `Hint · 1 of 3` button (key `W`) under the choices while the question is
  unanswered. After each rung it reads `Hint · 2 of 3`, then `Hint · 3 of 3`.
* **The count is this item's own.** The payload carries `rungs` (the rungs this item really
  has, in order), and the button counts only those: an MC item on a template without steps
  reads `Hint · 1 of 2` (rule out a trap, then the worked twin); a grid-in without steps reads
  `Hint · 1 of 1`. A rung that does not exist is never promised.
* **Rung 1, Rule out a trap** (MC only). It strikes one named distractor and says why:
  `Struck C: that's what you get if you used the slope as the intercept.` It picks, in order:
  the norm of the learner's own open or past trap on this template; the crowd's top mistake
  (n ≥ 20); the first non-filler option. It goes through the strike store (§2.5 /strike) with
  `by:'hint'`, so it looks like a strike, and Undo is off.
* **Rung 2, First step.** Step 1 of `Item.steps` (P1), shown above the choices. Skipped when the
  template has no steps. Grid-ins start here.
* **Rung 3, A worked twin.** The type's worked example (a reserved seed from
  `GET /api/types/{t}/example`, U2, with its key, reasons and steps) opens beside the question
  in a side panel at ≥ 1080 px, or in a sheet below. The question on screen stays.
* **Retry mode.** After a wrong try the footer reads `Hint · 2 tries left · Show answer`; the
  hint count is stored on the next try (`tries.hints`). A right answer after hints reads "Right
  on try 2 after 1 hint · counts as Mixed".
* **Server.** `POST /api/drill/{id}/hint {question_id}` →
  `{rung, kind: 'strike'|'step'|'example', choice?, reason?, step?, example?}`. It never
  returns the key of the question on screen. It raises `cfg.hints[qid]`, which the answer
  files as `attempts.hints`. 409 in end mode, the challenge and contests.
* **Summary.** A tile `Right with help · 2`. The navigator's Status legend gains `Helped 2` (a
  small `h` corner).

**Learn this type, inside Practice.** The session is T4's:
`POST /api/drill {source:'learn', templates:[t], example:true, count:3}`: card 0 is the
worked example (reserved seed, files nothing), question 1 has the example one tap away,
questions 2–3 are on your own, and question 3 is a tier up when possible. This file adds:
* **The traps in this question** under card 0: one line per distractor, "B · 1/18 · inverted
  the rate".
* **Watch for** above question 1's choices: the type's top 3 surveyed misconceptions (norms
  from `blueprint.kinds()`), with no letters.
* Question 1's "Show the example" sends `hints: 1` instead of T4's `guess: true` (§3.2), with
  the same counting.
* A question 3 "a tier up" uses P18's sibling when the template has one tier.
* **Pips** in the strip: `Example · With help · On your own · On your own`.
* **Summary**, after T4's line: `Proof comes back in 2 days, in your warm-up` (T3's rule after
  a clean right).

**Entry points** (Today's are T4's):
* `Learn this type` (quiet) on every TypeRow, in the Map popover (P14), in Details, and on
  Review's trap rows (S10).
* **After a second first-try miss** on one template within 30 days, the verdict offers
  `Missed this type twice. Learn it step by step · 3 questions · ~4 min`. That calls
  `POST /api/drill/{id}/more {question_id, ladder: true}`, which puts the example card and
  three slots next in this set. A fixed total grows by 3 (the example card is not a slot).
* **Builder setting** (in Answers shown) `New types: show me one worked first` (pref
  `worked_first`, default on). The first time a set serves a template the learner has never
  answered, its example card comes first. At most one per skill per set; never in timed sets,
  end mode or the challenge.
* **Fading.** The miss offer and `worked_first` apply only while the type has fewer than 2
  clean rights.

**See the traps (the scout sheet).** A `UI.sheet` titled with the type's name and about line:
* a live example in mode `example` (a reserved seed, key marked, steps open);
* "Traps in this type": each surveyed norm with the learner's record from P6 ("caught 2 ·
  dodged 3") and everyone's share of misses (crowd, n ≥ 20);
* the learner's record and best time.
The primary is **Drill 5 of these**; quiet actions **Another example** (the next reserved
seed) and **Learn it step by step**. It opens from the TypeRow ("See the traps"), search
results, Details and the Map popover.

**Data.** `attempts.hints INTEGER NOT NULL DEFAULT 0`; `tries.hints INTEGER DEFAULT 0`;
`cfg.hints {qid: n}`; example cards sit in `served` with `kind:'example'`, never filed, never
counted in total or accuracy.

**Acceptance.**
1. `/hint` on an MC question with a named distractor returns `kind:'strike'` and a `choice`
   whose reason is non-empty and is not the key. `GET /api/drill/{id}` shows it struck. The
   response has no `answer` or `answer_index`.
2. Answer right after one hint: `attempts.hints == 1`, an open trap on the template keeps its
   `owed`, and the mastery change is half that of a clean right (compare `mastery_of`).
3. `/hint` in an end-mode set → 409; in the challenge → 409.
4. The T4 body: card 0's seed ≥ 900000 and has no attempt row. "Show the example" on
   question 1 → `attempts.hints == 1` and `guess == 0`.
5. Two first-try misses on one template in one set: the second verdict contains "Missed this
   type twice", and `/more {ladder:true}` raises `total` by 3.
6. `worked_first` on, a 5-question untimed set over 2 skills for a new learner: at most 2
   example cards are served.
7. An MC question on a template without steps has `rungs == ['strike', 'example']`, and the
   button reads "Hint · 1 of 2".

#### P3. The Desmos way: one tap loads this question into the calculator, and we measure whether it helps

*From: experience #6, unfair-advantage #11, outcomes #10, the calculator parity gaps. Effort L
(content grows). Builders: T-bank (`Item.desmos`, audit, coverage), F3 (`UI.calc.walkthrough`,
capture), F5 (payload, filter `has`), F4 (`attempts.calc`), S4 (tab, summary, builder filter).*

**Why.** The built-in Desmos solves a large share of SAT Math questions faster and without sign
slips, and the minutes saved go to the hard questions. Theirs embeds the same calculator and
never shows how to use it on a question. It can't: their items are text and images. We hold
every item's exact equations.

**Bank (T-bank).**
* `Item.desmos: dict | None` = `{exprs: [{latex, label?, hidden?}], look: 'intersection' |
  'zeros' | 'vertex' | 'value' | 'regression' | 'table' | 'point', bounds: {left, right, bottom,
  top}, point: {x, y, label} | None, note}`, built from `params`. `note` is one line: "Graph
  both sides; the x of the intersection is the answer: x = 3".
* **Audit**: when `look` is `intersection`, `zeros`, `value` or `vertex`, `point`'s relevant
  coordinate equals the key. A regression look checks that its `y1 ~ m x1 + b` row lists every
  table row.
* **Coverage and the launch floor**: `tools/desmos_coverage.py` prints "n of 386 types have a
  Desmos way · floor f of 175". The floor is **every template** in the six families where the
  calculator changes the question: systems (20), linear functions and linear equations in two
  variables (45), nonlinear functions and nonlinear equations and systems (68), linear
  inequalities (18), circle equations (`circles.families.equation`, 6) and two-variable data
  (18). Interpretation questions in those families get a `table` or `point` look (graph it,
  read the value off the point), so none is exempt. The tool exits non-zero while any floor
  template lacks `desmos`. Other topics grow after launch in U8 weight order.

**After the verdict** (never before it; never in end mode before Finish):
* The explanation's **Desmos way** tab lists the numbered expressions (read-only KaTeX) and the
  note, with **Show me in Desmos** (`Shift+G`).
* `UI.calc.walkthrough(desmos)` (F3): saves the student's graph with `calculator.getState()`;
  opens the dock (or the phone sheet); `setBlank()`, then enters the expressions one by one,
  300 ms apart (all at once under reduced motion); `setMathBounds(bounds)`; adds the point with
  `label` and `showLabel` ("The lines meet at (3, 7), so x = 3"). A bar at the top reads **Back
  to my graph**, which calls `setState(saved)`.
* **Chips**: "Desmos way" on the strip after answering, and on the TypeRow.

**What you typed.**
* UI.calc observes `change`, debounced 1 s. While a question is on screen it sends
  `POST /api/drill/{id}/calc {question_id, exprs: [latex] ≤ 30}` → `cfg.calc[qid]`.
* `attempts.calc = 1` when the calculator changed while that question was on screen, before
  it was answered.
* The ReviewSheet and Review show "What you typed in Desmos" as a read-only KaTeX list, so a
  wrong entry can be diagnosed.

**Numbers.**
* Summary: "Calculator on 4 of 10 · right 4 / 4 with it · 3 / 6 without".
* SkillPanel, once both sides have 5 or more answers: "Systems: 90% with Desmos (10) · 60%
  without (15)", with the nudge "Use Desmos on these".

**Builder.** A Format-row checkbox "Only types with a Desmos way (N)" sends `has: ['desmos']`.
A preset chip "Desmos drills · N types" opens the dock, uses instant feedback and starts those
types.

**Needs, and the ship rule.** A production Desmos API key (open question 15), obtained
before launch; the demo key is for development only. P3 sits behind the server flag
`DESMOS_WAY` (off by default). I1 turns it on only when both hold: the production key is in
the kv store, and `desmos_coverage.py` exits 0 on the floor. With the flag off, no payload
carries `desmos`, the tab, chips, filter and preset are absent, and the scorecard row stays
PARITY. The typed-expression capture (What you typed) does not need the flag.

**Acceptance.**
1. `python3 tools/desmos_coverage.py` exits 0 only when all 175 floor templates carry
   `desmos` (removing one from a fixture makes it exit 1). The audit passes 200 seeds of every
   template with `desmos`.
2. A covered systems item's instant feedback has `desmos.exprs` with 2 entries. End-mode
   answers carry no `desmos`.
3. Browser: Show me in Desmos → `Calc.getExpressions().length == 2` within 1 s. Back to my
   graph restores the previous expression count.
4. Type an expression while question 3 is on screen, then answer it: `attempts.calc == 1`, and
   the ReviewSheet lists it under "What you typed in Desmos".
5. `POST /api/drill/preview {has:['desmos']}` counts only templates whose items carry `desmos`.
6. With `DESMOS_WAY` off, a covered systems item's instant feedback has no `desmos`, and the
   Desmos way tab is absent.

#### P4. Named grid-in mistakes from day one, borrowed from the multiple-choice version

*From: the unfair-advantage SPR gap (re-measured here). Effort S. Builders: F5
(`practice.to_question`), T-bank (the check script counts both sources).*

**Why.** §3.3.4 promises "Your answer 14 is what you get if you used the slope as the
intercept", but it waits on template edits (open question 11), so at launch it would say "No
named mistake for this value" almost everywhere. Half of all served grid-ins have an MC
version of the same seed with the same key and params, and that version's three named wrong
values apply to the grid-in.

**Rule** (`practice.to_question`, for an SPR item whose template takes `fmt`):
* Generate `(template, seed, fmt='mcq')`, cached with `functools.lru_cache(4096)`.
* When that item's `key` and `params` equal the grid-in's, take its non-filler distractors as
  `spr_reasons` (`[[reason, value_text]]`).
* A template's own `spr_mistakes` (T-bank) win whenever present.
* Grading is unchanged: `scoring.grid_equal` against each value.
* `ponytail:` one extra generation per served grid-in (~0.3 ms); precompute in the Builder if
  it shows in profiles.

**Coverage line.** The check script prints "n of 153 grid-in templates name their mistakes
(own a, borrowed b)".

**Acceptance.**
1. A template and seed whose MC version matches (the check script lists one): answering the
   grid-in with the MC item's option-C value returns `mistake == reasons[2]`, and the traps
   row uses that reason.
2. The check script prints a borrowed count of at least 80 templates.
3. A seed whose MC version differs in key or params carries no borrowed `spr_reasons`.

#### P5. Solve first: cover the choices, then match your answer to the traps

*From: unfair-advantage #3, outcomes #15. Effort M. Builders: F3 (workspace mode `cover`, `V`),
F5 / S4 (the answer body's `own`, `tries` n = 0), F4 (`attempts.cover`, the pref).*

**Why.** "Solve it before you look at the choices" is the most-taught SAT Math habit. It works
because the choices can't pull you toward a trap. Only a bank whose wrong options are computed
values with named causes can diagnose the value a student typed *before* seeing them.

**Controls.**
* A ToolButton **Cover choices** (key `V`) in the strip.
* A builder setting "Solve before seeing choices": Off · Medium and Hard · All (pref `cover`,
  default off). A preset chip "Solve first · 10" turns it on for one set. Mix-up sets (P17)
  default it to All.

**While covered.**
* The MC options sit under a paper panel with a "Your answer" field that uses the grid-in
  validation and preview.
* The stopwatch splits into "solve 1:02 · pick 0:08" (`cfg.ms_split[qid]`).

**Enter sends `POST /answer {question_id, own: "14", ms, conf}`.** The server compares numbers
with `scoring.grid_equal` against `item.numeral(choice)`, and expressions with
`satbank.expr.agree` when all four options parse. The response's `cover` is one of:
* `key`: the key is selected and checked. The verdict adds "Solved without the choices".
* `distractor`: this is the first try, filed with its named mistake: "Your 14 is choice C: you
  used the slope as the intercept."
* `none`: nothing is filed. "No choice is 17. Recheck, then pick." The choices uncover, the
  next pick is the first try, and the typed value is stored as a `tries` row with `n = 0` and
  reason `cover_miss`.

When the options are neither numbers nor parseable expressions, the field is replaced by
**Ready: show choices**, and only the split time is kept.

**Numbers.** Summary: "Solved before seeing choices: 6 of 8 · matched a trap 2 · no match 0 ·
right 88% covered vs 72% uncovered". A SkillRow shows "solve-first 75%" once a skill has 5
covered answers. `attempts.cover = 1` on every covered question.

**Acceptance.**
1. A covered item whose option C is a numeric distractor: `POST /answer {own: <C's value>}` →
   `correct:false`, `cover:'distractor'`, `mistake == reasons[2]`, `attempts.cover == 1`.
2. `own` equal to the key → `correct:true`, `cover:'key'`.
3. `own` matching nothing → `cover:'none'`, the attempts count unchanged, and a `tries` row
   with `n = 0`. The next `/answer {answer:'B'}` files the attempt.
4. Browser: `V` hides the choices and focuses the field.

#### P6. Traps on offer: dodged or caught, strikes graded, and habits in the builder

*From: unfair-advantage #2, the eliminate parity gaps of all three designers. Effort M.
Builders: F4 (`attempts.offered`, `attempts.struck`, backfill), F3 (verdict lines), S4 (builder
Habits view, summary), F5 (U6's `habits.py`, source `habit` with a list).*

**Why.** Every MC question offers three named traps. A student who dodges "stopped a step
early" nine times in a row has beaten that habit, and one who keeps catching it needs a drill
aimed at it. Their options carry no labels, so they can count neither dodges nor catches, and
can't grade an elimination.

**Data (F4).**
* `attempts.offered TEXT`: a JSON list of the norms of the named distractors shown (fillers
  left out), written by `progress.record` from `q['reasons']`.
* `attempts.struck TEXT`: a JSON list of the indices struck before answering (hint strikes
  included, marked `h`).
* A startup backfill fills `offered` for old rows by regenerating (template, seed), at 0.3 ms
  each.
* **Dodged** = on offer and not chosen; a struck distractor counts as dodged. **Caught** =
  chosen.
* A habit is U6's family of the norm (`habits.family(norm)`), so no bank tags are needed.

**Verdict (F3).**
* One line after the reveal: "Traps on offer: B used the slope as the intercept · C sign slip
  · dodged both", or "Caught by C: sign slip".
* **Strikes graded.** Each struck distractor reads "struck B · dodged: inverted the rate". A
  struck key reads "You struck the key (C)" in ink, and the coach counts it as a miss signal
  (`struck_key` in the feedback).
* The rail's text line adds "traps dodged 5 of 6".

**Builder: a Habits view.** The tree header's seg reads "Skills · Map · Habits" (Map is P14).
* One row per U6 family: the name and its tell in italics; "caught 7 times across 4 skills ·
  3 open · dodged 12 of 15 on offer · last Sep 21"; the glyphs of the skills where it was
  caught.
* Ticking habits makes the set a habit drill: `source:'habit', habits:[ids]`, drawn from the
  selected skills (or all skills when none is selected). U6's resolver takes a list; every MC
  question has an option in one of those families, found with U6's `want` walk.
* A preset chip "Your top habit · stopped early" appears when one family is 25% or more of the
  last 20 misses.

**SkillPanel.** "You reliably rule out: used the slope as the intercept (6 of 6 struck or
dodged)", for the norm with the best dodge record (5 or more on offer).

**Summary.** "Stopped a step early: dodged 7 of 9 (last week 3 of 8)" and "Strikes 14 · 13 on
wrong options (93%) · struck the key once".

**Acceptance.**
1. After an MC answer, `select offered from attempts order by id desc limit 1` is a JSON list
   of 3 norms (fewer when fillers were shown).
2. Strike the key, then answer another option: the feedback has `struck_key:true`, and
   `attempts.struck` contains the key's index.
3. `GET /api/bank?subject=math` has `habits: [{id, caught, dodged, offered, open, skills}]`
   for a learner with 5 answers.
4. `POST /api/drill {source:'habit', habits:['whole_part','sign'], count:6}` → 6 questions,
   each with an option whose norm maps to one of the two families.

#### P7. Confidence is the Check button: Sure · Unsure · Guess in the same one tap

*From: outcomes #1 (the control), experience #8, unfair-advantage #6, the outcomes overview
gap. Effort S. Builders: F3 (the split Check in the runner footer, the Confidence view), F4
(`attempts.conf`, R8 and R9 rules, coach priority), S4 (summary, builder pool), S10 (Review
filter).*

**Why.** A miss the student was sure of is a misconception to unlearn, and it costs points on
test day because nobody re-checks what feels certain. Corrected high-confidence errors are
retained best (hypercorrection). An Unsure right is fragile. Calibration tells a student when
to trust a first read in a timed module. `shell-me.md` and `today.md` rejected an *extra* tap
before Check because most students won't make it. This design has no extra tap: the button a
student already presses carries the answer's confidence.

**Control (F3, instant and retry modes; the first try only).**
* With pref `confidence = ask` (default), once a choice is selected or a valid grid-in is
  typed, the footer's Check becomes a four-part split:
  * `Check` (the orange pill, `Enter`; tapping the selected choice again, P23, is the same);
  * `Sure` (.btn);
  * `Unsure` (.btn, `Shift+Enter`);
  * `Guess` (.quiet, `I`).
  Each part submits. On a phone the split is full width, Check at 40% and 20% each for the
  others.
* **Sure means Sure.** Only a deliberate choice files `sure`:
  * a click or tap on the `Sure` part;
  * or `Check` / Enter / tap-again from an **active tagger**: a learner who used Unsure or
    Guess on at least 10% of their last 50 first tries (`progress.conf_active(learner)`, F4,
    returned in the set's state). For them the pill reads `Check · Sure`, so it says what it
    files.
  * Everyone else's `Check`, Enter and tap-again send `conf:'auto'`, which the server files as
    null, shown as **Unrated**. The client never decides; `answer()` resolves `auto`.
* The first 3 questions a learner ever answers show the helper "Sure? Tap Sure. Not sure? Tap
  Unsure. Check alone leaves it unrated." (`localStorage satf.conf.tip`, in try/catch).
* End mode: `Save & next` splits the same way, and a question's confidence can change until
  Finish. Tests keep §3.4's chips (`qstate.conf`) with the same vocabulary.
* `confidence = off`: a plain Check, `conf` null.

**What each files** (`attempts.conf TEXT`: `sure` · `unsure` · `guess` · null = unrated).
Everything below that reads `sure` reads only an explicit `sure`; an unrated miss is an
ordinary miss.
* **Guess**: `guess = 1` (R8): counts half, closes nothing, opens the explanation.
* **Unsure, right**: counts in full toward mastery but is not clean, and opens or refreshes an
  `~unsure` item owing 1: Review's rule for a flagged right (R8 and R9 amendments, §3.2).
* **Sure, wrong** (a confident miss):
  * the verdict note: "You were sure, and it's wrong: this kind costs points on test day,
    because you wouldn't re-check it. It comes back first.";
  * the explanation opens; the repair comes next even when repairs are `later` or `end`;
  * `progress.coach` and `_pick` rank traps whose latest wrong attempt has `conf = 'sure'` first,
    with reason `confident` (derived from attempts, no new column);
  * the Why line on its return: "You were sure of this one and missed it (Sep 22)".

**Summary: Calibration** (5 or more tagged answers). Four bars: "Sure 12 · 11 right (92%)",
"Unsure 6 · 3 right (50%)", "Guess 2 · 1 right", and "Unrated 8 · 6 right" in `--soft`, which
never enters a reading line. One reading line when its bucket has 5+:
* Sure ≥ 90%: "Your Sure is reliable: on a test, don't re-check those; spend the time on
  Unsure."
* Sure < 75%: "Your Sure was right 70%: slow down on questions that feel easy." Then the
  confident misses by name: "Sure on 3 wrong answers: used the slope as the intercept, …".
* Unsure ≥ 85%: "Your Unsure answers were right 90%: trust yourself and move on."
* When more than half of this set is Unrated: "Most answers here are unrated. Tap Sure or
  Unsure as you check, and this card shows whether your first read can be trusted on test
  day."

**Elsewhere.**
* Builder "Questions from" gains "Fresh numbers on confident misses · 4 types" (`pool:'redo'`,
  `ids`: those traps), and a preset chip with the same name. The Seen-before Result seg gains
  "Sure but wrong".
* The ReviewList, Review's list (S10) and the Navigator's Confidence view (P20) filter by it.
* The SkillPanel stats line adds "Sure-accuracy 95% (40)". U7's "When you guess" reads `conf`.

**Acceptance.**
1. `POST /answer {answer:'B', conf:'sure'}` on a wrong option → `attempts.conf == 'sure'`, and
   the next `GET /api/bank` coach reasons for that skill include `confident`.
2. `conf:'guess'` → `attempts.guess == 1`; a right answer leaves the trap's `owed` unchanged.
3. `conf:'unsure'` on a right answer → `/api/review/redo` gains an `unsure` item owing 1.
4. Browser: with a choice selected, `Shift+Enter` submits with `conf:'unsure'` (network log).
   With `prefs.confidence == 'off'`, the footer shows a single Check.
5. A set with 6 Sure answers, 5 right: the summary shows "Sure 6 · 5 right (83%)".
6. A learner with no Unsure or Guess in their last 50 first tries presses Enter on a wrong
   option: `attempts.conf` is null, the verdict has no "You were sure" note, the coach reasons
   gain no `confident`, and the Calibration card shows an Unrated bar.
7. The same learner after 6 Unsure answers in their last 50 (12%): `conf_active` is true, the
   pill reads "Check · Sure", and Enter files `conf == 'sure'`.

#### P8. Why you missed: T7's cause on every miss, corrected in one tap, and a different fix for each

*From: outcomes #11, the unfair-advantage "Read the ask" gap, today.md T7 (whose rule this
uses). Effort S. Builders: F4 (`progress.cause_of`, `attempts.miss_kind`, `causes` honouring
it), F3 (chips, the underline), S4 (endpoint, summary card, routing), S10 (grouping).*

**Why.** Misses have different causes, and "do more questions" does nothing for a misread or a
slip. Keeping an error log is standard SAT tutoring advice. Ours fills itself in from the option
picked, the history and the clock (T7's rule), so the student taps only to correct it. Their
QBank marks a miss red and records nothing.

**Chips** ("What happened?", under the verdict of a first-try miss: instant mode, retry once
final, and the ReviewSheet after an end-mode Finish). T7's five causes plus one only a student
can tell us:
* **Fell for a trap** (`trap`) · **Slip: I knew it** (`slip`) · **Misread the question**
  (`misread`) · **Ran out of time** (`clock`) · **Entered it wrong** (`entry`, grid-ins only) ·
  **Didn't know how to start** (`gap`).
* One is pre-selected by `progress.cause_of(attempt)` (F4): T7's first-match rule applied to
  this attempt (clock, entry, slip, trap, gap). The slip rule includes T7's "right on 4 of the
  last 5 first tries" and "easy, under half the median time", with the reason shown: "You
  usually get this type right, and this took 0:21."
* Tapping another sends `POST /api/drill/{id}/why {question_id, kind}` → `attempts.miss_kind`.
  The row is never required.

**Data.** `attempts.miss_kind TEXT` (null until corrected). `progress.causes` (T7) uses
`miss_kind` when set, and gains a `misread` segment that shows when non-zero (§3.2). R9 kinds:
trap → misconception; slip, misread, clock, entry → slip; gap → unsure. `drill.levels()`
leaves slips and misreads out of the crowd's top-mistake counts, so "most common mistake"
means a misconception.

**A fix per cause** (the summary card "Why you missed": one bar per cause, each with its
action):
* **Trap** → **Fix now** (`pool:'redo'`) and Review's Spot the trap.
* **Slip** → for the next 5 questions of that type, a soft line above Check: "Last time: a
  slip. Re-check the last step." On easy questions answered in under half the type's budget,
  Check asks "That took 0:12. Check anyway?" (Enter confirms). Plus T7's `Careful set · 8`.
* **Misread** → **Read the ask**. When 2 or more of the last 20 misses in a skill are misreads,
  or U6's `different` family is the learner's top habit, questions in that skill get a dashed
  underline on the stem's question sentence (`q.ask_span`: the last sentence ending in "?",
  else the last sentence), until 5 clean answers in that skill.
* The slip line, "Check anyway?" and the underline are study aids: they appear only where the
  shared rule allows (instant or retry practice, and review), never in tests, the challenge,
  contests, end mode before Finish or Test-like mode.
* **Clock** → two passes (P16) turns on for the next timed set, and T8's speed drill.
* **Entry** → T7's grid-in entry drill and the Grid-in rules popover.
* **Gap** → **Learn this type** (P2).

**Trend.** The SkillPanel shows "Slips: 30% of misses in Sep → 12% in Oct" when each month has
10 or more misses.

**Acceptance.**
1. A wrong answer on a template the learner got right on 4 of the previous 5 first tries: the
   verdict pre-selects "Slip: I knew it". `POST /why {kind:'misread'}` sets
   `attempts.miss_kind == 'misread'`, and `progress.causes` then counts it under `misread`.
2. Two misreads in circles, then a new circles question: `q.ask_span` is a two-integer list,
   and the browser draws a dashed underline over that span.
3. The summary's "Why you missed" bar counts add up to the first-try misses.
4. A slip-tagged miss is not counted in `drill.levels()`'s top mistake for its type.

#### P9. The next step, then vs now, and a type's trend in one line

*From: the outcomes attempt-history gap, experience #3's Then vs Now, outcomes #6's finish
lines. Effort S. Builders: F4 (`progress.steps_to`, shared with U4's "questions to Strong"),
F5 (feedback fields), S4 (verdict and summary head), F3 (`UI.history` head).*

**Why.** A near, specific goal raises effort (the goal-gradient effect). Seeing yourself beat a
type you used to miss builds the confidence that keeps a student practising daily. Their
session gives a coloured border and never ends.

**`next_step`** (one line under the verdict), the first that applies:
1. An open mistake on this template: "Left out the constant term: 1 more clean answer closes it".
2. A review (P12): "Held · back in 12 days if you keep it", or "Slipped since Sep 7 · back
   tomorrow".
3. Readiness (U8): "Count solutions is now ready · Circles 15 of 16 types ready".
4. Mastery: "Circles: 2 more first-try rights at Medium or Hard → Strong", from
   `progress.steps_to(learner, topic, STRONG, tier)`, which simulates `mastery_of` forward.
5. A run: "4 in a row in Circles · your best is 6".

**`then`** (when this answer is right and the learner has an earlier first-try miss on the
template): "Sep 12 on this type: B, used the slope as the intercept, 2:40 · today: right,
1:05", from attempts.

**Why this one** (§2.4) gains the payoff: "Open mistake · 1 clean answer closes it · Circles ≈
+5 pts".

**Attempt history head** (`UI.history`, F3, R23): above the table, the type's trend in one
line: first tries as ✕ ✕ ✓ ✓ ✓ (R20 glyphs), "median 2:10 → 0:58" (first 3 against last 3),
and "Ready · back in your warm-up Oct 2" (U8, T3).

**Summary head** adds "Mistakes closed 2 · types now ready 1 · reviews held 3 · ≈ +4 on the
table".

**Acceptance.**
1. A learner with an open trap owed 1 on t answers a fresh t question right: `next_step`
   contains "closes", and the trap is closed afterwards.
2. A learner who missed t on day 1 answers t right on day 3: `then` contains the day-1 letter
   and "today: right".
3. `progress.steps_to` has an assert self-check: a topic at mastery ≥ `STRONG` returns 0.
4. `GET /api/types/{t}/history` (R23's source) for 5 first tries returns `trend` with 5
   entries and `median_first`, `median_last`.

### B. Choosing what to practise

#### P10. Points on the table in the builder, and the route check

*From: outcomes #4, experience #4, unfair-advantage #12, the live-count and tree gaps. Effort S
(the model is U4's). Builders: F4 (`estimate.gains` from U4, `estimate.route` new), S4 (builder
columns, sort, Action bar, summary).*

**Why.** Practice pays most where a skill comes up often and the student misses it. Their
builder prices each skill by the size of their stock ("Linear functions 170"), which says
nothing about the student's score. The module-2 route is worth more than any single skill, and
nothing on their site explains it.

**Model.** U4's `estimate.gains(learner, subject)`, unchanged: per skill `{gain, per_test,
accuracy, to_strong, minutes}`, null under 30 answers. The builder reads it; it does not
recompute it.

**Route check** (`estimate.route(learner, subject)`, F4, new, pure, with an assert self-check):
* `p_tier` = the learner's first-try accuracy per tier (R8 counting), pulled toward 0.5 with
  EVIDENCE = 10.
* `m1 = (7·p_easy + 8·p_medium + 7·p_hard) / 22` (module 1's mix, `blueprint.TIERS`).
* Returns `{m1, route: m1 ≥ ROUTE_UP_AT ? 'upper' : 'lower', margin}`, null under 30 answers.

**Builder.**
* **Header meta**: "Math 560–640 · ≈ 120 points on the table", linking to Results. Under 30
  answers: "Points show after 30 answers".
* **Route line** under the header:
  * below 0.60: "Route check: about 54% on a first module. The harder module 2 needs about 60%;
    below it, Math tops out at 580." with the chip **Route-up · Easy and Medium in your 5
    weakest skills**;
  * at 0.65 or more: "About 71% on a first module: the harder module 2 is likely", with the
    chip **Practise the harder module's mix** (P11's `tier_mix: module2_upper`);
  * a "How we count" link to `/help/#points`.
* **SkillRow** gains a Worth column (80 px) after mastery: "≈ +15" in DM Mono 600, with the
  sub-line "about 3.4 of 44 · you miss ~1.6 of them". Under 5 answers: "Not measured yet".
* **DomainCard** header: "≈ +40 on the table".
* **Sort** gains "Most points"; it becomes the default once `gains` is not null.
* **Preset chip** "Biggest gains · 3 skills".
* **Coach line** names points: "Why these: Nonlinear functions ≈ +22 (5 a test, 56% first
  try) · Percentages: 2 open mistakes".
* **Action bar** line 1 ends "· covers ~21 of 44 · works on ≈ +30".

**Summary.** "What this set moved", per skill: "Linear functions 38% → 52% first try · on the
table +20 → +15".

**Copy.** Every figure says "≈" or "about". The helper line is U4's. Never shown in the
challenge.

**Acceptance.**
1. A learner seeded as in U4's first check: `GET /api/bank` skills carry `gain`, and the
   tree's default sort puts Circles above Linear functions.
2. `python3 server/estimate.py` passes a `route` assert: all-right gives 'upper', all-wrong
   'lower'.
3. A learner with 12 answers: the header reads "Points show after 30 answers" and there is no
   route line.
4. The Route-up chip selects tiers easy and medium and 5 skills.

#### P11. For me: difficulty aimed at your odds, levels that work from the first answer, test-shaped mixes, and "Check my level"

*From: experience #10, unfair-advantage #5, outcomes #9 (skill probe), the Question Score,
difficulty and adaptive gaps of all three. Effort M. Builders: T-bank (`cb-index`: College
Board's listing metadata with score bands), F4 (`server/ratings.py`: item and skill updates,
seeding, placement, the `skill_ratings` table), F5 (the zone picker, `tier_mix`, the probe
staircase), S4 (the Difficulty control, chips, summary), S8 (its contest updates call the same
function).*

**Why.** Practice moves a score fastest at a success rate around 70% ("desirable difficulty").
Their Question Score 1–7 is a fixed label, the same for every student, and their Adaptive
preference does nothing. v2's measured levels need 20 first tries per (template, tier); no
pair has more than 12, so every level cell would ship at 0. Ratings start from College Board's
own score bands and the student's own score, move with every answer and say how sure they
are, and a skill is not aimed at until its odds are real (placement).

**Model (`server/ratings.py`, F4).**
* **Item**: `item_ratings(template, tier)` (§2.5). Its prior comes from the official items the
  template maps to, and only falls back to the tier:
  * T-bank task `cb-index` captures College Board's Question Bank listing into
    `material/cb_index.json`: `{cb_id: {subject, domain, skill, tier, band}}` for every
    question in the bank (metadata only, no stem, choices or key). `band` is College Board's
    1–7 score band.
  * The prior of (template, tier) = the mean of `MID[band]` over the official items U2's map
    puts on it at that tier, where `MID` is the midpoint of level b's rating range below (L1
    800 · L2 925 · L3 1037 · L4 1112 · L5 1187 · L6 1287 · L7 1400).
  * A pair with no mapped official item keeps the tier prior 900 / 1100 / 1300.
  * So levels 1–7 are populated on day one from College Board's own bands, and ratings then
    move them.
* **Learner**: `skill_ratings(learner, topic, rating REAL, n INTEGER DEFAULT 0, seed TEXT)`,
  new, separate from `learners.rating` (Compete's single contest rating). A row is created on
  first use with a **seeded** rating, the first of:
  * U5's skill estimate or the diagnostic's for that topic (`seed 'probe'`);
  * `learners.current` (the Math score the student started from): `Rs = 1100 + 1.2 ×
    (current − 530)`, clamped to 700–1500 (`seed 'score'`). A 700 student starts at 1304:
    about 76% on a Medium prior and 51% on a Hard one;
  * otherwise 1000 (`seed 'none'`).
* **Odds**: `E = 1 / (1 + 10^((Ri − Rs) / 400))`.
* **Update**, on every clean first try (R8 clean: not a repeat, disputed, void, guess, helped
  or unsure) from practice, tests or contests:
  * `Rs += Ks(S − E)`, Ks = 32 while n < 30, 16 after;
  * `Ri −= Ki(S − E)`, Ki = max(4, 32/√(nᵢ + 1)).
  * `__main__` asserts: a right answer never lowers Rs; the two updates are symmetric in E.
* **Backfill**: replays attempts in order at startup, once.
* **Level** from Ri: L1 < 850 ≤ L2 < 1000 ≤ L3 < 1075 ≤ L4 < 1150 ≤ L5 < 1225 ≤ L6 < 1350 ≤ L7.
  The band priors spread the official-mapped types over all seven levels; the unmapped
  fallback priors land easy on L2, medium on L4, hard on L6. A level reads "rough" while
  nᵢ < 20 and "measured" after (U5's words).
* **Placement** (per skill): a skill is *placed* once it has 8 clean first tries
  (`skill_ratings.n ≥ 8`), or a Check my level, a U5 probe or the diagnostic has covered it
  (`seed 'probe'`). The zone picker only aims at placed skills (Picker, below).

**Builder: Difficulty** (replaces the LevelStrip block, §3.1 entry 12).
* **Seg** "Standard · For me". For me is the default (pref `zone`, default `stretch`). U15's
  Test-like bundle sets `zone: off` (Standard, all tiers).
* **For me**: Warm-up (80%+ likely) · Stretch (60–80%) · Challenge (35–60%). Helper: "Chosen
  from how you've done in each skill and how hard each type has been for everyone."
* **Standard**: the three tier toggles as today, Adaptive (R33), and a **Mix** seg: `Any ·
  Like module 1 (7/8/7) · Like the harder module 2 (3/8/11)` (`tier_mix`). Helper for the
  harder mix: "Aiming above 580? The harder module 2 is 11 Hard of 22."
* **Levels** 1–7: a second row of cells, always enabled, each counting the selection's types
  at that level, with the checkbox "Include rough levels · 312" (on).
* **TypeRow**: "L4 · rough (6)" or "L4", and "your odds ~72%".

**Picker (F5).**
* Order holds: repairs, then open traps, then review slots (P12), then zone.
* **Cold start.** A slot whose skill is not placed is served Standard: all tiers, filled in
  module 1's 7 / 8 / 7 proportions across the set's unplaced slots (the `tier_mix` rule
  below). The strip chip reads `For me starts after 8 answers here · 5 to go` in place of the
  zone name, and the builder's Difficulty helper lists the unplaced skills with **Check my
  level** beside them. So a new learner, or a TopTierPrep switcher who scores 700, never gets a
  run of Easy questions: they get the test's own mix until their odds are real.
* Zone picks, among the placed selection's (template, tier) pairs (`kinds()`), the one with
  the smallest `|odds − centre| + 0.05 × uses in this set`. Centres: 0.87, 0.70, 0.47.
  `ponytail:` a linear scan over at most 1,158 pairs per serve; index by topic if it shows in
  profiles.
* `tier_mix` fills slot tiers in `blueprint.TIERS[...]` proportions (largest remainder, over the
  tiers the selection can serve; the preview names any tier it cannot).
* Each served question stores `q.odds`.

**Check my level** (outcomes #9, as U5's probe for one skill).
* SkillPanel button `Check my level · 8 questions · ≈ 12 min`, and a preset chip `Check 3
  skills I haven't tried` (U5's Sharpen, restricted to untried skills).
* `POST /api/drill {source:'probe', topics:[t], count:8}` (U5's source, now taking `topics`).
  F5 runs a staircase: start Medium; after a right, step up (the same template's harder tier,
  else a P18 sibling); after a miss, step down. One type per skill label where it can. End-mode
  feedback, stopwatch on.
* Placement answers update `skill_ratings` with Ks = 32, so the skill's odds settle after one
  probe.
* **Result card** (the summary's first block, after U5's "What changed"): "Circles: solid on
  Easy and Medium, breaks on Hard · missed: arc fraction (gave the minor arc), equation from
  the centre", with `Fix these 2` and `Practise Circles at Hard`.

**Session.**
* The strip chip names the zone before answering ("Stretch"). The number waits: Details reads,
  after answering, "Level 4 of 7 · measured from 212 answers · your odds were 68% · everyone
  58%".
* **Summary**: "Expected 6.4 right · you got 8 · +1.6 above expected", from the sum of
  `q.odds`, for For-me sets only.

**Acceptance.**
1. A fresh learner on the shipped db: every `/api/bank` type has `level` in 1..7 and `rough`
   true, and at least one type sits at each level 1–7. `POST /api/drill
   {topics:['linear_functions'], levels:[1], unmeasured:false}` (where `unmeasured` now means
   rough) returns 409 naming 'level 1'.
2. After one clean first try on (t, tier), `item_ratings.n` has risen by 1 and `skill_ratings`
   has a row for the topic. A guessed or hinted answer changes neither.
3. A learner placed in circles (8 clean first tries): `POST /api/drill {topics:['circles'],
   zone:'stretch', count:5}`: each `q.odds` is within 0.15 of 0.70, or is the closest
   available in the selection (a check computes the minimum).
4. `POST /api/drill {topics:['linear_functions','circles'], tier_mix:'module2_upper',
   count:22}` → 3 easy, 8 medium, 11 hard.
5. `POST /api/drill {source:'probe', topics:['circles'], count:8}`: `cfg.feedback == 'end'`, and
   after a scripted right on slot 1 the next slot's tier is above slot 1's.
6. `python3 server/ratings.py` exits 0.
7. A fresh learner with default settings, 10 questions over three skills: at least 3 are
   Medium or Hard, and the strip reads "For me starts after 8 answers here".
8. A learner with `current = 700`: their new `skill_ratings` rows are created with `seed
   'score'` and rating 1304. After 8 scripted answers per skill that leave each rating within
   50 of 1304, a default 10-question set over two of those skills serves at least 2 Hard.
9. Every item in `material/cb_index.json` has `band` in 1..7, and `item_ratings` priors for a
   template mapped to band-7 items are at least 1350.

#### P12. Retrieval: a final round, review slots in every set, and marks that come back

*From: outcomes #2 (keep-warm slots), outcomes #5 (the final round), the outcomes mark gap, and
today.md T3, whose schedule this reads. Effort M. Builders: F4 (T3's
`progress.warmup_candidates` gains `marked`), F5 (review slots, the final round, pool `review`
reads T3), S4 (settings, tree marks, forecast, summary).*

**Why.** Spaced retrieval is the most robust retention effect known, and mixing old types into
new sets also trains recognising which kind of question is in front of you. Re-asking a miss at
the end of the set, after other questions have cleared working memory, shows whether the fix
took. TopTierPrep's Math bank has no schedule: a solved item stays solved. v2's "due" is a flat
10-day rule, and two clean answers two minutes apart close a mistake.

**One schedule.** T3's `progress.warmup_candidates(learner, tz)`, derived from attempts with no
new table: check-ins due (R9: 3, 10 and 30 days after a fix), then fading types (a counted
clean right is ≥ 20 h after the last counted one; intervals by counted rights k: 1 → 2 days, 2
→ 5, 3 → 12, 4+ → 30), then keep-warm. This file adds a candidate kind **`marked`**: a question
flagged (R5) 2 or more days ago whose template has no right first try since the flag. It comes
back as a fresh twin, so a mark does something even if the student never opens the list.

**Review slots** (builder setting **Mix in reviews**: Off · 2 per set · 20%, pref `review_mix`,
default 20%; checkbox **Only from the skills I picked**, pref `review_from`, default on. Ready
cards, Coach's pick and Up next pass `any`).
* Slots go at positions 3, 6, 9 and so on, never 1–2, on fresh seeds: `round(count × 0.2)`, at
  least 1 when anything is due; endless sets take every 5th. With nothing due, a slot goes back
  to the set's own selection.
* Each carries `why.kind = 'due'` (or `check`, `marked`), the strip chip `Review`, and a clock
  glyph on its rail segment.
* Why line: "Warm-up: right 8 days ago, held twice · back in 12 days if right" (T3's k and
  interval), or "You marked this type Sep 20".

**The final round** (pref and body field `final_round`, default true; fixed sets only; off in
end mode, where misses become the Fix set, and in the challenge).
* When the last slot is answered, Next reads `Final round: the 3 you missed, new numbers ·
  Start` with a quiet `Skip it` (which finishes).
* Start appends one fresh-seed slot per template first-try-missed in this set (repaired ones
  included), in the order missed, at the same tier, at most 5, with `why.kind = 'final'`. The
  rail shows them as a grouped block headed `Final round · 3`.
* Clean answers pay down `owed` as usual, so a repair plus a clean final round closes a
  mistake, and R9's 3-day check-in then tests whether it held.
* The Action bar's line 2 says `final round on`.

**Due SAT words in the set** (their "Include Vocab Review", done so it actually reviews).
* Builder setting (in Mix in reviews) **Mix in due SAT words**: `Off · 2 per set · All due`
  (pref `prefs.practice[subject].words_mix`, default Off). Decision 2: the EBRW word list and
  transitions only, never math language.
* Word cards go at set breaks: after questions 5, 10, 15 and so on, one per break, and any
  left over after the last slot. Never in timed sets, end mode, tests, the challenge or
  contests.
* A word card is S9's due review in its ladder format (W7), rendered in `UI.workspace` quiz
  mode. It sits in `served` with `kind:'word'`, like an example card: not a slot, not in
  `total`, accuracy, mastery, the score line, the rail's counts or `attempts`.
* Serving and grading are S9's: `words.due_items(learner, n)` returns public items with a
  token; `POST /api/drill/{id}/word {token, answer, ms}` calls `words.grade_item`, which files
  one `word_reviews` row and moves the word's box, exactly as a Words run would.
* The rail shows a small `Aa` tick between segments for each word card. Summary: "SAT words ·
  2 reviewed · 2 held", and the quiet "SAT words · 10 more due" action stays.
* Acceptance: with `words_mix = 2` and 5 words due, a 10-question set serves exactly 2 word
  cards (after questions 5 and 10); `attempts` gains no rows for them; after both are answered
  right, `words.today_summary(...).due` has dropped by 2 and `total` is still 10.

**Builder.**
* **Questions from**: "Fresh numbers on types due for review" reads T3. Its helper reads "3
  due now · 5 more this week · next 14 days ▸"; the link opens a `UI.pop` with a 14-bar
  `UI.barChart` from T3's `progress.due_forecast`.
* **Tree**: "Due 3" on the SkillRow mastery cell; TypeRow "Due today" or "Back Oct 2 · held
  2"; Sort gains "Most overdue". A Strong row adds "held after 16 days" when any of its types
  held a gap of 12+ days, else "not yet tested after a gap" (R37's word is unchanged).

**Summary.** A "Retrieval" card: "4 reviews · 3 held · 1 slipped (Circles: equation from
centre)" and "Final round 2 of 3 · Circles still open".

**Acceptance.**
1. A 10-question set with 2 first-try misses on different templates, `final_round` on: after
   slot 10, Start makes `total == 12`, and slots 11–12 have those templates, new seeds and
   `why.kind == 'final'`.
2. The same set in end mode never appends a final round.
3. A learner with 3 fading templates in circles: `POST /api/drill {topics:['circles'],
   count:10}` (default `review_mix`) serves at least 2 questions with `why.kind == 'due'`, none
   at positions 1–2.
4. A flag 3 days old with no right answer since: `warmup_candidates` includes that template
   with kind `marked`.
5. `POST /api/drill/preview {pool:'review'}` counts exactly T3's fading templates with no open
   trap.

#### P13. Official-question twins: College Board IDs, pasted questions and outside misses

*From: experience #1, unfair-advantage #1, the bank-toggle and Bluebook gaps of all three.
Effort M (the map is U2's). Builders: F5 (pool `official` in `drill.py`, the twin search; the
`cb_id` map is U2's `types.py`), S4 (builder field, chips, session line, Your sets tab, summary
grouping).*

**Why.** College Board's Question Bank and Bluebook are the most test-like practice there is,
and students already use them. Their Question Bank tab serves each official item once; after
that, "Redo" is the same memorised question. U2 already maps 911 official items exactly onto
served templates, and P11's listing index covers the rest of College Board's bank by skill,
tier and band, so any official question a student missed can become unlimited twins at the
same tier (with the same traps where the map is exact), without showing any College Board
content. Most students never exhaust 1,921 items; the point is that each official miss becomes
endless practice aimed at the trap that caught them, which a fixed bank cannot offer.

**Builder.**
* **Search accepts IDs and pasted questions.**
  * One or more 8-hex IDs (`^[0-9a-f]{8}$`), separated by anything (a pasted URL or list
    works), switch the field to "Match official questions".
  * Text over 60 characters switches it to "Match a question" and calls U2's
    `POST /api/types/match {text}`.
  * A TopTierPrep ID (`^\d{5,6}-[A-Z]{2}$`) reads "That's a TopTierPrep ID. Paste the question
    text instead."
* **Every College Board ID resolves.** Besides U2's exact map (911 IDs onto templates), F5
  reads P11's `material/cb_index.json`, which lists every question in College Board's bank
  (about 1,900 Math) with its skill, tier and band. So a Math ID outside the exact map still
  resolves to its skill and tier, and the twin search takes that skill's templates at that tier,
  closest in item rating to the band's midpoint (P11's `MID`), with the text match (if the
  student pasted text too) ranking them.
* **Result list**, one row per ID: "84664a7c · Linear functions · Easy · A line from a table ·
  Exact", or "Close: twins of Linear functions at Medium" (the index), or, for a Reading &
  Writing ID, "Reading & Writing question: logged for the R&W bank" (P15). "Not in our map" is
  left only for an ID in neither the map nor the index, and then U2's paste-or-pick path runs.
  Header "3 of 3 found". A Seg "Twins of each: 1 · 3 · 5" (default 3). The pill **Practise twins
  · 9 questions**.
* **Row actions** for a single match: **Practise 3 twins**; **See the traps** (P2); **Log it as
  a mistake** (U2's quick sheet, prefilled with the `cb_id`, asking for the letter picked).
* **Questions from** gains "Fresh numbers on mistakes I logged from outside · 4" (`pool:'redo'`,
  traps with `source 'outside'`). With the Repeats line, this is the answer to their Bluebook
  include / exclude.
* **TypeRow chip** "Built from 11 official questions" (U8's `official` count). **Settings
  checkbox** "Only types built from official questions (N of 386)" sends `has: ['official']`.
* **Official practice starts and ends in the builder.** Each SkillRow's panel carries
  "Official questions on College Board · 142" (the index's count for that skill), which opens
  College Board's own Question Bank in a new tab, filtered to that skill where their URL
  allows, else at the bank with the skill named. Under it, a **Paste what you missed there**
  field (IDs or text) feeds the result list above, so a student does an official set there and
  turns every miss into twins here in one paste.
* **Deep link** `/practice/?cb=84664a7c,06fc1726` presets the field; it never auto-starts.

**Server (F5).** `POST /api/drill {pool:'official', ids:[cb_id ≤ 50], each: 1–5}`.
* For each ID, from U2's map: the template, the official tier and the official format.
* The twin search walks up to 40 seeds of that template at that tier and format. It prefers a
  card sharing 2 or more norms with the official reproduction (`Source.build(Random(0))`), then
  1, then any valid card. It rejects a card whose params equal the pinned params, or whose stem
  equals the reproduction's.
* `q.why = {kind:'official', detail:'Twin of College Board question 84664a7c'}`;
  `cfg.official = [ids]`. No response carries official stem text (U2's rule and check).
* An index-only ID gets `why.detail 'Close twin of College Board question 1a2b3c4d
  (Linear functions, Medium)'`, so the student knows it is the skill and tier, not the exact
  form.

**No practice question copies a College Board question** (their Bluebook Exclude, for every
pool). At warm-up F5 builds `PINNED`, the set of `(template, frozen params)` from every
`Source`'s pinned call, and the normalised stems of those reproductions. `_fresh` rejects any
card whose params or normalised stem match one, in every pool, source and set kind, and calls
`b.keep` so the seed advances (a rejected seed is skipped, never re-tried). The Repeats line
(§1.7 item 10) says so: "No practice question copies a College Board question."

**Session.** Strip chip "Twin of CB 84664a7c". Details row "Modeled on: College Board 84664a7c
(and 10 more of this type)".

**Summary.** Rows grouped by ID: "84664a7c · 2 / 3 twins right".

**Your sets.** A tab "Official questions you brought · 12": each ID with twins done and the
right rate ("9 of 12 now right on twins"), and **Practise again**. `GET /api/drill` adds
`official: [{cb_id, template, twins, right, last}]`, aggregated from sets with `cfg.official`.

**Acceptance.**
1. `POST /api/drill {pool:'official', ids:['23c5fcce'], each:3}` → 3 questions, each on the
   template U2's map gives, with `difficulty` equal to the key file's tier and `why.kind ==
   'official'`.
2. None has params equal to the pinned Source params, and no response contains a 40-character
   substring of the official reproduction's stem.
3. Browser: pasting "23c5fcce 84664a7c" into Search shows "2 of 2 found" and "Practise twins ·
   6 questions".
4. After finishing, `GET /api/drill` lists `official[0].cb_id == '23c5fcce'` with `twins == 3`.
5. `POST /api/drill/preview {has:['official']}` counts only templates whose U8 `official` count
   is at least 1.
6. 20 random Math IDs from `material/cb_index.json` that are not in `material/keys`: each
   `POST /api/drill {pool:'official', ids:[id], each:3}` returns 3 questions in the index's
   skill at the index's tier, and none reads "Not in our map".
7. `python3 tools/pinned_check.py`: for every template with a `Source`, seeds 0–5000 through
   `_fresh` never yield a params tuple or normalised stem in `PINNED` (a standalone check, a
   few minutes; not in test_flow).
8. Browser: a SkillPanel shows "Official questions on College Board ·" with a count, and
   pasting two IDs into its field shows the result list.

#### P14. The type map: all 386 question types as a map you fill in, and Finish this skill

*From: experience #9, outcomes #6 (type states, "Finish this skill", "Close my gaps"), the
outcomes tree gap. Effort M. Builders: F1 (U8's atlas grid as `UI.atlas` in kit.js, shared with
S1), F5 (source `finish`), S4 (the builder view, selection and SkillPanel button).*

**Why.** Their tree stops at 19 skills with item counts. A student can't see which kinds of
Nonlinear-functions question they have never met, or which they have beaten. Ours shows every
type's state, and each skill gets a concrete finish line (the goal-gradient effect) with the
shortest set that reaches it.

**States** (U8's words, one vocabulary with Me): **unmet** (dashed) · **met** (`--tile-2`) ·
**ready** (answered right on the first try twice, R8 counting; ink with ✓) · **open mistake**
(orange dot) · **being fixed** (U3; hatched). Overlays: **due** (T3 fading; a small clock) and
**selected** (2 px ink ring). The legend counts each: "Met 41 of 386 · Ready 12 · Open 4 · Due
5 · Unmet 345".

**View.** The tree header's seg "Skills · Map · Habits". Map is one row per skill under the
domain headers, with `UI.atlas` cells of 16 px and 3 px gaps, largest U8 weight first. On a
phone they wrap at 18 per line (339 px), so there is no horizontal scroll. Each row ends "8 /
23 ready".

**Selecting.** A click toggles a cell. A mouse drag paints; on touch, long-press then drag. The
selection feeds the same `templates` the list uses. **Quick picks** above the map: "Select
unmet (345) · open mistakes (4) · due (5) · slow (P16)"; each also sets its pool.

**Popover** (focus or hover; `role=grid`, arrow keys move): the name and about line; the record
("met 6 · right 5 · last Sep 21"); your odds (P11); U8's "9 official questions take this form";
**Try one** (R24 `try`) · **See the traps** (P2) · **Learn this type** (P2) · **Add to
selection**.

**Finish this skill.**
* SkillPanel button `Finish Circles · 14 questions · ≈ 22 min`, shown while any type in the
  skill is not ready, or has an open mistake or is due.
* `POST /api/drill {source:'finish', topics:[t]}` → F5 builds `segments` (U1's field): open
  traps on the topic's templates (1 each), then due types (1 each), then met-but-not-ready types
  (2 − rights each), then unmet types by U8 weight (1 each), capped at 30. The preview returns
  the count and minutes (P16 budgets).
* Summary: "Circles: 21 of 23 types ready (was 14) · 2 to go", with **Finish Circles · 3**.
* When every type in a skill is ready, the row gets a check and a one-time toast, "Every
  Circles type ready · 16 of 16" (kept once per skill in `learners.ach_seen`).

**Final stretch.** Within 14 days of the exam (U15's stage), the legend adds "Unmet and common:
5 types · ≈ 4% of the test" (unmet types in the top half of U8 weight) with the quick pick
**Meet them · 5**. Rare unmet types are not pushed, as T13 drops them.

**Acceptance.**
1. Browser 1280: Map shows 386 cells, and the legend counts add up to 386.
2. "Select unmet", then Start → `cfg.pool == 'untried'`, and the served templates are among the
   selected cells.
3. `POST /api/drill {source:'finish', topics:['circles']}` for a learner with 1 open circles
   trap: slot 1's template is the trap's; `total ≤ 30`; the preview's count equals `total`.
4. Browser 390: `scrollWidth <= 390` with Map open.

#### P15. Fast starts: a Ready row, one-line sets, time boxes, saved presets and the subject switch

*From: outcomes #14 (ready sets), experience #12, the one-screen and volume gaps of all three,
the unfair-advantage presets and subject gaps. Effort S. Builders: F2 (`UI.parseSet`, shared
with the palette and U24; `next.queue`), S4 (the builder wiring), F4 (prefs `presets`), S7
(minutes left today), S9 (Words counts).*

**Why.** Theirs needs 5 to 7 controls on every visit. A daily habit needs a start with no
decisions, and the most common request, "10 hard circles, timed", should take one line. Students
also plan in minutes more than in question counts.

**Ready row** (above the preset bar; up to 4 cards in a row, 2 per row on a phone):
* Cards 1–3 are U1's `GET /api/next?limit=3` (one queue with the chrome and Today), each with
  the title, "3 q · 4 min · ≈ 6 pts", the reason line, **Start** (it posts the item's `start`
  body) and a quiet **Edit** (it loads that body into the tree and settings below, with the note
  "Settings from Up next").
* Card 4, **Again: your last set** (`{again: sid}` of the newest finished set), when one exists.
* A card with nothing to serve shows its reason in place of Start. Loading: two skeleton lines
  per card. Server down: the row hides; the builder still works.

**Command line** (the Search field; `/` focuses it on `/practice/`).
* `UI.parseSet(text) → {body, chips, unknown}` (F2, the palette's parser, exported).
* **Tokens**: numbers 1–120, `endless`; easy, medium, hard, grid-in, mc; timed, pace, untimed,
  "N min"; mistakes, due, untried, marked, saved, outside; "test mode", retry; warm-up,
  stretch, challenge; "mix-up"; skill names and TOPICS aliases; type names; CB IDs (P13).
* **Preview line**: removable chips, "Circles × · Hard × · 10 questions × · Timed 16 min ×",
  then "→ 10 hard Circles questions, timed 16 min · Enter to start". Unrecognised words stay a
  type search.
* **Keys**: Enter starts (the same POST as Start). Shift+Enter applies the line to the builder
  without starting. ↑ in an empty field recalls the last 10 lines (`localStorage satf.cmd`, in
  try/catch). **Enter in the empty field starts Ready card 1**, and the helper under the field
  says so: "Enter starts: Check-in · diameter vs radius · 3 q".

**Time boxes.**
* The Questions Seg gains **15 min · 30 min** → `{box: 15, count: null}` (U1's field and box
  clock). The helper reads "about 11 questions for you", from P16 budgets over the selection.
* **Fit to today's plan** appears when the active plan has minutes left today (S7's
  `plan.today_summary().minutes_left`); it sets `box` to those minutes, clamped to 5–60.

**Saved presets.** **Save as preset** at the end of the preset bar stores the current settings
and selection: `prefs.presets`, at most 8 of `{name ≤ 24, body}`; a 9th returns 422. Saved
presets show as chips after Custom, each with ⋯ Rename / Delete. **Copy link** copies the §1.10
deep link of the current settings.

**Subject switch.** The page header's eyebrow becomes a seg: "Math · Reading & Writing".
* Reading & Writing shows a panel with three parts, and no dead end:
  1. **Practise official R&W questions now.** The 10 R&W skills under their 4 domains
     (Information and Ideas: Central Ideas and Details, Inferences, Command of Evidence;
     Craft and Structure: Words in Context, Text Structure and Purpose, Cross-Text
     Connections; Expression of Ideas: Rhetorical Synthesis, Transitions; Standard English
     Conventions: Boundaries, Form, Structure, and Sense), each row with its count from
     `cb_index` ("Official on College Board · 212") opening College Board's bank filtered to
     that skill where their URL allows.
  2. **Log it** (a missed R&W question from there, Bluebook or a book): a College Board ID or
     pasted text, the skill (pre-filled from the index for an ID), and the letter picked.
     `POST /api/mistakes/log {subject:'rw', cb_id?, text?, skill, letter?}` stores it in the
     same outside-mistakes store as Math (U2) with `subject 'rw'`, so it shows in Review's
     Outside list now and becomes twins when the EBRW bank ships. A pasted R&W ID in the Math
     search reads "Reading & Writing question: logged for the R&W bank" with this form open.
  3. **Words drills ready now**: Words' drills with their counts (S9's
     `words.today_summary`: "SAT words · 12 due", "Transitions · 70"), each with Start →
     `/words/`. Decision 2: SAT Reading & Writing vocabulary only, no math-language deck.
* Closing line: "R&W practice questions come with the R&W bank. What you log here is waiting
  for it." This row stays below TopTierPrep until that bank exists.
* `/api/bank` takes `?subject=math` and returns `subject`.
* The practice summary's quiet actions add "SAT words · 12 due" when S9 reports due reviews.

**Acceptance.**
1. `UI.parseSet('circles hard 10 timed')` returns `body` with `topics:['circles']`,
   `tiers:['hard']`, `count:10`, `timing:'pace'`, and 4 chips.
2. Browser: `/`, type "percentages 5 grid-in", Enter → `/practice/session/?id=`, and the state
   has 5 slots, all `fmt 'spr'`.
3. "15 min" → the set has `cfg.box == 15` and `count == null`.
4. `PUT /api/me {prefs:{presets:[…9 items]}}` → 422 naming `presets`.
5. With `GET /api/next` returning a `checks` item first, Enter in the empty command line opens
   a session whose `cfg.pool == 'checks'`.
6. The Reading & Writing seg shows the 10 R&W skills with College Board links, the Log it
   form and the Words drills, and no Math skill tree.
7. `POST /api/mistakes/log {subject:'rw', cb_id:<an R&W ID from cb_index>, letter:'B'}` →
   200; the entry lists in `GET /api/review/counts`' outside count with `subject 'rw'`, and
   touches no Math mastery or trap.

#### P16. Fair time budgets per question type: the stopwatch, fluency, time sinks and two passes

*From: outcomes #7, experience #5, unfair-advantage #9, the timer, stopwatch and pace gaps of
all three. Effort M. Builders: F5 (budgets in the `drill.levels()` cache, `per_q`, the sprint
pool), F4 (fluency fields), F3 (stopwatch bar, skip chip, pace delta), S4 (summary Time card,
passes, Speed view), F1 (U7's `UI.quadrant`).*

**Why.** At 95 s a question, points are lost to time sinks and unfinished modules as much as to
not knowing. A flat 95 s (v2) calls every hard question slow and every easy one fine. Their 6
minutes a question trains the wrong pace, and their stopwatch resets on reload.

**Budgets (F5).**
* `budget_ms(template, tier)` is the crowd median of clean first-try rights when n ≥ 20,
  clamped to 0.6–1.6× the tier default.
* Otherwise the tier default of the template's subject: for Math **Easy 65 s · Medium 95 s ·
  Hard 126 s**. On module 1's 7 / 8 / 7 mix that is 2,097 s of 2,100, so R34's 95 s average
  holds. `TIER_BUDGET[subject]` is derived from `blueprint.SECTION[subject]` (the header's
  subject rule), so R&W gets its own when it ships.
* Served questions carry `budget_ms`. `/api/bank` types carry `{budget_ms, median_ms, best_ms,
  fluent, slow_right}`.

**Session.**
* **QStopwatch**: "0:48 / 1:05", with a thin bar filling to the budget and a tick at the
  learner's median on this type. Past the budget it turns amber-deep and gets a dot (the pace
  alert moves from a flat 1:35 to the budget).
* **Test pace: the clock is the plan's budget, and it follows the set.** `drill.py` serves
  lazily, so the clock cannot be the sum of questions not yet chosen. Instead:
  * At create, the picker commits a tier to every planned slot, `cfg.plan: [tier] × count`
    (`tier_mix`, the cold-start mix and the zone's expected tier already decide this; a zone
    slot plans the tier its odds pick at create time).
  * `seconds_left` at start = the sum of `TIER_BUDGET[subject][tier]` over `cfg.plan`,
    rounded up to the minute. Helper: "16:00 for these 10 · paced to each question's
    difficulty". T8's speed drill uses the same.
  * When the served question's budget differs from its slot's plan (the zone or R33's step
    moves the tier, or the crowd median differs from the tier default), `seconds_left` moves
    by the difference at serve time.
  * **Every added slot adds its own budget**: a repair, the final round, `/more` on any axis,
    Practise this trap, the Learn ladder's 3 slots, Twins of these, and P25's replacement.
    Under the timer a line reads "+1:05 for the repair" for 3 s, and the RunBar's caption keeps
    "incl. +3:10 added". The final round in a timed set is timed the same way.
  * P25: a voided question gives back the time spent on it, and its replacement takes over the
    slot's budget. A Learn example card pauses the clock while it is on screen.
  * `cfg.clock_log: [{at, delta_ms, why}]` records each change, so the pace delta, "N Hard
    left" and Time sinks are always measured against the clock the student actually had.
* **RunBar pace delta** (timed sets): "1:10 ahead of pace · 3 Hard left" or "0:40 behind",
  from the answered budgets minus the time spent; updated per answer, not per second.
* **Verdict word**: "Right · 0:48 · fluent", "Right · 2:10 · slow (budget 1:05)", "Incorrect ·
  0:12 · rushed" (under 25% of the budget). A right under the learner's previous best on the
  type adds "New best on this type: 0:58".
* **Two passes** (pref `two_passes`, default on; timed sets only). Past 1.5× the budget, a chip
  under the choices reads "Skip for now? S". The summary compares "Pass 1: 14 answered · 12
  right · 1:02 average" with "Pass 2: 4 answered · 2 right".

**Fluency.**
* A type is **Fluent** when its last 2 clean first-try rights were each under budget. It is
  **Right but slow** with 3+ first tries, 80%+ right, and a median right time over budget.
* SkillRow: "Fluent 6 of 23 types". Sort gains "Slowest vs budget". TypeRow: "Fluent · best
  0:48" or "Slow: right but 2:10 median".
* **Preset "Fluency sprint · 5 types"**: the Right-but-slow types. Each question counts down
  from the budget (`per_q: 1.0`); each on-time right tightens that type's target for the rest of
  the set by ×0.85, down to 0.6× the budget (`cfg.target`), shown as "Beat 1:12 (your median
  1:48)". Order Mixed.

**Speed view** (the SkillPanel's "Types · Speed" toggle): U7's `UI.quadrant` with one dot per
type that has 3+ first tries. x = median time ÷ budget (log scale, 0.5× to 2×); y = first-try
rate; lines at 1× and 70%. Four quadrants, each with a count and one action:
* **Fluent** → Keep warm (the due pool);
* **Careful** (slow and right) → **Beat the clock**: a per-question countdown at 90% of the
  budget (`per_q: 0.9`); going over is shown, never blocking;
* **Rushing** (fast and wrong) → **Slow down**: answers under 30% of the budget ask "That took
  0:12. Check anyway?" (Enter confirms);
* **Stuck** (slow and wrong) → Learn this type (P2).
It has a hidden data table; on a phone it is full width and 300 px tall.

**Summary: Time card.** One bar per question against its own budget tick ("Over budget 2 ·
under 8"). **Time sinks · 3**: the questions over 2× budget, "6:40 on 3 questions, 2 wrong
anyway. Moving on at the budget would have left about 4 minutes, enough for 3 more questions.",
then **Practise these at pace**. When it holds: "Your wrong answers came 0:31 faster than your
right ones", with **Slow down · 8**.

**Acceptance.**
1. A fresh db: a served medium question has `budget_ms == 95000`, a hard one 126000.
2. `POST /api/drill {timing:'pace', count:10}`: `seconds_left` at start equals the sum of the
   planned budgets over `cfg.plan`, rounded up to the minute. After a first-try miss with
   repairs `next`, `seconds_left` rises by that repair's `budget_ms / 1000`, and `clock_log`
   has an entry with `why 'repair'`.
3. Two clean rights on t, each under budget → the `/api/bank` type has `fluent == true`.
4. Browser: a timed question left open for 1.5× its budget shows "Skip for now?".
5. A right answer faster than the learner's `best_ms` on the type: the verdict contains "New
   best on this type".
6. A set with one answer over 2× budget lists it under "Time sinks · 1".
7. A timed 10-question set with 2 first-try misses (repairs `next`) and the final round
   started: when the first final-round question is served, `seconds_left` equals the start
   value, minus the time spent, plus the 2 repairs' and the 2 final-round slots' budgets.

#### P17. Mix-up sets: look-alike types interleaved, so you learn which method applies

*From: outcomes #12. Effort S. Builders: F5 (`order:'mixup'`, `blueprint.lookalikes`), S4 (the
entries and the summary block), F3 (reads T3's `cfg.hide_skill`).*

**Why.** Interleaving pays off most when types are easy to confuse: percent of, percent change
and the whole from a part; arc length, sector area and arc fraction. Blocked practice lets a
student use the method the last question used; a mix makes them choose it, which the test
always asks for. Mixed order interleaves across skills; this interleaves look-alikes inside one.
TopTierPrep serves whatever the skills return, and their items can't be paired by structure.

**Look-alikes (`blueprint.lookalikes(t, k=3)`, F5, cached with `kinds()`).** Templates in the
same topic ranked by norms shared with t (at least 1), then, if fewer than k, templates in other
topics sharing 2 or more norms.

**Entries.** SkillPanel `Mix it up · 8`; TypeRow ⋯ `Mix it up with look-alikes`; the Order seg
gains `Mix-up` (enabled with 1–6 types or one skill selected; the reason shows otherwise); the
command line's "mix-up".

**The set.** `order:'mixup'`: the chosen types plus their look-alikes, round-robin, shuffled,
never one template twice in a row; fresh seeds; instant feedback; repairs next; `cover` All
(P5, changeable); T3's `cfg.hide_skill = true`, so the strip reads `Mix-up` and the type name
appears only after Check.

**Summary: Mix-up block.** Per type: "Percent change · 2 of 4 here · 90% usually", from the
learner's first-try rate on the type outside mix-ups. When 2 or more types are 20 points below
usual: "In a mix you choose the method, not just use it. Lower here on 2 types." with **Mix it
up again in 3 days** (P19's `rematch_due`).

**Acceptance.**
1. `POST /api/drill {templates:['pct.change'], order:'mixup', count:8}` → at least 3 distinct
   templates, all in `lookalikes('pct.change') ∪ {'pct.change'}`, with no two adjacent equal.
2. `GET /api/drill/{id}` has `cfg.hide_skill == true`; at 1280 the strip reads "Mix-up" before
   Check and the type name after.
3. `python3 -c "from server.blueprint import lookalikes; assert 'pct.change' not in
   lookalikes('pct.change')"` exits 0.

### C. Again, done right

#### P18. Twins on any axis, and easier or harder for every type

*From: unfair-advantage #4, the outcomes adaptive and "another one like this" gaps. Effort M.
Builders: F5 (`/more {axis}`, `blueprint.siblings`, the axis survey in `kinds()`), F3 (the split
button), F2 (`T`, `Shift+T`).*

**Why.** "Another like this" is our signature, but v2's easier and harder need a template that
spans tiers, and only 59 of 386 do, so for most students "harder" would never appear and R33's
adaptive step would silently do nothing. Answering a different quantity than asked is the
largest trap family measured (849 reasons over 19 topics), and "same setup, a different
question" attacks it directly. A grid-in twin takes away the choices a student may have leaned
on. They have no second copy of any item.

**Siblings (`blueprint.siblings(t, step)`, F5).** For step ±1: the same template at the
adjacent tier when it has one; else templates in the same topic sharing a skill label at that
tier (156 of 386 types get at least one direction this way); else the same topic's template at
that tier with the most shared norms. Used by `/more {axis: easier | harder}`, R33's adaptive
step, the probe staircase (P11) and T4's "a tier up".

**Control.** After every reveal, in the ReviewSheet, in Review (R23) and on the TypeRow ("Try
one ▾"): a split button.
* **Another like this** (`T`): the same trap with new numbers.
* Its menu (`Shift+T`), listing only what this template supports:
  * **Easier** · **Harder**, labelled when a sibling is used: "Harder: another Circles type
    (arc length)";
  * **As a grid-in, no choices to lean on**;
  * **Same setup, a different question** ("You found the side; now find the perimeter").

**Server.** `POST /api/drill/{id}/more {question_id, axis: same | easier | harder | grid | ask}`.
* `grid`: the same template on a **fresh seed** with `fmt='spr'`; never the same seed, whose key
  the student has just seen.
* `ask`: the same seed's params passed back with another `ask` value; the survey confirms that
  the params survive and the stem changes (29 templates today).
* An unsupported axis returns 409.

**Survey** (`blueprint.kinds()`, at warm-up): `kinds()[t]['axes']` records `grid` when the
template emits SPR at any tier, and `ask` with its values after one confirmed flip per value.
T-bank grows `ask` coverage by recording `ask` in `params` (a check prints "n of 85 ask
templates keep their setup").

**Display.** The strip reads "Twin · as grid-in · of question 6". The summary's By type counts
twins per axis. R33's step reads "Stepped up to Hard: Arc length".

**Acceptance.**
1. `/more {axis:'grid'}` on an MC question of a template with SPR in kinds: the next question
   has the same template, `fmt 'spr'` and a different seed.
2. `/more {axis:'ask'}` on a confirmed template: params equal except `ask`, and the stem
   differs. On an unconfirmed template → 409.
3. `/more {axis:'harder'}` on a one-tier medium template with a same-label hard sibling: the
   next question is that sibling at hard.
4. `python3 -c "from server.blueprint import siblings; …"` asserts that at least 150 templates
   have a same-label sibling or a second tier.
5. Browser: `Shift+T` opens the menu and lists only supported axes.

#### P19. Rematch: the same types, new numbers, compared question by question

*From: experience #3, unfair-advantage #7, the Clear Session gaps. Effort S. Builders: F5
(`rematch` in the drill body), S4 (summary block, Your sets, MoreMenu), F2 (U1 picks up a due
rematch, §3.2).*

**Why.** Their Clear Session serves the same items again, so a second score measures memory. A
rematch serves every slot's type, tier and format on a fresh seed in the original order, so
Then → Now shows whether the skill moved. A finite bank can't spend a second item per slot.

**Server.** `POST /api/drill {rematch: sid, scope: 'all' | 'misses'}`.
* Each slot's (template, tier, fmt) on a fresh seed, in order, with the original settings.
* `cfg.rematch_of` (the root set, so chains compare to the original) and `cfg.slot_of {new_qid:
  old_qid}`. Repairs go to `end` and the final round is off, so slots stay aligned.
* A challenge parent → 409.
* `finish()` adds `slots: [{n, template, type_name, then {status, ms, mistake}, now {status, ms,
  mistake}, change: fixed | still_missing | slipped | held | same_trap}]`.

**Entry points.** Summary NextActions: the secondary pill **Rematch · same 10 types, new
numbers** and a quiet **Rematch my misses · 3**. Your sets Finished rows: **Rematch** first.
MoreMenu: **Rematch**. `Retake exact` stays, as "Retake exact (tests memory)". A chip **Rematch
in 3 days** stores `cfg.rematch_due`; U1's queue shows it that day.

**During.** After answering, the strip note reads "Rematch of question 4 · then ✕ 1:40". It
never shows before answering, so it can't prime.

**Start clean** (their Clear Session gives a clean redo; R6 would bring back the student's own
highlights, notes like "it's C", strikes and type rules on a retake).
* The Retake and Rematch confirm sheets (Your sets, MoreMenu, the summary) carry the checkbox
  **Start clean: hide my highlights, notes, strikes and rules on this copy**. On by default for
  Retake exact, off by default for Rematch (fresh seeds bring back only type rules).
* It sends `clean: true` → `cfg.clean`. Nothing is deleted: while `cfg.clean` and the copy is
  not finished, `/q`, `next` and state omit `note`, `marks` (highlights), `strikes`, `has_note`
  and `type_note` carried from other sittings; anything the student adds on this copy shows as
  usual.
* After Finish, the copy's ReviewSheet shows everything again, the old notes marked "from
  before".
* Acceptance: with the note 'check sign' saved on a question, `POST /api/drill {retake: sid,
  clean: true}`: `GET /api/drill/{new}/q/{same n}` returns no `note` until the set is finished,
  and returns `note 'check sign'` after `finish`. Without `clean`, v2 acceptance #17 still
  holds.

**Summary: Then → Now.** Headline "Then 6 / 10 → Now 9 / 10 · 3 fixed · 0 slipped · 14 s faster
per question". A table: # · type · then (status cell, time) · now (status cell, time) · change;
a repeated misconception reads "same trap again". A paired bar chart of then-time against
now-time (`UI.barChart`). "Still missing" rows offer **Steps** (P1) and **Twins ×3**.

**Acceptance.**
1. `POST /api/drill {rematch: sid}` serves the same templates, tiers and formats as `sid`, in
   order, every seed different.
2. `finish()` on it returns one `slots` entry per original slot, `change` in the allowed set.
3. A challenge sid → 409.
4. With `cfg.rematch_due` = today, `GET /api/next` has an item whose title starts "Rematch".

#### P20. A navigator and a Check Your Work that act

*From: the navigator gaps of outcomes and experience, the outcomes Check Your Work gap, the
unfair-advantage mark gap. Effort S. Builders: F3 (`UI.navigator` filters and views,
`UI.checkYourWork` triage), S4 (the Twins action).*

**Why.** Their overview, and v2's, only shows. A student looking at "Incorrect 2 · Over budget
3" wants to act on exactly those. Their Check Your Work lists what is blank and stops; the
minutes left are the decision.

**Navigator.**
* **Legend chips filter.** Tapping a chip filters the grid to its cells; the others take R20's
  Filtered-out token. Chips combine with AND. "Clear" resets.
* **Views** add **Confidence** (P7: an S / U / G corner letter, a confident miss ringed) and
  **Traps** (each wrong cell labelled with its habit glyph, U6; a trap chip filters and offers
  **Fix these**). The **Time** view rings cells over their own budget (P16).
* **Twins of these (n)** on any filtered state appends twins of those cells (`/more
  {axis:'same'}` for each, in order). In end mode before Finish it is hidden; after Finish it
  starts a new set.
* **Key**: `U` jumps to the next unanswered question.

**Check Your Work triage** (`UI.checkYourWork(host, cells, {triage})`; the test window can pass
the same option, §3.4's owner decides). Under the tiles, in this order, each line only when it
applies:
1. "2 unanswered. A blank scores the same as a wrong answer: put your best guess on each.",
   with a `Go to 7` button per blank.
2. End mode: "3 answers marked Unsure (P7): revisit them", with Go-to buttons.
3. Marked: "2 marked for review", with Go-to buttons.
4. Timed: "4:10 left · about 1:20 for each of these".
Timed sets print each cell's seconds under it.

**Acceptance.**
1. Browser: tap "Incorrect 2" in the legend → exactly 2 cells stay at full opacity.
2. "Twins of these (2)" raises `total` by 2, and the new slots have the filtered templates.
3. `U` moves to the lowest-numbered unanswered question.
4. An end-mode set with 2 unanswered and 3 Unsure answers: Check Your Work lists the
   unanswered line first with 2 Go-to buttons, then the Unsure line.

#### P21. Pools that give twins, and your rule for a type on every fresh one

*From: outcomes #13 (rule cards), the notes gaps of experience and unfair-advantage, the marked
and saved pool gaps. Effort S. Builders: F5 (`exact` per pool), S4 (the builder seg, prompts),
F4 (notes with seed −1), F3 (the tip above the stem), S10 (Review lists type rules), S4 print.*

**Why.** An exact replay tests memory of that item, and R8 leaves repeats out of mastery; a
twin tests the skill, and it counts. Notes keyed to an exact seed rarely come back in an
unlimited bank, so the student's own lessons die with the session. Writing the rule yourself
(the generation effect) makes it stick, and the cue then follows the type onto new numbers.

**Pools.** R5 keeps two stores apart: Mark (the `flags` table, per sitting) and Save (the
`saved` table, kept for good). The builder now starts from each, as its own row in
"Questions from", next to Seen before:
* **Questions I've seen · 212** (attempts), with Result and From sub-filters; the old "Marked
  for review only" checkbox under it is removed, because it read attempts, not flags.
* **Marked for review · 6** (`pool:'marked'`, from `flags`).
* **Saved · 9** (`pool:'saved'`, from `saved`).
* Each of the three carries a Seg "Exactly as they were · Fresh twins" (`exact: true |
  false`, §2.6). Defaults: **Fresh twins** for Seen before and Saved (U1's saved row already
  uses `exact:false`); **Exactly** for Marked, because the flag means "this one".
* Presets `Marked · 6` (pool marked) and `Saved · 9` (pool saved); a header link `Saved · 9`
  beside `Marked · 6`, which scrolls the builder to that row with it selected. Zero counts
  show "· 0" and the row is disabled with its reason.
* The exact helper reads "Exact replays test your memory of that question and don't move
  mastery."
* The summary's quiet actions add **Twins of what I marked · 2**.

**Your rule for this type.**
* **Prompts** (at most twice a set; never in timed sets or the challenge): after the first miss
  on a type, "Write your rule for Count solutions"; when a mistake closes, "You fixed it: write
  the rule so it sticks". Also from My note and Details at any time.
* A field of up to 140 characters ("Same slope + same intercept = infinitely many"), stored as
  `notes(learner, template, seed = −1, note)` via `POST /api/notes {session, question_id, note,
  scope:'type'}`. The My note popover gains the checkbox "Show this on every question of this
  type", which saves the note the same way.
* On every later question of that template, fresh seeds included, a collapsed tip above the
  stem: "Your rule · Sep 20: check the sign of the slope ▸", with "Still useful? Keep ·
  Remove". It does not count as help: it is the student's own knowledge.
* It is a study aid (the shared rule): only in instant or retry practice and in review, never
  in end mode before Finish, tests, the challenge, contests or Test-like mode, and never on a
  Start clean copy (P19). Pref `type_rules` (default on) turns it off everywhere; the My note
  popover links to it.
* The worked example (P2) shows it under the steps. The TypeRow shows a rule glyph. Review (S10)
  lists rules beside saved notes.
* **Print** (§2.12): a "My rules" sheet, one page grouped by domain, from the builder's
  `Printable worksheet` menu and from Me, for the week before the test.

**Acceptance.**
1. `POST /api/drill {pool:'saved'}` (default `exact:false`) serves templates from `saved` with
   seeds not in `saved`.
2. A type rule on t, then a fresh t question: `GET /api/drill/{id}/q/{n}` returns
   `type_note == 'check the sign'`, and answering it leaves `attempts.hints == 0`.
3. `POST /api/drill {pool:'marked'}` defaults to exact: its served (template, seed) equal the
   rows of `flags`, not of `attempts`.
4. `?print=rules` renders every type rule, grouped under 4 domain headings.
5. `POST /api/drill/preview` returns counts for `marked` and `saved` separately, and the
   builder shows both rows; the Seen-before row has no Marked checkbox.
6. A type rule on t and `prefs.type_rules = false`: a fresh t question's `/q` has no
   `type_note`.

#### P22. Shared sets and question links send twins by default

*From: the share and public-question gaps of all three designers. Effort S (U28 carries the
mechanism). Builders: F6 (`sets` `cfg.fresh` with slots), S4 (the share sheet, the results
view).*

**Why.** Identical questions let friends pass answers around, which is why the user chose twins
for the Daily Challenge (v2-decisions 1). Two friends comparing one exact sheet still want it
as a choice. There are no classes, rosters or assignments here (decision 5): a share is a
link, and anyone with it takes the set as themselves.

* **Share this set** opens a sheet with a Seg "Twins for each person (default) · Exactly these
  questions". Twins → `POST /api/sets {kind:'set', cfg:{slots:[[template, tier, fmt]],
  fresh:true}}`; each taker gets their own seeds in the same order.
* **Results aggregate per slot by type and named misconception**: "Slot 4 · Percent change ·
  14 / 22 · most common: used the new value as the base (5)". Each taker's summary adds "You vs
  everyone who took it" per slot.
* A set that friends want to race on the clock is Compete's private contest (an invite code
  or link that Compete owns), linked from the share sheet as "Race friends on this instead".
* **Question links**: U28's "Send a twin" is the default, "Exactly this question" second.

**Acceptance.** Two learners take one twin code: the same templates in the same order with
different seeds. The owner's results list both takers with per-slot `right` and `top_mistake`.

#### P23. One round trip per question, and fewer taps

*From: experience #7 (the safe half), the select-then-check gap. Effort S. Builders: F5 / S4
(`answer()` returns `next`), F3 (the workspace fast path, tap again).*

**Why.** For them, Check and Next are each a round trip, and after a miss there are two more
taps to open and close the explanation. The loop should feel instant.

* **`answer()` returns `next`, as a preview**: the next question (public, no key), with repair,
  review, final-round and zone logic applied, or null at the end. It is **not served yet**:
  the server holds it in `cfg.pending` (its template, seed, tier and why), outside `served`,
  `total` and `practice_seen`.
  * Next renders it without a request, then sends `POST /time` for the new position; that
    `/time` (or any `/q`, `/answer` or `/strike` naming its position) commits it to `served`
    and `practice_seen`.
  * `/more` (any axis, Practise this trap, the ladder, Twins of these), a navigator jump,
    Skip, the final round's Start and Exit discard it. The next Next asks the server, which
    picks again with the new state.
  * So `served` only ever holds questions the student was shown, "served ≥ total" stays
    true, and Check Your Work never lists a phantom blank.
* **Tap again to check** (touch): tapping the selected choice again checks it, like `Check`
  (`conf:'auto'`: Sure for an active tagger, else unrated; P7),
  with a 250 ms guard. The hint "Tap again to check" shows only in a learner's first 3
  questions ever (`localStorage satf.tap`).
* **Desktop**: after the verdict, focus moves to Next, so A–D, Enter, Enter runs the loop.
* The key never ships before the answer (§4), so practice rank stays honest (R3).

**Acceptance.**
1. Playwright network log: from Check to the next stem painting after Next, exactly one POST
   `/answer`, plus the fire-and-forget `/time`.
2. Touch emulation: a second tap on the selected choice produces a verdict with `conf:'auto'`
   in the request (filed per P7's rule); a double tap within 250 ms produces one answer.
3. The instant-mode payload of an unanswered question has no `answer`, `answer_index`,
   `reasons` or `steps`.
4. Answer a question, then `POST /more {axis:'same'}`: `state.served` contains no question the
   student was not shown, `total` rose by exactly 1, and `practice_seen` has no row for the
   discarded preview's seed.

#### P24. The reference sheet in context: which formula this used, and which ones aren't given

*From: the reference gaps of all three designers. Effort S. Builders: T-bank (`satbank/
formulas.py`), F3 (Reference anchors and highlight), S4 (verdict line, SkillPanel card).*

**Why.** Knowing which formulas the test gives and which must be memorised is a classic SAT
point, and their Reference modal is the same image for every question.

**Bank.** `satbank/formulas.py`:
* `SHEET`: the reference sheet's entries with ids (circle area and circumference, rectangle,
  triangle, Pythagorean, the special right triangles, box, cylinder, sphere, cone and pyramid
  volumes, 360°, 2π, 180°).
* `KNOW`: what is not on the sheet (slope, point-slope, vertex form, discriminant, quadratic
  formula, circle equation, exponential growth, percent change, mean and median, distance and
  midpoint, SOH-CAH-TOA).
* `USES = {template: [ids]}`: an **explicit entry for every one of the 386 templates**, a list
  of `SHEET` / `KNOW` ids, or `[]` for "uses no formula". No skill-level fallback exists. It is
  a 386-row table (T-bank, small effort), checked by the acceptance below.

**After the reveal.** A line: "Used: V = πr²h · on the reference sheet (F)", or "Not on the
sheet: (x − h)² + (y − k)² = r² · learn it", naming each formula the template uses. A
template with `[]` shows no formula line. `F` opens the Reference dialog scrolled to that
entry, with a `--wash` highlight.

**SkillPanel.** A card "Not on the sheet: you must know", listing the skill's `KNOW` entries,
each with **Drill it · 5** (`templates` whose `USES` include that id, 5 questions).

**Acceptance.**
1. `python3 -c "from satbank.formulas import USES, SHEET, KNOW; …"` asserts that `USES` has
   exactly 386 keys, equal to the registry's templates, that every id is in `SHEET` or `KNOW`,
   and that no verdict line in a 386-template sample contains "Formulas for".
2. After the reveal on a cylinder-volume template, the line contains "on the reference sheet",
   and the dialog's highlighted element has id `ref-cylinder`.
3. "Drill it · 5" on the circle equation → 5 questions, each from a template whose `USES`
   include `circle_equation`.

#### P25. Reports answered inside the session

*From: experience #11, unfair-advantage #8, the report gaps of all three. Effort S (U3 is the
check). Builders: S4 (session wiring), F3 (the Voided cell), F6 (U3).*

**Why.** Their report is a black box. U3 answers a key dispute in a second with a separate
solver. In a practice set the student should see the outcome where they are, and never lose a
question to a bug.

* The ReportSheet shows U3's outcomes (`remarked`, `forms`, `explained`, `broken`, `unsure`) in
  place of §2.9's "Thanks" line.
* **`broken`**: the rail segment takes R20's Voided state (⊘) with the note "Voided: broken
  question · replaced"; the session calls `/more {axis:'same'}` on a fresh seed of the same
  template (U3's quarantine skips the bad seed; a whole-template quarantine uses a P18 sibling),
  so a fixed set keeps its length. The summary counts it under neither right nor wrong.
* **`remarked`**: the cell flips to Correct in place, and the summary's score updates.
* End mode: nothing is checked until Finish (U3's live-sitting rule).

**Acceptance.** A fixture that makes `check_item` fail on the served seed: after the report,
the served list has a new question with the same template and another seed, `total` is
unchanged relative to before the void (+1 slot, −1 counted), and the old slot's status is
`voided`.

---

## 3. Spec overrides

### 3.1 Inside §3.3 (spec/rebuild-v2.md lines 3348–4779)

Each entry quotes the current text, then gives the replacement or the addition.

1. **1.2 Page header.**
   * Quote: "- Eyebrow `SAT MATH` (.k)."
   * Replace: "- Subject seg `Math · Reading & Writing` in the eyebrow's place (P15). Math is
     the default."
   * Quote: "- Mono meta line: `19 skills · 386 question types · unlimited questions, never
     repeated`, from /api/bank totals."
   * Add after it: "- A second meta line: `Math 560–640 · ≈ 120 points on the table` (P10),
     linking to Results, and the route line under it (P10)."
   * Quote: "**Right**, three links:" Replace: "**Right**, four links:" and add after
     "- `Marked · 6`, to /mistakes/#marked.": "- `Saved · 9`, which selects the Saved row in
     Questions from and scrolls to it (P21)."
2. **1.1 Desktop layout.** Quote: "3. Preset bar and coach line." Replace: "3. Ready row (P15),
   then the preset bar and coach line."
3. **1.4 Preset bar.** Add rows to the table:
   * `Biggest gains · 3 skills` (P10; disabled "needs 30 answers");
   * `Route-up` or `Practise the harder module's mix` (P10);
   * `Fluency sprint · 5 types` (P16; "needs 3 rights on a slow type");
   * `Desmos drills · N` (P3);
   * `Confident misses · 4` (P7; "0 confident misses");
   * `Your top habit · …` (P6);
   * `Solve first · 10` (P5);
   * `Check 3 skills I haven't tried` (P11);
   * `Saved · 9` (pool saved, Fresh twins; "0 saved") (P21);
   * the saved presets (P15).
   * Quote: "| `Marked · 6` | pool = Seen before, Marked only | '0 marked' |" Replace: "|
     `Marked · 6` | pool = Marked for review (flags), Exactly | '0 marked' |" (P21).
   * Quote: "A quiet `Reset` at the right end restores Coach's pick and your saved defaults."
   * Add: "`Save as preset` sits before it (P15)."
4. **1.4 Coach line.**
   * Quote: "`Why these: Percentages: 2 open mistakes · Circles: weakest, Learning, 48% first
     try · Linear functions: not practised for 12 days`"
   * Replace: "`Why these: Nonlinear functions ≈ +22 (5 a test, 56% first try) · Percentages: 2
     open mistakes · Circles: 1 confident miss`"
5. **1.5 Search.**
   * Quote: "- Label 'Search'. Placeholder 'Skills and question types, e.g. circle equation,
     margin of error'."
   * Replace: "- Label 'Search or build a set'. Placeholder 'circles hard 10 timed · a type name
     · a College Board ID · or paste a question'. It parses commands (P15), matches CB IDs and
     pasted text (P13), and otherwise filters as below. `/` focuses it; Enter in the empty
     field starts Ready card 1."
6. **1.6 Tree header.**
   * Quote: "- A native `<select>` 'Sort': Test order (the default), Weakest first, Most
     mistakes, Least practised, Recently practised. Sorting works within each domain."
   * Replace: "- A seg `Skills · Map · Habits` (P14, P6). A native `<select>` 'Sort': Most
     points (the default once points exist, P10), Test order (the default before that),
     Weakest first, Most mistakes, Most overdue (P12), Slowest vs budget (P16), Least
     practised, Recently practised. Sorting works within each domain."
7. **1.6 DomainCard.** Add to the header list: "- `≈ +40 on the table` (P10);", "- `Due 3`
   (P12);" and "- `14 of 23 types ready` (P14);".
8. **1.6 SkillRow.**
   * Quote: "**SkillRow.** 52 px, on a grid of: checkbox 20 | glyph 22 | name 1fr | mastery 140
     | record 150 | mistakes 80 | last 72 | chevron 28."
   * Replace: "**SkillRow.** 56 px, on a grid of: checkbox 20 | glyph 22 | name 1fr | mastery
     140 | worth 80 | record 150 | mistakes 80 | last 72 | chevron 28. Worth is P10's `≈ +15`
     with `about 3.4 of 44 · you miss ~1.6 of them`. The mastery cell adds `Due 3` (P12), and a
     Strong row adds `held after 16 days` or `not yet tested after a gap`. The record sub-line
     adds `Fluent 6 of 23` (P16) and `solve-first 75%` when it exists (P5)."
   * At 390 px, line 2 of the phone SkillRow adds the worth after the bar.
9. **1.6 SkillPanel.** Append to the stats line: "`· Sure-accuracy 95% (40)` (P7) · `With
   Desmos 90% (10) · without 60% (15)` (P3), each once it has data." Add items:
   * "4. **Types · Speed** toggle (P16)";
   * "5. **Not on the sheet** card with Drill it (P24)";
   * "6. Buttons `Finish Circles · 14 questions` (P14), `Check my level · 8 questions` (P11),
     `Mix it up · 8` (P17)";
   * "7. `You reliably rule out: …` (P6)";
   * "8. `Official questions on College Board · 142`, opening their bank at this skill, and the
     `Paste what you missed there` field (P13)".
10. **1.6 TypeRow.**
    * Quote: "- The level: `L4` when measured, or `L3–5 est.`."
    * Replace: "- The level from ratings: `L4`, or `L4 · rough (6)` (P11), and `your odds ~72%`."
    * Add after "- `Marked 2`.": "- the U8 state word (unmet / met / ready) and `Due today` or
      `Back Oct 2 · held 2` (P12, P14);", "- `Fluent · best 0:48` or `Slow: right but 2:10
      median` (P16);", "- chips `Desmos way` (P3), `Built from 11 official questions` (P13), a
      rule glyph (P21)."
    * Quote: "- A quiet `Try one`, which starts a one-question set of this type with the current
      settings."
    * Replace: "- A quiet split `Try one ▾` (P18's axes), `See the traps` and `Learn this type`
      (P2), and ⋯ `Mix it up with look-alikes` (P17)."
    * Quote: "A skill with more than 12 types collapses behind `Show all 36 types`." Replace
      (decision 4: nothing useful is hidden to save space): "An expanded skill shows every
      TypeRow, grouped under its skill-label sub-headers (e.g. `Arc length · 4 types`). Each
      sub-header is sticky inside the SkillPanel while its rows scroll, and carries its count,
      a tri-state select-all box and `3 ready · 1 open`. There is no Show-all line."
11. **1.7 Settings, 1. Questions from.**
    * Quote: "- `Fresh numbers on types due for review · 5 types`. Helper: 'Types you got right
      more than 10 days ago, so they stay strong.'"
    * Replace: "- `Fresh numbers on types due for review · 5 types`. Helper: '3 due now · 5 more
      this week · next 14 days ▸' (T3's schedule, P12)."
    * Add rows: "- `Fresh numbers on confident misses · 4 types` (P7).", "- `Fresh numbers on
      mistakes I logged from outside · 4` (P13).", "- `Twins of College Board questions` (P13;
      opens the ID field)."
    * Quote: "- `Questions I've seen, exactly · 212`. Helper: 'The same questions again, exactly
      as they were.' Choosing it opens its sub-filters in place:"
    * Replace: "- `Questions I've seen · 212`, with a Seg `Fresh twins · Exactly as they were`
      (P21; default Fresh twins). Its sub-filters open in place:"
    * Its Result seg gains `Sure but wrong` (P7, explicit Sure only).
    * Quote: "  - `Marked for review only · 6` (checkbox)." Delete it, and its helper line 'A marked
      question you get right here leaves your Marked list…' moves to the new Marked row.
    * Add rows after Seen before (P21): "- `Marked for review · 6` (flags), with the Seg
      `Exactly as they were · Fresh twins`, default Exactly. Helper: 'A marked question you
      get right here leaves your Marked list, unless you tick Keep marked on it.'" and "-
      `Saved · 9` (saved), with the same Seg, default Fresh twins. Helper: 'Questions you saved
      for good. Twins test the skill; Exactly replays the question.'"
12. **1.7 Settings, 2. Questions.**
    * Quote: "- Options: `5 · 10 · 20 · 30 · 40 · 50 · ∞`, plus an `Other` input (1–120; Enter
      starts)."
    * Replace: "- Options: `5 · 10 · 20 · 30 · 40 · 50 · ∞ · 15 min · 30 min`, plus an `Other`
      input (1–120; Enter starts) and `Fit to today's plan · 25 min` when the plan has time
      left (P15)."
    * The helper reads `≈ 16 min for you`, from P16 budgets.
13. **1.7 Settings, 3. Difficulty and level.** Replace the whole block, from "**3. Difficulty and
    level** (the LevelStrip)." through "It is disabled when Order is Easiest first, with the
    reason shown.", with P11's Difficulty control: the Seg `Standard · For me`; For me's three
    options; Standard's tier toggles, Adaptive and the Mix seg `Any · Like module 1 (7/8/7) ·
    Like the harder module 2 (3/8/11)`; the level cells from ratings, always enabled; `Include
    rough levels · 312`. The "**Levels are measured:**" table and the helper "Levels come from
    students' first-try accuracy. 18 of 386 types measured so far." are deleted.
14. **1.7 Settings, 4. Format.** Add the checkboxes "`Only types with a Desmos way (N)`" (P3) and
    "`Only types built from official questions (N of 386)`" (P13).
15. **1.7 Settings, 5. Timing.**
    * Quote: "- Test pace: 95 s a question. Helper: `16:00 for 10 questions · 1:35 each, like
      the test`."
    * Replace: "- Test pace: each question's own budget (65 / 95 / 126 s by tier for Math, or the
      crowd median; P16). The clock starts at the sum of the planned slots' budgets and every
      added question adds its own. Helper: `16:00 for these 10 · paced to each question's
      difficulty · added questions add their time`."
    * Quote: "- Toggle `Pace alert on each question`, on by default when timed: the stopwatch
      turns amber-deep after 1:35."
    * Replace: "- Toggle `Pace alert on each question`, on by default when timed: the stopwatch
      turns amber-deep past that question's budget. Toggle `Two passes: offer Skip past 1.5×
      the budget`, on by default when timed (P16)."
16. **1.7 Settings, 6. Answers shown.** Add under the radio:
    * "`Check asks how sure (Sure · Unsure · Guess)`: Ask · Off (P7)";
    * "`Hints before I answer`: on (P2)";
    * "`Solve before seeing choices`: Off · Medium and Hard · All (P5)";
    * "`New types: show me one worked first` (P2)".
17. **1.7 Settings, 7. After a miss.**
    * Quote: "**7. After a miss** (toggle, on by default): `Follow a miss with one like it (same
      trap, new numbers)`."
    * Replace: "**7. After a miss** (Seg): `Next question · 3 questions later · At the end ·
      Off`, meaning the repair (same trap, new numbers), default `Next question`. Checkbox
      `Final round: re-ask what I missed at the end, new numbers` (P12), on by default."
18. **1.7 Settings, new 7a. Mix in reviews** (P12): `Off · 2 per set · 20%`, and `Only from the
    skills I picked`. Then `Mix in due SAT words: Off · 2 per set · All due` with the helper
    `12 due · reviewed at set breaks, filed to Words, never counted in Math` (P12, decision 2).
19. **1.7 Settings, 8. Order.**
    * Quote: "**8. Order** (Seg): `Mixed · Grouped by skill · Easiest first`."
    * Replace: "**8. Order** (Seg): `Mixed · Grouped by skill · Easiest first · Mix-up` (P17).
      Mixed never serves 3 questions of one template in a row."
20. **1.7 Settings, 10. Repeats.** Append: "No practice question copies a College Board
    question: every pool skips an official item's exact numbers and wording (P13)."
21. **1.8 Action bar.**
    * Quote: "- Line 1, 600 15 px: `10 questions · 3 skills · 41 types · all levels · both
      formats`."
    * Replace: "- Line 1, 600 15 px: `10 questions · 3 skills · 41 types · For me: Stretch ·
      both formats · covers ~21 of 44 · works on ≈ +30` (P10, P11)."
    * Quote: "- Line 2, mono --soft: `Untimed · answers after each · repairs on · mixed · ≈16
      min`."
    * Replace: "- Line 2, mono --soft: `Untimed · answers after each · repairs next · final
      round on · 2 reviews mixed in · mixed · ≈ 16 min for you` (P12, P16)."
22. **1.9 Your sets.**
    * Quote: "- `Retake exact` sends {retake};"
    * Replace: "- `Rematch` sends {rematch} (P19); `Retake exact (tests memory)` sends {retake};"
    * Quote: "- `Share` copies the link, with the toast 'Link copied: friends get these exact
      questions';"
    * Replace: "- `Share` opens P22's sheet (Twins for each person by default);"
    * Tabs gain `Official questions you brought · 12` (P13).
    * Quote: "- Shared: 'Share a finished set to send the same questions to a friend or a class,
      and see how they did.'"
    * Replace: "- Shared: 'Share a finished set so friends each get their own twins of it, then
      see how they did.'"
    * The `Rematch` and `Retake exact` confirms carry P19's `Start clean` checkbox (on for
      Retake, off for Rematch).
23. **1.10 Deep links.** Add parameters `zone=warm|stretch|challenge|off`,
    `tier_mix=module1|module2_upper|module2_lower`, `box=5..60`, `review_mix=off|2|20`,
    `final_round=0|1`, `cover=off|hard|all`, `cb=ID,ID`, `habits=id,id`,
    `has=desmos,official`, `order=mixup`, `rematch=SID`, `clean=0|1`, `pool=marked|saved`,
    `words_mix=off|2|all`, and `subject=math` (the default; every link carries it, so
    `UI.parseSet` and deep links stay valid when R&W ships).
24. **2.2 RunBar, TimerBlock.** Add: "- Timed sets: a pace delta under the digits, `1:10 ahead of
    pace · 3 Hard left` (P16), updated per answer."
25. **2.3 ProgressRail.**
    * Quote: "- A repair adds a slot, which grows in with .seg.add."
    * Add after it: "- Review slots carry a clock glyph (P12). A final round appears as a
      grouped block after the last slot, headed `Final round · 3` (P12). A voided slot takes the
      Voided token (P25)."
26. **2.4 QuestionStrip.**
    * Quote: "- The difficulty chip: `Medium · L4` when measured, or `Medium` when not."
    * Replace: "- The difficulty chip: `Medium · L4`, or `Medium · L4 rough` (P11), plus the zone
      chip `Stretch` in For-me sets (the odds come after answering)."
    * Add chips: `Review` and `Final round` (P12), `Twin of CB 84664a7c` (P13), `Twin · as
      grid-in · of question 6` (P18), `Rematch of question 4` after answering (P19), the Learn
      pips (P2), `Mix-up` in place of the type name until Check (P17).
    * Add ToolButton: `Cover choices` (V) (P5).
    * Quote: "- The **QStopwatch**: mono mm:ss of time on this question, added up across visits.
      With the pace alert on, it turns amber-deep and gains a dot after 1:35."
    * Replace: "- The **QStopwatch**: `0:48 / 1:05`, time on this question against its budget,
      with a bar and a tick at your median on this type (P16), added up across visits. With the
      pace alert on, it turns amber-deep and gains a dot past the budget. While covered (P5) it
      reads `solve 1:02 · pick 0:08`."
27. **2.4 'Why this one'.** Add examples: 'Open mistake · 1 clean answer closes it · Circles ≈ +5
    pts' (P9); 'Warm-up: right 8 days ago, held twice' (P12); 'You marked this type Sep 20'
    (P12); 'Final round: you missed this one at question 4' (P12); 'You were sure of this one
    and missed it (Sep 22)' (P7); 'Twin of College Board question 84664a7c' (P13); 'Stretch:
    about 70% likely for you' (P11).
28. **2.5 Workspace.**
    * Quote: "**`I'm guessing`:** a toggle chip under the choices, off by default. Key I. When it
      is on at Check:"
    * Replace: "**Guess** (P7): the third part of the split Check (key I). A Guess answer keeps
      every rule below:"
    * Add paragraphs for: the **Hint** row (P2); **Cover choices** (P5); the **type-rule tip**
      above the stem (P21); the **Read the ask** underline (P8); **Watch for** in Learn's
      question 1 (P2); **Tap again to check** (P23); **word cards** in quiz mode (P12).
    * Add the study-aid gate from §2's shared rules: the type-rule tip, the underline, the slip
      line and "Check anyway?" render only when the payload carries them, and the server sends
      them only in instant or retry practice and in review.
29. **2.6 After each question.**
    * Quote: "- The Verdict reads `Correct · 0:48 · your average on this type 1:05`."
    * Replace: "- The Verdict reads `Correct · 0:48 · fluent (budget 1:05)` (P16), with `New best
      on this type` when it applies. Under it: the `next_step` line and, when it applies, `then`
      (P9); the traps-on-offer line and graded strikes (P6); `Solved without the choices` (P5);
      the formula line (P24)."
    * Quote: "- The explanation is collapsed behind `Explanation ▾`. It is open instead when
      prefs.open_explanations is on, or when I'm guessing was on."
    * Replace: "- The explanation is collapsed behind `Explanation ▾`. It is open instead when
      prefs.open_explanations is on, or when the answer was a Guess (P7). Its header is the
      type's about line, and its tabs are Steps · Short · Desmos way (P1, P3)."
    * Wrong: add the confident-miss note (P7), the `What happened?` cause chips (P8), and
      "Missed this type twice. Learn it step by step" (P2).
    * Quote: "**Every option explained**, shown by default (prefs.option_reasons can turn it
      off):"
    * Add: "Each line carries its value and `See where C comes from` · `Practise this trap`
      (P1)."
    * Quote: "**Another one like this:** shown after any answer, with `easier` and `harder`
      split buttons when the type spans tiers. It calls POST /more, and a fixed set grows by 1."
    * Replace: "**Another one like this ▾** (T, Shift+T): same · easier · harder · as a grid-in ·
      same setup, a different question, listing only the axes the type supports; easier and
      harder use a sibling type when the template has one tier (P18). It calls POST /more
      {axis}, and a fixed set grows by 1."
30. **2.6 After I retry.**
    * Quote: "- `2 tries left`, with buttons `Check` and a quiet `Show answer`."
    * Replace: "- `Hint · 2 tries left`, with buttons `Check`, `Hint` (W; P2) and a quiet `Show
      answer`."
31. **2.7 RunFooter.**
    * Quote: "- `Check` (a pill), disabled until a choice or a valid entry."
    * Replace: "- `Check`, disabled until a choice or a valid entry. With `prefs.confidence =
      ask` it is the split `Check` (Enter; unrated unless the learner tags, then it reads
      `Check · Sure`) · `Sure` · `Unsure` (Shift+Enter) · `Guess` (I) (P7)."
    * Quote: "- Next goes to the next served question, and at the frontier it asks the server
      for a new one."
    * Replace: "- Next goes to the next served question. At the frontier it renders the `next`
      preview that came with the verdict and commits it with `/time` (P23), and asks the server
      only after /more, a jump or a skip, which discard the preview. On the last slot with
      misses it offers the final round (P12)."
    * Quote: "- an amber note, e.g. '2 skipped. They count as unanswered.';"
    * Add after it: "- the triage lines of P20 (blanks first, then Unsure, then marked, then time
      per question);"
32. **2.8 Navigator.**
    * Quote: "- **Time:** seconds in each cell, and cells over pace get a 1.5 px amber-deep ring.
      Legend: `Over 1:35: 2 · average 1:04`."
    * Replace: "- **Time:** seconds in each cell, and cells over their own budget get a 1.5 px
      amber-deep ring. Legend: `Over budget: 2 · average 1:04` (P16)."
    * Add the **Confidence** and **Traps** views, legend chips as filters, `Twins of these (n)`
      and `U` (P20). The Status legend gains `Helped` (P2) and `Voided` (P25).
33. **2.9 DetailsPopover.**
    * Quote: "- **Difficulty:** `Medium · level 4 of 7, measured from 212 first tries (58%
      right)`, or `Medium · level not measured yet (3 first tries so far)`."
    * Replace: "- **Difficulty:** `Medium · level 4 of 7, measured from 212 answers`, or `rough (6
      answers)` (P11). After answering: `Your odds were 68% · everyone 58%`."
    * Add rows: **Modeled on** (P13), **Desmos way** (P3), **Formula** (P24), **Your rule for
      this type** (P21).
34. **2.9 AttemptsSheet.** Quote: "**AttemptsSheet**, 'Attempt history':" Add after it: "- **Trend
    head:** first tries as ✕ ✕ ✓ ✓ ✓, `median 2:10 → 0:58`, and the U8 state with its next
    return (P9)."
35. **2.9 ReportSheet.**
    * Quote: "- **Success:** 'Thanks. We can regenerate this exact question to check it.' with
      `Close`."
    * Replace: "- **Success:** U3's instant check and its outcomes. On `broken` the slot is voided
      and replaced at once; on `remarked` it flips to Correct (P25)."
36. **2.9 MoreMenu.**
    * Quote: "- `Start over with these exact questions`. It confirms: 'Starts a new copy of this
      set with the same questions. This one stays in your history.' Then it sends {retake}."
    * Replace: "- `Rematch: same types, new numbers` (P19). - `Start over with these exact
      questions (tests memory)`. It confirms: 'Starts a new copy of this set with the same
      questions. This one stays in your history.', with the checkbox `Start clean: hide my
      highlights, notes, strikes and rules on this copy` (on). Then it sends {retake, clean}
      (P19)."
    * Checkbox items gain `Check asks how sure` (P7), `Hints` (P2), `Solve before seeing
      choices` (P5), `Two passes` (P16) and `Final round` (P12).
37. **2.9 Calculator.**
    * Quote: "- Its state is kept per set, and its expressions persist across questions."
    * Add after it: "- `Show me in Desmos` runs `UI.calc.walkthrough` after the verdict, with
      `Back to my graph` (P3). While a question is on screen, the expressions are saved to it
      (P3)."
38. **2.9 Reference.**
    * Quote: "**Reference:** the formula-sheet dialog."
    * Replace: "**Reference:** the formula-sheet dialog, with an id on each entry. After the
      reveal it opens at the formula this question used, highlighted (P24)."
39. **2.10 Keyboard.** The rows follow R22 (calculator G, reference F, confidence K), with one
    fix: §2.8's runner row binds `A–D` to choosing and also `B` to save and `D` to details, so
    one key press would do two things. In the runner scope **save moves to `Z` and details to
    `X`** (both free there); `A–D` only choose. §2.8, the `?` shortcuts sheet and this table
    change together (§3.2).
    * Quote: "| D | details |" Replace: "| X | details |". Add "| Z | save (R5's Save, kept
      for good) |". The rows `C` and `R` already become `G` and `F` under R22.
    * Quote: "| Enter | Check, Next, or Save & next |"
    * Replace: "| Enter | Check (Sure for a learner who tags, else unrated), Next, or Save & next
      |" and add "| Shift+Enter | Check as Unsure (P7) |".
    * Quote: "| I | I'm guessing |"
    * Replace: "| I | Check as Guess (P7) |"
    * Add: `V` cover choices (P5); `W` hint (P2); `T` another like this, `Shift+T` its axes
      (P18); `U` next unanswered (P20); `Shift+G` show me in Desmos (P3); ↑ ↓ move between steps
      while the Steps list has focus (P1).
40. **2.11 Summary.**
    * Add blocks after 2 (StatTiles): **What this set moved** (P10); **Check my level** result
      (P11, probes); **Expected vs got** (P11, For-me sets); **Calibration** (P7); **Why you
      missed** (P8); **Traps on offer and strikes** (P6); **Retrieval and final round** (P12);
      **Mix-up** (P17); **Desmos use** (P3); **Solved first** (P5); **Official questions**
      (P13); **Then → Now** (P19, rematches only).
    * StatTiles gain `Right with help` (P2).
    * Quote: "5. **Time per question:** a bar per question, in order, with a 1:35 pace line. Bars
      over pace are amber-deep. Legend: `Over pace 2 · fastest 0:21 · slowest 2:48`."
    * Replace: "5. **Time per question:** a bar per question, in order, each against its own
      budget tick. Bars over budget are amber-deep. Legend: `Over budget 2 · fastest 0:21 ·
      slowest 2:48`. Then `Time sinks · n` and, when two passes was on, the passes (P16)."
    * Quote: "   - **With misses:** the primary pill is `Fix my 3 misses` ({from_session}), with the
      helper '3 new questions on the types you missed'."
    * Replace: "   - **The primary pill is the next set built from this one**: `segments` (U1's
      field) of confident misses, then time sinks, then other misses, then slipped reviews,
      e.g. `Fix 2 confident misses + 3 time sinks · 6 questions · ≈ 8 min`. With nothing to fix
      it is U1's Up next. `Fix my 3 misses` stays as the first quiet action."
    * Quote: "   - **Quiet actions:** `Retake these exact questions`, `Same settings, new
      questions`, `Share this set`, `Print`, `Back to Practice`."
    * Replace: "   - **Quiet actions:** `Rematch · same types, new numbers`, `Rematch my misses`,
      `Rematch in 3 days`, `Twins of what I marked` (P21), `Retake these exact questions (tests
      memory)`, `Same settings, new questions`, `Share this set`, `Print`, `SAT words · 12 due`
      when due (P15), `Back to Practice`."
41. **2.12 Print view.** The answer-key page prints Steps where they exist (P1) and the formula
    line (P24). Add `?print=rules`: the "My rules" sheet (P21).
42. **2.13 Challenge mode.**
    * Quote: "- no Pause, Skip, Another one like this, Retake, Share, Print, I'm guessing, 'Why
      this one' or Everyone line;"
    * Replace: "- no Pause, Skip, Another one like this (any axis), Retake, Rematch, Share, Print,
      Hint, Learn this type, review slots, final round, zone targeting, Mix-up, 'Why this one' or
      Everyone line. The split Check (Sure · Unsure · Guess), Cover, Steps, the Desmos way, the
      cause chips and the next-step line are allowed (after answering, where they reveal
      anything);"
43. **3.3.4 Extras.**
    * Quote: "TopTierPrep has one long explanation per item."
    * Replace: "TopTierPrep's report explanation is a Justification plus one prose line per wrong
      option. Ours is computed from the misconception that produced each option, carries its
      value, points at the step it gets wrong (P1), and drills that trap in one tap."
    * Quote: "- **Measured levels 1–7, shown honestly**: Levels come from real first-try
      accuracy with fixed thresholds, and the page says 'measured from N' or 'not measured
      yet'. The tier filter always works. Their Question Score is opaque, and missing from their
      Details."
    * Replace: "- **Levels 1–7 and odds from the first answer**: item and skill ratings move with
      every clean first try; a level says rough or measured, every type shows your odds, and
      Standard offers the tier mix of each module (P11). Their Question Score is opaque, and
      missing from their Details."
    * Add one bullet per P1–P25 (I1 copies the titles from §2).
44. **3.3.5 Server changes.**
    * **GET /api/bank** gains `subject`, `forecast`, `route`, `habits`, and per skill `gain,
      per_test, to_strong, fluent_n, due_n, ready_n, sure_rate, calc_split`; per type `level,
      rough, rating, odds, budget_ms, median_ms, best_ms, fluent, slow_right, due, k,
      next_return, state, official, desmos, steps, type_note, lookalikes`.
    * Quote: "- **Measured levels and crowd stats (drill.levels(), cached for 10 min)**"
    * Replace: "- **Crowd stats and budgets (drill.levels(), cached for 10 min).** It keeps n,
      first-try rate, reason counts (slips and misreads left out, P8) and the crowd object, and
      adds `median_ms` of clean rights. The level comes from ratings (P11), so the
      accuracy-threshold table is deleted."
    * Quote: "  - due = the last first try was right, 10 or more days ago, and there is no open
      trap."
    * Replace: "  - due = T3's fading rule (`progress.warmup_candidates`), with no open trap (P12)."
    * `answer()` accepts `conf` (`sure` · `unsure` · `guess` · `auto`, resolved by P7's rule),
      `own`, `hints` and returns `next` (a preview held in `cfg.pending`, P23), `budget`,
      `fluency`, `best`, `next_step`, `then`, `offered`, `struck_key`, `cover`, `cause`,
      `steps`, `diverge`, `wrong_step`, `option_steps`, `desmos` (only with `DESMOS_WAY` on),
      `formula`, `rungs`.
    * **drill.state**: `pace: 95` is replaced by `subject`, `plan` (the planned tier per slot),
      `clock_log`, `conf_active` and a `budget_ms` on each served entry (P16, P7). `served`
      entries gain `kind` (`question` · `example` · `word`). `can` gains `clean`. `/q` and state
      omit the study aids outside instant or retry practice and review, and omit carried notes,
      highlights, strikes and type rules on a `cfg.clean` copy until Finish (P19).
    * `POST /api/drill` takes `subject` (default `math`), `clean`, `words_mix`, `pool:'marked'`
      and `pool:'saved'`. `_fresh` skips `PINNED` cards in every pool (P13).
    * New endpoints: `POST /api/drill/{id}/hint`, `/why`, `/calc`, `/word`; `/more` takes
      `axis`, `want`, `n` and `ladder`; `GET /api/types/{t}/example` returns steps (U2's
      endpoint).
    * `finish()` adds `calibration, causes, dodged, strikes, retrieval, final, mixup, probe,
      calc, covered, official, expected, passes, time_sinks, slots, helped`.
    * **Tables and columns** as in §3.2.
45. **3.3.7 Shared needs.**
    * `UI.workspace` adds: the Steps (or Method) · Short · Desmos way tabs with the diverge
      compare; the Hint row counting the item's own rungs; modes `example`, `guided` and
      `cover`; the What happened? chips; the Read the ask underline; the type-rule tip; tap
      again to check; word cards in quiz mode. The study aids render only from payload fields
      the server sends in practice and review, so the exam runner, the challenge and contests
      never show them.
    * The runner footer (R21) adds the split Check (P7).
    * `UI.calc` adds `walkthrough` and capture. `UI.navigator` adds filters and the Confidence
      and Traps views. `UI.checkYourWork` adds `triage`. `UI.history` adds the trend head.
      `UI.atlas` (F1) is shared by P14 and U8.
46. **3.3.8 Acceptance checks.**
    * Replace #5 with: "Fresh learner, db as shipped: every /api/bank type has `level` 1..7 and
      `rough: true`. `POST /api/drill {topics:['linear_functions'], levels:[1],
      unmeasured:false}` returns 409 naming 'level 1'. With `unmeasured:true` it returns 200
      (guaranteed: P11's band priors put at least one type at every level, P11 check 1)."
    * Replace #6 with P11's check 2.
    * Replace #13 with: "`/more {axis:'same'}` raises `total` by 1, and the next served question
      has the same template and a different seed. `{axis:'grid'}` serves `fmt 'spr'`."
    * Replace #29's first sentence with: "Session: pressing 'b' selects B without submitting (no
      .verdict visible) and saves nothing; `Z` toggles save and `X` opens Details. Enter
      submits with `conf:'auto'`, filed as null for a learner who has not tagged (P7)."
    * Amend #17: "… returns note 'check sign', unless the retake was made with `clean: true`,
      in which case /q returns no note until the set is finished (P19)."
    * Append the acceptance checks of P1–P25.
47. **3.3.9 Open questions.**
    * The levels question ("Levels: are the thresholds acceptable …") is answered by P11.
      Replace it with: "The rating cut points for levels 1–7 and the zone centres (0.87 / 0.70 /
      0.47): OK?"
    * The replicas question ("Official-item replicas: …") is answered by P13 (twins, never
      replicas).
    * Add: "Citing College Board question IDs (never their content) on twins and in Details: OK
      under College Board's terms?"
    * Add: "Default difficulty `For me · Stretch`, served as the test's 7 / 8 / 7 mix in each
      skill until it is placed (8 clean first tries or a probe): OK?"
    * Add: "Capturing College Board's Question Bank listing metadata (ID, skill, tier, score
      band; no content) into `material/cb_index.json`, for P11's priors and P13's index: OK
      under College Board's terms?"
    * Add: "Active tagger at 10% Unsure or Guess in the last 50 first tries (P7): the right
      threshold for Enter to mean Sure?"
    * Open question 15 (the Desmos key) is no longer open: the production key is a launch
      requirement for P3, which ships dark without it.

### 3.2 Outside the section (Part 2 and sibling lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| R8 | A **clean answer** also needs `hints = 0` and `conf != 'unsure'`. A right answer with `hints > 0` counts half, like a guess. `guess = 1` exactly when `conf = 'guess'` | P2, P7 |
| R9 | A right answer with `conf = 'unsure'` opens or refreshes an `~unsure` item owing 1 (Review's flagged-right rule). `progress.coach` and `_pick` rank traps whose latest wrong attempt has an explicit `conf = 'sure'` first (null, unrated, is an ordinary miss). Kinds from `attempts.miss_kind`: trap → misconception; slip, misread, clock, entry → slip; gap → unsure | P7, P8 |
| R24 | Sources `finish`, `probe` (with topics) and Mix-up sets are ordinary sittings, as today.md lists `learn` | P11, P14, P17 |
| R33 | Adaptive is Standard mode's option; its step uses `blueprint.siblings` when the template has one tier. `zone` (For me) is the default adaptivity, per type by odds, once a skill is placed; before that the skill is served module 1's tier mix | P11, P18 |
| R5 | Marked (flags) and Saved (saved) are each a pool in the builder (`pool:'marked'`, `pool:'saved'`), with their own presets and header links; the Seen-before "Marked only" checkbox is removed | P21 |
| R6 | Notes and highlights come back on replay and retake, except on a copy made with `clean: true`, which hides them (and strikes and type rules) until Finish | P19 |
| R21 | The shared `UI.workspace` renders the study aids (type-rule tip, Read-the-ask underline, slip line, Check anyway?) only from payload fields; the exam runner, the challenge and contests never send them | shared rules |
| R34 | 95 s stays the module average. Per question the budget is 65 / 95 / 126 s by tier (Math; each subject derives its own from `blueprint.SECTION[subject]`), or the crowd median. Test pace starts at the sum of the planned slots' budgets (`cfg.plan`), moves when a served tier differs, and every added slot adds its own budget | P16 |
| §2.5 | `attempts`: `conf TEXT`, `hints INTEGER NOT NULL DEFAULT 0`, `miss_kind TEXT`, `offered TEXT`, `struck TEXT`, `cover INTEGER NOT NULL DEFAULT 0`, `calc INTEGER NOT NULL DEFAULT 0`. `tries`: `hints INTEGER DEFAULT 0`. New table `skill_ratings(learner, topic, rating REAL, n INTEGER DEFAULT 0, seed TEXT; PK learner, topic)`, seeded on creation (P11), in `LEARNER_TABLES` and `carry` (keep the side with larger n). `notes.seed = −1` means a type rule. `item_ratings` is written by F4's `ratings.py` for every clean first try. Startup backfills: `offered`, ratings (priors from `material/cb_index.json` bands). The outside-mistakes store (U2) gains `subject TEXT NOT NULL DEFAULT 'math'`. No spaced-review table: T3 derives it | P2, P3, P5–P8, P11, P15, P21 |
| §2.6 | Fields: `zone` (off / warm / stretch / challenge), `tier_mix` (module1 / module2_upper / module2_lower), `review_mix`, `review_from`, `final_round` (bool), `has` ([desmos, official, steps]), `habits` (a list, source `habit`), `rematch` + `scope`, `per_q`, `pool:'official'` with `ids` = CB ids and `each`, `order:'mixup'`. Pool `review` = T3's fading types. Sources: `official`, `sprint`, `rematch`, `finish`; `probe` takes `topics`. `/more` takes `axis`, `want`, `n`, `ladder`. Pools `marked` and `saved`. `subject` (default `math`), `clean` (bool), `words_mix` (off / 2 / all). The answer body takes `conf` (`sure` · `unsure` · `guess` · `auto`), `own`, `hints` | P2, P3, P6, P7, P11–P14, P16–P19, P21 |
| §2.7 | Builder keys live per subject under `prefs.practice[subject]`: `zone` (stretch), `review_mix` (20), `review_from` (picked), `final_round` (true), `hints` (true), `cover` (off), `worked_first` (true), `two_passes` (true), `words_mix` (off), `presets` ([] ≤ 8). Flat keys: `confidence` (ask \| off; ask), `type_rules` (true). `repairs` values add `later`. U15 bundles (written into `prefs.practice.math`): Learn `zone: stretch, repairs: next, final_round: true`; Build `zone: stretch, repairs: later, final_round: true`; Test-like `zone: off, confidence: ask, hints: false, two_passes: true`, and no study aids | P2, P5, P7, P11, P12, P15, P16, P21 |
| §2.8 | Runner: `A–D` only choose; save moves from `B` to `Z` and details from `D` to `X` (the Player scope's `A–D` pick while answers are hidden, so its save moves to `Z` too, one save key everywhere); the `?` sheet follows. `Enter` checks (Sure for an active tagger, else unrated), `Shift+Enter` as Unsure, `I` as Guess; `V` cover, `W` hint, `T` / `Shift+T` another like this and its axes, `U` next unanswered, `Shift+G` Desmos walkthrough. `K` stays the exam's confidence cycle | P2, P3, P5, P7, P18, P20 |
| §2.9 | Providers: F4 `ratings.update / odds / level`, `estimate.route`, `progress.steps_to`, `progress.cause_of` → F5, S4, S1, S8. S8's contest rating calls `ratings.update` for its item side (one rule). F5 `blueprint.siblings`, `blueprint.lookalikes` → S4, S3 (T4), S8. F1 `UI.atlas` → S1 (U8), S4 (P14). F2 `UI.parseSet` → S4. T-bank `Item.steps`, `Item.desmos`, `satbank.formulas` → F5, F3. S7 `plan.today_summary().minutes_left` → S4. S9 `words.today_summary`, `words.due_items(learner, n)` and `words.grade_item(learner, token, answer, ms)` → S4 (word cards). T-bank `material/cb_index.json` → F4 (priors), F5 (P13 index), S4 (College Board counts) | P1, P3, P8, P10–P15, P17, P18, P24 |
| §2.9 S4 hooks | "word chips in the verdict (`feedback.words`)" is not built: `words.of_reason` maps misconceptions to math-language words, and decision 2 ships no math-language deck. `UI.gloss` on stems stays only if the Words section keeps an EBRW gloss list | decision 2 |
| §2.12 F4 | F4 owns `server/ratings.py` | P11 |
| shell-me U1 | The queue gains a `rematch` row for `cfg.rematch_due ≤ today`. The builder's Ready row reads `GET /api/next?limit=3` | P15, P19 |
| shell-me U2 | `GET /api/types/{t}/example` also returns key, reasons, steps and `step_of` (reserved seeds only). `types.py` also reads `material/cb_index.json`: an ID outside the exact map resolves to its skill and tier ("Close"), an R&W ID reads "Reading & Writing question: logged for the R&W bank", and `via: 'none'` is left for IDs in neither. `POST /api/mistakes/log` takes `subject` (`rw` stores the ID or text, skill and letter for the EBRW bank). The helper's coverage line counts the index | P2, P13, P15 |
| shell-me U5 | `source:'probe'` also takes `topics:[t]` and `count: 8`: a staircase per skill with end-mode feedback | P11 |
| shell-me U6 | Source `habit` takes `habits: [ids]` | P6 |
| shell-me U7 | "When you guess" reads `attempts.conf = 'guess'` as well as `guess` | P7 |
| shell-me U8 | The atlas grid is F1's `UI.atlas` in kit.js, with the Due overlay | P14 |
| today T3 | `progress.warmup_candidates` gains kind `marked` (a flag 2+ days old whose template has no right first try since) | P12 |
| today T4 | "Show the example" sends `hints: 1` instead of `guess: true` (same counting, clean calibration). "A tier up" uses `blueprint.siblings` | P2, P18 |
| today T7 | `progress.causes` uses `attempts.miss_kind` when set, and adds a `misread` segment shown when non-zero | P8 |
| today T8 | The speed drill's `timing:'pace'` uses per-question budgets | P16 |

---

## 4. Rejected

* **Owing 3 clean answers after a Sure-and-wrong miss** (outcomes #1, unfair-advantage #6):
  Review's counts would swell for active taggers, and R9's check-ins already test whether the
  fix held. Ranking deliberate Sure misses first and opening the explanation carries the
  urgency.
* **Confidence chips beside Check** (experience #8, unfair-advantage #6): an extra optional tap,
  which shell-me and today.md already rejected. The split Check (P7) takes the same tap.
* **"Sure · Think so · Guessing" wording and `conf` as 0/1/2 replacing `guess`**
  (unfair-advantage #6): Tests already use Sure / Unsure / Guess (§3.4), and R8's `guess` column
  stays.
* **A fast "think so" miss filed as a slip owing 1** (unfair-advantage #6): T7's slip rule
  (P8) decides slips from history and time, one rule everywhere.
* **A per-learner Leitner `boxes` table** (outcomes #2) and **`type_memory`**: T3 already
  derives the schedule from attempts, and a second schedule would disagree with Today.
* **Review slots from any skill by default in hand-built sets** (outcomes #2): a student who
  picked Circles and gets Percentages is surprised. `any` is the default for Ready cards,
  Coach's pick and Up next.
* **Two clean answers at least 20 h apart to close a mistake** (outcomes #5): R9's check-ins at
  3, 10 and 30 days already test whether a fix held; changing the close rule would ripple
  through Review's counts. The final round is taken.
* **Steps and hints cut from the rationale's first clause** (outcomes #3, #8, and the outcomes
  explanation gap): today.md rejected the same cut, which is often nonsense or gives the answer
  away. Steps come from `Item.steps` only.
* **`attempts.helped`, or `guess` widened to a count** (outcomes #3, #8): `attempts.hints` is
  that count, kept apart from confidence.
* **Hint key `J`** (outcomes #8): `J` moves in the players and lists (§2.8). `W` is free.
* **Type states New · Learning · Solid · Mastered** (outcomes #6): a second vocabulary beside
  U8's unmet / met / ready and R37's words. U8's states plus the Due overlay say the same.
* **Mastered requiring a right inside test pace** (outcomes #6): it mixes pace into readiness;
  Fluent (P16) says it separately.
* **A probe seeding types straight to Solid** (outcomes #9): one right answer is not spaced
  proof. Probe answers file normally and settle `skill_ratings`.
* **"Graph it" loading the question into Desmos before answering** (outcomes #10): it solves
  the question for the student; on the test they type the setup themselves. The walkthrough
  comes after the verdict, and Desmos drills train the typing.
* **Tier budgets 60 / 95 / 130 s** (outcomes #7): 65 / 95 / 126 s sums to module 1's 2,100 s
  on its 7 / 8 / 7 mix.
* **A "park it" line at 2× the budget** (outcomes #7): two passes offers Skip at 1.5×, early
  enough to matter; 2× stays the time-sink line in the summary.
* **"Tighten": budgets 10% lower after an under-pace set** (outcomes gap), and **a separate
  Pace ladder timing mode** (unfair-advantage #9): the Fluency sprint's ×0.85 target does both
  inside one preset.
* **"Name the type first" picker in Mix-up** (outcomes #12): an extra step labelled with skill
  names that are not student words. The per-type "here vs usually" lines show the mix-up.
* **Opening "Your rule" counting as a hint** (outcomes #13): it would punish writing rules. The
  rule is the student's own knowledge.
* **Enter on page load starts the first ready set** (outcomes #14): an accidental start. Enter
  in the empty command line does it on purpose.
* **Preselecting the matching option after Cover, with a second Check** (outcomes #15): P5's
  version files the typed value as the first try, which is the diagnosis.
* **A reason on each mark (Unsure / Slow / Method?)** (outcomes gap): the split Check carries
  Unsure and the stopwatch carries Slow. Marks come back through T3 (P12).
* **A suggested "Learn · Train · Test" style from type states** (outcomes gap): U15's modes and
  the exam-date stage already choose.
* **A second points model ("≈1.6 of 4.1 test questions lost")** (outcomes #4): U4's `gains` is
  the one source. The row prints the same framing from `per_test × (1 − accuracy)`.
* **Points as ranges ("≈12–18 pts")** (unfair-advantage #12): Me and Today print U4's one
  rounded figure; the builder matches them.
* **"Same math, a different story" twin axis** (unfair-advantage #4): only 10 templates record
  two or more contexts. Revisit when T-bank records `ctx`.
* **A same-seed grid-in twin** (unfair-advantage #4 as written): the student has just seen that
  key. The grid axis uses a fresh seed; same-seed MC versions feed P4 instead.
* **Mastery ×1.25 for solving without the choices** (unfair-advantage #3): a second mastery rule
  for one tool. Solve-first accuracy is shown on its own.
* **Mis.habit tags authored in the bank** (unfair-advantage #2): U6's 11 families already tag
  across topics; open question 18 stays the place for exact mistake identity.
* **Levels from rating ranks within a tier** (unfair-advantage #5): with every item at its
  prior, a rank is arbitrary. P11 uses fixed cut points and says "rough".
* **"You" as `learners.rating`** (experience #10): that is Compete's one contest rating across
  all skills. `skill_ratings` is per skill.
* **The level strip hidden behind "Advanced" until 30 types are measured** (experience #10):
  P11's levels work from day one, so nothing needs hiding (decision 4).
* **Worksheet versions A–D, QR answer entry and a `/w/` page** (unfair-advantage #10): shell-me
  and today.md rejected printed per-student packs with QR entry, and with no classes
  (decision 5) there is no one handing them out. P22 gives each taker their own numbers
  online, and the worksheet already prints and can be answered online.
* **Shareable preset codes `?preset=CODE`** (unfair-advantage presets gap): "Copy link" gives
  the same thing from the existing deep link.
* **The key shipped in the question payload, and offline answering with verdicts** (experience
  #7): anyone could read keys in devtools and farm the practice-rank board (R3). One round trip
  (P23) gets most of the speed; `UI.saveQueue` rides out brief drops.
* **Desmos folders for the walkthrough** (experience #6): `getState` / `setState` restores the
  student's graph with the documented API.
* **A separate `official_map.json` / `official.json` build step** (experience #1,
  unfair-advantage #1): U2's `types.py` already builds the map at startup.
* **A separate `quarantine.json`** (experience #11): U3's `quarantine` table is the one store.
* **Math-word chips in the verdict** (§2.9's S4 hook): decision 2 ships no math-language deck.
