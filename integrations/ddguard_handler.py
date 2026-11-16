"""Adaptador de ddguard al punto de extensión genérico de ProxyManager (challenges.py).

No se activa solo. Dos llaves independientes deben estar puestas:

1. Código/despliegue: PROXYMANAGER_CHALLENGE_HANDLER=integrations.ddguard_handler:build_handler
   y las dependencias de integrations/ddguard/requirements.txt instaladas (`pip install -e '.[ddguard]'`).
2. Autorización en producción: en /admin/ → Desafíos, declarar quién autorizó y una referencia
   verificable. Sin esa declaración activa, /scrape nunca invoca este manejador aunque esté
   configurado (ver accounts... en realidad src/proxymanager/authorization.py y app.py).

Este adaptador SOLO actúa sobre idealista.com: para cualquier otro destino devuelve None (no
aplica) para que no se use por error fuera del alcance para el que se construyó y documentó.

Responsabilidad de quien active la llave 2: declarar una autorización real y verificable.
Ninguna de las dos llaves comprueba por software que la autorización exista de verdad.
"""
from __future__ import annotations

import os
from urllib.parse import urlsplit

from proxymanager.challenges import ChallengeContext, ChallengeResolution

_ALLOWED_SUFFIX = ".idealista.com"
_ALLOWED_HOST = "idealista.com"


class IdealistaDDGuardHandler:
    """Envuelve ddguard.DDSession. Una sesión (cookie jar) por identidad de red (proxy o directa)."""

    name = "ddguard-idealista"

    def __init__(self, store_dir: str = "dd_sessions", headless: bool = True, captcha_mode: str = "wait",
                 min_interval: float = 2.5, jitter: float = 1.5, cooldown_s: float = 900,
                 ban_cooldown_s: float = 6 * 3600, timeout: float = 30):
        self.store_dir, self.headless, self.captcha_mode = store_dir, headless, captcha_mode
        self.min_interval, self.jitter = min_interval, jitter
        self.cooldown_s, self.ban_cooldown_s, self.timeout = cooldown_s, ban_cooldown_s, timeout
        self._sessions: dict[str, object] = {}

    @staticmethod
    def _in_scope(url: str) -> bool:
        host = (urlsplit(url).hostname or "").lower()
        return host == _ALLOWED_HOST or host.endswith(_ALLOWED_SUFFIX)

    def _session_for(self, proxy_url: str | None):
        from .ddguard.session import DDSession
        from .ddguard.solver import BrowserSolver
        key = proxy_url or "_direct"
        if key not in self._sessions:
            solver = BrowserSolver(headless=self.headless, captcha_mode=self.captcha_mode)
            self._sessions[key] = DDSession(proxy_url=proxy_url, store_dir=self.store_dir, solver=solver,
                                             min_interval=self.min_interval, jitter=self.jitter,
                                             cooldown_s=self.cooldown_s, ban_cooldown_s=self.ban_cooldown_s,
                                             timeout=self.timeout)
        return self._sessions[key]

    async def handle(self, context: ChallengeContext) -> ChallengeResolution | None:
        if not self._in_scope(context.url):
            return None  # fuera de alcance: este manejador solo actúa sobre idealista.com
        from .ddguard.detect import Verdict
        from .ddguard.session import Blocked

        session = self._session_for(context.proxy_url)
        try:
            page = await session.get(context.url, referer=context.url)
        except Blocked as exc:
            return ChallengeResolution(resolved=False, note=f"identidad en pausa: {exc}")
        except Exception as exc:  # error de red/navegador: se informa, no se cobra
            return ChallengeResolution(resolved=False, note=f"ddguard falló: {exc.__class__.__name__}")
        return ChallengeResolution(
            resolved=page.verdict in (Verdict.OK, Verdict.NOT_FOUND),
            html=page.text, status_code=page.status,
            note=f"verdict={page.verdict.value} solved_by_browser={page.solved}",
        )

    async def aclose(self) -> None:
        for session in self._sessions.values():
            await session.close()


def build_handler() -> IdealistaDDGuardHandler:
    """Fábrica leída por PROXYMANAGER_CHALLENGE_HANDLER=integrations.ddguard_handler:build_handler."""
    return IdealistaDDGuardHandler(
        store_dir=os.getenv("DDGUARD_STORE_DIR", "dd_sessions"),
        headless=os.getenv("DDGUARD_HEADLESS", "true").strip().lower() not in ("0", "false", "no"),
        captcha_mode=os.getenv("DDGUARD_CAPTCHA_MODE", "wait"),
        min_interval=float(os.getenv("DDGUARD_MIN_INTERVAL", "2.5")),
        jitter=float(os.getenv("DDGUARD_JITTER", "1.5")),
        cooldown_s=float(os.getenv("DDGUARD_COOLDOWN_S", "900")),
        ban_cooldown_s=float(os.getenv("DDGUARD_BAN_COOLDOWN_S", str(6 * 3600))),
    )
