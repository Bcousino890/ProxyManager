from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
import secrets
from typing import Literal
import uuid

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import Settings
from .fetch import DestinationRejected, fetch, guard_url
from .storage import SessionStore
from .cookies import CookieStore
from .proxies import ProxyStore
from .health import ProxyHealth, QueueFull
from .accounts import AccountError, Accounts, SlidingWindow
from .transport import PinnedProxyTransport
from .importer import import_proxy_text
from .challenges import ChallengeContext, ChallengeHandler, load_handler
from .authorization import AuthorizationError, ChallengeAuthorization
import asyncio
from .fetch import classify

STATIC = Path(__file__).parent / "static"
SESSION_COOKIE = "pm_session"
FORBIDDEN_HEADERS = {"host", "content-length", "connection", "transfer-encoding", "te", "upgrade", "proxy-authorization", "proxy-connection", "keep-alive", "x-forwarded-for", "x-real-ip"}


@dataclass
class Caller:
    owner: str
    user_id: str | None = None
    key: dict | None = None


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
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"] = "GET"
    headers: dict[str, str] | None = None
    body: str | None = None
    country: str | None = Field(default=None, max_length=2)
    session_id: str | None = None
    use_proxy: bool = False
    expected_text: str | None = Field(default=None, max_length=500)
    solve_challenges: bool = False


class Credentials(BaseModel):
    email: str
    password: str


class KeyCreate(BaseModel):
    name: str
    credit_limit: int | None = None


class KeyLimit(BaseModel):
    credit_limit: int | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class ProxyUpdate(BaseModel):
    kind: Literal["isp", "residential", "datacenter", "unknown"] | None = None
    country: str | None = Field(default=None, min_length=2, max_length=2)
    enabled: bool | None = None


class ProxyImport(BaseModel):
    provider: str
    text: str = Field(max_length=200_000)
    kind: Literal["isp", "residential", "datacenter", "unknown"] = "unknown"
    country: str = Field(default="ZZ", min_length=2, max_length=2)


class ChallengeAuthorize(BaseModel):
    authorized_by: str = Field(min_length=1, max_length=200)
    authorization_reference: str = Field(min_length=1, max_length=4000)


class CreditGrant(BaseModel):
    email: str
    credits: int
    plan: str | None = None


def create_app(settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None, challenge_handler: ChallengeHandler | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    store = SessionStore(settings.db_path)
    cookies = CookieStore(settings.db_path, settings.credential_key, store, settings.allowed_hosts, settings.allow_any_public_host)
    accounts = Accounts(settings.db_path, settings.free_credits)
    scrape_limit = SlidingWindow(settings.rate_limit_per_minute)
    login_limit = SlidingWindow(settings.login_attempts_per_minute)
    proxies = ProxyStore(settings.db_path, settings.credential_key)
    health_checks = ProxyHealth(proxies, settings, transport)
    handler = challenge_handler or load_handler(settings.challenge_handler)
    authorization = ChallengeAuthorization(settings.db_path)
    @asynccontextmanager
    async def lifespan(app):
        health_checks.recover()
        sweeper = None
        if settings.health_url and settings.health_interval_seconds > 0:
            async def loop():
                while True:
                    await health_checks.sweep()
                    await asyncio.sleep(settings.health_interval_seconds)
            sweeper = asyncio.create_task(loop())
        yield
        if sweeper:
            sweeper.cancel()

    app = FastAPI(title="ProxyManager API", version="0.2.0", lifespan=lifespan, docs_url="/api-reference", redoc_url=None)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        if not request.url.path.startswith(("/api-reference", "/openapi.json")):
            response.headers.setdefault("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'")
        return response

    def authenticated(x_api_key: str | None = Header(default=None)) -> str:
        if not x_api_key or not any(key and secrets.compare_digest(x_api_key, key) for key in (settings.evaluator_key, settings.admin_key)):
            raise HTTPException(status_code=401, detail="Clave API inválida")
        return store.owner_id(x_api_key)

    def caller(x_api_key: str | None = Header(default=None)) -> Caller:
        """Clave de cliente (facturada) o clave interna de evaluación/administración."""
        if x_api_key and x_api_key.startswith("pm_live_"):
            key = accounts.authenticate_key(x_api_key)
            if key:
                return Caller(owner=key["user_id"], user_id=key["user_id"], key=key)
        return Caller(owner=authenticated(x_api_key))

    def client_ip(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for", "")
        return forwarded.split(",")[-1].strip() if forwarded else (request.client.host if request.client else "?")

    def web_token(request: Request) -> str:
        return request.cookies.get(SESSION_COOKIE, "")

    def web_user(request: Request) -> dict:
        user = accounts.user_for_token(web_token(request)) if web_token(request) else None
        if user is None:
            raise HTTPException(401, "Sesión no iniciada")
        if request.method not in ("GET", "HEAD") and request.headers.get("x-pm-csrf") != "1":
            raise HTTPException(403, "Falta la cabecera X-PM-CSRF")
        return user

    def start_web_session(response: Response, token: str):
        response.set_cookie(SESSION_COOKIE, token, max_age=accounts.web_ttl, httponly=True, secure=settings.cookie_secure, samesite="lax", path="/")

    def administrator(x_api_key: str | None = Header(default=None)) -> str:
        if not x_api_key or not settings.admin_key or not secrets.compare_digest(x_api_key, settings.admin_key):
            raise HTTPException(status_code=403, detail="Se requiere clave de administración")
        return store.owner_id(x_api_key)

    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse("/app/")

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
    def create_session(who: Caller = Depends(caller)):
        return store.create(who.owner, settings.session_ttl_seconds)

    @app.get("/v1/sessions/{session_id}")
    def get_session(session_id: str, who: Caller = Depends(caller)):
        result = store.get(session_id, who.owner)
        if result is None:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        return result

    @app.delete("/v1/sessions/{session_id}", status_code=204)
    def delete_session(session_id: str, who: Caller = Depends(caller)):
        if not store.delete(session_id, who.owner):
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

    @app.patch("/v1/proxies/{proxy_id}", status_code=204)
    def update_proxy(proxy_id: str, body: ProxyUpdate, _: str = Depends(administrator)):
        if not proxies.update(proxy_id, body.kind, body.country, body.enabled):
            raise HTTPException(404, "Proxy no encontrado")

    @app.delete("/v1/proxies/{proxy_id}", status_code=204)
    def delete_proxy(proxy_id: str, _: str = Depends(administrator)):
        if not proxies.delete(proxy_id):
            raise HTTPException(404, "Proxy no encontrado")

    @app.post("/v1/proxies/import")
    def import_proxies(body: ProxyImport, _: str = Depends(administrator)):
        try:
            added = import_proxy_text(body.text, proxies, body.provider, body.kind, body.country.upper())
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return {"added": added, "total": len(proxies.list())}

    @app.post("/v1/proxies/{proxy_id}/checks", status_code=202)
    def check_proxy(proxy_id: str, request: ScrapeRequest, background: BackgroundTasks, _: str = Depends(administrator)):
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
        background.add_task(health_checks.run, job_id, request.url, connection)
        return {"job_id": job_id, "state": "queued"}

    @app.get("/v1/proxies/{proxy_id}/checks")
    def proxy_check_history(proxy_id: str, _: str = Depends(authenticated)):
        return health_checks.history(proxy_id)

    async def run_scrape(request: ScrapeRequest, owner: str, user_id: str | None, key: dict | None):
        if request.session_id and store.get(request.session_id, owner) is None:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        if request.session_id and not settings.credential_key:
            raise HTTPException(status_code=503, detail="Configura PROXYMANAGER_CREDENTIAL_KEY para usar sesiones HTTP")
        proxied = request.use_proxy or bool(request.country)
        cost = settings.credits_per_proxied_request if proxied else settings.credits_per_request
        if user_id:
            reason = accounts.check_funds({"user_id": user_id, **(key or {})}, cost)
            if reason:
                raise HTTPException(status_code=402, detail=reason)
        headers = request.headers or {}
        if len(headers) > 30 or sum(len(k) + len(v) for k, v in headers.items()) > 8192 or any("\r" in k + v or "\n" in k + v for k, v in headers.items()):
            raise HTTPException(status_code=422, detail="Cabeceras inválidas o demasiado grandes")
        headers = {k: v for k, v in headers.items() if k.lower() not in FORBIDDEN_HEADERS}
        body = request.body.encode() if request.body is not None else None
        if body is not None and len(body) > settings.max_response_bytes:
            raise HTTPException(status_code=413, detail="Cuerpo demasiado grande")
        tried: list[str] = []
        cookie_header = ""
        proxy_id = None
        result = None
        try:
            guard_url(request.url, settings)
            for _ in range(2 if proxied else 1):
                use_transport = transport
                if proxied:
                    proxy_id = proxies.choose(request.country, request.session_id, set(tried), settings.health_ttl_seconds)
                    if proxy_id is None:
                        if result is None:
                            raise HTTPException(status_code=422, detail="No hay proxies sanos disponibles para esa petición")
                        break
                    if transport is None:
                        use_transport = PinnedProxyTransport(health_checks.connection(proxy_id), guard_url(request.url, settings)[1])
                cookie_header = cookies.header(request.session_id, owner, request.url) if request.session_id else ""
                on_set_cookie = (lambda h: cookies.record(request.session_id, owner, request.url, h)) if request.session_id else None
                result = await fetch(request.url, settings, use_transport, cookie_header, on_set_cookie, request.method, headers, body, request.expected_text)
                if proxied and result.get("error"):
                    health_checks.record(proxy_id, False, "scrape")
                    tried.append(proxy_id)
                    continue
                break
        except DestinationRejected as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        if proxied and proxy_id and not result.get("error"):
            health_checks.record(proxy_id, True, "scrape")
        result["proxy_id"] = proxy_id if proxied else None
        if result.get("validation", {}).get("challenge_detected"):
            auth_enabled = handler is not None and authorization.status()["enabled"]
            info = {"detected": True, "handler": handler.name if handler else None, "handled": False, "resolved": False}
            if handler and request.solve_challenges and not auth_enabled:
                info["pending_authorization"] = True
            if handler and request.solve_challenges and auth_enabled:
                info["handled"] = True
                try:
                    resolution = await handler.handle(ChallengeContext(request.url, request.method, result.get("status_code"), result.get("headers", {}), result.get("html", ""), request.session_id, proxy_id, cookie_header))
                except Exception:
                    resolution = None
                    info["error"] = "handler_failed"
                if resolution and resolution.resolved:
                    html = resolution.html if resolution.html is not None else result.get("html", "")
                    status = resolution.status_code or result.get("status_code") or 0
                    if request.session_id and resolution.set_cookies:
                        cookies.record(request.session_id, owner, request.url, resolution.set_cookies)
                    result["html"], result["status_code"] = html, status
                    if resolution.headers is not None:
                        result["headers"] = resolution.headers
                    result["success"], result["validation"] = classify(html, status, settings, request.expected_text)
                    info["resolved"] = bool(result["success"])
                    if info["resolved"]:
                        cost += settings.credits_challenge_resolved
            result["challenge"] = info
        if user_id:
            from urllib.parse import urlsplit
            accounts.record_usage(user_id, (key or {}).get("id"), urlsplit(request.url).hostname or "", result.get("status_code"), bool(result.get("success")), cost,
                                  result.get("bytes_transferred", 0), result.get("duration_ms"), proxied)
        return {"request_id": "req_" + uuid.uuid4().hex, "session_id": request.session_id, "credits_charged": cost if (user_id and result.get("success")) else 0, **result}

    @app.post("/scrape")
    async def scrape(request: ScrapeRequest, who: Caller = Depends(caller)):
        if not scrape_limit.allow((who.key or {}).get("id") or who.owner):
            raise HTTPException(status_code=429, detail="Límite de solicitudes por minuto superado", headers={"Retry-After": "60"})
        return await run_scrape(request, who.owner, who.user_id, who.key)

    # --- consola de clientes (cookie de sesión web) -------------------
    @app.post("/v1/account/signup", status_code=201)
    def signup(body: Credentials, request: Request, response: Response):
        if not settings.signup_enabled:
            raise HTTPException(403, "El registro está desactivado")
        if not login_limit.allow("signup|" + client_ip(request)):
            raise HTTPException(429, "Demasiados intentos")
        try:
            user, first_key = accounts.signup(body.email, body.password)
        except AccountError as exc:
            raise HTTPException(422, str(exc)) from exc
        start_web_session(response, accounts.login(body.email, body.password))
        return {"user": user, "api_key": first_key}

    @app.post("/v1/account/login")
    def login(body: Credentials, request: Request, response: Response):
        if not login_limit.allow(f"login|{client_ip(request)}|{body.email.lower()}"):
            raise HTTPException(429, "Demasiados intentos; espera un minuto")
        token = accounts.login(body.email, body.password)
        if token is None:
            raise HTTPException(401, "Correo o contraseña incorrectos")
        start_web_session(response, token)
        return {"ok": True}

    @app.post("/v1/account/logout", status_code=204)
    def logout(request: Request, response: Response, _: dict = Depends(web_user)):
        accounts.logout(web_token(request))
        response.delete_cookie(SESSION_COOKIE, path="/")

    @app.get("/v1/account/me")
    def me(user: dict = Depends(web_user)):
        return {**user, "rate_limit_per_minute": settings.rate_limit_per_minute, "credits_per_request": settings.credits_per_request,
                "credits_per_proxied_request": settings.credits_per_proxied_request, "support_email": settings.support_email}

    @app.post("/v1/account/password", status_code=204)
    def change_password(body: PasswordChange, request: Request, user: dict = Depends(web_user)):
        try:
            accounts.change_password(user["id"], body.current_password, body.new_password, web_token(request))
        except AccountError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/v1/account/keys")
    def list_keys(user: dict = Depends(web_user)):
        return accounts.list_keys(user["id"])

    @app.post("/v1/account/keys", status_code=201)
    def create_key(body: KeyCreate, user: dict = Depends(web_user)):
        try:
            return accounts.create_key(user["id"], body.name, body.credit_limit)
        except AccountError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.patch("/v1/account/keys/{key_id}", status_code=204)
    def update_key(key_id: str, body: KeyLimit, user: dict = Depends(web_user)):
        try:
            found = accounts.set_key_limit(user["id"], key_id, body.credit_limit)
        except AccountError as exc:
            raise HTTPException(422, str(exc)) from exc
        if not found:
            raise HTTPException(404, "Clave no encontrada")

    @app.delete("/v1/account/keys/{key_id}", status_code=204)
    def revoke_key(key_id: str, user: dict = Depends(web_user)):
        if not accounts.revoke_key(user["id"], key_id):
            raise HTTPException(404, "Clave no encontrada")

    @app.get("/v1/account/usage")
    def usage(days: int = 30, user: dict = Depends(web_user)):
        return accounts.usage_summary(user["id"], max(1, min(days, 90)))

    @app.post("/v1/account/playground")
    async def playground(request: ScrapeRequest, user: dict = Depends(web_user)):
        if not scrape_limit.allow("pg|" + user["id"]):
            raise HTTPException(429, "Límite de solicitudes por minuto superado")
        return await run_scrape(request, user["id"], user["id"], None)

    # --- administración de clientes (clave de administración) ----------
    @app.get("/v1/admin/challenge-handler")
    def challenge_handler_status(_: str = Depends(administrator)):
        return {"configured": handler is not None, "handler_name": handler.name if handler else None,
                **authorization.status(), "log": authorization.log(20)}

    @app.post("/v1/admin/challenge-handler/enable")
    def enable_challenge_handler(body: ChallengeAuthorize, _: str = Depends(administrator)):
        if handler is None:
            raise HTTPException(409, "No hay ningún manejador de desafíos configurado (PROXYMANAGER_CHALLENGE_HANDLER vacío)")
        try:
            return authorization.enable(body.authorized_by, body.authorization_reference)
        except AuthorizationError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.post("/v1/admin/challenge-handler/disable")
    def disable_challenge_handler(_: str = Depends(administrator)):
        return authorization.disable()

    @app.get("/v1/admin/stats")
    def admin_stats(_: str = Depends(administrator)):
        return accounts.stats()

    @app.get("/v1/admin/users")
    def admin_users(_: str = Depends(administrator)):
        return accounts.list_users()

    @app.post("/v1/admin/credits")
    def admin_credits(body: CreditGrant, _: str = Depends(administrator)):
        try:
            return accounts.grant_credits(body.email, body.credits, body.plan)
        except LookupError as exc:
            raise HTTPException(404, "Usuario no encontrado") from exc

    app.mount("/docs", StaticFiles(directory=STATIC / "docs", html=True), name="docs")
    app.mount("/admin", StaticFiles(directory=STATIC / "admin", html=True), name="admin")
    app.mount("/app", StaticFiles(directory=STATIC / "app", html=True), name="console")

    return app


app = create_app()
