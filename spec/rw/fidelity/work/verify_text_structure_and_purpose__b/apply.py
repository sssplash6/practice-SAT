import fcntl, json
P = "satbank/rw/text_structure_and_purpose__b.json"
W = "spec/rw/fidelity/work/verify_text_structure_and_purpose__b/"
blind = json.load(open(W + "blind_answers.json"))
pre = "text_structure_and_purpose."

def sub(it, field, old, new):
    assert it[field].count(old) == 1, (it["id"], field, old)
    it[field] = it[field].replace(old, new)

facts = {"P_study.easy": 6, "P_profile.easy": 6, "P_effort.easy": 8, "P_argue.easy": 7, "F_example.easy": 8,
         "F_term.easy": 7, "F_limit.easy": 6, "F_answer.easy": 8, "F_setup.easy": 7, "F_lit.easy": 3,
         "P_profile.medium": 9, "P_argue.medium": 6, "P_lit.medium": 3, "F_example.medium": 7, "F_term.medium": 7,
         "F_method.medium": 7, "F_setup.medium": 4, "F_qualify.medium": 4, "F_lit.medium": 3, "P_study.hard": 7,
         "P_profile.hard": 9, "P_view.hard": 6, "P_lit.hard": 4, "F_example.hard": 7, "F_setup.hard": 7}
fixes = {
    "P_profile.medium": ["Baldwin began teaching his family in 1991 alongside teaching himself (MacArthur), so the family no longer appears after the master's degree under “subsequently”; passage now says he taught himself and his family the language"],
    "F_answer.easy": ["“Instead, their basal metabolic rate is ...” did not follow from the fur clause; now “Instead, they rely on a basal metabolic rate ...”"],
    "P_lit.medium": ["restored the paragraph break before “For in spite of her vogue” (Gutenberg #78915 starts a new paragraph there)"],
    "P_lit.hard": ["context line trimmed (“fifteen,” dropped) so the full passage is 122 words, the hard-tier official maximum; trimming the excerpt at its only sentence boundary would have cut it to 64 body words and removed the basis for the key and for C"],
    "P_study.hard": ["option C reworded (“after they hatch”) so the key is no longer the uniquely longest option"],
    "F_term.easy": ["added the source for “captioning videos” (Kirkus review: a worker who captions videos for the platform Amara)"],
    "P_profile.hard": ["subject replaced: Máret Ánne Sara’s Pile o’Sápmi (a Sámi protest against a Norwegian state reindeer cull) shared people, country and conflict with official Rhetorical Synthesis 3.12 (Sámi protests over the Alta dam and reindeer herding); new subject is the Museum of Broken Relationships (Vištica and Grubišić, 2006; Kenneth Hudson Award 2011), with new options, explanation and sources; key letter kept at C",
                       "an Indigenous place-names map (Pearce 2017) was considered and rejected because official TSP 1.14 is an Indigenous map and 1.3 names the Potawatomi"],
}

new_profile = {
    "passage": "The Museum of Broken Relationships originated in 2006 as an art project by Olinka Vištica and Dražen Grubišić, former partners who solicited objects left over from their friends’ breakups and exhibited them in Zagreb, Croatia. Given a permanent home in Zagreb in 2010, the collection has continued to expand through donations from the public. Each item, frequently an object of no apparent value, is accompanied only by its donor’s anonymous account of the relationship. The European Museum Forum awarded the museum its 2011 Kenneth Hudson Award, an honor reserved for achievements that challenge common perceptions of museums’ role in society.",
    "options": [
        "To explain how the breakup of the museum’s founders inspired them to collect objects associated with failed relationships",
        "To argue that museums should give the public a greater role in deciding which objects are collected and how they are labeled",
        "To describe a museum of donated objects and anonymous stories that has been recognized for challenging ideas about museums",
        "To identify the kinds of relationships that donors most often recall and the objects they typically choose to represent them",
    ],
    "answer_letter": "C",
    "explanation": "The text tells how the Museum of Broken Relationships began, how its collection grows (objects donated by the public) and how each object is shown (with only the donor’s anonymous account), and ends with the European Museum Forum giving it an award reserved for achievements that challenge common perceptions of museums’ role. Choice C covers the museum and that recognition.",
    "distractors": {
        "A": {"recipe": "PART", "why_wrong": "The text says only that the founders were former partners; it never explains what inspired the project, and the origin is one sentence of a text that goes on to the collection and the award."},
        "B": {"recipe": "STANCE", "why_wrong": "The text describes how this museum collects and labels objects and how it was honored; it never recommends that other museums change their practices."},
        "D": {"recipe": "INV", "why_wrong": "No pattern in the donations is described; the text says only that items are often of no apparent value and come with anonymous accounts."},
    },
    "sources": [
        {"what": "founded by artists Olinka Vištica and Dražen Grubišić after their relationship ended; they asked friends to donate objects left behind from their break-ups; first shown in 2006 at Glyptotheque Zagreb in the 41st Zagreb Salon; later items donated by members of the public; each item comes with an anonymous story from the donor; permanent museum in Zagreb’s Upper Town opened October 2010; Kenneth Hudson Award, May 2011, given for the most unusual, daring achievement that challenges common perceptions of the role of museums in society",
         "url": "https://en.wikipedia.org/wiki/Museum_of_Broken_Relationships"},
        {"what": "a joint-author art project of a former couple begun in 2006; donated objects of no apparent value displayed anonymously with the donors’ accounts as the only text; European Museum Forum’s Kenneth Hudson Award 2011; challenges common perceptions of the role of the museum in society",
         "url": "https://presentations.thebestinheritage.com/2012/Museum%20of%20Broken%20Relationships"},
        {"what": "the museum still invites the public to send items and break-up stories", "url": "https://brokenships.com/"},
    ],
    "notes": "Humanities (museums). Replaces Pile o’Sápmi, whose Sámi reindeer-herding protest against the Norwegian state was too close to official Rhetorical Synthesis 3.12 (Alta dam). Profile build as in 3.13: origin, method, how the work departs from convention, recognition. Distractors: a partial origin reading (A), a stance trap that turns the method into a recommendation (B), an invented pattern in the donations (D). Passage 96 words; models’ median 90.",
}

with open(P + ".lock", "w") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    d = json.load(open(P))
    items = {it["id"][len(pre):]: it for it in d["items"]}
    todo = [k for k, it in items.items() if it.get("review") is None]
    assert len(todo) == 25 and set(todo) == set(facts), todo

    it = items["P_profile.medium"]
    sub(it, "passage", "nevertheless taught himself the language,", "nevertheless taught himself and his family the language,")
    sub(it, "passage", "earned a master’s degree in linguistics, taught myaamia to his family, and in 2001", "earned a master’s degree in linguistics and in 2001")
    sub(it, "explanation", "follows Baldwin as he learns the language from archival sources, teaches it to his family, and founds",
        "follows Baldwin as he learns the language from archival sources and teaches it to his family, then founds")

    it = items["F_answer.easy"]
    sub(it, "passage", "Instead, their basal metabolic rate is roughly three times", "Instead, they rely on a basal metabolic rate roughly three times")

    it = items["P_lit.medium"]
    sub(it, "passage", "boredom or introspection. For in spite", "boredom or introspection.\n\nFor in spite")
    it["notes"] += " Reviewer restored the source’s paragraph break before “For in spite of her vogue.”"

    it = items["P_lit.hard"]
    sub(it, "passage", "Lucilla Marjoribanks, fifteen, has been refused", "Lucilla Marjoribanks has been refused")

    it = items["P_study.hard"]
    i = 2
    assert it["options"][i].endswith("how much they will grow after hatching.")
    it["options"][i] = it["options"][i].replace("after hatching.", "after they hatch.")

    it = items["F_term.easy"]
    k = [s for s in it["sources"] if "kirkus" in s["url"]]
    assert len(k) == 1
    k[0]["what"] += "; one worker profiled captions videos for the on-demand platform Amara"

    it = items["P_profile.hard"]
    it.update(new_profile)
    it["rewrite"] += " Reviewer then replaced Pile o’Sápmi with the Museum of Broken Relationships (too close to the official Sámi Alta dam item)."

    for k in todo:
        it = items[k]
        it["word_count"] = len((it["passage"].split("\n\n", 1)[1] if it["passage"].startswith("The following text") else it["passage"]).split())
        ba = blind[pre + k][0]
        it["review"] = {"blind_answer": ba, "agreed": ba == it["answer_letter"], "facts_checked": facts[k],
                        "fixes": fixes.get(k, []), "status": "fixed" if k in fixes else "pass"}
    with open(P, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    fcntl.flock(lk, fcntl.LOCK_UN)
print("ok")
