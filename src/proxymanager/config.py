from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    db_path: str = "proxymanager.db"
    evaluator_key: str = ""
    admin_key: str = ""
    allowed_hosts: tuple[str, ...] = ()
    expected_text: str = ""
    session_ttl_seconds: int = 3600
    timeout_seconds: float = 15.0
    max_response_bytes: int = 1_000_000
    monthly_budget_usd: float = 25.0

    @classmethod
    def from_env(cls) -> "Settings":
        hosts = tuple(host.strip().lower() for host in os.getenv("PROXYMANAGER_ALLOWED_HOSTS", "").split(",") if host.strip())
        return cls(
            db_path=os.getenv("PROXYMANAGER_DB_PATH", "proxymanager.db"),
            evaluator_key=os.getenv("PROXYMANAGER_EVALUATOR_KEY", ""),
            admin_key=os.getenv("PROXYMANAGER_ADMIN_KEY", ""),
            allowed_hosts=hosts,
            expected_text=os.getenv("PROXYMANAGER_EXPECTED_TEXT", ""),
            session_ttl_seconds=int(os.getenv("PROXYMANAGER_SESSION_TTL_SECONDS", "3600")),
            timeout_seconds=float(os.getenv("PROXYMANAGER_TIMEOUT_SECONDS", "15")),
            max_response_bytes=int(os.getenv("PROXYMANAGER_MAX_RESPONSE_BYTES", "1000000")),
            monthly_budget_usd=float(os.getenv("PROXYMANAGER_MONTHLY_BUDGET_USD", "25")),
        )
