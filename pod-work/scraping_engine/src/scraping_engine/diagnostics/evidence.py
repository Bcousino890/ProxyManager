"""
Evidencia de respuestas HTTP para diagnóstico de protección anti-bot.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from scraping_engine.diagnostics.response_classifier import ResponseClassification


@dataclass
class Evidence:
    """Evidencia de una respuesta HTTP."""
    
    http_status_code: int
    headers: Dict[str, str]
    content: Optional[str] = None
    response_time: Optional[float] = None
    classification: Optional[ResponseClassification] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la evidencia a un diccionario."""
        return {
            'http_status_code': self.http_status_code,
            'headers': self.headers,
            'content': self.content,
            'response_time': self.response_time,
            'classification': self.classification.__dict__ if self.classification else None
        }