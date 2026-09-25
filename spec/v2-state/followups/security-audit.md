# Server security and abuse audit — 2026-09-25

Audited merged server at `6576c0c` (server code unchanged from `1a897cb`). This covers every route currently installed by `server/app.py`, including `api_*.py`, `reports.py`, and `sets.py`, and their calls into `deps.py`, `drill.py`, and `progress.py`. `api_words.py`, `words.py`, and the new S8/S7 routes were not on master at this revision; audit them after merge. Reproductions below ran with `TestClient`, a temporary SQLite database, and a temporary report directory. No production database or server was used.

## Findings

| ID | Severity | Finding |
| --- | --- | --- |
| SEC-01 | High | Signup lets an unrelated finished sitting change a verified user's name and discover whether an email is verified. |
| SEC-02 | High | Disposable learner codes reveal the daily answer before a different code answers; the current challenge also serves identical questions to both codes. |
| SEC-03 | Medium | Diagnostic and mock session routes treat the session ID as the sole credential for reading, answering, finishing, signup, and results. |
| SEC-04 | Medium | The outside-mistake quota counts distinct second-resolution timestamps, so a burst of repeated logs passes the 30-per-day check. |
| SEC-05 | Medium | Chunked multipart report uploads are fully parsed and spooled before their aggregate size is checked. |
| SEC-06 | Medium | An unbounded, unauthenticated GET inserts arbitrary `cb_unknown` IDs into SQLite. |
| SEC-07 | Medium | Legacy practice and mock creation bypass `learner_of`, including the retired-code write prohibition. |
| SEC-08 | Medium | The daily challenge board reads and sorts every finisher before applying its 100-row response cap. |
| SEC-09 | Low | `/api/mistakes/log` writes trap state for a `sample:` learner despite the sample's read-only policy. |

### SEC-01 — verified account name overwrite and email enumeration

**Location:** `server/api_account.py:25-55`. Signup checks that *some* session finished, then looks up the supplied email. For an existing verified user, lines 41-42 update that user's name without proof of mailbox ownership. The response also distinguishes `already-verified` from an unverified address.

**Reproduction:** In the common script below, `verified_name_overwrite` printed `200 Changed Name ... already-verified`. The caller created its own diagnostic and did not possess the victim's account or email token.

**Fix:** Do not update a verified user from a new signup. Keep the sitting unlinked until the mailbox owner confirms a fresh one-use token. Return the same public response for known and unknown email addresses.

### SEC-02 — daily answer farming with disposable identities

**Location:** `server/api_today.py:63-95`, `server/api_compete.py:34-50`, `server/challenge.py:26-45`, `server/deps.py:65-94`. Any valid-looking `a:` code is accepted as a new learner. One code can answer the question of the day and receive the key; a second code then answers the same day correctly. At this audited revision, the challenge stores one shared set of ten questions for all learners, so a disposable finished sitting also exposes the exact next entrant's questions and keys.

**Reproduction:** The common script prints `qotd_disposable ... True`. The optional challenge script below prints `same_first True` after the disposable sitting finishes and can read `/api/session/{sid}/results`.

**Fix:** Treat unauthenticated daily scores as unranked or require a verified, rate-limited identity for ranked attempts. The pending S8 twin design reduces direct answer copying for contests; recheck it after merge. A public deterministic question of the day cannot enforce one attempt per person solely with browser-minted codes.

### SEC-03 — session ID alone authorizes test changes and key disclosure

**Location:** `server/api_tests.py:131-228`, `server/api_results.py:16-51`, `server/api_account.py:25-55`. These routes call `session_or_404` but never `mine` or `learner_of`. A caller who obtains a session ID can read the saved answers, change an answer, finish a sitting, attach signup, and fetch the full key after finish. IDs are random, which limits guessing, but an ID copied from a link or log is sufficient. A cross-site form can also POST the bodyless `/finish` URL if it knows the ID.

**Reproduction:** The common script creates the sitting with learner A, then posts an answer with no `X-Learner`; `session_takeover 200 0` is returned, and learner B can read the saved answer.

**Fix:** Require `X-Learner` ownership for learner-owned sittings. For truly anonymous diagnostic sittings, issue a separate server-minted bearer secret and verify it on every read and write; do not use the routable ID as that secret. Require the same check before returning results or associating an email.

### SEC-04 — outside-mistake quota bypass

**Location:** `server/api_bank.py:227-243`, `server/progress.py:137-138`, `server/progress.py:329-361`. The quota uses `COUNT(*)` over `DISTINCT template,norm,at`, while `at` has second precision. Repeating the same mistake within one second appends trap-log events but counts as one toward the 30-per-day limit.

**Reproduction:** The common script sent 35 requests and printed `outside_mistake_limit 35 [200] 36`; all succeeded and at least 36 events were recorded (the first opening writes two events).

**Fix:** Count outside log requests or durable log rows by learner and day, not distinct timestamps. Enforce it with a transaction/atomic insert so concurrent requests cannot all pass the same prior count.

### SEC-05 — chunked multipart body spooled before upload cap

**Location:** `server/reports.py:627-649`, `server/reports.py:839-860`. The early gate only runs if `Content-Length` is decimal. A chunked request has no such header. `request.form()` then parses and spools up to 100 files before `_check_files` applies the 200 MiB aggregate cap or the 10-file limit; the report rate check runs even later. Repeated streams can consume temporary disk and worker time even when all reports are rejected.

**Reproduction:** The scaled TestClient script below lowers the cap to 64 bytes. A normal request is rejected by the early gate with `file: null`; the streamed request reaches `_check_files` and reports `file: x.png`. The order is the same at the production 200 MiB cap.

**Fix:** Enforce a byte cap while reading the ASGI request stream, before multipart parsing and spooling, for both fixed-length and chunked bodies. Apply a request rate/connection limit before accepting upload bytes.

### SEC-06 — unbounded durable writes from GET `/api/types/match`

**Location:** `server/api_bank.py:93-101`. The `id` query parameter has no length or format limit and is inserted into `cb_unknown` whenever unknown. A new ID per request grows the table; there is no learner check or request rate limit. The GET is not read-only.

**Reproduction:** The common script sends a 1,017-character unknown ID and prints `unknown_id_write 200 0 1` for the table row count.

**Fix:** Require the College Board ID format and a short maximum length; reject malformed values before lookup. Rate-limit telemetry writes and bound retention/rows. Prefer a POST for telemetry and keep GET read-only.

### SEC-07 — retired-code write through legacy creation routes

**Location:** `server/api_legacy.py:28-57`, `server/api_tests.py:131-140,295-305`, `server/deps.py:80-85`. `POST /api/practice` and the older `/api/mock/{num}` accept a body-supplied learner without calling `writer_of` or `learner_of`. `/api/session` similarly accepts a header by regex only. The swap middleware records method but does not enforce retirement by itself.

**Reproduction:** The common script inserts a retired code, calls `/api/practice` with that code in the JSON body, and prints `retired_legacy_write 200 1` for the new session count.

**Fix:** Route all learner creation through `writer_of` (or an explicit anonymous mode with a server-minted code) and validate body-supplied codes too. Retired and sample codes must fail before generating questions or writing sessions.

### SEC-08 — unbounded daily board work

**Location:** `server/challenge.py:55-76`, `server/api_compete.py:53-59`. `challenge.board` fetches every finished sitting on the requested date, builds an entry for each, and sorts the entire list; only then does it take 100 rows. The public `day` query accepts any date. Cost and memory rise with all finishers, although the response has at most 101 entries.

**Reproduction:** The common script adds 1,000 finished rows and requests the board; `board_unbounded_work 200 1000 100` shows all 1,000 were processed for 100 returned rows.

**Fix:** Compute rank/count and the top rows in indexed SQL, with a bounded query for the caller's own row. Validate a reasonable day range. Recheck after S8 merges, as that branch replaces this board.

### SEC-09 — sample learner trap writes

**Location:** `server/api_bank.py:227-250`, `server/progress.py:329-361`, `server/deps.py:141-147`. This write route calls `learner_of`, not `writer_of`, then calls `record_trap`, which lacks the sample guard present on `progress.record` and `progress.log_mistake`.

**Reproduction:** The common script prints `sample_write 200 1`: a `sample:` learner now has a trap row.

**Fix:** Use `writer_of` at every mutating route, and guard `record_trap` itself against sample learners so internal callers cannot bypass the policy.

## Reproduction scripts

Run from the repository root; the scripts use temporary storage. The output shown above was obtained with `PYTHONPATH=. python3`.

```python
# Save as /tmp/sec-audit-repro.py; run with PYTHONPATH=. python3 /tmp/sec-audit-repro.py
import os, tempfile
os.environ['SATF_DB'] = tempfile.mktemp(prefix='satf-security-', suffix='.db')
os.environ['SATF_REPORTS'] = tempfile.mkdtemp(prefix='satf-security-files-')
from fastapi.testclient import TestClient
from server import db
from server.app import app

with TestClient(app) as c:
    a, b = {'X-Learner': 'a:auditvictim01'}, {'X-Learner': 'a:auditattacker01'}
    made = c.post('/api/session', headers=a).json()
    sid, qid = made['id'], made['questions'][0]['id']
    changed = c.post(f'/api/session/{sid}/answer', json={'question_id': qid, 'answer': 0})
    seen = c.get(f'/api/session/{sid}', headers=b).json()['answers']
    print('session_takeover', changed.status_code, seen.get(qid))

    db.run('INSERT INTO users(id,first,last,email,verified,created) VALUES(?,?,?,?,1,?)',
           'audit-user', 'Original', 'Student', 'victim@samplemail.com',
           '2026-09-25T00:00:00+00:00')
    c.post(f'/api/session/{sid}/finish')
    signed = c.post(f'/api/session/{sid}/signup', json={
        'first': 'Changed', 'last': 'Name', 'email': 'victim@samplemail.com'})
    name = db.one('SELECT first,last FROM users WHERE id=?', 'audit-user')
    print('verified_name_overwrite', signed.status_code, name['first'], name['last'], signed.json()['email'])

    day = c.get('/api/qotd', headers=a).json()['day']
    leaked = c.post('/api/qotd', headers=a, json={'answer': 0, 'day': day})
    key = leaked.json()['answer_index']
    clean = c.post('/api/qotd', headers=b, json={'answer': key, 'day': day})
    print('qotd_disposable', leaked.status_code, key, clean.status_code, clean.json()['correct'])

    before = db.one('SELECT COUNT(*) AS n FROM cb_unknown')['n']
    probe = c.get('/api/types/match', params={'id': 'unknown-audit-id-' + 'x' * 1000})
    after = db.one('SELECT COUNT(*) AS n FROM cb_unknown')['n']
    print('unknown_id_write', probe.status_code, before, after)

    codes = [c.post('/api/mistakes/log', headers=b, json={'template': 'lin.evaluate'}).status_code
             for _ in range(35)]
    events = db.one('SELECT COUNT(*) AS n FROM trap_log WHERE learner=?', b['X-Learner'])['n']
    print('outside_mistake_limit', len(codes), sorted(set(codes)), events)
    sample = c.post('/api/mistakes/log', headers={'X-Learner': 'sample:audit'},
                    json={'template': 'lin.evaluate'})
    sample_traps = db.one('SELECT COUNT(*) AS n FROM traps WHERE learner=?', 'sample:audit')['n']
    print('sample_write', sample.status_code, sample_traps)

    db.run('INSERT INTO retired(code,"into",at) VALUES(?,?,?)',
           'a:auditretired01', 'a:newcode01', '2026-09-25T00:00:00+00:00')
    old = c.post('/api/practice', json={'learner': 'a:auditretired01',
                                        'basket': {'linear_equations_in_one_variable': 1}})
    stored = db.one('SELECT COUNT(*) AS n FROM sessions WHERE learner=?', 'a:auditretired01')['n']
    print('retired_legacy_write', old.status_code, stored)

    with db.transaction() as conn:
        for i in range(1000):
            conn.execute('INSERT INTO sessions(id,kind,learner,day,started,finished,result)'
                         ' VALUES(?,?,?,?,?,?,?)',
                         (f'board-{i}', 'challenge', f'a:board{i:05d}', '2026-09-25',
                          '2026-09-25T00:00:00+00:00', '2026-09-25T00:01:00+00:00',
                          '{"right":1,"asked":10}'))
    board = c.get('/api/challenge/board', params={'day': '2026-09-25'})
    print('board_unbounded_work', board.status_code, board.json()['players'],
          len(board.json()['entries']))
```

The current shared challenge can be checked separately on a fresh temporary database: start with `a:first`, answer its ten questions through `/api/drill/{sid}/answer`, finish through `/api/drill/{sid}/finish`, and retrieve `/api/session/{sid}/results`. Starting with `a:second` on the same day returns the same first stem. This was run and printed `same_first True`.

```python
# Save as /tmp/sec-upload-repro.py; run with PYTHONPATH=. python3 /tmp/sec-upload-repro.py
import os, tempfile
os.environ['SATF_DB'] = tempfile.mktemp(prefix='satf-upload-', suffix='.db')
os.environ['SATF_REPORTS'] = tempfile.mkdtemp(prefix='satf-upload-files-')
from fastapi.testclient import TestClient
from server.app import app
from server import reports
reports.MAX_TOTAL, reports.MB = 64, 1  # scale down without changing the parsing order
with TestClient(app) as c:
    payload = b'\x89PNG\r\n\x1a\n' + b'x' * 100
    data = {'data': '{"kind":"page","category":"idea"}'}
    files = {'files': ('x.png', payload, 'image/png')}
    h = {'X-Learner': 'a:uploadprobe01'}
    normal = c.post('/api/report', headers=h, data=data, files=files)
    raw = (b'--audit-boundary\r\nContent-Disposition: form-data; name="data"\r\n\r\n'
           + data['data'].encode() + b'\r\n'
           + b'--audit-boundary\r\nContent-Disposition: form-data; name="files"; filename="x.png"\r\n'
           + b'Content-Type: image/png\r\n\r\n' + payload + b'\r\n--audit-boundary--\r\n')
    streamed = c.post('/api/report', headers={**h, 'Content-Type':
                     'multipart/form-data; boundary=audit-boundary'},
                     content=(part for part in [raw]))
    print('fixed length:', normal.status_code, normal.json()['detail'])
    print('streamed:', streamed.status_code, streamed.json()['detail'])
# fixed length: 413 {'file': None, 'limit': 64}
# streamed:     413 {'file': 'x.png', 'limit': 64}
```

## Checks with no finding at this revision

- User-supplied SQL values in the audited routes are bound as parameters. Dynamic SQL identifiers in `api_me.py`, `progress.py`, `deps.py`, and `reports.py` come from fixed server-side lists or model fields. No reproduced SQL injection was found.
- `drill.want_regex` requires literal text and escapes it before compilation; the prior client-regex ReDoS path is closed.
- Admin routes require `SATF_ADMIN_TOKEN`; when unset they return 404, and comparisons use `hmac.compare_digest`.
- Report paths are rooted under the report ID and filenames are generated by the server. The file type is checked from magic bytes and the stored file is only served from an admin route. The upload-size finding concerns **when** bytes are parsed, not path traversal.
- Ordinary learner writes send `X-Learner`, which requires a CORS preflight cross-origin. The session-ID-only POST routes in SEC-03 are the notable cross-site write path because `/finish` accepts a bodyless form POST.
