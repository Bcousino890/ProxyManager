import asyncio
import socket

import httpx

from lab_server import local_lab
from proxymanager.config import Settings
from proxymanager.fetch import fetch


class LoopbackTransport(httpx.AsyncBaseTransport):
    """Map the guarded fake public IP to the local-only fixture server."""

    def __init__(self, port):
        self.port = port
        self.inner = httpx.AsyncHTTPTransport()

    async def handle_async_request(self, request):
        request.url = httpx.URL(f"http://127.0.0.1:{self.port}{request.url.raw_path.decode()}")
        return await self.inner.handle_async_request(request)

    async def aclose(self):
        await self.inner.aclose()


def test_local_lab_exercises_fetch_classifier_and_transport(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))])
    settings = Settings(db_path=str(tmp_path / "lab.db"), allowed_hosts=("lab.example",), expected_text="expected content", timeout_seconds=0.03)

    async def run(port):
        async def get(path):
            return await fetch(f"https://lab.example{path}", settings, LoopbackTransport(port))

        content = await get("/content")
        challenge = await get("/captcha")
        redirect = await get("/redirect")
        slow = await get("/slow")
        cut = await get("/cut")
        assert content["success"] is True
        assert challenge["success"] is False and challenge["validation"]["challenge_detected"] is True
        assert redirect["status_code"] == 302 and redirect["success"] is False
        assert slow["error"]["type"] == "transport_error"
        assert cut["error"]["type"] == "transport_error"

    with local_lab() as port:
        asyncio.run(run(port))
