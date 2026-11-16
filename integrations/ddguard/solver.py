"""Browser solver: clear a DataDome challenge in a real browser, then hand the cookie back to HTTP.

Flow:
  1. Open a stealth browser on the SAME IP/proxy as the HTTP session (the cookie is IP-bound).
  2. Inject the current cookies (keeps the login + DataDome history) and open the blocked URL.
  3. Interstitial (rt:'i'): move the mouse and wait. It clears by itself in ~20 s (measured).
  4. Slider CAPTCHA (rt:'c'): depending on `captcha_mode`:
       "wait"     -> visible window. Call `notify` and wait for a human to solve it
                     (on a VPS: Xvfb + noVNC, see README). Free.
       "callback" -> call `captcha_callback(page, dd)`; plug in any solver you want.
       "fail"     -> give up and raise (the caller cools down).
  5. Return cookies + navigator.userAgent + the page HTML. The browser stays open for
     `idle_close_s` seconds, so the next challenge does not pay the start-up cost again.

Engine: Camoufox (Firefox with fingerprint spoofing) by default. It cleared Idealista's
interstitial in ~20 s in our tests, and its cookie replays over curl_cffi `firefox147`/`firefox144`
(NOT over Safari/Chrome TLS: the fingerprint must match the browser that earned the cookie).
"chromium" uses the plain Playwright Chromium the client already has (not tested against DD).
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Awaitable, Callable
from urllib.parse import urlparse

from .detect import parse_dd

log = logging.getLogger("ddguard.solver")

BLOCKED_TEXT = ("acceso se ha bloqueado", "uso indebido", "access is temporarily restricted",
                "you have been blocked", "has been blocked")

NotifyFn = Callable[[str], "Awaitable[None] | None"]
CaptchaCallback = Callable[[object, dict], Awaitable[bool]]


class SolveFailed(RuntimeError):
    pass


@dataclass
class SolveResult:
    cookies: dict[str, str]
    user_agent: str
    html: str
    engine: str
    seconds: float
    final_url: str = ""


def _pw_proxy(proxy_url: str | None) -> dict | None:
    if not proxy_url:
        return None
    p = urlparse(proxy_url)
    out = {"server": f"{p.scheme}://{p.hostname}:{p.port}"}
    if p.username:
        out["username"] = p.username
        out["password"] = p.password or ""
    return out


async def page_state(page) -> tuple[str, str]:
    """Return ('ok'|'interstitial'|'captcha'|'banned'|'pending', html)."""
    try:
        html = await page.content()
    except Exception:  # noqa: BLE001  (navigation in progress)
        return "pending", ""
    frame = next((f for f in page.frames if "captcha-delivery.com" in f.url), None)
    if not frame and "captcha-delivery.com" not in html[:6000]:
        return "ok", html
    if frame is None:
        return "pending", html
    if "t=bv" in frame.url:
        return "banned", html
    try:
        ftext = (await frame.inner_text("body", timeout=3000)).lower()
    except Exception:  # noqa: BLE001  (frame still loading)
        ftext = ""
    # The /interstitial/ frame carries the "uso indebido / acceso bloqueado" text as fallback
    # while its JS check runs (measured 16 Nov), so that text only means a ban on /captcha/.
    if "/interstitial/" in frame.url:
        return "interstitial", html
    # Hard block page: "Se ha detectado un uso indebido. El acceso se ha bloqueado" (no t=bv in URL)
    if any(m in ftext for m in BLOCKED_TEXT):
        return "banned", html
    if "/captcha/" in frame.url and ftext:
        return "captcha", html   # slider / puzzle
    return "pending", html


class BrowserSolver:
    def __init__(self, engine: str = "camoufox", headless: bool = True,
                 captcha_mode: str = "wait", captcha_wait_s: int = 600,
                 interstitial_wait_s: int = 75, notify: NotifyFn | None = None,
                 captcha_callback: CaptchaCallback | None = None, idle_close_s: int = 300):
        self.engine = engine
        self.headless = headless
        self.captcha_mode = captcha_mode
        self.captcha_wait_s = captcha_wait_s
        self.interstitial_wait_s = interstitial_wait_s
        self.notify = notify
        self.captcha_callback = captcha_callback
        self.idle_close_s = idle_close_s
        self._cm = self._browser = self._ctx = self._page = None
        self._proxy: str | None = None
        self._lock = asyncio.Lock()
        self._idle_task: asyncio.Task | None = None
        self._last_used = time.monotonic()

    async def _notify(self, msg: str) -> None:
        log.warning(msg)
        if self.notify:
            r = self.notify(msg)
            if asyncio.iscoroutine(r):
                await r

    async def _launch(self, proxy_url: str | None):
        if self.engine == "camoufox":
            from camoufox.async_api import AsyncCamoufox
            cm = AsyncCamoufox(headless=self.headless, humanize=True, proxy=_pw_proxy(proxy_url),
                               geoip=bool(proxy_url), locale="es-ES",
                               i_know_what_im_doing=True)
            return cm, await cm.__aenter__()
        from playwright.async_api import async_playwright
        cm = async_playwright()
        pw = await cm.__aenter__()
        browser = await pw.chromium.launch(headless=self.headless, proxy=_pw_proxy(proxy_url),
                                           args=["--disable-blink-features=AutomationControlled"])
        return cm, browser

    async def _ensure(self, proxy_url: str | None, cookies: dict[str, str] | None):
        if self._browser is not None and self._proxy == proxy_url:
            return
        await self._close_unlocked()
        self._cm, self._browser = await self._launch(proxy_url)
        self._proxy = proxy_url
        self._ctx = await self._browser.new_context(locale="es-ES")
        if cookies:
            await self._ctx.add_cookies([{"name": k, "value": v, "domain": ".idealista.com",
                                          "path": "/"} for k, v in cookies.items()])
        self._page = await self._ctx.new_page()
        if self._idle_task is None or self._idle_task.done():
            self._idle_task = asyncio.ensure_future(self._idle_watch())

    async def _idle_watch(self):
        while self._browser is not None:
            await asyncio.sleep(15)
            if time.monotonic() - self._last_used > self.idle_close_s:
                async with self._lock:
                    if time.monotonic() - self._last_used > self.idle_close_s:
                        log.info("browser idle %ss -> closed", self.idle_close_s)
                        await self._close_unlocked()

    async def solve(self, url: str, cookies: dict[str, str] | None = None,
                    proxy_url: str | None = None) -> SolveResult:
        """Open `url` in the browser, clear any challenge, return cookies + UA + HTML."""
        async with self._lock:
            t0 = time.monotonic()
            self._last_used = t0
            await self._ensure(proxy_url, cookies)
            page, ctx = self._page, self._ctx
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=90_000)
                if resp is not None and resp.status in (404, 410):
                    raise SolveFailed(f"HTTP {resp.status} (listing removed?)")
            except SolveFailed:
                raise
            except Exception as e:  # noqa: BLE001  (challenge pages sometimes abort the load)
                log.info("goto raised %r, polling anyway", e)
            try:
                html = await self._wait_clear(page, url)
                await asyncio.sleep(1.0)  # let DataDome set the final cookie
                jar = {c["name"]: c["value"] for c in await ctx.cookies()
                       if "idealista" in c.get("domain", "")}
                ua = await page.evaluate("() => navigator.userAgent")
                final_url = page.url
            finally:
                self._last_used = time.monotonic()
            return SolveResult(jar, ua, html, self.engine, time.monotonic() - t0, final_url)

    async def _wait_clear(self, page, url: str) -> str:
        deadline = time.monotonic() + self.interstitial_wait_s
        captcha_announced = False
        i = 0
        while True:
            state, html = await page_state(page)
            if state == "ok" and len(html) > 20_000:
                return await page.content()
            if state == "banned":
                raise SolveFailed("IP blocked by DataDome ('uso indebido' / t=bv): "
                                  "change IP or wait several hours")
            if state == "captcha":
                if self.captcha_mode == "fail":
                    raise SolveFailed("slider CAPTCHA and captcha_mode='fail'")
                if self.captcha_mode == "callback" and self.captcha_callback:
                    if not await self.captcha_callback(page, parse_dd(html)):
                        raise SolveFailed("captcha_callback could not solve it")
                elif not captcha_announced:
                    captcha_announced = True
                    if self.headless:
                        raise SolveFailed("slider CAPTCHA in headless mode: set headless=False "
                                          "(Xvfb + noVNC on the VPS) to solve it by hand")
                    deadline = time.monotonic() + self.captcha_wait_s
                    await self._notify(f"[ddguard] CAPTCHA on {url}: solve it in the browser "
                                       f"window (waiting {self.captcha_wait_s}s)")
            if time.monotonic() > deadline:
                raise SolveFailed(f"challenge not cleared in time (last state={state})")
            try:  # human-ish mouse movement helps the interstitial pass
                await page.mouse.move(120 + (i * 37) % 600, 140 + (i * 23) % 400, steps=8)
            except Exception:  # noqa: BLE001
                pass
            i += 1
            await asyncio.sleep(2.0)

    async def _close_unlocked(self):
        b, cm = self._browser, self._cm
        self._browser = self._cm = self._ctx = self._page = None
        for closer in (lambda: b.close() if b else None,
                       lambda: cm.__aexit__(None, None, None) if cm else None):
            try:
                r = closer()
                if r is not None:
                    await r
            except Exception:  # noqa: BLE001
                pass

    async def close(self):
        async with self._lock:
            await self._close_unlocked()
        if self._idle_task:
            self._idle_task.cancel()
