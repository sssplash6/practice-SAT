import json, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, '../../../../../satbank/rw/words_in_context.json')))
keep = ('id', 'passage', 'stem', 'options', 'table', 'figure')
out = [{k: i[k] for k in keep} for i in d['items'] if i.get('review') is None]
json.dump(out, open(os.path.join(here, 'blind.json'), 'w'), indent=2, ensure_ascii=False)
print(len(out))
