# Conectar un manejador de desafíos (opcional)

ProxyManager **no incluye** ninguna lógica para resolver CAPTCHA ni superar sistemas antibot (DataDome u otros). Solo ofrece un punto de extensión: sin manejador, un desafío se devuelve tal cual con `success: false`, `challenge.handled: false` y **sin cobro**.

## Cuándo se invoca

En `POST /scrape`, solo si se cumplen las tres condiciones:
1. Hay un manejador configurado (`PROXYMANAGER_CHALLENGE_HANDLER=paquete.modulo:fabrica`).
2. La respuesta contiene marcadores de desafío (`validation.challenge_detected`).
3. El cliente envió `"solve_challenges": true`.

## Contrato (`src/proxymanager/challenges.py`)

```python
class MiManejador:
    name = "mi-manejador"

    async def handle(self, context: ChallengeContext) -> ChallengeResolution | None:
        # context: url, method, status_code, headers, html, session_id, proxy_id, cookies
        return ChallengeResolution(resolved=True, html="...", status_code=200, set_cookies=["sid=...; Path=/"])
```

- Devuelve `None` si no aplica. Si lanzas una excepción, se contiene: el cliente recibe `challenge.error = "handler_failed"` y el mensaje no se expone.
- Si `resolved=True`, se revalida el resultado con las mismas reglas (2xx, texto esperado, sin marcadores). El cargo extra `PROXYMANAGER_CREDITS_CHALLENGE_RESOLVED` (por defecto 0) solo se suma si la revalidación sale bien.
- `set_cookies` se guardan cifradas en la sesión del cliente.
- `fabrica` puede ser una clase sin argumentos, una función que devuelve el objeto o el objeto ya construido.

## Responsabilidad

Quien conecte un manejador debe tener **autorización sobre el destino** y cumplir sus condiciones de uso y la ley aplicable. El encargo original del proyecto excluye la evasión de controles de acceso de terceros; usar esta interfaz con ese fin queda fuera de ese alcance. Para pruebas legítimas (p. ej. una instalación propia o autorizada de DataDome) este es el lugar donde integrarlas y medirlas.

## Probar

`tests/test_accounts.py::test_challenge_handler_plugs_in_and_is_opt_in` muestra un manejador de prueba completo.


## Ejemplo conectado: ddguard (Idealista)

Guía de instalación en el VPS (imagen aparte, noVNC, qué es automático y qué no): `docs/ddguard-vps.md`.

`integrations/ddguard/` trae un manejador real para Idealista (`curl_cffi` + Camoufox) y
`integrations/ddguard_handler.py` lo adapta al contrato de arriba. **Solo actúa sobre
idealista.com**: para cualquier otro destino devuelve `None` sin tocar nada.

Dos llaves, independientes, deben estar puestas antes de que una solicitud real lo invoque:

1. **Configuración del despliegue:** `pip install -e '.[ddguard]'` y
   `PROXYMANAGER_CHALLENGE_HANDLER=integrations.ddguard_handler:build_handler`.
2. **Autorización declarada:** en `/admin/` → *Desafíos*, indicar quién autorizó el uso contra
   Idealista y una referencia verificable (correo, contrato, ticket). Queda registrado con fecha
   y visible en el panel. Sin esa declaración activa, `/scrape` nunca llama al manejador aunque
   esté configurado: la solicitud se informa como desafío no resuelto y no se cobra.

Ninguna de las dos llaves comprueba por software que la autorización sea real. Quien la declara
es responsable de que lo sea. Variables opcionales: `DDGUARD_STORE_DIR`, `DDGUARD_HEADLESS`,
`DDGUARD_CAPTCHA_MODE`, `DDGUARD_MIN_INTERVAL`, `DDGUARD_JITTER`, `DDGUARD_COOLDOWN_S`,
`DDGUARD_BAN_COOLDOWN_S` (ver `integrations/ddguard/README.md` para el detalle de cada una).
