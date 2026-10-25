"""Write safety verdicts and bands onto staged items. Usage: apply_safety.py safety_dir band_rule staged.json...
band_rule: 'review' = band 7 when the reviewer's band7 verdict is "band 7", else 6; 'six' = band 6 for all hard items."""
import fcntl, json, sys

sdir, rule, files = sys.argv[1], sys.argv[2], sys.argv[3:]
key, ans = json.load(open(f"{sdir}/key.json")), json.load(open(f"{sdir}/answers.json"))
verdict = {}
for q, k in key.items():
    a = ans[q]
    verdict[k["id"]] = {"agreed": a["answer"] == k["answer"] and not a.get("also_defensible") and not a.get("unfair"),
                        "answer": a["answer"], "also_defensible": a.get("also_defensible") or [], "unfair": a.get("unfair") or ""}
for path in files:
    with open(path + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        d = json.load(open(path))
        n = 0
        for it in d["items"]:
            if it["id"] in verdict:
                it["safety"] = verdict[it["id"]]
                v = (it.get("band7") or (it.get("review") or {}).get("band7") or {}).get("verdict")
                it["band"] = 7 if rule == "review" and v == "band 7" else 6
                n += 1
        json.dump(d, open(path, "w"), indent=2, ensure_ascii=False)
    print(path, n, "items marked;", [i["id"] for i in d["items"] if i["id"] in verdict and not i["safety"]["agreed"]], "not agreed")
