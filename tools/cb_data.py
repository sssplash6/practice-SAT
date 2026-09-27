"""Collect public College Board metadata and import a Student Bank UI snapshot.

Fetches are cached outside this repository and spaced at least one second apart.
The committed outputs contain metadata only: no question stems, answers, or explanations.
The Student Bank importer reads an already captured table snapshot; it never
handles an account, credential, or authenticated HTTP request.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "material" / "cb"
CACHE = Path(os.environ.get("SATF_CB_CACHE", Path.home() / ".cache" / "satbank-cb-data"))
ALLOWED_HOSTS = {
    "satsuite.collegeboard.org", "research.collegeboard.org",
    "privacy.collegeboard.org", "satsuitequestionbank.collegeboard.org",
    "satsuiteeducatorquestionbank.collegeboard.org", "qbank-api.collegeboard.org",
}
USER_AGENT = "satbank-cb-data/1.0 (public metadata collection; no account access)"
PERMISSION = "College Board, by phone to the user, 2026-09-27; written confirmation pending"
QB = "https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank"
LOOKUP = QB + "/lookup"
QUESTIONS = QB + "/digital/get-questions"
BANK_PAGE = "https://satsuiteeducatorquestionbank.collegeboard.org/digital/search"
BANK_RESULTS = "https://satsuiteeducatorquestionbank.collegeboard.org/digital/results"
PERCENTILES = "https://research.collegeboard.org/reports/sat-suite/understanding-scores/sat"
RW_SPEC = "https://satsuite.collegeboard.org/k12-educators/about/alignment/reading"
MATH_SPEC = "https://satsuite.collegeboard.org/k12-educators/about/alignment/math"
DOMAINS = "https://satsuite.collegeboard.org/practice/content-domains"
DATES = "https://satsuite.collegeboard.org/sat/dates-deadlines"
SCORES = "https://satsuite.collegeboard.org/scores/score-release-dates"
TRADEMARKS = "https://privacy.collegeboard.org/copyright-trademark/guidelines"
MARK_LIST = "https://privacy.collegeboard.org/copyright-trademark/college-board"
COPYRIGHT = "https://privacy.collegeboard.org/copyright-trademark/request-instructions"
STUDENT_BANK = "https://satsuite.collegeboard.org/practice/student-question-bank"
STUDENT_RESULTS = "https://mypractice.collegeboard.org/questionbank/results"
ALLOWED_URLS = {BANK_PAGE, LOOKUP, QUESTIONS, PERCENTILES, RW_SPEC, MATH_SPEC,
                DOMAINS, DATES, SCORES, TRADEMARKS, MARK_LIST, COPYRIGHT, STUDENT_BANK}


def fetch(url: str, *, refresh: bool = False, payload: dict | None = None) -> tuple[bytes, dict]:
    parsed = urlparse(url)
    if url not in ALLOWED_URLS or parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"not an allowed public College Board URL: {url}")
    if CACHE.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("SATF_CB_CACHE must be outside the repository")
    CACHE.mkdir(parents=True, exist_ok=True)
    request_key = url + (json.dumps(payload, sort_keys=True) if payload is not None else "")
    key = hashlib.sha256(request_key.encode()).hexdigest()
    body_file, meta_file = CACHE / f"{key}.body", CACHE / f"{key}.json"
    if body_file.exists() and meta_file.exists() and not refresh:
        return body_file.read_bytes(), json.loads(meta_file.read_text())
    stamp = CACHE / "last_request"
    with stamp.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        lock.seek(0)
        previous = lock.read().strip()
        if previous:
            wait = 1.0 - (time.time() - float(previous))
            if wait > 0:
                time.sleep(wait)
        lock.seek(0)
        lock.truncate()
        lock.write(str(time.time()))
        lock.flush()
        fcntl.flock(lock, fcntl.LOCK_UN)
    headers = {"User-Agent": USER_AGENT}
    response = (requests.post(url, json=payload, headers=headers, timeout=30,
                              allow_redirects=True) if payload is not None else
                requests.get(url, headers=headers, timeout=30, allow_redirects=True))
    final = urlparse(response.url)
    if final.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"request redirected outside approved hosts: {response.url}")
    response.raise_for_status()
    meta = {"requested_url": url, "url": response.url,
            "method": "POST" if payload is not None else "GET",
            **({"payload": payload} if payload is not None else {}),
            "fetched": dt.datetime.now(dt.timezone.utc).date().isoformat(),
            "status": response.status_code,
            "content_type": response.headers.get("Content-Type", "")}
    body_file.write_bytes(response.content)
    meta_file.write_text(json.dumps(meta, indent=2) + "\n")
    return response.content, meta


def source(*metas: dict) -> dict:
    return {"permission": PERMISSION,
            "fetched_timezone": "UTC",
            "urls": [{"url": meta["url"], "fetched": meta["fetched"]} for meta in metas]}


def html(url: str, refresh: bool) -> tuple[BeautifulSoup, dict]:
    body, meta = fetch(url, refresh=refresh)
    return BeautifulSoup(body, "html.parser"), meta


def save(name: str, data: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def index(refresh: bool) -> tuple[dict, dict]:
    _, page_meta = html(BANK_PAGE, refresh)
    _, student_meta = html(STUDENT_BANK, refresh)
    lookup_bytes, lookup_meta = fetch(LOOKUP, refresh=refresh)
    lookup = json.loads(lookup_bytes)["lookupData"]
    assessment = next(x for x in lookup["assessment"] if x["text"] == "SAT")
    items: dict[str, dict] = {}
    metas = [page_meta, student_meta, lookup_meta]
    for subject, test_id, domain_key in (("rw", 1, "R&W"), ("math", 2, "Math")):
        domain = ",".join(x["primaryClassCd"] for x in lookup["domain"][domain_key])
        body, meta = fetch(QUESTIONS, refresh=refresh,
                           payload={"asmtEventId": int(assessment["id"]),
                                    "test": test_id, "domain": domain})
        metas.append(meta)
        rows = json.loads(body)
        for row in rows:
            cb_id = row["questionId"]
            band = row["score_band_range_cd"]
            tier = {"E": "easy", "M": "medium", "H": "hard"}[row["difficulty"]]
            assert cb_id not in items, f"duplicate ID: {cb_id}"
            assert type(band) is int and 1 <= band <= 7, (cb_id, band)
            items[cb_id] = {"subject": subject, "domain": row["primary_class_cd_desc"],
                            "skill": row["skill_desc"], "tier": tier, "band": band}
    counts = {"total": len(items), "by_subject": dict(sorted(Counter(v["subject"] for v in items.values()).items())),
              "by_tier": dict(sorted(Counter(v["tier"] for v in items.values()).items())),
              "by_band": dict(sorted(Counter(str(v["band"]) for v in items.values()).items()))}
    result = {"source": source(*metas), "assessment": "SAT", "counts": counts,
              "public_item_deep_link": {"pattern": None, "status": "not_verified",
                                        "finding": "The public Educator Question Bank opens ID previews in a results-page modal; its URL remains /digital/results and depends on session search state. No per-ID public URL pattern was verified.",
                                        "results_url": BANK_RESULTS},
              "partner_export_or_sign_in_needed": [
                  "A stable, verifiable per-item deep-link pattern (if one exists).",
                  "Student Question Bank inventory, which College Board places behind My Practice sign-in; it may differ from this public Educator Question Bank inventory."],
              "items": dict(sorted(items.items()))}
    save("cb_index.json", result)
    return result, lookup


def percentile_value(value: str) -> str | int:
    return value if value in ("1-", "99+") else int(value)


def percentile_tables(soup: BeautifulSoup) -> dict:
    total_table = soup.find("table", attrs={"summary": "Percentiles for Total Scores"})
    section_table = soup.find("table", attrs={"summary": "Percentiles for Section Scores"})
    assert total_table and section_table, "percentile table missing"
    out = {"national": {"total": {}, "rw": {}, "math": {}},
           "user": {"total": {}, "rw": {}, "math": {}}}
    for row in total_table.find_all("tr"):
        cells = [x.get_text(" ", strip=True) for x in row.find_all(["td", "th"], recursive=False)]
        if len(cells) == 3 and cells[0].isdigit():
            score = cells[0]
            out["national"]["total"][score] = percentile_value(cells[1])
            out["user"]["total"][score] = percentile_value(cells[2])
    for row in section_table.find_all("tr"):
        cells = [x.get_text(" ", strip=True) for x in row.find_all(["td", "th"], recursive=False)]
        if len(cells) == 5 and cells[0].isdigit():
            score = cells[0]
            for cohort, subject, value in (("national", "rw", cells[1]), ("user", "rw", cells[2]),
                                           ("national", "math", cells[3]), ("user", "math", cells[4])):
                out[cohort][subject][score] = percentile_value(value)
    assert all(len(out[c][s]) == (121 if s == "total" else 61)
               for c in out for s in out[c]), "incomplete percentile table"
    return out


def percentiles(refresh: bool) -> dict:
    soup, meta = html(PERCENTILES, refresh)
    tables = percentile_tables(soup)
    existing = json.loads((ROOT / "server" / "data" / "cb_percentiles.json").read_text())["tables"]
    differences = []
    for subject in ("total", "rw", "math"):
        for score in sorted(set(tables["user"][subject]) | set(existing[subject]), key=int):
            new, old = tables["user"][subject].get(score), existing[subject].get(score)
            if new != old:
                differences.append({"subject": subject, "score": int(score),
                                    "server": old, "current": new})
    result = {"source": source(meta), "edition_year": None,
              "note": "College Board's page does not print an edition year; source.fetched is the observation date.",
              "cohorts": {"national": "nationally representative", "user": "SAT user group"},
              "tables": tables,
              "comparison_with_server_data_cb_percentiles_json": {
                  "user_percentile_differences": differences,
                  "national_percentiles_in_server_file": False}}
    save("percentiles.json", result)
    return result


def specs(refresh: bool, lookup: dict) -> dict:
    rw_soup, rw_meta = html(RW_SPEC, refresh)
    math_soup, math_meta = html(MATH_SPEC, refresh)
    domain_soup, domain_meta = html(DOMAINS, refresh)
    shares = {"rw": {}, "math": {}}
    for subject, soup in (("rw", rw_soup), ("math", math_soup)):
        table = soup.find("table")
        assert table
        for row in table.find_all("tr"):
            cells = [x.get_text(" ", strip=True) for x in row.find_all(["th", "td"], recursive=False)]
            if len(cells) == 4 and cells[3].startswith("≈"):
                shares[subject][cells[0]] = float(cells[3].strip("≈%"))
        assert len(shares[subject]) == 4, (subject, shares[subject])
    domains = {}
    for subject, key in (("rw", "R&W"), ("math", "Math")):
        domains[subject] = [
            {"name": d["text"], "question_share_percent_approx": shares[subject][d["text"]],
             "skills": [x["text"] for x in d["skill"]]}
            for d in lookup["domain"][key]]
    guidance_table = [t for t in domain_soup.find_all("table")
                      if "Progress Bar Range for SAT" in t.get_text(" ", strip=True)][0]
    bands = {}
    for row in guidance_table.find_all("tr"):
        cells = [x.get_text(" ", strip=True) for x in row.find_all(["th", "td"], recursive=False)]
        if cells and cells[0] in ("Easy", "Medium", "Hard"):
            bands[cells[0].lower()] = cells[-1].replace("–", "-")
    assert bands == {"easy": "1-3", "medium": "4-5", "hard": "6-7"}, bands
    result = {"source": source(rw_meta, math_meta, domain_meta),
              "scope": "Digital SAT; shares are approximate proportions of operational questions.",
              "domains": domains,
              "difficulty": {
                  "item_tiers": ["easy", "medium", "hard"],
                  "item_tier_definition": "The public Educator Question Bank labels items Easy, Medium, or Hard but publishes no numeric item-difficulty thresholds on these pages.",
                  "sat_domain_performance_bar_guidance": bands,
                  "performance_bar_note": "These 1-7 ranges describe student domain performance and suggested practice difficulty, not a formula for each item's tier. The index's band is the API score_band_range_cd field."}}
    save("specs.json", result)
    return result


MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def parse_date(value: str) -> str:
    match = re.search(r"([A-Za-z]+)\.?\s+(\d{1,2}),\s*(20\d\d)", value)
    assert match, value
    return dt.date(int(match[3]), MONTHS[match[1][:3]], int(match[2])).isoformat()


def dates(refresh: bool) -> dict:
    date_soup, date_meta = html(DATES, refresh)
    score_soup, score_meta = html(SCORES, refresh)
    entries = {}
    for row in date_soup.find_all("table")[0].find_all("tr"):
        cells = [x.get_text(" ", strip=True) for x in row.find_all(["td", "th"], recursive=False)]
        if len(cells) == 3 and re.search(r"20\d\d", cells[0]):
            day = parse_date(cells[0])
            entries[day] = {"day": day, "register_by": parse_date(cells[1]),
                            "late_by": parse_date(cells[2]), "scores_by": None,
                            "anticipated": False}
    for row in score_soup.find_all("table")[0].find_all("tr"):
        cells = [x.get_text(" ", strip=True) for x in row.find_all(["td", "th"], recursive=False)]
        if len(cells) == 3 and re.search(r"20\d\d", cells[0]):
            day = parse_date(cells[0])
            assert day in entries, day
            entries[day]["scores_by"] = parse_date(cells[1])
    heading = date_soup.find("h2", string=lambda x: x and "Anticipated SAT Weekend" in x)
    assert heading
    for tag in heading.next_elements:
        if getattr(tag, "name", None) == "h2":
            break
        if getattr(tag, "name", None) == "li" and re.fullmatch(r"[A-Za-z]+ \d{1,2}, 20\d\d", tag.get_text(" ", strip=True)):
            day = parse_date(tag.get_text(" ", strip=True))
            entries[day] = {"day": day, "register_by": None, "late_by": None,
                            "scores_by": None, "anticipated": True}
    module_spec = importlib.util.spec_from_file_location("satdates", ROOT / "server" / "satdates.py")
    assert module_spec and module_spec.loader
    satdates = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(satdates)
    mismatch = []
    for day in sorted(set(entries) | set(satdates.DEADLINES)):
        current = entries.get(day)
        server = satdates.DEADLINES.get(day)
        if current is None or server is None:
            mismatch.append({"day": day, "kind": "published_past_date_omitted_from_server" if server is None and day < dt.date.today().isoformat() else "missing_date",
                             "source": current, "server": server})
        elif (current["register_by"], current["late_by"], current["scores_by"]) != server:
            mismatch.append({"day": day, "kind": "different_deadlines", "source": current, "server": server})
    result = {"source": source(date_meta, score_meta), "scope": "SAT Weekend; student score releases",
              "note": "Score release dates are unpublished for spring 2027 and anticipated 2027-28 dates. Current 2026-27 table also includes August and September dates now past.",
              "dates": [entries[k] for k in sorted(entries)],
              "comparison_with_server_satdates_py": {"mismatches": mismatch}}
    assert len(entries) >= 16, len(entries)
    save("dates.json", result)
    return result


def markdown_source(*metas: dict) -> str:
    lines = ["## Source", "", f"- Permission: {PERMISSION}"]
    lines += [f"- Fetched {meta['fetched']} UTC: {meta['url']}" for meta in metas]
    return "\n".join(lines) + "\n"


def legal_notes(refresh: bool) -> None:
    _, trademarks_meta = html(TRADEMARKS, refresh)
    _, marks_meta = html(MARK_LIST, refresh)
    _, copyright_meta = html(COPYRIGHT, refresh)
    _, student_meta = html(STUDENT_BANK, refresh)
    brand = f"""# College Board marks in the product

{markdown_source(trademarks_meta, marks_meta, copyright_meta)}
## Public rules and product guidance

- **Name:** [College Board's trademark list]({MARK_LIST}) identifies SAT® as a registered mark and Bluebook™ as a trademark. [The guidelines]({TRADEMARKS}) allow descriptive titles that clearly identify an independent source (for example, “Smith's App for the SAT® Exam”). They disallow using a mark as part of a company, product, service, or domain name or making the mark more prominent than the product name. Obtain written approval for any proposed branded product title under the partnership before shipping it.
- **Copy:** Use SAT® and Bluebook™ as adjectives with a noun, apply the right symbol, and give the ownership/affiliation disclaimer on each page displaying a mark, as the [guidelines]({TRADEMARKS}) specify. Refer to the SAT® exam or Bluebook™ testing application accurately. Do not claim College Board endorsement, certification, or a specific partnership scope beyond the written agreement.
- **Screenshots and logos:** The [guidelines]({TRADEMARKS}) require an express written logo license. The [copyright instructions]({COPYRIGHT}) require written permission to reproduce or modify protected materials. Treat screenshots of Bluebook, official questions, and College Board artwork as needing explicit written scope before product or marketing use. Plain text links to official pages are allowed.
- **Advertising:** The [guidelines]({TRADEMARKS}) restrict use of College Board marks in search and social advertising; have partner contacts approve any exception in writing.
- **Partnership scope:** The user reports an official partnership and email confirmation. This task records the phone permission specified in the helper file; the written agreement was not available for review here. Check the agreement for any negotiated exceptions before changing these defaults.
"""
    replicas = f"""# Original questions that mirror official structure (open question 17)

{markdown_source(copyright_meta, trademarks_meta, student_meta)}
## What the published terms cover

- The [copyright instructions]({COPYRIGHT}) say: “Reproduction of any official SAT test materials is not allowed in test prep and other commercial settings.” They also require express written permission to modify or reuse College Board content.
- The [trademark guidelines]({TRADEMARKS}) say College Board “does not grant permission for its copyrighted content, including practice test questions, to be used in conjunction with generative AI.” They also prohibit training an AI system on College Board content.
- The [copyright instructions]({COPYRIGHT}) allow ordinary links to College Board pages. They do not grant rights to copy the linked content.

## Open question for the partner agreement

The public terms address official material and its reproduction. They do not expressly settle whether independently written questions with original wording, values, and explanations may mirror an official item's abstract structure. Obtain a written answer from the College Board partner contact for this exact scenario, including acceptable similarity, examples, and any required review. Until then, keep using original authored content and do not import official stems, answer choices, explanations, screenshots, or variants into the product or AI workflows.
"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "brand.md").write_text(brand)
    (OUT / "replicas.md").write_text(replicas)


def import_student(path: Path) -> dict:
    """Turn the signed-in results table's four visible metadata columns into an index."""
    path = path.resolve()
    if path.is_relative_to(ROOT.resolve()):
        raise ValueError("the raw Student Bank snapshot must remain outside the repository")
    raw = json.loads(path.read_text())
    assert set(raw) == {"rw", "math"}
    specs = json.loads((OUT / "specs.json").read_text())["domains"]
    valid = {subject: {(domain["name"], skill) for domain in specs[subject]
                       for skill in domain["skills"]} for subject in raw}
    valid["rw"].add(("Craft and Structure", "Cross-text Connections"))
    items: dict[str, dict] = {}
    for subject, rows in raw.items():
        for row in rows:
            assert isinstance(row, list) and len(row) == 4, "expected visible table columns only"
            cb_id, tier, domain, skill = row
            assert isinstance(cb_id, str) and re.fullmatch(r"[0-9a-f]{8}", cb_id), cb_id
            assert tier in ("Easy", "Medium", "Hard"), (cb_id, tier)
            assert (domain, skill) in valid[subject], (cb_id, domain, skill)
            assert cb_id not in items, f"duplicate Student Bank ID: {cb_id}"
            items[cb_id] = {"subject": subject, "domain": domain, "skill": skill,
                            "tier": tier.lower(), "band": None, "public_item_url": None}
    assert len(items) == 3311 and len(raw["rw"]) == 1845 and len(raw["math"]) == 1466
    educator = json.loads((OUT / "cb_index.json").read_text())["items"]
    overlap = len(items.keys() & educator.keys())
    observed = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc)
    counts = {"total": len(items),
              "by_subject": dict(sorted(Counter(v["subject"] for v in items.values()).items())),
              "by_tier": dict(sorted(Counter(v["tier"] for v in items.values()).items())),
              "by_domain": dict(sorted(Counter(v["domain"] for v in items.values()).items()))}
    result = {
        "source": {"permission": PERMISSION, "fetched_timezone": "UTC",
                   "method": "signed-in browser results table; user entered credentials directly",
                   "observed_at_utc": observed.isoformat(timespec="seconds"),
                   "urls": [{"url": STUDENT_RESULTS, "fetched": observed.date().isoformat()}]},
        "assessment": "SAT", "inventory": "Student Question Bank",
        "capture": "All domains in each section; no difficulty filter; Exclude Active Questions off; 50 results per page.",
        "counts": counts, "overlap_with_educator_index": overlap,
        "missing_fields": {"band": "not displayed in Student results table",
                           "public_item_url": "no stable per-item URL verified; preview is a modal on /questionbank/results"},
        "items": dict(sorted(items.items())),
    }
    save("student_index.json", result)
    return result


def check() -> None:
    expected = {"cb_index.json", "student_index.json", "percentiles.json", "specs.json",
                "dates.json", "brand.md", "replicas.md", "student_bank.md"}
    assert expected <= {p.name for p in OUT.iterdir()}, "missing outputs"
    for path in OUT.iterdir():
        if path.suffix == ".json":
            data = json.loads(path.read_text())
            assert data["source"]["permission"] == PERMISSION
            assert all(x["url"].startswith("https://") and x["fetched"] for x in data["source"]["urls"])
        elif path.suffix == ".md":
            assert PERMISSION in path.read_text() and "## Source" in path.read_text()
    bank = json.loads((OUT / "cb_index.json").read_text())
    assert len(bank["items"]) == bank["counts"]["total"]
    assert all(set(v) == {"subject", "domain", "skill", "tier", "band"} and 1 <= v["band"] <= 7
               for v in bank["items"].values())
    student = json.loads((OUT / "student_index.json").read_text())
    assert student["counts"]["total"] == len(student["items"]) == 3311
    assert student["overlap_with_educator_index"] == len(student["items"].keys() & bank["items"].keys())
    assert all(set(v) == {"subject", "domain", "skill", "tier", "band", "public_item_url"}
               and v["band"] is None and v["public_item_url"] is None
               for v in student["items"].values())
    p = json.loads((OUT / "percentiles.json").read_text())
    assert all(len(p["tables"][cohort][section]) == (121 if section == "total" else 61)
               for cohort in ("national", "user") for section in ("total", "rw", "math"))
    d = json.loads((OUT / "dates.json").read_text())
    assert len(d["dates"]) >= 16
    print(f"cb_index: {bank['counts']['total']} items; {bank['counts']['by_subject']}; "
          f"tiers {bank['counts']['by_tier']}; bands {bank['counts']['by_band']}")
    print(f"student_index: {student['counts']['total']} items; {student['counts']['by_subject']}; "
          f"Educator ID overlap {student['overlap_with_educator_index']}")
    print(f"percentiles: {sum(len(x) for cohort in p['tables'].values() for x in cohort.values())} values; "
          f"server differences {len(p['comparison_with_server_data_cb_percentiles_json']['user_percentile_differences'])}")
    print(f"dates: {len(d['dates'])}; server mismatches {len(d['comparison_with_server_satdates_py']['mismatches'])}")
    print("cb-data checks: all good")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="refresh cached responses")
    parser.add_argument("--check", action="store_true", help="validate existing outputs")
    parser.add_argument("--import-student", type=Path, metavar="PATH",
                        help="import a metadata-only Student Bank table snapshot from outside the repo")
    args = parser.parse_args()
    if args.import_student:
        import_student(args.import_student)
        check()
    elif args.check:
        check()
    else:
        _, lookup = index(args.refresh)
        percentiles(args.refresh)
        specs(args.refresh, lookup)
        dates(args.refresh)
        legal_notes(args.refresh)
        check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
