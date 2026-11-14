"""
Configuración del panel de scraping.
"""

import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Configuración de la API
API_KEY = os.environ.get("SCRAPING_API_KEY", "default_api_key_12345")

# Configuración de proxies
PROXIES_FILE = BASE_DIR / "proxies.txt"
PROXY_LIST = []

# Configuración del scraping
MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT", "5"))
TIMEOUT = int(os.environ.get("SCRAPING_TIMEOUT", "30"))
RETRY_ATTEMPTS = int(os.environ.get("SCRAPING_RETRY_ATTEMPTS", "3"))

# Configuración de seguridad
ALLOWED_ORIGINS = [
    "http://localhost:8787",
    "http://127.0.0.1:8787",
    "https://proxymanager.local"
]

# Configuración del servidor
SERVER_HOST = os.environ.get("SCRAPING_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SCRAPING_SERVER_PORT", "8080"))