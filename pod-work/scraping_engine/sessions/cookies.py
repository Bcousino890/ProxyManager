"""Gestor de cookies para sesiones de scraping."""

import http.cookies
from typing import Dict, Optional, Union
from datetime import datetime


class CookieJar:
    """Almacén de cookies seguro."""
    
    def __init__(self, initial_cookies: Optional[Dict[str, str]] = None):
        """
        Inicializa el almacén de cookies.
        
        Args:
            initial_cookies (Optional[Dict[str, str]]): Cookies iniciales
        """
        self._cookies: Dict[str, Dict[str, Union[str, int]]] = {}
        if initial_cookies:
            for name, value in initial_cookies.items():
                self.set_cookie(name, value)
    
    def set_cookie(self, name: str, value: str, domain: Optional[str] = None,
                   path: str = "/", secure: bool = False, http_only: bool = False,
                   expires: Optional[datetime] = None):
        """
        Establece una cookie.
        
        Args:
            name (str): Nombre de la cookie
            value (str): Valor de la cookie
            domain (Optional[str]): Dominio
            path (str): Ruta
            secure (bool): Si es segura
            http_only (bool): Si es solo HTTP
            expires (Optional[datetime]): Fecha de expiración
        """
        cookie_data = {
            'value': value,
            'domain': domain,
            'path': path,
            'secure': secure,
            'http_only': http_only
        }
        
        if expires:
            cookie_data['expires'] = int(expires.timestamp())
            
        self._cookies[name] = cookie_data
    
    def get_cookie(self, name: str) -> Optional[str]:
        """
        Obtiene el valor de una cookie.
        
        Args:
            name (str): Nombre de la cookie
            
        Returns:
            Optional[str]: Valor de la cookie o None
        """
        cookie_data = self._cookies.get(name)
        return cookie_data['value'] if cookie_data else None
    
    def get_all_cookies(self) -> Dict[str, str]:
        """
        Obtiene todas las cookies como un diccionario.
        
        Returns:
            Dict[str, str]: Diccionario de cookies
        """
        return {name: data['value'] for name, data in self._cookies.items()}
    
    def get_cookie_header(self) -> str:
        """
        Obtiene el encabezado Cookie para HTTP.
        
        Returns:
            str: Encabezado Cookie
        """
        cookies = self.get_all_cookies()
        if not cookies:
            return ""
            
        cookie_parts = []
        for name, value in cookies.items():
            cookie_parts.append(f"{name}={value}")
            
        return "; ".join(cookie_parts)
    
    def delete_cookie(self, name: str):
        """
        Elimina una cookie.
        
        Args:
            name (str): Nombre de la cookie
        """
        if name in self._cookies:
            del self._cookies[name]
    
    def clear(self):
        """Limpia todas las cookies."""
        self._cookies.clear()
    
    def __len__(self) -> int:
        """Obtiene el número de cookies."""
        return len(self._cookies)
    
    def __bool__(self) -> bool:
        """Verifica si hay cookies."""
        return len(self._cookies) > 0