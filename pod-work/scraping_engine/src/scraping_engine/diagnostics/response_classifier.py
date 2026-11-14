"""
Clasificador de respuestas HTTP para identificar protección y estado de acceso.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class ResponseStatus(Enum):
    """Estados posibles de una respuesta HTTP."""
    OK = "ok"
    DATA_DOME_CHALLENGE = "data_dome_challenge"
    CAPTCHA = "captcha"
    ACCESS_DENIED = "access_denied"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    SERVER_ERROR = "server_error"
    REDIRECT = "redirect"
    EMPTY_RESPONSE = "empty_response"
    UNEXPECTED_CONTENT = "unexpected_content"
    PROXY_ERROR = "proxy_error"
    TLS_ERROR = "tls_error"

@dataclass
class ResponseClassification:
    """Clasificación de una respuesta HTTP."""
    status_code: int
    http_status_code: int  # Código HTTP real
    is_accessible: bool  # Indica si el contenido es accesible
    protection_type: Optional[ResponseStatus] = None
    content_length: int = 0
    headers: Optional[dict] = None
    error_message: Optional[str] = None

    @property
    def status(self) -> ResponseStatus:
        return self.protection_type

    def __init__(self, status_code: int, http_status_code: int, is_accessible: bool, 
                 protection_type: Optional[ResponseStatus], content_length: int, headers: dict):
        self.status_code = status_code
        self.http_status_code = http_status_code
        self.is_accessible = is_accessible
        self.protection_type = protection_type
        self.content_length = content_length
        self.headers = headers

class ResponseClassifier:
    """Clasificador de respuestas HTTP."""
    
    @staticmethod
    def classify(status_code: int, content: str, headers: dict = None) -> ResponseClassification:
        """
        Clasifica una respuesta HTTP según su código, contenido y encabezados.
        
        Args:
            status_code: Código HTTP de la respuesta
            content: Contenido de la respuesta
            headers: Encabezados de la respuesta
            
        Returns:
            ResponseClassification con la clasificación
        """
        # Inicializar clasificación
        classification = ResponseClassification(
            status_code=status_code,
            http_status_code=status_code,
            is_accessible=False,
            protection_type=None,
            content_length=len(content) if content else 0,
            headers=headers or {}
        )
        
        # Verificar errores de conexión o timeout
        if not content:
            classification.is_accessible = False
            classification.protection_type = ResponseStatus.EMPTY_RESPONSE
            return classification
            
        # Verificar código HTTP específico
        if status_code == 403:
            # Verificar si es un desafío DataDome
            if ResponseClassifier._is_data_dome_challenge(content, headers):
                classification.is_accessible = False
                classification.protection_type = ResponseStatus.DATA_DOME_CHALLENGE
                return classification
            elif ResponseClassifier._is_captcha(content, headers):
                classification.is_accessible = False
                classification.protection_type = ResponseStatus.CAPTCHA
                return classification
            else:
                classification.is_accessible = False
                classification.protection_type = ResponseStatus.ACCESS_DENIED
                return classification
                
        elif status_code == 429:
            classification.is_accessible = False
            classification.protection_type = ResponseStatus.REDIRECT
            return classification
            
        elif status_code in [500, 502, 503, 504]:
            classification.is_accessible = False
            classification.protection_type = ResponseStatus.SERVER_ERROR
            return classification
            
        elif status_code >= 300 and status_code < 400:
            classification.is_accessible = True
            classification.protection_type = ResponseStatus.REDIRECT
            return classification
            
        elif status_code == 200:
            # Verificar si el contenido es útil
            if ResponseClassifier._is_empty_content(content):
                classification.is_accessible = False
                classification.protection_type = ResponseStatus.EMPTY_RESPONSE
                return classification
            elif ResponseClassifier._is_challenge_content(content):
                classification.is_accessible = False
                classification.protection_type = ResponseStatus.DATA_DOME_CHALLENGE
                return classification
            else:
                classification.is_accessible = True
                classification.protection_type = ResponseStatus.OK
                return classification
                
        # Otros códigos HTTP
        if status_code >= 400:
            classification.is_accessible = False
            classification.protection_type = ResponseStatus.UNEXPECTED_CONTENT
            return classification
            
        # Código 200 o similar, contenido útil
        classification.is_accessible = True
        classification.protection_type = ResponseStatus.OK
        return classification

    @staticmethod
    def classify_response(status_code: int, content: str, headers: dict = None, response_time: float = None) -> ResponseClassification:
        """Alias para classify para mantener compatibilidad con tests."""
        return ResponseClassifier.classify(status_code, content, headers)
        
    @staticmethod
    def _is_data_dome_challenge(content: str, headers: dict) -> bool:
        """Verifica si la respuesta es un desafío DataDome."""
        # Verificar encabezados típicos de DataDome
        if headers:
            for key, value in headers.items():
                if "datadome" in key.lower() or "datadome" in value.lower():
                    return True
                    
        # Verificar contenido HTML típico de DataDome
        content_lower = content.lower()
        data_dome_indicators = [
            r'datadome',
            r'datadome\.io',
            r'cloudflare.*challenge',
            r'blocked by datadome',
            r'datadome.*captcha'
        ]
        
        for pattern in data_dome_indicators:
            if re.search(pattern, content_lower):
                return True
                
        return False
        
    @staticmethod
    def _is_captcha(content: str, headers: dict) -> bool:
        """Verifica si la respuesta contiene un CAPTCHA."""
        # Verificar encabezados de CAPTCHA
        if headers:
            for key, value in headers.items():
                if "captcha" in key.lower() or "captcha" in value.lower():
                    return True
                    
        # Verificar contenido HTML típico de CAPTCHA
        content_lower = content.lower()
        captcha_indicators = [
            r'<.*captcha.*>',
            r'captcha',
            r'google.*recaptcha',
            r'hcaptcha'
        ]
        
        for pattern in captcha_indicators:
            if re.search(pattern, content_lower):
                return True
                
        return False
        
    @staticmethod
    def _is_empty_content(content: str) -> bool:
        """Verifica si el contenido está vacío o es inválido."""
        if not content:
            return True
            
        stripped = content.strip()
        if len(stripped) == 0:
            return True
            
        # Si el contenido tiene más de 30 caracteres y no es solo HTML básico, considerarlo útil
        if len(stripped) > 30:
            return False
            
        # Si el contenido tiene entre 1 y 30 caracteres, verificar si es útil
        if 1 <= len(stripped) <= 30:
            # Verificar si contiene texto significativo (no solo etiquetas HTML)
            clean_content = re.sub(r'<[^>]+>', '', stripped)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            # Si el contenido limpio tiene más de 5 caracteres, considerarlo útil
            if len(clean_content) > 5:
                return False
                
        # Si llegamos aquí, es porque el contenido es corto y no tiene texto significativo
        return True

    @staticmethod
    def _is_data_dome_challenge(content: str, headers: dict) -> bool:
        """Verifica si la respuesta es un desafío DataDome."""
        # Verificar encabezados típicos de DataDome
        if headers:
            for key, value in headers.items():
                if "datadome" in key.lower() or "datadome" in value.lower():
                    return True
                    
        # Verificar contenido HTML típico de DataDome
        content_lower = content.lower()
        data_dome_indicators = [
            r'datadome',
            r'datadome\.io',
            r'cloudflare.*challenge',
            r'blocked by datadome',
            r'datadome.*captcha'
        ]
        
        for pattern in data_dome_indicators:
            if re.search(pattern, content_lower):
                return True
                
        # Verificar contenido específico de DataDome
        datadome_indicators = [
            'datadome',
            'cloudflare',
            'captcha',
            'challenge',
            'blocked'
        ]
        
        for indicator in datadome_indicators:
            if indicator in content_lower:
                return True
                
        return False
        
    @staticmethod
    def _is_challenge_content(content: str) -> bool:
        """Verifica si el contenido es un desafío de protección."""
        content_lower = content.lower()
        
        challenge_indicators = [
            r'challenge.*required',
            r'access.*denied',
            r'blocked.*access',
            r'security.*check',
            r'please.*verify',
            r'verify.*you.*are.*human'
        ]
        
        for pattern in challenge_indicators:
            if re.search(pattern, content_lower):
                return True
                
        return False