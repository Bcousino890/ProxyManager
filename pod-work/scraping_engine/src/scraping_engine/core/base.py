"""Base classes for scraping engines."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import time


@dataclass
class ScrapingResult:
    """Resultado de una operación de scraping."""
    
    success: bool
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    response_time: Optional[float] = None


class BaseEngine:
    """Motor base para scraping."""
    
    def __init__(self):
        self.name = "BaseEngine"
        
    async def scrape(self, url: str, **kwargs) -> ScrapingResult:
        """
        Método principal de scraping.
        
        Args:
            url (str): URL a scrapear
            **kwargs: Parámetros adicionales
            
        Returns:
            ScrapingResult: Resultado del scraping
        """
        raise NotImplementedError("Este método debe ser implementado por las subclases")