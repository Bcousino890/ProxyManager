# Arquitectura del Motor de Scraping

## Visión General

El motor de scraping está diseñado para ser modular, robusto y portable. Se compone de múltiples capas que trabajan en conjunto para proporcionar una solución completa de extracción de datos.

## Estructura Modular

### 1. API
- **Rutas principales**: `/health`, `/ready`, `/scrape`, `/jobs/{id}`, etc.
- **Autenticación**: Basada en API keys
- **Validación**: Entradas y salidas tipadas
- **Protección**: SSRF, rate limiting, restricciones de destino

### 2. Motores de Scraping
- **HTTP Engine**: Basado en `httpx` para solicitudes asíncronas
- **Browser Engine**: Basado en `Playwright` para navegación completa

### 3. Gestión de Proxies
- **Proxy Manager**: Gestiona endpoints Decodo
- **Health Checks**: Verificación de conectividad y autenticación
- **Distribución**: Balanceo de solicitudes

### 4. Sesiones
- **Gestor de Sesiones**: Manejo seguro de cookies y sesiones autorizadas
- **Aislamiento**: Sesiones independientes por usuario/trabajo

### 5. Diagnóstico de Protecciones
- **Response Classifier**: Clasificación de respuestas HTTP
- **Protection Detector**: Detección de DataDome, CAPTCHA, etc.
- **Evidence Logger**: Registro de evidencias sin almacenar secretos

### 6. Extractores
- **Genéricos**: HTML, texto, metaetiquetas, enlaces
- **Inmobiliarios**: Datos específicos de inmuebles (Idealista)

### 7. Trabajos y Persistencia
- **Job Manager**: Cola de trabajos con estados
- **Worker**: Ejecución de trabajos
- **Storage**: Persistencia en SQLite

### 8. Integraciones
- **Proveedores Autorizados**: Acceso autorizado a sitios bloqueados
- **Extensibilidad**: Sistema para nuevos adaptadores

## Flujo Principal

1. El usuario envía una solicitud de scraping
2. La API recibe y valida la solicitud
3. Se crea un trabajo en la cola
4. El worker procesa el trabajo usando motores adecuados
5. Se utilizan proxies si es necesario
6. Se detectan protecciones anti-bot
7. Se extrae información usando extractores
8. Los resultados se almacenan y devuelven

## Características Clave

- **Robustez**: Manejo de errores, reintentos, timeouts
- **Seguridad**: Gestión segura de sesiones y credenciales
- **Escalabilidad**: Concurrencia controlada
- **Portabilidad**: Dockerización completa
- **Extensibilidad**: Interfaces claras para nuevos motores o extractores