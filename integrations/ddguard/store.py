"""Persistent session store: cookies + User-Agent + TLS profile, one file per network identity.

The `datadome` cookie is bound to the IP that earned it, so the store keys sessions by
"identity" (the proxy URL, or "direct" for the VPS IP). Never share a cookie across IPs.
Writes are atomic (tmp file + rename) so a crash never leaves a corrupt session.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


def identity_key(proxy_url: str | None) -> str:
    if not proxy_url:
        return "direct"
    return "proxy-" + hashlib.sha1(proxy_url.encode()).hexdigest()[:10]


@dataclass
class SessionState:
    identity: str
    cookies: dict[str, str] = field(default_factory=dict)
    user_agent: str | None = None      # set when cookies came from a browser
    tls_profile: str | None = None     # curl_cffi profile that matches that browser
    logged_in: bool = False
    solved_at: float | None = None     # last time a browser cleared a challenge
    ok_requests: int = 0
    challenges: int = 0
    cooldown_until: float = 0.0
    updated_at: float = field(default_factory=time.time)


class SessionStore:
    def __init__(self, directory: str | os.PathLike = "dd_sessions"):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, identity: str) -> Path:
        return self.dir / f"{identity}.json"

    def load(self, identity: str) -> SessionState:
        p = self._path(identity)
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return SessionState(**data)
            except (ValueError, TypeError):
                p.rename(p.with_suffix(".corrupt.json"))  # keep it for debugging, start clean
        return SessionState(identity=identity)

    def save(self, state: SessionState) -> None:
        state.updated_at = time.time()
        p = self._path(state.identity)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")
        os.replace(tmp, p)

    # --- Playwright interop -------------------------------------------------------------
    @staticmethod
    def to_playwright_cookies(state: SessionState, domain: str = ".idealista.com") -> list[dict]:
        return [{"name": k, "value": v, "domain": domain, "path": "/", "secure": True,
                 "sameSite": "Lax"} for k, v in state.cookies.items()]

    @staticmethod
    def from_playwright_cookies(cookies: list[dict], domain_filter: str = "idealista") -> dict:
        return {c["name"]: c["value"] for c in cookies if domain_filter in c.get("domain", "")}
