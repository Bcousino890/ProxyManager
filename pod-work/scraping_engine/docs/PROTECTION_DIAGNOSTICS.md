# Diagnóstico de Protecciones Anti-Bot

## Descripción

Este módulo implementa un sistema extensible para identificar y clasificar diferentes tipos de protección anti-bot, especialmente DataDome y otras soluciones similares.

## Clasificación de Respuestas

### Estados HTTP

- **200 OK**: Posible contenido útil o desafío
- **403 Forbidden**: Acceso denegado (posiblemente DataDome)
- **429 Too Many Requests**: Rate limiting
- **503 Service Unavailable**: Protección temporal

### Tipos de Protección Detectada

1. **DataDome Challenge**
   - Respuestas con contenido de desafío DataDome
   - Encabezados específicos de DataDome
   - Patrones en el HTML de verificación

2. **CAPTCHA**
   - Páginas con CAPTCHA visible
   - Formularios de verificación
   - Scripts de detección

3. **Access Denied Pages**
   - Páginas de acceso denegado estándar
   - Mensajes específicos de bloqueo

4. **Empty Responses**
   - HTML vacío o incompleto
   - Respuestas sin contenido útil

## Mecanismos de Detección

### 1. Análisis de Encabezados HTTP

- Verificación de encabezados específicos de protección
- Identificación de patrones en User-Agent
- Comprobación de encabezados de seguridad

### 2. Análisis del Contenido HTML

- Búsqueda de scripts de detección
- Identificación de elementos característicos de DataDome
- Análisis de estructura de páginas de desafío

### 3. Métricas de Respuesta

- Tiempo de respuesta anormal
- Tamaño de respuesta inusual
- Patrones de redirección

## Clasificador de Protección

El clasificador `ResponseClassifier` en `src/scraping_engine/diagnostics/response_classifier.py` proporciona:

```python
from scraping_engine.diagnostics.response_classifier import ResponseClassifier

classifier = ResponseClassifier()
protection_type = classifier.classify(response)
```

## Evidencia Registrada

El sistema registra evidencias sin almacenar secretos ni información sensible:

- Headers HTTP recibidos
- Contenido HTML de respuesta
- Tiempos de respuesta
- IP de salida utilizada
- Código de estado HTTP

## Extensibilidad

El sistema está diseñado para ser extendido con nuevos detectores:

1. Crear nuevo detector en `src/scraping_engine/diagnostics/`
2. Registrar el detector en el clasificador
3. Añadir pruebas específicas

## Uso en el Motor

Los motores de scraping utilizan este diagnóstico automáticamente para:

- Determinar si una respuesta es accesible
- Decidir si se requiere un proxy o sesión diferente
- Registrar información para análisis posterior