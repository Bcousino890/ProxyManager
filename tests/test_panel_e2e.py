import os
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest
import httpx
import uvicorn
from cryptography.fernet import Fernet

from proxymanager.app import create_app
from test_api import make_settings


def _node_has_playwright() -> bool:
    node = shutil.which("node")
    if not node:
        return False
    root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip() if shutil.which("npm") else ""
    probe = subprocess.run([node, "-e", "require('playwright')"], capture_output=True, env={**os.environ, "NODE_PATH": root})
    return probe.returncode == 0


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/blocked":
        return httpx.Response(403, text="captcha-delivery datadome challenge")
    return httpx.Response(200, text="Producto de prueba")


@pytest.mark.skipif(not _node_has_playwright(), reason="requiere Node y Playwright (npm i -g playwright)")
def test_panel_in_real_browser(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 443))])   # el destino de prueba "resuelve" a una IP pública
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
    settings = make_settings(tmp_path, rate_limit_requests=0, auth_failure_limit=0, credential_key=Fernet.generate_key().decode())
    server = uvicorn.Server(uvicorn.Config(create_app(settings, transport=httpx.MockTransport(_handler)), host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True); thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    try:
        root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        script = Path(__file__).parent.parent / "scripts" / "panel_e2e.js"
        run = subprocess.run(["node", str(script)], capture_output=True, text=True, timeout=180,
                             env={**os.environ, "NODE_PATH": root, "BASE": f"http://127.0.0.1:{port}", "ADMIN": "admin-secret", "EVAL": "eval-secret"})
        assert run.returncode == 0, run.stdout + run.stderr
    finally:
        server.should_exit = True; thread.join(timeout=5)
