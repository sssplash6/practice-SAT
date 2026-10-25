# Compete area: Math vs R&W inventory (read-only map, 2026-10-22)

Scope: server/compete.py, server/api_compete.py, server/ratings.py (as compete uses it), web/compete/*, web/assets/compete-ui.js.
Paths below are relative to /Users/workingmyassof/freshbot/satbank. "cp" = server/compete.py, "ac" = server/api_compete.py,
"cui" = web/assets/compete-ui.js, "ov" = web/compete/overview.js, "ct" = web/compete/contest/contest.js,
"lb" = web/compete/leaderboard/leaderboard.js, "rk" = web/compete/rankings/rankings.js.

## 0. Headline findings

1. No scheduled contest serves R&W bank items (`rw_*`). Every scheduled kind except Word Sprint is inserted with
   subject "math" (cp:179-185 default; daily cp:403-405, sprint cp:412-414, rush cp:415-418, weekly/final cp:437-440,
   trap cp:455-459). Private contests are hard-coded "math" (cp:2319).
2. The only R&W contest is the Word Sprint (cp:419-424, subject "rw", rated False, 240 s). It draws from the legacy
   vocabulary deck (server/words.py frames/pairs, templates `rw.wic.*` / `rw.tr.*`), not the 3,433-item bank. It is
   dormant: `sprint_available()` (words.py:1104-1107) needs reviewed Transitions pairs at every tier, and
   server/words/pairs.json has 0 of 153 reviewed, so `ensure()` never inserts `words-<week>` unless
   SATF_WORDS_UNREVIEWED=1. Local DB confirms: contests table has daily/final/rush/sprint/trap/weekly, all "math", no words.
   (Prod env not checked.)
3. The template catalogue is subject-blind. `blueprint.kinds()`, `abilities()`, `by_domain()` iterate
   `satbank.registry.templates()`, which includes the rw_ topics (load_topics returns 8 domains: the 4 Math plus
   Craft and Structure, Expression of Ideas, Information and Ideas, Standard English Conventions). Compete restricts
   by Math domain lists in most places, but not all (see Rush and Private below: API-reachable R&W leaks, stored as "math").
4. The twin model cannot serve R&W by construction. `pool()` (cp:166-172) needs >= `supply_need()` distinct items per
   (template, tier) with a floor of 100 (cp:157-163). server/cache/twin_supply.json (current bank hash e31bf179a1f0e8d1)
   holds 311 rw pairs: max 68, median 8, 45 pairs >= 20, 0 pairs >= 100. Per skill and tier the bank has 22 to 253
   items (e.g. rw_cross_text_connections easy 22, rw_words_in_context easy 253). So daily/sprint/weekly/final/trap
   would 409 "twin supply is too small" for R&W. A different fairness model is needed (section 4).
5. Live-contest item protection is keyed (template, seed) (server/deps.py:223-247, contest_items template/seed).
   R&W templates map seeds to fixed items by `seed % n` (satbank/topics/rw.py:50-53), so the same R&W item under
   another seed is NOT protected while a contest is live. Any R&W contest must protect by item id (source_id) or qhash.
6. One contest rating for everything: `learners.rating` (cp:936-966, rated via progress.py:547-551 on every ranked
   contest answer). No subject dimension. Champions table has no subject column; `close_champions()` (cp:1824-1878)
   always computes Math (`_champion_values` default subject "math", cp:1772).
7. Leaderboard already accepts `?subject=math|rw` (ac:305-312, cp:1909) and the client already reads/writes it
   (lb:13, lb:74, lb:162, lb:258), with the switch deliberately hidden (lb:117 "Subject waits until a second subject
   has a board (decision 3)"). But 4 of 7 metrics ignore subject on the server (section 2).
8. Score bands shown in compete are 200 wide (Weekly Module) and 140 wide (Season Final), both labelled "Math" in
   scoring.py; climb windows produce 80/160/320-wide "Started lo-hi" ranges. None meet the 20-point target (section 3).

## 1. Feature-by-feature

Verdict key: works = works for R&W today; partial; math-only.

### 1.1 Daily Challenge (`daily-YYYY-MM-DD`)
- Verdict: math-only.
- Server: built cp:388-405 via `_daily_slots` cp:194-205: domains from `challenge.MIX` (server/challenge.py:20-21, the 4
  Math domains 3/3/2/2), tiers `challenge.LADDER` (3 easy, 4 medium, 3 hard), grid-ins at `challenge.SPR_AT` (4, 8)
  (challenge.py:23). 10 questions, 950 s (cp:405, 10 x 95). Twin per entrant: `twin_questions` cp:473-510 (a new
  rendered item per slot per entrant, unique qhash per slot). Started by ac:218-296 as a drill "challenge" session.
- Page: ov:42-131 (Daily card), ct (lobby/result), ladder cui:291-309 (labels "grid-in" cui:296, topic names via
  `topicName` cui:646 which only knows `UI.TOPIC` Math slugs, falls back to "rw central ideas..." for rw_).
- Math-specific: MIX, LADDER, SPR_AT, 950 s (95 s/q), twin numbers, "different numbers for everyone" copy
  (cui:266, ct:943), pace rule text "easy 1:05 · medium 1:35 · hard 2:06" (ct:936).
- Parity: an R&W Daily: 10 items, domain mix by CB weights (Craft and Structure 28%, Information and Ideas 26%,
  Standard English Conventions 26%, Expression of Ideas 20%, so about 3/3/2/2), no grid-ins, R&W pace 49/71/94 s
  (drill.py:103-104, so about 710 s for 10). Fairness: same form for everyone or a sibling item of the same skill and
  tier (not template, supply too thin). Overview UI: two Daily cards side by side (Math Daily, R&W Daily), each with
  its own streak or one shared streak (decide); contest page is per-contest so it just needs subject-aware copy.

### 1.2 Legacy identical Daily (`/api/challenge`, `/api/challenge/start`, `/api/challenge/board`)
- Verdict: math-only. ac:28-74; seconds = `CHALLENGE_SIZE * SECONDS_PER_QUESTION` (ac:35, deps.py:19 = 95, a Math
  constant). Questions from `challenge.challenge(day)` (challenge.py:36-55, Math domains). `/challenge` redirects to
  the contest page (ac:847-850). Kept for old links; parity optional.

### 1.3 Sprint (`sprint-<week>`, kind sprint)
- Verdict: math-only.
- Server: cp:208-227 `_sprint_slots`: theme domain rotates over `tuple(challenge.MIX)` by ISO week (cp:210, cp:414),
  60 slots, easy x4 then medium/hard alternating, prefers mcq else spr (cp:219-225). 300 s (cp:413). Runs repeat;
  best run per week counts (leaderboard cp:1936-1941, champions cp:1800-1804). No pace bonus, no finish bonus
  (cp:1012, cp:1018).
- Page: title "Sprint · <domain short> week" via `UI.DOMAINS` (cui:200-203, Math only); ct:307 "Every run draws
  fresh questions"; "Run again" ct:397-403.
- Parity: R&W sprint rotating over the 4 R&W domains. 60 fresh items per run per entrant x repeat runs exhausts
  R&W quickly (a domain has roughly 600 to 1,000 items in total); repeat runs would repeat items. Needs an exposure
  rule (no item twice per learner, retire after N contest uses).

### 1.4 Rush (`rush-<week>`, three strikes, adaptive)
- Verdict: math by label and UI; partial/leaky through the API.
- Server: `rush_start` cp:513-552: `domain` validated against `blueprint.by_domain()` (cp:519-521), which includes
  the 4 R&W domains, so `POST /api/contest/rush-<week>/start?domain=Information and Ideas` (ac:781-789) is accepted
  and runs an R&W Rush. Starting skill: "Rush is Math" filter for domain=all (cp:526-527), per-topic
  `ratings.skill` for a chosen domain (cp:528-530). Session inserted with subject 'math' always (cp:549-551).
  `rush_next` cp:562-621: candidate pairs come from `blueprint.abilities()` with no subject guard (cp:576-578);
  for domain=all the sort only puts the rotation's Math domain first (cp:592-599, rotation over `challenge.MIX`), so
  when that domain has no fresh pair in the climbing direction the nearest pair "in another domain" can be an
  R&W item (comment cp:592-594). Item ratings `ratings.item` (ratings.py:66-68; unseen rw pairs fall back to
  TIER_PRIOR 900/1100/1300, ratings.py:46). Budget `drill.budget_ms` IS subject-aware (drill.py:1273-1277). Answers
  go through `progress.record` so they rate `learners.rating` (progress.py:547-551, cp:936-966).
  Board `rush_board` cp:673-695 (right, then top item rating).
- Page: domain select uses `UI.DOMAINS` only (ct:257-260), so the UI never offers R&W. Columns ct:593
  ("Top item" prints `L${top_item}` where top_item is a raw item rating like 1240: existing bug).
- Parity: subject on the Rush contest (or a separate `rush-rw-<week>`), domain list per subject, session subject from
  the domain, per-subject rating, and a guard in `rush_next` so a Math run never falls into rw_ pairs.

### 1.5 Word Sprint (`words-<week>`, kind words)
- Verdict: partial (the only R&W contest), but dormant (see 0.2).
- What it is: not flashcards, not the bank. `words.sprint_items` (words.py:1110-1160) generates 80 SAT-form
  four-choice items alternating Words in Context "complete the text" frames (`rw.wic.<frame>`) and Transitions pairs
  (`rw.tr.<pair>`) from the vocabulary deck, difficulty band rising every 5 answers from a placement level
  (cp:710-717). Template order is shared via a contest seed; passages vary per learner (cp:718-721).
- Server: cp:698-850 (start/next/answer/finish/board), subject 'rw' (cp:742-745), 240 s scaled by timing pref
  (cp:727-732), score right - wrong/3 (cp:820), traps per item. Grades go to `words.grade` (word_reviews, SRS) and
  `record_contest_miss` (cp:796-805), never to `attempts`, `skill_ratings`, `item_ratings` or `learners.rating`
  (words.RW_TO_ATTEMPTS at words.py:34 is used only by server/checks/s9.py). Unrated (cp:424).
  API routes: ac:790-792, 800-801, 811-815, 828-829, review ac:532-541, debrief ac:686-693, board ac:520-521.
- Page: runner `/words/run/?id=` (cui:215; web/words/run/index.html exists). Result ct:361-364; rules ct:933;
  columns ct:594; overview TRAINS ov:135.
- Gaps even if enabled: `_meta` count = 0 (no slots), so "x of 0 answered" (ct:212) and the share text reads
  "12/0 · – pts" (cui:277-287 uses r.asked/c.count/r.points, absent for words); champions skip it for points
  (cp:1797) while the leaderboard counts it (cp:1936) (inconsistent).
- Parity decision: keep as a vocab mini-game (then review the pairs so it opens) or replace with a bank-based R&W
  sprint. It does not use `rw_*`.

### 1.6 Weekly Module (`weekly-<week>`, Saturday to Monday)
- Verdict: math-only.
- Server: `_module_slots("module1", 1, cid)` cp:361-369 -> `blueprint.slots` (DOMAIN_SPLIT Math 8/7/4/3,
  blueprint.py:24-29; TIERS 7/8/7; SPR_AT 6,7,13,14,21,22 blueprint.py:47; MODULE_SIZE 22). 2100 s (cp:440).
  Started as a test-runner "module" session with subject = contest subject (ac:258-268). Result estimate comes from
  `scoring.score` (api_tests.py:1336) -> 200-wide band, `"section": "Math"` (scoring.py:376-386).
- Page: ct:263 copy, ct:306 "Module estimate low-high", clockText "35 min" cui:257.
- Parity: R&W module = 27 questions, 32 min (1920 s), no grid-ins, R&W domain split, items ordered by domain
  group with difficulty rising inside each group (CB R&W order). Needs an R&W blueprint (slots, split, size,
  seconds) and an R&W estimate; twin supply blocker applies.

### 1.7 Season Final (`final-<SAT date>`)
- Verdict: math-only (a full Math section only).
- Server: module 1 plus `slots_m2` lower/upper (cp:432-440), 4200 s; module 2 served by api_tests.py:1068-1076
  via `compete.twin_questions`. Estimate `scoring.section_score` (api_tests.py:1372) -> MOCK_HALF_BAND 70, 140 wide,
  lower route capped at 580 (scoring.py:82, 87, 95-109), `"section": "Math"` (scoring.py:108). `final_focus`
  cp:1337-1373 (budgets 65/95/126 s at cp:1355-1356; band at cp:1370). Test-day card ac:342-355 (pace strings
  "2:10 / 3:10 / 4:12" = 2x Math budgets at ac:353; band at ac:355).
- Page: ov:334 "full Math section"; ct:243 "Module 2 · 22 questions"; ct:300-305 "Section estimate";
  ct:496-511 test-day card (ct:504 pace, ct:507 band); board "Band" column ct:597 is dead (server board entries
  have no band, cp:1614-1619).
- Parity (owner wants full mocks with both sections): a Final of R&W M1 + routed M2 (27 + 27, 64 min) and Math
  M1 + routed M2 (22 + 22, 70 min), section estimates for each (200-800) plus a total (400-1600), ranked on
  points with both sections; test-day card with R&W pace (49/71/94 s, 2x = 1:38/2:22/3:08).

### 1.8 Trap of the week (`trap-<week>`)
- Verdict: math-only.
- Server: `trap_families` cp:249-293 uses `habits.families()` which returns Math families only
  (server/habits.py:81-83 "future R&W families can be added by subject"); slots cp:340-358; 950 s (cp:458).
  `pool("trap", tier)` iterates all templates; with a current supply cache rw pairs never qualify, but if the cache
  is missing or stale (first 30 s after start, or after any satbank/*.py change until the survey finishes) the
  fallback `variety >= 15` (cp:171-172) admits rw templates whose why_wrong text might regex-match a Math habit.
- Page: ct:245-254 tell line, result ct:344-352 (drill this habit).
- Parity: R&W habit families (e.g. "too broad", "half right", "out of scope", "comma splice") in habits.py with
  subject "rw", then an R&W trap week.

### 1.9 Private contest and series (`p-<hex>`, rounds `-rN`)
- Verdict: math by UI; partial/leaky through the API.
- Server: `create_private` cp:2238-2323. Question types from: `paper` (Math papers, cp:2272-2274),
  `from_session` (any sitting of yours, cp:2275-2282: an R&W practice sitting yields rw_ templates), `my_traps`
  filtered to Math (cp:2283-2284), or `topics`/`templates` mapped through `blueprint.kinds()` with no subject check
  (cp:2285-2287). Format both/mcq/spr (cp:2293-2295). Default clock `count * 95` s (cp:2319). Subject inserted
  "math" (cp:2319). Unrated (cp:2313). Series board cp:2346-2367, streak cp:2370-2386, nudge cp:2389-2399;
  join ac:206-209; owner edits ac:456-507.
- Page: create sheet cui:802-968: skills picker built from `UI.DOMAINS`/`UI.TOPICS` (Math only, cui:803, cui:836-846),
  "Format: Both / Multiple choice / Grid-in" (cui:852-854), "Auto (95 s a question)" (cui:858, cui:915),
  Papers = Math papers (cui:893-912). "Challenge a friend" pre-fills from the Daily's topics (ct:409).
- Parity: a Subject choice in the sheet (Math / R&W), R&W skill list (UI.RW_SKILL exists, ui.js:681-687 and
  ui.js:3248), hide Format for R&W, auto clock 71 s/q, store the real subject, `my_traps` by chosen subject.

### 1.10 Contest machinery shared by kinds
- twin_questions cp:473-510: per-slot unique item per entrant; R&W supply too small (0.4).
- par / expected score cp:875-907: worth 10/20/30 (cp:892), budgets 65/95/126 s (cp:893), learner rating
  `learners.rating`; feeds `_meta` (ac:96-115) and forecast (ac:121-127). Math constants.
- finish_contest cp:976-1078: points 10/20/30 + 5 pace (budget fallback Math cp:1009-1010; uses `q.budget_ms`
  when the drill runner set it, which is subject-aware drill.py:1896) + 10 finish; ranked/ghost/repeat/fast.
  Subject-neutral apart from the fallback.
- debrief cp:1103-1189 (budget fallback cp:1136-1137); returns `subject` (cp:1184). UI cui:666-752.
- rematch ac:697-731 / cp:1192-1232: "same types, new numbers" twins (cui:747 copy). R&W: sibling passages.
- warmup ac:734-758: other templates of the 3 lowest-chance topics; subject-neutral by topic.
- flag / confirm cp:1376-1438: confirm serves a twin "on new numbers" (ct:940 copy); R&W needs a sibling item.
- race / pacer cp:1450-1542: par levels at rating 700 + 150*(level-1) (cp:1466); pace marks 65/95/126 s (cp:1534).
- review ac:525-561 renders through `UI.workspace` (ct:~866), which already renders R&W passages (question.js:399-434).
- grid / compare / field traps ac:564-675: subject-neutral (attempts-based); words has no attempts so grid would be
  blank, but the grid toggle is hidden for runs (ct:695).
- clock cp:853-872: subject-neutral.

### 1.11 Boards and rankings
| Board | Server | Subject today | Page |
|---|---|---|---|
| Contest board | `board` cp:1587-1690 | per contest (follows the contest) | ct:569-760 |
| Series board | `series_board` cp:2346-2367 | per contest | ct:591, ct:697 |
| Rush board | cp:673-695 | per contest | ct:593 |
| Word board | cp:829-850 (`"subject": "rw"`) | rw | ct:594 |
| Leaderboard `points` | cp:1928-1944 | filters `contest_subject` (cp:1926); words counted best-per-week | lb |
| `net` | same | filters subject; excludes sprint/rush/words | lb |
| `climb` | `_climb_cohort` cp:2060-2078 | ignores subject (module/mock/diagnostic sittings of any subject) | lb |
| `test` | cp:1945-1949 | ignores subject (non-contest mocks pass the filter at cp:1926); best timed mock band midpoint | lb:20 says "full Math section" |
| `skill` | cp:1950-1958 | silently Math: `progress.topics()` defaults to math (progress.py:188-189) | lb |
| `right` | cp:1959-1968 | respects subject via `subject_of`; domain filter uses Math topics only | lb |
| `rating` | cp:1969-1990 | value ignores subject (one `learners.rating`); sort=change filters subject | lb |
- `?subject=rw` today: points = Word Sprint only (none exist), right = R&W practice answers, skill/test/rating =
  Math numbers under an R&W label. Domain picker is `UI.DOMAINS` (lb:129). Server ignores `domain` for `points`
  though the UI offers it (lb:118, cp:1951-1966): existing bug.
- Callers that never pass subject (all Math): `rank_snapshot` cp:2164-2173 (used by /api/compete ac:164,
  /api/compete/me ac:325, shell_part cp:2212-2218, api_profile.py:479), `ranks` cp:2176-2182, `test_rank`
  cp:2185-2191 (unused), board_preview ac:175, `/api/compete/me` boards ac:328-329, ov:354/360, rk:239.
- Snapshot key includes subject (cp:2020): moves per subject already separate.
- Parity UI: a subject switch (segmented Math / R&W, plus Total where meaningful) on the leaderboard and rankings,
  wired to the existing `?subject=`; server: per-subject skill (`progress.topics(subject)`), test (filter session
  subject; add Total = sum of section midpoints from full mocks), climb (per subject or total), rating (per subject).

### 1.12 Contest rating and levels
- `learners.rating` single number, Elo K 32 then 12 (cp:953-959), item rating `ratings.item(template, tier)`.
  No subject. Rivals use it (cp:2444-2464, +-200), `_identity` level (cp:1564), champion level bands (cp:1848),
  scope=level boards (cp:1635-1637, cp:2005).
- Two ladders: server `ratings.level_of` 7 levels, EDGES (850, 1000, 1075, 1150, 1225, 1350) (ratings.py:47,62);
  client `LADDER` 10 levels, 150 wide from 800 to 2000 (cui:338-340), used by ct:324, ov:112/257, rk:345-352,
  lb:249. Board par rows assume the client ladder (midpoints 1025/1325/1625/1925 for levels 3/5/7/9, cp:1679;
  race par cp:1466) while `_identity` sends server levels 1-7, so "level 9 par" never matches anyone's level and
  champion band "7-10" holds only server level 7. Pre-existing inconsistency, worth fixing with per-subject ratings.
- Parity: per-subject contest rating (column or table keyed subject), R&W item ratings (better keyed by item
  source_id than template/tier since one rw template covers a handful of fixed items), level from one ladder.

### 1.13 Champions, podiums, titles, seasons
- `close_champions` cp:1824-1878: weekly and season podiums for points/net/change plus level bands, Final podium.
  Always Math (no subject passed to `_champion_values` cp:1845, 1861, 1869). `champions` table has no subject;
  rows keyed (kind, period, board, place). `champion_title` ring cp:1759-1769. `seasons` standings cp:1870-1871.
- Pages: rk:327-342 (reads `c.boards.bands`, server key is `band`: band winners line never shows, existing bug),
  ring on every board row (cui:472, cui:630).
- Parity: subject column (or board names like `rw:points`), close both subjects, title says which subject.

### 1.14 Records, history, week line, recap, badges, streak
- records cp:1081-1100: bests per contest kind (Math kinds + words), fastest perfect Daily, peak rating, streak.
  Subject-blind except through kinds. rk:248-255.
- history ac:363-392: all kinds; rk:355-435 (kind filter list rk:356 includes Words).
- week_line cp:1294-1307: counts daily/weekly only.
- season_recap cp:1310-1334: subject-blind, uses single rating.
- evaluate (badges) cp:2096-2121: pace-setter = answers <= 95,000 ms (cp:2103, Math medium budget); sprinter =
  Math sprint; weekly-4, dress-rehearsal Math kinds. Badge art includes Math domain glyphs only (cui:1020-1023).
- challenge_streak cp:2124-2161: any `daily-%` contest; a second subject's Daily would need a rule (both, either).
- traps_index cp:1255-1291: habits catalogue Math only; reads all attempts with no subject filter.
- Parity: per-subject bests; pace badge by subject budget; streak rule for two Dailies.

### 1.15 Social: rivals, h2h, follow, report name, nudge
- cp:2389-2464, ac:395-453. Subject-neutral except rivals use the single rating (+-200). Race links (ct:408) work
  per contest. Parity: rivals per subject rating.

### 1.16 Share card / copy result / test-day card
- `copyResult` cui:277-287: "SAT Freshman · <kind> · <day>", "right/asked · points pts · time · #rank", glyph strip,
  link. Subject-neutral text, but no subject in the title (two Dailies would need "Daily R&W"). Breaks for words
  and rush (no asked/points). Used by ov:117 and ct:405-411.
- Test-day card ac:342-355 / ct:496-511: Math pace and Math Final band only.

### 1.17 Shell / overview pieces
- shell_part cp:2212-2218 and /api/compete ac:158-180: one Daily id (`daily-<day>`), Math ranks.
- Overview QOTD ov:232-245 is not compete: daily.py:31-34 already rotates math:mcq, math:spr, rw:wic,
  rw:transition (R&W slots from the words deck too).
- rk:166 `value: 'rw'` is "Right vs wrong" (pace view), not Reading and Writing; do not confuse in a refactor.

## 2. What is Math-specific (consolidated)

- Domain/topic lists: `challenge.MIX` (challenge.py:20-21) for daily (cp:197), sprint theme (cp:209-210, cp:414),
  rush rotation (cp:596); `blueprint.DOMAIN_SPLIT`/`TIERS`/`SPR_AT`/`MODULE_SIZE` for weekly/final (cp:364);
  `UI.DOMAINS`/`UI.TOPICS`/`UI.TOPIC` (ui.js:652-679) in cui:200-203, cui:646, cui:803-846, ct:258, lb:129-132,
  rk:151, rk:169.
- Subject literals: cp:180 default "math", cp:527 "Rush is Math", cp:550 'math', cp:1772 default "math",
  cp:1903 default "math", cp:2284 `subject="math"`, cp:2319 "math"; ac:307 default "math".
- Pacing 95 s/q and 65/95/126 tier budgets: deps.py:19 via ac:35; cp:893, cp:1009-1010, cp:1136-1137,
  cp:1355-1356, cp:1534, cp:2103, cp:2319; ac:353; ct:936 copy; cui:858, cui:915; tier points with pace in
  `step` cui:380. Subject-aware alternative already exists: `drill.TIER_BUDGET` (drill.py:103-104) and
  `drill.budget_ms` (drill.py:1273-1277), used by Rush (cp:615) and the drill runner (drill.py:1896).
- Grid-in handling: SPR slots in daily (cp:198), sprint fmt fallback (cp:220-225), trap (cp:354-355), private
  format (cp:2293-2295), ladder label (cui:296), create sheet (cui:852-854). R&W has none.
- Twins "different numbers": cp:181 `twin: True`, copy cui:266, ct:170, ct:943, cui:880, rematch cui:747,
  confirm ct:940. R&W items are fixed; the analogue is a different passage of the same skill and tier.
- Ratings keyed only by Math: `learners.rating` single; skill board via Math `progress.topics()`; Rush start skill
  filter cp:526-527.
- Item generation: every twin path walks seeds (`blueprint.draw_matching` blueprint.py:211-228). For R&W, seeds
  cycle a few fixed items (rw.py:50-53), so repeat exposure, contest leakage and the (template, seed) protection key
  (deps.py:223-247) all need an item-id model.
- Score labels: `"section": "Math"` (scoring.py:108, 386); "Test score" help "full Math section" (lb:20);
  ov:334 "full Math section".

## 3. Every score / band / range / rating range in compete

SAT score scale:
| Where computed | Width | Shown |
|---|---|---|
| Weekly Module estimate: `scoring.score` HALF_BAND 100 (scoring.py:61, 376-378), set at api_tests.py:1336 | 200 (section 200-800, "Math") | ct:306 "Module estimate low-high" |
| Season Final estimate: `scoring.section_score` MOCK_HALF_BAND 70 (scoring.py:87, 95-109), api_tests.py:1372; lower route caps high at 580 (scoring.py:82, 104-107) | 140 (narrower only when capped) | ct:300-305 "Section estimate"; ct:507 test-day card; ac:355; `final_focus` cp:1370 |
| Contest board "Band" column | n/a (no data sent) | ct:597 (dead) |
| Leaderboard `test`: best timed mock band midpoint (cp:1945-1948) | single number from a 140-wide band | lb:20 "Band middle" |
| `_midpoint` cp:2053-2057 for climb | midpoint of 140/200-wide bands | climb gain |
| Climb cohort windows +-40/80/160 (cp:2072), `climb()` lo/hi = start +-window (cp:2090-2092) | 80, 160 or 320 | me.js:703-709 "Started lo-hi" (outside compete pages); lb climb board; rk:233 "Climb +x" |
| `test_rank` cp:2185-2191 | uses `test` board | unused |
All are wider than 20. Narrowing is a scoring.py constant change (HALF_BAND, MOCK_HALF_BAND, the cap's
`low = min(low, high - 10)`), not compete code; compete only displays. Note: a 20-wide band from one 22-question
module claims more precision than the data has (scoring.py comments say so); the owner's call.
No total 400-1600 anywhere in compete today.

Contest points scale (not SAT): par expected points (base rounded to 5, cp:905; points cp:906; sd cp:906),
forecast rank range "likely #lo-#hi" from base +- sd (ac:121-127, cui:313-314), board par rows (cp:1677-1688),
field median/best (ac:144-148).

Rating scale (Elo, not SAT): client levels 150 wide (cui:338-340; tooltip cui:369; ladder table rk:345-352);
server levels 75 to 150 wide (ratings.py:47); champion level bands 1-3/4-6/7-10 (cp:1848, cp:1864); race par
ratings 700 + 150 steps (cp:1466); board par midpoints (cp:1679); rivals +-200 (cp:2450); Rush target 700 or
rating - 300, +60/-120 (cp:533, cp:638); `levelIn` hard prior 1300 (cui:343); skill seed from section score
1100 + 1.2 x (score - 530) clamped 700-1500 (ratings.py:79), which seeds R&W topic skills from the Math score.

## 4. R&W parity: what it needs

1. Subject on every contest row, real and used: pass subject to `_insert`, store it on private contests, sessions
   from `contest["subject"]` (Rush cp:550 included).
2. R&W blueprints: daily (10, CB weights, no SPR), sprint (domain rotation over the 4 R&W domains), weekly module
   (27 q, 1920 s), final (both sections, 4 modules), rush domain list per subject.
3. Fairness model for fixed items: either one identical form per contest (legacy style; protect by item id until
   close, then retire from future contests) or per-entrant siblings keyed by (skill, tier), not (template, tier).
   `pool()`/`supply_need()` thresholds need an R&W variant; `contest_items` must record source_id; deps._protected
   must match by item id.
4. Pacing: replace every hard-coded 65/95/126 and 95 with `drill.TIER_BUDGET[subject]`.
5. Ratings: per-subject contest rating and levels; skill board per subject; one level ladder.
6. Leaderboards: expose the existing `?subject=` as a switch (Math / R&W, plus Total for test score and season);
   fix skill/test/rating/climb to honour subject; per-subject champions (subject column).
7. Overview: two Daily cards side by side (each subject's Daily is the daily habit), contests list with a subject
   chip; stats tile shows both ratings. Contest page: subject-aware copy and rules (no grid-in, "different passage").
8. Trap of the week: R&W habit families.
9. Private: subject choice, R&W skill picker (UI.RW_SKILL), no format row, 71 s auto clock.
10. Word Sprint: review the transitions pairs to open it, or replace it with a bank sprint; fix its share text,
    "of 0" count and the champions/leaderboard inconsistency either way.
11. Guards now: `rush_next` subject guard (cp:576-578), `rush_start` domain validation by subject (cp:519-521),
    `create_private` subject filter (cp:2285-2287), trap pool fallback (cp:171-172).

## 5. Existing bugs found on the way (not subject-specific)
- ct:597 Final "Band" column never has data (board entries carry no band).
- rk:337-341 reads `c.boards.bands`; server groups by board name `band` (cp:1893-1894): band winners never shown.
- rk:143-151 "Skill ratings, all practice" never renders: /api/compete/me (ac:322-329) sends no `skills`.
- Leaderboard `domain` ignored for `points` on the server (cp:1951-1966) though the UI offers it (lb:118).
- ct:593 Rush "Top item" shows "L1240" (a raw item rating) as if it were a level.
- Two level ladders (1.12).
- Champions skip words for points (cp:1797) but the points leaderboard counts them (cp:1936).
- Share text for words/rush prints "x/0 · – pts" (cui:284).
