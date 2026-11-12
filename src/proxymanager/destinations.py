"""Destinos autorizados gestionados desde el panel, además de los del entorno.

Añadir un destino amplía a qué sitios puede llegar el servidor, así que:
- solo hostnames públicos (sin IP, sin puerto, sin comodines, sin nombres de una sola etiqueta);
- cada alta exige una referencia de la autorización del titular del sitio y queda registrada (quién y cuándo);
- los destinos del entorno no se pueden quitar desde el panel;
- las comprobaciones de IP pública y HTTPS de `guard_url` siguen aplicándose siempre."""
import ipaddress
import re
import sqlite3
import threading
import time

_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")
MAX_NOTE = 200
CACHE_SECONDS = 5.0


def normalize_host(raw: str) -> str:
    host = raw.strip().lower().rstrip(".")
    if not host or len(host) > 253:
        raise ValueError("Host vacío o demasiado largo")
    try:
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        pass
    else:
        raise ValueError("Usa un nombre de host, no una dirección IP")
    labels = host.split(".")
    if len(labels) < 2 or not all(_LABEL.fullmatch(label) for label in labels):
        raise ValueError("Host inválido: usa solo un nombre de dominio completo (sin esquema, puerto, ruta ni comodines)")
    if host.endswith((".local", ".internal", ".localhost", ".lan", ".home.arpa")) or host == "localhost":
        raise ValueError("No se permiten nombres de red interna")
    return host


class DestinationStore:
    def __init__(self, db_path: str, env_hosts: tuple[str, ...] = ()):
        self.db_path, self.env_hosts = db_path, frozenset(h.lower().rstrip(".") for h in env_hosts)
        self._lock, self._cache, self._cached_at = threading.Lock(), frozenset(), 0.0
        with sqlite3.connect(db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS allowed_destinations (host TEXT PRIMARY KEY, note TEXT NOT NULL, added_by TEXT, added_at REAL NOT NULL)")

    def hosts(self) -> frozenset[str]:
        """Entorno + panel. Se relee cada pocos segundos para que otros procesos vean los cambios."""
        with self._lock:
            if time.monotonic() - self._cached_at > CACHE_SECONDS:
                with sqlite3.connect(self.db_path) as db:
                    self._cache = frozenset(r[0] for r in db.execute("SELECT host FROM allowed_destinations"))
                self._cached_at = time.monotonic()
            return self.env_hosts | self._cache

    def _invalidate(self) -> None:
        with self._lock:
            self._cached_at = 0.0

    def add(self, host: str, note: str, added_by: str | None) -> dict:
        host, note = normalize_host(host), note.strip()
        if not 5 <= len(note) <= MAX_NOTE:
            raise ValueError("Indica la referencia de la autorización del titular del sitio (5 a 200 caracteres)")
        if host in self.env_hosts:
            raise ValueError("Ese destino ya está autorizado desde la configuración del servidor")
        with sqlite3.connect(self.db_path) as db:
            if db.execute("SELECT 1 FROM allowed_destinations WHERE host=?", (host,)).fetchone():
                raise ValueError("Ese destino ya está autorizado")
            now = time.time()
            db.execute("INSERT INTO allowed_destinations VALUES (?, ?, ?, ?)", (host, note, added_by, now))
        self._invalidate()
        return {"host": host, "source": "panel", "note": note, "added_at": now}

    def remove(self, host: str) -> bool:
        with sqlite3.connect(self.db_path) as db:
            removed = db.execute("DELETE FROM allowed_destinations WHERE host=?", (host.strip().lower().rstrip("."),)).rowcount > 0
        self._invalidate()
        return removed

    def list(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT host, note, added_at FROM allowed_destinations ORDER BY host").fetchall()
        items = [{"host": h, "source": "entorno", "note": "Configurado en el servidor (no editable desde el panel)", "added_at": None} for h in sorted(self.env_hosts)]
        return items + [{"host": h, "source": "panel", "note": n, "added_at": t} for h, n, t in rows]
