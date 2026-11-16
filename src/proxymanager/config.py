from dataclasses import dataclass
import os


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
    monthly_budget_usd: float = 25.0
    allow_any_public_host: bool = False
    blocked_hosts: tuple[str, ...] = ()
    signup_enabled: bool = True
    free_credits: int = 100
    credits_per_request: int = 1
    credits_per_proxied_request: int = 2
    rate_limit_per_minute: int = 60
    login_attempts_per_minute: int = 10
    cookie_secure: bool = True
    support_email: str = ""

    def __post_init__(self):
        if min(self.rate_limit_per_minute, self.login_attempts_per_minute, self.credits_per_request, self.credits_per_proxied_request) <= 0 or self.free_credits < 0:
            raise ValueError("Los límites deben ser positivos")
        if min(self.health_concurrency, self.health_queue_limit, self.session_ttl_seconds, self.timeout_seconds, self.max_response_bytes) <= 0:
            raise ValueError("Los límites deben ser positivos")

    @classmethod
    def from_env(cls) -> "Settings":
        hosts = tuple(host.strip().lower() for host in os.getenv("PROXYMANAGER_ALLOWED_HOSTS", "").split(",") if host.strip())
        def flag(name, default):
            return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")
        blocked = tuple(h.strip().lower().lstrip(".") for h in os.getenv("PROXYMANAGER_BLOCKED_HOSTS", "").split(",") if h.strip())
        return cls(
            allow_any_public_host=flag("PROXYMANAGER_ALLOW_ANY_PUBLIC_HOST", "false"),
            blocked_hosts=blocked,
            signup_enabled=flag("PROXYMANAGER_SIGNUP_ENABLED", "true"),
            free_credits=int(os.getenv("PROXYMANAGER_FREE_CREDITS", "100")),
            credits_per_request=int(os.getenv("PROXYMANAGER_CREDITS_PER_REQUEST", "1")),
            credits_per_proxied_request=int(os.getenv("PROXYMANAGER_CREDITS_PER_PROXIED_REQUEST", "2")),
            rate_limit_per_minute=int(os.getenv("PROXYMANAGER_RATE_LIMIT_PER_MINUTE", "60")),
            login_attempts_per_minute=int(os.getenv("PROXYMANAGER_LOGIN_ATTEMPTS_PER_MINUTE", "10")),
            cookie_secure=flag("PROXYMANAGER_COOKIE_SECURE", "true"),
            support_email=os.getenv("PROXYMANAGER_SUPPORT_EMAIL", ""),
            health_concurrency=int(os.getenv("PROXYMANAGER_HEALTH_CONCURRENCY", "2")),
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
        )
