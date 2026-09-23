# v2 upgrades: Score report and results

Written 2026-09-23 for `spec/rebuild-v2.md` §3.5 (lines 6055–7045). It merges three designers'
proposals (outcomes O1–O11, experience E1–E12, unfair advantage A1–A12, and their 53 parity
gaps) into one build-ready list, SR1–SR25, against the TopTierPrep inventory in §3.5.1,
`spec/toptierprep-teardown.md`, `ttp-notes.md` and the live walk in `ttp-live.md`.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.5 where
  they differ; §3 lists every change. Part 2 resolutions (R1–R38) still hold, except the lines
  named in §3.2 "Outside the section".
* **Shared with the sibling files.** These upgrades reuse what the siblings already specify,
  and never specify it twice:
  * `today.md`: `progress.causes` and its five causes clock · entry · slip · trap · gap (T7),
    `estimate.rescore` and the sitting card's cause and worth lines (T16), `UI.twinSheet` (T5),
    Learn it, `source:'learn'` (T4), `estimate.per_question` (T8), the practice delta (T10), and
    the compare endpoint T16 asks S6 for.
  * `practice.md`: worked Steps with the step where your answer left the path (P1), borrowed
    grid-in names (P4), `attempts.conf` (P7), `attempts.miss_kind` and its chips (P8), ratings
    and levels L1–L7 (P11), `budget_ms` per type (P16), twins on an axis (P17), Rematch and its
    `slots` (P18), type notes with `notes.seed = −1` (P20).
  * `shell-me.md`: the instant key check (U3), `estimate.gains / need / projection` (U4, U9),
    habits (U6), `progress.pace` and `UI.quadrant` (U7), the type atlas (U8), Climb (U11), the
    lever popovers (U13), the Up next queue (U1), page sections in the nav (U26), question links
    that send a twin (U28).
  * Review (§3.10): flag calibration, the worksheet, Spot the trap, the family API.
    Tests (§3.4): the twin kind, the custom test from misses, `qstate`, pauses, extended time,
    notes, peers.
  Where this file needs one of them to change, §3.2 lists the change.
* **The bar.** A student who uses TopTierPrep's score report today opens ours and wants to
  switch, because it tells them what each miss cost, why it happened, what to do first and
  whether the fix held. Parity is failure.
* **Names.** Upgrades are SR1–SR25. Builders are Part 4's tasks (F1–F6, S1–S10, T-bank). S6
  owns `web/results/**`, `server/api_results.py`, `web/assets/results-ui.js` and
  `server/checks/s6.py`. Shared functions stay with their owners (F4 `estimate.py` and
  `progress.py`, F3 `UI.review`, F1 charts).
* **Subject-aware** (decision 3). Every new payload about a section carries `subject` (`math`
  now): the ledger, causes, the second look, recovery, comparisons, the national table and the
  total. The total's R&W part is `source:'self'` today and becomes `source:'measured'` when an
  R&W bank scores a section, with no component change.
  * **Review items carry `subject`** too, and every question has one canonical address,
    `{subject}-m{module}-{n}` (`math-m1-7`; `math-7` for a sitting without modules). The hash
    and `?q=` parser reads `m1-7` and `7` as shorthand for `math-…`, so links already shared
    keep working when R&W arrives.
  * **Labels** print `M1 Q7` while a sitting has one subject, and `Math M1 Q7` / `R&W M1 Q7`
    when it has two. Aria-labels, CSV (`subject` and `address` columns), the player header and
    chips all call one helper, `UI.qlabel(item, sitting)` (F1).
  * **`UI.sittingCard`** (shared with Tests and Today) groups its chips by (subject, module):
    `M1 ✕ 1 6 7` today, `Math M1 ✕ 1 6 7 · R&W M2 ✕ 4` later.
  * **Route and count copy** reads its numbers from the payload, never from constants: results
    carry `route_rule [{subject, cut, needed, m1_asked, lower_ceiling, half_band}]` (the spec's
    `route_rule`, keyed per subject), so "14 of 22 sends you to the harder Module 2" is
    `{needed} of {m1_asked}`. Compare headings print the paired count ("SAME 44 QUESTION
    TYPES" is `paired`), and the ledger's `route.needed` comes from the same rule.
* **No new tables or columns.** The second look, seen keys, the visit log and the away log live
  in `sessions.qstate` (R7). The ledger, causes, recovery, comparisons and the crowd are
  computed on read from rows that already exist. `sessions.note` exists (§2.5). One data file
  is added: `server/data/cb_percentiles.json` (SR5).
* **Facts this file relies on** (code and db as of 2026-09-23):
  * `scoring.ANCHORS` = (0, 200), (0.25, 300), (0.5, 480), (0.75, 620), (1.0, 780); mid-scale
    the curve rises 560 points per unit of weighted fraction.
  * Weights easy 1 / medium 2 / hard 3. Module 1 carries 44 weight points
    (`blueprint.TIERS` 7 / 8 / 7), the upper module 2 52 (3 / 8 / 11), the lower 36 (11 / 8 / 3).
    In a routed-up section (96) one miss mid-scale moves the band's centre about 6 (easy), 12
    (medium) or 17 (hard) points.
  * `ROUTE_UP_AT` = 0.60 (14 of 22). `LOWER_ROUTE_CEILING` = 580. `MOCK_HALF_BAND` = 70 for a
    section; `HALF_BAND` = 100 for a module or the diagnostic.
  * `section_score` rounds low and high to tens, so one miss moves the printed band by 0 or 10.
    The ledger (SR1) works on the unrounded centre and prints to the nearest 5.
  * The results are `sessions.result` JSON written at finish; the review is marked on read from
    `marked_questions(row)`. A rescore is a rewrite of `result` plus a note (SR19).
  * `blueprint.SPR_AT` = (6, 7, 13, 14, 21, 22): 12 of 44 questions are grid-ins.
  * The db holds 19 mock sittings (12 finished), 8 diagnostics, 16 drills, 3 challenges,
    287 attempts (166 with `ms`) and 26 learner codes. No (template, tier) has 20 first tries.
    So the measured crowd (n ≥ 20) is empty for months, levels read "rough" (P11), and the
    in-site percentile reads "needs 20". What works on day one: the national table (SR5) and
    P11's ratings, which exist from the first answer. SR12 builds every crowd feature on the
    ratings first (your odds, and the odds of a 1000-rated student labelled "estimated") and
    switches each line to the measured crowd once its n reaches 20.
  * Learner codes that start `sample:` (SR24) are left out of every figure computed across
    students.

---

## 1. Scorecard

"v2 spec" is §3.5 as written. The verdict says why ours is way better. Where v2 was only at
parity (or below), the verdict names the upgrade that fixes it. Rows 1–34 are TopTierPrep's
features in this area (§3.5.1 and the two note files); rows 35–36 are what they miss entirely.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Report header | "PRACTICE TEST REVIEW · Paper #47 · 2025-08-31", a date styled like an official form | Kind eyebrow with a sequence number ("FULL MATH SECTION #7 · ADAPTIVE"), date, time, minutes, Timed/Untimed | Eyebrows for papers, twins, custom, shared and Prove it. Condition chips (timing, calculator, pauses, window left, harder module 1). A validity badge: "Counts toward your estimate" or "Practice only: 1.5× time". Deltas compare like with like. An editable sitting note (SR18) | v2 PARITY (the same facts plus a number). **SR18 → WAY BETTER.** The header says whether the score can be trusted and what it is compared with. |
| 2 | Section ring gauge | A ring, score/800, "2 Correct, 25 Wrong", which counts blanks as wrong and contradicts the tiles below | A 240° arc 200–800: band, midpoint tick, the previous band as a ghost, a target tick; one bucket set (R35) | Adds the hollow "With a second look" band (SR3), the dotted "Today ≈" band from what has been proven since (SR6) and a dashed What-if band (SR2). The lost-points bar sits right under it (SR1). On the first view it sweeps from the previous band (SR4) | v2 PARITY: their ring with more ticks. **SR1 + SR3 + SR4 + SR6 → WAY BETTER.** One picture shows the score, what the slips cost, and what has been won back since. |
| 3 | Total score card | Blue centre card: Total 420/1600, a bar, "4 of 49 correct" | Math only, captioned "Reading and Writing is not on SAT Freshman yet" | "Total ≈ 1,130–1,270 · about the 62nd–83rd percentile · Math measured here · R&W 610, you entered Sep 12 (Bluebook)", the R&W part hatched, a stale warning after 60 days, R&W entries kept as dated history under the chart, the gap to a total target split into what this report can move (Math) and what it can't (R&W), and an inline "Add your R&W score" when there is none (SR4, SR5) | v2 BELOW theirs. **Still below theirs until the R&W bank exists (decision 3), mitigated by SR4 + SR5.** Theirs measures R&W; ours adds a number the student typed. The mitigation makes it honest and useful (provenance, national total percentile, a split gap), and the payload turns `source:'measured'` with no component change when R&W questions land. |
| 4 | Ranked pill and percentile | "N% scored at or below you on their first attempt", ranked sittings only, else "Practice test — not ranked" | The same rule on SAT Freshman's first sittings, with n, a 20-student floor, and why a sitting is not ranked | Adds where the band sits on College Board's published national user percentiles, with source and year, and a dot histogram of first sittings once n ≥ 20 (SR5) | v2 PARITY, and in practice worse: 12 finished mocks means "needs 20" for months. **SR5 → WAY BETTER.** A real reference point from the first sitting. |
| 5 | Count-up numbers | Every number counts up from 0 on every load | Numbers count up over 600 ms on first paint | Numbers count from the previous same-kind sitting to this one and a delta chip lands, only on the first view after Finish. Up to 2 earned milestone stamps. Revisits are static (SR4) | v2 PARITY (motion with no meaning). **SR4 → WAY BETTER.** The motion is the change. |
| 6 | Performance summary tiles | Correct / Incorrect / Unanswered / Accuracy % | 8 tiles (adds Time, Per question, Flagged, Changed), each a filter; missing data says why | 10 tiles. Counts carry their cost ("Incorrect 11 · ≈ −130 pts"), Correct says what the target needs on this route ("need 35 for 700"), Unanswered says a guess costs nothing. New Second look and Recovered tiles (SR1, SR2, SR3, SR6) | v2 PARITY (more counts). **SR1 + SR2 + SR6 → WAY BETTER.** Each tile says what it is worth and what to do. |
| 7 | Domain performance | R&W \| Math toggle; 2×2 cards with %, a 7-segment level bar and "13% · 13% of test section, 1-8 questions" (meaning 1 of 8) | 4 cards: %, right/asked, the difficulty-weighted 7-segment bar, a per-question strip, the SAT share, a delta, "Missed most" | Each card adds "≈ −55 pts · 40% of your gap" and its best-value skill with Start, and expands in place to its skills with "Fix this domain". Sorted by points. A weight check: "Algebra is 35% of the section and 48% of the points you lost". The domain shares are Shapley splits of the gap, so they add to exactly 100% on either route, even at the 580 cap (SR1, SR2) | v2 PARITY (their card with the copy fixed). **SR1 + SR2 → WAY BETTER.** Shares that add up, in scaled points. |
| 8 | Per-domain `domainScore` | Returned by their API, shown nowhere | Nothing equivalent | Points lost per domain in scaled points: exact re-scoring split fairly across domains (Shapley), so the four add to the whole gap (SR1) | v2 missing. **SR1 → WAY BETTER.** It shows the number theirs hides, and it adds up. |
| 9 | Question review filters | All / R&W / Math / Flagged (n) | Show (7 states with counts, 0 disabled) plus Module, Domain, Topic, Difficulty, Format and Time; Colour by; View; state in the URL | An "Act on" row: Cause, Should-have-had, Sure and wrong, Guessed right, Recovered, Slipping, Not looked at, Has note; Show adds Mixed (practice), Skipped and Voided (contests); a 17-column table with a specified layout (sticky #/Skill, its own scroll box, glyph columns, a two-table landscape print) that sorts by Worth (SR15, SR25) | v2 wider, PARITY in kind (it slices by property). **SR15 → WAY BETTER.** It filters by what to do next, and the table is buildable at 1280 and 390. |
| 10 | Review legend | Correct / Incorrect / Unanswered / Flagged (n) | Always visible, glyphs, counts, follows Colour by | Adds legends for Cause, Points, Level and Crowd, and the ▲ route marker (SR1, SR15) | **WAY BETTER already.** |
| 11 | Per-module colour grids | "R&W - M1 2/27", green / red / grey squares, an orange dot when flagged | Status cells with glyphs; groups with right/asked/time; filtered cells at 30% | Colour by Cause, Points, Level or Crowd (the crowd estimated from ratings until measured); a hover card with worth, cause, your odds, % of students right and Try one; Shift/Ctrl-click and long-press selection with an action bar: Fix · Twins · Retry sheet · Save · What if; Mixed, Skipped and Voided cells (SR15, SR12, SR25) | v2 PARITY in kind (their grid, better labelled). **SR15 → WAY BETTER.** The grid is a control, not a picture. |
| 12 | Review modal chrome | Title, status and flagged chips, Hide answers, Report, "1 of 49", Close, ← → | A full-screen player in the practice-session layout: navigator, labelled tools, position within the filter, keys, `#q=` hash | Swipe on the phone, the next question preloaded, a Second look mode, a two-up compare mode (SR16, SR3, SR7) | **WAY BETTER already.** SR16 makes it instant and thumb-friendly. |
| 13 | Review modal body | Passage, choices with the key in green, Your / Correct answer boxes, "Justification:" then "Distractor Analysis" with one line per wrong option | Key tagged, your pick struck, every wrong option's named misconception open by default, answer boxes for every format, "Also accepted", the explanation, the mistake state | Steps on this question's numbers with the step where your answer left the path (P1), required at launch for every template a section or the diagnostic can draw, checked by `tools/steps_coverage.py --section` at 100%; a template without steps opens with a written Method block (the idea, the method, the check that catches the common trap), never the bare 21-word line; your odds on the type (SR12); "your 3rd time · also in Systems" (SR11); a grid-in diagnosis (SR10); "See one solved first", with the option your mistake produces on the new numbers tagged (SR16) | v2 ahead on labels, PARITY on depth (our rationale is a median 21 words; theirs is a paragraph). **SR16 + P1 at 100% of section templates → WAY BETTER.** Every reviewed section question is worked on its own numbers and shows where the student's working left the path; theirs is one paragraph about the item. |
| 14 | Hide answers | Hides the key box and explanation, persists across Next; you cannot re-answer | A persistent mode; a pick reveals locally and files nothing, which contradicts R21 | **Second look**: every miss whose key you haven't seen is re-answered cold before it shows, filed as a repeat (R8), which sorts slips from gaps and draws a "With a second look" band (SR3). One server function holds back every field derived from the key (answer, reasons, rationale, mistake, steps, diverge, option_steps, accepted, diagnosis, option shares, key evidence, crossed-key marks) from every payload, CSV and print while the offer stands. Hide answers stays for self-testing questions already seen | v2 PARITY, and a conflict with R21. **SR3 → WAY BETTER.** Retrieval practice plus a diagnosis, and the key really is hidden. |
| 15 | Per-question data | No domain, skill, difficulty or time in the payload | Skill, difficulty, format, time, trap and history on every item | Adds cause, worth, level, crowd, second look, recovery and visits (SR1, SR3, SR6, SR8, SR12, SR13) | **WAY BETTER already.** |
| 16 | Report a problem | A "Sent with your report" box, title 0/200, 6 categories, details 0/5000, 10 images × 50 MB, then silence | Their modal, "at least as capable" (R17 makes it Shell's modal) | U3's independent-solver check answers most key disputes in a second, inside the report. An upheld correction re-scores the sitting and says so on it ("re-scored 520–660 → 530–670") (SR19) | v2 PARITY. **SR19 → WAY BETTER.** A real fix reaches past scores; theirs can't correct a fixed paper. |
| 17 | Details popover | QUESTION ID, DOMAIN, SKILL, DIFFICULTY | Adds format, time, sitting, position and Copy ID | Adds the level L1–L7 and what it rests on, "your odds were 82%" from day one, "about 64% of students get this type right (estimated)" until 20 first tries and then the measured rate with its time, your record on the type, what it is worth here, the College Board question it is modelled on, and "Copy link to a fresh one" (SR12) | v2 PARITY. **SR12 → WAY BETTER.** Personal odds from the first answer; theirs has none. |
| 18 | Question Score 1–7 | A builder filter only; on no report and in no popover | Easy / Medium / Hard glyph | P11's L1–L7 on every question with its basis ("measured from 212" / "rough (6)"), plus your odds; Colour by Level; Should-have-had (a miss where your odds were 75%+) and Hard for you (35% or less), both working on the shipped db (SR12) | v2 BELOW (no finer scale). **SR12 → WAY BETTER.** A level that says what it rests on, and odds that are about the student, from day one. |
| 19 | Attempt History | QBank only, per exact item: "#1 ⊗ Incorrect · Option A · 00:22" | "Earlier on this question type": the last 5 attempts on the template | A trajectory for the type (result and time per attempt, including twins and Prove it since), ending in Recovered or Slipping (SR16, SR6). A practice set also lists this sitting's tries: "Tries in this set: ✕ A · used the slope as the intercept · 0:22 → ✓ C · 0:41" (SR25) | v2 dropped their per-try history. **SR25 + SR16 → WAY BETTER.** Every try with its named mistake, then the type's direction. |
| 20 | Question overview Status \| Difficulty | QBank session only | Colour by Status \| Difficulty \| Time in the report | Adds Cause, Points, Level and Crowd (SR15); Mixed (✕ then ✓ in retry mode, R20's ~) as its own status, Show chip and legend entry (SR25) | v2 had no Mixed. **SR15 + SR25 → WAY BETTER.** |
| 21 | Score Overview card | "Total Estimated Score / Math / English" only after a full four-module test | A current estimate from any scored sitting, confidence with a reason, trend, latest, best, target, exam date | Adds what would raise confidence as a one-tap action, practice movement since the last test (T10), the projection to the exam date (U9), "fix your top 3 ≈ +34" (U4), Climb (U11) and the national range (SR21, SR5) | **WAY BETTER already** (it fills from any sitting). SR21 makes it look forward. |
| 22 | Share / Export Report | A button with no click handler | A read-only share link, Print / Save as PDF, CSV, a tutor progress link | Adds a repair pack (the misses regenerated, fresh twins, a key with every option's misconception), a retry sheet, a tutor packet, and question links that send a twin (SR20) | **WAY BETTER already** (theirs is dead). SR20 prints new practice, not only the past. |
| 23 | Results list cards | "Paper #47 · COMPLETED: 8H AGO", red chips mixing wrong and blank as plain spans, [Review], no score | Score, delta, duration, wrong vs blank chips that open the question, "still open", Review, Fix | Peek in place (a mini report with module strips that open the player), a recovery ring ("Recovered 9/13 · ≈ 60 open"), the cause line, "Reviewed 7 of 13", select two to Compare, J / K / Space / Enter / F / X (SR23) | v2 PARITY in kind. **SR23 → WAY BETTER.** Five sittings triaged without a page load. |
| 24 | Results paging and empty state | Pages of 10; "No completed exams yet. / Complete a practice test to see your results here." | 20 a page with Show more, week groups, an empty state with Practise | Week summary lines ("This week · 3 sittings · 128 questions · 6 h 10 m · +40"). A new learner gets a live sample report and "Add a score you already have". The sample learner is read-only, dated, and left out of every figure computed across students (SR23, SR24) | Empty state PARITY. **SR24 → WAY BETTER.** A new student sees the value before sitting for 70 minutes, and nobody else's numbers move. |
| 25 | Estimated Score card (Practice catalog) | "Math 200-280 · LOW CONFIDENCE" with a reason and a trend; a section at 200 is dropped | R16's estimate: confidence with its reason, trend; floor scores count | Adds "One more full section → High · Start 70 min", the projection and the practice delta (SR21) | v2 PARITY in parts. **SR21 → WAY BETTER.** Low confidence becomes a button. |
| 26 | Counting quirks | A "Custom Set · 2 Modules" never counts ("Not taken", attempts 0/1) | Every scored sitting counts; one bucket set | Also like with like: an extended-time sitting says "Practice only" and is compared with its own conditions (SR18) | **WAY BETTER already.** |
| 27 | Score Trend chart (Profile) | A line chart, "Latest: 0" | Bands, trend line, target line, estimate zone, tooltips, range and kind filters | Adds outside scores as hollow diamonds, what happened between two sittings, the projection cone, brackets joining twin pairs; two clicked points open Compare (SR21, SR7) | v2 PARITY (it plots outcomes). **SR21 → WAY BETTER.** Effort and score read together. |
| 28 | Profile tiles | Streak / Tests / Solved / Vocab; the streak disagrees with QOTD's | 6 totals with their windows stated, a 14-day chart | Adds "Question types met · 185 of 386" (U8) and "Recovered this week · ≈ +35" (SR22) | v2 PARITY. **SR22 → WAY BETTER.** |
| 29 | Time analysis (Contest Rankings) | "Average seconds per answered question, by difficulty", empty | Accuracy and average time by difficulty and format; pace bars per question with rushed and long chips | A clock replay per module (where you fell behind, revisits, blanks never opened); each question against its own time budget (P16); Banked / Time sink / Rushed / Stuck chips; what a time sink cost; Speed, Careful and Learn-it sets (SR13) | v2 PARITY (their measure, filled in). **SR13 → WAY BETTER.** |
| 30 | Per-contest stats | Score / Correct / Incorrect / Skipped / Voided; answers only after the contest ends | Challenge hero "#12 of 140 · average 6.1/10" and the crowd per option letter | Compete's own numbers on the report: "Points 230 · base 200 · pace 20 · finish 10" and "right 8 · wrong 1 · skipped 1 · voided 0" from `sessions.result`; tiles Points / Right / Wrong / Skipped / Voided / Time / Per question / Rank; Skipped and Voided cells with R20's tokens; a key correction is its own state, "Removed from scoring" (SR25). The crowd per slot and per named misconception, which works with twin challenges (decision 1), where option letters never line up (SR12) | v2 dropped Skipped, Voided and the points, and its crowd broke under decision 1. **SR25 + SR12 → WAY BETTER.** The same counts as Compete's panel, plus how the field fell for each trap. |
| 31 | Recent Tests card (dashboard) | "TOTAL SCORE · 23/09/2026 · 420 · R&W 200 · Math 220 · [Review]" | `UI.sittingCard`, shared | T16's cause and worth lines plus SR23's ring, reviewed meter and peek, one component | **WAY BETTER** (T16 + SR23). |
| 32 | QBank session report | None: sessions never end or summarise | Every practice set gets the full report | A rematch is compared slot by slot in the same region (P18, SR7); end-mode sets get a second look (SR3); retry-mode sets show Mixed and every try (SR25) | **WAY BETTER already.** |
| 33 | Another question like the one you missed | Impossible: fixed papers, and a retake shows keys already seen | Try one like this inline, Fix these variants, Retake as a test | See one solved first for gaps (SR16), twins on an axis (P17), Prove it under test rules (SR6), a twin test compared slot by slot (SR7) | **WAY BETTER already.** SR6 and SR7 prove the fix held. |
| 34 | Unfinished sittings | Resume by URL only; resume limits | An In progress group with Resume or See your report | Unchanged | **WAY BETTER already.** |
| 35 | Where the points went, what to fix first | Nothing links a miss to points | A what-if line for one tier | Every miss priced; cause and difficulty bars that add up exactly; the route cliff; the path to target ("4 questions from 700"); a Fix ordered by points per minute; What-if mode (SR1, SR2) | Missing on theirs; v2's one line was a start. **SR1 + SR2 → WAY BETTER.** |
| 36 | Flags and how you judged your answers | A Flagged (n) filter and a dot | A Flagged tile ("2 of them wrong") and filter; answer changes; the confidence calibration Tests §3.4.7 promised has no region | **Judgement**: Sure / Unsure / Guess against right and wrong, "Sure and wrong" first in Mistakes, what flags were worth, your first-instinct record, crossed-out keys, time away, notes (SR9) | v2 PARITY, with a missing region. **SR9 → WAY BETTER.** |

---

## 2. Accepted upgrades

Grouped by what they answer. Each gives why, screens and components, controls and states, data
and endpoints, how it uses the rest of the site, and acceptance checks a verifier can run.
Learner codes in the checks start `a:v2revrep`; S6's port is 8026.

Shared rules for every upgrade:
* **Scored sittings** are mock, module, diagnostic, paper, twin and shared sittings that
  produce an estimate. Custom tests and harder-module-1 sections finish with `scored:false`
  (Tests check 11), and drills and challenges have no band: for them every points figure is
  left out and the counts stay.
* **Owner only.** Second look, cause corrections, rules, notes, Put in my plan and every drill
  action need `mine:true`. A read-only viewer (`mine:false`) sees the ledger, causes, recovery,
  compare, judgement and pace, as the spec already lets them see the review.
* **Worth** is printed `≈ +15`, rounded to 5, or `under 5`. Points are never added up on
  screen except where the server has summed them exactly (the ledger's buckets, recovery).
* **One primary per region** (§0 of the spec) now covers the page header, the second-look
  banner, the player, the skill panel and the selection bar.

### Layout after these upgrades

**Report, desktop (≥1100)**, 12 columns, in this order (SR14):
```
header ×12                (eyebrow, conditions, note, actions)
recovery strip ×12        (SR6, scored sittings, owner)
second-look banner ×12    (SR3, while offered)
hero: gauge ×5 | facts ×7
ledger ×12                (SR1)
compare ×12               (SR7, when paired or ?vs=)
takeaways ×12             (SR14, three cards)
tiles ×12                 (5 × 2)
habits ×12                (SR11, when it applies)
mistakes ×8 | value ×4    (SR2 "Best value next" beside the list)
review ×12                (toolbar, act-on row, grid or table)
modules ×12 · domains ×12 · skills ×12 · judgement ×12 · split ×12 · pace ×12
up next ×12
```
A sticky jump bar appears under the page bar once the hero scrolls away (SR14).

**Tablet (860–1099)**: the same order; tiles 5 × 2; mistakes and value stack.
**Phone (390)**: one column in the same order; tiles 2 × 5; the jump bar is a `Jump to ▾`
select beside the sticky primary; no horizontal page scroll.

**Results `/results/`, desktop**: header · estimate ×4 | chart ×8 · gap to target ×12 (SR22)
· totals ×12 · last 14 days ×12 · why you miss ×12 (SR22) · split ×12 · pace ×12 (U7's card)
· domains across sections ×12 · skills ×12 · top misconceptions ×12 · sittings ×12.

---

### A. What the score means

#### SR1. Where your points went: every miss priced, by cause or by difficulty, with the route cliff

*From: outcomes #2, experience #1, unfair-advantage #1; the gauge, tiles, domain and domainScore
gaps of all three (OG3, OG4, EG4, AG1, AG5, AG6). Effort M. Builders: F4
(`estimate.ledger`, `estimate.mid`, asserts), S6 (payload, `#ledger`, worth everywhere), F1
(`UI.stackBar`).*

**Why.** Theirs says "Total Score 420/1600 · 4 of 49 correct" and keeps a per-domain
`domainScore` it never shows. Nothing on it links a single miss to points, so a student can't
tell whether 3 easy slips or 1 hard concept is the bigger leak. Our scoring is ours, pure and
cheap, so every miss can be re-scored exactly.

**The model** (`estimate.ledger(sid)`, F4, pure over `marked_questions(row)`, the answers, the
route taken and SR8's causes):
* **The measure** is the band's unrounded midpoint, `estimate.mid(earned, possible, route,
  half)`:
  * centre `c = scoring._interpolate(earned / possible)`;
  * `low = max(200, c − half)`, `high = min(800, c + half)`;
  * on the lower route `high = min(high, 580)` and `low = min(low, high − 10)`;
  * `mid = (low + high) / 2`. `half` is 70 for a section and 100 for a module or the diagnostic,
    as scoring does.
* **Per miss**: `pts` = the midpoint with only this question right, minus the midpoint as sat.
  The route is held as taken. `capped: true` when the 580 cap ate part of it.
* **Buckets, exact and order-free (Shapley).** Per-miss values do not sum (the curve bends and
  the 580 cap clips), and a cumulative flip in a fixed order hands whichever bucket goes first a
  different share. So every bucket set is split by Shapley value: a bucket's points are its
  gain averaged over every order of flipping the buckets. With `v(S)` = the midpoint with every
  miss in the buckets of S flipped right, minus `mid`, and k buckets,
  `pts_i = Σ_{S ⊆ N∖{i}} |S|! (k − |S| − 1)! / k! · (v(S ∪ {i}) − v(S))`.
  * It needs `v` on every subset once: 2^k re-scores. **By cause** (clock · entry · slip · trap ·
    gap, SR8) is 32, **by difficulty** (easy · medium · hard; blanks in their tier) 8, **by
    domain** (4 Math domains) 16, **incorrect vs blank** (the tiles) 4.
  * Each set sums to `all_right.mid − mid` exactly (Shapley's efficiency), on either route and
    at the cap, so a share can never pass 100% and "% of your gap" is honest.
  * An empty bucket gets 0; two buckets whose misses are interchangeable get equal points.
  * **Printed** to the nearest 5 by largest remainder, so the printed buckets add to the printed
    total. Per-miss `pts` stay as they are (this miss alone), and the page never adds them.
* **All right on this route**: `{low, high, mid}`.
* **Route cliff** (a section on the lower route): `{m1_right, m1_asked, needed, short_by,
  savers: [qid], cap_cost}`, with `needed` and the ceiling read from the subject's
  `route_rule` (14 of 22 and 580 for Math today).
  * `savers` are Module 1 misses, easiest first, then by `pts`; the first `short_by` of them.
  * `cap_cost` is the uncapped all-right high minus the ceiling, when positive.
* `ponytail:` about 44 per-miss + 60 subset re-scores (32 + 16 + 8 + 4) of at most 44 items
  per read, a few ms; cache per (sid, answers hash) only if profiles show it. A subject with
  more than 6 domains would switch by_domain to sampled orders; Math has 4.

**Region `#ledger`** (right under the hero; scored sittings):
* **Heading** `WHERE YOUR POINTS WENT`, with the line `About 140 points below all right on this
  route (710–790)`. On the right, `.seg By cause · By difficulty` (remembered in
  localStorage, try/catch).
* **The bar** (`UI.stackBar`, F1): one horizontal bar, segment widths proportional to points.
  * Each segment carries its label, points and count: `Traps ≈ 60 (4) · Slips ≈ 45 (5) · Clock
    ≈ 25 (3) · Entry ≈ 10 (1)`. On the phone the labels sit in a list under the bar.
  * Ink shades, the largest segment orange, never colour alone. A hidden table lists every
    bucket.
  * The legend lists all five causes (or three tiers) with counts; a 0 bucket is shown disabled.
  * The helper's `.quiet How this works` explains the split: `Each group's points are what
    fixing it is worth on average, whatever you fix first, so the groups add up to the whole
    gap.`
  * Each segment is a button: it sets the review filter `cause=<x>` (or `difficulty=<x>`) and
    scrolls to `#review`. Its tooltip: `Slips · 5 misses · ≈ 45 points · you had these`.
* **Route line**, when `short_by ≤ 3`: `Module 1: 13 of 22 (59%). 1 more right would have
  earned the harder Module 2. Your easiest Module 1 misses: M1 Q3 · M1 Q9` (the numbers from
  `route_rule`, the labels from `UI.qlabel`). Each chip opens the player. When `cap_cost > 0`:
  `On the easier Module 2 this section tops out at 580; all right here would have been 640.` Saver cells carry a small ▲ in the grid, with a legend entry
  "▲ would have routed you up".
* **Helper**: `Points on the band's midpoint, re-scored with this report's own scoring (easy 1,
  medium 2, hard 3), on the route you took.` with `.quiet How this works` → `/help/#points`.
* **Unscored sittings**: the region is titled `WHY YOU MISSED` and shows SR8's counts without
  points, with the line `Points are worked out for scored sittings.`

**Worth everywhere else.** `≈ +15` on each mistakes row, in the player header, in a sortable
**Worth** table column, in the cell's hover card and aria-label ("M2 Q4, incorrect, slip, about
10 points"), and as a `worth` CSV column.
* **Tiles**: Incorrect reads `≈ −130 pts · 9 still open`; Unanswered reads `≈ −25 pts · a guess
  costs nothing` (SR13).
* **Domains**: each card adds `≈ −55 pts · 40% of your gap`, and `#domains` gains `.seg By
  points · SAT order` (By points is the default for scored sittings). Under the cards, a weight
  check shows when a domain's share of lost points (its Shapley `pts ÷ total`) differs from its
  share of the section by 10 points or more: `Algebra is 35% of the section and 48% of the
  points you lost.` The shares always add to 100%. A card
  expands in place (its chevron, or Enter) to its skills in this sitting (right/asked, worth,
  open traps) with `.btn Fix this domain · 5`, and the per-question strip carries each
  question's difficulty glyph.

**Data.** Results gain `ledger: {subject, mid, all_right {low, high, mid}, total, per_q {qid:
{pts, capped}}, by_cause [{cause, n, pts}], by_tier [{tier, n, pts}], by_domain [{domain, n,
pts}], incorrect_pts, blank_pts, route {m1_right, m1_asked, needed, short_by, savers,
cap_cost} | null}`, or `null` for unscored sittings. Each review item gains `worth`.

**Uses the rest of the site.** T16's worth line on the sitting card, SR2's path and Fix, SR6's
recovery and SR22's overview all read this one function. U13's Band lever may too.

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

#### SR2. Win back the cheapest points: the path to target, a Fix ordered by value, and What-if mode

*From: experience #1 (the Fix pill), outcomes #2 (path to target, win-back rows),
unfair-advantage #1 (What-if mode and presets), unfair-advantage #4 (best value next, forecast,
plan), experience #3 (Put in my plan), OG3. Effort M. Builders: F4 (`estimate.rescore` with
`right`/`wrong`), S6 (UI and the whatif route), F5 (`order:'given'`), S7 (task `start`), F1
(`UI.gauge` redraw).*

**Why.** Study time is the binding constraint. A student grinding hard questions while easy
points leak is losing points per minute. "4 questions from 700" is a goal a student can count;
a band and a domain word are not. Theirs can't price anything.

**`estimate.rescore(sid, right=(), wrong=(), drop=())`** (F4) extends T16's
`rescore(sid, positions)` (positions = `right`): re-mark with those qids right, those wrong,
and those left out of scoring (SR19). The route is held as taken. It returns `{low, high, mid,
capped, route}` with the printed band in scoring's tens and `mid` unrounded.

**The path to target** (when the profile has a target and the ledger exists): flip misses
greedily by `pts`, highest first (ties: easier first), until `mid ≥ target`.
* Hero, under Target: `4 questions from 700 on this section: M2 Q4 (easy · slip) · M1 Q7 ·
  M2 Q11 · M1 Q20`, each chip opening the player.
* Blocked by the route: `700 needs the harder Module 2: 1 more right in Module 1 (M1 Q3).`
* Out of reach even all right: `All right on this route reaches 660; 700 needs the harder
  Module 2.`
* Reached: `Target 700 reached on this section.`
* The Correct tile's sub-line reads `70% of 44 · need 35 for 700`, where 35 = right + the
  path's length, so the tile and the path always agree.

**The Fix primary** (scored sittings): `Win back ≈ 60 pts · 9 questions · 14 min`.
* Misses are ordered by `pts ÷ minutes`, where minutes = P16's `budget_ms(template, tier)`.
  They are taken in that order until the minutes reach the learner's daily `minutes` (R15), or
  every miss when none is set. The points are `rescore(right = that subset)` minus `mid`.
* The body is `{from_session, only: [qids in that order], order: 'given', source: 'fix'}`.
* The ⌄ menu keeps every spec variant and adds, each with its count (0 is disabled):
  * `Everything · 13`;
  * `Traps only · 4`;
  * `Slips, timed at pace · 5` (`timing: 'pace'`);
  * `Clock losses: a paced set of these types · 3` (`timing: 'pace'`);
  * `Entry: grid-in rules and 5 grid-ins` (T7's body);
  * `Gaps: Learn it first · 2 types` (`source: 'learn'`, those templates, T4);
  * `Sure and wrong · 3` and `Guessed right · 2` (SR9);
  * `Should-have-had · 4` (SR12);
  * `Fix the selection · n` while cells are selected (SR15; it replaces the spec's "Just the 4
    shown").
* Drills keep the spec's `Fix these · 13`.

**Best value next** (`#value`, beside Mistakes on desktop, under it on the phone). One row per
topic with misses in this sitting, sorted by points ÷ minutes:
* the glyph and name, `≈ +25 on this test` (`rescore(right = the topic's misses)`), `3 misses ·
  about 5 min` (their budgets), and a value bar;
* `.btn Fix these 3` (`{from_session, only, order:'given', source:'fix'}`), `.quiet Practise
  skill` (`/practice/?topics=`), and `.quiet Put in my plan` when a plan exists;
* a forecast line under the top 3: `Fix the top 3: this test re-scores at 590–730 · your target
  700 falls inside` (`rescore(right = those topics' misses)`);
* a time line under it, when the learner has daily `minutes`: `The top 3 take about 25 min:
  under one of your 40-minute study days.` (budget arithmetic only, no forecast of points);
* the helper: `Re-scored on this test with those questions right. A guide to order, not a
  promise.`;
* each domain card's "best value" line (replacing "Missed most") is that domain's top row.

**Put in my plan** calls S7's `POST /api/plan/{id}/tasks {day, title, minutes, start}` with the
row's drill body as `start` (§3.2). The row then reads `In your plan · Thu`.

**Up next** (§1.15) leads with the top value row on scored sittings: `Start: Circles · ≈ +30 ·
~12 min`. The coach's pick follows as the second row.

**What-if mode.** A toolbar toggle `What if…` (key `W`, §3.2):
* While it is on, clicking a miss cell marks it with a ghost ✓, and clicking a correct cell marks
  a ghost ✕. After a 150 ms debounce the gauge draws a dashed "What if" band, and a line reads
  `What if: 560–700 (+40) · 3 flipped · Module 2 stays as you sat it`.
* Presets: `Flip my slips · 5` · `Flip easy misses · 3` · `Flip clock losses · 3` · `Drop
  guessed rights · 2` · `Reset`. The spec's what-if sentence stays in the hero facts as the
  `Flip easy misses` fact: `3 easy misses: with them right, 560–700.`
* Esc or `W` leaves the mode, and the band goes.
* **Endpoint** `POST /api/session/{sid}/whatif {right: [qid], wrong: [qid]}` (S6, calling
  `estimate.rescore`) → `{low, high, mid, delta, capped, note: 'Module 2 is not re-routed'}`.
  It writes nothing. 409 for an unfinished sitting, 422 for an unknown qid or more than 44 ids.
  Any viewer who can read the report may call it.

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

#### SR3. Second look: re-answer your misses before the key shows, and learn a slip from a gap

*From: outcomes #1, experience #2, unfair-advantage #3; the Hide answers gaps of all three
(OG5, EG6, AG9). Effort M. Builders: S6 (endpoints, banner, the held-back payload), F3
(`UI.review` mode `second`), F4 (`source:'second'` filing, causes reading `qstate.second`,
prefs key).*

**Why.** Theirs shows the key at once and can't re-answer, so the chance to try again cold is
gone and nobody learns whether a miss was not knowing or rushing. Those need opposite fixes.
Trying again before feedback makes the correction stick, and the result sorts every miss
without asking the student to judge themselves. The spec's "pick reveals locally, files
nothing" throws that evidence away and contradicts R21.

**When it is offered.** A finished sitting of kind mock, module, diagnostic, custom, twin, paper
or shared, or a drill run with `feedback:'end'`, when:
* at least one miss (incorrect or blank) has no `qstate[qid].seen_key`;
* `prefs.second_look` is on (the default);
* `qstate._session.second.state` is unset;
* the viewer is the owner.
It is never offered for challenges, instant or retry drills (their keys were shown), or shared
read-only views.

**Banner `#second`** (above the hero):
* `SECOND LOOK · 13 misses · answers still hidden · about 12 min` (the minutes are the misses'
  budgets, rounded).
* Helper: `Re-work each miss cold, before you see the answer. It tells a slip from a gap, and
  it makes the fix stick.`
* `.btn-primary Start second look` and `.quiet Show answers now`.
* While it is offered, for the misses not yet seen: the player hides the key, reasons,
  explanation, steps and answer boxes; Mistakes rows read `Misconception hidden until your
  second look`; the table's Correct, Mistake and Students-right-by-option cells read `Hidden`.
  Statuses, times, domains, the score, the ledger, the worth and the cause counts still show
  (none of them names the key; see the held-back set below).
* `Show answers now` sets the state `skipped`. The offer lapses after 3 days (state `lapsed`).

**The player in mode `second`** (`UI.review(host, items, {mode:'second'})`, F3):
* It serves the unseen misses in sitting order. The header chip reads `Second look · 3 of 13 ·
  no clock`; a stopwatch counts up quietly for the record.
* All four choices are pickable. The first pick is hidden behind `.quiet Show what I picked`
  (off by default). A grid-in takes a new entry with its preview.
* Tests' Sure · Unsure · Guess chips are optional (`K` cycles, R22).
* Enter (or Check) sends the answer, then reveals everything with one verdict:
  * `Right on a second look: you knew this (a slip)`;
  * `Right, but a guess: counted as a gap`;
  * `The same answer again: a trap you believe · <label>`;
  * `A different wrong answer · <label>`, or `· not a named mistake`.
* `.quiet Skip this one` moves on without filing; it stays unseen. `H` reveals without filing
  ("Just show me") and marks it seen, which takes it out of the second look.
* **End card**: `Right on a second look 5 (slips) · Same trap again 4 · A different wrong answer
  2 · Still blank 2`, then the next rung:
  * `.btn Twins of the 8 still wrong` (T5's sheet, one after another,
    `{from_session, only, each:1, source:'twin', parent}`);
  * `.btn Learn it · 3 gap types` (`source:'learn'`, T4);
  * `.quiet See the full report`.

**Filing and state** (S6, `server/api_results.py`):
* `POST /api/session/{sid}/second {question_id, answer, conf?, ms}`:
  * 409 unless finished; 403 for another learner; 409 `answers already shown` once `seen_key`
    is set; 409 when the state is `skipped` or `lapsed`; 422 for a bad answer.
  * It stores `qstate[qid].second = {answer, correct, conf, ms, at}` and sets `seen_key`.
  * It files through `progress.record(..., source:'second')`. The exact (template, seed) has an
    attempt already, so R8 marks it `repeat = 1`: no mastery, closes nothing, counts as study
    time.
  * A right non-guess answer sets the miss's trap kind to `slip` (R9's kinds); a same-norm
    answer keeps `misconception`.
  * It returns `{correct, answer, reasons, rationale, accepted, cause, verdict}`.
* `POST /api/session/{sid}/seen {qids}` (owner, finished) sets `seen_key`. The player calls it,
  batched, whenever it shows an unseen question with answers visible.
* `POST /api/session/{sid}/second/state {state: 'skipped' | 'done'}`.
* Results gain `second: {state, unseen: [qid], looked, right, same, other, still_blank, with:
  {low, high, mid} | null}`.

**The held-back set.** While the offer stands, no payload, file or print carries anything
derived from an unseen miss's key. One function does it, `api_results.hold_back(sitting,
item)`, and every serializer of a review item calls it: results, compare (SR7), CSV, the print
layouts, the repair pack and worksheet (SR20), the tutor packet, `/api/history` peeks (SR23)
and the briefing (SR17). It applies to every viewer, owner or not, so a shared link can't be
used to peek. For an unseen miss it removes or blanks:
* `answer`, `reasons`, `rationale`, `mistake` (and the Mistakes label), `accepted`;
* P1's `steps`, `diverge`, `wrong_step` and `option_steps` (the last step's value is the key);
* SR10's `diagnosis` ("Right value, too few digits: 2/3 needs .6666" names it);
* SR12's `crowd.option_share` (its null marks the key's position); `crowd.n`, `rate`, `level`
  and your odds stay;
* SR8's `cause.evidence` lines about the key (`you crossed out the answer`). SR8's **entry**
  rule needs the diagnosis, so an unseen grid-in miss is classified without it (it falls
  through to slip, trap or gap) and takes `entry` once its key is seen; the by-cause bar
  therefore never points at a grid-in whose typed value equals the key;
* SR9's `judgement.crossed_key` entries for unseen qids, the names in `sure_wrong` (the count
  stays, `Sure and wrong · 3 · named after your second look`), and the struck marks on the
  key's option in `marks` (the player opens the question with struck options shown only once
  seen);
* SR11's `habits` and `norms` are computed from seen misses only, with a line `3 more misses
  join these after your second look`.
The page never infers them either: Colour by Crowd and the hover card use only the kept
fields.

**Files and prints while it stands.**
* **CSV** writes `Hidden` in the `correct`, `mistake`, `diagnosis` and `accepted` columns of
  unseen misses, with a first comment line `# 13 answers hidden until your second look`.
* **The report print** shows `Hidden` in those cells and a banner line with the same count.
* **Repair pack, tutor packet and the key page** show them, so they ask first: a confirm
  sheet `This prints the answers and ends your second look for 13 questions · Print anyway ·
  Start second look`. Print anyway calls `POST /seen` with those qids, then prints. A
  read-only viewer gets the prints with `Hidden` instead (they can't end the owner's look).
* **The retry sheet** needs no confirm: its fresh seeds and their key leak nothing about the
  originals.
* `with` = `estimate.rescore(right = right non-guess second looks)`. The gauge draws it as a
  hollow band: `With a second look: 580–720 · 60 points were slips, not gaps.`
* Review items gain `second` and `seen`.

**Elsewhere.** SR8's causes read it (a right non-guess second look is a slip; a wrong one is
never a slip). A **Second look** tile: `5 of 13` with the sub-line `slips · 6 gaps · 2 to go`.
A table column Second look (✓ / ✕ / –). SR14's review progress counts looked-at misses.
Settings gains the row "Second look after tests" (`prefs.second_look`, §3.2).

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

#### SR4. A hero that shows movement: previous → now, the extra bands, the total and earned milestones

*From: experience #11 (earned reveal), AG1, AG2, OG2, EG3 (motion), EG1 and AG4 (total).
Effort S. Builders: F1 (`UI.gauge` layers and sweep), F4 (`estimate.total`), S6, S1 (R25 rules),
S4 and S5 (`?fresh=1`).*

**Why.** Theirs counts every number up from 0 on every visit, so the motion means nothing, and
their total card needs both sections. A number that moves from last time to this time is the
news; a total with its provenance is honest and matches what switchers think in.

**Gauge layers** (`UI.gauge`, bottom to top):
1. the scale and ticks;
2. the previous same-kind band, a `--mat` ghost labelled "Section #6";
3. `Today ≈` (SR6), a dotted outline;
4. `With a second look` (SR3), a hollow outline;
5. `What if` (SR2), dashed; it replaces Today while the mode is on;
6. this sitting's band in orange with the graphite midpoint tick;
7. the target tick.
A legend line under the gauge names only the layers present: `orange = this sitting · grey =
Section #6 · hollow = with a second look · dotted = today`.

**The first view after Finish.** The runner's and the session's redirect add `?fresh=1`; the
page removes it with `history.replaceState`.
* Once, in about 1.2 s: the band sweeps from the previous band (from 200 when there is none),
  the centre counts from the previous midpoint, and the delta chip lands (`+90 vs Section #6`).
* Tiles count from the previous same-kind values.
* Then up to 2 **milestone stamps**, each shown only the first time it is true (R25's `earned`),
  each linking to its evidence: `New best band` · `First time on the harder Module 2` · `Target
  reached` · `Every easy question right` · `5 mistakes closed since your last test`.
* Revisits and `prefers-reduced-motion` show the final state at once. Nothing loops.

**The total** (`estimate.total(learner, sid)`, F4, shared with T16's card). It is honest
about being below theirs until an R&W bank exists (decision 3): theirs measures R&W, ours adds
a number the student typed. What it adds is provenance, a national placement and a gap split
by what this report can move.
* When `learners.rw_now` (R15) is set, or an outside score with R&W within 60 days exists
  (S3's `outside_scores`): under the band, `Total ≈ 1,130–1,270 · about the 62nd–83rd
  percentile` (SR5's total table at the total's low and high), with the provenance line `Math
  520–660 measured here · R&W 610, you entered Sep 12 (Bluebook)`.
* The R&W part of a small total bar is hatched.
* Older than 60 days: `R&W is 74 days old · Update`, which opens the field.
* **Gap to a total target**, when `target` and `rw_target` are both set (total target = their
  sum): `Total target 1400 · 130 above your total's high end`, split in two rows:
  * `Math: what this report can move · 4 questions from 700 (SR2's path)` with its chips;
  * `R&W: your entered 610 · target 700 · practise R&W vocabulary in Words` (the only R&W study
    on the site today, decision 2).
* None: an inline `Add your R&W score (200–800)` field with a source select (`Bluebook` ·
  `Official` · `Other`) and Save. Save sends `PUT /api/me {rw_now}` and appends a dated row
  through S3's `add_outside_score({rw, math: null, source})`, so every R&W entry is kept as
  history (R16 counts only rows with `math`, so it doesn't touch the Math estimate).
* **R&W history on `/results/`'s chart** (SR21): the R&W entries as a hatched step line in a
  lane under the Math chart, labelled `R&W (yours)`, each point dated with its source.
* The caption becomes `Math measured here. Reading and Writing is your own score until SAT
  Freshman has R&W questions.`
* Payload: `total: {low, high, pct {low_pct, high_pct, year} | null, parts: [{subject:'math',
  low, high, source:'measured'}, {subject:'rw', value, source:'self' | 'bluebook' | 'official',
  at}], gap {target, math_path: [qid], rw_to_target} | null, rw_history [{day, value,
  source}]}`. A measured R&W section later adds `{subject:'rw', low, high, source:'measured'}`
  and nothing else changes.

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

#### SR5. Percentiles that work on day one: the national range for your band, and the in-site picture

*From: AG3 (national), EG2 (the distribution strip); open question 2. Effort S. Builders:
F4 (`estimate.national`, the data file), S6, F1 (`UI.dotStrip`).*

**Why.** Theirs and the spec compare a sitting only with the site's own first sittings. We have
12 finished mocks, so the spec's percentile reads "needs 20" for months. College Board
publishes user percentiles for Math section scores, so a student can see where their band sits
nationally from the first sitting, clearly labelled as a placement of our estimate.

**Data.** `server/data/cb_percentiles.json` = `{title, source: <the College Board document
URL>, year, tables: {math: {"200": p, …, "800": p}, rw: {…}, total: {"400": p, …, "1600":
p}}}`, transcribed by hand from College Board's published SAT user percentiles (the section
and total tables of the same document). The builder fills the real values and cites the exact
document; nothing is interpolated or estimated. A check asserts 61 keys for `math` and `rw`
(200 to 800 by 10), 121 for `total` (400 to 1600 by 10), non-decreasing values, and a non-empty
`source` and `year`. `rw` is there so a measured R&W section later needs no data change.

**Hero percentile block** (standard sittings, R16):
* `Nationally: your band 520–660 sits at about the {p(520)}th–{p(660)}th percentile of SAT
  takers (College Board, {year})`, with ⓘ: `Our band is an estimate. This places it on College
  Board's published table; it is not a College Board score.`
* The spec's in-site line and pill stay as written.
* When the in-site count is 20 or more, a dot histogram (`UI.dotStrip`, F1): first same-kind
  sittings' midpoints in 20-point bins from 200 to 800, the band shaded, a "you" marker,
  `role=img` with a summary line.
* A non-standard sitting reads `Percentiles compare standard timed sittings only.`

**Elsewhere.** The Results estimate card adds `Nationally about the Nth–Mth percentile`
(SR21). Payload: `rank.national {low_pct, high_pct, source, year}` and `rank.hist [counts] |
null`.

**Acceptance.**
1. `python3 server/checks/f4.py` validates the data file as above (61 / 61 / 121 keys).
2. Results for a standard mock: `rank.national.low_pct <= rank.national.high_pct`, and both
   equal the table's values at the band's low and high.
3. With 19 first sittings, `rank.hist == null` and no histogram renders; with 20 the SVG has
   at least 20 circles.

#### SR6. A living report: Recovered, Slipping, Prove it and the recovery strip

*From: unfair-advantage #2, outcomes #3 (the recovery steps), outcomes #11 (recovered points),
AG5, AG12, AG16, OG13. Effort M. Builders: F4 (`progress.recovery`), S6 (strip, band, tile,
history fields), S5 (the custom test's link-back), S7 (task `start`).*

**Why.** Their report is a photo of one day, and proving a fix needs a new question of the same
type, which a finite bank can't supply without showing a seen key. An old report that shows
what has been won back since is a reason to reopen it, and it turns "Fix all 13 now" into a
plan that is checked a week later.

**The rule** (`progress.recovery(learner, sid)`, F4; one query over the sitting's templates,
sharing the `history` query):
* For each miss, take the learner's clean answers (R8) on the same template after `finished`,
  in any other sitting (twins, practice, Prove it, later tests).
* **Recovered**: the latest clean answer is right, and the trap has closed or there have been 2
  clean rights since. **Slipping**: the latest clean answer is wrong. **Open**: otherwise.
  Second-look answers are repeats (R8) and never count.
* `now = estimate.rescore(sid, right = recovered)`.
  `points_recovered = now.mid − ledger.mid`; `points_open = all_right.mid − now.mid`. Both are
  exact, and they sum to the ledger's total.
* `timeline`: dated events from attempts and traps: `Sep 23 sat · Sep 24 fixed 5 · Sep 26
  proved 4 of 6 · Oct 1 slipped 1`.

**On the report.**
* **Gauge**: the dotted `Today ≈ 570–710` band, captioned `Re-scored with what you've proven
  since on these question types. Not a new test.` A chip: `Recovered 9 of 13 · ≈ +50 · 4 open
  (≈ 60)`. Shown once anything is recovered or slipping.
* **Recovery strip** (under the header; scored sittings; owner). Four steps, each with its state
  and date, each a button to its action:
  1. `Second look` ✓ or `to do` (SR3);
  2. `Fix · 5 of 13 closed` (traps opened by this sitting and closed since);
  3. `Check-ins · 2 due Sep 26` (R9's due dates for this sitting's fixed traps);
  4. `Prove it · Sep 30` (finished + 7 days; ✓ once a Prove-it test from this sitting finished).
* **Prove it · 13**: Tests' custom test `POST /api/mock/new {kind:'custom', custom:{source:
  'misses', from_session: sid, count: 13, order: 'mixed'}}`, under test rules (95 s a question,
  no feedback until hand-in). Its report opens with `Proved 9 of 13 from Section #7 →`, linking
  back, and SR7's compare with `with = from_session`. Step 4 has `.quiet Put in my plan`: an S7
  task on the next study day from finished + 7, `start` = that body.
* **Tiles**: a `Recovered` tile, `9 of 13`, sub-line `≈ +50 since · 4 open`.
* **Grid**: a recovered miss takes the Fixed-since token (§2.3), now driven by proof and not only
  by a trap closing. Slipping keeps the Incorrect token and has its own filter (SR15).
* **Player**: the status chip adds `Recovered Sep 26` or `Slipping`; the trajectory (SR16) ends
  with the same verdict.

**Elsewhere.** `/api/history` items add `recovery {recovered, slipping, open, points_open}`,
drawn as the card's ring (SR23), so Today's test card (T16) can say `60 points still open`.
Results' `Recovered this week` tile sums `points_recovered` over sittings with recovery events
this week (SR22).

**Data.** Results gain `recovery: {subject, recovered: [qid], slipping: [qid], open: [qid], now
{low, high, mid}, points_recovered, points_open, timeline: [{day, kind, n}], steps: [{n, kind,
state, due, sid?}]}`.

**Acceptance.**
1. A mock with a miss on template t; then two clean right answers on t in a later drill:
   `recovery.recovered` contains the qid, `recovery.now.mid > ledger.mid`, and
   `points_recovered + points_open` equals `ledger.total` within 1.
2. Then a clean wrong answer on t: the qid moves to `slipping`.
3. A right second look (a repeat) on t leaves the qid in `open`.
4. Prove it posts `{kind:'custom', custom:{source:'misses', from_session}}`; the new sitting's
   templates equal the misses' templates, every seed differs, and its report contains
   "Proved".

#### SR7. Then vs now: a twin, a rematch or any two sittings, compared slot by slot

*From: outcomes #8, experience #6, unfair-advantage #8, T16's compare endpoint, P18. Effort M.
Builders: S6 (`GET /api/session/{sid}/compare`, `#compare`, `?vs=`), F3 (`UI.review` mode
`pair`), F1 (`UI.bandChart` `pairs`), S5 (the twin's slot map).*

**Why.** A new random section mixes the student's change with how hard that form happened to
be. A slot-matched pair isolates it: "9 of your 13 miss types are now right" is the strongest
reason to keep practising, and "Slipped" catches forgetting early. Theirs retakes a fixed paper
whose keys the student has seen, and compares nothing.

**One parallel form.** Tests' `POST /api/mock/new {kind:'twin', twin_of}` is the only one; the
spec's `{like}` is deleted (§3). S5 stores `cfg.slot_of {new_qid: src_qid}` for module 1, and
for module 2 when the route matches (otherwise module 2 is fresh). P18's rematch stores the same
`cfg.slot_of`. Prove it (SR6) pairs by template.

**Endpoint** `GET /api/session/{sid}/compare?with={other}` (S6):
* Both sittings must be the viewer's own, finished: 403 otherwise, 409 unfinished.
* `with` defaults to `cfg.twin_of`, `cfg.rematch_of` or `cfg.custom.from_session`; with none
  and no `with`, 404.
* Pairing: `cfg.slot_of` when present, else by template in order (the first unused match).
* Returns `{subject, with {id, seq, label, finished, estimate}, paired, unpaired, slots [{n,
  module, template, type_name, tier, then {qid, status, ms, mistake}, now {qid, status, ms,
  mistake}, change}], counts {fixed, slipped, still_missing, same_trap, held}, band {then, now,
  delta}, ms_per_q {then, now}, explained {fixed_pts, slipped_pts}, skills [{topic, then {right,
  asked}, now {right, asked}}], module2: 'paired' | 'different_route' | 'none'}`.
* `change` is `fixed` (✕→✓), `slipped` (✓→✕), `still_missing` (✕→✕), `same_trap` (✕→✕ with
  the same norm; it also counts in still_missing) or `held` (✓→✓).
* `explained.fixed_pts` sums the then-sitting's `per_q` over fixed slots; `slipped_pts` sums the
  now-sitting's over slipped slots. Both print with "≈".
* P18's drill `finish().slots` is built by the same function, so the practice summary and the
  report agree.

**Region `#compare`** (after the ledger, when the sitting has a pairing or `?vs=` is set):
* Heading `COMPARED WITH SECTION #7 · SAME 44 QUESTION TYPES` (the number is `paired`, never a
  constant), or `19 question types appear in both`.
* Verdict: `520–660 → 590–730 (+70) · 9 of your 13 misses are now right · 2 slipped · 14 s
  faster a question`, then `+70: 9 fixed (≈ +95), 2 slipped (≈ −35)`.
* Per (subject, module), two strips as long as that module, then above and now below,
  slot-aligned, each cell in the R20 token with its glyph.
* Both sides go through SR3's `hold_back`: an unseen miss on the then-sitting shows its status
  and `Hidden` for its mistake.
* Chips, each a filter: `Fixed 9 · Slipped 2 · Still missing 4 (same trap again 2) · Held 29`.
  In the table view slipped rows come first.
* `Module 2: a different route (you routed up this time)` headlines when that happens.
* A skills table, then → now, with ▲ ▼.
* Clicking a pair opens `UI.review` in mode `pair` (F3): both question bodies side by side at
  ≥1100 px, stacked below, both read-only, each labelled with your answer then and now.

**Any two sittings.**
* The ⋯ menu gains `Compare with…`: a sheet listing same-kind sittings (`/api/history?kind=…
  &limit=20`), which loads `?vs=<id>`.
* On `/results/` the chart joins twin pairs with a bracket (`UI.bandChart(…, {pairs})`), and
  clicking two points opens the newer report with `?vs=` (SR21). Sitting cards can be selected
  with `X` for a Compare bar (SR23).

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

### B. Why each miss happened

#### SR8. A cause on every miss, one tap to correct, trended over time

*From: experience #4, the cause rules of outcomes #2 and unfair-advantage #1, OG12, AG7; P8's
chips; T7's rule. Effort S. Builders: F4 (`progress.causes` per question, second-look and
`miss_kind` inputs), S6 (chips, filter, CSV), F3 (P8's chips in the player).*

**Why.** "Study more" is the wrong fix for most misses: a slip needs checking, a clock loss
needs pace, a trap needs unlearning, an entry error needs one rule. Tutors make students keep
this error log by hand. Ours fills itself from the trail, the clock, the options and the second
look, and correcting it costs one tap. Theirs has no time, skill or difficulty to infer from.

**One vocabulary**: T7's five causes, now for one sitting. `progress.causes(learner, tz,
session=sid)` adds `per_q: {qid: {cause, auto, evidence}}`. First match wins:
1. **clock**: a blank in a timed sitting whose module clock ran out, or an answer in the
   module's last 90 s after under 25 s on it (`qstate` ms and `made_left`, R7).
2. **entry**: a grid-in whose SR10 diagnosis is `form` or `short`, once its key is seen (while
   SR3's offer stands the diagnosis is held back, so the rule is skipped for that miss).
3. **slip**: right on the second look and not a guess (SR3). Before a second look, T7's
   inference: 4 of the last 5 first tries on the template right, or easy and under half the
   student's median easy time.
4. **trap**: the pick, or the second-look pick, names a misconception.
5. **gap**: everything else.
A wrong second look is never a slip. `evidence` holds the facts behind the pick, shown in the
chip's popover: `0:18 on it · 4 of your last 5 on this type right · you crossed out the answer`
(from `qstate.struck`). The struck-key line is held back until the key is seen (SR3).

**Correcting it.** The player header shows `Cause: Slip (auto) ▾`. It opens P8's six chips
(Fell for it · Misread the question · Slip in the arithmetic · Didn't know how to start ·
Rushed · Ran long, then guessed). A tap sends `POST /api/session/{sid}/why {question_id, kind}`
(S6; P8's drill route calls the same handler), which writes `attempts.miss_kind`. A
student-set kind wins over the rule and maps onto the five causes: fell for it → trap; misread,
slip, rushed → slip; didn't know → gap; ran long → clock (§3.2 amends T7). "auto" drops.

**Where it shows.**
* SR1's By-cause bar.
* **Colour by Cause** (SR15): five steps of warm grey with a corner letter C / E / S / T / G,
  never colour alone.
* A `Cause ▾` select in the review's Act-on row, with counts.
* A cause chip on each Mistakes row; a Cause table column; `cause` and `cause_auto` CSV
  columns.
* The Fix menu's per-cause items (SR2).
* Results' **Why you miss, over time** (SR22).

**Acceptance.**
1. A timed mock finished with 3 blanks at time-up: those qids have `per_q[q].cause == 'clock'`.
2. `POST why {question_id: q, kind: 'misread'}` → `per_q[q] == {cause: 'slip', auto: false}`,
   and `attempts.miss_kind == 'misread'` for that row.
3. The `per_q` count equals `summary.incorrect + summary.unanswered`, and the counts per cause
   equal `ledger.by_cause[].n`.

#### SR9. Judgement: confidence, flags, answer changes, eliminations, time away and notes

*From: outcomes #6, experience #7, unfair-advantage #6, OG15; Tests §3.4.7 ("render
notes, highlights, confidence calibration, away time and answer changes"), which §3.5 never
designed. Effort S. Builders: S6 (the region), F4 (`progress.calibration`, shared with Review's
flag calibration and P7), F3 (`UI.annotate` read-only), S5 (`away_log`).*

**Why.** A miss the student was sure of is a belief, and it costs points on test day because
nobody re-checks what feels certain; corrected high-confidence errors are the ones retained
best. A lucky guess is a point not owned yet. Whether flagging and changing answers pays is a
test-day skill. Tests collects all of this and the spec's report drops it. Theirs counts flags
and nothing more.

**Region `#judgement`** (tests, and drills with confidence tags; the spec's 1.10 moves in here):
1. **Confidence**, when 5 or more answers are tagged (`qstate.conf` in tests, `attempts.conf`
   in drills):
   * a 3 × 2 grid, Sure / Unsure / Guess × Right / Wrong, with counts; every cell is a filter;
   * `Sure and wrong · 3: misconceptions you believe`, each named, with `.btn Fix these 3`;
   * `Guessed right · 2: points you don't own yet · without them 500–640` (`estimate.rescore(
     wrong = those)`), with `.btn Add them to Fix`;
   * P7's reading lines (`Your Sure is reliable…`, `Your Sure was right 70%…`);
   * tags off: `Turn on confidence tags for your next test · one tap a question, and it shows
     which mistakes you were sure of`, a toggle that writes `prefs.confidence = 'ask'`.
2. **Flags**, from Review's calibration function for this sitting: `Flagged 5 · went back to 4
   · changed 2, both wrong → right · 1 flagged and left wrong`. One advice line by rule:
   * flags that paid off: `Keep flagging and coming back.`;
   * 2 or more flags never revisited (SR13's visits): `Leave 3 minutes at the end for your
     flags.`
3. **Answer changes** (the spec's 1.10 text), plus the all-time first-instinct line from every
   test trail: `When you change an answer you end up right 62% of the time (21 changes).`
4. **Eliminations and time away**:
   * `You crossed out the right answer 2× (M1 Q9, M2 Q3)`, as chips that open the player,
     where struck options render struck as they were in the test. Only seen questions count
     here and render struck marks on the key (SR3's held-back set);
   * `Left the test window 3× · 1:40 in all`, with the question each time, from
     `qstate._session.away_log [[qid, ms]]` (S5, capped at 50);
   * `Paused 2×` (`sessions.pauses`).
* **Notes and highlights**: the player renders the sitting's marks read-only (`UI.annotate`,
  R6), with a notes rail; the Act-on row gains `Has note`.
* **Mistakes** gains a first group `Sure and wrong · 3`, above Open. When no tags exist it uses
  T9's inferred blind spots (fast and not a guess), with the same label.

**Data.** Results gain `judgement: {conf {sure {right, wrong}, unsure {…}, guess {…}, untagged},
sure_wrong: [qid], guessed_right: [qid], without_guesses {low, high} | null, flags {flagged,
revisited, changed_right, left_wrong}, changes {…, instinct {changes, right}}, crossed_key:
[qid], away {n, ms, log}, pauses}`.

**Acceptance.**
1. A test with `conf:'sure'` on a wrong answer: `judgement.conf.sure.wrong == 1`, and the
   report's first Mistakes group is "Sure and wrong · 1".
2. `judgement.without_guesses.high <= estimate.high`.
3. `qstate.struck` containing the key's index on 2 questions → `crossed_key|length == 2`.
4. Tags off: clicking the toggle makes `GET /api/prefs` return `confidence: 'ask'`.

#### SR10. Grid-in misses named and diagnosed

*From: OG6, the grid-in half of EG7, experience #4 rule 6; P4. Effort S. Builders: F4
(`scoring.grid_diagnose` with asserts), S6.*

**Why.** Their boxes show two numbers and say nothing about why the typed value failed. Many
grid-in misses are entry errors (too few digits, a mixed number) or one step off (sign, ×100),
and each has a one-line fix.

**`scoring.grid_diagnose(given, key) -> {kind, text} | None`**, first match:
* `form`: the value equals the key in a form the grid refuses (a mixed number, over 5
  characters positive or 6 negative): `Right value, in a form the grid refuses: enter 3/2 or
  1.5.`
* `short`: within 1% of the key, a decimal that fits but has too few digits: `Right value, too
  few digits: 2/3 needs .6666 or .6667.` (from `accepted_forms`)
* `sign`: equals −key: `Right size, wrong sign.`
* `percent`: equals key × 100 or key ÷ 100: `Off by a factor of 100: percent and decimal mixed
  up.`
* `ten`: equals key × 10 or key ÷ 10: `Off by a factor of 10: check the place value.`
* `named`: equals a `spr_reasons` value (P4's borrowed names or the template's own): that
  misconception.
* otherwise `None`: `A different value, not a named mistake.`

**Where it shows** (once the key is seen, SR3). Under the player's "Your answer" box on a
grid-in miss; on the Mistakes row in place of "Missed grid-in"; as SR8's entry cause for `form` and `short`. The entry fix is
T7's `Grid-in entry drill · 5` with the grid-in rules popover. U3's `forms` outcome and T7's
entry rule call the same function (§3.2).

**Acceptance.** Asserts in `server/checks/f4.py`: `('0.66', '2/3') → short`; `('1 1/2', '3/2')
→ form`; `('-7', '7') → sign`; `('45', '0.45') → percent`; `('12', '8') → None`. The results
review for a grid-in miss typed "0.66" to "2/3" carries `diagnosis.kind == 'short'`.

#### SR11. Habits and trap patterns across skills

*From: unfair-advantage #5, outcomes #9, EG7's "same mistake in other question types", AG10's
"your 3rd time"; U6's families. Effort S. Builders: S6, F5 (`habits.py`, pool `related`), S10
(Spot).*

**Why.** Their Distractor Analysis is prose on one item, with no idea which errors recur. One
habit, "stopped a step early", costs points in every domain; fixing it once pays everywhere,
and repairing template by template can't reach that. U6 already tags every reason into 11
families, so the report only has to show it.

**Region `#habits`** (above Mistakes), when 2 or more misses here share a U6 family across 2 or
more templates, or one norm has 2 or more hits here or 3 or more all time:
* **Family rows**: `Stopped a step early or went a step too far · 3 of your 11 named mistakes ·
  in Linear functions, Systems, Circles`; the tell in italics (`Reread the last line: is this
  the final quantity?`); the question chips; `in 4 of your last 5 tests` when it recurs; `.btn
  Drill this habit · 8` (U6's `{source:'habit', habit, count:8}`).
* **Norm rows** (the same misconception across types): `Changed the sign of the slope ×3 · 3
  question types`; `also appears in 4 types you haven't met` (U6's norm index); `.btn Trap
  drill · 10` (`{pool:'related', ids:[norm], count:10}`).
* **In the player**, under the picked wrong option: `your 3rd time · also in Systems`
  (`hits` over traps with the same norm) and `.quiet Spot this trap` (Review's `POST
  /api/review/spot {trap_id}`).
* Mistakes rows carry a habit chip.
* **Results `#traps`** (spec 2.8) groups by norm across templates ("in 3 question types") and
  gains T9's `.seg By question type · By habit`.

**Data.** Results gain `habits: [{id, name, tell, qids, topics, recur}]` and `norms: [{norm,
label, qids, templates, hits_all_time, unmet_types}]`.

**Acceptance.** A sitting with 2 misses whose reasons tag `whole_part` in 2 topics:
`habits[0].id == 'whole_part'` with 2 topics, and its button posts `{source:'habit', habit:
'whole_part', count:8}`. A norm with 3 hits all time shows a row whose Trap drill posts
`pool:'related'`.

#### SR12. Every question in context: your odds and level from day one, how students do, how they picked, and should-have-had misses

*From: experience #5, unfair-advantage #9, OG8, EG8, AG11, AG10's option share, AG19's
challenge fix; P11's ratings. Effort S. Builders: F5 (`drill.levels()` adds `median_ms_right`;
the reverse lookup in `types.py`), F4 (P11's `ratings.level` and `ratings.odds`, the odds
snapshot at finish), S8 (the daily review per slot), S6.*

**Why.** Their Question Score 1–7 is a builder filter, and their per-question payload has no
difficulty, skill or time, let alone a crowd rate. Whether a miss is a slip on a type the
student usually gets, or a type that beats everyone, changes what to do next. The spec shows a
crowd only on the challenge, and groups it by (template, seed), which decision 1's twin
challenges break: no two students share a seed, so option letters never line up. And no
(template, tier) has 20 first tries yet, so a crowd-only design ships empty. P11's ratings
exist from the first answer, so every line here works on day one and turns measured as data
arrives.

**Data.** Each review item gains `odds` and `crowd`:
* `odds: {you, at: 'sitting' | 'now', avg, skill_rating, item_rating}`:
  * `you` = P11's `E = 1 / (1 + 10^((Ri − Rs) / 400))` for this learner's
    `skill_ratings[topic]` against `item_ratings[(template, tier)]`. At finish, F4 reads
    `ratings.odds(learner, template, tier)` for every item **before** the sitting's answers
    update the ratings, and stores them in `sessions.result.odds {qid: E}` (the result JSON, no
    new column), so the odds are the ones the student sat with (`at: 'sitting'`). A sitting
    finished before this ships has none: it uses the current ratings and reads "your odds now"
    (`at: 'now'`).
  * `avg` = E for a 1000-rated learner against the same item rating: the estimated share of
    students who get it right, always labelled "estimated".
* `crowd: {n, rate, median_ms_right, option_share: [share | null × 4], level, rough,
  level_n}`, measured:
  * from `drill.levels()[(template, tier)]` (first clean tries, guesses out; §3.3.5) with P16's
    `median_ms_right`, and P11's `ratings.level(template, tier)`;
  * below n = 20 only `{n, level, rough: true}` is sent; every line below then uses `odds.avg`
    with "estimated", and switches to `rate` at n ≥ 20;
  * `option_share[i]` = the share of first-try misses on this (template, tier) whose reason
    norm equals option i's norm, sent once there are 20 such misses (pooled over the template's
    tiers when one tier has fewer); below that it is absent and the popover reads `How students
    pick: after 20 misses on this type · 7 so far`. It is held back on unseen misses (SR3).

**Where it shows.**
* **Player header**: `L4 · your odds were 82% · rough (6)`, then the students line: measured
  `74% of 212 students get this type right · they take 1:05 · you 1:42`, or `About 64% of
  students get this type right (estimated) · you 1:42`.
* **Under a wrong option**: `31% of students who miss it pick this one`, when shares exist.
* **Details popover** adds:
  * `Level 4 of 7 · measured from 212 answers`, or `rough · 6 answers`;
  * `Your odds were 82%: your Linear functions rating 1180 against this type's 1020`;
  * the students line;
  * `You on this type: 1 of 4 right`;
  * `Worth here ≈ +12` (SR1);
  * `Modelled on College Board question 06469-DC`, when U2's `types.py` map has one for the
    template;
  * `Copy link to a fresh one` (U28's twin link) and `Copy link to exactly this question` (R19's
    permalink, for tutors).
* **Review** (SR15), all working on day one:
  * `Should-have-had · 4`: a miss where your odds were 75% or more;
  * `Hard for you · 3`: a miss where your odds were 35% or less;
  * `Hard for everyone · 2`: the students' rate (measured, else estimated) is 35% or less;
  * Colour by Level (§2.3's tints with the level number) and by Crowd (the students' rate; an
    estimated one carries a small `est.` corner, never colour alone);
  * Level, Odds and Students right table columns (`64% est.` until measured);
  * the Mistakes sort `Surprise first` (highest odds first).
* **Hero fact**, when 2 or more: `4 misses were on types you had 75%+ odds on: the cheapest
  points here.` It also feeds a takeaway (SR14).
* **Difficulty and format rows** add `students who got them right 0:45` once measured.
* **Challenge**: the crowd per slot comes from S8's `/api/contest/daily/review` function (the
  slots share a template, decision 1): `41% of 140 got slot 7 right · most picked: forgot to
  halve (31%)`. Option shares are by norm, never by letter.

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

### C. Time

#### SR13. Clock replay and time budgets: where each module's 35 minutes went, and the set that fixes it

*From: outcomes #7, experience #8, unfair-advantage #7, EG14, AG17, OG10; P16's budgets, U7's
quadrant. Effort M. Builders: S5 (the visit log), F1 (`UI.clockLane`), S6 (`#pace`), F5
(`budget_ms`).*

**Why.** Their report has no time per question at all; their only time view is an empty
contest chart. The spec's bars show how long each question took, but not the order, the
revisits, or the moment the student fell behind, and it judges every question against a flat
95 s. Easy and medium blanks at the end of a module are the most avoidable loss on the digital
SAT, and pacing can be trained once it can be seen.

**Data.** The S5 runner logs `qstate._session.visits [[qid, t_in, t_out]]` in module-elapsed ms
(pauses excluded), capped at 400, through the existing `/state` queue (R7). Older sittings have
none: the lane is left out with `Visit order was not recorded for this sitting.` and the bars
still come from `ms`.

**Region `#pace`** (replaces the spec's 1.9):
1. **Clock replay**, one per module (`UI.clockLane`, F1):
   * a horizontal lane 0:00 → 35:00 (or the sitting's clock): blocks in visit order, width =
     time, fill = the final status token; revisits in a second lane;
   * markers for a flag set, an answer change (↺) and the clock's end;
   * a dashed even-pace line (where each question's budget would have put you), with the lane
     shaded ahead or behind;
   * hover or tap: `M2 Q14 · 3:10 · 2nd visit · changed C → B`; a click opens the player;
   * on the phone the lane runs vertically.
   * **Auto lines**: `4:30 behind pace by Q15, with 2:10 left for the last 7` · `Skip and return
     worked 3 times` · `2 blanks were never opened` · the starved case: `M2 Q19 took 4:12 and was
     wrong; Q20–22 got 0:40 between them`.
2. **Each question against its budget**: the spec's bars keep their status fill, and each gains
   a tick at P16's `budget_ms` (the crowd median when n ≥ 20, else the tier default). The flat
   `Test pace 1:35` line stays as a reference.
3. **Chips**, each a filter: `Banked · 18` (right, within budget) · `Time sink · 3` (right, over
   1.5× budget) · `Rushed · 3` (wrong, under 0.5× budget) · `Stuck · 2` (wrong, over 1.5×
   budget).
4. **Facts**:
   * `Time sinks cost 6:20. At budget you would have had time to open your 2 blanks.`
   * `Those 2 blanks are worth ≈ +25 if right.` (the ledger)
   * `A guess on a multiple-choice blank is right 1 time in 4: ≈ +6 expected here. Never leave
     one blank.` (0.25 × the blanks' worth; for a grid-in blank: `Enter your best estimate: a
     blank grid-in scores nothing.`)
5. **Actions**: `.btn Speed set · 8` (P16's Beat the clock on the time-sink types, `per_q:0.9`),
   `.btn Careful set · 3` (P16's Slow down on the rushed types), `.btn Learn it · 2` (the stuck
   types, `source:'learn'`).
* **Difficulty and format** (the spec's 1.8) rows add the budget and the crowd: `Easy 6/6 · avg
  0:58 · budget 1:05 · students 0:45`.
* **Results**: the Pace region is U7's card (`UI.quadrant` over `progress.pace`), placed after
  `#split`.

**Data.** Results gain `pace: {visits_recorded, modules [{n, visits, behind_at, behind_ms,
left_for_rest_ms, never_opened: [qid], returns_worked, starved: [{qid, ms, after: [qid]}]}],
budget_ms {qid: ms}, chips {banked, time_sink, rushed, stuck}, sink_ms, blank_ev}`.

**Acceptance.**
1. A mock whose runner posted visits: `pace.visits_recorded == true` and each module's `visits`
   is non-empty.
2. `behind_at` is the first question where elapsed time exceeds the summed budgets by more than
   60 s (an assert in `server/checks/s6.py`).
3. On a fresh db a medium question's `budget_ms == 95000`.
4. An older sitting without visits renders "Visit order was not recorded for this sitting." and
   its bars.

### D. Reading and acting on the page

#### SR14. Debrief first: takeaways, the new order, a jump bar and review progress

*From: experience #3, the useful half of outcomes #4. Effort M. Builders: S6 (`debrief`
rules, order, jump bar), F2 (page scope `report` in `UI.keys`), F1 (sticky bar).*

**Why.** Theirs runs rings → tiles → domains → grid, and the only way into a question is to
scroll to the grid. The spec puts Mistakes tenth of twelve regions, thousands of pixels down
at 390 px. The minutes after a test are when a student still remembers their reasoning; the
page should say what happened and what to do before the analysis.

**Order**: as in the layout above (header, recovery strip, second-look banner, hero, ledger,
compare, takeaways, tiles, habits, mistakes with best value, review, modules, domains, skills,
judgement, split, pace, up next). Nothing is removed.

**Takeaways `#takeaways`**: three cards from `results.debrief[]`, rule-based, ranked by points
at stake (by counts for unscored sittings). Rules, each with one primary and a `.quiet Put in
my plan`:
* biggest leak: `Linear inequalities · 3 misses · ≈ 40 pts · the same trap twice` → `Fix 3`;
* pace: `3 rushed misses in Module 2's last 6 minutes · ≈ 20 pts` → `Careful set`;
* route: `1 more right in Module 1 would have routed you up` → `Review M1 Q3`;
* changes (2 or more right → wrong): `Second-guessing cost 2 questions` → `See them`;
* sure and wrong (2 or more), should-have-had (2 or more), slips on the second look (3 or more:
  `5 slips: you knew these` → `Slips, timed`);
* a win, always included when one exists: `Geometry 7/7, up from 4/7 on Section #6`.

**Jump bar**: sticky under the page bar once the hero scrolls away: `Score · Points · Mistakes
13 · Questions 44 · Skills · Judgement · Time`, with scroll-spy. On the phone it is one `Jump to
▾` select beside the sticky primary. The page also registers its sections with
`UI.shell({sections})` for U26's nav sub-links.

**Keys** (page scope `report`, §3.2), ignored while the player is open or while typing:
* `1`–`9`: jump to that item of the jump bar;
* `N`: open the player at the first miss (the player's own `N` is "next miss");
* `F`: open the Fix menu;
* `W`: What-if mode (SR2);
* `?`: the shortcuts sheet.

**Review progress**: `Reviewed 7 of 13` in the Mistakes heading counts misses opened with answers
visible or second-looked (`seen_key` or `second`). `/api/history` items add `reviewed {n, of}`
for the card (SR23). U1's queue gains a row `Finish reviewing Section #7 · 6 left` for a test
finished within 7 days with misses not reviewed (§3.2).

**Acceptance.**
1. The report's regions appear in the DOM in the order above.
2. `results.debrief` has at most 3 items, each with `action`; each card renders one button.
3. Pressing `3` scrolls `#mistakes` into view; `N` opens the player at the first miss.
4. After opening 2 misses in the player, the heading reads "Reviewed 2 of".

#### SR15. A question review that acts: action filters, more views, selection and new columns

*From: EG5, AG7, AG8, experience #5's columns, unfair-advantage #1's Worth column, OG12.
Effort M. Builders: S6, F1 (the filter bar and a selection bar).*

**Why.** Their filters and the spec's slice by property (module, domain, difficulty). A student
deciding what to do needs to slice by action, and to act on a group of questions without
opening each one.

**Toolbar additions** (the spec's toolbar stays):
* **Show** gains the states a sitting can have (SR25): `Mixed` (practice sets in retry mode),
  `Skipped` and `Voided` (contests), and `Removed from scoring` (a key correction, SR19), each
  with its count and shown only for kinds that can have it.
* **Act-on row** under Show, each chip with a count, 0 disabled: `Cause ▾` · `Should-have-had` ·
  `Hard for you` · `Hard for everyone` · `Sure and wrong` · `Guessed right` · `Recovered` ·
  `Slipping` · `Not looked at` · `Has note`. It wraps on the phone and moves into the
  `Filters · n` sheet with the selects.
* **Colour by**: Status | Difficulty | Time | Cause | Points | Level | Crowd. The legend follows.
  Points uses four warm steps with the worth printed under the number.
* **Table columns** (18): # · Skill · Difficulty · Level · Format · Time (and its budget) · Your
  answer · Correct · Result · Cause · Worth · Odds · Second look · Students right · Changed ·
  Flag · Note · Mistake. Sortable additionally by Worth, Cause, Level, Odds and Students right.
* **Table layout** (it must work inside the 1120 px content width and at 390):
  * The table sits in its own scroll box (`.table-wrap`, `overflow-x: auto`,
    `overscroll-behavior-x: contain`); the page never scrolls sideways. `#` and `Skill` are
    `position: sticky; left: 0` (Skill offset by #'s width) on an opaque `--paper` background.
    An inset edge shadow shows on the right while more columns are off-screen and on the left
    once scrolled (two `scroll`-driven classes, no library).
  * Widths (`table-layout: fixed`, `<colgroup>`): # 64 · Skill 180 · Difficulty 72 · Format 56
    · Time 88 · Your answer 112 · Correct 112 · Result 72 · Cause 80 · Worth 64 · Odds 56 ·
    Students right 72 · Mistake 240. Level, Second look, Changed, Flag and Note are 36 px glyph
    columns whose headers are the glyph with a tooltip and an `aria-label` (`Level`, `Second
    look`, `Answer changed`, `Flagged`, `Has note`). Total ≈ 1,450 px, so at 1280 (1,120 px of
    content) about three quarters shows and the rest scrolls.
  * Answers (inequalities, expressions, sentences) sit on one line with an ellipsis
    (`max-width` of the column, KaTeX inline); the full text is in the row's hover card, its
    `title`, and the player. The Mistake cell wraps to 2 lines, then ellipsis, with the full
    label in the hover card.
  * Keyboard: the wrap is focusable (`tabindex=0`, `role=region`, `aria-label="Question table,
    scrolls sideways"`), ← → scroll it by one column when it has focus, and every header is a
    `<button>` (sorting, or for an unsortable column showing its tooltip on focus); focusing
    a header scrolls it into view (`scrollIntoView({inline: 'nearest'})`), so every column is
    reachable without a mouse.
  * Phone (390): the same wrap, with # and Skill (Skill at 120 px) sticky.
  * **Print** (`@page { size: landscape }`): two tables, both with # repeated. The first: # ·
    Skill · Your answer · Correct · Result · Cause · Worth · Mistake, with answers and mistakes
    printed in full (wrapping). The second: # · Difficulty · Level · Format · Time · Budget ·
    Odds · Second look · Students right · Changed · Flag · Note. Headers repeat on each page
    (`thead { display: table-header-group }`); SR3's `Hidden` applies.
* **Hover card** (hover devices): `M2 Q4 · Incorrect · Slip · ≈ +10 · your odds 82% · 74% of
  students right · 1:42 (budget 1:35)` and the full answers and mistake, with `.btn Try one like
  this`.
* The state stays in the query string (`cause=slip&act=should`).

**Selection.** Shift-click selects a range and Ctrl or Cmd-click toggles one; Space toggles the
focused cell; a long-press on the phone enters select mode, then taps toggle; Esc clears. A
sticky selection bar (one primary) reads `4 selected · Fix these 4 · Twins of these 4 · Print a
retry sheet · Save 4 · What if these were right (+40)`. The last one calls SR2's whatif; Twins
runs T5's sheet one after another; Print calls SR20.

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

#### SR16. The player: steps with your step, see one solved first, the type's trajectory, swipe and zero wait

*From: EG7 and P1 (the steps), outcomes #5 and T4 (a solved example first), AG12, EG15,
EG16, OG7. Effort M here; the steps content is P1's Effort L, now due for every section
template. Builders: F3 (`UI.review`), S6, S4 and S5 (the prefetch), F5 (the example endpoint's
reasons), T-bank (steps for every section template, `METHOD` for the rest, the coverage gate).*

**Why.** Theirs is one long explanation of the same item and can't produce another like it. The
spec's twin asks the student to succeed cold on the thing they just showed they don't
understand. The player is where most review time goes, so it has to teach and it has to be
fast.

* **The explanation card** is P1's: the type's about line, then the Steps tab, with the step
  where the student's answer left the path outlined (`Right: 54 ÷ 3 = 18 | Your B: 3 ÷ 54 =
  1/18`), then P1's option lines and the rationale (Short).
  * **Steps are a launch requirement for sections.** Every template that `blueprint` can draw
    into a section or the diagnostic has P1 steps before the v2 report ships, not only P1's
    first 50%-of-weight milestone (§3.2 amends P1). `tools/steps_coverage.py --section` lists
    the templates `blueprint.draw_matching` can return for any (domain, tier, format) slot and
    exits non-zero unless all of them have steps.
  * **A template without steps** (practice-only templates, or one added before its steps are
    written) never shows the bare rationale. Its card opens with a **Method** block written for
    that template: at least 3 sentences, (1) the idea of the type (its about line), (2) the
    method in order, (3) the check that catches its most common trap (`Check: put your x back
    into the second equation, not the first; the first always works`). It sits above the
    rationale and P1's option lines. T-bank stores it as the template's `METHOD` string, and
    `satbank/audit.py` fails a template that has neither `steps` nor a `METHOD` of 3+
    sentences and 40+ words.
* **See one solved first.** On a trap or gap miss (or a relapsed trap), the actions row's
  primary becomes a split, `Try one like this ▾`, whose menu holds:
  * `See one solved first`: T4's worked example (a reserved seed from `GET
    /api/types/{t}/example`, never filed), with the key marked and **the option your mistake
    produces on these numbers tagged** (`Your mistake gives 184 here`), matched by the norm of
    the student's pick; its only button is `Your turn`, which starts the twin;
  * `Learn it · example + 3` (`source:'learn'`, T4);
  * P17's axes that the template supports: Easier · Harder · As a grid-in · Same setup, a
    different question.
  A slip or clock miss keeps the plain twin as the primary.
* **The type's trajectory.** "Earlier on this question type" becomes `UI.history` (R23) as a
  strip: one result glyph per attempt, oldest to newest, over every sitting (including twins,
  Prove it and practice after this sitting), with the time under each. The line reads `1:40 →
  0:52 · 3 right in a row since` and ends with SR6's verdict, `Recovered Sep 26`.
* **The header** adds SR8's cause chip, SR1's worth and SR12's crowd line.
* **Tries in this set** (practice sets, SR25): above the type's trajectory, one line per try
  from S4's `tries`: `Tries in this set: ✕ A · used the slope as the intercept · 0:22 → ✓ C ·
  0:41`.
* **Your rule** (SR17) sits under the explanation.
* **Swipe** (touch): left and right move within the filter. There is a 24 px edge-safe zone,
  and a swipe that starts inside a scrollable table or figure is ignored. Swiping down on the
  header closes the player. On the phone `Next miss` and `Try one like this` sit in the bottom
  bar's thumb zone. A light snap, none under reduced motion.
* **Zero wait.** The player renders the next item in the filter ahead of time (KaTeX and
  figures), so ← → never waits. The runner (S5) and the practice session (S4) prefetch
  `/results` into `sessionStorage['satf.results.<sid>']` while "Finishing…" shows; the report
  paints from it at once, then revalidates (U23's pattern), and drops the copy.

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

#### SR17. Your rules, and a briefing before the next test

*From: outcomes #10. Effort S. Builders: S6 (the prompt, `GET /api/session/{sid}/briefing`), F4
(R6 notes, P20's type notes), S5 (the lobby hook).*

**Why.** Writing "when X, I do Y" after a miss is one of the most effective study habits, and a
lesson brought back just before a test is used when it matters. Theirs carries nothing from one
sitting to the next.

**In the player**, under the explanation of a miss (owner): `Next time I will…` with three
suggested rules and a free-text field (up to 140 characters).
* The suggestions are the miss's U6 family tell, then generic ones: `Reread what the question
  asks before choosing` · `Write the sign on its own line` · `Estimate first: does the answer
  fit?`
* A rule is saved as the template's type note (`POST /api/notes {session, question_id, note,
  type: true}` → `notes.seed = −1`, P20), so it shows wherever that type comes back. Edit and
  Delete sit beside it.

**The briefing.** `GET /api/session/{sid}/briefing` (S6), for the learner's last scored sitting,
returns:
* up to 5 rules written from it, newest first;
* 2 pace facts from SR13, e.g. `You fell behind at Q12. Aim to reach Q11 by 17:00` (the budget
  checkpoint);
* 1 answer-change fact from SR9, e.g. `Changes cost you 1 question last time: change only with
  a reason`;
* 1 route fact per subject sat, from `route_rule`: `Module 1 decides the route: 14 of 22 sends
  you to the harder Module 2.`

The Tests lobby (S5) shows it before Begin as `Your briefing from Section #7`. The tutor packet
(SR20) prints it.

**Acceptance.**
1. Saving a rule creates a `notes` row with `seed = −1` for the question's template.
2. The briefing returns at most 5 rules and 2 pace facts.
3. For that learner, `/test/?s=<new sitting>`'s lobby contains "Your briefing from".

#### SR18. Header: conditions, validity and a note

*From: EG17, AG20. Effort S. Builders: S6 (header, note endpoint), S5 (the fields already in
`cfg`, `qstate` and `sessions`).*

**Why.** A score from 1.5× time, a paused sitting or a harder module 1 is not the same score,
and comparing it with an official-timing sitting misleads. Theirs labels a paper and a date.

* **Eyebrows** for every kind (R36): `PRACTICE TEST · PAPER #3 · LAUNCH SET` (`· RETAKE 2`) ·
  `TWIN OF SECTION #7` · `CUSTOM TEST · 20 QUESTIONS` · `SHARED BY SAM · FULL SECTION` · `PROVE
  IT · FROM SECTION #7`, alongside the spec's mock, module, diagnostic, drill and challenge.
* **Condition chips**, from `cfg`, `qstate._session` and `sessions`: `Official timing` / `1.5×
  time` / `Untimed` · `Calculator on` / `off` · `Paused 2×` · `Left the window 3× · 1:40` ·
  `Harder Module 1` · `Route shown during the test`.
* **Validity badge**: `Counts toward your estimate` for R16's standard sittings, else `Practice
  only: 1.5× time` (with the reason). A pause adds the chip but not "Practice only".
* **Like with like**: the delta, the previous ghost band and the percentile use the last sitting
  with the same standard / non-standard status: `+90 vs Section #6 (also official timing)`.
* **Note**: `Add a note` (owner), e.g. "tired, after school", up to 140 characters, stored in
  `sessions.note` through `POST /api/session/{sid}/note {note}` (S6; one handler if S5 already
  serves one). It shows on the sitting card.

**Acceptance.**
1. A `timing:'x1.5'` section's report shows "1.5× time" and "Practice only", and its delta
   names a non-standard sitting or reads "First at these conditions".
2. `POST note {note:'tired'}` → `/api/history` lists `note == 'tired'` on that item.

### E. After the report

#### SR19. Reports that close the loop: the instant check here, and re-scoring when a key is corrected

*From: experience #9, unfair-advantage #11, OG11, EG9, AG13; U3. Effort S. Builders: F6 (U3's
check, already in `POST /api/report`), F4 (`estimate.rescore_sitting`), S6.*

**Why.** Their report form sends an exam ID into silence, and a fixed paper can never correct a
past score. U3 already answers most disputes in a second with an independent solver. The one
piece missing is that a real correction must reach the student's past score, and the report
must say so.

* **Report** in the player is R17's `UI.report` with U3's instant check. It runs only once the
  key has been shown, so it marks the question `seen_key` (SR3).
* **The tag** in the player and the table reads `Reported · being checked`, `Checked: key
  confirmed` or `Fixed`, from `GET /api/reports`.
* **Re-scoring on a correction.** When U3 marks attempts `disputed = 1` (outcome `broken`, or the
  admin's "Key was wrong") or re-marks one right (`remarked`), F4's
  `estimate.rescore_sitting(sid)` runs for every finished sitting that holds the question:
  * a broken or wrong-key question is **removed from scoring**: left out of both earned and
    possible, with its own state `Removed from scoring` (SR25's token, ⊖), so ⊘ keeps R20's
    meaning, a contest question voided by leaving or copying;
  * a remarked one counts right;
  * the route is held as taken;
  * it rewrites `sessions.result`'s estimate and appends `result.rescored [{at, qid, how:
    'removed' | 'remarked', before {low, high}, after {low, high}, report}]`.
* **The strip** on the report: `M1 Q7 was corrected on Oct 2 after a report. This sitting was
  re-scored: 520–660 → 530–670.` The chart point moves, and `estimate.py` reads the new result.
  The reporter's U3 reply adds `Your report re-scored 3 sittings.`
* An open dispute changes nothing in the score; the item shows `Disputed · being checked`.

**Acceptance.**
1. A U3 `broken` fixture on a mock question: that sitting's `result.rescored` has 1 entry with
   `how == 'removed'`, the question's review status is `removed` (its cell carries ⊖, not ⊘),
   and `ledger.all_right` is computed over 43 questions.
2. A `remarked` grid-in counts right, and the estimate's `mid` rises or stays.
3. A dispute left open leaves the estimate unchanged.

#### SR20. Print a repair pack, a retry sheet and a tutor packet; share links that send twins

*From: unfair-advantage #12, experience #12, OG16, AG11's fresh link. Effort S. Builders:
S10 (the worksheet takes `session` and `qids`), S6 (menu, print CSS), F1 (print conventions).*

**Why.** Their Share / Export button has no handler. A finite bank can only reprint the paper
the student has seen. Ours prints new questions with the same traps every time, which is what a
tutor or an offline student needs.

**The ⋯ menu gains** (key `P` for the repair pack, page scope):
* **Print repair pack**:
  1. page 1: the hero, the ledger by cause, Best value next;
  2. per miss: the question regenerated exactly, your answer, the key, the misconception, the
     explanation;
  3. **Fresh practice**: 1–3 twins per miss (a select, default 2) from Review's `GET
     /api/review/worksheet?session=<sid>&qids=…&each=2`, with space to work;
  4. last page: the key with every option's misconception.
  The seeds are remembered as seen for the sitting's owner. The footer reads `These answers are
  not filed. Enter them online: /s/?c=CODE`, which opens the worksheet as an end-mode set, as
  Review's worksheet already can.
* **Print retry sheet**: only the Fresh practice pages and the key, for the active filter or
  selection.
* **Tutor packet**: the report's print layout (the spec's 1.17), then the briefing (SR17), then
  the repair pack, as one job.
* On a shared read-only view the report print and the Fresh practice pages work (fresh seeds
  leak nothing); step 2 needs the owner.
* **While a second look is offered** (SR3), the repair pack, the tutor packet and the key page
  open SR3's confirm sheet first (`This prints the answers and ends your second look for 13
  questions`); the retry sheet and CSV don't ask, and print `Hidden` where a key would be.
* **Sharing a question** from the player defaults to U28's `Send a question like this` (a twin
  link); `Copy link to exactly this question` is the second option.

**Acceptance.**
1. Emulating print on the repair pack page: 2 fresh items per miss, and every fresh seed
   differs from the originals.
2. `GET /api/review/worksheet?session=<live test>&qids=…` → 409.
3. The worksheet's `/s/` code opens as an end-mode set whose answers file.
4. With a second look offered, `P` opens the confirm sheet, and until Print anyway is chosen
   the print DOM holds no unseen miss's key or misconception.

### F. Results overview

#### SR21. An estimate and a chart that look forward and explain themselves

*From: EG10, AG14, part of OG9, EG11, AG15, OG14; U9, U11, U4, T10. Effort S. Builders: S6,
F4 (reused functions), F1 (`UI.bandChart` options).*

**Why.** Their Estimated Score card has the same three parts as the spec's (range, confidence,
trend), and their trend chart plots only the past. A student needs to know what would make the
estimate trustworthy, where it is heading by the exam date, and what happened between two
points.

**Estimate card `#estimate`** adds, under the spec's lines:
* **What would raise confidence**, from R16's rules, as a button: `One more full section →
  High · Start 70 min`, or `A section within 30 days → Medium`.
* **Practice since** (T10): `Practice since Sep 21: ≈ +15`, with its helper.
* **Projection** (U9): `At this pace: 640–700 on Nov 7`, with the cone on the chart; hidden
  under U9's rule (fewer than 2 standard sittings in 60 days).
* **Your top 3** (U4): `Fix your top 3 skills: ≈ +34` → `Practise the top 3`.
* **Climb** (U11): `Started near 520 · +90 · ahead of 74% of 212`, when n ≥ 20.
* **Nationally** (SR5): `about the 49th–88th percentile`.
* **Total** (SR4) when R&W is known, with its national percentile range and the split gap to a
  total target.

**Chart `#overview`** adds:
* **Outside scores** (S3's `outside_scores`) as hollow diamonds labelled by source (Bluebook,
  PSAT, official), already counted in R16's `mean3`.
* **What happened between** two sittings (U9's `gaps`): on hover or focus of the gap, `Sep 12 →
  Sep 20: 212 questions · 3 h 40 m · 11 mistakes fixed · Circles → Strong · +40`.
* **Twin brackets** joining paired sittings (SR7).
* **The projection cone** (U9).
* **R&W (yours)**: SR4's `rw_history` as a hatched step line in its own 200–800 lane under the
  Math chart, one dated point per entry with its source; it is never drawn as a measured band.
* **Compare**: clicking two points opens the newer report with `?vs=` (SR7).
* The legend adds `◇ = a score you added · bracket = twin pair · cone = projection · hatched =
  R&W you entered`.

**Acceptance.**
1. A learner with an outside score: the chart SVG has a diamond whose aria-label names its
   source. A learner with two R&W entries: the R&W lane has 2 points.
2. Two standard sittings 14 days apart: the SVG has a cone path, and the estimate card contains
   "At this pace".
3. The tooltip on the gap between two points contains "questions".

#### SR22. Where your points go across sittings: the gap to target, causes over time, recovered this week

*From: experience #1's overview card, experience #4's trend, outcomes #11, outcomes #6's trend,
AG18, the tile half of unfair-advantage #10. Effort S. Builders: S6 (`/api/stats` fields), F4.*

**Why.** One report says why one sitting lost points. Across sittings the question is which
cause is shrinking and whether daily practice is paying, which an all-time counter never shows.

* **Gap to target `#gap`** (under the estimate): the last 3 scored sittings' ledgers, averaged
  by cause and by domain: `Target 700 · 40 above your estimate's high end. Where your last 3
  tests lost points: Traps ≈ 55 · Slips ≈ 30 · Clock ≈ 20 · Advanced Math, hard ≈ 25`. Each
  row's `Start` drills those sittings' still-open misses in that bucket (`{pool:'history',
  ids:[attempt ids], exact:false, each:1}`).
* **Why you miss, over time `#why`**: one 100% stacked bar per scored sitting (last 10) by
  cause, with a line when a cause moved 15 points or more: `Slips fell from 45% to 20% since
  Sep 13`. Under it, the calibration trend: `Sure answers right: 88% → 93%` (SR9).
* **Totals** gain two tiles:
  * `Question types met · 185 of 386` (U8's count), linking to `/me/#atlas`;
  * `Recovered this week · ≈ +35`, sub-line `5 mistakes closed · 2 check-ins passed` (SR6's
    `points_recovered` over sittings with recovery events this week; R9's checks).
* **Skills** (the spec's 2.7): the sort adds `By points` (U4's gains), the default once gains
  exist, and each tile prints `≈ +20`.
* **Pace**: U7's card (SR13).

**Data.** `/api/stats` adds `gap {by_cause [{cause, pts}], by_domain [{domain, tier, pts}],
from: [sid]}`, `why [{id, seq, by {cause: n}}]`, `calibration_trend [{id, sure_right, n}]`,
`types_met {met, of}` and `week {recovered_pts, closed, checks_passed}`.

**Acceptance.**
1. A learner with 3 scored sittings: `/api/stats.gap.by_cause` exists and every `pts >= 0`.
2. For each `why[i]`, the counts sum to that sitting's misses.
3. The Types met tile's number equals U8's count for the learner.

#### SR23. The sittings list: peek in place, keyboard triage, recovery rings and compare

*From: experience #10, experience #6's selection, A2 / AG16 / OG13's ring, EG12. Effort M.
Builders: S6 (`UI.sittingCard`, `/api/history` fields), F3 (the `UI.review` dialog reused).*

**Why.** Their list cards show no score, and their wrong-number chips are plain spans, so
reaching a missed question takes Review → scroll → a square. The spec links the chips, but every
sitting still costs a page load. A list that says what is still owed on each sitting is a to-do
list.

**The card** (`UI.sittingCard`, shared with Tests and Today) adds:
* a recovery ring: `Recovered 9/13 · ≈ 60 open` (SR6);
* miss chips that take the Fixed-since badge once recovered;
* the cause line: `Lost 13: 6 traps · 3 clock · 2 slips · 1 entry · 1 gap` (T16);
* `Reviewed 7 of 13` (SR14);
* for a pair: `vs Section #7: fixed 9` (SR7);
* the note (SR18);
* miss chips grouped by (subject, module) with `UI.qlabel` (`M1 ✕ 1 6 7`; `Math M1 …` once a
  sitting has two subjects), never a hard-coded M1 / M2 pair.

**Peek.** A chevron, or Space on a focused card, expands the card in place into a mini report:
the band and the ledger bar, the domain bars, one status strip per (subject, module) (each cell
opens the player as a dialog over Results for that sitting), the reviewed meter, and Fix and Review.
Several can be open.

**Keys** (page scope `results`, §3.2): `J` / `K` move between cards, Space peeks, Enter opens the
report, `F` opens the card's Fix, `X` selects it for Compare. Two selected show a Compare bar
linking `/results/report/?id=<newer>&vs=<older>`.

**Filters** add `Not reviewed yet`, `Has skill ▾` (sittings that included a topic) and the sort
`Most points still open`. Week headers carry a summary: `This week · 3 sittings · 128 questions ·
6 h 10 m · +40`.

**Data.** `/api/history` items add `ledger {total, by_cause}` (scored), `recovery {recovered,
open, points_open}`, `reviewed {n, of}`, `causes {cause: n}`, `pair {with, fixed}` and `note`.
New params: `reviewed=0`, `topic=`, `sort=points_open`. Week groups come with `summary
{sittings, questions, ms, delta}`.

**Acceptance.**
1. `/api/history?kind=tests&sort=points_open` is ordered by `recovery.points_open`, descending.
2. Space on a focused card expands `.peek` containing a gauge; Enter opens the report.
3. `X` on two cards shows the Compare bar with a link containing `vs=`.

#### SR24. A first visit that shows the value: a live sample report, and a score you already have

*From: EG13. Effort S. Builders: S6 (the sample sitting in `init()`), F5 (a fixed seed list).*

**Why.** Their empty state and the spec's both say "complete a test first". A switching
student has to commit 70 minutes before seeing anything. A real, working report shows the
value in a minute.

* **Sample report.** S6's `init()` (§2.10) creates, idempotently, a finished section for the
  learner `sample:report` with the id `sample-section`, from a fixed seed list: 31 of 44 right,
  13 misses of every cause, a second look done, 4 recovered.
  * **Fixed timestamps**: the section starts `2026-09-01T16:00:00Z` and finishes 64 min later;
    the second look is dated Sep 1, the recovery attempts Sep 3–8 and a Prove-it sitting Sep 8,
    so every "since" is after the sitting and the timeline reads the same on every rebuild. Its
    `result.odds` (SR12) is stored from fixed ratings, not the live ones.
  * **Left out of every figure across students.** Every query that aggregates over learners
    adds one shared fragment, `db.NOT_SAMPLE` (`learner NOT LIKE 'sample:%'`): the in-site
    percentile and histogram (R16, SR5), `drill.levels()` crowd counts and times (SR12, P16),
    `ratings.py` updates and its startup backfill (P11: a `sample:` attempt never moves an
    `item_ratings` row), Compete boards, seasons and Climb (U11), U8's counts, S8's daily
    review field, and admin counts. `server/checks/s6.py` greps `server/` for queries over
    `attempts` or `sessions` without a `learner = ?` filter and fails any that lack
    `NOT_SAMPLE`.
  * **Nobody can write as it.** A request whose learner code starts with `sample:` is refused
    (403) on every write route, so the sample can't be added to or claimed. `/results/report/?id=sample-section`
  renders it read-only under the strip `Sample report · not yours`. Every control is live
  (filters, Colour by, the player, What if, compare with a paired sample twin). Anything that
  would write is disabled with the tip `Sit your own section to use this.`
* **On `/results/` for a new learner**, above the empty states: a card `See what a report shows
  you` → the sample, and `Add a score you already have` (S3's add-a-score sheet), which puts a
  diamond on the chart and feeds R16's estimate at once.
* The spec's estimate empty state (Full section · One module · Diagnostic) stays.

**Acceptance.**
1. Results for `sample-section` as any learner: `mine == false`, `ledger` non-null, 13 misses.
2. The page contains "Sample report", and the Fix button is disabled.
3. Any POST to that sitting (`second`, `why`, `note`, drill `from_session`) → 403, and any
   write with `X-Learner: sample:x` → 403.
4. On a db, record `rank.n` of a standard mock, `crowd.n` of an item, every `item_ratings` row
   and the daily board; delete and recreate the sample (`init()`): all are unchanged.
5. The sample's `recovery.timeline` days are all after its `finished`, and two rebuilds give
   byte-equal results payloads.

### G. Every state a sitting had

#### SR25. Tries and Mixed in practice sets, Compete's own numbers on contests, and removed questions

*From: the parity gaps on rows 19, 20, 30 and 32 (their Attempt History, their Mixed cell,
their contest Score / Correct / Incorrect / Skipped / Voided); R20's states; S4's `tries`;
Compete's `sessions.result`. Effort S. Builders: S6 (statuses, the contest hero and tiles, the
tries read), F1 (legend entries and the ⊖ token), S4 (`tries`, already stored), S8 (the result
fields, already stored).*

**Why.** Their QBank history lists every try (`#1 ⊗ Incorrect · Option A · 00:22`), their
overview marks wrong-then-right as Mixed, and their contest panel shows Score / Correct /
Incorrect / Skipped / Voided. The spec's report reads none of S4's `tries`, has no Mixed, and
gives a challenge only `8/10 · 9:42`, so a retry-mode question that was wrong then right shows
as plain Incorrect, and the report and Compete's panel disagree about the same sitting. A
report that shows fewer states than the sitting had, or other numbers than the contest's own
panel, loses the student's trust.

**Practice sets.**
* Review items for drills gain `tries [{n, given, correct, reason, ms, at}]`, S4's `tries` rows
  for (session, qid) in order.
* **Mixed** (R20's ~, the diagonal split): the first try wrong and a later try right, in retry
  mode. Only the first try counts (R20), so it is a miss: it sits in Mistakes with the tag
  `right on try 2`, and in Incorrect's count with the sub-line `2 of them right on a later try`.
* The Show chip `Mixed · 2`, its legend entry, and Colour by Status draw it. Drill tiles add
  `Mixed · 2 · right on a later try` for retry-mode sets.
* **The player**, above the type's trajectory (SR16): `Tries in this set: ✕ A · used the slope
  as the intercept · 0:22 → ✓ C · 0:41`, each try with its glyph, letter or typed value, named
  mistake (or SR10's diagnosis) and time. Hints taken (`tries.hints`, practice.md) show as `· 1 hint`.

**Contest sittings** (the daily challenge and private contests; a private contest is an invite
code or link that Compete owns, decision 5).
* Review items carry R20's **Skipped** (», left without an answer) and **Voided** (⊘, voided by
  leaving or copying), from `sessions.result` and `qstate`, with Show chips (`Skipped · 1` ·
  `Voided · 0`, 0 disabled) and legend entries.
* **Hero**: `Points 230 · base 200 · pace 20 · finish 10` and `right 8 · wrong 1 · skipped 1 ·
  voided 0`, then the spec's `#12 of 140 today · average 6.1/10` and `Board` (a private
  contest ranks among its own players: `#3 of 9 in Maya's contest`). All are read from
  `sessions.result` (`points`, `points_parts`, `right`, `wrong`, `skipped`, `voided`), the same
  fields Compete's panel reads; the report never recounts them.
* **Tiles** (8; 4×2, 2×4 on phone): Points (`base 200 · pace 20 · finish 10`) · Right · Wrong ·
  Skipped (`a skip earns nothing`) · Voided (`left the tab or copied`) · Time · Per question ·
  Rank.

**Removed from scoring** (SR19's key corrections) is its own state, so ⊘ keeps R20's contest
meaning. Token: paper with a dotted `--ink` edge and glyph ⊖. Tooltip: `Removed from scoring on
Oct 2 after a report`. It has a Show chip, a legend entry, and is left out of every count
except its own.

**Data.** Review item `status` adds `mixed`, `skipped`, `voided` and `removed`; drills add
`tries`. Contest results add `contest {points, points_parts {base, pace, finish}, right, wrong,
skipped, voided, rank, n, board}`, copied from `sessions.result` on read.

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

### 3.1 Inside §3.5 (spec/rebuild-v2.md lines 6055–7045)

Line numbers are the file's as of 2026-09-23. "Add" means insert after the quoted line; "replace"
means the quoted text goes.

**§3.5.3 Review changes, and §0 Rules**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6145 | `- Count-up numbers.` | Replace: `- Numbers count from the previous same-kind sitting, on the first view after Finish only.` | SR4 |
| 6166 | `` - **Retake as a test:** a parallel section, same templates on fresh seeds matched on tier and format through `blueprint.draw_matching`, with Module 2 routed afresh and scored like any section. `` | Replace: `- **Retake as a test:** Tests' twin (POST /api/mock/new {kind:'twin', twin_of}), reported slot by slot against its source.` | SR7 |
| 6185 | `There is one orange-filled primary per region: the page header, the player and the skill panel.` | Replace: `There is one orange-filled primary per region: the page header, the second-look banner, the player, the skill panel and the selection bar.` | SR3, SR15 |
| 6196 | `- **Filtered out:** 30% opacity.` | Add: `- **Removed from scoring:** ⊖, paper with a dotted ink edge, a question taken out of scoring by a key correction (SR25); ⊘ stays R20's contest Voided.`, `- **Mixed:** R20's ~ in retry-mode practice sets; **Skipped** » and **Voided** ⊘ in contests (SR25).` and `- **Recovered:** a miss proven since takes Fixed since, driven by proof (SR6), not only by a trap closing.` | SR19, SR25, SR6 |
| 6201 | `` … and URL hash (`#q=m1-7`, `#q=7`) all use it. `` | Replace the addresses: `the canonical address is {subject}-m{module}-{n} (#q=math-m1-7); #q=m1-7 and #q=7 are shorthand for Math. Labels come from UI.qlabel: “M1 Q7” with one subject, “Math M1 Q7” with two.` Add: `The page also accepts ?q=M1-7 (Tests' chips, §3.4.7) and turns it into the hash on load.` | decision 3; — (a conflict with §3.4.7) |
| 6204 | `` - **Motion:** numbers count up over 600 ms and bars grow on first paint, once. `prefers-reduced-motion` shows final values at once. `` | Replace: `- **Motion:** on the first view after Finish (?fresh=1) the gauge sweeps from the previous band, numbers count from the previous same-kind values and bars grow, once. Revisits and prefers-reduced-motion show final values at once.` | SR4 |

**§1.1 Layout and §1.2 Header**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6210 | `- **Section order:** header, hero, tiles, modules, domains, skills in this sitting, difficulty & format, pace, answer changes, mistakes, question review, up next.` | Replace: `- **Section order:** header, recovery strip, second-look banner, hero, ledger, compare, takeaways, tiles, habits, mistakes with best value, question review, modules, domains, skills in this sitting, judgement, difficulty & format, pace, up next. A jump bar sticks under the page bar once the hero scrolls away.` | SR14 |
| 6213 | `  - Tiles run 2 across (4 rows) and domains 2×2.` | Replace: `  - Tiles run 2 across (5 rows) and domains 2×2.` | SR3, SR6 |
| 6214 | `  - Once the hero scrolls away, an action strip sticks under the top bar: the primary, plus “Review” and ⋯.` | Replace: `…: the primary, “Jump to ▾”, “Review” and ⋯.` | SR14 |
| 6226 | `- drill: “PRACTICE SET #45 · FROM SECTION #7”. …` | Add the kinds: paper `PRACTICE TEST · PAPER #3 · LAUNCH SET` (`· RETAKE 2`), twin `TWIN OF SECTION #7`, custom `CUSTOM TEST · 20 QUESTIONS`, shared `SHARED BY SAM · FULL SECTION`, Prove it `PROVE IT · FROM SECTION #7`. | SR18 |
| 6229 | `**Title line:** “Wed, Sep 23, 2026 · 6:15 AM · 64 min · Timed”. …` | Add: condition chips (Official timing / 1.5× time / Untimed · Calculator on or off · Paused n× · Left the window n× · Harder Module 1 · Route shown during the test), the validity badge (Counts toward your estimate / Practice only: reason), and `Add a note` (sessions.note). | SR18 |
| 6232 | `1. **Primary split pill “Fix these · 13”.** The main part runs every miss once. ⌄ opens a menu:` | Replace: `1. **Primary split pill “Win back ≈ 60 pts · 9 questions · 14 min”** on scored sittings (“Fix these · 13” on drills). The main part runs the misses in order of points per minute up to the daily minutes, as {from_session, only, order:'given', source:'fix'}. ⌄ opens a menu:` Add to the menu: Everything · Traps only · Slips, timed at pace · Clock losses · Entry · Gaps: Learn it first · Sure and wrong · Guessed right · Should-have-had · Fix the selection (which replaces “Just the 4 shown”). | SR2 |
| 6241 | `` 3. **Outline “Retake as a test”** (mock, module, diagnostic): POST `/api/mock/new {like: sid, full}`. It builds a parallel section … `` | Replace: `3. **Outline “Retake as a test”** (mock, module, diagnostic, paper): POST /api/mock/new {kind:'twin', twin_of: sid}. Its report opens with Then vs now against this sitting.` The helper stays. | SR7 |
| 6247 | `   - “Report a problem with this sitting”` | Add to the ⋯ menu: `Compare with…`, `What if…`, `Print repair pack`, `Print retry sheet`, `Tutor packet`. | SR7, SR2, SR20 |

**§1.3 Score hero**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6261 | `` - The previous same-kind band is a `--mat` ghost segment. `` | Add: `- Today ≈ (dotted), With a second look (hollow) and What if (dashed) layers, and a legend line naming the layers present.` | SR4, SR3, SR6, SR2 |
| 6264 | `- Caption: “Math section only · Reading and Writing is not on SAT Freshman yet”.` | Replace: `- Total, when R&W is known: “Total ≈ 1,130–1,270 · Math 520–660 measured here · R&W 610, you entered Sep 12 (Bluebook)”; else an inline “Add your R&W score” field. Caption: “Math measured here. Reading and Writing is your own score until SAT Freshman has R&W questions.”` | SR4 |
| 6270 | `- **Percentile:** “62% of students here scored at or below you on their first section (148 students)”.` | Add before it: `- **Nationally:** “your band 520–660 sits at about the Nth–Mth percentile of SAT takers (College Board, year)”, with the ⓘ note.` Add after its sub-bullets: the dot histogram at n ≥ 20. | SR5 |
| 6276 | `  - Lower: “Module 1: 11/22 (50%) → easier Module 2, which tops out at 580.” …` | Add: `  - When Module 1 is 3 or fewer right short: SR1's route line with the saver chips.` | SR1 |
| 6277 | `` - **What-if** (from `whatif`): “3 easy misses. With them right: 560–700 on the same Module 2.” If there are no easy misses, it uses medium misses. Omitted when nothing was missed. `` | Replace: `- **What-if:** “3 easy misses: with them right, 560–700” (the Flip easy misses preset, from estimate.rescore). Then the path to target: “4 questions from 700 on this section: …”. The ledger and What-if mode follow.` | SR1, SR2 |
| 6278 | `` - **Twins:** “Tried 3 like this since · 2 right” … `` | Add: `- **Recovered:** “Recovered 9 of 13 · ≈ +50 · 4 open (≈ 60)”, and the fact “4 misses were on types you had 75%+ odds on” when 2 or more.` | SR6, SR12 |
| 6291–6292 | `- Big “8/10” and “9:42”.` / `- “#12 of 140 today · average 6.1/10” and a “Board” link.` | Add before them: `- “Points 230 · base 200 · pace 20 · finish 10” and “right 8 · wrong 1 · skipped 1 · voided 0”, from sessions.result, the same fields as Compete's panel. A private contest (invite code or link, Compete's) ranks among its own players.` | SR25 |
| 6279 | `` - **`<details>` “How this is estimated”:** `` | Add two lines: `“Points: each miss is re-scored with this report's scoring, on the route you took.”` and `“Nationally: College Board's published user percentiles ({year}); our band is placed on them, it is not a College Board score.”` | SR1, SR5 |

**§1.4 Tiles to §1.10**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6296 | `Eight tiles: 4×2 on desktop and tablet, 2×4 on phone.` | Replace: `Ten tiles: 5×2 on desktop and tablet, 2×5 on phone.` Add rows: `Second look · 5 of 13 · “slips · 6 gaps · 2 to go”` and `Recovered · 9 of 13 · “≈ +50 since · 4 open”`. | SR3, SR6 |
| 6300 | `\| Correct \| 31 \| “70% of 44” \|` | Sub-line: `“70% of 44 · need 35 for 700”` | SR2 |
| 6301 | `\| Incorrect \| 11 \| “9 still open” \|` | Sub-line: `“≈ −130 pts · 9 still open”` | SR1 |
| 6302 | `\| Unanswered \| 2 \| “counted as not correct” \|` | Sub-line: `“≈ −25 pts · a guess costs nothing”` | SR1, SR13 |
| 6309 | `- **Drill:** the tiles become Correct / Incorrect / Repairs / Accuracy / Time / Per question / Opened / Fixed.` | Add: `/ Second look (end-mode sets) / Recovered / Mixed (retry-mode sets)`. Add: `- **Challenge and private contests:** Points / Right / Wrong / Skipped / Voided / Time / Per question / Rank.` | SR3, SR6, SR25 |
| 6328 | `` - **Focus:** “Missed most: Linear inequalities, Systems” (scoring's existing `focus`). `` | Replace: `- **Best value:** “Linear inequalities · ≈ +25 · Fix 3” (the domain's top Best value row). - **Points:** “≈ −55 pts · 40% of your gap”. #domains sorts By points by default on scored sittings, with the weight check under the cards.` | SR1, SR2 |
| 6344 | `- Easy / Medium / Hard rows: glyph, “6/6 · 100%”, bar, “avg 0:58”.` | Replace the last part: `“avg 0:58 · budget 1:05 · students 0:45”`. | SR13, SR12 |
| 6348–6363 | `` ###### 1.9 Pace (`#pace`) `` and its chart, chips, phone and no-data lines | Replace with SR13's region: the clock replay per module, each bar with its budget tick (the flat 1:35 line stays as a reference), the Banked / Time sink / Rushed / Stuck chips, the facts, the three sets. "No time data" keeps its line. | SR13 |
| 6365–6368 | `` ###### 1.10 Answer changes (`#changes`, tests) `` and its three lines | Replace the heading with `` ###### 1.10 Judgement (`#judgement`, tests and tagged drills) ``. The three lines become its panel 3; add panels Confidence, Flags, Eliminations and time away, and the notes rail. | SR9 |

**§1.11 Mistakes and §1.12 Question review**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6372 | `**Heading:** “Mistakes · 13”, with the helper “9 named misconceptions · 2 grid-ins · 2 not answered · 3 fixed since”.` | Add to the helper: `· Reviewed 7 of 13`. While a second look is offered, unseen rows read “Misconception hidden until your second look”. | SR14, SR3 |
| 6374 | `**Sort select:** Question order / Open first / By topic / Most hit.` | Replace: `**Sort select:** Most points (the default on scored sittings) / Question order / Open first / By topic / Most hit / Surprise first.` | SR1, SR12 |
| 6376 | `**Groups, all shown, never cut:** Open (n), Fixed since (n), Not answered (n).` | Replace: `**Groups, all shown, never cut:** Sure and wrong (n), Open (n), Fixed since (n), Not answered (n).` | SR9 |
| 6380 | `- Meta: “M1 Q1 · Linear inequalities · Hard · ×3 all time”.` | Replace: `- Meta: “M1 Q1 · Linear inequalities · Hard · ×3 all time · ≈ +15 · Trap · habit: sign”`. | SR1, SR8, SR11 |
| 6386 | `- **Grid-in misses:** “Missed grid-in: 8/161”, with the skill in the meta line (“Two-way table”).` | Replace: `- **Grid-in misses:** the named mistake or SR10's diagnosis (“Right value, too few digits: 2/3 needs .6666 or .6667”), with the skill in the meta line.` | SR10 |
| 6394 | `- **“Show” segmented with live counts:** All 44 · Incorrect 11 · …` | Add to Show, for the kinds that have them: `Mixed · Skipped · Voided · Removed from scoring`. Add: `- **Act on:** Cause ▾ · Should-have-had · Hard for you · Hard for everyone · Sure and wrong · Guessed right · Recovered · Slipping · Not looked at · Has note, each with a count, 0 disabled.` | SR15, SR25, SR12 |
| 6404 | `- **“Colour by”:** Status \| Difficulty \| Time.` | Replace: `- **“Colour by”:** Status \| Difficulty \| Time \| Cause \| Points \| Level \| Crowd.` | SR15 |
| 6416 | `- **Status:** Correct ✓ · Incorrect ✕ · Fixed since · Unanswered – · …` | Add: `· Mixed ~ · Skipped » · Voided ⊘ (contests) · Removed from scoring ⊖ · ▲ would have routed you up`, and legends for Cause, Points, Level and Crowd (an estimated crowd marked est.). | SR25, SR19, SR1, SR15, SR12 |
| 6424 | `- Challenge cells show the crowd % under the number.` | Replace: `- Challenge cells show the slot's % right under the number (S8's daily review).` Add: the hover card, and Shift / Ctrl-click, Space and long-press selection with the selection bar. | SR12, SR15 |
| 6427 | `- **Columns:** # · Skill (glyph + topic, skill label under it) · Difficulty · Format · Time · Your answer · Correct · Result · Changed · Flag · Mistake.` | Replace: `- **Columns:** # · Skill · Difficulty · Level · Format · Time (and budget) · Your answer · Correct · Result · Cause · Worth · Odds · Second look · Students right · Changed · Flag · Note · Mistake.` Add: SR15's layout (its own scroll box, sticky # and Skill, edge shadows, the fixed widths, 36 px glyph columns with tooltips, one-line answers with the full text in the hover card, every header a button). | SR15, SR12 |
| 6428 | `` - Sortable by #, Time, Difficulty and Result, with `aria-sort`. `` | Replace: `- Sortable by #, Time, Difficulty, Result, Worth, Cause, Level, Odds and Students right, with aria-sort.` | SR15 |

**§1.13 Review player**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6456 | `- The difficulty glyph and word, “Multiple choice” / “Grid-in”, and “1:42 · pace 1:35”.` | Replace the end: `“1:42 · budget 1:35”`. Add: `- “L4 · your odds were 82% · rough (6)” and the students line (“74% of 212 students get this type right · they take 1:05”, or “About 64% … (estimated)” below 20), the cause chip “Cause: Slip (auto) ▾” and “≈ +10”.` | SR13, SR12, SR8, SR1 |
| 6477 | ``   - Grid-ins: “Your answer −7” and “Correct answer 8/161”, plus “Also accepted: .0496, .0497” (`accepted`). `` | Add: `, and SR10's diagnosis under “Your answer”.` | SR10 |
| 6479 | `` - **Explanation card:** `--tile` fill, heading “Explanation”, the rationale in serif. `` | Replace: `- **Explanation card:** P1's card: the type's about line, the Steps tab with the step where your answer left the path outlined (every section and diagnostic template has steps at launch), P1's option lines, then the rationale in serif. A template without steps opens with its written Method block (3+ sentences: the idea, the method, the check for the common trap), never the rationale alone. “Next time I will…” sits under it (owner).` | SR16, SR17 |
| 6481 | `` - **“Earlier on this question type”:** the last 5 attempts on the same template from other sittings (`history`). `` | Replace: `- **“This question type over time”:** UI.history as a strip of every attempt on the template before and after this sitting, with times, ending with Recovered or Slipping. Rows stay available under it.` Add before it, for practice sets: `- **“Tries in this set”:** each try from S4's tries with its glyph, answer, named mistake and time.` | SR16, SR6, SR25 |
| 6484 | `- **Challenge:** “41% of 140 students got this right”, plus how the crowd picked each option: “A 12% · B 41% · C 9% · D 38%”, each wrong one naming its misconception.` | Replace: `- **Challenge:** “41% of 140 got slot 7 right · most picked: forgot to halve (31%)”, from S8's daily review per slot, by named misconception, never by option letter (decision 1).` Add for every other kind: `“31% of students who miss it pick this one”` under each wrong option (n ≥ 20). | SR12 |
| 6487 | `- **Primary “Try one like this”:**` | Replace: `- **Primary split “Try one like this ▾”:** on a trap or gap miss its menu holds See one solved first (the option your mistake produces on the new numbers tagged), Learn it · example + 3, and P17's axes.` The sub-bullets stay. | SR16 |
| 6501 | `- A pick reveals locally (“B · wrong again” / “D · right this time”) without filing anything, and restores that question.` | Replace: `- On a question whose key you have already seen, a pick reveals locally (“B · wrong again” / “D · right this time”) and files nothing. A miss you have not seen yet is answered in Second look instead, which files a repeat (R21).` | SR3 |
| 6503 | `**Bottom bar:** “← Previous” \| the position within the active filter (“7 of 11 incorrect”) \| “Next →”. …` | Add: `On a phone, Next miss and Try one like this sit in the bottom bar, and left / right swipes move within the filter.` | SR16 |
| 6514 | `- Esc: close` | Add: `- In Second look: A–D or 1–4 pick, Enter checks, K confidence, H shows the answer without filing.` | SR3 |

**§1.14 to §1.17**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6518–6534 | `` ###### 1.14 Report a problem (`UI.reportDialog`, …) `` with its fields, 0/120 and 0/2000 counters, 9 categories and “up to 3, PNG/JPEG/WebP, 5 MB each” | Replace with: `R17: Shell §2.10's UI.report(ctx), its category union, up to 10 images and Your reports, plus U3's instant check. It runs only after the key has been shown and marks the question seen. The tag reads “Reported · being checked”, “Checked: key confirmed” or “Fixed”. An upheld correction re-scores the sitting.` | SR19 |
| 6537 | `` - The coach's pick from `/api/map`: topic chips, “10 questions · 16 min”, a “Start” pill and a “New section” link. `` | Add before it: `- On scored sittings, the top Best value row first: “Start: Circles · ≈ +30 · ~12 min”.` | SR2 |
| 6541 | `` - **Loading:** static skeletons at real sizes (a gauge circle, 8 tiles, cell rows), `aria-busy` on main. No dashes, no loops. `` | Replace the start: `- **Loading:** paint at once from the prefetched copy in sessionStorage when there is one, then revalidate; otherwise static skeletons at real sizes (a gauge circle, 10 tiles, cell rows), …` Add: `- **Sample** (id=sample-section): read-only, every write disabled with a tip.` | SR16, SR24 |
| 6557–6560 | `  - hero (with percentile and what-if), tiles, modules and domains;` … `  - the full question table (your answer, key, mistake, time).` | Add: `the ledger, compare, judgement and pace`. The question table prints landscape as SR15's two tables (# · Skill · Your answer · Correct · Result · Cause · Worth · Mistake, then the rest), with SR3's `Hidden` while a second look is offered. The repair pack, retry sheet and tutor packet are separate print jobs; the first and last ask before printing unseen keys (SR3). | SR20, SR15, SR3 |

**§2 Results overview**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6579 | `  - “Exam Oct 3 · 10 days”` | Add: what would raise confidence (a button), Practice since (T10), the projection (U9), Fix your top 3 (U4), Climb (U11), Nationally (SR5), the total (SR4). | SR21 |
| 6580 | `- **Footnote:** “Math section only · Reading and Writing is not on SAT Freshman yet.”` | Replace with SR4's caption. | SR4 |
| 6592 | `- **Legend:** “Band = estimated range · dot = middle · line = trend · dashed = target · shaded = current estimate”.` | Add: `· ◇ = a score you added · bracket = twin pair · cone = projection`. Add bullets: outside scores as diamonds, what happened between two sittings on the gap, twin brackets, the projection cone, two clicked points open Compare. | SR21, SR7 |
| 6595 | `` ###### 2.4 Totals (`#totals`, 6 tiles; 3×2 on phone; every window is stated) `` | Replace: `8 tiles; 2×4 on phone`. Add rows: `Question types met · 185 of 386 · → /me/#atlas` and `Recovered this week · ≈ +35 · “5 mistakes closed · 2 check-ins passed”`. | SR22 |
| 6606 | `**Last 14 days** (under the tiles): …` | Add after it: `#gap` (Gap to target, decomposed) and `#why` (Why you miss, over time, with the calibration trend). | SR22 |
| 6610 | `- Line: “Average time: easy 0:58 · medium 1:31 · hard 2:24 (test pace 1:35)”.` | Add: each row's budget and students' median; then U7's Pace card as its own region. | SR13 |
| 6624 | `- **Sort:** By domain / Weakest first / Most open mistakes / Least practised / Least recent. …` | Replace: `- **Sort:** By points (the default once U4's gains exist) / By domain / Weakest first / …`, and each tile prints “≈ +20”. | SR22 |
| 6638 | `- The 10 most-hit traps of all time. A row: …` | Replace the first sentence: `- The 10 most-hit misconceptions of all time, grouped by norm across question types (“in 3 question types”), with T9's .seg By question type · By habit.` | SR11 |
| 6646–6648 | `- Tests adds a kind select: …` / `- Check-chip “Has open mistakes”.` / `- Sort: Newest / Oldest / Highest / Lowest.` | Add: check-chips `Not reviewed yet`, `Has skill ▾`; sort `Most points still open`. | SR23 |
| 6671 | `  - “Tried 3 like this” when that applies;` | Add: the recovery ring, the cause line, `Reviewed 7 of 13`, `vs Section #7: fixed 9`, the note; the peek; keys J / K / Space / Enter / F / X; the Compare bar; week summary lines. | SR23 |
| 6681 | `- **New learner:** the estimate empty state; tiles at 0; …` | Add: `the “See what a report shows you” card (the sample report) and “Add a score you already have”`. | SR24 |

**§3 Changes elsewhere, §3.5.4 Extras**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6689 | ``   - The time on each question is accumulated while it is visible, and POSTed to `/time` on every question change and before finish, chained on the existing `sent` promise. `` | Replace: `  - Per R7: the dwell ms goes with each answer save and other deltas through POST /api/session/{sid}/state. The runner also logs qstate._session.visits and away_log, adds ?fresh=1 to the report redirect, and prefetches /results while “Finishing…” shows.` | SR13, SR9, SR4, SR16 |
| 6690 | `` - **Practice session summary:** a “Review every answer” outline → `/results/report/?id=`. `` | Add: `The finish redirect adds ?fresh=1 and prefetches the results. - **Tests lobby:** shows the briefing from the last scored sitting before Begin.` | SR4, SR16, SR17 |
| 6716 | `- **Retake as a test (parallel form)**: …` | Replace: `- **Twin test, compared slot by slot**: Tests' parallel form of any finished sitting, reported as Then vs now: fixed, slipped, still missing, same trap again.` | SR7 |
| 6718 | `- **What-if line**: “3 easy misses. With them right: 560–700.” …` | Replace: `- **Where your points went**: every miss priced by exact re-scoring, by cause and by difficulty, the route cliff, the path to target, a Fix ordered by points per minute, and What-if mode.` | SR1, SR2 |
| 6731 | `- **Challenge crowd %, per option**: Everyone sits the same ten, so …` | Replace: `- **Challenge crowd, per slot and per named misconception**: everyone sits the same ten question types with their own numbers (decision 1), so each slot shows “41% got this right” and how many fell for each named misconception.` | SR12 |

**§3.5.5 Server changes**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6746–6764 | `- **Store flags, per-question time and an answer trail on test sittings**` with `db.py LATER_COLUMNS gains:` the three `sessions` columns, `New POST /api/session/{sid}/flag`, `New POST /api/session/{sid}/time`, the trail in put_answer | Replace with: `- **Flags, per-question time and the trail follow R5 and R7**: the flags table through S10's POST /api/session/{sid}/flag; ms, trail, conf, struck, visits and away_log in sessions.qstate through S5's /state. The three columns, /time and the put_answer trail are not built (§2.5).` | R5, R7 |
| 6766 | `` - **Tests file their time**: progress.record_paper(learner, session, questions, answers, times) passes times.get(qid) as ms, … finish() reads row['times']. … `` | Replace `times.get(qid)` with `qstate[qid].ms` and `row['times']` with `row['qstate']`. | R7 |
| 6789 | `  - rank {ranked, attempt, pct\|null, n}: …` | Replace the shape: `rank {ranked, attempt, pct\|null, n, national {low_pct, high_pct, source, year}, hist\|null}`. | SR5 |
| 6790 | `  - whatif {tier, count, estimate}: flip the easy misses (else the medium ones) to correct, then re-run scoring.score, plus section_score on the same route.` | Replace: `  - ledger (SR1), second (SR3), recovery (SR6), total (SR4), judgement (SR9), habits and norms (SR11), pace (SR13), debrief (SR14). whatif is not built: its sentence is the Flip easy misses preset.` | SR1–SR14 |
| 6795 | `  Each review item gains:` | Add to the list: `subject and address; worth; cause {cause, auto, evidence}; second; seen; odds; crowd; diagnosis (grid-ins); recovery ('recovered' \| 'slipping' \| 'open'); note and marks (R6); tries (practice sets); status mixed, skipped, voided or removed; rescored (when removed or remarked).` While a second look is offered, SR3's hold_back leaves the whole held-back set out of unseen misses for every viewer (answer, reasons, rationale, mistake, accepted, steps, diverge, wrong_step, option_steps, diagnosis, crowd.option_share, the struck-key evidence and marks), and results add `contest {…}` (SR25), `route_rule` per subject and `odds`. | SR1, SR3, SR6, SR8, SR10, SR12, SR19, SR25, decision 3 |
| 6806 | `  - crowd for challenges: {right, n, options [4 shares]}, from first attempts grouped by (template, seed) across that day's challenge sessions.` | Replace: `  - odds for every item: {you, at, avg, skill_rating, item_rating} from P11, with result.odds stored at finish. crowd for every item: {n, rate, median_ms_right, option_share, level, rough, level_n} from drill.levels() and P11 (n ≥ 20; below it the estimated rate from odds.avg). For challenges, per slot from S8's daily review, shares by norm.` | SR12 |
| 6809 | `- **POST /api/drill: only / each / scope / twin**` | Add: `order: 'given' keeps only's order; source 'fix'.` | SR2 |
| 6828–6836 | `` - **POST /api/mock/new {like}** `` and `NewMock gains like: str \| None.` with its paragraph | Replace: `Not built. Retake as a test is Tests' {kind:'twin', twin_of} with cfg.slot_of (S5), compared through GET /api/session/{sid}/compare.` | SR7 |
| 6836 | (after the deleted block) | Add the new routes, all in `server/api_results.py`: `POST /api/session/{sid}/whatif`, `/second`, `/seen`, `/second/state`, `/why`, `/note`; `GET /api/session/{sid}/compare`, `/briefing`. | SR2, SR3, SR7, SR8, SR17, SR18 |
| 6853 | `  - open (traps opened in it and still open)` | Add: `ledger {total, by_cause}, recovery {recovered, open, points_open}, reviewed {n, of}, causes, pair {with, fixed}, note`; params `reviewed=0`, `topic=`, `sort=points_open`; week summaries. | SR23 |
| 6876 | `  - profile {target, exam_date}` (in /api/stats) | Add: `gap, why, calibration_trend, types_met, week`. | SR22 |
| 6893 | `  POST /api/report is multipart: … and up to 3 images (png/jpeg/webp, ≤5 MB each, magic bytes checked). …` | Replace with: `R17 and U3: Shell §2.10's POST /api/report (up to 10 images, the category union, the instant check). An upheld correction calls estimate.rescore_sitting.` | SR19 |
| 6899 | `  LATER_COLUMNS gains ("learners","share","TEXT").` | Replace: `R18(a): the progress link is links(kind='progress'); /results/?share= accepts that token.` (§2.5 already drops the column.) | R18 |
| 6908 | `  - flag, time and trail round-trips` | Replace: `  - flag (S10) and qstate ms, trail and visits (R7) round-trips` | R5, R7, SR13 |
| 6911 | `  - mock/new like (same templates, new seeds)` | Replace: `  - the twin's compare (slot pairing and change counts)` | SR7 |
| 6913 | `  - whatif ≥ actual` | Replace: `  - the ledger's Shapley sums (by cause, by tier, by domain and incorrect/blank each equal all right minus actual, also at the 580 cap) and whatif = rescore` | SR1, SR2 |
| 6914 | `  - crowd %` | Replace: `  - crowd by (template, tier) and by norm, with the n ≥ 20 rule` | SR12 |

**§3.5.7 Shared needs, §3.5.8 Acceptance, §3.5.9 Open questions**

| line | the spec says | change | upgrade |
|---|---|---|---|
| 6947 | `` … 'Also accepted'; and a hide-answers mode. … `` | Add: `UI.review gains the modes second (SR3) and pair (SR7), swipe and preload (SR16).` | SR3, SR7, SR16 |
| 6952 | `- UI.gauge (200–800 arc: band, midpoint, target, previous ghost) and UI.scoreChart (…)` | Add: gauge layers Today, With a second look, What if, and the first-view sweep; chart options `outside`, `gaps`, `pairs`, `projection`. New F1 components: `UI.stackBar`, `UI.clockLane`, `UI.dotStrip`, and a selection bar. | SR1, SR4, SR5, SR13, SR15, SR21 |
| 6959 | `- UI.reportDialog plus multipart POST /api/report (meta box, title, categories, details, 3 screenshots, 'Reported' tag), …` | Replace: `- UI.report (R17) with U3's instant check.` | SR19 |
| 6964 | `- Exam runner posts flags and per-question times, and the server keeps an answer trail (POST /api/session/{sid}/flag, /time), built with the exam-runner section.` | Replace: `- Exam runner: flags through S10's endpoint (R5); ms, trail, visits and away_log through /state (R7); ?fresh=1 and the results prefetch on finish; the briefing in the lobby.` | SR4, SR9, SR13, SR16, SR17 |
| 6987 | `6. Start a mock and POST /api/session/{sid}/time {times: {qid: 90000}} for several questions, …` | Replace the call: `POST /api/session/{sid}/state {question_id, ms: 90000}` for several questions. | R7 |
| 6990 | `9. POST /api/mock/new {like: <finished mock>} returns a module 1 whose sorted template keys equal the source's module-1 keys, and every seed differs.` | Replace: `9. POST /api/mock/new {kind:'twin', twin_of: <finished mock>}; after finishing it, GET /api/session/{new}/compare has paired == 44 (22 when routes differ), each slot's template equal to its source slot's, and every seed different.` | SR7 |
| 6997 | `13. For a mock with at least one easy miss, whatif.tier == 'easy' and whatif.estimate.high >= estimate.high.` | Replace: `13. For a mock with at least one easy miss, POST whatif with the easy misses returns high >= estimate.high, and ledger.by_tier sums to ledger.total within 1.` | SR1, SR2 |
| 7029 | `25. Challenge: after two learners sit a day's challenge and the day has passed, results.review[i].crowd.n == 2 and crowd.options sums to about 100. …` | Replace: `25. Challenge: after two learners sit a day's challenge, results.review[i].crowd comes from S8's daily review for that slot, has no letter-keyed shares, and its norm shares sum to at most 100. The player shows “x% of 2 got slot n right”.` Add: `28. Every acceptance check in spec/v2-upgrades/reports.md SR1–SR25.` | SR12 |
| 7037 | `- Total score: we are Math only. Should the hero show only the Math 200–800 gauge (the default here), or accept a self-reported R&W score …` | Resolved: `accept the R&W score the student enters (R15 rw_now) or an outside score, and show the total with its provenance (SR4).` | SR4 |
| 7038 | `- National percentile: College Board publishes user percentiles for Math section scores. Should we add that table …` | Resolved: `add it, transcribed with its source and year (SR5).` | SR5 |
| 7039 | `- Colour semantics: …` | Resolved by R20. | R20 |
| 7040 | `- Share by link: reports stay readable by anyone with the sitting id …` | Kept as the default, with SR3's held-back set applied to every viewer while a second look is offered. The sample report (SR24) is the public example, left out of every figure across students. | SR24, SR3 |
| 7041 | `- Report screenshots: store up to 3 images per report on disk …` | Resolved by R17 (up to 10 images on disk). | R17 |
| 7042 | `- Share-progress link for a tutor or parent: build it with this section (the default), or defer it to Me?` | Resolved by R18(a) (S1's progress link). | R18 |

### 3.2 Outside the section (Part 2 and sibling lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| R7 | `qstate` adds per qid `second {answer, correct, conf, ms, at}` and `seen_key`, and `_session.second {state, at}`, `_session.visits [[qid, t_in, t_out]]` (≤ 400) and `_session.away_log [[qid, ms]]` (≤ 50). After finish, only S6's `/second`, `/seen` and `/second/state` may write `qstate`; `/state` stays refused (409) | SR3, SR9, SR13 |
| R8 | Unchanged: second-look answers are exact re-attempts, so `progress.record` marks them `repeat = 1`. `attempts.source` gains `second` | SR3 |
| R9 | A right non-guess second look sets its trap's kind to `slip` | SR3 |
| R20, §2.3 | Adds the state **Removed from scoring**: paper, dotted `--ink` edge, glyph ⊖, "taken out of scoring by a key correction". ⊘ Voided stays for contests only | SR19, SR25 |
| R16 | `estimate.py` adds `mid`, `ledger` (Shapley buckets), `total` (with the total percentile and `rw_history`), `national`, `rescore_sitting`; `rescore(sid, right, wrong, drop)` extends T16's `rescore(sid, positions)`. Comparisons for the delta, the ghost band and the percentile use the same standard / non-standard status. The in-site percentile and histogram leave out `sample:` learners. `route_rule` is served per subject | SR1, SR2, SR4, SR5, SR18, SR19, SR24 |
| R17, shell-me U3 | An upheld correction (`broken`, "Key was wrong", `remarked`) calls `estimate.rescore_sitting` for every finished sitting holding the question; U3's reply adds "Your report re-scored n sittings". The instant check marks the question `seen_key` | SR19 |
| R21, R23 | `UI.review` modes `second` and `pair`; review-mode re-answers are Second look (they file a repeat) | SR3, SR7 |
| R24 | Unchanged: Prove it is a Tests custom test, listed as a sitting; `learn` and `twin` from the player stay inline | SR6, SR16 |
| §2.5 | No new tables or columns. `server/data/cb_percentiles.json` is a checked-in data file (F4) with `math`, `rw` and `total` tables. `db.NOT_SAMPLE` (`learner NOT LIKE 'sample:%'`) is the one fragment every cross-learner query adds, and writes by a `sample:` code are refused (403). `sessions.result` gains `odds {qid: E}` at finish (JSON, not a column) | SR5, SR12, SR24 |
| §2.6 | `order` adds `given` (keep `only`'s order). `source` adds `fix` | SR2 |
| §2.7 | Key `second_look` (bool, default true). `confidence` (P7's key) is also the test default the Judgement toggle writes | SR3, SR9 |
| §2.8 | Page scope `report`: `1`–`9` jump, `N` first miss, `F` Fix menu, `W` What if, `P` repair pack, `?` sheet. Page scope `results`: `J`, `K`, Space, Enter, `F`, `X`. Player: `H` in Second look shows the answer without filing | SR2, SR3, SR14, SR20, SR23 |
| §2.9 | Providers: F4 `estimate.ledger / mid / rescore / total / national / rescore_sitting`, `progress.recovery`, `progress.causes(per_q)`, `progress.calibration`, `scoring.grid_diagnose`, `ratings.odds` → S6, S3, S5, S10, F6; F1 `UI.stackBar`, `UI.clockLane`, `UI.dotStrip`, `UI.qlabel`, gauge layers → S6, S3, S5, S1; S5 visits, away_log, `?fresh=1`, the lobby briefing → S6; S8 daily review per slot and contest result fields → S6; S10 worksheet `session` + `qids` → S6 (serialized through S6's `hold_back`); S7 task `start` → S6, S3 | all |
| today.md T7 | `progress.causes` takes a student-set `attempts.miss_kind` over its rule (fell for it → trap; misread, slip, rushed → slip; didn't know → gap; ran long → clock), reads `qstate.second` (a right non-guess look is a slip; a wrong one never is), returns `per_q` when `session` is given, and uses `scoring.grid_diagnose` for entry | SR8, SR10 |
| today.md T16 | The card's worth line reads `estimate.ledger`; the twin's line reads `GET /api/session/{id}/compare`; the total reads `estimate.total`; the card adds SR6's ring and SR14's reviewed meter | SR1, SR4, SR6, SR7, SR14 |
| practice.md P8 | `POST /api/drill/{id}/why` and `POST /api/session/{sid}/why` are one handler (S6 serves both paths) | SR8 |
| practice.md P16 | `drill.levels()` also returns `median_ms_right` per (template, tier) for the crowd line, and leaves out `sample:` learners | SR12, SR13, SR24 |
| practice.md P1, T-bank | Steps become a launch requirement for every template `blueprint` can draw into a section or the diagnostic (not only the 50%-of-weight milestone). `tools/steps_coverage.py --section` exits non-zero below 100% of those templates. Any template without steps carries a `METHOD` string (3+ sentences, 40+ words: the idea, the method, the check for its common trap), which the audit enforces and the explanation card shows above the rationale | SR16 |
| practice.md P11 | `ratings.odds(learner, template, tier)` returns E; F4 snapshots it for every item into `sessions.result.odds` at finish, before the sitting's answers update the ratings. `ratings.py` updates and the startup backfill skip `sample:` learners | SR12, SR24 |
| practice.md S4 | S6 reads `tries` (session, qid) for a practice set's review items; the report's status set adds Mixed (R20) | SR25 |
| practice.md P18 | The rematch's `finish().slots` is built by S6's compare function, so the summary and the report agree | SR7 |
| shell-me U1 | The queue gains a row `Finish reviewing Section #7 · 6 left` for a test finished within 7 days with unreviewed misses (opens the player at the first) | SR14 |
| shell-me U3 | The instant check's `forms` outcome uses `scoring.grid_diagnose` | SR10 |
| Tests §3.4 (S5) | `{kind:'twin'}` stores `cfg.slot_of`; the runner sends visits and away_log; the finish redirect adds `?fresh=1` and prefetches results; the lobby shows `GET /api/session/{last}/briefing`; a custom test from misses shows "Proved n of m" on its report | SR3, SR6, SR7, SR9, SR13, SR16, SR17 |
| Plan §3.6 (S7) | `POST /api/plan/{id}/tasks` accepts an optional `start` (a §2.6 drill body or a `/api/mock/new` body); the task row's primary launches it | SR2, SR6, SR14 |
| Review §3.10 (S10) | `GET /api/review/worksheet` accepts `session` and `qids` (misses of one finished sitting; 409 for a live test), for any viewer who can read that report; seeds are remembered as seen for the sitting's owner | SR20 |
| Compete §3.7 (S8) | The daily review function is callable from S6 for one slot, returning the field's rate and norm shares. S6 reads `sessions.result`'s `points`, `points_parts`, `right`, `wrong`, `skipped` and `voided` for the contest hero and tiles, and a private contest's rank among its players (a private contest is Compete's invite code or link, decision 5). Boards, seasons, Climb and the daily review field leave out `sample:` learners | SR12, SR25, SR24 |
| S3 (outside scores) | `add_outside_score()` accepts an R&W-only row (`math` null) from the report's inline field; R16 reads only rows with `math` | SR4 |
| F1 | `UI.qlabel(item, sitting)` prints `M1 Q7` or `Math M1 Q7` from the canonical address; `UI.sittingCard` groups chips by (subject, module); `UI.bandChart` adds the hatched R&W lane | SR16, SR23, SR21, decision 3 |

---

## 4. Rejected

* **A four-screen guided debrief stepper on first open** (outcomes #4): it puts the report
  behind screens, against decision 4. The takeaways, the second-look banner and the new order
  (SR14, SR3) give the sequence with nothing hidden.
* **Decoy right answers in the second look, with a neutral grid while it is pending** (outcomes
  #1): it hides statuses the student has already earned and needs a whole locked page state.
  The Guess chip keeps chance rights out of "slip".
* **A `deps.access` "kept" lock on the owner's own keys** (outcomes #1): a second rule inside
  R19 for one feature. The results payload simply leaves unseen keys out while the offer stands.
* **Second look on every first open of any miss** (experience #2 as written): it would force
  itself on students who skipped it. It is offered once per sitting, and Hide answers covers
  the rest.
* **The first pick shown struck and unpickable in the second look** (unfair-advantage #3):
  picking the same wrong answer again is the clearest "trap you believe" signal. The pick is
  hidden behind a toggle instead.
* **Drill `order:'interleave'` and a `redo` pool limited to one sitting** (outcomes #3): Mixed
  order and `from_session` already do both.
* **A stored `traps.points` column** (outcomes #3, #11): points come from the ledger on read, so
  there is no copy to drift.
* **Recovery steps that slide automatically and fold into Review after 14 days, created as plan
  tasks without asking** (outcomes #3): R9's check-ins and Review's Redo already carry
  unfinished work; Put in my plan adds a step only when the student asks.
* **A separate four-rung ladder with a stored rung per trap ("Rung 2 of 3")** (outcomes #5):
  T4's and P2's Learn it ladder exists; the player offers it (SR16).
* **Hints cut from the rationale's first clause** (outcomes #5): the cut is often nonsense or
  gives the answer away (today.md rejected the same). The worked example is the hint.
* **An extra day-10 check-in for sure-and-wrong misses** (outcomes #6): R9 already checks at 3,
  10 and 30 days.
* **An unsure-rate-per-skill panel on Results** (outcomes #6): P7's SkillPanel "Sure-accuracy"
  covers it.
* **A skip-and-return what-if assuming 60% success on freed questions** (outcomes #7): an
  invented model. SR13 states the time freed and the blanks' worth "if right".
* **A new fluency map chart on Results** (outcomes #7): U7's quadrant card shows the same data
  and is reused.
* **`families.json` with 12 new families and an 880-label manual pass** (outcomes #9): U6's 11
  regex families already tag every reason.
* **The rule shown above the next twin's stem on rung 2 only** (outcomes #10): P20's type notes
  already show wherever the type comes back.
* **A weekly goal ring, "Close 5 this week"** (outcomes #11): U14's week goals hold outcome
  goals.
* **Personal records (fastest median, longest clean run, most traps closed in a day)** (outcomes
  #11): novelty; today.md rejected personal-best lines.
* **"Most students at your level get this"** from a band-overlap cohort (outcomes #2): that
  cohort won't reach 20 for years. SR12's Should-have-had uses the student's own odds (P11),
  which exist from the first answer.
* **A per-template fix-cost table** (median clean answers to close × time, outcomes #2): a
  second model on thin data. Minutes come from P16's budgets.
* **An improvement percentile and a cohort path** ("students who started near 520 and reached
  700 closed about 34 mistakes", OG1): U11's Climb covers the first; the second needs a cohort
  we don't have and implies causation.
* **A practice-only estimate shown before any test** (OG9): shell-me and today.md rejected
  showing U4's S as a score. T10's practice delta shows the movement (SR21).
* **Leaving a disputed item out of the score while the dispute is open** (OG11): it invites
  disputing every miss. Only upheld corrections re-score (SR19).
* **Ranking retakes against other students' same retake number** (EG2): n is smaller still, and
  the pill already says why retakes aren't ranked.
* **A per-skill percentile** ("On Linear inequalities you beat 78%", AG3): it gives no action,
  and n per skill stays under 20 for a long time.
* **A value model of points × personal fix rate ÷ minutes** (unfair-advantage #4): a second
  model. SR2 ranks by exact points on this test per budget minute.
* **A third question-type coverage map on /results/** (unfair-advantage #10): U8's atlas and
  P14's type map exist; Results links to them from a tile (SR22).
* **Template version tags, regenerating every stored (template, seed) when a template changes,
  and renaming old grid-in misses** (unfair-advantage #11): heavy machinery for rare events.
  SR19 re-scores from U3's upheld corrections, which is the part a student sees.
* **Its own cause chip list** (Careless · Misread · Didn't know · Ran out of time · Calculator ·
  Other, experience #4): one vocabulary. P8's chips map onto T7's five causes (SR8).
* **`C` then 1–6 for the cause** (experience #4): C picks option C in the second look. The chip
  is one Tab away.
* **A separate `GET /api/report/check` before Send** (experience #9): U3 runs the check inside
  `POST /api/report`.
* **A "Quick check · 8 questions" empty-state test** (EG13): the diagnostic and U5's Sharpen
  already make a small real report.
* **"Retake in 7 days" as the recovery plan's last step** (outcomes #8): Prove it (a custom
  test from the misses) is that step; a full twin after 7 days is Today's plan-test-day default
  (T16).
* **"Gains past the cap read 0" as a separate `route_gap` rule** (unfair-advantage #1): the
  ledger's capped midpoint already reports it, with `capped: true`.
* **A split primary "Prove it · 13" beside Fix** (unfair-advantage #2): one primary per region.
  Prove it is step 4 of the recovery strip and has its own button there.
* **Drag-lasso selection in the grid** (EG5): Shift / Ctrl-click and long-press cover it, and a
  lasso fights scrolling on touch.
* **A "Fastest full section" milestone** (experience #11): it rewards rushing.
* **`R` for the first miss and `F` to start Fix at once** (experience #3): R is Report in the
  player, and a set shouldn't start from one stray key. `N` opens the first miss; `F` opens the
  Fix menu.
* **"What you did / What works" built from the rationale's first sentence** (EG7): P1's step
  compare does this properly where steps exist, and a cut sentence would often mislead.
* **A single national percentile number** (AG3 as written): our band is an estimate, so SR5
  shows the range the band spans.
