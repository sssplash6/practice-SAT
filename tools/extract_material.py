"""Turn the College Board PDFs in material/ into the two things a topic author needs:

  material/keys/<topic>.json   the answer key, read from the PDF's own text layer
  material/items/<topic>/<tier>/<n>.jpg   one image per question, in key order

The questions are page images; only the key table is text. Every question in a
file is exactly one embedded image, in document order, so image n is item n.
The extraction refuses to write a topic whose image count and key-row count
disagree -- a silent off-by-one would mis-key every item after it.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATERIAL = os.path.join(HERE, "material")
KEYS = os.path.join(MATERIAL, "keys")
ITEMS = os.path.join(MATERIAL, "items")

TIER = {"1": "easy", "2": "medium", "3": "hard"}


def slug(topic: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")


def key_rows(pdf: str) -> list[dict]:
    txt = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
    toks = [t.strip() for t in txt.splitlines() if t.strip()]
    rows, i = [], 0
    headers = {"Answer", "Question #", "ID"}
    while i < len(toks) - 2:
        if re.fullmatch(r"\d+\.\d+", toks[i]) and re.fullmatch(r"[0-9a-f]{8}", toks[i + 1]):
            # a page break can float the "Answer" column header between the id
            # and its answer; the header is never an answer, so step over it
            j = i + 2
            while j < len(toks) and toks[j] in headers:
                j += 1
            # a grid-in may list every acceptable answer, one per line:
            # "10/3," "15/4," "25/6". A trailing comma means it continues.
            answer = toks[j]
            while answer.rstrip().endswith(",") and j + 1 < len(toks):
                j += 1
                answer += " " + toks[j]
            rows.append({"id": toks[i], "cb_id": toks[i + 1], "answer": answer})
            i = j + 1
        else:
            i += 1
    return rows


def images(pdf: str, out_dir: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run(["pdfimages", "-j", "-p", pdf, os.path.join(out_dir, "img")], check=True)
    return sorted(f for f in os.listdir(out_dir) if f.startswith("img"))


def main() -> int:
    keys_only = "--keys-only" in sys.argv
    os.makedirs(KEYS, exist_ok=True)
    pdfs = sorted(f for f in os.listdir(MATERIAL) if f.endswith(".pdf"))
    by_topic: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for f in pdfs:
        m = re.fullmatch(r"(.+) ([123])~Key\.pdf", f)
        if not m:
            print(f"  skipped (unrecognised name): {f}")
            continue
        by_topic[m.group(1)].append((TIER[m.group(2)], f))

    summary = []
    for topic, files in sorted(by_topic.items()):
        s = slug(topic)
        key = {"topic": topic, "slug": s, "items": []}
        for tier, f in sorted(files, key=lambda t: ("easy", "medium", "hard").index(t[0])):
            pdf = os.path.join(MATERIAL, f)
            rows = key_rows(pdf)
            out_dir = os.path.join(ITEMS, s, tier)
            if keys_only:
                imgs = sorted(os.listdir(out_dir)) if os.path.isdir(out_dir) else []
            else:
                shutil.rmtree(out_dir, ignore_errors=True)
                imgs = images(pdf, out_dir)
            if len(imgs) != len(rows):
                print(f"  !! {f}: {len(rows)} key rows but {len(imgs)} images -- "
                      "not writing, the mapping cannot be trusted")
                return 1
            for row, img in zip(rows, imgs):
                ext = os.path.splitext(img)[1]
                dest = f"{row['id'].replace('.', '-')}{ext}"
                if not keys_only:
                    os.rename(os.path.join(out_dir, img), os.path.join(out_dir, dest))
                key["items"].append({**row, "tier": tier,
                                     "image": f"material/items/{s}/{tier}/{dest}"})
        with open(os.path.join(KEYS, f"{s}.json"), "w") as fh:
            json.dump(key, fh, indent=2)
        summary.append((topic, s, len(key["items"])))
        print(f"  {topic:<40} {len(key['items']):3d} items -> material/keys/{s}.json")

    print(f"\n{len(summary)} topics, {sum(n for _, _, n in summary)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
