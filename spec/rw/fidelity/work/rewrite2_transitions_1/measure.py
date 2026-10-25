import json, sys, statistics as s
sys.path.insert(0, '/Users/workingmyassof/freshbot/satbank/tools')
from check_rw import register
P = json.load(open(sys.argv[1]))
for tier in ('easy', 'medium'):
    rows = [(k, v) for k, v in P.items() if k.endswith(tier)]
    for k, v in rows:
        r = register(v)
        print(f"{k:40} {r[0]:.2f} {100*r[1]:4.1f}% {r[2]:5.1f}  n={len(v.split())}")
    m = [s.mean(register(v)[i] for _, v in rows) for i in range(3)]
    print(f"== {tier}: {m[0]:.3f} {100*m[1]:.1f}% {m[2]:.1f}\n")
