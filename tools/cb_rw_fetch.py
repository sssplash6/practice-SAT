"""Fetch every Reading and Writing question from the public College Board Educator
Question Bank (permission: see material/cb/cb_index.json) as text, with key,
CB rationale, tier and 1 to 7 score band. Run from the repo root:

  python3 tools/cb_rw_fetch.py   (python.org builds on macOS may lack CA certs: use /usr/bin/python3)

Raw responses are cached in material/rw/cb_api/raw/<cb_id>.json (reruns only fetch
what is missing); the readable set is material/rw/cb_api/<skill_slug>.json.
Nothing here ships in the product."""

import html
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/"
OUT = "material/rw/cb_api"
RAW = f"{OUT}/raw"
TIER = {"E": "easy", "M": "medium", "H": "hard"}


def post(path, body):
    req = urllib.request.Request(API + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))


def text(h):
    """CB html to the transcript conventions: paragraphs \\n\\n, <u> kept, blank ______."""
    h = re.sub(r'<span class="sr-only">.*?</span>', "", h or "", flags=re.S)
    h = re.sub(r"<(/?)u>", r"[[\1u]]", h)
    h = re.sub(r"<br\s*/?>", "\n", h)
    h = re.sub(r"</(p|li|tr|h\d|figcaption|caption)>", "\n\n", h)
    h = re.sub(r"<li[^>]*>", "• ", h)
    h = re.sub(r"</t[dh]>", " | ", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = html.unescape(h).replace("[[u]]", "<u>").replace("[[/u]]", "</u>").replace("\xa0", " ")
    h = re.sub(r"[ \t]+", " ", h)
    return re.sub(r"\n\s*\n+", "\n\n", h).strip()


def fetch(meta):
    path = f"{RAW}/{meta['questionId']}.json"
    if not os.path.exists(path):
        d = post("get-question", {"external_id": meta["external_id"]})
        json.dump(d, open(path, "w"), ensure_ascii=False)
    return meta, json.load(open(path))


def main():
    os.makedirs(RAW, exist_ok=True)
    metas = post("get-questions", {"asmtEventId": 99, "test": 1, "domain": "INI,CAS,EOI,SEC"})
    with ThreadPoolExecutor(4) as ex:                 # polite: 4 requests at a time
        got = list(ex.map(fetch, metas))
    by = {}
    for m, d in got:
        ids = [o["id"] for o in d["answerOptions"]]
        key = "ABCD"[ids.index(d["keys"][0])]
        stim = d.get("stimulus") or ""
        by.setdefault(re.sub(r"[^a-z0-9]+", "_", m["skill_desc"].lower()).strip("_"), []).append({
            "cb_id": m["questionId"], "tier": TIER[m["difficulty"]], "band": m["score_band_range_cd"],
            "passage": text(stim), "stem": text(d["stem"]), "options": [text(o["content"]) for o in d["answerOptions"]],
            "answer_letter": key, "rationale": text(d["rationale"]),
            "has_table": "<table" in stim, "has_figure": bool(re.search(r"<(img|svg)", stim)),
        })
    for slug, items in by.items():
        items.sort(key=lambda i: (i["band"], i["cb_id"]))
        json.dump({"source": API + "get-question", "fetched": time.strftime("%Y-%m-%d"), "items": items},
                  open(f"{OUT}/{slug}.json", "w"), indent=2, ensure_ascii=False)
        print(f"{slug:28} {len(items):4}  band 7: {sum(i['band'] == 7 for i in items)}")


if __name__ == "__main__":
    sys.exit(main())
