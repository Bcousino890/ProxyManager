# ddguard en el VPS: qué es automático y qué no, y cómo instalarlo aparte

Esta página es para la sesión que instale esto en el VPS real. Nada de lo de aquí se ha
ejecutado contra un VPS ni contra Idealista; está escrito a partir del código subido y de
pruebas locales sin red real (ver `handoff/STATUS.md`, 16 nov 2026).

## El flujo, tal como queda (cliente → nosotros → destino)

```
Cliente                         ProxyManager                              Destino
  │  POST /scrape                   │                                        │
  │  {"url": "...", ...}            │                                        │
  ├─────────────────────────────────►                                        │
  │                                 │  1. HTTP normal (httpx)                │
  │                                 ├───────────────────────────────────────►│
  │                                 │◄───────────────────────────────────────┤
  │                                 │  2. ¿200 y sin marcadores de desafío?  │
  │                                 │     → se valida y se responde          │
  │                                 │                                         │
  │                                 │  2b. ¿Desafío? y "solve_challenges":true│
  │                                 │      y manejador conectado Y AUTORIZADO │
  │                                 │      en /admin/ → Desafíos              │
  │                                 ├──────► ddguard (dentro del mismo        │
  │                                 │         contenedor): HTTP con huella    │
  │                                 │         de navegador, y si hace falta,  │
  │                                 │         un navegador real (Camoufox)    │
  │                                 │         abre esa URL                    │
  │                                 │◄──────┤                                 │
  │◄─────────────────────────────────┤  3. Responde: estado, cabeceras,      │
  │  {"success":…, "html":…, …}     │     cuerpo, validación y challenge{}   │
```

Esto coincide con lo que mostraste: una sola llamada `POST /scrape`, una sola respuesta con el
resultado. La diferencia frente a un anuncio genérico de "el sistema antibot se encargó de ello"
está en el paso 2b, y es donde hay que ser precisos:

## Qué se resuelve solo y qué necesita una persona

| Situación | ¿Automático? |
|---|---|
| Página normal, sin desafío | Sí. Siempre. |
| "Interstitial" (`rt:'i'`, verificación de dispositivo) | Sí, el navegador la supera solo en ~20-30 s, sin que nadie mire. |
| CAPTCHA deslizante (`rt:'c'`) | **No, con la configuración actual.** `ddguard` necesita que una persona lo resuelva viendo el navegador por noVNC (`captcha_mode="wait"`), o que conectes tú un servicio de pago que lo resuelva (`captcha_mode="callback"`, no incluido). En modo sin pantalla (`headless=True`), si aparece un deslizante **falla directamente** en vez de intentar nada: así lo decidió quien escribió `ddguard` (ver `integrations/ddguard/solver.py`, función `_wait_clear`). |
| IP bloqueada ("uso indebido", `t='bv'`) | No se puede resolver; se pausa esa IP varias horas. |

Así que si el plan es anunciar "resuelto automáticamente" sin matices, hay que decidir entre dos
caminos antes de activar nada: (a) dejar el deslizante para resolverlo tú a mano por noVNC cuando
toque, o (b) contratar y conectar un servicio de resolución de CAPTCHA de pago (no es parte de
este proyecto; habría que evaluarlo aparte).

## Instalación en el VPS, en su propia imagen

No se mezcla con la imagen normal de la API: es una imagen aparte (`Dockerfile.ddguard`), más
pesada porque incluye un navegador real. Dentro de la misma carpeta aislada `/opt/proxymanager/`
(ver `deploy/README.md`):

```bash
cd /opt/proxymanager/deploy
# Variables específicas de ddguard, además de las de .env:
echo 'DDGUARD_HEADLESS=false' >> .env        # false = navegador visible por noVNC (necesario para el deslizante)
echo 'DDGUARD_CAPTCHA_MODE=wait' >> .env
echo 'DDGUARD_VNC_PASSWORD=pon-una-contraseña-larga-aqui' >> .env

docker compose -f docker-compose.yml -f docker-compose.ddguard.yml up -d --build
```

Esto construye `Dockerfile.ddguard` (instala `curl_cffi`/Camoufox/Playwright, descarga el
navegador con `camoufox fetch`, arranca Xvfb + x11vnc + noVNC dentro del propio contenedor) y
monta un volumen `dd_sessions` (cookies/sesión por IP, separado de `pmdata`). El puerto 6080
(noVNC) se publica **solo en `127.0.0.1` del VPS**, nunca abierto a Internet:

```bash
# desde tu ordenador, abre un túnel y entra en tu propio navegador:
ssh -L 6080:localhost:6080 usuario@TU-VPS
# luego: http://localhost:6080/vnc.html  (contraseña: DDGUARD_VNC_PASSWORD)
```

Esto todavía **no activa nada**: `PROXYMANAGER_CHALLENGE_HANDLER` queda configurado, pero
`/scrape` sigue sin invocarlo hasta declarar la autorización en `/admin/` → *Desafíos* (doble
llave ya existente, ver `docs/extending-challenge-handlers.md`).

## Qué falta verificar en el VPS real (no se pudo hacer aquí)

- Que `Dockerfile.ddguard` construya sin errores. Faltan librerías de sistema para Camoufox que
  no pude confirmar sin una máquina real; si `camoufox fetch` o el lanzamiento del navegador
  fallan por una dependencia que falta, instala el paquete `apt` que falte y vuelve a construir.
- Que `python -m ddguard login` (dentro del contenedor, con `DISPLAY=:99`) funcione para iniciar
  sesión en Idealista si se decide usarlo (es opcional; las páginas de anuncios son públicas).
- Rendimiento real del deslizante y del ritmo de peticiones (`DDGUARD_MIN_INTERVAL`,
  `DDGUARD_COOLDOWN_S`) contra el entorno que de verdad se vaya a usar.
- Anota la evidencia real en `handoff/STATUS.md` cuando se pruebe, no antes.
