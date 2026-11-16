# Pruebas reales: de cero a un `/scrape` verificado

Todo se prueba **solo contra destinos propios o autorizados**.

## 0. Antes del VPS: pruébalo en tu propio Mac/PC (sin Docker)

No uses `deploy/docker-compose.yml` para esto: ese monta Caddy con HTTPS público (Let's Encrypt),
que necesita una IP y un dominio accesibles desde Internet, y tu máquina local normalmente no los
tiene. Para probar en local basta con Python, tal como en el quickstart del `README.md`:

```bash
git clone https://github.com/Bcousino890/ProxyManager   # si aún no la tienes clonada
cd ProxyManager
python3 -m venv .venv && .venv/bin/pip install -e '.[test]'
cp .env.example .env
```

Edita `.env`: pon `PROXYMANAGER_ADMIN_KEY` (algo largo), genera
`PROXYMANAGER_CREDENTIAL_KEY` con `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`,
y añade `PROXYMANAGER_COOKIE_SECURE=false` (solo en local, por HTTP) y
`PROXYMANAGER_ALLOW_ANY_PUBLIC_HOST=true` si quieres probar contra cualquier sitio público.

```bash
set -a; source .env; set +a
.venv/bin/pytest -q                          # 49 passed, sin red
.venv/bin/python -m proxymanager.doctor      # corrige cualquier [ERROR]
.venv/bin/uvicorn proxymanager.app:app --port 8000 &
.venv/bin/python -m proxymanager.smoke --base-url http://127.0.0.1:8000 \
  --target https://example.com/ --expected-text "Example Domain"
```

Abre en el navegador: `http://127.0.0.1:8000/app/` (consola), `http://127.0.0.1:8000/admin/`
(panel), `http://127.0.0.1:8000/docs/` (documentación).

Si quieres probar también `ddguard` localmente: en un Mac/PC con pantalla **no hace falta
Xvfb/noVNC** (eso es solo para un VPS sin pantalla) — `headless=False` abre una ventana de
navegador de verdad en tu propia pantalla:

```bash
.venv/bin/pip install -e '.[ddguard]'
.venv/bin/python -m camoufox fetch
export PROXYMANAGER_CHALLENGE_HANDLER=integrations.ddguard_handler:build_handler
export DDGUARD_HEADLESS=false
```

Sigue sin activarse nada en `/scrape` hasta declarar la autorización en `/admin/` → *Desafíos*
(ver `docs/extending-challenge-handlers.md`); eso aplica igual en local que en el VPS.

Cuando todo esto funcione en tu máquina, repite los mismos pasos de configuración (mismas
variables de `.env`) en el VPS siguiendo `deploy/README.md`, que sí usa Docker y Caddy porque ahí
sí hay una IP pública para el dominio `sslip.io`.

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
