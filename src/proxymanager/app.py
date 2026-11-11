import asyncio
from contextlib import asynccontextmanager
import secrets
from typing import Literal
import uuid

import httpx
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from .config import Settings
from .fetch import DestinationRejected, fetch, guard_url
from .storage import SessionStore
from .cookies import CookieStore
from .proxies import ProxyStore
from .selection import NoHealthyProxy, ProxyBusy, ProxyMetrics
from .transport import PinnedProxyTransport
from .bench import BenchConflict, BenchRunner, BenchStore
from .expenses import ExpenseStore
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


class BenchCreate(BaseModel):
    url: str
    requests: int
    concurrency: int = 1
    rps: float | None = None
    use_proxy: bool = True
    country: str | None = None


class ExpenseCreate(BaseModel):
    concept: str
    amount_usd: float


class ScrapeRequest(BaseModel):
    url: str
    country: str | None = None
    session_id: str | None = None
    use_proxy: bool = False


def create_app(settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    store = SessionStore(settings.db_path)
    cookies = CookieStore(settings.db_path, settings.credential_key, store, settings.allowed_hosts)
    proxies = ProxyStore(settings.db_path, settings.credential_key)
    limiter = RateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)
    audit = AuditLog(settings.db_path)
    failures = RateLimiter(settings.auth_failure_limit, settings.rate_limit_window_seconds)  # intentos fallidos por IP
    metrics = ProxyMetrics(settings.db_path, settings.proxy_window_seconds, settings.proxy_min_success_rate, settings.proxy_max_inflight)
    bench = BenchStore(settings.db_path)
    expenses = ExpenseStore(settings.db_path)
    health_checks = ProxyHealth(proxies, settings, transport, metrics)
    bench_runner = BenchRunner(bench, metrics, health_checks, settings, transport)

    @asynccontextmanager
    async def lifespan(app):
        if settings.strict and (found := settings.problems()):
            raise RuntimeError("Configuración insegura: " + "; ".join(found))
        audit.purge(settings.audit_retention_days)
        bench.recover()
        workers = [asyncio.create_task(health_checks.worker()) for _ in range(settings.health_concurrency)] + [asyncio.create_task(bench_runner.worker())]
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
            client = request.client.host if request.client else "?"
            wait = failures.blocked(client)
            if wait:
                raise HTTPException(status_code=429, detail="Demasiados intentos fallidos", headers={"Retry-After": str(int(wait) + 1)})
            role = role_of(x_api_key)
            if role is None:
                failures.record(client)
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

    panel_dir = Path(__file__).parent / "panel"
    panel_headers = {"Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
                     "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", "Cache-Control": "no-store"}

    @app.get("/panel", include_in_schema=False)
    def panel_page():
        return FileResponse(panel_dir / "index.html", media_type="text/html", headers=panel_headers)

    @app.get("/panel/style.css", include_in_schema=False)
    def panel_style():
        return FileResponse(panel_dir / "style.css", media_type="text/css", headers=panel_headers)

    @app.get("/panel/app.js", include_in_schema=False)
    def panel_script():
        return FileResponse(panel_dir / "app.js", media_type="text/javascript", headers=panel_headers)

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

    @app.get("/v1/sessions")
    def list_sessions(owner: str = Depends(require("sessions"))):
        return store.list_active(owner)

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
        metrics.forget_session(session_id)

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

    @app.post("/v1/benchmarks", status_code=202)
    def create_benchmark(request: BenchCreate, owner: str = Depends(require("bench:write"))):
        if not 1 <= request.requests <= settings.bench_max_requests or not 1 <= request.concurrency <= settings.bench_max_concurrency or (request.rps is not None and request.rps <= 0):
            raise HTTPException(422, f"Límites: 1-{settings.bench_max_requests} solicitudes, concurrencia 1-{settings.bench_max_concurrency}, rps > 0")
        try:
            guard_url(request.url, settings)
            params = {**request.model_dump(), "url": request.url.split("?")[0].split("#")[0]}
            return {"id": bench.create(owner, params), "state": "queued"}
        except DestinationRejected as exc:
            raise HTTPException(422, str(exc)) from exc
        except BenchConflict as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get("/v1/benchmarks")
    def list_benchmarks(owner: str = Depends(require("bench:read"))):
        return bench.recent(owner)

    @app.get("/v1/expenses")
    def list_expenses(_: str = Depends(require("expenses:read"))):
        return expenses.month(settings.monthly_budget_usd)

    @app.post("/v1/expenses", status_code=201)
    def add_expense(request: ExpenseCreate, _: str = Depends(require("expenses:write"))):
        try:
            return expenses.add(request.concept, request.amount_usd)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/v1/overview")
    def overview(_: str = Depends(require("proxies:read"))):
        items = [{**p, "stats": metrics.stats(p["id"])} for p in proxies.list()]
        healthy = sum(1 for p in items if p["stats"]["healthy"])
        return {"proxies": items, "healthy": healthy, "total": len(items), "allowed_hosts": list(settings.allowed_hosts), "monthly_budget_usd": settings.monthly_budget_usd}

    @app.get("/v1/benchmarks/{run_id}")
    def get_benchmark(run_id: str, owner: str = Depends(require("bench:read"))):
        found = bench.get(run_id, owner)
        if found is None:
            raise HTTPException(404, "Benchmark no encontrado")
        return found

    @app.post("/v1/benchmarks/{run_id}/cancel", status_code=202)
    def cancel_benchmark(run_id: str, owner: str = Depends(require("bench:write"))):
        if not bench.cancel(run_id, owner):
            raise HTTPException(404, "Benchmark no encontrado o ya terminado")
        return {"id": run_id, "cancel_requested": True}

    @app.get("/v1/proxies/{proxy_id}/stats")
    def proxy_stats(proxy_id: str, _: str = Depends(require("proxies:read"))):
        return metrics.stats(proxy_id)

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
            proxy_id, route = None, transport
            if request.use_proxy:
                _, hostname = guard_url(request.url, settings)
                try:
                    proxy_id = metrics.choose(request.country, request.session_id, acquire=True)
                except NoHealthyProxy as exc:
                    raise HTTPException(status_code=503, detail=str(exc)) from exc
                except ProxyBusy as exc:
                    raise HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": "1"}) from exc
            try:
                if proxy_id:
                    route = transport or PinnedProxyTransport(health_checks.connection(proxy_id), hostname)
                result = await fetch(request.url, settings, route, cookie_header, on_set_cookie)
            finally:
                if proxy_id:
                    metrics.release(proxy_id)
            if proxy_id:
                metrics.record(proxy_id, "scrape", result.get("status_code") is not None, result.get("duration_ms"))
        except DestinationRejected as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {"request_id": "req_" + uuid.uuid4().hex, "session_id": request.session_id, "proxy_id": proxy_id, **result}

    return app


app = create_app()
