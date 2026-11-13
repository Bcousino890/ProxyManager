# Validador de Proxies

Un validador simple para proxies en formato `host:puerto:usuario:clave`.

## Instalación

```bash
cd /ProxyManager/pod-work/validador_proxies
pip install -e .
```

## Uso

```python
from validador_proxies import validar_proxy

proxy = validar_proxy("192.168.1.1:8080:usuario1:clave1")
print(proxy.host)   # 192.168.1.1
print(proxy.port)   # 8080
print(proxy.username)  # usuario1
print(proxy.password)  # clave1
```

## Pruebas

Ejecutar pruebas con pytest:

```bash
cd /ProxyManager/pod-work/validador_proxies
pytest
```

## Validaciones

- El proxy debe tener exactamente 4 partes separadas por `:`
- El puerto debe ser un número entre 1 y 65535
- Ningún campo puede estar vacío
- El proxy debe ser una cadena de texto