"""Benchmarks acotados: una ejecución a la vez, con topes de solicitudes, concurrencia y bytes.

Solo contra hosts de la allowlist. Un benchmark interrumpido por un reinicio NO se reintenta
automáticamente (repetir tráfico externo exige decisión humana)."""
import asyncio
import json
import sqlite3
import time
import uuid

from .fetch import fetch, guard_url
from .selection import NoHealthyProxy, ProxyBusy
from .transport import PinnedProxyTransport


class BenchConflict(ValueError):
    pass


class BenchStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS bench_runs (id TEXT PRIMARY KEY, owner TEXT NOT NULL, created REAL, started REAL, finished REAL, state TEXT NOT NULL, params TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '{}', cancel INTEGER NOT NULL DEFAULT 0)")

    def create(self, owner: str, params: dict) -> str:
        run_id = "bnc_" + uuid.uuid4().hex
        with sqlite3.connect(self.db_path, isolation_level=None) as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM bench_runs WHERE state IN ('queued','running')").fetchone():
                db.execute("ROLLBACK")
                raise BenchConflict("Ya hay un benchmark en cola o ejecución")
            db.execute("INSERT INTO bench_runs (id, owner, created, state, params) VALUES (?, ?, ?, 'queued', ?)", (run_id, owner, time.time(), json.dumps(params)))
            db.execute("COMMIT")
        return run_id

    def claim(self):
        with sqlite3.connect(self.db_path, isolation_level=None) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT id, params FROM bench_runs WHERE state='queued' ORDER BY created LIMIT 1").fetchone()
            if row:
                db.execute("UPDATE bench_runs SET state='running', started=? WHERE id=?", (time.time(), row[0]))
            db.execute("COMMIT")
        return (row[0], json.loads(row[1])) if row else None

    def get(self, run_id: str, owner: str | None = None) -> dict | None:
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT id, owner, created, started, finished, state, params, summary, cancel FROM bench_runs WHERE id=?", (run_id,)).fetchone()
        if row is None or (owner is not None and row[1] != owner):
            return None
        return {"id": row[0], "created_at": row[2], "started_at": row[3], "finished_at": row[4], "state": row[5], "params": json.loads(row[6]), "summary": json.loads(row[7]), "cancel_requested": bool(row[8])}

    def recent(self, owner: str, limit: int = 20) -> list[dict]:
        with sqlite3.connect(self.db_path) as db:
            ids = [r[0] for r in db.execute("SELECT id FROM bench_runs WHERE owner=? ORDER BY created DESC LIMIT ?", (owner, min(limit, 100))).fetchall()]
        return [self.get(i, owner) for i in ids]

    def cancel(self, run_id: str, owner: str) -> bool:
        with sqlite3.connect(self.db_path) as db:
            n = db.execute("UPDATE bench_runs SET cancel=1 WHERE id=? AND owner=? AND state IN ('queued','running')", (run_id, owner)).rowcount
            db.execute("UPDATE bench_runs SET state='cancelled', finished=? WHERE id=? AND state='queued' AND cancel=1", (time.time(), run_id))
        return bool(n)

    def cancelled(self, run_id: str) -> bool:
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT cancel FROM bench_runs WHERE id=?", (run_id,)).fetchone()
        return bool(row and row[0])

    def save(self, run_id: str, summary: dict, state: str | None = None) -> None:
        with sqlite3.connect(self.db_path) as db:
            if state:
                db.execute("UPDATE bench_runs SET summary=?, state=?, finished=? WHERE id=?", (json.dumps(summary), state, time.time(), run_id))
            else:
                db.execute("UPDATE bench_runs SET summary=? WHERE id=?", (json.dumps(summary), run_id))

    def recover(self) -> None:
        dead = json.dumps({"error": "interrupted"})
        with sqlite3.connect(self.db_path) as db:
            db.execute("UPDATE bench_runs SET state='failed', summary=?, finished=? WHERE state='running'", (dead, time.time()))


def percentile(sorted_values: list[float], p: float) -> float | None:
    if not sorted_values:
        return None
    return round(sorted_values[min(len(sorted_values) - 1, int(p * len(sorted_values)))], 2)


class BenchRunner:
    def __init__(self, bench: BenchStore, metrics, health, settings, transport=None):
        self.bench, self.metrics, self.health, self.settings, self.transport = bench, metrics, health, settings, transport

    async def worker(self):
        while True:
            job = await asyncio.to_thread(self.bench.claim)
            if job is None:
                await asyncio.sleep(self.settings.health_poll_seconds)
                continue
            try:
                await self.execute(*job)
            except Exception as exc:  # noqa: BLE001 - nunca dejar una ejecución colgada en 'running'
                await asyncio.to_thread(self.bench.save, job[0], {"error": type(exc).__name__}, "failed")

    async def execute(self, run_id: str, params: dict):
        url, total, workers = params["url"], params["requests"], params["concurrency"]
        gap = 1.0 / params["rps"] if params.get("rps") else 0.0
        _, hostname = guard_url(url, self.settings)
        started = time.perf_counter()
        outcomes: dict[str, int] = {}
        per_proxy: dict[str, int] = {}
        latencies: list[float] = []
        state = {"issued": 0, "done": 0, "bytes": 0, "stop": None}
        lock = asyncio.Lock()

        def summary():
            elapsed = max(time.perf_counter() - started, 1e-9)
            ordered = sorted(latencies)
            return {"requested": total, "completed": state["done"], "outcomes": dict(outcomes), "stopped_because": state["stop"],
                    "latency_ms": {"p50": percentile(ordered, 0.5), "p95": percentile(ordered, 0.95), "max": percentile(ordered, 0.999999)},
                    "bytes_transferred": state["bytes"], "duration_s": round(elapsed, 2), "achieved_rps": round(state["done"] / elapsed, 2),
                    "per_proxy_requests": dict(per_proxy)}

        async def one():
            proxy_id, route = None, self.transport
            if params["use_proxy"]:
                while True:
                    try:
                        proxy_id = self.metrics.choose(params.get("country"), None, acquire=True)
                        break
                    except ProxyBusy:
                        await asyncio.sleep(0.05)
                route = self.transport or PinnedProxyTransport(self.health.connection(proxy_id), hostname)
            try:
                result = await fetch(url, self.settings, route)
            finally:
                if proxy_id:
                    self.metrics.release(proxy_id)
            if proxy_id:
                self.metrics.record(proxy_id, "bench", result.get("status_code") is not None, result.get("duration_ms"))
            return proxy_id, result

        async def loop():
            while True:
                async with lock:
                    if state["stop"] or state["issued"] >= total:
                        return
                    if state["bytes"] >= self.settings.bench_max_bytes:
                        state["stop"] = "byte_budget"
                        return
                    if state["issued"] % 10 == 0 and await asyncio.to_thread(self.bench.cancelled, run_id):
                        state["stop"] = "cancelled"
                        return
                    state["issued"] += 1
                    if gap:
                        await asyncio.sleep(gap)
                try:
                    proxy_id, result = await one()
                except NoHealthyProxy:
                    async with lock:
                        state["stop"] = "no_healthy_proxy"
                    return
                except Exception:  # noqa: BLE001
                    proxy_id, result = None, {"status_code": None}
                if result.get("success"):
                    kind = "success"
                elif result.get("status_code") is None:
                    kind = "transport_error"
                elif result.get("validation", {}).get("challenge_detected"):
                    kind = "challenge"
                else:
                    kind = "unexpected_response"
                async with lock:
                    outcomes[kind] = outcomes.get(kind, 0) + 1
                    state["done"] += 1
                    state["bytes"] += result.get("bytes_transferred", 0)
                    if result.get("duration_ms") is not None:
                        latencies.append(result["duration_ms"])
                    if proxy_id:
                        per_proxy[proxy_id] = per_proxy.get(proxy_id, 0) + 1
                    if state["done"] % 50 == 0:
                        await asyncio.to_thread(self.bench.save, run_id, summary())

        await asyncio.gather(*(loop() for _ in range(workers)))
        final = "cancelled" if state["stop"] == "cancelled" else ("failed" if state["stop"] else "completed")
        await asyncio.to_thread(self.bench.save, run_id, summary(), final)
