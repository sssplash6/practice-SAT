import fcntl, json, sys
P = "satbank/rw/text_structure_and_purpose__a.json"

def sub(it, field, old, new):
    assert it[field].count(old) == 1, (it["id"], field, old)
    it[field] = it[field].replace(old, new)

blind = json.load(open("spec/rw/fidelity/work/verify_text_structure_and_purpose__a/blind_answers.json"))
facts = [13, 8, 9, 6, 8, 5, 9, 10, 6, 6, 9, 7, 9, 11, 11, 8]
fixes = {
    0: ["Vai located as devised “in present-day Liberia” (the language is also spoken in Sierra Leone)",
        "Bamum syllabary given as “some eighty characters” (Wikipedia gives 80 in the lead but 82 plus digits for the 1910 version)",
        "dropped the opening “And” of the last example, which echoed model 1.12"],
    4: ["the aerial walkways join the two new towers to each other, not the old sheds to the towers (SESC Pompeia article); passage now says she raised new towers beside the sheds, joined by walkways"],
    15: ["Steffen and colleagues searched for planets close to hot Jupiters (near the 2:1 resonances), so “additional planets around stars hosting hot Jupiters” became “additional planets close to hot Jupiters”",
         "second “and colleagues” replaced by the three named authors (Huang, Wu, Triaud)",
         "why_wrong for B and C rewritten: B keeps a roughly true first move; C also misstates who discovered the system and what the authors claim"],
}

with open(P + ".lock", "w") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    d = json.load(open(P))
    items = d["items"]
    todo = [i for i, it in enumerate(items) if it.get("review") is None]
    assert len(todo) == 16 and todo == list(range(16)), todo

    a = items[0]
    sub(a, "passage", "for the Vai language of present-day Liberia", "for the Vai language in present-day Liberia")
    sub(a, "passage", "into a syllabary of eighty characters", "into a syllabary of some eighty characters")
    sub(a, "passage", "And in the late 1980s, brothers", "In the late 1980s, brothers")
    a["sources"][1]["what"] += "; the article gives 80 characters in its lead and 82 plus 10 digits for the 1910 version, hence “some eighty”"

    b = items[4]
    sub(b, "passage", "and linked them by aerial walkways to new concrete towers.",
        "and beside them raised new concrete towers joined by aerial walkways.")
    b["sources"].append({"what": "a pair of new concrete towers housing sports facilities, connected to each other by eight pedestrian walkways; conversion 1977 to 1986; soccer teams and a theater company had occupied the building",
                         "url": "https://en.wikipedia.org/wiki/SESC_Pompeia"})

    c = items[15]
    sub(c, "passage", "for additional planets around stars hosting hot Jupiters,", "for additional planets close to hot Jupiters,")
    sub(c, "passage", "which Chelsea Huang and colleagues attribute", "which Chelsea Huang, Yanqin Wu, and Amaury Triaud attribute")
    sub(c, "explanation", "reports Steffen and colleagues’ observation that stars with hot Jupiters showed no other nearby planets",
        "reports Steffen and colleagues’ observation that no other planets showed up close to hot Jupiters")
    c["distractors"]["B"] = {"recipe": "later-move break: invented method improvement (INV)",
        "why_wrong": "The search did come up empty, but the text proposes no better method, and WASP-47b is presented as an exception explained by how it formed, not as a discovery made with an improved method."}
    c["distractors"]["C"] = {"recipe": "later-move break: stance flip and misattribution (STANCE/SWAP)",
        "why_wrong": "The first two moves are right, but the text does not treat WASP-47b as evidence against the migration account: Huang, Wu, and Triaud explain its neighbors by its having formed without that migration, which is what the account predicts. The text also never says they discovered the system."}

    for i in (0, 4, 15):
        items[i]["word_count"] = len(items[i]["passage"].split())

    for i in todo:
        it = items[i]
        ba = blind[f"q{i}"][0]
        it["review"] = {"blind_answer": ba, "agreed": ba == it["answer_letter"], "facts_checked": facts[i],
                        "fixes": fixes.get(i, []), "status": "fixed" if i in fixes else "pass"}
    with open(P, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    fcntl.flock(lk, fcntl.LOCK_UN)
print("ok")
