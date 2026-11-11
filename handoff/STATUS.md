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
