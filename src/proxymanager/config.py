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
    public_url: str = ""

    def __post_init__(self):
        if min(self.health_concurrency, self.health_queue_limit, self.session_ttl_seconds, self.timeout_seconds, self.max_response_bytes) <= 0:
            raise ValueError("Los límites deben ser positivos")

    @classmethod
    def from_env(cls) -> "Settings":
        hosts = tuple(host.strip().lower() for host in os.getenv("PROXYMANAGER_ALLOWED_HOSTS", "").split(",") if host.strip())
        return cls(
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
            public_url=os.getenv("PROXYMANAGER_PUBLIC_URL", ""),
        )
