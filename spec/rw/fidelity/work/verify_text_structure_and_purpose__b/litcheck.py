import json, re, sys
G = sys.argv[1]
src = {'F_lit.easy': '125', 'P_lit.medium': '78915', 'F_setup.medium': '54700',
       'F_qualify.medium': '5721', 'F_lit.medium': '66191', 'P_lit.hard': '41286'}
def norm(s):
    s = re.sub(r'</?u>', '', s)
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace('—', '--').replace('_', '')
    return re.sub(r'\s+', ' ', s).strip()
d = json.load(open('satbank/rw/text_structure_and_purpose__b.json'))
for it in d['items']:
    k = it['id'].split('.', 1)[1]
    if k not in src: continue
    body = it['passage'].split('\n\n', 1)[1]
    t = norm(open(f'{G}/{src[k]}.txt', encoding='utf-8').read())
    b = norm(body)
    print('=====', k)
    if b in t:
        print('EXACT (normalized)'); continue
    # sentence-by-sentence
    for sent in re.split(r'(?<=[.!?])\s+', b):
        print(' OK ' if sent in t else ' MISS', sent[:110])
