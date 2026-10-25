"""Score a blind round: python3 score.py <round>. Writes <round>/tells.json (authored id -> judge tell)."""
import glob, json, os, sys
R = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
tells, tot = {}, [0, 0]
print(f"{'skill':28}{'n':>4}{'recog':>6}{'AUC':>7}{'acc':>6}{'p(ours)':>9}{'p(CB)':>7}")
for kp in sorted(glob.glob(f"{HERE}/{R}/keys/*.json")):
    slug = os.path.basename(kp)[:-5]; jp = f"{HERE}/{R}/judged/{slug}.json"
    if not os.path.exists(jp): print(f"{slug:28} (not judged)"); continue
    key = {k["item"]: k for k in json.load(open(kp))}
    try:
        j = {x["item"]: x for x in json.load(open(jp))}
    except ValueError:
        print(f"{slug:28} (being written)"); continue
    rows = [(key[i]["truth"] == "authored", x["p_imitation"], x) for i, x in j.items() if i in key and not x.get("recognized")]
    pos = [p for t, p, _ in rows if t]; neg = [p for t, p, _ in rows if not t]
    auc = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / max(1, len(pos) * len(neg))
    acc = sum((p > 0.5) == t for t, p, _ in rows if p != 0.5) / max(1, sum(p != 0.5 for _, p, _ in rows))
    rec = sum(bool(x.get("recognized")) for x in j.values())
    auc = auc if pos and neg else float("nan")
    print(f"{slug:28}{len(j):4}{rec:6}{auc:7.2f}{acc:6.2f}{sum(pos)/max(1,len(pos)):9.2f}{sum(neg)/max(1,len(neg)):7.2f}")
    for i, x in j.items():
        if i in key and key[i]["truth"] == "authored":
            tells[key[i]["id"]] = {"p": x["p_imitation"], "tell": x.get("tell", "")}
json.dump(tells, open(f"{HERE}/{R}/tells.json", "w"), indent=1, ensure_ascii=False)
print("AUC 0.50 = indistinguishable; 1.00 = every imitation spotted")
