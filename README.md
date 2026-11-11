# ProxyManager

Para continuar en otra sesión de Codex o Claude Code, empieza por [handoff/START-HERE.md](handoff/START-HERE.md).

Plataforma académica para investigar sesiones HTTP, redes proxy, desafíos y mediciones en destinos autorizados. Esta es la **primera versión ejecutable**, no la plataforma final descrita en el encargo del TFG.

## Inicio local

Requiere Python 3.12 o superior.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
cp .env.example .env
# Edita .env; luego exporta las variables en tu entorno.
set -a; source .env; set +a
.venv/bin/uvicorn proxymanager.app:app --host 127.0.0.1 --port 8000
```

La documentación OpenAPI queda en `http://127.0.0.1:8000/docs`. Sin claves, los endpoints protegidos rechazan las solicitudes. Sin hosts autorizados, `/scrape` rechaza todos los destinos. Configura únicamente hosts públicos bajo tu control o con permiso expreso.

```bash
curl -H 'X-API-Key: CLAVE_DE_EVALUACION' http://127.0.0.1:8000/v1/system
curl -H 'X-API-Key: CLAVE_DE_EVALUACION' -H 'Content-Type: application/json' \
  -d '{"url":"https://lab.example/producto"}' http://127.0.0.1:8000/scrape
```

La URL de ejemplo no funcionará hasta autorizar un destino real y configurar el texto esperado. El servidor conserva el código HTTP del destino en `status_code`; el HTTP 200 de nuestra API significa que procesó la petición, no que el contenido sea válido. `success` requiere HTTP 200, el texto esperado y ausencia de marcadores básicos de desafío. No se siguen redirecciones.

## Reglas revisables

Las variables de `.env.example` controlan claves, clave de cifrado, destinos, patrón de contenido esperado, duración de sesiones, tiempo de espera, tamaño máximo de respuesta y presupuesto indicativo. Los valores del encargo son parámetros iniciales, no reglas fijas. Cambiar `.env` y reiniciar el servicio modifica el comportamiento sin editar código. No se interpreta `MONTHLY_BUDGET_USD` como un límite de gasto efectivo todavía.

## Estado comprobable

Implementado: API FastAPI, OpenAPI, salud, claves, sesiones persistentes SQLite aisladas por clave, catálogo de proxies con credenciales cifradas, acceso HTTPS con allowlist, rechazo de IP privada/reservada, DNS resuelto antes de conectar, conexión fijada a la IP comprobada, no seguimiento de redirecciones y clasificación inicial de contenido. Las pruebas usan transporte simulado: no envían solicitudes a terceros. El registro de un proxy con credenciales requiere `PROXYMANAGER_CREDENTIAL_KEY`; la API nunca devuelve usuario ni contraseña. El catálogo aún no utiliza esos proxies para enviar tráfico.

Pendiente: uso efectivo y comprobación de conexiones proxy, cookies persistentes, verificación DataDome real, análisis CAPTCHA con OpenCV, workers, benchmark, métricas, costes efectivos, panel, HTTPS público, monitorización y operación durante 30 días. La detección de desafío por palabras clave es preliminar. `bytes_transferred` mide bytes de contenido recibidos por HTTPX, no el tráfico de red comprimido. No se ha probado DataDome real, ni 100.000 solicitudes, ni disponibilidad mensual. **No despliegues esta versión como API pública.**

## Verificación

```bash
.venv/bin/pytest -q
```

Las pruebas comprueban autenticación, aislamiento de sesiones, autorización de destinos, clasificación de HTTP 200 y conexión a IP fijada. Consulta el [diseño](docs/superpowers/specs/2026-11-11-proxymanager-initial-design.md), el [plan inicial](docs/superpowers/plans/2026-11-11-initial-api.md), la [hoja de ruta de ocho fases](docs/roadmap.md) y el [informe de conectividad](docs/reports/2026-11-11-proxy-connectivity.md). Las diez conexiones de prueba están importadas solo en la base de datos local con credenciales cifradas; no se subieron credenciales a GitHub.

## Salud de proxies

`POST /v1/proxies/{id}/checks` con clave administrativa y cuerpo `{"url":"https://destino-autorizado/ruta"}` devuelve HTTP 202. `GET /v1/proxies/{id}/checks` consulta el historial con clave válida. El destino se valida contra la allowlist; el túnel conecta a una IP pública comprobada y TLS verifica el hostname original. La respuesta no incluye credenciales ni contenido HTML.

Configura `PROXYMANAGER_HEALTH_CONCURRENCY` y `PROXYMANAGER_HEALTH_QUEUE_LIMIT`. Ejecuta **un solo worker** por base de datos: al arrancar se marcan como interrumpidos los trabajos anteriores pendientes. La cola llena devuelve HTTP 429. El historial omite parámetros de consulta de las URLs. El adaptador usa el backend AutoBackend de httpcore 1.0.x, con dependencia acotada y prueba de TLS.
