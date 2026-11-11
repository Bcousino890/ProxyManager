# ProxyManager

Plataforma académica para estudiar sesiones HTTP, proxies, clasificación de respuestas y mediciones **solo en destinos propios o autorizados**. Las reglas operativas son configurables; el estado y las limitaciones están en [handoff/STATUS.md](handoff/STATUS.md). Para continuar desde otra sesión de Codex o Claude Code, empieza por [handoff/START-HERE.md](handoff/START-HERE.md).

## Inicio local

Requiere Python 3.12 o superior. Usa claves de prueba locales y hosts bajo tu control.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
cp .env.example .env
# Edita .env, después carga las variables en el entorno.
set -a; source .env; set +a
.venv/bin/uvicorn proxymanager.app:app --host 127.0.0.1 --port 8000
```

El panel está en `http://127.0.0.1:8000/panel`. Para uso fuera de localhost, [docs/deploy.md](docs/deploy.md) describe HTTPS y los requisitos de despliegue; esos archivos aún no se han probado en un VPS. La API rechaza destinos fuera de `PROXYMANAGER_ALLOWED_HOSTS`, direcciones privadas o reservadas y conexiones HTTP sin TLS. Fija la IP pública validada antes de conectar y no sigue redirecciones.

## Funciones disponibles en código

- API con claves por alcance, sesiones y cookies cifradas, catálogo de proxies cifrado, comprobaciones persistentes y selección por salud, carga y latencia. El panel permite gestionar proxies, sesiones, benchmarks y gastos manuales.
- Benchmark acotado por solicitudes, concurrencia y bytes; métricas y resúmenes locales. El máximo por defecto es 1.000 solicitudes por ejecución; no se ha ejecutado el objetivo de 100.000.
- Rate limiting, auditoría, validación estricta opcional, alertas webhook opcionales (`PROXYMANAGER_ALERT_WEBHOOK_URL`, vacío = desactivadas) y [copias de SQLite](docs/deploy.md). Los avisos de presupuesto se basan en importes introducidos manualmente, no en facturación del proveedor.
- [Laboratorio local](docs/lab.md) con contenido, CAPTCHA genérico, redirección y fallos de transporte. El clasificador es preliminar; no se ha validado con DataDome real.

Las comprobaciones de proxy encoladas sobreviven a reinicios mediante leases y reintentos limitados. Un benchmark que estaba ejecutándose al reiniciar queda fallido y no se reintenta automáticamente, para evitar repetir tráfico externo. `bytes_transferred` cuenta bytes de contenido recibidos por HTTPX, no tráfico de red comprimido. Los límites y valores iniciales pueden cambiarse en la configuración con una evaluación apropiada del destino y presupuesto.

## Estado de las fases

La [hoja de ruta](docs/roadmap.md) separa implementación de validación: las fases 2, 4, 5 y 6 tienen código; las fases 3, 7 y 8 siguen pendientes. Tampoco se ha demostrado 30 días de operación, un despliegue AWS/VPS, IP/ASN/geolocalización de salida, ni una revisión de seguridad independiente. No expongas la API en Internet hasta completar la revisión y el despliegue autorizado.

## Pruebas

```bash
.venv/bin/pytest -q
```

La suite usa transporte simulado y un servidor en loopback; no envía tráfico a terceros. La prueba del panel se salta si faltan Node o Playwright. Consulta [handoff/STATUS.md](handoff/STATUS.md) para los resultados ejecutados y sus límites.
