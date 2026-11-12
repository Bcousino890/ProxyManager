# Estado comprobado — 11 noviembre 2026

Este archivo conserva un historial cronológico de avances. Las listas iniciales describen cortes anteriores; el estado vigente se resume en `README.md` y `docs/roadmap.md`, con las evidencias más recientes al final de este archivo.

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

Concurrencia y capacidad de cola configurables por entorno. Esta nota registra el diseño inicial; la recuperación actual de comprobaciones mediante lease y reintentos se documenta más abajo. El historial conserva destino sin query para evitar persistir secretos de URL.

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

`PROXYMANAGER_HEALTH_CONCURRENCY` workers asíncronos reclaman comprobaciones de SQLite de forma atómica (`BEGIN IMMEDIATE`, estados `queued → running → completed/failed`). Un trabajo `running` cuyo lease (`PROXYMANAGER_HEALTH_LEASE_SECONDS`, 120) expira vuelve a `queued`; tras `PROXYMANAGER_HEALTH_MAX_ATTEMPTS` (3) intentos queda `failed` con `max_attempts`. Los trabajos pendientes sobreviven a reinicios y varios procesos pueden compartir la base sin duplicar trabajo (atomicidad probada con reclamaciones secuenciales, no con carga multiproceso real). La URL de destino se ejecuta sin query (la que se persiste). `pytest -q` → **36 passed** (11 noviembre 2026).

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

## Avance: cola de benchmarks acotada (fase 4, solo código)

`POST /v1/benchmarks` (alcance `bench:write`, solo admin por defecto), `GET /v1/benchmarks/{id}` (`bench:read`), `POST /v1/benchmarks/{id}/cancel`. Un único benchmark activo (409 si hay otro). Topes configurables: `PROXYMANAGER_BENCH_MAX_REQUESTS` (1000), `..._MAX_CONCURRENCY` (10), `..._MAX_BYTES` (50 MB); `rps` opcional; solo hosts de la allowlist; la URL se guarda sin query. Resumen: resultados por tipo (`success`, `challenge`, `unexpected_response`, `transport_error`), p50/p95/máx de latencia, bytes, rps logrado y solicitudes por proxy; se corta por `byte_budget`, `cancelled` o `no_healthy_proxy`. Un benchmark interrumpido por reinicio queda `failed: interrupted` y NO se reintenta. Los 1.000 por ejecución son un tope de seguridad, no el objetivo: el benchmark de 100.000 sigue requiriendo autorización específica, destino autorizado y presupuesto, y subir el tope explícitamente. Probado solo con transporte simulado (`pytest -q` → **49 passed**, 25 ejecuciones seguidas sin fallos; se corrigió un test inestable). No se ha ejecutado ningún benchmark real.

`scripts/ip_survey.py`: mide la IP de salida de cada proxy contra un servicio indicado en `PROXYMANAGER_IP_URL` (propio o aprobado); no se ejecuta contra ninguno por defecto, no consulta geolocalización ni ASN.

## Avance: panel de administración (fase 5, primera versión)

`/panel` (HTML + JS + CSS estáticos servidos por la propia API, sin dependencias ni build). Pestañas: Proxies (estado, tasa de éxito, latencia, botón de comprobación), Benchmarks (lanzar con confirmación, ver resultados, cancelar) y Auditoría. La clave API se pide al entrar, se guarda solo en `sessionStorage` y se descarta al salir; todo el contenido dinámico se inserta con `textContent`. Cabeceras: CSP `default-src 'self'` (sin scripts ni estilos en línea), `nosniff`, `no-referrer`, `frame-ancestors 'none'`. Nuevos endpoints: `GET /v1/overview` (`proxies:read`) y `GET /v1/benchmarks` (`bench:read`). Verificado en Chromium (Playwright) a 1200 px y 390 px: sin errores de consola salvo el 401 esperado con clave incorrecta, sin desbordamiento horizontal, capturas revisadas; esa verificación fue manual, no hay prueba automatizada de navegador. `pytest -q` → **51 passed** (11 noviembre 2026). Pendiente: gráficas históricas, gestión de sesiones y gastos en el panel, alta de proxies desde la interfaz, modo oscuro sin revisar visualmente, accesibilidad no auditada, y servir por HTTPS (el panel envía la clave en cabecera: no usar sin TLS fuera de localhost).

## Avance: ficheros de despliegue (fase 6, sin desplegar)

`Dockerfile` reforzado (healthcheck, un worker), `.dockerignore` (excluye `.env`, bases, `data.txt`), `docker-compose.yml` (API interna de solo lectura + Caddy con HTTPS automático), `Caddyfile`, `deploy.env.example` y `docs/deploy.md`. Verificado: healthcheck real contra uvicorn, `PROXYMANAGER_STRICT=1` rechaza configuración vacía y `docker compose config` valida el compose con un `.env` temporal. **No verificado:** `docker build` ni la ejecución del compose (sin demonio de Docker), ni Caddy/Let's Encrypt; no hay servidor ni dominio. Sin gasto ni recursos creados.

## Avance: panel ampliado y prompt de servidor temporal

Panel: alta de proxies (credenciales cifradas; el campo de contraseña se limpia tras guardar), historial de comprobaciones por proxy y pestaña de gastos (`GET/POST /v1/expenses`, alcances `expenses:read/write`; gastos anotados a mano frente a `PROXYMANAGER_MONTHLY_BUDGET_USD`, mes UTC, sin consultar facturación real). Verificado en Chromium (escritorio y móvil); se corrigió una regla CSS que ocultaba la columna "Concepto" en móvil. `pytest -q` → **53 passed**. `handoff/PROMPT-TEMP-SERVER.md`: prompt completo para una sesión local que cree un servidor Spot de ~2 h (tope 5 USD, confirmación previa, dominio temporal sslip.io, destrucción verificada). No se ha ejecutado.

## Revisión de seguridad propia (11 noviembre 2026)

Hallazgos corregidos: (1) intentos fallidos de clave sin límite → bloqueo por IP tras `PROXYMANAGER_AUTH_FAILURE_LIMIT` (10) fallos por ventana, 429 con `Retry-After` (en compose se confía en `X-Forwarded-For` solo porque únicamente Caddy alcanza la API); (2) `/scrape` devolvía el texto de la excepción de transporte, que con proxies podría exponer datos de la conexión → ahora solo el nombre de la clase; (3) Caddy sin límite de cuerpo → `max_size 1MB`. Revisado sin hallazgos: auditoría sin secretos, panel sin `innerHTML` y con CSP estricta, URL de benchmark sin query, credenciales de proxies cifradas y nunca listadas, comparación de claves en tiempo constante, SSRF mitigado por allowlist+IP pública fijada. **Limitaciones**: revisión hecha por el propio autor, no independiente; sin pruebas de penetración; el límite de fallos es por IP en memoria (un proceso); un atacante con la IP de Caddy o IPv6 rotatoria no queda cubierto del todo; sin 2FA ni rotación de claves; las claves son estáticas de entorno. `pytest -q` → **56 passed**.

## Prueba automática del panel en navegador

`scripts/panel_e2e.js` (Node + Playwright) y `tests/test_panel_e2e.py` (lanza la API en un puerto libre y ejecuta el script; se salta si no hay Node/Playwright: `npm i -g playwright`). Cubre en escritorio y móvil: clave incorrecta, acceso, alta de proxy con limpieza de credenciales y sin contraseña en el DOM, historial, gastos (columna Concepto visible), sin desbordamiento horizontal ni errores de consola, y aviso de permiso para la clave de evaluación en Auditoría. Se comprobó que falla si se reintroduce el fallo CSS anterior. `pytest -q` → **57 passed** (11 noviembre 2026). No cubre modo oscuro, accesibilidad ni otros navegadores.

## Accesibilidad y modo oscuro del panel

Revisión con axe-core 4.10.2 (Playwright, CSP desactivada solo en el navegador de prueba) en claro y oscuro, login y panel: tras corregir el contraste del botón principal en oscuro (`--on-accent`) y las cabeceras de tabla vacías ("Acciones"), **0 violaciones** automáticas. Revisión visual del modo oscuro hecha. Las herramientas automáticas no sustituyen una auditoría con lector de pantalla ni navegación completa por teclado, que no se han hecho. `handoff/CODEX-FINISH.md`: encargo para Codex con lo que puede terminar solo y lo que requiere al propietario.

## Codex finish: CI (11 noviembre 2026)

Se añadió `.github/workflows/ci.yml` para ejecutar `pytest -q` con Python 3.12 en push y pull request. Verificación local previa al commit: `.venv/bin/pytest -q` → 56 passed, 1 skipped, 1 warning. La ejecución en GitHub Actions queda pendiente hasta el push; no se atribuye aquí un resultado de CI todavía.

## Codex finish: sesiones en panel (11 noviembre 2026)

`GET /v1/sessions` devuelve solo sesiones activas del propietario autenticado y requiere alcance `sessions`; la pestaña «Sesiones» permite crear, listar y borrar la propia sesión y sus cookies. El panel conserva CSP estricta y construye contenido dinámico con `textContent`. Evidencia local: `NPM_CONFIG_PREFIX=/tmp/pm-npm .venv/bin/pytest -q` → 58 passed, 1 warning; `NPM_CONFIG_PREFIX=/tmp/pm-npm AXE=1 .venv/bin/pytest -q tests/test_panel_e2e.py` → 1 passed, 1 warning. Esta ejecución de axe incluye la pestaña de sesiones en claro y oscuro y reportó cero violaciones WCAG automáticas. Playwright y axe se instalaron fuera del repositorio en `/tmp/pm-npm`; CI normal no requiere Node.

## Codex finish: alertas webhook opcionales (11 noviembre 2026)

Implementado `PROXYMANAGER_ALERT_WEBHOOK_URL` (vacío por defecto). Si se configura, solo acepta HTTPS sin credenciales ni fragmento. El servicio emite un aviso al pasar de sano a no sano según las métricas existentes y otro al superar el 80 % del presupuesto mensual registrado manualmente. Los cuerpos contienen únicamente tipo de evento, identificador de proxy o mes, y cifras de gasto; excluyen conceptos, claves, credenciales y destinos. Las pruebas usan `httpx.MockTransport`: comprueban que sin configurar no hay envíos, que el aviso de salud ocurre una sola vez por transición y que el concepto privado no aparece en la alerta de presupuesto. Evidencia: `NPM_CONFIG_PREFIX=/tmp/pm-npm .venv/bin/pytest -q` → 62 passed, 1 warning. No se ha configurado ni contactado ningún webhook real. La entrega del aviso es de mejor esfuerzo y no tiene reintentos persistentes.

## Codex finish: copia de seguridad SQLite (11 noviembre 2026)

`scripts/backup.sh` crea una copia consistente con `sqlite3 .backup`, directorio 0700, archivo 0600 y retención por días configurable. La clave de cifrado se respalda aparte; el script no la lee. `docs/deploy.md` describe uso y restauración. Evidencia: `.venv/bin/pytest -q tests/test_backup.py` → 1 passed; el test abre la copia, comprueba una fila, permisos y eliminación de una copia de diez días. Pendiente comprobar el programa de copias y una restauración en un VPS autorizado.

## Codex finish: laboratorio local de clasificación (11 noviembre 2026)

`tests/lab_server.py` sirve cinco casos solo en loopback: contenido esperado, CAPTCHA genérico, redirección, lentitud y respuesta cortada. `tests/test_local_lab.py` ejercita `fetch` con DNS y transporte de prueba, sin tráfico externo. Evidencia: `.venv/bin/pytest -q tests/test_local_lab.py` → 1 passed. El clasificador existente distingue los casos observados; no se cambió sin evidencia de un fallo. Diferencias y límites en `docs/lab.md`. No equivale a una prueba de DataDome real.

## Codex finish: documentación de fases (11 noviembre 2026)

`README.md` y `docs/roadmap.md` separan fases 2, 4, 5 y 6 hechas en código de fases 3, 7 y 8 pendientes. `docs/reports/validation-template.md` contiene solo apartados vacíos, sin resultados inventados. Se retiraron del texto vigente las descripciones antiguas de recuperación de comprobaciones; los benchmarks sí mantienen su estado `failed: interrupted` al reiniciar, según `src/proxymanager/bench.py:76-79` y `tests/test_bench.py:86-93`. Pendientes: DataDome real, 100.000 solicitudes, 30 días de operación, despliegue y gasto AWS/VPS, IP/ASN/geolocalización mediante servicio aprobado, y revisión de seguridad independiente. Estas tareas requieren acceso, autorización o tiempo real del propietario.

## CI de GitHub recuperado (12 noviembre 2026, hora de Madrid)

Tras la incidencia de GitHub Actions, se creó el commit vacío `23a4a4c` para generar una ejecución nueva sin cambiar código. La ejecución de pull request [43116283882](https://github.com/Bcousino890/ProxyManager/actions/runs/43116283882) terminó correctamente: `gh run watch 43116283882 --repo Bcousino890/ProxyManager --interval 5 --exit-status` → salida 0; el paso `pytest -q` registró **63 passed, 1 skipped, 1 warning in 5.40s** en Python 3.12. La prueba del panel se omite en CI sin Playwright. En local, `NPM_CONFIG_PREFIX=/tmp/pm-npm .venv/bin/pytest -q` → 64 passed, 1 warning. Las ejecuciones antiguas de la incidencia seguían en cola al comprobarlo y están sustituidas por esta ejecución verde.

## Avance: reintento con otro proxy en `/scrape` (11 noviembre 2026)

Con `use_proxy`, si el proxy elegido falla por **transporte** (sin respuesta HTTP), se reintenta con otro proxy sano distinto, hasta `PROXYMANAGER_SCRAPE_PROXY_ATTEMPTS` (2) intentos; el fallo queda registrado en las métricas del proxy y, con `session_id`, la sesión se reasigna al proxy que funcionó. No se reintenta ante respuestas HTTP (aunque sean 4xx/5xx o desafíos): eso es del sitio, no del proxy. Sin alternativas sanas se devuelve el último fallo. La respuesta incluye `attempts`. Verificado: failover, sin fugas de concurrencia (límite 1), sin reintento ante 500 del sitio, y rendición cuando fallan todos; `pytest -q` → **66 passed** (3 ejecuciones seguidas). Probado solo con transporte simulado.

**Reparto de trabajo acordado:** Codex (sesión local) abre y gestiona servidores/VPS y lo que corre en el equipo del propietario, siguiendo `handoff/PROMPT-TEMP-SERVER.md`; Claude (sesión cloud) lleva GitHub (PRs, fusiones, CI) y el código del repositorio. El PR #2 de Codex se fusionó en la rama del PR #1 tras verificar CI en verde y 64 pruebas.

## Avance: claves API múltiples y revocables (11 noviembre 2026)

`POST/GET /v1/keys` y `DELETE /v1/keys/{id}` (alcance `keys:manage`, solo la clave de administración de entorno). Las claves (`pm_…`, 256 bits aleatorios) se muestran una única vez y se guardan solo como SHA-256; cada una tiene alcances, caducidad opcional (hasta 3650 días), revocación inmediata y último uso (actualizado como mucho una vez por minuto). Una clave adicional no puede tener `keys:manage` (sin escalada de privilegios) y la clave de evaluación de entorno tampoco; máximo 100 activas. Cada clave tiene sesiones aisladas. Las claves de entorno siguen como arranque/recuperación. Pestaña "Claves" en el panel (la clave nueva se borra del DOM al cambiar de pestaña; nunca aparece en la lista); prueba de navegador ampliada y axe sin violaciones en claro y oscuro. `pytest -q` → **70 passed**. Limitaciones: SHA-256 sin sal (válido para claves aleatorias largas, no para contraseñas); sin rotación automática ni notificación de caducidad; auditoría registra el hash del propietario, no el nombre de la clave.

## Avance: cierre de `/docs`, tráfico por proxy e importación desde el panel (11 noviembre 2026)

- **Esquema público**: con `PROXYMANAGER_STRICT=1`, `/docs`, `/redoc` y `/openapi.json` devuelven 404 (el panel y `/health` siguen); el contenedor arranca uvicorn con `--no-server-header`.
- **Tráfico por proxy**: cada comprobación, `/scrape` y benchmark registra los bytes del cuerpo de respuesta (`proxy_events.bytes`, migración automática); `GET /v1/overview` devuelve `traffic_month_bytes` (mes UTC, por proxy y total) y, si `PROXYMANAGER_PROXY_COST_PER_GB_USD` > 0, `estimated_proxy_cost_usd`. **Es una estimación inferior**: no cuenta cabeceras, handshake TLS ni CONNECT, y no sustituye la factura del proveedor. Eventos con más de 35 días se purgan al arrancar.
- **Importar lote desde el panel**: `POST /v1/proxies/import` (alcance `proxies:write`, máx. 500 líneas y 64 KB, valida todo antes de insertar, errores solo con número de línea, nunca el contenido; duplicados por host y puerto omitidos). El textarea se vacía al terminar y la prueba de navegador comprueba que las credenciales no quedan en el DOM.
- Verificación: `pytest -q` → **74 passed** (incluye navegador); axe: 0 violaciones en claro, oscuro y móvil (390 px) sobre la pestaña de proxies con el importador abierto.
## Prueba EC2 temporal interrumpida y recursos limpiados (12 noviembre 2026)

Con autorización expresa del propietario tras mostrar el coste, se lanzó en AWS cuenta Zinto, región `eu-south-2`, una `t3.medium` Spot temporal con Ubuntu 24.04, disco gp3 de 20 GB, IP pública asignada automáticamente, y recursos etiquetados `pm-run=20261112-temp`. Instancia `i-092a828caa9a33fdc`, lanzada a las 00:29 hora de Madrid. La consola la mostró **terminada** unos dos minutos después, con motivo `Client.UserInitiatedShutdown: User initiated shutdown`. La causa concreta del cierre no quedó demostrada; no se desplegó ProxyManager ni se ejecutaron pruebas desde ese servidor.

Tras recuperar el acceso a la consola y con confirmación específica del propietario, se verificó en EC2 España: ninguna instancia activa, ningún volumen EBS, ninguna instantánea propia, ninguna IP elástica, ninguna interfaz de red y ninguna solicitud Spot visible. Se eliminó el grupo de seguridad temporal `sg-0decd5a353e819592` (`pm-temp-20261112`); la consola confirmó el borrado y, tras actualizar, mostró únicamente el grupo predeterminado. Se eliminó el par de claves `pm-temp-20261112`; la consola confirmó el borrado y mostró la lista vacía. La clave privada temporal local se borró y se verificó su ausencia. No se creó una segunda instancia.

El cálculo previo era de unos **0,042 USD para dos horas**, antes de impuestos y transferencia; el coste efectivo de esta instancia breve aún no está confirmado en facturación AWS. Pendientes: despliegue HTTPS, importación y pruebas reales de proxies, medición del gasto efectivo y cualquier prueba de operación remota. Para otra instancia se necesitará un nuevo plan y autorización de gasto.

Verificación local de este cambio documental: `NPM_CONFIG_PREFIX=/tmp/pm-npm .venv/bin/pytest -q` → **64 passed, 1 warning in 8.83s**. No prueba el despliegue remoto.

## Rediseño del panel (12 noviembre 2026, rama `claude/redesign-dashboard`)

Panel nuevo con barra lateral fija e iconos propios y nueve secciones: Resumen, Proxies, Sesiones, Benchmarks, Claves API, Playground, Uso, Gastos y Auditoría. Estructura inspirada en las capturas de referencia aportadas (barra lateral, tarjetas blancas, acento verde azulado, métricas grandes, Playground con barra de petición, opciones y bloque de código oscuro); marca, textos e iconos son propios. Sin librerías: HTML, CSS y JS en `src/proxymanager/panel/` (`icons.js`, `charts.js`, `app.js`), gráficas SVG construidas por código, CSP estricta (sin scripts ni estilos en línea, sin `innerHTML`; solo se sirven ficheros de una lista cerrada).

- **Datos reales, sin simular**: nuevo `GET /v1/usage?days=1..90` (alcance `usage:read`, incluido por defecto en la clave de evaluación) con solicitudes, latencia (media y p95), resultados, bytes por día y por **dominio**; solo se guarda el host de destino, nunca ruta ni query (hay prueba). Se registra cada `/scrape` y cada solicitud de benchmark. Las gráficas muestran estados vacíos claros cuando no hay datos y los días sin datos no inventan latencia.
- **Transporte frente a entrega**: `GET /v1/overview` añade `delivery_24h` por proxy y `concurrency`. Un proxy puede estar "sano" (respondió) y a la vez "bloqueado" por el sitio (desafío/403); se muestran por separado. Clasificación común en `usage.classify`: success, challenge, blocked (401/403/429), unexpected_response, transport_error.
- **Playground**: solo GET (lo único que soporta la API). Opciones reales: usar proxy, país, sesión persistente; timeout, tamaño máximo y reintentos son del servidor (`/v1/system` ahora los expone) y se muestran como solo lectura. Muestra estado, duración, tamaño, proxy, intentos, id de solicitud, aviso interpretado y cuerpo (primeros 20.000 caracteres) o detalles JSON. Ejemplos cURL, Python y Node.js que usan `PROXYMANAGER_API_KEY`, nunca la clave real. **No existen** (y no se simulan): créditos, vista previa renderizada (iría contra la CSP), cabeceras de respuesta completas ni cookies devueltas.
- **Claves API**: la clave nueva aparece oculta, con Mostrar/Ocultar y Copiar, se borra del DOM al cambiar de sección; la lista muestra la huella `pm_…XXXX` (últimos 4 caracteres; columna nueva con migración automática).
- **Seguridad**: el Playground y los ejemplos no revelan la clave API; el sitio de terceros que devuelve un desafío se informa tal cual: ProxyManager lo detecta, no lo resuelve ni lo esquiva.

Verificación: `pytest -q` → **79 passed** (dos ejecuciones seguidas); prueba de navegador (`tests/test_panel_e2e.py` + `scripts/panel_e2e.js`) recorre las nueve secciones en escritorio y móvil, formularios, Playground (éxito, desafío, host no permitido), claves y que las credenciales no queden en el DOM; **axe-core: 0 violaciones** en las nueve secciones, en claro y oscuro, a 1200 px y 390 px (`AXE=1 AXE_CORE_PATH=… node scripts/panel_e2e.js`). Revisión visual de capturas en escritorio, móvil y oscuro. Corregido en el proceso: tablas con scroll horizontal ahora son enfocables con teclado. Limitaciones: la verificación visual usó datos de muestra en una base temporal; no se probó en Safari/Firefox; los ejemplos de código no se ejecutan automáticamente; la latencia por día depende de que existan solicitudes registradas.
