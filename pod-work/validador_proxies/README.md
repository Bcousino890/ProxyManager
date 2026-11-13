# Validador de Proxies

Este proyecto contiene una función que valida proxies en formato `host:puerto:usuario:clave`.

## Características

- Valida el formato del proxy
- Verifica que el puerto sea un número válido entre 1 y 65535
- Asegura que todos los campos estén presentes
- Proporciona mensajes de error claros en caso de fallo

## Instalación

```bash
pip install -e .
```

## Uso

```python
from validador_proxies import validar_proxy

proxy = "192.168.1.1:8080:user:pass"
resultado = validar_proxy(proxy)
print(resultado)  # Proxy válido
```

## Pruebas

Ejecutar pruebas con pytest:

```bash
pytest
```