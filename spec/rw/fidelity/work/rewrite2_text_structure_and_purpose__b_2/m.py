import sys,glob,os,statistics as s
sys.path.insert(0,'/Users/workingmyassof/freshbot/satbank/tools')
from check_rw import register
CB={'medium':(4.86,0.111,30.0),'hard':(5.28,0.150,31.9)}
rows={}
for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__),'d','*.txt'))):
    p=open(f).read().strip(); name=os.path.basename(f)[:-4]; t=name.split('.')[-1]
    r=register(p); body=p.split('\n\n',1)[1] if p.startswith('The following') else p
    rows.setdefault(t,[]).append(r)
    print(f"{name:20} {r[0]:.3f} {r[1]:.3f} {r[2]:5.1f}  words {len(p.split())} body {len(body.split())}")
for t,rs in rows.items():
    m=[s.mean(x[k] for x in rs) for k in range(3)]
    print(t,'MINE',[round(x,3) for x in m],'CB',CB[t], 'wps range',round(CB[t][2]*.85,1),round(CB[t][2]*1.15,1))
