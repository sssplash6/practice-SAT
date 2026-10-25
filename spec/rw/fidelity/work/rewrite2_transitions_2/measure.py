import json, sys, statistics as s
sys.path.insert(0, '/Users/workingmyassof/freshbot/satbank/tools')
from check_rw import register
P = json.load(open(sys.argv[1]))
off = {i['id']: i for i in json.load(open('/Users/workingmyassof/freshbot/satbank/material/rw/transcripts/transitions.json'))['items']}
mine = {i['id'].split('.', 1)[1]: i for i in json.load(open('/Users/workingmyassof/freshbot/satbank/satbank/rw/transitions.json'))['items']}
for tier in ('medium', 'hard'):
    rows = [(k, v) for k, v in P.items() if k.endswith(tier)]
    for k, v in rows:
        r = register(v); n = len(v.split()) - 1
        med = s.median(len(off[m]['passage'].split()) for m in mine[k]['models'])
        flag = ('SHORT' if n + 1 < med else '') + ('LONG' if n > 66 else '')
        print(f"{k:28} {r[0]:.2f} {100*r[1]:4.1f}% {r[2]:5.1f}  wc={n} med={med:g} {flag}")
    m = [s.mean(register(v)[i] for _, v in rows) for i in range(3)]
    print(f"== {tier}: {m[0]:.3f} {100*m[1]:.1f}% {m[2]:.1f}\n")
print("targets: medium 5.34 15.3% 34.0 | hard 5.15 13.5% 34.4")
