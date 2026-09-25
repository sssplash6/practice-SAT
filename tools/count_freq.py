#!/usr/bin/env python3
"""Build the offline word-frequency table from pinned public-domain sources.

The manifest stores exact source URLs. Downloads are cached outside the repo so a
second run does not fetch the corpus again. The committed table is the offline
input to the Words build; running this script is only needed to refresh it.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools/data/freq_sources.txt"
OUTPUT = ROOT / "tools/data/freq.txt"
WORDS = ROOT / "server/words/sat.json"
TOKEN = re.compile(r"[a-z]+(?:'[a-z]+)?")
START = re.compile(r"(?im)^.*\*\*\*\s*START OF .*?PROJECT GUTENBERG EBOOK.*$")
END = re.compile(r"(?im)^.*\*\*\*\s*END OF .*?PROJECT GUTENBERG EBOOK.*$")
TARGET = {
    "nasa": ("class", "entry-content"),
    "noaa": ("class", "newspaper1"),
    "crs": ("id", "report-content"),
}


class ArticleText(HTMLParser):
    """Take only the article body, excluding site chrome and embedded code."""

    def __init__(self, kind: str):
        super().__init__(convert_charrefs=True)
        self.kind = kind
        self.depth = 0
        self.skip = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        props = dict(attrs)
        if self.depth:
            self.depth += 1
            if tag in {"script", "style", "nav", "footer", "aside"}:
                self.skip += 1
            return
        key, value = TARGET[self.kind]
        if value in (props.get(key) or "").split():
            self.depth = 1

    def handle_endtag(self, tag: str) -> None:
        if not self.depth:
            return
        if tag in {"script", "style", "nav", "footer", "aside"} and self.skip:
            self.skip -= 1
        self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.depth and not self.skip:
            self.chunks.append(data)


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        self.chunks.append(data)


def sources(path: Path) -> list[tuple[str, str, str]]:
    result = []
    seen = set()
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3 or parts[0] not in {"pg", "nsf", "nasa", "noaa", "crs"}:
            raise ValueError(f"{path}:{line_no}: expected kind, URL, label")
        kind, url, label = parts
        if not url.startswith("https://") or url in seen:
            raise ValueError(f"{path}:{line_no}: duplicate or non-HTTPS URL")
        seen.add(url)
        result.append((kind, url, label))
    return result


def download(source: tuple[str, str, str], cache: Path) -> tuple[str, Path]:
    kind, url, _ = source
    digest = hashlib.sha256(url.encode()).hexdigest()
    destination = cache / f"{digest}.{kind}"
    if not destination.is_file():
        partial = cache / f"{digest}.{os.getpid()}.tmp"
        try:
            completed = subprocess.run(
                ["curl", "--http1.1", "-fLsS", "--retry", "5", "--retry-delay", "1", "--max-time", "120",
                 "--user-agent", "satbank-frequency-builder/1.0", url, "-o", str(partial)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            if completed.returncode:
                raise RuntimeError(completed.stderr.decode(errors="replace").strip())
            if not partial.stat().st_size:
                raise ValueError("empty response")
            partial.replace(destination)
        except Exception:
            partial.unlink(missing_ok=True)
            raise
    return url, destination


def source_text(kind: str, payload: bytes) -> str:
    raw = payload.decode("utf-8-sig", errors="replace")
    if kind == "pg":
        start = START.search(raw)
        end = END.search(raw, start.end() if start else 0)
        if not start or not end:
            raise ValueError("missing Gutenberg start/end markers")
        return raw[start.end():end.start()]
    if kind == "nsf":
        awards = json.loads(raw)["response"]["award"]
        abstract = awards[0].get("abstractText") if awards else None
        if not abstract:
            raise ValueError("NSF award has no abstract")
        parser = PlainText()
        parser.feed(abstract)
        return " ".join(parser.chunks)
    parser = ArticleText(kind)
    parser.feed(raw)
    article = " ".join(parser.chunks)
    if len(article.split()) < 100:
        raise ValueError(f"article body too short ({len(article.split())} words)")
    return article


def count(text: str) -> Counter[str]:
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.encode("ascii", errors="ignore").decode("ascii").lower()
    return Counter(TOKEN.findall(text))


def band(rank: int | None) -> int:
    if rank is None:
        return 5
    for limit, level in ((3000, 1), (10000, 2), (25000, 3), (50000, 4)):
        if rank <= limit:
            return level
    return 5


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path(os.environ.get(
        "SATF_FREQ_CACHE", str(Path.home() / ".cache/satbank/frequency"))))
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    args.cache.mkdir(parents=True, exist_ok=True)
    manifest = sources(MANIFEST)
    print(f"Fetching {len(manifest)} pinned sources into {args.cache}", flush=True)
    paths: dict[str, Path] = {}
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        jobs = {executor.submit(download, source, args.cache): source for source in manifest}
        for number, job in enumerate(as_completed(jobs), 1):
            source = jobs[job]
            try:
                url, path = job.result()
            except Exception as exc:
                failures.append(f"{source[1]}: {exc}")
            else:
                paths[url] = path
            if number % 25 == 0 or number == len(manifest):
                print(f"Fetched {number}/{len(manifest)} ({len(failures)} failed)", flush=True)
    if failures:
        raise RuntimeError("Could not download:\n" + "\n".join(failures))

    frequencies: Counter[str] = Counter()
    by_kind: Counter[str] = Counter()
    for number, (kind, url, _) in enumerate(manifest, 1):
        try:
            text = source_text(kind, paths[url].read_bytes())
        except Exception as exc:
            raise RuntimeError(f"Could not parse {url}: {exc}") from exc
        local = count(text)
        frequencies.update(local)
        by_kind[kind] += sum(local.values())
        if number % 50 == 0 or number == len(manifest):
            print(f"Counted {number}/{len(manifest)}", flush=True)

    rows = sorted(((word, amount) for word, amount in frequencies.items() if amount >= 5),
                  key=lambda row: (-row[1], row[0]))
    output = "".join(f"{word} {amount}\n" for word, amount in rows)
    if len(output.encode()) >= 5_000_000:
        raise ValueError("freq.txt exceeds 5 MB; trim the rare-word tail explicitly")
    OUTPUT.write_text(output)
    ranks = {word: n for n, (word, _) in enumerate(rows, 1)}
    bands: Counter[int] = Counter()
    print("Corpus tokens:", dict(sorted(by_kind.items())), "total", sum(by_kind.values()))
    print(f"Wrote {len(rows)} words to {OUTPUT} ({len(output.encode())} bytes)")
    print("slug\tword\trank\tband")
    for entry in json.loads(WORDS.read_text()):
        word = entry["word"].lower()
        rank = ranks.get(word)
        level = band(rank)
        bands[level] += 1
        print(f"{entry['slug']}\t{word}\t{rank if rank is not None else 'unranked'}\t{level}")
    print("Band counts:", " ".join(f"{level}={bands[level]}" for level in range(1, 6)))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"frequency build failed: {exc}", file=sys.stderr)
        sys.exit(1)
