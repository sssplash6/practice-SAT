import json, sys
src, out = sys.argv[1], sys.argv[2]
d = json.load(open(src))
keep = ("passage", "stem", "options", "table", "figure")
items = [dict(id=f"q{i}", **{k: it.get(k) for k in keep})
         for i, it in enumerate(d["items"]) if it.get("review") is None]
json.dump(items, open(out, "w"), indent=2, ensure_ascii=False)
print(len(items), "items")
