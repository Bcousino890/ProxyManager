"""Per-proxy metrics and health-based selection.

Un evento es "alcanzable" cuando el proxy devolvió una respuesta HTTP (cualquier código);
un error de transporte cuenta como fallo del proxy. Que el sitio muestre un desafío o
contenido inesperado NO penaliza al proxy: eso se mide aparte en `/scrape`.
"""
import sqlite3
import threading
import time


class NoHealthyProxy(LookupError):
    pass


class ProxyBusy(LookupError):
    pass


class ProxyMetrics:
    RATE_TOLERANCE = 0.1  # proxies a menos de 10 puntos de la mejor tasa compiten por carga y latencia

    def __init__(self, db_path: str, window_seconds: float = 3600.0, min_success_rate: float = 0.5, max_inflight: int = 5):
        self.db_path, self.window, self.min_rate, self.max_inflight = db_path, window_seconds, min_success_rate, max_inflight
        self._inflight: dict[str, int] = {}
        self._lock = threading.Lock()  # carga en vuelo: solo este proceso
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

    def release(self, proxy_id: str) -> None:
        with self._lock:
            self._inflight[proxy_id] = max(self._inflight.get(proxy_id, 0) - 1, 0)

    def choose(self, country: str | None = None, session_id: str | None = None, acquire: bool = False) -> str:
        """Elige proxy sano. Con acquire=True cuenta una solicitud en vuelo; hay que llamar a release()."""
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT id FROM proxies" + (" WHERE upper(country)=upper(?)" if country else ""), (country,) if country else ()).fetchall()
            bound = db.execute("SELECT proxy_id FROM session_proxy WHERE session_id=?", (session_id,)).fetchone() if session_id else None
        healthy = {}
        for (pid,) in rows:
            s = self.stats(pid)
            if s["healthy"]:
                healthy[pid] = s
        if not healthy:
            raise NoHealthyProxy("No hay proxies sanos; ejecuta comprobaciones primero")
        with self._lock:
            if bound and bound[0] in healthy:  # la sesión conserva su proxy aunque esté ocupado (coherencia de IP/cookies)
                chosen = bound[0]
            else:
                best = max(s["success_rate"] for s in healthy.values())
                pool = [(pid, s) for pid, s in healthy.items() if s["success_rate"] >= best - self.RATE_TOLERANCE
                        and self._inflight.get(pid, 0) < self.max_inflight]
                if not pool:
                    raise ProxyBusy("Todos los proxies sanos están en su límite de concurrencia")
                # menos carga en vuelo, luego menor latencia media (sin datos al final), luego menos usado
                chosen = min(pool, key=lambda x: (self._inflight.get(x[0], 0), x[1]["avg_duration_ms"] if x[1]["avg_duration_ms"] is not None else float("inf"), x[1]["events"], x[0]))[0]
            if acquire:
                self._inflight[chosen] = self._inflight.get(chosen, 0) + 1
        if session_id and not (bound and bound[0] == chosen):
            with sqlite3.connect(self.db_path) as db:
                db.execute("INSERT OR REPLACE INTO session_proxy VALUES (?, ?)", (session_id, chosen))
        return chosen

    def forget_session(self, session_id: str) -> None:
        with sqlite3.connect(self.db_path) as db:
            db.execute("DELETE FROM session_proxy WHERE session_id=?", (session_id,))
