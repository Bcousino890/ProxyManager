# Gestor de Proxies

## Descripción

El gestor de proxies es una capa fundamental del motor de scraping que permite la gestión y uso eficiente de proxies para evitar bloqueos y distribuir solicitudes.

## Funcionalidades

### 1. Gestión de Endpoints Decodo

- **Adición**: Añadir nuevos endpoints ISP
- **Eliminación**: Remover endpoints obsoletos
- **Selección**: Seleccionar proxy aleatorio o por criterio
- **Verificación**: Comprobar conectividad y autenticación

### 2. Health Checks

- **Conectividad**: Verificar acceso al endpoint
- **Autenticación**: Validar credenciales
- **Latencia**: Medir tiempo de respuesta
- **IP de Salida**: Obtener dirección IP real

### 3. Distribución de Solicitudes

- **Balanceo**: Distribuir solicitudes entre proxies activos
- **Límites de Concurrencia**: Controlar uso concurrente
- **Reintentos**: Reintentar con otro proxy en caso de fallo

## Configuración

Los endpoints Decodo se definen en `src/scraping_engine/proxies/config.py`:

```python
DECODO_ENDPOINTS = [
    "isp.decodo.com:10001",
    "isp.decodo.com:10002",
    # ... más endpoints
]
```

Las credenciales deben estar en variables de entorno:
- `DECODO_USER`
- `DECODO_PASS`

## Uso en el Motor

El gestor se integra automáticamente en los motores de scraping:

```python
from scraping_engine.proxies.manager import ProxyManager

# Inicializar
proxy_manager = ProxyManager()

# Obtener proxy
proxy = proxy_manager.get_proxy()

# Usar en solicitud HTTP
response = httpx.get(url, proxies={"http://": proxy, "https://": proxy})
```

## Estado del Sistema

El estado actual se puede verificar mediante el endpoint `/proxies/status`.

## Limitaciones

- No asume que diez endpoints representan diez IPs distintas
- No almacena credenciales en GitHub
- Requiere acceso a los endpoints Decodo para funcionar correctamente