import socket

import httpx
import pytest
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
