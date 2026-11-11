import socket
import sqlite3
import time

import httpx
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.selection import ProxyMetrics
from test_api import make_settings

A, E = {"X-API-Key": "admin-secret"}, {"X-API-Key": "eval-secret"}


def test_openapi_and_docs_hidden_only_in_strict_mode(tmp_path):
    open_app = TestClient(create_app(make_settings(tmp_path)))
    assert open_app.get("/docs").status_code == 200 and open_app.get("/openapi.json").status_code == 200
    strict = TestClient(create_app(make_settings(tmp_path / "s" if (tmp_path / "s").mkdir() is None else tmp_path, strict=True)))
    assert [strict.get(p).status_code for p in ("/docs", "/redoc", "/openapi.json")] == [404, 404, 404]
    assert strict.get("/panel").status_code == 200 and strict.get("/health").status_code == 200


def test_traffic_bytes_are_recorded_per_proxy_and_cost_estimated(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    body = "Producto de prueba" * 50
    settings = make_settings(tmp_path, proxy_cost_per_gb_usd=4.0)
    with TestClient(create_app(settings, transport=httpx.MockTransport(lambda r: httpx.Response(200, text=body)))) as c:
        pid = c.post("/v1/proxies", headers=A, json={"provider": "l", "host": "p.example", "port": 1, "kind": "unknown", "country": "ES"}).json()["id"]
        with sqlite3.connect(settings.db_path) as db:
            db.execute("INSERT INTO proxy_events (proxy_id, at, source, reachable, duration_ms) VALUES (?, ?, 'check', 1, 5)", (pid, time.time()))
        for _ in range(3):
            assert c.post("/scrape", headers=E, json={"url": "https://lab.example/", "use_proxy": True}).status_code == 200
        data = c.get("/v1/overview", headers=E).json()
    expected = 3 * len(body.encode())
    assert data["traffic_month_bytes"] == expected == data["proxies"][0]["traffic_month_bytes"]
    assert data["estimated_proxy_cost_usd"] == round(expected / 1e9 * 4.0, 4)


def test_events_older_than_retention_are_purged_and_old_months_not_counted(tmp_path):
    from proxymanager.proxies import ProxyStore
    db = str(tmp_path / "m.db"); ProxyStore(db)
    m = ProxyMetrics(db)
    m.record("p", "check", True, 5, 1000)
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO proxy_events (proxy_id, at, source, reachable, bytes) VALUES ('p', ?, 'check', 1, 999)", (time.time() - 60 * 86400,))
    assert m.traffic_month() == {"p": 1000}
    assert m.purge_events(35) == 1


def test_batch_import_endpoint(tmp_path):
    settings = make_settings(tmp_path, credential_key=Fernet.generate_key().decode())
    with TestClient(create_app(settings)) as c:
        batch = "h1.example:8080:user1:pass1\nh2.example:8081:user2:pa:ss2\n"
        assert c.post("/v1/proxies/import", headers=E, json={"provider": "x", "text": batch}).status_code == 403
        r = c.post("/v1/proxies/import", headers=A, json={"provider": "x", "text": batch})
        assert r.status_code == 201 and r.json() == {"added": 2, "duplicates_skipped": 0, "total": 2}
        again = c.post("/v1/proxies/import", headers=A, json={"provider": "x", "text": batch}).json()
        assert again["added"] == 0 and again["duplicates_skipped"] == 2 and again["total"] == 2
        bad = c.post("/v1/proxies/import", headers=A, json={"provider": "x", "text": "h3.example:99999:SECRETUSER:SECRETPASS\n"})
        assert bad.status_code == 422 and "SECRET" not in bad.text and "línea 1" in bad.text
        assert c.post("/v1/proxies/import", headers=A, json={"provider": "x", "text": "\n".join(f"h{i}.example:1:u:p" for i in range(501))}).status_code == 422
        assert c.post("/v1/proxies/import", headers=A, json={"provider": "x", "text": "a" * 70_000}).status_code == 413
        assert "pass1" not in c.get("/v1/proxies", headers=A).text
    no_key = TestClient(create_app(make_settings(tmp_path / "n" if (tmp_path / "n").mkdir() is None else tmp_path)))
    assert no_key.post("/v1/proxies/import", headers=A, json={"provider": "x", "text": "h.example:1:u:p"}).status_code == 422
