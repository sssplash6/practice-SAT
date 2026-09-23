"""Save the v2 build exactly as it stands, so an interruption loses nothing finished.

    python3 tools/v2_checkpoint.py            # write spec/v2-state/, print a summary
    python3 tools/v2_checkpoint.py --quiet    # the same, silently (for the background loop)

What it writes, all under spec/v2-state/:

* STATE.md -- when, every v2 branch (head, commits ahead of master), every worktree
  (branch, uncommitted files), every workflow run (agents finished and still running,
  by label), and how to resume.
* runs/<run>/<label>.json -- every finished agent's full result, one file each, taken from
  the workflow journals. A result is never lost once an agent returns.
* wip/<worktree>/ -- each worktree's uncommitted work: diff.patch (tracked changes against
  HEAD) and untracked.tar (new files). This never touches a worktree's git index, so it is
  safe to run while agents are working in them. Restore with
  `git -C <worktree> apply diff.patch && tar -xf untracked.tar -C <worktree>`.

It only reads git and the journals and only writes inside spec/v2-state/, so it is safe to
run at any time, as often as wanted.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
STATE = REPO / "spec" / "v2-state"
RUNS = pathlib.Path.home() / ".claude/projects/-Users-workingmyassof-satbank/9030c288-6222-49fa-a25a-6e6802e22cd3/subagents/workflows"


def git(*args: str, cwd: pathlib.Path = REPO) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True).stdout


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "unlabelled").lower()).strip("-")[:80]


def runs() -> list[dict]:
    out = []
    for journal in sorted(RUNS.glob("*/journal.jsonl")):
        label, done, started = {}, {}, set()
        for line in journal.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            k = r.get("key")
            if r.get("type") == "started":
                started.add(k)
                label[k] = r.get("label")
            elif r.get("type") == "result":
                done[k] = r.get("result", r.get("value"))
        run = journal.parent.name
        target = STATE / "runs" / run
        target.mkdir(parents=True, exist_ok=True)
        for k, v in done.items():
            name = f"{slug(label.get(k))}-{k[-8:]}.json"
            path = target / name
            body = json.dumps({"label": label.get(k), "key": k, "result": v}, ensure_ascii=False, indent=1)
            if not path.exists() or path.read_text() != body:
                path.write_text(body)
        out.append({"run": run, "done": sorted(filter(None, (label.get(k) for k in done))),
                    "running": sorted(filter(None, (label.get(k) for k in started - set(done))))})
    return out


def worktrees() -> list[dict]:
    out, cur = [], {}
    for line in git("worktree", "list", "--porcelain").splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
            cur = {}
        elif line.startswith("worktree "):
            cur["path"] = line[9:]
        elif line.startswith("branch "):
            cur["branch"] = line[7:].replace("refs/heads/", "")
        elif line.startswith("HEAD "):
            cur["head"] = line[5:12]
    result = []
    for w in out:
        p = pathlib.Path(w["path"])
        if p == REPO or not p.exists():
            continue
        dirty = [l[3:] for l in git("status", "--porcelain", cwd=p).splitlines()]
        w["dirty"] = dirty
        if dirty:
            keep = STATE / "wip" / p.name
            keep.mkdir(parents=True, exist_ok=True)
            (keep / "diff.patch").write_text(git("diff", "HEAD", "--binary", cwd=p))
            untracked = git("ls-files", "--others", "--exclude-standard", cwd=p).split()
            tar = keep / "untracked.tar"
            if untracked:
                subprocess.run(["tar", "-cf", str(tar), *untracked], cwd=p, capture_output=True)
            elif tar.exists():
                tar.unlink()
            (keep / "where.txt").write_text(f"{p}\nbranch {w.get('branch', '(detached)')} at {w.get('head')}\n")
        result.append(w)
    return result


def branches() -> list[str]:
    lines = []
    for b in git("branch", "--list", "v2/*", "--format=%(refname:short) %(objectname:short)").splitlines():
        name, head = b.split()
        ahead = git("rev-list", "--count", f"master..{name}").strip()
        lines.append(f"- `{name}` at {head}, {ahead} commits ahead of master")
    return lines


def main() -> None:
    quiet = "--quiet" in sys.argv
    STATE.mkdir(parents=True, exist_ok=True)
    r, w, b = runs(), worktrees(), branches()
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    md = [f"# v2 build state -- {now}", "",
          "Written by `tools/v2_checkpoint.py`. Nothing below is lost on an interruption: finished",
          "agent results are in `runs/`, uncommitted worktree work in `wip/`.", "",
          "## Branches", "", *b, "", "## Worktrees", ""]
    for x in w:
        md.append(f"- `{x['path']}` on `{x.get('branch', 'detached ' + str(x.get('head')))}`: "
                  f"{len(x['dirty'])} uncommitted" + (f" (saved in wip/{pathlib.Path(x['path']).name}/)" if x["dirty"] else ""))
    md += ["", "## Workflow runs", ""]
    for x in r:
        md.append(f"### {x['run']}: {len(x['done'])} finished, {len(x['running'])} unfinished")
        if x["running"]:
            md.append("Unfinished when saved: " + ", ".join(x["running"]))
        md.append("")
    md += ["## Resuming", "",
           "Do not re-run finished agents: read their results from `runs/`. Do not discard a worktree's",
           "uncommitted work: a restarted agent continues from it (or from `wip/` if the worktree is gone).", ""]
    (STATE / "STATE.md").write_text("\n".join(md))
    if not quiet:
        print("\n".join(md))


if __name__ == "__main__":
    main()
