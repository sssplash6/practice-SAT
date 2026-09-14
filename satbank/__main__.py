"""CLI: satbank generate | templates | topics | check | capacity | export"""

from __future__ import annotations

import argparse
import json
import random
import sys

from .registry import generate, generate_many, templates, topic_of
from .topic import load_topics


def item_json(it) -> dict:
    return {"template": it.template, "skill": it.skill, "difficulty": it.difficulty,
            "seed": it.seed, "stem": it.stem, "format": it.fmt, "choices": it.choices,
            "latex": it.latex_choices, "answer": it.answer, "rationale": it.rationale,
            "distractor_reasons": it.reasons, "figure": it.figure, "table": it.table}


def capacity(draws: int, topics: list[str] | None = None) -> int:
    """How many distinct items each template can actually produce.

    A template whose count is still climbing when sampling stops is reported
    with a "+": that figure is a floor, not a total.
    """
    from .item import ItemError
    everything = {}
    names = [n for n in templates() if not topics or topic_of(n) in topics]
    print(f"{'template':<34}{'distinct':>10}   sampled {draws:,} times")
    print("-" * 62)
    for name in names:
        seen, quarter = set(), None
        for seed in range(draws):
            try:
                it = generate(name, seed)
            except ItemError:
                continue
            sig = (it.stem, it.figure, it.answer, str(it.table))
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
    g.add_argument("--template", action="append")
    g.add_argument("--topic", action="append")
    g.add_argument("--json", action="store_true")
    g.add_argument("--hide-reasons", action="store_true")

    t = sub.add_parser("templates", help="list template names")
    t.add_argument("--topic", action="append")

    sub.add_parser("topics", help="list topics, with what each one covers")

    k = sub.add_parser("check", help="run the quality gate over a topic, or all of them")
    k.add_argument("--topic", action="append")
    k.add_argument("--per-template", type=int, default=300,
                   help="items generated per template for the audit pass")
    k.add_argument("--draws", type=int, default=1200, help="draws for the capacity floor")
    k.add_argument("--quick", action="store_true", help="a fast pass while iterating")
    k.add_argument("--quiet", action="store_true", help="print only what fails")

    c = sub.add_parser("capacity", help="count the distinct items each template can make")
    c.add_argument("--draws", type=int, default=20000)
    c.add_argument("--topic", action="append")

    e = sub.add_parser("export", help="write a pool of items as JSON")
    e.add_argument("--n", type=int, default=500)
    e.add_argument("--seed", type=int, default=0)
    e.add_argument("--out", required=True)

    a = ap.parse_args(argv)
    if a.cmd == "check":
        from .check import check_all
        return check_all(a.topic, a.per_template, a.draws, a.quick, not a.quiet)
    if a.cmd == "topics":
        from .topic import key_file
        print(f"{'topic':<40}{'templates':>10}{'sources':>9}{'official':>10}  domain")
        for slug, t in sorted(load_topics().items()):
            n = len(key_file(slug)["items"])
            print(f"{t.name:<40}{len(t.templates):>10}{len(t.sources):>9}{n:>10}  {t.domain}")
        return 0
    if a.cmd == "capacity":
        return capacity(a.draws, a.topic)
    if a.cmd == "templates":
        for name in templates():
            if not a.topic or topic_of(name) in a.topic:
                print(f"{name:<34}{topic_of(name)}")
        return 0
    if a.cmd in ("generate", "export") and getattr(a, "template", None):
        unknown = [t for t in a.template if t not in templates()]
        if unknown:
            near = [n for n in templates()
                    if any(u.split(".")[-1] in n or n.split(".")[-1] in u for u in unknown)]
            print(f"no such template: {', '.join(unknown)}"
                  + (f"\ndid you mean: {', '.join(near[:5])}?" if near else
                     "\nrun `satbank templates` to list them"), file=sys.stderr)
            return 2
    if a.cmd == "generate":
        items = list(generate_many(a.n, a.seed, a.template, a.topic))
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
