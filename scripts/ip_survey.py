"""Mide la IP de salida de cada proxy contra un servicio que devuelva la IP en texto plano.

NO se ejecuta por defecto contra ningún servicio: debes indicar uno PROPIO o que apruebes tú
(p. ej. un endpoint tuyo, o un servicio público de eco de IP si decides usarlo):
  PROXYMANAGER_IP_URL=https://tu-servicio/ip  python scripts/ip_survey.py
Requiere PROXYMANAGER_DB_PATH y PROXYMANAGER_CREDENTIAL_KEY de un lote ya importado.
Imprime solo la IP observada por proxy, cuántas IPs distintas hay y su prefijo /24; nunca credenciales.
No consulta geolocalización ni ASN (eso requiere otro servicio; decídelo aparte)."""
import asyncio
import ipaddress
import os
from urllib.parse import urlsplit

from proxymanager.config import Settings
from proxymanager.fetch import fetch
from proxymanager.health import ProxyHealth
from proxymanager.proxies import ProxyStore
from proxymanager.transport import PinnedProxyTransport

URL = os.environ.get("PROXYMANAGER_IP_URL")
if not URL:
    raise SystemExit("Define PROXYMANAGER_IP_URL con un servicio propio o aprobado por ti.")
settings = Settings(db_path=os.environ["PROXYMANAGER_DB_PATH"], credential_key=os.environ["PROXYMANAGER_CREDENTIAL_KEY"],
                    allowed_hosts=(urlsplit(URL).hostname,), max_response_bytes=4096)
store = ProxyStore(settings.db_path, settings.credential_key)
health = ProxyHealth(store, settings)


async def probe(proxy):
    try:
        transport = PinnedProxyTransport(health.connection(proxy["id"]), urlsplit(URL).hostname)
        text = (await fetch(URL, settings, transport)).get("html", "").strip()
        return str(ipaddress.ip_address(text))
    except Exception:  # noqa: BLE001
        return None


async def main():
    proxies = store.list()
    ips = await asyncio.gather(*(probe(p) for p in proxies))
    for n, (p, ip) in enumerate(zip(proxies, ips), 1):
        print(f"{n:>2}  puerto {p['port']}  IP de salida: {ip or 'sin respuesta válida'}")
    seen = {ip for ip in ips if ip}
    nets = {str(ipaddress.ip_network(ip + '/24', strict=False)) for ip in seen if ':' not in ip}
    print(f"IPs distintas: {len(seen)} de {len(proxies)}; prefijos /24 distintos: {len(nets)}")

asyncio.run(main())
