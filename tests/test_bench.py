import socket
import sqlite3
import time

import httpx
from fastapi.testclient import TestClient

from proxymanager.app import create_app
from test_api import make_settings

A, E = {"X-API-Key": "admin-secret"}, {"X-API-Key": "eval-secret"}
URL = "https://lab.example/page"


def ready_client(tmp_path, monkeypatch, handler=None, **kw):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    handler = handler or (lambda r: httpx.Response(200, text="Producto de prueba"))
    return TestClient(create_app(make_settings(tmp_path, **kw), transport=httpx.MockTransport(handler)))


def add_healthy_proxy(c, tmp_path):
    pid = c.post("/v1/proxies", headers=A, json={"provider": "l", "host": "p.example", "port": 1, "kind": "unknown", "country": "ES"}).json()["id"]
    with sqlite3.connect(str(tmp_path / "test.db")) as db:
        db.execute("INSERT INTO proxy_events (proxy_id, at, source, reachable, duration_ms) VALUES (?, ?, 'check', 1, 5)", (pid, time.time()))
    return pid


def wait(c, run_id, states=("completed", "failed", "cancelled")):
    for _ in range(200):
        r = c.get(f"/v1/benchmarks/{run_id}", headers=A).json()
        if r["state"] in states:
            return r
        time.sleep(0.05)
    raise AssertionError("benchmark no terminó")


def test_benchmark_runs_and_summarizes(tmp_path, monkeypatch):
    with ready_client(tmp_path, monkeypatch) as c:
        pid = add_healthy_proxy(c, tmp_path)
        r = c.post("/v1/benchmarks", headers=A, json={"url": URL + "?secret=1", "requests": 25, "concurrency": 3})
        assert r.status_code == 202
        done = wait(c, r.json()["id"])
    s = done["summary"]
    assert done["state"] == "completed" and s["completed"] == 25 and s["outcomes"] == {"success": 25}
    assert s["per_proxy_requests"] == {pid: 25} and s["latency_ms"]["p50"] is not None and s["bytes_transferred"] > 0
    assert "secret" not in str(done)          # la query no se persiste


def test_limits_scopes_and_destination_guard(tmp_path, monkeypatch):
    with ready_client(tmp_path, monkeypatch, bench_max_requests=10, bench_max_concurrency=2) as c:
        body = {"url": URL, "requests": 5}
        assert c.post("/v1/benchmarks", headers=E, json=body).status_code == 403          # alcance
        assert c.post("/v1/benchmarks", headers=A, json={**body, "requests": 11}).status_code == 422
        assert c.post("/v1/benchmarks", headers=A, json={**body, "concurrency": 3}).status_code == 422
        assert c.post("/v1/benchmarks", headers=A, json={**body, "url": "https://other.example/"}).status_code == 422


def test_only_one_active_benchmark(tmp_path, monkeypatch):
    with ready_client(tmp_path, monkeypatch) as c:
        add_healthy_proxy(c, tmp_path)
        first = c.post("/v1/benchmarks", headers=A, json={"url": URL, "requests": 100, "rps": 5}).json()["id"]   # ~20 s: sigue activo
        assert c.post("/v1/benchmarks", headers=A, json={"url": URL, "requests": 5}).status_code == 409
        c.post(f"/v1/benchmarks/{first}/cancel", headers=A)
        assert wait(c, first)["state"] == "cancelled"
        assert c.post("/v1/benchmarks", headers=A, json={"url": URL, "requests": 5}).status_code == 202   # libre otra vez


def test_no_healthy_proxy_fails_cleanly(tmp_path, monkeypatch):
    with ready_client(tmp_path, monkeypatch) as c:
        done = wait(c, c.post("/v1/benchmarks", headers=A, json={"url": URL, "requests": 5}).json()["id"])
    assert done["state"] == "failed" and done["summary"]["stopped_because"] == "no_healthy_proxy"


def test_cancel_and_byte_budget(tmp_path, monkeypatch):
    slow = lambda r: httpx.Response(200, text="Producto de prueba" * 100)
    with ready_client(tmp_path, monkeypatch, handler=slow, bench_max_bytes=5000) as c:
        add_healthy_proxy(c, tmp_path)
        done = wait(c, c.post("/v1/benchmarks", headers=A, json={"url": URL, "requests": 500, "concurrency": 1}).json()["id"])
        assert done["state"] == "failed" and done["summary"]["stopped_because"] == "byte_budget" and done["summary"]["completed"] < 500
        rid = c.post("/v1/benchmarks", headers=A, json={"url": URL, "requests": 500, "concurrency": 1, "rps": 50}).json()["id"]
        assert c.post(f"/v1/benchmarks/{rid}/cancel", headers=A).status_code == 202
        assert wait(c, rid)["state"] == "cancelled"
        assert c.post(f"/v1/benchmarks/{rid}/cancel", headers=A).status_code == 404       # ya terminado


def test_interrupted_run_is_not_retried(tmp_path):
    from proxymanager.bench import BenchStore
    store = BenchStore(str(tmp_path / "b.db"))
    rid = store.create("o", {"url": URL})
    store.claim()
    store.recover()
    got = store.get(rid)
    assert got["state"] == "failed" and got["summary"] == {"error": "interrupted"} and store.claim() is None
