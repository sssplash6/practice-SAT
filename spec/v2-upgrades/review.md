# v2 upgrades: Review (redo, marked, saved, history, fixed)

Written 2026-09-23 for `spec/rebuild-v2.md` §3.9 (lines 10030–10969). It merges the three
designers' proposals in `spec/v2-upgrades/_proposals/review.json` (outcomes, experience,
unfair advantage; cited as "outcomes #1" and so on, and "… gap" for their parity gaps) into one
build-ready list, V1–V19. The TopTierPrep inventory is §3.9.1, checked against
`spec/toptierprep-teardown.md`, `ttp-notes.md` and the live walk in `ttp-live.md`.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.9 where
  they differ, and §3 lists every change. Part 2 resolutions (R1–R38) still hold, except the
  lines named in §3.2 "Outside the section".
* **Siblings.** `shell-me.md` (U1–U28), `today.md` (T1–T20), `practice.md` (P1–P25) and
  `plan.md` (L1–L20) are already written. Where they specify something Review shows, the
  upgrade here names it and does not specify it again. Where a proposal would build a second
  version of a sibling's model, this file uses the sibling's:
  * spaced returns: T3's `progress.warmup_candidates` and R9's check-ins (3, 10, 30 days);
  * the cause of a miss: T7's `progress.causes` with P8's `attempts.miss_kind`;
  * confidence: P7's `attempts.conf` (the split Check) and T9's inferred "sure";
  * points: U4's `estimate.gains` and U1's `redo` formula (`gain(t) × share`);
  * habits and the gauntlet: U6's 11 families (`server/habits.py`) and P6's `attempts.offered`;
  * time: P16's per-question budgets (65 / 95 / 126 s, or the crowd median) and fluency;
  * Learn it: T4's session and P2's ladder; twins on any axis: P18; rematch: P19;
  * type rules: P21's `notes` row with `seed = −1`; the trap sheet: L19's, built here once;
  * twins for shared sets: P22 and U28.
* **Closing rule unchanged.** A mistake still closes on 2 clean answers (1 for Unsure), as R8
  and R9 say. `practice.md` rejected "two different days" for the same reason this file does
  (§4): R9's 3-day check-in is the delayed proof. What changes is that the Fixed tab now says
  which fixes have held a check-in and which have not been tested yet (V10).
* **The bar.** A student who uses TopTierPrep today opens Review and wants to switch, because
  every miss is named, ordered by what it costs, brought back on new numbers until it holds, and
  the whole daily job fits in ten minutes and then ends. Parity is failure.
* **Names.** Upgrades are V1–V19. Builders are Part 4's tasks (F1–F6, S1–S10, T-bank). S10 owns
  `web/review/**`, `web/mistakes/**`, `server/api_review.py`, `server/checks/s10.py` and the new
  `server/review.py` (pure functions other modules read through `deps.part('review', …)`).
* **Subject-aware.** Per v2-decisions item 3, every new payload about a section's mistakes (due,
  counts, calibration, ledger, trap sheet) carries `subject` (`math` now) and filters on it, so
  Reading & Writing mistakes are additive: a second subject adds rows, not a second hub. The
  filter bar gains a Subject chip (their All / R&W / Math) only once a second subject exists.
* **Copy.** Functional labels only: a number carries its unit, a rule states itself once, a
  control never narrates what it does (the standing "never overexplain" rule). Decision 4 still
  holds: nothing useful is cut to save space.
* **Facts measured for this file** (current bank and dev db, 2026-09-23):
  * 349 templates make multiple choice. Over 24 seeds each they offer 3,152 distinct (template,
    misconception) pairs. **2,794 of them (88.6%) turn up again within the first 40 reserved
    example seeds** (900000+, never served in practice), after a median of 3 seeds and at most
    20 for 90% of them. So a worked example that carries the student's own trap is cheap (V11,
    V19).
  * Of 7,429 surveyed MC items, 7,352 (99.0%) carry 3 named wrong options, 66 carry 2 and 11
    carry 1. So "What happened?" can almost always offer three real misconceptions (V2).
  * The dev db has 131 traps. All 10 closed ones have `closed` equal to `opened` to the second
    (seeded data, but nothing in the rule stops a same-minute close). That is why V10 separates
    "held a check-in" from "not checked yet".
  * 287 attempts, 166 with `ms`. 5 of the 123 timed wrong answers came in under 25 s.
  * 59 of 386 templates make more than one tier; P18's siblings raise the types that can go
    easier or harder to 156 (practice.md's survey).

---

## 1. Scorecard

"v2 spec" is §3.9 as written, read with the resolutions. The verdict says why ours is way
better. Where v2 was only at parity (or below), the verdict names the upgrade that fixes it.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Redo List filter (QBank builder) | A select, All / Redo only. `toggleRedo` exists in the API, but no screen calls it, so the list is always empty and Profile reads "Redo Questions 0". No page lists redo questions | A Review hub whose Redo tab lists every open mistake by its named misconception, with pips, a pane, fresh versions at the missed tier and `Redo all · 22` | A finite **Due today** list (check-ins, relapses, sure-and-wrong misses, half-fixed, saved, marked, then the costliest), capped to the student's day, started with **Start review · 10 min** and ending in "Done for today" (V1). Every row priced in points (V4) | **WAY BETTER already** (theirs is empty). V1 turns a 25-row backlog into a daily ten-minute job that ends. |
| 2 | Marked for Review filter = their saved list | All / Saved only: marking a QBank question is saving it (`toggleSaved`) | Two things (R5): Marked (a flag per sitting) and Saved (kept for good), each a tab | Marked opens with **Your instincts**: sure-and-wrong, lucky guesses, answer changes and what flags caught, across every sitting (V5). Saved becomes a spaced deck on new numbers (V3) | v2 PARITY: two lists instead of one. **V5 + V3 → WAY BETTER.** A flag says what it was worth; a save comes back until it is learned. |
| 3 | Solved filter | All / Solved only / Unsolved only. The finite bank runs out of Unsolved; Solved only replays the same items | History selection → Fresh versions or Again, exactly, from any mode; never runs out | Sittings rematch on new numbers with Then vs Now (V13, P19); slow-right types get a speed set (V12) | **WAY BETTER already.** V13 makes the replay measure the skill, not memory of the item. |
| 4 | Question Score 1–7 | A dual-thumb slider in the builder; never shown in Details | Review filters Easy / Medium / Hard only; Level `As missed · Any · Harder` by tier | A Level chip L1–L7 from P11's ratings (`rough` until 20 answers), `▃ Medium · L4` on every row and in the pane; Harder steps to P18's sibling when the type has one tier (V15) | v2 BELOW. **V15 → WAY BETTER.** A level that moves with every answer and says how sure it is, in every list. |
| 5 | Mark for Review in a QBank session | A bookmark that fills blue; yellow cell in the Overview; the same as saving | A flag per sitting; a flagged answer is not clean; flagged and right opens an Unsure mistake | A mark comes back as a twin two days later (P12); each flag's history in Marked (V5) | **WAY BETTER already.** A flag changes what counts; theirs is a bookmark. |
| 6 | Mark for Review in the exam runner | "Unmark" in yellow, a red For Review flag in the navigator, a FOR REVIEW card on Check Your Work | Flags on the server per sitting; they survive a reload and module 2 | Each flag's history: flagged at 0:40, came back 1×, changed C → A, never came back. Check Your Work adds "1 not revisited" (V5, S5 hook) and P20's clock line | v2 PARITY (it fixes our own bug). **V5 → WAY BETTER.** |
| 7 | Flagged in the score report | All / R&W / Math / Flagged (n), orange corner dot, a "Flagged for review" chip | All · Wrong · Blank · Flagged (n), a corner flag, a legend entry | Over the grid: "Your flags caught 2 of your 7 misses". Across sittings: flag hit rate per topic, with advice (V5) | v2 PARITY. **V5 → WAY BETTER.** It says whether flagging is working for this student. |
| 8 | Attempt History modal | One question in one session: `#1 ⊗ Incorrect · Option A · 00:22 · Sep 23, 11:35 AM`. "No attempts yet." | The whole question type, every source, with misconception, flag, time and Open, plus integrity rules | P9's trend head, plus a verdict chip (Fluent · Right but slow · Same trap twice · Getting faster) with one next step, and a "This mistake only" filter (V8) | **WAY BETTER already.** V8 tells the student what to do next. |
| 9 | Unlimited retries, key hidden after a miss | Retry until right or open the explanation; accuracy means little | First try counts; the key and every option's misconception at once; the repair on new numbers | Test misses get **Review my misses**: try it again blind, name the mistake, see it, prove it on a twin (V2) | **WAY BETTER already.** V2 is the tutor's post-test routine, built in. |
| 10 | Mixed status and the Question Overview | Mixed = wrong then right on the same item; Status · Difficulty views; ignores Esc | Repaired = right on a fresh repair; glyphs; legend always visible; Status · Difficulty | P20's Confidence, Traps and Time views; every repair a node in the mistake's story (V8) | **WAY BETTER already.** |
| 11 | Per-question stopwatch | Counts up; a reload resets it; never analysed | Dwell time in tests too; History median, time column, Slowest sort | Time against each question's own budget everywhere; **Slow right** and **Rushed** filters; a Pace block with a Fluency sprint (V12, P16) | v2 PARITY in Review (stored and sorted). **V12 → WAY BETTER.** Right-but-slow becomes something to fix. |
| 12 | Details popover | ID, domain, skill, difficulty; closes on an outside click only | Skill, difficulty, format, source and date inline; Details keeps the address and Copy link; Esc | Adds `L4 · rough`, time against budget and points at stake to the inline meta (V15, V12, V4) | **WAY BETTER already.** |
| 13 | Saved Content card on Profile | Counts only: Saved Words / Redo Questions / Saved Questions | Me: `Open mistakes 25 · Marked 3 · Saved 14 · Fixed 40 · Answers 312`, each linking to its tab (plus shell-me's saved words and marked) | `12 due today · Start review`, `25 open ▼3 this week` with a 12-week sparkline, `Saved 14 · 4 due` (V1, V9, V3; S1 hook) | v2 PARITY. **V1 + V9 → WAY BETTER.** Each count has its direction and its next action. |
| 14 | Review modal in the report | Hide answers persists across Next; Report; "1 of 49"; ←/→; no re-answer; no skill, difficulty or time | `UI.review` (R23) with per-option misconceptions, re-answerable Hide answers, Save, Mark, History, Share, Fresh one | **Review these 6 misses** starts the walk (V2); See one solved (V11); your path through the question (V8) | **WAY BETTER already.** |
| 15 | Explanation depth | "Justification:" prose plus "Distractor Analysis:", one line per wrong option | A one-sentence rationale (median 21 words) plus every option's misconception | P1's steps on this question's numbers, with the step where the pick left the path; **See one solved**: a worked twin on new numbers with the student's own trap outlined (V11) | v2 BELOW in depth. **P1 + V11 → WAY BETTER.** Prose can't show which step went wrong, or an unseen example with the same trap. |
| 16 | Moving through the review | ←/→ keys and "1 of 49" | ←/→ and J/K, `3 of 25`, a phone dialog | A result strip to jump, `N` next wrong, `U` next not yet seen, seen marks, prefetch, swipe, long-press to select, and the numbers visibly changing on "Fresh one" (V14) | v2 PARITY. **V14 → WAY BETTER.** |
| 17 | Wrong-number chips on the Results list | Red chips per module ("2 3 4 5 6 7 +19"), not clickable | History sitting headers with actions, no per-question chips | Clickable result cells per sitting, each opening its question in the pane; **Walk these misses** (V13, V2) | v2 BELOW for scanning. **V13 → WAY BETTER.** |
| 18 | Shared session | Share → `/question-bank/shared/:id`, "Start Practice"; `navigator.share` froze the page | A sets link (R18), Start exactly or fresh, the clipboard with a fallback field | **Ask for help** sends the question with the pick, the named mistake, the note and the type's record; twins keep the sharer's trap on offer (V17, P22) | v2 PARITY (the working version). **V17 → WAY BETTER.** |
| 19 | Clear Session | Deletes the session's answers, notes and attempts to redo it | Again, exactly: a retake that deletes nothing | **Rematch** leads: the same types on new numbers, Then vs Now, retakes nested under the original; Again, exactly is kept as "tests memory" (V13, P19) | v2 PARITY. **V13 → WAY BETTER.** |
| 20 | Eliminations and annotations kept on the server | Per session, never shown in review | Kept (R6, R7); the pane shows only the pick and the key | **Your path**: struck options drawn struck, "You crossed out the right answer", answer changes with times, time against budget, confidence, highlights (V8) | v2 PARITY. **V8 → WAY BETTER.** |
| 21 | My Words: Saved Words + Due Today | Two cards, spaced repetition for vocab only | Saved is a bookmark list; only fixed mistakes are spaced | Saved · Due today · Learned, on fresh numbers at 1, 3, 7 and 21 days (V3) | v2 PARITY. **V3 → WAY BETTER.** Their best pattern, applied to math, never showing a seen key. |
| 22 | Report from the review | A Report button | Report a problem (R17) | **Not what I did?** corrects the cause in one tap; **The label is wrong** files a label report, and the admin sees dispute rates per label (V6) | v2 PARITY. **V6 → WAY BETTER.** Every student's correction improves the bank. |
| 23 | Share / Export Report | A dead button | History CSV | A Mistakes block in the parent/tutor progress link; a printable error log and trap sheet (V17, V19) | v2 PARITY. **V17 + V19 → WAY BETTER.** |
| 24 | Reviewing mistakes at all | No review-mistakes flow, no session summary, no list of sessions (weakness #1) | The hub, the pane, the Sitting view | The walk (V2) and the daily queue (V1) | **WAY BETTER.** |
| 25 | Empty states | "No attempts yet."; "No saved words match these filters" | A line per tab, and a three-line panel for a new student | A live example row made from a real item, and **Try one now**, whose miss becomes the first real row (V16) | v2 PARITY. **V16 → WAY BETTER.** The page shows itself instead of describing itself. |
| 26 | Volume and Timed on every source | Volume 10 … All and Timed/Untimed apply to Redo, Marked and Solved | Only Redo's action bar has Level and Timed | Volume, Clock and Feedback on every tab's action bar, echoed in its summary (V15) | v2 BELOW. **V15 → WAY BETTER.** |

---

## 2. Accepted upgrades

Grouped by how directly they move the score. Each gives why, screens and components, controls
and states, data and endpoints, how it uses the rest of the site, and acceptance checks.
Learner codes in the checks start `a:v2revreview`; `:PORT` is S10's 8030. Server checks go in
`server/checks/s10.py`.

### Layout after these upgrades

**Desktop (≥ 1080 px)**, `max-width: var(--max)`:
```
header      H1 Review · rule line                    [5 · 10 · 20 · All] [Start review · 10 min ▾]
walk card   6 new misses from Section · Sep 21 · about 9 min        [Review them]   (when new > 0)
stat strip  DUE TODAY · OPEN · AT STAKE · MARKED · SAVED · FIXED          (6 tiles, one row)
tabs        Due 12 · Redo 25 · Marked 3 · Saved 14 · History 312 · Fixed 40
filter bar  Topic · Difficulty · Level · Format · Kind · Cause · Confidence · Habit · … · Sort · Search
body        list (minmax(0,1fr))                     | pane 460px, sticky
action bar  summary · options · primary                                 (sticky bottom)
```
Tab heads (above each list): Due → today's card and forecast (V1); Redo → Why you lose points
bar (V6), habits strip (V7), Worth the most strip (V4); Marked → Your instincts (V5); Saved →
`Questions · Your rules` and the deck cards (V3, V19); History → summary card, Pace block (V12);
Fixed → the ledger (V9) and the held line (V10).

**Phone (390 px)**: header with the full-width pill and its duration seg above it; the walk
card; tiles in a 2 × 3 grid; six tab segments sticky under the top bar; the list; the pane as a
full-screen dialog; the action bar above the tab bar (v2 §11).

**Calls.** `GET /api/review/counts` paints the tiles and tab counts. The open tab's list
endpoint and its head's endpoint run in parallel; a head's failure shows its own Retry and
leaves the list alone (§2.1 rule 8).

---

### A. The daily loop

#### V1. Due today: one finite list, and Start review · 10 min as the page's main button

*From: outcomes #1, experience #1, the outcomes "Redo all as a one-sitting backlog" gap, the
stat-strip gaps of all three. Effort M. Builders: S10 (`review.due`, `review.resolve_drill`, the
Due tab, the header), F5 (source `due` through the §2.6 registry), F2 (the nav badge), S3
(Today's card uses the same pill), S4 (the summary for source `due`).*

**Why.** Spaced retrieval on new numbers, mixed across topics, is the most reliable gain in
learning research, and a finite daily goal is what keeps a habit going. A 25-row backlog is
neither: students clear it in one sitting now and then, or never. Theirs has a Due Today list
for vocab words only, and their math redo list is always empty. v2's `Redo all · 22 questions ·
about 35 min` is their Redo filter made to work, still a backlog.

**What is due** (`review.due(learner, tz, subject='math')`, S10, pure over the rows; one item
per template, first reason wins), in this order:
1. **Check-in** — a fixed trap whose R9 `due` is today or earlier, most overdue first.
2. **Relapsed** — an open trap with `relapses ≥ 1` whose latest miss came after its last fix.
3. **Sure and wrong** — an open trap whose latest miss was sure (P7's `conf = 'sure'`, else
   T9's inferred rule). V5 calls these blind spots.
4. **Half fixed** — an open trap owed 1.
5. **Saved** — a saved question due by V3's schedule.
6. **Marked** — P12's `marked` candidate (flagged 2+ days ago, no right first try since).
7. **Mistake** — any other open trap whose last attempt on its template was on an earlier local
   day, by U1's `redo` points, then hits.

**The cap.** `cap = clamp(round(0.4 × minutes_per_day × 60 / 95), 6, 30)`, where
`minutes_per_day` is `learners.minutes` (R15), else 30 (so 8 by default). The first `cap` items
are today's list. The rest are shown as `14 more wait for later days` and are never counted as
debt. An item is **done** for today when its template (for a flag, the flagged template) gets
any first-try answer today. Items not done roll to the top of tomorrow, since they stay due.

**The Due tab** (first tab, the default when `left > 0`; otherwise Redo).
* **Today's card** at the top:
  * a ring `0 / 12` (done / today's list), and kind chips with counts:
    `3 check-ins · 1 relapsed · 2 sure and wrong · 2 half fixed · 2 saved · 1 marked · 1 mistake`;
  * `about 16 min` (U1's rule: count × the learner's median seconds over 60 days, 95 by
    default);
  * a 7-day forecast strip (`UI.barChart`, one bar a day, today ringed): check-ins from T3's
    `progress.due_forecast` plus saved items from V3, the only kinds whose dates are fixed;
  * `14 more wait for later days` (DM Mono, `--soft`) when the cap cut the list.
* **The list**: one row per item, 56 px, in the order above. Each row: the kind chip (the
  §2.3 glyph plus text: `Check-in ✓`, `Relapsed`, `Sure ✕`, `Half fixed ●○`, `Saved`,
  `Marked`, `Mistake`), the label (Archivo 600 15), a DM Mono meta
  `skill · ▃ Medium · ≈ 6 pts`, the why line (`Fixed Sep 20 · checking it holds`,
  `You were sure · Sep 22`, `1 clean answer closes it`, `Saved Sep 20 · back after 3 days`),
  and an `×` button (`aria-label="Not today: <label>"`). Done rows move to the bottom with a ✓
  and a line-through on the why line. Clicking a row opens its question in the pane.
* **Not today** reuses U1's snooze: `localStorage satf.next.snooze {key: YYYY-MM-DD}` with the
  same key format, so a snooze in Up next or here hides the item in both on this device. The
  client drops snoozed keys from the ring and the count. `ponytail:` per device, like U1; move
  to the server if students ask for it to sync.

**The header pill** (replaces v2's `Redo all · 22 questions`).
* A `UI.seg` above it: `5 · 10 · 20 · All min`, default `prefs.review_minutes` (10). Changing it
  saves the pref.
* The split pill **Start review · 10 min** (`Shift+R` on this page). Its `▾` opens the preview
  sheet: `POST /api/drill/preview {source:'due', box:10}` returns T1's block shape, one row per
  template with its kind, label and `×` to drop it; `Start` at the bottom.
* The meta line under it: `3 check-ins · 2 quick wins · closes up to 5 mistakes`, where quick
  wins are half-fixed traps and "closes up to" counts the items whose one clean answer closes a
  mistake (open items owed 1).
* **All** is v2's Redo all: every open trap `max(owed)` times plus today's list, capped at 120,
  labelled `All · 22 questions · about 35 min`.
* Nothing due and nothing open: the pill reads **Keep going · 10 min** (the coach's set,
  `source:'quick'`). Due done but mistakes open: **Another 10 min** on the open ones by points.

**The session.** `POST /api/drill {source:'due', box: 10 | null}`, resolved by
`review.resolve_drill(learner, body)` through the §2.6 registry (like `like` and `word`).
* Segments in the list's order, one question per template (fresh seed at the tier of the latest
  miss; a check-in at the highest proven tier, V10), then, if time remains, other open traps by
  points, then P16's right-but-slow types. `order:'mixed'`: no two consecutive questions share a
  topic when two or more topics are in play.
* `cfg.hide_skill = true` (T3): the skill line reads `Mixed review` until Check, so the student
  has to recognise the method; the strip chip that says why an item was chosen (`From your
  Redo`, `Check-in`) shows only after answering.
* Instant feedback and `repairs:'next'` always (U15: fixing drills show the key after each
  answer). The box clock is U1's (`12:40 left of your 10`).
* It is an ordinary sitting (not inline), listed as "Review · 10 min" in Results, resumable.

**End screen** (S4's summary for `source:'due'`): `Due today 12 of 12 done · Closed 4 · half
fixed 2 · relapsed 1 · open 25 → 21 · ≈ +12 pts recovered` (V4), the primary **Another 10 min**
(the same body) and **Back to Review**.

**Done for today** (the Due tab and Today's card when `left == 0`): the ring full, `Done for
today · 9 of 12 right · 2 fixed · 7 due tomorrow`, and **Another 10 min** as a `.btn`.

**The badge.** The sidebar Review item, the phone top-bar chip and the menu-sheet footer cell
show **today's due left** (hidden at 0), not the open count: a number a student can clear. The
tooltip reads `12 due today · 25 open`. `/api/me.review` becomes `{open, due_left}` (§3.2).

**Stat strip** (six tiles, one row at ≥ 1080 px, 2 × 3 on a phone):

| label | number | sub line | opens |
|---|---|---|---|
| DUE TODAY | 12 | `3 check-ins · 6 mistakes · 2 saved · 1 marked`; a `Start` link | Due |
| OPEN | 25 | `▼3 this week · 7 half fixed · 4 sure and wrong · 1 relapsed`, a 12-week sparkline (V9) | Redo |
| AT STAKE | ≈ 45 pts | `Circles ≈ 15 · Linear functions ≈ 10` (V4); under 30 answers `after 30 answers` | Redo, sort worth |
| MARKED | 3 | `from 2 sittings · flags caught 24% of misses` (V5) | Marked |
| SAVED | 14 | `4 due · 3 learned · 4 with notes` (V3) | Saved |
| FIXED | 40 | `6 this week · 31 held a check-in` (V10) | Fixed |

**States.** Loading: the card skeleton (ring, chips, 6 rows) at final size. Error in the due
call: the card shows Retry; the tabs still work. New student: V16's panel. Storage blocked:
snoozes are not kept (no banner beyond the shell's).

**Data.**
* `GET /api/review/due` → `{subject, cap, left, done, total, waiting, minutes, items: [{key,
  kind, template, trap_id?, saved?: [template, seed], flag?: [session, qid], topic, label,
  skill, tier, why, pts, since, done}], forecast: [{day, checks, saved}]}`. `key` is
  `due:<kind>:<template>` (the snooze key).
* `/api/review/counts` adds `due_left`, `due_total`, `waiting`, `blind`, `new`, `stake_total`,
  `open_week_delta`, `held`, `unchecked`.
* `prefs.review_minutes`: 5 | 10 | 20 | 0 (0 = All), default 10 (§2.7, §3.2).

**Uses the rest of the site.** Today's `#mist` card (R30, T9) takes the same pill and the
`12 due today` line. Up next's `checks` row stays (U1); finishing either clears both, because
"due" is derived from attempts. The builder's "Questions from" gains **Today's review · 12 due**
(`source:'due'`, S4). Plan's Rechecks task keeps T3's warm-up body.

**Acceptance.**
1. A learner (`a:v2revreview1`) seeded with one trap fixed 4 days ago (R9 due), one relapsed
   trap, one open trap whose latest miss has `conf='sure'`, one trap owed 1, one saved question
   saved 2 days ago with no answer since, and 20 more open traps: `GET /api/review/due` has
   `items[0..4].kind == ['check','relapsed','sure','half','saved']`, `cap == 8`, and `waiting
   == total - 8`.
2. `POST /api/drill {source:'due', box:10}` → `GET /api/drill/{id}` has `cfg.hide_skill ==
   true` and `cfg.box == 10`; its first 5 served templates are those five items' templates, and
   no two consecutive served questions share a topic.
3. Answer the check-in item's question: a second `GET /api/review/due` shows it with `done ==
   true`, and `left` is one lower. `GET /api/me` has `review.due_left` equal to `left`.
4. With `learners.minutes = 60`: `cap == 15`. With 90: `cap == 23`. With nothing open and
   nothing due: `items == []`, and `/review/` at 1280 shows the pill "Keep going · 10 min".
5. Browser 1280: the `×` on a row hides it, and after a reload it stays hidden for that local
   day; `localStorage['satf.next.snooze']` holds its key.
6. Browser 390: six tab segments fit with `document.documentElement.scrollWidth === 390`, each
   segment at least 44 px tall; the Due tab is selected when `left > 0`.
7. `POST /api/drill/preview {source:'due', box:10, drop:['due:check:<t>']}` returns no block
   with that key, and its minutes stay within 10 ± 3.

#### V2. Review my misses: try it again, name the mistake, see it, prove it on new numbers

*From: unfair-advantage #1, outcomes #3, unfair-advantage #4 (the confirm), the experience
"Not what I did?" gap, the unfair-advantage wrong-number-chips gap. Effort M. Builders: S10 (the
walk page, the endpoints), F3 (`UI.review` mode `walk`), S6 (the report entry), S4 (the summary
entry), S3 (Today's line).*

**Why.** Test misses die unread in a report: TopTierPrep's report can't be re-answered, and
nothing makes the student work the mistake afterwards (their weakness #1). Diagnosing an error
before being told, then studying it, then solving a new one outperforms being shown the
correction (self-explanation, erroneous-example studies such as McLaren et al.). Naming the trap
is what lets a student catch it mid-solve on test day. Only we can offer the item's other real
misconceptions as the choices, and a fresh twin as the proof.

**The inbox.** A trap is **New** when its latest wrong attempt came from a sitting where no
feedback was shown (a section, module, diagnostic or custom test, or an end-mode set) and that
attempt's `diag` is null. New rows carry an ink dot and `New`. When any are New, a card sits at
the top of Due and Redo: `6 new misses from Section · Sep 21 · about 9 min` with the pill
**Review them**. Every entry point below opens the same walk:
* the report (S6): `Review these 6 misses · about 9 min` beside Fix these;
* an end-mode set's summary (S4);
* Today's `#mist` card (S3): `4 new misses from Sep 21's section · Review them`;
* each History sitting header: **Walk these misses** (V13);
* a Redo selection: **Walk these** in the action bar.

**The walk** (`/review/walk/?id=<drill id>`, `UI.review(host, items, {mode:'walk'})`, F3). A
rail at the top: `Mistake 3 of 6`, one result dot per mistake, **Back**, **Skip**. Enter moves to
the next step. Each mistake runs up to four steps:
1. **Try again** — only when the student has not seen this key (the New case). The exact
   question in Hide-answers mode, their earlier pick tagged `You picked C`. Check files through
   the walk drill; `progress.record` marks it a repeat, so it never counts. Skipped for misses
   whose key was already shown.
2. **What happened?** — up to six plain sentences, shuffled, no letters:
   * the misconceptions behind the item's wrong options (usually 3, measured);
   * `Misread the question` · `A slip: I knew how` · `Didn't know how to start`.
   Keys 1–6 choose. `POST /api/review/why {attempt_id, diag}` stores the choice. A general
   choice also sets P8's `miss_kind` (`misread`, `slip`, `gap`). A grid-in offers P4's named
   grid-in mistakes when the template has them, else the three general choices.
3. **The trap** — the reveal: the key, every option's misconception line, P1's steps with the
   step where the pick left the path, the rationale. A verdict line: `You called it`, or `Your
   pick came from: used 180° for a whole circle`. Under the `Your pick ·` line, a quiet **Not
   what I did?** (V6). Save, and **Write your rule** (V19) when the trap has 2+ hits.
4. **Prove it** — a fresh twin inline (`POST /api/drill/{id}/more {question_id, axis:'same'}`,
   P18) at the tier of the miss. A miss queues its repair (`Try the repair`); a clean answer
   fills a pip with the map bar's animation.

**End card.** `6 reviewed · you named 4 of 6 · 4 proven on new numbers · 2 still open · first
check-ins Sep 26`, then **Walk the 2 still open** and **Done**. The Redo head then reads `You
named your own mistake 11 of 17 times (65%)`.

**The pane agrees.** Opening a New item in the Review pane (not the walk) starts at step 2, with
a quiet **Just show me**, which files `diag = 'skip'` and reveals.

**Phone.** One step per full-screen sheet, with a sticky footer `‹ · primary · ›`.

**Controls and states.**
* Position survives a reload and another device: the walk drill's `cfg.walk {items, i, step}` is
  saved on each move (`POST /api/review/walk/{id}/at {i, step}`).
* A live-test item → 409 from `deps.access` (R19); the walk never includes one.
* A mistake that closed since (a clean answer elsewhere) shows `Fixed since` (§2.3) and skips
  to the next one.
* Empty (no misses in that sitting): `No misses in this sitting.` with the sitting's report link.

**Data.**
* `attempts.diag TEXT`: a norm, or `misread` · `slip` · `gap` · `skip` (§3.2, F4). "You called
  it" = `diag == attempts.norm`. The self-diagnosis rate is SQL over `diag not in ('skip')`.
* `POST /api/review/walk {session? | ids?: [trap id] | new?: true}` → `{id, n, minutes}`. It
  creates an inline drill (`source:'review'`, R24) whose `cfg.walk.items` are `[{attempt, trap,
  template, seed, try: bool}]`. Minutes = n × 1.5.
* `POST /api/review/walk/{id}/at {i, step}` → `{ok}` (owner only).
* `POST /api/review/why {attempt_id, diag?, kind?, guess?}` (owner only; the attempt must be
  wrong): sets `diag` once (a second `diag` is ignored, so the rate stays honest), `miss_kind`
  (P8's values) and `guess`. Returns `{called: bool, norm, label, cause}`.
* `GET /api/review/item` returns `new: bool` and, for a New item, `diag_choices: [{id, text}]`
  (norms and the three general ids, shuffled server-side with the attempt id as the seed).

**Acceptance.**
1. A learner finishes a module with 3 wrong MC answers: `GET /api/review/redo?lens=new` lists 3
   items with `new == true`, and `/api/review/counts.new == 3`.
2. `POST /api/review/walk {session: <that sid>}` → `n == 3`; `GET /api/drill/{id}` has
   `cfg.inline == true` and `cfg.walk.items[0].try == true`. `/api/history` does not list it.
3. `POST /api/review/why {attempt_id, diag: <that attempt's norm>}` → `called == true`; a second
   call with another `diag` leaves `attempts.diag` unchanged. The item is no longer New.
4. `POST /api/review/why {attempt_id, diag:'misread'}` on another attempt sets `miss_kind ==
   'misread'`, and `progress.causes` counts it under `misread`.
5. Browser 1280: the walk's step 2 shows between 3 and 6 choices and no letters; pressing `2`
   selects the second; Enter reveals the key. A reload returns to the same mistake and step.
6. The Try again answer files `attempts.repeat == 1`; the trap's `owed` is unchanged.

#### V3. Saved becomes a spaced deck on fresh numbers

*From: experience #6, the outcomes and experience saved gaps, shell-me U1 row 9. Effort M.
Builders: S10 (the schedule, the tab head), F5 (pool `saved` with `due`), S4 and F3 (the Save
toast chips, "Your note"), F2 (U1 row 9 reads it).*

**Why.** A bookmark drawer that never comes back is forgotten. TopTierPrep's My Words pairs
Saved with Due Today for vocab; their saved questions are a count on Profile. Spaced returns on
new numbers mean a due card never shows a key the student has already seen.

**The schedule** (`review.saved_due(learner, tz)`, derived from attempts, no new column, the way
T3 derives fading types). For each saved (template, seed):
* `k` = counted clean rights on the template since the later of the save and the last wrong
  answer on it, a counted right being at least 20 h after the previous counted one (T3's rule);
* next due = (the last counted right, else the later of the save or the last miss) + `[1, 3, 7,
  21][k]` days;
* `k ≥ 4` → **Learned**: still saved, never due, a ✓ on the row.
* A miss on the template resets `k` to 0 (due tomorrow) and opens or refreshes its trap as usual.
* `prefs.saved_spaced` (default true); off makes Saved a plain bookmark list, never due.

**The Saved tab head.** A seg `Questions 14 · Your rules 9` (Your rules is V19). Under
Questions, three filter cards like their My Words: `Saved 14`, `Due today 4`, `Learned 3`; the
selected card filters the list. The primary of the action bar becomes **Practise due · 4**:
`{pool:'saved', ids, exact:false, each:1}` (P21: the Saved pool gives twins by default). With nothing due, the primary is **Fresh versions**.

**Rows** add `due today` / `next Oct 2` / `Learned ✓` and `box 2 of 4` (4 small pips) to the
meta line. The Status filter for Saved: `Due · Not due · Learned`.

**Why you saved it** (optional). After Save, in the session and the pane, the 5 s toast that
v2 gives a `Note` link becomes: `Saved · Nice trick · Hard · Got lucky · Ask a tutor · Note`.
* `Got lucky` calls `POST /api/mistakes/add {template, seed}` (an Unsure owing 1, v2 §server).
* `Ask a tutor` opens V17's Ask for help sheet.
* `Nice trick` and `Hard` store `saved.why`; the Saved filter gains `Why`.
* Tapping nothing stores nothing.

**Your note comes back.** A fresh version served from the Saved pool shows, after the verdict,
`Your note on the saved one · Sep 20: check the sign of the slope` (the note is R6's, on the
saved seed). F5's feedback adds `saved_note` for items from pool `saved`.

**Up next.** U1 row 9 ("a question saved 7 or 21 days ago, ±1 day") reads `review.saved_due`
instead, so there is one saved schedule (§3.2).

**Acceptance.**
1. Save (t, s) on day 0: `saved_due` lists it on day 1 with `k == 0`. One clean right on a fresh
   t seed on day 1 → due on day 4. A second clean right 10 h later does not raise `k`.
2. Four counted clean rights on four days → the row is `learned: true` and never in `due`.
3. A wrong answer on t after `k == 2` → due tomorrow with `k == 0`, and a trap is open on t.
4. `POST /api/drill {pool:'saved', ids:[[t, s]], exact:false, each:1}` serves t with a seed
   other than s; after answering, the feedback has `saved_note` when a note exists.
5. `PUT /api/me {prefs:{saved_spaced:false}}` → `saved_due` returns `[]` and U1's queue has no
   `saved` row.
6. Browser: Save, then tap `Got lucky` in the toast → `/api/review/redo?kind=unsure` gains the
   item.

---

### B. What to fix first

#### V4. Points at stake on every mistake, group and header, and Worth most as the default order

*From: unfair-advantage #2, experience #3, outcomes #8, the outcomes most-missed gap, the
unfair-advantage Prev/Next gap. Effort S (the model is U4's and U1's). Builders: S10 (rows,
groups, tile, sorts), F4 (`trap_log.pts`).*

**Why.** With limited time, fixing first what the test asks most and what the student misses
most gives the most points per minute. A trap in Linear functions (about 4 questions a test)
costs more than one in Probability (about 1). v2's Most-missed strip ranks by hit count, which
favours whatever the student happened to practise most. Theirs has no order at all.

**One formula** (no second model: U4 is the source, U1 already prices a `redo` row).
* A trap's points: `gain(t) × share`, where `share` = this trap's wrong attempts ÷ all wrong
  first-try attempts in skill t over the last 60 days (U1). Rounded to whole points, hidden
  below 1, and all hidden while `estimate.gains` is null (under 30 answers).
* A group's points: the sum of its rows (never more than `gain(t)`, since shares add to at most 1).
* **AT STAKE** tile: the sum over open traps, `≈ 45 pts in open mistakes`, with the top two
  topics.

**Where it shows.**
* Row meta: `≈ 6 pts` (DM Mono 600) at the end of line 2.
* Group header: `≈ 20 pts · about 4 of 44 a test` (U4's `per_test`).
* Redo sort **Most points** (`sort=worth`), the default once `gains` exists; the pane's Prev /
  Next and `N` follow the current sort, so → always goes to the next most valuable mistake.
* The Most-missed strip becomes **Worth the most**: up to 5 chips (label cut to 40 characters and
  `≈ 6 pts`), then **Redo these 5 · about +18 pts**.
* Each figure is a button opening U13's popover: "Circles is worth about +20 if it reached 80%.
  This mistake is 3 of your 10 Circles misses in 60 days, so about 6."
* **Recovered.** When a trap closes as fixed, `trap_log` stores its points at that moment
  (V9's log). The Fixed tab reads `Recovered ≈ +30 pts this month`; V1's end screen and done
  state read `≈ +12 pts recovered` for the day.

**Acceptance.**
1. The U1 acceptance learner (`gains.skills.probability.gain == 20`, 10 wrong first tries in 60
   days, 3 on one open trap): `/api/review/redo` has that trap with `pts == 6`, and its group
   `pts >= 6`.
2. A learner with 12 answers: every `pts` is null, and the AT STAKE tile reads "after 30
   answers".
3. `sort=worth` returns items in non-increasing `pts`.
4. Closing a trap worth 6: `select pts from trap_log where event='fixed' order by id desc
   limit 1` is 6, and `/api/review/fixed.stats.recovered_month >= 6`.

#### V5. Blind spots and your instincts: what your flags, first answers and certainty are worth

*From: experience #2, unfair-advantage #5, outcomes #4, the flag gaps of all three, the
experience Marked-rows gap. Effort M. Builders: S10 (the panel, endpoint, chips), S5 (visit
counts in `qstate`, the Check Your Work line), S6 (the report line).*

**Why.** A miss the student was sure of is never re-checked on test day, so it is pure point
loss, and corrected high-confidence errors are the ones remembered best (hypercorrection).
Knowing, topic by topic, when to trust a first answer and when to flag and return is a test-day
skill. TopTierPrep counts flags and never relates them to results; their report overwrites
changed answers.

**Blind spots in Redo.** A trap whose latest miss was sure gets an ink `Sure ✕` chip. Sure is
P7's `attempts.conf = 'sure'`; with no tag, T9's rule (not a guess, and faster than 0.6 × the
learner's median for that tier), shown as `Sure ✕ (assumed)` in the tooltip. Redo gains the
sort **Blind spots first**, the lens chip `Blind spots · 4` in the filter bar, the pane header
line `You were sure`, and the action **Drill my blind spots** (`{pool:'redo', ids: blind,
level:'as_missed'}`).

**Your instincts** (a card at the top of Marked; a Since seg `30 days · 90 days · All`).
1. **Certainty** — a 3 × 2 grid, rows Sure · Unsure · Guess, columns Right · Wrong, each cell a
   count and a %, each a button opening History filtered (`?conf=sure&result=wrong`). Sure
   includes assumed ones, with `12 assumed` under the row. A footnote counts `untagged 40`.
   Headline: `Blind spots 14: sure and wrong` and `Lucky 5: unsure or guessed, but right`.
2. **Readings**, at most three, each only with 10+ answers in its bucket and topic:
   * sure-accuracy under 80% in a topic: `Linear functions: 5 sure but wrong. Check your work
     here before moving on.`;
   * unsure-accuracy 70% or more: `Circles: right 78% when you doubt yourself. Trust your first
     answer.`
3. **Answer changes** (tests), T7's `changes` over the Since range, split: `12 changes · 7 wrong
   → right · 3 right → wrong · 2 wrong → wrong · net +4 questions ≈ +50 pts` (net ×
   `estimate.per_question`, T8). The tip follows the sign: net > 0 `Your second looks pay:
   keep flagging and returning.`; net < 0 `Your first answer is usually better: change only for
   a new reason.`
4. **Flags** — `18 flagged · 11 came back · 7 never came back (4 of them wrong)`, and `Your
   flags caught 5 of your 21 test misses (24%)`, with the lowest topic: `Circles: flags caught
   1 of 6 misses. Flag more there.`

**Each flag's history** (Marked rows, test flags). The meta line adds `flagged at 0:40 · 2:10 on
it (budget 1:35) · came back 1× · changed C → A · right`, from `flags.at − sessions.started`,
`qstate[qid].ms`, `visits`, `first` and the final answer. A `Never came back` chip when `visits
== 1`. The group header adds `2 of 3 flags came back`.

**Elsewhere.**
* The report (S6), over the question grid: `Your flags caught 2 of your 7 misses`.
* Check Your Work in the test window (S5): P20's marked line reads `3 marked for review · 1 not
  revisited`.
* The MARKED tile's sub line: `flags caught 24% of misses`.

**Data.**
* `qstate[qid].visits` (int), incremented by the runner each time a question is shown (S5, R7
  amendment, §3.2).
* `GET /api/review/calibration?since=&until=` → `{subject, matrix: {sure: {right, wrong,
  assumed}, unsure: {right, wrong}, guess: {right, wrong}, untagged}, topics: [{topic, sure: {n,
  right}, unsure: {n, right}}], readings: [text], changes: {n, wr, rw, ww, net, pts}, flags: {n,
  revisited, never, never_wrong, caught, misses, by_topic: [{topic, caught, misses}]}}`, all SQL
  over attempts (`conf`, `guess`, `flagged`, `ms`), flags and `sessions.qstate`, leaving out
  repeats, disputed and voided rows (R8).
* `/api/review/redo` items gain `blind: bool`; the query takes `lens=blind` and `sort=blind`.

**Acceptance.**
1. Three wrong answers with `conf='sure'` and two right with `conf='unsure'`: `matrix.sure.wrong
   == 3`, `matrix.unsure.right == 2`, and each of the three traps has `blind == true`.
2. A wrong answer with `conf` null, `guess = 0` and `ms` under 0.6 × the tier median is counted
   in `matrix.sure.assumed` and flagged `blind`.
3. A test with 4 flags, 2 of them shown only once: `flags.never == 2`; `GET /api/review/marked`
   rows for those carry `visits == 1`.
4. `changes.net` equals `wr − rw` over tests in range, and `pts == round(net ×
   per_question / 5) × 5`.
5. Browser: clicking the Sure × Wrong cell lands on History with `conf=sure&result=wrong` in the
   URL and only wrong rows.

#### V6. Why you lose points: the cause of every miss, one bar, a fix per cause, and labels students can correct

*From: unfair-advantage #4, today.md T7, practice.md P8, the experience and unfair-advantage
Report gaps. Effort S. Builders: S10 (the bar, the row chips, `POST /api/review/why`), F6 (the
label-dispute view), F3 (the "Not what I did?" menu).*

**Why.** "Do more questions" fixes nothing for a misread or a slip. A careless student needs to
check, a slow one needs pace, a misconception needs fixing. Their 'Distractor Analysis' is prose,
and with unlimited retries they can't tell which pick came first, so they can't separate these.

**The bar** (Redo head, `WHY YOU LOSE POINTS · LAST 30 DAYS`). T7's `progress.causes(learner,
tz, days=30)`, which honours P8's `miss_kind`: one stacked bar `Traps 14 · Slips 4 · Misread 2
· Clock 3 · Entry 2 · Gaps 5`. The largest segment is orange, the rest ink shades, each with its
text label, and a hidden table. Each segment is a button that filters Redo to traps whose latest
miss has that cause (`cause=`), and shows its fix in a row under the bar, the fixes being P8's:
* Traps → **Fix now** (the filtered Redo) and **Spot the trap**;
* Slips → **Careful set · 8** and the helper `You know these. Reread the last line before
  Check.`;
* Misread → **Read the ask** (P8's underline, turned on for those skills);
* Clock → T8's speed drill and two passes (P16);
* Entry → the grid-in entry drill;
* Gaps → **Learn this type** (P2).

**Rows** show the cause as a chip when it isn't a trap (`Slip`, `Misread`, `Clock`, `Entry`,
`Gap`); the filter bar gains a **Cause** chip.

**Not what I did?** Under the pane's `Your pick ·` line, a quiet link opening a menu:
`I guessed` · `Misread the question` · `A slip: I knew how` · `Ran out of time` · `Didn't know
how to start` · `The label is wrong`. The first five call `POST /api/review/why {attempt_id,
kind | guess}` (V2), so the row's cause, the bar and V5's blind-spot state update at once. `The
label is wrong` opens `UI.report` (R17) with the category `Wrong mistake label` and (template,
seed, option) filled in.

**Label disputes.** `/admin/reports` (F6) gains a `Labels` view: per (template, norm), the
number of `Wrong mistake label` reports and of "Not what I did?" corrections, sorted by rate,
listing any label disputed by 15% or more of 20 or more learners. The bank owner fixes the
misconception once, and every student's mistake names improve.

**Acceptance.**
1. A learner with 2 misses corrected to `misread` and 3 traps: the bar's `misread == 2`, and
   `/api/review/redo?cause=misread` returns exactly those traps.
2. `POST /api/review/why {attempt_id, guess:true}` sets `attempts.guess == 1`; the trap is no
   longer `blind`.
3. `The label is wrong` creates a `reports` row with `category == 'Wrong mistake label'` and the
   attempt's template and seed.
4. Browser: clicking the Slips segment shows a row whose button body has `feedback:'instant'`
   and those templates.

#### V7. Habits, the gauntlet and the same trap elsewhere

*From: outcomes #7, experience #4, unfair-advantage #3, shell-me U6, today.md T9, practice.md
P6. Effort S (every model is a sibling's). Builders: S10 (grouping, the strip, chips).*

**Why.** One habit, such as "answered a different quantity than asked", costs points in every
domain. Fixing it once with one check that works everywhere beats working through 25 separate
labels. TopTierPrep names no misconceptions at all, so they can't even count one.

* **Group by: Habit.** Redo's Group by becomes `Topic · Domain · Habit · Mistake type · None`.
  Habit uses U6's 11 families (`habits.family(norm)`); Mistake type stays v2's exact-norm index
  (§14). Each habit group header: the name, the tell in italics, `9 misses in 6 topics`,
  `≈ 18 pts`, and **Drill this habit · 8** (U6's `source:'habit'`).
* **Habits strip** on the Redo head, when any habit spans 2 or more templates: T9's rows (top 3)
  with `avoided 2 of the last 5` or `Broken · Sep 30`, **Drill this habit · 8** and **Spot it ·
  3**, and U6's **Trap gauntlet · 10** pill at the strip's right.
* **Dodged elsewhere.** From P6's `attempts.offered`: a trap whose norm was on offer in other
  question types and not chosen reads `dodged in 3 other types` on its row and in the pane's
  Same-mistake-elsewhere line (`Also a trap in 4 other types · dodged in 3 of them`).
* The filter bar gains a **Habit** chip.

**Acceptance.**
1. A learner with 3 traps tagging `whole_part` over 2 topics: `?group=habit` returns one group
   `whole_part` with 3 items, and its button body is `{source:'habit', habit:'whole_part',
   count:8}`.
2. A trap norm on offer and not chosen in 2 other templates (P6 rows): its item has
   `dodged_elsewhere == 2`.
3. `?habit=sign` returns only traps whose norm maps to `sign`.

---
### C. Proof and progress

#### V8. The story of a mistake: its timeline, your path through the question, and a History head that says what to do

*From: unfair-advantage #10, experience #5 (the timeline), the experience and unfair-advantage
eliminations gaps, the outcomes and experience attempt-history gaps. Effort M. Builders: F4
(`trap_log`), S10 (item and family payloads), F3 (the timeline and path blocks in `UI.review`,
the `UI.history` head).*

**Why.** Seeing a mistake go from the miss to proof on new numbers, then hold at spaced checks,
is what makes "fixed" believable, and seeing where you had the right answer and changed away
from it is the lesson. TopTierPrep's Attempt History covers one item in one session; they never
show a fix, and never show the eliminations they store.

**The log** (`trap_log`, F4, §3.2): `id INTEGER PRIMARY KEY, learner, template, norm, at, event,
attempt INTEGER, pts INTEGER`. Events: `open` · `miss` · `pip` · `fixed` · `check_ok` ·
`relapse` · `dismissed` · `restored` · `reopened`. `progress.record` and the mistake endpoints
write it in the same transaction as the traps row. It is keyed by (learner, template, norm), not
by trap id, so `progress.carry` only re-keys the learner. A one-off backfill writes `open` at
`traps.opened` and `fixed` at `traps.closed` for existing rows.

**The timeline** (the pane, under the header, when `open=trap:<id>`). One node per event, left
to right, each a `UI.cell` with its date and a source chip, for example:
`Sep 12 · Section #7 · Q14 · picked C · Wrong (trap)` → `Sep 12 · Repair ↻ · new numbers` →
`Sep 14 · Practice ✓ clean · Fixed` → `Sep 17 · Check-in 1 ✓` → `Sep 24 · Check-in 2 due`.
A relapse is a graphite node. A node with an attempt opens that exact question in the pane;
Back returns to the timeline. A summary line reads `Fixed in 2 days with 3 answers · held 10
days`. Fixed rows show the chain as a compact run of cells.

**Your path** (the pane body, for the attempt shown):
* Options the student struck are drawn struck (P6's `attempts.struck`, tests' `qstate.struck`).
  When the key was struck: `You crossed out the right answer (A) before picking C`, in ink.
* Answer changes in tests: `B → C · C → D` from `qstate.trail`, with `first answer: B (right)`
  when the first was right.
* Time against budget: `2:52 · budget 1:35 · 1:17 over` (P16), or `0:12 · rushed`.
* Confidence: `You said Sure` / `Unsure` / `Guess`, or `Sure (assumed)`.
* The student's highlights and notes, read-only (R6, `UI.annotate`).
* P9's `then` line when the student has since answered the type right.

**The History modal head** (`UI.history`, R23; the table stays v2's). Under P9's trend line:
* a verdict chip, the first that applies: `Same trap twice` (the last two misses share a norm) ·
  `Right but slow` (P16) · `Fluent` (P16) · `Getting faster` (median of the last 3 rights at
  least 20% under the first 3) · `Fixed · held 10 days`;
* one next-step button tied to it: `Learn it` (T4) · `Speed drill · 8` (T8) · `Keep warm · 3`
  · `Another like this` · `Check in now`;
* a `This mistake only` toggle that filters rows to one norm (the pane's trap), counted
  (`4 of 11`).

**Data.**
* `GET /api/review/item` adds `story: [{at, event, attempt?, source, session?, qid?, result,
  pick?, pts?}]` (for a trap), `path: {struck, trail, first, ms, budget_ms, conf, conf_assumed,
  marks}`, and `summary: {days_to_fix, answers, held_days}`.
* `GET /api/review/family` adds `verdict: {kind, text, start: {body} | href}` and takes `norm=`.

**Acceptance.**
1. A trap missed, repaired, answered clean and fixed: `select event from trap_log where
   template='<t>' order by id` gives `open, miss, pip, pip, fixed` (the miss that opened it
   also logs `miss`).
2. `POST /api/me/carry` moves `trap_log` rows to the new code, and `/api/review/item?…` for the
   carried trap returns the same story length.
3. An attempt with the key struck: `path.struck` contains the key's index, and the pane shows
   "You crossed out the right answer".
4. `GET /api/review/family?template=<t>` for a learner whose last two misses on t share a norm
   has `verdict.kind == 'same_trap'`; `&norm=<n>` returns only rows with that norm.
5. Browser: clicking a timeline node loads that exact stem in the pane, and Back restores the
   timeline.

#### V9. The ledger: mistakes made against mistakes fixed, week by week, and when the list reaches zero

*From: experience #8, outcomes #10, the stat-tile and Me-card gaps of all three. Effort S.
Builders: S10 (the chart, the forecast), F1 (`UI.barChart` stacked below the axis with a line),
S1 (Me's line).*

**Why.** Net progress on mistakes is what keeps a student coming back, and tying the backlog to
the exam date turns a list into a plan. TopTierPrep never shows what was fixed; "Redo Questions
0" is the whole story. v2 has one stat line.

**The chart** (the Fixed tab head; `UI.barChart`, `role=img`, a hidden data table):
* 12 weeks (8 on a phone, fitting the width); graphite bars below the axis for mistakes opened,
  the relapse part hatched; amber bars above for fixed; an ink line for the open count at each
  week's end. The legend carries counts.
* A tap or hover on a week: `Sep 15–21 · 9 made · 12 fixed · open 28 → 25`; a click filters
  Fixed or History to that week (`since`, `until`).
* The headline: `This week: fixed 12, made 9, net −3 · median 2 days to fix`.
* One earned line only when fixed > made this week: `Fixing them faster than you make them.`
* Under 2 weeks of data: a single line, `9 made · 12 fixed so far`.

**The forecast** (shown when the last 4 weeks have net fixes > 0 and `exam_date` is set):
`At this pace (8 fixed a week, 5 made) open mistakes reach 0 around Oct 30, 8 days before your
SAT.` When it lands after the exam, and the learner has 10+ fixes in 28 days, their own rate
prices the gap: `That's after your SAT. You fix about 1 per 6 minutes of review, so about 5 more
minutes a day clears them by Nov 7.` The rate is the student's measured fixes ÷ minutes in
`source:'due'` and redo sessions over 28 days; with less data, no minutes line.

**Direction on the tiles.** OPEN's sub line takes `▼3 this week` and a 12-week sparkline of the
open count; FIXED's takes `6 this week`.

**Me** (S1, §3.2): Saved & in progress's `Open mistakes 25` line becomes `Open mistakes 25 ▼3
this week · 12 due today`, with **Start review · 10 min** and the sparkline.

**Data.** `GET /api/review/ledger?weeks=12` → `{subject, weeks: [{week, opened, relapsed,
fixed, open_end}], rate: {fixed_week, made_week, minutes_per_fix | null}, forecast: {zero_on |
null, after_exam: bool, extra_minutes | null}}`, from `trap_log` in X-Tz local weeks.

**Acceptance.**
1. A learner with 5 `open` and 3 `fixed` events this week and 2 `relapse`: this week's row has
   `opened == 5`, `fixed == 3`, `relapsed == 2`, and `open_end` equals the open count.
2. With net fixes ≤ 0 over 4 weeks: `forecast.zero_on == null` and no forecast line renders.
3. At 390, the chart shows 8 weeks and `scrollWidth === 390`; its hidden table has 8 rows.

#### V10. Fixed that holds: which fixes have held a check-in, and at which difficulty

*From: unfair-advantage #11, the outcomes Repaired gap, today.md T3's schedule. Effort S.
Builders: S10 (the Fixed rows, `Prove it`), F5 (check-ins at the highest proven tier).*

**Why.** A mistake can close within minutes of opening (every closed trap in the dev db did).
R9's check-ins at 3, 10 and 30 days are the real proof, so the Fixed tab should say which fixes
have passed one. And a mistake fixed only at Medium hasn't been shown at Hard.

**Fixed rows.**
* The check-in state reads R9's schedule: `Not checked yet · first check Sep 26` (amber
  outline), `Held 1 check ✓ · next Oct 3`, `Held 2 ✓ · next Oct 23`, `Held all 3 ✓`, or
  `Dismissed`.
* **Proven at**: `▁✓ ▃✓ ▅○`, only for tiers the template makes (`drill._tiers_of`, or P18's
  sibling tier). A tier is proven by a clean right at it after the trap opened (derived from
  attempts, no column). A row with an unproven higher tier offers **Prove it at Hard**: an
  inline one-question drill (`{templates:[t], tiers:['hard'], count:1, source:'review'}`), or
  the sibling's template when the type has one tier.
* The Fixed stat line: `40 fixed · 31 held a check-in · 9 not checked yet · 3 relapsed (8%) ·
  median 2 days to fix · recovered ≈ +30 pts this month`. Dismissed ones are not counted as
  fixed.
* Sort gains **Not checked yet first**; Status gains `Not checked yet · Held`.

**Check-ins test the level reached.** A check-in (pool `checks`, R9) draws its fresh seed at the
highest proven tier of the trap's template (§3.2, F5). A row fixed below its template's top
tier reads `Fixed at Medium`.

**Acceptance.**
1. A trap fixed today: `/api/review/fixed` has it with `held == 0` and `checks == 0`; the row
   reads "Not checked yet". After one clean check-in: `held == 1`.
2. A trap on a two-tier template fixed with clean rights only at medium: `tiers_proven ==
   ['medium']`, `tiers_available == ['medium','hard']`; its check-in drill serves a medium seed.
   After a clean hard right, the check-in serves hard.
3. `counts.held + counts.unchecked == counts.fixed` (dismissed excluded).

#### V11. Stuck mistakes go to Learn it, and "See one solved" puts a worked twin beside your miss

*From: outcomes #6, unfair-advantage #6, today.md T4, practice.md P2. Effort S. Builders: S10
(status, entry points), F5 (`GET /api/types/{t}/example?want=`), F3 (the side-by-side sheet).*

**Why.** Hammering a question type the student keeps failing repeats the error. Studying one
worked instance, then solving with support fading, beats solving alone (worked-example and fading
research). TopTierPrep can only show the same item's explanation again, after which re-answering
it tests memory. A worked example on new numbers that carries the student's own trap needs an
unlimited bank and labelled distractors; 88.6% of our traps turn up within 40 reserved seeds.

**Stuck.** A trap with `hits ≥ 3` or `relapses ≥ 1` (T4's rule) gets the status chip `Stuck`
and a row action **Learn it** (T4's body, `{source:'learn', templates:[t], example:true,
count:3}`), which is also the pane's primary for that trap in place of Fresh one like this.

**See one solved** (the pane, beside Fresh one like this, key `V`). A `UI.sheet` (960 px on
desktop, full screen on a phone):
* Left, `You missed`: the original with the pick marked.
* Right, `Worked · new numbers`: a reserved example (`GET /api/types/{t}/example?want=<norm>`)
  with the key highlighted, the rationale and P1's steps open, and the option carrying the same
  misconception outlined: `Same trap as your C: used 180° for a whole circle. Here it gives 36.`
  When no reserved seed within 40 carries the norm, the example still shows, without the outline.
* Under both, **Now you: a new one**, which closes the sheet and runs Fresh one like this
  inline, so the order is example → attempt.
* On a phone the two stack under a seg `You missed · Worked`.
* It files nothing; the example seeds are never served in practice (T4, U2).

**Data.** F5's `GET /api/types/{t}/example` takes `want` (a norm) and `tier`: it walks the
reserved seeds from 900000 (at most 40) for an item whose option reasons include that norm, and
returns `trap_index` (§3.2).

**Acceptance.**
1. A trap with 3 hits: `/api/review/redo` item `status == 'stuck'`; its row button posts the T4
   body with `templates == [t]`.
2. `GET /api/types/<t>/example?want=<norm>` for a template and norm that appear in its survey
   returns `seed >= 900000` and a `trap_index` whose option reason normalises to the norm.
3. Browser 1280: See one solved opens a sheet with two columns and exactly one outlined option in
   the right one; Now you closes it and shows a new question in the pane with a different stem.

#### V12. Right but slow, and rushed: time as something to fix

*From: outcomes #5, experience #9, unfair-advantage #7, the time-per-question gaps of all three.
Effort S (P16 owns budgets and fluency). Builders: S10 (filters, the Pace block, the box fill).*

**Why.** On a timed module a right answer that took three minutes costs the two questions after
it, and today's lists count it as simply right. TopTierPrep's stopwatch resets on reload and is
never analysed; v2's Review only sorts by Slowest.

* **Time against budget everywhere.** Every row that shows time shows it against P16's budget for
  that (template, tier): `1:12 · budget 1:35` on History rows and in the pane meta, ink when over,
  with a glyph and text, never colour alone.
* **History's Result filter** gains `Slow right` (right, over budget) and `Rushed` (wrong, under
  25% of budget). The summary card adds `Slow right 11 · 18 min over budget` and `Rushed 5`.
* **The Pace block** (History head): up to 5 of P16's Right-but-slow types, each `Area of a
  sector · your median 2:40 · budget 1:35 · right 88%`, with **Fluency sprint · 5 types** (P16's
  preset body over those templates) and, per row, **Speed drill · 8** (T8's).
* **Rushed rule line**, when 3+ rushed misses in 30 days: `4 misses in under 25 s this month:
  slow down on these`, with **Careful set · 8**.
* **The review box** (V1) fills leftover time with Right-but-slow types.

**Acceptance.**
1. A learner with a right answer at 150 s on a medium template with no crowd budget:
   `/api/review/history?result=slow` includes it; at 50 s it does not.
2. A wrong answer at 20 s on a medium question (budget 95 s) is in `result=rushed`.
3. `summary.slow.over_ms` equals the sum of `ms − budget_ms` over the slow rows.

---

### D. Again, done right

#### V13. Rematch any sitting: clickable result cells, Then vs Now, and retakes nested under the original

*From: experience #7, the outcomes and experience sitting-retake gaps, the unfair-advantage
wrong-number-chips gap, practice.md P19. Effort S. Builders: S10 (the Sitting view), S4 (P19's
summary), S6 (`/api/history` returns `rematch_of`).*

**Why.** Their Clear Session serves the same items again after deleting the record a student
would compare against, so a second score measures memory. A rematch serves every slot's type,
tier and format on new numbers in the original order, and Then → Now shows whether the skill
moved.

**Sitting header** (History, Group by Sitting):
* `Practice · Linear functions, Percentages · Sep 23 14:02 · 9/12 · 14 min`, then a row of
  `UI.cell`s, one per question (R20 glyphs, flag overlay), each a button that opens that question
  in the pane with its misconception on hover or focus.
* Primary **Rematch · same 12 types, new numbers** (`{rematch: sid}`, P19). Secondary
  **Rematch my misses · 3** (`scope:'misses'`), **Rematch weak spots · 5** (`scope:'weak'`: misses
  plus over-budget rights, §3.2), **Walk these misses** (V2), **Report / summary**.
* Overflow: **Again, exactly (tests memory)**, **Fix the misses** (`from_session`).
* **Nested retakes.** Rematches and exact retakes of a sitting nest under it, collapsed:
  `Rematched ×2 · best 11/12 · Then 6 → Now 11`. Expanding shows each child's header.

**The summary** is P19's Then → Now (aligned cells, flips, score and time before and after).

**Acceptance.**
1. After a rematch of sid, `/api/review/history?group=sitting` returns sid with `children:
   [<rematch id>]` and `best` set; the child is not a top-level sitting.
2. `POST /api/drill {rematch: sid, scope:'weak'}` serves one fresh slot per first-try miss and
   per right answer over its budget, in the original order.
3. Browser: a sitting header shows one cell per question; clicking cell 4 opens question 4 in the
   pane.

---

### E. Moving through Review

#### V14. A pane that moves as fast as you think

*From: the experience Prev/Next gap, the unfair-advantage Prev/Next gap, experience #10.
Effort S. Builders: F3 (`UI.review` pane, `UI.stemDiff`), S10 (prefetch, seen marks).*

**Why.** Their review modal already has ←/→ and "1 of 49"; so does v2. The point of a review is
the next mistake worth looking at, reached in one key, rendered instantly.

* **Result strip** in the pane header: one `UI.cell` per row of the current list (up to 60, then
  a `+140` cell that pages), the current one ringed; a click jumps. Rows opened this visit get a
  small seen dot (sessionStorage, try/catch).
* **Keys** (player scope, §2.8): `N` next wrong (already there), `U` next not yet seen this
  visit. Prev/Next follow the list's sort (V4).
* **Prefetch.** The pane requests `/api/review/item` for the 2 rows before and after the current
  one and keeps the last 20 in memory, so a move paints in the same frame.
* **Phone.** A horizontal swipe on the pane (over 60 px, under 30° from horizontal) moves Prev /
  Next with the card sliding (instant under reduced motion). A 500 ms long-press on a row starts
  selection mode, showing every checkbox and the action bar.
* **The numbers change in front of you.** Fresh one like this (`T`) keeps the stem in place and
  swaps only the tokens that differ: `UI.stemDiff(old, new)` splits both stems on
  `/(\d[\d.,/]*|\s+)/`, diffs them with LCS (stems are ≤ about 400 characters), and wraps changed
  tokens in `<mark class=chg>`: the old fades to the new in 220 ms with an amber underline that
  stays 1.2 s; figures cross-fade; choices re-render. Instant under reduced motion, the underline
  kept. The first 3 uses caption it `Same question type, new numbers`.

**Acceptance.**
1. Browser 1280, a list of 25: the pane header has 25 cells; clicking the 10th opens row 10; `U`
   from row 1 after opening rows 1–3 goes to row 4.
2. After opening row 5, the network log shows item requests for rows 3, 4, 6 and 7; moving to row
   6 makes no new item request.
3. Fresh one like this: the stem element is the same node before and after (not re-created), and
   at least one `mark.chg` exists when the numbers differ.
4. Browser 390: a left swipe on the pane moves to the next row; a long-press on a row shows the
   action bar with `1 selected`.

#### V15. One set of options on every action bar, and levels 1–7 in every list

*From: the unfair-advantage Volume/Timed gap, the difficulty/Level gaps of all three. Effort S.
Builders: S10 (the bars and filters), F5 (`level:'harder'` via siblings), F4 (`ratings.level`,
P11).*

**Why.** TopTierPrep's builder applies Volume and Timed to its Redo, Marked and Solved pools and
filters on a 1–7 score; v2's Review offers Level and Timed on Redo only, and three tiers.

* **Every action bar** (Due, Redo, Marked, Saved, History, Fixed) takes the same options, echoed
  in its summary line (`12 selected · 10 questions · as missed · pace clock · instant`):
  * **Volume** `10 · 20 · All` (cut by the tab's current sort);
  * **Clock** `Off · Pace · Custom` with the minutes field (the builder's `clock` values; Pace is
    the sum of P16's budgets);
  * **Feedback** `Instant · At the end` (end turns the set into a test-like retest);
  * **Level** `As missed · Any · Harder` on Redo and Fixed (v2's).
* **Harder** steps one tier up where the template has one, else to P18's sibling at the next tier
  (`blueprint.siblings(t, +1)`), else As missed; the summary says `3 can't go harder`.
* **Level filter**: a chip `Level` with cells L1–L7 (P11's `ratings.level(template, tier)`), each
  counting this tab's rows, and `Include rough levels` (on). Rows and the pane meta read `▃ Medium
  · L4` or `L4 · rough`.

**Acceptance.**
1. Marked with Volume 10 over 14 rows: the started drill has `count == 10`, taken in the tab's
   sort order.
2. A one-tier medium template with a same-label hard sibling: `{pool:'redo', ids:[trap], level:
   'harder'}` serves the sibling at hard.
3. `?levels=4,5` returns only rows whose (template, tier) rates L4 or L5.

#### V16. Empty states that show instead of tell

*From: the experience and unfair-advantage empty-state gaps. Effort S. Builders: S10.*

**Why.** Their empty states are text lines; v2's are too. A new student learns what Review does
fastest by seeing a real row, and by making one.

* **New student** (replaces v2's three-line panel): a sample Redo row built from a real reserved
  item (`GET /api/types/{t}/example`, the coach's pick), tagged `Example`, with its pips, its
  misconception label and its kind. Clicking it opens the pane read-only with every option's
  reason. Beside it, **Try one now**: an inline question (`{source:'try', topics:[coach pick],
  count:1}`, R24). A wrong answer makes the first real Redo row appear live, with its named
  misconception and pips; a right one shows a clean-answer cell, with **Flag it and answer
  another** to show how an Unsure is made. Then **Take the diagnostic** (quiet).
* **Empty tabs** keep v2's one line each, plus the matching action: Marked → **Try one now**;
  Saved → the example row with its bookmark; History → **Try one now**; Fixed → the ledger's empty
  line.
* **An empty History modal** offers **Try one now** on that template.

**Acceptance.**
1. A new code at 1280: `/review/` shows one row with the `Example` tag and a Try one now
   question. Answering it wrong makes `/api/review/redo` return one item, and the list shows it
   without a reload.
2. The example row's pane shows a reason under every wrong option and files no attempt.

---

### F. Share, paper and test week

#### V17. Ask for help: share a mistake with what you picked and why; twins that keep the trap; a Mistakes block for a tutor

*From: experience #11, the outcomes share gap, the unfair-advantage share and export gaps,
practice.md P22. Effort S. Builders: F6 (`sets` `cfg.context`, the `/s/` landing), S10 (the
share menu), S1 (the progress view block).*

**Why.** A tutor or friend needs to see what went wrong, not just the question. TopTierPrep's
Share froze the page, and even working it sends a bare session; their Export is a dead button.

**Ask for help** (the pane's Share menu; a Redo selection's action bar `Ask for help · 5`; the
Save toast's `Ask a tutor`). A sheet with two checkboxes, **Include my answer** (on) and
**Include my note** (off), and **Copy link**.
* It creates `POST /api/sets {kind:'items', items:[[t, s]], cfg:{context:true, note:bool}}`. The
  server builds the context from the sharer's own attempts (never from the client): `{pick,
  mistake, when, source, family: {seen, right}, note?}`.
* **The landing** (`/s/?c=CODE`, F6): the question with answers hidden and **Try it** (a
  one-question drill for the visitor); after their answer, `Your friend picked C: halved the
  circumference instead of subtracting the given arc`, the note if included, the key, the
  rationale and P1's steps.
* The sharer's menu shows `Opened 2 · tried 1` (R18's owner results).

**Twins that keep the trap.** A Review set shared as twins (P22's default) walks each twin's seed
(at most 40, `want`) until the sharer's picked misconception is on offer, so every taker meets
the same trap on their own numbers.

**For a tutor or parent.** The progress link's view (`/share/?t=`, R18(a), S1) gains a read-only
**Mistakes** block from `review.progress_part(learner)`: the counts, V6's cause bar, the top 10
open mistakes by points with their labels and causes, fixed this month, and V9's chart. Rules and
notes stay private.

**Acceptance.**
1. `POST /api/sets {kind:'items', items:[[t, s]], cfg:{context:true}}` for an item the sharer
   missed: `GET /api/sets/{code}` has no stem and no context; after a second learner answers
   through the landing, the landing's context has `pick` and `mistake` equal to the sharer's.
2. The same call with `note:false` never returns the note.
3. A twin share of 3 missed items: each taker's served items carry an option whose norm equals
   the sharer's picked norm on that item (when a seed within 40 has it).
4. `/share/?t=<token>` shows the Mistakes block with the same open count as `/api/review/counts`.

#### V18. Paper that counts: a printed worksheet whose answers are filed

*From: outcomes #11, unfair-advantage #8, v2 §16 and its open question, the Practice builder's
worksheet (§3.3 "2.12 Print view"). Effort S. Builders: S10 (the answer sheet page), S4 (its print
view, reused).*

**Why.** v2's Review worksheet burns seeds and files nothing, so a miss on paper never reaches
Redo. The Practice builder already makes a worksheet an end-mode set left In progress; Review
should use that, not a second printer.

* **Print worksheet** (Redo, Saved, a selection) creates the builder's worksheet:
  `POST /api/drill {pool: <tab>, ids, exact:false, each: 1–3, feedback:'end', source:'worksheet'}`
  and opens S4's print view `/practice/session/?id=<sid>&print=1` (the header, numbered questions
  with figures, entry boxes, the optional answer-key page with every option's misconception).
  Its header adds `Enter answers: /review/sheet/?id=<sid>`.
* **Print another version** makes a new set on new seeds, for a second student or a second try.
* **The answer sheet** (`/review/sheet/?id=<sid>`, S10): one row per number, A–D buttons or a
  grid-in field with the usual keystroke filter and preview, an optional `Minutes taken` field,
  and **Submit**. It posts each answer to `/api/drill/{id}/answer` (end mode, ms = minutes ÷ n),
  then finishes the set, and lands on its summary. The seeds were unseen, so right answers are
  clean, each miss is named and opens a trap, and pips fill.
* **Visible state.** Review's header shows `1 worksheet waiting for answers · Enter answers` while
  one is In progress.
* This answers v2's open question: the seeds are consumed, and the answers are filed when entered.

**Acceptance.**
1. Print worksheet from Saved with 3 selected and `each:2` → a drill with 6 questions,
   `cfg.feedback == 'end'`, `source == 'worksheet'`, not finished.
2. Submitting the answer sheet with one wrong MC answer files 6 attempts (`select count(*) from
   attempts where session='<sid>'`), finishes the set, and opens one trap.
3. `/review/` shows the waiting-worksheet line before submitting and not after.

#### V19. Your traps sheet, your rules and an error log, for test week

*From: experience #12, unfair-advantage #9, outcomes #9, experience #5 (the rule), plan.md L19,
practice.md P21, the unfair-advantage export gap. Effort S. Builders: S10 (`review.trapsheet`,
the print page, the rules view), S7 (Plan's endpoint reads it), F4 (`POST /api/notes` takes an
attempt id).*

**Why.** A short list of the student's own mistakes, each with a rule they wrote, is the most
useful last review there is; no generic cheat sheet matches it. Rules written in their own words
are remembered better (the generation effect). TopTierPrep can't name what a student falls for.

**One trap sheet** (`review.trapsheet(learner, n=10)`, S10). Plan's `GET /api/plan/{id}/trapsheet`
(L19) returns the same entries (§3.2), so `/plan/?print=traps` and `/review/print.html?sheet=traps`
print one list: U6's top habits, then the top open or relapsed traps by points (V4), each with
the label, hits and tell; a reserved example walked for the trap (V11's `want`), its trap option
marked `Your trap`, the key and the rationale's first sentence; **Your rule** (P21's type rule)
when one exists; and the record `dodged 4 of the last 5` (P6). Title `Your traps · Sep 23 · 10
of 31`. Print CSS, 1–2 pages, and a readable phone view.

**Exam week** (from 7 days before `exam_date`): a card at the top of Due, `Your SAT is Sat, Nov
7`, with **Your trap sheet** and **Final check · one fresh question per trap · 10 · about 16 min**
(`{templates: the sheet's templates, count: 10, timing:'pace', order:'mixed', source:'mistakes'}`).

**Your rules** (Saved tab seg, P21's store). Every type rule: the type's name, the rule, the
date, **Try one** (a fresh inline question of that type), edit in place, and `Still useful? Keep
· Remove`. **Print my rules** uses P21's `?print=rules`.
* **Prompts in Review**, at most once per trap: when a trap closes in the pane or the walk (`You
  fixed it. Write the rule so it sticks.`), and when a trap reaches 2 hits or relapses (`Missed
  twice. Write the rule in your own words.`). A 140-character field whose placeholder comes from
  the label, saved with `POST /api/notes {attempt_id, scope:'type', note}` (the server resolves
  the template from the learner's own attempt, §3.2).
* The rule shows after each check-in answer (`Your rule: …`), on the trap sheet, and in the pane
  under the trap's label.

**Error log** (`/review/print.html?sheet=log`, Redo's overflow): every open mistake as a row, the
stem's first line (`attempts.stem`), `picked C → key A`, the named misconception, the cause,
the status and pips, and the rule. Print CSS; the parent/tutor view links it (V17).

**Acceptance.**
1. `GET /api/review/trapsheet` returns ≤ 10 entries, each example `seed >= 900000`, habits first;
   `GET /api/plan/{id}/trapsheet` for the same learner returns the same template list in the same
   order.
2. `POST /api/notes {attempt_id, scope:'type', note:'check the sign'}` stores a `notes` row with
   `seed == -1` and the attempt's template; another learner's attempt id → 404.
3. A trap closed in the pane shows the rule prompt once; closing another trap on the same
   template with a rule already written shows no prompt.
4. A learner with `exam_date` 5 days away sees the Exam week card; 9 days away, no card.
5. `/review/print.html?sheet=log` lists one row per open trap, and `@media print` hides the shell.

---
## 3. Spec overrides

### 3.1 Inside §3.9 (spec/rebuild-v2.md lines 10030–10969)

Each item quotes the line as it stands, then gives the replacement. Lines already changed by a
resolution (R1's phone tabs, R6's notes, R9's 3/10/30 schedule, R18's sets, R22's keys) are read
as the resolution says; the replacements here are written on top of that reading.

1. **§3.9.3 Review hub, intro.**
   * Quote: "TopTierPrep spreads this across builder selects, a profile counter and a modal for one question at a time. Here it is one page with five tabs over a list: **Redo, Marked, Saved, History, Fixed**. A question pane sits beside the list."
     → "TopTierPrep spreads this across builder selects, a profile counter and a modal for one
     question at a time. Here it is one page with six tabs over a list: **Due, Redo, Marked,
     Saved, History, Fixed**. Due is today's finite list and the page's main button starts it
     (V1). A question pane sits beside the list."

2. **§0 Vocabulary, Mistake statuses.**
   * Quote: "- **Fixed**: closed by clean answers."
     → "- **Fixed**: closed by clean answers. It reads **Not checked yet** until its first R9
     check-in passes, then **Held 1 / 2 / all 3** (V10)."
   * After "- **Dismissed**: closed by the student. A later miss reopens it as Open, not Relapsed." add:
     "- **New**: open, and its latest miss came from a sitting that showed no feedback and has not
     been looked at (V2).
     - **Stuck**: open with hits ≥ 3 or relapses ≥ 1 (T4's rule); its primary is Learn it (V11).
     - **Sure ✕** (an overlay on any open status): the latest miss was sure (V5)."

3. **§1 Navigation, the badge.**
   * Quote: "- Review carries a badge: an orange dot and the number of open mistakes, hidden at 0. It reads `/api/me`'s new `review.open`, so there is no extra request."
     → "- Review carries a badge: an orange dot and the number of items due today and not yet done,
     hidden at 0, with the tooltip `12 due today · 25 open`. It reads `/api/me`'s
     `review.due_left`, so there is no extra request (V1)."

4. **§1 URL state.**
   * Quote: "/review/?tab=redo|marked|saved|history|fixed"
     → "/review/?tab=due|redo|marked|saved|history|fixed&view=questions|rules"
   * Quote: "  &topics=a,b&difficulty=hard&fmt=mcq&kind=…&status=…&source=…&result=…"
     → "  &topics=a,b&difficulty=hard&levels=4,5&fmt=mcq&kind=…&status=…&cause=…&conf=…&habit=…&lens=blind|new|stuck&source=…&result=…"
   * New route: `/review/walk/?id=<drill id>` (V2), `/review/sheet/?id=<sid>` (V18),
     `/review/print.html?sheet=traps|log` (V19).

5. **§1 Links in.**
   * Quote: "- The report's Mistakes block ('See all in Review')."
     → "- The report's Mistakes block ('See all in Review'), and its **Review these n misses**,
     which opens the walk (V2).
     - An end-mode set's summary: **Review these n misses** (V2).
     - Today's `#mist` card: **Start review · 10 min**, `12 due today`, and `n new misses ·
     Review them` (V1, V2)."

6. **§2 Header row.**
   * Quote: "- Right: the primary pill **Redo all · 22 questions**, with a meta line under it: `11 question types · about 35 min`."
     and its three sub-bullets ("The number is the sum…", "The minutes come from `blueprint`
     pace.", "The button is hidden only when nothing is open.")
     → "- Right: the duration seg `5 · 10 · 20 · All min` (`prefs.review_minutes`) above the split
     pill **Start review · 10 min**, with the meta line `3 check-ins · 2 quick wins · closes up
     to 5 mistakes` (V1). `All` keeps v2's count, the sum over open templates of the largest
     `owed`: `All · 22 questions · about 35 min`. With nothing due or open the pill reads **Keep
     going · 10 min**.
     - Under the header, when any miss is New: the walk card `6 new misses from Section · Sep 21
     · about 9 min · Review them` (V2); from 7 days before the exam, the Exam week card (V19);
     while a worksheet is In progress, `1 worksheet waiting for answers · Enter answers` (V18)."

7. **§2 Stat strip.**
   * Quote: "**Stat strip.** Five tiles in one row. Each is `--tile`, 10px radius, with a DM Mono 11px uppercase label, an Archivo 800 32px number and a sub line."
     → "**Stat strip.** Six tiles in one row. …" (the rest of the sentence unchanged), and the
     table becomes V1's: DUE TODAY · OPEN · AT STAKE · MARKED · SAVED · FIXED.
   * Quote: "Each tile is a button that opens its tab with the matching filter. For example, CHECK-INS DUE opens Fixed with `status=due`."
     → "Each tile is a button that opens its tab with the matching filter: DUE TODAY opens Due,
     AT STAKE opens Redo sorted by points, FIXED opens Fixed with `status=unchecked` when any
     are not checked yet."

8. **§2 Tab bar.**
   * Quote: "**Tab bar.** Segmented tabs, each with its count: `Redo 25 · Marked 3 · Saved 14 · History 312 · Fixed 40`."
     → "**Tab bar.** Segmented tabs, each with its count: `Due 12 · Redo 25 · Marked 3 · Saved
     14 · History 312 · Fixed 40`. Due is selected by default while items are left today,
     otherwise Redo."

9. **§2 Filter bar table.**
   * Quote: "| Difficulty | Easy / Medium / Hard, as multi-toggle pills. | all |"
     → unchanged; add after it: "| Level | L1–L7 cells, each with its count, and `Include
     rough levels` (V15) | all |".
   * Quote: "| Kind | Misconception / Grid-in / Slip / Unsure. | Redo |"
     → unchanged; add after it:
     "| Cause | Trap / Slip / Misread / Clock / Entry / Gap (V6) | Redo, History |"
     "| Confidence | Sure / Unsure / Guess / Untagged, and the lens `Blind spots` (V5) | Redo,
     History |"
     "| Habit | U6's 11 families (V7) | Redo |".
   * Quote: "| Status | Redo: Open / Half fixed / Relapsed. Fixed: Check due / Checked / Fixed / Dismissed. | Redo, Fixed |"
     → "| Status | Redo: New / Open / Half fixed / Relapsed / Stuck. Saved: Due / Not due /
     Learned. Fixed: Not checked yet / Check due / Held / Dismissed. | Redo, Saved, Fixed |"
   * Quote: "| Source | Practice / Section / Module / Diagnostic / Challenge / Question of the day / Review / Shared set. | History, Marked, Saved |"
     → "| Source | Practice / Today's review / Section / Module / Diagnostic / Challenge /
     Question of the day / Review / Shared set / Worksheet. | History, Marked, Saved |"
   * Quote: "| Result | Right / Wrong / Repaired / Repeat. | History |"
     → "| Result | Right / Wrong / Repaired / Repeat / Slow right / Rushed / Changed (V12, V5) |
     History |"

10. **§2 Sort options.**
    * Quote: "- Redo: Most recent / Most missed / Closest to fixed / Oldest / Topic order."
      → "- Redo: Most points (the default once points exist, V4) / Blind spots first (V5) / Most
      recent / Most missed / Closest to fixed / Oldest / Topic order."
    * Quote: "- Saved: Newest / Oldest / Topic / Not answered first."
      → "- Saved: Due first (the default while `saved_spaced` is on, V3) / Newest / Oldest /
      Topic / Not answered first."
    * Quote: "- History: Newest / Oldest / Slowest."
      → "- History: Newest / Oldest / Slowest / Most over budget (V12)."
    * Quote: "- Fixed: Recently fixed / Longest to fix / Most relapses / Check due first."
      → "- Fixed: Recently fixed / Not checked yet first (V10) / Longest to fix / Most relapses /
      Check due first."

11. **§3 Redo, the strip.**
    * Quote: "**Most-missed strip** (shown when 5 or more are open): up to 5 chips, each the label cut to 40 characters plus `×hits`, then **Redo these 5 · n questions**."
      → "**Above the list**, in order: the walk card when any are New (V2); **Why you lose
      points** (V6); the habits strip with the Trap gauntlet (V7); and **Worth the most** (shown
      when 5 or more are open): up to 5 chips, each the label cut to 40 characters plus `≈ 6
      pts` (`×hits` until points exist), then **Redo these 5 · about +18 pts** (V4). The head
      also reads `You named your own mistake 11 of 17 times (65%)` once 5 have been named (V2)."

12. **§3 Grouping.**
    * Quote: "**Grouping.** A 'Group by' select: Topic (default) / Domain / Mistake type / None. 'Mistake type' groups rows that share a norm across templates (§14). Each group header has:"
      → "**Grouping.** A 'Group by' select: Topic (default) / Domain / Habit / Mistake type /
      None. 'Habit' groups by U6's families, with the tell and Drill this habit (V7). 'Mistake
      type' groups rows that share a norm across templates (§14). Each group header has:"
    * Quote: "- `n open`,"
      → "- `n open · ≈ 20 pts · about 4 of 44 a test` (V4),"

13. **§3 Row.**
    * Quote: "   - Line 2: DM Mono 12px soft, separated by dots: `skill · ▃ Medium · MC · missed 3× · last Sep 21 · Practice · picked C`."
      → "   - Line 2: DM Mono 12px soft, separated by dots: `skill · ▃ Medium · L4 · MC · missed
      3× · last Sep 21 · Practice · picked C · ≈ 6 pts` (V15, V4)."
    * Quote: "4. The kind chip or status chip, if any."
      → "4. The kind chip or status chip, if any, plus `New` (V2), `Sure ✕` (V5), `Stuck` (V11)
      and the cause when it isn't a trap (V6). A Stuck row's action is **Learn it**."
    * Quote: "5. `+2 elsewhere` when the same mistake is open on other templates."
      → "5. `+2 elsewhere` when the same mistake is open on other templates, and `dodged in 3
      other types` (V7)."

14. **§3 Action bar, Redo.**
    * Quote: "  - **Timed**: the same clock toggle and minutes blank as the Practice builder."
      → "  - **Volume**, **Clock** and **Feedback**, the same on every tab (V15). Harder uses
      P18's sibling when the template has one tier."
    * Quote: "- Secondary: **Print worksheet** (§16) and **Share** (§15)."
      → "- Secondary: **Walk these** (V2), **Drill my blind spots** when the selection has any
      (V5), **Print worksheet** (V18), **Ask for help** and **Share** (V17)."

15. **§4 Marked.**
    * Quote: "**Calibration line** at the top: `You flagged 12 questions · 7 were right (58%)`, with the tip *'Most flags right: trust your first answer more. Most wrong: flag and come back.'* It only counts flags set during a sitting, meaning the flag time is earlier than the finish."
      → "**Your instincts** at the top (V5): certainty (Sure / Unsure / Guess × Right / Wrong),
      readings per topic, answer changes and flags. Its flag figures count only flags set during
      a sitting, meaning the flag time is earlier than the finish."
    * Quote: "- `flagged later` when the mark was added from the report or Review."
      → "- `flagged later` when the mark was added from the report or Review.
      - For a test flag, its history: `flagged at 0:40 · 2:10 on it (budget 1:35) · came back 1×
      · changed C → A`, and a `Never came back` chip (V5)."

16. **§5 Saved.**
    * Before "**Row** (a taller card, 88px minimum):" add: "**Head.** The seg `Questions 14 ·
      Your rules 9` (V19), and under Questions the cards `Saved 14 · Due today 4 · Learned 3`,
      each a filter (V3)."
    * Quote: "- the meta: `topic chip · skill · difficulty · MC · saved Sep 20 · answered: Wrong (picked C) · 2 tries`,"
      → "- the meta: `topic chip · skill · difficulty · MC · saved Sep 20 · answered: Wrong
      (picked C) · 2 tries · due today | next Oct 2 | Learned ✓ · box 2 of 4`, and the why tag
      (`Nice trick`, `Hard`) when set (V3),"
    * Quote: "- **Again, exactly** (primary)."
      → "- **Practise due · n** (primary; **Fresh versions** when nothing is due), with `1 / 2 /
      3 each` (V3, P21).
      - **Again, exactly** (tests memory)."
    * Quote: "- **Fresh versions**, with `1 / 2 / 3 each`."
      → removed (it is the primary above).

17. **§6 History.**
    * Quote: "- Repeats 6."
      → "- Repeats 6.
      - Slow right 11 · 18 min over budget · Rushed 5 (V12)."
    * After the summary card add: "**Pace block**: up to 5 right-but-slow types with Fluency
      sprint and Speed drill (V12)."
    * Quote: "- **Sitting header**: `Practice · Linear functions, Percentages · Sep 23 14:02 · 9/12 · 14 min`, with these buttons:"
      and its four sub-bullets
      → V13's header: the result cells, **Rematch** (primary), **Rematch my misses**,
      **Rematch weak spots**, **Walk these misses**, **Report / summary**; overflow **Again,
      exactly (tests memory)** and **Fix the misses**; retakes nested under the original.
    * Quote: "- the time spent (`1:12` or `—`),"
      → "- the time spent against its budget (`1:12 · budget 1:35`, or `—`) (V12),"

18. **§7 Fixed.**
    * Quote: "**Stat line:** `40 fixed · 6 this week · median 2 days to fix · 3 relapsed · 2 dismissed`. Dismissed ones are not counted as fixed."
      → "**Head:** the ledger chart and its forecast (V9). **Stat line:** `40 fixed · 31 held a
      check-in · 9 not checked yet · 3 relapsed (8%) · median 2 days to fix · recovered ≈ +30
      pts this month · 2 dismissed` (V10, V4). Dismissed ones are not counted as fixed."
    * Quote: "- the check-in state: `Check due Sep 27` (amber outline), `Checked ✓ Oct 4 · next Oct 25`, `Checked twice ✓`, or `Dismissed`,"
      → "- the check-in state (R9's 3 / 10 / 30 days): `Not checked yet · first check Sep 26`
      (amber outline), `Check due`, `Held 1 check ✓ · next Oct 3`, `Held 2 ✓ · next Oct 23`,
      `Held all 3 ✓`, or `Dismissed`,
      - **Proven at** `▁✓ ▃✓ ▅○` and **Prove it at Hard** (V10),
      - the story as a compact run of cells (V8),"

19. **§8 Question pane.**
    * Quote: "- a meta line: `Circles · Arc length · ▃ Medium · MC · Practice, Sep 21 14:02 · 1:12`, where the source is a link to the sitting's report or summary."
      → "- a meta line: `Circles · Arc length · ▃ Medium · L4 · MC · Practice, Sep 21 14:02 ·
      1:12 · budget 1:35 · ≈ 6 pts`, where the source is a link to the sitting's report or
      summary (V15, V12, V4).
      - for a trap: the timeline (V8); for a blind spot: `You were sure` (V5); your rule under
      the label when one exists (V19);
      - a result strip, one cell per list row (V14)."
    * Quote: "  - The picked one starts with `Your pick ·`."
      → "  - The picked one starts with `Your pick ·` and ends with the quiet link **Not what I
      did?** (V6)."
    * Quote: "- A grid-in shows `You entered 12 · Answer 9`."
      → "- A grid-in shows `You entered 12 · Answer 9`.
      - P1's steps, and **Your path**: struck options, answer changes, time against budget,
      confidence, highlights (V8).
      - A New item opens at V2's **What happened?** step, with **Just show me**."
    * Quote: "- primary **Fresh one like this**,"
      → "- primary **Fresh one like this** (**Learn it** for a Stuck trap), with **See one
      solved** beside it (V11); the swap animates only the numbers that change (V14),"
    * Quote: "- **Share**,"
      → "- **Share** and **Ask for help** (V17),"

20. **§9 Attempt History modal.**
    * Quote: "**Summary row.** `seen 6 · right 3 · repaired 1 · repeats 1 · median 1:10`, then the open mistakes on this template, with their pips and labels."
      → "**Summary row.** P9's trend line, then `seen 6 · right 3 · repaired 1 · repeats 1 ·
      median 1:10`, then the open mistakes on this template, with their pips and labels, then
      the verdict chip with its one next step and the `This mistake only` toggle (V8)."

21. **§10 Elsewhere.**
    * Quote: "- primary **Redo all · 22**, secondary **Open Review**."
      → "- primary **Start review · 10 min** with `12 due today`, secondary **Open Review**, and
      `n new misses · Review them` when any are New (V1, V2)."
    * Quote: "**Me.** A Saved content card: `Open mistakes 25 · Marked 3 · Saved 14 · Fixed 40 · Answers 312`. Each number links to its tab."
      → "**Me.** A Saved content card: `12 due today · Open mistakes 25 ▼3 this week · Marked 3
      · Saved 14 · 4 due · Fixed 40 · Answers 312`, with **Start review · 10 min** and the
      12-week open-count sparkline (V1, V9, V3). Each number links to its tab."
    * Quote: "- A **Source** segmented control: `New | Redo 25 | Marked 3 | Saved 14 | Fixed (check) 2`."
      → "- A **Source** segmented control: `New | Today's review 12 | Redo 25 | Marked 3 | Saved
      14 | Fixed (check) 2` (V1; practice.md's "Questions from" carries the same entries)."
    * Quote: "**Session summary.** Each 'Opened' and 'Fixed' line links to `/review/?open=trap:<id>`."
      → "**Session summary.** Each 'Opened' and 'Fixed' line links to `/review/?open=trap:<id>`.
      A `source:'due'` set's summary is V1's end screen; an end-mode set's offers **Review these
      n misses** (V2)."

22. **§11 Phone.**
    * Quote: "- **Header.** The H1 at 28px, the helper line, and **Redo all · 22 questions** as a full-width pill."
      → "- **Header.** The H1 at 28px, the helper line, the duration seg, and **Start review · 10
      min** as a full-width pill (V1)."
    * Quote: "- **Stat strip.** A 2-column grid: Open / Marked / Saved / Fixed. Check-ins due spans the full width when it is above 0."
      → "- **Stat strip.** A 2 × 3 grid: Due today / Open / At stake / Marked / Saved / Fixed."
    * Quote: "- **Tabs.** Five equal segments, sticky under the top bar. Each segment has two lines: the label (Archivo 600 13px) and the count (DM Mono 12px)."
      → "- **Tabs.** Six equal segments, sticky under the top bar. Each segment has two lines: the
      label (Archivo 600 13px) and the count (DM Mono 12px)."
    * Add: "- **Pane.** A horizontal swipe moves Prev / Next; a long-press on a row starts
      selection mode (V14)."

23. **§12 States.**
    * Quote: "- A panel with three lines, each with an icon:"
      and the four lines under it (the three quoted definitions and "Then **Start practice** …")
      → "- V16's example row, built from a real reserved item and tagged `Example`, and **Try one
      now**, whose miss becomes the first real row; then a quiet **Take the diagnostic**."
    * Quote: "**Nothing open, but history exists.** 'Nothing open. 40 fixed, 6 this week.' Then **Check 2 fixed mistakes** if check-ins are due, or **Keep going** (the coach set) if not."
      → "**Nothing left today.** V1's Done for today on the Due tab. **Nothing open at all, but
      history exists.** 'Nothing open. 40 fixed, 6 this week.' Then **Keep going · 10 min** (the
      coach set)."

24. **§13 Keyboard.**
    * Quote: "- **Pane keys:** ←/→ Prev/Next, F fresh one, E again exactly, S save, M mark, H history, A hide/show answers."
      → "- **Pane keys:** §2.8's player map (←/→ or J/K, N next miss, H hide / show answers, T
      fresh one, E again exactly, B save, M mark, Y history, I details, R report, A–D / 1–4 while
      hidden), plus `U` next not yet seen (V14) and `V` see one solved (V11). Page: `Shift+R`
      starts Start review (V1). In the walk: `1`–`6` choose, Enter next step (V2)."

25. **§14 Same mistake, other question types.**
    * Quote: "- The Redo 'Group by: Mistake type' uses the same index."
      → "- The Redo 'Group by: Mistake type' uses the same index. 'Group by: Habit' uses U6's
      families, and the pane adds `dodged in 3 of them` from P6's `offered` (V7)."

26. **§15 Share.**
    * After the paragraph that starts "**Share** in any action bar, and on the pane, creates" add: "The same menu offers
      **Ask for help** (V17), which carries the pick, the named mistake and optionally the note.
      A Review set shared as twins keeps the sharer's trap on offer (V17)."

27. **§16 Printable worksheet.**
    * Quote: "**Print worksheet** on Redo and Saved opens `/review/print.html?…`: 1–3 fresh versions per selected template, numbered, with the stems, figures and choices, and space to work. The answers and each option's misconception are on the last page. It uses print CSS only."
      → "**Print worksheet** on Redo, Saved and any selection creates the Practice builder's
      worksheet set (`feedback:'end'`, `source:'worksheet'`, 1–3 fresh versions per template)
      and opens its print view `/practice/session/?id=<sid>&print=1`, whose header adds
      `Enter answers: /review/sheet/?id=<sid>` (V18)."
    * Quote: "The seeds are remembered as seen, so the worksheet never repeats in practice. The page says 'These answers are not filed. Practise online to count them.'"
      → "The seeds are served to that set, so they never repeat in practice. Answers entered on
      `/review/sheet/` are filed like online ones: misses are named and open traps, clean rights
      fill pips (V18)."

28. **§3.9.4 Extras.**
    * Quote: "- **Spaced check-ins on fixed mistakes**: A fixed mistake comes back once as a fresh question at 7 days, and again at 21 days if that is clean. A miss reopens it as Relapsed. This is TopTierPrep's vocab 'Due Today' applied to math, and it cannot run dry."
      → "- **Spaced check-ins on fixed mistakes**: A fixed mistake comes back as a fresh question
      at 3, 10 and 30 days (R9), at the highest tier it was proven at (V10). A miss reopens it as
      Relapsed. The Fixed tab says which fixes have held. This is TopTierPrep's vocab 'Due
      Today' applied to math, and it cannot run dry."
    * Quote: "- **Printable fresh worksheet**: A tutor, parent or offline student gets a new worksheet every time, with answers and each option's misconception on the last page. A finite bank can only print the same pages."
      → "- **Printable fresh worksheet whose answers count**: A tutor, parent or offline student
      gets a new worksheet every time, with answers and each option's misconception on the last
      page, and the answers entered afterwards are filed and named (V18). A finite bank can only
      print the same pages."
    * Append one line each for V1 (a finite daily review), V2 (name it before we name it), V3
      (saved as a spaced deck), V4 (points at stake), V5 (instincts), V6 (causes and label
      disputes), V8 (the story and your path), V9 (the ledger), V11 (a worked twin with your
      trap), V17 (Ask for help), V19 (your trap sheet and rules), each as its §2 "Why" states.

29. **§3.9.5 Server: access rule.**
    * Quote: "Shares also refuse any pair in today's daily.challenge until the day is over (it is the same for everyone)."
      → "Shares also refuse any pair from today's challenge until the day is over (every student
      gets the same ten question types in the same order, decision 1, so a shared twin would
      still pass the method around)."

30. **§3.9.5 Server: counts and /api/me.**
    * Quote: "  /api/me adds review: {open} for the nav badge, which the shell already fetches."
      → "  /api/me adds review: {open, due_left} for the nav badge, which the shell already
      fetches (V1)."
    * Quote: "  /api/review/counts returns {open, half, relapsed, unsure, marked, marked_right, marked_during, saved, noted, saved_unanswered, fixed, fixed_week, median_days, dismissed, due, answers, redo_questions, redo_templates}. redo_questions = Σ over open templates of max(owed)."
      → the same list plus `subject, due_left, due_total, waiting, new, blind, stuck,
      stake_total, open_week_delta, held, unchecked, recovered_month, saved_due, learned,
      diag_n, diag_right, worksheets_waiting`. `due` stays the check-ins due count;
      `redo_questions` stays Σ over open templates of max(owed) (used by `All`).

31. **§3.9.5 Server: GET /api/review/redo.**
    * Quote: "  Query: topics, difficulty, fmt, kind (misconception|gridin|slip|unsure), status (open|half|relapsed), q, sort (recent|hits|near|oldest|topic), group (topic|domain|norm)."
      → "  Query: topics, difficulty, levels, fmt, kind (misconception|gridin|slip|unsure), status
      (new|open|half|relapsed|stuck), cause (trap|slip|misread|clock|entry|gap), conf
      (sure|unsure|guess|untagged), habit, lens (blind|new|stuck), q, sort
      (worth|blind|recent|hits|near|oldest|topic), group (topic|domain|habit|norm)."
    * Quote: "  - items: [{id, template, norm, label, reason, kind, skill, topic, name, domain, hits, owed, clean, status, relapses, opened, last, difficulty, fmt, seed, session, source, given, given_label, elsewhere}]. The item fields come from the trap's latest wrong attempts row, joined on (learner, template, norm)."
      → the same fields plus `attempt` (that row's id), `pts`, `blind`, `conf`, `cause`, `new`,
      `stuck`, `habit`, `level`, `level_rough`, `dodged_elsewhere`, `rule`.
    * Quote: "  - groups: [{key, name, domain, count, questions}]"
      → "  - groups: [{key, name, domain, count, questions, pts, per_test, tell?}]"

32. **§3.9.5 Server: marked, saved, fixed, history.**
    * After the line that starts "  - marked items:" add: "`calibration`
      is replaced by `GET /api/review/calibration` (V5); marked items add `visits, first,
      changes, budget_ms, flagged_at_ms`."
    * After "  - saved items: the same fields, plus note, tries and last_result." add: "plus `box,
      due, learned, why` (V3)."
    * After the line that starts "  - fixed items:" add: "plus `held, tiers_proven, tiers_available, pts`; stats add
      `held, unchecked, recovered_month` (V10, V4)."
    * After the line that starts "  - history items:" add: "items add `budget_ms, slow, rushed, conf, changed`; result
      takes `slow|rushed|changed`; summary adds `slow {n, over_ms}, rushed`; the response adds
      `pace: [types]` (V12); sittings add `cells, rematch_of, children, best` (V13)."

33. **§3.9.5 Server: item and family.**
    * Quote: "  - saved, note, flagged, address, access."
      → "  - saved, note, flagged, address, access, and `new, diag_choices` (V2), `story, path,
      summary` (V8), `level, level_rough, budget_ms, pts, rule` (V15, V12, V4, V19)."
    * After "It returns {template, skill, topic, summary, attempts: […], next}." add: "It also
      returns `verdict {kind, text, start}` and takes `norm=` (V8)."

34. **§3.9.5 Server: schema.**
    * Quote: "  - saved gains note TEXT, session TEXT and qid TEXT."
      → "  - saved gains session TEXT, qid TEXT and why TEXT ('trick' | 'hard'); the note is in
      `notes` (R6).
      - attempts gains diag TEXT (V2).
      - A new table trap_log(id INTEGER PRIMARY KEY, learner, template, norm, at, event,
      attempt INTEGER, pts INTEGER), indexed (learner, at) and (learner, template, norm), written
      with every traps change (V8)."

35. **§3.9.5 Server: spaced check-ins.**
    * Quote: "  When a trap closes with how='fixed': due = closed + 7 days, checks = 0."
      → "  When a trap closes with how='fixed': due = closed + 3 days, checks = 0 (R9)."
    * Quote: "  - the first check sets checks = 1 and due = today + 21 days,"
      → "  - the first check sets checks = 1 and due = today + 10 days,"
    * Quote: "  - the second sets checks = 2 and due = NULL."
      → "  - the second sets checks = 2 and due = today + 30 days; the third sets checks = 3 and
      due = NULL (R9). Each check draws at the highest proven tier of the template (V10)."

36. **§3.9.5 Server: worksheet.**
    * Quote: "- **Worksheet (extra)**: GET /api/review/worksheet?list=&ids=&each=1..3 returns fresh items (public fields, answer, reasons, rationale), remembered as seen and not filed. It is capped at 40 items."
      → "- **Worksheet (extra)**: no endpoint of its own. Print worksheet posts `POST /api/drill
      {pool, ids, exact:false, each: 1–3, feedback:'end', source:'worksheet'}` (≤ 40 items) and
      opens S4's print view; `/review/sheet/?id=` files the answers through that drill (V18)."

37. **§3.9.5 Server: new endpoints.** After "- **Mistake actions**" add V1–V19's endpoints:
    `GET /api/review/due`, `POST /api/drill {source:'due'}` through `review.resolve_drill`,
    `POST /api/review/walk`, `POST /api/review/walk/{id}/at`, `POST /api/review/why`,
    `GET /api/review/calibration`, `GET /api/review/ledger`, `GET /api/review/trapsheet`, each as
    its upgrade specifies, all owner-only and subject-aware.

38. **§3.9.6 Files.** Add rows: `server/review.py` · S10; `web/review/walk/index.html` · S10;
    `web/review/sheet/index.html` · S10. `web/review/print.html` stays S10's, for the trap sheet
    and the error log only.

39. **§3.9.7 Shared needs.** Add: `UI.review` mode `walk` and `UI.stemDiff` (F3); `trap_log` and
    `attempts.diag` (F4); `GET /api/types/{t}/example?want=&tier=` (F5); `sets` `cfg.context` and
    its landing, and the admin Labels view (F6); `qstate[qid].visits` (S5).

40. **§3.9.8 Acceptance checks.**
    * Quote: "1. curl -s -H 'X-Learner: a:v2revacc1' localhost:8000/api/review/counts returns all zeros for a new code, /api/me has review.open == 0, and /review/ shows the new-student panel with 'Start practice'."
      → "1. curl -s -H 'X-Learner: a:v2revacc1' localhost:8000/api/review/counts returns all
      zeros for a new code, /api/me has review.open == 0 and review.due_left == 0, and /review/
      shows V16's Example row and Try one now."
    * Append the acceptance lists of V1–V19.

41. **§3.9.9 Open questions.**
    * Quote: "- The worksheet consumes seeds (remembered as seen) without filing answers. Is that the right trade, or should worksheet seeds stay available to practice?"
      → "- Resolved (V18): the seeds are consumed and the answers are filed when entered."
    * Quote: "- Grid-in misses name no misconception because SPR items carry no distractors. Where a template can also render the same parameters as MC, the typed value could be matched to a distractor's value. Worth asking the bank owner."
      → "- Resolved by practice.md P4 and T-bank's `spr_mistakes`; V2's What happened? offers
      them."

### 3.2 Outside the section (Part 2 and sibling lines these upgrades need; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| R1 | The Review badge (sidebar meta, phone top-bar chip, menu-sheet footer cell) shows today's due left, hidden at 0, tooltip `12 due today · 25 open`; `/api/me.review = {open, due_left}` | V1 |
| R7 | `qstate[qid].visits` (int), +1 each time the runner shows the question, sent with `POST /api/session/{sid}/state {question_id, visit:true}` | V5 |
| R9 | Every traps change also writes a `trap_log` row in the same transaction. A check-in draws at the highest tier with a clean right since the trap opened. Display: Fixed = `Not checked yet` until the first check passes | V8, V10 |
| R18(a) | The progress view `/share/?t=` renders `review.progress_part(learner)` as a read-only Mistakes block | V17 |
| R18(c) | `sets` kind `items` takes `cfg.context` (built server-side from the owner's attempts; `note` opt-in); the `/s/` landing reveals it after the visitor answers. A twin share from Review walks each seed (≤ 40, `want`) until the sharer's picked norm is on offer | V17 |
| R24 | Sources `due` and `worksheet` are ordinary sittings (listed, resumable). The walk is an inline drill (`source:'review'`) | V1, V2, V18 |
| §2.5 | New table `trap_log(id INTEGER PK, learner, template, norm, at, event, attempt INTEGER, pts INTEGER)`, indexes `(learner, at)` and `(learner, template, norm)`, in `LEARNER_TABLES` and `carry` (re-keyed by learner). Columns `attempts.diag TEXT`, `saved.why TEXT`. Startup backfill: `open` and `fixed` events from existing traps | V2, V3, V8 |
| §2.6 | Source `due`, resolved by `review.resolve_drill` (S10) through the registry, with `box` (5–60 or null = All); its preview returns T1's `blocks` and takes `drop`. `rematch` takes `scope:'weak'` (misses plus rights over budget). `level:'harder'` falls back to `blueprint.siblings(t, +1)`. Pool `saved` feedback adds `saved_note`. `GET /api/types/{t}/example` takes `want` (a norm) and `tier`, walking ≤ 40 reserved seeds, and returns `trap_index` | V1, V3, V11, V13, V15 |
| §2.7 | Keys: `review_minutes` (5 \| 10 \| 20 \| 0 = All; default 10; Review header, Settings) and `saved_spaced` (bool, default true; Settings, the Saved tab) | V1, V3 |
| §2.8 | Player: `U` next not yet seen, `V` see one solved. Page scope `review`: `Shift+R` Start review. Walk: `1`–`6`, Enter | V1, V2, V11, V14 |
| §2.9 | S10 provides `review.due`, `review.saved_due`, `review.trapsheet`, `review.progress_part`, `review.resolve_drill` → F2 (badge, U1 row 9), F5 (the resolver), S3 (`#mist`), S7 (the trap sheet), S1 (Me, the progress view). F5 provides the example `want` → S10, S7. F6 provides `cfg.context` and the admin Labels view. S5 provides `visits` | all |
| shell-me U1 | Row 9 `saved` lists V3's due saved questions (`review.saved_due`) instead of "saved 7 or 21 days ago ±1 day"; its start body is unchanged | V3 |
| shell-me §3.1 override 30 (Me, Saved & in progress) | The Open mistakes line reads `Open mistakes 25 ▼3 this week · 12 due today` with **Start review · 10 min** and the sparkline; Saved questions reads `Saved 14 · 4 due` | V1, V3, V9 |
| today T9 / R30 | `#mist`'s primary is **Start review · 10 min** (`source:'due'`, `box: prefs.review_minutes`) with `12 due today`; a line `n new misses · Review them` opens the walk when any are New | V1, V2 |
| practice P19 | `scope` adds `weak` (first-try misses plus rights over P16's budget, in order) | V13 |
| practice P21 | `POST /api/notes` also takes `{attempt_id, scope:'type', note}`: the server resolves the template from the learner's own attempt (404 otherwise). Review lists rules in Saved's `Your rules` and prompts on close and at 2 hits | V19 |
| practice §3.3 builder | "Questions from" gains **Today's review · 12 due** (`source:'due'`) | V1 |
| plan L19 | `GET /api/plan/{id}/trapsheet` returns `review.trapsheet(learner)` (read through `deps.part`); entries add `rule` and the dodge record | V19 |
| S4 session | The summary for `source:'due'` is V1's end screen; an end-mode set's summary offers **Review these n misses** (V2); the print view's header adds `Enter answers: /review/sheet/?id=`; the Save toast carries V3's why chips | V1, V2, V3, V18 |
| S5 test window | Sends `visit:true`; Check Your Work's marked line adds `n not revisited` | V5 |
| S6 report | **Review these n misses · about m min** beside Fix these; the line `Your flags caught 2 of your 7 misses` over the grid; `/api/history` returns `rematch_of` so retakes nest | V2, V5, V13 |
| F6 admin | `/admin/reports` gains a Labels view: per (template, norm), label reports and "Not what I did?" corrections, rate-sorted | V6 |

---

## 4. Rejected

* **A mistake closes only on two different days** (outcomes #2, and the outcomes Repaired gap):
  `practice.md` rejected the same rule; R9's 3-day check-in is the delayed proof. V10 makes the
  Fixed tab say which fixes have held instead.
* **The "primed" rule (pane answers within 10 minutes of reading the label don't count)**
  (outcomes #2): the practice repair, read right after the key, already counts as clean; one
  rule everywhere.
* **Cover questions, 1 slot in 4 of new material in the review** (outcomes #1): the review is
  already interleaved and skill-hidden (T3's `hide_skill`), and P12 mixes reviews into new sets
  the other way, without adding minutes to the review.
* **A separate saved ladder of 1 / 3 / 7 / 21 / 60 days** (outcomes #1): V3's 1 / 3 / 7 / 21 then
  Learned; a 60-day rung outlives most students' prep.
* **`saved.box` and `saved.due` columns** (experience #6): derived from attempts like T3's fading
  types; `practice.md` rejected a boxes table for the same reason.
* **Withholding the key on the server until the diagnosis is posted** (outcomes #3): the finished
  report already shows it; the walk's order is a study aid, not a lock.
* **A `diagnoses` table and `traps.reviewed`** (outcomes #3): one `attempts.diag` column carries
  the choice and the New state.
* **A Sure / Unsure chip in the practice session behind a pref** (outcomes #4): P7's split Check
  records confidence with no extra tap.
* **Slow-right as a Redo kind (`~slow` traps with pips)** (outcomes #5): Redo stays wrong answers.
  Slow lives in History's Pace block, the review box's leftover time and P16's fluency.
* **Tier targets 65 / 95 / 125 s, or a flat 2 × 95 s slow line** (outcomes #5, experience #9):
  P16's budgets (65 / 95 / 126 s, or the crowd median) are the one clock.
* **Target tightening by 15 s and 1.5 × the crowd median** (unfair-advantage #7), and **"Up to
  speed" as a Fixed status**: P16's Fluency sprint (×0.85) and its Fluent state do both.
* **A hinted rung with `attempts.scaffold` and `traps.stage`** (outcomes #6): T4's Learn it and
  P2's hint ladder, with `attempts.hints`, already fade support.
* **Our own 10-habit list with regex rules** (outcomes #7) and **`satbank/habits.json` with a
  failing `satbank check`** (experience #4): U6's 11 families and its OVERRIDES are the one
  taxonomy.
* **A second points model** (outcomes #8's TOPIC_SHARE, experience #3's `progress.stake`,
  unfair-advantage #2's exposure × fall rate): U4's `gains` with U1's redo share is the one
  source; `practice.md` and `today.md` rejected second models too.
* **Points as ranges ("about 40–60 points a section")** (unfair-advantage #2): one rounded figure,
  as Me and Today print.
* **`traps.note` as the rule store** (outcomes #9, experience #5): P21's type rule (`notes`, seed
  −1) is the one store, and it follows the type onto fresh numbers.
* **A rule shown only after answering** (experience #5): P21 already shows it collapsed above the
  stem, and it doesn't count as help.
* **A 120-character rule field** (experience #5): P21's 140.
* **A second, plan-less trap sheet** (experience #12, unfair-advantage #9 as written): one
  `review.trapsheet` feeds both Plan's and Review's print pages.
* **Worksheet codes, QR marking, `/w/CODE` or `/p/CODE` pages, Versions A / B** (outcomes #11,
  unfair-advantage #8): three siblings rejected QR entry until teachers ask. Every Print is already
  a new version, and `/review/sheet/?id=` files the answers.
* **A code checked once per learner for a whole class** (unfair-advantage #8): class homework is
  U27's.
* **A bare `R` key for Start review** (experience #1): `R` is the player's Report key; `Shift+R`.
* **20% control questions in the gauntlet** (unfair-advantage #3): U6 owns the gauntlet; P6's
  dodge counts in ordinary sets already measure the trap where it isn't forced.
* **Cause-specific drill modes (a 30 s Check lock, an estimate prompt, tap-the-ask sets)**
  (unfair-advantage #4): P8's remedies (the re-check line, Read the ask, Careful set) cover them.
* **Slip, Rushed and Misread owing one clean answer** (unfair-advantage #4): a student could halve
  their work by tagging every miss a slip; v2's owed rule stays.
* **Relabelling a trap to another misconception from "Not what I did?"** (the experience Report
  gap): an option's value is produced by its misconception, so the pick fixes the norm; a wrong
  label is a bank report (V6).
* **Logging selection changes before Check in practice** (unfair-advantage #5): picking before
  Check is exploring, not an answer; tests' trail is the real signal.
* **A reason on each flag (Unsure · Guessed · Come back, or Between two · Too long)** (outcomes and
  unfair-advantage flag gaps): `practice.md` rejected it; confidence tags and dwell against budget
  carry the same, and V5 shows both on each flag.
* **Quiz me / Retest blind over a whole list** (outcomes and experience Hide-answers gaps): Rematch
  my misses (P19, V13) and Fresh one like this retest on new numbers; Hide answers keeps v2's
  exact re-answer.
* **Each seed's parameters on History rows (`θ=150°, C=192`)** (experience History gap): the names
  are internal; the stem excerpt already carries the numbers.
* **A `Climb` level per template** (unfair-advantage #11): R33 steps per skill after 2 first-try
  rights, and a redo set asks each template once or twice, so it would never step. Prove it at
  Hard (V10) covers the intent.
* **A `traps.proven` bitmask** (unfair-advantage #11): derived from attempts.
* **`GET /api/review/worked` burning a practice seed** (unfair-advantage #6): the reserved example
  seeds (T4, U2) never cost a real question; V11 walks them for the trap.
* **Time and Traps views in the Question Overview** (the unfair-advantage overview gap): P20
  already adds them.
* **Mix in my mistakes in the builder** (the experience builder gap): practice's picker already
  re-asks open traps in the chosen topics, and P12's review slots mix in the rest.
* **Compare results with a friend by name** (experience share gap, unfair-advantage "Challenge a
  friend"): P22's per-slot "You vs the group" with R18's name opt-in does it.
* **A Monday recap line on Today** (outcomes #10): U14's week review holds it.
