from fastapi.testclient import TestClient

from proxymanager.app import create_app
from test_api import make_settings

E, A = {"X-API-Key": "eval-secret"}, {"X-API-Key": "admin-secret"}


def test_default_evaluator_cannot_write_or_audit(tmp_path):
    with TestClient(create_app(make_settings(tmp_path))) as c:
        assert c.get("/v1/audit", headers=E).status_code == 403
        assert c.post("/v1/proxies/x/checks", json={"url": "https://lab.example/"}, headers=E).status_code == 403
        assert c.get("/v1/proxies", headers=E).status_code == 200
        assert c.get("/v1/audit", headers=A).status_code == 200
        assert c.get("/v1/system").status_code == 401


def test_custom_scopes_restrict_evaluator(tmp_path):
    with TestClient(create_app(make_settings(tmp_path, evaluator_scopes=("sessions",)))) as c:
        assert c.post("/v1/sessions", headers=E).status_code == 201
        assert c.get("/v1/proxies", headers=E).status_code == 403
        assert c.post("/scrape", json={"url": "https://lab.example/"}, headers=E).status_code == 403
        assert c.post("/v1/proxies", json={}, headers=A).status_code != 403


def test_unknown_scope_is_reported(tmp_path):
    assert any("desconocidos" in p for p in make_settings(tmp_path, evaluator_scopes=("typo",)).problems())
