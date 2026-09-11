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


def capacity(draws: int) -> int:
    """How many distinct items each template can actually produce.

    A template whose count is still climbing when sampling stops is reported
    with a "+": that figure is a floor, not a total.
    """
    from .item import ItemError
    everything = {}
    print(f"{'template':<34}{'distinct':>10}   sampled {draws:,} times")
    print("-" * 62)
    for name in TEMPLATES:
        seen, quarter = set(), None
        for seed in range(draws):
            try:
                it = generate(name, seed)
            except ItemError:
                continue
            sig = (it.stem, it.figure, it.answer)
            seen.add(sig)
            everything[hash(sig)] = True
            if seed == draws // 4 - 1:
                quarter = len(seen)
        growing = bool(quarter and len(seen) > quarter * 1.15)
        print(f"{name:<34}{len(seen):>10,}   {'still growing' if growing else 'exhausted'}")
    print("-" * 62)
    print(f"{'distinct overall':<34}{len(everything):>10,}")
    return 0


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

    c = sub.add_parser("capacity", help="count the distinct items each template can make")
    c.add_argument("--draws", type=int, default=20000)

    e = sub.add_parser("export", help="write a pool of items as JSON")
    e.add_argument("--n", type=int, default=500)
    e.add_argument("--seed", type=int, default=0)
    e.add_argument("--out", required=True)

    a = ap.parse_args(argv)
    if a.cmd == "capacity":
        return capacity(a.draws)
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
