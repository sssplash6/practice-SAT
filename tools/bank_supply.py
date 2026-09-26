"""Count distinct templates available in each topic, tier, and format cell.

Each generator is sampled at seeds 0-99. A template counts once in every cell
it actually produces; sampling more items does not inflate supply.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from satbank.item import ItemError  # noqa: E402
from satbank.registry import generate, templates, topic_of  # noqa: E402
from satbank.topic import load_topics  # noqa: E402

TIERS = ("easy", "medium", "hard")
FORMATS = ("mcq", "spr")


def survey(seeds: int = 100) -> dict[tuple[str, str, str], set[str]]:
    cells: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for name in templates():
        topic = topic_of(name)
        for seed in range(seeds):
            try:
                item = generate(name, seed, verify=False)
            except ItemError:
                continue
            if item.difficulty not in TIERS or item.fmt not in FORMATS:
                raise ValueError(f"{name} seed {seed}: unexpected cell {item.difficulty}/{item.fmt}")
            cells[topic, item.difficulty, item.fmt].add(name)
    return cells


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--json", action="store_true", help="print machine-readable cell counts")
    args = parser.parse_args()
    if args.seeds < 1:
        parser.error("--seeds must be positive")
    cells = survey(args.seeds)
    rows = [
        {"skill": topic, "tier": tier, "format": fmt,
         "count": len(cells.get((topic, tier, fmt), ())),
         "templates": sorted(cells.get((topic, tier, fmt), ()))}
        for topic in sorted(load_topics()) for tier in TIERS for fmt in FORMATS
    ]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        thin = sorted((r for r in rows if r["count"] < 3),
                      key=lambda r: (r["count"], r["skill"], r["tier"], r["format"]))
        print(f"{len(templates())} templates; {len(rows)} cells; {len(thin)} below 3")
        for row in thin:
            print(f"{row['skill']:<44} {row['tier']:<6} {row['format']:<3} "
                  f"{row['count']}/3  {', '.join(row['templates'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
