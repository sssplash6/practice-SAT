"""Structural validation over a large random sample of generated items.

Every check here is something that, left unchecked, makes a generated item
detectably fake or outright wrong.
"""

from __future__ import annotations

import re
import sys
from collections import Counter

from satbank.item import ItemError
from satbank.registry import TEMPLATES, generate

BAD_TEXT = re.compile(r"None|\{|\}|  +|inchs|foots|\bof the a\b")


def validate(it) -> list[str]:
    errs = []
    if it.fmt == "mcq":
        if len(it.choices) != 4:
            errs.append("not 4 options")
        if len(set(it.choices)) != len(it.choices):
            errs.append(f"duplicate options {it.choices}")
        if it.answer not in "ABCD":
            errs.append(f"bad answer letter {it.answer!r}")
        vals = [c for c in it.choices if re.fullmatch(r"-?[\d,]+(\.\d+)?", c)]
        if len(vals) == len(it.choices):
            nums = [float(c.replace(",", "")) for c in it.choices]
            if nums != sorted(nums):
                errs.append(f"numeric options not ascending: {it.choices}")
            if any(n <= 0 for n in nums):
                errs.append(f"non-positive option: {it.choices}")
        if len(it.reasons) != len(it.choices):
            errs.append("reason list misaligned")
        elif sum(1 for r in it.reasons if r == "") != 1:
            errs.append("key not uniquely marked")
    else:
        if not it.answer or it.answer in ("None", ""):
            errs.append("empty grid-in answer")
        if not re.fullmatch(r"-?\d+(\.\d+)?(/\d+)?", it.answer):
            errs.append(f"grid-in not enterable: {it.answer!r}")
    if not it.stem.strip().endswith("?"):
        errs.append("stem does not end in a question")
    if BAD_TEXT.search(it.stem):
        errs.append(f"malformed stem text: {it.stem[:90]!r}")
    if it.figure and not (it.figure.startswith("<svg") and it.figure.endswith("</svg>")):
        errs.append("malformed figure")
    if not it.rationale.strip():
        errs.append("missing rationale")
    return errs


def main() -> int:
    per = 400
    total = fails = 0
    filler = Counter()
    stems = {}
    problems = []
    for name in TEMPLATES:
        seen = set()
        for seed in range(per):
            try:
                it = generate(name, seed)
            except ItemError as exc:
                problems.append(f"{name} seed={seed}: {exc}")
                fails += 1
                continue
            total += 1
            seen.add((it.stem, it.figure, it.answer))
            errs = validate(it)
            if errs:
                fails += 1
                if len(problems) < 12:
                    problems.append(f"{name} seed={seed}: {'; '.join(errs)}")
            for r in it.reasons:
                if r:
                    filler[r == "near-miss arithmetic slip"] += 1
        stems[name] = len(seen)

    print(f"generated and validated {total} items across {len(TEMPLATES)} templates")
    print(f"failures: {fails}")
    modelled = filler[False]
    generic = filler[True]
    print(f"distractors traced to a named misconception: {modelled}/{modelled+generic} "
          f"({100*modelled//max(modelled+generic,1)}%)")
    thin = {k: v for k, v in stems.items() if v < per * 0.5}
    print(f"distinct items per template (out of {per}): "
          f"min={min(stems.values())}, median={sorted(stems.values())[len(stems)//2]}, "
          f"max={max(stems.values())}")
    if thin:
        print("templates with a small parameter space: " +
              ", ".join(f"{k}={v}" for k, v in sorted(thin.items(), key=lambda t: t[1])))
    if problems:
        print("\nproblems:")
        for p in problems[:12]:
            print("  " + p)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
