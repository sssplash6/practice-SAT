"""Seed item_ratings priors for every (template, tier) before launch (review.md V15).

    SATF_DB=server/v2.db PYTHONPATH=. python3 tools/seed_ratings.py

Idempotent: a pair that has answers keeps its own rating, and a second run
writes the same priors. Prints the level histogram and fails unless each of
L1-L7 holds at least 5% of the types.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from server import db, ratings  # noqa: E402


def main() -> int:
    db.init()
    before = [tuple(r) for r in db.rows("SELECT template,tier,rating,n FROM item_ratings ORDER BY template,tier")]
    ratings.write_priors()
    after = [tuple(r) for r in db.rows("SELECT template,tier,rating,n FROM item_ratings ORDER BY template,tier")]
    hist = ratings.histogram()
    for level, share in hist.items():
        print(f"L{level}  {100 * share:5.1f}%  {'#' * round(60 * share)}")
    print(f"{len(after)} types, {sum(1 for a, b in zip(before, after) if a != b) if before else len(after)} changed")
    ok = all(share >= 0.05 for share in hist.values())
    print("every level holds at least 5% of types" if ok else "a level holds under 5% of types")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
