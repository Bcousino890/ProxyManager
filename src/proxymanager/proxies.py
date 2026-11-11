import json
import sqlite3
import uuid

from cryptography.fernet import Fernet


class ProxyStore:
    def __init__(self, db_path: str, credential_key: str = ""):
        self.db_path = db_path
        self.cipher = Fernet(credential_key.encode()) if credential_key else None
        with sqlite3.connect(self.db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS proxies (id TEXT PRIMARY KEY, provider TEXT NOT NULL, host TEXT NOT NULL, port INTEGER NOT NULL, kind TEXT NOT NULL, country TEXT NOT NULL, credentials BLOB)")

    def create(self, provider: str, host: str, port: int, kind: str, country: str, username: str | None, password: str | None) -> dict:
        if (username or password) and not self.cipher:
            raise ValueError("Configura PROXYMANAGER_CREDENTIAL_KEY para guardar credenciales")
        credential_blob = self.cipher.encrypt(json.dumps({"username": username, "password": password}).encode()) if (username or password) else None
        proxy_id = "prx_" + uuid.uuid4().hex
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT INTO proxies VALUES (?, ?, ?, ?, ?, ?, ?)", (proxy_id, provider, host, port, kind, country, credential_blob))
        return {"id": proxy_id, "provider": provider, "host": host, "port": port, "kind": kind, "country": country, "has_credentials": bool(credential_blob)}

    def list(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT id, provider, host, port, kind, country, credentials IS NOT NULL FROM proxies ORDER BY provider, id").fetchall()
        return [dict(zip(("id", "provider", "host", "port", "kind", "country", "has_credentials"), row)) for row in rows]
