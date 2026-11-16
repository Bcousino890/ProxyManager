"""DDSession: fetch Idealista pages over cheap HTTP, clear DataDome with a browser only when needed.

    async with DDSession() as dd:
        page = await dd.get("https://www.idealista.com/inmueble/110467049/")
        html = page.text

Why this works (measured 14-16 Nov 2026):
  * curl_cffi `safari2601` (Safari 26 TLS + HTTP/2 fingerprint) with a sticky cookie jar passed
    35/35 requests (5 search pages + 30 listings) from a residential IP with no browser.
    Chrome/Edge/Firefox profiles from curl_cffi were challenged on the same IP.
  * A datacenter VPS IP also passed, until we fired ~35 challenged requests
    in a row. After that, every request on the IP was challenged. Lesson: on a challenge, do
    NOT retry over HTTP. Clear it once in a real browser, then go back to HTTP.

Rules this class enforces:
  * One cookie jar per IP (identity). It is saved to disk, so restarts keep the session and login.
  * Requests are paced (min_interval + jitter), never bursty.
  * Challenge -> the browser opens THAT url, clears it and returns its HTML; its cookies go back
    to HTTP (Firefox TLS to match). A challenged request is never retried over HTTP.
  * Solve fails (CAPTCHA nobody solved, timeout) -> cooldown instead of burning the IP.
  * Ban (t=bv) -> long cooldown; with a DDPool the next IP takes over.
"""
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from urllib.parse import urlparse

from curl_cffi.requests import AsyncSession

from .detect import Classified, Verdict, classify
from .solver import BrowserSolver, SolveFailed
from .store import SessionState, SessionStore, identity_key

log = logging.getLogger("ddguard")

BASE = "https://www.idealista.com/"
DEFAULT_PROFILE = "safari2601"   # the only family that passed cold in our matrix
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}


class Blocked(RuntimeError):
    """The identity is cooling down / banned. Back off or use another IP."""

    def __init__(self, msg: str, retry_after: float):
        super().__init__(msg)
        self.retry_after = retry_after


@dataclass
class Page:
    url: str
    status: int
    text: str
    verdict: Verdict
    solved: bool = False  # True when a browser solve happened for this request


def _path(u: str) -> str:
    return urlparse(u).path.rstrip("/") if u else ""


def _removed_listing(url: str, html: str) -> bool:
    """A removed /inmueble/ listing serves the home page (same URL, status 200).
    `main-info__title` exists on every live listing page and nowhere else (checked 16 Nov)."""
    return "/inmueble/" in url and "main-info__title" not in html


def profile_for_ua(ua: str | None) -> str:
    """Keep TLS and User-Agent consistent after a browser solve (a mismatch is a bot signal)."""
    if ua and "Firefox/" in ua:
        return "firefox147"   # measured: cookie from Camoufox replays OK on firefox147/144
    if ua and "Chrome/" in ua:
        return "chrome146"
    return DEFAULT_PROFILE


class DDSession:
    def __init__(self, proxy_url: str | None = None, store_dir: str = "dd_sessions",
                 solver: BrowserSolver | None = None, min_interval: float = 2.5,
                 jitter: float = 1.5, cooldown_s: float = 900, ban_cooldown_s: float = 6 * 3600,
                 data_marker: str | None = None, timeout: float = 30):
        self.proxy_url = proxy_url
        self.identity = identity_key(proxy_url)
        self.store = SessionStore(store_dir)
        self.state: SessionState = self.store.load(self.identity)
        self.solver = solver or BrowserSolver()
        self.min_interval, self.jitter = min_interval, jitter
        self.cooldown_s, self.ban_cooldown_s = cooldown_s, ban_cooldown_s
        self.data_marker = data_marker
        self.timeout = timeout
        self._http: AsyncSession | None = None
        self._http_profile: str | None = None
        self._pace_lock = asyncio.Lock()
        self._solve_lock = asyncio.Lock()
        self._last_req = 0.0
        self._dirty = 0

    # --- lifecycle ----------------------------------------------------------------------
    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()

    async def close(self):
        self._persist(force=True)
        await self.solver.close()
        if self._http:
            await self._http.close()
            self._http = None

    # --- internals ----------------------------------------------------------------------
    def _client(self) -> AsyncSession:
        profile = self.state.tls_profile or DEFAULT_PROFILE
        if self._http is None or self._http_profile != profile:
            if self._http:
                asyncio.ensure_future(self._http.close())
            proxies = {"http": self.proxy_url, "https": self.proxy_url} if self.proxy_url else None
            self._http = AsyncSession(impersonate=profile, proxies=proxies, timeout=self.timeout)
            self._http_profile = profile
        return self._http

    def _persist(self, force: bool = False):
        self._dirty += 1
        if force or self._dirty >= 10:
            self.store.save(self.state)
            self._dirty = 0

    async def _pace(self):
        async with self._pace_lock:
            wait = self._last_req + self.min_interval + random.uniform(0, self.jitter) - time.time()
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_req = time.time()

    async def _raw_get(self, url: str, referer: str | None) -> tuple[Classified, str, int]:
        await self._pace()
        headers = dict(HEADERS)
        if self.state.user_agent:
            headers["User-Agent"] = self.state.user_agent
        if referer:
            headers["Referer"] = referer
        try:
            r = await self._client().get(url, headers=headers, cookies=self.state.cookies)
        except Exception as e:  # noqa: BLE001  (network error, connection reset)
            log.warning("network error %s: %r", url, e)
            return Classified(Verdict.ERROR, 0), "", 0
        # merge cookies DataDome/Idealista rotate on every response
        for k, v in r.cookies.items():
            self.state.cookies[k] = v
        return classify(r.status_code, r.text, dict(r.headers), self.data_marker), r.text, r.status_code

    def _check_cooldown(self):
        left = self.state.cooldown_until - time.time()
        if left > 0:
            raise Blocked(f"{self.identity} cooling down for {left:.0f}s", left)

    def _cool(self, seconds: float, why: str):
        self.state.cooldown_until = time.time() + seconds
        self._persist(force=True)
        log.error("%s -> cooldown %.0fs (%s)", self.identity, seconds, why)
        raise Blocked(f"{self.identity}: {why}", seconds)

    async def solve(self, url: str = BASE) -> str:
        """Open `url` in a browser on this identity's IP, clear the challenge, adopt its
        cookies + UA (and the matching Firefox TLS). Returns the page HTML."""
        async with self._solve_lock:
            log.warning("DataDome challenge -> browser solve (%s) on %s", self.solver.engine, url)
            # Do NOT hand the browser the `datadome` cookie that came with the 403: it is already
            # flagged and drags the fresh browser down to the slider CAPTCHA (measured 16 Nov:
            # with it, the next request escalated; without it, 4/4 replays passed).
            # Login/session cookies are kept.
            carry = {k: v for k, v in self.state.cookies.items() if k != "datadome"}
            res = await self.solver.solve(url, carry, self.proxy_url)
            self.state.cookies.update(res.cookies)
            self.state.user_agent = res.user_agent
            self.state.tls_profile = profile_for_ua(res.user_agent)
            self.state.solved_at = time.time()
            self._persist(force=True)
            log.warning("solved in %.0fs; HTTP continues with %s", res.seconds,
                        self.state.tls_profile)
            if res.final_url and _path(res.final_url) != _path(url):
                # removed listings redirect to the home page / search: report it, not "OK"
                raise SolveFailed(f"HTTP 404 (redirected to {res.final_url})")
            return res.html

    # --- public API ---------------------------------------------------------------------
    async def get(self, url: str, referer: str | None = BASE, retries: int = 2) -> Page:
        """Fetch a page. Raises `Blocked` while this IP is cooling down (sleep or switch IP)."""
        self._check_cooldown()
        for attempt in range(retries + 1):
            c, text, status = await self._raw_get(url, referer)
            v = c.verdict
            if v in (Verdict.OK, Verdict.NOT_FOUND):
                if v == Verdict.OK and _removed_listing(url, text):
                    return Page(url, 404, text, Verdict.NOT_FOUND)
                self.state.ok_requests += v == Verdict.OK
                self._persist()
                return Page(url, status, text, v)
            if v == Verdict.BANNED:
                self._cool(self.ban_cooldown_s, "IP banned by DataDome (t=bv)")
            if c.is_challenge:
                self.state.challenges += 1
                # Never retry a challenged request over HTTP: repeated 403s are what get an IP
                # banned. The browser opens THIS url, clears it, and its HTML is the answer.
                try:
                    html = await self.solve(url)
                except SolveFailed as e:
                    if "HTTP 404" in str(e) or "HTTP 410" in str(e):
                        return Page(url, 404, "", Verdict.NOT_FOUND, True)
                    ban = "blocked" in str(e)
                    self._cool(self.ban_cooldown_s if ban else self.cooldown_s,
                               f"solve failed: {e}")
                if _removed_listing(url, html):
                    return Page(url, 404, html, Verdict.NOT_FOUND, True)
                self.state.ok_requests += 1
                self._persist()
                return Page(url, 200, html, Verdict.OK, True)
            # rate limit / network / 5xx: exponential backoff, few attempts
            await asyncio.sleep(min(60, 5 * 2 ** attempt) + random.uniform(0, 2))
        if v == Verdict.RATE_LIMITED:
            self._cool(self.cooldown_s / 3, "HTTP 429 persists")
        return Page(url, status, text, v)


class DDPool:
    """Several identities (VPS IP + optional proxies). Uses the first one that is not cooling down."""

    def __init__(self, proxy_urls: list[str | None], **kw):
        self.sessions = [DDSession(proxy_url=p, **kw) for p in proxy_urls]

    async def get(self, url: str, **kw) -> Page:
        last: Blocked | None = None
        for s in self.sessions:
            try:
                return await s.get(url, **kw)
            except Blocked as e:
                last = e
        raise last or Blocked("no identities", 60)

    async def close(self):
        for s in self.sessions:
            await s.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()
