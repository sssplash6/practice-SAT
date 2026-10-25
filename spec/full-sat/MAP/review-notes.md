# Review cluster: R&W parity notes (Fork A)

Scope: review queue (Due), Redo (mistakes), Marked, Saved, History, Fixed, walk, worksheet sheet, print (trap sheet, error log), outside-logged mistakes. Read-only. Evidence verified by two probes on a scratch DB (`scratchpad/map/probe_review.py`, `probe_review2.py`), output quoted where it matters.

## 0. The one-line picture

Server: almost every Review read endpoint already takes `?subject=` and filters correctly (`server/api_review.py:343-346` `_subject`, and `subject: str = "math"` on counts/due/snooze/redo/marked/saved/fixed/history/history.csv/ledger/calibration/trapsheet at 379-1022). Probe: `GET /api/review/redo?subject=rw` returns the R&W mistake; `GET /api/review/redo` (no subject) returns nothing.

Page: `web/review/review.js` never sends `subject` anywhere (grep for "subject" in review.js: zero hits). Same for `walk.js`, `sheet.js`, `print.html`, `item.js`. So the Review hub is Math-only in practice: R&W misses, saved, marked, history, fixed, due are invisible.

Every drill body the Review pages POST also omits `subject`, and `drill.resolve` defaults to math (`server/drill.py:896`) and then (a) 422s an R&W template (`drill.py:914-915` "too many templates or wrong subject"), (b) drops R&W ids from items/queue (`drill.py:1083-1084`, gives 409 `filters_removed_all`), (c) reads only Math open traps for pool redo (`drill.py:246` gives 409 `no_open_mistakes`), (d) rematch slots of R&W fail `no_bank` (`drill.py:1122`). So even with the lists shown, every action button fails for R&W.

No subject picker exists on any Review page (index.html, walk, sheet, print). The only subject switch in the site near this cluster is the Practice builder's (`web/practice/builder.js:265-270`).

## 1. Feature by feature

| Feature | R&W today | Server | Page |
|---|---|---|---|
| Counts strip / tab counts | Math-only (page) | `api_review.py:378-381` subject-aware; probe `counts?subject=rw` open=1 | `review.js:133` `/review/counts` no subject |
| Due today list | Math-only (page) | `review.py:547` `due(subject)`; frozen per subject in `due_days` (`review.py:489-499`) | `review.js:140` `/review/due` no subject |
| Snooze | Math-only (page) | `api_review.py:395-403` subject-aware | `review.js:862` no subject (404 "not on today's list" for an R&W key) |
| Start review / All / "Fix N" | Math-only | body `{source:'due', box}` goes through `drill.py:1071-1078` (warmup_candidates by `subject`, default math). `review.resolve_drill` (`review.py:644-717`) is dead code: nothing calls it (grep), and it is math-pinned anyway (`review.py:648` `due(learner, tz)`, `659` unfiltered `open_traps`, `682` `frozen(learner, tz)`, `684` `pts_fn(learner)`, `701` `fluency(...)` default math, `_zone` `review.py:636` `subject='math'`) | `review.js:165` `startBody` no subject |
| Redo list | Math-only (page) | `api_review.py:406-505` subject-aware | `review.js:494-510` `listPath` no subject |
| Redo Fix / Fix these / Worth the most / blind spots | Math-only | pool redo needs `subject:'rw'`; probe: no subject `no_open_mistakes`, with subject servable | `review.js:1914-1920` `redoBody`, `1735` blind, `1420` worth: no subject |
| Twin this set / Same questions again (Marked, Saved, History, a sitting's Retake) | Math-only | items dropped without subject (`drill.py:1084`) | `review.js:1932-1945` `barBody`, `1744-1756`, retake `1189` |
| Check these now (Fixed) | Math-only | pool checks, `drill.py:246-249` (checks query unfiltered, then `1083` filter) | `review.js:1963` |
| Pane: Another like this (twin) | Math-only | probe: `{templates:[rw], source:'review'}` 422 wrong subject; with subject 200 | `review.js:2052-2057` `twinBody` no subject |
| Pane: The very same question | Math-only | probe: 409 `filters_removed_all` | `web/assets/runner.js:3798` default `again` body, no subject |
| Pane: easier / harder axes | Math-only | same 422 | `review.js:2051` axes via the same body |
| Walk (new / ids / session) | Math-only | `api_review.py:1092-1137`: attempts unfiltered by subject, but `drill.create` at `1129` has no subject: all-R&W walk 409 `filters_removed_all` (probe), mixed walk keeps R&W rows only in `cfg.walk` | `walk.js:58,64` no subject; a 409 is shown as "Nothing to walk right now" (`walk.js:69-72`) |
| Walk step 1 Try again | Math-only | 409 | `walk.js:140` no subject |
| Walk step 2 name it | broken for R&W even with subject | `api_review.py:1076` `called = diag == norm`; R&W norm is always "" (`progress.py:98-102` `miss_norm`), so an R&W miss is never "called"; the end card reads "you named 0" | choices are the distractor `why_wrong` texts (`walk.js:88-99`, `api_review.py:880-888`) plus "Arithmetic slip" copy (`api_review.py:886`) |
| Walk step 4 Prove it | Math-only, and runs out | 422 without subject; with subject a 1-item type gives 409 `filters_removed_all` at the missed tier and `pool_empty` for a plain twin (probe 2) | `walk.js:156-162` `proveBody` (no subject, tier pinned to the miss) |
| Spot the trap | Math by design | `api_review.py:1231-1232` 409 for norm in UNNAMED (every R&W trap); probe confirms | `review.js:1405-1408` picks a misconception row |
| Habits, Trap gauntlet, Drill this habit | Math by design | `habits.families` is Math (`server/habits.py:81-83`); probe: habit body 422, gauntlet `no_bank` | `review.js:905-907`, `1371-1384` |
| Cause fixes: Speed drill, Careful set, Read the ask, Learn this type | Math-only (no subject) | servable for R&W with subject (probe: learn rw servable) | `review.js:1394-1399`; "Grid-in entry · 8" (`1397`) is Math by nature |
| Right but slow / Fluency sprint (History head) | Math-only | `history?subject=` pace part subject-aware | `review.js:1659-1666` bodies no subject |
| Final check (exam week) | Math-only | trapsheet subject-aware | `review.js:1521-1524` `/review/trapsheet` and drill body, no subject |
| Your rules card | Math-only | `/api/bank` defaults math | `review.js:1540` `/bank` no subject |
| Ledger / calibration | Math-only (page) | subject-aware (`review.py:918`, `978`) | `review.js:416`, `1434` no subject |
| Print worksheet (Redo/Saved) | Math-only | 409 without subject | `review.js:1779-1786` |
| Worksheet answer sheet + key | works (renders) once a sheet exists | `/drill/{sid}` | `sheet.js:92-120` A-D for mcq, key via `UI.workspace` renders the passage (`sheet.js:243`); "Print another version" `{again: sid}` (`sheet.js:196`) loses subject (`drill.py:855-857` does not copy `subject`) |
| Print: trap sheet | Math-only (page) | `review.trapsheet` subject-aware; example renders R&W passage (`print.html:139`) | `print.html:164` no subject |
| Print: error log | Math-only (page), wrong copy for R&W | `/review/redo` | `print.html:200` no subject; `print.html:110` KIND gridin = "Grid-in: a wrong value" would label every R&W row |
| Item detail `/api/review/item` | works | no subject filter; `public()` passes `text` (`api_tests.py:39-40`) | pane/walk render via `UI.workspace`, which draws the passage (`question.js:430-575`) |
| Mistake dismiss / restore / reopen / add | works | id-based, subject-neutral (`api_review.py:283-340`) | fine |
| Legacy `/api/mistakes` | Math-only | `api_review.py:63-74` `progress.topics()` and `open_traps(learner)` filtered to Math names; probe returns `[]` with an R&W trap open | used by `web/tests/start.js:468` (trap tests, outside this cluster) |
| `/mistakes/` page | redirect | `api_review.py:55-60` 307 to `/review/?tab=redo` (keeps query) | `web/mistakes/index.html` same, static fallback |

## 2. Math-specific details (beyond the missing subject param)

1. **R&W misses are typed "gridin".** `progress.trap_kind("")` returns "gridin" (`progress.py:92-93`) and every R&W miss has norm "" (`progress.py:98-102`). Review uses it at `review.py:265-267`, `api_review.py:441`, `api_review.py:645`. Shows as "grid-in entry" (`review.js:952`), counted under Kind = Grid-in (`review.js:441`), "Grid-in: a wrong value" in the error log (`print.html:110`). Probe: `kind: gridin` on an R&W Redo row.
2. **One R&W trap per template.** norm "" means `traps(learner, template, norm)` collapses every R&W miss of a type into one trap (probe: second miss became `hits: 2` on trap 1). Group by "Mistake type" (`api_review.py:486-490`, key = norm) puts all R&W traps in one group named after the first row's label.
3. **R&W labels are item subtypes.** `record_trap` labels an R&W miss with `practice.skill_of(q)` (`progress.py:385-386`), which is the item's `subtype` (`satbank/topics/rw.py:37`): 1,724 distinct strings across 3,433 items, some passage-specific (probe label: "T1 link: a skeletal condition common among the crew and among modern archers"). A logged R&W miss gets the blueprint majority label instead (`api_bank.py:283`), so the same type reads two ways.
4. **Fixed tab "tiers proven"** counts only same-template clean answers (`api_review.py:638-641`), but an R&W trap closes on clean answers anywhere in its skill (`progress.py:490-493`), so an R&W fixed row can show no proven tier.
5. **Counts not subject-filtered**: `recovered_month` (trap_log, `review.py:811`), `open_week_delta` (`ledger_deltas`, `review.py:785-786, 819`), `worksheets_waiting` (`review.py:821`). They would show the same number on both subjects.
6. **Grid-in / Math UI**: Format filter MC/Grid-in (`review.js:431`), row "MC" bit (`review.js:947,1010,1029`), "Grid-in entry · 8" (`review.js:1397`), Topic filter and short names from `UI.TOPICS`/`UI.DOMAINS`, which are the 19 Math topics only (`web/assets/ui.js:652-679`; used at `review.js:61-62, 421-424`). `UI.RW_SKILL` exists (`ui.js:681-687`) but Review does not use it.
7. **"New numbers" copy** on R&W: `review.js:298` ("prove it on new numbers"), `review.js:1165` (Rematch title), `walk.js:177` ("proven on new numbers"), runner copy `runner.js:1853, 2802, 3869, 3901, 4114, 4157`, `sheet.js:206` ("New numbers"). R&W twins are new passages, not new numbers.
8. **Empty-state samples are Math**: `review.js:751-752` ("If 3x + 5 = 20...", "Linear equations"), `review.js:756` fetches `/types/rr.partner/example`.
9. **Seeds assumed unlimited**: twin, prove, Twin this set (each up to N), worksheet `each`, Print another version, Fix (each 2) all ask the same template for a fresh seed. R&W templates hold 1 to 110 items (median 19; 7 templates hold 3 or fewer). Probe 2: after one answer on a 1-item type, a twin is 409 `pool_empty`; prove at the missed tier 409 `filters_removed_all`. Redo already falls back to other types of the skill via `_rw_serve` (`drill.py:194-205`); twin/prove/again do not.
10. **Trap sheet example leaks bank items**: `review.trapsheet` calls `api_bank.example(template, want=None)` for R&W (`review.py:868-875`), seed 900000+crc (`api_bank.py:187`), and `seed % n` lands on a real bank item, possibly the missed one or one not yet served, printed with its key and not marked seen. The drill's own worked example avoids this (`drill.py` `_example` avoid); the trap sheet does not.

## 3. Outside-logged mistakes

- **Builder R&W "Log it" always fails**: `web/practice/builder.js:321` posts `{subject:'rw', skill, letter, cb_id | text}` to `/api/mistakes/log`, whose model requires `template` (`server/api_bank.py:249-256`) and has no `subject/skill/text`. Probe: 422 `body.template missing`. The success copy "It waits in Review's Outside list for the R&W bank" (`builder.js:322`) is stale on two counts: the bank exists, and Review has no Outside list (TABS `review.js:65-68`; outside traps show in Redo as "logged by you", `review.js:950`, only when the page asks for that subject).
- **With a template, logging works**: probe `/api/mistakes/log {template: rw..., origin}` 200, `norm ""`, `source outside`.
- **R&W College Board IDs never match**: `_match_id` reads `material/keys/*.json` only (`api_bank.py:36-45, 88-99`), 19 Math files. R&W ids return `via: none`, though `drill.cb_index()` knows their skill (`drill.py:449-470`). Quick sheet (`web/assets/quick.js:364`) therefore cannot map an R&W ID.
- **match_pick letter to reason** (`api_bank.py:165-177`) maps a letter onto the type's sampled reasons; meaningless for R&W (distractor texts of other passages). An R&W log should send no reason (unnamed, closes on clean answers in the skill).
- **After logging**: quick sheet "Practise 3" `{pool:'redo', ids:[trap], source:'outside'}` (`quick.js:572, 582`) has no subject: probe 409-equivalent `no_open_mistakes` for an R&W trap. "Practise {skill} · n" (`quick.js:472`) sends an R&W topic without subject: 422 "a topic of the other subject" (`drill.py:908-909`).
- `/api/outside/misses` is advertised (`api_shell.py:281`, `quick.js:673-674`) but has no route; quick.js falls back to a topics drill.

## 4. What parity needs (concrete, smallest first)

1. **Root fix in one place: infer the subject in `drill.resolve`** when the body has none, before `drill.py:896`: from `templates`/`topics`, from `ids` pairs (items, saved, marked, history attempt ids), from trap `ids` (pool redo/checks), from `rematch`/`again` parent `cfg.subject`, from `from_session`. That alone makes every Review/walk/pane/runner/sheet/quick body work for R&W without touching each caller (twin, very same question, prove, Fix, Twin this set, worksheet, Print another version, Rematch, Practise 3). Also copy `subject` in the `again` key list (`drill.py:855-857`). Explicit `subject` still wins; mixed bodies stay a 422.
2. **One subject switch on Review** that adds `subject` to every GET in `review.js` (counts, due, snooze, redo, marked, saved, fixed, history, history.csv, ledger, calibration, trapsheet, bank) and to `print.html` (`/review/redo`, `/review/trapsheet`) and to the print links; carry it in the URL (`?subject=rw`) the way the builder does (`builder.js:100, 269`) so `/mistakes/?subject=rw` (redirect keeps the query, `api_review.py:59`) and Today/Up next links land right. Due's frozen list is already per subject (`due_days.subject`), and `snooze` is keyed per subject call.
3. **Topic filter and names**: build the Topic filter from the response's topics (or `UI.RW_SKILL` plus the 4 R&W domains) when subject is rw (`review.js:421-424`, `61-62`).
4. **Kind for R&W**: make `review.trap_kind` return "misconception" (or a new "reading" kind) for an R&W trap without a student cause, so no "Grid-in" anywhere (`review.py:265-267`; display `review.js:441,952`, `print.html:110`). Hide Format filter, "Grid-in entry", Spot the trap, habits/gauntlet for R&W.
5. **Walk naming**: `api_review.py:1076` compare the diag against the norm of the picked option's reason too (`a["reason"]`), so "you named it" works for R&W; drop "Arithmetic slip" from R&W choices (`api_review.py:886`, `walk.js:34`).
6. **Fixed items running out**: twin/prove/again for R&W should fall back to another type of the skill when the template has no fresh item (reuse `drill._rw_serve`'s rule, `drill.py:194-205`), and prove should not pin the miss tier when the type lacks it. Copy: "new passage" not "new numbers" when subject is rw.
7. **Trap sheet example**: skip or avoid-seen for R&W (`review.py:868-875`), as the drill's worked example does.
8. **Outside log**: make the builder's R&W form resolve a template (cb_id through `drill.cb_index()` skill to `rw_<skill>`, then a type of that skill; or `/api/mistakes/log` accepts `{subject:'rw', skill, cb_id}` and picks the type) and teach `_match_id` R&W ids via `cb_index`; fix the success copy.
9. **Labels**: decide one R&W trap label (type name from `blueprint.kinds()[t]["skill"]` or the CB skill) instead of the per-item subtype (`progress.py:385-386`).
10. **Dead code**: delete `review.resolve_drill` and `_zone` (`review.py:630-717`) or subject them; nothing calls them. Separately (shared with Math, not R&W-specific): "Fix N · box min" (`review.js:175`) sends `{source:'due', box}`, which never includes open mistakes (`drill.py:1071-1078`), so with mistakes open and nothing due it gets `nothing_due` (probe 2, R&W; same code path for Math).

## 5. Where a subject can be picked

- Review hub, walk, worksheet sheet, print: nowhere. Server endpoints accept `?subject=` but the pages never send it.
- `/mistakes/` redirect keeps the query string (`api_review.py:59`, `web/mistakes/index.html:18-19`), so a `?subject=rw` would survive once Review reads it.
- Practice builder: Math | Reading & Writing seg, `?subject=rw` in the URL (`builder.js:100, 265-270`).
- Quick sheet log: no subject; Pick by skill uses Math `UI.TOPIC` (`quick.js:39`).
