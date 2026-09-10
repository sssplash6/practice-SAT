"""CLI: satbank generate | verify | export"""

from __future__ import annotations

import argparse
import json
import random
import sys

from .registry import TEMPLATES, generate, generate_many


def item_json(it) -> dict:
    return {"template": it.template, "skill": it.skill, "difficulty": it.difficulty,
            "seed": it.seed, "stem": it.stem, "format": it.fmt, "choices": it.choices,
            "latex": it.latex_choices, "answer": it.answer, "rationale": it.rationale,
            "distractor_reasons": it.reasons, "figure": it.figure, "table": it.table}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="satbank")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="print generated items")
    g.add_argument("--n", type=int, default=5)
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--template", action="append", choices=list(TEMPLATES))
    g.add_argument("--json", action="store_true")
    g.add_argument("--hide-reasons", action="store_true")

    sub.add_parser("templates", help="list template names")

    e = sub.add_parser("export", help="write a pool of items as JSON")
    e.add_argument("--n", type=int, default=500)
    e.add_argument("--seed", type=int, default=0)
    e.add_argument("--out", required=True)

    a = ap.parse_args(argv)
    if a.cmd == "templates":
        for name in TEMPLATES:
            print(name)
        return 0
    if a.cmd == "generate":
        items = list(generate_many(a.n, a.seed, a.template))
        if a.json:
            print(json.dumps([item_json(i) for i in items], indent=2))
        else:
            for it in items:
                print(it.pretty(show_reasons=not a.hide_reasons))
                print()
        return 0
    items = list(generate_many(a.n, a.seed))
    with open(a.out, "w") as fh:
        json.dump([item_json(i) for i in items], fh)
    print(f"wrote {len(items)} items to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
