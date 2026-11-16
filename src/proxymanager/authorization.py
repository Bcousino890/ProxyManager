"""Activación declarada del manejador de desafíos.

El manejador puede estar *configurado* (PROXYMANAGER_CHALLENGE_HANDLER apunta a una clase que
carga) sin estar *activado*. Activarlo exige declarar en /admin/ quién autorizó el uso contra el
destino y una referencia verificable; queda registrado con fecha. Ninguna de las dos cosas
comprueba por software que la autorización sea real: es responsabilidad de quien la declara.
"""
import os
import sqlite3
import time


class AuthorizationError(ValueError):
    pass


class ChallengeAuthorization:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with self._db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS challenge_authorization (
                id INTEGER PRIMARY KEY CHECK (id = 1), enabled INTEGER NOT NULL DEFAULT 0,
                authorized_by TEXT, authorization_reference TEXT, declared_at REAL);
            CREATE TABLE IF NOT EXISTS challenge_authorization_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL,
                authorized_by TEXT, authorization_reference TEXT, at REAL NOT NULL);
            """)
        if db_path != ":memory:":
            os.chmod(db_path, 0o600)

    def _db(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db

    def status(self) -> dict:
        with self._db() as db:
            row = db.execute("SELECT enabled, authorized_by, authorization_reference, declared_at FROM challenge_authorization WHERE id=1").fetchone()
        data = dict(row) if row else {"enabled": 0, "authorized_by": None, "authorization_reference": None, "declared_at": None}
        data["enabled"] = bool(data["enabled"])
        return data

    def enable(self, authorized_by: str, authorization_reference: str) -> dict:
        authorized_by, authorization_reference = authorized_by.strip(), authorization_reference.strip()
        if not (1 <= len(authorized_by) <= 200):
            raise AuthorizationError("Indica quién autorizó (1-200 caracteres)")
        if not (1 <= len(authorization_reference) <= 4000):
            raise AuthorizationError("Indica una referencia verificable de la autorización (1-4000 caracteres)")
        now = time.time()
        with self._db() as db:
            db.execute("DELETE FROM challenge_authorization")
            db.execute("INSERT INTO challenge_authorization (id, enabled, authorized_by, authorization_reference, declared_at) VALUES (1, 1, ?, ?, ?)",
                       (authorized_by, authorization_reference, now))
            db.execute("INSERT INTO challenge_authorization_log (action, authorized_by, authorization_reference, at) VALUES ('enable', ?, ?, ?)",
                       (authorized_by, authorization_reference, now))
        return self.status()

    def disable(self) -> dict:
        now = time.time()
        with self._db() as db:
            db.execute("DELETE FROM challenge_authorization")
            db.execute("INSERT INTO challenge_authorization (id, enabled, declared_at) VALUES (1, 0, ?)", (now,))
            db.execute("INSERT INTO challenge_authorization_log (action, at) VALUES ('disable', ?)", (now,))
        return self.status()

    def log(self, limit: int = 50) -> list[dict]:
        with self._db() as db:
            rows = db.execute("SELECT action, authorized_by, authorization_reference, at FROM challenge_authorization_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
