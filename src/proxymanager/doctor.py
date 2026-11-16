"""Diagnóstico previo al arranque: `python -m proxymanager.doctor`. No imprime secretos."""
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

from cryptography.fernet import Fernet

from .challenges import load_handler
from .config import Settings
from .proxies import ProxyStore


def diagnose(settings: Settings) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    add = lambda level, msg: out.append((level, msg))
    if len(settings.admin_key) < 24:
        add("ERROR", "PROXYMANAGER_ADMIN_KEY vacía o corta (<24 caracteres): el panel /admin/ no es seguro")
    else:
        add("OK", "Clave de administración configurada")
    try:
        Fernet(settings.credential_key.encode())
        add("OK", "PROXYMANAGER_CREDENTIAL_KEY es una clave Fernet válida")
    except Exception:
        add("ERROR", "PROXYMANAGER_CREDENTIAL_KEY ausente o inválida: sin ella no se guardan credenciales de proxy ni cookies de sesión")
    folder = Path(settings.db_path).resolve().parent
    add("OK" if os.access(folder, os.W_OK) else "ERROR", f"Directorio de la base de datos {'escribible' if os.access(folder, os.W_OK) else 'NO escribible'}")
    add("OK" if settings.cookie_secure else "WARN", "Cookie de consola Secure" if settings.cookie_secure else "PROXYMANAGER_COOKIE_SECURE=false: solo válido en desarrollo por HTTP")
    if settings.allow_any_public_host:
        add("WARN", "ALLOW_ANY_PUBLIC_HOST=true: /scrape llega a cualquier host HTTPS público; confirma la política de uso aceptable")
    else:
        add("OK" if settings.allowed_hosts else "WARN", f"Modo cerrado: {len(settings.allowed_hosts)} hosts autorizados" + ("" if settings.allowed_hosts else " (los clientes no podrán scrapear nada)"))
    if settings.ca_bundle:
        add("OK" if Path(settings.ca_bundle).is_file() else "ERROR", "PROXYMANAGER_CA_BUNDLE " + ("existe" if Path(settings.ca_bundle).is_file() else "no existe"))
    try:
        handler = load_handler(settings.challenge_handler)
        add("OK", f"Manejador de desafíos: {handler.name}" if handler else "Sin manejador de desafíos (por defecto)")
    except Exception as exc:
        add("ERROR", f"Manejador de desafíos no carga: {exc}")
    if settings.health_interval_seconds > 0:
        ok = urlsplit(settings.health_url).scheme == "https"
        add("OK" if ok else "ERROR", "Barrido de salud activo" if ok else "HEALTH_INTERVAL>0 pero PROXYMANAGER_HEALTH_URL no es una URL https")
    else:
        add("WARN", "Barrido periódico de salud desactivado (solo comprobación manual y pasiva)")
    if not settings.support_email:
        add("WARN", "PROXYMANAGER_SUPPORT_EMAIL vacío: los clientes no verán dónde pedir recargas")
    if settings.credential_key:
        try:
            proxies = ProxyStore(settings.db_path, settings.credential_key).list()
            enabled = [p for p in proxies if p["enabled"]]
            add("OK" if enabled else "WARN", f"Proxies: {len(enabled)} activos de {len(proxies)}")
        except Exception:
            add("ERROR", "No se pudo leer el catálogo de proxies")
    return out


def main() -> None:
    results = diagnose(Settings.from_env())
    for level, message in results:
        print(f"[{level:5}] {message}")
    sys.exit(1 if any(level == "ERROR" for level, _ in results) else 0)


if __name__ == "__main__":
    main()
