"""Optional, minimal webhook notifications for local state transitions."""
import httpx


class AlertService:
    def __init__(self, webhook_url: str, transport: httpx.AsyncBaseTransport | None = None):
        self.webhook_url = webhook_url
        self.transport = transport

    async def _send(self, payload: dict) -> None:
        if not self.webhook_url:
            return
        try:
            async with httpx.AsyncClient(transport=self.transport, timeout=5, trust_env=False, follow_redirects=False) as client:
                await client.post(self.webhook_url, json=payload)
        except httpx.HTTPError:
            # An unavailable optional webhook must not interrupt checks or expense entry.
            pass

    async def record_proxy(self, metrics, proxy_id: str, source: str, reachable: bool, duration_ms: float | None = None) -> None:
        was_healthy = metrics.stats(proxy_id)["healthy"] if self.webhook_url else False
        metrics.record(proxy_id, source, reachable, duration_ms)
        if was_healthy and not metrics.stats(proxy_id)["healthy"]:
            await self._send({"event": "proxy_unhealthy", "proxy_id": proxy_id})

    async def budget_crossed(self, month: str, before: float, after: float, budget: float) -> None:
        if budget > 0 and before <= budget * 0.8 < after:
            await self._send({"event": "budget_threshold", "month": month, "spent_usd": after, "budget_usd": budget})
