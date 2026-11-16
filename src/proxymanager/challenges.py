"""Punto de extensión para desafíos (CAPTCHA, páginas de verificación).

El servicio **no incluye** ninguna implementación: por defecto no hay manejador y los desafíos se
informan sin resolver (`challenge.handled = false`) y no se cobran. Un programador puede conectar el
suyo con `PROXYMANAGER_CHALLENGE_HANDLER=paquete.modulo:fabrica`. Quien lo conecte es responsable de
tener autorización sobre el destino y de cumplir las condiciones del sitio y la ley aplicable.
Ver docs/extending-challenge-handlers.md.
"""
from dataclasses import dataclass, field
import importlib
from typing import Protocol


@dataclass
class ChallengeContext:
    url: str
    method: str
    status_code: int | None
    headers: dict[str, str]
    html: str
    session_id: str | None = None
    proxy_id: str | None = None
    cookies: str = ""


@dataclass
class ChallengeResolution:
    resolved: bool
    html: str | None = None
    status_code: int | None = None
    headers: dict[str, str] | None = None
    set_cookies: list[str] = field(default_factory=list)  # valores Set-Cookie para guardar en la sesión
    note: str = ""


class ChallengeHandler(Protocol):
    name: str

    async def handle(self, context: ChallengeContext) -> ChallengeResolution | None:
        """Devuelve una resolución o None si no aplica. Puede lanzar excepciones: se registran como error."""


class NoopHandler:
    name = "noop"

    async def handle(self, context: ChallengeContext) -> ChallengeResolution | None:
        return None


def load_handler(spec: str) -> ChallengeHandler | None:
    """`modulo:fabrica` -> objeto con `name` y `handle`. Cadena vacía = sin manejador."""
    if not spec.strip():
        return None
    module_name, _, attr = spec.partition(":")
    if not module_name or not attr:
        raise ValueError("PROXYMANAGER_CHALLENGE_HANDLER debe tener el formato modulo:fabrica")
    target = getattr(importlib.import_module(module_name), attr)
    handler = target() if isinstance(target, type) or (callable(target) and not hasattr(target, "handle")) else target
    if not hasattr(handler, "handle") or not hasattr(handler, "name"):
        raise ValueError("El manejador debe tener los atributos name y handle()")
    return handler
