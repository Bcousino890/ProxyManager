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
