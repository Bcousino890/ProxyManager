"""Evidencia de diagnóstico para identificar protección y problemas en las respuestas."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Evidence:
    """Evidencia de diagnóstico."""
    
    indicator: str
    """Identificador único del indicador (ej. 'datadome_header', 'empty_content')."""
    
    description: str
    """Descripción legible del indicador."""
    
    confidence: float = 1.0
    """Nivel de confianza del indicador (de 0.0 a 1.0)."""
    
    source: Optional[str] = None
    """Fuente del indicador (ej. 'header', 'content', 'status_code')."""
    
    details: Optional[dict] = None
    """Información adicional específica del indicador."""
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}