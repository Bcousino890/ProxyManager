from collections import defaultdict, deque
import sqlite3
import threading
import time


class RateLimiter:
    """Ventana deslizante en memoria por propietario. Válido para un solo proceso API."""

    def __init__(self, limit: int, window_seconds: float, clock=time.monotonic):
        self.limit, self.window, self.clock = limit, window_seconds, clock
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, owner: str) -> float:
        """Devuelve 0 si se permite; si no, segundos hasta poder reintentar."""
        if self.limit <= 0:
            return 0.0
        now = self.clock()
        with self._lock:
            hits = self._hits[owner]
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return max(self.window - (now - hits[0]), 0.001)
            hits.append(now)
            return 0.0


class AuditLog:
    """Eventos sin clave API, query, cuerpo ni URL: solo propietario (hash), método, ruta genérica y estado."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS audit_events (id INTEGER PRIMARY KEY AUTOINCREMENT, at REAL NOT NULL, owner TEXT, method TEXT NOT NULL, route TEXT NOT NULL, status INTEGER NOT NULL)")

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def record(self, owner: str | None, method: str, route: str, status: int) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO audit_events (at, owner, method, route, status) VALUES (?, ?, ?, ?, ?)", (time.time(), owner, method, route, status))

    def recent(self, limit: int = 100) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT at, owner, method, route, status FROM audit_events ORDER BY id DESC LIMIT ?", (min(limit, 500),)).fetchall()
        return [dict(zip(("at", "owner", "method", "route", "status"), r)) for r in rows]
