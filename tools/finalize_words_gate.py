"""Combine the two independent seed-0 Words verdict passes.

Only a frame whose every legal key has two correct ``one`` votes is approved.
The source verdict files are never changed; blocked frames stay in the review
queue with both votes for a human to resolve.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from build_words import CONTENT, ROOT, key_token, load, review_hash, rows


def read(name: str) -> object:
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def write(name: str, value: object) -> None:
    (CONTENT / name).write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")


def normalized(value: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", value).casefold()
                   if not unicodedata.combining(ch))


def keyed_votes(votes: list[dict], who: str, frames: dict[str, dict]) -> dict[tuple[str, str, int], dict]:
    result = {}
    for vote in votes:
        assert vote["by"] == who and vote["seed"] == 0, vote
        frame = vote["frame"]
        assert frame in frames, frame
        if who == "model:helper-a":
            key = vote["key"]
        else:
            matches = [key for key in frames[frame]["keys"]
                       if key_token(frame, key) == vote["key_slug"]]
            assert len(matches) == 1, (frame, vote["key_slug"])
            key = matches[0]
        assert key in frames[frame]["keys"], (frame, key)
        address = frame, key, 0
        assert address not in result, address
        result[address] = vote
    return result


def generated_answers(expected: set[tuple[str, str, int]]) -> dict[tuple[str, str, int], str]:
    """Verify the key against the exact item both reviewers saw."""
    with tempfile.TemporaryDirectory() as tmp:
        previous_db = os.environ.get("SATF_DB")
        previous_review = os.environ.get("SATF_WORDS_UNREVIEWED")
        os.environ["SATF_DB"] = str(Path(tmp) / "gate.db")
        os.environ["SATF_WORDS_UNREVIEWED"] = "1"
        try:
            sys.path.insert(0, str(ROOT))
            from server import db, words
            db.init()
            words.init()
            answers = {}
            for frame, key, seed in sorted(expected):
                item = words.item("rw.wic." + frame, seed, key)
                assert item["word"] == key, (frame, key)
                answers[frame, key, seed] = item["choices"][item["answer_index"]]
            return answers
        finally:
            if previous_db is None:
                os.environ.pop("SATF_DB", None)
            else:
                os.environ["SATF_DB"] = previous_db
            if previous_review is None:
                os.environ.pop("SATF_WORDS_UNREVIEWED", None)
            else:
                os.environ["SATF_WORDS_UNREVIEWED"] = previous_review


def main() -> None:
    plan = read("gate_plan.json")
    plan_frames = [row["frame"] for row in plan["frames"]]
    assert len(plan_frames) == len(set(plan_frames)) == plan["counts"]["frames"]
    frames_data = load("frames", [])
    frames = {frame["id"]: frame for frame in rows(frames_data)}
    sat = {word["slug"]: word for word in rows(load("sat", []))}
    a = keyed_votes(read("adjudications_a.json"), "model:helper-a", frames)
    b = keyed_votes(read("adjudications_b.json"), "model:helper-b", frames)
    expected = {(frame, key, 0) for frame in plan_frames for key in frames[frame]["keys"]}
    assert set(a) == set(b) == expected, (len(expected - set(a)), len(expected - set(b)))
    answers = generated_answers(expected)

    combined = []
    blocked: dict[str, set[str]] = defaultdict(set)
    for frame in plan_frames:
        for key in frames[frame]["keys"]:
            address = frame, key, 0
            answer = answers[address]
            for label, vote in (("A", a[address]), ("B", b[address])):
                verdict = vote["verdict"]
                assert verdict in {"one", "more", "none"}, vote
                raw_option = vote.get("option")
                if verdict == "one":
                    assert isinstance(raw_option, str), vote
                    correct = normalized(raw_option) in {normalized(key), normalized(answer)}
                    if not correct:
                        blocked[frame].add(f"{label}_wrong_option")
                    option = key if correct else raw_option
                else:
                    blocked[frame].add(f"{label}_{verdict}")
                    option = raw_option
                record = {"frame": frame, "key": key, "seed": 0, "by": vote["by"],
                          "verdict": verdict, "option": option}
                if raw_option != option:
                    record["observed_option"] = raw_option
                if vote.get("note"):
                    record["note"] = vote["note"]
                combined.append(record)

    approved = set(plan_frames) - set(blocked)
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    for frame in rows(frames_data):
        if frame["id"] in approved:
            frame["reviewed"] = {"by": "model:helper-a+model:helper-b", "date": today,
                                 "hash": review_hash(frame, sat), "seeds": [0]}
        elif frame["id"] in blocked:
            frame["reviewed"] = None

    queue = read("review-queue.json")
    queued = {row["frame"]: row for row in queue["frames"]}
    assert len(queued) == len(queue["frames"]) and set(queued) <= set(frames)
    verdicts_by_frame = defaultdict(list)
    for vote in combined:
        verdicts_by_frame[vote["frame"]].append(vote)
    waiting = []
    for frame_data in rows(frames_data):
        frame = frame_data["id"]
        if frame in approved:
            continue
        row = queued.get(frame, {"frame": frame,
                                 "hash": review_hash(frame_data, sat),
                                 "keys": {key_token(frame, key): key
                                          for key in frame_data["keys"]}})
        if frame in blocked:
            row["status"] = "blocked"
            row["reasons"] = sorted(blocked[frame])
            row["verdicts"] = verdicts_by_frame[frame]
        waiting.append(row)
    queue["about"] = ("Unapproved Words frames. Planned frames blocked by the two seed-0 "
                      "passes include both verdicts and reasons; other frames await review. "
                      "Approved frames have only seed 0 reviewed.")
    queue["counts"] = {"approved": len(approved), "blocked": len(blocked),
                       "unselected_unreviewed": len(waiting) - len(blocked)}
    queue["frames"] = waiting

    write("adjudications.json", combined)
    write("frames.json", frames_data)
    write("review-queue.json", queue)
    kinds = Counter(reason for reasons in blocked.values() for reason in reasons)
    approved_senses = {key for frame in approved for key in frames[frame]["keys"]}
    print(f"approved={len(approved)} blocked={len(blocked)} "
          f"approved_senses={len(approved_senses)} uncovered={len(plan['uncovered'])}")
    print("block_reasons=" + json.dumps(dict(sorted(kinds.items())), sort_keys=True))


if __name__ == "__main__":
    main()
