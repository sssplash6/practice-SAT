"""Render a sample set of authored R&W items to HTML (then Chrome prints it to PDF).
python3 build.py <out.html>   (run from the satbank repo root)"""
import glob, html, io, json, re, sys
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

PICK = [  # SAT module order: Craft and Structure, Information and Ideas, Conventions, Expression of Ideas
    "words_in_context.B2.easy", "words_in_context.M1.medium", "words_in_context.B5.hard",
    "text_structure_and_purpose.F_term.easy", "text_structure_and_purpose.P_lit.medium", "text_structure_and_purpose.S16_finding_pattern_exception.hard",
    "cross_text_connections.S1_refute_data.easy", "cross_text_connections.S2_shared_premise.medium", "cross_text_connections.S4_relate.hard",
    "central_ideas_and_details.T3.easy", "central_ideas_and_details.T4_poem.medium", "central_ideas_and_details.T6.hard",
    "command_of_evidence.T2_lit_quote.easy", "command_of_evidence.Q1_P3_pairwise.medium", "command_of_evidence.Q2_P8_quantifier.hard",
    "inferences.S1.easy", "inferences.S7.medium", "inferences.S11.hard",
    "boundaries.S1_comma_conj.easy", "boundaries.S3_dash_pair.medium", "boundaries.S5_series.hard",
    "form_structure_and_sense.R4_past_dated.easy", "form_structure_and_sense.R3_past_participle.medium", "form_structure_and_sense.R6_grid.hard",
    "transitions.C1_two_subject.easy", "transitions.E1_consequence.medium", "transitions.K1_grant_turn.hard",
    "rhetorical_synthesis.SIM.easy", "rhetorical_synthesis.QUOTE.medium", "rhetorical_synthesis.NARR.hard",
]
SKILL = {"words_in_context": "Words in Context", "text_structure_and_purpose": "Text Structure and Purpose",
         "cross_text_connections": "Cross-Text Connections", "central_ideas_and_details": "Central Ideas and Details",
         "command_of_evidence": "Command of Evidence", "inferences": "Inferences", "boundaries": "Boundaries",
         "form_structure_and_sense": "Form, Structure, and Sense", "transitions": "Transitions",
         "rhetorical_synthesis": "Rhetorical Synthesis"}

items = {}
for p in glob.glob("satbank/rw/*.json"):
    for i in json.load(open(p))["items"]:
        items[i["id"]] = i


def inline(s):
    s = html.escape(s, quote=False).replace("&lt;u&gt;", "<u>").replace("&lt;/u&gt;", "</u>")
    return s.replace("______", '<span class="blank"></span>')


def passage(p):
    out = []
    for para in p.split("\n\n"):
        lines = para.split("\n")
        if para in ("Text 1", "Text 2"):
            out.append(f'<p class="texthead">{para}</p>')
        elif any(l.startswith("• ") for l in lines):
            head = [l for l in lines if not l.startswith("• ")]
            out += [f"<p>{inline(h)}</p>" for h in head]
            out.append("<ul>" + "".join(f"<li>{inline(l[2:])}</li>" for l in lines if l.startswith("• ")) + "</ul>")
        else:
            out.append("<p>" + "<br>".join(inline(l) for l in lines) + "</p>")
    return "\n".join(out)


def table(t):
    head = "".join(f"<th>{inline(c)}</th>" for c in t["columns"])
    rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in t["rows"])
    note = f'<p class="note">{inline(t["note"])}</p>' if t.get("note") else ""
    return f'<p class="ftitle">{inline(t.get("title") or "")}</p><table>{head and "<tr>" + head + "</tr>"}{rows}</table>{note}'


def figure(f):
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    series = f.get("data") or []
    if f.get("kind", "").startswith("bar"):
        cats = [str(x) for x, _ in series[0]["points"]]
        w = 0.8 / len(series)
        shades = ["#bbbbbb", "#555555", "#888888", "#222222"]
        for k, s in enumerate(series):
            ax.bar([j + (k - (len(series) - 1) / 2) * w for j in range(len(cats))], [y for _, y in s["points"]],
                   w, label=s["series"], color=shades[k % 4], edgecolor="black", linewidth=0.5)
        ax.set_xticks(range(len(cats)), cats)
    else:
        marks = ["^", "s", "o", "D"]
        styles = ["-", "--", ":", "-."]
        for k, s in enumerate(series):
            ax.plot([x for x, _ in s["points"]], [y for _, y in s["points"]], styles[k % 4], marker=marks[k % 4],
                    color="black", label=s["series"])
    ax.set_xlabel(f.get("x_axis") or "")
    ax.set_ylabel(f.get("y_axis") or "", fontsize=8)
    ax.grid(axis="y", color="#dddddd", linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if len(series) > 1:
        ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    buf = io.StringIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
    svg = re.sub(r"^.*?(<svg)", r"\1", buf.getvalue(), flags=re.S)
    return f'<p class="ftitle">{inline(f.get("title") or "")}</p><div class="fig">{svg}</div>'


def status(i):
    if "rewrite" in i and i.get("review"):
        return "rewritten for fidelity, reviewed"
    if "rewrite" in i:
        return "rewritten for fidelity, review in progress"
    return "first version, reviewed (fidelity rewrite pending)"


CSS = """
@page { size: Letter; margin: 0.7in 0.75in; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.45; color: #111; }
h1 { font-family: -apple-system, Helvetica, sans-serif; font-size: 20pt; margin: 0 0 4pt; }
h2 { font-family: -apple-system, Helvetica, sans-serif; font-size: 14pt; margin: 0 0 10pt; page-break-before: always; }
.intro { font-family: -apple-system, Helvetica, sans-serif; font-size: 9.5pt; color: #444; margin-bottom: 14pt; }
.q { break-inside: avoid; border-top: 1px solid #999; padding: 10pt 0 6pt; }
.meta { font-family: -apple-system, Helvetica, sans-serif; font-size: 8.5pt; color: #666; margin-bottom: 6pt; }
.num { display: inline-block; min-width: 18pt; padding: 1pt 4pt; margin-right: 6pt; background: #111; color: #fff;
       font-family: -apple-system, Helvetica, sans-serif; font-size: 9pt; font-weight: 600; text-align: center; }
.passage p { margin: 0 0 6pt; }
.passage ul { margin: 0 0 6pt 14pt; padding: 0; }
.texthead { font-weight: bold; margin-top: 8pt !important; }
.blank { display: inline-block; width: 60pt; border-bottom: 1px solid #111; vertical-align: baseline; }
.stem { font-weight: bold; margin: 8pt 0 4pt; }
.opts { list-style: none; padding: 0; margin: 0; }
.opts li { margin: 0 0 3pt 0; padding-left: 20pt; text-indent: -20pt; }
table { border-collapse: collapse; margin: 4pt auto 8pt; font-family: -apple-system, Helvetica, sans-serif; font-size: 8.5pt; }
th, td { border: 1px solid #555; padding: 3pt 6pt; text-align: center; }
th { background: #eee; }
.ftitle { text-align: center; font-family: -apple-system, Helvetica, sans-serif; font-weight: 600; font-size: 9pt; margin: 8pt 0 2pt; }
.fig { text-align: center; } .fig svg { width: 5.4in; height: auto; }
.note { font-size: 8.5pt; }
.k { break-inside: avoid; border-top: 1px solid #ccc; padding: 7pt 0 3pt; font-size: 9.5pt; }
.k p { margin: 0 0 4pt; }
.small { font-family: -apple-system, Helvetica, sans-serif; font-size: 8pt; color: #666; margin-left: 6pt; }
.wrong { margin: 0 0 0 14pt; padding: 0; }
"""


def main(out):
    qs, keys = [], []
    for n, k in enumerate(PICK, 1):
        i = items[k]
        slug = k.split(".")[0]
        tier = i["tier"].capitalize()
        body = passage(i["passage"])
        if i.get("table"):
            body += table(i["table"])
        if i.get("figure"):
            body += figure(i["figure"])
        opts = "".join(f'<li><b>{l})</b> {inline(o)}</li>' for l, o in zip("ABCD", i["options"]))
        qs.append(f'<section class="q"><div class="meta"><span class="num">{n}</span>{SKILL[slug]} · {tier}</div>'
                  f'<div class="passage">{body}</div><p class="stem">{inline(i["stem"])}</p><ol class="opts">{opts}</ol></section>')
        wrong = "".join(f'<li><b>{l}:</b> {inline(d["why_wrong"])}</li>' for l, d in sorted(i["distractors"].items()))
        keys.append(f'<section class="k"><p><span class="num">{n}</span><b>Answer: {i["answer_letter"]}</b>'
                    f' <span class="small">{SKILL[slug]} · {tier} · {status(i)}</span></p>'
                    f'<p>{inline(i["explanation"])}</p><ul class="wrong">{wrong}</ul></section>')

    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>SAT Reading and Writing: Sample Set</title><style>{CSS}</style></head><body>
    <h1>SAT Reading and Writing: Sample Set</h1>
    <p class="intro">30 original questions written for SAT Freshman: all 10 skills, one easy, one medium and one hard question each, in the order the digital SAT uses (Craft and Structure, Information and Ideas, Standard English Conventions, Expression of Ideas). The answer key with explanations starts after question 30.</p>
    {''.join(qs)}
    <h2>Answer key and explanations</h2>
    {''.join(keys)}
    </body></html>"""
    open(out, "w").write(doc)
    print("ok", len(PICK))


if __name__ == "__main__":
    main(sys.argv[1])
