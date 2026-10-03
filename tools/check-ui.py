#!/usr/bin/env python3
"""UI rules the project keeps: run `python3 tools/check-ui.py` (exit 1 on a violation).
- No fully rounded buttons: a button selector (.pill, .btn, button) with border-radius of 24px or more (999px pills).
- No oversized buttons: a .pill or .btn taller than 48px.
Use the existing .pill (primary) and .btn (secondary): 10px corners, 34 to 44px tall."""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent / "web"
BTN = re.compile(r"(^|[\s,>])(\.pill|\.btn|button)\b[^{]*\{([^}]*)\}", re.I)
bad = []
for f in list(ROOT.rglob("*.css")) + list(ROOT.rglob("*.html")) + list(ROOT.rglob("*.js")):
    if "dev" in f.parts or f.name == "tour.js":
        continue
    text = f.read_text(errors="ignore")
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        sel, body = m.group(1).strip().split("\n")[-1], m.group(2)
        if not re.search(r"(\.pill|\.btn)\b", sel) or "skel" in sel or "pill-" in sel:
            continue
        r = re.search(r"border-radius:\s*(\d+)px", body)
        h = re.search(r"(?<![\w-])height:\s*(\d+)px", body)
        line = text[:m.start()].count("\n") + 1
        if r and int(r.group(1)) >= 24:
            bad.append(f"{f.relative_to(ROOT.parent)}:{line} {sel[:60]} has border-radius {r.group(1)}px (use the 10px corners)")
        if h and int(h.group(1)) > 48:
            bad.append(f"{f.relative_to(ROOT.parent)}:{line} {sel[:60]} is {h.group(1)}px tall (48px at most)")
print("\n".join(bad) or "ok: no pill-shaped or oversized buttons")
sys.exit(1 if bad else 0)
