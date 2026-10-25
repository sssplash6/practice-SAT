import fcntl, json
P = "satbank/rw/words_in_context.json"
W = "spec/rw/fidelity/work/verify_words_in_context/"

def sub(obj, field, old, new):
    assert obj[field].count(old) == 1, (field, old)
    obj[field] = obj[field].replace(old, new)

blind = json.load(open(W + "blind_answers.json"))
facts = {"B1.easy": 6, "B2.easy": 6, "B3.easy": 6, "B4.easy": 5, "B5.easy": 5, "B6.easy": 5,
         "B1.medium": 6, "B2.medium": 6, "B3.medium": 4, "B4.medium": 7, "B5.medium": 5, "B6.medium": 4,
         "B1.hard": 5, "B2.hard": 7, "B3.hard": 5, "B4.hard": 6, "B5.hard": 5, "B6.hard": 5, "M1.hard": 5}
fixes = {
    "B4.medium": ["“For Every One (2018), his instructional video ...” read as a work titled “For Every One” once italics are lost; "
                  "now “The installation Every One (2018) began with an instructional video inviting ...” (MAD release: the installation began as an instructional video)"],
    "B2.hard": ["“members of a work team” and “teammates” implied joint production; the paper stresses three-worker production units with "
                "no joint production (NBER w22491, p. 3), so now “the three workers in a production unit” and “co-workers”"],
}

with open(P + ".lock", "w") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    d = json.load(open(P))
    todo = {it["id"].split(".", 1)[1]: it for it in d["items"] if it.get("review") is None}
    assert sorted(todo) == sorted(facts), sorted(todo)

    a = todo["B4.medium"]
    sub(a, "passage", "For Every One (2018), his instructional video invited communities",
        "The installation Every One (2018) began with an instructional video inviting communities")
    sub(a, "passage", "two-inch clay beads, and Luger strung about", "two-inch clay beads; Luger then strung about")

    b = todo["B2.hard"]
    sub(b, "passage", "paying the members of a work team different wages lowered the output of the lowest-paid members",
        "paying the three workers in a production unit different wages lowered the output of the lowest-paid worker")
    sub(b, "passage", "better-paid teammates", "better-paid co-workers")
    sub(b, "explanation", "better-paid teammates", "better-paid co-workers")
    b["distractors"]["D"]["why_wrong"] = b["distractors"]["D"]["why_wrong"].replace("teammates’", "co-workers’")
    assert "teammate" not in json.dumps(b, ensure_ascii=False)
    b["sources"][0]["what"] += "; workers sit in three-worker production units, production individual (p. 3)"

    for k, it in todo.items():
        it["word_count"] = len(it["passage"].split())
        ans = blind["words_in_context." + k][0]
        it["review"] = {"blind_answer": ans, "agreed": ans == it["answer_letter"], "facts_checked": facts[k],
                        "fixes": fixes.get(k, []), "status": "fixed" if k in fixes else "pass"}

    tmp = P + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    import os; os.replace(tmp, P)
print("ok")
