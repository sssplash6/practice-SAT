"""The serving layer.

    pip install fastapi uvicorn
    python3 -m uvicorn server.app:app --reload --port 8000

A student's first move is the diagnostic, so that is what this serves: one of
ten fixed forms, drawn at random, twenty questions, marked here. The answer
key never leaves this process -- questions go out without it, responses come
back, and grading happens on this side. A student reading the page source finds
their own answers and nothing else.

This file is the app: startup, health, the cache header, the routers
(server/api_*.py, listed in ROUTERS) and the pages in web/, mounted last.
"""

from __future__ import annotations

import json
import logging
import pathlib

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import blueprint, db, deps, practice
from .api_tests import FORM_IDS, FORMS, MOCKS

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("satf")

HERE = pathlib.Path(__file__).resolve().parent
WEB = HERE.parent / "web"
FORMS_PATH = HERE / "forms.json"
RW_FORMS_PATH = HERE / "forms_rw.json"          # tools/build_rw_forms.py, ids 101+
MOCKS_PATH = HERE / "mocks.json"

# Every planned router (spec/rebuild-v2.md 2.10), each included once its module
# exists, so a task adds its router without editing this file.
ROUTERS = ("api_shell", "api_legacy", "api_me", "api_notes", "api_account", "api_profile",
           "api_practice", "api_bank", "api_tests", "api_results", "api_today", "api_review",
           "api_plan", "api_compete", "api_words", "classes", "reports", "sets", "api_admin", "api_parent")
# and every module whose init() startup runs when it has one: data migrations,
# warm caches, the weekly paper
STARTUP = ROUTERS + ("account", "achievements", "challenge", "compete", "daily", "papers",
                     "plan", "prefs", "progress", "words")

app = FastAPI(title="SAT Freshman")


@app.on_event("startup")
def startup() -> None:
    db.init()
    if not FORMS_PATH.exists():
        raise SystemExit(f"{FORMS_PATH} is missing. Run tools/build_diagnostics.py first.")
    for subject, path in (("math", FORMS_PATH), ("rw", RW_FORMS_PATH)):
        if not path.exists():
            raise SystemExit(f"{path} is missing. Run tools/build_diagnostics.py (Math) or tools/build_rw_forms.py.")
        FORM_IDS[subject].clear()
        for form in json.loads(path.read_text())["forms"]:
            FORMS[form["id"]] = form["questions"]
            FORM_IDS[subject].append(form["id"])
    log.info("loaded %d diagnostic forms (%d Math, %d R&W), %d questions each",
             len(FORMS), len(FORM_IDS["math"]), len(FORM_IDS["rw"]), len(next(iter(FORMS.values()))))
    # the bank's lazy globals are not thread safe on first touch, so they are
    # warmed here rather than on whichever request happens to arrive first
    cat = practice.catalogue()
    log.info("practice catalogue: %d topics, %d templates",
             len(cat["by_topic"]), sum(len(v) for v in cat["by_topic"].values()))

    if MOCKS_PATH.exists():
        for m in json.loads(MOCKS_PATH.read_text())["mocks"]:
            MOCKS[m["id"]] = m
        log.info("loaded %d mock sections", len(MOCKS))
    else:
        log.warning("%s is missing; run tools/build_mocks.py", MOCKS_PATH)
    # what every template can make, which fresh sections and difficulty
    # filters both need, surveyed once rather than on a student's first request
    can = blueprint.abilities()
    log.info("surveyed %d templates", len(can))
    # the builder's tree (blueprint.kinds) took ~16 s on the first Practice open after each
    # restart, and the one process stalled every visitor meanwhile: built here instead
    from .api_practice import _catalogue
    for subject in ("math", "rw"):
        _catalogue(subject)
    log.info("builder catalogue ready")
    for name in STARTUP:
        init = deps.part(name, "init")
        if init is not None:
            init()


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "forms": len(FORMS)}


@app.middleware("http")
async def revalidate(request, call_next):
    """Ask the browser to check before reusing a file.

    Without this a page keeps running the stylesheet and script it loaded an
    hour ago, which during development means testing a fix that is not there.
    The etag still means nothing is re-downloaded when it has not changed.
    """
    response = await call_next(request)
    if not request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-cache"
    return response


# retired codes may read but not write, and a minted device token rides back as X-Learner-Swap
app.middleware("http")(deps.swap_middleware)


for name in ROUTERS:
    router = deps.part(name, "router")
    if router is not None:
        app.include_router(router)

# The site itself. Mounted last so every router above wins the match.
if WEB.is_dir():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
else:                                              # pragma: no cover
    @app.get("/", response_class=HTMLResponse)
    def missing() -> str:
        return f"<p>No web directory at {WEB}</p>"
