import sqlite3
import time

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.config import Settings
from proxymanager.limits import AuditLog
from test_api import make_settings


def good(tmp_path, **kw):
    values = dict(evaluator_key="e" * 20, admin_key="a" * 20, credential_key=Fernet.generate_key().decode())
    values.update(kw)
    return make_settings(tmp_path, **values)


def test_problems_detects_each_issue(tmp_path):
    assert good(tmp_path).problems() == []
    assert len(Settings().problems()) >= 4
    assert any("distintas" in p for p in good(tmp_path, admin_key="e" * 20).problems())
    assert any("Fernet" in p for p in good(tmp_path, credential_key="nope").problems())


def test_strict_refuses_to_start_when_insecure(tmp_path):
    with pytest.raises(RuntimeError, match="Configuración insegura"):
        with TestClient(create_app(make_settings(tmp_path, strict=True))):
            pass
    with TestClient(create_app(good(tmp_path, strict=True))) as client:
        assert client.get("/health").status_code == 200


def test_audit_purge_removes_only_old_events(tmp_path):
    log = AuditLog(str(tmp_path / "a.db"))
    log.record("o", "GET", "/x", 200)
    with sqlite3.connect(str(tmp_path / "a.db")) as db:
        db.execute("UPDATE audit_events SET at = ?", (time.time() - 40 * 86400,))
    log.record("o", "GET", "/y", 200)
    assert log.purge(30) == 1
    assert [e["route"] for e in log.recent()] == ["/y"]
