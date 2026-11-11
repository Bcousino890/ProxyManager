from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from proxymanager.importer import import_proxy_file
from proxymanager.proxies import ProxyStore


def test_imports_unique_proxy_connections_without_plaintext(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("proxy.example:10001:alice:secret1\nproxy.example:10002:alice:secret1\n")
    db = tmp_path / "proxies.db"
    store = ProxyStore(str(db), Fernet.generate_key().decode())
    assert import_proxy_file(path, store, "lab-batch") == 2
    assert import_proxy_file(path, store, "lab-batch") == 0
    assert len(store.list()) == 2
    assert all(item["kind"] == "unknown" and item["country"] == "ZZ" for item in store.list())
    assert b"secret1" not in db.read_bytes()
    assert db.stat().st_mode & 0o777 == 0o600


def test_invalid_file_imports_nothing(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("proxy.example:10001:alice:secret1\nbroken line\n")
    store = ProxyStore(str(tmp_path / "proxies.db"), Fernet.generate_key().decode())
    with pytest.raises(ValueError):
        import_proxy_file(path, store, "lab-batch")
    assert store.list() == []
