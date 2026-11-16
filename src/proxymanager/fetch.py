import ipaddress
import socket
import ssl
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
    if any(host == b or host.endswith("." + b) for b in settings.blocked_hosts):
        raise DestinationRejected("Destino bloqueado por la política del servicio")
    if host not in settings.allowed_hosts and not (settings.allow_any_public_host and "." in host):
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


CHALLENGE_MARKERS = ("captcha", "datadome", "device check")


def classify(html: str, status_code: int, settings: Settings, expected_text: str | None = None) -> tuple[bool, dict]:
    challenge = any(marker in html.lower() for marker in CHALLENGE_MARKERS)
    required = settings.expected_text if expected_text is None else expected_text
    expected = (required in html) if required else True
    return 200 <= status_code < 300 and expected and not challenge, {"content_expected": expected, "challenge_detected": challenge}


async def fetch(url: str, settings: Settings, transport: httpx.AsyncBaseTransport | None = None,
                cookie_header: str = "", on_set_cookie: Callable[[list[str]], None] | None = None,
                method: str = "GET", headers: dict[str, str] | None = None, body: bytes | None = None, expected_text: str | None = None) -> dict:
    pinned_url, host = guard_url(url, settings)
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(transport=transport, timeout=settings.timeout_seconds, follow_redirects=False, trust_env=False, **({"verify": ssl.create_default_context(cafile=settings.ca_bundle)} if settings.ca_bundle and transport is None else {})) as client:
            out_headers = {k: v for k, v in (headers or {}).items() if k.lower() != "cookie"}
            out_headers["Host"] = host
            cookies = "; ".join(p for p in ((headers or {}).get(next((k for k in (headers or {}) if k.lower() == "cookie"), ""), ""), cookie_header) if p)
            if cookies:
                out_headers["Cookie"] = cookies
            request = client.build_request(method, pinned_url, headers=out_headers, content=body, extensions={"sni_hostname": host})
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
                success, validation = classify(html, response.status_code, settings, expected_text)
                return {
                    "success": success,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    "bytes_transferred": len(content),
                    "headers": {k: v for k, v in response.headers.items() if k.lower() != "set-cookie"},
                    "validation": validation,
                    "html": html,
                }
            finally:
                await response.aclose()
    except httpx.HTTPError as exc:
        return {"success": False, "status_code": None, "error": {"type": "transport_error", "message": str(exc)}, "validation": {"content_expected": False, "challenge_detected": False}}
