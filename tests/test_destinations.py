import socket

import httpx
import pytest
from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.destinations import DestinationStore, normalize_host
from test_api import make_settings

A, E = {"X-API-Key": "admin-secret"}, {"X-API-Key": "eval-secret"}
NOTE = "Autorización escrita del titular, 12/11/2026"


@pytest.mark.parametrize("good,expected", [("Example.COM", "example.com"), (" sitio.example. ", "sitio.example"), ("www.sub.dominio.es", "www.sub.dominio.es")])
def test_normalize_accepts_plain_hostnames(good, expected):
    assert normalize_host(good) == expected


@pytest.mark.parametrize("bad", ["", "localhost", "intranet", "10.0.0.5", "8.8.8.8", "[::1]", "https://a.example", "a.example:8080", "a.example/ruta", "*.example.com",
                                  "a_b.example", "-a.example", "a.example?x=1", "servidor.local", "api.internal", "a b.example", "x" * 300 + ".com"])
def test_normalize_rejects_ips_schemes_ports_wildcards_and_internal_names(bad):
    with pytest.raises(ValueError):
        normalize_host(bad)


def test_store_requires_note_blocks_duplicates_and_env_hosts_cannot_be_removed(tmp_path):
    store = DestinationStore(str(tmp_path / "d.db"), ("env.example",))
    assert store.hosts() == {"env.example"}
    with pytest.raises(ValueError):
        store.add("a.example", "ok", "o")                  # falta una referencia real de la autorización
    with pytest.raises(ValueError):
        store.add("env.example", NOTE, "o")                   # ya viene del servidor
    added = store.add("A.Example", NOTE, "owner-hash")
    assert added["host"] == "a.example" and store.hosts() == {"env.example", "a.example"}   # visible al instante en este proceso
    with pytest.raises(ValueError):
        store.add("a.example", NOTE, "o")
    assert store.remove("env.example") is False and store.remove("a.example") is True
    assert store.hosts() == {"env.example"}
    assert [i["source"] for i in store.list()] == ["entorno"]


def test_api_scopes_confirmation_and_audit(tmp_path):
    with TestClient(create_app(make_settings(tmp_path, allowed_hosts=("lab.example",)))) as c:
        body = {"host": "nuevo.example", "note": NOTE, "confirmed": True}
        assert c.get("/v1/destinations", headers=E).status_code == 200                   # el evaluador puede verlos
        assert c.post("/v1/destinations", headers=E, json=body).status_code == 403       # pero no añadir
        assert c.post("/v1/destinations", headers=A, json={**body, "confirmed": False}).status_code == 422
        assert c.post("/v1/destinations", headers=A, json={**body, "host": "10.0.0.1"}).status_code == 422
        assert c.post("/v1/destinations", headers=A, json={**body, "note": ""}).status_code == 422
        assert c.post("/v1/destinations", headers=A, json=body).status_code == 201
        listed = {i["host"]: i for i in c.get("/v1/destinations", headers=E).json()}
        assert listed["lab.example"]["source"] == "entorno" and listed["nuevo.example"]["note"] == NOTE
        assert "nuevo.example" in c.get("/v1/system", headers=E).json()["allowed_hosts"]
        assert c.delete("/v1/destinations/lab.example", headers=A).status_code == 404    # los del entorno no se quitan
        assert c.delete("/v1/destinations/nuevo.example", headers=E).status_code == 403
        assert c.delete("/v1/destinations/nuevo.example", headers=A).status_code == 204
        events = c.get("/v1/audit", headers=A).json()
    assert any(e["method"] == "POST" and e["route"] == "/v1/destinations" and e["status"] == 201 for e in events)


def test_scrape_follows_panel_destinations_live_and_private_ips_stay_blocked(tmp_path, monkeypatch):
    resolved = {"nuevo.example": "8.8.8.8", "interno.example": "10.0.0.7"}
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, *a, **k: [(2, 1, 6, "", (resolved[host], 443))])
    handler = lambda r: httpx.Response(200, text="Producto de prueba")
    with TestClient(create_app(make_settings(tmp_path, allowed_hosts=("lab.example",)), transport=httpx.MockTransport(handler))) as c:
        scrape = lambda host: c.post("/scrape", headers=E, json={"url": f"https://{host}/"})
        assert scrape("nuevo.example").status_code == 422                                          # aún no autorizado
        for host in ("nuevo.example", "interno.example"):
            assert c.post("/v1/destinations", headers=A, json={"host": host, "note": NOTE, "confirmed": True}).status_code == 201
        assert scrape("nuevo.example").status_code == 200                                          # vigente sin reiniciar
        blocked = scrape("interno.example")
        assert blocked.status_code == 422 and "no pública" in blocked.text                         # autorizado, pero resuelve a IP privada
        assert c.delete("/v1/destinations/nuevo.example", headers=A).status_code == 204
        assert scrape("nuevo.example").status_code == 422                                          # revocado al instante
