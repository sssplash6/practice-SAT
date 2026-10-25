"""Build the Reading and Writing diagnostic forms (server/forms_rw.json).

The same shape as the Math diagnostic (tools/build_diagnostics.py): twenty
questions, five per domain, one easy, two medium and two hard in each, fixed
ahead of time and handed out at random. Inside a domain the five go to its
skills by the College Board Question Bank weights (blueprint.skill_counts), and
the form runs in Bluebook's order: domain by domain, skill by skill, easiest to
hardest inside each. No item appears on two forms, and a form takes each
template once where the skill has enough of them.

    PYTHONPATH=. python3 tools/build_rw_forms.py
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import random
import sys

from server import blueprint, practice

FORMS = 10
FIRST_ID = 101                      # Math forms are 1-10; one FORMS dict holds both
PER_DOMAIN = ("easy", "medium", "medium", "hard", "hard")
OUT = pathlib.Path(__file__).resolve().parent.parent / "server" / "forms_rw.json"
RANK = {"easy": 0, "medium": 1, "hard": 2}


def pool() -> dict[tuple[str, str], list[practice.Card]]:
    """Every R&W item once, by (skill topic, tier). An R&W template's items are fixed and its
    seed is an index (seed % n), so walking seeds until one repeats lists them all."""
    out: dict[tuple[str, str], list[practice.Card]] = {}
    for topic in blueprint.RW_ORDER:
        for t in practice.catalogue()["by_topic"][topic]:
            seen = set()
            for seed in range(400):
                card = practice.Card.of(t, seed, practice.generate(t, seed), topic)
                h = practice.question_hash(card.item)
                if h in seen:
                    break
                seen.add(h)
                out.setdefault((topic, card.item.difficulty), []).append(card)
    return out


def slots() -> list[tuple[str, str]]:
    """(skill, tier) per position: each domain's ladder dealt over its skills, as blueprint.slots does."""
    domains = {practice.catalogue()["topics"][t].domain for t in blueprint.RW_ORDER}
    counts = blueprint.skill_counts({d: len(PER_DOMAIN) for d in domains})
    out = []
    for d in sorted(domains):
        skills = {s: n for s, n in counts.items() if practice.catalogue()["topics"][s].domain == d}
        out += zip(blueprint.spread(skills), PER_DOMAIN)
    return sorted(out, key=lambda st: (blueprint.RW_ORDER.index(st[0]), RANK[st[1]]))


def main() -> int:
    rng = random.Random(20261022)          # reproducible, like the Math forms
    items = pool()
    for v in items.values():
        rng.shuffle(v)
    used: set[str] = set()
    forms = []
    for f in range(FORMS):
        fid = FIRST_ID + f
        picked, here = [], set()
        for skill, tier in slots():
            bucket = [c for c in items[(skill, tier)] if practice.question_hash(c.item) not in used]
            card = next((c for c in bucket if c.key not in here), None) or (bucket[0] if bucket else None)
            if card is None:
                raise SystemExit(f"form {fid}: nothing left for {skill} / {tier}")
            used.add(practice.question_hash(card.item))
            here.add(card.key)
            picked.append(card)
        qs = [dict(practice.to_question(c, i), id=f"f{fid}q{i:02d}") for i, c in enumerate(picked, 1)]
        for d in {q["domain"] for q in qs}:
            assert sorted(q["difficulty"] for q in qs if q["domain"] == d) == sorted(PER_DOMAIN), (fid, d)
        assert all(q["type"] == "mcq" and len(q["choices"]) == 4 and q["text"] for q in qs), fid
        forms.append({"id": fid, "questions": qs})
        print(f"  form {fid}: {len(qs)} questions, {len(here)} templates")
    OUT.write_text(json.dumps({
        "built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "blueprint": {"subject": "rw", "per_domain": list(PER_DOMAIN)}, "forms": forms},
        ensure_ascii=False, indent=1))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
