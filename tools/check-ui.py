#!/usr/bin/env python3
"""UI rules the project keeps: run `python3 tools/check-ui.py` (exit 1 on a violation).
- No fully rounded buttons: a button selector (.pill, .btn, button) with border-radius of 24px or more (999px pills),
  or 50% (round buttons): the element a rule styles is a button when its last compound is .pill, .btn or button.
  An answer bubble drawn as a button opts out with /* check-ui: round-ok */ inside its rule.
- No oversized buttons: a .pill or .btn taller than 48px.
Use the existing .pill (primary) and .btn (secondary): 10px corners, 34 to 44px tall."""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent / "web"
BTN = re.compile(r"(^|[\s,>])(\.pill|\.btn|button)\b[^{]*\{([^}]*)\}", re.I)
bad = []
for f in list(ROOT.rglob("*.css")) + list(ROOT.rglob("*.html")) + list(ROOT.rglob("*.js")):
    if "dev" in f.parts:
        continue
    text = f.read_text(errors="ignore")
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        sel, body = m.group(1).strip().split("\n")[-1], m.group(2)
        line = text[:m.start()].count("\n") + 1
        # round buttons: the styled element itself (each selector's last compound, no pseudo-element) is a button
        lasts = [re.split(r"[\s>+~]+", part.strip())[-1] for part in sel.split(",") if part.strip()]
        # an answer bubble or radio mark that is a button says so: /* check-ui: round-ok */ in its rule
        if re.search(r"border-radius:\s*50%", body) and "check-ui: round-ok" not in body and any(
                re.search(r"(^|[.\w-])(\.pill|\.btn)\b|^button\b", c) and "::" not in c for c in lasts):
            bad.append(f"{f.relative_to(ROOT.parent)}:{line} {sel[:60]} is a round button (use the 10px or 8px corners)")
        if not re.search(r"(\.pill|\.btn)\b", sel) or "skel" in sel or "pill-" in sel:
            continue
        r = re.search(r"border-radius:\s*(\d+)px", body)
        h = re.search(r"(?<![\w-])height:\s*(\d+)px", body)
        if r and int(r.group(1)) >= 24:
            bad.append(f"{f.relative_to(ROOT.parent)}:{line} {sel[:60]} has border-radius {r.group(1)}px (use the 10px corners)")
        if h and int(h.group(1)) > 48:
            bad.append(f"{f.relative_to(ROOT.parent)}:{line} {sel[:60]} is {h.group(1)}px tall (48px at most)")
print("\n".join(bad) or "ok: no pill-shaped or oversized buttons")
sys.exit(1 if bad else 0)
