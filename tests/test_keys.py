import sqlite3
import time

from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.config import SCOPES
from proxymanager.keys import ApiKeyStore
from test_api import make_settings

A, E = {"X-API-Key": "admin-secret"}, {"X-API-Key": "eval-secret"}


def new_key(c, **body):
    return c.post("/v1/keys", headers=A, json={"name": "n", "scopes": ["sessions"], **body})


def test_key_lifecycle_scopes_and_one_time_secret(tmp_path):
    settings = make_settings(tmp_path)
    with TestClient(create_app(settings)) as c:
        created = new_key(c, scopes=["sessions", "proxies:read"]).json()
        key, h = created["key"], {"X-API-Key": created["key"]}
        assert key.startswith("pm_") and len(key) > 40
        assert c.post("/v1/sessions", headers=h).status_code == 201
        assert c.get("/v1/proxies", headers=h).status_code == 200
        assert c.post("/scrape", headers=h, json={"url": "https://lab.example/"}).status_code == 403   # sin alcance scrape
        listed = c.get("/v1/keys", headers=A).json()
        assert listed[0]["state"] == "active" and "key" not in listed[0] and key not in str(listed)    # el secreto no se vuelve a mostrar
        assert c.delete(f"/v1/keys/{created['id']}", headers=A).status_code == 204
        assert c.post("/v1/sessions", headers=h).status_code == 401                                     # revocada
        assert c.delete(f"/v1/keys/{created['id']}", headers=A).status_code == 404
    stored = sqlite3.connect(settings.db_path).execute("SELECT key_hash FROM api_keys").fetchone()[0]
    assert key not in stored and len(stored) == 64                                                       # solo hash en la base


def test_only_env_admin_manages_keys_and_no_privilege_escalation(tmp_path):
    with TestClient(create_app(make_settings(tmp_path))) as c:
        assert c.get("/v1/keys", headers=E).status_code == 403
        assert new_key(c, scopes=["keys:manage"]).status_code == 422                 # una clave adicional no puede gestionar claves
        assert new_key(c, scopes=["nope"]).status_code == 422
        assert new_key(c, scopes=[]).status_code == 422
        assert new_key(c, name="").status_code == 422
        assert new_key(c, expires_days=-1).status_code == 422
        extra = new_key(c, scopes=sorted(set(SCOPES) - {"keys:manage"})).json()
        assert c.get("/v1/keys", headers={"X-API-Key": extra["key"]}).status_code == 403   # ni con todos los demás alcances


def test_expiry_and_unknown_keys(tmp_path):
    settings = make_settings(tmp_path)
    with TestClient(create_app(settings)) as c:
        created = new_key(c, expires_days=1).json()
        h = {"X-API-Key": created["key"]}
        assert c.post("/v1/sessions", headers=h).status_code == 201
        with sqlite3.connect(settings.db_path) as db:
            db.execute("UPDATE api_keys SET expires_at=? WHERE id=?", (time.time() - 1, created["id"]))
        assert c.post("/v1/sessions", headers=h).status_code == 401
        assert c.get("/v1/keys", headers=A).json()[0]["state"] == "expired"
        assert c.get("/v1/system", headers={"X-API-Key": "pm_" + "x" * 43}).status_code == 401


def test_each_key_has_isolated_sessions_and_store_limits(tmp_path):
    with TestClient(create_app(make_settings(tmp_path))) as c:
        k1, k2 = (new_key(c, name=n).json()["key"] for n in ("a", "b"))
        sid = c.post("/v1/sessions", headers={"X-API-Key": k1}).json()["session_id"]
        assert c.get(f"/v1/sessions/{sid}", headers={"X-API-Key": k1}).status_code == 200
        assert c.get(f"/v1/sessions/{sid}", headers={"X-API-Key": k2}).status_code == 404
    store = ApiKeyStore(str(tmp_path / "limit.db"), SCOPES)
    import proxymanager.keys as keys
    keys.MAX_KEYS = 2
    store.create("a", ["sessions"]); store.create("b", ["sessions"])
    try:
        store.create("c", ["sessions"])
        assert False, "debería rechazar la tercera"
    except ValueError:
        pass
    finally:
        keys.MAX_KEYS = 100
