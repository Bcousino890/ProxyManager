import socket

import httpx
import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.selection import NoHealthyProxy, ProxyMetrics
from test_api import make_settings

A, E = {"X-API-Key": "admin-secret"}, {"X-API-Key": "eval-secret"}


def add_proxy(client, country="ES", host="proxy.example"):
    return client.post("/v1/proxies", headers=A, json={"provider": "lab", "host": host, "port": 8080, "kind": "unknown", "country": country}).json()["id"]


def test_metrics_health_rules(tmp_path):
    from proxymanager.proxies import ProxyStore
    db = str(tmp_path / "m.db")
    ProxyStore(db)
    m = ProxyMetrics(db, min_success_rate=0.5)
    assert m.stats("none")["healthy"] is False
    m.record("p", "check", True, 10); m.record("p", "check", False)
    assert m.stats("p")["success_rate"] == 0.5 and m.stats("p")["healthy"] is True
    m.record("p", "check", False)
    assert m.stats("p")["healthy"] is False


def test_choose_prefers_best_rate_sticks_to_session_and_filters_country(tmp_path):
    from proxymanager.proxies import ProxyStore
    db = str(tmp_path / "m.db")
    store = ProxyStore(db)
    a = store.create("l", "a.example", 1, "unknown", "ES", None, None)["id"]
    b = store.create("l", "b.example", 1, "unknown", "FR", None, None)["id"]
    m = ProxyMetrics(db)
    m.record(a, "check", True, 5); m.record(a, "check", False)
    m.record(b, "check", True, 5)
    assert m.choose() == b                       # mejor tasa
    assert m.choose("es") == a                   # filtro de país, sin distinguir mayúsculas
    assert m.choose(session_id="s1") == b
    for _ in range(5):
        m.record(a, "check", True, 1)            # a mejora, pero la sesión sigue en b mientras b esté sano
    assert m.choose(session_id="s1") == b
    m.record(b, "check", False); m.record(b, "check", False); m.record(b, "check", False)
    assert m.choose(session_id="s1") == a        # b deja de estar sano: se reasigna
    with pytest.raises(NoHealthyProxy):
        m.choose("DE")


def test_scrape_via_proxy_requires_healthy_proxy_then_records_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    transport = httpx.MockTransport(lambda r: httpx.Response(200, text="Producto de prueba"))
    with TestClient(create_app(make_settings(tmp_path), transport=transport)) as c:
        body = {"url": "https://lab.example/", "use_proxy": True}
        assert c.post("/scrape", headers=E, json=body).status_code == 503     # sin comprobaciones previas
        pid = add_proxy(c)
        route = f"/v1/proxies/{pid}/checks"
        c.post(route, headers=A, json={"url": "https://lab.example/"})
        import time
        for _ in range(100):
            if c.get(route, headers=A).json()[0]["state"] == "completed":
                break
            time.sleep(0.05)
        r = c.post("/scrape", headers=E, json=body)
        assert r.status_code == 200 and r.json()["proxy_id"] == pid and "proxy.example" not in r.text
        stats = c.get(f"/v1/proxies/{pid}/stats", headers=E).json()
        assert stats["events"] == 2 and stats["healthy"] is True
        assert c.post("/scrape", headers=E, json={"url": "https://lab.example/"}).json()["proxy_id"] is None


def _store(tmp_path, n=3, **kw):
    from proxymanager.proxies import ProxyStore
    db = str(tmp_path / "r.db")
    store = ProxyStore(db)
    ids = [store.create("l", f"h{i}.example", 1, "unknown", "ES", None, None)["id"] for i in range(n)]
    return ProxyMetrics(db, **kw), ids


def test_prefers_lower_latency_among_equally_reliable(tmp_path):
    m, (a, b, c) = _store(tmp_path)
    for pid, ms in ((a, 300), (b, 80), (c, 150)):
        m.record(pid, "check", True, ms)
    assert m.choose() == b


def test_spreads_load_and_respects_inflight_limit(tmp_path):
    m, (a, b, c) = _store(tmp_path, max_inflight=1)
    for pid, ms in ((a, 100), (b, 200), (c, 300)):
        m.record(pid, "check", True, ms)
    picked = [m.choose(acquire=True) for _ in range(3)]
    assert sorted(picked) == sorted([a, b, c])        # una por proxy, aunque a sea más rápido
    from proxymanager.selection import ProxyBusy
    with pytest.raises(ProxyBusy):
        m.choose(acquire=True)
    m.release(a)
    assert m.choose(acquire=True) == a


def test_much_worse_reliability_is_not_chosen_even_if_idle(tmp_path):
    m, (a, b, _) = _store(tmp_path)
    for _ in range(4):
        m.record(a, "check", True, 500)
    m.record(b, "check", True, 10); m.record(b, "check", False)
    assert m.choose(acquire=True) == a and m.choose(acquire=True) == a


def test_inflight_is_released_after_each_request(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    app = create_app(make_settings(tmp_path, proxy_max_inflight=1), transport=httpx.MockTransport(lambda r: httpx.Response(200, text="Producto de prueba")))
    with TestClient(app) as c:
        pid = add_proxy(c)
        import sqlite3, time
        with sqlite3.connect(str(tmp_path / "test.db")) as db:
            db.execute("INSERT INTO proxy_events (proxy_id, at, source, reachable, duration_ms) VALUES (?, ?, 'check', 1, 5)", (pid, time.time()))
        body = {"url": "https://lab.example/", "use_proxy": True}
        assert c.post("/scrape", headers=E, json=body).status_code == 200
        assert c.post("/scrape", headers=E, json=body).status_code == 200   # liberó la concurrencia tras la primera


def test_scrape_transport_error_does_not_echo_exception_text(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    def broken(request):
        raise httpx.ConnectError("proxy http://user:private-password@p.example:8080 refused")
    with TestClient(create_app(make_settings(tmp_path), transport=httpx.MockTransport(broken))) as c:
        r = c.post("/scrape", headers=E, json={"url": "https://lab.example/"})
    assert r.status_code == 200 and "private-password" not in r.text and r.json()["error"]["message"] == "ConnectError"


def _two_healthy(c, tmp_path):
    ids = [add_proxy(c, host=f"p{i}.example") for i in range(2)]
    with sqlite3.connect(str(tmp_path / "test.db")) as db:
        for pid in ids:
            db.execute("INSERT INTO proxy_events (proxy_id, at, source, reachable, duration_ms) VALUES (?, ?, 'check', 1, 5)", (pid, time.time()))
    return ids


import sqlite3
import time


def test_scrape_fails_over_to_another_proxy_on_transport_error_only(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    calls = []
    def flaky(request):
        calls.append(1)
        if len(calls) == 1:
            raise httpx.ConnectError("boom")
        return httpx.Response(200, text="Producto de prueba")
    with TestClient(create_app(make_settings(tmp_path, proxy_max_inflight=1, credential_key=Fernet.generate_key().decode()), transport=httpx.MockTransport(flaky))) as c:
        a, b = _two_healthy(c, tmp_path)
        sid = c.post("/v1/sessions", headers=E).json()["session_id"]
        r = c.post("/scrape", headers=E, json={"url": "https://lab.example/", "use_proxy": True, "session_id": sid}).json()
        assert r.get("success") is True and r["attempts"] == 2 and len(calls) == 2, r
        first_failed = [p for p in (a, b) if p != r["proxy_id"]][0]
        assert c.get(f"/v1/proxies/{first_failed}/stats", headers=E).json()["reachable"] == 1   # 1 de 2 eventos: el fallo quedó registrado
        again = c.post("/scrape", headers=E, json={"url": "https://lab.example/", "use_proxy": True, "session_id": sid}).json()
        assert again["proxy_id"] == r["proxy_id"]                    # la sesión quedó ligada al proxy que funcionó
        for _ in range(3):                                           # sin fugas de concurrencia (límite 1)
            assert c.post("/scrape", headers=E, json={"url": "https://lab.example/", "use_proxy": True}).status_code == 200


def test_no_failover_on_site_errors_and_gives_up_when_all_proxies_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    with TestClient(create_app(make_settings(tmp_path), transport=httpx.MockTransport(lambda r: httpx.Response(500, text="x")))) as c:
        _two_healthy(c, tmp_path)
        r = c.post("/scrape", headers=E, json={"url": "https://lab.example/", "use_proxy": True}).json()
        assert r["attempts"] == 1 and r["status_code"] == 500          # el proxy respondió: no es fallo del proxy
    def down(request):
        raise httpx.ConnectError("boom")
    with TestClient(create_app(make_settings(tmp_path / "x" if (tmp_path / "x").mkdir() is None else tmp_path), transport=httpx.MockTransport(down))) as c:
        _two_healthy(c, tmp_path / "x")
        r = c.post("/scrape", headers=E, json={"url": "https://lab.example/", "use_proxy": True}).json()
        assert r["attempts"] == 2 and r["success"] is False and r["error"]["type"] == "transport_error"
