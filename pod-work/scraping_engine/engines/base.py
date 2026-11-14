"""
Módulo base para motores de scraping.
Define interfaces y clases base comunes.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ScrapingResult:
    """Resultado de una operación de scraping."""
    success: bool
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    response_time: Optional[float] = None


class BaseEngine(ABC):
    """Interfaz base para motores de scraping."""

    @abstractmethod
    async def fetch(self, url: str, **kwargs) -> ScrapingResult:
        """
        Realiza una solicitud HTTP o navegador.
        
        Args:
            url: URL a acceder
            **kwargs: Parámetros adicionales
            
        Returns:
            Resultado del scraping
        """
        pass

    @abstractmethod
    async def close(self):
        """Cierra recursos del motor."""
        pass