# Load survey — 2026-09-27

## Method

`PYTHONPATH=. python3 tools/load_test.py --seconds 3 --json /tmp/satf-load-final.json --server-log /tmp/satf-load-final-server.log`

The tool started one Uvicorn worker on ephemeral port 57657 with a temporary `SATF_DB`, seeded 200 distinct learners, and exercised drill create/answer/next, Today, Shell, Me, Words, and a diagnostic start/answer/finish. No production database or port 8000 was used. Each stage started 10, 50, or 200 workers for three seconds. In-flight requests were allowed to complete or hit the 15-second client timeout, so actual stage times were longer. Latency percentiles below include **successful responses only**; errors and throughput include every attempt. This is a short saturation survey on one local Mac, not a sustained production capacity estimate.

| Concurrent learners | Actual stage time | Requests | Errors | Attempts/s | Successful/s | First failures or slow routes |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 10 | 17.20 s | 22 | 10 | 1.28 | 0.70 | Drill create 5/5 and Shell 5/5 timed out; Today p95 1.56 s |
| 50 | 7.41 s | 222 | 0 | 29.96 | 29.96 | Drill create p95 4.90 s; drill next 2.32 s; Shell 2.18 s |
| 200 | 36.95 s | 422 | 129 | 11.42 | 7.93 | Test finish 29/33 errors; Shell 26/68; drill answer 24/43 |

The three slowest routes at 200 learners by **successful p95** were:

| Route | Successful responses / attempts | p50 / p95 / p99 | Likely cause |
| --- | ---: | ---: | --- |
| `POST /api/session/{sid}/finish` | 4 / 33 | 9.30 / 10.28 / 10.40 s | Write contention while finalizing and recording a paper. Server logs show `sqlite3.OperationalError: database is locked` in `db.run` and `BEGIN IMMEDIATE`; 500s and timeouts account for most failed finishes. |
| `GET /api/me` | 39 / 45 | 1.96 / 9.52 / 10.84 s | Shared worker and database pressure. This route was much faster at 50 learners (p95 1.46 s); loaded requests queued behind synchronous contest generation and writes. |
| `GET /api/words` | 47 / 66 | 3.64 / 6.17 / 8.06 s | The same worker and database pressure. This route was p95 1.34 s at 50 learners; 19 requests timed out or lost their connection at 200. |

Shell is the **cold-start hotspot**, even though its successful p95 at 200 learners (3.34 s, 26 errors) is below those three. A `cProfile` run of five direct Shell calls took 11.09 s and 42.6 million function calls. `compete.ensure()` consumed 11.09 s, called 15 times; `trap_families()` consumed 8.68 s and generated 9,689 bank items. Shell calls `closing_soon`/`due_today`, and its Compete part calls `ensure` and `due_today` again. On a fresh database this builds contest schedules and trap supply during requests. A direct profile of five drill creates took 0.016 s, so its loaded 4.90-second p95 at 50 learners is chiefly shared contention rather than intrinsic selection cost.

To profile the worst 200-learner route, five direct `api_tests.finish()` calls with one answered diagnostic question each took 0.015 s total. `progress.record_paper()` used 0.014 s; commits and access checks were small when uncontended. Its 10.28-second loaded p95 therefore follows concurrent write pressure, consistent with the SQLite lock traces. These profiles are uncontended function timings and cannot by themselves assign every queued millisecond to a single component.

An earlier eight-second survey corroborated overload: at 200 learners, 1,945 of 2,066 attempts failed, mostly connection errors or timeouts. The Uvicorn process was still alive before the tool shut it down; this was a service collapse, not a process crash. The background twin-supply survey starts 30 seconds after startup when its cache is absent, adding CPU work during long cold runs. The final three-second run's 200-worker stage also crossed that delay. Both effects should be measured separately after moving expensive contest generation out of the request path and reducing SQLite write contention.

## Backup exercise

`tools/backup_db.py` was exercised against a temporary WAL database during a live SQLite connection. Snapshot verification reported `integrity_check=ok` and one table row; restore reproduced the row count; overwriting a nonempty target failed without `--force` and succeeded with it. Synthetic dated files confirmed retention of 14 daily and 8 weekly copies. Backups must use `SATF_BACKUPS` outside the repository.

## Task 17 after run — 2026-09-27

`PYTHONPATH=. python3 tools/load_test.py --seconds 3 --json /tmp/satf-perf-final-run.json --server-log /tmp/satf-perf-final-run-server.log` used a temporary database and ephemeral port after the Compete transaction changes. The result is a single short run, not a capacity certification. The server was still alive at shutdown. The log contained **no `database is locked` error**. `server/checks/perf.py` separately verified WAL, a 2.5-second SQLite busy timeout, 400 concurrent writes, an external writer wait, precomputed contests, and Words cache invalidation.

| Learners | Before attempts / errors | After attempts / errors | Before total attempts/s | After total attempts/s | Main after p95s |
| ---: | ---: | ---: | ---: | ---: | --- |
| 10 | 22 / 10 | 167 / 0 | 1.28 | 47.85 | Drill create 1.18 s, next 0.85 s, Shell 0.20 s |
| 50 | 222 / 0 | 241 / 0 | 29.96 | 35.76 | Drill create 4.65 s, next 3.68 s, Shell 1.32 s, Words 0.34 s |
| 200 | 422 / 129 | 511 / 0 | 11.42 | 39.80 | Shell 10.08 s, drill next 6.80 s, test finish 7.99 s |

The 10- and 50-learner **zero-error** targets and the 200-learner **no SQLite lock error** target passed in this run. The **50-learner hot-route p95 under 1 s target did not pass**. Drill create and next dominate the remaining latency; see `perf-for-sections.md` for the profile and the section-owned fix. An earlier run with the same database changes and before the final Compete transaction edits recorded 237/0, 257/0, and 508/0 attempts/errors at 10/50/200, but also missed the latency target. The small runs vary, and none establish subsecond performance at 50.
