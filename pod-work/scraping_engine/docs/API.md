# Documentación de la API

## Endpoints Principales

### `/health` - Verificación de Salud

**GET** `/health`

Verifica que el servicio esté funcionando correctamente.

**Respuesta Exitosa:**
```json
{
  "status": "healthy",
  "timestamp": "2026-11-14T03:48:00Z"
}
```

### `/ready` - Verificación de Preparación

**GET** `/ready`

Verifica que el servicio esté listo para recibir solicitudes.

**Respuesta Exitosa:**
```json
{
  "status": "ready",
  "timestamp": "2026-11-14T03:48:00Z"
}
```

### `/scrape` - Iniciar Scraping

**POST** `/scrape`

Inicia un nuevo proceso de scraping.

**Cuerpo de la Solicitud:**
```json
{
  "url": "https://example.com",
  "engine": "http",  // opcional, por defecto "http"
  "use_proxy": true, // opcional, por defecto false
  "headers": {
    "User-Agent": "Mozilla/5.0..."
  },
  "timeout": 30, // segundos
  "max_retries": 3
}
```

**Respuesta Exitosa:**
```json
{
  "job_id": "uuid-12345",
  "status": "queued",
  "url": "https://example.com"
}
```

### `/scrape/batch` - Scraping por Lotes

**POST** `/scrape/batch`

Inicia múltiples procesos de scraping en paralelo.

**Cuerpo de la Solicitud:**
```json
{
  "urls": [
    "https://example.com/page1",
    "https://example.com/page2"
  ],
  "engine": "http",
  "use_proxy": true,
  "headers": {
    "User-Agent": "Mozilla/5.0..."
  }
}
```

**Respuesta Exitosa:**
```json
{
  "job_ids": ["uuid-12345", "uuid-67890"],
  "status": "queued"
}
```

### `/jobs/{id}` - Estado del Trabajo

**GET** `/jobs/{id}`

Obtiene el estado actual de un trabajo.

**Respuesta Exitosa:**
```json
{
  "job_id": "uuid-12345",
  "url": "https://example.com",
  "status": "completed", // queued, running, completed, failed
  "created_at": "2026-11-14T03:48:00Z",
  "updated_at": "2026-11-14T03:48:05Z",
  "result": {
    "content": "<html>...</html>",
    "metadata": {
      "title": "Example Domain",
      "status_code": 200
    }
  }
}
```

### `/jobs/{id}/cancel` - Cancelar Trabajo

**POST** `/jobs/{id}/cancel`

Cancela un trabajo en ejecución.

**Respuesta Exitosa:**
```json
{
  "job_id": "uuid-12345",
  "status": "cancelled"
}
```

### `/proxies/status` - Estado de Proxies

**GET** `/proxies/status`

Obtiene el estado actual de los proxies.

**Respuesta Exitosa:**
```json
{
  "total": 10,
  "active": 8,
  "inactive": 2,
  "endpoints": [
    {
      "url": "isp.decodo.com:10001",
      "status": "active",
      "latency_ms": 150
    }
  ]
}
```

### `/metrics` - Métricas del Sistema

**GET** `/metrics`

Obtiene métricas de rendimiento y uso.

**Respuesta Exitosa:**
```json
{
  "requests_total": 1247,
  "errors_total": 3,
  "active_jobs": 5,
  "proxy_usage": {
    "active": 8,
    "inactive": 2
  }
}
```

### `/history` - Historial de Trabajos

**GET** `/history`

Obtiene el historial de trabajos completados.

**Respuesta Exitosa:**
```json
{
  "jobs": [
    {
      "job_id": "uuid-12345",
      "url": "https://example.com",
      "status": "completed",
      "created_at": "2026-11-14T03:48:00Z",
      "duration_seconds": 5.2
    }
  ]
}
```

## Autenticación

Todos los endpoints requieren un API key en el encabezado `X-API-Key`.

```http
X-API-Key: your_api_key_here
```

## Errores Comunes

### 400 Bad Request
Solicitud inválida.

### 401 Unauthorized
Falta o clave de API incorrecta.

### 403 Forbidden
Acceso denegado por protección anti-bot.

### 429 Too Many Requests
Límite de tasa alcanzado.

### 500 Internal Server Error
Error interno del servidor.