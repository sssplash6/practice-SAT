import sys
sys.path.insert(0, '/Users/workingmyassof/freshbot/satbank/tools')
from check_rw import register
t = open(sys.argv[1], encoding='utf-8').read().strip()
for k, p in enumerate(t.split('\n====\n')):
    r = register(p.strip())
    body = p.strip().split('\n\n', 1)[-1] if p.strip().startswith('The following') else p.strip()
    print(k, [round(x, 3) for x in r], 'words', len(p.split()), 'body', len(body.split()))
