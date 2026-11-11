import sqlite3
import threading

from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.limits import RateLimiter
from test_api import make_settings


def test_limiter_window_and_owner_isolation():
    now = [0.0]
    limiter = RateLimiter(2, 10, lambda: now[0])
    assert limiter.check("a") == 0 and limiter.check("a") == 0
    assert limiter.check("a") > 0
    assert limiter.check("b") == 0
    now[0] = 10.0
    assert limiter.check("a") == 0


def test_limiter_concurrent_never_exceeds_limit():
    limiter = RateLimiter(5, 60)
    results = []
    threads = [threading.Thread(target=lambda: results.append(limiter.check("a"))) for _ in range(40)]
    [t.start() for t in threads]; [t.join() for t in threads]
    assert sum(1 for r in results if r == 0) == 5


def test_api_returns_429_with_retry_after(tmp_path):
    app = create_app(make_settings(tmp_path, rate_limit_requests=2))
    with TestClient(app) as client:
        h = {"X-API-Key": "eval-secret"}
        assert client.get("/v1/system", headers=h).status_code == 200
        assert client.get("/v1/system", headers=h).status_code == 200
        r = client.get("/v1/system", headers=h)
        assert r.status_code == 429 and int(r.headers["Retry-After"]) >= 1
        assert client.get("/health").status_code == 200


def test_audit_has_no_secrets_or_urls(tmp_path):
    settings = make_settings(tmp_path)
    app = create_app(settings)
    with TestClient(app) as client:
        client.post("/v1/sessions", headers={"X-API-Key": "eval-secret"})
        sid = client.post("/v1/sessions", headers={"X-API-Key": "eval-secret"}).json()["session_id"]
        client.get(f"/v1/sessions/{sid}?token=SECRETQ", headers={"X-API-Key": "eval-secret"})
        assert client.get("/v1/audit", headers={"X-API-Key": "eval-secret"}).status_code == 403
        events = client.get("/v1/audit", headers={"X-API-Key": "admin-secret"}).json()
    dump = repr(events) + repr(sqlite3.connect(settings.db_path).execute("SELECT * FROM audit_events").fetchall())
    assert "SECRETQ" not in dump and sid not in dump and "eval-secret" not in dump
    assert any(e["route"] == "/v1/sessions/{session_id}" and e["status"] == 200 for e in events)
