import json
d = json.load(open('satbank/rw/transitions.json'))
blind = [{'id': i['id'], 'passage': i['passage'], 'stem': i['stem'], 'options': i['options']}
         for i in d['items'] if i.get('review') is None]
json.dump(blind, open('spec/rw/fidelity/work/verify_transitions/blind.json', 'w'), indent=2, ensure_ascii=False)
print(len(blind))
