"""
Clasificador de respuestas HTTP para identificar protección anti-bot.
"""

from enum import Enum
from typing import Optional, Dict, Any
import re

class ResponseStatus(Enum):
    """Estados posibles de una respuesta HTTP."""
    SUCCESS = "success"
    REDIRECT = "redirect"
    CLIENT_ERROR = "client_error"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    PROXY_ERROR = "proxy_error"
    TLS_ERROR = "tls_error"
    DATA_DOME_CHALLENGE = "datadome_challenge"
    CAPTCHA = "captcha"
    ACCESS_DENIED = "access_denied"
    EMPTY_RESPONSE = "empty_response"
    UNEXPECTED_REDIRECT = "unexpected_redirect"

class ProtectionType(Enum):
    """Tipos de protección detectados."""
    NONE = "none"
    DATADOME = "datadome"
    CLOUDFLARE = "cloudflare"
    CAPTCHA = "captcha"
    RATE_LIMIT = "rate_limit"
    ACCESS_DENIED = "access_denied"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"

class ResponseClassification:
    """Clasificación de una respuesta HTTP."""
    
    def __init__(
        self,
        http_status_code: int,
        status: ResponseStatus,
        protection_type: ProtectionType,
        headers: Optional[Dict[str, str]] = None,
        content_length: Optional[int] = None,
        response_time: Optional[float] = None,
        error_message: Optional[str] = None,
        is_accessible: bool = True,
        is_content_valid: bool = True,
        evidence: Optional[list] = None
    ):
        self.http_status_code = http_status_code
        self.status = status
        self.protection_type = protection_type
        self.headers = headers or {}
        self.content_length = content_length
        self.response_time = response_time
        self.error_message = error_message
        self.is_accessible = is_accessible
        self.is_content_valid = is_content_valid
        self.evidence = evidence or []
        
    def __repr__(self):
        return f"ResponseClassification(status={self.status}, http_status_code={self.http_status_code})"
    
    def _is_accessible(self) -> bool:
        """Determina si la respuesta es accesible."""
        return (
            self.status == ResponseStatus.SUCCESS and 
            self.protection_type == ProtectionType.NONE and
            self.http_status_code < 400
        )
    
    def _is_content_valid(self) -> bool:
        """Determina si el contenido de la respuesta es válido."""
        # Si no hay contenido, no es válido
        if self.content_length == 0:
            return False
        
        # Si es un error de servidor o cliente, no es válido
        if self.http_status_code >= 400:
            return False
            
        return True

class ResponseClassifier:
    """Clasificador de respuestas HTTP para identificar protección anti-bot."""
    
    # Patrones comunes para detectar DataDome
    DATADOME_PATTERNS = [
        re.compile(r'datadome', re.IGNORECASE),
        re.compile(r'datadome\.io', re.IGNORECASE),
        re.compile(r'cloudflare', re.IGNORECASE),  # Cloudflare también puede estar presente
    ]
    
    # Patrones comunes para detectar CAPTCHA
    CAPTCHA_PATTERNS = [
        re.compile(r'captcha', re.IGNORECASE),
        re.compile(r'challenge.*page', re.IGNORECASE),
        re.compile(r'blocked.*access', re.IGNORECASE),
        re.compile(r'please.*verify', re.IGNORECASE),
    ]
    
    # Patrones para identificar páginas de acceso denegado
    ACCESS_DENIED_PATTERNS = [
        re.compile(r'access.*denied', re.IGNORECASE),
        re.compile(r'forbidden', re.IGNORECASE),
        re.compile(r'403', re.IGNORECASE),
        re.compile(r'blocked', re.IGNORECASE),
    ]
    
    # Patrones para identificar respuestas vacías o inválidas
    EMPTY_RESPONSE_PATTERNS = [
        re.compile(r'<html[^>]*><body[^>]*></body></html>', re.IGNORECASE),
        re.compile(r'<html[^>]*></html>', re.IGNORECASE),
    ]
    
    @classmethod
    def classify_response(
        cls,
        http_status_code: int,
        headers: Dict[str, str],
        content: Optional[str] = None,
        response_time: Optional[float] = None
    ) -> ResponseClassification:
        """
        Clasifica una respuesta HTTP según su estado, encabezados y contenido.
        
        Args:
            http_status_code: Código de estado HTTP
            headers: Encabezados HTTP
            content: Contenido de la respuesta (opcional)
            response_time: Tiempo de respuesta en segundos
            
        Returns:
            ResponseClassification: Clasificación de la respuesta
        """
        # Inicializar clasificación por defecto
        classification = ResponseClassification(
            status=ResponseStatus.SUCCESS,
            protection_type=ProtectionType.NONE,
            http_status_code=http_status_code,
            headers=headers,
            response_time=response_time
        )
        
        # Verificar código de estado HTTP
        if http_status_code == 403:
            classification.status = ResponseStatus.DATA_DOME_CHALLENGE
            classification.protection_type = ProtectionType.DATADOME
            classification.is_accessible = False
            
        elif http_status_code == 429:
            classification.status = ResponseStatus.ERROR
            classification.protection_type = ProtectionType.RATE_LIMIT
            
        elif http_status_code in [408, 504]:
            classification.status = ResponseStatus.ERROR
            classification.protection_type = ProtectionType.TIMEOUT
            
        elif http_status_code >= 500:
            classification.status = ResponseStatus.ERROR
            classification.protection_type = ProtectionType.CONNECTION_ERROR
            
        elif http_status_code in [301, 302, 307, 308]:
            classification.status = ResponseStatus.REDIRECT
            classification.protection_type = ProtectionType.NONE
            
        # Verificar encabezados para protección anti-bot
        for header_name, header_value in headers.items():
            header_value_lower = header_value.lower()
            
            # Detectar DataDome
            if any(pattern.search(header_value_lower) for pattern in ResponseClassifier.DATADOME_PATTERNS):
                classification.status = ResponseStatus.DATA_DOME_CHALLENGE
                classification.protection_type = ProtectionType.DATADOME
                
            # Detectar CAPTCHA
            elif any(pattern.search(header_value_lower) for pattern in ResponseClassifier.CAPTCHA_PATTERNS):
                classification.status = ResponseStatus.CAPTCHA
                classification.protection_type = ProtectionType.CAPTCHA
                
            # Detectar acceso denegado
            elif any(pattern.search(header_value_lower) for pattern in ResponseClassifier.ACCESS_DENIED_PATTERNS):
                classification.status = ResponseStatus.ERROR
                classification.protection_type = ProtectionType.ACCESS_DENIED
                
        # Verificar contenido para protección anti-bot
        if content:
            content_lower = content.lower()
            
            # Detectar DataDome en el cuerpo de la respuesta
            if any(pattern.search(content_lower) for pattern in ResponseClassifier.DATADOME_PATTERNS):
                classification.status = ResponseStatus.DATA_DOME_CHALLENGE
                classification.protection_type = ProtectionType.DATADOME
                classification.is_accessible = False
                
            # Detectar CAPTCHA en el cuerpo de la respuesta
            elif any(pattern.search(content_lower) for pattern in ResponseClassifier.CAPTCHA_PATTERNS):
                classification.status = ResponseStatus.ERROR
                classification.protection_type = ProtectionType.CAPTCHA
                classification.is_accessible = False
                
            # Detectar páginas vacías o inválidas
            elif any(pattern.match(content_lower) for pattern in ResponseClassifier.EMPTY_RESPONSE_PATTERNS):
                classification.status = ResponseStatus.EMPTY_CONTENT
                classification.protection_type = ProtectionType.NONE
                classification.is_content_valid = False
        else:
            # Si no hay contenido, se marca como no accesible y sin contenido válido
            classification.is_accessible = False
            classification.is_content_valid = False
            classification.evidence.append("Empty content detected")
                
        return classification