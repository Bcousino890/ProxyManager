"""
Detector de protección anti-bot para respuestas HTTP.
"""

from typing import Optional, Dict, Any
import time
import asyncio

from scraping_engine.diagnostics.response_classifier import (
    ResponseClassifier,
    ResponseClassification,
    ProtectionType
)
from scraping_engine.diagnostics.evidence import Evidence


class DetectionResult:
    """Resultado de la detección de protección."""
    
    def __init__(
        self,
        is_protected: bool,
        protection_type: ProtectionType,
        evidence: Evidence,
        detection_time: Optional[float] = None
    ):
        self.is_protected = is_protected
        self.protection_type = protection_type
        self.evidence = evidence
        self.detection_time = detection_time or time.time()


class ProtectionDetector:
    """Detector de protección anti-bot para respuestas HTTP."""
    
    def __init__(self):
        self.classifier = ResponseClassifier()
        
    async def detect_protection(
        self,
        http_status_code: int,
        headers: Dict[str, str],
        content: Optional[str] = None,
        response_time: Optional[float] = None
    ) -> DetectionResult:
        """
        Detecta si una respuesta HTTP está protegida por algún mecanismo anti-bot.
        
        Args:
            http_status_code: Código de estado HTTP
            headers: Encabezados HTTP
            content: Contenido de la respuesta (opcional)
            response_time: Tiempo de respuesta en segundos
            
        Returns:
            DetectionResult: Resultado de la detección
        """
        # Clasificar la respuesta
        classification = self.classifier.classify_response(
            http_status_code=http_status_code,
            headers=headers,
            content=content,
            response_time=response_time
        )
        
        # Crear evidencia
        evidence = Evidence(
            http_status_code=http_status_code,
            headers=headers,
            content=content,
            response_time=response_time,
            classification=classification
        )
        
        # Determinar si está protegido
        is_protected = classification.protection_type != ProtectionType.NONE
        
        return DetectionResult(
            is_protected=is_protected,
            protection_type=classification.protection_type,
            evidence=evidence,
            detection_time=time.time()
        )