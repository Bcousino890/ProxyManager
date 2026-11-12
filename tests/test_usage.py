import socket
import sqlite3
import time

import httpx
from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.usage import UsageStore, classify
from test_api import make_settings

A, E = {"X-API-Key": "admin-secret"}, {"X-API-Key": "eval-secret"}


def test_classify_separates_transport_from_delivery():
    assert classify({"success": True, "status_code": 200}) == "success"
    assert classify({"success": False, "status_code": None}) == "transport_error"
    assert classify({"success": False, "status_code": 403, "validation": {"challenge_detected": True}}) == "challenge"
    assert classify({"success": False, "status_code": 403, "validation": {}}) == "blocked"
    assert classify({"success": False, "status_code": 429}) == "blocked"
    assert classify({"success": False, "status_code": 500}) == "unexpected_response"


def test_summary_buckets_by_day_domain_and_percentiles(tmp_path):
    store = UsageStore(str(tmp_path / "u.db"))
    now = time.time()
    for ms in (100, 200, 300, 400):
        store.record("Lab.Example", "scrape", "p1", {"success": True, "status_code": 200, "duration_ms": ms, "bytes_transferred": 10})
    store.record("other.example", "scrape", "p2", {"success": False, "status_code": 403, "validation": {"challenge_detected": True}, "duration_ms": 50, "bytes_transferred": 5})
    with sqlite3.connect(store.db_path) as db:
        db.execute("INSERT INTO usage_events (at, host, source, outcome, duration_ms, bytes) VALUES (?, 'old.example', 'scrape', 'success', 9, 1)", (now - 40 * 86400,))
    s = store.summary(7)
    assert len(s["daily"]) == 7 and s["daily"][-1]["date"] == s["today"]["date"]
    assert s["totals"]["requests"] == 5 and s["outcomes"]["challenge"] == 1 and s["totals"]["success_rate"] == 0.8
    assert s["today"]["requests"] == 5 and s["today"]["p95_ms"] == 400 and s["today"]["avg_ms"] == 210
    assert [d["host"] for d in s["domains"]] == ["lab.example", "other.example"] and s["domains"][0]["success_rate"] == 1.0
    assert all(d["requests"] == 0 and d["avg_ms"] is None for d in s["daily"][:-1])      # días vacíos: sin inventar latencia
    assert store.summary(1000)["days"] == 90
    assert store.purge(30) == 1


def test_scrape_records_host_only_and_overview_separates_blocking_from_transport(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    handler = lambda r: httpx.Response(403, text="captcha-delivery datadome challenge")
    settings = make_settings(tmp_path)
    with TestClient(create_app(settings, transport=httpx.MockTransport(handler))) as c:
        pid = c.post("/v1/proxies", headers=A, json={"provider": "l", "host": "p.example", "port": 1, "kind": "unknown", "country": "ES"}).json()["id"]
        with sqlite3.connect(settings.db_path) as db:
            db.execute("INSERT INTO proxy_events (proxy_id, at, source, reachable, duration_ms) VALUES (?, ?, 'check', 1, 5)", (pid, time.time()))
        r = c.post("/scrape", headers=E, json={"url": "https://lab.example/secret/path?token=PRIVATE", "use_proxy": True}).json()
        assert r["status_code"] == 403 and r["proxy_id"] == pid
        usage = c.get("/v1/usage?days=7", headers=E).json()
        overview = c.get("/v1/overview", headers=E).json()
    assert usage["outcomes"]["challenge"] == 1 and usage["domains"][0]["host"] == "lab.example"
    stored = str(sqlite3.connect(settings.db_path).execute("SELECT * FROM usage_events").fetchall())
    assert "secret" not in stored and "PRIVATE" not in stored                              # solo el host
    p = overview["proxies"][0]
    assert p["stats"]["healthy"] is True and p["delivery_24h"]["blocked"] == 1 and p["delivery_24h"]["success"] == 0   # sano en transporte, bloqueado por el sitio
    assert overview["concurrency"]["current"] == 0


def test_usage_endpoint_scope_and_bounds_and_system_limits(tmp_path):
    with TestClient(create_app(make_settings(tmp_path, evaluator_scopes=("system:read",)))) as c:
        assert c.get("/v1/usage", headers=E).status_code == 403
        assert c.get("/v1/usage?days=0", headers=A).status_code == 422 and c.get("/v1/usage?days=91", headers=A).status_code == 422
        assert c.get("/v1/usage", headers=A).json()["totals"]["requests"] == 0
        system = c.get("/v1/system", headers=E).json()
        assert system["timeout_seconds"] == 15.0 and system["proxy_max_inflight"] == 5 and "admin" not in str(system)


def test_panel_serves_only_listed_static_files(tmp_path):
    c = TestClient(create_app(make_settings(tmp_path)))
    assert c.get("/panel/app.js").status_code == 200
    for bad in ("/panel/index.html", "/panel/..%2Fapp.py", "/panel/%2e%2e/config.py", "/panel/nothing.js", "/panel/.env"):
        assert c.get(bad).status_code in (404, 405), bad
