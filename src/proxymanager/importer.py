"""Import locally supplied proxy connections without exporting credentials."""

import argparse
import os
from pathlib import Path
import re

from .proxies import ProxyStore

_HOST = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\Z")


def import_proxy_file(path: Path, store: ProxyStore, provider: str) -> int:
    if not provider.strip():
        raise ValueError("El proveedor no puede estar vacío")
    parsed = []
    for number, raw in enumerate(path.read_text().splitlines(), 1):
        if not raw.strip():
            continue
        fields = raw.strip().split(":", 3)
        if len(fields) != 4:
            raise ValueError(f"Formato inválido en línea {number}")
        host, port_text, username, password = fields
        if not _HOST.fullmatch(host) or not port_text.isdigit() or not 1 <= int(port_text) <= 65535 or not username or not password:
            raise ValueError(f"Formato inválido en línea {number}")
        parsed.append((host, int(port_text), username, password))
    if parsed and store.cipher is None:
        raise ValueError("PROXYMANAGER_CREDENTIAL_KEY es obligatorio")
    known = {(item["host"], item["port"]) for item in store.list()}
    added = 0
    for host, port, username, password in parsed:
        if (host, port) in known:
            continue
        store.create(provider, host, port, "unknown", "ZZ", username, password)
        known.add((host, port))
        added += 1
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description="Importar proxies locales; nunca imprime credenciales")
    parser.add_argument("file", type=Path)
    parser.add_argument("--provider", required=True)
    args = parser.parse_args()
    key = os.getenv("PROXYMANAGER_CREDENTIAL_KEY", "")
    if not key:
        parser.error("PROXYMANAGER_CREDENTIAL_KEY es obligatorio")
    store = ProxyStore(os.getenv("PROXYMANAGER_DB_PATH", "proxymanager.db"), key)
    added = import_proxy_file(args.file, store, args.provider)
    print(f"Importadas: {added}; total: {len(store.list())}")


if __name__ == "__main__":
    main()
