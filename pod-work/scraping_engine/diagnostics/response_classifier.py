"""Clasificador de respuestas HTTP para identificar protección y estado del sitio."""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from scraping_engine.diagnostics.evidence import Evidence


class ResponseStatus(Enum):
    """Estados posibles de una respuesta HTTP."""
    
    SUCCESS = "success"           # 2xx exitoso
    REDIRECT = "redirect"         # 3xx redirección
    CLIENT_ERROR = "client_error" # 4xx error del cliente
    SERVER_ERROR = "server_error" # 5xx error del servidor
    PROXY_ERROR = "proxy_error"   # Error de proxy
    TIMEOUT = "timeout"           # Timeout
    CONNECTION_ERROR = "connection_error"  # Error de conexión


class ProtectionType(Enum):
    """Tipos de protección identificables."""
    
    NONE = "none"                 # Sin protección
    DATADOME = "datadome"         # Protección DataDome
    CLOUDFLARE = "cloudflare"     # Protección Cloudflare
    CAPTCHA = "captcha"           # Desafío CAPTCHA
    RATE_LIMIT = "rate_limit"     # Límite de tasa
    ACCESS_DENIED = "access_denied"  # Acceso denegado
    UNAUTHORIZED = "unauthorized"   # No autorizado
    SERVER_ERROR = "server_error"   # Error del servidor
    CONNECTION_ERROR = "connection_error"  # Error de conexión
    TIMEOUT = "timeout"           # Timeout


@dataclass
class ResponseClassification:
    """Clasificación completa de una respuesta HTTP."""
    
    status: ResponseStatus
    protection_type: ProtectionType
    http_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    content_length: Optional[int] = None
    content_type: Optional[str] = None
    is_accessible: bool = True
    is_content_valid: bool = True
    evidence: List[Evidence] = None
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []
    
    def add_evidence(self, evidence: Evidence):
        """Añade evidencia a la clasificación."""
        self.evidence.append(evidence)
    
    def get_protection_indicators(self) -> List[str]:
        """Obtiene los indicadores de protección detectados."""
        indicators = []
        if self.protection_type != ProtectionType.NONE:
            indicators.append(self.protection_type.value)
        
        for evidence in self.evidence:
            if evidence.indicator:
                indicators.append(evidence.indicator)
                
        return indicators


class ResponseClassifier:
    """Clasificador de respuestas HTTP para identificar protección y estado del sitio."""
    
    # Patrones comunes para detectar protección
    DATADOME_PATTERNS = [
        re.compile(r'datadome', re.IGNORECASE),
        re.compile(r'datadome\.io', re.IGNORECASE),
        re.compile(r'cdn\.datadome\.co', re.IGNORECASE),
        re.compile(r'datadome.*security', re.IGNORECASE),
    ]
    
    CLOUDFLARE_PATTERNS = [
        re.compile(r'cloudflare', re.IGNORECASE),
        re.compile(r'cf-ray', re.IGNORECASE),
        re.compile(r'cloudflare-nginx', re.IGNORECASE),
    ]
    
    CAPTCHA_PATTERNS = [
        re.compile(r'captcha', re.IGNORECASE),
        re.compile(r'challenge.*page', re.IGNORECASE),
        re.compile(r'blocked.*by.*security', re.IGNORECASE),
        re.compile(r'access.*denied.*security', re.IGNORECASE),
    ]
    
    ACCESS_DENIED_PATTERNS = [
        re.compile(r'access denied', re.IGNORECASE),
        re.compile(r'forbidden', re.IGNORECASE),
        re.compile(r'restricted access', re.IGNORECASE),
        re.compile(r'blocked.*by.*firewall', re.IGNORECASE),
    ]
    
    # Patrones para contenido vacío o inválido
    EMPTY_CONTENT_PATTERNS = [
        re.compile(r'<html[^>]*><head[^>]*></head><body[^>]*></body></html>', re.IGNORECASE),
        re.compile(r'<html[^>]*><head[^>]*></head><body[^>]*><\/body><\/html>', re.IGNORECASE),
    ]
    
    def __init__(self):
        """Inicializa el clasificador."""
        pass
    
    def classify(self, 
                 http_code: Optional[int] = None,
                 headers: Optional[Dict[str, str]] = None,
                 content: Optional[str] = None) -> ResponseClassification:
        """
        Clasifica una respuesta HTTP.
        
        Args:
            http_code (Optional[int]): Código HTTP
            headers (Optional[Dict[str, str]]): Encabezados HTTP
            content (Optional[str]): Contenido de la respuesta
            
        Returns:
            ResponseClassification: Clasificación de la respuesta
        """
        classification = ResponseClassification(
            status=ResponseStatus.SUCCESS,
            protection_type=ProtectionType.NONE,
            http_code=http_code,
            headers=headers or {},
            content_length=len(content) if content else 0,
            content_type=self._get_content_type(headers),
            is_accessible=True,
            is_content_valid=True
        )
        
        # Verificar código HTTP
        if http_code:
            classification = self._classify_http_code(http_code, classification)
            
        # Verificar encabezados
        if headers:
            classification = self._analyze_headers(headers, classification)
            
        # Verificar contenido
        if content:
            classification = self._analyze_content(content, classification)
            
        return classification
    
    def _classify_http_code(self, code: int, classification: ResponseClassification) -> ResponseClassification:
        """Clasifica por código HTTP."""
        
        if 200 <= code < 300:
            classification.status = ResponseStatus.SUCCESS
        elif 300 <= code < 400:
            classification.status = ResponseStatus.REDIRECT
        elif 400 <= code < 500:
            classification.status = ResponseStatus.CLIENT_ERROR
        elif 500 <= code < 600:
            classification.status = ResponseStatus.SERVER_ERROR
            
        # Detectar protección específica por código
        if code == 403:
            classification.protection_type = ProtectionType.ACCESS_DENIED
        elif code == 429:
            classification.protection_type = ProtectionType.RATE_LIMIT
        elif code == 503:
            classification.protection_type = ProtectionType.SERVER_ERROR
            
        return classification
    
    def _analyze_headers(self, headers: Dict[str, str], classification: ResponseClassification) -> ResponseClassification:
        """Analiza los encabezados HTTP."""
        
        # Convertir encabezados a minúsculas para comparación
        lower_headers = {k.lower(): v for k, v in headers.items()}
        
        # Buscar indicadores de protección en encabezados
        for pattern in self.DATADOME_PATTERNS:
            if any(pattern.search(header_value) for header_value in lower_headers.values()):
                classification.protection_type = ProtectionType.DATADOME
                classification.add_evidence(Evidence(
                    indicator="datadome_header",
                    description="Encabezado de protección DataDome detectado"
                ))
                break
                
        for pattern in self.CLOUDFLARE_PATTERNS:
            if any(pattern.search(header_value) for header_value in lower_headers.values()):
                classification.protection_type = ProtectionType.CLOUDFLARE
                classification.add_evidence(Evidence(
                    indicator="cloudflare_header",
                    description="Encabezado de protección Cloudflare detectado"
                ))
                break
                
        for pattern in self.CAPTCHA_PATTERNS:
            if any(pattern.search(header_value) for header_value in lower_headers.values()):
                classification.protection_type = ProtectionType.CAPTCHA
                classification.add_evidence(Evidence(
                    indicator="captcha_header",
                    description="Encabezado de desafío CAPTCHA detectado"
                ))
                break
                
        return classification
    
    def _analyze_content(self, content: str, classification: ResponseClassification) -> ResponseClassification:
        """Analiza el contenido de la respuesta."""
        
        # Verificar si es contenido vacío o inválido
        if not content or len(content.strip()) == 0:
            classification.is_content_valid = False
            classification.add_evidence(Evidence(
                indicator="empty_content",
                description="Contenido vacío"
            ))
            return classification
            
        # Verificar patrones comunes de contenido vacío o protegido
        for pattern in self.EMPTY_CONTENT_PATTERNS:
            if pattern.search(content):
                classification.is_content_valid = False
                classification.add_evidence(Evidence(
                    indicator="empty_html_pattern",
                    description="Patrón HTML vacío detectado"
                ))
                break
                
        # Buscar indicadores de protección en el contenido
        content_lower = content.lower()
        
        for pattern in self.DATADOME_PATTERNS:
            if pattern.search(content_lower):
                classification.protection_type = ProtectionType.DATADOME
                classification.add_evidence(Evidence(
                    indicator="datadome_content",
                    description="Indicador de protección DataDome en contenido"
                ))
                break
                
        for pattern in self.CLOUDFLARE_PATTERNS:
            if pattern.search(content_lower):
                classification.protection_type = ProtectionType.CLOUDFLARE
                classification.add_evidence(Evidence(
                    indicator="cloudflare_content",
                    description="Indicador de protección Cloudflare en contenido"
                ))
                break
                
        for pattern in self.CAPTCHA_PATTERNS:
            if pattern.search(content_lower):
                classification.protection_type = ProtectionType.CAPTCHA
                classification.add_evidence(Evidence(
                    indicator="captcha_content",
                    description="Indicador de desafío CAPTCHA en contenido"
                ))
                break
                
        for pattern in self.ACCESS_DENIED_PATTERNS:
            if pattern.search(content_lower):
                classification.protection_type = ProtectionType.ACCESS_DENIED
                classification.add_evidence(Evidence(
                    indicator="access_denied_content",
                    description="Indicador de acceso denegado en contenido"
                ))
                break
                
        return classification
    
    def _get_content_type(self, headers: Optional[Dict[str, str]]) -> Optional[str]:
        """Obtiene el tipo de contenido de los encabezados."""
        if not headers:
            return None
        return headers.get('content-type', headers.get('Content-Type'))