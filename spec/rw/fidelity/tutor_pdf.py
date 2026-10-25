"""Tutor panel: 40 of our items and 45 official ones, shuffled and rendered alike, for
tutors to rate (official or new, seen before). Run from the repo root:
python3 spec/rw/fidelity/tutor_pdf.py <panel name>; then print tutors/<panel>/panel.html to PDF with headless Chrome
and make it fillable with tutor_fields.py add <panel>.
The answer key (which items are ours) goes to tutors/<panel>/key.json, never into the PDF; an existing panel is never overwritten.
Items with graphs are left out of both sides: official graphs exist only as scans."""
import glob, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sample_pdf import CSS, SKILL, inline, passage, table

HERE = os.path.dirname(os.path.abspath(__file__))
OURS, OFF = 4, 4                                  # per skill
EXTRA = ["command_of_evidence", "words_in_context", "boundaries", "form_structure_and_sense", "rhetorical_synthesis"]
TIERS = ("easy", "medium", "hard")
rng = random.Random("tutor-panel-1")

ours, off = {}, {}
for p in glob.glob("satbank/rw/*.json"):
    d = json.load(open(p))
    ours.setdefault(d["slug"], []).extend(i for i in d["items"] if not i.get("figure"))
# official items whose key is not CB's, that look broken, or that are filed under the wrong skill (spec/rw/README.md)
BAD = re.compile(r"solved by reading|Not in the College Board question bank index|no underlining")
for p in glob.glob("material/rw/transcripts/*.json"):
    d = json.load(open(p))
    off[d["slug"]] = [i for i in d["items"] if not i.get("figure") and not i["cb_id"].startswith("abcd")
                      and not BAD.search(i.get("notes") or "") and (d["slug"], i["id"]) != ("central_ideas_and_details", "3.15")]
seen = set()                                      # officials an AI judge recognised: likely well known
for r in ("round1", "round2"):
    for kp in glob.glob(f"{HERE}/{r}/keys/*.json"):
        slug = os.path.basename(kp)[:-5]
        j = {x["item"]: x for x in json.load(open(f"{HERE}/{r}/judged/{slug}.json"))}
        seen |= {(slug, k["id"]) for k in json.load(open(kp)) if k["truth"] == "official" and j[k["item"]].get("recognized")}

pool = []
for slug in sorted(SKILL):
    tiers = list(TIERS) + [rng.choice(TIERS)]     # one of each tier, then one more
    mine = []
    for t in tiers:
        cand = [i for i in ours[slug] if i["tier"] == t and i not in mine] or [i for i in ours[slug] if i not in mine]
        fresh = [i for i in cand if i["template"] not in {m["template"] for m in mine}]   # no template twice
        mine.append(rng.choice(fresh or cand))
    models = {m for i in mine for m in i.get("models", [])}
    picked = []
    for t in tiers[:OFF] + ([rng.choice(TIERS)] if slug in EXTRA else []):
        cand = [i for i in off[slug] if i["tier"] == t and i not in picked] or [i for i in off[slug] if i not in picked]
        rng.shuffle(cand)
        cand.sort(key=lambda i: ((slug, i["id"]) in seen) + (i["id"] in models))
        picked.append(cand[0])
    pool += [("ours", slug, i) for i in mine] + [("official", slug, i) for i in picked]
rng.shuffle(pool)
half = (len(pool) + 1) // 2

BOX = '<span class="box"></span>'
qs, key = [], []
for n, (truth, slug, i) in enumerate(pool, 1):
    body = passage(i["passage"]) + (table(i["table"]) if i.get("table") else "")
    opts = "".join(f'<li><b>{l})</b> {inline(o)}</li>' for l, o in zip("ABCD", i["options"]))
    head = '<h2>Part 2</h2>' if n == half + 1 else ""
    qs.append(f'{head}<section class="q"><div class="meta"><span class="num">{n}</span>{SKILL[slug]} · {i["tier"].capitalize()}'
              f'<span class="key">Key: {i["answer_letter"]}</span></div>'
              f'<div class="passage">{body}</div><p class="stem">{inline(i["stem"])}</p><ol class="opts">{opts}</ol>'
              f'<div class="rate"><b>Official</b> {" ".join(f"{BOX}{k}" for k in range(1, 6))} <b>New</b>'
              f'<span class="gap"></span>{BOX}Seen before</div><div class="why">Why:</div></section>')
    key.append({"item": n, "truth": truth, "id": i["id"], "skill": slug, "tier": i["tier"]})

rows = lambda a, b: "".join(f"<tr><td>{n}</td><td></td><td></td><td></td></tr>" for n in range(a, b))
th = "<tr><th>#</th><th>1 to 5</th><th>Seen</th><th>Why</th></tr>"
grid = f"<table>{th}{rows(1, half + 1)}</table><table>{th}{rows(half + 1, len(pool) + 1)}</table>"
EXTRA_CSS = """
.key { float: right; color: #444; }
.rate { font-family: -apple-system, Helvetica, sans-serif; font-size: 8.5pt; margin-top: 6pt; }
.box { display: inline-block; width: 8pt; height: 8pt; border: 1px solid #333; margin: 0 2pt 0 5pt; vertical-align: -1pt; }
.gap { display: inline-block; width: 14pt; }
.why { font-family: -apple-system, Helvetica, sans-serif; font-size: 8.5pt; border-bottom: 1px solid #999; height: 16pt; margin-top: 4pt; }
.intro li { margin-bottom: 4pt; }
.grid { display: flex; gap: 18pt; align-items: flex-start; }
.grid table { width: 50%; margin: 0; font-size: 8pt; }
.grid td:last-child { width: 45%; }
.grid td { height: 13pt; padding: 0 4pt; }
"""
doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>SAT Reading and Writing: Tutor Panel</title>
<style>{CSS}{EXTRA_CSS}</style></head><body>
<h1>SAT Reading and Writing: Tutor Panel</h1>
<div class="intro"><p>This set mixes official College Board questions with new questions we wrote to the same specifications.
How many of each is not fixed, so judge every question on its own. It takes about two hours; Part 2 starts at question {half + 1}, so you can do it in two sittings.</p>
<ol>
<li><b>Official or new:</b> 1 means you are sure it is an official College Board question, 5 that you are sure it is new, 3 that you cannot tell.</li>
<li><b>Seen before:</b> tick it if you remember this exact question from the College Board question bank, Bluebook or any prep material.</li>
<li><b>Why:</b> one line on what decided it (topic, wording, answer choices, difficulty, anything). This is the most useful part.</li>
</ol>
<p>Formatting has been made the same for every question, so ignore layout, and ignore small typos that look like copying errors: judge the question itself.
Please do not look questions up online or discuss them until you have finished. The key for each question is shown next to its number.
You can fill this PDF in on screen: click the boxes (tick one rating), type in the Why line, then save the file and send it back. If you print it instead, copy your answers into the answer grid on the last pages and send a photo.</p></div>
{''.join(qs)}
<h2>Answer grid</h2>
<p class="intro">Official or new: 1 to 5. Seen: tick.</p>
<div class="grid">{grid}</div>
</body></html>"""
panel = f"{HERE}/tutors/{sys.argv[1]}"
if os.path.exists(f"{panel}/key.json"):
    sys.exit(f"{panel} exists: a sent panel must keep matching its key; pick a new name")
os.makedirs(panel)
open(f"{panel}/panel.html", "w").write(doc)
json.dump(key, open(f"{panel}/key.json", "w"), indent=1)
print(len(pool), "items:", sum(k["truth"] == "ours" for k in key), "ours,", sum(k["truth"] == "official" for k in key), "official; part 2 from", half + 1)
