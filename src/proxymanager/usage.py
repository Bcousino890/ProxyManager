"""Uso de /scrape y benchmarks por día y dominio.

Solo se guarda el HOST del destino (nunca ruta, query ni cuerpo). Separa dos cosas distintas:
- transporte: el proxy devolvió respuesta HTTP (`status_code` no nulo);
- entrega: el sitio devolvió el contenido esperado, un desafío o un bloqueo."""
import sqlite3
import time
from datetime import datetime, timezone

OUTCOMES = ("success", "challenge", "blocked", "unexpected_response", "transport_error")
MAX_DAYS = 90


def classify(result: dict) -> str:
    if result.get("success"):
        return "success"
    status = result.get("status_code")
    if status is None:
        return "transport_error"
    if result.get("validation", {}).get("challenge_detected"):
        return "challenge"
    if status in (401, 403, 429):
        return "blocked"
    return "unexpected_response"


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[min(len(ordered) - 1, int(p * len(ordered)))], 2)


class UsageStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS usage_events (id INTEGER PRIMARY KEY AUTOINCREMENT, at REAL NOT NULL, host TEXT NOT NULL, source TEXT NOT NULL, proxy_id TEXT, outcome TEXT NOT NULL, status_code INTEGER, duration_ms REAL, bytes INTEGER NOT NULL DEFAULT 0)")
            db.execute("CREATE INDEX IF NOT EXISTS usage_events_at ON usage_events (at)")

    def record(self, host: str, source: str, proxy_id: str | None, result: dict) -> None:
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT INTO usage_events (at, host, source, proxy_id, outcome, status_code, duration_ms, bytes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (time.time(), host.lower(), source, proxy_id, classify(result), result.get("status_code"), result.get("duration_ms"), max(int(result.get("bytes_transferred") or 0), 0)))

    def purge(self, keep_days: float = MAX_DAYS) -> int:
        with sqlite3.connect(self.db_path) as db:
            return db.execute("DELETE FROM usage_events WHERE at < ?", (time.time() - keep_days * 86400,)).rowcount

    @staticmethod
    def _day(ts: float) -> str:
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")

    def summary(self, days: int = 14, now: float | None = None) -> dict:
        days = max(1, min(int(days), MAX_DAYS))
        now = now or time.time()
        first = datetime.fromtimestamp(now, timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() - (days - 1) * 86400
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT at, host, outcome, duration_ms, bytes FROM usage_events WHERE at>=?", (first,)).fetchall()
        labels = [self._day(first + i * 86400) for i in range(days)]
        daily = {d: {"date": d, "requests": 0, "outcomes": dict.fromkeys(OUTCOMES, 0), "bytes": 0, "_ms": []} for d in labels}
        domains: dict[str, dict] = {}
        all_ms: list[float] = []
        outcomes = dict.fromkeys(OUTCOMES, 0)
        for at, host, outcome, ms, size in rows:
            day = daily.get(self._day(at))
            if day is None:
                continue
            day["requests"] += 1; day["outcomes"][outcome] = day["outcomes"].get(outcome, 0) + 1; day["bytes"] += size
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            dom = domains.setdefault(host, {"host": host, "requests": 0, "success": 0, "bytes": 0})
            dom["requests"] += 1; dom["success"] += outcome == "success"; dom["bytes"] += size
            if ms is not None:
                day["_ms"].append(ms); all_ms.append(ms)
        series = []
        for d in labels:
            item = daily[d]; ms = item.pop("_ms")
            item["success"] = item["outcomes"]["success"]
            item["avg_ms"] = round(sum(ms) / len(ms), 2) if ms else None
            item["p95_ms"] = percentile(ms, 0.95)
            series.append(item)
        total = sum(i["requests"] for i in series)
        top = sorted(domains.values(), key=lambda x: -x["requests"])[:20]
        for dom in top:
            dom["success_rate"] = round(dom["success"] / dom["requests"], 4)
        return {"days": days, "daily": series, "domains": top, "outcomes": outcomes,
                "totals": {"requests": total, "success_rate": round(outcomes["success"] / total, 4) if total else None,
                           "avg_ms": round(sum(all_ms) / len(all_ms), 2) if all_ms else None, "p95_ms": percentile(all_ms, 0.95),
                           "bytes": sum(i["bytes"] for i in series)},
                "today": {k: series[-1][k] for k in ("date", "requests", "success", "avg_ms", "p95_ms")}}

    def delivery_by_proxy(self, window_seconds: float = 86400.0) -> dict[str, dict]:
        """Por proxy, en la ventana: solicitudes y cuántas fueron entregadas, bloqueadas/desafiadas o fallaron en transporte."""
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT proxy_id, outcome, COUNT(*) FROM usage_events WHERE proxy_id IS NOT NULL AND at>=? GROUP BY proxy_id, outcome", (time.time() - window_seconds,)).fetchall()
        out: dict[str, dict] = {}
        for pid, outcome, n in rows:
            item = out.setdefault(pid, {"requests": 0, "success": 0, "blocked": 0, "transport_error": 0, "other": 0})
            item["requests"] += n
            key = "success" if outcome == "success" else ("blocked" if outcome in ("challenge", "blocked") else ("transport_error" if outcome == "transport_error" else "other"))
            item[key] += n
        return out
