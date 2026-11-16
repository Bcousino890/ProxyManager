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

## Avance (16 noviembre 2026): plataforma de cliente para vender la API

Implementado: cuentas con contraseña scrypt y sesión web por cookie `HttpOnly` + cabecera `X-PM-CSRF`; claves `pm_live_…` por cliente (solo hash SHA-256, límite de créditos por clave, revocación, máximo 10); créditos por solicitud **validada** (1 directa / 2 por proxy, configurable; las no validadas no cuestan); registro de uso; límite de 60 solicitudes/min por clave y límite de intentos de login/alta; `/scrape` acepta `method`, `headers`, `body`, `expected_text`, `use_proxy`, `country` y devuelve `headers`; enrutado por proxy del catálogo (`ProxyStore.pick`); `GET/POST /v1/admin/*` para listar usuarios y conceder créditos; cabeceras de seguridad y CSP; consola SPA en `/app/` (resumen, claves, Playground, uso, cuenta, suscripción, apoyo); documentación en `/docs/`; OpenAPI movido a `/api-reference`; `deploy/` con Caddy + Docker Compose para un dominio `*.sslip.io`.

Probado: `.venv/bin/pytest -q` → **37 passed** (16 nov 2026; 15 nuevos en `tests/test_accounts.py`, transporte simulado). Consola comprobada con Chromium (alta, clave visible una vez, Playground, docs) contra un servidor local. El Playground hacia Internet falló aquí por el proxy TLS del sandbox (`CERTIFICATE_VERIFY_FAILED`); no se desactivó la verificación, así que **no hay evidencia de una petición real de éxito** fuera de los tests.

No hecho / pendiente: despliegue (no hay VPS ni IP, no se contrató nada); pasarela de pago (las recargas son manuales vía `/v1/admin/credits`); verificación de correo y recuperación de contraseña; rate limit y cola en memoria (un solo proceso); selección de proxy sin salud ni sticky; tipo/país de proxies siguen `unknown`; política de uso aceptable y términos legales sin revisar por el propietario; `PROXYMANAGER_ALLOW_ANY_PUBLIC_HOST` desactivado por defecto; sin DataDome real ni benchmark. No exponer públicamente hasta pasar una revisión de seguridad.

## Avance (16 noviembre 2026): panel de administración `/admin/`

Panel con la clave `PROXYMANAGER_ADMIN_KEY` (guardada solo en `sessionStorage`): resumen, catálogo de proxies (añadir, importar lote `host:puerto:usuario:contraseña`, tipo, país, activar/desactivar, eliminar, lanzar comprobación con una URL autorizada, última comprobación) y clientes (listado y concesión de créditos). Nuevos endpoints de administración: `PATCH/DELETE /v1/proxies/{id}`, `POST /v1/proxies/import`, `GET /v1/admin/stats`. Los proxies desactivados no se eligen en `/scrape`. Probado: `pytest -q` → **39 passed**; capturas con Chromium usando datos de demostración en una base temporal. Pendiente: la clave de administración única no es un login con usuarios/2FA; añadir auditoría de acciones de administración.

## Avance (16 noviembre 2026): salud de proxies en `/scrape` y gancho de desafíos

- Selección: activos, sin fallo en los últimos `PROXYMANAGER_HEALTH_TTL_SECONDS`, prefiriendo los que superaron una comprobación. Fallos de transporte reales se registran (comprobación pasiva) y apartan el proxy; un éxito lo rehabilita. Un reintento con otro proxy. IP fija por `session_id` (tabla `session_proxy`, purgada al borrar la sesión). Barrido periódico opcional con `PROXYMANAGER_HEALTH_URL` + `PROXYMANAGER_HEALTH_INTERVAL_SECONDS`. Sin proxies sanos: 422.
- `src/proxymanager/challenges.py`: interfaz `ChallengeHandler`, sin implementación; ver `docs/extending-challenge-handlers.md`. Respuesta incluye `challenge` y `proxy_id`.
- Probado: `pytest -q` → **45 passed** (transporte simulado). No probado con proxies reales ni barrido periódico en vivo; la selección no distingue fallos del destino de fallos del proxy salvo por error de transporte.

## Avance (16 noviembre 2026): herramientas para pruebas reales

- `python -m proxymanager.doctor` (diagnóstico de configuración), `python -m proxymanager.smoke` (prueba de humo de un despliegue: salud, páginas, alta, 401, scrape directo, scrape por proxy con IP fija), `python -m proxymanager.handlercheck` (probar un manejador sin servidor). Plantilla en `examples/handler_template.py`; en Docker, `deploy/handlers/` montado en `/handlers`. Guía: `docs/real-testing.md`.
- `PROXYMANAGER_CA_BUNDLE` permite una CA propia manteniendo la verificación TLS (necesario en este sandbox, cuyo proxy intercepta TLS).
- Corregido: `load_handler` no instanciaba clases.
- **Evidencia real (16 nov 2026, sandbox):** servidor local + `smoke` contra `https://example.com/` con `expected_text` → HTTP 200 validado, 1 crédito, 75 ms, TLS verificado. `pytest -q` → **48 passed**. `docker compose config` válido; **la imagen Docker no se pudo construir aquí (sin daemon)**.
- Sin probar: proxies reales (las 10 conexiones del propietario solo existen en su máquina), despliegue en VPS, HTTPS con sslip.io/Let's Encrypt, DataDome.

## Avance (16 noviembre 2026): manejador de desafíos conectado (Idealista), con activación declarada

- El material que el programador subió (`ddguard`: `curl_cffi` + Camoufox contra DataDome de Idealista) está integrado en `integrations/ddguard/` y adaptado al contrato de `challenges.py` en `integrations/ddguard_handler.py`. El adaptador solo actúa sobre `idealista.com`/subdominios; para cualquier otro host devuelve `None` sin crear sesión ni red (comprobado).
- **Doble llave antes de que dispare una sola solicitud real:** (1) el operador configura `PROXYMANAGER_CHALLENGE_HANDLER` e instala `pip install -e '.[ddguard]'`; (2) en `/admin/` → *Desafíos*, alguien declara **quién autorizó** y una **referencia verificable**, lo que queda registrado con fecha en `challenge_authorization`/`challenge_authorization_log` (nueva tabla, `src/proxymanager/authorization.py`). Sin esa declaración activa, `/scrape` nunca invoca el manejador aunque esté configurado (`challenge.pending_authorization: true`, sin cobro). El botón de desactivar no exige declaración.
- Nuevos endpoints: `GET/POST /v1/admin/challenge-handler`, `POST …/enable`, `POST …/disable`.
- **Lo que no hice:** no instalé Camoufox ni Playwright (solo `curl_cffi`, ligero, para validar que el adaptador importa y usa la API real sin tocar red), no ejecuté nada contra `idealista.com`, no until existe autorización real documentada en este momento. Probado: `pytest -q` → **49 passed**, incluida la ruta completa (configurado→no autorizado→autorizado→se dispara→se desactiva) con un manejador de prueba; capturas del panel `/admin/` → *Desafíos* con una declaración de ejemplo (inventada, no una autorización real).
- Pendiente antes de usarlo de verdad: que exista la autorización de Idealista; instalar `camoufox fetch` en el VPS; `noVNC` para el slider del CAPTCHA (`integrations/ddguard/deploy/novnc-setup.sh`); probar `login`/`status` del CLI de ddguard.

## Avance (16 noviembre 2026): despliegue en VPS documentado (carpeta aislada) y aclaración sobre ddguard

- **El CAPTCHA deslizante de Idealista NO se resuelve en automático** con `ddguard` tal como está escrito: solo el "interstitial" se supera solo (~20-30 s). El deslizante necesita que una persona lo resuelva por noVNC (`captcha_mode="wait"`, confirmado leyendo `integrations/ddguard/solver.py::_wait_clear`: en modo sin pantalla falla directo en vez de intentarlo) o un servicio de pago no incluido (`captcha_mode="callback"`). Documentado en `docs/ddguard-vps.md` con el diagrama del flujo cliente→API→destino.
- `deploy/README.md` reescrito: carpeta aislada `/opt/proxymanager/` en el VPS, `name: proxymanager` fijado en `docker-compose.yml` (contenedores/redes/volúmenes con ese prefijo, sin chocar con otros proyectos del mismo Docker), comprobación de puertos 80/443 antes de instalar, y una Opción B para convivir con un proxy inverso que ya exista en el VPS sin tocarlo.
- `deploy/Dockerfile.ddguard` + `deploy/docker-compose.ddguard.yml` + `deploy/ddguard-entrypoint.sh`: imagen **separada y opcional** (no se construye por defecto) con Camoufox, Xvfb y noVNC dentro del propio contenedor; el puerto 6080 solo se publica en `127.0.0.1` del VPS (acceso por túnel SSH, nunca abierto a Internet). Sigue exigiendo la autorización declarada en `/admin/` → Desafíos para disparar.
- **No construido ni probado:** no hay Docker daemon en este entorno (confirmado), así que `Dockerfile.ddguard` no se ha construido de verdad; puede faltar alguna dependencia de sistema para Camoufox que solo aparecerá al construir en el VPS real. `docker compose config` validó la sintaxis YAML de ambos archivos. `pytest -q` → **49 passed** (sin cambios de código de producto en este avance, solo documentación/infra de despliegue).
