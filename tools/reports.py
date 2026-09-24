"""Reports from the command line (R17): the same table and the same functions
as /admin/reports, for whoever answers them from a terminal.

    PYTHONPATH=. python3 tools/reports.py list [--status new] [--category key_wrong] [--limit 30]
    PYTHONPATH=. python3 tools/reports.py show 123
    PYTHONPATH=. python3 tools/reports.py reply 123 "Fixed, thanks." [--status fixed] [--note "Figure redrawn"]
    PYTHONPATH=. python3 tools/reports.py status 123 checking
    PYTHONPATH=. python3 tools/reports.py key 123 right|wrong [--since 2026-09-01] [--reply "..."]
    PYTHONPATH=. python3 tools/reports.py item circles.central_angle 88213
    PYTHONPATH=. python3 tools/reports.py stop circles.central_angle [SEED] [--note "..."]
    PYTHONPATH=. python3 tools/reports.py release circles.central_angle [SEED]
    PYTHONPATH=. python3 tools/reports.py labels

`key wrong` disputes every learner's attempts on the reported seed, or with
--since on every seed of the template answered since that date, and re-scores
their sittings. SATF_DB picks the database, as it does for the server.
"""

from __future__ import annotations

import argparse
import json
import sys

from server import db, reports


def _line(r: dict) -> str:
    flags = " ".join(x for x in (
        "BROKEN" if r["check"] == "broken" else "",
        f"SIGNAL {r['signal']}" if r["signal"] else "",
        "dispute" if r["dispute"] else "", "awaiting" if r["awaiting"] else "",
        "pending" if r["pending"] else "", f"+{r['children']} me too" if r["children"] else "",
        f"{r['files']} files" if r["files"] else "") if x)
    head = f"#{r['id']:<5} {r['date']:>6}  {r['status']:<9} {r['category']:<11} {r['context_chip'][:28]:<28}"
    tail = f"\n        {r['summary'][:90]}" + (f"   [{flags}]" if flags else "")
    if r["template"]:
        tail += f"\n        tools/reports.py item {r['template']} {r['seed']}"
    return head + tail


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Answer SAT Freshman reports from the terminal.")
    sub = p.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list", help="open reports, those waiting for a person first")
    ls.add_argument("--status", choices=sorted(reports.STATUSES))
    ls.add_argument("--category")
    ls.add_argument("--template")
    ls.add_argument("--limit", type=int, default=30)
    ls.add_argument("--json", action="store_true")
    sh = sub.add_parser("show", help="one report, with the item regenerated")
    sh.add_argument("id", type=int)
    rp = sub.add_parser("reply", help="reply (the student sees it under Settings › Your reports)")
    rp.add_argument("id", type=int)
    rp.add_argument("text")
    rp.add_argument("--status", choices=sorted(reports.STATUSES))
    rp.add_argument("--note", help="the one line Help › Fixed shows")
    st = sub.add_parser("status", help="set a status")
    st.add_argument("id", type=int)
    st.add_argument("status", choices=sorted(reports.STATUSES))
    ky = sub.add_parser("key", help="decide a key dispute")
    ky.add_argument("id", type=int)
    ky.add_argument("verdict", choices=("right", "wrong"))
    ky.add_argument("--since", help="wrong on every seed of the template since this date (YYYY-MM-DD)")
    ky.add_argument("--reply")
    it = sub.add_parser("item", help="regenerate an item, key included")
    it.add_argument("template")
    it.add_argument("seed", type=int)
    for name, what in (("stop", "stop serving a seed, or the whole template"), ("release", "serve it again")):
        q = sub.add_parser(name, help=what)
        q.add_argument("template")
        q.add_argument("seed", type=int, nargs="?")
        q.add_argument("--note", default="")
    sub.add_parser("labels", help="mistake labels students dispute most (V6)")
    a = p.parse_args(argv)

    db.init()
    show = lambda x: print(json.dumps(x, indent=2, ensure_ascii=False, default=str))  # noqa: E731
    if a.cmd == "list":
        got = reports.admin_list(status=a.status, category=a.category, template=a.template, limit=a.limit)
        if a.json:
            show(got)
            return 0
        print(f"mail: {got['mail']}  ·  " + "  ".join(f"{reports.STATUSES[k]} {v}" for k, v in got["counts"].items()))
        if got["flagged"]:
            print("\nWaiting for a person")
            for r in got["flagged"]:
                print(_line(r))
        print("\nNewest")
        for r in got["items"]:
            print(_line(r))
    elif a.cmd == "show":
        show(reports.admin_detail(a.id))
    elif a.cmd == "reply":
        show(reports.resolve(a.id, reports.AdminPut(reply=a.text, status=a.status, fixed_note=a.note)))
    elif a.cmd == "status":
        show(reports.resolve(a.id, reports.AdminPut(status=a.status)))
    elif a.cmd == "key":
        body = reports.AdminPut(dispute_outcome=f"key_{a.verdict}", reply=a.reply,
                                status="fixed" if a.verdict == "wrong" else "no_change",
                                scope="template" if a.since else "one", since=a.since)
        show(reports.resolve(a.id, body))
    elif a.cmd == "item":
        show(reports.question(a.template, a.seed))
    elif a.cmd == "stop":
        reports.quarantine(a.template, a.seed, a.note)
        print(f"stopped serving {a.template}" + (f" seed {a.seed}" if a.seed is not None else " (every seed)"))
    elif a.cmd == "release":
        print("released" if reports.release(a.template, a.seed) else "it wasn't stopped")
    elif a.cmd == "labels":
        for r in reports.admin_labels():
            mark = "!" if r["flagged"] else " "
            print(f"{mark} {r['rate']:>5.0%}  {r['disputed']:>3}/{r['learners']:<4} {r['template']}  {r['reason'] or r['norm']}")
    return 0


if __name__ == "__main__":
    from fastapi import HTTPException
    try:
        sys.exit(main())
    except HTTPException as e:
        sys.exit(f"{e.status_code}: {e.detail}")
