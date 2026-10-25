"""Copy the reviewed hard items of staged wave files into dir/<slug>.json for make_gate/make_safety.
Usage: hard_in.py out_dir staged.json..."""
import json, os, sys
out, files = sys.argv[1], sys.argv[2:]
os.makedirs(out, exist_ok=True)
for p in files:
    d = json.load(open(p))
    hard = [i for i in d["items"] if i["tier"] == "hard" and (i.get("review") or {}).get("status") in ("pass", "fixed")]
    dst = f"{out}/{d['slug']}.json"
    if os.path.exists(dst):
        hard = json.load(open(dst))["items"] + hard
    json.dump({**d, "items": hard}, open(dst, "w"), indent=1, ensure_ascii=False)
    print(p, len(hard))
