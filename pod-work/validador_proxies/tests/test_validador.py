import pytest
from validador_proxies import validar_proxy, Proxy

def test_validacion_correcta():
    """Prueba una cadena de proxy válida."""
    resultado = validar_proxy("192.168.1.1:8080:usuario1:clave1")
    assert resultado == Proxy(host="192.168.1.1", port=8080, username="usuario1", password="clave1")

def test_puerto_invalido():
    """Prueba un puerto inválido."""
    with pytest.raises(ValueError, match="El puerto debe estar entre 1 y 65535"):
        validar_proxy("192.168.1.1:70000:usuario1:clave1")

def test_puerto_no_numerico():
    """Prueba un puerto que no es numérico."""
    with pytest.raises(ValueError, match="El puerto debe ser un número entero"):
        validar_proxy("192.168.1.1:puerto:usuario1:clave1")

def test_formato_invalido():
    """Prueba un formato inválido (más de 4 partes)."""
    with pytest.raises(ValueError, match="Formato inválido"):
        validar_proxy("192.168.1.1:8080:usuario1:clave1:extra")

def test_formato_invalido_menos_partes():
    """Prueba un formato inválido (menos de 4 partes)."""
    with pytest.raises(ValueError, match="Formato inválido"):
        validar_proxy("192.168.1.1:8080:usuario1")

def test_host_vacio():
    """Prueba host vacío."""
    with pytest.raises(ValueError, match="El host no puede estar vacío"):
        validar_proxy(":8080:usuario1:clave1")

def test_usuario_vacio():
    """Prueba usuario vacío."""
    with pytest.raises(ValueError, match="El nombre de usuario no puede estar vacío"):
        validar_proxy("192.168.1.1:8080::clave1")

def test_clave_vacia():
    """Prueba clave vacía."""
    with pytest.raises(ValueError, match="La contraseña no puede estar vacía"):
        validar_proxy("192.168.1.1:8080:usuario1:")

def test_tipo_invalido():
    """Prueba tipo inválido."""
    with pytest.raises(ValueError, match="El proxy debe ser una cadena de texto"):
        validar_proxy(12345)