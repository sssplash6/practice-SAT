"""Where each wave-3 batch stands, read from disk (so a resumed lead knows what to launch next).
Stages: plan -> written (staged file, all planned items present) -> reviewed (every item has review)
-> solved (every reviewed hard item has safety) -> promoted (every ready item is in satbank/rw/<skill>__w3.json).
Usage: python3 spec/rw/waves/scripts/w3_status.py [--json]"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
W = os.path.join(ROOT, "spec/rw/waves/w3")
plan = json.load(open(os.path.join(W, "plan.json")))
out = []
for skill, batches in plan.items():
    bank_path = os.path.join(ROOT, "satbank/rw", f"{skill}__w3.json")
    bank = {i["id"] for i in json.load(open(bank_path))["items"]} if os.path.exists(bank_path) else set()
    for b, cells in batches.items():
        want = sum(c["count"] for c in cells)
        f = os.path.join(W, f"{skill}_{b}.json")
        row = {"batch": f"{skill}_{b}", "want": want, "stage": "plan", "items": 0}
        if os.path.exists(f):
            try:
                d = json.load(open(f))
            except Exception:
                row["stage"] = "writing (unreadable)"; out.append(row); continue
            its = d.get("items", []); row["items"] = len(its)
            gone = len(d.get("removed", []))
            row["stage"] = "writing" if len(its) + gone < want and not d.get("done") else "written"
            if its and all(i.get("review") for i in its):
                row["stage"] = "reviewed"
                ok = [i for i in its if (i.get("review") or {}).get("status") in ("pass", "fixed")]
                hard = [i for i in ok if i["tier"] == "hard"]
                if all(i.get("safety") for i in hard):
                    row["stage"] = "solved"
                    ready = [i for i in ok if i["tier"] != "hard" or i["safety"].get("agreed")]
                    row["ready"] = len(ready)
                    row["not_agreed"] = [i["id"] for i in hard if not i["safety"].get("agreed")]
                    if ready and all(i["id"] in bank for i in ready):
                        row["stage"] = "promoted"
        out.append(row)
if "--json" in sys.argv:
    print(json.dumps(out, indent=1))
else:
    from collections import Counter
    print(Counter(r["stage"] for r in out))
    for r in out:
        print(f"{r['batch']:34} {r['stage']:10} {r['items']:3}/{r['want']:<3} {('ready ' + str(r['ready'])) if 'ready' in r else ''}")
    live = sum(len(json.load(open(os.path.join(ROOT, 'satbank/rw', f)))['items']) for f in os.listdir(os.path.join(ROOT, 'satbank/rw')) if f.endswith('__w3.json'))
    print('wave 3 items live in satbank/rw:', live)
