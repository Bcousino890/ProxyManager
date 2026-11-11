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
