"""Build blind sets: every authored item of a skill mixed with as many official items of
the same tiers, rendered alike and shuffled. python3 build.py <round> [<earlier round> ...]
Official items that judges recognised in an earlier round, or that an authored item in the
set lists as a model, are drawn only when a tier runs out of others."""
import glob, json, os, random, sys
R = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(f"{HERE}/{R}/sets", exist_ok=True); os.makedirs(f"{HERE}/{R}/keys", exist_ok=True)
def render(n, it):
    out = [f"=== Item {n} ===", it["passage"].strip()]
    t = it.get("table")
    if t:
        out.append(f"[Table] {t.get('title') or ''}\n" + " | ".join(t["columns"]) + "\n" + "\n".join(" | ".join(r) for r in t["rows"]) + (f"\n{t['note']}" if t.get("note") else ""))
    f = it.get("figure")
    if f:
        out.append(f"[{f.get('kind') or 'figure'}] {f.get('title') or ''}; x-axis: {f.get('x_axis')}; y-axis: {f.get('y_axis')}. {f.get('description') or ''}")
    out.append(it["stem"])
    out += [f"{l}) {o}" for l, o in zip("ABCD", it["options"])]
    out.append(f"Key: {it['answer_letter']}")
    return "\n\n".join(out[:2]) + "\n\n" + "\n".join(out[2:]) + "\n"
off = {}
for p in glob.glob("material/rw/transcripts/*.json"):
    d = json.load(open(p)); off[d["slug"]] = [i for i in d["items"] if not i["cb_id"].startswith("abcd")]
ours = {}
for p in glob.glob("satbank/rw/*.json"):
    d = json.load(open(p)); ours.setdefault(d["slug"], []).extend(d["items"])
rng = random.Random(f"blind-{R}")
seen = set()  # (slug, official id) recognised in earlier rounds
for E in sys.argv[2:]:
    for kp in glob.glob(f"{HERE}/{E}/keys/*.json"):
        slug = os.path.basename(kp)[:-5]
        try: j = {x["item"]: x for x in json.load(open(f"{HERE}/{E}/judged/{slug}.json"))}
        except (OSError, ValueError): continue
        seen |= {(slug, k["id"]) for k in json.load(open(kp)) if k["truth"] == "official" and j.get(k["item"], {}).get("recognized")}
for slug, mine in sorted(ours.items()):
    pool = []
    for tier in ("easy", "medium", "hard"):
        k = sum(i["tier"] == tier for i in mine)
        models = {m for i in mine for m in i.get("models", [])}
        cand = [i for i in off[slug] if i["tier"] == tier]
        rng.shuffle(cand)
        cand.sort(key=lambda i: ((slug, i["id"]) in seen) + (i["id"] in models))  # stable: fresh ones first
        pool += [("official", i) for i in cand[:k]]
    pool += [("authored", i) for i in mine]
    rng.shuffle(pool)
    open(f"{HERE}/{R}/sets/{slug}.txt", "w").write("\n".join(render(n + 1, it) for n, (_, it) in enumerate(pool)))
    json.dump([{"item": n + 1, "truth": src, "id": it["id"], "tier": it["tier"]} for n, (src, it) in enumerate(pool)],
              open(f"{HERE}/{R}/keys/{slug}.json", "w"), indent=1)
    print(slug, len(pool))
