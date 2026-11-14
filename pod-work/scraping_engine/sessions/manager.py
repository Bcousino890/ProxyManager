"""Gestor de sesiones para scraping autorizado."""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .cookies import CookieJar


@dataclass
class Session:
    """Representa una sesión de scraping."""
    
    id: str
    cookies: CookieJar = field(default_factory=CookieJar)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Verifica si la sesión ha expirado."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def update_last_used(self):
        """Actualiza la marca de tiempo de última utilización."""
        self.last_used = datetime.now()


class SessionManager:
    """Gestor centralizado de sesiones."""
    
    def __init__(self, session_timeout: int = 3600):
        """
        Inicializa el gestor de sesiones.
        
        Args:
            session_timeout (int): Tiempo de expiración en segundos (por defecto 1 hora)
        """
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = session_timeout
        
    def create_session(self, session_id: str, cookies: Optional[Dict[str, str]] = None, 
                      metadata: Optional[Dict[str, Any]] = None) -> Session:
        """
        Crea una nueva sesión.
        
        Args:
            session_id (str): ID único de la sesión
            cookies (Optional[Dict[str, str]]): Cookies iniciales
            metadata (Optional[Dict[str, Any]]): Metadatos adicionales
            
        Returns:
            Session: La sesión creada
        """
        expires_at = datetime.now() + timedelta(seconds=self.session_timeout)
        session = Session(
            id=session_id,
            cookies=CookieJar(cookies) if cookies else CookieJar(),
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Obtiene una sesión por su ID.
        
        Args:
            session_id (str): ID de la sesión
            
        Returns:
            Optional[Session]: La sesión si existe y no ha expirado, None en caso contrario
        """
        session = self.sessions.get(session_id)
        if session and not session.is_expired():
            session.update_last_used()
            return session
        elif session:
            # Eliminar sesión expirada
            del self.sessions[session_id]
        return None
    
    def delete_session(self, session_id: str):
        """
        Elimina una sesión.
        
        Args:
            session_id (str): ID de la sesión a eliminar
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Limpia las sesiones expiradas."""
        current_time = datetime.now()
        expired_ids = [
            sid for sid, session in self.sessions.items() 
            if session.is_expired()
        ]
        
        for sid in expired_ids:
            del self.sessions[sid]
    
    def get_active_sessions_count(self) -> int:
        """Obtiene el número de sesiones activas."""
        self.cleanup_expired_sessions()
        return len(self.sessions)