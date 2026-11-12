"""Claves API adicionales, guardadas solo como hash SHA-256 (las claves son aleatorias de 256 bits).

La clave en claro se muestra una única vez al crearla. Cada clave tiene alcances, caducidad opcional
y puede revocarse. Las claves de entorno (admin/evaluación) siguen funcionando como arranque."""
import hashlib
import json
import secrets
import sqlite3
import time
import uuid

PREFIX = "pm_"
MAX_KEYS = 100
TOUCH_SECONDS = 60  # last_used_at se actualiza como mucho una vez por minuto


def digest(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


class ApiKeyStore:
    def __init__(self, db_path: str, valid_scopes: tuple[str, ...], forbidden_scopes: tuple[str, ...] = ("keys:manage", "destinations:write")):
        self.db_path, self.valid, self.forbidden = db_path, set(valid_scopes) - set(forbidden_scopes), set(forbidden_scopes)
        with sqlite3.connect(db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS api_keys (id TEXT PRIMARY KEY, name TEXT NOT NULL, key_hash TEXT NOT NULL UNIQUE, scopes TEXT NOT NULL, created REAL NOT NULL, expires_at REAL, revoked_at REAL, last_used REAL)")
            if "hint" not in {r[1] for r in db.execute("PRAGMA table_info(api_keys)")}:
                db.execute("ALTER TABLE api_keys ADD COLUMN hint TEXT NOT NULL DEFAULT ''")

    def create(self, name: str, scopes: list[str], expires_days: float | None = None) -> dict:
        name = name.strip()
        if not name or len(name) > 60:
            raise ValueError("Nombre de 1 a 60 caracteres")
        if not scopes or set(scopes) - self.valid:
            raise ValueError("Alcances inválidos; no se permite keys:manage en claves adicionales")
        if expires_days is not None and not 0 < expires_days <= 3650:
            raise ValueError("Caducidad entre 0 y 3650 días")
        with sqlite3.connect(self.db_path) as db:
            if db.execute("SELECT COUNT(*) FROM api_keys WHERE revoked_at IS NULL").fetchone()[0] >= MAX_KEYS:
                raise ValueError("Demasiadas claves activas; revoca alguna")
            key, key_id, now = PREFIX + secrets.token_urlsafe(32), "key_" + uuid.uuid4().hex[:12], time.time()
            expires = now + expires_days * 86400 if expires_days else None
            db.execute("INSERT INTO api_keys (id, name, key_hash, scopes, created, expires_at, hint) VALUES (?, ?, ?, ?, ?, ?, ?)", (key_id, name, digest(key), json.dumps(sorted(set(scopes))), now, expires, key[-4:]))
        return {"id": key_id, "name": name, "key": key, "scopes": sorted(set(scopes)), "expires_at": expires}

    def lookup(self, api_key: str) -> frozenset[str] | None:
        """Alcances de una clave válida (no revocada, no caducada); None si no es válida."""
        if not api_key.startswith(PREFIX):
            return None
        now = time.time()
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT id, scopes, expires_at, revoked_at, last_used FROM api_keys WHERE key_hash=?", (digest(api_key),)).fetchone()
            if row is None or row[3] is not None or (row[2] is not None and row[2] <= now):
                return None
            if row[4] is None or now - row[4] >= TOUCH_SECONDS:
                db.execute("UPDATE api_keys SET last_used=? WHERE id=?", (now, row[0]))
        return frozenset(json.loads(row[1])) & self.valid

    def list(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT id, name, scopes, created, expires_at, revoked_at, last_used, hint FROM api_keys ORDER BY created DESC").fetchall()
        now = time.time()
        return [{"id": r[0], "name": r[1], "scopes": json.loads(r[2]), "created_at": r[3], "expires_at": r[4], "revoked_at": r[5], "last_used_at": r[6], "hint": ("pm_…" + r[7]) if r[7] else "pm_…",
                 "state": "revoked" if r[5] else ("expired" if r[4] and r[4] <= now else "active")} for r in rows]

    def revoke(self, key_id: str) -> bool:
        with sqlite3.connect(self.db_path) as db:
            return db.execute("UPDATE api_keys SET revoked_at=? WHERE id=? AND revoked_at IS NULL", (time.time(), key_id)).rowcount > 0
