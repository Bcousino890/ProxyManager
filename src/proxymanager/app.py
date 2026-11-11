import secrets
from typing import Literal
import uuid

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from .config import Settings
from .fetch import DestinationRejected, fetch
from .storage import SessionStore
from .proxies import ProxyStore


class ProxyCreate(BaseModel):
    provider: str
    host: str
    port: int
    kind: Literal["isp", "residential", "datacenter", "unknown"]
    country: str
    username: str | None = None
    password: str | None = None


class ScrapeRequest(BaseModel):
    url: str
    country: str | None = None
    session_id: str | None = None


def create_app(settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    store = SessionStore(settings.db_path)
    proxies = ProxyStore(settings.db_path, settings.credential_key)
    app = FastAPI(title="ProxyManager", version="0.1.0")

    def authenticated(x_api_key: str | None = Header(default=None)) -> str:
        if not x_api_key or not any(key and secrets.compare_digest(x_api_key, key) for key in (settings.evaluator_key, settings.admin_key)):
            raise HTTPException(status_code=401, detail="Clave API inválida")
        return store.owner_id(x_api_key)

    def administrator(x_api_key: str | None = Header(default=None)) -> str:
        if not x_api_key or not settings.admin_key or not secrets.compare_digest(x_api_key, settings.admin_key):
            raise HTTPException(status_code=403, detail="Se requiere clave de administración")
        return store.owner_id(x_api_key)

    @app.get("/health")
    def health():
        return {"service": "ProxyManager", "status": "ok"}

    @app.get("/ready")
    def ready():
        return {"ready": bool(settings.evaluator_key or settings.admin_key)}

    @app.get("/v1/system")
    def system(_: str = Depends(authenticated)):
        return {"service": "ProxyManager", "allowed_hosts": list(settings.allowed_hosts), "monthly_budget_usd": settings.monthly_budget_usd}

    @app.post("/v1/sessions", status_code=201)
    def create_session(owner: str = Depends(authenticated)):
        return store.create(owner, settings.session_ttl_seconds)

    @app.get("/v1/sessions/{session_id}")
    def get_session(session_id: str, owner: str = Depends(authenticated)):
        result = store.get(session_id, owner)
        if result is None:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        return result

    @app.delete("/v1/sessions/{session_id}", status_code=204)
    def delete_session(session_id: str, owner: str = Depends(authenticated)):
        if not store.delete(session_id, owner):
            raise HTTPException(status_code=404, detail="Sesión no encontrada")

    @app.get("/v1/proxies")
    def list_proxies(_: str = Depends(authenticated)):
        return proxies.list()

    @app.post("/v1/proxies", status_code=201)
    def create_proxy(request: ProxyCreate, _: str = Depends(administrator)):
        if not request.provider.strip() or not request.host.strip() or not request.country.strip() or not 1 <= request.port <= 65535:
            raise HTTPException(status_code=422, detail="Datos de proxy inválidos")
        try:
            return proxies.create(request.provider, request.host, request.port, request.kind, request.country, request.username, request.password)
        except ValueError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post("/scrape")
    async def scrape(request: ScrapeRequest, owner: str = Depends(authenticated)):
        if request.session_id and store.get(request.session_id, owner) is None:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        try:
            result = await fetch(request.url, settings, transport)
        except DestinationRejected as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {"request_id": "req_" + uuid.uuid4().hex, "session_id": request.session_id, **result}

    return app


app = create_app()
