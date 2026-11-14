"""Base classes for scraping engines."""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

from scraping_engine.core.base import BaseEngine, ScrapingResult


class EngineType(str, Enum):
    """Tipos de motores de scraping."""
    
    HTTP = "http"
    BROWSER = "browser"


@dataclass
class EngineConfig:
    """Configuración común para motores de scraping."""
    
    timeout: int = 30
    max_retries: int = 3
    headers: Optional[Dict[str, str]] = None
    proxy: Optional[str] = None
    use_cookies: bool = True


class BaseHttpEngine(BaseEngine):
    """Motor base para scraping HTTP."""
    
    def __init__(self, config: Optional[EngineConfig] = None):
        super().__init__()
        self.name = "BaseHttpEngine"
        self.config = config or EngineConfig()
        
    async def scrape(self, url: str, **kwargs) -> ScrapingResult:
        """
        Método principal de scraping HTTP.
        
        Args:
            url (str): URL a scrapear
            **kwargs: Parámetros adicionales
            
        Returns:
            ScrapingResult: Resultado del scraping
        """
        raise NotImplementedError("Este método debe ser implementado por las subclases")