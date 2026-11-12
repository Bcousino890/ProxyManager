"""Encrypted, per-session HTTP cookie storage for authorized destinations."""

from datetime import timezone
from email.utils import parsedate_to_datetime
from http.cookies import CookieError, SimpleCookie
import re
import sqlite3
import time
from urllib.parse import urlsplit

from cryptography.fernet import Fernet

from .storage import SessionStore

MAX_COOKIE_BYTES = 4096
MAX_COOKIES_PER_SESSION = 50
_COOKIE_NAME = re.compile(r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")


class CookieStore:
    def __init__(self, db_path: str, key: str, sessions: SessionStore, allowed_hosts):  # tupla fija o función que devuelve los destinos vigentes
        self.db_path = db_path
        self.key = key
        self.cipher = Fernet(key.encode()) if key else None
        self.sessions = sessions
        self._allowed = allowed_hosts if callable(allowed_hosts) else (lambda: allowed_hosts)
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS session_cookies (
                session_id TEXT NOT NULL, name TEXT NOT NULL, domain TEXT NOT NULL,
                path TEXT NOT NULL, host_only INTEGER NOT NULL, secure INTEGER NOT NULL,
                http_only INTEGER NOT NULL, same_site TEXT NOT NULL, expires_at REAL NOT NULL,
                encrypted_value BLOB NOT NULL,
                PRIMARY KEY (session_id, name, domain, path)
            )""")

    def record(self, session_id: str, owner: str, url: str, headers: list[str]) -> None:
        session = self.sessions.get(session_id, owner)
        if session is None:
            raise ValueError("Sesión no encontrada")
        if headers and self.cipher is None:
            raise ValueError("Configura PROXYMANAGER_CREDENTIAL_KEY para guardar cookies")
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme != "https" or host not in self._allowed():
            raise ValueError("Destino de cookie no autorizado")
        default_path = parsed.path.rsplit("/", 1)[0] or "/"
        now = time.time()
        with sqlite3.connect(self.db_path) as db:
            for header in headers:
                jar = SimpleCookie()
                try:
                    jar.load(header)
                except CookieError:
                    continue
                for name, morsel in jar.items():
                    value = morsel.value
                    if len(name) + len(value) > MAX_COOKIE_BYTES:
                        continue
                    if not _COOKIE_NAME.fullmatch(name) or any(ord(c) < 32 or ord(c) == 127 or c == ";" for c in value):
                        continue
                    raw_domain = morsel["domain"].lower().lstrip(".").rstrip(".")
                    domain = raw_domain or host
                    if domain not in self._allowed() or (host != domain and not host.endswith("." + domain)):
                        continue
                    path = morsel["path"] if morsel["path"].startswith("/") else default_path
                    try:
                        if morsel["max-age"]:
                            expires_at = now + int(morsel["max-age"])
                        elif morsel["expires"]:
                            expiry = parsedate_to_datetime(morsel["expires"])
                            expires_at = expiry.replace(tzinfo=timezone.utc).timestamp() if expiry.tzinfo is None else expiry.timestamp()
                        else:
                            expires_at = session["expires_at"]
                    except (ValueError, OverflowError, TypeError):
                        continue
                    db.execute("DELETE FROM session_cookies WHERE session_id=? AND name=? AND domain=? AND path=?", (session_id, name, domain, path))
                    if expires_at <= now:
                        continue
                    if db.execute("SELECT COUNT(*) FROM session_cookies WHERE session_id=?", (session_id,)).fetchone()[0] >= MAX_COOKIES_PER_SESSION:
                        continue
                    db.execute("""INSERT INTO session_cookies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                        session_id, name, domain, path, int(not raw_domain), int(bool(morsel["secure"])),
                        int(bool(morsel["httponly"])), morsel["samesite"], min(expires_at, session["expires_at"]),
                        self.cipher.encrypt(value.encode()),
                    ))

    def header(self, session_id: str, owner: str, url: str) -> str:
        if self.sessions.get(session_id, owner) is None:
            return ""
        if self.cipher is None:
            raise ValueError("Configura PROXYMANAGER_CREDENTIAL_KEY para usar cookies")
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        if host not in self._allowed():
            return ""
        request_path = parsed.path or "/"
        now = time.time()
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("""SELECT name, domain, path, host_only, secure, encrypted_value
                FROM session_cookies WHERE session_id=? AND expires_at>? ORDER BY length(path) DESC, rowid""", (session_id, now)).fetchall()
        pairs = []
        for name, domain, path, host_only, secure, encrypted_value in rows:
            if (host_only and host != domain) or (not host_only and host != domain and not host.endswith("." + domain)):
                continue
            if secure and parsed.scheme != "https":
                continue
            if not (request_path == path or (request_path.startswith(path) and (path.endswith("/") or request_path[len(path):].startswith("/")))):
                continue
            pairs.append(f"{name}={self.cipher.decrypt(encrypted_value).decode()}")
        return "; ".join(pairs)
