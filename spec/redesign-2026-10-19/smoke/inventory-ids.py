# every gone id: is it still referenced in web/ (outside web/dev/) or server/? usage: python3 inventory-ids.py <id> ...
import re, pathlib, sys
ids = sys.argv[1:]
files = [p for root in ('web', 'server') for p in pathlib.Path(root).rglob('*') if p.suffix in ('.js', '.html', '.css', '.py') and '/vendor/' not in str(p) and not str(p).startswith('web/dev/')]
for i in ids:
    e = re.escape(i)
    pat = re.compile(rf"#{e}\b(?!-)|getElementById\(\s*['\"]{e}['\"]|byId\(\s*['\"]{e}['\"]|\bid\s*[:=]\s*['\"]{e}['\"]|aria-(controls|labelledby|describedby)\s*[:=]\s*['\"][^'\"]*\b{e}\b(?!-)|for=['\"]{e}['\"]|\bhtmlFor\s*=\s*['\"]{e}['\"]|\$\(\s*['\"]{e}['\"]")
    hits = []
    for p in files:
        for n, line in enumerate(p.read_text(errors='ignore').splitlines(), 1):
            if pat.search(line): hits.append(f"  {p}:{n}: {line.strip()[:200]}")
    print(f"=== {i} ({len(hits)})"); print('\n'.join(hits[:12]))
