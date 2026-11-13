def validar_proxy(proxy_str):
    """
    Valida un proxy en formato host:puerto:usuario:clave.
    
    Args:
        proxy_str (str): Proxy en formato host:puerto:usuario:clave
        
    Returns:
        dict: Diccionario con 'valido' (bool) y 'error' (str) si aplica
        
    Example:
        >>> validar_proxy("192.168.1.1:8080:user:pass")
        {'valido': True, 'error': None}
        
        >>> validar_proxy("192.168.1.1:99999:user:pass")
        {'valido': False, 'error': 'Puerto inválido: 99999'}
    """
    if not isinstance(proxy_str, str):
        return {"valido": False, "error": "El proxy debe ser una cadena de texto"}
    
    partes = proxy_str.split(":")
    
    if len(partes) != 4:
        return {"valido": False, "error": f"Formato inválido. Se esperaban 4 partes separadas por ':', se recibieron {len(partes)}"}
    
    host, puerto, usuario, clave = partes
    
    # Validar que el puerto sea un número
    try:
        puerto_num = int(puerto)
    except ValueError:
        return {"valido": False, "error": f"El puerto debe ser un número válido: {puerto}"}
    
    # Validar rango del puerto
    if not (1 <= puerto_num <= 65535):
        return {"valido": False, "error": f"Puerto inválido: {puerto_num}. Debe estar entre 1 y 65535"}
    
    # Validar que todos los campos estén presentes
    if not host:
        return {"valido": False, "error": "El host no puede estar vacío"}
        
    if not usuario:
        return {"valido": False, "error": "El usuario no puede estar vacío"}
        
    if not clave:
        return {"valido": False, "error": "La clave no puede estar vacía"}
    
    return {"valido": True, "error": None}