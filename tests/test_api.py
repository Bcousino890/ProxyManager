import httpx
import pytest
from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.config import Settings


def make_settings(tmp_path, **changes):
    values = dict(db_path=str(tmp_path / "test.db"), evaluator_key="eval-secret", admin_key="admin-secret", allowed_hosts=("lab.example",), expected_text="Producto de prueba")
    values.update(changes)
    return Settings(**values)


def test_health_and_auth(tmp_path):
    app = create_app(make_settings(tmp_path))
    with TestClient(app) as client:
        assert client.get("/health").json()["service"] == "ProxyManager"
        assert client.get("/v1/system").status_code == 401
        assert client.get("/v1/system", headers={"X-API-Key": "eval-secret"}).status_code == 200


def test_session_isolation(tmp_path):
    app = create_app(make_settings(tmp_path, evaluator_key="first", admin_key="second"))
    with TestClient(app) as client:
        created = client.post("/v1/sessions", headers={"X-API-Key": "first"}).json()
        sid = created["session_id"]
        assert client.get(f"/v1/sessions/{sid}", headers={"X-API-Key": "first"}).status_code == 200
        assert client.get(f"/v1/sessions/{sid}", headers={"X-API-Key": "second"}).status_code == 404


def test_scrape_classification_and_destination_guard(tmp_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, type: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))])
    def handler(request):
        if request.url.path == "/challenge":
            return httpx.Response(200, text="CAPTCHA challenge")
        if request.url.path == "/redirect":
            return httpx.Response(302, headers={"Location": "https://elsewhere.example"})
        return httpx.Response(200, text="Producto de prueba")

    app = create_app(make_settings(tmp_path), transport=httpx.MockTransport(handler))
    headers = {"X-API-Key": "eval-secret"}
    with TestClient(app) as client:
        assert client.post("/scrape", headers=headers, json={"url": "http://127.0.0.1/"}).status_code == 422
        assert client.post("/scrape", headers=headers, json={"url": "https://elsewhere.example/"}).status_code == 422
        ok = client.post("/scrape", headers=headers, json={"url": "https://lab.example/product"}).json()
        assert ok["success"] is True and ok["validation"]["content_expected"] is True
        challenge = client.post("/scrape", headers=headers, json={"url": "https://lab.example/challenge"}).json()
        assert challenge["success"] is False and challenge["validation"]["challenge_detected"] is True
        redirect = client.post("/scrape", headers=headers, json={"url": "https://lab.example/redirect"}).json()
        assert redirect["success"] is False


def test_fetch_pins_resolved_public_ip(tmp_path, monkeypatch):
    import socket

    def fake_lookup(host, port, type):
        assert host == "lab.example"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_lookup)
    seen = {}

    def handler(request):
        seen["host"] = request.headers["host"]
        seen["url"] = str(request.url)
        seen["sni"] = request.extensions.get("sni_hostname")
        return httpx.Response(200, text="Producto de prueba")

    app = create_app(make_settings(tmp_path), transport=httpx.MockTransport(handler))
    with TestClient(app) as client:
        response = client.post("/scrape", headers={"X-API-Key": "eval-secret"}, json={"url": "https://lab.example/product"})
    assert response.status_code == 200
    assert seen == {"host": "lab.example", "url": "https://8.8.8.8/product", "sni": "lab.example"}


def test_no_key_configured_denies_access(tmp_path):
    app = create_app(make_settings(tmp_path, evaluator_key="", admin_key=""))
    with TestClient(app) as client:
        assert client.get("/v1/system", headers={"X-API-Key": "anything"}).status_code == 401


def test_private_dns_answer_is_rejected(tmp_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, type: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))])
    called = []
    app = create_app(make_settings(tmp_path), transport=httpx.MockTransport(lambda request: called.append(request) or httpx.Response(200)))
    with TestClient(app) as client:
        result = client.post("/scrape", headers={"X-API-Key": "eval-secret"}, json={"url": "https://lab.example/"})
    assert result.status_code == 422
    assert not called
