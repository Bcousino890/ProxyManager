"""
Clases base para motores de scraping.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ScrapingResult:
    """Resultado de una operación de scraping."""
    
    url: str
    status_code: int
    content: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    response_time: float
    error: Optional[Exception] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseEngine(ABC):
    """Motor base de scraping."""
    
    @abstractmethod
    async def fetch(self, url: str, **kwargs) -> ScrapingResult:
        """
        Realiza una solicitud HTTP a la URL especificada.
        
        Args:
            url: URL a acceder
            **kwargs: Parámetros adicionales
            
        Returns:
            ScrapingResult con los datos de la respuesta
        """
        pass
    
    @abstractmethod
    async def post(self, url: str, data: Dict[str, Any], **kwargs) -> ScrapingResult:
        """
        Realiza una solicitud POST a la URL especificada.
        
        Args:
            url: URL a acceder
            data: Datos a enviar en el cuerpo de la solicitud
            **kwargs: Parámetros adicionales
            
        Returns:
            ScrapingResult con los datos de la respuesta
        """
        pass