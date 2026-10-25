import json,statistics as s,sys
sys.path.insert(0,'tools')
from check_rw import register
IDS=["text_structure_and_purpose.P_lit.medium", "text_structure_and_purpose.F_example.medium", "text_structure_and_purpose.F_term.medium", "text_structure_and_purpose.F_method.medium", "text_structure_and_purpose.F_setup.medium", "text_structure_and_purpose.F_qualify.medium", "text_structure_and_purpose.F_lit.medium", "text_structure_and_purpose.P_study.hard", "text_structure_and_purpose.P_profile.hard", "text_structure_and_purpose.P_view.hard", "text_structure_and_purpose.P_lit.hard", "text_structure_and_purpose.F_example.hard", "text_structure_and_purpose.F_setup.hard"]
d=json.load(open('satbank/rw/text_structure_and_purpose__b.json'))
cb=json.load(open('material/rw/transcripts/text_structure_and_purpose.json'))['items']
mine=[i for i in d['items'] if i['id'] in IDS]
for t in ('medium','hard'):
    off=[register(i['passage']) for i in cb if i['tier']==t]
    print(t,'CB',[round(s.mean(x[k] for x in off),3) for k in range(3)])
    rs=[]
    for i in mine:
        if i['tier']!=t: continue
        r=register(i['passage']); rs.append(r)
        o=i['options']; kl=len(o['ABCD'.index(i['answer_letter'])])==max(map(len,o))
        print('  ',i['id'].split('.',1)[1].ljust(16),[round(x,3) for x in r], 'wc',len(i['passage'].split()), 'key',i['answer_letter'],'longest' if kl else '')
    print(t,'MINE',[round(s.mean(x[k] for x in rs),3) for k in range(3)])
from collections import Counter
print(Counter(i['answer_letter'] for i in d['items']), Counter(i['answer_letter'] for i in mine))
