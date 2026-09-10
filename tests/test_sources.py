"""Acceptance test: drive every template with its source item's own numbers
and check the engine lands on the official answer.

Also reports how many of College Board's own distractors the misconception
library reproduces -- the measure of whether the wrong options are modelled
or merely invented.
"""

from __future__ import annotations

import random
import sys

from satbank.sources import ALL


def norm(s: str) -> str:
    return (s.replace(",", "").replace(" ", "").replace("·", "*")
             .replace("×", "*").replace("−", "-"))


def main() -> int:
    key_ok = key_bad = 0
    dis_hit = dis_total = 0
    exact_sets = 0
    mcq = 0
    failures, notes = [], []

    for src in ALL:
        try:
            item = src.build(random.Random(0))
        except Exception as exc:                                    # noqa: BLE001
            failures.append(f"{src.id}: template raised {type(exc).__name__}: {exc}")
            key_bad += 1
            continue

        got = item.answer if item.fmt == "spr" else item.choices["ABCD".index(item.answer)]
        if norm(got) == norm(src.answer):
            key_ok += 1
        else:
            key_bad += 1
            failures.append(f"{src.id} ({src.cb_id}): official {src.answer!r}, engine {got!r}")

        if src.options and item.fmt == "mcq":
            mcq += 1
            official = {norm(o) for o in src.options}
            mine = {norm(c) for c in item.choices}
            dis_hit += len(official & mine)
            dis_total += len(official)
            if official == mine:
                exact_sets += 1
        if src.note:
            notes.append(f"  {src.id}: {src.note}")

    n = len(ALL)
    print(f"acceptance: {key_ok}/{n} official answers reproduced")
    print(f"option sets reproduced exactly: {exact_sets}/{mcq} multiple-choice items")
    print(f"official options matched: {dis_hit}/{dis_total} "
          f"({100*dis_hit//max(dis_total,1)}%) -- how much of College Board's own "
          f"distractor design the misconception library recreates")
    by_tier = {}
    for s in ALL:
        by_tier[s.tier] = by_tier.get(s.tier, 0) + 1
    print("source items by tier: " + ", ".join(f"{k}={v}" for k, v in by_tier.items()))
    if notes:
        print("\nnotes on source items:")
        print("\n".join(notes))
    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for f in failures:
            print("  " + f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
