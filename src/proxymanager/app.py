import secrets
import uuid

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from .config import Settings
from .fetch import DestinationRejected, fetch
from .storage import SessionStore


class ScrapeRequest(BaseModel):
    url: str
    country: str | None = None
    session_id: str | None = None


def create_app(settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    store = SessionStore(settings.db_path)
    app = FastAPI(title="ProxyManager", version="0.1.0")

    def authenticated(x_api_key: str | None = Header(default=None)) -> str:
        if not x_api_key or not any(key and secrets.compare_digest(x_api_key, key) for key in (settings.evaluator_key, settings.admin_key)):
            raise HTTPException(status_code=401, detail="Clave API inválida")
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
