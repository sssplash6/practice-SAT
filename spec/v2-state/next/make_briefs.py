"""Write compact per-task briefs for the wave-2 builders and their checkers.

    python3 spec/v2-state/next/make_briefs.py

briefs/<id>.md keeps only what building needs: the decisions, the task entry, the upgrade file's accepted
upgrades and overrides (without scorecards, rejected lists and "Why" paragraphs), the section spec's design,
extras, server changes, files, shared needs and acceptance (without the competitor teardown and open
questions), the Part 2 rules the section uses, and the API headers of the merged foundation files.
briefs/<id>-check.md is the checker's thin brief: decisions, task entry, acceptance lists and contracts.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
SPEC = (ROOT / "spec/rebuild-v2.md").read_text().splitlines()
OUT = ROOT / "spec/v2-state/briefs"

TASKS = {  # id: (section lines, upgrade file, name, pages only)
    "S1": ((653, 2294), "shell-me", "Account, Me, Settings, Help pages (Part 3.1 §1, §3-§6, §8, §9; §2 is the shell, §7 classes are dropped, §10 is F6's)", "helper"),
    "S3": ((2295, 3347), "today", "Today pages", "helper"),
    "S4": ((3348, 4779), "practice", "Practice builder and session pages", "helper"),
    "S5": ((4780, 6054), "tests", "Tests and the test window pages", "helper"),
    "S6": ((6055, 7045), "reports", "Results and score report pages", "helper"),
    "S10": ((10030, 10969), "review", "Review pages", "helper"),
    "S7": ((7046, 8096), "plan", "Plan pages (the server is merged)", True),
    "S8": ((8097, 9133), "compete", "Compete pages (the server is merged)", True),
    "S9": ((9134, 10029), "words", "Words pages (the server is merged)", True),
    "F2B": ((653, 2294), "shell-me", "Shell follow-ups (Part 3.1 §2 is the part that matters)", False),
}
DROP_SECTION = re.compile(r"^### 3\.\d+\.\d+ (What they have|What we have now|This section's open questions)")
API_FILES = ["web/assets/ui.js", "web/assets/kit.js", "web/assets/charts.js", "web/assets/question.js",
             "web/assets/runner.js", "web/assets/report.js"]


def lines(a: int, b: int) -> list[str]:
    return SPEC[a - 1:b]


def section_text(a: int, b: int) -> str:
    out, skip = [], False
    for line in lines(a, b):
        if line.startswith("### "):
            skip = bool(DROP_SECTION.match(line))
        if not skip:
            out.append(line)
    return "\n".join(out)


def upgrade_text(name: str) -> str:
    text = (ROOT / f"spec/v2-upgrades/{name}.md").read_text()
    start = text.find("\n## 2. Accepted upgrades")
    end = text.find("\n## 4. Rejected")
    body = text[start:end if end > 0 else None]
    return re.sub(r"\n\*\*Why\.\*\*.*?(?=\n\n)", "", body, flags=re.S)


def part2(used: str, tid: str, sec_no: str) -> str:
    keep = []
    heads = [i for i, l in enumerate(SPEC[:652]) if l.startswith("### 2.")]
    for n, i in enumerate(heads):
        j = heads[n + 1] if n + 1 < len(heads) else 652
        block = SPEC[i:j]
        title = block[0]
        if title.startswith("### 2.12"):
            continue
        if title.startswith("### 2.2"):
            refs = set(re.findall(r"\bR(\d{1,2})\b", used))
            block = [l for l in block if not l.startswith("| R") or re.match(r"\| R(\d+) ", l) and
                     re.match(r"\| R(\d+) ", l).group(1) in refs]
        elif title.startswith("### 2.9"):
            block = [l for l in block if not l.startswith("| ") or f"| {tid} " in l or l.startswith("| task") or
                     l.startswith("|---") or tid in l]
        elif title.startswith("### 2.13"):
            block = [l for l in block if not l.startswith("| 3.") or l.startswith(f"| {sec_no} ")]
        keep += block
    return "\n".join(keep)


def api_headers() -> str:
    out = []
    for f in API_FILES:
        p = ROOT / f
        if not p.exists():
            continue
        m = re.match(r"\s*(/\*.*?\*/)", p.read_text(), re.S)
        if m:
            out.append(f"### {f}\n\n```\n{m.group(1)}\n```")
    return "\n\n".join(out)


def acceptance(text: str) -> str:
    blocks = re.findall(r"(\*\*Acceptance\.\*\*.*?)(?=\n#### |\n### |\Z)", text, re.S)
    return "\n\n".join(blocks)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dec = (ROOT / "spec/v2-decisions.md").read_text()
    prod = (ROOT / "spec/v2-upgrades/product.md").read_text().splitlines()
    part4 = "\n".join(SPEC[10969:11183])
    apis = api_headers()
    for tid, ((a, b), up, name, pages_only) in TASKS.items():
        sec = section_text(a, b)
        upg = upgrade_text(up)
        rows = "\n".join(l for l in prod if f"{up}.md" in l or f"`{tid}`" in l) or "(none)"
        m = re.search(rf"\*\*{tid} · .*?(?=\n\*\*[A-Z]\d* · |\n### 4\.3)", part4, re.S)
        entry = m.group(0) if m else "(see the task prompt)"
        sec_no = SPEC[a - 1].split()[1] if SPEC[a - 1].startswith("## 3.") else ""
        rules = part2(sec + upg, tid, sec_no)
        note = ("You build only the PAGES: the server is being built by the user's other agent on v2/" + tid.lower() + "-server; code "
                "against the endpoints in section 5 and degrade quietly until they land; list any server change you need."
                if pages_only == "helper" else
                "You build only the PAGES: the server is merged; use its endpoints and list any server change you need."
                if pages_only else "You build the server half and the pages.")
        brief = f"""# Brief for {tid}: {name}

{note} This brief is everything you need from the plan: do not open spec/rebuild-v2.md or other upgrade files.
Precedence: the decisions > the upgrade file > the section spec > Part 2. For the foundations' APIs use section 6
below (their header comments); open those files only to read one function you are calling.

## 1. Decisions

{dec}

## 2. Your task entry

{entry}

## 3. Accepted upgrades and spec overrides (spec/v2-upgrades/{up}.md)

{upg}

## 4. product.md rows that name you

{rows}

## 5. The section spec (design, extras, server, files, shared needs, acceptance)

{sec}

## 6. The foundation APIs you call

{apis}

## 7. Part 2 rules this section uses

{rules}
"""
        (OUT / f"{tid}.md").write_text(brief)
        acc_sec = re.search(r"### 3\.\d+\.8 Acceptance checks.*?(?=\n### |\Z)", sec, re.S)
        check = f"""# Check brief for {tid}: {name}

## Decisions

{dec}

## Task entry

{entry}

## The section's acceptance list

{acc_sec.group(0) if acc_sec else '(see the task prompt)'}

## The upgrades' acceptance items (spec/v2-upgrades/{up}.md)

{acceptance(upg)}

## Contracts and amended checks

{chr(10).join(l for l in rules.splitlines() if l.startswith('| ') or l.startswith('### 2.9') or l.startswith('### 2.13'))}
"""
        (OUT / f"{tid}-check.md").write_text(check)
        print(f"{tid}: brief {len(brief) / 4000:.0f}k tokens, check brief {len(check) / 4000:.0f}k")


if __name__ == "__main__":
    main()
