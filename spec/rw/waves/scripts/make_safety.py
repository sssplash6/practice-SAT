"""Final safety set: the given pilot files' reviewed items, shuffled, keys apart.
Usage: make_safety.py out_dir pilot_file..."""
import json, random, sys

out, files = sys.argv[1], sys.argv[2:]
rng = random.Random(7)
pool = []
for p in files:
    for it in json.load(open(p))["items"]:
        if (it.get("review") or {}).get("status") in ("pass", "fixed"):
            text = it["passage"]
            if it.get("table"):
                t = it["table"]
                text = "\n".join([t.get("title") or "", " | ".join(t["columns"]), *(" | ".join(r) for r in t["rows"])]) + "\n\n" + text
            if it.get("figure"):
                f = it["figure"]
                text = "\n".join([f"[{f['kind']}] {f.get('title') or ''}", f"x-axis: {f.get('x_axis')}; y-axis: {f.get('y_axis')}",
                                  *(s["series"] + ": " + ", ".join(f"{x} = {y}" for x, y in s["points"]) for s in f["data"])]) + "\n\n" + text
            pool.append((it["id"], it["answer_letter"], text, it["stem"], it["options"]))
rng.shuffle(pool)
key, batch = {}, []
for n, (iid, ans, text, stem, opts) in enumerate(pool):
    qid = f"s{n:02d}"
    key[qid] = {"id": iid, "answer": ans}
    batch.append({"qid": qid, "passage": text, "question": stem, "options": dict(zip("ABCD", opts))})
json.dump(key, open(f"{out}/key.json", "w"), indent=1)
json.dump(batch, open(f"{out}/safety.json", "w"), indent=1, ensure_ascii=False)
print(len(pool), "items")
