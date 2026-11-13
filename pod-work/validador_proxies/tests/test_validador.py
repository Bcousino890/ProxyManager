import pytest
from validador_proxies.validador import validar_proxy

def test_proxy_valido():
    """Prueba un proxy válido"""
    resultado = validar_proxy("192.168.1.1:8080:user:pass")
    assert resultado["valido"] is True
    assert resultado["error"] is None

def test_formato_invalido_muchos_campos():
    """Prueba formato con demasiados campos"""
    resultado = validar_proxy("192.168.1.1:8080:user:pass:extra")
    assert resultado["valido"] is False
    assert "Formato inválido" in resultado["error"]

def test_formato_invalido_pocos_campos():
    """Prueba formato con pocos campos"""
    resultado = validar_proxy("192.168.1.1:8080:user")
    assert resultado["valido"] is False
    assert "Formato inválido" in resultado["error"]

def test_puerto_no_es_numero():
    """Prueba puerto que no es número"""
    resultado = validar_proxy("192.168.1.1:puerto:user:pass")
    assert resultado["valido"] is False
    assert "debe ser un número válido" in resultado["error"]

def test_puerto_fuera_rango():
    """Prueba puerto fuera de rango"""
    resultado = validar_proxy("192.168.1.1:99999:user:pass")
    assert resultado["valido"] is False
    assert "Puerto inválido" in resultado["error"]

def test_puerto_minimo_valido():
    """Prueba puerto mínimo válido"""
    resultado = validar_proxy("192.168.1.1:1:user:pass")
    assert resultado["valido"] is True

def test_puerto_maximo_valido():
    """Prueba puerto máximo válido"""
    resultado = validar_proxy("192.168.1.1:65535:user:pass")
    assert resultado["valido"] is True

def test_host_vacio():
    """Prueba host vacío"""
    resultado = validar_proxy(":8080:user:pass")
    assert resultado["valido"] is False
    assert "El host no puede estar vacío" in resultado["error"]

def test_usuario_vacio():
    """Prueba usuario vacío"""
    resultado = validar_proxy("192.168.1.1:8080::pass")
    assert resultado["valido"] is False
    assert "El usuario no puede estar vacío" in resultado["error"]

def test_clave_vacia():
    """Prueba clave vacía"""
    resultado = validar_proxy("192.168.1.1:8080:user:")
    assert resultado["valido"] is False
    assert "La clave no puede estar vacía" in resultado["error"]

def test_tipo_invalido():
    """Prueba tipo de dato inválido"""
    resultado = validar_proxy(12345)
    assert resultado["valido"] is False
    assert "debe ser una cadena de texto" in resultado["error"]