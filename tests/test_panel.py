import re
import socket

from fastapi.testclient import TestClient

from proxymanager.app import create_app
from test_api import make_settings

A, E = {"X-API-Key": "admin-secret"}, {"X-API-Key": "eval-secret"}


def test_panel_is_static_with_strict_headers_and_no_inline_code(tmp_path):
    with TestClient(create_app(make_settings(tmp_path))) as c:
        page = c.get("/panel")
        assert page.status_code == 200 and "default-src 'self'" in page.headers["content-security-policy"]
        assert page.headers["x-content-type-options"] == "nosniff"
        assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", page.text)       # sin scripts en línea
        assert "onclick" not in page.text and "<style" not in page.text and "style=" not in page.text   # CSP sin unsafe-inline
        assert c.get("/panel/style.css").headers["content-type"].startswith("text/css")
        scripts = ""
        for name in ("icons.js", "charts.js", "app.js"):
            script = c.get(f"/panel/{name}")
            assert script.status_code == 200 and "javascript" in script.headers["content-type"] and f"/panel/{name}" in page.text
            assert "innerHTML" not in script.text and "outerHTML" not in script.text and "insertAdjacentHTML" not in script.text   # solo textContent
            assert "eval(" not in script.text and "document.write" not in script.text
            scripts += script.text
        assert "admin-secret" not in page.text + scripts
        for view in ("overview", "proxies", "sessions", "bench", "keys", "playground", "usage", "expenses", "audit"):
            assert f'data-view="{view}"' in page.text and f'id="view-{view}"' in page.text
        assert "PROXYMANAGER_API_KEY" in scripts                                  # los ejemplos de código usan una variable, nunca la clave real


def test_overview_and_benchmark_list_require_scopes(tmp_path):
    with TestClient(create_app(make_settings(tmp_path))) as c:
        assert c.get("/v1/overview").status_code == 401
        pid = c.post("/v1/proxies", headers=A, json={"provider": "lab", "host": "p.example", "port": 1, "kind": "unknown", "country": "ES", "username": None}).json()["id"]
        data = c.get("/v1/overview", headers=E).json()
        assert data["total"] == 1 and data["healthy"] == 0 and data["proxies"][0]["id"] == pid
        assert "password" not in str(data) and "host" in data["proxies"][0]            # sin credenciales
        assert c.get("/v1/benchmarks", headers=E).status_code == 403
        assert c.get("/v1/benchmarks", headers=A).json() == []
