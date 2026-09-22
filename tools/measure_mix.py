"""Does a mixed set actually stop feeling repetitive?

Claiming it does is worthless; this measures it. For each topic it builds sixty
questions the scheduler's way and sixty the obvious way -- draw a template at
random, draw a seed at random -- and counts how often the set repeats itself.

What is counted, per feature (template, opening words, skill, difficulty,
format):

  runs    the longest stretch of consecutive questions that share it
  adj     how many neighbouring pairs share it, as a percentage
  uniq    how many distinct values appeared across the sixty

    PYTHONPATH=. python3 tools/measure_mix.py
    PYTHONPATH=. python3 tools/measure_mix.py --topic probability --n 60
"""

from __future__ import annotations

import argparse
import random
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 2)[0])

from satbank.item import ItemError                        # noqa: E402
from satbank.registry import generate                     # noqa: E402
from server import practice                               # noqa: E402

FEATURES = ("template", "opening", "skill", "difficulty", "fmt")


def naive(topic: str, n: int, rng: random.Random) -> list[practice.Card]:
    """The obvious way: a template at random, a seed at random."""
    pool = practice.catalogue()["by_topic"][topic]
    out, seen = [], set()
    while len(out) < n and len(seen) < n * 60:
        key = rng.choice(pool)
        seed = rng.randrange(100_000)
        if (key, seed) in seen:
            continue
        seen.add((key, seed))
        try:
            out.append(practice.Card.of(key, seed, generate(key, seed), topic))
        except ItemError:
            continue
    return out


def stats(cards: list[practice.Card]) -> dict:
    out = {}
    for f in FEATURES:
        vals = [c.feats[f] for c in cards]
        run = best = 1
        adj = 0
        for i in range(1, len(vals)):
            if vals[i] == vals[i - 1]:
                run += 1
                adj += 1
            else:
                run = 1
            best = max(best, run)
        out[f] = {
            "run": best,
            "adj": round(100 * adj / max(1, len(vals) - 1)),
            "uniq": len(set(vals)),
        }
    out["distinct_stems"] = len({c.item.stem for c in cards})
    return out


def line(label: str, s: dict, n: int) -> str:
    bits = "  ".join(
        f"{f[:4]}: run {s[f]['run']:>2}  adj {s[f]['adj']:>3}%  uniq {s[f]['uniq']:>2}"
        for f in FEATURES
    )
    return f"  {label:<10} {bits}   stems {s['distinct_stems']}/{n}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", help="just this one")
    ap.add_argument("--n", type=int, default=60)
    a = ap.parse_args()

    cat = practice.catalogue()
    topics = [a.topic] if a.topic else sorted(cat["by_topic"])
    rng = random.Random(7)

    worst = []
    for topic in topics:
        pool = cat["by_topic"][topic]
        t0 = time.perf_counter()
        mixed = practice.build({topic: a.n}, learner="measure")
        ms = (time.perf_counter() - t0) * 1000
        plain = naive(topic, a.n, rng)

        sm, sp = stats(mixed), stats(plain)
        print(f"\n{topic}  ({len(pool)} templates, {len(mixed)} built in {ms:.0f} ms)")
        print(line("scheduled", sm, a.n))
        print(line("random", sp, a.n))
        worst.append((sm["template"]["run"], sm["opening"]["adj"], topic))

    worst.sort(reverse=True)
    print("\nworst scheduled runs of one template:")
    for run, adj, topic in worst[:5]:
        print(f"  {topic:42} run {run}, {adj}% of neighbours share an opening")
    return 0


if __name__ == "__main__":
    sys.exit(main())
