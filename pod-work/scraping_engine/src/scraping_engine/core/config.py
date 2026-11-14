"""
Configuración central del motor de scraping.
"""
import os
from typing import Optional

class ScraperConfig:
    """Configuración principal."""
    
    # Nivel de registro
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Timeout por defecto para solicitudes HTTP
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30"))
    
    # Límite de concurrencia
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    
    # Límites de reintentos
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Intervalo entre reintentos (segundos)
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "1.0"))
    
    # Proxy por defecto
    DEFAULT_PROXY: Optional[str] = os.getenv("DEFAULT_PROXY")
    
    # Directorio de trabajo
    WORK_DIR: str = os.getenv("WORK_DIR", "/tmp/scraping_engine")