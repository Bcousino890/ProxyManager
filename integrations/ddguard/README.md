> **Aviso.** Este módulo está escrito para operar contra **idealista.com** saltándose su protección
> DataDome (device check + CAPTCHA). En ProxyManager se conecta mediante
> `integrations/ddguard_handler.py` y **no se activa por sí solo**: el operador debe (1) configurar
> `PROXYMANAGER_CHALLENGE_HANDLER` en el despliegue, y (2) declarar en `/admin/` → *Desafíos* quién
> autorizó su uso y una referencia verificable; esa declaración queda registrada con fecha. Antes de
> activarlo confirma que existe autorización real de Idealista (o úsalo solo contra un entorno de
> pruebas propio). Usarlo sin autorización puede incumplir las condiciones de uso del sitio y la ley
> aplicable; quien lo active es responsable de esa decisión.

# ddguard — DataDome para Idealista (Python)

Módulo para integrar en tu motor actual. Gestiona DataDome en Idealista: detecta el desafío, lo resuelve, guarda la sesión (cookies + login) en disco y **continúa el scraping sin reiniciar**.

## Cómo funciona

```
tu motor ──► DDSession.get(url)
               │
               ├─ 1. HTTP rápido (curl_cffi, huella TLS de Safari 26, cookies persistentes)
               │      → 200 con datos: listo (≈30-40 KB por página, sin navegador)
               │
               ├─ 2. ¿Desafío DataDome? (403 + captcha-delivery.com)
               │      → NO se reintenta por HTTP (los 403 repetidos son lo que banea la IP)
               │      → Camoufox (Firefox anti-detección) abre ESA url en la MISMA IP
               │      → interstitial (rt:'i'): se resuelve solo en ~20-30 s
               │      → slider CAPTCHA (rt:'c'): aviso a ti (Telegram/panel) y espera
               │        a que lo resuelvas por noVNC, o llama a tu propio solver
               │      → devuelve el HTML y pasa las cookies nuevas al HTTP (TLS Firefox)
               │
               └─ 3. ¿Bloqueo duro ("uso indebido") o falla la resolución?
                      → pausa (cooldown) en vez de seguir quemando la IP
                      → con DDPool, la siguiente IP sigue trabajando
```

- **Sesión persistente:** `dd_sessions/<ip>.json` guarda cookies, User-Agent, perfil TLS, login y contadores. Si reinicias el proceso, sigue con la misma sesión.
- **Una sesión por IP:** la cookie `datadome` está ligada a la IP que la obtuvo. Nunca se comparte entre IPs.
- **El navegador solo se abre cuando hace falta** y se cierra solo tras 5 min sin uso, así el VPS no gasta RAM en Chromium todo el día.

## Instalación

```bash
pip install -r requirements.txt
python -m camoufox fetch          # descarga el navegador Camoufox (una vez)
```

## Integración

**Opción A (recomendada): sustituir `page.goto()` por `DDSession.get()`.** Tu parser recibe el mismo HTML de siempre.

```python
from ddguard import DDSession, BrowserSolver, Blocked

solver = BrowserSolver(headless=False, captcha_mode="wait", notify=enviar_telegram)
async with DDSession(store_dir="dd_sessions", solver=solver) as dd:
    page = await dd.get("https://www.idealista.com/inmueble/110467049/")
    datos = tu_parser(page.text)
```

**Opción B: mantener Playwright.** Cambia una línea en tu motor:

```python
from ddguard.playwright_guard import PageGuard
guard = PageGuard(store_dir="dd_sessions", notify=enviar_telegram)
await guard.restore(context)                 # carga cookies/login guardados
html = await guard.goto(page, url)           # espera el desafío y continúa
```

Ejemplos completos: `examples/http_engine.py` y `examples/playwright_engine.py`.

**Varias IPs** (la del VPS + proxies opcionales):

```python
from ddguard import DDPool
async with DDPool([None, "http://user:pass@proxy:port"], solver=solver) as pool:
    page = await pool.get(url)     # usa la primera IP que no esté en pausa
```

## Login con tu cuenta de Idealista (opcional)

```bash
python -m ddguard login            # abre el navegador, inicias sesión tú, se guardan las cookies
python -m ddguard login --auto     # usa IDEALISTA_EMAIL / IDEALISTA_PASSWORD
python -m ddguard status           # estado de las sesiones guardadas
```

Hazlo en el VPS (por noVNC) o con el mismo proxy que usará el VPS, porque las cookies van ligadas a la IP. Las páginas de anuncios y búsquedas son públicas, así que **el login no es obligatorio**. Si lo usas, todas las peticiones quedan asociadas a esa cuenta.

## Resolver el slider en un VPS sin pantalla (gratis)

```bash
sudo bash deploy/novnc-setup.sh    # Xvfb + x11vnc + noVNC como servicios
export DISPLAY=:99                 # y BrowserSolver(headless=False)
```

Cuando llegue el aviso, abre `http://IP_DEL_VPS:6080/vnc.html`, mueve el slider y el motor continúa solo. Si prefieres no intervenir nunca, `captcha_mode="callback"` acepta cualquier servicio de resolución. Eso es de pago y no viene incluido.

## Parámetros principales

| Parámetro | Defecto | Qué hace |
|---|---|---|
| `min_interval` + `jitter` | 2.5 s + 0-1.5 s | Ritmo por IP. No bajes de ~2 s. |
| `cooldown_s` | 900 s | Pausa si no se pudo resolver un desafío |
| `ban_cooldown_s` | 6 h | Pausa si la IP recibe bloqueo duro |
| `captcha_mode` | `wait` | `wait` / `callback` / `fail` |
| `idle_close_s` | 300 s | Cierra el navegador tras inactividad |

## Pruebas

```bash
python -m pytest tests -q          # sin red
python -m ddguard fetch --quiet https://www.idealista.com/inmueble/110467049/
python -m ddguard fetch --quiet --out salida https://www.idealista.com/alquiler-viviendas/madrid/tetuan/
```

- `--quiet`: salida limpia (estado, tiempo, tamaño y título de cada página).
- `--out CARPETA`: guarda el HTML de cada página y un `results.json` con un resumen (precio, ubicación, características / tarjetas de búsqueda). Es solo para comprobar; tu motor hace el parseo.
- Proxy: `--proxy http://user:pass@host:puerto`, o la variable de entorno `DDGUARD_PROXY` (así las credenciales no aparecen en la línea de comandos).
- Un anuncio retirado (Idealista muestra la portada en la misma URL) se devuelve como `NOT_FOUND`, no como datos.

## Límites conocidos

- DataDome cambia con el tiempo. El perfil TLS (`safari2601`) y el navegador pueden necesitar ajustes cada cierto tiempo.
- El interstitial se resuelve solo. El slider CAPTCHA no: necesita una persona (noVNC) o un servicio de pago.
- Una IP que acumula muchos 403 seguidos pasa a slider y luego a bloqueo de horas. El módulo está hecho para evitarlo, pero el ritmo de peticiones lo eliges tú.
