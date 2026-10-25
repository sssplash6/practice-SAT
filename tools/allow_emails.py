"""Add addresses to the approved list for email sign-in (table email_allow, see account.beta_account).

Usage:  SATF_DB=/path/to/satfreshman.db python3 tools/allow_emails.py students.csv
        SATF_DB=... python3 tools/allow_emails.py --count

The CSV has a header row with `email` and optionally `name` and `group`. Addresses are trimmed and
lowercased (a trailing full stop is dropped); a row with no valid address is reported and skipped.
Running it again with the same file changes nothing, and a later file only adds or renames.
Rosters hold students' personal data: keep them out of the repository. The admin page /admin/access/
does the same from a pasted list.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from server import account, db  # noqa: E402


def main(argv: list[str]) -> int:
    db.init()
    if argv[:1] == ["--count"]:
        print(db.one("SELECT COUNT(*) n FROM email_allow")["n"], "addresses on the approved list")
        return 0
    if len(argv) != 1:
        print(__doc__)
        return 2
    added = skipped = 0
    with open(argv[0], newline="", encoding="utf-8") as f:
        for n, row in enumerate(csv.DictReader(f), 2):
            if account.allow(row.get("email", ""), row.get("name") or "", row.get("group") or "") == "invalid":
                print(f"line {n}: skipped, not an email: {row.get('email', '')!r}")
                skipped += 1
                continue
            added += 1
    total = db.one("SELECT COUNT(*) n FROM email_allow")["n"]
    print(f"{added} addresses added or updated, {skipped} skipped; {total} on the approved list")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
