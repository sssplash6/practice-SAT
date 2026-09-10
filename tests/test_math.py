"""Mathematical audit at volume: re-derive every generated answer independently.

Distinct from test_fuzz.py, which checks an item's *shape* (four options, sorted,
key marked). This checks the item is *right*.
"""

from __future__ import annotations

import sys
from collections import Counter

from satbank.audit import AuditError, audit
from satbank.item import ItemError
from satbank.registry import TEMPLATES, generate


def main(per: int = 1500) -> int:
    checked = Counter()
    failures = []
    for name in TEMPLATES:
        for seed in range(per):
            try:
                item = generate(name, seed)
            except ItemError:
                continue
            try:
                audit(item)
                checked[name] += 1
            except AuditError as exc:
                failures.append(f"{name} seed={seed}: {exc}")

    total = sum(checked.values())
    print(f"independently re-derived {total:,} answers across {len(TEMPLATES)} templates")
    print(f"disagreements: {len(failures)}")
    thin = [n for n in TEMPLATES if checked[n] == 0]
    if thin:
        print("templates never audited: " + ", ".join(thin))
    if failures:
        print(f"\nFAILURES (first 15 of {len(failures)}):")
        for f in failures[:15]:
            print("  " + f)
    return 1 if failures or thin else 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 1500))
