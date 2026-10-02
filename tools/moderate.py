"""Paper discussion moderation (X21, §3.1 item 73): the site operator who reads
SATF_REPORTS_TO runs it. SATF_DB picks the database, as it does for the server.

    PYTHONPATH=. python3 tools/moderate.py list [--all]      reported posts (pending by default)
    PYTHONPATH=. python3 tools/moderate.py --pending         exit 1 while any report waits (launch check)
    PYTHONPATH=. python3 tools/moderate.py hide 42           hide a post (and mark it reviewed)
    PYTHONPATH=. python3 tools/moderate.py restore 42        show it again (and mark it reviewed)
    PYTHONPATH=. python3 tools/moderate.py mute a:abc123     that code's new posts are hidden
    PYTHONPATH=. python3 tools/moderate.py unmute a:abc123

Three reports from different codes hide a post on their own; a moderator's
hide or restore settles it, so it leaves the pending list.
"""

from __future__ import annotations

import argparse
import sys

from server import db, papers


def _line(r: dict) -> str:
    state = "hidden" if r["hidden"] else "shown"
    return (f"#{r['id']:<5} paper {r['paper']:<4} {r['reports']} reports  {state:<6} {r['at'][:16]}  "
            f"{r['learner']}  {r['name'] or ''}\n        {(r['text'] or '')[:160]}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="moderate paper discussion posts")
    ap.add_argument("--pending", action="store_true", help="list pending reports; exit 1 if any")
    sub = ap.add_subparsers(dest="cmd")
    ls = sub.add_parser("list")
    ls.add_argument("--all", action="store_true", help="every reported post, reviewed ones too")
    for name in ("hide", "restore"):
        sub.add_parser(name).add_argument("post", type=int)
    for name in ("mute", "unmute"):
        sub.add_parser(name).add_argument("code")
    args = ap.parse_args(argv)
    db.init()
    if args.pending or args.cmd in (None, "list"):
        rows = papers.reported(pending_only=not getattr(args, "all", False))
        for r in rows:
            print(_line(r))
        print(f"{len(rows)} {'reported' if getattr(args, 'all', False) else 'pending'}")
        return 1 if args.pending and rows else 0
    if args.cmd in ("hide", "restore"):
        ok = (papers.hide if args.cmd == "hide" else papers.restore)(args.post)
        print(f"{args.cmd} #{args.post}: {'done' if ok else 'no such post'}")
        return 0 if ok else 1
    papers.mute(args.code, on=args.cmd == "mute")
    print(f"{args.cmd}d {args.code}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
