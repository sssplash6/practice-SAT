# v2 upgrades: Compete (contests, rankings, leaderboards)

Written 2026-09-23 for `spec/rebuild-v2.md` §3.7 (lines 8097–9133). It merges three designers'
proposals (outcomes, experience, unfair advantage) into one build-ready list, C1–C27. C26
(twins that never collide) and C27 (champions and past boards) were added in review and sit in
their groups.

* **Precedence.** `spec/v2-decisions.md` wins over this file. This file wins over §3.7 where
  they differ: §3 of this file lists every place that changes. Part 2 resolutions (R1–R38) still
  hold, except the lines named in §3.2 "Outside the section".
* **Siblings.** `shell-me.md`, `today.md` and `practice.md` already specify pieces Compete
  reads: Up next and finish-screen chaining (U1, T2), habit families and the personal gauntlet
  (U6, `server/habits.py`), pace quadrants (U7, `progress.pace`), Climb and rank movement (U11),
  "what moves it" and badge Go (U13), spare days (U16), reminders (U18), the inbox (U25),
  the twin sheet (T5, `UI.twinSheet`), miss causes (T7,
  `progress.causes`), the final stretch (T13, `next.stage`), item and skill ratings (P11,
  `server/ratings.py`), per-question time budgets (P16, `budget_ms`) and Rematch (P18). This
  file reads those functions and never re-specifies them. Where it needs one of them to change,
  the change is in §3.2.
* **The bar.** A student who uses TopTierPrep today opens ours and wants to switch, because
  competing here does more for their score and is fairer, livelier and faster. Parity is
  failure.
* **Names.** Upgrades are C1–C27. Builders are Part 4's tasks. S8 owns `web/compete/**`,
  `server/compete.py`, `server/api_compete.py`, `web/assets/compete-ui.js` and
  `server/checks/s8.py`. The runners are S4 (practice session) and S5 (test window), through
  R28's hooks.
* **Subject-aware.** Per v2-decisions item 3, `contests` gains `subject` (`math` now, `rw` for
  the Word Sprint, C14). Every new payload (par, debrief, ratings, boards, records) carries
  `subject`, and every board query takes it. Math-only rules (blueprints, the level ladder,
  domains) are keyed by subject, not assumed.
* **Twins everywhere** (v2-decisions item 1). Every ranked kind deals twins, so a key can be
  shown at once, a race or a rematch leaks nothing, and a slot is comparable across students.
  C26 makes sure no two entrants of one contest ever get the same whole question.
* **No classes** (v2-decisions item 5). Compete has no teacher or student roles, classes,
  homework, assignments, class codes, class boards or owner "teacher views". Friends compete
  through **private contests**: an invite code or link that Compete owns, which can repeat as a
  series (C18, C19). R4 ("groups are classes") is void, so v2's groups go too: every place
  §3.7 names a group is rewritten in §3.1 entry 40.
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
  * A 3,000-seed survey of whole questions (stem, choices, figure, table) found
    `nleq.sum_product` gives only 201 distinct questions and `sys.relation_pair` 648. Both pass
    v2's slot rule (≥ 15 distinct in 18 seeds), which checks short-range variety only. C26
    replaces it with a supply floor.
  * P11's item priors are three values (900 / 1100 / 1300), and no (template, tier) has 20 first
    tries yet, so every item inside a tier starts at the same rating (C13 spreads them).
  * P11's item levels are L1–L7 (1,300 = L6). Compete's student ladder is Level 1–10 (1,300 =
    Level 5). The two scales never share the word "Level" on one screen (C13).

---

## 1. Scorecard

"v2 spec" is §3.7 as written. The verdict says why ours is way better. Where v2 was only at
parity (or below), the verdict names the upgrade that fixes it.

| # | Their feature | Their version | v2 spec | After these upgrades | Verdict |
|---|---|---|---|---|---|
| 1 | Three sidebar sections | Contests & Challenges, Contest Rankings, Leaderboards: three nav items, three trips | One Compete section (R1: sidebar item; avatar menu on phone), four pages under a sub-nav | Today's challenge pill starts question 1 in one tap. A Compete key map; board scopes switch from cache in under 100 ms (C24) | **WAY BETTER already in v2** (one section, always live). **C24** makes it 1 tap to Q1 and 0 to your rank. Theirs takes about 8 actions and a wait for the contest to close, behind a paid plan. |
| 2 | Global Leaderboard card | "GLOBAL LEADERBOARD", Rankings link; "No rankings yet. Finish a contest to be the first on the board." | E: THIS WEEK · POINTS, the top 5, then your row | The top 5 kept, then a separator, then you ± 2, every row with movement and the gap. Chips for Points · Over par · Climb, each with its own top 5. Par rows fill it when fewer than 5 have played (C10, C5, C6) | v2 PARITY: a top-5 card and one row for you. **C10 + C6 → WAY BETTER.** It keeps their whole leader list, adds your own race with direction and distance, lets every level see a top 5 it can reach, and is never empty. |
| 3 | Your Contest Stats card | Trophy, "Not ranked yet", then your global rank | D: rating, level and six rank tiles | Every tile carries movement and its next milestone ("40 pts to top 10%"). The Rating card shows the Contest rating with "Level 4 in +17 ≈ 2 hard rights", and beside it, labelled apart, four Skill rating rows from all practice. A rival line with Race (C10, C11, C9) | v2 PARITY: more static numbers of the same kind. **→ WAY BETTER.** Each number says where it is going and what moves it, and each rating says what it counts. |
| 4 | Active contests list | Posted by hand; empty on both walks | Daily and Sprint always live; Weekly or Final and the next Sprint upcoming; Private | Adds Trap of the week, Rush and the Word Sprint (C12–C14). Each row says what it trains and shows your par against your last result (C7) | **WAY BETTER already in v2** (never empty). Now every row also says why to enter. |
| 5 | Contest types | Daily / Weekly / Seasonal (bundle), never seen live | Daily, Sprint, Weekly Module, Seasons + Season Final, Private | Trap of the week: one misconception habit in every question, across skills. Rush: an adaptive run that ends on three strikes. Word Sprint: SAT-form Words in Context and Transitions items, each wrong option naming its trap (C12–C14) | **WAY BETTER.** Eight kinds that schedule themselves. Three of them exist only because every wrong option names its misconception and the bank never runs out. |
| 6 | Contest tiers by plan | Free: none. Pro: standard. Elite: prize contests | Everything free | Everything free, and winning lasts: every closed week and season keeps its final board, a Champions hall lists each podium (Points, Over par, Most improved, and one per level band), and a season podium earns a ring on the level badge and a title on Me (C27) | v2 BELOW: no contest had a stake, and a closed period could not be viewed. **C27 → WAY BETTER.** Free, and a win is on record for good, at every level, without a paywall. |
| 7 | Scoring rule | Points by difficulty plus a raw speed bonus | 10 / 20 / 30, +5 within a flat 95 s, +10 finish | +5 within each question's own time budget (easy 1:05, medium 1:35, hard 2:06; C3). Par and Over par: the points a student at your rating is expected to score on your ten, and a board ranked on beating it (C5) | v2 PARITY in shape. A flat 95 s is free on easy questions and pushes students to rush hard ones. **C3 + C5 → WAY BETTER.** It rewards real SAT pacing and gives every level a score it can beat today. |
| 8 | Integrity rules | Fullscreen; switching tabs, leaving fullscreen, copying or pasting voids the open question at once | Void after 5 s hidden or on copy/cut/paste; optional fullscreen; too fast → unranked | **Verify, don't void.** Flags: the tab hidden ≥ 5 s, the window out of focus ≥ 5 s (a second window or monitor), a copy of the stem followed by leaving the window, a paste outside our calculator, and too-fast answers. A flagged right answer is confirmed at hand-in on a strict twin, and keeps its points if the twin is right. Copying into our calculator is free. Board rows carry a legend-backed Clean / Confirmed mark (C15) | v2 PARITY: their penalty with a grace, and it voided copying a stem into our own Desmos. **C15 → WAY BETTER.** It catches everything theirs catches (their copy trigger becomes copy-then-leave), plus a second window theirs misses, yet a phone notification never costs a minor a point, and a looked-up answer has to be repeated on new numbers. Only an unlimited twin supply allows that. |
| 9 | One attempt, delayed reveal | "One attempt per contest. Answers are revealed after the contest ends." | The key after each question (twins); ghost sittings of closed contests | No two entrants ever share a whole question, and every entrant gets the same ten types in the same order (C26). Rematch the misses on new numbers in 2 days, with the same traps (C2). Race any finished run (C8) | **WAY BETTER already in v2**, and C26 makes "answers can't be passed on" hold at any field size. A finished contest keeps teaching and keeps being playable. |
| 10 | Resume limit | Over the limit, the attempt is scored 0 | Leaving skips the open question and stops the clock; nothing zeroes | A blip or leave during a question is confirmed, not zeroed (C15) | **WAY BETTER.** |
| 11 | Per-contest stats | Score / Correct / Incorrect / Skipped / Voided | The same counts, the points parts, mastery bars, mistakes opened and closed | **Debrief:** points lost by cause and by misconception, what each miss cost in places ("Q6 right → #2"), Fix it · 3 on same-trap twins, a Rematch in 2 days, time against each question's budget (C1–C3) | v2 PARITY: the same five counts. **C1–C3 → WAY BETTER.** A result becomes a priced to-do list. |
| 12 | Anonymous names | "Anonymous student" on some boards | Hidden rows keep their rank as "Anonymous" | Hiding costs nothing: par, your own-best and SAT-pace pacers, and rivals shown only to you (C5, C8, C9) | **WAY BETTER already in v2** (ranks stay honest). |
| 13 | Performance Summary | Empty, with "Browse contests" | Ten tiles and a Top % / Rating chart | A "Since last week" line whose parts link to their drills. An Over par series on the chart. A Records row (C10, C5, C21) | v2 PARITY: a richer dashboard that points nowhere. **→ WAY BETTER.** |
| 14 | Contest Leaderboard picker | "Pick a contest you've finished to see how you placed." | A select, then a mini board | Folded into Contest history. Each row expands in place to your strip, a mini board, the debrief's top row, the follow-up and Race (C22) | v2 PARITY, and a duplicate of History. **C22 → WAY BETTER.** One list, one tap, with the next action. |
| 15 | Your Rankings card | Global rank, Contests played | A table: Everyone / Country / groups × Week / Month / Season / All | Every cell adds movement and the gap to the next place. Rows: Everyone, Country, Following, My level, Same exam date, and each private series you're in (C10, C9, C18). Last week's and last season's final places sit beside the live ones (C27) | v2 PARITY. **→ WAY BETTER.** |
| 16 | Time Analysis | Average seconds per answered question by difficulty; "under pressure" copy | Pace ×4 views against the field and a flat 95 s | Reads U7's `progress.pace` with a contest filter: tier budgets, each row's drill, time-sink and banked trends. A Time block on every result (C3) | v2 PARITY: numbers with no action, and a second pace calculation beside U7. **C3 → WAY BETTER.** |
| 17 | Badge Progress | Empty | The Compete badges through R25, with progress and dates | Go on every badge in progress starts what advances it, including the Compete badges R25 folded into Shell's tiered rules. Rarity ("earned by 4%"). New ladders: Over par, Won back, Rush, Trap-proof week, Full house (C23) | **WAY BETTER already in v2.** Go makes progress drive practice. |
| 18 | Contest History | Empty list | A table with kind and sort filters, R·W·S·V, rank, top %, rating Δ | Over par and Follow-up columns, an "Open follow-ups (n)" filter, rows that expand (C22) | v2 PARITY: a log. **C22 → WAY BETTER.** A to-do list. |
| 19 | Rankings layout | Two-column grid of six cards | Six ordered sections, two-column where noted | Adds the Rating card, Trap Index, Rivals, Records and the level ladder | **WAY BETTER already in v2.** Every section works and says what moves it. |
| 20 | Leaderboard hero and podium | Centred title, a large empty top-3 space | Podium 2 · 1 · 3 with values; empty cards read "Open" | A "Your path" line under it ("#12 · 60 pts to top 10 · 140 to the podium"). The podium follows the metric, so Over par and Climb give every level one to reach. Par rows instead of "Open" (C10, C5, C6) | v2 PARITY. **→ WAY BETTER.** |
| 21 | Period control | Weekly / Monthly (default) / Yearly | Week / Month / Season / Year / All, and 7d (R3); reset time stated | A past-period stepper ("‹ Week 38 ›", "‹ Road to Sep 12 ›") opens any closed week, month, season or year with its final standings, frozen at the close (C27) | v2 PARITY: only the live period could be seen, so last week's winner had nothing to show. **C27 → WAY BETTER.** The season ends on a real SAT date, the reset is stated in your time, and every closed period stays on record. |
| 22 | Scope | Global ↔ your country | Everyone / Near me / Country / each group / same exam date (R3) | Adds Following, My level (± 1) and your extended-time placing; groups go (decision 5), and a private series' own board ranks friends round by round (C9, C17, C18) | v2 PARITY in kind. **→ WAY BETTER.** Every student has a board of people they actually race. |
| 23 | Metric | Contest Points ǀ Overall Score | Points / Rating / Questions right / Test score | Adds Over par and Climb, a Rating sort by Change, and a separate **Skill rating** metric (all practice) with the Domain select (C5, C10, C11) | v2 PARITY: it ranks ability or volume. **→ WAY BETTER.** Two boards reward improvement, and the skill board splits by domain under its own name, so no metric changes source when a filter moves. |
| 24 | Leaderboard table | RANK / USERNAME / ACCURACY / TIME; scrolls without end to "No more rankings yet." | Rank / Student + level / metric / Accuracy / Avg time / Contests; paging; you-bar | Move and Gap columns, level separators, Find a student, a you-bar naming the cheapest way past the next row ("22 pts · one medium right at pace"), row actions Race / Follow / Compare, a Clean / Confirmed mark with its legend on contest boards, and a champion ring on last season's podium (C10, C8, C9, C6, C15, C27) | v2 PARITY: a list to read. **→ WAY BETTER.** |
| 25 | Profile Performance Snapshot | Global Rank 128, Country Rank 43, with no contests played | Me Boards: ranks, "—" until a ranked contest | Movement and gap from one source, `compete.ranks` (U11, C10) | **WAY BETTER.** Honest ranks with direction. |
| 26 | Profile Achievements | Four hard-coded tiles; "View All" is dead | The 4 latest earned + All badges | Go on each (C23) | **WAY BETTER.** |
| 27 | Ranked pill and percentile on the report | "Practice test — not ranked"; "N% scored at or below you on their first attempt" | R16's pill and percentile | The pill adds this sitting's place on the Test score board and your Climb ("#41 of 212 this month · Climb +90, ahead of 74%"), with links (C10) | v2 PARITY: their sentence. **C10 → WAY BETTER.** A sitting is placed on a live board and on a fair improvement race. Other report upgrades are `reports.md`'s. |
| 28 | Username on boards | The Google account name | R12 handles, unique, name / anon / hidden, name reports | Follow and Find a student by unique name (C9) | **WAY BETTER already in v2.** |
| 29 | Question of the Day | Two a day, one attempt, a "1 day" streak pill; the right choice not shown | Today owns it (R27); the contest page's QOTD panel with the spread, past days and streak | Unchanged here (Today's T14) | **WAY BETTER** (`today.md` #14). |
| 30 | Classes and homework (hidden); /teacher | Hidden pages; homework with due dates; a teacher dashboard | Groups, which R4 made classes; group contests with a due time; an owner results table with CSV | Classes, homework and teacher views are out (decision 5: a separate platform has them). What friends used them for stays and grows: private contests by invite code or link that can repeat as a series, with a series board ranked on points and on Over par, entrant dots, a series streak and nudges, rounds built from "my" or "our" open traps, and the grid view with each question's top trap for every entrant (C18, C19, C20) | Out of scope for Compete (decision 5). The friends' side → **WAY BETTER** than theirs: their private play exists only inside a teacher's hidden class pages; ours is a link, free, with a reason to come back every round. |
| 31 | Share | `navigator.share`, which froze the page; a shared QBank landing | Copy result (plain text) + Challenge a friend | **Race links.** The copied link races your run on twins, ranked if it is the friend's first sitting, and the result comes back to your inbox (C8) | v2 PARITY: a brag that asks nothing. **C8 → WAY BETTER.** A share is a fair race that needs no account. |
| 32 | Nothing is live without staff | Empty on both walks | Self-scheduling contests; field lines at ≥ 5, top % at ≥ 10, podium at 3 | Par rows at Levels 3/5/7/9, your best and 7-day average rows, a field line that falls back to every first try on the type and then to your level's expectation, SAT-pace and own-best pacers (C6, C8) | v2 still looks empty with 7 learners. **C6 + C8 → WAY BETTER.** Meaningful from the first sitting with nobody else on the site, and it never invents people. |
| 33 | Contest timing | One fixed fullscreen time | Fixed clocks; `prefs.test_timing` ignored | 1.5× and 2× in every contest, never shown publicly. The lobby states where an extended sitting is placed, and a one-time sheet confirms it before the first extended contest. Private contests rank extended sittings with everyone (C17) | v2 BELOW: it shut out 504/IEP students, although Tests supports them. **C17 → WAY BETTER.** Nothing about placement happens without the student being told first. |

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
side: D Your stats (rating card, movement) · Rivals · H Season · E Board (top 5 + you ± 2)
      · Traps this week · Champions (C27) · F Next badges (Go)
      · G Your private contests (series streak, C18)
top, when a season has just closed: the season recap card (C21)
```
Phone order: recap, A, D, Rivals, H, B, E, Traps, Champions, C, F, G.

**Contest page** main column: state panel → **Debrief** (C1) → **Time** (C3) → Board (List ·
Grid, C20) → Review → Traps. Side: rules, pacer select (C8), QOTD panel, entrants (private),
owner controls (private: code, link, close, extend, rename, remove, delete; no results table,
decision 5). Phone: one column in that order, with a 56 px thumb bar (C24).

**Leaderboard:** controls (Metric · Period with its ‹ › stepper · Scope · Domain · Subject) →
podium → "Your path" line → Find a student → table.

**Your rankings:** Performance summary (with "Since last week") → Rating card (C11) | Pace (C3)
→ Records (C21) → Trap Index (C12) → Rivals (C9) → Badges → Seasons → Champions (C27) → Level
ladder (C11) → Contest history (C22). The "How you placed" picker goes (C22).

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

**Result panel, after the band.** Which block shows depends on the student's exam date (the
one Plan and Today's picker store, `prefs.exam_date`):
* **"Your last week"**, only when `exam_date` equals this season's SAT date. Day rows from the
  day after the Final to the eve, read from T13's `next.stage` preview, with the Final's items
  first:
  * the 3 traps that cost the most points in the Final (C1's `by_norm`), each "Fix: Used the
    diameter as the radius · ~10 min";
  * "Skip first on test day: Circles, Percentages": skills with a Final question over 2× budget
    that was also wrong (they join U7's list, which Tests' checklist reads);
  * T13's own rows: rehearsal, sweep, eve rest.
  * No second schedule. T13 runs the week; this block shows it and puts the Final first.
* **"Final focus"**, when the exam date is another day or not set. Two rows and no day rows:
  * "3 traps to fix: Used the diameter as the radius · Swapped the columns · Percent of what?",
    each with **Fix it · 3** (C1);
  * "Skip first on test day: Circles, Percentages".
  * Helper, with an exam date: "Your SAT is Nov 7. These lead your final week when it starts on
    Oct 31." Without one: "Set your SAT date and these lead your final week." + quiet **Set
    date** (Today's picker).
  * `final_focus` still feeds `next.stage`, which lists these traps first when that student's
    own taper starts. No eve rest and no taper rows are shown for a date that isn't this one.
* Either way: quiet **Test-day card** → `/compete/contest/?id=final-…&card=1`.

**Test-day card.** A print page (`@media print`, no chrome), one sheet at A4 and Letter:
* the pacing rule from P16's budgets: "Move on at 2× the budget and come back: easy 2:10 ·
  medium 3:10 · hard 4:12";
* the skip-first list;
* the 3 tells of your top habits (U6);
* the Final's band and route;
* the doors line, fixed now as one constant in `compete.py` (`DOORS_LINE`, editable later):
  "Doors open by 7:45 AM; check your admission ticket."
* the date line: your exam date when set ("SAT · Sat Nov 7"), else the season's.

**Data.** `compete.final_focus(learner)` → `{sid, traps: [trap ids], skip_first: [topics], band,
route, mode: 'last_week' | 'focus'}` (`last_week` only when `exam_date` equals the season's SAT
date). F2's taper lists those traps first until each closes, whenever the student's taper
starts.

**Acceptance.**
1. A Final with 2 wrong answers over 2× budget in circles → `final_focus.skip_first` contains
   `circles`.
2. With exam date = Final + 7 and `final_focus.traps = [t]`, `GET /api/next` during the taper
   lists trap `t` before any other trap, and `final_focus.mode == 'last_week'`.
3. With exam date = Final + 42 (or none), `mode == 'focus'`: the result panel has no eve-rest
   row and no day rows, and has the "3 traps to fix" and "Skip first" rows. With exam date =
   Final + 42, `GET /api/next` on day 36 after the Final (that student's taper) lists trap `t`
   first.
4. The card page has no `nav`, contains "Doors open by 7:45 AM", and a Playwright print-to-PDF
   of it is one page at A4 and Letter.

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
* **Ladder cells** show each slot's skill and your chance on it, from the same `E_i`: "Q9 ·
  Circles · Hard", a thin fill bar and "34%". Every entrant sees the same ladder, so it is fair,
  and knowing the ten skills is study, not a leak: twins mean nobody can see the numbers. The
  template (the exact question type) is never shown before you start. This replaces v2's
  domains-only ladder, one rule for the lobby, the warm-up and the result.
* **Warm up · 6** (replaces "Practice for it"): 2 questions each on the skill and tier of your 3
  lowest-chance slots, drawn from templates **not** in the contest's slot list, key after each.
  The button's line names them: "Circles · Percentages · Linear functions". It is offered only
  before you start.
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
3. `ladder[i].chance` equals `E_i` for the learner's frozen rating, to 2 decimals, and
   `ladder[i]` has `topic` and `tier` but no `template` before the sitting starts.
4. The warm-up's served topics equal the `topic` of the 3 lowest-chance `ladder` cells.

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
v2 a friends board needed a group, which R4 turned into a class (void under decision 5). Follow
needs nothing: no code, no account, no owner.

* **Follow** (row menu, and `F` on a focused row): named and handle rows. Private, one-way, at
  most 50, no follower lists, no messages. Following a student who later hides drops them.
* **Rivals**: three a week, picked lazily on the first request of the ISO week:
  1. students you follow within ± 200 rating, most recently shared contest first;
  2. then public learners with a ranked contest in the last 14 days and a rating within ± 100,
     widening to ± 200, then the nearest; same exam date first, then fellow entrants of your
     private contests (C18);
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
  `points:month`, `points:season`, `points:all`, `net:week`, `rating`, `skill`, `skill:<domain>`
  and `right:7d` (U11 reads the last). Kept 90 days. `ponytail:` one full write per board per day;
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
* **Overview E**: the top 5, a separator, then you ± 2 (merged into the top 5 when you are in
  it or next to it), every row with movement and gap. Metric chips **Points · Over par ·
  Climb**, each with its own top 5. Fewer than 5 players: par rows and your best fill the
  empty places (C6). Footer "Full board ›" with the chip's metric in the link.
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
5. `GET /api/compete` → `board_preview` has the top 5 entries plus you ± 2; with you at #12 it
   has 10 rows with a separator after #5, and with you at #6 it has 8 rows and no separator.

#### C11. Contest rating and Skill ratings, labelled apart; the next level in questions; a measured level bridge

*From: outcomes #6, experience #11, unfair-advantage #9. Effort S. Builders: S8 (the Rating
card, the Skill rating board, the ladder table), F4 (P11's `skill_ratings`), S1 (Me's Rating
tile tooltip).*

**Why.** One rating hides where the points are. A rating per domain and per skill says where
the next 30 minutes pay most, and which contest trains it. Theirs has no rating at all, and v2
disabled the domain filter for Rating.

**Two ratings, never mixed** (design rule 5, one source per fact). They are two systems that
measure different things, so every surface names which one it shows, and neither is ever drawn
as a breakdown of the other:
* **Contest rating** = `learners.rating`: ranked contest answers only (K 32, then 12). It drives
  levels on boards, par (C5), rivals (C9) and the Rating board.
* **Skill rating** = P11's `skill_ratings(learner, topic)`: every clean first try in any mode,
  contests included (K 32, then 16). A domain's Skill rating is the n-weighted mean of its
  topics', and its n is their sum; "All domains" is the n-weighted mean of all 19. Placing while
  a domain has n < 15 (a skill n < 10).
* The level word applies to both through the same 1–10 ladder (`spec/rating.md`), and a level
  badge next to a Skill rating is outlined, not filled, so the two never look alike.
* One line under the card's title says it: "Contest rating moves only on ranked contest
  answers. Skill ratings move on every first try, in practice, tests and contests."

**Rating card** (Your rankings; a compact version in Overview D shows the Contest rating block
only, plus the Weakest line):
* **Contest rating** block: the badge (48 px), "Contest rating 1,084 · Level 3 · 212 rated
  answers"; **Level 4 in +17 ≈ 2 hard rights at your level**: ceil(gap / (K × (1 − E_hard))),
  with K your current contest K and E_hard against the mean hard item rating.
* **Skill ratings (all practice)** block, headed so, below a rule:
  * four domain rows: glyph, name, 32 px outlined badge, "Skill 1,240 · Level 4 · 86 answers ·
    ▲40 in 30 days" (from `rank_snapshots` `skill:<domain>`), a bar on the level ladder, and an
    expectation line from item ratings: "At 890 you'd get about 45% of medium Geometry
    questions";
  * a **Skills · 19** disclosure listing each topic the same way;
  * **Weakest** line: "Geometry & Trig · Skill Level 3 (your others Level 5)" + pill **Practise
    Geometry & Trig · 10** (`{topics: its skills, zone: 'stretch', count: 10}`, P11) + quiet
    **Rush Geometry** (C13) + quiet "Sprint · Geometry week in 9 days · Add to calendar".
* **Result panel**: the Contest rating tile ("+14 → 1,084"), and beside it a separate tile
  **Skill ratings** with the domain deltas, "Algebra +18 · Geometry −6" (aggregates stored in
  `result.domains` at start and at finish).
* **Leaderboard**: **Rating** is the Contest rating, and the Domain select stays disabled for it
  (tooltip "Contest rating is one number; pick Skill rating to rank a domain"). A separate metric
  **Skill rating** ranks the chosen domain's aggregate ("All domains" by default) among learners
  with n ≥ 15 there and a clean answer in it during the period. Its column header, podium and
  you-bar read "Skill rating · Geometry & Trig".
* **Level ladder table** (Your rankings): Level · Rating · Students at it · Timed-section median.
  The last column is the median R16 `mean3` midpoint of learners at that level with a timed full
  section within 30 days, shown per level only when n ≥ 20 ("630 · 38 students"); otherwise
  "—". It is measured, never modelled. The same line is the level badge's tooltip.

**Acceptance.**
1. One clean right Geometry practice answer changes that topic's `skill_ratings` row and the
   Geometry aggregate, leaves the other domains' aggregates unchanged, and leaves
   `learners.rating` unchanged.
2. `/api/leaderboard?metric=skill&domain=Geometry%20%26%20Trigonometry` orders by the Geometry
   aggregate; `?metric=rating&domain=…` → 400 `{"error": "domain applies to metric=skill"}`.
3. Browser: on Your rankings, the Leaderboard and the result panel, every rating number sits
   under or beside the words "Contest rating" or "Skill rating", and no surface shows a Skill
   rating row inside the Contest rating block.
4. With 19 learners at Level 5 holding a recent timed section, that ladder cell is "—"; with 20
   it shows a number.
5. The "Level N in" line for rating 1,084 (K 12, hard items at 1,300) reads "+17 ≈ 2 hard
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
* 10 slots, 3E / 4M / 3H, over at least 5 topics (the topic floor; 3 when relaxed, below).
  Each slot is a template with a distractor in
  the week's family, and each twin is drawn with `want {template: family regex}`, so every
  question holds the trap. Slots are multiple choice, except grid-in slots whose template's
  named grid-in mistakes match the family.
* Answer clock 950 s, twins, key after each question, ranked first sitting, rated, season
  points, par (C5). Points as the Daily (maximum 260).
* **Theme**: `compete.trap_theme(week)` = the family with the highest fall rate last week (wrong
  first tries naming it ÷ first tries on questions carrying it, all modes, ≥ 30 chances),
  skipping the last W themes. Before there is data, it walks the qualified families in U6's
  order.
* **Which families can theme a week** (`compete.trap_families()`, computed at startup and
  cached):
  * `slip` (arithmetic slip) is never a theme: it is not a habit the tell can catch across
    skills.
  * A template is **slot-feasible** for a family at a tier when it passes C26's supply floor, can
    serve that tier, and has a surveyed distractor (or, for grid-ins, a named grid-in mistake)
    whose reason matches the family regex.
  * A family **qualifies** when every tier has ≥ 10 slot-feasible templates and they span ≥ 5
    topics.
  * The no-repeat window is W = min(4, qualified − 1).
  * If fewer than 5 families qualify, the topic floor relaxes to 3 for the families that reach 3
    topics but not 5, which then qualify too, and W is recomputed. If still fewer than 2
    qualify, the Trap of the week is not scheduled that week and the Contests list shows
    nothing in its place (acceptance 4 is then skipped by `s8.py` with a printed reason).
  * `python3 server/checks/s8.py --traps` prints, per family and tier, the slot-feasible
    template count and topic count, which families qualify, the topic floor used and W, and
    asserts the chosen setting builds.
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
2. `trap_theme` of a week never equals any of the W previous weeks' themes, and is never
   `slip`.
3. A learner with 5 resisted chances over 3 templates in 30 days → that family has `proven:
   true`.
4. `GET /api/contests?status=live` always contains a `trap` row.
5. On the shipped bank, `s8.py --traps` builds 12 consecutive `trap_theme` weeks (with no
   answer data, so the walk is used), and every one has 10 slots, 3E / 4M / 3H, over at least
   the topic floor it printed.

#### C13. Rush: three strikes, and the difficulty climbs with you

*From: unfair-advantage #6. Effort M. Builders: S8 (the kind, boards, results), F5 (a `target`
rating pick that respects the learner's seen set), F4 (per-template priors in `ratings.py`,
§3.2), S4 (Sprint mode's header variant).*

**Why.** An endless run that seeks your level is two minutes of fresh, well-aimed practice you
can replay all day, and the fastest way through placement. A finite bank runs dry at the top of a
skill. Theirs has no retakeable ranked mode.

* **The kind.** `rush-YYYY-Www`, always live, subject `math`; an Overview row "Rush · best 17
  today" and a **Rush** tab on the Sprint lobby. A **Domain** select: All · Algebra · Advanced
  Math · Problem-Solving & Data Analysis · Geometry & Trig.
* **Item spread at launch** (so the climb has more than three steps). P11's priors are one value
  per tier, and no item is measured yet. F4's `ratings.py` gives each (template, tier) its own
  prior, written once at backfill and replaced by the item's own rating as answers arrive:
  * **Measured share first**: when the pair has ≥ 20 first tries in any mode (R8 clean), prior
    = the answerers' mean Skill rating − 400 × log10(p / (1 − p)), p its right share (clamped
    0.05–0.95), shrunk toward the tier prior by n / (n + 20).
  * **Otherwise a structural prior** from fields every Item already has, over 18 surveyed
    seeds: the tier prior + 50 when `fmt` is `spr` (grid-in), + 25 when it has a `figure` or
    `table`, and + 25 per rationale sentence above the tier's median sentence count (− 25 per
    sentence below); clamped to ± 150 of the tier prior.
  * `ratings.py` `__main__` prints the spread per tier and asserts that each tier has at least
    8 distinct prior values.
* **Run.** It starts at a question rated your Skill rating in the chosen domain (All: the
  aggregate) − 300 (700 while Placing).
  * A right answer moves the target up 60.
  * A miss moves it down 120 and costs a strike.
  * An answer over 1.5× its budget (× timing factor) is also a strike (P16's "skip for now"
    threshold).
  * 3 strikes end the run.
  * Each question is the unseen (template, tier) whose item rating is nearest the target at or
    above it after a right answer (at or below after a miss), round-robin over the chosen
    domains. A run never repeats a template and never serves a (template, seed) you have seen.
  * **Top of the bank**: when the target passes the highest-rated unused item in the chosen
    domains, the target is capped there and the header shows "Top of the bank". The run goes on
    at the hardest items left; the board's top-item column reads "Top".
* **Item labels.** Rush names an item's difficulty with P11's L-code ("L6"), the code Practice's
  TypeRow uses, and never the word "Level", which on Compete screens is the student's 1–10
  ladder. The level badge beside it stays the student's.
* **Runner**: Sprint mode. Header "Right 14 · strikes ✕✕○ · now L6", or "Right 22 · strikes
  ✕○○ · Top of the bank". The verdict shows the key and the mistake line, with "Why" collapsed.
* **End**: "14 right · reached L6 items · best ever 17", a strip shaded by item L-code with a
  legend (L1 … L7, Top), "Your 3 strikes: Swapped the columns · slow · Used the diameter as the
  radius" + **Practice these 3**.
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
4. For a learner with a Skill rating of 1,600, the first 5 right answers in a run serve strictly
   rising item ratings, or the header reads "Top of the bank" from the answer where they stop
   rising.
5. `python3 server/ratings.py` reports ≥ 8 distinct priors per tier on the shipped bank, and
   no Rush screen (runner, end, board) contains the word "Level" next to an item.

#### C14. Word Sprint: Reading & Writing enters Compete, and contests become subject-aware

*From: experience #12; v2-decisions items 2 and 3. Effort M. Builders: F4 (`contests.subject`),
S8 (the kind, the board, the Subject filter), S9 (`words.sprint_items`,
`words.record_contest_miss`, W16's run over W1 and W2 items; the words.md change is in §3.2).*

**Why.** Words is the first piece of Reading & Writing on the site (decision 2), and the platform
will grow to the full SAT (decision 3). A weekly race on the SAT's own vocabulary item types gives
Words a reason to come back, and building Compete subject-aware now makes R&W contests additive
later. Theirs covers both sections but was never live, and their vocabulary quiz is a definition
matched to word tiles. Ours races the real forms: W1's Words in Context and W2's Transitions,
generated without limit, each wrong option naming its trap.

**Overrides words.md.** words.md rejected "a daily words challenge in Compete, a daily sprint
board" and keeps R&W out of Compete. §3.2 changes that one line: Compete runs **one weekly Word
Sprint board**, which is W16's run and scoring with W1 and W2 items and a board. Nothing else
in words.md changes: R&W answers stay in `word_reviews`, never in `attempts`, the Math rating,
Practice or Tests.

* **The kind.** `words-YYYY-Www`, subject `rw`, always live (Mon 00:00 UTC → next Mon, as the
  Sprint). Runs as many as you like; the week's best run counts.
* **The run is W16's**, one rule, with its items changed:
  * one key (or tap) answers and moves on at once; a slim timer bar; misses collect in a tray;
  * **score = right − wrong ÷ 3**, one decimal (W16's rule, so guessing doesn't pay); skips
    score 0;
  * the clock is **4:00** (× timing factor, C17), not W16's 60 or 120 s, because an SAT-form
    item is a short text, not a single word. The lobby states it: "4 minutes · Words in Context
    and Transitions · right − wrong ÷ 3".
* **Items** are `words.sprint_items(learner, seed, n, level)`: W1 Words in Context and W2
  Transitions items from `server/rw_items.py`, alternating, over the SAT word list and
  transitions (decision 2). The level starts at your Words placement (W10) and rises one band
  every 5 answers. Each learner gets their own items (twins in kind: the same forms and levels,
  different texts).
* **End screen**: "Score 11.3 · 13 right · 5 wrong · best this week 12.0", then:
  * **Traps**, like the Math debrief: "Traps: 2 × Right idea, wrong strength · 1 × Topical lure ·
    1 × Read contrast as concession", counted from the named trap of each wrong option (W1's
    trap names, W2's logic names);
  * the **Missed** tray with meanings (W16), **Study these** (W16's cards run of them) and, on
    each missed item, **Another like this** (W1 / W2's one-key generator).
* Sprint answers are filed in `word_reviews` with mode `sprint` and never promote; a miss marks
  the word Missed lately without dropping its box (W16), through
  `words.record_contest_miss(learner, word, trap)`.
* Not rated (the Math rating stays Math). Counts for the R&W season standings (Σ of weekly best
  scores) and for badges.
* **Board**: best run this week; order score ↓, then right ↓ (C16: time never ranks). Columns:
  Rank | Student | Score | Right | Wrong | Runs | Move.
* **Subject everywhere.** `contests.subject`. The Leaderboard gets a **Subject** select (Math
  default · Reading & Writing). Season standings and boards are per subject; the Season card
  shows an R&W line only when you have R&W runs. Today's Words tile shows "Word Sprint · best
  12.0".

**Data.** `words.sprint_items(learner, seed, n, level)` → W1 / W2 items in the bank's Item shape
(S9, defined in words.md by §3.2); `words.record_contest_miss(learner, word, trap)` (S9). Word
Sprint sittings are `sessions.kind = 'words'` (R36) with `contest` set; `result = {score, right,
wrong, skipped, traps: [{trap, label, n}]}`.

**Acceptance.**
1. `GET /api/contests?status=live` has a row with `kind == 'words'` and `subject == 'rw'`.
2. `GET /api/leaderboard?metric=points&subject=math` never includes Word Sprint runs, and no
   Word Sprint answer adds a row to `attempts`.
3. A run with 9 right and 3 wrong → `result.score == 8.0`.
4. A word missed in a Word Sprint has its Missed lately flag set and its `box` unchanged (W16's
   rule).
5. A run with 2 wrong W1 answers whose chosen options name trap T → `result.traps` has `{trap:
   T, n: 2}`, and the end screen's Traps line names it.
6. Every served item has `kind` in `incontext`, `transition` (W1, W2 item types), never a
   definition-to-word tile.

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
* **the window out of focus for ≥ 5 s**: `document.hasFocus()` polled each second is false (a
  second window, another app, a second monitor). Focus inside the calculator host counts as in
  focus: the calculator's iframe keeps `hasFocus()` true, and `document.activeElement` being the
  calculator host is checked as well;
* **copy, then leave**: a `copy` whose selection is inside the stem or the choices, followed
  within 20 s by the window losing focus or the tab hiding, for any length. This is their copy
  trigger, aimed at the one case it exists for (pasting the question elsewhere). A copy followed
  by a paste into our calculator raises nothing;
* a paste whose target is outside the calculator host;
* a `pagehide` beacon;
* **fast**: a right answer with `sms` < max(4 s, the 2nd percentile of clean right times on that
  (template, tier), once n ≥ 50).
A copy on its own, and cut, trigger nothing. `ponytail:` the triggers see only this page; a
second device is out of reach of any web page, which is why a flag leads to a confirm on new
numbers rather than a zero.

**What a flag does.** Only a flagged **right** answer needs confirming; a flagged wrong answer
is just wrong. The verdict still shows the key and rationale. The first flag shows a banner
naming the trigger: "Question 4 needs a quick confirm at the end: the tab was hidden for 12 s."
· "…: this window was out of focus for 8 s." · "…: the question was copied and the window
left."

**Confirm step**, after the last question and before the result:
* a sheet: "Confirm 2 answers · a twin of each · stay on this tab";
* each confirm is a twin of the flagged slot (same template, tier and format; a whole question
  not yet dealt in the contest, C26), in **strict mode**: every trigger above forfeits it at
  once, with no 5 s grace (the tab hidden, the window out of focus, copy-then-leave, a paste
  outside the calculator, pagehide), and so does a fast answer;
* its own countdown is the question's budget × timing factor;
* a right confirm keeps the slot's base points (the pace bonus only if both answers came within
  budget); a wrong, skipped or forfeited confirm scores the slot 0 and counts it Voided;
* at most 5 confirms; flags beyond the fifth are voided;
* more than 5 **fast** flags in one sitting → no confirm step, and the sitting is Unranked
  "fast": "Not ranked: answers came in faster than the questions can be read.";
* leaving during the step forfeits the open confirm (the leave sheet says so).
* **Test window, Weekly Module** (one module): the same step after hand-in and before the result
  (S5).
* **Test window, Season Final** (two modules, routed):
  * Module 1 is routed on its answers **as given, with flagged answers counted right**. The
    route is decided at module 1's hand-in, before any confirm.
  * Module 1's confirms run **at the module break**, on their own clock (each confirm's budget ×
    timing factor, as above; the break's own 10 minutes is not used), before module 2 is built.
    The break screen reads "Confirm 2 answers from module 1 · then module 2".
  * A failed confirm only rescores that slot (0, Voided). The route stands.
  * Module 2's confirms run after its hand-in, before the result.
  * The result shows "Route kept: decided before confirms" when any module 1 confirm failed,
    and the band is scored on the rescored answers along the route actually taken.

**Result and board.** "8 right (1 confirmed) · 1 wrong · 1 skipped · 0 voided". A **Clean run**
chip when nothing was flagged. Confirm answers file as normal attempts (study time, mastery),
tagged `cfg.confirm_of`, and they are rated. Flagged answers are not rated. A failed confirm sets
`attempts.void` on the original answer, so R8 leaves it out.

**Clean mark on board rows** (contest boards). A small glyph in the Student cell, after the
level badge, backed by a legend:
* a check-in-a-ring glyph for a clean sitting (nothing flagged); tooltip "Clean: nothing
  flagged";
* the text mark "✓2" for a sitting with confirms that all held; tooltip "2 answers confirmed on
  new numbers";
* no mark when a confirm failed (the Voided count already says it).
* A legend line above the table: "31 clean · 6 with confirms", and a legend chip in the header
  that explains both marks. Anonymous rows carry their mark too; it identifies no one.
* Boards without flags (Rush, Word Sprint runs, ghost sittings) show no mark and no legend.

**Data.** `POST /api/drill/{sid}/void {question_id, why: 'left' | 'blur' | 'copyleave' | 'paste'
| 'pagehide' | 'fast', secs}` now records a flag in `cfg.flags[qid]`. Board entries add `mark:
'clean' | 'confirmed' | null` and `n`; `board()` adds `marks {clean, confirmed}`. The Final's
session payload adds `route_kept`. `GET /api/drill/{sid}` returns `confirm {due, next}` once the last question is
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
5. Playwright: during a ranked daily, open a second window and focus it for 6 s → the confirm
   banner ("out of focus") shows on return. Focusing the calculator for 30 s raises nothing.
6. Playwright: copy text in the stem, then focus a second window for 2 s → the banner ("copied
   and the window left") shows.
7. During a confirm twin, focusing a second window for 1 s forfeits it (`voided == 1`).
8. A Final with 2 flagged right answers in module 1 → both confirms are served at the module
   break before `GET /api/session/{sid}` returns module 2's questions, and `route` equals the
   route for module 1's as-given right count. One failed confirm → `route` unchanged, that slot
   scores 0, and the result has `route_kept: true`.
9. A daily board with 3 clean sittings and 1 with a held confirm → the legend reads "3 clean ·
   1 with confirms", and the entries carry `mark: 'clean'` × 3 and `mark: 'confirmed', n: 1`.

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
* **Consequence line**, always under the row, so nobody is placed without being told:
  * extended: "Extended time: on this board you're placed among extended-time sittings (only
    you see where). Rating, Over par and Climb count you with everyone.";
  * official: "Official time: placed on the public board.";
  * a private contest: "Ranked with everyone in this private contest. Nobody sees your timing."
* **One-time confirm sheet** before the first extended contest on this account (stored as the
  pref `contest_timing_seen`, so it follows the student across devices): "You have 1.5× time set
  for tests. In contests, extended sittings are placed apart on Points, Season and contest
  boards, shown only to you, and counted with everyone on Rating, Over par and Climb." Buttons:
  pill **Use 1.5×** · quiet **Use official time for contests**. The second writes
  `contest_timing: 'official'`, a contest-only override (default: follow `test_timing`), so a
  student can keep 1.5× in Tests and sit contests on the official clock. Change on the lobby
  row edits the override from then on.
* **Clock and points**: the clock, each budget (pace bonus, Rush strikes, confirms) and the
  Sprint, Rush and Word Sprint clocks scale by the factor. Points are otherwise identical.
* **Where extended sittings count**:
  * Rating, Over par, Questions right, Test score and Climb: everyone, since they are time-neutral
    (R16 already keeps extended sittings out of the Test score's standard set);
  * Points, Season, Sprint, Rush and Word Sprint boards, and public contest boards: official
    sittings only. An extended sitting is placed among extended sittings, shown only to its
    owner: the you-bar reads "#3 of 12 with extended time".
  * **Private contests** (C18): extended sittings rank with everyone on the contest's board and
    its series board, in their real place, so an accommodated student never disappears from a
    friends' contest. Private contests carry no season points, so nothing public moves.
  * Streaks, badges (Pace setter's threshold scaled), review, the field's answers, debrief and
    races all count.
* **Nothing public shows it**: no row, chip, copied result, race link or private board carries
  the timing; only the student sees it on their own result.

**Data.** `sessions.cfg.timing` ('official' | 'x1.5' | 'x2'), from `prefs.contest_timing` when
set, else `prefs.test_timing`; public board queries filter on it, private boards don't;
`board(scope='extended')` returns only you, the count, and no names. New prefs (§2.7):
`contest_timing` ('follow' | 'official' | 'x1.5' | 'x2', default 'follow') and
`contest_timing_seen` (bool).

**Acceptance.**
1. With `test_timing: 'x1.5'`, `POST /api/contest/daily/start` → `clock.left == 1425`.
2. That learner's finished daily is absent from the daily board's entries and `players`; its
   board response has `you.extended == {rank, of}`.
3. The same learner appears on `metric=net` and `metric=rating`.
4. Copy result's text of an extended sitting equals the official format, character for
   character, apart from the numbers.
5. A learner with `test_timing: 'x1.5'` sees the consequence line on the daily lobby and, on
   the first extended start, the confirm sheet; "Use official time for contests" makes the
   next `start` return `clock.left == 950` while Tests still start at 1.5×.
6. That learner's finished private contest sitting is in that contest's board `entries` at its
   real rank, and no entry field names the timing.

#### C26. Twins that never collide: whole-question keys and a supply floor

*From: the review of §1.1 "Twin questions" (decision 1). Effort S–M. Builders: S8
(`contest_items`, the supply cache, the slot pool, `s8.py`), F5 (`blueprint.fill` takes the pool).*

**Why.** Decision 1 promises every student the same ten question types in the same order, each
with their own numbers, so answers can't be passed on. v2 de-duplicates on (template, seed) and
admits any template with ≥ 15 distinct questions in 18 seeds. That checks short-range variety
only: `nleq.sum_product` has 201 distinct whole questions in 3,000 seeds, so a Daily the size of
theirs ("1.6k took it") would hand the same question to several entrants, and v2's fix (fall back
to another template) breaks the same-ten-types promise. A finite bank can't make this promise at
all; ours can, if slots draw only from templates deep enough for the field.

* **Whole-question keys.** `contest_items(contest, slot, qhash, learner, template, seed)`, unique
  on (contest, slot, qhash), where `qhash` = sha1 of the normalised stem, choices, figure and
  table (the same hash v2 uses to de-duplicate twins). Dealing a slot tries the learner's next
  seeds of the slot's template until one's `qhash` is unused (at most 50 tries), so a slot
  **never** falls back to another template.
* **Supply survey.** `python3 server/compete.py --survey` generates up to 3,000 seeds per
  (template, tier), stopping once 1,000 distinct `qhash` values are found, and writes
  `server/cache/twin_supply.json` `{bank: <bank version hash>, pairs: {"template|tier":
  distinct}}`. It runs as a deploy step whenever the bank changes. At startup the file is read;
  if it is missing or its bank hash is stale, the survey runs in a background thread and, until
  it finishes, the pool uses v2's 15-in-18 rule plus the 50-try deal. `ponytail:` about 1.2M
  generations per bank change, off the request path; parallelise across topics if the deploy
  step gets slow.
* **Supply floor.** A slot of a twin kind (Daily, Sprint, Weekly, Final, Trap, twin private
  contests, and confirm twins) draws only from (template, tier) pairs with distinct ≥ `need`,
  where `need` = min(1,000, max(100, 2 × F)) and F = the largest ranked field of that kind in the
  last 30 days. With today's 7 learners `need` is 100; it rises with the site and stops at 1,000.
* `blueprint.fill` takes the pool as an argument; the canonical slot list is drawn from it, and
  C12's slot-feasible test uses the same pool.
* `s8.py --supply` prints, per blueprint cell (domain × tier × format), how many templates pass
  at `need` = 1,000, and asserts every Daily, Weekly and Final cell has at least 3.
* Nothing on screen changes. The lobby's rule line keeps "Your own twin questions: same types,
  your own numbers".

**Data.** `contest_items` as above (replaces v2's (contest, template, seed) key); `compete.pool(kind,
tier)`; the cache file.

**Acceptance.**
1. Simulate 500 entrants on today's daily (`s8.py --simulate 500`): no slot has a duplicate
   `qhash`, and every entrant's template list equals the canonical `spec.slots` templates, in
   order.
2. A pair with 201 distinct is excluded from the pool once F ≥ 101, and included while F ≤ 100.
3. With the cache file deleted, startup serves a daily without error, and the file reappears
   with the current bank hash.

---

### E. Friends: private contests by invite

#### C18. Private contests with friends: one invite link, repeats, a series board, a series streak and nudges

*From: outcomes #10, unfair-advantage #11 (in part), decision 5. Effort M. Builders: S8 (the
create sheet, `contests.series`, `compete.series_streak`, nudges, the series board, card G), S1
(the feed merges nudges).*

**Why.** A streak other people depend on gets a student to do the Daily on the days they would
skip, and days practised drive the score. Friends who study together want a board of just them,
week after week. Decision 5 drops classes, so this lives where decision 5 puts it: a private
contest that Compete owns, reached by an invite code or link, with no owner view beyond its
settings. Theirs has no private contests outside a teacher's hidden class pages.

* **One contest or a series.** The create sheet (§3.1 entry 26) gains **Repeat**: Once
  (default) · Every day · Every week, and with a repeat, **Rounds**: 2–30 (Every day defaults
  to 7, Every week to 4).
  * Each round is its own contest, `p-…-r2`, with the same settings and its own slots (twins
    drawn from its own id, C26). Round n opens when round n − 1 closes, at the same local time.
  * One invite code and link join the whole series; joining once enters every later round. The
    link is the contest page itself, `…/compete/contest/?code=K7M2QX`, which opens the lobby
    with a **Join** pill (no separate join page).
  * The join sheet says who sees what: "Entrants see your board name here (Anonymous if your
    name is off on Me)." A student whose board setting is `anon` or `hidden` (R12) shows as
    "Anonymous" to other entrants, in their real place.
* **Series board** on a series' contest page: an underline **This round · Series** above the
  board.
  * Series ranks Σ points over the rounds so far; a round not sat scores 0 and shows "–".
  * A second column **Over par** (Σ Net, C5) with its own sort, so every level can win the
    series (labelled "Fair for every level").
  * Columns: Rank | Student | Rounds sat | Points | Over par | Move (since the last round).
* **Series streak**:
  * with 2–10 entrants: consecutive rounds that every entrant finished;
  * with 11 or more: rounds that ≥ 75% finished;
  * shown as "Series streak 3 · best 5".
* **Overview G › Your private contests** (replaces v2's "Your groups"). Per open contest or
  series you're in:
  * the title, "Round 3 of 7 · closes 11:59 PM" (a one-off: "Closes Fri 4:10 PM");
  * entrant dots (✓ done · half-filled in progress · empty not yet), named on hover;
  * "Series streak 3", your place this round and in the series;
  * **Copy link** and, on each not-yet entrant, a quiet **Nudge**.
  * Empty: "Private contests are for friends: make one and share the link." + quiet "+ Create a
    contest" · quiet "Join with a code".
* **Nudge**: one feed item (U25), "Ada nudged you: round 3 of Friday Five closes 11:59 PM", at
  most one per sender per entrant per round (429 after). Fixed text, no messages. Only between
  entrants of the same private contest; none to someone who has left it.
* **Ownership is settings only.** The creator can rename, extend 24 h, close now, remove an
  entrant and delete (each with a confirm sheet). The creator sees exactly what entrants see: no
  results table, no roster view, no CSV, no due dates (decision 5).
* Private contests carry no rating and no season points (v2), so a series never moves a
  public board.
* Achievement **Full house** (R25, declared in `compete.ACHIEVEMENTS`): a series streak of 5 /
  10 / 30 rounds.

**Data.** `contests.series TEXT` (the first round's id; NULL for a one-off), `contests.round
INTEGER`, `contests.spec.repeat {every: 'day' | 'week', rounds}`; `contest_members(contest =
series id, learner, joined)`; `nudges(sender, target, contest, round, at)`, PK (sender, target,
contest, round). `compete.series_board(series, sort)`, `compete.series_streak(series)`. `POST
/api/compete/nudge {contest, member}`. `GET /api/contest/{cid}?view=series`.

**Acceptance.**
1. `POST /api/contests {repeat: {every: 'day', rounds: 3}, …}` → one code; rounds 1–3 open on
   consecutive local days; a learner who joined in round 1 is an entrant of round 2 with no
   second join.
2. A 3-entrant series where all 3 finished rounds 1 and 2 → `series_streak == 2`. One entrant
   missing round 3 → it holds at 2 until round 3 closes, then 0.
3. A second nudge from one sender to one entrant in one round → 429.
4. The series board with round 2 unsat by one entrant shows "–" for that round and ranks Σ
   points; `sort=net` orders by Σ Net.
5. `GET /api/groups` and `GET /api/classes` → 404; `db.py` has no `groups`, `group_members`,
   `classes` or `class` column (decision 5).

#### C19. Private contests built from traps, and results every entrant can use

*From: the private-contest gaps of all three. Effort S. Builders: S8 (the create sheet source,
the grid footer).*

**Why.** A friend challenge is sharper on the traps that catch you, and a series is sharper on
the traps its entrants share. v2's results were an owner-only table (a teacher view, gone under
decision 5); the same numbers help every entrant decide what to fix.

* **Create a contest › Questions from**, a new underline above Skills: **Skills I pick** (default)
  · **My open mistakes** (your open traps' templates, drawn with `want`: "beat me on the traps
  that catch me") · **Our open mistakes** (series rounds from round 2 on: the 10 norms most
  entrants hold open, each held by ≥ 2, drawn with `want`; nobody is told who holds which). The
  summary line reads "10 questions · from 10 open mistakes held by 4 of 6 of you".
* **Results for everyone** who has finished, in the Grid view (C20), which replaces v2's owner
  results table:
  * its footer names each question's top misconception with its share ("41% fell for: inverted
    the slope") beside % right and median time;
  * **Where we went wrong** above the grid: the top 3 misconceptions, each with how many
    entrants fell for it ("3 of 6") and, when you did, **Fix it · 3** (C1's twin sheet).
* No assignments, repairs for others or CSV: each entrant fixes their own.

**Data.** `contests.spec.source = 'skills' | 'my_traps' | 'our_traps'`; `GET
/api/contest/{cid}/grid` adds `footer [{slot, right_share, median_ms, top: {norm, label,
share}}]` and `where [{norm, label, fell, of, you}]`. v2's `GET /api/contest/{cid}/results` is
removed.

**Acceptance.**
1. A series round from our open mistakes with 3 entrants each holding norm X open → at least one
   slot regenerates with an option whose norm is X.
2. `our_traps` on a one-off contest or a series' round 1 → 400 "Our open mistakes starts from
   round 2."
3. `GET /api/contest/{cid}/results` → 404; `/grid` for a finished entrant has `footer[i].top`
   and `where`, and is 403 before they finish (C20).

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
* It replaces v2's owner results table (a teacher view, dropped by decision 5): in a private
  contest it is the results view for every entrant who has finished, with C19's footer and
  "Where we went wrong".

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
`compete.go_for`), S1 (R25's engine, `achievements.FOLDED`, rarity and `go` in
`/api/me/achievements`).*

**Why.** Progress shown is not progress driven. Theirs are dead tiles; v2's work but wait.

**Who owns what.** R25 folded half of v2's 18 Compete badges into Shell's tiered rules
(first-contest became "the Challenge rule at tier I"), so their ids are Shell's, not Compete's.
So the Go map is keyed through one table and served by one function:
* **S1** exports `achievements.FOLDED`: `{old Compete id: (Shell rule id, tier)}` for every v2
  Compete badge R25 folded (first-contest, streak-7, daily-7, daily-30, perfect-ten, podium,
  solved-1000, consistency, trap-hunter), since S1 did the folding and names the rules.
* **S8** provides `compete.go_for(rule_id, learner) → {href, label} | None`. It accepts a
  Compete id or a Shell rule id, resolving Shell ids through FOLDED's inverse.
* **S1** calls `go_for` for every rule that started as a Compete badge (FOLDED's rules, and
  every rule in `compete.ACHIEVEMENTS`) and puts the result in the row's `go`.

**Go targets** (as U13 does on Me), by origin:
* first-contest, daily-7, daily-30, perfect-ten, top-ten, podium → today's Daily ("Start the
  challenge", or "Tomorrow's Daily opens in 6h" once today's is sat);
* streak-7, consistency, solved-1000 → Up next's first item (these are study rules; Shell's
  own Go may already cover them, and S1 keeps Shell's when both exist);
* pace-setter → today's Daily with the SAT-pace pacer; sprinter → a Sprint run; weekly-4 → the
  Weekly (or "Opens Sat"); dress-rehearsal → the Final's lobby; level-5 and level-8 → Rush;
  all-rounder → Rush in the weakest domain; trap-hunter → Fix all; season-top-10 → Season
  standings;
* the new ladders: over-par → today's Daily; won-back → the oldest due Rematch (C2), else
  today's Daily; rush → a Rush run; trap-week → this week's Trap of the week; full-house → your
  series with the most entrants still to sit, else "+ Create a contest".

**Rarity** "earned by 4%" once ≥ 50 learners were active in 30 days (S1, cached hourly).

**New ladders** (R25, declared in `compete.ACHIEVEMENTS`): Over par (3 / 5 / 10 Dailies in a
row), Won back (10 / 50 / 200 questions, C2), Rush (a run of 10 / 20 / 30 right), Trap-proof week
(resisted all 10 in a Trap of the week, 1 / 4 / 12 times), Full house (a series streak of 5 / 10
/ 30 rounds, C18).

pace-setter's rule reads "every right answer within its budget".

**Acceptance.**
1. For every id in v2's 18-badge list and every rule in `compete.ACHIEVEMENTS`, resolved through
   `FOLDED` where folded: a learner with `have < next` on that rule gets a row whose `go` is
   non-null (`s8.py` walks the list against a seeded learner).
2. `compete.go_for(<Shell's Challenge rule id>, learner)` equals `go_for('first-contest',
   learner)`.
3. Resisting all 10 in a trap contest adds `earned (id 'trap-week', tier 1)`.

#### C24. One tap to question 1, a Compete key map, a thumb bar, and instant scopes

*From: experience #6. Effort S. Builders: S8 (keys, thumb bar, prefetch), S3 (Today's pill), F2
(`UI.keys` registry, §2.8 row).*

**Why.** Theirs is about 8 actions and a wait for the contest to close before you see where you
placed, with no shortcuts. v2 is 2 taps to Q1. Once the rules have been seen, one is enough.

* **One tap.** Today's challenge pill and Overview A's pill start the sitting directly once this
  device has shown that kind's rules (localStorage `satf.rules.<kind>`, in try/catch); otherwise
  they open the lobby. The runner's top bar gets a **Rules** link that opens the §1.2 list in a
  sheet. The rank shows at hand-in.
* **Keys** (a "Compete pages" row in §2.8), **scoped by focus region** so they never clash with
  the Player keys of the contest page's Review (`B` save, `R` report, `Y` history, `J` `K`
  move, all §2.8's Player row):
  * **Page keys** (Shift-chorded, free in every scope on these pages): `Shift+B` jump to the
    board · `Shift+V` jump to Review · `Shift+Y` jump to your row · `,` `.` previous / next day.
    On the Overview, `Enter` starts or resumes the Daily while focus is on the page body.
  * **Player keys** apply while focus is inside a review item (the Player region), exactly as
    §2.8 lists them.
  * **Board keys** apply while focus is inside a board (the board region, `role="grid"`): `J` `K`
    or `↑` `↓` move row focus · `Enter` row menu · `F` follow · `Esc` leaves the board region.
    `F` is the runner's reference key only in the runner, a different page.
  * **Leaderboard** (no Player region): `/` focuses Find a student (the Leaderboard and the
    contest page join §2.8's list of pages where `/` is local) · `M` / `P` cycle metric /
    period · `,` `.` step to the previous / next period (C27; the same keys step days on the
    contest page), outside the text field. `[` stays Global's sidebar key.
  * The `?` sheet lists each region's keys under its own heading, and a region's heading
    appears only when focus is in it or the page has one.
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
4. Browser: on the contest page with a review item focused, `B` saves the question (the Saved
   state shows) and the page does not scroll to the board; `Shift+B` scrolls to the board.
   With a board row focused, `J` moves row focus and does not move the review.

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

#### C27. Champions and past boards: a win that lasts past the reset

*From: the review of rows 6 and 21 (their Elite prize contests, the period control). Effort S–M.
Builders: S8 (`champions`, the period stepper, the Champions card and section, the ring), S1
(Me's titles line), F4 (the `champions` table, §3.2).*

**Why.** Their prize contests give winning a stake, behind their top plan. v2 dropped them with
nothing in their place: once a week, month or season closed, its final standings could not be
viewed at all, and a student who won last week or the Season Final had nothing to show. Ours
stays free and makes every win permanent and public, at every level, because the level bands and
Over par give lower levels podiums they can actually reach.

* **Past periods.** The Leaderboard's Period control gains a stepper, "‹ Week 38 ›", "‹ September
  ›", "‹ Road to Sep 12 ›", "‹ 2026 ›" (none for All or 7d; disabled with its reason for Rating,
  Skill rating and Climb, which have no period). URL: `?period=week&at=2026-W38` (month
  `2026-09`, season `road-2026-09-12`, year `2026`); no `at` means the live period.
  * Weeks, months and years are recomputed from ranked sittings finished inside the window.
    A period is **closed** at its close time (weeks at Monday 12:00 UTC, when the week's last
    Daily closes everywhere; months and years likewise at 12:00 UTC on the 1st), and after that
    nothing changes it.
  * Seasons read their stored `seasons.standings` (frozen at `close_season`), so "Season
    standings ›" can open any past season, not only the live one.
  * A closed period's header reads "Final standings · closed Mon Sep 21". The you-bar keeps
    your place and the gap but drops the cheapest-step line; Move is hidden.
  * `,` `.` step periods on the keyboard (C24).
* **Champions.** When a week or season closes, the first request after it writes its podiums to
  `champions` (lazily, as snapshots are):
  * per closed **week** and **season**: the top 3 on **Points**, **Over par** and **Most improved**
    (Contest rating change over the period, C10's Change sort), and #1 in each level band
    (Levels 1–3, 4–6, 7–10) on Points;
  * per **Season Final**: its podium by points, with each band ("610–750");
  * ties share the place (C16); hidden students (R12) are recorded and shown as "Anonymous".
* **Overview › Champions** card (side, after Traps this week): last week's three podiums in one
  compact table (place × board), each band's #1 below, and after a season closes, "Season
  champions · Road to Sep 12" with the Final's podium. Each name opens that closed board at
  its row. Your own finish is highlighted with "You · Over par #2".
* **Your rankings › Champions**: the hall. Every closed week (8 a page) and season, newest
  first, each row "Week 38 · Points: Maya · Sam · Lee · Over par: …". Filter chips **All ·
  Mine**; Mine lists only the periods where you placed.
* **A mark that lasts** (no money, nothing to buy):
  * a top-3 place on any season board or the Season Final podium earns a 2 px orange **ring**
    on the level badge wherever it shows (boards, Me, Rivals), through the whole next season;
    its tooltip names the title;
  * the title line "Champion · Road to Oct 3 · Over par #1" sits on your board row's meta line
    through the next season, and on Me's Boards block permanently, with every title listed
    ("3 titles ›");
  * a weekly podium goes into Records (C21) as "Week 38 · Over par #2", and the hall;
  * a hidden student's ring and title show only to themselves.
* A **Champions** line joins the season recap (C21): "Your titles this season: Week 36 Over par
  #1 · Week 38 Points #3."

**Data.** Table `champions(kind 'week' | 'season' | 'final', period TEXT, board TEXT, place
INTEGER, learner TEXT, value REAL, band TEXT)`, PK (kind, period, board, place, learner); in
`LEARNER_TABLES` and `progress.carry`. `GET /api/leaderboard?…&at=` (400 for a period not yet
closed or not yet started, except the live one); `GET /api/compete/champions?kind=&mine=&before=`
→ `[{kind, period, boards: {points: [...], net: [...], change: [...], bands: {...}}}]`. Board
and learner payloads add `ring: bool` and `title: {kind, period, board, place} | null`.

**Acceptance.**
1. After a week closes, `GET /api/leaderboard?period=week&at=<last week>` returns the same
   ranks and values before and after new Dailies are sat this week.
2. The first leaderboard request after Monday 12:00 UTC writes 3 `champions` rows per board
   (Points, Over par, Most improved) and 1 per band for the closed week; a second request
   writes none.
3. A learner in a closed season's top 3 has `ring: true` on their board entries throughout the
   next season, and `false` after it.
4. A hidden learner on a podium appears as "Anonymous" in `/api/compete/champions` to others,
   and by name to themselves.
5. `?period=season&at=road-2026-09-12` equals that season's stored `seasons.standings` order.

---

## 3. Spec overrides

### 3.1 Inside §3.7 (spec/rebuild-v2.md lines 8097–9133)

Each entry quotes the current text, then gives the replacement or addition.

1. **§3.7.3, Review changes, item 3.**
   * Quote: "the open question is voided after 5 s away or on copy/cut/paste (theirs voids at
     once, with no grace);"
   * Replace with: "a flagged right answer is confirmed on a strict twin at hand-in, and keeps
     its points if the twin is right (C15). A copy on its own and cut trigger nothing; copying
     the question and then leaving the window flags it, and a paste into the calculator is
     free."

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
    * Replace with: "- `k` "THIS WEEK" + chips Points · Over par · Climb, each with its own
      top 5. Rows: the top 5, a separator, then you ± 2 (merged when adjacent), each with
      movement and gap. Fewer than 5 players: par rows and your best fill the empty places. Footer
      "Full board ›" (C10, C6)."

12. **§3 Overview, new side cards.**
    * Quote: "**F. Next badges** (tile)"
    * Add before it: "**Rivals** (C9)", "**Traps this week** (C12)" and "**Champions**
      (C27)".
    * Quote: "- The three unearned badges you're closest to: icon, name, rule line, a progress bar
      and "5/7"."
    * Append: " Each has **Go** (C23)."
    * Quote: "**G. Your groups** (tile)" and its four lines.
    * Replace with: "**G. Your private contests** (tile)", C18's card: per open contest or series,
      the round and close time, entrant dots, the series streak, your place, Copy link and
      Nudge; the empty line and "+ Create a contest" · "Join with a code". No groups (decision 5).
    * Quote: "- One column in this order: A, D, H, B, E, C, F, G."
    * Replace with: "- One column in this order: recap, A, D, Rivals, H, B, E, Traps, Champions,
      C, F, G."

13. **§4 Contest page, Upcoming.**
    * Quote: "- Quiet "Add to calendar". Pill "Practice for it": a 10-question drill over the
      contest's domains."
    * Replace with: "- Quiet "Add to calendar". The par line and **Warm up · 6** (C7)."

14. **§4, Live, not started.**
    * Quote: "- Rules, ladder, field line: "128 in · 6 sitting now · median 260 pts · best 410"."
    * Append: " The par line and forecast (C5, C7), ladder cells with each slot's skill and
      your chance (C7), the **Race** select (C8), and "Your time: Official · Change" with its
      consequence line (C17)."

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
    * Append: " Then **Your last week** (when your exam date is this season's SAT date) or
      **Final focus** (otherwise), and the **Test-day card** (C4). With module 1 confirms, the
      route line adds "Route kept: decided before confirms" when one failed (C15)."
    * Quote: "- Sprint: "Best this week 240 pts (run 3 of 3)" and a pill "Run again"."
    * Append: " and "Race your best · 240" (C8)."

16. **§4, Board section.**
    * Quote: "- Scope underline: Everyone · Near me · Country · {each of your groups}."
    * Replace with: "- Scope underline: Everyone · Near me · Following · My level · Country.
      A private series adds **This round · Series** (C18). Header controls: **List · Grid**
      (C20), **Points · Over par** (C5), **Pars** (C6), Find a student (C9), and the legend chip
      and line for the Clean / Confirmed marks (C15)."
    * Quote: "  - Daily and Private: Rank | Student | Score | Points | Answer time."
    * Append to each table line: " | Net | Move | Gap" (Trap adds Resisted before Points; Rush:
      Rank | Student | Right | Top item (L-code or "Top") | Runs | Move; Word Sprint: Rank |
      Student | Score | Right | Wrong | Runs | Move)."
    * Quote: "  - Unranked sittings never appear. Your own unranked result shows as a line above the
      table: "Your sitting is unranked: {reason}.""
    * Append: " On public boards, extended-time sittings are placed only for their owner;
      private contest boards rank them with everyone (C17)."
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

18. **§4, Owner controls.**
    * Quote: "- **Results table** (the teacher view):" and its three sub-bullets.
    * Delete (decision 5: no teacher views). Every finished entrant gets the Grid view instead
      (C20), with C19's footer (% right, median time, top misconception) and "Where we went
      wrong" with **Fix it · 3** on your own misses.
    * Quote: "###### Owner controls (private and group contests)"
    * Replace with: "###### Owner controls (private contests): settings only. The creator sees
      what entrants see (C18)."

19. **§5 Leaderboard, controls.**
    * Quote: "  - *Metric* underline: Points · Rating · Questions right · Test score."
    * Replace with: "  - *Metric* underline: Points · Over par · Contest rating · Skill rating ·
      Questions right · Test score · Climb (C5, C10, C11). Contest rating gets "Sort: Rating ·
      Change"."
    * Add helpers: Over par: "Base points minus your par, over ranked contests. Beat what a student
      at your rating is expected to score." Climb: "Gain since your first scored section, among
      students who started near you (U11)." Skill rating: "From every first try in practice,
      tests and contests. Contest rating counts ranked contests only."
    * Quote: "  - *Scope* `<select>`: Everyone · Near me · Country ({yours}, or "Country: set on
      Me", which links to Me) · each of your groups."
    * Replace with: "  - *Scope* `<select>`: Everyone · Near me · Following · My level · Country
      (…) · Same exam date (R3) (C9). No group or class scopes (decision 5)."
    * Quote: "  - *Domain* `<select>` (Points and Questions right only; disabled with a tooltip
      otherwise)"
    * Replace with: "  - *Domain* `<select>` (Points, Questions right and Skill rating;
      disabled with a tooltip otherwise, Contest rating's tooltip naming Skill rating; C11)"
    * Add: "  - *Subject* `<select>`: Math (default) · Reading & Writing (C14)."
    * Quote: "  - The controls live in the URL (`?metric=points&period=week&scope=all&domain=`)"
    * Append: " plus `&subject=math` and, for a closed period, `&at=` (C27)."
    * Add: "  - *Period* gains the ‹ › stepper to any closed week, month, season or year, with
      "Final standings · closed …" (C27)."

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
    * Quote: "   - A table with a row for Everyone, Country and each group, and columns Week /
      Month / Season / All time."
    * Replace "and each group" with ", Following, My level, Same exam date and each private
      series you're in (its Series rank)", and add a column **Last week** with that closed
      week's final place (C27). Each cell carries movement and gap (C10).
    * Quote: "     - Last row: "Contests played 14"."
    * Add before it: a row **Climb** (C10).
    * Quote: "   - **Pace** (theirs: Time Analysis). Underline toggle: By difficulty · By domain ·
      Right vs wrong · Under pressure."
    * Replace the Pace block with C3's "Your rankings › Pace".

23. **§6, 3. How you placed in a contest.**
    * Quote: "3. **How you placed in a contest** (theirs: Contest Leaderboard)" and its two
      sub-bullets.
    * Delete. Contest history rows expand instead (C22).
    * Add new sections in the §6 order: Rating card (C11), Records (C21), Trap Index (C12),
      Rivals (C9), Champions (C27), Level ladder (C11).

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
    * Add C23's ladders (over-par, won-back, rush, trap-week, full-house).

26. **§7 Create a private contest.**
    * Quote: "- **Skills**: the shared topic picker from the practice builder (4 domains × 19
      skills, select-all per domain). The default is all."
    * Add before it: "- **Questions from**: Skills I pick (default) · My open mistakes · Our
      open mistakes (series rounds from round 2) (C19)."
    * Quote: "- **For**: "Anyone with the code" (default) · {each group you own}. A group contest
      lists every member as an entrant from the start."
    * Replace with: "- **Repeat**: Once (default) · Every day · Every week, and with a repeat
      **Rounds** 2–30. One code and link join every round (C18)."
    * Quote: " For a group, this becomes **Due**: a `datetime-local`, from 1 hour to 30 days
      ahead."
    * Delete (decision 5: no due times).
    * Quote: "- **Strict**, switch, off by default: "Leaving the tab or copying voids the open
      question.""
    * Replace the helper with: "Leaving the tab or window, or copying the question and leaving,
      means a quick confirm on new numbers at the end (C15)."
    * Quote: "##### 7. Create a private contest (a sheet from Overview; also "Challenge a friend"
      and a group's "Set a contest")"
    * Replace with: "##### 7. Create a private contest (a sheet from Overview; also "Challenge a
      friend")"

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
    * Append: " Rush uses it with the header "Right 14 · strikes ✕✕○ · now L6" or "Top of the
      bank" (C13)."
    * Quote: "  https://…/compete/contest/?id=daily-2026-09-23"
    * Replace with: "  Beat 170: https://…/compete/contest/?id=daily-2026-09-23&race=<pid>" (C8).
    * Quote: "- Voids use the same rules as above, for the question on screen, via
      `/api/session/{sid}/void`."
    * Append: " The Weekly's Confirm step runs after hand-in, before the result; the Final
      confirms module 1 at the module break, after routing on answers as given (C15). The Final
      forces the pace guide off (C3)."

28. **§9 Today, Me, Results, Report.**
    * Quote: "- "#4 of 37 · top 11%" + "Next one in 07:14:22" once done;"
    * Add after it: "- before starting, the par line (C5); once done, the follow-up chip (C2);
      the pill starts in one tap (C24);"
    * Quote: "- **Rank snapshot:** "Week #12 of 340 · Country #14 of 96 · All time #210 · Level 3
      (1,084)", linking to Your rankings."
    * Append: " It reads `compete.ranks` with movement and gap (C10); the season recap line
      shows after a season closes (C21)."
    * Quote: "- **Groups:** a list with name, code + Copy, member count and "Leave". An owner
      instead gets "Delete group" and a member list with "Remove"."
    * Replace with: "- **Private contests:** each open contest or series you're in, with its
      code + Copy link, entrants, the series streak and "Leave"; the creator gets "Delete"
      (C18)." Add: "- **Titles:** "Champion · Road to Oct 3 · Over par #1" and "3 titles ›"
      (C27)."
    * Quote: "Helper: "Off: you're listed as Anonymous. Groups you join still see your name.""
    * Replace with: "Helper: "Off: you're listed as Anonymous, including in private contests.""
    * Quote: "- Ranked sittings add a percentile: "Higher than 71% of timed full sections in the
      last 90 days (212 sections)", shown once there are ≥ 20."
    * Replace with: "- Ranked sittings add R16's percentile and Compete's line "#41 of 212 on this
      month's Test score board · Climb +90, ahead of 74%" (C10)."

29. **§10 Build order.** Replace the list with:
    1. Model and fixes, as written, plus: rating and level (moved from step 8, since par, rivals
       and levels read it), the budget pace bonus (C3), flags and confirms (C15), ties by points
       (C16), timing (C17), `contests.subject`, whole-question twin keys and the supply floor
       (C26).
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
    9. Seasons + Final (module-break confirms, C15) + Season period + H card + Seasons table +
       last week or Final focus and the test-day card (C4) + recaps (C21) + past periods and
       Champions (C27).
    10. Me Boards + country scope + report name + Rivals (C9).
    11. Private contests and series (C18) + Challenge a friend + Copy result + calendar +
        reminder + ghost sittings + trap sources and the grid footer (C19) + make-up and
        reminders (C25). No groups or classes (decision 5).
    12. Trap of the week and the Trap Index (C12); Rush (C13).
    13. Word Sprint and the Subject filter (C14), once S9's quiz items are merged.
    14. README serving-layer rows and spec/rebuild.md §9 updated.

30. **§3.7.4 Extras.**
    * Quote: "- **Skip with the key shown, and voids with a grace period**:"
    * Replace the entry with: "- **Skip with the key shown, and verify instead of void**: a skip
      still teaches, a blip is confirmed on a strict twin instead of zeroed, and leaving never
      zeroes a sitting (C15)."
    * Append entries for C1–C27 in their own words (one line each), in the list's style.

31. **§3.7.5 Server changes, db.py.**
    * Quote: "  - contests(id TEXT PK, kind TEXT daily|sprint|weekly|final|private, title TEXT, …"
    * Replace the kind list with `daily|sprint|weekly|final|private|trap|rush|words` and add
      `subject TEXT DEFAULT 'math'`, `series TEXT`, `round INTEGER`; drop `grp` (decision 5).
    * Quote: "  - groups(id TEXT PK, code TEXT UNIQUE, name TEXT, owner TEXT, created TEXT)." and
      "  - group_members(grp, learner, joined, PK)."
    * Delete both (decision 5).
    * `contest_items` is keyed (contest, slot, qhash) (C26).
    * Add tables `follows`, `rank_snapshots`, `nudges`, `champions` (C9, C10, C18, C27; F4 adds
      them, §3.2).

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
      `move`, `gap`, `mark` and the scopes `following`, `level`, `extended`, and `view=series`
      for a private series (C6, C9, C10, C15, C17, C18)."
    * Quote: "board(cid, me, scope='all'|'near'|'country'|'group-{gid}', …"
    * Replace `'group-{gid}'` with `'following'|'level'|'extended'` (decision 5).
    * Quote: "  - public=0 rows keep their rank with name 'Anonymous' and anon:true, except in group
      scopes and your own row."
    * Replace "except in group scopes and your own row" with "except your own row"

34. **§3.7.5, compete.py: leaderboard().**
    * Quote: "  leaderboard(metric='points'|'rating'|'right'|'test', period=…"
    * Replace with: "metric='points'|'net'|'rating'|'skill'|'right'|'test'|'climb'", plus
      `subject`, `sort` ('value' | 'change', Rating), `find`, `at` (a closed period, C27), and
      the scopes of C9 and C17. Domain applies to `skill` through `skill_ratings`, never to
      `rating` (C11).

35. **§3.7.5, compete.py: rating.**
    * Quote: "  - Ri −= 4(S−E), with Ri starting at 900 easy / 1100 medium / 1300 hard;"
    * Replace with: "  - the item side is P11's `ratings.update` (one rule for every mode);"
    * Add: "Flagged answers are not rated; confirm answers are (C15)."

36. **§3.7.5, app.py: contest endpoints.** Add: `GET /api/contest/{cid}/debrief` (C1), `POST
    …/rematch` (C2), `POST …/warmup` (C7), `GET …/grid` (C20), `?race=` on `GET /api/contest/{cid}`
    (C8), `POST /api/drill/{sid}/confirm` and `POST /api/session/{sid}/confirm` (C15),
    `POST/DELETE /api/follows`, `GET /api/compete/rivals` (C9), `GET /api/compete/traps-index`
    (C12), `GET /api/compete/recap` (C21), `POST /api/compete/nudge` (C18), `GET
    /api/compete/champions` (C27), `?view=series` on `GET /api/contest/{cid}` (C18).
    * Quote: "GET /api/contest/{cid}/results" (the owner results) and "GET/POST /api/groups, GET
      /api/groups/{gid}, DELETE /api/groups/{gid}, DELETE /api/groups/{gid}/members/{pid|me}."
    * Delete all of them (decision 5). `POST /api/join {code}` stays for contest codes only.
    * Quote: "  - POST /api/contests (create private): validates count ∈ {5,10,15,22}, topics ⊂
      catalogue, minutes 5–70, open_for ∈ {1,24,72,168} h or due within 1 h–30 d for an owned
      group, twin, reveal, strict."
    * Replace "or due within 1 h–30 d for an owned group" with ", repeat {every, rounds ∈ 2–30},
      source (C18, C19)", and "unique across contests and groups" with "unique across contests".
    * Quote, in `GET /api/compete`'s hub payload: "board_preview, next_badges, groups, sat_dates"
    * Replace "groups" with "private (C18's card rows), champions (C27's card)".

37. **§3.7.7 Shared needs.** Append:
    * "`UI.pacer(host, pacer)` (the race rail) and `UI.debrief(host, data)`: built in S8
      compete-ui.js, loaded by the practice session defensively (§2.4)."
    * "The runners' Confirm step (S4, S5) through `compete.confirm_next(row)` (R28); S5 also
      calls it at the Final's module break, after routing and before module 2 is built (C15)."
    * "The runners' flag triggers (S4, S5): visibility, window focus, copy-then-leave, paste
      outside the calculator host, pagehide (C15)."
    * "`compete.go_for(rule_id, learner)` (S8) for S1's achievements rows; `achievements.FOLDED`
      (S1) for S8 (C23)."
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
    * Quote: "18. POST /api/contests {count:10, topics:[…], open_for:24, twin:true} → .code
      matches ^[A-HJ-NP-Z2-9]{6}$ and is not a group code. POST /api/join {code} from another
      learner → {kind:'contest'}. After both sit it the board has 2 players, and GET
      /api/contest/{cid}/results is 200 for the owner and 403 for the other learner."
    * Replace with: "18. POST /api/contests {count:10, topics:[…], open_for:24, twin:true} → .code
      matches ^[A-HJ-NP-Z2-9]{6}$. POST /api/join {code} from another learner → {kind:'contest'}.
      After both sit it the board has 2 players, `GET /api/contest/{cid}/grid` is 200 for both,
      and `GET /api/contest/{cid}/results` is 404 (C19)."
    * Add C1–C27's acceptance lists as items 34 onward.

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
    * Quote: "- Country is opt-in and blank by default, with a suggestion from the browser language.
      Is a country field acceptable for minors, or should the country board go and groups stay?"
    * Replace "or should the country board go and groups stay?" with "or should the country board
      go? (Groups are gone under decision 5; Following and private contests are the friends'
      boards.)"

40. **Decision 5 sweep: groups, classes and teacher views leave §3.7.** R4 is void, so v2's groups
    go with it. Friends compete through private contests and series (C18, C19). Each quote below
    is deleted or replaced as stated.
    * Review list, item 10: quote "Groups and Near me stay." → "Near me stays; Following (C9)
      and private series (C18) are the friends' boards."
    * Review list, item 16: quote "16. **Classes and homework** (hidden in theirs, with a teacher
      dashboard) had no equivalent. …" and its sentences → "16. **Classes and homework** are
      out of Compete (decision 5: a separate platform has them). Friends get private contests
      by invite code or link, which can repeat as a series (C18)."
    * Review list: quote "    - contest and group codes now share one namespace;" → delete.
    * Kind mapping table: quote "| Classes & homework (hidden) | Groups, with group contests
      that have a due time and an owner results table |" → "| Classes & homework (hidden) |
      Out of scope (decision 5); private contests and series by invite (C18) |".
    * §1.1 window, Private: quote "; a group contest runs until its due time" → "; a series
      opens each round as the last closes (C18)". Ranked sitting: "each member's first sitting
      in the window" → "each entrant's first sitting in the round".
    * §3 B, Title: quote ""Period 3 quiz · Ms. Lee's group"" → ""Friday Five · round 3 of 7"".
      Window line: quote "· group "Due Fri 5:00 PM · in 2d"" → "· series "Round 3 of 7 ·
      closes 11:59 PM"".
    * §3 Sheets: quote "No contest or group has that code." → "No contest has that code.";
      quote "A group code shows "You're in {group}." and the group appears in G." → delete;
      quote "- **Create a group**: a name field (3–40 chars) and "Create". …" → delete.
    * §4 header `k`: quote ""PRIVATE CONTEST · by Ms. Lee"" → ""PRIVATE CONTEST · by Sam"" (a
      series adds " · ROUND 3 OF 7").
    * §4 Layout: quote "  - The owner results table spans both columns under Board." and "  -
      The owner results table scrolls inside its own box, with the Student column sticky." →
      delete both.
    * §9 Today: quote "Group contests with a due time show as a row under it: "Period 3 quiz ·
      due Fri 5:00 PM · Start"." → "Private contests you've joined and not yet sat this round
      show as a row under it: "Friday Five · round 3 · closes 11:59 PM · Start" (C18)."
    * §3.7.4 Extras: quote "- **Private contests, 'Challenge a friend', and group contests with
      a due time**: …" → "- **Private contests, 'Challenge a friend', and series by invite**:
      anyone can set a contest over chosen skills, length and window, repeat it as a series with
      its own board, streak and nudges, and every entrant who finishes sees the grid with each
      question's top trap (C18–C20)." Quote "- **Groups and Near me alongside the country
      board**: …" → "- **Following, My level and Near me alongside the country board**: the
      people a student actually races, with no code or owner (C9)."
    * §3.7.5 carry: quote "carry also moves group_members, contest_members and badges" →
      "carry also moves contest_members, follows, nudges, champions and badges".
    * §3.7.5 hub and Me: quote "(name rules, public, country, ranks, badges strip, groups)" →
      "(name rules, public, country, ranks, badges strip, private contests, titles)".
    * §3.7.7 Shared needs, `UI.board`: quote "the rankings picker and group boards" → "and
      private series boards"; quote "  ↳ R4: groups are classes (S2)" → delete.
    * §3.7.8 check list: quote "private create, join and board; group due time and owner
      results;" → "private create, join, board and series (C18);".

41. **§1.1 Twin questions** (C26).
    * Quote: "- A (template, seed) that another entrant of the same contest already got is
      skipped (`contest_items`)."
    * Replace with: "- A whole question another entrant of the same contest already got is
      skipped: `contest_items` is unique on (contest, slot, qhash), the sha1 of stem, choices,
      figure and table (C26)."
    * Quote: "- A slot only takes templates that showed **≥ 15 distinct questions in 18 surveyed
      seeds**. Today only similar.area fails this."
    * Replace with: "- A slot only takes (template, tier) pairs whose 3,000-seed survey found at
      least `need` = min(1,000, max(100, 2 × the largest recent field)) distinct whole questions
      (C26)."
    * Quote: "If a student's history has used a template up, the slot falls back to a template of
      the same topic, tier and format, same skill first. Field statistics for a slot are grouped
      by misconception, so a fallback still counts."
    * Replace with: "A slot never falls back to another template: dealing tries the learner's
      next seeds of the slot's template until its whole question is unused (C26), so every
      entrant gets the canonical ten types in order."

### 3.2 Outside the section (Part 2 and sibling files; I1 applies them with the owners)

| where | change | upgrade |
|---|---|---|
| R3 | Shell's practice-rank scopes lose "each class" (decision 5): everyone / same exam date / following | C9 |
| R4 | **Void** (decision 5). Compete has no groups and no classes; `groups`, `group_members`, `contests.grp` and the group endpoints are not built. Private contests and series are Compete's own (C18) | C18, C19 |
| R8 | Unchanged in meaning. A flagged answer is filed with `void` NULL; a failed confirm sets `void` on it afterwards, so boards and mastery leave it out | C15 |
| R12 | Unchanged. Raceable and followable rows are `name` and `anon`; `hidden` rows have no row menu | C8, C9 |
| R25 | New Compete ladders: over-par, won-back, rush, trap-week, full-house; rarity and `go` in `/api/me/achievements` (S1). S1 exports `achievements.FOLDED` (old Compete id → Shell rule id, tier) and fills `go` from `compete.go_for` for every rule that started as a Compete badge | C18, C23 |
| R28 | Hooks add `compete.pacer(row, answered)`, `compete.confirm_next(row)` (in the test window also at the Final's module break, before module 2 is built), `compete.field_line(…)`, `compete.pool(kind, tier)` and the Rush pick; `state_extra` carries the rail, the field line and the flag banner | C6, C8, C13, C15, C26 |
| R34 | The average stays 95 s a question; the pace bonus and confirms use each question's P16 budget | C3 |
| §2.5 | Tables: `follows(learner, target, at, auto INTEGER DEFAULT 0, week TEXT)` PK (learner, target); `rank_snapshots(day, board, learner, rank, value)` PK (day, board, learner); `nudges(sender, target, contest, round, at)` PK (sender, target, contest, round); `champions(kind, period, board, place, learner, value, band)` PK (kind, period, board, place, learner). Columns: `contests.subject TEXT DEFAULT 'math'`, `contests.series TEXT`, `contests.round INTEGER`. `contest_items` unique on (contest, slot, qhash). No `groups`, `group_members`, `contests.grp` or class tables (decision 5). `LEARNER_TABLES` and `progress.carry` include `follows`, `nudges` and `champions` | C9, C10, C14, C18, C26, C27 |
| §2.6 | Field `target` (a rating, set by S8 server code only, for Rush). `rematch` with `scope: 'misses'` draws each named miss with `want {template: norm}`. Sources `rematch`, `warmup`, `confirm`, `rush` | C2, C7, C13, C15 |
| §2.7 | New keys `race_rail` (bool, default true; the session's More menu), `contest_timing` ('follow' \| 'official' \| 'x1.5' \| 'x2', default 'follow') and `contest_timing_seen` (bool) | C8, C17 |
| §2.8 | New row "Compete pages", scoped by focus region. Page: `Shift+B` board · `Shift+V` review · `Shift+Y` your row · `,` `.` previous / next day (contest page) or period (Leaderboard) · `Enter` start the Daily (Overview body). Inside a review item: the Player row, unchanged. Inside a board (`role="grid"`): `J` `K` `↑` `↓` rows · `Enter` row menu · `F` follow · `Esc` leave. Leaderboard: `M` `P` metric / period. `/` focuses Find a student on the Leaderboard and contest page (added to the pages where `/` is local). The `?` sheet lists the regions | C24, C27 |
| §2.9 | Providers: F5 `budget_ms` → S8; F4 `ratings.update`, `skill_ratings`, per-template priors → S8; F4 `progress.causes(session=)`, `progress.pace(only=)` → S8; F3 `UI.twinSheet` → S8; S8 `compete.final_focus` → F2; S8 `compete.feed_items(learner, since)` (race, rival, nudge, season items) → S1's feed; S8 `compete.ranks`, `compete.test_rank`, `compete.week_line`, `compete.go_for` and titles → S1, S6; S1 `achievements.FOLDED` → S8; S9 `words.sprint_items`, `words.record_contest_miss` → S8. The S2 row (classes, assignments, members) is removed, and S8 has no class scope (decision 5) | all |
| `practice.md` P18 | "A challenge parent returns 409" → 409 only while the contest sitting is unfinished. Scope `misses` uses `want` per named miss | C2 |
| `practice.md` P16 | `q.budget_ms` is frozen on each served question, so the contest pace bonus doesn't move mid-day | C3 |
| `practice.md` P11 | `item_ratings` priors are per (template, tier), not per tier: the measured share once n ≥ 20 (shrunk by n / (n + 20)), else C13's structural prior from `fmt`, figure / table and rationale length, ± 150 of the tier value; `ratings.py` `__main__` asserts ≥ 8 distinct priors per tier | C13 |
| `words.md` Rejected, "A Words module tile on Tests, a daily words challenge in Compete, a daily sprint board" | Narrowed: Tests and the daily Compete kinds stay Math, but Compete runs **one weekly Word Sprint board** (C14). Its run is W16's (one key, tray, never promotes, a miss sets Missed lately without dropping the box, score = right − wrong ÷ 3) with a 4:00 clock and W1 / W2 items instead of meaning items. R&W answers stay in `word_reviews`, out of `attempts` and the Math rating | C14 |
| `words.md` W16 and §3.1 server entries | S9 defines and owns `words.sprint_items(learner, seed, n, level)` (W1 Words in Context and W2 Transitions items from `rw_items.py`, alternating, level from W10 placement rising every 5 answers) and `words.record_contest_miss(learner, word, trap)` (W16's miss rule, the trap kept for the Traps line); sprint runs return `traps [{trap, label, n}]` | C14 |
| `today.md` T15 | Copy "ranked by right answers, then time" → "ranked by points: 10 / 20 / 30 by difficulty, +5 within each question's time budget; equal points share a rank" | C3, C16 |
| `today.md` T2, T13 | Due today and Up next list a contest sitting's `rematch_due`; T13's taper lists `compete.final_focus` traps first | C2, C4 |
| `shell-me.md` U11 | Movement reads `rank_snapshots` (daily; the 7-days-ago row), not a weekly snapshot | C10 |
| `shell-me.md` U14 | The Monday sheet shows `compete.week_line` | C21 |
| `shell-me.md` U18 | Feed titles include the Daily and due rematches; push kind `daily` ("Daily Challenge still open", off by default, 2 h before local midnight) | C25 |
| `shell-me.md` U25 | Feed kinds add `race`, `rival`, `nudge` (private-contest entrants only), `season` (from `compete.feed_items`) | C8, C9, C18, C21 |
| `shell-me.md` Me Boards | Me shows the titles line from C27 and the private contests list from C18; no groups or classes | C18, C27 |

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
* **Everything built on classes** (experience #4, unfair-advantage #8 and #11: live class mode
  on a projector, class battles, class boards, class streaks, repairs assigned to members):
  decision 5 removes classes, teacher views and homework, since a separate platform has them.
  The friends' side is kept and upgraded as private contests and series (C18, C19).
* **Paper contests with per-student sheets** (unfair-advantage #12): `shell-me.md` and
  `practice.md` rejected per-student printed packs; Review's worksheet prints.
* **Squads or friend groups as a separate type** (unfair-advantage #11): a repeating private
  contest is the friends' board, with its own series standings and streak (C18), and Following
  (C9) needs no code at all. A third container would say the same thing.
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
