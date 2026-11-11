import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from proxymanager.alerts import AlertService
from proxymanager.app import create_app
from proxymanager.config import Settings
from proxymanager.selection import ProxyMetrics
from test_api import make_settings


def test_unconfigured_webhook_never_sends(tmp_path):
    sent = []
    transport = httpx.MockTransport(lambda request: (sent.append(request), httpx.Response(204))[1])
    alerts = AlertService("", transport)
    metrics = ProxyMetrics(str(tmp_path / "events.db"))

    async def run():
        await alerts.record_proxy(metrics, "p1", "check", True)
        await alerts.record_proxy(metrics, "p1", "check", False)
        await alerts.budget_crossed("2026-11", 19, 21, 25)

    asyncio.run(run())
    assert sent == []


def test_proxy_alert_only_on_healthy_to_unhealthy_transition(tmp_path):
    payloads = []

    def receive(request):
        payloads.append(json.loads(request.content))
        assert str(request.url) == "https://alerts.example/hook"
        return httpx.Response(204)

    alerts = AlertService("https://alerts.example/hook", httpx.MockTransport(receive))
    metrics = ProxyMetrics(str(tmp_path / "events.db"))

    async def run():
        await alerts.record_proxy(metrics, "p1", "check", False)
        await alerts.record_proxy(metrics, "p1", "check", True)
        await alerts.record_proxy(metrics, "p1", "check", False)
        await alerts.record_proxy(metrics, "p1", "check", False)

    asyncio.run(run())
    assert payloads == [{"event": "proxy_unhealthy", "proxy_id": "p1"}]


def test_budget_alert_crosses_eighty_percent_once_and_redacts_concept(tmp_path):
    payloads = []

    def receive(request):
        payloads.append(json.loads(request.content))
        return httpx.Response(204)

    settings = make_settings(tmp_path, monthly_budget_usd=25, alert_webhook_url="https://alerts.example/hook")
    with TestClient(create_app(settings, alert_transport=httpx.MockTransport(receive))) as client:
        headers = {"X-API-Key": "admin-secret"}
        for amount in (20, 0.01, 1):
            response = client.post("/v1/expenses", headers=headers, json={"concept": "https://secret.example/?token=private", "amount_usd": amount})
            assert response.status_code == 201
    assert len(payloads) == 1
    assert payloads[0]["event"] == "budget_threshold"
    assert payloads[0]["spent_usd"] == 20.01
    assert "secret.example" not in str(payloads)
    assert "private" not in str(payloads)


def test_invalid_webhook_url_is_rejected():
    for url in ("http://alerts.example/hook", "https://user:password@alerts.example/hook", "https://alerts.example/hook#fragment"):
        with pytest.raises(ValueError):
            Settings(alert_webhook_url=url)
