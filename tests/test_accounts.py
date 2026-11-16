import socket

import httpx
from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.config import Settings

CSRF = {"X-PM-CSRF": "1"}


def make(tmp_path, **changes):
    values = dict(db_path=str(tmp_path / "t.db"), admin_key="admin-secret", cookie_secure=False, allow_any_public_host=True, free_credits=3)
    values.update(changes)
    return Settings(**values)


def public_dns(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, type: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))])


def signup(client, email="a@example.com"):
    r = client.post("/v1/account/signup", json={"email": email, "password": "correct-horse-1"})
    assert r.status_code == 201, r.text
    return r.json()["api_key"]


def ok_transport():
    return httpx.MockTransport(lambda request: httpx.Response(200, text="hola", headers={"X-Seen": request.method}))


def test_signup_login_and_key_is_hashed(tmp_path):
    with TestClient(create_app(make(tmp_path), transport=ok_transport())) as c:
        key = signup(c)
        assert key.startswith("pm_live_")
        assert c.get("/v1/account/me").json()["credits_remaining"] == 3
        keys = c.get("/v1/account/keys").json()
        assert len(keys) == 1 and key not in str(keys)
        assert c.post("/v1/account/signup", json={"email": "a@example.com", "password": "correct-horse-1"}).status_code == 422
        c.cookies.clear()
        assert c.get("/v1/account/me").status_code == 401
        assert c.post("/v1/account/login", json={"email": "a@example.com", "password": "wrong"}).status_code == 401
        assert c.post("/v1/account/login", json={"email": "a@example.com", "password": "correct-horse-1"}).status_code == 200
    assert key.encode() not in (tmp_path / "t.db").read_bytes()


def test_short_password_rejected(tmp_path):
    with TestClient(create_app(make(tmp_path))) as c:
        assert c.post("/v1/account/signup", json={"email": "a@example.com", "password": "short"}).status_code == 422


def test_csrf_header_required_for_mutations(tmp_path):
    with TestClient(create_app(make(tmp_path))) as c:
        signup(c)
        assert c.post("/v1/account/keys", json={"name": "x"}).status_code == 403
        assert c.post("/v1/account/keys", json={"name": "x"}, headers=CSRF).status_code == 201


def test_customer_key_scrape_charges_only_success_and_runs_out(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    with TestClient(create_app(make(tmp_path), transport=ok_transport())) as c:
        key = signup(c)
        h = {"X-API-Key": key}
        for _ in range(3):
            r = c.post("/scrape", headers=h, json={"url": "https://example.org/x", "method": "POST", "body": "a=1"})
            assert r.status_code == 200
            assert r.json()["headers"]["x-seen"] == "POST"
        assert c.get("/v1/account/me").json()["credits_remaining"] == 0
        assert c.post("/scrape", headers=h, json={"url": "https://example.org/"}).status_code == 402
        usage = c.get("/v1/account/usage").json()
        assert usage["requests"] == 3 and usage["credits"] == 3


def test_failed_content_is_free(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    transport = httpx.MockTransport(lambda r: httpx.Response(403, text="captcha"))
    with TestClient(create_app(make(tmp_path), transport=transport)) as c:
        key = signup(c)
        r = c.post("/scrape", headers={"X-API-Key": key}, json={"url": "https://example.org/"})
        assert r.json()["credits_charged"] == 0
        assert c.get("/v1/account/me").json()["credits_remaining"] == 3


def test_per_key_limit_and_revocation(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    with TestClient(create_app(make(tmp_path, free_credits=50), transport=ok_transport())) as c:
        signup(c)
        created = c.post("/v1/account/keys", json={"name": "ci", "credit_limit": 1}, headers=CSRF).json()
        h = {"X-API-Key": created["key"]}
        assert c.post("/scrape", headers=h, json={"url": "https://example.org/"}).status_code == 200
        assert c.post("/scrape", headers=h, json={"url": "https://example.org/"}).status_code == 402
        assert c.delete(f"/v1/account/keys/{created['id']}", headers=CSRF).status_code == 204
        assert c.post("/scrape", headers=h, json={"url": "https://example.org/"}).status_code == 401


def test_customers_cannot_reach_staff_endpoints(tmp_path):
    with TestClient(create_app(make(tmp_path))) as c:
        key = signup(c)
        h = {"X-API-Key": key}
        assert c.get("/v1/proxies", headers=h).status_code == 401
        assert c.get("/v1/system", headers=h).status_code == 401
        assert c.get("/v1/admin/users", headers=h).status_code == 403


def test_rate_limit(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    with TestClient(create_app(make(tmp_path, free_credits=50, rate_limit_per_minute=2), transport=ok_transport())) as c:
        h = {"X-API-Key": signup(c)}
        codes = [c.post("/scrape", headers=h, json={"url": "https://example.org/"}).status_code for _ in range(3)]
        assert codes == [200, 200, 429]


def test_open_mode_still_blocks_private_and_blocklist(tmp_path, monkeypatch):
    with TestClient(create_app(make(tmp_path, blocked_hosts=("blocked.example",)), transport=ok_transport())) as c:
        h = {"X-API-Key": signup(c)}
        monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, type: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 443))])
        assert c.post("/scrape", headers=h, json={"url": "https://internal.example/"}).status_code == 422
        public_dns(monkeypatch)
        assert c.post("/scrape", headers=h, json={"url": "https://a.blocked.example/"}).status_code == 422
        assert c.post("/scrape", headers=h, json={"url": "https://localhost/"}).status_code == 422
        assert c.post("/scrape", headers=h, json={"url": "http://example.org/"}).status_code == 422


def test_closed_mode_default_denies(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    with TestClient(create_app(make(tmp_path, allow_any_public_host=False), transport=ok_transport())) as c:
        h = {"X-API-Key": signup(c)}
        assert c.post("/scrape", headers=h, json={"url": "https://example.org/"}).status_code == 422


def test_sessions_isolated_between_customers_and_headers_filtered(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    seen = []
    transport = httpx.MockTransport(lambda r: seen.append(dict(r.headers)) or httpx.Response(200, text="ok"))
    with TestClient(create_app(make(tmp_path, free_credits=50), transport=transport)) as c:
        k1 = signup(c, "a@example.com")
        c.cookies.clear()
        k2 = signup(c, "b@example.com")
        sid = c.post("/v1/sessions", headers={"X-API-Key": k1}).json()["session_id"]
        assert c.get(f"/v1/sessions/{sid}", headers={"X-API-Key": k2}).status_code == 404
        c.post("/scrape", headers={"X-API-Key": k1}, json={"url": "https://example.org/", "headers": {"X-Custom": "1", "Host": "evil", "Proxy-Authorization": "x"}})
        assert seen[-1]["x-custom"] == "1" and seen[-1]["host"] == "example.org" and "proxy-authorization" not in seen[-1]
        bad = c.post("/scrape", headers={"X-API-Key": k1}, json={"url": "https://example.org/", "headers": {"A": "b\r\nInjected: 1"}})
        assert bad.status_code == 422


def test_admin_grant_credits(tmp_path):
    with TestClient(create_app(make(tmp_path))) as c:
        signup(c)
        r = c.post("/v1/admin/credits", headers={"X-API-Key": "admin-secret"}, json={"email": "A@example.com", "credits": 500, "plan": "pro"})
        assert r.status_code == 200 and r.json()["credits_remaining"] == 503 and r.json()["plan"] == "pro"
        assert c.post("/v1/admin/credits", headers={"X-API-Key": "admin-secret"}, json={"email": "no@x.com", "credits": 1}).status_code == 404


def test_password_change_and_static_pages(tmp_path):
    with TestClient(create_app(make(tmp_path))) as c:
        signup(c)
        assert c.post("/v1/account/password", headers=CSRF, json={"current_password": "bad", "new_password": "another-long-pass"}).status_code == 422
        assert c.post("/v1/account/password", headers=CSRF, json={"current_password": "correct-horse-1", "new_password": "another-long-pass"}).status_code == 204
        assert c.get("/app/").status_code == 200
        assert c.get("/docs/").status_code == 200
        r = c.get("/", follow_redirects=False)
        assert r.status_code in (302, 307) and r.headers["location"] == "/app/"
        assert "default-src" in c.get("/app/").headers["content-security-policy"]


def test_proxy_routing_requires_catalog(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    with TestClient(create_app(make(tmp_path), transport=ok_transport())) as c:
        h = {"X-API-Key": signup(c)}
        assert c.post("/scrape", headers=h, json={"url": "https://example.org/", "use_proxy": True}).status_code == 422


def test_expected_text_per_request(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    with TestClient(create_app(make(tmp_path, free_credits=10), transport=ok_transport())) as c:
        h = {"X-API-Key": signup(c)}
        miss = c.post("/scrape", headers=h, json={"url": "https://example.org/", "expected_text": "otra cosa"}).json()
        assert miss["success"] is False and miss["credits_charged"] == 0
        hit = c.post("/scrape", headers=h, json={"url": "https://example.org/", "expected_text": "hola"}).json()
        assert hit["success"] is True and hit["credits_charged"] == 1


def test_admin_proxy_management(tmp_path):
    from cryptography.fernet import Fernet
    admin = {"X-API-Key": "admin-secret"}
    with TestClient(create_app(make(tmp_path, credential_key=Fernet.generate_key().decode()))) as c:
        r = c.post("/v1/proxies/import", headers=admin, json={"provider": "lote", "text": "p1.example:8080:u:p\np2.example:8080:u:p\np1.example:8080:u:p", "country": "es", "kind": "isp"})
        assert r.json() == {"added": 2, "total": 2}
        assert c.post("/v1/proxies/import", headers=admin, json={"provider": "lote", "text": "mal formato"}).status_code == 422
        assert c.post("/v1/proxies/import", headers={"X-API-Key": "x"}, json={"provider": "l", "text": ""}).status_code in (401, 403)
        listed = c.get("/v1/proxies", headers=admin).json()
        assert {p["country"] for p in listed} == {"ES"} and all(p["enabled"] for p in listed)
        pid = listed[0]["id"]
        assert c.patch(f"/v1/proxies/{pid}", headers=admin, json={"enabled": False, "country": "fr"}).status_code == 204
        changed = [p for p in c.get("/v1/proxies", headers=admin).json() if p["id"] == pid][0]
        assert changed["enabled"] is False and changed["country"] == "FR"
        assert c.delete(f"/v1/proxies/{pid}", headers=admin).status_code == 204
        assert c.delete(f"/v1/proxies/{pid}", headers=admin).status_code == 404
        assert c.get("/v1/admin/stats", headers=admin).json()["users"] == 0
        assert c.get("/admin/").status_code == 200


def test_disabled_proxy_not_picked(tmp_path):
    from cryptography.fernet import Fernet
    from proxymanager.proxies import ProxyStore
    store = ProxyStore(str(tmp_path / "p.db"), Fernet.generate_key().decode())
    p = store.create("x", "h.example", 8080, "isp", "ES", None, None)
    assert store.pick("es") == p["id"]
    store.update(p["id"], enabled=False)
    assert store.pick("ES") is None


def seed_proxies(c, n=2, country="ES"):
    text = "\n".join(f"p{i}.example:8080:u:p" for i in range(n))
    assert c.post("/v1/proxies/import", headers={"X-API-Key": "admin-secret"}, json={"provider": "l", "text": text, "country": country}).status_code == 200


def test_proxy_health_selection_failover_and_sticky(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    from cryptography.fernet import Fernet
    from proxymanager.proxies import ProxyStore
    mode = {"fail": False}

    def handler(request):
        if mode["fail"]:
            raise httpx.ConnectError("boom")
        return httpx.Response(200, text="hola")

    app = create_app(make(tmp_path, credential_key=Fernet.generate_key().decode(), free_credits=50), transport=httpx.MockTransport(handler))
    with TestClient(app) as c:
        seed_proxies(c, 2)
        h = {"X-API-Key": signup(c)}
        sid = c.post("/v1/sessions", headers=h).json()["session_id"]
        first = c.post("/scrape", headers=h, json={"url": "https://example.org/", "country": "es", "session_id": sid}).json()
        assert first["success"] and first["proxy_id"]
        for _ in range(4):  # misma IP durante toda la sesión
            assert c.post("/scrape", headers=h, json={"url": "https://example.org/", "country": "ES", "session_id": sid}).json()["proxy_id"] == first["proxy_id"]
        mode["fail"] = True  # ambos proxies fallan: se reintenta con el otro y luego quedan apartados
        failed = c.post("/scrape", headers=h, json={"url": "https://example.org/", "country": "ES"}).json()
        assert failed["success"] is False and failed["credits_charged"] == 0
        mode["fail"] = False
        blocked = c.post("/scrape", headers=h, json={"url": "https://example.org/", "country": "ES"})
        assert blocked.status_code == 422 and "sanos" in blocked.json()["detail"]
        assert c.post("/scrape", headers=h, json={"url": "https://example.org/"}).status_code == 200  # sin proxy sigue funcionando


def test_pick_prefers_proven_and_skips_failed(tmp_path):
    import time
    from cryptography.fernet import Fernet
    from proxymanager.health import ProxyHealth
    from proxymanager.proxies import ProxyStore
    store = ProxyStore(str(tmp_path / "p.db"), Fernet.generate_key().decode())
    health = ProxyHealth(store, make(tmp_path))
    a, b, c3 = (store.create("x", f"h{i}.example", 8080, "isp", "ES", None, None)["id"] for i in range(3))
    health.record(a, True)
    health.record(b, False)
    assert {store.pick("ES") for _ in range(30)} == {a}  # a probado; b apartado; c sin datos queda en reserva
    store.update(a, enabled=False)
    assert store.pick("ES") == c3
    assert store.pick("ES", exclude={c3}) is None
    assert store.pick("ES", ttl=0) in (b, c3)  # con TTL vencido b vuelve a ser elegible


def test_challenge_hook_is_off_by_default(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    transport = httpx.MockTransport(lambda r: httpx.Response(200, text="Please solve this CAPTCHA"))
    with TestClient(create_app(make(tmp_path), transport=transport)) as c:
        h = {"X-API-Key": signup(c)}
        r = c.post("/scrape", headers=h, json={"url": "https://example.org/", "solve_challenges": True}).json()
        assert r["success"] is False and r["credits_charged"] == 0
        assert r["challenge"] == {"detected": True, "handler": None, "handled": False, "resolved": False}


class FakeHandler:
    name = "fake"

    def __init__(self, resolve=True, boom=False):
        self.resolve, self.boom, self.calls = resolve, boom, []

    async def handle(self, context):
        from proxymanager.challenges import ChallengeResolution
        self.calls.append(context)
        if self.boom:
            raise RuntimeError("secreto-interno")
        return ChallengeResolution(self.resolve, html="contenido real", status_code=200)


def test_challenge_handler_plugs_in_and_is_opt_in(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    transport = httpx.MockTransport(lambda r: httpx.Response(403, text="captcha required"))
    fake = FakeHandler()
    with TestClient(create_app(make(tmp_path, credits_challenge_resolved=4, free_credits=50), transport=transport, challenge_handler=fake)) as c:
        h = {"X-API-Key": signup(c)}
        no_opt = c.post("/scrape", headers=h, json={"url": "https://example.org/"}).json()
        assert no_opt["success"] is False and not fake.calls and no_opt["challenge"]["handled"] is False
        r = c.post("/scrape", headers=h, json={"url": "https://example.org/", "solve_challenges": True}).json()
        assert r["success"] is True and r["html"] == "contenido real" and r["credits_charged"] == 5  # 1 base + 4 extra
        assert r["challenge"]["resolved"] is True and len(fake.calls) == 1


def test_challenge_handler_failure_is_contained(tmp_path, monkeypatch):
    public_dns(monkeypatch)
    transport = httpx.MockTransport(lambda r: httpx.Response(403, text="captcha"))
    with TestClient(create_app(make(tmp_path), transport=transport, challenge_handler=FakeHandler(boom=True))) as c:
        h = {"X-API-Key": signup(c)}
        r = c.post("/scrape", headers=h, json={"url": "https://example.org/", "solve_challenges": True})
        assert r.status_code == 200 and r.json()["success"] is False and "secreto-interno" not in r.text
        assert r.json()["challenge"]["error"] == "handler_failed"


def test_load_handler_spec():
    import pytest
    from proxymanager.challenges import NoopHandler, load_handler
    assert load_handler("") is None
    assert load_handler("proxymanager.challenges:NoopHandler").name == NoopHandler.name
    with pytest.raises(ValueError):
        load_handler("sin-formato")
