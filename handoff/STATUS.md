# Estado comprobado — 11 noviembre 2026

## Implementado

- Paquete Python instalable; FastAPI/OpenAPI, `/health`, `/ready`, `/v1/system`, sesiones y `/scrape`.
- Claves API de evaluación y administración; el alta de proxies exige administración.
- SQLite con permisos de archivo 0600; sesiones aisladas por clave; catálogo de proxies con credenciales Fernet.
- Allowlist HTTPS, rechazo de direcciones privadas/reservadas, DNS resuelto antes de conectar con IP fijada, redirecciones desactivadas.
- Clasificación preliminar del contenido por texto esperado y marcadores de desafío.
- Importador local de conexiones `host:port:usuario:contraseña`, idempotente, con tipo y país desconocidos.

## Evidencia

- Las diez entradas privadas del usuario respondieron una vez a `https://zinto.app/robots.txt` con HTTP 200 y cuerpo idéntico al directo. [Informe sin secretos](../docs/reports/2026-11-11-proxy-connectivity.md).
- Esas entradas se importaron en la base **local** del primer desarrollador, con credenciales cifradas. No se subieron los datos a GitHub.
- Tests automatizados, sin tráfico externo, en `tests/`. Vuelve a ejecutar `pytest -q` en cada sesión; no reutilices un conteo antiguo como evidencia nueva.
- Costes de servidores/proxies: [fotografía parcial de precios](../docs/research/2026-11-11-cost-snapshot.md), sin compra ni decisión final.

## No demostrado / pendiente

- Las diez entradas pueden compartir IP de salida; no se midió geolocalización, ASN ni clase de red.
- El catálogo aún no selecciona ni monitoriza proxies para `/scrape`.
- No hay persistencia de cookies, rotación de sesiones, workers, benchmark, panel, gastos efectivos, HTTPS público, alertas ni 30 días de operación.
- No se ha accedido a una instalación DataDome autorizada ni probado su verificación real. El clasificador actual es preliminar.
- No se ha efectuado un benchmark de 100.000 solicitudes. No hay VPS contratado ni gasto aprobado.
- No exponer la API actual a Internet: aún faltan rate limiting, permisos más granulares, auditoría y revisión de seguridad.

## Commits anteriores

- `79d0f6a` base API.
- `c42ff5c` catálogo cifrado.
- `9a8e4fc` comprobación de proxies y hoja de ruta.

Este archivo es un corte temporal. Actualízalo con evidencia en cada cambio significativo.

## Avance: comprobaciones desde API

Implementados `POST /v1/proxies/{id}/checks` (administración, HTTP 202) y `GET /v1/proxies/{id}/checks` (historial). Dos comprobaciones simultáneas y máximo 20 pendientes por base. Persistencia de resultados y errores redactados. Los trabajos se ejecutan dentro del proceso API; un reinicio puede dejar trabajos pendientes y aún falta recuperación automática.

Prueba real posterior: un proxy contra robots.txt de Zinto devolvió error de transporte usando el destino fijado por IP. El sondeo anterior por nombre había funcionado. La compatibilidad de CONNECT con destino por IP requiere diagnóstico; no se desactivó la protección DNS para ocultar el fallo.

## Actualización: TLS por proxy corregido

La biblioteca httpcore usaba la IP fijada como nombre TLS dentro del túnel CONNECT. Se añadió un transporte que conserva CONNECT a la IP validada y verifica el certificado TLS contra el hostname original. No se desactivó la validación de certificados. Las diez conexiones devolvieron HTTP 200 y contenido esperado a través de la API; evidencia en `docs/reports/2026-11-11-api-proxy-checks.json`.

Concurrencia y capacidad de cola configurables por entorno. Al arrancar un único proceso API, los trabajos pendientes anteriores se marcan `interrupted`; no se reenvían automáticamente. El historial conserva destino sin query para evitar persistir secretos de URL. Despliegue actual requiere un solo worker; múltiples procesos necesitan coordinación adicional.

El propietario confirmó que dispone de VPS, pero no de acceso DataDome. Se han solicitado los datos no secretos del VPS. No se ha realizado despliegue.

El propietario eligió AWS por horas para las pruebas y pospuso la elección del servidor mensual. Plan y condiciones en `docs/research/2026-11-11-aws-test-plan.md`. No se ha comprado ni creado ningún recurso AWS.

Comparación de pruebas AWS temporales en Europa (España): Lightsail 4 GB cuesta 0,03225 USD/h con disco e IPv4 incluidos; EC2 t3.medium x86 comparable cuesta 0,04560 USD/h más IPv4 (0,005 USD/h) y disco EBS gp3 de 80 GB (7,04 USD/mes). La t3a.medium usada como referencia anterior no figura en esa región. Desglose y fuentes en `docs/research/2026-11-11-aws-ec2-vs-lightsail.md`. No se creó instancia.

Objetivo de coste total: desarrollar localmente, usar Lightsail para pruebas remotas breves y considerar Netcup VPS Lite 1 G12.5s para operación continua. Su precio publicado actual es 5,86 €/mes con contrato y facturación de 6 meses (35,16 € al precio mostrado); confirmar el importe para España antes de comprar. Comparación y fuentes en `docs/research/2026-11-11-netcup-lite-vs-aws.md`. No se contrató ningún servicio.

Se comprobó también la tabla oficial de EC2 Spot en vivo (11 noviembre 2026): `t3.medium` en España desde 0,0136 USD/h de cómputo, más IPv4 y EBS. Con 80 GB, una prueba de 120 h sería ~3,39 USD frente a 3,87 USD de Lightsail, sin impuestos ni extras. Spot puede interrumpirse y T3 Unlimited puede facturar créditos de CPU; Lightsail sigue siendo la opción principal para pruebas estables, pero el criterio se revisará según la prueba y el precio del momento. Detalles en `docs/research/2026-11-11-aws-ec2-vs-lightsail.md`.

## Avance: cookies de sesión persistentes

Se añadió `CookieStore`: valores `Set-Cookie` cifrados con Fernet en SQLite, asociados a sesión y propietario. `/scrape` con `session_id` envía las cookies compatibles con host, dominio, ruta, HTTPS y caducidad; `Max-Age=0` las elimina y borrar la sesión purga sus cookies. Los atributos `HttpOnly` y `SameSite` se guardan como metadatos. Sin clave de cifrado, el uso de sesión HTTP devuelve 503 para evitar almacenamiento en claro. Pruebas locales con transporte simulado: `python3 -m pytest -q` → **22 passed** (11 noviembre 2026). No se ha probado aún con un servicio externo ni con DataDome real.

## Avance: rate limiting y auditoría

`RateLimiter` (ventana deslizante en memoria por propietario, seguro entre hilos) aplicado a todos los endpoints autenticados: 429 con `Retry-After`. Configurable con `PROXYMANAGER_RATE_LIMIT_REQUESTS` (60; 0 desactiva) y `PROXYMANAGER_RATE_LIMIT_WINDOW_SECONDS` (60). Solo válido con un único proceso API. `AuditLog` guarda en SQLite hora, hash de propietario, método, ruta genérica y estado — sin clave, query, cuerpo ni URL; consulta en `GET /v1/audit` (administración). Prueba: `pytest -q` → **26 passed** (11 noviembre 2026), sin tráfico externo. Nota: el trabajo equivalente de Codex no llegó a GitHub (límite de uso), así que se reimplementó aquí; la API sigue sin revisión de seguridad ni permisos granulares: no exponer a Internet.

## Avance: validación de configuración y retención de auditoría

`Settings.problems()` detecta claves ausentes o <16 caracteres, claves iguales, clave Fernet inválida, allowlist vacía y rate limit desactivado. Con `PROXYMANAGER_STRICT=1` el servicio se niega a arrancar si hay problemas (por defecto desactivado para no romper desarrollo/tests). La auditoría se purga al arrancar según `PROXYMANAGER_AUDIT_RETENTION_DAYS` (30). `pytest -q` → **29 passed** (11 noviembre 2026). Permisos granulares siguen pendientes: hoy solo hay dos roles (evaluación/administración).

## Avance: permisos por alcance y límites de cookies

Cada endpoint exige un alcance (`system:read`, `sessions`, `scrape`, `proxies:read`, `proxies:write`, `checks:write`, `audit:read`). La clave admin los tiene todos; los de la clave de evaluación se configuran con `PROXYMANAGER_EVALUATOR_SCOPES` (por defecto sin escritura ni auditoría). Sin clave → 401; sin alcance → 403. Alcances desconocidos se reportan en `Settings.problems()`. Cookies: máx. 4096 bytes por cookie y 50 por sesión (las que exceden se descartan; reemplazar una existente sigue permitido). `pytest -q` → **33 passed** (11 noviembre 2026). Sigue siendo un modelo de dos claves, no multiusuario; sin revisión de seguridad externa.

## Avance: worker persistente de comprobaciones

Las comprobaciones ya no dependen de `BackgroundTasks`. `PROXYMANAGER_HEALTH_CONCURRENCY` workers asíncronos reclaman trabajos de SQLite de forma atómica (`BEGIN IMMEDIATE`, estados `queued → running → completed/failed`). Un trabajo `running` cuyo lease (`PROXYMANAGER_HEALTH_LEASE_SECONDS`, 120) expira vuelve a `queued`; tras `PROXYMANAGER_HEALTH_MAX_ATTEMPTS` (3) intentos queda `failed` con `max_attempts`. Los trabajos pendientes sobreviven a reinicios y varios procesos pueden compartir la base sin duplicar trabajo (atomicidad probada con reclamaciones secuenciales, no con carga multiproceso real). Cambio de comportamiento: el estado `interrupted` ya no existe; la URL de destino se ejecuta sin query (la que se persiste). Aún no hay cola genérica para benchmarks, solo para comprobaciones. `pytest -q` → **36 passed** (11 noviembre 2026).

## Avance: selección de proxy por salud y métricas

`/scrape` acepta `use_proxy: true` (y `country` opcional, sin distinguir mayúsculas). `ProxyMetrics` registra eventos (`proxy_events`) de comprobaciones y de `/scrape`; "alcanzable" = el proxy devolvió una respuesta HTTP, un error de transporte penaliza al proxy, un desafío o contenido inesperado no. Un proxy es elegible si en la ventana (`PROXYMANAGER_PROXY_WINDOW_SECONDS`, 3600) tiene eventos, tasa ≥ `PROXYMANAGER_PROXY_MIN_SUCCESS_RATE` (0.5) y al menos un éxito. Se elige la mejor tasa, a igualdad el menos usado; con `session_id` el proxy queda ligado a la sesión mientras siga sano, y se reasigna si deja de estarlo. Sin proxies sanos → 503 (hay que ejecutar comprobaciones antes). `GET /v1/proxies/{id}/stats` (alcance `proxies:read`). La respuesta incluye `proxy_id`, nunca host ni credenciales. Pruebas con transporte simulado: `pytest -q` → **39 passed** (11 noviembre 2026). No se verificó con proxies reales desde este entorno; la rotación es por mejor tasa, no round-robin ni por latencia.

## Intento de prueba real desde el entorno cloud (11 noviembre 2026)

Se importaron las 10 conexiones privadas en una base temporal fuera del repositorio y se lanzaron comprobaciones contra `https://zinto.app/robots.txt`. Resultado: 10/10 `transport_error`. Diagnóstico: el entorno cloud de Claude Code rechaza TCP directo a `isp.decodo.com:10001` (`ConnectionRefusedError`; solo permite HTTPS por su proxy de salida), así que **no es evidencia de que los proxies o el código fallen**, y `/scrape` con `use_proxy` devolvió 503 como corresponde sin proxies sanos. La verificación real debe correr en la máquina del propietario o en el VPS/AWS: `scripts/live_check.py` (variables en su docstring) ejecuta las comprobaciones y un `/scrape` con proxy y solo imprime resultados. Las credenciales se usaron únicamente en una base local del scratchpad; no están en el repositorio.

## Script de prueba real en EC2 Spot (sin ejecutar)

`scripts/aws_spot_test.sh` se ejecuta en AWS CloudShell con la sesión del propietario (sin claves). Muestra cuenta y precio Spot de `t3.medium` en `eu-south-2`, pide confirmación (`SI`), recibe el archivo de proxies por la terminal sin eco, lanza una instancia Spot (CPU Standard, IMDSv2, sin reglas de entrada, disco de 16 GB), ejecuta `scripts/live_check.py` allí, recupera solo líneas `PM|` de la salida de consola y elimina instancia, security group y temporales (con verificación final). Solo se comprobó sintaxis, shellcheck y el user-data generado; **no se ha ejecutado contra AWS**. Pendientes conocidos: si Decodo exige IP autorizada, la IP pública de la instancia es aleatoria y habría que autorizarla o usar una Elastic IP; la salida de consola de AWS puede tardar minutos en actualizarse.

## Avance: rotación por latencia y carga

La selección de proxy ya no es solo "mejor tasa": compiten los sanos a menos de 10 puntos de la mejor tasa de éxito, ordenados por menos solicitudes en vuelo, menor latencia media (sin datos al final) y menos eventos. Cada proxy admite `PROXYMANAGER_PROXY_MAX_INFLIGHT` (5) solicitudes simultáneas; si todos los elegibles están llenos, `/scrape` responde 429 con `Retry-After: 1`. La sesión conserva su proxy aunque esté ocupado (coherencia de IP/cookies). La carga en vuelo es en memoria: válida para un solo proceso API. La concurrencia se libera siempre (también si la solicitud falla). `pytest -q` → **43 passed** (11 noviembre 2026), con transporte simulado; sin medición con proxies reales ni bajo carga.

## Evidencia: prueba real desde el equipo del propietario (11 noviembre 2026, 17:33 hora local)

`scripts/live_check.py` en macOS (Python 3.12) con base nueva y las 10 conexiones de Decodo importadas (`Importadas: 10`), contra `https://zinto.app/robots.txt`: 10/10 comprobaciones `completed` con éxito y HTTP 200, 374–591 ms; `/scrape` con `use_proxy` devolvió éxito HTTP 200 en 403 ms eligiendo proxy por salud; estadísticas del primer proxy: 2 eventos, tasa 1,0, media 566 ms, sano. `pytest -q` → 43 passed en esa máquina. Evidencia aportada como captura del propietario; los resultados no contienen credenciales. **No demuestra** IPs de salida distintas, geolocalización, comportamiento con otros destinos, carga ni DataDome. Descartado: el fallo previo `KeyError: 0` era del propio script (límite de 60/min); corregido en `dbda83c`. En el entorno cloud de Claude Code esta prueba no puede ejecutarse (solo salen 80/443).
