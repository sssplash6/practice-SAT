"""Score the gate: per skill, pilot vs official band 6 / band 7 on accuracy and mean p(key);
per pilot item its p(key). Usage: score_gate.py key.json answers_dir"""
import collections, glob, json, sys

key = json.load(open(sys.argv[1]))
got = collections.defaultdict(list)
for f in glob.glob(f"{sys.argv[2]}/*.json"):
    for qid, a in json.load(open(f)).items():
        got[qid].append(a)


def pk(a, ans):
    p = a.get("p") or {}
    return p.get(ans, 0) / (sum(p.values()) or 1) if p else float(a.get("answer") == ans)


rows = []
for qid, k in key.items():
    if got.get(qid):
        rs = got[qid]
        rows.append({**k, "acc": sum(r.get("answer") == k["answer"] for r in rs) / len(rs),
                     "pk": sum(pk(r, k["answer"]) for r in rs) / len(rs)})
grp = collections.defaultdict(list)
for r in rows:
    grp[(r["skill"], "pilot" if r["src"] == "pilot" else f"band {r['band']}")].append(r)
print(f"{len(rows)} of {len(key)} answered\n\nskill                        group    n   acc  p(key)")
for (s, g), xs in sorted(grp.items()):
    print(f"{s:28} {g:7} {len(xs):3}  {sum(x['acc'] for x in xs) / len(xs):.2f}  {sum(x['pk'] for x in xs) / len(xs):.2f}")
allg = collections.defaultdict(list)
for r in rows:
    allg["pilot" if r["src"] == "pilot" else f"band {r['band']}"].append(r)
print("\nall:", {g: (len(xs), round(sum(x['acc'] for x in xs) / len(xs), 2), round(sum(x['pk'] for x in xs) / len(xs), 2))
                 for g, xs in sorted(allg.items())})
print("\npilot items by p(key):")
for r in sorted((r for r in rows if r["src"] == "pilot"), key=lambda r: r["pk"]):
    print(f"  {r['pk']:.2f}  {'right' if r['acc'] >= .5 else 'WRONG'}  {r['id']}")
