import json
import os
import secrets
import sqlite3
import uuid

from cryptography.fernet import Fernet


class ProxyStore:
    def __init__(self, db_path: str, credential_key: str = ""):
        self.db_path = db_path
        self.cipher = Fernet(credential_key.encode()) if credential_key else None
        with sqlite3.connect(self.db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS proxies (id TEXT PRIMARY KEY, provider TEXT NOT NULL, host TEXT NOT NULL, port INTEGER NOT NULL, kind TEXT NOT NULL, country TEXT NOT NULL, credentials BLOB)")
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

    def pick(self, country: str | None = None) -> str | None:
        """Devuelve el id de un proxy al azar, filtrado por país si se indica."""
        query, args = "SELECT id FROM proxies WHERE enabled=1", ()
        if country:
            query, args = query + " AND upper(country)=?", (country.upper(),)
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute(query, args).fetchall()
        return secrets.choice(rows)[0] if rows else None
