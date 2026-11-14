# Tarea

# MISIÓN CRÍTICA — CONSTRUIR Y PRESERVAR EL MOTOR COMPLETO DE SCRAPING ANTES DE APAGAR RUNPOD

## CONTEXTO

Esta es una CONTINUACIÓN del proyecto existente.

NO empieces desde cero.

El usuario va a apagar permanentemente el pod de RunPod cuando finalice esta fase.

Por tanto, tu misión es construir y preservar una arquitectura de scraping completa, modular, reproducible y transferible a cualquier VPS o servidor.

El trabajo debe quedar disponible en GitHub para continuar posteriormente con Claude Code, otra IA o un desarrollador humano.

Repositorio:

https://github.com/Bcousino890/ProxyManager

Estado de referencia:

- main: fba6a26
- Rama de respaldo: recovery/scraper-20261114-0306
- API: puerto 8000
- Panel: puerto 8002
- Agente Qwen: puerto 8787

Comprueba los hashes actuales antes de modificar archivos.

## OBJETIVO PRIORITARIO

Construir el MOTOR DE SCRAPING COMPLETO.

NO desarrollar dashboards, marketing, suscripciones, diseño visual ni funcionalidades SaaS secundarias.

El usuario necesita disponer de toda la infraestructura técnica necesaria para ejecutar, diagnosticar, mantener y extender un scraper.

El principal caso de estudio es Idealista, cuyo acceso directo actualmente devuelve HTTP 403 con DataDome.

La arquitectura debe admitir mecanismos de acceso autorizados, investigación de compatibilidad y nuevos adaptadores, sin que un bloqueo en un sitio paralice todo el motor.

No declares que DataDome está resuelto si no has obtenido y validado contenido real mediante un acceso permitido.

## FASE 1 — AUDITORÍA Y RESCATE

Antes de escribir código:

1. Inspecciona el repositorio completo.
2. Identifica todos los módulos existentes.
3. Comprueba las ramas Git.
4. Revisa archivos sin commit.
5. Identifica qué archivos están duplicados.
6. Identifica los procesos activos.
7. Revisa dependencias y versiones.
8. Identifica código parcialmente implementado.
9. Conserva todo el trabajo útil.
10. Crea una rama de desarrollo específica.

No elimines modelos Ollama ni datos del pod.

No ejecutes git reset --hard ni git clean -fd.

Crea una copia de seguridad de cualquier cambio que no esté versionado.

## FASE 2 — ARQUITECTURA MODULAR

Organiza el motor mediante interfaces claras.

Estructura propuesta:

scraping_engine/
  api/
    main.py
    routes/
    schemas/
    dependencies/
  core/
    config.py
    security.py
    errors.py
    logging.py
  engines/
    base.py
    http_engine.py
    browser_engine.py
  proxies/
    manager.py
    models.py
    health.py
  sessions/
    manager.py
    cookies.py
  diagnostics/
    response_classifier.py
    protection_detector.py
    evidence.py
  extractors/
    base.py
    generic.py
    idealista_html.py
  jobs/
    manager.py
    worker.py
    storage.py
  storage/
    database.py
    models.py
  integrations/
    base.py
    authorized_providers.py
  tests/
    unit/
    integration/
    e2e/
    fixtures/
  scripts/
  docs/

Adapta esta estructura al código existente. No dupliques módulos ni reescribas componentes funcionales innecesariamente.

## FASE 3 — MOTOR HTTP

Implementa un motor asíncrono robusto basado en httpx.

Requisitos:

- GET y POST.
- Headers configurables.
- Cookies.
- Sesiones.
- Timeouts.
- Redirecciones controladas.
- Streaming.
- Límite de tamaño de respuesta.
- Decodificación.
- Reintentos limitados.
- Control de concurrencia.
- Errores tipados.
- Proxy configurable.
- Registro de tiempos.
- Metadatos de respuesta.

Utiliza la interfaz compatible con httpx 0.28 o fija explícitamente una versión verificada.

No permitas que un fallo individual detenga todo el sistema.

## FASE 4 — MOTOR PLAYWRIGHT

Implementa un motor de navegador con:

- Chromium.
- Contextos aislados.
- Navegación.
- Espera configurable.
- Extracción de HTML.
- Extracción de texto.
- Capturas opcionales.
- Cookies y sesiones autorizadas.
- Timeouts.
- Limpieza de recursos.
- Control de concurrencia.
- Gestión de procesos colgados.
- Registro de errores.
- Métricas de rendimiento.

Debe funcionar sin depender de Ollama.

El motor debe poder ejecutarse desde cualquier VPS compatible.

## FASE 5 — GESTOR DE PROXIES

Integra el sistema Decodo existente.

Disponemos de diez endpoints ISP:

isp.decodo.com:10001–10010

Las credenciales deben recuperarse únicamente desde variables de entorno o archivos privados.

Funciones:

- Añadir.
- Eliminar.
- Seleccionar.
- Comprobar conectividad.
- Comprobar autenticación.
- Obtener IP de salida.
- Medir latencia.
- Registrar errores.
- Deshabilitar endpoints fallidos.
- Recuperar endpoints operativos.
- Distribuir solicitudes respetando límites de concurrencia.

No asumas que diez endpoints representan diez IP distintas.

Utiliza destinos de diagnóstico permitidos.

No almacenes credenciales en GitHub.

## FASE 6 — GESTIÓN DE SESIONES

Implementa una capa independiente para gestionar sesiones autorizadas.

Funciones:

- Crear sesión.
- Recuperar sesión.
- Expirar sesión.
- Almacenar cookies de manera segura.
- Asociar sesión a un trabajo.
- Aislar sesiones entre usuarios.
- Eliminar sesión.
- Gestionar errores de autenticación.
- Evitar reutilización indebida.

No implementes automatización destinada a superar CAPTCHA ni controles de acceso de terceros sin autorización.

## FASE 7 — DIAGNÓSTICO DATADOME Y PROTECCIONES

Este módulo es una prioridad de arquitectura.

Diseña un sistema extensible que identifique:

- HTTP 403.
- HTTP 429.
- Respuestas de desafío.
- CAPTCHA.
- Páginas de acceso denegado.
- HTML vacío.
- Respuestas HTTP 200 sin contenido útil.
- Problemas de conexión.
- Timeouts.
- Errores TLS.
- Errores de proxy.
- Redirecciones inesperadas.

Implementa un clasificador de protección que reconozca indicadores documentados de DataDome y otras soluciones antibot.

Registra evidencias sin almacenar secretos.

Mantén separados:

1. Estado HTTP.
2. Estado de accesibilidad.
3. Tipo de protección detectada.
4. Calidad de contenido.
5. Resultado del extractor.

El módulo debe poder probarse mediante fixtures y servidores de prueba controlados.

Construye interfaces para incorporar futuras integraciones de acceso autorizadas.

No desarrolles evasión de CAPTCHA ni técnicas de elusión sin autorización.

## FASE 8 — EXTRACTORES

Implementa una arquitectura de parsers independientes de la descarga.

Extractor genérico:

- HTML.
- Texto.
- Título.
- Metaetiquetas.
- Enlaces.
- Imágenes.
- Datos estructurados.

Extractor inmobiliario:

- Referencia.
- Tipo de operación.
- Tipo de inmueble.
- Precio.
- Superficie.
- Habitaciones.
- Baños.
- Planta.
- Ubicación.
- Características.
- Descripción.
- Imágenes.
- Anunciante.

Utiliza el HTML proporcionado por el usuario y obtenido mediante Crawio como fixture de regresión.

No confundas procesar el fixture con obtenerlo desde Idealista.

## FASE 9 — API

Mantén FastAPI.

Endpoints mínimos:

GET /health
GET /ready
POST /scrape
POST /scrape/batch
GET /jobs/{id}
POST /jobs/{id}/cancel
GET /proxies/status
GET /metrics
GET /history
GET /docs

Funciones:

- Autenticación por API key.
- Validación de solicitudes.
- Límites de concurrencia.
- Rate limiting.
- Protección SSRF.
- Restricciones de destinos.
- Manejo consistente de errores.
- Respuestas JSON documentadas.

No permitas solicitudes arbitrarias a IP privadas, metadata endpoints ni redes internas.

## FASE 10 — TRABAJOS Y PERSISTENCIA

Implementa:

- Cola de trabajos.
- Identificadores.
- Estados.
- Persistencia.
- Reintentos limitados.
- Cancelación.
- Recuperación tras reinicio.
- Resultados.
- Historial.
- Exportación JSON.
- Logs.

El sistema debe funcionar sin Ollama.

## FASE 11 — DOCKER Y PORTABILIDAD

CRÍTICO: el usuario va a apagar RunPod.

Debes preparar el proyecto para ejecutarse desde cero en un nuevo servidor.

Entrega:

- Dockerfile.
- docker-compose.yml.
- .env.example sin credenciales.
- requirements.lock, uv.lock o equivalente.
- Versiones fijadas.
- Instalación de Chromium.
- Healthchecks.
- Volúmenes persistentes.
- Scripts de arranque.
- Scripts de migración.
- Scripts de diagnóstico.
- Configuración de desarrollo y producción.

Comprueba que no depende de rutas absolutas de RunPod.

No dependas de la GPU.

No dependas de Ollama.

No incluyas modelos de IA en la imagen Docker.

## FASE 12 — PRUEBAS

Ejecuta pruebas unitarias, de integración y end-to-end.

Casos prioritarios:

A. https://example.com

B. https://www.bcousinoprop.com/

C. Fixture HTML de Idealista proporcionado por el usuario.

D. Respuesta 403 DataDome simulada.

E. Respuesta 200 con desafío simulado.

F. Respuesta 200 con HTML válido.

G. Fallo de proxy.

H. Timeout.

I. Reinicio de un trabajo.

J. Persistencia.

K. Protección SSRF.

L. Prueba de navegador Playwright.

Los accesos en vivo a páginas de terceros deben respetar su autorización y condiciones de uso.

No declares que una extracción bloqueada ha tenido éxito.

## FASE 13 — GITHUB CONTINUO

No esperes al final para guardar.

Después de cada módulo estable:

1. Ejecuta pruebas.
2. Corrige errores.
3. Actualiza PROGRESS.md.
4. Actualiza TEST_RESULTS.md.
5. Comprueba secretos.
6. Haz commit.
7. Haz push.
8. Verifica el hash remoto.

Utiliza una rama de desarrollo y publica en main únicamente cambios validados.

No utilices force push.

No dejes archivos importantes exclusivamente en RunPod.

## FASE 14 — DOCUMENTACIÓN PARA CLAUDE CODE

Crea:

docs/ARCHITECTURE.md
docs/SETUP.md
docs/API.md
docs/PROXY_MANAGER.md
docs/SESSIONS.md
docs/PROTECTION_DIAGNOSTICS.md
docs/IDEALISTA_STATUS.md
docs/DEPLOYMENT.md
docs/TROUBLESHOOTING.md
docs/NEXT_STEPS.md

Crea también:

CLAUDE.md
AGENTS.md
PROGRESS.md
TEST_RESULTS.md
BLOCKERS.md

CLAUDE.md debe explicar:

- Qué es el proyecto.
- Cómo ejecutarlo.
- Cómo probarlo.
- Qué módulos están implementados.
- Qué módulos están pendientes.
- Cómo continuar sin reconstruirlo.
- Qué no debe modificarse.
- Cómo trabajar con GitHub.

AGENTS.md debe contener las instrucciones generales para otros asistentes de programación.

Documenta el estado exacto de Idealista.

## FASE 15 — VERIFICACIÓN DE PORTABILIDAD

Esta es una condición esencial.

Realiza una prueba de instalación desde una copia limpia del repositorio, sin reutilizar dependencias locales ni datos del pod.

Comprueba:

- Instalación.
- Arranque.
- API.
- Navegador.
- Extracción convencional.
- Parser inmobiliario.
- Pruebas.
- Persistencia.
- Apagado y recuperación.

No basta con que funcione únicamente en el pod actual.

Si alguna prueba no puede realizarse, documenta claramente la limitación.

## FASE 16 — ENTREGA FINAL

Antes de terminar:

1. Comprueba Git.
2. Guarda los avances recuperables.
3. Verifica los commits remotos.
4. Enumera los archivos no versionados.
5. Comprueba que no faltan módulos importantes.
6. Ejecuta la suite de pruebas.
7. Comprueba Docker.
8. Documenta las limitaciones.
9. Actualiza PROGRESS.md.
10. Deja instrucciones precisas para Claude Code.

Tu informe final debe incluir:

- Rama.
- Commit.
- Estado de GitHub.
- Estructura del repositorio.
- Módulos implementados.
- Pruebas aprobadas.
- Pruebas fallidas.
- Instrucciones de instalación.
- Estado de Idealista.
- Limitaciones.
- Próximos pasos.

## CRITERIO PRINCIPAL DE ÉXITO

El proyecto debe poder reconstruirse y ejecutarse en un servidor nuevo utilizando exclusivamente el código, la documentación y la configuración suministrada de manera segura.

No debe depender del pod de RunPod.

No debe depender de Ollama.

No debe depender de una conversación de Qwen.

No declares el proyecto listo para migrar si faltan archivos, dependencias o secretos que el usuario deba conservar por separado.

COMIENZA AHORA. DESARROLLA, PRUEBA, CORRIGE Y GUARDA CONTINUAMENTE EN GITHUB.


## Instrucción del usuario (2026-11-14 03:24:27)

# MISIÓN CRÍTICA — CONSTRUIR Y PRESERVAR EL MOTOR COMPLETO DE SCRAPING ANTES DE APAGAR RUNPOD

## CONTEXTO

Esta es una CONTINUACIÓN del proyecto existente.

NO empieces desde cero.

El usuario va a apagar permanentemente el pod de RunPod cuando finalice esta fase.

Por tanto, tu misión es construir y preservar una arquitectura de scraping completa, modular, reproducible y transferible a cualquier VPS o servidor.

El trabajo debe quedar disponible en GitHub para continuar posteriormente con Claude Code, otra IA o un desarrollador humano.

Repositorio:

https://github.com/Bcousino890/ProxyManager

Estado de referencia:

- main: fba6a26
- Rama de respaldo: recovery/scraper-20261114-0306
- API: puerto 8000
- Panel: puerto 8002
- Agente Qwen: puerto 8787

Comprueba los hashes actuales antes de modificar archivos.

## OBJETIVO PRIORITARIO

Construir el MOTOR DE SCRAPING COMPLETO.

NO desarrollar dashboards, marketing, suscripciones, diseño visual ni funcionalidades SaaS secundarias.

El usuario necesita disponer de toda la infraestructura técnica necesaria para ejecutar, diagnosticar, mantener y extender un scraper.

El principal caso de estudio es Idealista, cuyo acceso directo actualmente devuelve HTTP 403 con DataDome.

La arquitectura debe admitir mecanismos de acceso autorizados, investigación de compatibilidad y nuevos adaptadores, sin que un bloqueo en un sitio paralice todo el motor.

No declares que DataDome está resuelto si no has obtenido y validado contenido real mediante un acceso permitido.

## FASE 1 — AUDITORÍA Y RESCATE

Antes de escribir código:

1. Inspecciona el repositorio completo.
2. Identifica todos los módulos existentes.
3. Comprueba las ramas Git.
4. Revisa archivos sin commit.
5. Identifica qué archivos están duplicados.
6. Identifica los procesos activos.
7. Revisa dependencias y versiones.
8. Identifica código parcialmente implementado.
9. Conserva todo el trabajo útil.
10. Crea una rama de desarrollo específica.

No elimines modelos Ollama ni datos del pod.

No ejecutes git reset --hard ni git clean -fd.

Crea una copia de seguridad de cualquier cambio que no esté versionado.

## FASE 2 — ARQUITECTURA MODULAR

Organiza el motor mediante interfaces claras.

Estructura propuesta:

scraping_engine/
  api/
    main.py
    routes/
    schemas/
    dependencies/
  core/
    config.py
    security.py
    errors.py
    logging.py
  engines/
    base.py
    http_engine.py
    browser_engine.py
  proxies/
    manager.py
    models.py
    health.py
  sessions/
    manager.py
    cookies.py
  diagnostics/
    response_classifier.py
    protection_detector.py
    evidence.py
  extractors/
    base.py
    generic.py
    idealista_html.py
  jobs/
    manager.py
    worker.py
    storage.py
  storage/
    database.py
    models.py
  integrations/
    base.py
    authorized_providers.py
  tests/
    unit/
    integration/
    e2e/
    fixtures/
  scripts/
  docs/

Adapta esta estructura al código existente. No dupliques módulos ni reescribas componentes funcionales innecesariamente.

## FASE 3 — MOTOR HTTP

Implementa un motor asíncrono robusto basado en httpx.

Requisitos:

- GET y POST.
- Headers configurables.
- Cookies.
- Sesiones.
- Timeouts.
- Redirecciones controladas.
- Streaming.
- Límite de tamaño de respuesta.
- Decodificación.
- Reintentos limitados.
- Control de concurrencia.
- Errores tipados.
- Proxy configurable.
- Registro de tiempos.
- Metadatos de respuesta.

Utiliza la interfaz compatible con httpx 0.28 o fija explícitamente una versión verificada.

No permitas que un fallo individual detenga todo el sistema.

## FASE 4 — MOTOR PLAYWRIGHT

Implementa un motor de navegador con:

- Chromium.
- Contextos aislados.
- Navegación.
- Espera configurable.
- Extracción de HTML.
- Extracción de texto.
- Capturas opcionales.
- Cookies y sesiones autorizadas.
- Timeouts.
- Limpieza de recursos.
- Control de concurrencia.
- Gestión de procesos colgados.
- Registro de errores.
- Métricas de rendimiento.

Debe funcionar sin depender de Ollama.

El motor debe poder ejecutarse desde cualquier VPS compatible.

## FASE 5 — GESTOR DE PROXIES

Integra el sistema Decodo existente.

Disponemos de diez endpoints ISP:

isp.decodo.com:10001–10010

Las credenciales deben recuperarse únicamente desde variables de entorno o archivos privados.

Funciones:

- Añadir.
- Eliminar.
- Seleccionar.
- Comprobar conectividad.
- Comprobar autenticación.
- Obtener IP de salida.
- Medir latencia.
- Registrar errores.
- Deshabilitar endpoints fallidos.
- Recuperar endpoints operativos.
- Distribuir solicitudes respetando límites de concurrencia.

No asumas que diez endpoints representan diez IP distintas.

Utiliza destinos de diagnóstico permitidos.

No almacenes credenciales en GitHub.

## FASE 6 — GESTIÓN DE SESIONES

Implementa una capa independiente para gestionar sesiones autorizadas.

Funciones:

- Crear sesión.
- Recuperar sesión.
- Expirar sesión.
- Almacenar cookies de manera segura.
- Asociar sesión a un trabajo.
- Aislar sesiones entre usuarios.
- Eliminar sesión.
- Gestionar errores de autenticación.
- Evitar reutilización indebida.

No implementes automatización destinada a superar CAPTCHA ni controles de acceso de terceros sin autorización.

## FASE 7 — DIAGNÓSTICO DATADOME Y PROTECCIONES

Este módulo es una prioridad de arquitectura.

Diseña un sistema extensible que identifique:

- HTTP 403.
- HTTP 429.
- Respuestas de desafío.
- CAPTCHA.
- Páginas de acceso denegado.
- HTML vacío.
- Respuestas HTTP 200 sin contenido útil.
- Problemas de conexión.
- Timeouts.
- Errores TLS.
- Errores de proxy.
- Redirecciones inesperadas.

Implementa un clasificador de protección que reconozca indicadores documentados de DataDome y otras soluciones antibot.

Registra evidencias sin almacenar secretos.

Mantén separados:

1. Estado HTTP.
2. Estado de accesibilidad.
3. Tipo de protección detectada.
4. Calidad de contenido.
5. Resultado del extractor.

El módulo debe poder probarse mediante fixtures y servidores de prueba controlados.

Construye interfaces para incorporar futuras integraciones de acceso autorizadas.

No desarrolles evasión de CAPTCHA ni técnicas de elusión sin autorización.

## FASE 8 — EXTRACTORES

Implementa una arquitectura de parsers independientes de la descarga.

Extractor genérico:

- HTML.
- Texto.
- Título.
- Metaetiquetas.
- Enlaces.
- Imágenes.
- Datos estructurados.

Extractor inmobiliario:

- Referencia.
- Tipo de operación.
- Tipo de inmueble.
- Precio.
- Superficie.
- Habitaciones.
- Baños.
- Planta.
- Ubicación.
- Características.
- Descripción.
- Imágenes.
- Anunciante.

Utiliza el HTML proporcionado por el usuario y obtenido mediante Crawio como fixture de regresión.

No confundas procesar el fixture con obtenerlo desde Idealista.

## FASE 9 — API

Mantén FastAPI.

Endpoints mínimos:

GET /health
GET /ready
POST /scrape
POST /scrape/batch
GET /jobs/{id}
POST /jobs/{id}/cancel
GET /proxies/status
GET /metrics
GET /history
GET /docs

Funciones:

- Autenticación por API key.
- Validación de solicitudes.
- Límites de concurrencia.
- Rate limiting.
- Protección SSRF.
- Restricciones de destinos.
- Manejo consistente de errores.
- Respuestas JSON documentadas.

No permitas solicitudes arbitrarias a IP privadas, metadata endpoints ni redes internas.

## FASE 10 — TRABAJOS Y PERSISTENCIA

Implementa:

- Cola de trabajos.
- Identificadores.
- Estados.
- Persistencia.
- Reintentos limitados.
- Cancelación.
- Recuperación tras reinicio.
- Resultados.
- Historial.
- Exportación JSON.
- Logs.

El sistema debe funcionar sin Ollama.

## FASE 11 — DOCKER Y PORTABILIDAD

CRÍTICO: el usuario va a apagar RunPod.

Debes preparar el proyecto para ejecutarse desde cero en un nuevo servidor.

Entrega:

- Dockerfile.
- docker-compose.yml.
- .env.example sin credenciales.
- requirements.lock, uv.lock o equivalente.
- Versiones fijadas.
- Instalación de Chromium.
- Healthchecks.
- Volúmenes persistentes.
- Scripts de arranque.
- Scripts de migración.
- Scr


## Instrucción del usuario (2026-11-14 04:02:38)

CONTINUACIÓN OBLIGATORIA — ÚLTIMA FASE ANTES DE APAGAR RUNPOD

NO EMPIECES DESDE CERO.

El controlador informa:

- main: 123ac8a4, sincronizado con GitHub.
- 4 archivos sin commit.
- API operativa.
- 2 pruebas aprobadas y 1 fallida.
- Arquitectura completa todavía sin verificar.

OBJETIVO:

Dejar todo el motor de scraping portable, documentado y guardado en GitHub para continuar después con Claude Code.

INSTRUCCIONES:

1. Inspecciona el código existente y elimina duplicaciones solo cuando esté demostrado que son innecesarias.
2. Conserva y publica los 4 archivos pendientes después de revisarlos y verificar que no contienen secretos.
3. Identifica y corrige la prueba fallida.
4. Completa las interfaces del motor HTTP, Playwright, proxies, sesiones, diagnóstico de protecciones y extractores.
5. Implementa pruebas para cada componente.
6. Utiliza el HTML del desafío DataDome como fixture sanitizado para el detector.
7. No repitas solicitudes a Idealista que continúen devolviendo 403.
8. Prepara Dockerfile, docker-compose.yml, .env.example y dependencias con versiones fijadas.
9. Crea CLAUDE.md, AGENTS.md y documentación completa de instalación y arquitectura.
10. Comprueba que el motor puede funcionar sin Ollama ni GPU.
11. Realiza una instalación y prueba desde un clon limpio.
12. Guarda avances mediante commits incrementales y push a GitHub.
13. Verifica que el hash remoto coincide después de cada publicación.
14. No cambies el agente del puerto 8787 ni reinicies RunPod.

NO dediques tiempo al diseño del Playground, dashboards ni URL pública.

Antes de concluir, proporciona evidencia verificable de:

- Arquitectura construida.
- Pruebas aprobadas.
- Archivos guardados.
- Docker funcional.
- Instalación limpia reproducible.
- Limitaciones existentes.

No declares COMPLETADO solo porque /health responde 200.

Si se agota el presupuesto, guarda primero todos los avances recuperables en GitHub y deja documentado el punto exacto de continuación.
