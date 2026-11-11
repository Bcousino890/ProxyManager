import hashlib
import os
import secrets
import sqlite3
import time


class SessionStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, owner TEXT NOT NULL, created_at REAL NOT NULL, expires_at REAL NOT NULL)")
        if self.db_path != ":memory:":
            os.chmod(self.db_path, 0o600)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    @staticmethod
    def owner_id(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()

    def create(self, owner: str, ttl_seconds: int) -> dict:
        now = time.time()
        record = {"session_id": "ses_" + secrets.token_urlsafe(24), "created_at": now, "expires_at": now + ttl_seconds}
        with self._connect() as db:
            db.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)", (record["session_id"], owner, now, record["expires_at"]))
        return record

    def get(self, session_id: str, owner: str) -> dict | None:
        with self._connect() as db:
            row = db.execute("SELECT id, created_at, expires_at FROM sessions WHERE id=? AND owner=? AND expires_at>?", (session_id, owner, time.time())).fetchone()
        return {"session_id": row[0], "created_at": row[1], "expires_at": row[2]} if row else None

    def delete(self, session_id: str, owner: str) -> bool:
        with self._connect() as db:
            result = db.execute("DELETE FROM sessions WHERE id=? AND owner=?", (session_id, owner))
            if result.rowcount > 0 and db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='session_cookies'").fetchone():
                db.execute("DELETE FROM session_cookies WHERE session_id=?", (session_id,))
            return result.rowcount > 0
