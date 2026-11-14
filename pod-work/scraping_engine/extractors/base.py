"""
Módulo base para extractores de datos.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Resultado de una extracción."""
    data: Dict[str, Any]
    metadata: Dict[str, Any]


class BaseExtractor(ABC):
    """Clase base para extractores."""

    @abstractmethod
    def extract(self, content: str, **kwargs) -> ExtractionResult:
        """
        Extrae datos del contenido proporcionado.

        Args:
            content (str): Contenido HTML o texto a extraer.
            **kwargs: Parámetros adicionales.

        Returns:
            ExtractionResult: Resultado de la extracción.
        """
        pass