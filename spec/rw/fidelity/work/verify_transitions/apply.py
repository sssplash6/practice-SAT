"""Apply the review of satbank/rw/transitions.json (items with review null)."""
import fcntl, json

PATH = 'satbank/rw/transitions.json'
BLIND = json.load(open('spec/rw/fidelity/work/verify_transitions/blind_answers.json'))

# id -> dict of edits: passage replacements [(old, new)], field sets, extra sources, fixes text
EDITS = {
 'transitions.C1_two_subject.easy': dict(
    subtype='Contrast: two subjects, opposite values (sentence-initial)',
    fixes=['subtype label said "interrupter after the subject" but the blank opens the sentence; label corrected']),
 'transitions.C3_limiting_fact.easy': dict(
    passage=[('In the 1930s and early 1940s, Chinese American cinematographer James Wong Howe was among Hollywood’s most sought-after camera artists, renowned for his mastery of shadow and pioneering use of deep focus. ______ after being named in testimony as a Communist sympathizer, Howe was graylisted and struggled to find work until director Samuel Fuller hired him in 1950.',
              'Chinese American cinematographer James Wong Howe, renowned for his mastery of shadow and his pioneering use of deep focus, was among Hollywood’s most sought-after camera artists in the 1930s and early 1940s. ______ he was graylisted after being named in testimony as a Communist sympathizer, and he struggled to find work until director Samuel Fuller hired him in 1950.')],
    fixes=['sentence frame copied from official 1.10 (“In the [decade], [person] was [famous] ... ______ [despite/after phrase], [surname] ...”) replaced: the decade moves to the end of the first sentence and the blank sentence opens with its subject']),
 'transitions.E2_motive_action.easy': dict(
    passage=[('a team that included Cornell University scientist Britney Schmidt', 'a team that included astrobiologist Britney Schmidt')],
    sources=[{'what': 'Britney Schmidt, earth scientist and astrobiologist; at Georgia Tech 2013 to 2021, at Cornell from 2021 (so not a Cornell scientist in early 2020)', 'url': 'https://en.wikipedia.org/wiki/Britney_Schmidt'}],
    fixes=['“Cornell University scientist” was anachronistic: in early 2020 Schmidt was at Georgia Tech (she joined Cornell in 2021); now “astrobiologist Britney Schmidt” (source en.wikipedia.org/wiki/Britney_Schmidt)']),
 'transitions.T1_sequence_time.easy': dict(
    subtype='Sequence: the next step of a procedure',
    fixes=['subtype label still named the “First ... ______ ... Finally” frame the rewrite removed; label corrected']),
 'transitions.C2_belief_finding.medium': dict(
    subtype='Contrast: established pattern, then a case that breaks it (interrupter after the subject)',
    fixes=['subtype label said “blank after an introductory phrase”, but the blank is an interrupter after the subject; label corrected']),
 'transitions.E2_motive_action.medium': dict(
    passage=[('the Room for the River program, carried out between 2007 and 2015, moved dikes farther back, excavated high-water channels, and lowered floodplains at 34 locations.',
              'the Room for the River program, carried out at 34 locations between 2007 and 2015, moved dikes farther back, excavated high-water channels, and lowered floodplains.')],
    fixes=['“lowered floodplains at 34 locations” implied floodplain lowering at all 34 sites; the 34 locations now qualify the whole program (UNESCO-IHE brochure: room at 34 locations with a mix of measures)']),
 'transitions.P1_purpose_aptness.medium': dict(
    passage=[('the Fourth Plinth in London’s Trafalgar Square, a pedestal originally intended for an equestrian statue, has displayed commissions by contemporary artists.',
              'the Fourth Plinth in London’s Trafalgar Square has displayed temporary commissions by contemporary artists.')],
    fixes=['cut the equestrian-statue aside (trivia the question never uses), which also brings the passage from 65 words, above the official medium maximum of 62, to 58']),
 'transitions.C1_two_subject.hard': dict(
    passage=[('Researchers disagree about how farming can coexist with wildlife. Surveying birds and trees in Ghana and India, Ben Phalan and colleagues concluded in 2011 that most species fare best when crops are grown intensively on minimal land, leaving more forest intact; ______ ecologists Ivette Perfecto and John Vandermeer contend that biodiversity depends chiefly on the quality of the farmland between forest fragments, through which species move.',
              'Surveying birds and trees in Ghana and India, Ben Phalan and colleagues concluded in 2011 that most species fare best when crops are grown intensively on minimal land, leaving more forest intact. For ecologists Ivette Perfecto and John Vandermeer, ______ what matters most is not how much forest is spared but the quality of the farmland between forest fragments, through which species must migrate to survive.')],
    subtype='Contrast: two positions on one question (blank after an introductory phrase)',
    explanation='Phalan and colleagues conclude that most species do best when farming is intensive and confined to as little land as possible, so that more forest is spared. Perfecto and Vandermeer hold that what matters most is not the amount of forest spared but the quality of the farmland between forest fragments. These are opposing answers to the same question, so “by contrast” is the logical transition.',
    distractors={'A': {'recipe': 'unearned cause', 'why_wrong': 'Perfecto and Vandermeer’s view does not follow from Phalan’s findings; it rejects the idea that sparing forest is what matters most.'},
                 'B': {'recipe': 'additive decoy', 'why_wrong': '“Moreover” would add a point that supports Phalan’s conclusion, but Perfecto and Vandermeer put the quality of farmland ahead of the amount of forest spared, the opposite emphasis.'},
                 'C': {'recipe': 'wrong grain (restatement)', 'why_wrong': 'The last sentence does not reword Phalan’s conclusion; it gives other researchers’ competing view.'}},
    notes='Contrast: two positions on one question, the blank after an introductory phrase (lowercase options). The context sentence that announced the disagreement and the “; ______ [role] [Name] [verb]” frame of official 3.18 are gone.',
    sources=[{'what': 'Nature’s Matrix (Perfecto, Vandermeer and Wright): ultimate survival depends on whether the matrix allows migration; land sparing rejected', 'url': 'https://archive.foodfirst.org/publication/biodiversity-and-agriculture-natures-matrix-and-the-future-of-conservation/'}],
    fixes=['frame copied from official 3.18 (a sentence announcing a scholarly disagreement, then “; ______ [role] [Name] [verb]”) replaced: no announcing sentence, the second view opens its own sentence with the blank after “For ecologists Ivette Perfecto and John Vandermeer,” and states the opposition in content (not how much forest is spared but the quality of the farmland); explanation and why_wrong updated']),
 'transitions.C3_limiting_fact.hard': dict(
    passage=[('a harp adapted in the 1960s from the instrument of Wassoulou hunters', 'a harp derived from the instrument of Wassoulou hunters')],
    subtype='Contrast: a claim about one side of a figure’s work, then a fact about the same work that pulls against it (interrupter after the subject)',
    notes='Contrast with the key “though” as an interrupter after the subject noun phrase. The template is still C3 (claim, then a limiting fact about the same subject: her sound follows tradition, her lyrics challenge it); the official 3.7 frame (“Even in this ... work, ______”) is deliberately not used.',
    fixes=['subtype label still described the dropped “Even in X, ______” frame; relabelled (the key relation, a contrast limiting a claim about the same subject, still matches C3)',
           'removed “in the 1960s” from the kamalengoni gloss: the date made the instrument read as an innovation, which gave “likewise” a foothold']),
 'transitions.K1_grant_turn.hard': dict(
    sources=[{'what': 'older men at Papunya began painting in 1971 after Bardon’s mural project; painted on bits of old masonite and other found surfaces with acrylic paint; style traditional in sand and ceremonial body adornment', 'url': 'https://en.wikipedia.org/wiki/Papunya_Tula'}],
    fixes=[]),
 'transitions.E1_consequence.hard': dict(
    passage=[('In all four species studied, the DNA revealed large populations whose genetic diversity held steady for the 4,000 years before the extinction. Claims that moa were already declining before humans arrived, ______ appear unfounded.',
              'In all four species studied, the DNA revealed large populations whose genetic diversity held steady for the 4,000 years before the extinction; ______ people, not a prior decline, most likely drove the birds to extinction.')],
    subtype='Cause/effect: evidence, then the conclusion it licenses (after a semicolon)',
    explanation='The DNA study found that moa populations stayed large and genetically stable right up to the extinction, which followed Polynesian settlement. That evidence rules out a decline already under way and points to people as the cause. The clause after the semicolon draws this conclusion from the evidence, so “therefore” is the logical transition.',
    distractors={'B': {'recipe': 'false parallel', 'why_wrong': 'The conclusion about what caused the extinction is not a second, similar finding; it is drawn from the DNA evidence.'},
                 'C': {'recipe': 'false opposition (concession)', 'why_wrong': '“Nevertheless” would mean the conclusion holds in spite of the evidence, but the large, stable populations are exactly what rule out a prior decline.'},
                 'D': {'recipe': 'wrong time', 'why_wrong': 'The clause does not describe something happening at the same time as the study; it draws a conclusion from the study’s results.'}},
    notes='Cause/effect: evidence, then the conclusion it licenses, after a semicolon (lowercase options). The official 3.9 frame (the belief as subject, “______ should be regarded with skepticism”) is not used.',
    sources=[{'what': 'abstract: findings contradict claims of a decline before Polynesian settlement; populations large and stable before suddenly disappearing; most rapid human-facilitated megafauna extinction', 'url': 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1073/pnas.1314972111&resultType=core&format=json'}],
    fixes=['verdict sentence copied the frame of official 3.9 (“[the belief], ______ [doubtful verdict]”); now a semicolon clause drawing the study’s own conclusion (people, not a prior decline, drove the extinction; PNAS abstract via Europe PMC); explanation and why_wrong updated']),
 'transitions.P1_purpose_aptness.hard': dict(
    sources=[{'what': 'entire construction budget remained within the village and its surroundings; workers were day labourers from Rudrapur; local earth and bamboo (confirms the MoMA quote, which blocks fetching)', 'url': 'https://urbannext.net/meti-school/'},
             {'what': 'completed 2005; hand-built in four months by architects, local craftsmen, pupils, parents and teachers; loam, straw and bamboo', 'url': 'https://the.akdn/en/how-we-work/our-agencies/aga-khan-trust-culture/akaa/school-rudrapur'}],
    fixes=[]),
 'transitions.A1_addition.hard': dict(
    passage=[('his impoverished and hers privileged', 'his uprooted and hers privileged')],
    subtype='Addition: a further strand of one work',
    fixes=['subtype label still named the echo phrase the rewrite removed; relabelled (the key, “Additionally,” is still an addition word, matching A1)',
           '“his impoverished” childhood was stronger than the sources (TCJ: a traumatic, uprooted childhood amid turmoil and poverty); now “his uprooted”']),
 'transitions.U1_culmination_alt.hard': dict(
    sources=[{'what': 'after Song Shiping’s death in 2002 Zhao Xiangyuan became withdrawn and kept everything; in 2005 Song Dong persuaded her to make the work with him; 10,000 objects over five decades (confirms the MoMA facts, which block fetching)', 'url': 'https://portrait.gov.au/magazines/45/family-collective'}],
    fixes=[]),
}

FACTS = {  # claims checked per item (named people, places, dates, numbers, findings)
 'C1_two_subject.easy': 5, 'C2_belief_finding.easy': 5, 'C3_limiting_fact.easy': 5, 'E1_consequence.easy': 4,
 'E2_motive_action.easy': 5, 'P1_purpose_aptness.easy': 5, 'A1_addition.easy': 6, 'X1_example.easy': 5,
 'S1_spec_restate.easy': 4, 'M1_emphasis.easy': 4, 'T1_sequence_time.easy': 5, 'C1_two_subject.medium': 5,
 'C2_belief_finding.medium': 5, 'E1_consequence.medium': 5, 'E2_motive_action.medium': 6, 'P1_purpose_aptness.medium': 6,
 'A1_addition.medium': 5, 'T1_sequence_time.medium': 5, 'U1_culmination_alt.medium': 6, 'C1_two_subject.hard': 5,
 'C3_limiting_fact.hard': 5, 'K1_grant_turn.hard': 6, 'K2_qualification.hard': 4, 'E1_consequence.hard': 6,
 'P1_purpose_aptness.hard': 6, 'A1_addition.hard': 6, 'S1_spec_restate.hard': 5, 'M1_emphasis.hard': 5,
 'U1_culmination_alt.hard': 6,
}

with open(PATH + '.lock', 'w') as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    d = json.load(open(PATH, encoding='utf-8'))
    todo = [it for it in d['items'] if it.get('review') is None]
    assert len(todo) == len(BLIND) == 29
    for it, (blind, _why) in zip(todo, BLIND):
        e = EDITS.get(it['id'], {})
        for old, new in e.get('passage', []):
            assert it['passage'].count(old) == 1, (it['id'], old)
            it['passage'] = it['passage'].replace(old, new)
        for k in ('subtype', 'explanation', 'notes'):
            if k in e:
                it[k] = e[k]
        for L, v in e.get('distractors', {}).items():
            assert L in it['distractors']
            it['distractors'][L] = v
        it['sources'] += e.get('sources', [])
        it['word_count'] = len(it['passage'].replace('______', '').split())
        fixes = e.get('fixes', [])
        it['review'] = {'blind_answer': blind, 'agreed': blind == it['answer_letter'],
                        'facts_checked': FACTS[it['id'].split('.', 1)[1]], 'fixes': fixes,
                        'status': 'fixed' if fixes else 'pass'}
    with open(PATH, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    fcntl.flock(lk, fcntl.LOCK_UN)
print('ok')
