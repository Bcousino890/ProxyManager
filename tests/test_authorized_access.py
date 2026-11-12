import json
import socket

import httpx
import pytest
from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.config import Settings
from test_api import make_settings

A, E = {"X-API-Key": "admin-secret"}, {"X-API-Key": "eval-secret"}
TOKEN = "token-entregado-por-el-sitio-9f3a"



def test_headers_apply_only_to_the_exact_configured_host():
    s = Settings(db_path=":memory:", allowed_hosts=("a.example", "b.example"), user_agent="Proyecto-Universidad/1.0 (contacto@ejemplo.org)",
                 host_headers_json=json.dumps({"A.example.": {"X-Acceso-Autorizado": TOKEN}}))
    assert s.headers_for("a.example") == {"User-Agent": "Proyecto-Universidad/1.0 (contacto@ejemplo.org)", "X-Acceso-Autorizado": TOKEN}
    assert s.headers_for("b.example") == {"User-Agent": "Proyecto-Universidad/1.0 (contacto@ejemplo.org)"}   # otro host: sin el token
    assert Settings(db_path=":memory:").headers_for("a.example") == {}


@pytest.mark.parametrize("bad", ['[]', '{"a.example": []}', '{"a.example": {}}', '{"a.example": {"Host": "x"}}', '{"a.example": {"Cookie": "x"}}',
                                  '{"a.example": {"X-Api-Key": "x"}}', '{"a.example": {"Bad Name": "x"}}', '{"a.example": {"X-T": "a\\r\\nInjected: 1"}}', '{"a.example": {"X-T": ""}}'])
def test_invalid_host_headers_are_rejected(bad):
    with pytest.raises(ValueError):
        Settings(db_path=":memory:", host_headers_json=bad)


def test_user_agent_with_control_characters_is_rejected():
    with pytest.raises(ValueError):
        Settings(db_path=":memory:", user_agent="mal\nagente")


def test_scrape_sends_authorized_headers_only_to_that_host_and_never_exposes_them(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])
    seen = []
    def handler(request):
        seen.append(dict(request.headers))
        return httpx.Response(200, text="Producto de prueba")
    settings = make_settings(tmp_path, allowed_hosts=("lab.example", "otro.example"), user_agent="Proyecto-Universidad/1.0",
                             host_headers_json=json.dumps({"lab.example": {"X-Acceso-Autorizado": TOKEN}}))
    with TestClient(create_app(settings, transport=httpx.MockTransport(handler))) as c:
        for host in ("lab.example", "otro.example"):
            assert c.post("/scrape", headers=E, json={"url": f"https://{host}/"}).status_code == 200
        exposed = c.get("/v1/system", headers=E).text + c.get("/v1/overview", headers=E).text + c.get("/v1/usage", headers=A).text + c.get("/v1/audit", headers=A).text
    assert seen[0]["x-acceso-autorizado"] == TOKEN and seen[0]["user-agent"] == "Proyecto-Universidad/1.0" and seen[0]["host"] == "lab.example"
    assert "x-acceso-autorizado" not in seen[1] and seen[1]["user-agent"] == "Proyecto-Universidad/1.0"
    assert TOKEN not in exposed
