import json
import os
import secrets
import sqlite3
import time
import uuid

from cryptography.fernet import Fernet


class ProxyStore:
    def __init__(self, db_path: str, credential_key: str = ""):
        self.db_path = db_path
        self.cipher = Fernet(credential_key.encode()) if credential_key else None
        with sqlite3.connect(self.db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS proxies (id TEXT PRIMARY KEY, provider TEXT NOT NULL, host TEXT NOT NULL, port INTEGER NOT NULL, kind TEXT NOT NULL, country TEXT NOT NULL, credentials BLOB)")
            db.execute("CREATE TABLE IF NOT EXISTS session_proxy (session_id TEXT PRIMARY KEY, proxy_id TEXT NOT NULL)")
            if "enabled" not in {r[1] for r in db.execute("PRAGMA table_info(proxies)")}:
                db.execute("ALTER TABLE proxies ADD COLUMN enabled INTEGER NOT NULL DEFAULT 1")
        if self.db_path != ":memory:":
            os.chmod(self.db_path, 0o600)

    def create(self, provider: str, host: str, port: int, kind: str, country: str, username: str | None, password: str | None) -> dict:
        if (username or password) and not self.cipher:
            raise ValueError("Configura PROXYMANAGER_CREDENTIAL_KEY para guardar credenciales")
        credential_blob = self.cipher.encrypt(json.dumps({"username": username, "password": password}).encode()) if (username or password) else None
        proxy_id = "prx_" + uuid.uuid4().hex
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT INTO proxies (id, provider, host, port, kind, country, credentials) VALUES (?, ?, ?, ?, ?, ?, ?)", (proxy_id, provider, host, port, kind, country, credential_blob))
        return {"id": proxy_id, "provider": provider, "host": host, "port": port, "kind": kind, "country": country, "has_credentials": bool(credential_blob), "enabled": True}

    def list(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT id, provider, host, port, kind, country, credentials IS NOT NULL, enabled FROM proxies ORDER BY provider, id").fetchall()
            last = {r[0]: r[1:] for r in db.execute("SELECT proxy_id, created, result FROM proxy_checks WHERE rowid IN (SELECT max(rowid) FROM proxy_checks WHERE state='completed' GROUP BY proxy_id)")} if db.execute("SELECT 1 FROM sqlite_master WHERE name='proxy_checks'").fetchone() else {}
        out = []
        for row in rows:
            item = dict(zip(("id", "provider", "host", "port", "kind", "country", "has_credentials", "enabled"), row))
            item["enabled"] = bool(item["enabled"])
            check = last.get(item["id"])
            if check:
                try:
                    result = json.loads(check[1])
                except ValueError:
                    result = {}
                item["last_check"] = {"at": check[0], "success": bool(result.get("success")), "status_code": result.get("status_code"), "duration_ms": result.get("duration_ms")}
            out.append(item)
        return out

    def update(self, proxy_id: str, kind: str | None = None, country: str | None = None, enabled: bool | None = None) -> bool:
        sets, args = [], []
        for column, value in (("kind", kind), ("country", country.upper() if country else None), ("enabled", None if enabled is None else int(enabled))):
            if value is not None:
                sets.append(f"{column}=?")
                args.append(value)
        if not sets:
            return True
        with sqlite3.connect(self.db_path) as db:
            return db.execute(f"UPDATE proxies SET {', '.join(sets)} WHERE id=?", (*args, proxy_id)).rowcount > 0

    def delete(self, proxy_id: str) -> bool:
        with sqlite3.connect(self.db_path) as db:
            deleted = db.execute("DELETE FROM proxies WHERE id=?", (proxy_id,)).rowcount > 0
            if deleted and db.execute("SELECT 1 FROM sqlite_master WHERE name='proxy_checks'").fetchone():
                db.execute("DELETE FROM proxy_checks WHERE proxy_id=?", (proxy_id,))
        return deleted

    def _candidates(self, country: str | None, exclude, ttl: float, now: float | None = None) -> "list[dict]":
        now = now or time.time()
        out = []
        for proxy in self.list():
            check = proxy.get("last_check")
            if not proxy["enabled"] or proxy["id"] in exclude or (country and proxy["country"].upper() != country.upper()):
                continue
            if check and not check["success"] and now - check["at"] < ttl:
                continue  # falló hace poco: se aparta hasta que caduque ttl o una comprobación vuelva a salir bien
            out.append(proxy)
        return out

    def pick(self, country: str | None = None, exclude=(), ttl: float = 3600) -> str | None:
        """Elige al azar entre proxies activos y sin fallo reciente; prefiere los que ya superaron una comprobación."""
        candidates = self._candidates(country, exclude, ttl)
        proven = [p for p in candidates if p.get("last_check") and p["last_check"]["success"]]
        pool = proven or candidates
        return secrets.choice(pool)["id"] if pool else None

    def choose(self, country: str | None, session_id: str | None, exclude=(), ttl: float = 3600) -> str | None:
        """Como pick, pero mantiene el mismo proxy por sesión mientras siga sano."""
        if session_id:
            with sqlite3.connect(self.db_path) as db:
                row = db.execute("SELECT proxy_id FROM session_proxy WHERE session_id=?", (session_id,)).fetchone()
            if row and any(p["id"] == row[0] for p in self._candidates(country, exclude, ttl)):
                return row[0]
        chosen = self.pick(country, exclude, ttl)
        if chosen and session_id:
            with sqlite3.connect(self.db_path) as db:
                db.execute("INSERT OR REPLACE INTO session_proxy (session_id, proxy_id) VALUES (?, ?)", (session_id, chosen))
        return chosen
