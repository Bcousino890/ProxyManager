# Encargo para Codex: terminar lo que se puede terminar sin el propietario

Pégalo en una sesión de Codex abierta en la carpeta del repositorio. Rama de partida: `claude/amazing-darwin-rvk1xf` (PR https://github.com/Bcousino890/ProxyManager/pull/1, con todo el trabajo de Codex y Claude hasta hoy). Crea tu rama desde ahí, p. ej. `codex/finish-<tema>`; no fuerces push sobre ramas ajenas.

---

Eres Codex trabajando en ProxyManager. Lee `AGENTS.md`, `CLAUDE.md`, `handoff/START-HERE.md`, `STATUS.md`, `NEXT-TASK.md` y `docs/deploy.md`. Prepara el entorno: `python3 -m venv .venv && .venv/bin/pip install -e '.[test]' && .venv/bin/pytest -q` (hoy: 57 passed; 56 si no tienes Node/Playwright). Habla español.

## Reglas
- Nunca commitees ni imprimas claves, credenciales de proxies, cookies, `.env`, `data.txt` ni bases SQLite. Nada de tráfico externo, compras, despliegues ni cargas: solo código, pruebas locales con transporte simulado y documentación.
- **Haz commit y push solo si `pytest -q` pasa completo.** (Hoy se subió una rama rota por encadenar el commit sin esa condición.) Muestra la salida real de pytest; no reutilices conteos antiguos.
- Cada afirmación en `STATUS.md` con su evidencia (comando y resultado); separa implementado / probado / pendiente. Actualiza `NEXT-TASK.md` al cerrar cada bloque.
- Los límites de seguridad (allowlist HTTPS, IP pública fijada, alcances por clave, tope de benchmarks) no se relajan para que algo funcione.

## Haz esto, en este orden
1. **CI**: `.github/workflows/ci.yml` con `pytest -q` en Python 3.12 (sin Node: la prueba de navegador se salta sola). Debe pasar en el PR.
2. **Sesiones en el panel**: listar y borrar las sesiones del propietario (nuevo endpoint `GET /v1/sessions` con alcance `sessions`), pestaña en `src/proxymanager/panel/`, sin `innerHTML` ni scripts/estilos en línea (CSP estricta). Amplía `scripts/panel_e2e.js` y vuelve a pasar axe (cero violaciones en claro y oscuro) si puedes ejecutarlo.
3. **Alertas**: aviso opcional por webhook (`PROXYMANAGER_ALERT_WEBHOOK_URL`, vacío = desactivado) cuando un proxy pasa de sano a no sano o cuando el gasto del mes supera el 80 % del presupuesto. Solo se llama a la URL configurada por el propietario; sin secretos ni URLs de destino en el cuerpo; con pruebas de que no se envía nada si no está configurado.
4. **Copias de seguridad**: `scripts/backup.sh` (copia consistente de SQLite con `sqlite3 .backup`, permisos 600, rotación) y sección en `docs/deploy.md`. Deja claro que la clave Fernet se guarda aparte; el script NO la incluye.
5. **Laboratorio de fase 3** (sin DataDome real): un servidor local de pruebas dentro de `tests/` o `lab/` con páginas de contenido, de desafío CAPTCHA genérico, de redirección y de respuesta lenta/cortada, para ejercitar `fetch` y el clasificador. Mejora el clasificador solo con lo que el laboratorio demuestre. **Prohibido**: imitar o evadir protecciones de terceros, ni afirmar que el laboratorio equivale a DataDome real; documenta la diferencia.
6. **Documentación**: actualiza `README.md` y `docs/roadmap.md` con el estado real (fases 2, 4, 5 y 6 hechas en código; fases 3, 7 y 8 pendientes), quita referencias obsoletas (`interrupted`, `BackgroundTasks`) y crea `docs/reports/validation-template.md` para la fase 7 (plantilla vacía; sin resultados inventados).
7. Marca el PR como listo para revisión SOLO si el propietario lo pide; no lo fusiones.

## Lo que NO puedes terminar (no lo finjas; déjalo escrito como pendiente)
- 30 días de operación real; acceso y pruebas con DataDome real; benchmark de 100.000 solicitudes; despliegue y gasto en AWS/VPS; medición de IP/ASN/geolocalización de los proxies (necesita servicio aprobado); revisión de seguridad independiente. Cada uno requiere autorización o acciones del propietario.

Al terminar entrega: lista de commits, salida literal de `pytest -q`, qué quedó pendiente y por qué.
