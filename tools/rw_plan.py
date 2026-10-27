"""Quotas for growing the authored Reading and Writing bank to TOTAL items.

Domains get their share of the test (material/cb/specs.json); within a domain,
skills get their share of the College Board question bank (cb_index.json); each
skill keeps the bank's tier mix with no tier under 15%; within a tier, templates
get their share of the official items of that tier (plan.templates in satbank/rw).
Quotas per wave are what still has to be written, spread evenly over the waves left.

    python3 tools/rw_plan.py              # targets, items so far, wave 1 quotas
    python3 tools/rw_plan.py 2 --json     # wave 2 quotas as JSON for the wave brief
    python3 tools/rw_plan.py 5 --pending w4   # counts w4's unpromoted planned cells as written
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOTAL, WAVES, FLOOR = 5000, 5, 0.15
TIERS = ("easy", "medium", "hard")


def slug(skill: str) -> str:
    return skill.strip().lower().replace(",", "").replace("-", "_").replace(" ", "_")


def spread(total: int, weights: dict) -> dict:
    """Largest-remainder split of total in proportion to weights."""
    s = sum(weights.values())
    raw = {k: total * w / s for k, w in weights.items()}
    out = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: out[k] - raw[k])[:total - sum(out.values())]:
        out[k] += 1
    return out


def targets() -> dict[str, dict[str, int]]:
    specs = json.load(open(os.path.join(ROOT, "material/cb/specs.json")))["domains"]["rw"]
    bank = defaultdict(Counter)
    for it in json.load(open(os.path.join(ROOT, "material/cb/cb_index.json")))["items"].values():
        if it["subject"] == "rw":
            bank[slug(it["skill"])][it["tier"]] += 1
    out = {}
    domains = spread(TOTAL, {d["name"]: d["question_share_percent_approx"] for d in specs})
    for d in specs:
        skills = spread(domains[d["name"]], {slug(s): sum(bank[slug(s)].values()) for s in d["skills"]})
        for s, n in skills.items():
            mix = {t: max(bank[s][t] / sum(bank[s].values()), FLOOR) for t in TIERS}
            out[s] = spread(n, mix)
    return out


def bank() -> tuple[dict, Counter]:
    """Official item counts per (skill, template, tier), and authored items per (skill, template, tier)."""
    official, have = defaultdict(Counter), Counter()
    for p in glob.glob(os.path.join(ROOT, "satbank/rw/*.json")):
        d = json.load(open(p))
        for t in d["plan"]["templates"]:
            for tier, ids in t.get("official_tiers", {}).items():     # band-7 parts carry no official map
                official[(d["slug"], tier)][t["code"]] += len(ids)
        for it in d["items"]:
            have[(d["slug"], it["template"], it["tier"])] += 1
    return official, have


def pending(w: str) -> Counter:
    """Planned cells of wave w's batches that are not promoted yet, so the next wave can be planned while w finishes."""
    st = json.loads(subprocess.run(["python3", "spec/rw/waves/scripts/wave_status.py", "--json"], cwd=ROOT,
                                   env={**os.environ, "WAVE": w}, capture_output=True, text=True, check=True).stdout)
    open_ = {r["batch"] for r in st if r["stage"] != "promoted"}
    out = Counter()
    for s, batches in json.load(open(os.path.join(ROOT, "spec/rw/waves", w, "plan.json"))).items():
        for b, cells in batches.items():
            if f"{s}_{b}" in open_:
                for c in cells:
                    out[(s, c["template"], c["tier"])] += c["count"]
    return out


def wave(n: int, pend: str | None = None) -> dict[str, dict[str, dict[str, int]]]:
    """skill -> tier -> template -> items to write in wave n (1-based)."""
    official, have = bank()
    if pend:
        have += pending(pend)
    out = {}
    for s, tiers in targets().items():
        out[s] = {}
        for tier, goal in tiers.items():
            final = spread(goal, official[(s, tier)])      # each template's share at the end
            left = {c: max(0, k - have[(s, c, tier)]) for c, k in final.items()}
            out[s][tier] = {c: k for c, k in spread(sum(left.values()) // (WAVES - n + 1), left).items() if k}
    return out


def demo() -> None:
    assert spread(10, {"a": 1, "b": 1, "c": 1}) in ({"a": 4, "b": 3, "c": 3}, {"a": 3, "b": 4, "c": 3}, {"a": 3, "b": 3, "c": 4})
    t = targets()
    assert sum(sum(v.values()) for v in t.values()) == TOTAL and len(t) == 10
    assert all(min(v.values()) >= FLOOR * sum(v.values()) - 1 for v in t.values())


if __name__ == "__main__":
    demo()
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
    pend = sys.argv[sys.argv.index("--pending") + 1] if "--pending" in sys.argv else None
    w = wave(n, pend)
    if "--json" in sys.argv:
        print(json.dumps(w, indent=1))
        sys.exit()
    _, have = bank()
    print(f"{'skill':28} {'target E/M/H':>16} {'have':>5}  wave {n}")
    for s, tiers in targets().items():
        got = sum(v for (k, _, _), v in have.items() if k == s)
        print(f"{s:28} {'/'.join(map(str, tiers.values())):>16} {got:5}  "
              + " ".join(f"{t[0].upper()}{sum(w[s][t].values())}" for t in TIERS))
    print(f"wave {n}: {sum(sum(x.values()) for v in w.values() for x in v.values())} items")
