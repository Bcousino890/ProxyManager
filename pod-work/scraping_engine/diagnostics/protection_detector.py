"""Detector de protección web para identificar mecanismos de seguridad como DataDome."""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from scraping_engine.diagnostics.response_classifier import ResponseClassification, ProtectionType


class DetectionMethod(Enum):
    """Métodos de detección disponibles."""
    
    HEADER = "header"        # Detección por encabezados HTTP
    CONTENT = "content"      # Detección por contenido HTML/JS
    STATUS_CODE = "status_code"  # Detección por código HTTP
    MIXED = "mixed"          # Detección combinada


@dataclass
class DetectionResult:
    """Resultado de la detección de protección."""
    
    is_protected: bool
    protection_type: ProtectionType
    confidence: float  # De 0.0 a 1.0
    methods_used: List[DetectionMethod]
    indicators: List[str]
    details: Dict[str, str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class ProtectionDetector:
    """Detector de protección web para identificar mecanismos de seguridad como DataDome."""
    
    # Patrones específicos para diferentes tipos de protección
    PROTECTION_PATTERNS = {
        ProtectionType.DATADOME: [
            re.compile(r'datadome', re.IGNORECASE),
            re.compile(r'datadome\.io', re.IGNORECASE),
            re.compile(r'cdn\.datadome\.co', re.IGNORECASE),
            re.compile(r'datadome.*security', re.IGNORECASE),
            re.compile(r'datadome.*anti.*bot', re.IGNORECASE),
            re.compile(r'datadome.*captcha', re.IGNORECASE),
        ],
        
        ProtectionType.CLOUDFLARE: [
            re.compile(r'cloudflare', re.IGNORECASE),
            re.compile(r'cf-ray', re.IGNORECASE),
            re.compile(r'cloudflare-nginx', re.IGNORECASE),
            re.compile(r'cloudflare.*security', re.IGNORECASE),
            re.compile(r'cloudflare.*challenge', re.IGNORECASE),
        ],
        
        ProtectionType.CAPTCHA: [
            re.compile(r'captcha', re.IGNORECASE),
            re.compile(r'challenge.*page', re.IGNORECASE),
            re.compile(r'blocked.*by.*security', re.IGNORECASE),
            re.compile(r'access.*denied.*security', re.IGNORECASE),
            re.compile(r'captcha.*required', re.IGNORECASE),
        ],
        
        ProtectionType.RATE_LIMIT: [
            re.compile(r'rate.*limit', re.IGNORECASE),
            re.compile(r'too.*many.*requests', re.IGNORECASE),
            re.compile(r'request.*too.*frequent', re.IGNORECASE),
        ],
        
        ProtectionType.ACCESS_DENIED: [
            re.compile(r'access denied', re.IGNORECASE),
            re.compile(r'forbidden', re.IGNORECASE),
            re.compile(r'restricted access', re.IGNORECASE),
            re.compile(r'blocked.*by.*firewall', re.IGNORECASE),
        ]
    }
    
    # Indicadores de contenido específico para cada protección
    CONTENT_INDICATORS = {
        ProtectionType.DATADOME: [
            'datadome',
            'Datadome',
            'DataDome',
            'cdn.datadome.co',
            'datadome.io',
            'anti-bot',
            'anti-crawler',
            'security check',
        ],
        
        ProtectionType.CLOUDFLARE: [
            'cloudflare',
            'CloudFlare',
            'CF-RAY',
            'cloudflare challenge',
            'security check',
        ],
        
        ProtectionType.CAPTCHA: [
            'captcha',
            'challenge page',
            'verification required',
            'security verification',
        ],
    }
    
    def __init__(self):
        """Inicializa el detector de protección."""
        pass
    
    def detect(self, 
               classification: ResponseClassification,
               content: Optional[str] = None) -> DetectionResult:
        """
        Detecta si hay protección en la respuesta.
        
        Args:
            classification (ResponseClassification): Clasificación previa de la respuesta
            content (Optional[str]): Contenido de la respuesta
            
        Returns:
            DetectionResult: Resultado de la detección
        """
        # Inicializar resultado
        result = DetectionResult(
            is_protected=False,
            protection_type=ProtectionType.NONE,
            confidence=0.0,
            methods_used=[],
            indicators=[]
        )
        
        # Si ya se ha detectado protección en la clasificación, usar esa
        if classification.protection_type != ProtectionType.NONE:
            result.is_protected = True
            result.protection_type = classification.protection_type
            result.confidence = 0.95  # Alta confianza si ya fue detectada
            result.methods_used.append(DetectionMethod.STATUS_CODE)
            return result
        
        # Detectar por código HTTP (más rápido)
        if classification.http_code:
            detected = self._detect_by_status_code(classification.http_code, result)
            if detected:
                return result
                
        # Detectar por encabezados
        if classification.headers:
            detected = self._detect_by_headers(classification.headers, result)
            if detected:
                return result
                
        # Detectar por contenido
        if content:
            detected = self._detect_by_content(content, result)
            if detected:
                return result
                
        # Si no se detectó protección, devolver resultado por defecto
        return result
    
    def _detect_by_status_code(self, code: int, result: DetectionResult) -> bool:
        """Detecta protección por código HTTP."""
        
        if code == 403:
            result.is_protected = True
            result.protection_type = ProtectionType.ACCESS_DENIED
            result.confidence = 0.85
            result.methods_used.append(DetectionMethod.STATUS_CODE)
            result.indicators.append("http_403")
            return True
            
        elif code == 429:
            result.is_protected = True
            result.protection_type = ProtectionType.RATE_LIMIT
            result.confidence = 0.90
            result.methods_used.append(DetectionMethod.STATUS_CODE)
            result.indicators.append("http_429")
            return True
            
        elif code == 503:
            result.is_protected = True
            result.protection_type = ProtectionType.SERVER_ERROR
            result.confidence = 0.80
            result.methods_used.append(DetectionMethod.STATUS_CODE)
            result.indicators.append("http_503")
            return True
            
        return False
    
    def _detect_by_headers(self, headers: Dict[str, str], result: DetectionResult) -> bool:
        """Detecta protección por encabezados HTTP."""
        
        # Convertir a minúsculas para comparación
        lower_headers = {k.lower(): v for k, v in headers.items()}
        
        # Buscar indicadores de protección en encabezados
        for protection_type, patterns in self.PROTECTION_PATTERNS.items():
            for pattern in patterns:
                if any(pattern.search(header_value) for header_value in lower_headers.values()):
                    result.is_protected = True
                    result.protection_type = protection_type
                    result.confidence = 0.95
                    result.methods_used.append(DetectionMethod.HEADER)
                    result.indicators.append(f"header_{protection_type.value}")
                    return True
                    
        return False
    
    def _detect_by_content(self, content: str, result: DetectionResult) -> bool:
        """Detecta protección por contenido."""
        
        content_lower = content.lower()
        
        # Buscar indicadores de protección en el contenido
        for protection_type, indicators in self.CONTENT_INDICATORS.items():
            for indicator in indicators:
                if indicator.lower() in content_lower:
                    result.is_protected = True
                    result.protection_type = protection_type
                    result.confidence = 0.85
                    result.methods_used.append(DetectionMethod.CONTENT)
                    result.indicators.append(f"content_{protection_type.value}")
                    return True
                    
        # Buscar patrones específicos de protección
        for protection_type, patterns in self.PROTECTION_PATTERNS.items():
            for pattern in patterns:
                if pattern.search(content_lower):
                    result.is_protected = True
                    result.protection_type = protection_type
                    result.confidence = 0.90
                    result.methods_used.append(DetectionMethod.CONTENT)
                    result.indicators.append(f"content_pattern_{protection_type.value}")
                    return True
                    
        return False
    
    def get_protection_info(self, protection_type: ProtectionType) -> Dict[str, str]:
        """Obtiene información sobre un tipo de protección."""
        
        info = {
            ProtectionType.NONE: {
                "name": "Sin protección",
                "description": "No se detectó protección activa.",
                "recommendation": "El sitio es accesible sin restricciones."
            },
            
            ProtectionType.DATADOME: {
                "name": "DataDome",
                "description": "Protección anti-bot de DataDome.",
                "recommendation": "Utilizar proxies autorizados o sesiones autorizadas para evitar bloqueos."
            },
            
            ProtectionType.CLOUDFLARE: {
                "name": "Cloudflare",
                "description": "Protección anti-bot de Cloudflare.",
                "recommendation": "Esperar antes de reintentar o utilizar proxies autorizados."
            },
            
            ProtectionType.CAPTCHA: {
                "name": "CAPTCHA",
                "description": "Desafío CAPTCHA activo.",
                "recommendation": "Requiere interacción humana o solución automatizada."
            },
            
            ProtectionType.RATE_LIMIT: {
                "name": "Límite de tasa",
                "description": "Se ha alcanzado el límite de solicitudes permitidas.",
                "recommendation": "Reducir la frecuencia de las solicitudes o utilizar proxies autorizados."
            },
            
            ProtectionType.ACCESS_DENIED: {
                "name": "Acceso denegado",
                "description": "Acceso denegado al recurso solicitado.",
                "recommendation": "Verificar credenciales o permisos de acceso."
            },
            
            ProtectionType.SERVER_ERROR: {
                "name": "Error del servidor",
                "description": "El servidor devolvió un error interno.",
                "recommendation": "Reintentar la solicitud más tarde."
            },
        }
        
        return info.get(protection_type, info[ProtectionType.NONE])