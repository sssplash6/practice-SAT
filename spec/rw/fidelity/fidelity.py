import glob, json, re, statistics as st
from collections import Counter, defaultdict
rank = {}
for i, l in enumerate(open("tools/data/freq.txt")):
    rank.setdefault(l.split()[0], i)
STOP = {w for w, r in rank.items() if r < 150}
W = lambda s: re.findall(r"[a-z’']+", re.sub(r"</?u>", " ", s.lower()))
def sents(p): return [x for x in re.split(r"(?<=[.!?”])\s+(?=[A-Z“])", p.replace("\n", " ")) if x.strip()]
def stats(items):
    pw, wps, rare, ow, longest, ko, do, letters, tr = [], [], [], [], 0, [], [], Counter(), defaultdict(list)
    for it in items:
        p = it["passage"]; w = W(p)
        if not w or len(it["options"]) != 4: continue
        pw.append(len(p.split())); ss = sents(p); wps.append(len(w) / max(1, len(ss)))
        r = sum(1 for x in w if rank.get(x, 10**9) > 20000) / len(w); rare.append(r); tr[it["tier"]].append(r)
        opts = it["options"]; k = "ABCD".index(it["answer_letter"])
        ow.append(st.mean(len(o.split()) for o in opts))
        longest += len(opts[k]) == max(map(len, opts))
        pset = {x for x in w if x not in STOP}
        def ov(o):
            c = [x for x in W(o) if x not in STOP]; return sum(x in pset for x in c) / len(c) if c else 0
        ko.append(ov(opts[k])); do += [ov(o) for j, o in enumerate(opts) if j != k]
        letters[it["answer_letter"]] += 1
    n = len(pw)
    return dict(n=n, words=st.median(pw), wps=st.mean(wps), rare=100*st.mean(rare), optw=st.mean(ow),
                longest=100*longest/n, kov=st.mean(ko), dov=st.mean(do), maxL=100*max(letters.values())/n,
                rare_tier={t: round(100*st.mean(v), 1) for t, v in sorted(tr.items())})
off, ours, stems = {}, defaultdict(list), {}
for p in glob.glob("material/rw/transcripts/*.json"):
    d = json.load(open(p)); off[d["slug"]] = d["items"]; stems[d["slug"]] = {i["stem"] for i in d["items"]}
for p in glob.glob("satbank/rw/*.json"):
    d = json.load(open(p)); ours[d["slug"]] += d["items"]
cols = ["words", "wps", "rare", "optw", "longest", "kov", "dov", "maxL"]
print(f"{'skill':26}{'src':5}" + "".join(f"{c:>9}" for c in cols) + "  stem=  rare% by tier")
for s in sorted(off):
    for name, its in (("CB", off[s]), ("ours", ours[s])):
        r = stats(its)
        stem = "" if name == "CB" else f"{100*sum(i['stem'] in stems[s] for i in its)/len(its):.0f}%"
        print(f"{s[:25]:26}{name:5}" + "".join(f"{r[c]:9.2f}" for c in cols) + f"  {stem:5}  {r['rare_tier']}")
