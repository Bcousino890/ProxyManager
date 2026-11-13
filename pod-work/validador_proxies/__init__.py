"""
Validador de proxies en formato host:puerto:usuario:clave.
"""
from typing import NamedTuple

class Proxy(NamedTuple):
    """Representa un proxy validado."""
    host: str
    port: int
    username: str
    password: str

def validar_proxy(proxy_str: str) -> Proxy:
    """
    Valida un proxy en formato 'host:puerto:usuario:clave'.
    
    Args:
        proxy_str: Cadena con el proxy en formato host:puerto:usuario:clave
        
    Returns:
        Proxy: Objeto Proxy validado
        
    Raises:
        ValueError: Si el proxy no es válido
    """
    if not isinstance(proxy_str, str):
        raise ValueError("El proxy debe ser una cadena de texto")
        
    partes = proxy_str.split(':')
    
    if len(partes) != 4:
        raise ValueError(f"Formato inválido. Se esperaban 4 partes separadas por ':', se recibieron {len(partes)}")
        
    host, port_str, username, password = partes
    
    # Validar puerto
    try:
        port = int(port_str)
    except ValueError:
        raise ValueError("El puerto debe ser un número entero")
        
    if not (1 <= port <= 65535):
        raise ValueError("El puerto debe estar entre 1 y 65535")
        
    # Validar que no haya campos vacíos
    if not host:
        raise ValueError("El host no puede estar vacío")
        
    if not username:
        raise ValueError("El nombre de usuario no puede estar vacío")
        
    if not password:
        raise ValueError("La contraseña no puede estar vacía")
        
    return Proxy(host=host, port=port, username=username, password=password)