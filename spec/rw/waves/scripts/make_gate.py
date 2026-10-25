"""Band-7 gate set: every reviewed pilot item plus, per pilot skill, 6 band-6 and 6 band-7 official
anchors (no figures), shuffled, keys apart. Usage: make_gate.py pilot_dir cb_api_dir out_dir"""
import glob, json, random, sys

pilot_dir, cb_dir, out = sys.argv[1:4]
rng = random.Random(16)
pool = []
for p in sorted(glob.glob(f"{pilot_dir}/*.json")):
    slug = p.split("/")[-1][:-5]
    for it in json.load(open(p))["items"]:
        if (it.get("review") or {}).get("status") in ("pass", "fixed"):
            text = it["passage"]
            if it.get("table"):
                t = it["table"]
                text = "\n".join([t.get("title") or "", " | ".join(t["columns"]),
                                  *(" | ".join(r) for r in t["rows"])]) + "\n\n" + text
            if it.get("figure"):
                f = it["figure"]
                text = "\n".join([f"[{f['kind']}] {f.get('title') or ''}", f"x-axis: {f.get('x_axis')}; y-axis: {f.get('y_axis')}",
                                  *(s["series"] + ": " + ", ".join(f"{x} = {y}" for x, y in s["points"]) for s in f["data"])]) + "\n\n" + text
            pool.append({"src": "pilot", "id": it["id"], "skill": slug, "band": 0, "passage": text,
                         "stem": it["stem"], "options": it["options"], "answer": it["answer_letter"]})
    off = [i for i in json.load(open(f"{cb_dir}/{slug}.json"))["items"] if not i["has_figure"]]
    for band in (5, 6, 7):
        for i in rng.sample([x for x in off if x["band"] == band], 6):
            pool.append({"src": "official", "id": i["cb_id"], "skill": slug, "band": band, "passage": i["passage"],
                         "stem": i["stem"], "options": i["options"], "answer": i["answer_letter"]})
rng.shuffle(pool)
key, batch = {}, []
for n, x in enumerate(pool):
    qid = f"g{n:03d}"
    key[qid] = {k: x[k] for k in ("src", "id", "skill", "band", "answer")}
    batch.append({"qid": qid, "passage": x["passage"], "question": x["stem"], "options": dict(zip("ABCD", x["options"]))})
json.dump(key, open(f"{out}/key.json", "w"), indent=1)
json.dump(batch, open(f"{out}/gate.json", "w"), indent=1, ensure_ascii=False)
print(len(pool), "items:", sum(x["src"] == "pilot" for x in pool), "pilot")
