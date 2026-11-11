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


def test_list_sessions_is_scoped_to_owner_and_excludes_expired(tmp_path):
    app = create_app(make_settings(tmp_path, evaluator_key="first", admin_key="second"))
    with TestClient(app) as client:
        first = {"X-API-Key": "first"}
        second = {"X-API-Key": "second"}
        sid = client.post("/v1/sessions", headers=first).json()["session_id"]
        other = client.post("/v1/sessions", headers=second).json()["session_id"]
        assert [item["session_id"] for item in client.get("/v1/sessions", headers=first).json()] == [sid]
        assert [item["session_id"] for item in client.get("/v1/sessions", headers=second).json()] == [other]
        assert client.delete(f"/v1/sessions/{sid}", headers=first).status_code == 204
        assert client.get("/v1/sessions", headers=first).json() == []
        assert client.get("/v1/sessions").status_code == 401


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


def test_proxy_registration_requires_admin_and_hides_credentials(tmp_path):
    from cryptography.fernet import Fernet
    settings = make_settings(tmp_path, credential_key=Fernet.generate_key().decode())
    app = create_app(settings)
    payload = {"provider": "test-provider", "host": "proxy.example", "port": 8080, "kind": "isp", "country": "ES", "username": "sample-user", "password": "sample-pass"}
    with TestClient(app) as client:
        assert client.post("/v1/proxies", headers={"X-API-Key": "eval-secret"}, json=payload).status_code == 403
        created = client.post("/v1/proxies", headers={"X-API-Key": "admin-secret"}, json=payload)
        assert created.status_code == 201
        listed = client.get("/v1/proxies", headers={"X-API-Key": "eval-secret"})
        assert listed.status_code == 200
        assert listed.json()[0]["provider"] == "test-provider"
        assert "sample-pass" not in listed.text
    assert b"sample-pass" not in (tmp_path / "test.db").read_bytes()


def test_credentials_require_encryption_key(tmp_path):
    app = create_app(make_settings(tmp_path, credential_key=""))
    with TestClient(app) as client:
        result = client.post("/v1/proxies", headers={"X-API-Key": "admin-secret"}, json={"provider": "test", "host": "proxy.example", "port": 8080, "kind": "isp", "country": "ES", "username": "u", "password": "p"})
    assert result.status_code == 503


def test_proxy_network_classification_can_remain_unknown(tmp_path):
    app = create_app(make_settings(tmp_path))
    with TestClient(app) as client:
        result = client.post("/v1/proxies", headers={"X-API-Key": "admin-secret"}, json={"provider": "test-batch", "host": "proxy.example", "port": 8080, "kind": "unknown", "country": "ZZ"})
    assert result.status_code == 201
    assert result.json()["kind"] == "unknown"


def test_database_file_is_private(tmp_path):
    settings = make_settings(tmp_path)
    create_app(settings)
    assert (tmp_path / "test.db").stat().st_mode & 0o777 == 0o600


def test_session_cookies_roundtrip_persist_and_stay_isolated(tmp_path, monkeypatch):
    import socket
    from cryptography.fernet import Fernet

    monkeypatch.setattr(socket, 'getaddrinfo', lambda host, port, type: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 443))])
    observed = []

    def handler(request):
        observed.append(request.headers.get('cookie', ''))
        if request.url.path == '/login':
            return httpx.Response(200, headers={'Set-Cookie': 'sid=private-cookie; Path=/account; Secure; HttpOnly'}, text='Producto de prueba')
        return httpx.Response(200, text='Producto de prueba')

    settings = make_settings(tmp_path, credential_key=Fernet.generate_key().decode())
    headers = {'X-API-Key': 'eval-secret'}
    with TestClient(create_app(settings, transport=httpx.MockTransport(handler))) as client:
        first = client.post('/v1/sessions', headers=headers).json()['session_id']
        second = client.post('/v1/sessions', headers=headers).json()['session_id']
        response = client.post('/scrape', headers=headers, json={'url': 'https://lab.example/login', 'session_id': first})
        assert response.status_code == 200
        assert 'private-cookie' not in response.text
    with TestClient(create_app(settings, transport=httpx.MockTransport(handler))) as client:
        client.post('/scrape', headers=headers, json={'url': 'https://lab.example/account/orders', 'session_id': first})
        client.post('/scrape', headers=headers, json={'url': 'https://lab.example/account/orders', 'session_id': second})
        client.post('/scrape', headers=headers, json={'url': 'https://lab.example/accountant', 'session_id': first})
        client.delete(f'/v1/sessions/{first}', headers=headers)
    assert observed == ['', 'sid=private-cookie', '', '']
    assert b'private-cookie' not in (tmp_path / 'test.db').read_bytes()


def test_session_scrape_requires_cookie_encryption_key(tmp_path):
    app = create_app(make_settings(tmp_path, credential_key=''))
    with TestClient(app) as client:
        headers = {'X-API-Key': 'eval-secret'}
        session_id = client.post('/v1/sessions', headers=headers).json()['session_id']
        response = client.post('/scrape', headers=headers, json={'url': 'https://lab.example/', 'session_id': session_id})
        assert response.status_code == 503
