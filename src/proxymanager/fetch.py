import ipaddress
import socket
import time
from collections.abc import Callable
from urllib.parse import urlsplit, urlunsplit

import httpx

from .config import Settings


class DestinationRejected(ValueError):
    pass


def guard_url(url: str, settings: Settings) -> tuple[str, str]:
    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        port = parsed.port
    except ValueError as exc:
        raise DestinationRejected("URL inválida") from exc
    if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.fragment or port not in (None, 443):
        raise DestinationRejected("Solo se permiten URLs HTTPS estándar")
    if host not in settings.allowed_hosts:
        raise DestinationRejected("Destino no autorizado")
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        addresses = [str(literal)]
    else:
        try:
            addresses = [item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)]
        except socket.gaierror as exc:
            raise DestinationRejected("No se pudo resolver el destino") from exc
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise DestinationRejected("El destino resuelve a una dirección no pública")
    pinned_host = f"[{addresses[0]}]" if ":" in addresses[0] else addresses[0]
    pinned_url = urlunsplit(("https", pinned_host, parsed.path or "/", parsed.query, ""))
    return pinned_url, host


async def fetch(url: str, settings: Settings, transport: httpx.AsyncBaseTransport | None = None,
                cookie_header: str = "", on_set_cookie: Callable[[list[str]], None] | None = None) -> dict:
    pinned_url, host = guard_url(url, settings)
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(transport=transport, timeout=settings.timeout_seconds, follow_redirects=False, trust_env=False) as client:
            headers = {"Host": host}
            if cookie_header:
                headers["Cookie"] = cookie_header
            request = client.build_request("GET", pinned_url, headers=headers, extensions={"sni_hostname": host})
            response = await client.send(request, stream=True)
            try:
                if on_set_cookie:
                    on_set_cookie(response.headers.get_list("set-cookie"))
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > settings.max_response_bytes:
                        raise ValueError("La respuesta supera el límite configurado")
                html = content.decode(response.encoding or "utf-8", errors="replace")
                lowered = html.lower()
                challenge = any(marker in lowered for marker in ("captcha", "datadome", "device check"))
                expected = bool(settings.expected_text and settings.expected_text in html)
                success = response.status_code == 200 and expected and not challenge
                return {
                    "success": success,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    "bytes_transferred": len(content),
                    "validation": {"content_expected": expected, "challenge_detected": challenge},
                    "html": html,
                }
            finally:
                await response.aclose()
    except httpx.HTTPError as exc:
        return {"success": False, "status_code": None, "error": {"type": "transport_error", "message": type(exc).__name__}  # solo la clase: el texto puede contener datos de la conexión del proxy, "validation": {"content_expected": False, "challenge_detected": False}}
