import pytest
import asyncio
from scraping_engine.engine import ScrapingEngine

@pytest.mark.asyncio
async def test_health_endpoint():
    engine = ScrapingEngine()
    # Simular una solicitud GET a /health
    from fastapi.testclient import TestClient
    client = TestClient(engine.app)
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_scrape_endpoint():
    engine = ScrapingEngine()
    from fastapi.testclient import TestClient
    client = TestClient(engine.app)
    
    # Prueba con una URL válida (página de prueba)
    response = client.post("/scrape", json={"url": "https://httpbin.org/get"})
    assert response.status_code == 200

import asyncio, httpx
from scraping_engine.engine import ScrapingEngine

def test_httpx_extraction_works_with_and_without_proxy(monkeypatch):
    """Regresión: `httpx.AsyncClient(proxies=...)` ya no existe en httpx 0.28 y la extracción devolvía siempre HTTP 500."""
    real = httpx.AsyncClient
    handler = lambda req: httpx.Response(200, headers={"content-type": "text/html"}, text="<h1>Example Domain</h1>")
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real(**{**kw, "transport": httpx.MockTransport(handler)}))
    eng = ScrapingEngine()
    r = asyncio.run(eng._scrape_with_httpx("https://example.com/", None))
    assert r.status_code == 200 and "Example Domain" in r.content and not r.error and not r.is_datadome_blocked and r.duration_ms >= 0
    r = asyncio.run(eng._scrape_with_httpx("https://example.com/", "http://127.0.0.1:9"))      # proxy muerto: debe intentar usarlo y fallar al CONECTAR, no por argumentos
    assert r.status_code == 500 and "unexpected keyword" not in (r.error or "") and "connect" in (r.error or "").lower()

def test_http_403_datadome_is_flagged_not_success(monkeypatch):
    real = httpx.AsyncClient
    handler = lambda req: httpx.Response(403, headers={"server": "DataDome", "x-datadome": "protected"}, text="Please enable JS")
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real(**{**kw, "transport": httpx.MockTransport(handler)}))
    r = asyncio.run(ScrapingEngine()._scrape_with_httpx("https://www.idealista.com/x", None))
    assert r.status_code == 403 and r.is_datadome_blocked          # BLOQUEADO por antibot, no extracción exitosa


def test_web_panel_form_contract_and_extraction(monkeypatch):
    """Regresión del panel 8002: importaba una clase inexistente y esperaba Form mientras el formulario envía JSON."""
    from fastapi.testclient import TestClient
    from scraping_engine.web_panel import app
    real = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real(**{**kw, "transport": httpx.MockTransport(lambda req: httpx.Response(200, headers={"content-type": "text/html"}, text="<h1>Example Domain</h1>"))}))
    c = TestClient(app)
    assert c.get("/").status_code == 200
    r = c.post("/scrape", json={"url": "https://example.com/", "use_js": False, "proxy": ""})
    assert r.status_code == 200 and r.json()["status_code"] == 200 and "Example Domain" in r.json()["content"] and r.json()["datadome_blocked"] is False
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real(**{**kw, "transport": httpx.MockTransport(lambda req: httpx.Response(403, headers={"server": "DataDome"}, text="enable JS"))}))
    r = c.post("/scrape", json={"url": "https://www.idealista.com/x", "use_js": False})
    assert r.json()["status_code"] == 403 and r.json()["datadome_blocked"] is True
