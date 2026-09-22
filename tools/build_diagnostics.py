"""Build the ten diagnostic forms.

A diagnostic is twenty questions: four domains, and from each of them one easy,
two medium and two hard. That is deliberately not the exam blueprint --
the real test weights Algebra and Advanced Math at 35% each against 15% for
the other two. A diagnostic is trying to measure four things, not to predict
one, so it spends its questions evenly.

The forms are fixed and built ahead of time rather than drawn per student.
Drawing live would hit the repeat the README warns about -- distinct seeds
collide onto identical parameters, and Area and Volume repeated 25 stems in
1,000 items -- and would make one student's result unreproducible. Ten forms
built once, checked for duplicates across all 200 questions, and handed out at
random cost nothing to serve and can be looked at before anyone sits them.

    PYTHONPATH=. python3 tools/build_diagnostics.py
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import random
import sys

from satbank.item import ItemError
from satbank.registry import generate, templates, topic_of
from satbank.topic import load_topics

FORMS = 10
# Two hard per domain, not one. A single hard question is a coin toss, and the
# top of the range is exactly where a diagnostic has to separate people.
PER_DOMAIN = ("easy", "medium", "medium", "hard", "hard")
DOMAINS = (
    "Algebra",
    "Advanced Math",
    "Problem-Solving and Data Analysis",
    "Geometry and Trigonometry",
)
SEEDS_PER_TEMPLATE = 45
OUT = pathlib.Path(__file__).resolve().parent.parent / "server" / "forms.json"


def signature(it) -> tuple:
    """What makes two items the same question. Matches `satbank capacity`."""
    return (it.stem, it.figure, it.answer, str(it.table))


def build_pool(log=print) -> dict:
    """Generate across every template and file the results by domain and tier."""
    names = templates()                       # also warms the lazy globals
    topics = load_topics()
    domain_of = {n: topics[topic_of(n)].domain for n in names}

    pool: dict[tuple[str, str], list] = {}
    seen: set[tuple] = set()
    made = failed = 0

    for n in sorted(names):
        dom = domain_of[n]
        for seed in range(SEEDS_PER_TEMPLATE):
            try:
                it = generate(n, seed)
            except ItemError:
                failed += 1
                continue
            sig = signature(it)
            if sig in seen:                   # the seed collision, dropped here
                continue
            seen.add(sig)
            made += 1
            pool.setdefault((dom, it.difficulty), []).append(
                {
                    "key": n,
                    "seed": seed,
                    "topic": topic_of(n),
                    "topic_name": topics[topic_of(n)].name,
                    "domain": dom,
                    "difficulty": it.difficulty,
                    "type": it.fmt,
                    "stem": it.stem,
                    "choices": list(it.choices),
                    "latex": list(it.latex_choices),
                    "figure": it.figure,
                    "table": it.table,
                    "answer": it.answer,
                    "rationale": it.rationale,
                    "reasons": list(it.reasons),
                }
            )

    log(f"pool: {made} distinct items, {failed} seeds refused")
    for dom in DOMAINS:
        row = "  ".join(f"{d}={len(pool.get((dom, d), [])):4d}" for d in ("easy", "medium", "hard"))
        log(f"  {dom:36} {row}")
    return pool


def deal(pool: dict, rng: random.Random, log=print) -> list[list[dict]]:
    """Hand out the forms, spreading topics and never repeating a question."""
    # shuffle each bucket once, then deal off the top, preferring a topic this
    # form has not used yet so a student does not get four Circles questions
    buckets = {k: v[:] for k, v in pool.items()}
    for v in buckets.values():
        rng.shuffle(v)

    used: set[tuple[str, int]] = set()
    # A stem can recur across templates with a different figure behind it, which
    # is a fair question but reads as a repeat. Ten forms out of seventeen
    # thousand items can afford to never show the same sentence twice.
    used_stems: set[str] = set()
    forms: list[list[dict]] = []

    for f in range(FORMS):
        picked: list[dict] = []
        topics_here: set[str] = set()
        for dom in DOMAINS:
            for tier in PER_DOMAIN:
                bucket = buckets.get((dom, tier), [])

                def free(c):
                    return (c["key"], c["seed"]) not in used and c["stem"] not in used_stems

                choice = None
                # first pass: a topic this form has not touched
                for i, cand in enumerate(bucket):
                    if free(cand) and cand["topic"] not in topics_here:
                        choice = bucket.pop(i)
                        break
                if choice is None:                  # second pass: any unused item
                    for i, cand in enumerate(bucket):
                        if free(cand):
                            choice = bucket.pop(i)
                            break
                if choice is None:
                    raise SystemExit(
                        f"form {f + 1}: nothing left for {dom} / {tier}. "
                        f"Raise SEEDS_PER_TEMPLATE."
                    )
                used.add((choice["key"], choice["seed"]))
                used_stems.add(choice["stem"])
                topics_here.add(choice["topic"])
                picked.append(choice)

        # the real test runs a module easiest to hardest, so this does too
        order = {"easy": 0, "medium": 1, "hard": 2}
        picked.sort(key=lambda q: order[q["difficulty"]])
        for i, q in enumerate(picked, 1):
            q["id"] = f"f{f + 1}q{i:02d}"
        forms.append(picked)
        log(f"  form {f + 1:2d}: {len(picked)} questions, "
            f"{len({q['topic'] for q in picked})} topics, "
            f"{sum(1 for q in picked if q['type'] == 'spr')} grid-in, "
            f"{sum(1 for q in picked if q['figure'])} with a figure")

    return forms


def check(forms: list[list[dict]]) -> None:
    """Refuse to ship a set that repeats a question or misses the blueprint."""
    stems: dict[str, str] = {}
    for f, form in enumerate(forms, 1):
        assert len(form) == len(DOMAINS) * len(PER_DOMAIN), f"form {f} is the wrong length"
        for dom in DOMAINS:
            got = sorted(q["difficulty"] for q in form if q["domain"] == dom)
            assert got == sorted(PER_DOMAIN), f"form {f} {dom}: {got}"
        for q in form:
            assert q["stem"] not in stems, f"form {f} repeats a stem from {stems[q['stem']]}"
            stems[q["stem"]] = f"form {f}"
            if q["type"] == "mcq":
                assert len(q["choices"]) == 4, f"{q['id']} has {len(q['choices'])} choices"
                assert q["answer"] in "ABCD", f"{q['id']} keyed {q['answer']!r}"
            else:
                assert q["choices"] == [], f"{q['id']} is spr but carries choices"
                assert q["answer"], f"{q['id']} has no answer"
    print(f"checked: {len(stems)} questions, all distinct, blueprint holds")


def main() -> int:
    rng = random.Random(20260922)          # the forms are reproducible on purpose
    pool = build_pool()
    print("dealing:")
    forms = deal(pool, rng)
    check(forms)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(
        {
            "built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "blueprint": {"domains": list(DOMAINS), "per_domain": list(PER_DOMAIN)},
            "forms": [{"id": i + 1, "questions": qs} for i, qs in enumerate(forms)],
        },
        ensure_ascii=False, indent=1))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
