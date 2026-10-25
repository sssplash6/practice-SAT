import json, sys
src = 'satbank/rw/text_structure_and_purpose__b.json'
out = 'spec/rw/fidelity/work/verify_text_structure_and_purpose__b/blind.json'
d = json.load(open(src))
keep = ('id', 'tier', 'passage', 'stem', 'options', 'table', 'figure')
blind = [{k: it.get(k) for k in keep} for it in d['items'] if it.get('review') is None]
json.dump(blind, open(out, 'w'), indent=2, ensure_ascii=False)
print(len(blind))
