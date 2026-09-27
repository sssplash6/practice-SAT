"""Run a bounded HTTP load survey against an isolated SAT server.

Example: python3 tools/load_test.py --seconds 8 --learners 200 --json /tmp/satf-load.json
Each concurrency stage lasts --seconds; the temporary database and server are removed afterward.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from collections import defaultdict

import httpx

ROOT = pathlib.Path(__file__).resolve().parents[1]
ROUTES = ("today", "shell", "me", "words", "drill", "test")


def _port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def _percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low, high = int(position), min(int(position) + 1, len(ordered) - 1)
    return round(ordered[low] + (ordered[high] - ordered[low]) * (position - low), 1)


class Survey:
    def __init__(self, base: str, timeout: float):
        self.client = httpx.AsyncClient(base_url=base, timeout=timeout,
                                        limits=httpx.Limits(max_connections=300, max_keepalive_connections=300))
        self.attempts: dict[str, int] = defaultdict(int)
        self.samples: dict[str, list[float]] = defaultdict(list)
        self.error_counts: dict[str, int] = defaultdict(int)
        self.errors: dict[str, list[str]] = defaultdict(list)

    async def close(self) -> None:
        await self.client.aclose()

    async def call(self, label: str, method: str, path: str, learner: str, body=None) -> dict | None:
        start = time.perf_counter()
        self.attempts[label] += 1
        try:
            reply = await self.client.request(method, path, headers={"X-Learner": learner, "X-Tz": "0"}, json=body)
            if reply.status_code >= 400:
                self.error_counts[label] += 1
                if len(self.errors[label]) < 20:
                    self.errors[label].append(f"HTTP {reply.status_code}: {reply.text[:100]}")
                return None
            result = reply.json()
            self.samples[label].append((time.perf_counter() - start) * 1000)
            return result
        except (httpx.HTTPError, ValueError) as exc:
            self.error_counts[label] += 1
            if len(self.errors[label]) < 20:
                self.errors[label].append(type(exc).__name__ + ": " + str(exc)[:100])
            return None

    async def operation(self, kind: str, learner: str) -> None:
        if kind in {"today", "shell", "me", "words"}:
            await self.call(kind, "GET", "/api/" + kind, learner)
        elif kind == "drill":
            made = await self.call("drill_create", "POST", "/api/drill", learner,
                                   {"templates": ["lin.evaluate"], "count": 2, "repairs": "off"})
            if made and made.get("question"):
                sid = made["id"]
                answered = await self.call("drill_answer", "POST", f"/api/drill/{sid}/answer", learner,
                                           {"question_id": made["question"]["id"], "answer": 0, "ms": 5000})
                if answered:
                    await self.call("drill_next", "POST", f"/api/drill/{sid}/next", learner, {})
        else:
            made = await self.call("test_start", "POST", "/api/session", learner, {})
            if made and made.get("questions"):
                sid = made["id"]
                await self.call("test_answer", "POST", f"/api/session/{sid}/answer", learner,
                                {"question_id": made["questions"][0]["id"], "answer": 0})
                await self.call("test_finish", "POST", f"/api/session/{sid}/finish", learner, {})


async def stage(base: str, learners: list[str], concurrency: int, seconds: float, timeout: float,
                routes: tuple[str, ...]) -> dict:
    survey = Survey(base, timeout)
    gate = asyncio.Event()
    began = time.perf_counter()
    deadline = began + seconds

    async def worker(index: int) -> None:
        await gate.wait()
        turn = index
        while time.perf_counter() < deadline:
            await survey.operation(routes[turn % len(routes)], learners[index])
            turn += 1

    tasks = [asyncio.create_task(worker(i)) for i in range(concurrency)]
    gate.set()
    await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - began
    rows = {}
    for name, attempts in sorted(survey.attempts.items()):
        samples = survey.samples[name]
        errors = survey.errors[name]
        rows[name] = {"requests": attempts, "errors": survey.error_counts[name],
                      "rps": round(attempts / elapsed, 2),
                      "success_rps": round(len(samples) / elapsed, 2),
                      "p50_ms": _percentile(samples, .5), "p95_ms": _percentile(samples, .95),
                      "p99_ms": _percentile(samples, .99), "examples": errors[:3]}
    await survey.close()
    broken = [name for name, row in rows.items() if row["errors"] or (row["p95_ms"] or 0) > 2000]
    broken.sort(key=lambda name: (-rows[name]["errors"], -(rows[name]["p95_ms"] or 0)))
    return {"concurrency": concurrency, "seconds": round(elapsed, 2),
            "requests": sum(row["requests"] for row in rows.values()), "routes": rows,
            "breaks": broken}


async def run(base: str, learners: list[str], seconds: float, timeout: float,
              routes: tuple[str, ...], stages: tuple[int, ...]) -> dict:
    async with httpx.AsyncClient(base_url=base, timeout=timeout) as client:
        for learner in learners:
            reply = await client.put("/api/me", headers={"X-Learner": learner, "X-Tz": "0"},
                                     json={"minutes": 30})
            if reply.status_code != 200:
                raise RuntimeError(f"seeding failed: HTTP {reply.status_code} {reply.text[:120]}")
    result = {"learners": len(learners), "routes": routes, "stages": []}
    for concurrency in stages:
        print(f"stage {concurrency} learners for {seconds:g}s", flush=True)
        result["stages"].append(await stage(base, learners, concurrency, seconds, timeout, routes))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=8)
    parser.add_argument("--learners", type=int, default=200)
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--json", type=pathlib.Path)
    parser.add_argument("--server-log", type=pathlib.Path)
    parser.add_argument("--routes", default=",".join(ROUTES), help="comma-separated route groups")
    parser.add_argument("--stages", default="10,50,200", help="comma-separated concurrency levels")
    args = parser.parse_args()
    routes = tuple(part.strip() for part in args.routes.split(",") if part.strip())
    try:
        stages = tuple(int(part.strip()) for part in args.stages.split(",") if part.strip())
    except ValueError:
        parser.error("stages must be comma-separated integers")
    if args.seconds <= 0 or args.learners < 200 or args.timeout <= 0 or args.port == 8000:
        parser.error("seconds/timeout must be positive, learners >= 200, and port cannot be 8000")
    if not routes or any(route not in ROUTES for route in routes) or not stages or any(
            stage < 1 or stage > args.learners for stage in stages):
        parser.error("routes must be known groups and stages must be 1..learners")
    port = args.port or _port()
    with tempfile.TemporaryDirectory(prefix="satf-load-") as folder:
        root = pathlib.Path(folder)
        log_path = root / "server.log"
        env = {**os.environ, "SATF_DB": str(root / "load.db"), "PYTHONFAULTHANDLER": "1"}
        with log_path.open("w") as server_log:
            server = subprocess.Popen([sys.executable, "-m", "uvicorn", "server.app:app", "--host", "127.0.0.1",
                                       "--port", str(port), "--log-level", "error"], cwd=ROOT, env=env,
                                      stdout=server_log, stderr=subprocess.STDOUT)
            try:
                base = f"http://127.0.0.1:{port}"
                ready = False
                for _ in range(100):
                    if server.poll() is not None:
                        break
                    try:
                        if httpx.get(base + "/api/health", timeout=1).status_code == 200:
                            ready = True
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(.2)
                if not ready:
                    raise RuntimeError("server did not become ready: " + log_path.read_text()[-1200:])
                prefix = uuid.uuid4().hex[:8]
                learners = [f"a:load{prefix}{i:04d}" for i in range(args.learners)]
                report = asyncio.run(run(base, learners, args.seconds, args.timeout, routes, stages))
                report["server_exit_before_shutdown"] = server.poll()
            finally:
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()
                if args.server_log:
                    shutil.copy2(log_path, args.server_log)
    report["port"] = port
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
