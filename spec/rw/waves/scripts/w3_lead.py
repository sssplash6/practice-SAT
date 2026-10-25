"""Lead-only steps for one wave-3 batch after its review. Usage:
  w3_lead.py prep <skill>_<bN>    -> scratch/<batch>/{hard,safety,gate}: the hard set, the safety set and (gated
                                      skills with band-7 targets) the gate set; prints the solver runs to launch
  w3_lead.py finish <skill>_<bN>  -> scores the gate (if any), picks the band rule, applies safety, promotes
Scratch root: $W3_SCRATCH. Promotes run here only, one at a time (they write satbank/rw/<skill>__w3.json)."""
import glob, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
S = os.environ["W3_SCRATCH"]
SIX = {"central_ideas_and_details", "inferences", "cross_text_connections"}      # band 6 by plan
NOGATE_REVIEW = {"words_in_context"}                                           # reviewer's rarity call, no gate
step, batch = sys.argv[1], sys.argv[2]
skill = re.sub(r"_b\d+$", "", batch)
staged = os.path.join(ROOT, "spec/rw/waves/w3", f"{batch}.json")
d = os.path.join(S, batch)
sc = lambda *a: os.path.join(ROOT, "spec/rw/waves/scripts", *a)
run = lambda *a: subprocess.run(["python3", *a], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def gated():
    hard = [i for i in json.load(open(staged))["items"] if i["tier"] == "hard" and (i.get("review") or {}).get("status") in ("pass", "fixed")]
    return skill not in SIX | NOGATE_REVIEW and any(i.get("band_target") == 7 for i in hard), len(hard)


if step == "prep":
    shutil.rmtree(d, ignore_errors=True)
    for x in ("hard", "safety", "gate/answers"):
        os.makedirs(os.path.join(d, x))
    run(sc("hard_in.py"), f"{d}/hard", staged)
    g, n = gated()
    if n:
        print(run(sc("make_safety.py"), f"{d}/safety", f"{d}/hard/{skill}.json").strip(), "-> safety set", f"{d}/safety/safety.json")
    else:
        print("no reviewed hard items: no safety solve needed")
    if g:
        print(run(sc("make_gate.py"), f"{d}/hard", os.path.join(ROOT, "material/rw/cb_api"), f"{d}/gate").strip(), "-> gate set", f"{d}/gate/gate.json (2 haiku runs)")
    else:
        print("no gate for this batch")
elif step == "finish":
    g, n = gated()
    rule = "six" if skill in SIX else "review" if skill in NOGATE_REVIEW else "six"
    if g and glob.glob(f"{d}/gate/answers/*.json"):
        out = run(sc("score_gate.py"), f"{d}/gate/key.json", f"{d}/gate/answers")
        pk = {m.group(1): float(m.group(2)) for m in re.finditer(rf"^{skill}\s+(pilot|band \d)\s+\d+\s+[\d.]+\s+([\d.]+)", out, re.M)}
        b6, b7, ours = pk.get("band 6"), pk.get("band 7"), pk.get("pilot")
        if None not in (b6, b7, ours):
            ok = abs(ours - b7) < abs(ours - b6) if b6 - b7 >= 0.05 else ours <= min(b6, b7) + 0.02
            rule = "review" if ok else "six"
        print(f"gate p(key): band6 {b6} band7 {b7} ours {ours} -> rule {rule}")
        json.dump({"band6": b6, "band7": b7, "ours": ours, "rule": rule}, open(f"{d}/gate/verdict.json", "w"))
    elif g:
        print("gate set but no gate answers: band 6 for all hard items")
    if n:
        if not os.path.exists(f"{d}/safety/answers.json"):
            sys.exit("safety answers missing: launch the safety solve first")
        print(run(sc("apply_safety.py"), f"{d}/safety", rule, staged).strip())
    print(run(os.path.join(ROOT, "tools/rw_promote.py"), staged).strip())
