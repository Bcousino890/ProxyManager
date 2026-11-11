from datetime import datetime, timezone

from fastapi.testclient import TestClient

from proxymanager.app import create_app
from proxymanager.expenses import ExpenseStore
from test_api import make_settings

A, E = {"X-API-Key": "admin-secret"}, {"X-API-Key": "eval-secret"}


def test_month_total_budget_and_previous_month_excluded(tmp_path):
    import sqlite3
    store = ExpenseStore(str(tmp_path / "e.db"))
    old = store.add("servidor viejo", 9.99)
    with sqlite3.connect(str(tmp_path / "e.db")) as db:
        db.execute("UPDATE expenses SET at=? WHERE id=?", (datetime(2020, 1, 15, tzinfo=timezone.utc).timestamp(), old["id"]))
    store.add("proxies", 7.5); store.add("spot", 3.25)
    m = store.month(10.0)
    assert m["spent_usd"] == 10.75 and m["remaining_usd"] == -0.75 and m["over_budget"] is True and len(m["entries"]) == 2


def test_validation_and_scopes(tmp_path):
    with TestClient(create_app(make_settings(tmp_path, monthly_budget_usd=25))) as c:
        assert c.post("/v1/expenses", headers=E, json={"concept": "x", "amount_usd": 1}).status_code == 403
        assert c.get("/v1/expenses", headers=E).status_code == 403
        for bad in ({"concept": "", "amount_usd": 1}, {"concept": "x", "amount_usd": 0}, {"concept": "x", "amount_usd": -5}, {"concept": "y" * 81, "amount_usd": 1}, {"concept": "x", "amount_usd": 1e9}):
            assert c.post("/v1/expenses", headers=A, json=bad).status_code == 422
        assert c.post("/v1/expenses", headers=A, json={"concept": "t3.medium spot", "amount_usd": 3.39}).status_code == 201
        data = c.get("/v1/expenses", headers=A).json()
        assert data["spent_usd"] == 3.39 and data["remaining_usd"] == 21.61 and data["entries"][0]["concept"] == "t3.medium spot"
