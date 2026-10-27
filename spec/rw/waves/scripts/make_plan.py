"""Split a wave's quotas (tools/rw_plan.py N --json) into writer batches of about 25.
Usage: make_plan.py N [--pending wM]  -> spec/rw/waves/wN/plan.json (freeze it: rw_plan recomputes from live counts;
--pending counts wave M's unpromoted planned cells as written, to plan N while M finishes)

Hard cells alternate band_target 7/6, except Central Ideas, Inferences and Cross-Text, whose hard
items landed at band 6 in the pilot, the trial and wave 2 (band 6 by plan). Cells are dealt
round-robin, so every batch gets a mix of templates and tiers. Hard cells on a template with no band-7
official item (the assignment table in spec/rw/band7/<skill>.md, Boundaries and FSS) are band 6, and hard FSS
tense (R4) cells move to medium (CB has no tense item above band 5)."""
import json, math, os, re, subprocess, sys

wave = sys.argv[1]
SIX = {"central_ideas_and_details", "inferences", "cross_text_connections"}


def no_band7(slug):
    """Templates whose band-7 column is 'none' in the report's assignment table; None when there is no table."""
    p = f"spec/rw/band7/{slug}.md"
    s = open(p).read() if os.path.exists(p) else ""
    if "## Appendix: template assignment" not in s:
        return None
    rows = re.findall(r"^\| (\w+) \|.*\| (.+?) \|$", s.split("## Appendix: template assignment")[1], re.M)
    return {t for t, b7 in rows if b7.strip() == "none"}


q = json.loads(subprocess.run(["python3", "tools/rw_plan.py", wave, "--json", *sys.argv[2:]], capture_output=True, text=True, check=True).stdout)
plan = {}
for slug in q:
    cells, nb7 = [], no_band7(slug)
    if slug == "form_structure_and_sense":
        for code in [c for c in q[slug]["hard"] if c.startswith("R4_")]:
            q[slug]["medium"][code] = q[slug]["medium"].get(code, 0) + q[slug]["hard"].pop(code)
    for tier in ("hard", "medium", "easy"):
        for code, n in sorted(q[slug][tier].items(), key=lambda kv: -kv[1]):
            for k in range(n):
                six = slug in SIX or (nb7 is not None and code in nb7)
                bt = (6 if six else (7 if k % 2 == 0 else 6)) if tier == "hard" else None
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
