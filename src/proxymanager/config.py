from dataclasses import dataclass
import os
from urllib.parse import urlsplit

from cryptography.fernet import Fernet


SCOPES = ("usage:read", "keys:manage", "expenses:read", "expenses:write", "bench:read", "bench:write", "system:read", "sessions", "scrape", "proxies:read", "proxies:write", "checks:write", "audit:read")


@dataclass(frozen=True)
class Settings:
    db_path: str = "proxymanager.db"
    evaluator_key: str = ""
    credential_key: str = ""
    admin_key: str = ""
    allowed_hosts: tuple[str, ...] = ()
    expected_text: str = ""
    session_ttl_seconds: int = 3600
    timeout_seconds: float = 15.0
    max_response_bytes: int = 1_000_000
    health_concurrency: int = 2
    health_queue_limit: int = 20
    health_max_attempts: int = 3
    health_lease_seconds: float = 120.0
    health_poll_seconds: float = 0.2
    monthly_budget_usd: float = 25.0
    rate_limit_requests: int = 60
    audit_retention_days: float = 30.0
    auth_failure_limit: int = 10
    proxy_window_seconds: float = 3600.0
    proxy_min_success_rate: float = 0.5
    proxy_max_inflight: int = 5
    scrape_proxy_attempts: int = 2
    proxy_cost_per_gb_usd: float = 0.0
    bench_max_requests: int = 1000
    bench_max_concurrency: int = 10
    bench_max_bytes: int = 50_000_000
    evaluator_scopes: tuple[str, ...] = ("system:read", "sessions", "scrape", "proxies:read", "usage:read")
    strict: bool = False
    rate_limit_window_seconds: float = 60.0
    alert_webhook_url: str = ""

    def __post_init__(self):
        if min(self.health_max_attempts, self.health_lease_seconds + 1, self.health_poll_seconds, self.health_concurrency, self.health_queue_limit, self.session_ttl_seconds, self.timeout_seconds, self.max_response_bytes) <= 0 or self.audit_retention_days <= 0 or self.auth_failure_limit < 0 or self.proxy_window_seconds <= 0 or self.proxy_max_inflight <= 0 or self.scrape_proxy_attempts < 1 or self.proxy_cost_per_gb_usd < 0 or min(self.bench_max_requests, self.bench_max_concurrency, self.bench_max_bytes) <= 0 or not 0 <= self.proxy_min_success_rate <= 1 or self.rate_limit_requests < 0 or self.rate_limit_window_seconds <= 0:
            raise ValueError("Los límites deben ser positivos")
        if self.alert_webhook_url:
            parts = urlsplit(self.alert_webhook_url)
            if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.fragment:
                raise ValueError("PROXYMANAGER_ALERT_WEBHOOK_URL debe ser HTTPS sin credenciales ni fragmento")

    def scopes_for(self, role: str) -> frozenset[str]:
        return frozenset(SCOPES) if role == "admin" else frozenset(self.evaluator_scopes)

    def problems(self) -> list[str]:
        """Fallos de configuración que impiden servir de forma segura."""
        found = []
        for name, key in (("EVALUATOR_KEY", self.evaluator_key), ("ADMIN_KEY", self.admin_key)):
            if len(key) < 16:
                found.append(f"PROXYMANAGER_{name} falta o tiene menos de 16 caracteres")
        if "keys:manage" in self.evaluator_scopes:
            found.append("La clave de evaluación no puede tener keys:manage")
        if unknown := set(self.evaluator_scopes) - set(SCOPES):
            found.append("Alcances desconocidos: " + ", ".join(sorted(unknown)))
        if self.evaluator_key and self.evaluator_key == self.admin_key:
            found.append("Las claves de evaluación y administración deben ser distintas")
        try:
            Fernet(self.credential_key.encode())
        except Exception:
            found.append("PROXYMANAGER_CREDENTIAL_KEY falta o no es una clave Fernet válida")
        if not self.allowed_hosts:
            found.append("PROXYMANAGER_ALLOWED_HOSTS está vacío")
        if self.rate_limit_requests == 0:
            found.append("El rate limiting está desactivado")
        return found

    @classmethod
    def from_env(cls) -> "Settings":
        hosts = tuple(host.strip().lower() for host in os.getenv("PROXYMANAGER_ALLOWED_HOSTS", "").split(",") if host.strip())
        return cls(
            health_concurrency=int(os.getenv("PROXYMANAGER_HEALTH_CONCURRENCY", "2")),
            health_max_attempts=int(os.getenv("PROXYMANAGER_HEALTH_MAX_ATTEMPTS", "3")),
            health_lease_seconds=float(os.getenv("PROXYMANAGER_HEALTH_LEASE_SECONDS", "120")),
            health_poll_seconds=float(os.getenv("PROXYMANAGER_HEALTH_POLL_SECONDS", "0.2")),
            health_queue_limit=int(os.getenv("PROXYMANAGER_HEALTH_QUEUE_LIMIT", "20")),
            db_path=os.getenv("PROXYMANAGER_DB_PATH", "proxymanager.db"),
            evaluator_key=os.getenv("PROXYMANAGER_EVALUATOR_KEY", ""),
            credential_key=os.getenv("PROXYMANAGER_CREDENTIAL_KEY", ""),
            admin_key=os.getenv("PROXYMANAGER_ADMIN_KEY", ""),
            allowed_hosts=hosts,
            expected_text=os.getenv("PROXYMANAGER_EXPECTED_TEXT", ""),
            session_ttl_seconds=int(os.getenv("PROXYMANAGER_SESSION_TTL_SECONDS", "3600")),
            timeout_seconds=float(os.getenv("PROXYMANAGER_TIMEOUT_SECONDS", "15")),
            max_response_bytes=int(os.getenv("PROXYMANAGER_MAX_RESPONSE_BYTES", "1000000")),
            monthly_budget_usd=float(os.getenv("PROXYMANAGER_MONTHLY_BUDGET_USD", "25")),
            audit_retention_days=float(os.getenv("PROXYMANAGER_AUDIT_RETENTION_DAYS", "30")),
            evaluator_scopes=tuple(x.strip() for x in os.getenv("PROXYMANAGER_EVALUATOR_SCOPES", ",".join(cls.evaluator_scopes)).split(",") if x.strip()),
            proxy_window_seconds=float(os.getenv("PROXYMANAGER_PROXY_WINDOW_SECONDS", "3600")),
            proxy_min_success_rate=float(os.getenv("PROXYMANAGER_PROXY_MIN_SUCCESS_RATE", "0.5")),
            proxy_max_inflight=int(os.getenv("PROXYMANAGER_PROXY_MAX_INFLIGHT", "5")),
            bench_max_requests=int(os.getenv("PROXYMANAGER_BENCH_MAX_REQUESTS", "1000")),
            bench_max_concurrency=int(os.getenv("PROXYMANAGER_BENCH_MAX_CONCURRENCY", "10")),
            bench_max_bytes=int(os.getenv("PROXYMANAGER_BENCH_MAX_BYTES", "50000000")),
            auth_failure_limit=int(os.getenv("PROXYMANAGER_AUTH_FAILURE_LIMIT", "10")),
            scrape_proxy_attempts=int(os.getenv("PROXYMANAGER_SCRAPE_PROXY_ATTEMPTS", "2")),
            proxy_cost_per_gb_usd=float(os.getenv("PROXYMANAGER_PROXY_COST_PER_GB_USD", "0")),
            strict=os.getenv("PROXYMANAGER_STRICT", "") == "1",
            rate_limit_requests=int(os.getenv("PROXYMANAGER_RATE_LIMIT_REQUESTS", "60")),
            rate_limit_window_seconds=float(os.getenv("PROXYMANAGER_RATE_LIMIT_WINDOW_SECONDS", "60")),
            alert_webhook_url=os.getenv("PROXYMANAGER_ALERT_WEBHOOK_URL", ""),
        )
