"""
Configuración del panel de scraping.
"""

import os
from pathlib import Path

class Settings:
    """Configuración del panel de scraping."""
    
    # Clave API para autenticación
    API_KEY = os.environ.get("SCRAPING_API_KEY", "default_api_key_12345")
    
    # Configuración del servidor
    SERVER_HOST = os.environ.get("SCRAPING_SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.environ.get("SCRAPING_SERVER_PORT", "8080"))
    
    # Configuración de proxies
    MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT", "5"))
    TIMEOUT = int(os.environ.get("SCRAPING_TIMEOUT", "30"))
    RETRY_ATTEMPTS = int(os.environ.get("SCRAPING_RETRY_ATTEMPTS", "3"))
    
    # Configuración de seguridad
    ALLOWED_ORIGINS = [
        "http://localhost:8787",
        "http://127.0.0.1:8787",
        "https://proxymanager.local"
    ]
    
    # Configuración de scraping
    ALLOWED_HOSTS = [
        "example.com",
        "httpbin.org"
    ]
    
    MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MB
    
    EXPECTED_TEXT = None

# Instancia única de la configuración
settings = Settings()