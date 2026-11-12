import asyncio
from contextlib import asynccontextmanager
import secrets
from typing import Literal
import uuid

import httpx
from pathlib import Path
from urllib.parse import urlsplit

from fastapi.responses import FileResponse
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from .config import SCOPES, Settings
from .fetch import DestinationRejected, fetch, guard_url
from .storage import SessionStore
from .cookies import CookieStore
from .proxies import ProxyStore
from .selection import NoHealthyProxy, ProxyBusy, ProxyMetrics
from .transport import PinnedProxyTransport
from .bench import BenchConflict, BenchRunner, BenchStore
from .expenses import ExpenseStore
from .keys import ApiKeyStore
from .importer import import_proxy_text
from .usage import UsageStore
from .limits import AuditLog, RateLimiter
from .health import ProxyHealth, QueueFull
from .alerts import AlertService


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


class ProxyImport(BaseModel):
    provider: str
    text: str


class KeyCreate(BaseModel):
    name: str
    scopes: list[str]
    expires_days: float | None = None


class ExpenseCreate(BaseModel):
    concept: str
    amount_usd: float


class ScrapeRequest(BaseModel):
    url: str
    country: str | None = None
    session_id: str | None = None
    use_proxy: bool = False


def create_app(settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None, alert_transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
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
    api_keys = ApiKeyStore(settings.db_path, SCOPES)
    usage = UsageStore(settings.db_path)
    alerts = AlertService(settings.alert_webhook_url, alert_transport)
    health_checks = ProxyHealth(proxies, settings, transport, metrics, alerts)
    bench_runner = BenchRunner(bench, metrics, health_checks, settings, transport, usage)

    @asynccontextmanager
    async def lifespan(app):
        if settings.strict and (found := settings.problems()):
            raise RuntimeError("Configuración insegura: " + "; ".join(found))
        audit.purge(settings.audit_retention_days)
        metrics.purge_events()
        usage.purge()
        bench.recover()
        workers = [asyncio.create_task(health_checks.worker()) for _ in range(settings.health_concurrency)] + [asyncio.create_task(bench_runner.worker())]
        try:
            yield
        finally:
            for task in workers:
                task.cancel()
            await asyncio.gather(*workers, return_exceptions=True)

    docs = {} if not settings.strict else {"docs_url": None, "redoc_url": None, "openapi_url": None}   # en estricto no se publica el esquema
    app = FastAPI(title="ProxyManager", version="0.1.0", lifespan=lifespan, **docs)

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
            granted = settings.scopes_for(role) if role else (api_keys.lookup(x_api_key) if x_api_key else None)
            if granted is None:
                failures.record(client)
                raise HTTPException(status_code=401, detail="Clave API inválida")
            if scope not in granted:
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

    panel_types = {".css": "text/css", ".js": "text/javascript"}
    panel_files = {f.name for f in panel_dir.iterdir() if f.is_file() and f.suffix in panel_types}

    @app.get("/panel/{filename}", include_in_schema=False)
    def panel_asset(filename: str):
        if filename not in panel_files:  # lista cerrada: sin rutas arbitrarias
            raise HTTPException(404, "No encontrado")
        return FileResponse(panel_dir / filename, media_type=panel_types[Path(filename).suffix], headers=panel_headers)

    @app.get("/health")
    def health():
        return {"service": "ProxyManager", "status": "ok"}

    @app.get("/ready")
    def ready():
        return {"ready": bool(settings.evaluator_key or settings.admin_key)}

    @app.get("/v1/system")
    def system(_: str = Depends(require("system:read"))):
        return {"service": "ProxyManager", "allowed_hosts": list(settings.allowed_hosts), "monthly_budget_usd": settings.monthly_budget_usd,
                "timeout_seconds": settings.timeout_seconds, "max_response_bytes": settings.max_response_bytes, "proxy_max_inflight": settings.proxy_max_inflight, "scrape_proxy_attempts": settings.scrape_proxy_attempts}

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

    @app.post("/v1/proxies/import", status_code=201)
    def import_proxies(request: ProxyImport, _: str = Depends(require("proxies:write"))):
        if len(request.text) > 65_536:
            raise HTTPException(413, "Lote demasiado grande")
        try:
            before = len(proxies.list())
            added = import_proxy_text(request.text, proxies, request.provider)
            return {"added": added, "duplicates_skipped": max(len([l for l in request.text.splitlines() if l.strip()]) - added, 0), "total": before + added}
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

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

    @app.post("/v1/keys", status_code=201)
    def create_key(request: KeyCreate, _: str = Depends(require("keys:manage"))):
        try:
            return api_keys.create(request.name, request.scopes, request.expires_days)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/v1/keys")
    def list_keys(_: str = Depends(require("keys:manage"))):
        return api_keys.list()

    @app.delete("/v1/keys/{key_id}", status_code=204)
    def revoke_key(key_id: str, _: str = Depends(require("keys:manage"))):
        if not api_keys.revoke(key_id):
            raise HTTPException(404, "Clave no encontrada o ya revocada")

    @app.get("/v1/expenses")
    def list_expenses(_: str = Depends(require("expenses:read"))):
        return expenses.month(settings.monthly_budget_usd)

    @app.post("/v1/expenses", status_code=201)
    async def add_expense(request: ExpenseCreate, _: str = Depends(require("expenses:write"))):
        try:
            before = expenses.month(settings.monthly_budget_usd)["spent_usd"] if settings.alert_webhook_url else 0
            item = expenses.add(request.concept, request.amount_usd)
            if settings.alert_webhook_url:
                after = expenses.month(settings.monthly_budget_usd)
                await alerts.budget_crossed(after["month"], before, after["spent_usd"], settings.monthly_budget_usd)
            return item
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/v1/usage")
    def usage_summary(days: int = 14, _: str = Depends(require("usage:read"))):
        if not 1 <= days <= 90:
            raise HTTPException(422, "days debe estar entre 1 y 90")
        return usage.summary(days)

    @app.get("/v1/overview")
    def overview(_: str = Depends(require("proxies:read"))):
        traffic = metrics.traffic_month()
        delivery = usage.delivery_by_proxy()
        empty = {"requests": 0, "success": 0, "blocked": 0, "transport_error": 0, "other": 0}
        items = [{**p, "stats": metrics.stats(p["id"]), "traffic_month_bytes": traffic.get(p["id"], 0), "delivery_24h": delivery.get(p["id"], empty)} for p in proxies.list()]
        healthy = sum(1 for p in items if p["stats"]["healthy"])
        total_bytes = sum(p["traffic_month_bytes"] for p in items)
        return {"concurrency": metrics.inflight(), "traffic_month_bytes": total_bytes, "estimated_proxy_cost_usd": round(total_bytes / 1e9 * settings.proxy_cost_per_gb_usd, 4) if settings.proxy_cost_per_gb_usd else None,
                "proxies": items, "healthy": healthy, "total": len(items), "allowed_hosts": list(settings.allowed_hosts), "monthly_budget_usd": settings.monthly_budget_usd}

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
            hostname = guard_url(request.url, settings)[1] if request.use_proxy else None
            tried: set[str] = set()
            last_proxy = None
            for _ in range(settings.scrape_proxy_attempts if request.use_proxy else 1):
                proxy_id, route = None, transport
                if request.use_proxy:
                    try:
                        proxy_id = metrics.choose(request.country, request.session_id, acquire=True, exclude=frozenset(tried))
                    except NoHealthyProxy as exc:
                        if tried:
                            break  # sin alternativas: se devuelve el último fallo
                        raise HTTPException(status_code=503, detail=str(exc)) from exc
                    except ProxyBusy as exc:
                        if tried:
                            break
                        raise HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": "1"}) from exc
                    tried.add(proxy_id)
                try:
                    if proxy_id:
                        route = transport or PinnedProxyTransport(health_checks.connection(proxy_id), hostname)
                    result = await fetch(request.url, settings, route, cookie_header, on_set_cookie)
                finally:
                    if proxy_id:
                        metrics.release(proxy_id)
                last_proxy = proxy_id
                if proxy_id:
                    await alerts.record_proxy(metrics, proxy_id, "scrape", result.get("status_code") is not None, result.get("duration_ms"), result.get("bytes_transferred", 0))
                if proxy_id is None or result.get("status_code") is not None:
                    break  # hubo respuesta HTTP (aunque sea de error del sitio): no se reintenta; solo fallos de transporte
        except DestinationRejected as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        proxy_id = last_proxy if request.use_proxy else None  # el proxy del último intento, también si se agotaron las alternativas
        usage.record(urlsplit(request.url).hostname or "", "scrape", proxy_id, result)
        return {"request_id": "req_" + uuid.uuid4().hex, "session_id": request.session_id, "proxy_id": proxy_id, "attempts": len(tried) or 1, **result}

    return app


app = create_app()
