"""Check (default) or write (--write) the 13 rewritten items into satbank/rw/text_structure_and_purpose__b.json.
Run from the repo root: python3 spec/rw/fidelity/work/rewrite2_text_structure_and_purpose__b_2/apply.py [--write]"""
import fcntl, json, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, "tools")
from check_rw import register, key_longest
from items import ITEMS

PATH = "satbank/rw/text_structure_and_purpose__b.json"
CB = {"medium": (4.863, 0.111, 30.031), "hard": (5.285, 0.150, 31.939)}


def body(p):
    return p.split("\n\n", 1)[1] if p.startswith("The following") else p


def check(d):
    bad = []
    for i in d["items"]:
        if i["id"] not in ITEMS:
            continue
        o, k = i["options"], "ABCD".index(i["answer_letter"])
        lens = [len(x) for x in o]
        for f in ("explanation", "notes", "rewrite"):
            if "—" in i[f]:
                bad.append(f"{i['id']}: em dash in {f}")
        for l, v in i["distractors"].items():
            if "—" in v["why_wrong"]:
                bad.append(f"{i['id']}: em dash in why_wrong {l}")
        txt = i["passage"] + i["stem"] + "".join(o)
        if "'" in txt or '"' in txt:
            bad.append(f"{i['id']}: straight quote")
        print(f"{i['id'].split('.', 1)[1]:17} key {i['answer_letter']} lens {lens} "
              f"{'LONGEST' if key_longest(i) else ''} body {i['word_count']} full {len(i['passage'].split())} "
              f"reg {[round(x, 3) for x in register(i['passage'])]}")
    for t in ("medium", "hard"):
        rs = [register(i["passage"]) for i in d["items"] if i["id"] in ITEMS and i["tier"] == t]
        print(t, [round(st.mean(r[x] for r in rs), 3) for x in range(3)], "CB", CB[t])
    print("key longest (mine):", sum(key_longest(i) for i in d["items"] if i["id"] in ITEMS), "/ 13")
    return bad


def merge(d):
    for i in d["items"]:
        new = ITEMS.get(i["id"])
        if not new:
            continue
        i.update(new)
        i["word_count"] = len(body(i["passage"]).split())
        i["review"] = None
    return d


if __name__ == "__main__":
    write = "--write" in sys.argv
    with open(PATH + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        d = merge(json.load(open(PATH)))
        assert sum(i["id"] in ITEMS for i in d["items"]) == 13
        bad = check(d)
        print("\n".join(bad) or "no local problems")
        if write and not bad:
            json.dump(d, open(PATH, "w"), indent=2, ensure_ascii=False)
            print("written")
