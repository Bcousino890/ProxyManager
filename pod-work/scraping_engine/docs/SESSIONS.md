# Gestión de Sesiones

## Descripción

La gestión de sesiones es una capa independiente que permite el manejo seguro y eficiente de cookies y sesiones autorizadas en el motor de scraping.

## Funcionalidades

### 1. Creación de Sesiones

- Generar identificadores únicos para cada sesión
- Almacenar cookies de manera segura
- Asociar sesiones a trabajos específicos

### 2. Recuperación y Expiración

- Recuperar sesiones existentes por ID
- Expirar sesiones automáticamente tras un tiempo
- Eliminar sesiones expiradas periódicamente

### 3. Aislamiento

- Sesiones independientes por usuario/trabajo
- Evitar reutilización indebida de cookies
- Manejo seguro de sesiones autorizadas

## Implementación

### Session Manager

El gestor de sesiones se encuentra en `src/scraping_engine/sessions/manager.py`:

```python
from scraping_engine.sessions.manager import SessionManager

# Inicializar
session_manager = SessionManager()

# Crear sesión
session_id = session_manager.create_session()

# Recuperar sesión
session = session_manager.get_session(session_id)

# Expirar sesión
session_manager.expire_session(session_id)
```

### Uso en Motores

Las sesiones se utilizan automáticamente en los motores de scraping cuando se requiere autenticación:

```python
# En un motor HTTP
session = session_manager.get_session(job_id)
cookies = session.cookies

response = httpx.get(url, cookies=cookies)
```

## Persistencia

Las sesiones se almacenan en la base de datos SQLite para mantener su estado entre reinicios del sistema.

## Seguridad

- Las cookies se almacenan cifradas
- No se comparten sesiones entre usuarios
- Se implementan mecanismos de expiración automática