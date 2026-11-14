"""
Módulo base para extractores de datos.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Resultado de la extracción de datos."""
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    errors: List[str]


class BaseExtractor(ABC):
    """Clase base para extractores de datos."""
    
    @abstractmethod
    def extract(self, content: str, **kwargs) -> ExtractionResult:
        """
        Extrae datos del contenido proporcionado.
        
        Args:
            content (str): Contenido a extraer
            **kwargs: Parámetros adicionales
            
        Returns:
            ExtractionResult: Resultado de la extracción
        """
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Valida los datos extraídos.
        
        Args:
            data (Dict[str, Any]): Datos a validar
            
        Returns:
            bool: True si los datos son válidos
        """
        pass