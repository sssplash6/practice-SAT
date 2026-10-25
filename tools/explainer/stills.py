"""Screens of a board at given seconds: python3 stills.py <name> t1 t2 ..."""
import pathlib, sys
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
CHROME = str(pathlib.Path("~/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell").expanduser())
name, ts = sys.argv[1], [float(x) for x in sys.argv[2:]]
out = HERE / "out" / name
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    page = b.new_page(viewport={"width": 1920, "height": 1080})
    page.on("console", lambda m: print("page:", m.text)); page.on("pageerror", lambda e: print("pageerror:", e))
    page.goto((HERE / "board.html").as_uri() + "?capture=1&d=" + out.as_uri() + "/")
    page.wait_for_function("window.READY === true", timeout=30000)
    for t in ts:
        page.evaluate("t => seek(t)", t)
        page.screenshot(path=str(out / f"still-{t:05.1f}.jpg"), type="jpeg", quality=80)
    b.close()
