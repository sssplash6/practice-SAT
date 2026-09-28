# Section-owned traffic bottlenecks — 2026-09-27

Task 17 cannot edit `server/drill.py`, `server/ratings.py`, `server/api_shell.py`, `server/api_today.py`, or `server/api_tests.py`. The performance branch handles SQLite lock failures, Compete schedule generation, and Words caching. The remaining 50-learner latency target needs the section builders' changes below.

## Drill selection and next question

The latest full-route 50-learner run has **0 errors**, but `POST /api/drill` is **4.65 s p95** and `POST /api/drill/{sid}/next` is **3.68 s p95**. These are the first routes above the 1 s target. In a warmed drill/test-only run, they can fall below 1 s, but adding Shell or Today traffic raises the tails again. A direct `cProfile` of drill create with 2,000 attempts took about 10 ms: `drill.resolve()` was about 7 ms, and `drill._levels_at()` about 6 ms. That rebuild calls `ratings.level()` for roughly 485 template/tier pairs and does one SQL point read per pair. Its cache key is `MAX(attempts.id)`, so every new answer invalidates it during mixed write traffic. A naive database-wide ratings snapshot made the 200-learner run much worse because writes invalidated the snapshot between the individual `ratings.level()` calls; that experiment was removed.

**For the Drill builder:** in `drill._levels_at`, fetch all `item_ratings` rows with one SQL query and join them to the already batched attempts in memory. Build one coherent levels snapshot per rebuild, then let the next `MAX(attempts.id)` invalidate that whole snapshot. Avoid re-reading one rating per pair during the same rebuild. Profile `_fresh` and `_pick` under 50 mixed learners after that change; the direct empty-bank timing alone misses the contention.

## Test finish and shared worker pressure

`POST /api/session/{sid}/finish` was **1.61 s p95** in the latest 50-learner run (1.15 s in an earlier one). Five uncontended finishes with one answered item each took 15 ms total in the earlier profile, with `progress.record_paper` at 14 ms. The large loaded tail follows shared database and worker pressure rather than test scoring itself; the after run had no `database is locked` trace. Re-profile after Drill's batched ratings read. If the tail remains, the S5 builder should measure its time in `progress.record_paper()` and its write transaction separately.

## Measurements and limits

The controlled tool used 200 seeded learners, one Uvicorn worker, a temp `SATF_DB`, an ephemeral port, and three-second 10/50/200 stages. At 50 learners, the latest run handled 241 attempts with zero errors; the full after table is in `load-test.md`. Direct route profiles and live p95 measure different things. The 50-learner stage includes newly active worker threads; a second stage of the same size sometimes improves in an isolated drill/test mix but did not cure the full mixed workload. The background twin-supply survey can add CPU after 30 seconds on a cold checkout, so compare its impact separately when running longer tests.
