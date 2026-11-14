"""Pruebas unitarias para el gestor de sesiones."""

import pytest
from datetime import datetime, timedelta

from sessions.manager import SessionManager, Session
from sessions.cookies import CookieJar


def test_cookie_jar():
    """Prueba el gestor de cookies."""
    jar = CookieJar()
    
    # Añadir una cookie
    jar.set_cookie("session_id", "abc123")
    assert jar.get_cookie("session_id") == "abc123"
    
    # Obtener todas las cookies
    all_cookies = jar.get_all_cookies()
    assert all_cookies["session_id"] == "abc123"
    
    # Encabezado de cookie
    cookie_header = jar.get_cookie_header()
    assert "session_id=abc123" in cookie_header
    
    # Eliminar cookie
    jar.delete_cookie("session_id")
    assert jar.get_cookie("session_id") is None
    
    # Limpiar
    jar.set_cookie("test", "value")
    jar.clear()
    assert len(jar) == 0


def test_session():
    """Prueba la clase Session."""
    session = Session(id="test_session")
    
    assert session.id == "test_session"
    assert not session.is_expired()
    
    # Verificar expiración
    future_time = datetime.now() + timedelta(seconds=1)
    session.expires_at = future_time
    
    # Debe ser válida
    assert not session.is_expired()
    
    # Actualizar última utilización
    old_last_used = session.last_used
    session.update_last_used()
    assert session.last_used != old_last_used


def test_session_manager():
    """Prueba el gestor de sesiones."""
    manager = SessionManager(session_timeout=10)
    
    # Crear sesión
    session = manager.create_session("test1", {"cookie1": "value1"})
    assert session.id == "test1"
    assert session.cookies.get_cookie("cookie1") == "value1"
    
    # Obtener sesión
    retrieved_session = manager.get_session("test1")
    assert retrieved_session is not None
    assert retrieved_session.id == "test1"
    
    # Verificar expiración
    session.expires_at = datetime.now() - timedelta(seconds=1)
    expired_session = manager.get_session("test1")
    assert expired_session is None
    
    # Contador de sesiones activas
    manager2 = SessionManager()
    manager2.create_session("session1")
    manager2.create_session("session2")
    assert manager2.get_active_sessions_count() == 2
    
    # Limpieza de sesiones expiradas
    manager3 = SessionManager(session_timeout=0)
    manager3.create_session("expired")
    manager3.cleanup_expired_sessions()
    assert manager3.get_active_sessions_count() == 0


def test_session_manager_with_metadata():
    """Prueba el gestor de sesiones con metadatos."""
    metadata = {"user_agent": "test-agent", "source": "scraping"}
    session = Session(id="meta_test", metadata=metadata)
    
    assert session.metadata["user_agent"] == "test-agent"
    assert session.metadata["source"] == "scraping"