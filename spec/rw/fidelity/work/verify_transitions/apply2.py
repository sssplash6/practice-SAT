import fcntl, json
PATH = 'satbank/rw/transitions.json'
REPL = {
 'transitions.P1_purpose_aptness.medium': ('has displayed temporary commissions by contemporary artists', 'has displayed a rotating series of commissions by contemporary artists'),
 'transitions.C3_limiting_fact.hard': ('a harp derived from the instrument of Wassoulou hunters', 'a harp derived from the instrument played by Wassoulou hunters'),
}
with open(PATH + '.lock', 'w') as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    d = json.load(open(PATH, encoding='utf-8'))
    for it in d['items']:
        if it['id'] in REPL:
            old, new = REPL[it['id']]
            assert it['passage'].count(old) == 1
            it['passage'] = it['passage'].replace(old, new)
            it['word_count'] = len(it['passage'].replace('______', '').split())
            print(it['id'], it['word_count'])
            if it['id'].endswith('P1_purpose_aptness.medium'):
                it['review']['fixes'] = ['cut the equestrian-statue aside (trivia the question never uses) and said instead that the plinth shows a rotating series of commissions; 65 words, above the official medium maximum of 62, down to 62']
    json.dump(d, open(PATH, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    fcntl.flock(lk, fcntl.LOCK_UN)
