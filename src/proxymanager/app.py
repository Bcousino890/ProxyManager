import asyncio
from contextlib import asynccontextmanager
import secrets
from typing import Literal
import uuid

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from .config import Settings
from .fetch import DestinationRejected, fetch, guard_url
from .storage import SessionStore
from .cookies import CookieStore
from .proxies import ProxyStore
from .limits import AuditLog, RateLimiter
from .health import ProxyHealth, QueueFull


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
    cookies = CookieStore(settings.db_path, settings.credential_key, store, settings.allowed_hosts)
    proxies = ProxyStore(settings.db_path, settings.credential_key)
    limiter = RateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)
    audit = AuditLog(settings.db_path)
    health_checks = ProxyHealth(proxies, settings, transport)
    @asynccontextmanager
    async def lifespan(app):
        if settings.strict and (found := settings.problems()):
            raise RuntimeError("Configuración insegura: " + "; ".join(found))
        audit.purge(settings.audit_retention_days)
        workers = [asyncio.create_task(health_checks.worker()) for _ in range(settings.health_concurrency)]
        try:
            yield
        finally:
            for task in workers:
                task.cancel()
            await asyncio.gather(*workers, return_exceptions=True)

    app = FastAPI(title="ProxyManager", version="0.1.0", lifespan=lifespan)

    def throttle(owner: str, request: Request) -> str:
        retry = limiter.check(owner)
        if retry:
            raise HTTPException(status_code=429, detail="Límite de solicitudes excedido", headers={"Retry-After": str(int(retry) + 1)})
        request.state.owner = owner
        return owner

    def role_of(api_key: str | None) -> str | None:
        if api_key and settings.admin_key and secrets.compare_digest(api_key, settings.admin_key):
            return "admin"
        if api_key and settings.evaluator_key and secrets.compare_digest(api_key, settings.evaluator_key):
            return "evaluator"
        return None

    def require(scope: str):
        def dependency(request: Request, x_api_key: str | None = Header(default=None)) -> str:
            role = role_of(x_api_key)
            if role is None:
                raise HTTPException(status_code=401, detail="Clave API inválida")
            if scope not in settings.scopes_for(role):
                raise HTTPException(status_code=403, detail=f"La clave no tiene el alcance {scope}")
            return throttle(store.owner_id(x_api_key), request)
        return dependency

    @app.middleware("http")
    async def audit_requests(request: Request, call_next):
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            route = request.scope.get("route")
            audit.record(getattr(request.state, "owner", None), request.method, getattr(route, "path", "(sin ruta)"), status)

    @app.get("/health")
    def health():
        return {"service": "ProxyManager", "status": "ok"}

    @app.get("/ready")
    def ready():
        return {"ready": bool(settings.evaluator_key or settings.admin_key)}

    @app.get("/v1/system")
    def system(_: str = Depends(require("system:read"))):
        return {"service": "ProxyManager", "allowed_hosts": list(settings.allowed_hosts), "monthly_budget_usd": settings.monthly_budget_usd}

    @app.post("/v1/sessions", status_code=201)
    def create_session(owner: str = Depends(require("sessions"))):
        return store.create(owner, settings.session_ttl_seconds)

    @app.get("/v1/audit")
    def audit_events(limit: int = 100, _: str = Depends(require("audit:read"))):
        return audit.recent(limit)

    @app.get("/v1/sessions/{session_id}")
    def get_session(session_id: str, owner: str = Depends(require("sessions"))):
        result = store.get(session_id, owner)
        if result is None:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        return result

    @app.delete("/v1/sessions/{session_id}", status_code=204)
    def delete_session(session_id: str, owner: str = Depends(require("sessions"))):
        if not store.delete(session_id, owner):
            raise HTTPException(status_code=404, detail="Sesión no encontrada")

    @app.get("/v1/proxies")
    def list_proxies(_: str = Depends(require("proxies:read"))):
        return proxies.list()

    @app.post("/v1/proxies", status_code=201)
    def create_proxy(request: ProxyCreate, _: str = Depends(require("proxies:write"))):
        if not request.provider.strip() or not request.host.strip() or not request.country.strip() or not 1 <= request.port <= 65535:
            raise HTTPException(status_code=422, detail="Datos de proxy inválidos")
        try:
            return proxies.create(request.provider, request.host, request.port, request.kind, request.country, request.username, request.password)
        except ValueError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post("/v1/proxies/{proxy_id}/checks", status_code=202)
    def check_proxy(proxy_id: str, request: ScrapeRequest, _: str = Depends(require("checks:write"))):
        try:
            guard_url(request.url, settings)
            connection = health_checks.connection(proxy_id)
            job_id = health_checks.queue(proxy_id, request.url)
        except QueueFull as exc:
            raise HTTPException(429, "Cola de comprobaciones llena") from exc
        except LookupError as exc:
            raise HTTPException(404, "Proxy no encontrado") from exc
        except ValueError as exc:
            raise HTTPException(422, "Destino, configuración o capacidad de cola inválidos") from exc
        return {"job_id": job_id, "state": "queued"}

    @app.get("/v1/proxies/{proxy_id}/checks")
    def proxy_check_history(proxy_id: str, _: str = Depends(require("proxies:read"))):
        return health_checks.history(proxy_id)

    @app.post("/scrape")
    async def scrape(request: ScrapeRequest, owner: str = Depends(require("scrape"))):
        if request.session_id and store.get(request.session_id, owner) is None:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        if request.session_id and not settings.credential_key:
            raise HTTPException(status_code=503, detail="Configura PROXYMANAGER_CREDENTIAL_KEY para usar sesiones HTTP")
        try:
            cookie_header = cookies.header(request.session_id, owner, request.url) if request.session_id else ""
            on_set_cookie = (lambda headers: cookies.record(request.session_id, owner, request.url, headers)) if request.session_id else None
            result = await fetch(request.url, settings, transport, cookie_header, on_set_cookie)
        except DestinationRejected as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {"request_id": "req_" + uuid.uuid4().hex, "session_id": request.session_id, **result}

    return app


app = create_app()
