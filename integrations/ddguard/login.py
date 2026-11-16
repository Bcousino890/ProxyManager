"""Log in to Idealista once and keep the session in the same store as the DataDome cookie.

Two ways:
  * manual (recommended, safest): a visible browser opens, you log in yourself (and solve any
    CAPTCHA), the cookies are saved. Run it on the VPS through noVNC, or on your PC with the SAME
    proxy as the VPS (cookies are IP-bound).
  * auto: fills email + password from env IDEALISTA_EMAIL / IDEALISTA_PASSWORD. The login form
    selectors are generic (input[type=email] / input[type=password]); if Idealista changes the form,
    fall back to manual.

Login is OPTIONAL: listing and search pages are public. A logged-in account gives DataDome one
more "trusted" signal, but every request is then tied to that account (it can be banned).
"""
from __future__ import annotations

import asyncio
import logging
import os
import time

from .solver import BrowserSolver
from .store import SessionStore, identity_key

log = logging.getLogger("ddguard.login")

LOGIN_URL = "https://www.idealista.com/login"
LOGGED_IN_HINTS = ("logout", "cerrar sesión", "mi cuenta", "user-menu")


async def login(proxy_url: str | None = None, store_dir: str = "dd_sessions",
                mode: str = "manual", timeout_s: int = 600, engine: str = "camoufox") -> bool:
    solver = BrowserSolver(engine=engine, headless=False, captcha_mode="wait",
                           captcha_wait_s=timeout_s)
    store = SessionStore(store_dir)
    state = store.load(identity_key(proxy_url))
    try:
        res = await solver.solve(LOGIN_URL, state.cookies, proxy_url)  # clears DD if needed
        page = solver._page  # noqa: SLF001  (same warm page)
        if mode == "auto":
            email, pwd = os.environ["IDEALISTA_EMAIL"], os.environ["IDEALISTA_PASSWORD"]
            await page.fill("input[type=email], input[name*=email]", email)
            await page.fill("input[type=password]", pwd)
            await page.keyboard.press("Enter")
        else:
            print(f"Log in in the browser window (you have {timeout_s}s)...")
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            html = (await page.content()).lower()
            if any(h in html for h in LOGGED_IN_HINTS) and "/login" not in page.url:
                break
            await asyncio.sleep(3)
        else:
            log.error("login not detected before timeout")
            return False
        jar = {c["name"]: c["value"] for c in await solver._ctx.cookies()  # noqa: SLF001
               if "idealista" in c.get("domain", "")}
        state.cookies.update(jar)
        state.user_agent = res.user_agent
        from .session import profile_for_ua
        state.tls_profile = profile_for_ua(res.user_agent)
        state.logged_in = True
        store.save(state)
        log.warning("logged in; %d cookies saved for %s", len(jar), state.identity)
        return True
    finally:
        await solver.close()
