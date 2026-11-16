"""Cuentas de clientes, claves API, créditos y registro de uso (SQLite)."""
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
import uuid
from collections import defaultdict, deque

_EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,}$")
KEY_PREFIX = "pm_live_"
MAX_KEYS = 10


class AccountError(ValueError):
    pass


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, digest = stored.split("$")
        candidate = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1, dklen=32)
        return hmac.compare_digest(candidate.hex(), digest)
    except ValueError:
        return False


_DUMMY = hash_password("dummy-password-for-timing")


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class SlidingWindow:
    """Límite en memoria; válido con un solo proceso API."""

    def __init__(self, limit: int, window: float = 60.0):
        self.limit, self.window = limit, window
        self.hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        queue = self.hits[key]
        while queue and now - queue[0] > self.window:
            queue.popleft()
        if len(queue) >= self.limit:
            return False
        queue.append(now)
        return True


class Accounts:
    def __init__(self, db_path: str, free_credits: int = 100, web_session_seconds: int = 7 * 86400):
        self.db_path, self.free_credits, self.web_ttl = db_path, free_credits, web_session_seconds
        with self._db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
                created_at REAL NOT NULL, credits_total INTEGER NOT NULL, credits_used INTEGER NOT NULL DEFAULT 0, plan TEXT NOT NULL DEFAULT 'free');
            CREATE TABLE IF NOT EXISTS web_sessions (token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, created_at REAL NOT NULL, expires_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS api_keys (id TEXT PRIMARY KEY, user_id TEXT NOT NULL, name TEXT NOT NULL, key_hash TEXT NOT NULL UNIQUE,
                prefix TEXT NOT NULL, last4 TEXT NOT NULL, created_at REAL NOT NULL, revoked_at REAL, credit_limit INTEGER,
                credits_used INTEGER NOT NULL DEFAULT 0, last_used_at REAL);
            CREATE TABLE IF NOT EXISTS usage (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, key_id TEXT, ts REAL NOT NULL,
                host TEXT, status_code INTEGER, success INTEGER NOT NULL, credits INTEGER NOT NULL, bytes INTEGER NOT NULL DEFAULT 0,
                duration_ms REAL, proxied INTEGER NOT NULL DEFAULT 0);
            CREATE INDEX IF NOT EXISTS usage_user_ts ON usage (user_id, ts);
            """)
        if db_path != ":memory:":
            os.chmod(db_path, 0o600)

    def _db(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db

    # --- usuarios -------------------------------------------------
    def signup(self, email: str, password: str) -> tuple[dict, str]:
        email = email.strip().lower()
        if not _EMAIL.match(email):
            raise AccountError("Correo electrónico inválido")
        if len(password) < 10 or len(password) > 200:
            raise AccountError("La contraseña debe tener entre 10 y 200 caracteres")
        user_id = "usr_" + uuid.uuid4().hex
        try:
            with self._db() as db:
                db.execute("INSERT INTO users (id, email, password_hash, created_at, credits_total) VALUES (?,?,?,?,?)",
                           (user_id, email, hash_password(password), time.time(), self.free_credits))
        except sqlite3.IntegrityError as exc:
            raise AccountError("Ese correo ya está registrado") from exc
        key = self.create_key(user_id, "Por defecto")
        return self.user(user_id), key["key"]

    def user(self, user_id: str) -> dict | None:
        with self._db() as db:
            row = db.execute("SELECT id, email, created_at, credits_total, credits_used, plan FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        data["credits_remaining"] = max(0, data["credits_total"] - data["credits_used"])
        return data

    def login(self, email: str, password: str) -> str | None:
        with self._db() as db:
            row = db.execute("SELECT id, password_hash FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
        ok = verify_password(password, row["password_hash"] if row else _DUMMY)
        if not (row and ok):
            return None
        token = secrets.token_urlsafe(32)
        now = time.time()
        with self._db() as db:
            db.execute("DELETE FROM web_sessions WHERE expires_at<?", (now,))
            db.execute("INSERT INTO web_sessions VALUES (?,?,?,?)", (_sha(token), row["id"], now, now + self.web_ttl))
        return token

    def user_for_token(self, token: str) -> dict | None:
        with self._db() as db:
            row = db.execute("SELECT user_id FROM web_sessions WHERE token_hash=? AND expires_at>?", (_sha(token), time.time())).fetchone()
        return self.user(row["user_id"]) if row else None

    def logout(self, token: str) -> None:
        with self._db() as db:
            db.execute("DELETE FROM web_sessions WHERE token_hash=?", (_sha(token),))

    def change_password(self, user_id: str, current: str, new: str, keep_token: str | None = None) -> None:
        if len(new) < 10 or len(new) > 200:
            raise AccountError("La contraseña debe tener entre 10 y 200 caracteres")
        with self._db() as db:
            row = db.execute("SELECT password_hash FROM users WHERE id=?", (user_id,)).fetchone()
            if not row or not verify_password(current, row["password_hash"]):
                raise AccountError("Contraseña actual incorrecta")
            db.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new), user_id))
            db.execute("DELETE FROM web_sessions WHERE user_id=? AND token_hash<>?", (user_id, _sha(keep_token or "")))

    # --- claves ---------------------------------------------------
    def create_key(self, user_id: str, name: str, credit_limit: int | None = None) -> dict:
        name = name.strip()
        if not 1 <= len(name) <= 60:
            raise AccountError("El nombre debe tener entre 1 y 60 caracteres")
        if credit_limit is not None and credit_limit <= 0:
            raise AccountError("El límite de créditos debe ser positivo")
        with self._db() as db:
            if db.execute("SELECT count(*) FROM api_keys WHERE user_id=? AND revoked_at IS NULL", (user_id,)).fetchone()[0] >= MAX_KEYS:
                raise AccountError(f"Máximo {MAX_KEYS} claves activas")
            plain = KEY_PREFIX + secrets.token_urlsafe(32)
            key_id = "key_" + uuid.uuid4().hex[:16]
            db.execute("INSERT INTO api_keys (id, user_id, name, key_hash, prefix, last4, created_at, credit_limit) VALUES (?,?,?,?,?,?,?,?)",
                       (key_id, user_id, name, _sha(plain), plain[:11], plain[-4:], time.time(), credit_limit))
        return {"id": key_id, "name": name, "key": plain, "credit_limit": credit_limit}

    def list_keys(self, user_id: str) -> list[dict]:
        with self._db() as db:
            rows = db.execute("SELECT id, name, prefix, last4, created_at, credit_limit, credits_used, last_used_at FROM api_keys WHERE user_id=? AND revoked_at IS NULL ORDER BY created_at", (user_id,)).fetchall()
        return [{**dict(r), "masked": f"{r['prefix']}…{r['last4']}"} for r in rows]

    def revoke_key(self, user_id: str, key_id: str) -> bool:
        with self._db() as db:
            return db.execute("UPDATE api_keys SET revoked_at=? WHERE id=? AND user_id=? AND revoked_at IS NULL", (time.time(), key_id, user_id)).rowcount > 0

    def set_key_limit(self, user_id: str, key_id: str, credit_limit: int | None) -> bool:
        if credit_limit is not None and credit_limit <= 0:
            raise AccountError("El límite de créditos debe ser positivo")
        with self._db() as db:
            return db.execute("UPDATE api_keys SET credit_limit=? WHERE id=? AND user_id=? AND revoked_at IS NULL", (credit_limit, key_id, user_id)).rowcount > 0

    def authenticate_key(self, plain: str) -> dict | None:
        if not plain.startswith(KEY_PREFIX):
            return None
        with self._db() as db:
            row = db.execute("SELECT id, user_id, credit_limit, credits_used FROM api_keys WHERE key_hash=? AND revoked_at IS NULL", (_sha(plain),)).fetchone()
        return dict(row) if row else None

    # --- créditos y uso ------------------------------------------
    def check_funds(self, auth: dict, cost: int) -> str | None:
        user = self.user(auth["user_id"])
        if user is None or user["credits_remaining"] < cost:
            return "Créditos de la cuenta agotados"
        if auth.get("id") and auth.get("credit_limit") is not None:
            with self._db() as db:
                used = db.execute("SELECT credits_used FROM api_keys WHERE id=?", (auth["id"],)).fetchone()["credits_used"]
            if used + cost > auth["credit_limit"]:
                return "Límite de créditos de la clave alcanzado"
        return None

    def record_usage(self, user_id: str, key_id: str | None, host: str, status_code: int | None, success: bool, credits: int, nbytes: int, duration_ms: float | None, proxied: bool) -> None:
        now = time.time()
        credits = credits if success else 0
        with self._db() as db:
            db.execute("INSERT INTO usage (user_id, key_id, ts, host, status_code, success, credits, bytes, duration_ms, proxied) VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (user_id, key_id, now, host, status_code, int(success), credits, nbytes, duration_ms, int(proxied)))
            if credits:
                db.execute("UPDATE users SET credits_used=credits_used+? WHERE id=?", (credits, user_id))
            if key_id:
                db.execute("UPDATE api_keys SET credits_used=credits_used+?, last_used_at=? WHERE id=?", (credits, now, key_id))

    def usage_summary(self, user_id: str, days: int = 30) -> dict:
        since = time.time() - days * 86400
        with self._db() as db:
            totals = db.execute("SELECT count(*) n, coalesce(sum(success),0) ok, coalesce(sum(credits),0) credits, coalesce(sum(bytes),0) bytes, avg(duration_ms) avg_ms FROM usage WHERE user_id=? AND ts>=?", (user_id, since)).fetchone()
            daily = db.execute("SELECT date(ts,'unixepoch') day, count(*) n, sum(success) ok, sum(credits) credits FROM usage WHERE user_id=? AND ts>=? GROUP BY day ORDER BY day", (user_id, since)).fetchall()
            recent = db.execute("SELECT u.ts, u.host, u.status_code, u.success, u.credits, u.duration_ms, u.proxied, k.name key_name FROM usage u LEFT JOIN api_keys k ON k.id=u.key_id WHERE u.user_id=? ORDER BY u.id DESC LIMIT 50", (user_id,)).fetchall()
        return {"days": days, "requests": totals["n"], "successful": totals["ok"], "credits": totals["credits"], "bytes": totals["bytes"],
                "avg_duration_ms": round(totals["avg_ms"], 1) if totals["avg_ms"] is not None else None,
                "daily": [dict(r) for r in daily], "recent": [dict(r) for r in recent]}

    # --- administración ------------------------------------------
    def grant_credits(self, email: str, credits: int, plan: str | None = None) -> dict:
        with self._db() as db:
            row = db.execute("SELECT id FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
            if not row:
                raise LookupError("Usuario no encontrado")
            db.execute("UPDATE users SET credits_total=max(credits_used, credits_total+?), plan=coalesce(?, plan) WHERE id=?", (credits, plan, row["id"]))
        return self.user(row["id"])

    def list_users(self) -> list[dict]:
        with self._db() as db:
            rows = db.execute("SELECT id, email, created_at, credits_total, credits_used, plan FROM users ORDER BY created_at").fetchall()
        return [dict(r) for r in rows]
