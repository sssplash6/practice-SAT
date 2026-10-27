"""Registry of running wave agents (copy into the session scratchpad next to running.json). reg.py add <batch> <stage> <agent_id> | rm <batch> [stage] | ls"""
import json, os, sys, time
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "running.json")
r = json.load(open(F)) if os.path.exists(F) else {}
a = sys.argv[1:]
if a[0] == "add":
    r[f"{a[1]}:{a[2]}"] = {"agent": a[3], "at": time.strftime("%H:%M")}
elif a[0] == "rm":
    for k in [k for k in r if k.split(":")[0] == a[1] and (len(a) < 3 or k.split(":")[1] == a[2])]:
        del r[k]
json.dump(r, open(F, "w"), indent=1)
for k, v in sorted(r.items()):
    print(f"{k:45} {v['agent']:20} {v['at']}")
print("running:", len(r))
