"""Online SQLite backups for the SAT server.

Set SATF_DB and SATF_BACKUPS, then run ``python3 tools/backup_db.py``.
Use --verify [file] to inspect a copy, or --restore FILE TARGET [--force].
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _outside_repo(path: pathlib.Path) -> pathlib.Path:
    resolved = path.resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError("SATF_BACKUPS must be outside the repository")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _snapshot(source: pathlib.Path, target: pathlib.Path) -> None:
    """sqlite3.backup reads a consistent snapshot, including committed WAL data."""
    if not source.is_file():
        raise ValueError(f"database does not exist: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".satf-backup-", suffix=".db", dir=target.parent)
    os.close(handle)
    temporary_path = pathlib.Path(temporary)
    try:
        with sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True) as live:
            with sqlite3.connect(temporary_path) as copy:
                live.backup(copy, pages=256, sleep=.01)
        with temporary_path.open("rb") as copy_file:
            os.fsync(copy_file.fileno())
        os.replace(temporary_path, target)
    finally:
        temporary_path.unlink(missing_ok=True)


def verify(path: pathlib.Path) -> dict:
    if not path.is_file():
        raise ValueError(f"backup does not exist: {path}")
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as copy:
        result = [row[0] for row in copy.execute("PRAGMA integrity_check")]
        if result != ["ok"]:
            raise ValueError(f"integrity_check failed: {result[:5]}")
        names = [row[0] for row in copy.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        counts = {name: copy.execute(f'SELECT COUNT(*) FROM "{name.replace(chr(34), chr(34) * 2)}"').fetchone()[0]
                  for name in names}
    return {"file": str(path.resolve()), "integrity_check": "ok", "tables": counts}


def _retain(directory: pathlib.Path) -> None:
    daily: dict[str, list[pathlib.Path]] = {}
    for path in directory.glob("daily-*.db"):
        daily.setdefault(path.name[6:16], []).append(path)
    for day in sorted(daily, reverse=True):
        copies = sorted(daily[day], reverse=True)
        for old in copies[1:] if day in sorted(daily, reverse=True)[:14] else copies:
            old.unlink()
    for old in sorted(directory.glob("weekly-*.db"), reverse=True)[8:]:
        old.unlink()


def backup(source: pathlib.Path, directory: pathlib.Path) -> dict:
    directory = _outside_repo(directory)
    stamp = dt.datetime.now(dt.timezone.utc)
    name = stamp.strftime("daily-%Y-%m-%dT%H%M%S.%fZ.db")
    copy = directory / name
    _snapshot(source, copy)
    try:
        report = verify(copy)
    except Exception:
        copy.unlink(missing_ok=True)
        raise
    week = directory / f"weekly-{stamp:%G}-W{stamp:%V}.db"
    if not week.exists():
        temporary = week.with_suffix(".tmp")
        try:
            shutil.copy2(copy, temporary)
            os.replace(temporary, week)
        finally:
            temporary.unlink(missing_ok=True)
    _retain(directory)
    return report


def restore(source: pathlib.Path, target: pathlib.Path, force: bool = False) -> dict:
    report = verify(source)
    target = target.resolve()
    if source.resolve() == target:
        raise ValueError("source and target are the same file")
    if target.exists() and target.stat().st_size and not force:
        raise ValueError("target is non-empty; pass --force to overwrite it")
    if any(pathlib.Path(str(target) + suffix).exists() for suffix in ("-wal", "-shm")):
        raise ValueError("target has SQLite sidecars; stop the server and remove them before restoring")
    _snapshot(source, target)
    return {"restored": str(target), "source": report["file"], "tables": report["tables"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=pathlib.Path, default=os.environ.get("SATF_DB"))
    parser.add_argument("--verify", nargs="?", const="latest", metavar="FILE")
    parser.add_argument("--restore", nargs=2, metavar=("FILE", "TARGET"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        if args.restore:
            result = restore(pathlib.Path(args.restore[0]), pathlib.Path(args.restore[1]), args.force)
        elif args.verify is not None:
            if args.verify == "latest":
                directory = _outside_repo(pathlib.Path(os.environ["SATF_BACKUPS"]))
                copies = sorted(directory.glob("daily-*.db"))
                if not copies:
                    raise ValueError("no daily backup to verify")
                path = copies[-1]
            else:
                path = pathlib.Path(args.verify)
            result = verify(path)
        else:
            if args.db is None or not os.environ.get("SATF_BACKUPS"):
                raise ValueError("set SATF_DB and SATF_BACKUPS (or pass --db)")
            result = backup(pathlib.Path(args.db), pathlib.Path(os.environ["SATF_BACKUPS"]))
    except (ValueError, KeyError, OSError, sqlite3.Error) as exc:
        print(f"backup_db: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
