import sys, re
sys.path.insert(0, '/Users/workingmyassof/freshbot/satbank/tools')
from check_rw import register
path, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 15
txt = open(path, encoding='utf-8').read().replace('\r', '')
import re as _r
m=_r.search(r'\*\*\* ?START OF.*?\*\*\*', txt); txt = txt[m.end():] if m else txt
txt = txt.split('*** END OF')[0]
paras = [re.sub(r'\s+', ' ', p).strip() for p in txt.split('\n\n')]
out = []
for i, p in enumerate(paras):
    w = len(p.split())
    if lo <= w <= hi and '_' not in p:
        r = register(p)
        out.append((r[0] + r[1] * 5, i, w, r, p))
out.sort(reverse=True)
for sc, i, w, r, p in out[:n]:
    print(f"#{i} w{w} cw{r[0]:.2f} lw{r[1]:.3f} ws{r[2]:.1f}\n{p}\n")
