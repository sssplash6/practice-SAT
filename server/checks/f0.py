"""F0: the manifest is JSON with icons that exist, and every page has the head."""

import pathlib

WEB = pathlib.Path(__file__).resolve().parent.parent.parent / "web"
HEAD = ('<script src="/assets/head.js"></script>', '<link rel="manifest" href="/manifest.webmanifest">',
        '<meta name="theme-color" content="#FFFFFF">')


def check(c) -> None:
    m = c.get("/manifest.webmanifest").json()
    assert m["start_url"] == "/" and m["display"] == "standalone", m
    for src in [i["src"] for i in m["icons"]] + ["/assets/apple-touch-icon.png", "/assets/head.js"]:
        assert c.get(src).status_code == 200, src
    pages = sorted(WEB.rglob("*.html"))
    for p in pages:
        s = p.read_text()
        missing = [h for h in HEAD if h not in s]
        assert not missing, f"{p.relative_to(WEB)} lacks {missing}"
    print(f"ok  the manifest is JSON, its icons are served, and all {len(pages)} pages carry the head")
