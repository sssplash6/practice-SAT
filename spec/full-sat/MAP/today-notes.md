# Today, Up next, daily question, challenge, /s: R&W parity notes (Fork B)

Read-only audit, 2026-10-22. Paths relative to /Users/workingmyassof/freshbot/satbank.

## 0. Shared mechanics that decide most verdicts

- `drill.resolve` defaults `subject` to math: server/drill.py:896. Topics of the other subject are a 422 (:908), templates of the other subject a 422 (:914). After pooling, every queue and item is filtered to the set's subject: :1083-1084 (`deps.subject_of(t) == subject`), so a mistake/saved/history/check-in pool started without `subject:"rw"` silently drops R&W rows and then 409s `filters_removed_all` (:1095) when nothing Math is left.
- Fallback picks with no topics are Math-only even when the body says rw: `source in {"coach","today","next"}` calls `progress.coach(learner, ...)` with no subject (:1116-1119), `source == "quick"` likewise (:1109-1112), then `_empty("no_bank")` (:1121-1123) for rw.
- `progress.coach/board/topics/warmup_candidates/open_traps(subject=None)` default to math or all: progress.py:807, :259, :188, :1119, :246. `progress.due_rechecks` has NO subject filter at all: progress.py:1098-1109.
- Legacy `drill.create(learner, sid, topics, ...)` (used by the challenge and /s) writes no `subject` into cfg and none into `sessions.subject`: drill.py:2043-2065. Everything downstream then reads `cfg.get("subject","math")`.
- Nothing on the web side injects a subject: Today's `drill()`/`go()` post the body as given (web/index.html:646-655); `UI.start` likewise (web/assets/ui.js:1289-1295); `twinRun/twinSheet/twinInline` post `o.body` (web/assets/question.js:1975-2090).
- Rendering: `UI.workspace` (question.js) renders `q.text` as a passage, plus figure and table (question.js:429-460, 570-575). `UI.question` (ui.js:2940-2964), the older renderer, renders figure, table and stem only, NO passage. Used by /s inline help (web/s/index.html:308), quick.js fallback (quick.js:212) and quick.js `example()` (quick.js:116).
- Topic names on the client: `UI.TOPICS/UI.DOMAINS/UI.TOPIC` are the 19 Math skills only (ui.js:652-679); R&W has only `UI.RW_SKILL` names (ui.js:681-687), no glyph, no domain list. Today's `TOP(slug)` falls back to the raw slug with underscores replaced: web/index.html:512, so an R&W topic would print as "rw words in context".

## 1. GET /api/today (server/api_today.py today_payload :1121-1177)

No `subject` param; every block is Math or all-subject:
- coach: `progress.coach(learner, count=...)` math (:1131).
- open mistakes: `progress.open_traps(learner, subject="math")` explicitly (:1132); feeds `traps()` card, `mistakes` count, `workload`.
- gains: `estimate.gains(learner)` math (:1134); and `estimate.gains` returns None for any non-math subject (server/estimate.py:493), so R&W has no points model at all.
- domains: `progress.board(learner)` math + `progress.DOMAINS` = Math BLUEPRINT only (api_today.py:204-219, progress.py:55-57).
- warmup: `progress.warmup_candidates(learner, tz)` math (:334).
- review counts: `_call("review","counts", learner, tz, "math")` hard-coded (:512).
- week/plan "moved": `progress.board(learner)` math (:324, :453); `strongest()` math (:593-595).
- brief(): check-ins due count uses `due_rechecks` (all subjects, :877) and links to `#mist`, which lists Math only; "moved" fact uses `progress.topics()` math (:911).
- receipt(): moved list built from ALL attempts' topics (:965-972), so R&W topics appear and the page prints them via TOP() as raw slugs (web/index.html:1087).
- time_split(): domains Math only via `progress.topics()`/`progress.DOMAINS`, but `kinds` minutes count every attempt incl. R&W (:1336-1353), so the two figures disagree for a mixed student.
- workload(): open traps Math (`len(open_list)`), checks all subjects (:1020-1021); target sizing via `estimate.need` (Math).
- readiness() and the final-stretch trap groups use `44 * shares` (Math section of 44): :245-269, :1100-1118.
- stretch_coach(): "of 44 a test", Math shares (:643-660).
- at_risk(): body is either `{"pool":"checks","ids":[due[0]["trap_id"]],"source":"try"}` (due from all subjects) or coach topics (math); no subject (:945-946). If the first due check-in is R&W the drill 409s (drill.py:1083 then :1095).

## 2. Today cards (web/index.html)

| Card / feature | R&W today | Evidence | What is Math-specific |
|---|---|---|---|
| Up next lead + "Study" session builder | math-only | sessBody `{source:'next', box/count}` no subject (index.html:1034-1037); server next.resolve_drill math (next.py:340-403) | Coach topics, open traps, weak/warm skill all Math. "More options" link `/practice/?topics=...` (index.html:1255-1259) has no `subject` and the builder ignores `topics` (it reads `skills`, builder.js:1452-1456) |
| "See an example first" (new skill) | math-only | drill({source:'learn', topics:[coach topic]}) index.html:1251 | coach topic Math |
| Q1 inline preview | dead for everyone | paintQ1 reads `p.first`, `p.blocks` (index.html:1339-1376) but drill.preview never returns them (drill.py:1156-1184) | n/a |
| Due today: Review row | math-only | due_fallback row 4 start `{source:'due', box}` no subject (api_today.py:783-801); drill resolve due branch `warmup_candidates(subject=subject)` = math (drill.py:1071-1079) | R&W check-ins/fading never get a row or a Start |
| Due today: Sweep | math-only in effect | `{pool:'checks', sweep:true}` no subject (api_today.py:803-814) | R&W fixed traps dropped by the subject filter |
| Due today: Words | works (Words module, vocab) | api_today.py:815-830, words.today_summary | It is Words' vocabulary, not the R&W bank |
| Due today: Day's questions | partial | api_today.py:831-840 | see section 4 |
| Due today: Challenge | math-only | start `/api/challenge/start` (api_today.py:844-846); page starts `/contest/daily/start` (index.html:656-659) | see section 5 |
| Plan rows | R&W shown as no-Start | plan R&W tasks are custom "On your own · Bluebook or official SAT practice", `start=None` (server/plan.py:692-699); Math tasks carry /api/drill bodies with no subject (plan.py:566-578) | R&W time is never served from the bank |
| Mistakes card | math-only | `traps()` from open_traps math (api_today.py:1132, :245); Fix all `drill({mistakes:true})` (index.html:1646); row fix `drill({mistakes:true, templates:[t]})` (:1654); Twin `twinSheet({pool:'redo', ids, source:'try'})` (:1666); "Learn it again" (:1665) | All bodies without subject. Twin sheet copy "Same kind of question, new numbers" (question.js:2048) |
| Mistakes by habit + Trap gauntlet | dead | `habits.of_learner` does not exist, `_call` returns None (api_today.py:258); gauntlet has no server handling (only in SOURCES, drill.py:86) | habits are Math-only by design: habits.families(subject) returns [] for rw (server/habits.py:81-83) |
| Points on the table (gain) | math-only | insights loaded as `/today/insights` with no subject (index.html:740) though the server takes `?subject=` (api_today.py:1361-1381); `estimate.gains` is None for rw (estimate.py:493) | copy "how far your Math band would move" (index.html:1979); "Practise · 10" grid-ins `formats:['spr']` (:2043) |
| Pace | math-only | same insights call; `_pace_extras` only for math (api_today.py:1369); module limit 2100 s (35 min) (index.html:2072); "Speed drill · 8 in 12:40" `timing:'pace'` (:2100) | Math module clock; "Timed set · 10" `{count:10, timing:'pace', source:'gain'}` (:2079) has no topics and `gain` is not a coach-fallback source (drill.py:1116), so it likely 409s `no_templates` for everyone |
| Causes ("why you miss") | math-only | `progress.causes(subject)` via insights (api_today.py:1368); grid-in entry drill `formats:['spr']` (index.html:2255) | entry/clock causes are Math concepts |
| Score / SAT / target | math-only by design | "We only test Math" (index.html:2305); Math target 200-800 (:2271); R&W only as a typed number `rw_now` (:2143, :2284) | estimate model Math |
| Study time / time split | partial | time_split Math domains only (api_today.py:1333-1353), stack bar by Math domain (index.html:2640); "Rebalance · 10 in {domain}" (index.html:2646) Math | minutes of R&W practice count in kinds but not domains |
| Calendar day detail | partial | `/api/calendar` missed ids are all subjects (api_today.py ~1406-1418); "Redo this day's misses" `{pool:'history', ids, exact:false}` no subject (index.html:2727) | R&W misses silently dropped (drill.py:1084) |
| Tests card | math-only | `/history?kind=tests` Math sittings (index.html:2849-2930) | Math tests |
| Words tile | works | index.html:2822-2840 | Words module |
| Unlocks strip ("Unlocks as you practise") | partial | SOON list + counts from insights (index.html:869-903); `ins.answers` counts ALL subjects (api_today.py:1371) while gains are Math only | an R&W-only student sees "30 of 30" but Points never unlocks; Pace counts Math timed answers |

Subject switch on Today: none. The only subject split on the page is the Day's questions tab strip, Math first then R&W (index.html:1708-1709). Insights could switch (server already takes `?subject=`), nothing else could without server work.

## 3. Up next (server/next.py, GET /api/next in api_shell.py:310-320, Today's `next.items`)

`/api/next` takes no subject (api_shell.py:310-320). `queue()` (next.py:96-337) is Math throughout; its keys even end in `:math` ("rest:eve:math" :111, "start:new:math" :132, "diagnostic:new:math" :137, "review:due:math" :213, "checks:checks:math" :226, "probe:new:math" :269), so the design expected per-subject keys.

| Item kind | R&W today | Evidence |
|---|---|---|
| rest (eve) + warm-up | math-only | body `{source:'warmup'}` no subject (next.py:110-116) -> due, math |
| start / diagnostic (new student) | math-only | `{source:'start'}` (next.py:132-136) -> drill.py:1113-1115 all topics of `subject` (math); copy "One from each part of SAT Math"; diagnostic is Math |
| resume test / resume drill | works (resumes any sitting) | next.py:118-130, 152-162 |
| contest (private) | n/a here | next.py:164-176 |
| plan tasks | Math bodies; R&W plan tasks have start None | next.py:178-209 + plan.py:692-699 |
| review (due) | math-only | `due()` -> `review.due(learner, tz)` with default subject math (next.py:49-53, review.py:547); body `{source:'due', box}` (next.py:211-218) |
| checks (when review.due missing) | breaks on R&W | fallback `progress.due_rechecks` is all-subject (next.py:54-66), body `{pool:'checks', ids}` no subject (next.py:219-231) -> R&W ids filtered out, 409 |
| redo (Fix: label) | math-only | `progress.open_traps(learner, subject="math")` (next.py:145); body `{pool:'redo', ids:[id], count:3}` (next.py:233-245) |
| habit | math-only | habits.family_of is Math regexes (habits.py:86-92); body `{source:'habit', habit}` (next.py:247-265). `_wrong()` counts R&W misses too (next.py:75-82), so R&W misses inflate "N of your last 20 misses" |
| probe (Sharpen · 12) | math-only | `board` math, body `{source:'probe', count:12}` (next.py:267-271) |
| skill (Most points / next useful skill) | math-only | gains math, fallback `progress.coach(learner, k=1)` math (next.py:273-280) |
| saved (try a fresh one, day 6-8 and 20-22) | breaks on R&W | saved rows of any subject (next.py:282-291), body `{pool:'saved', ids:[[t,seed]], exact:false}` no subject -> R&W item dropped by drill.py:1084, 409 `filters_removed_all` |
| warm (keep warm) | math-only | `board` math (next.py:293-301) |
| untried (new kinds of X) | math-only | `deps.subject_of(t) == "math"` explicit (next.py:307) |
| qotd | partial | checks only the Math MC session `qotd:{day}` (next.py:318-321) |
| next.resolve_drill (Up next time box) | math-only | review.due math, open_traps math (:370), `progress.board(learner)` weakest Math skill (:383), Math warm skill (next.py:340-403); returned body has no subject so drill.resolve runs as math |

## 4. Daily question (server/daily.py, api_today.py:1476-1655, index.html:1685-1958)

Four slots: math:mcq, math:spr from the generated Math bank; rw:wic and rw:transition from Words (daily.py:30-35, 102-104, 138-143). The R&W written bank (10 skills, 3,433 items) never supplies a day's question.

- Pick: `daily.question()` filters templates to `deps.subject_of(k) == "math"` (daily.py:63-69), spr walks seeds; R&W slots come from `words.daily_item` (server/words.py:1355-1394), vocab frames and transition pairs only.
- Answer: Math via `progress.record` and `daily.feedback` (subject hard-coded "math", SAT pace math) (api_today.py:1576-1588, daily.py:293-316); R&W via `words.record_daily` and `rw_feedback` (api_today.py:1554-1574, daily.py:319-338). Late R&W answers 409 `late_rw_unavailable` unless Words takes `session` (api_today.py:1562-1563).
- Twin: Math `POST /api/drill {like:{day,slot}, count:1, source:'twin'}` resolved by `daily.resolve_drill`, which 422s any non-Math slot (daily.py:449-470); R&W twin is `POST /api/qotd/another` via Words (api_today.py:1591-1631).
- "5 more like this": Math drill({like}) (index.html:1853); R&W is a link to `/words/#wic` (index.html:1850), not the R&W practice bank.
- Save: Math only (api_today.py:1634-1656, daily.py:473-485); R&W offers "Add to my words".
- Rendering: R&W slot passage is painted by the page as `.qd-text` (index.html:1776) and `wsQ` passes only stem/choices (index.html:1772-1775); Math slot passes the whole public q to `UI.workspace`, which already renders `text`, figure and table.
- Up next's qotd row only checks the Math MC session (next.py:318-321).
- Verdict: partial. "R&W" exists as Words vocabulary slots only; there is no R&W bank question of the day.

Parity needs: an R&W bank slot (e.g. `rw:bank`) picked like `daily.question` from `deps.subject_of(k) == "rw"` templates, routed through the Math-style path (progress.record, `feedback()` with subject from the slot and `SAT_PACE_MS["rw"]`), `resolve_drill`/`saved_item` accepting it and setting `subject:"rw"` on the drill body, and Today's tab label in `SLOT_SHORT` (index.html:1685). Trap: R&W templates hold 1 to 110 fixed items (seed % n), so a date-hashed seed can land on an item the learner already met in practice; `daily.remember` only stops the reverse. The "twin" of an R&W item is another fixed item of the same template, and a 1-item template has none. The past-days strip and `marks/past` assume `math:mcq`/`math:spr` keys (daily.py:423-432).

## 5. Challenge (server/challenge.py, api_compete.py:28-74, web/challenge/index.html, Today chal card)

Two paths, both Math-only by construction:
- Legacy `/api/challenge` + `/api/challenge/start` (api_compete.py:28-57), used by web/challenge/index.html:117-148. `challenge.challenge(day)` builds 10 from `MIX` = the four Math domains, `LADDER`, two grid-ins at `SPR_AT=(4,8)` (challenge.py:18-22, 36-58). Started with legacy `drill.create(... "challenge", kind="challenge", fixed=True)`: no subject in cfg (api_compete.py:48-51, drill.py:2043-2065). Clock `CHALLENGE_SIZE * SECONDS_PER_QUESTION` (Math pace) (api_compete.py:35).
- Today's card loads `/contest/daily` and starts `/contest/daily/start` (index.html:749-752, 656-659); `compete._daily_slots` reuses `challenge.MIX/SPR_AT/LADDER` (server/compete.py:194-205) and needs a twin supply per template (`compete.pool`, compete.py:166-172).
- Page copy: no subject named; "10 question types" (index.html:2738) and web/challenge has no subject switch.
- Verdict: math-only.

Parity needs: an R&W MIX (Information and Ideas 3, Craft and Structure 3, Expression of Ideas 2, Standard English Conventions 2 from RW_BLUEPRINT 26/28/20/26, progress.py:58), no SPR_AT, R&W seconds (71 s a question, drill.py:104 medium budget, daily.py:28), `subject` written on the session/contest (compete `_insert` already takes `subject`, compete.py:179-185), a separate board per subject or an alternating day. Trap: compete's daily deals each entrant a "fresh twin" of each slot; R&W twins are other fixed items of the same template and tier, so supply per template/tier is thin (median 19 items a template, some 1); `pool("daily", tier)` will reject small templates and `_daily_slots` raises 409 "daily twin supply is too small" (compete.py:202-203).

## 6. /s shared set (web/s/index.html, server/sets.py)

- kind `set` redirects to `/practice/?share=` (s/index.html:123) and kind `test` to Tests; only kind `items` (exact shared questions, "Asked for help") runs on /s.
- Start: `POST /api/sets/{code}/start` -> legacy `drill.create(learner, sid, topics, n, None, timed, "shared", items=pairs)` with no subject (server/sets.py:785-803). R&W items are served (exact pairs, runner renders passages) but cfg/session have no subject, so budgets (TIER_BUDGET), coach "next" and every `cfg.get("subject","math")` reader treat it as Math.
- Inline help path (one item, `s.help`): renders with `UI.question` (s/index.html:308), which has no passage support (ui.js:2940-2964): an R&W item shows its stem without the passage. Must switch to `UI.workspace`.
- Facts block counts grid-ins (s/index.html:166); topic chips link `/practice/?topic=` and "Practise this skill" `/practice/?topic=` (s/index.html:172, :325): no `subject`, and the builder ignores `topic`.
- Verdict: partial.

## 7. Quick sheet (web/assets/quick.js)

- Quick question: `POST /api/drill {source:'quick', count:null}` no subject (quick.js:176-180) -> drill.py:1109-1112 Math coach topic. "Practise {skill}" `{topics:[q.topic], source:'map'}` (quick.js:157). Formats pref single value can force grid-ins (quick.js:178). Math-only. Rendering goes through `UI.workspace` (passages fine) unless question.js is missing, then `UI.question` (no passage).
- Log a mistake: catalogue `/api/shell/catalog` built from `api_bank.types()` with default subject math (api_shell.py:335-340, api_bank.py:82-87); copy "College Board's ... Math question IDs" (quick.js:330); skill picker `UI.DOMAINS/UI.TOPICS` Math only (quick.js:426-436); `example()` uses `UI.question` (quick.js:116). Text match `POST /api/types/match` scans all templates incl. R&W (api_bank.py:142-155), so a pasted R&W question can match an R&W type whose name/example the sheet then cannot show, and the follow-up drills (`{pool:'redo', ids, source:'outside'}`, quick.js:572, :582) carry no subject, so an R&W trap is dropped (409). The R&W "Log it" form lives on the practice builder's R&W panel instead (builder.js:308-323).
- No subject switch in the sheet.

## 8. Where a student can pick a subject (this cluster)

- Today: nowhere. Day's questions shows both subjects' slots as tabs (index.html:1708-1709), that is all.
- Up next / shell / `/api/next`: no subject param, no switch.
- Challenge page and Today chal card: no switch.
- /s: no switch (subject follows the shared items, but is not recorded).
- Quick sheet: no switch.
- Server endpoints that already accept a subject: `/api/today/insights?subject=` (api_today.py:1361-1365) and `/api/bank?subject=` (api_practice.py:349-352). `/api/today`, `/api/next`, `/api/qotd`, `/api/challenge`, `/api/contest/daily` do not.

## 9. What parity needs (cluster, concrete)

1. One rule: every body this cluster posts to /api/drill carries `subject` (Up next items, Today rows, at_risk, Mistakes card, calendar redo, quick, /s). Cheapest root fix: next.py `_item` and api_today `_row`/`_plan_row` stamp `subject` from the row's topic or template (`deps.subject_of`), and drill.resolve could infer subject from the first template/topic/trap/item when the body omits it instead of defaulting to math (drill.py:896). The latter fixes every caller at once, including saved/checks/history pools.
2. `/api/today` and `next.queue` either take `?subject=` or return both subjects' items (Review row per subject, Fix rows from `open_traps(subject=None)` labelled by subject, R&W due check-ins via `review.due(subject="rw")`).
3. `due_rechecks` consumers (brief, at_risk, next.due fallback, review_done) should either filter by subject or the drill must accept R&W ids.
4. Plan R&W tasks get a real start (`{subject:'rw', topics:[R&W topics of that domain], box: minutes}`) instead of "On your own · Bluebook".
5. Insights: pass `?subject=` from the page (gain/pace/causes), plus an R&W gains model (estimate.gains returns None for rw).
6. Day's question: an R&W bank slot (section 4).
7. Challenge: an R&W daily (section 5) or a subject switch on the board.
8. `UI.question` callers that can meet an R&W item (/s inline help, quick.js fallback and examples) move to `UI.workspace`, or `UI.question` learns `q.text`.
9. Client topic names: an R&W entry in `UI.TOPIC` (short name, glyph) so TOP()/chips stop printing raw slugs (receipt, slots, calendar).

## 10. R&W-specific traps

- Fixed items: "fresh seeds" cycle (`seed % n`, satbank/topics/rw.py:58-60). Twins, "Another like this", Saved "try a fresh one", the Sweep's "one fresh twin" and the challenge's per-entrant twin all assume another item of the same template exists; for R&W fall back to another template of the same skill and tier (drill._rw_serve does this for mistakes, drill.py:194-204).
- Copy: "new numbers" (question.js:2048, index.html:1881 "same trap, new numbers"), "Grid-in", "SAT Math", "44 a test", "35 minutes" module clock are Math words.
- Clock: R&W module is 32 min for 27 questions (64 for 54); Math pace constants (SECONDS_PER_QUESTION, 2100 s module, "8 in 12:40") must not apply to R&W drills.
- Habits and grid-in entry causes have no R&W meaning; hide rather than port.
