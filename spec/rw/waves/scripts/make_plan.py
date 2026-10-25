"""Split a wave's quotas (tools/rw_plan.py N --json) into writer batches of about 25.
Usage: make_plan.py N   -> spec/rw/waves/wN/plan.json (freeze it: rw_plan recomputes from live counts)

Hard cells alternate band_target 7/6, except Central Ideas, Inferences and Cross-Text, whose hard
items landed at band 6 in the pilot, the trial and wave 2 (band 6 by plan). Cells are dealt
round-robin, so every batch gets a mix of templates and tiers."""
import json, math, os, subprocess, sys

wave = sys.argv[1]
SIX = {"central_ideas_and_details", "inferences", "cross_text_connections"}
q = json.loads(subprocess.run(["python3", "tools/rw_plan.py", wave, "--json"], capture_output=True, text=True, check=True).stdout)
plan = {}
for slug in q:
    cells = []
    for tier in ("hard", "medium", "easy"):
        for code, n in sorted(q[slug][tier].items(), key=lambda kv: -kv[1]):
            for k in range(n):
                bt = (6 if slug in SIX else (7 if k % 2 == 0 else 6)) if tier == "hard" else None
                cells.append((code, tier, bt))
    nb = math.ceil(len(cells) / 25)
    plan[slug] = {}
    for b in range(nb):
        cnt = {}
        for c in cells[b::nb]:
            cnt[c] = cnt.get(c, 0) + 1
        plan[slug][f"b{b + 1}"] = [{"template": t, "tier": tr, "band_target": bt, "count": n} for (t, tr, bt), n in cnt.items()]
    print(slug, len(cells), "items in", nb, "batches:", [sum(x["count"] for x in plan[slug][b]) for b in plan[slug]])
os.makedirs(f"spec/rw/waves/w{wave}", exist_ok=True)
json.dump(plan, open(f"spec/rw/waves/w{wave}/plan.json", "w"), indent=1)
