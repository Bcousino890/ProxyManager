"""Per-proxy metrics and health-based selection.

Un evento es "alcanzable" cuando el proxy devolvió una respuesta HTTP (cualquier código);
un error de transporte cuenta como fallo del proxy. Que el sitio muestre un desafío o
contenido inesperado NO penaliza al proxy: eso se mide aparte en `/scrape`.
"""
import sqlite3
import time


class NoHealthyProxy(LookupError):
    pass


class ProxyMetrics:
    def __init__(self, db_path: str, window_seconds: float = 3600.0, min_success_rate: float = 0.5):
        self.db_path, self.window, self.min_rate = db_path, window_seconds, min_success_rate
        with sqlite3.connect(db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS proxy_events (id INTEGER PRIMARY KEY AUTOINCREMENT, proxy_id TEXT NOT NULL, at REAL NOT NULL, source TEXT NOT NULL, reachable INTEGER NOT NULL, duration_ms REAL)")
            db.execute("CREATE INDEX IF NOT EXISTS proxy_events_by_proxy ON proxy_events (proxy_id, at)")
            db.execute("CREATE TABLE IF NOT EXISTS session_proxy (session_id TEXT PRIMARY KEY, proxy_id TEXT NOT NULL)")

    def record(self, proxy_id: str, source: str, reachable: bool, duration_ms: float | None = None) -> None:
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT INTO proxy_events (proxy_id, at, source, reachable, duration_ms) VALUES (?, ?, ?, ?, ?)", (proxy_id, time.time(), source, int(reachable), duration_ms))

    def stats(self, proxy_id: str) -> dict:
        with sqlite3.connect(self.db_path) as db:
            n, ok, avg, last = db.execute("SELECT COUNT(*), COALESCE(SUM(reachable), 0), AVG(CASE WHEN reachable=1 THEN duration_ms END), MAX(CASE WHEN reachable=1 THEN at END) FROM proxy_events WHERE proxy_id=? AND at>=?", (proxy_id, time.time() - self.window)).fetchone()
        rate = ok / n if n else None
        return {"proxy_id": proxy_id, "window_seconds": self.window, "events": n, "reachable": ok, "success_rate": rate,
                "avg_duration_ms": None if avg is None else round(avg, 2), "last_success_at": last,
                "healthy": bool(n and rate >= self.min_rate and last is not None)}

    def choose(self, country: str | None = None, session_id: str | None = None) -> str:
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT id FROM proxies" + (" WHERE upper(country)=upper(?)" if country else ""), (country,) if country else ()).fetchall()
            bound = db.execute("SELECT proxy_id FROM session_proxy WHERE session_id=?", (session_id,)).fetchone() if session_id else None
        ranked = []
        for (pid,) in rows:
            s = self.stats(pid)
            if s["healthy"]:
                ranked.append((-s["success_rate"], s["events"], pid))
        if not ranked:
            raise NoHealthyProxy("No hay proxies sanos; ejecuta comprobaciones primero")
        healthy = {pid for _, _, pid in ranked}
        if bound and bound[0] in healthy:
            return bound[0]
        ranked.sort()  # mejor tasa; a igualdad, el menos usado
        chosen = ranked[0][2]
        if session_id:
            with sqlite3.connect(self.db_path) as db:
                db.execute("INSERT OR REPLACE INTO session_proxy VALUES (?, ?)", (session_id, chosen))
        return chosen

    def forget_session(self, session_id: str) -> None:
        with sqlite3.connect(self.db_path) as db:
            db.execute("DELETE FROM session_proxy WHERE session_id=?", (session_id,))
