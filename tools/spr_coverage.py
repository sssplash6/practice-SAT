"""How many grid-in templates name the mistake behind a wrong typed answer.

A template counts as a grid-in template when any of seeds 0-40 makes an spr
item, drawn as it draws itself and again with fmt="spr" where it takes one. It
names its mistakes when one of those grid-ins carries `spr_mistakes`.

    PYTHONPATH=. python3 tools/spr_coverage.py
"""

from __future__ import annotations

import sys
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 2)[0])

from satbank.item import ItemError                        # noqa: E402
from satbank.registry import generate, templates, topic_of  # noqa: E402

SEEDS = range(41)


def grid_ins(name: str):
    forced = True
    for seed in SEEDS:
        try:
            it = generate(name, seed)
        except ItemError:
            it = None
        if it is not None and it.fmt == "spr":
            yield it
        if forced:
            try:
                it = generate(name, seed, fmt="spr")
            except TypeError:           # the template takes no fmt
                forced = False
                continue
            except ItemError:
                continue
            if it.fmt == "spr":
                yield it


def main() -> int:
    named, without = defaultdict(list), defaultdict(list)
    for name in templates():
        items = list(grid_ins(name))
        if items:
            (named if any(it.spr_mistakes for it in items) else without)[
                topic_of(name)].append(name)
    n = sum(map(len, named.values()))
    total = n + sum(map(len, without.values()))
    print(f"{n} of {total} grid-in templates name their mistakes")
    for slug in sorted(named.keys() | without.keys()):
        print(f"  {slug:<44}{len(named[slug])} of {len(named[slug]) + len(without[slug])}")
    print("still without:")
    for slug in sorted(without):
        for name in without[slug]:
            print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
