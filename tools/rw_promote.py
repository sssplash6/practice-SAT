"""Move gated Reading and Writing items from staging (spec/rw/waves/<wave>/<skill>_<batch>.json) into the
served bank (satbank/rw/<skill>__<wave>.json), where satbank/topics/rw.py picks them up.

An item is promoted when its review passed (`review.status` pass or fixed, spec/rw/VERIFY.md) and, if
it is hard, its blind safety solve agreed (`safety.agreed` true, no second defensible option). Items
already in the bank are replaced by id, so a re-run after fixes is safe.

    python3 tools/rw_promote.py spec/rw/waves/w1/boundaries_b1.json [...]
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ready(it: dict) -> bool:
    ok = (it.get("review") or {}).get("status") in ("pass", "fixed")
    safe = it.get("tier") != "hard" or (it.get("safety") or {}).get("agreed") is True
    return ok and safe


def promote(path: str) -> tuple[int, int]:
    d = json.load(open(path))
    wave = os.path.basename(os.path.dirname(path))
    out_path = os.path.join(ROOT, "satbank/rw", f"{d['slug']}__{wave}.json")
    out = json.load(open(out_path)) if os.path.exists(out_path) else {
        "skill": d["skill"], "slug": d["slug"], "part": wave, "domain": d["domain"], "plan": {"templates": []}, "items": []}
    codes = {t["code"] for t in out["plan"]["templates"]}
    out["plan"]["templates"] += [{"code": t["code"], "name": t["name"]} for t in d["plan"]["templates"] if t["code"] not in codes]
    keep = [it for it in d["items"] if ready(it)]
    ids = {it["id"] for it in keep}
    out["items"] = [it for it in out["items"] if it["id"] not in ids] + keep
    json.dump(out, open(out_path, "w"), indent=2, ensure_ascii=False)
    return len(keep), len(d["items"])


if __name__ == "__main__":
    assert ready({"tier": "easy", "review": {"status": "pass"}}) and not ready({"tier": "hard", "review": {"status": "pass"}})
    assert ready({"tier": "hard", "review": {"status": "fixed"}, "safety": {"agreed": True}})
    for p in sys.argv[1:]:
        k, n = promote(p)
        print(f"{p}: {k} of {n} promoted")
