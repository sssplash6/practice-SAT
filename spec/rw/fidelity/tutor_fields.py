"""Make a tutor panel PDF fillable, and read the answers back out of returned copies.

    python3 spec/rw/fidelity/tutor_fields.py add panel1            # adds fields to tutors/panel1/SAT_RW_Tutor_Panel.pdf
    python3 spec/rw/fidelity/tutor_fields.py read panel1 a.pdf ... # one JSON list per tutor, in score.py's format

Fields sit on the boxes Chrome drew under each question (6 per question: 5 ratings and seen) plus a text field on the Why line. Checkboxes, not radio buttons: generated radio
groups share one on-state and toggle together in some viewers. Ticking two ratings averages them.
"""
import json, os, sys
import pymupdf as fz

HERE = os.path.dirname(os.path.abspath(__file__))


def boxes(doc):
    """Rating boxes per question, in reading order, from the question pages only."""
    out = []
    for page in doc:
        if page.search_for("Seen: tick"):            # the answer grid: its cells are not questions
            break
        rs = [it[1] for d in page.get_drawings() for it in d["items"]
              if it[0] == "re" and 6 < it[1].width < 12 and 6 < it[1].height < 12]
        out += [(page, r) for r in sorted(rs, key=lambda r: (round(r.y0), r.x0))]
    assert len(out) % 6 == 0, f"{len(out)} boxes is not 6 per question"
    return [out[i:i + 6] for i in range(0, len(out), 6)]


def add(path):
    doc = fz.open(path)
    for n, row in enumerate(boxes(doc), 1):
        names = [f"q{n}_r{k}" for k in range(1, 6)] + [f"q{n}_seen"]
        page = row[0][0]
        for (_, r), name in zip(row, names):
            w = fz.Widget()
            w.field_type, w.field_name, w.rect = fz.PDF_WIDGET_TYPE_CHECKBOX, name, r
            w.border_width, w.field_value = 0, False
            page.add_widget(w)
        y = row[0][1].y1
        why = [r for r in page.search_for("Why:") if y < r.y0 < y + 30]
        assert why, f"no Why line under question {n}"
        w = fz.Widget()
        w.field_type, w.field_name = fz.PDF_WIDGET_TYPE_TEXT, f"q{n}_why"
        w.rect = fz.Rect(why[0].x1 + 4, why[0].y0 - 2, page.rect.width - 54, why[0].y1 + 3)
        w.text_fontsize, w.border_width = 8, 0
        page.add_widget(w)
    doc.save(path, incremental=True, encryption=fz.PDF_ENCRYPT_KEEP)
    return n


def read(path):
    """Answers as score.py's judged list: p_imitation from the 1 to 5 rating, recognized from Seen."""
    v = {w.field_name: w.field_value for page in fz.open(path) for w in page.widgets()}
    out, n = [], 1
    while f"q{n}_r1" in v:
        ticked = [k for k in range(1, 6) if v[f"q{n}_r{k}"] not in (False, "Off", "")]
        if ticked:
            out.append({"item": n, "p_imitation": (sum(ticked) / len(ticked) - 1) / 4,
                        "recognized": v[f"q{n}_seen"] not in (False, "Off", ""),
                        "tell": v.get(f"q{n}_why") or ""})
        n += 1
    return out


def demo(path):
    """Fill a copy the way a tutor would, then read it back."""
    tmp = path + ".check.pdf"
    doc = fz.open(path)
    for page in doc:
        for w in page.widgets():
            if w.field_name in ("q1_r4", "q2_r1", "q2_seen"):
                w.field_value = w.on_state()
                w.update()
            if w.field_name == "q1_why":
                w.field_value = "too many exact figures"
                w.update()
    doc.save(tmp)
    got = {x["item"]: x for x in read(tmp)}
    os.remove(tmp)
    assert got[1]["p_imitation"] == 0.75 and got[1]["tell"] == "too many exact figures"
    assert got[2]["p_imitation"] == 0 and got[2]["recognized"] and 3 not in got


if __name__ == "__main__":
    cmd, panel = sys.argv[1], f"{HERE}/tutors/{sys.argv[2]}"
    pdf = f"{panel}/SAT_RW_Tutor_Panel.pdf"
    if cmd == "add":
        print(add(pdf), "questions made fillable")
        demo(pdf)
        print("read-back check ok")
    else:
        for p in sys.argv[3:]:
            print(json.dumps(read(p)))
