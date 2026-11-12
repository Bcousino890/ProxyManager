import os
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest
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


@pytest.mark.skipif(not _node_has_playwright(), reason="requiere Node y Playwright (npm i -g playwright)")
def test_panel_in_real_browser(tmp_path):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(make_settings(tmp_path, rate_limit_requests=0, auth_failure_limit=0, credential_key=Fernet.generate_key().decode())), host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True); thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    try:
        root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        script = Path(__file__).parent.parent / "scripts" / "panel_e2e.js"
        run = subprocess.run(["node", str(script)], capture_output=True, text=True, timeout=90,
                             env={**os.environ, "NODE_PATH": root, "BASE": f"http://127.0.0.1:{port}", "ADMIN": "admin-secret", "EVAL": "eval-secret"})
        assert run.returncode == 0, run.stdout + run.stderr
    finally:
        server.should_exit = True; thread.join(timeout=5)
