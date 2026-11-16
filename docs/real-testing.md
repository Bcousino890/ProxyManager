# Pruebas reales: de cero a un `/scrape` verificado

Todo se prueba **solo contra destinos propios o autorizados**.

## 1. Diagnóstico de configuración
```bash
set -a; source .env; set +a
.venv/bin/python -m proxymanager.doctor      # [OK]/[WARN]/[ERROR]; no imprime secretos
```
Corrige los `ERROR` antes de seguir (clave de administración, clave Fernet, base de datos, manejador que no carga).

## 2. Arrancar y cargar proxies
Local: `uvicorn proxymanager.app:app --port 8000` (con `PROXYMANAGER_COOKIE_SECURE=false` en HTTP). Desplegado: ver `deploy/README.md`.
Abre `/admin/` → **Proxies** → importa el lote, ajusta tipo/país **solo si los verificaste** y pulsa *Comprobar* con una URL autorizada.

## 3. Prueba de humo automática
```bash
.venv/bin/python -m proxymanager.smoke --base-url https://TU-DOMINIO \
  --target https://tu-sitio-autorizado.example/ --expected-text "texto que debe aparecer" --country ES
```
Comprueba salud, páginas, alta de cuenta de prueba (o `--api-key`), 401 con clave inválida, `/scrape` directo validado y, con `--country`, `/scrape` por proxy con la **misma IP** durante la sesión. Sale con código 1 si algo falla. Sin `--api-key` crea una cuenta de prueba que consume créditos gratuitos.

## 4. Conectar el manejador de desafíos (el programador)
1. Copia `examples/handler_template.py` (o `deploy/handlers/handler_template.py`) y programa `handle()`.
2. Pruébalo sin servidor con una página guardada de un destino **autorizado**:
   `python -m proxymanager.handlercheck handler_template:TemplateHandler --html pagina.html`
3. Conéctalo: en Docker, deja el archivo en `deploy/handlers/` y pon `PROXYMANAGER_CHALLENGE_HANDLER=modulo:Clase` en `deploy/.env`; en local, exporta `PYTHONPATH` a su carpeta. `doctor` confirma que carga.
4. Los clientes lo activan por solicitud con `"solve_challenges": true`. Contrato completo: `docs/extending-challenge-handlers.md`.

## Qué queda por medir con esto
La tasa de éxito real por proxy, la latencia, el consumo de transferencia y el comportamiento ante el sistema antibot **autorizado** que se vaya a evaluar. Los resultados de laboratorio no son resultados de DataDome real salvo que se hayan obtenido contra una instalación real autorizada.
