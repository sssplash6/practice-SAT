# v2 upgrades: Compete (contests, rankings, leaderboards)

Written 2026-09-23 for `spec/rebuild-v2.md` §3.7 (lines 8097–9133). It merges three designers'
proposals (outcomes, experience, unfair advantage) into one build-ready list, C1–C25.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.7 where
  they differ: §3 of this file lists every place that changes. Part 2 resolutions (R1–R38) still
  hold, except the lines named in §3.2 "Outside the section".
* **Siblings.** `shell-me.md`, `today.md` and `practice.md` already specify pieces Compete
  reads: Up next and finish-screen chaining (U1, T2), habit families and the personal gauntlet
  (U6, `server/habits.py`), pace quadrants (U7, `progress.pace`), Climb and rank movement (U11),
  "what moves it" and badge Go (U13), spare days (U16), reminders (U18), the inbox (U25),
  classes and "Reach a level" (U27), the twin sheet (T5, `UI.twinSheet`), miss causes (T7,
  `progress.causes`), the final stretch (T13, `next.stage`), item and skill ratings (P11,
  `server/ratings.py`), per-question time budgets (P16, `budget_ms`) and Rematch (P18). This
  file reads those functions and never re-specifies them. Where it needs one of them to change,
  the change is in §3.2.
* **The bar.** A student who uses TopTierPrep today opens ours and wants to switch, because
  competing here does more for their score and is fairer, livelier and faster. Parity is
  failure.
* **Names.** Upgrades are C1–C25. Builders are Part 4's tasks. S8 owns `web/compete/**`,
  `server/compete.py`, `server/api_compete.py`, `web/assets/compete-ui.js` and
  `server/checks/s8.py`. The runners are S4 (practice session) and S5 (test window), through
  R28's hooks.
* **Subject-aware.** Per v2-decisions item 3, `contests` gains `subject` (`math` now, `rw` for
  the Word Sprint, C14). Every new payload (par, debrief, ratings, boards, records) carries
  `subject`, and every board query takes it. Math-only rules (blueprints, the level ladder,
  domains) are keyed by subject, not assumed.
* **Twins everywhere** (v2-decisions item 1). Every ranked kind deals twins, so a key can be
  shown at once, a race or a rematch leaks nothing, and a slot is comparable across students.
* **Facts this file relies on** (checked 2026-09-23):
  * The dev DB holds 7 learners, 287 attempts and 3 challenge sittings. The spec's field lines
    need ≥ 5 answers, top % ≥ 10 players, the podium 3 and the percentile 20, so as written
    almost every screen is empty for months (C6 fixes that).
  * `attempts` already has `template`, `difficulty`, `fmt`, `reason` and `ms`, so whole-bank
    field statistics per (template, tier) need no new column.
  * P16's tier budgets are easy 65 s, medium 95 s, hard 126 s. The Daily's 3E/4M/3H ladder sums
    to 953 s (clock 950 s) and module 1's 7/8/7 to 2,097 s (clock 2,100 s).
  * With P11's item priors (900 / 1100 / 1300), a 1,000-rated student's expected Daily is 3.8
    right and 62 base points. A Level 5 student (1,325) expects 7.5 right and 139 base points.
  * The ladder (`spec/rating.md`): Level 1 ≤ 800, then 150-wide bands from 801, Level 10 from
    2,001. Seed 1,000 is Level 3.
  * U6 found "answered a different quantity" behind 849 surveyed reasons over all 19 topics,
    so a habit can theme a whole contest across skills.

---

## 1. Scorecard

"v2 spec" is §3.7 as written. The verdict says why ours is way better. Where v2 was only at
parity (or below), the verdict names the upgrade that fixes it.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Three sidebar sections | Contests & Challenges, Contest Rankings, Leaderboards: three nav items, three trips | One Compete section (R1: sidebar item; avatar menu on phone), four pages under a sub-nav | Today's challenge pill starts question 1 in one tap. A Compete key map; board scopes switch from cache in under 100 ms (C24) | **WAY BETTER already in v2** (one section, always live). **C24** makes it 1 tap to Q1 and 0 to your rank. Theirs takes about 8 actions and a wait for the contest to close, behind a paid plan. |
| 2 | Global Leaderboard card | "GLOBAL LEADERBOARD", Rankings link; "No rankings yet. Finish a contest to be the first on the board." | E: THIS WEEK · POINTS, the top 5, then your row | #1, then you ± 2 with movement and the gap. Chips for Points · Over par · Climb. Par rows fill it when fewer than 5 have played (C10, C5, C6) | v2 PARITY: the same top-5 card, the same five names every week. **C10 + C6 → WAY BETTER.** It shows your race and is never empty. |
| 3 | Your Contest Stats card | Trophy, "Not ranked yet", then your global rank | D: rating, level and six rank tiles | Every tile carries movement and its next milestone ("40 pts to top 10%"). The rating becomes a card with four domain rows and "Level 4 in +17 ≈ 2 hard rights". A rival line with Race (C10, C11, C9) | v2 PARITY: more static numbers of the same kind. **→ WAY BETTER.** Each number says where it is going and what moves it. |
| 4 | Active contests list | Posted by hand; empty on both walks | Daily and Sprint always live; Weekly or Final and the next Sprint upcoming; Private | Adds Trap of the week, Rush and the Word Sprint (C12–C14). Each row says what it trains and shows your par against your last result (C7) | **WAY BETTER already in v2** (never empty). Now every row also says why to enter. |
| 5 | Contest types | Daily / Weekly / Seasonal (bundle), never seen live | Daily, Sprint, Weekly Module, Seasons + Season Final, Private | Trap of the week: one misconception habit in every question, across skills. Rush: an adaptive run that ends on three strikes. Word Sprint: Reading & Writing vocabulary (C12–C14) | **WAY BETTER.** Eight kinds that schedule themselves. Two of them exist only because every wrong option names its misconception and the bank never runs out. |
| 6 | Contest tiers by plan | Free: none. Pro: standard. Elite: prize contests | Everything free | Unchanged | **WAY BETTER.** Free. |
| 7 | Scoring rule | Points by difficulty plus a raw speed bonus | 10 / 20 / 30, +5 within a flat 95 s, +10 finish | +5 within each question's own time budget (easy 1:05, medium 1:35, hard 2:06; C3). Par and Over par: the points a student at your rating is expected to score on your ten, and a board ranked on beating it (C5) | v2 PARITY in shape. A flat 95 s is free on easy questions and pushes students to rush hard ones. **C3 + C5 → WAY BETTER.** It rewards real SAT pacing and gives every level a score it can beat today. |
| 8 | Integrity rules | Fullscreen; switching tabs, leaving fullscreen, copying or pasting voids the open question at once | Void after 5 s hidden or on copy/cut/paste; optional fullscreen; too fast → unranked | **Verify, don't void.** A flagged right answer is confirmed at hand-in on a strict twin, and keeps its points if the twin is right. Copying an expression into our calculator is free. Too-fast answers are confirmed too (C15) | v2 PARITY: their penalty with a grace, and it voided copying a stem into our own Desmos. **C15 → WAY BETTER.** A phone notification never costs a minor a point, and a looked-up answer has to be repeated on new numbers. Only an unlimited twin supply allows that. |
| 9 | One attempt, delayed reveal | "One attempt per contest. Answers are revealed after the contest ends." | The key after each question (twins); ghost sittings of closed contests | Rematch the misses on new numbers in 2 days, with the same traps (C2). Race any finished run (C8) | **WAY BETTER already in v2.** Now a finished contest keeps teaching and keeps being playable. |
| 10 | Resume limit | Over the limit, the attempt is scored 0 | Leaving skips the open question and stops the clock; nothing zeroes | A blip or leave during a question is confirmed, not zeroed (C15) | **WAY BETTER.** |
| 11 | Per-contest stats | Score / Correct / Incorrect / Skipped / Voided | The same counts, the points parts, mastery bars, mistakes opened and closed | **Debrief:** points lost by cause and by misconception, what each miss cost in places ("Q6 right → #2"), Fix it · 3 on same-trap twins, a Rematch in 2 days, time against each question's budget (C1–C3) | v2 PARITY: the same five counts. **C1–C3 → WAY BETTER.** A result becomes a priced to-do list. |
| 12 | Anonymous names | "Anonymous student" on some boards | Hidden rows keep their rank as "Anonymous" | Hiding costs nothing: par, your own-best and SAT-pace pacers, and rivals shown only to you (C5, C8, C9) | **WAY BETTER already in v2** (ranks stay honest). |
| 13 | Performance Summary | Empty, with "Browse contests" | Ten tiles and a Top % / Rating chart | A "Since last week" line whose parts link to their drills. An Over par series on the chart. A Records row (C10, C5, C21) | v2 PARITY: a richer dashboard that points nowhere. **→ WAY BETTER.** |
| 14 | Contest Leaderboard picker | "Pick a contest you've finished to see how you placed." | A select, then a mini board | Folded into Contest history. Each row expands in place to your strip, a mini board, the debrief's top row, the follow-up and Race (C22) | v2 PARITY, and a duplicate of History. **C22 → WAY BETTER.** One list, one tap, with the next action. |
| 15 | Your Rankings card | Global rank, Contests played | A table: Everyone / Country / classes × Week / Month / Season / All | Every cell adds movement and the gap to the next place. New rows: Following, My level, Same exam date (C10, C9) | v2 PARITY. **→ WAY BETTER.** |
| 16 | Time Analysis | Average seconds per answered question by difficulty; "under pressure" copy | Pace ×4 views against the field and a flat 95 s | Reads U7's `progress.pace` with a contest filter: tier budgets, each row's drill, time-sink and banked trends. A Time block on every result (C3) | v2 PARITY: numbers with no action, and a second pace calculation beside U7. **C3 → WAY BETTER.** |
| 17 | Badge Progress | Empty | The Compete badges through R25, with progress and dates | Go on every badge in progress starts what advances it. Rarity ("earned by 4%"). New ladders: Over par, Won back, Rush, Trap-proof week (C23) | **WAY BETTER already in v2.** Go makes progress drive practice. |
| 18 | Contest History | Empty list | A table with kind and sort filters, R·W·S·V, rank, top %, rating Δ | Over par and Follow-up columns, an "Open follow-ups (n)" filter, rows that expand (C22) | v2 PARITY: a log. **C22 → WAY BETTER.** A to-do list. |
| 19 | Rankings layout | Two-column grid of six cards | Six ordered sections, two-column where noted | Adds the Rating card, Trap Index, Rivals, Records and the level ladder | **WAY BETTER already in v2.** Every section works and says what moves it. |
| 20 | Leaderboard hero and podium | Centred title, a large empty top-3 space | Podium 2 · 1 · 3 with values; empty cards read "Open" | A "Your path" line under it ("#12 · 60 pts to top 10 · 140 to the podium"). The podium follows the metric, so Over par and Climb give every level one to reach. Par rows instead of "Open" (C10, C5, C6) | v2 PARITY. **→ WAY BETTER.** |
| 21 | Period control | Weekly / Monthly (default) / Yearly | Week / Month / Season / Year / All, and 7d (R3); reset time stated | Unchanged | **WAY BETTER already in v2.** The season ends on a real SAT date and the reset is stated in your time. |
| 22 | Scope | Global ↔ your country | Everyone / Near me / Country / each class / same exam date (R3) | Adds Following, My level (± 1), Classes (class rows) and your extended-time placing (C9, C18, C17) | v2 PARITY in kind. **→ WAY BETTER.** Every student has a board of people they actually race. |
| 23 | Metric | Contest Points ǀ Overall Score | Points / Rating / Questions right / Test score | Adds Over par and Climb, a Rating sort by Change, and the Domain select for Rating (C5, C10, C11) | v2 PARITY: it ranks ability or volume. **→ WAY BETTER.** Two boards reward improvement, and the skill board splits by domain. |
| 24 | Leaderboard table | RANK / USERNAME / ACCURACY / TIME; scrolls without end to "No more rankings yet." | Rank / Student + level / metric / Accuracy / Avg time / Contests; paging; you-bar | Move and Gap columns, level separators, Find a student, a you-bar naming the cheapest way past the next row ("22 pts · one medium right at pace"), row actions Race / Follow / Compare (C10, C8, C9, C6) | v2 PARITY: a list to read. **→ WAY BETTER.** |
| 25 | Profile Performance Snapshot | Global Rank 128, Country Rank 43, with no contests played | Me Boards: ranks, "—" until a ranked contest | Movement and gap from one source, `compete.ranks` (U11, C10) | **WAY BETTER.** Honest ranks with direction. |
| 26 | Profile Achievements | Four hard-coded tiles; "View All" is dead | The 4 latest earned + All badges | Go on each (C23) | **WAY BETTER.** |
| 27 | Ranked pill and percentile on the report | "Practice test — not ranked"; "N% scored at or below you on their first attempt" | R16's pill and percentile | The pill adds this sitting's place on the Test score board and your Climb ("#41 of 212 this month · Climb +90, ahead of 74%"), with links (C10) | v2 PARITY: their sentence. **C10 → WAY BETTER.** A sitting is placed on a live board and on a fair improvement race. Other report upgrades are `reports.md`'s. |
| 28 | Username on boards | The Google account name | R12 handles, unique, name / anon / hidden, name reports | Follow and Find a student by unique name (C9) | **WAY BETTER already in v2.** |
| 29 | Question of the Day | Two a day, one attempt, a "1 day" streak pill; the right choice not shown | Today owns it (R27); the contest page's QOTD panel with the spread, past days and streak | Unchanged here (Today's T14) | **WAY BETTER** (`today.md` #14). |
| 30 | Classes and homework (hidden); /teacher | Hidden pages; homework with due dates; a teacher dashboard | Classes (R4); class contests with a due time; an owner results table with CSV | A class streak with member dots and nudges, a Classes board ranked fairly on Over par, contests built from the class's open traps, a results footer naming each question's top trap with Assign a repair, and the public grid view (C18, C19, C20) | v2 PARITY: their dashboard, visible and free. **→ WAY BETTER.** A class has a daily reason to show up together. |
| 31 | Share | `navigator.share`, which froze the page; a shared QBank landing | Copy result (plain text) + Challenge a friend | **Race links.** The copied link races your run on twins, ranked if it is the friend's first sitting, and the result comes back to your inbox (C8) | v2 PARITY: a brag that asks nothing. **C8 → WAY BETTER.** A share is a fair race that needs no account. |
| 32 | Nothing is live without staff | Empty on both walks | Self-scheduling contests; field lines at ≥ 5, top % at ≥ 10, podium at 3 | Par rows at Levels 3/5/7/9, your best and 7-day average rows, a field line that falls back to every first try on the type and then to your level's expectation, SAT-pace and own-best pacers (C6, C8) | v2 still looks empty with 7 learners. **C6 + C8 → WAY BETTER.** Meaningful from the first sitting with nobody else on the site, and it never invents people. |
| 33 | Contest timing | One fixed fullscreen time | Fixed clocks; `prefs.test_timing` ignored | 1.5× and 2× in every contest, never shown publicly, placed among extended sittings (C17) | v2 BELOW: it shut out 504/IEP students, although Tests supports them. **C17 → WAY BETTER.** |

---

## 2. Accepted upgrades

Grouped by how directly they move the score. Each gives why, screens and components, controls
and states, data and endpoints, how it uses the rest of the site, and acceptance checks.
Learner codes start `a:v2revc`. Curl checks run on S8's port, `localhost:8028`, with
`-H 'X-Tz: 0'` unless stated. Unit checks live in `server/checks/s8.py`.

### Layout after these upgrades

**Overview `/compete/`**, desktop `2fr 1fr`:
```
main: A Daily Challenge (par, forecast, follow-ups) · B Contests (8 kinds) · C Question of the day
side: D Your stats (rating card, movement) · Rivals · H Season · E Board (#1 + you ± 2)
      · Traps this week · F Next badges (Go) · G Your classes (class streak)
top, when a season has just closed: the season recap card (C21)
```
Phone order: recap, A, D, Rivals, H, B, E, Traps, C, F, G.

**Contest page** main column: state panel → **Debrief** (C1) → **Time** (C3) → Board (List ·
Grid, C20) → Review → Traps. Side: rules, pacer select (C8), QOTD panel, entrants, owner
controls. Phone: one column in that order, with a 56 px thumb bar (C24).

**Leaderboard:** controls (Metric · Period · Scope · Domain · Subject) → podium → "Your path"
line → Find a student → table.

**Your rankings:** Performance summary (with "Since last week") → Rating card (C11) | Pace (C3)
→ Records (C21) → Trap Index (C12) → Rivals (C9) → Badges → Seasons → Level ladder (C11) →
Contest history (C22). The "How you placed" picker goes (C22).

---

### A. Every result is the next study step

#### C1. Debrief: where your points went, what each miss cost in places, and Fix it

*From: outcomes #1, experience #3, unfair-advantage #4, the per-contest-stats gaps of all three.
Effort S–M. Builders: S8 (`compete.debrief`, the block in `compete-ui.js`), F4
(`progress.causes(session=)`, T7's function), F3 (`UI.twinSheet`, T5), S4 (renders the block in
the contest-mode summary through `compete.state_extra`).*

**Why.** "8/10, #4" says nothing about what to do next. Named misconceptions let us price each
miss and serve the same trap again on new numbers. Theirs has five counts and hides answers
until the contest closes, and their options carry no labels, so they cannot total points by
mistake or re-serve a trap.

**Block** on the result panel, after the tiles, before the mastery rows. `h2` "Where your points
went" + `meta` "90 of 260 left".
* **Points bar.** One stacked horizontal bar, "260 possible → 170 scored". Lost segments, each
  labelled with points and count (never colour alone; a hidden table lists them):
  * the T7 causes of the wrong answers, from `progress.causes(learner, tz, session=sid)`:
    "Traps −50 (2)", "Slips −20 (1)", "Clock −30 (1)", "Entry −20 (1)", "Gaps −30 (1)";
  * "Skipped −30 (1)", "Voided −20 (1)";
  * "Over budget −15 (3 right but slow)": pace bonus not earned on right answers;
  * "Finish bonus −10".
  Each segment is a button. It sets the Review filter below to exactly those questions and
  scrolls there.
* **Headline**, from the counterfactual below: "Q6 right would have put you #2: one fix from the
  podium." When no single fix moves you: "All of them right → #1 of 37."
* **Rows**, one per lost item, sorted by places gained, then points:
  * "Q7 · Advanced Math · Hard · fell for Swapped the columns · −35 · right → #2 (+5 places)";
  * a `rushed` chip on a wrong answer given in under 25% of its budget (P16's word);
  * the last row: "All of them right → #1".
  * The counterfactual re-ranks your points plus that slot's value against the board as it
    stands, with competition ranking (C16). A slot's value is its tier points, +5 if its time
    was within budget, +10 when it was your only skip or void (the finish bonus).
* **By misconception** line: "Lost 70: 40 to Swapped the columns (2 slots) · 30 to a skip."
* **One action per row:**
  * trap, slip, gap or entry → quiet **Fix it · 3**. It opens T5's `UI.twinSheet` with
    `{from_session: sid, only: [qid], each: 3, source: 'twin', parent: sid, want: {template:
    escaped norm}}`. The collapsed header recalls the original. The three twins show the same
    trap option (F5 walks up to 40 seeds for it, else serves the nearest).
  * clock or over budget → **Speed drill · 8** (U7's body on those templates, `per_q: 1.0`).
  * skip → **Try it now** (the twin sheet, `each: 1`).
  * The whole block's primary: **Rematch my misses · n** (C2).
* **Weekly roll-up** on Your rankings, under the summary: "This week: −210 pts to traps, 60% of
  it one trap: Swapped the columns" + **Fix it** (the twin sheet over that norm's templates).
* **Ghost sittings** get the same block. The counterfactual reads "would have placed #2".
* **Test-window kinds** (Weekly, Final) get it too. Their per-question time comes from R7's
  `qstate.ms`; the "Over budget" segment is left out until it exists.

**Data.** `GET /api/contest/{cid}/debrief` → `{subject, max, points, rank, players,
lost: [{qid, slot, kind: 'trap'|'slip'|'clock'|'entry'|'gap'|'skip'|'void'|'pace'|'finish',
template, tier, topic, norm, label, pts, rank_if, places, rushed}], by_norm: [{norm, label, pts,
slots}], all_right_rank}`. The `lost` rows sum to `max − points`. 403 until your sitting is
finished. `compete.debrief(sid)` is pure over the sitting, its attempts and the board.

**States.** A perfect sitting: "Nothing left on the table. 260 of 260." + Race your run (C8).
Fewer than 2 ranked players: the rank parts are hidden and the points parts stay.

**Acceptance.**
1. A daily sitting with 2 wrong (two different reasons), 1 skip and 1 right-but-slow answer →
   `/debrief.lost` has 4 rows, Σ `pts` == `max − points`, and the wrong rows' `pts` equal their
   tier points (+5 when their time was within budget).
2. On a seeded board where one more medium right moves you from #4 to #2 → that row's
   `rank_if == 2` and `places == 2`.
3. **Fix it** on a trap row posts a body whose `want[template]` equals the attempt's norm; the
   three served questions each regenerate with an option whose norm equals it (check in s8.py).
4. Browser: clicking the "Traps" segment leaves only those questions visible in Review, and the
   filter underline reads "Selected · 2".

#### C2. Rematch and Won back: your misses on new numbers, two days later

*From: outcomes #1 (the delayed rematch), unfair-advantage #4, P18. Effort S. Builders: S8
(`POST /api/contest/{cid}/rematch`, won-back), F5 (P18 `rematch` + `want` on scope misses; the
409 lifted, §3.2), F2 (Up next picks up `rematch_due`, already in P18).*

**Why.** A fix right after the feedback feels learned and fades. A retry on fresh numbers two
days later is what makes it stick. Calling it "winning points back" gives a reason to come
back. A fixed bank has no second copy of each item.

**Result panel.** The Debrief's primary **Rematch my misses · 3** with a seg under it:
**In 2 days** (default) · **Now**. Helper: "Same types, new numbers, the same traps. Coming back
in 2 days fixes them for longer."
* In 2 days: `cfg.rematch_due` = your local day + 2 is stored on the contest sitting. The chip
  then reads "Rematch · Thu". Up next shows "Rematch · Tue's Daily · 3 questions · ~5 min" that
  day (P18's rule) and on each later day until it is done.
* Now: the drill starts at once.
* Either way: `POST /api/drill {rematch: sid, scope: 'misses', source: 'rematch'}` (P18). Each
  missed, skipped or voided slot is served as the same template, tier and format on a fresh
  seed. A slot whose miss had a named reason is drawn with `want {template: norm}`, so the same
  trap option is on screen. Untimed, key after each question, unranked, unrated.
* A right answer is a clean answer (R8): it closes the trap, and R9's check-ins follow.

**Won back.** When the rematch finishes, compete reads P18's `slots` (`change` per slot):
* `won_back` = Σ tier points of slots whose change is `fixed`; `of` = Σ tier points of the
  missed slots;
* the contest's result panel shows "Won back 50 of 70 · Thu", with ✓ / ✕ against each original
  mark;
* History's Follow-up column (C22): "Rematch Thu", "Won back 50/70" or "—";
* the "Won back" achievement ladder (C23).

**Data.** `POST /api/contest/{cid}/rematch {when: 'now' | 'later'}` → `{session}` or `{due}`.
The contest payload's `me.followup` = `{due, session, won_back, of}`.

**Acceptance.**
1. After a daily with 2 wrong and 1 skipped, `POST /rematch {when:'later'}` sets `rematch_due`
   to the local day + 2, and `GET /api/next` for that day has an item whose title starts
   "Rematch".
2. `{when:'now'}` serves 3 questions with the original slots' templates, tiers and formats and
   different seeds. A slot with a named miss regenerates with an option whose norm equals the
   original's.
3. After the rematch with 2 of 3 right → `me.followup.won_back` equals those two slots' tier
   points, and the trap of each right slot is closed.
4. `POST /api/drill {rematch: <unfinished contest sitting>}` → 409.

#### C3. Pace against each question's budget: the pace bonus, the Time block, and a guide that fades by the Final

*From: outcomes #3, the scoring and time-analysis gaps of all three, P16, U7. Effort S–M.
Builders: S8 (points, the Time block data, the Pace section), F5 (`budget_ms` frozen on each
served question, P16), F4 (`progress.pace(…, only='contest')`), S4 (renders P16's Time card in
the contest summary), S5 (the Final forces the pace guide off).*

**Why.** Points are lost to three-minute sinks as much as to content. A flat 95 s treats every
easy question as fine and every hard one as slow, and v2's Pace card was a second pace
calculation beside U7's. Their "speed bonus" rewards rushing.

**Scoring.** The pace bonus becomes **+5 for each right answer that stands (not voided, C15)
given within its own budget** (`q.budget_ms`, frozen at serve time, × the timing factor
of C17). It applies to the answer-clock kinds except Sprint and Rush. The Daily's maximum stays
260. The lobby's rule line reads "+5 for each right answer within its time budget (easy 1:05 ·
medium 1:35 · hard 2:06)."

**Result panel "Time" block** (after the Debrief). It is P16's summary Time card, which S4
already builds for the session summary:
* one bar per question against its budget tick, plus a graphite tick at the field median for
  that slot (twins make slots comparable; shown at ≥ 5 answers, else C6's fallback);
* "Time sinks · 2": the questions over 2× budget, with P16's saved-time line ("6:40 on 2
  questions, both wrong. Moving on at the budget would have left 3:40, about 2 questions.");
* a **Banked** line: "Easy: median 0:41 against 1:05 · 1:12 banked for the hard ones";
* two pills from U7's quadrants: **Speed drill · {slowest skill answered right}** and **Careful
  set · {skill answered fastest and wrong}**.

**Your rankings › Pace** (replaces §6.2 Pace). It reads `progress.pace(learner, days=90,
only='contest')` (U7's function with a filter), so Me and Compete show one calculation.
* The four views stay: By difficulty · By domain · Right vs wrong · Under pressure.
* The flat 95 s line becomes each tier's budget line.
* Each row carries its U7 quadrant action (Speed drill, Careful set, Learn it untimed, Keep
  warm).
* Two trend rows over the last 10 contests: "Time in sinks per contest" and "Banked on easy",
  each a 10-point strip with its latest value.

**Test window.** The Weekly Module follows the student's `test_pace` pref (Tests' pace guide
tick). The Season Final forces it off (`cfg.pace = false`), and its lobby reads "No pace guide:
test conditions."

**Acceptance.**
1. A daily where Q2 (easy) is right in 70 s and Q5 (medium) right in 90 s → Q2 earns no pace
   bonus and Q5 earns +5 (`result.points_parts.pace` counts one).
2. With every answer right within budget, `points == 260` and `points_parts == {base:200,
   pace:50, finish:10}` (§3.7.8 item 9 still holds).
3. `/api/compete/me.pace` equals `progress.pace(learner, days=90, only='contest')` field for
   field (s8.py).
4. The Final's session payload has `cfg.pace == false`, and the test window renders no pace
   tick for it.

#### C4. Season Final → your last week, and a test-day card

*From: outcomes #9. Effort S. Builders: S8 (`compete.final_focus`, the block, the card page),
F2 (`next.stage` reads it in the taper), S5 (per-question time via R7).*

**Why.** The Final sits a week before the SAT, exactly where T13's taper starts. A plan built on
a full timed rehearsal targets the few traps that cost the most and the pacing rule, instead of
cramming new content. Theirs ends a "Seasonal" contest at a label.

**Result panel, after the band: "Your last week".**
* Day rows from the day after the Final to the eve, read from T13's `next.stage` preview, with
  the Final's items first:
  * the 3 traps that cost the most points in the Final (C1's `by_norm`), each "Fix: Used the
    diameter as the radius · ~10 min";
  * "Skip first on test day: Circles, Percentages": skills with a Final question over 2× budget
    that was also wrong (they join U7's list, which Tests' checklist reads);
  * T13's own rows: rehearsal, sweep, eve rest.
* No second schedule. T13 runs the week; this block shows it and puts the Final first.
* Quiet **Test-day card** → `/compete/contest/?id=final-…&card=1`.

**Test-day card.** A print page (`@media print`, no chrome), one sheet at A4 and Letter:
* the pacing rule from P16's budgets: "Move on at 2× the budget and come back: easy 2:10 ·
  medium 3:10 · hard 4:12";
* the skip-first list;
* the 3 tells of your top habits (U6);
* the Final's band and route;
* the doors time from Tests' checklist (wording per open question 10).

**Data.** `compete.final_focus(learner)` → `{sid, traps: [trap ids], skip_first: [topics], band,
route}`. F2's taper lists those traps first until each closes.

**Acceptance.**
1. A Final with 2 wrong answers over 2× budget in circles → `final_focus.skip_first` contains
   `circles`.
2. With exam date = Final + 7 and `final_focus.traps = [t]`, `GET /api/next` during the taper
   lists trap `t` before any other trap.
3. The card page has no `nav`, and a Playwright print-to-PDF of it is one page at A4 and
   Letter.

---

### B. A race every student can win

#### C5. Par and Over par: your own expected score, and boards any level can top

*From: outcomes #4, unfair-advantage #2, experience #1 (par rows). Effort M. Builders: S8
(`compete.par`, metric `net`), F4 (P11's `item_ratings`, calibrated from every clean first
try), S4 (the Par tile in the summary).*

**Why.** A raw rank tells a Level 2 student they lost again, so they stop. Beating par tells
them they did better than expected today, which keeps them coming back, and it is a board they
can actually top. Theirs cannot compute par: their items carry no ratings. Ours are calibrated
from every answer the site records, in every mode (P11).

**Par.**
* For each slot i: `E_i = 1 / (1 + 10^((R_item − R_you) / 400))`, with `R_item` from
  `item_ratings(template, tier)`.
* `par.base` = round to 5 of Σ `E_i × tier points`. `par.right` = Σ `E_i` (one decimal).
* `par.points` = `par.base` + 5 × Σ `E_i × q_i` + 10, where `q_i` is the share of that type's
  clean rights given within budget (prior 0.75). It is the par in board units, used for par rows
  (C6).
* `R_you` is frozen at start as max(`learners.rating`, 30-day peak − 100), so throwing a sitting
  to lower tomorrow's par doesn't pay.
* It is stored at start in `sessions.result.par = {base, right, points, rating, rough}`. `rough`
  is true while you are Placing or any slot's item has n < 30.
* **Net** (over par) = base points − `par.base`. Pace and finish are left out, so Net is
  time-neutral (C17).

**Surfaces.**
* Lobby and Today's card: "Your par 60 · about 3.8 right" + helper "What a student at your
  rating scores on these 10, on average." A Placing student sees "Par (rough)".
* Result: a **Par** tile, "+15 over par · base 75 vs par 60".
* Contest board: a Net column and an underline toggle **Points · Over par** that re-sorts it.
* Leaderboard: metric **Over par** = Σ Net over ranked sittings in the period. It counts the
  Daily, Weekly, Final and Trap of the week; Private, Sprint, Rush and Word Sprint are left out. Listed: placed students
  (30 rated answers) with ≥ 3 sittings in the period. A Placing student's you-bar reads "Over
  par ranks after placement · 12 of 30".
* Its podium is the Over par podium, so each metric has its own reachable top three.
* A chip "Over par 4 Dailies running" on the Daily card.
* Rankings chart: an **Over par** series beside Top % and Rating.

**Data.** `compete.par(learner, slots, at)`; board entries add `net`; `GET
/api/leaderboard?metric=net`.

**Acceptance.**
1. `par` for `R_you = 1100` against three slots of 10 / 20 / 30 points whose items are all
   rated 1100 → `base == 30`, `right == 1.5` (s8.py).
2. The lobby's `me.par.base` equals the finished sitting's `result.par.base`.
3. A learner whose rating fell 150 in a week gets `result.par.rating == peak − 100`.
4. `/api/leaderboard?metric=net&period=week` lists no learner with fewer than 30 rated answers
   or fewer than 3 sittings in the week.

#### C6. Never an empty board: par rows, a field line with fallbacks, level separators

*From: experience #1, the field-statistics gap of outcomes, the small-field gaps of all three.
Effort S. Builders: S8 (`board().pars`, `compete.field_line`), S4 (the verdict line via
`state_extra`).*

**Why.** With 7 learners, every threshold in the spec leaves the page blank, as theirs was on
both walks. Benchmarks computed from the question ratings place a student meaningfully from
their first sitting, with nobody else on the site, and never invent people.

**Par rows** on every fixed-slot contest board (Daily, Weekly, Final, Trap, Private):
* rows for Levels 3, 5, 7 and 9 at their midpoints, plus "Your level" when it is none of them;
* each reads "Level 5 par · 7.5 right · 175 pts", computed as C5's `par.points` over the
  contest's canonical slots;
* a dashed-outline row with a flag glyph and no rank numeral, placed at its points between real
  players;
* never counted in players, ranks, top % or the podium;
* labelled "par (estimated)" until every slot's item has n ≥ 30.
* **Your rows**: "Your best Daily · 230" and "You, last 7 days avg · 184", styled the same way.
* A **Pars** switch in the board header, on by default, stored per viewer in localStorage.
* The result panel's placement line: "Between Level 5 and Level 6 par · 12 above your 7-day
  average."

**Field line** (the verdict after each answer, and each Review row), first match:
1. the contest's own ranked field on this slot, when ≥ 5 have answered: "62% of 37 got this
   right";
2. every first try on this (template, tier) in any mode, when ≥ 20 (R8 exclusions): "64% of
   1,284 first tries on this type";
3. the expectation at your level: "Expected at Level 4: 58%".

Review's "How the field answered" falls back the same way: below 5 contest answers it shows the
misconception spread of the type's first tries in all modes, labelled "on this type, all
modes".

**Boards elsewhere.**
* The Rating leaderboard gets level separator rows ("Level 5 · 1,251").
* The Leaderboard's empty period shows the par ladder (Levels 1–10 with their par on today's
  Daily) + "Your spot appears after your first ranked contest" + pill "Start the challenge".
* The Overview preview (E) fills with par rows and your best when fewer than 5 have played.

**Data.** `board()` returns `pars: [{level, right, points, rough}]` and `mine: [{label,
points}]`. `compete.field_line(template, tier, cid, slot, rating)` → `{source: 'contest' | 'type'
| 'expected', share, n, level}`.

**Acceptance.**
1. A daily board with 1 player returns 4 or 5 `pars`; `players == 1` and the player's rank is 1.
2. A verdict on a slot with 3 contest answers and 40 first tries on the type → `field.source ==
   'type'` and `n == 40`. With 10 first tries → `'expected'`.
3. Browser: the par rows carry no rank text, and switching Pars off hides them after a reload.

#### C7. Every lobby forecasts your result and offers a warm-up

*From: unfair-advantage #10, the outcomes "Practice for it" gap. Effort S. Builders: S8 (the
lobby, `POST /api/contest/{cid}/warmup`), S3 (Today's card line).*

**Why.** A student who knows what to expect, and shores up the weakest part first, enters
instead of putting it off. Theirs shows a title and a plan gate. v2's "Practice for it" was a
generic domain drill.

* **Lobby line**, and on Today's card and each Contests row: "Par 60 · about 3.8 right · likely
  #8–#14 of ~37".
  * The range maps `par.base ± sd` (sd = √Σ `E_i(1 − E_i) × tier²`) onto this contest's ranked
    points so far, or the previous day's Daily when this one has fewer than 10.
  * It is hidden until 10 ranked players exist.
* **Ladder cells** show your chance on that slot, from the same `E_i`: a thin fill bar and
  "34%". Hover or focus: "Q9 · Geometry & Trig · Hard · your chance 34%". Domains only, never
  the skill or template.
* **Warm up · 6** (replaces "Practice for it"): 2 questions each on the topic and tier of your 3
  lowest-chance slots, drawn from templates **not** in the contest's slot list, key after each.
  It is offered only before you start.
* After the contest, the result reads "Warmed up on Circles · Q9 right".
* Contests rows add a **Trains** line ("module pace and routing", "Advanced Math fluency", "this
  week's trap: percent of what?") and "par 290 · last week 260".

**Data.** `GET /api/contest/{cid}` → `me.par`, `me.forecast {lo, hi, of} | null`, `ladder[i].
chance`. `POST /api/contest/{cid}/warmup` → `{session}` (a drill with `templates` = those topics'
templates minus the slot templates, `tiers`, `count: 6`, `cfg.warmup_for = cid`); 409 once your
sitting has started.

**Acceptance.**
1. The warm-up drill's served templates never include any template of the contest's `spec.slots`
   (s8.py over 20 seeds).
2. With 9 ranked players `me.forecast` is null; with 10 it has `lo <= hi`.
3. `ladder[i].chance` equals `E_i` for the learner's frozen rating, to 2 decimals.

#### C8. Races: race any run, your best, par or SAT pace; a race link is the share

*From: outcomes #8, experience #2, unfair-advantage #1, the Share gaps of all three. Effort M.
Builders: S8 (`compete.pacer`, the race param, the lobby select, `compete-ui.js` `UI.pacer`), S4
(the rail in the session header through `state_extra`), S1 (the feed merges race items).*

**Why.** A new free site's boards stay thin for months. Racing a near-peer or your own best
keeps effort up with nobody online, and every race is more retrieval on the same skills with new
numbers. Theirs allows one attempt, hides answers and has no head-to-head, and their Share froze
the page. A fixed bank cannot allow a replay without handing out the answers.

**Pacers** (a select on the lobby, "Race: No one · Your best · SAT pace · Field median · Level N
par · {a rival or followed student} · {the link's sender}"):
* **a run**: another student's ranked sitting (or best Sprint / Rush run) of this contest.
  Allowed: rows with `board = name` or `anon` (R12), and anyone whose own race link you
  followed. Hidden rows have no row menu (R12) and cannot be raced.
* **your best**: your best finished sitting of the same kind (a past Daily for the Daily).
* **SAT pace**: one question per budget, no marks ("SAT pace: 1:35").
* **field median**: the slot's median time and % right (≥ 5 answers).
* **Level N par**: right where `E_i ≥ 0.5`, at the budget's time.
* Defaults: Sprint and Rush → your best this week; a race link → its sender; otherwise No one.

**In the runner** (practice session; not the test window, which keeps test conditions):
* A race rail under the progress bar: two 6 px tracks, you in orange, the pacer in graphite, and
  a right-aligned line "You 5 ✓ · 120 · Ada 6 ✓ · 140 at this point".
* The pacer advances by its own recorded answer-clock times measured against **your** answer
  clock, so it freezes while you read a rationale.
* After each verdict on the same contest: "Ada: ✓ in 0:48". For a pacer from another contest
  (your best Daily of another day): only running points at the same clock time.
* The server sends a pacer mark only for slots you have already answered, never its numbers or
  picks.
* Pref `race_rail` (default true) hides the rail; the session's More menu toggles it.

**Ranked or not.** Racing never changes ranking. A race that is your first sitting of a live
contest is your ranked sitting; twins mean the pacer reveals nothing about your numbers.
Otherwise it is a ghost sitting ("would have placed").

**End.** "Beat Ada by 30 pts", or "Ada by 10: she was 1:12 faster on Q7". On the same contest the
Compare sheet opens on its own, with the head-to-head record (C9). **Race again**: a new run for
Sprint and Rush, a ghost sitting otherwise.

**Race links.**
* Copy result's link becomes `…/compete/contest/?id=daily-2026-09-23&race=<pid>`. The copied text
  keeps its first three lines, and its fourth reads `Beat 170: https://…&race=…`.
* A result panel quiet **Race link** copies just the link.
* The landing is the lobby: "Race Ada · 8/10 · 170 pts · 11:42", one Start pill, and the rules.
  A first visit mints a learner code as usual.
* The sender gets one feed item (U25) per racer per contest: "Sam raced your Daily · Sam 190 ·
  you 170 · Race back".
* Switching to hidden revokes every link (403 "This run is private now.").

**Entry points.** Board row menu **Race** (once you have finished, or the contest has closed);
Sprint and Rush results "Race your best · 240"; lobby select; Rivals card; history rows.

**Data.**
* `sessions.cfg.race = {kind: 'run' | 'best' | 'pace' | 'median' | 'par', target, sid, level}`
  (`target` is a learner id, server side only). `result.race = {them, you, won}`.
* `GET /api/contest/{cid}?race=<pid | best | pace | median | par:5>` → `race {label, level,
  points, right, secs}` or 403.
* `GET /api/drill/{sid}` → `pacer {label, level, at: n answered by the pacer at your clock,
  points_at, marks: [≤ your answered count]}`.
* `compete.learner_of(pid)`: an in-memory pid → learner index, rebuilt when a learner row is
  added. `ponytail:` one HMAC per learner at rebuild; fine to ~50k learners.

**Acceptance.**
1. `GET /api/drill/{sid}` after answering 3 of 10 in a race → `pacer.marks` has exactly 3 items.
2. With a verdict showing for 10 s (clock not running), `pacer.at` doesn't change between two
   reads.
3. `?race=<pid of a hidden learner>` → 403. `?race=<pid of a named learner>` → 200.
4. A race started on today's live daily by a learner with no sitting → the finished sitting has
   `ranked == 1`.
5. Copy result's text: line 3 is 10 characters from `■□·`, and line 4 starts `Beat ` and
   contains `&race=`.

#### C9. Rivals and Following: people you actually race

*From: experience #7, unfair-advantage #7, the scope gaps. Effort S. Builders: S8 (`follows`,
`compete.rivals`, scopes `following` and `level`, the card and table), S1 (the feed merges rival
items).*

**Why.** A student at #300 has nobody within reach on a global board. Three close opponents
and a running score against each give a race every day. Theirs has Global ↔ Country only, and in
v2 a friends board needed a class, which needs a saved account (R4).

* **Follow** (row menu, and `F` on a focused row): named and handle rows. Private, one-way, at
  most 50, no follower lists, no messages. Following a student who later hides drops them.
* **Rivals**: three a week, picked lazily on the first request of the ISO week:
  1. students you follow within ± 200 rating, most recently shared contest first;
  2. then public learners with a ranked contest in the last 14 days and a rating within ± 100,
     widening to ± 200, then the nearest; same exam date first, then classmates;
  3. never a hidden learner.
* **Overview › Rivals** card (side column, above the board preview). Each row: name + 20 px
  level badge, "You lead 4–2 this season" (ranked contests both sat, by points), the last shared
  result ("Daily · Sep 23 · you 170 · them 150"), and **Race** on their latest run you haven't
  raced. Empty: "Rivals appear when 3 students near your level have played in the last two
  weeks. Until then, race your best run." + **Race your best**.
* The result panel adds "Rivals today: beat Maya · lost to Sam · Lee hasn't sat yet".
* The feed gets at most one rival item a day: "Sam beat your Daily by 20 · Race his run".
* **Scopes** on every board and the Leaderboard: **Following** (followed students + you) and
  **My level** (your level ± 1).
* **Find a student**: a field on the Leaderboard and contest boards. An exact public name (names
  are unique, R12) jumps to and highlights that row. Otherwise "No public student has that
  name."
* **Your rankings › Rivals** table: name, level, this season's record, last result, Unfollow.

**Data.** Table `follows(learner, target, at, auto INTEGER DEFAULT 0, week TEXT)`, PK (learner,
target); auto rows are the week's picks. `POST /api/follows {pid}`, `DELETE /api/follows/{pid}`,
`GET /api/compete/rivals`, `compete.h2h(learner, target, season)`. Board scopes `following`,
`level`; `GET /api/leaderboard?…&find=<name>` → `{offset}`. `progress.carry` moves `follows`.

**Acceptance.**
1. A learner at 1,080 with public learners active at 1,050, 1,120 and 1,400 → rivals are the
   first two, then the third.
2. A hidden learner is never an auto rival, and `POST /api/follows` on their pid → 403.
3. `scope=following` returns only followed learners and you; `scope=level` returns only levels
   within ± 1 of yours.
4. `find=ada` (a public "Ada" at rank 212) → `offset == 200` with a page size of 50.

#### C10. Where you stand: movement, the gap, and the cheapest way past the next student

*From: the podium, table, hub, stats, ranks and summary gaps of all three designers; U11. Effort
S–M. Builders: S8 (`rank_snapshots`, `compete.ranks`, the columns and lines), S1 (Me reads
`compete.ranks`), S6 (the report pill line).*

**Why.** A position without direction is a number to forget. Movement, the gap and the
cheapest next step turn every row into a goal, which is what U13 does for the rest of the site.

* **Snapshots.** `rank_snapshots(day, board, learner, rank, value)`, PK (day, board, learner),
  written lazily by the first leaderboard request of each UTC day for the boards `points:week`,
  `points:month`, `points:season`, `points:all`, `net:week`, `rating`, `rating:<domain>` and
  `right:7d` (U11 reads the last). Kept 90 days. `ponytail:` one full write per board per day;
  fine to ~20k learners.
* **Movement**: on the Week period since yesterday ("▲3 today"); otherwise since 7 days ago
  ("▲3 this week"); "new" when absent. The tooltip states which.
* **Board columns** (contest boards and the Leaderboard): **Move** and **Gap** ("+34" / "−12" in
  the metric's units, against you).
* **You-bar**: "You · #212 · 150 pts · 22 pts to pass #211 · one medium right at pace" + **Jump
  to me**. The gap to pass is their value − yours + 1, since equal values tie. The cheapest step is the smallest single answer worth at least the gap (easy 15,
  medium 25, hard 35 with pace; 10 / 20 / 30 on boards without pace), else "2 hard rights". For
  Rating: "about 3 hard rights at your level" (C11's formula). Right: "7 right answers". Over
  par: "beat par by 12 more".
* **"Your path"** under the podium: "#12 · 60 pts to top 10 · 140 to the podium · your average
  Daily is 170".
* **Overview E**: #1, a separator, then you ± 2, each with movement and gap. Metric chips
  **Points · Over par · Climb**.
* **Your stats tiles** (Overview D) and **Your ranks** cells: "#12 of 340 · top 4% · ▲3 · 7 pts to
  #11". New ranks rows: Following, My level, Same exam date (R3). A **Climb** row reads U11's
  `compete.climb`.
* **Leaderboard metrics** add **Climb** (U11: gain since your first scored sitting within your
  starting-band cohort; its period control is disabled, "since you started") and **Rating ›
  Sort: Rating · Change** (a "Most improved" board with its own podium).
* **"Since last week"** line above Your rankings' tiles: "Rating +46 (Algebra +60, Geometry −12) ·
  won back 3 traps · 2 time sinks in Geometry". Each part links to its drill or section.
* **Score report pill** (S6 renders it from `compete.test_rank(sid)`): "#41 of 212 on this
  month's Test score board · ▲3 · Climb +90, ahead of 74%", with links to both boards.
* **Me** reads the same `compete.ranks(learner)` (one source).

**Acceptance.**
1. After two days of snapshots, a learner who moved from #9 to #6 on `points:week` has `move ==
   3` on day 2's board.
2. With you at 150 and the row above at 171, the you-bar reads "22 pts to pass #211" and the
   step "one medium right at pace". At 160 above you: "11 pts" and "one easy right at pace".
3. `/api/me.ranks` and `/api/compete.me` give equal week, country and all-time ranks.
4. `GET /api/leaderboard?metric=climb` ignores `period` and returns `window` from
   `compete.climb`.

#### C11. Ratings by domain and skill, the next level in questions, and a measured level bridge

*From: outcomes #6, experience #11, unfair-advantage #9. Effort S. Builders: S8 (the Rating
card, the domain Rating board, the ladder table), F4 (P11's `skill_ratings`), S1 (Me's Rating
tile tooltip).*

**Why.** One rating hides where the points are. A rating per domain and per skill says where
the next 30 minutes pay most, and which contest trains it. Theirs has no rating at all, and v2
disabled the domain filter for Rating.

* **Source.** Skill rows are P11's `skill_ratings(learner, topic)` (every clean first try,
  contests included). A domain's rating is the n-weighted mean of its topics' ratings, and its
  n is their sum. Placing while a domain has n < 15 (a skill n < 10). The overall contest rating
  stays `learners.rating`.
* **Rating card** (Your rankings; a compact version in Overview D):
  * the overall badge (48 px): "Contest rating 1,084 · Level 3";
  * **Level 4 in +17 ≈ 2 hard rights at your level**: ceil(gap / (K × (1 − E_hard))), with K your
    current K and E_hard against the mean hard item rating;
  * four domain rows: glyph, name, 32 px badge, "1,240 · Level 4 · 86 answers · ▲40 in 30 days"
    (from `rank_snapshots`), a bar on the level ladder, and an expectation line from item
    ratings: "At 890 you'd get about 45% of medium Geometry questions";
  * a **Skills · 19** disclosure listing each topic the same way;
  * **Weakest** line: "Geometry & Trig · Level 3 (your others Level 5)" + pill **Practise
    Geometry & Trig · 10** (`{topics: its skills, zone: 'stretch', count: 10}`, P11) + quiet
    **Rush Geometry** (C13) + quiet "Sprint · Geometry week in 9 days · Add to calendar".
* **Result panel**: the Rating tile expands to domain deltas, "Algebra +18 · Geometry −6"
  (aggregates stored in `result.domains` at start and at finish).
* **Leaderboard**: the Domain select is enabled for Rating. It ranks that domain's aggregate
  among learners with n ≥ 15 there and a clean answer in it during the period.
* **Level ladder table** (Your rankings): Level · Rating · Students at it · Timed-section median.
  The last column is the median R16 `mean3` midpoint of learners at that level with a timed full
  section within 30 days, shown per level only when n ≥ 20 ("630 · 38 students"); otherwise
  "—". It is measured, never modelled. The same line is the level badge's tooltip.

**Acceptance.**
1. One clean right Geometry answer changes that topic's `skill_ratings` row and the Geometry
   aggregate, and leaves the other domains' aggregates unchanged.
2. `/api/leaderboard?metric=rating&domain=Geometry%20%26%20Trigonometry` orders by the Geometry
   aggregate.
3. With 19 learners at Level 5 holding a recent timed section, that ladder cell is "—"; with 20
   it shows a number.
4. The "Level N in" line for rating 1,084 (K 12, hard items at 1,300) reads "+17 ≈ 2 hard
   rights".

---

### C. Contests only our bank can run

#### C12. Trap of the week and the Trap Index

*From: unfair-advantage #5, outcomes #7, experience #9. Effort M. Builders: S8 (the kind in
`compete.ensure`, `compete.trap_theme`, the index), F5 (U6's `habits.py` families and the `want`
matcher), S4 (the family label in the verdict, already U6's chip).*

**Why.** One habit, such as answering a different quantity than asked, costs points in every
domain. Meeting it across ten skills in a row, interleaved, is the fastest way to build the check
that catches it on test day. Their options carry no labels, so they cannot build a contest
around a mistake or count who fell for it.

**The kind.** `trap-YYYY-Www`, subject `math`.
* Window: your local Monday 00:00 → Sunday 23:59; closes everywhere Monday 12:00 UTC.
* 10 slots, 3E / 4M / 3H, over at least 5 topics. Each slot is a template with a distractor in
  the week's family, and each twin is drawn with `want {template: family regex}`, so every
  question holds the trap. Slots are multiple choice, except grid-in slots whose template's
  named grid-in mistakes match the family.
* Answer clock 950 s, twins, key after each question, ranked first sitting, rated, season
  points, par (C5). Points as the Daily (maximum 260).
* **Theme**: `compete.trap_theme(week)` = the family with the highest fall rate last week (wrong
  first tries naming it ÷ first tries on questions carrying it, all modes, ≥ 30 chances),
  skipping the last 4 themes. Before there is data, it walks U6's 11 families in order. A family
  with fewer than 10 slot-feasible templates at a tier is skipped (checked at startup).
* **Lobby**: `k` "TRAP OF THE WEEK" + the family name + the tell in italics (U6) + "caught 41% of
  the field last week · 10 questions in 6 skills, each with this trap in it".
* **Result**: "Resisted 8 of 10 · field 5.9 · caught on Q3 (Percentages) and Q8 (Circles)", the
  tell, and **Drill this habit · 8** (U6's habit drill).
* **Board**: a **Resisted** column.

**Trap Index** (Your rankings section, and a 3-row "Traps this week" card on Overview):
* one row per family: "field 41% this week ▲6" · "you 12% · 17 chances in 30 days" · a
  **Trap-proof** chip when proven · **Drill · 8**;
* a chance is a first try on a question carrying a distractor in the family; it is resisted when
  you didn't pick that distractor;
* proven = ≥ 5 chances over ≥ 3 templates in 30 days with no fall;
* the Overview card shows the week's theme and the 2 families catching the field most, with your
  own rate.

**Data.** `result.trap = {family, resisted, chances, field_mean}`. `GET
/api/compete/traps-index` → `[{family, name, tell, field_share, field_move, you_share,
chances, proven}]`.

**Acceptance.**
1. For this week's trap contest, every slot's twin for two different learners regenerates with
   an option whose reason matches the family regex (s8.py).
2. `trap_theme` of a week never equals any of the 4 previous weeks' themes.
3. A learner with 5 resisted chances over 3 templates in 30 days → that family has `proven:
   true`.
4. `GET /api/contests?status=live` always contains a `trap` row.

#### C13. Rush: three strikes, and the difficulty climbs with you

*From: unfair-advantage #6. Effort M. Builders: S8 (the kind, boards, results), F5 (a `target`
rating pick that respects the learner's seen set), S4 (Sprint mode's header variant).*

**Why.** An endless run that seeks your level is two minutes of fresh, well-aimed practice you
can replay all day, and the fastest way through placement. A finite bank runs dry at the top of a
skill. Theirs has no retakeable ranked mode.

* **The kind.** `rush-YYYY-Www`, always live, subject `math`; an Overview row "Rush · best 17
  today" and a **Rush** tab on the Sprint lobby. A **Domain** select: All · Algebra · Advanced
  Math · Problem-Solving & Data Analysis · Geometry & Trig.
* **Run.** It starts at a question rated your rating − 300 (700 while Placing).
  * A right answer moves the target up 60.
  * A miss moves it down 120 and costs a strike.
  * An answer over 1.5× its budget (× timing factor) is also a strike (P16's "skip for now"
    threshold).
  * 3 strikes end the run.
  * Each question is the (template, tier) whose item rating is nearest the target, round-robin
    over the chosen domains. A run never repeats a template and never serves a (template, seed)
    you have seen.
* **Runner**: Sprint mode. Header "Right 14 · strikes ✕✕○ · Level 6 question". The verdict shows
  the key and the mistake line, with "Why" collapsed.
* **End**: "14 right · reached Level 6 questions · best ever 17", a strip shaded by difficulty,
  "Your 3 strikes: Swapped the columns · slow · Used the diameter as the radius" +
  **Practice these 3**.
* **Boards**: each student's best run per day, week and all time; order right ↓, then the
  highest item rating solved ↓ (C16: time never ranks). Filtered by Domain. Every run ranks.
* Rated (every answer moves rating and item ratings). No season points and no Points board
  entry, since unlimited runs would swamp them.

**Data.** Drill kind `rush`, `cfg {target, strikes, domain}`; drill field `target` (S8 server
code only, §3.2); `result {right, top_item, strikes: [{template, reason}]}`.

**Acceptance.**
1. After a right answer, the next served item's rating is ≥ the previous one's; after a miss it is
   lower.
2. The run ends on the third strike, and no template repeats within a run.
3. The weekly board lists each learner once, with their best run.

#### C14. Word Sprint: Reading & Writing enters Compete, and contests become subject-aware

*From: experience #12; v2-decisions items 2 and 3. Effort M. Builders: F4 (`contests.subject`),
S8 (the kind, the Subject filter), S9 (`words.sprint_items`, the quiz run in sprint mode, missed
words to due).*

**Why.** Words is the first piece of Reading & Writing on the site (decision 2), and the platform
will grow to the full SAT (decision 3). A word race gives vocabulary a daily reason, and building
Compete subject-aware now makes R&W contests additive later. Theirs covers both sections but was
never live.

* **The kind.** `words-YYYY-Www`, subject `rw`, always live. A 3-minute run, as many as you like;
  the week's best run counts.
* Items come from S9's quiz mode over the SAT word list and transitions (decision 2): definition
  → four word tiles. Difficulty rises every 8 questions.
* Points 10 / 20 / 30 by word difficulty band. Not rated (the Math rating stays Math). Counts for
  badges and the R&W season points.
* The end screen lists **Missed words**, added to My words due today (S9's hook).
* **Subject everywhere.** `contests.subject`. The Leaderboard gets a **Subject** select (Math
  default · Reading & Writing). Season points and boards are per subject; the Season card shows
  an R&W line only when you have R&W points. Today's Words tile shows "Word Sprint · best 190".

**Data.** `words.sprint_items(seed, n, level)` (S9), `words.record_contest_miss(learner, word)`
(S9). Word Sprint sittings are `sessions.kind = 'words'` (R36) with `contest` set.

**Acceptance.**
1. `GET /api/contests?status=live` has a row with `kind == 'words'` and `subject == 'rw'`.
2. `GET /api/leaderboard?metric=points&subject=math` never includes Word Sprint points.
3. A word missed in a Word Sprint has `is_due == true` in `GET /api/words` the same day.

---

### D. Fair to everyone

#### C15. Verify, don't void: a strict twin re-check instead of a zero

*From: unfair-advantage #3, the integrity gaps of outcomes and experience. Effort M. Builders:
S8 (`compete.flag`, `compete.confirm_next`, `finish_contest`), S4 and S5 (the Confirm step, the
triggers), F3 (the calculator host id for the paste rule).*

**Why.** A notification or a sibling at the door should not cost a minor a point, and copying a
stem's expression into our own Desmos is a real SAT workflow (P3 even loads the question into it),
yet both voided under v2. A student who looked an answer up has to be able to do it again on new
numbers. That needs an unlimited twin supply; a fixed bank would re-serve the item or keep a
reserve that leaks. This settles §3.7.9's open question on voiding strictness.

**Triggers** (ranked sittings, and Strict private contests), while a question is open:
* the tab hidden for ≥ 5 s (`visibilitychange`);
* a paste whose target is outside the calculator host;
* a `pagehide` beacon;
* **fast**: a right answer with `sms` < max(4 s, the 2nd percentile of clean right times on that
  (template, tier), once n ≥ 50).
Copy and cut no longer trigger anything.

**What a flag does.** Only a flagged **right** answer needs confirming; a flagged wrong answer
is just wrong. The verdict still shows the key and rationale. The first flag shows a banner:
"Question 4 needs a quick confirm at the end: the tab was hidden for 12 s."

**Confirm step**, after the last question and before the result:
* a sheet: "Confirm 2 answers · a twin of each · stay on this tab";
* each confirm is a twin of the flagged slot (same template, tier and format; a seed not yet
  dealt in the contest), in strict mode: hiding the tab or pasting forfeits it, and so does a
  fast answer;
* its own countdown is the question's budget × timing factor;
* a right confirm keeps the slot's base points (the pace bonus only if both answers came within
  budget); a wrong, skipped or forfeited confirm scores the slot 0 and counts it Voided;
* at most 5 confirms; flags beyond the fifth are voided;
* more than 5 **fast** flags in one sitting → no confirm step, and the sitting is Unranked
  "fast": "Not ranked: answers came in faster than the questions can be read.";
* leaving during the step forfeits the open confirm (the leave sheet says so).
* Test window (Weekly, Final): the same step after hand-in and before the result (S5).

**Result and board.** "8 right (1 confirmed) · 1 wrong · 1 skipped · 0 voided". A **Clean run**
chip when nothing was flagged. Confirm answers file as normal attempts (study time, mastery),
tagged `cfg.confirm_of`, and they are rated. Flagged answers are not rated. A failed confirm sets
`attempts.void` on the original answer, so R8 leaves it out.

**Data.** `POST /api/drill/{sid}/void {question_id, why, secs}` now records a flag in
`cfg.flags[qid]`. `GET /api/drill/{sid}` returns `confirm {due, next}` once the last question is
answered. `POST /api/drill/{sid}/confirm` serves the next confirm twin. Test window: `POST
/api/session/{sid}/void` and `/confirm`.

**Acceptance.**
1. Flag a right answer (`void {why:'left', secs:12}`), then answer its confirm twin right → the
   slot scores its base points, `voided == 0`, and the breakdown says "1 confirmed".
2. Forfeit the confirm (a second void call during it) → the slot adds 0, `voided == 1`, and the
   original attempt has `void = 'left'`.
3. A sitting with 6 right answers each in 1 s → `ranked == 0`, `why == 'fast'`, no confirm step.
   With 3 such answers → a confirm step of 3.
4. Browser: a copy event in the stem and a paste into the calculator during a ranked daily raise
   no banner; a paste into the grid-in field does.

#### C16. Ties by points: time never breaks them

*From: the experience scoring gap. Effort S. Builder: S8 (`board()`, `leaderboard()`).*

**Why.** The pace bonus caps speed, but a time tie-break brings the raw speed race back exactly
where it matters, at the top of the Daily, where perfect runs would be separated by who rushed.
With per-question budgets (C3) every sitting's time is inside its clock anyway.

* Board order: **points ↓**. Equal points share a rank (`=1`), and the next distinct score takes
  the following place (competition ranking). Within a tie, the earlier finisher is listed first.
* Sprint: best-run points ↓, then right ↓. Rush: right ↓, then the highest item rating solved ↓.
* Time stays a column everywhere, and a personal record ("fastest perfect Daily", C21).
* A line above a tied top: "=1 · 4 perfect runs".

**Acceptance.**
1. Two learners with equal points and different answer times → both have rank 1 with `tie:
   true`, and the next distinct entry has rank 3.
2. §3.7.8 item 10 still passes.

#### C17. Accommodated time (1.5× and 2×) in every contest, never shown publicly

*From: experience #8. Effort S. Builders: S8 (`compete.clock` scaling, the extended placing),
S4 and S5 (the lobby timing row), F4 (`prefs.test_timing` exists).*

**Why.** Students with 504 or IEP extended time get it on the real SAT and in our Tests, but v2's
fixed contest clocks shut them out. Theirs has no accommodations at all.

* **Lobby**: "Your time: 1.5× · 23:45 answer clock · Change". The row writes the same
  `test_timing` pref as the test start sheet. It offers Official · 1.5× · 2×; `untimed` reads as
  Official in contests (a contest always has a clock).
* **Clock and points**: the clock, each budget (pace bonus, Rush strikes, confirms) and the
  Sprint, Rush and Word Sprint clocks scale by the factor. Points are otherwise identical.
* **Where extended sittings count**:
  * Rating, Over par, Questions right, Test score and Climb: everyone, since they are time-neutral
    (R16 already keeps extended sittings out of the Test score's standard set);
  * Points, Season, Sprint, Rush and Word Sprint boards, and contest boards: official sittings
    only. An extended sitting is placed among extended sittings, shown only to its owner: the
    you-bar reads "#3 of 12 with extended time".
  * Streaks, badges (Pace setter's threshold scaled), review, the field's answers, debrief and
    races all count.
* **Nothing public shows it**: no row, chip, copied result or race link carries the timing.

**Data.** `sessions.cfg.timing` ('official' | 'x1.5' | 'x2'); board queries filter on it;
`board(scope='extended')` returns only you, the count, and no names.

**Acceptance.**
1. With `test_timing: 'x1.5'`, `POST /api/contest/daily/start` → `clock.left == 1425`.
2. That learner's finished daily is absent from the daily board's entries and `players`; its
   board response has `you.extended == {rank, of}`.
3. The same learner appears on `metric=net` and `metric=rating`.
4. Copy result's text of an extended sitting equals the official format, character for
   character, apart from the numbers.

---

### E. Classes and friends

#### C18. Class streak, nudges, and a fair Classes board

*From: outcomes #10, unfair-advantage #11 (in part). Effort M. Builders: S8
(`compete.class_streak`, `nudges`, the Classes scope), S2 (the owner's listing switch on the
class page, members), S1 (the feed merges nudges).*

**Why.** A streak other people depend on gets a student to do the Daily on the days they would
skip, and days practised drive the score. Their classes are hidden and have no social layer. v2
had class boards and class contests, but nothing that made one student's practice matter to the
others day to day.

* **Class streak** (any class, R4):
  * with 2–10 current members: consecutive days on which every member finished that day's Daily,
    each on their own local day;
  * with 11 or more: days on which ≥ 75% did;
  * a member's spare day (U16) counts as done for them.
* **Overview G › Your classes**, per class: member dots (✓ done · half-filled in progress · empty
  not yet), named inside the class by R4's display names; "Class streak 6 · best 11"; a quiet
  **Nudge** on each not-yet member.
* **Nudge**: one feed item (U25), "Ada nudged you: today's Daily closes 11:59 PM", at most one per
  sender per member per day (429 after). Fixed text, no messages. Not shown for members who
  have left.
* **Classes board** (Leaderboard scope "Classes", period Week): class rows ranked by the mean
  weekly Over par (C5) per active member (≥ 1 ranked contest that week), for classes with ≥ 5
  active. Columns: rank, class, active members, mean over par, movement. A class is named only
  when its owner switched on "List this class on the Classes board" (off by default, on the class
  page); others show as "A class" at their real rank. Your own classes always show their names to
  you.
* The class owner's view shows the class's place.
* Achievement "Class week": a 7-day class streak (R25).

**Data.** `nudges(sender, target, class, day, at)`, PK (sender, target, day). `POST
/api/compete/nudge {class, member}`. `compete.class_streak(class, tz)`.
`classes.listed INTEGER DEFAULT 0` (S2's column, §3.2).

**Acceptance.**
1. A 3-member class where all 3 finished today's and yesterday's Daily → `class_streak == 2`.
   One member missing today → it holds at 2 until their local day ends, then 0 (spares aside).
2. A second nudge from one sender to one member on one day → 429.
3. The Classes board names an unlisted class as "A class" to a non-member, and by name to a
   member.

#### C19. Private and class contests built from traps, and results that assign the repair

*From: the private-contest and teacher-view gaps of all three. Effort S. Builders: S8 (the create
sheet source, the results footer), S2 (Shell §7's repair assignment).*

**Why.** A teacher wants to test what the class keeps getting wrong, and a friend challenge is
sharper on the traps that catch you. Their homework is a fixed set; v2's owner table showed marks
but not what to do about them.

* **Create a contest › Questions from**, a new underline above Skills: **Skills I pick** (default)
  · **The class's open mistakes** (for a class you own: the 10 norms most members hold open, each
  held by ≥ 2; twins drawn with `want`) · **My open mistakes** (your open traps' templates, drawn
  with `want`: "beat me on the traps that catch me"). The summary line reads "10 questions ·
  from 10 open mistakes held by 14 of 24".
* **Owner results table** gains a footer row naming each question's top misconception with its
  share ("41% fell for: inverted the slope").
* Above the table, **Where the class went wrong**: the top 3 misconceptions, each with **Assign a
  repair to these 9** (Shell §7's 5-question repair assignment for exactly those members) and a
  quiet **Reach a level** (U27).

**Data.** `contests.spec.source = 'skills' | 'class_traps' | 'my_traps'`; `GET
/api/contest/{cid}/results` adds `footer [{slot, right_share, top: {norm, label, share}}]`.

**Acceptance.**
1. A class contest from class traps with 3 members each holding norm X open → at least one slot
   regenerates with an option whose norm is X.
2. **Assign a repair** on a footer misconception creates one assignment whose `who` equals the
   members who fell for it.

---

### F. Seeing it all, fast

#### C20. Board grid view: the whole field's answers at a glance

*From: experience #10. Effort S. Builders: S8 (`GET /api/contest/{cid}/grid`, `UI.board` grid
mode).*

**Why.** "Everyone missed Q7" is visible in one glance, and twins make it comparable slot by slot.
Their table is Rank / Username / Accuracy / Time.

* Every fixed-slot contest board gets a **List · Grid** toggle, gated like Review (after you
  finish, or after the contest closes everywhere).
* Rows are players in rank order, 50 a page, your row pinned at the top. Columns Q1…Qn, each cell
  a §2.3 status token with its glyph. A footer row gives % right and median time per slot.
* A column header's tooltip: "Q7 · Circles · Hard · 23% right · top trap: Used the diameter as
  the radius". Clicking a column opens that slot's review item; clicking a named row opens
  Compare.
* Hidden students show as "Anonymous" in their real place and are not clickable (R12).
* Phone: the grid scrolls inside its own box with a sticky name column; a Daily's 10 cells at 22 px
  fit at 390.
* It is the same component as the owner results table, without the owner's columns.

**Acceptance.**
1. `/grid` before finishing → 403; after → rows whose `marks` length equals the slot count.
2. Browser at 390: `document.documentElement.scrollWidth <= innerWidth` with the grid open.

#### C21. Records, the rank reveal at hand-in, and season recaps

*From: experience #5, unfair-advantage #13. Effort S. Builders: S8 (`compete.records`, the recap
at `close_season`), S1 (Me's recap line; U14's Monday sheet reads the Compete line).*

**Why.** Personal records motivate even with one player on the site. A season recap shows a
student what the stretch before a test date did for them, and sets the next target. Theirs has
four dead achievement tiles.

* **Records** per kind: best points, best top %, fastest perfect Daily, best Sprint, best Rush,
  longest challenge streak, peak rating, first time at each level; each with its date. A
  **Records** row of tiles on Your rankings. History rows and chart points carry a small star
  glyph (our icon) where a record was set.
* **At hand-in** the result panel plays one entry-only reveal: the board slice (you ± 2) with
  your row sliding into place and "Passed Grace and Ada · 15 pts to #3"; record chips ("New best
  Daily · 245 (was 230)", "First top 10%"). `prefers-reduced-motion` or `prefs.motion = reduce`
  renders it static. It never replays (localStorage key per session, in try/catch).
* **Week line**: `compete.week_line(learner)` → "Last week: 5 Dailies · 1 Weekly · 620 pts (#12 →
  #8) · rating +41 · 2 records". U14's Monday sheet shows it; Overview D shows it on Mondays.
* **Season recap** at `close_season`, stored per learner in `seasons.standings`: "Road to Oct 3:
  24 contests · rating 980 → 1,190 (Level 3 → 4) · 31 mistakes closed · trap you beat most:
  Swapped the columns (7×) · best finish #2 · Season Final 610–750". It shows as a card at the
  top of Overview until dismissed or the next season's first contest, and as a line on Me.
  **Copy recap** copies plain text. The next season opens with a goal line: "Road to Nov 7: Level
  5 is 61 rating away".

**Data.** `compete.records(learner)`; finish responses add `records_new`; `GET
/api/compete/recap?season=` → the stored recap.

**Acceptance.**
1. A Daily of 245 after a best of 230 → `records_new` contains `{kind:'daily', value:245,
   was:230}`.
2. The recap's contest count equals `/api/compete/history` rows within the season window.
3. Browser with reduced motion: the result panel renders with no running animation.

#### C22. History as a to-do list: one expanding list replaces the picker

*From: the picker and history gaps of all three. Effort S. Builder: S8.*

**Why.** Their Contest Leaderboard picker and Contest History are two views of one list, and
neither gives the student anything left to do.

* **Remove** §6.3 "How you placed in a contest".
* **Contest history** columns add **Over par** and **Follow-up** ("Rematch Thu", "Won back 50/70",
  "2 open" or "—").
* Filters add **Open follow-ups (n)**.
* Each row expands in place: your answer strip, a mini board (#1, then you ± 2), the gap to the
  next place, the debrief's top row (C1) with **Fix it**, the follow-up with **Rematch**, and
  **Race the winner** · **Race yourself** · **Review ›**.
* Rating and Top % chart points open the same expanded row.
* A placing trend strip per kind sits above the table (the last 10 top % values).

**Acceptance.**
1. `/compete/rankings/` has no contest `<select>`.
2. `GET /api/compete/history?followup=open` returns only rows with an unfinished rematch or an
   open trap from that sitting.
3. Browser: expanding a Daily row shows its strip and a mini board without leaving the page.

#### C23. Badges that start what advances them

*From: the badge gaps of all three. Effort S. Builders: S8 (`ACHIEVEMENTS` in `compete.py`,
the Go map), S1 (R25's engine, rarity in `/api/me/achievements`).*

**Why.** Progress shown is not progress driven. Theirs are dead tiles; v2's work but wait.

* **Go** on every Compete badge in progress (as U13 does on Me): first-contest, daily-7,
  daily-30, perfect-ten, top-ten, podium → today's Daily; pace-setter → today's Daily with the
  SAT-pace pacer; sprinter → a Sprint run; weekly-4 → the Weekly (or "Opens Sat"); dress-rehearsal
  → the Final's lobby; level-5 and level-8 → Rush; all-rounder → Rush in the weakest domain;
  trap-hunter → Fix all; season-top-10 → Season standings.
* **Rarity** "earned by 4%" once ≥ 50 learners were active in 30 days (S1, cached hourly).
* **New ladders** (R25, declared in `compete.ACHIEVEMENTS`): Over par (3 / 5 / 10 Dailies in a
  row), Won back (10 / 50 / 200 questions, C2), Rush (a run of 10 / 20 / 30 right), Trap-proof week
  (resisted all 10 in a Trap of the week, 1 / 4 / 12 times), Class week (C18).
* pace-setter's rule reads "every right answer within its budget".

**Acceptance.**
1. `/api/me/achievements` rows of Compete badges with `have < next` all carry `go`.
2. Resisting all 10 in a trap contest adds `earned (id 'trap-week', tier 1)`.

#### C24. One tap to question 1, a Compete key map, a thumb bar, and instant scopes

*From: experience #6. Effort S. Builders: S8 (keys, thumb bar, prefetch), S3 (Today's pill), F2
(`UI.keys` registry, §2.8 row).*

**Why.** Theirs is about 8 actions and a wait for the contest to close before you see where you
placed, with no shortcuts. v2 is 2 taps to Q1. Once the rules have been seen, one is enough.

* **One tap.** Today's challenge pill and Overview A's pill start the sitting directly once this
  device has shown that kind's rules (localStorage `satf.rules.<kind>`, in try/catch); otherwise
  they open the lobby. The runner's top bar gets a **Rules** link that opens the §1.2 list in a
  sheet. The rank shows at hand-in.
* **Keys** (a "Compete pages" row in §2.8):
  * Overview: `Enter` starts or resumes the Daily.
  * Contest page: `B` board · `R` review · `Y` jump to your row · `,` `.` previous / next day.
  * Boards: `J` `K` or `↑` `↓` move row focus · `Enter` row menu · `F` follow · `/` find a student
    · `M` / `P` cycle metric / period (Leaderboard).
* **Thumb bar** (phone, contest page): a 56 px bar above the tabs with the state's primary
  (Start · Resume · See the board) and **Jump to me**. It replaces the sticky you-bar there.
* **Instant scopes.** Board responses go through U23's `UI.cached`. After the first load, the
  other scopes and the next page prefetch when idle. A switch renders from cache in under
  100 ms, then revalidates, with `meta` "updated 12 s ago".

**Acceptance.**
1. Browser: with `satf.rules.daily` set, one click on Today's challenge pill lands on the runner
   with question 1 on screen.
2. On the Leaderboard, `/` focuses Find a student, and `M` changes `?metric=` in the URL.
3. Switching scope after the first load issues no blocking request before the table renders
   (Playwright network trace).

#### C25. The challenge streak survives a missed day made up, and reminders say what is due

*From: the unfair-advantage streak gap, the outcomes reminder gap. Effort S. Builders: S8
(`compete.challenge_streak`), S7 and S1 (U18's feed titles and push kind).*

**Why.** One missed day wipes theirs. A make-up that requires doing the work keeps the habit
without cheapening it. A reminder that names what is due gets opened; a static alarm gets
dismissed.

* **Make-up.** A missed Daily sat as a ghost sitting within 48 h of the end of its local day
  counts for the challenge streak. It never counts for rank, rating or season points. The 30-day
  strip gets a **made up** state (orange outline with a ✓), and the legend reads "sat · made up ·
  ghost · missed". Past-day pages offer "Make up Sep 22 · keeps your streak · 1 day left".
* **Reminders** (U18): the feed's daily event is titled from what is due ("Daily Challenge +
  Rematch 3 · about 20 min"). A push kind "Daily Challenge still open" (off by default) fires 2 h
  before local midnight on days not yet sat. The §3 "Daily reminder" `.ics` stays as the
  fallback.

**Acceptance.**
1. A learner who sat days 1–5, missed day 6 and sat day 6's ghost on day 7 → `challenge_streak ==
   7` after day 7's Daily. The same ghost sat on day 9 → the streak restarts.
2. With push kind `daily` on and today's Daily unsat, `POST /api/push/next` at 21:59 local
   returns text starting "Daily Challenge".

---

## 3. Spec overrides

### 3.1 Inside §3.7 (spec/rebuild-v2.md lines 8097–9133)

Each entry quotes the current text, then gives the replacement or addition.

1. **§3.7.3, Review changes, item 3.**
   * Quote: "the open question is voided after 5 s away or on copy/cut/paste (theirs voids at
     once, with no grace);"
   * Replace with: "a flagged right answer is confirmed on a strict twin at hand-in, and keeps
     its points if the twin is right (C15). Copy and cut trigger nothing; a paste into the
     calculator is free."

2. **§1.1 Kinds.**
   * Quote: "| board order | points ↓, answer time ↑ | best-run points ↓, right ↓, answer time ↑ |
     points ↓, time used ↑ | points ↓, time used ↑ (the estimate band is shown) | points ↓,
     answer time ↑ |"
   * Replace with: "| board order | points ↓ | best-run points ↓, right ↓ | points ↓ | points ↓
     (the estimate band is shown) | points ↓ |" (C16).
   * Add after the table: a second table for **Trap of the week** (C12), **Rush** (C13) and **Word
     Sprint** (C14) with the rows id, window, questions, clock, runner, twins, key shown, skip,
     voiding, ranked sitting, board order, rated, season points, subject, as each upgrade states.
   * Add a row to both tables: "| subject | math | … |" (`rw` for the Word Sprint).

3. **§1.2 How it's ranked, Points.**
   * Quote: "  - **Pace bonus:** +5 for each right answer given within 95 s (answer-clock kinds
     except Sprint)."
   * Replace with: "  - **Pace bonus:** +5 for each right answer given within its own time
     budget (P16: easy 1:05, medium 1:35, hard 2:06, × your timing), in answer-clock kinds except
     Sprint and Rush (C3)."
   * Add: "  - **Par:** what a student at your rating is expected to score on your slots. Over par
     = base points − par (C5)."

4. **§1.2, Voids.**
   * Quote: "- **Voids** (ranked sittings):" and its three sub-bullets.
   * Replace with: "- **Flags and confirms** (ranked sittings and Strict private contests):" and
     C15's Triggers, What a flag does and Confirm step, verbatim.

5. **§1.2, Ties.**
   * Quote: "- **Ties:** equal points and equal answer time share a rank, shown `=4`, and the next
     distinct score takes rank 6 (competition ranking). Within a tie, the earlier finisher is
     listed first."
   * Replace with: "- **Ties:** equal points share a rank, shown `=4`, and the next distinct score
     takes the following place (competition ranking). Time never breaks a tie; within one, the
     earlier finisher is listed first (C16)."

6. **§1.2, Ranked / Unranked, too fast.**
   * Quote: "  - **too fast**:" and its three sub-bullets.
   * Replace with: "  - **too fast**: more than 5 right answers faster than max(4 s, the type's
     2nd percentile). Up to 5 are confirmed instead (C15). Shown as "Not ranked: answers came in
     faster than the questions can be read.""

7. **§1.2, Rating and level.**
   * Quote: "  - Each (template, tier) has a rating that calibrates from everyone's rated answers."
   * Replace with: "  - Each (template, tier) has a rating that calibrates from every clean first
     try in any mode (P11's `ratings.update`)."
   * Add: "  - Domain and skill ratings come from P11's `skill_ratings` (C11)."

8. **§3 Overview, A. Daily Challenge card.**
   * Quote: "- Facts line: "10 questions · 15:50 answer clock · one sitting · ranked"."
   * Add after it: "- Par line: "Your par 60 · about 3.8 right · likely #8–#14 of ~37" + quiet
     **Warm up · 6** (C5, C7). The chip "Over par 4 Dailies running" when it holds."
   * Quote: "  - *Not started*: pill "Start the challenge"."
   * Append: "It starts the runner directly once this device has seen the rules (C24)."
   * Quote: "    - Buttons: pill "See the board"; quiet "Review answers", "Copy result"."
   * Append: "; the follow-up chip "Rematch · Thu" or "Won back 50/70" (C2); "Rivals today" (C9)."
   * Quote: "- Footer: "Past days ›" (yesterday's contest page) · "Daily reminder" (sheet, below)."
   * Append: " · "Make up yesterday · keeps your streak" when it applies (C25)."

9. **§3 Overview, B. Contests.**
   * Quote: "  - **Kind icon:** sprint = bolt, weekly = module sheet, final = flag, daily = trophy,
     private = two people."
   * Append: ", trap = the misconception glyph, rush = three strikes, words = the word mark."
   * Quote: "  - **Facts:** "22 questions · 35 min · your own twin questions · 128 in"."
   * Add after it: "  - **Trains** line and "par 290 · last week 260" (C7)."

10. **§3 Overview, D. Your stats.**
    * Quote: "- 2×3 stat tiles: "Week rank #12 of 340" · "All-time rank #210 of 1,284" · "Country
      #14 of 96" (or "Set a country on Me") · "Points this week 620" · "Contests 14" · "Best
      finish #2 · Sep 19"."
    * Append: "Each tile adds movement and its next milestone (C10). Above them, the compact
      Rating card with "Level 4 in +17 ≈ 2 hard rights" (C11). On Mondays, the week line (C21)."

11. **§3 Overview, E. Leaderboard preview.**
    * Quote: "- `k` "THIS WEEK · POINTS". Five rows: rank, name, 20 px level badge, points."
    * Replace with: "- `k` "THIS WEEK" + chips Points · Over par · Climb. Rows: #1, a separator,
      then you ± 2, each with movement and gap. Fewer than 5 players: par rows and your best
      fill it (C10, C6)."

12. **§3 Overview, new side cards.**
    * Quote: "**F. Next badges** (tile)"
    * Add before it: "**Rivals** (C9)" and "**Traps this week** (C12)".
    * Quote: "- The three unearned badges you're closest to: icon, name, rule line, a progress bar
      and "5/7"."
    * Append: " Each has **Go** (C23)."
    * Quote: "**G. Your groups** (tile)"
    * Replace with: "**G. Your classes** (R4), with member dots, the class streak and Nudge (C18)."
    * Quote: "- One column in this order: A, D, H, B, E, C, F, G."
    * Replace with: "- One column in this order: recap, A, D, Rivals, H, B, E, Traps, C, F, G."

13. **§4 Contest page, Upcoming.**
    * Quote: "- Quiet "Add to calendar". Pill "Practice for it": a 10-question drill over the
      contest's domains."
    * Replace with: "- Quiet "Add to calendar". The par line and **Warm up · 6** (C7)."

14. **§4, Live, not started.**
    * Quote: "- Rules, ladder, field line: "128 in · 6 sitting now · median 260 pts · best 410"."
    * Append: " The par line and forecast (C5, C7), ladder cells with your chance (C7), the
      **Race** select (C8) and "Your time: Official · Change" (C17)."

15. **§4, Finished (you): the result panel.**
    * Quote: "  - Points "170", with the sub-line "120 + 40 pace + 10 finish""
    * Add after the tiles list: "  - Par "+15 over par · base 75 vs par 60" (C5)."
    * Quote: "  - Rating "+14 → 1,084" with a level badge (a level-up shows "Level 3 → 4")"
    * Append: ", expanding to domain deltas (C11)."
    * Quote: "- Breakdown line: "8 right · 1 wrong · 1 skipped · 0 voided"."
    * Replace with: "- Breakdown line: "8 right (1 confirmed) · 1 wrong · 1 skipped · 0 voided",
      and a **Clean run** chip when nothing was flagged (C15)."
    * Add after the breakdown: "- **Where your points went** (C1), then **Time** (C3), then the
      race line (C8), the rivals line (C9) and the reveal with record chips (C21)."
    * Quote: "- Actions: pill "See the board". Quiet: "Practice my misses" (the existing
      `from_session`), "Practice the field's traps", "Copy result", "Challenge a friend"."
    * Replace with: "- Actions: pill "See the board". The Debrief's **Rematch my misses · n** (C2).
      Quiet: "Practice the field's traps", "Copy result", "Race link", "Challenge a friend"."
    * Quote: "- The Final shows the section band from `scoring.section_score` as a big number
      pair, "610–750", with "Route: harder module 2", beside the rank."
    * Append: " Then **Your last week** and the **Test-day card** (C4)."
    * Quote: "- Sprint: "Best this week 240 pts (run 3 of 3)" and a pill "Run again"."
    * Append: " and "Race your best · 240" (C8)."

16. **§4, Board section.**
    * Quote: "- Scope underline: Everyone · Near me · Country · {each of your groups}."
    * Replace with: "- Scope underline: Everyone · Near me · Following · My level · Country ·
      {each of your classes}. Header controls: **List · Grid** (C20), **Points · Over par**
      (C5), **Pars** (C6), Find a student (C9)."
    * Quote: "  - Daily and Private: Rank | Student | Score | Points | Answer time."
    * Append to each table line: " | Net | Move | Gap" (Trap adds Resisted before Points; Rush:
      Rank | Student | Right | Top level | Runs | Move)."
    * Quote: "  - Unranked sittings never appear. Your own unranked result shows as a line above the
      table: "Your sitting is unranked: {reason}.""
    * Append: " Extended-time sittings are placed only for their owner (C17)."
    * Quote: "- **Sticky you-bar:** while your row is out of view (IntersectionObserver), a bar
      pinned above the phone tabs (bottom 0 on desktop) reads "You · #212 · 150 pts · Jump to
      me"."
    * Replace the quoted text with "You · #212 · 150 pts · 22 pts to pass #211 · one medium right
      at pace · Jump to me" (C10). On the phone contest page it merges into the thumb bar (C24).
    * Quote: "  - "Compare" (once you've finished too);"
    * Add after it: "  - "Race" (C8); "Follow" / "Unfollow" (C9);"
    * Quote: "  - For twins, compared slot by slot."
    * Add: "  - The head-to-head record this season (C9)."
    * Quote: "- Empty: "No one has finished yet." Near me while you're unranked: "Finish this
      contest to see who's around you.""
    * Replace with: "- Empty: par rows and your own rows (C6) with "No one else has finished yet."
      Near me while you're unranked: "Finish this contest to see who's around you.""

17. **§4, Review section.**
    * Quote: "  - **How the field answered.**"
    * Append: " Below 5 contest answers it falls back to the type's first tries in all modes,
      labelled so (C6)."
    * Quote: "  - Quiet "Another like this": a 5-question drill on that template with fresh seeds."
    * Append: " Wrong rows also get **Fix it · 3** (C1)."

18. **§4, Owner controls, Results table.**
    * Quote: "  - A footer row with each question's % right."
    * Replace with: "  - A footer row with each question's % right and top misconception, and
      above the table "Where the class went wrong" with **Assign a repair to these N** (C19)."

19. **§5 Leaderboard, controls.**
    * Quote: "  - *Metric* underline: Points · Rating · Questions right · Test score."
    * Replace with: "  - *Metric* underline: Points · Over par · Rating · Questions right · Test
      score · Climb (C5, C10). Rating gets "Sort: Rating · Change"."
    * Add helpers: Over par: "Base points minus your par, over ranked contests. Beat what a student
      at your rating is expected to score." Climb: "Gain since your first scored section, among
      students who started near you (U11)."
    * Quote: "  - *Scope* `<select>`: Everyone · Near me · Country ({yours}, or "Country: set on
      Me", which links to Me) · each of your groups."
    * Replace with: "  - *Scope* `<select>`: Everyone · Near me · Following · My level · Country
      (…) · Same exam date (R3) · each of your classes · Classes (C9, C18)."
    * Quote: "  - *Domain* `<select>` (Points and Questions right only; disabled with a tooltip
      otherwise)"
    * Replace with: "  - *Domain* `<select>` (Points, Questions right and Rating; disabled with a
      tooltip otherwise; C11)"
    * Add: "  - *Subject* `<select>`: Math (default) · Reading & Writing (C14)."
    * Quote: "  - The controls live in the URL (`?metric=points&period=week&scope=all&domain=`)"
    * Append: " plus `&subject=math`."

20. **§5, Podium and table.**
    * Quote: "  - With fewer than 3 players, the empty cards read "Open"."
    * Replace with: "  - With fewer than 3 players, the empty places show par rows (C6). Under
      the podium, the "Your path" line (C10)."
    * Quote: "- **Table:** Rank | Student (name + level badge) | {Points | Rating | Right | Band} |
      Accuracy | Avg time | Contests (Rating: Change; Test score: Sections)."
    * Append: " | Move | Gap (C10). The Rating board has level separator rows (C6). A Find a
      student field sits above the table (C9)."
    * Quote: "  - Empty period: "No ranked contests yet this week." + a link to the nearest period
      that has players ("This month: 212 students ›") + pill "Start the challenge"."
    * Append: " The par ladder fills the table (C6)."

21. **§6 Your rankings, 1. Performance summary.**
    * Quote: "   - Under them, a line chart, 100% wide and 120 px tall, with an underline toggle
      **Top % · Rating**"
    * Replace with: "…toggle **Top % · Rating · Over par** (C5)". Add above the tiles: the "Since
      last week" line (C10) and the weekly trap roll-up (C1).

22. **§6, 2. Your ranks | Pace.**
    * Quote: "     - Last row: "Contests played 14"."
    * Add before it: rows Following, My level, Same exam date, Climb; each cell with movement and
      gap (C10).
    * Quote: "   - **Pace** (theirs: Time Analysis). Underline toggle: By difficulty · By domain ·
      Right vs wrong · Under pressure."
    * Replace the Pace block with C3's "Your rankings › Pace".

23. **§6, 3. How you placed in a contest.**
    * Quote: "3. **How you placed in a contest** (theirs: Contest Leaderboard)" and its two
      sub-bullets.
    * Delete. Contest history rows expand instead (C22).
    * Add new sections in the §6 order: Rating card (C11), Records (C21), Trap Index (C12),
      Rivals (C9), Level ladder (C11).

24. **§6, 6. Contest history.**
    * Quote: "   - Table: Date | Contest | Score | R · W · S · V | Points | Time | Rank | Top % |
      Rating Δ | Ranked/Unranked | "Review ›"."
    * Replace with: "   - Table: Date | Contest | Score | R · W · S · V | Points | Over par | Time |
      Rank | Top % | Rating Δ | Ranked/Unranked | Follow-up | ▸ (expands, C22)."
    * Quote: "   - Filters: Kind select (All / Daily / Sprint / Weekly / Final / Private)"
    * Replace with: "   - Filters: Kind select (All / Daily / Sprint / Weekly / Final / Trap / Rush
      / Words / Private) · **Open follow-ups (n)**"

25. **§6, Badge set.**
    * Quote: "| pace-setter | Pace setter | 8+ right on a Daily, every right answer within 95 s |
      best/8 |"
    * Replace with: "| pace-setter | Pace setter | 8+ right on a Daily, every right answer within
      its budget | best/8 |"
    * Add C23's ladders (over-par, won-back, rush, trap-week, class-week).

26. **§7 Create a private contest.**
    * Quote: "- **Skills**: the shared topic picker from the practice builder (4 domains × 19
      skills, select-all per domain). The default is all."
    * Add before it: "- **Questions from**: Skills I pick (default) · The class's open mistakes ·
      My open mistakes (C19)."

27. **§8 The runner in contest mode.**
    * Quote: "- **Voids** (ranked sittings, and Strict private contests):" and its four
      sub-bullets.
    * Replace with C15's triggers, banner and Confirm step.
    * Quote: "- **The verdict adds the field:** "62% of 37 got this right" (for twins, the same
      slot), shown once ≥ 5 have answered."
    * Replace with: "- **The verdict adds the field line** with C6's fallbacks."
    * Add: "- **Race rail** under the progress bar when a pacer is set (C8)."
    * Add: "- **Rules** link in the top bar (C24). The clock follows the timing factor (C17)."
    * Quote: "- **Sprint mode:**"
    * Append: " Rush uses it with the header "Right 14 · strikes ✕✕○ · Level 6 question" (C13)."
    * Quote: "  https://…/compete/contest/?id=daily-2026-09-23"
    * Replace with: "  Beat 170: https://…/compete/contest/?id=daily-2026-09-23&race=<pid>" (C8).
    * Quote: "- Voids use the same rules as above, for the question on screen, via
      `/api/session/{sid}/void`."
    * Append: " The Confirm step runs after hand-in, before the result (C15). The Final forces the
      pace guide off (C3)."

28. **§9 Today, Me, Results, Report.**
    * Quote: "- "#4 of 37 · top 11%" + "Next one in 07:14:22" once done;"
    * Add after it: "- before starting, the par line (C5); once done, the follow-up chip (C2);
      the pill starts in one tap (C24);"
    * Quote: "- **Rank snapshot:** "Week #12 of 340 · Country #14 of 96 · All time #210 · Level 3
      (1,084)", linking to Your rankings."
    * Append: " It reads `compete.ranks` with movement and gap (C10); the season recap line
      shows after a season closes (C21)."
    * Quote: "- **Groups:** a list with name, code + Copy, member count and "Leave"."
    * Replace "Groups" with "Classes" (R4) and add the class streak (C18).
    * Quote: "- Ranked sittings add a percentile: "Higher than 71% of timed full sections in the
      last 90 days (212 sections)", shown once there are ≥ 20."
    * Replace with: "- Ranked sittings add R16's percentile and Compete's line "#41 of 212 on this
      month's Test score board · Climb +90, ahead of 74%" (C10)."

29. **§10 Build order.** Replace the list with:
    1. Model and fixes, as written, plus: rating and level (moved from step 8, since par, rivals
       and levels read it), the budget pace bonus (C3), flags and confirms (C15), ties by points
       (C16), timing (C17), `contests.subject`.
    2. Contest page (daily, twins) + `/challenge/` redirect + NAV/SECTION + Overview (A, B, D, E)
       + Today's card + one tap and keys (C24).
    3. Leaderboard as written + snapshots, Move, Gap, you-bar step, Your path (C10); par rows and
       the field line (C6); Following, My level, Find (C9).
    4. Your rankings: summary, chart, ranks, Pace from `progress.pace` (C3), history with expanding
       rows (C22).
    5. Review with the field's answers + traps + Compare + QOTD + Another like this + Debrief
       (C1) + Rematch and Won back (C2) + the Time block (C3) + Grid (C20).
    6. Sprint + races and race links (C8).
    7. Weekly Module in the test window + its Confirm step (C15).
    8. Badges with Go and the new ladders (C23) + Test score + the report pill line (C10) + par
       and Over par (C5) + forecast and warm-up (C7) + the Rating card and ladder (C11) + records
       and the reveal (C21).
    9. Seasons + Final + Season period + H card + Seasons table + last week and the test-day card
       (C4) + recaps (C21).
    10. Classes (R4) + Me Boards + country scope + report name + Rivals (C9) + class streak, nudges
        and the Classes board (C18).
    11. Private and class contests + owner results + Challenge a friend + Copy result + calendar +
        reminder + ghost sittings + trap sources and Assign a repair (C19) + make-up and
        reminders (C25).
    12. Trap of the week and the Trap Index (C12); Rush (C13).
    13. Word Sprint and the Subject filter (C14), once S9's quiz items are merged.
    14. README serving-layer rows and spec/rebuild.md §9 updated.

30. **§3.7.4 Extras.**
    * Quote: "- **Skip with the key shown, and voids with a grace period**:"
    * Replace the entry with: "- **Skip with the key shown, and verify instead of void**: a skip
      still teaches, a blip is confirmed on a strict twin instead of zeroed, and leaving never
      zeroes a sitting (C15)."
    * Append entries for C1–C25 in their own words (one line each), in the list's style.

31. **§3.7.5 Server changes, db.py.**
    * Quote: "  - contests(id TEXT PK, kind TEXT daily|sprint|weekly|final|private, title TEXT, …"
    * Replace the kind list with `daily|sprint|weekly|final|private|trap|rush|words` and add
      `subject TEXT DEFAULT 'math'`.
    * Add tables `follows`, `rank_snapshots`, `nudges` (C9, C10, C18; F4 adds them, §3.2).

32. **§3.7.5, compete.py: clock, points, secs, ranked.**
    * Quote: "  - finish_contest(row), at finish: points = Σ right unvoided × {easy 10, medium 20,
      hard 30} + 5 × right unvoided with sms ≤ 95000 (answer-clock kinds except sprint) + 10 when
      all were answered with no skip or void (not sprint)."
    * Replace "with sms ≤ 95000" with "with sms ≤ q.budget_ms × timing factor"; "right unvoided"
      counts confirmed flags and leaves out failed confirms (C3, C15).
    * Quote: "  - Ranked checks, in order: 'ghost' if started outside the window; 'repeat' if a
      ranked sitting already exists (sprint excepted); 'fast' if median sms < 4000, or test-window
      (finished − started)/asked < 20 s, with right ≥ asked/2."
    * Replace the 'fast' clause with: "'fast' when more than 5 right answers were flagged fast
      (C15)." Sprint, Rush and Word Sprint are excepted from 'repeat'.
    * Add: `result.par`, `result.domains`, `result.race`, `result.trap`, `records_new`, and the
      follow-up fields (C2, C5, C8, C11, C12, C21).

33. **§3.7.5, compete.py: board().**
    * Quote: "  - Competition ranking over (points DESC, secs ASC), listed by finished ASC within a
      tie."
    * Replace with: "  - Competition ranking over points DESC (Sprint: best points, right; Rush:
      right, top item), listed by finished ASC within a tie (C16). Returns `pars`, `mine`,
      `move`, `gap` and the scopes `following`, `level`, `extended` (C6, C9, C10, C17)."

34. **§3.7.5, compete.py: leaderboard().**
    * Quote: "  leaderboard(metric='points'|'rating'|'right'|'test', period=…"
    * Replace with: "metric='points'|'net'|'rating'|'right'|'test'|'climb'", plus `subject`,
      `sort` ('value' | 'change', Rating), `find`, and the scopes of C9, C18 and C17. Domain
      applies to Rating through `skill_ratings` (C11).

35. **§3.7.5, compete.py: rating.**
    * Quote: "  - Ri −= 4(S−E), with Ri starting at 900 easy / 1100 medium / 1300 hard;"
    * Replace with: "  - the item side is P11's `ratings.update` (one rule for every mode);"
    * Add: "Flagged answers are not rated; confirm answers are (C15)."

36. **§3.7.5, app.py: contest endpoints.** Add: `GET /api/contest/{cid}/debrief` (C1), `POST
    …/rematch` (C2), `POST …/warmup` (C7), `GET …/grid` (C20), `?race=` on `GET /api/contest/{cid}`
    (C8), `POST /api/drill/{sid}/confirm` and `POST /api/session/{sid}/confirm` (C15),
    `POST/DELETE /api/follows`, `GET /api/compete/rivals` (C9), `GET /api/compete/traps-index`
    (C12), `GET /api/compete/recap` (C21), `POST /api/compete/nudge` (C18). The owner check on
    `/results` stays.

37. **§3.7.7 Shared needs.** Append:
    * "`UI.pacer(host, pacer)` (the race rail) and `UI.debrief(host, data)`: built in S8
      compete-ui.js, loaded by the practice session defensively (§2.4)."
    * "The runners' Confirm step (S4, S5) through `compete.confirm_next(row)` (R28)."
    * "`progress.causes(…, session=)` (T7), `progress.pace(…, only='contest')` (U7),
      `budget_ms` (P16) and `skill_ratings` (P11) are read by S8."

38. **§3.7.8 Acceptance checks.**
    * Quote: "11. A daily with all answers inside 1 s and ≥ 5 right → /api/contest/daily .me.ranked
      == false and .me.why == 'fast'. It is absent from the board entries."
    * Replace with: "11. A daily with 6 right answers inside 1 s → .me.ranked == false and .me.why
      == 'fast', absent from the board. With 3 such answers → a Confirm step of 3 (C15)."
    * Quote: "28. Browser: during a ranked daily, hiding the tab for 6 s (document.visibilityState
      via Playwright page emulation or a second tab) shows the voided banner on return."
    * Replace "the voided banner" with "the confirm banner ("needs a quick confirm at the end")".
    * Quote: "31. … With a:v2revpod on the podium, only that card has the amber edge and no podium
      card has an orange ground."
    * Keep, and add: "Par rows never carry a rank numeral."
    * Add C1–C25's acceptance lists as items 34 onward.

39. **§3.7.9 Open questions.**
    * Quote: "- Voiding is on for every ranked kind, with a 5 s grace and no void for leaving
      fullscreen. …"
    * Append: "Answered by C15: nothing is zeroed for a blip; flagged right answers are confirmed
      on strict twins."
    * Quote: "- Real-time head-to-head duels (spec/rating.md) are still left out. …"
    * Append: "Races (C8) give head-to-head play on any contest with no live infrastructure."
    * Quote: "- 'Questions right' counts practice answers, so it rewards volume on purpose, as an
      effort board. …"
    * Append: "Over par and Climb (C5, C10) are the learning boards beside it."

### 3.2 Outside the section (Part 2 and sibling files; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| R8 | Unchanged in meaning. A flagged answer is filed with `void` NULL; a failed confirm sets `void` on it afterwards, so boards and mastery leave it out | C15 |
| R12 | Unchanged. Raceable and followable rows are `name` and `anon`; `hidden` rows have no row menu | C8, C9 |
| R25 | New Compete ladders: over-par, won-back, rush, trap-week, class-week; rarity in `/api/me/achievements` (S1) | C18, C23 |
| R28 | Hooks add `compete.pacer(row, answered)`, `compete.confirm_next(row)`, `compete.field_line(…)` and the Rush pick; `state_extra` carries the rail, the field line and the flag banner | C6, C8, C13, C15 |
| R34 | The average stays 95 s a question; the pace bonus and confirms use each question's P16 budget | C3 |
| §2.5 | Tables: `follows(learner, target, at, auto INTEGER DEFAULT 0, week TEXT)` PK (learner, target); `rank_snapshots(day, board, learner, rank, value)` PK (day, board, learner); `nudges(sender, target, class, day, at)` PK (sender, target, day). Columns: `contests.subject TEXT DEFAULT 'math'`, `classes.listed INTEGER DEFAULT 0`. `LEARNER_TABLES` and `progress.carry` include `follows` and `nudges` | C9, C10, C14, C18 |
| §2.6 | Field `target` (a rating, set by S8 server code only, for Rush). `rematch` with `scope: 'misses'` draws each named miss with `want {template: norm}`. Sources `rematch`, `warmup`, `confirm`, `rush` | C2, C7, C13, C15 |
| §2.7 | New key `race_rail` (bool, default true; the session's More menu) | C8 |
| §2.8 | New row "Compete pages": Overview `Enter`; contest page `B` `R` `Y` `,` `.`; boards `J` `K` `↑` `↓` `Enter` `F` `/` `M` `P`. `/` focuses Find a student on the Leaderboard and contest boards (added to the pages where `/` is local) | C24 |
| §2.9 | Providers: F5 `budget_ms` → S8; F4 `ratings.update`, `skill_ratings` → S8; F4 `progress.causes(session=)`, `progress.pace(only=)` → S8; F3 `UI.twinSheet` → S8; S8 `compete.final_focus` → F2; S8 `compete.feed_items(learner, since)` (race, rival, nudge, season items) → S1's feed; S8 `compete.ranks`, `compete.test_rank`, `compete.week_line` → S1, S6; S9 `words.sprint_items`, `words.record_contest_miss` → S8; S2 `classes.listed` → S8 | all |
| `practice.md` P18 | "A challenge parent returns 409" → 409 only while the contest sitting is unfinished. Scope `misses` uses `want` per named miss | C2 |
| `practice.md` P16 | `q.budget_ms` is frozen on each served question, so the contest pace bonus doesn't move mid-day | C3 |
| `today.md` T15 | Copy "ranked by right answers, then time" → "ranked by points: 10 / 20 / 30 by difficulty, +5 within each question's time budget; equal points share a rank" | C3, C16 |
| `today.md` T2, T13 | Due today and Up next list a contest sitting's `rematch_due`; T13's taper lists `compete.final_focus` traps first | C2, C4 |
| `shell-me.md` U11 | Movement reads `rank_snapshots` (daily; the 7-days-ago row), not a weekly snapshot | C10 |
| `shell-me.md` U14 | The Monday sheet shows `compete.week_line` | C21 |
| `shell-me.md` U18 | Feed titles include the Daily and due rematches; push kind `daily` ("Daily Challenge still open", off by default, 2 h before local midnight) | C25 |
| `shell-me.md` U25 | Feed kinds add `race`, `rival`, `nudge`, `season` (from `compete.feed_items`) | C8, C9, C18, C21 |

---

## 4. Rejected

* **Weekly leagues by level** (outcomes #5): My level scope, Over par, Rivals and Near me already
  give every level a weekly race it can win, without placement, division merges and weekly
  closes. Revisit when a few hundred students are active each week.
* **Daily Encore** (outcomes #2): U1 and T2 chaining already put "Next: 3 check-ins due · about
  4 min" on the contest result, one tap away. A second, contest-only interstitial and pref say the
  same thing.
* **Trap Tuesday as a modified Daily** (outcomes #7): the Daily keeps one rule for everyone
  (decision 1's same ten types). The habit theme runs as its own weekly kind (C12).
* **A mixed 12-trap Gauntlet contest** (experience #9): merged into C12, where one habit across
  skills is the lesson (U6's rationale). U6's personal gauntlet already serves your own traps.
* **A Trap-proof leaderboard metric** (unfair-advantage #5): U6's Trap-proof ladder and the Trap
  Index show it. A seventh metric with twelve possible values would be a board of ties.
* **Call your score before each contest** (outcomes #11): `practice.md` rejected the
  score-prediction stepper as novelty; P7's per-answer calibration carries the signal.
* **A modelled Math band from the rating ("Level 4 ≈ 520–600")** (outcomes #4): a second score
  model beside R16's estimate that could contradict it (`today.md` rejected the same kind).
  C11's measured medians show real numbers once n ≥ 20.
* **"Your 650 target ≈ Level 6" and target-based weakest domain** (outcomes #4, #6): both depend
  on the modelled band. The weakest line compares domains to each other instead.
* **Live class mode on a projector** (experience #4, unfair-advantage #8): `shell-me.md` rejected
  the live class check (classroom novelty on polling). Class contests with due times, the grid
  view (C20) and Assign a repair (C19) cover the teaching loop. Revisit when a teacher asks.
* **Paper contests with per-student sheets** (unfair-advantage #12): `shell-me.md` and
  `practice.md` rejected per-student printed packs; Review's worksheet prints.
* **Class battles between two classes** (unfair-advantage #11): the Classes board ranks every
  class on the same fair measure every week. A paired battle adds scheduling for one comparison.
* **Squads as a separate group type** (unfair-advantage #11): R4 makes every group a class.
* **Async duels with a W–L record and duel points** (unfair-advantage #1): a race link on any
  contest, or Challenge a friend with 5 twin questions, is the same play without a new kind. C9's
  head-to-head record counts shared contests.
* **Racing hidden students' rows** (unfair-advantage #1): R12 gives hidden rows no row menu, and
  their choice to hide should cover their runs.
* **A `races` table with revocable codes** (unfair-advantage #1): the board pid in the link works,
  and switching to hidden revokes every link.
* **Three podiums side by side** (unfair-advantage #2): each metric (Points, Over par, Climb,
  Rating by Change) already has its own podium through the metric switch.
* **A separate `rematch` contest kind, disguise twins of right answers, and merging rematches due
  the same day** (outcomes #1): P18's drill rematch with `rematch_due` does the job; Up next lists
  each rematch.
* **A cumulative time-trace chart on every result** (outcomes #3): P16's bar per question against
  its budget, plus the field tick, shows the same thing in one chart the session already has.
* **A lobby pace-guide switch for the Weekly** (outcomes #3): Tests' `test_pace` pref already is
  that switch.
* **A 7-point sparkline on every leaderboard row** (experience table gap): the Move column carries
  direction; a chart per stranger adds little.
* **A "Go to rank" number field** (experience board-navigation gap): Find a student, Near me and
  Jump to me cover it.
* **Swipe between questions in review** (experience #6): review items are rows on the page, and
  the Player (R23) has its keys. A gesture for one list is not worth its conflicts with scrolling.
* **`C` to copy the result** (experience #6): it clashes with choosing C in the contest page's QOTD
  panel.
* **A "Clean" glyph on every board row** (experience integrity gap): the result's Clean run chip
  and the voided counts carry it; a glyph on every row is noise.
* **Spare days on the challenge streak** (unfair-advantage streak gap): one mechanism is enough.
  The 48-hour make-up (C25) keeps the streak by doing the missed Daily; U16's spares stay on the
  study streak.
* **League points for held fixes** (outcomes #5): leagues are out, and Climb and Won back already
  reward learning that lasted.
* **"Put it in my plan": a 6-day taper written into Plan** (outcomes #9): T13 already runs the
  final week from `next.stage`; C4 feeds it the Final's traps instead of writing a second
  schedule.
* **"Send to calculator" on every expression** (outcomes integrity gap): P3 already loads the
  question into Desmos in one tap, and C15 stops pastes into the calculator from voiding.
* **College Board percentile ranges, a same-exam-date percentile and a histogram on the report**
  (report gaps of all three): the report belongs to `spec/v2-upgrades/reports.md`, and R16 owns
  the percentile. Compete adds only its board line (C10).
* **A Monday recap card at the top of Overview** (experience #5): U14's Monday sheet is the one
  weekly review. Compete gives it a line (C21) and shows it in Your stats on Mondays.
