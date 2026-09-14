"""Render generated items to a page, so a human can look at them.

The gate proves an item is right. It cannot say whether the sentence reads
like an SAT sentence, whether the figure is legible, or whether the four
options look like four options. That needs eyes, and eyes need a page.

    PYTHONPATH=. python3 tools/preview.py <slug> [--per 3] [--out preview.html]
"""

from __future__ import annotations

import argparse
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from satbank.item import ItemError                                  # noqa: E402
from satbank.registry import generate                               # noqa: E402
from satbank.topic import load_topics                               # noqa: E402

CSS = """
body{font:15px/1.5 ui-sans-serif,system-ui,sans-serif;margin:0;padding:28px;
     background:#fbfbfa;color:#16150f}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:#6b6858;
   margin:28px 0 10px;border-bottom:1px solid #e3e0d4;padding-bottom:6px}
.item{background:#fff;border:1px solid #e3e0d4;border-radius:10px;padding:16px 18px;
      margin:0 0 14px;max-width:720px}
.meta{font:11px ui-monospace,SFMono-Regular,monospace;color:#8a8672;margin-bottom:8px}
.stem{margin:0 0 10px}
.fig{margin:6px 0 12px}
table{border-collapse:collapse;margin:8px 0 12px;font-size:14px}
td,th{border:1px solid #d8d4c4;padding:4px 10px;text-align:left}
ol{margin:0;padding-left:22px}
li{margin:3px 0}
li.key{font-weight:600}
li.key::marker{content:attr(data-l) ") "}
.why{color:#8a8672;font-size:13px;margin-left:8px}
.rat{margin-top:10px;font-size:13px;color:#55523f;border-top:1px dashed #e3e0d4;padding-top:8px}
.spr{font-weight:600}
"""


def render(slug: str, per: int, out: str) -> int:
    topic = load_topics()[slug]
    parts = [f'<meta charset="utf-8">',
             f"<title>{topic.name}</title><style>{CSS}</style>",
             f"<h1>{html.escape(topic.name)}</h1>",
             f"<div class=meta>{len(topic.templates)} templates &middot; {per} items each "
             f"&middot; {topic.domain}</div>"]
    for name in topic.templates:
        parts.append(f"<h2>{html.escape(name)}</h2>")
        shown = 0
        for seed in range(per * 40):
            if shown >= per:
                break
            try:
                it = generate(name, seed)
            except ItemError:
                continue
            shown += 1
            parts.append("<div class=item>")
            parts.append(f"<div class=meta>seed {it.seed} &middot; {it.difficulty} "
                         f"&middot; {it.fmt}</div>")
            parts.append(f"<p class=stem>{html.escape(it.stem)}</p>")
            if it.figure:
                parts.append(f"<div class=fig>{it.figure}</div>")
            if it.table:
                rows = "".join(
                    "<tr>" + "".join(f"<{'th' if i == 0 else 'td'}>{html.escape(str(c))}"
                                     f"</{'th' if i == 0 else 'td'}>" for c in row) + "</tr>"
                    for i, row in enumerate(it.table))
                parts.append(f"<table>{rows}</table>")
            if it.fmt == "spr":
                parts.append(f"<div class=spr>answer: {html.escape(it.answer)}</div>")
            else:
                lis = []
                for i, ch in enumerate(it.choices):
                    letter = "ABCD"[i]
                    why = it.reasons[i] or "the key"
                    cls = " class=key" if letter == it.answer else ""
                    lis.append(f"<li{cls} data-l='{letter}'>{html.escape(ch)}"
                               f"<span class=why>&larr; {html.escape(why)}</span></li>")
                parts.append("<ol type=A>" + "".join(lis) + "</ol>")
            parts.append(f"<div class=rat>{html.escape(it.rationale)}</div></div>")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("".join(parts))
    print(f"wrote {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--per", type=int, default=3)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    return render(a.slug, a.per, a.out or f"/tmp/preview-{a.slug}.html")


if __name__ == "__main__":
    sys.exit(main())
