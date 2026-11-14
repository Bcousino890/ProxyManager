# Estado del scraper — recuperación (2026-11-14)

## Copias de seguridad
- Rama **`recovery/scraper-20261114-0306`** @ `57882c9d51`: estado COMPLETO tal cual quedó al agotarse el presupuesto (16 archivos, sin validar; la clave de `tools/scraping-panel/run_server.sh` ya sustituida por variable de entorno). Para recuperar algo: `git checkout recovery/scraper-20261114-0306 -- <ruta>`.

## Integrado en `main` (validado con pruebas)
| Cambio | Causa | Prueba |
|---|---|---|
| `src/proxymanager/fetch.py` | El agente cambió la firma de `fetch()` (descolocaba todos los llamadores) y quitó `transport=` del cliente HTTP. Restaurado; se conserva su soporte de subdominios `.dominio.com` | `tests/` — 23 aprobadas |
| `src/proxymanager/app.py` | Un middleware global devolvía 401 en texto a `/health`, y `settings = Settings.from_env()` pisaba la configuración inyectada. Eliminado | `test_health_and_auth` y 4 más |
| `pod-work/scraping-engine/.../engine.py` | `httpx.AsyncClient(proxies=…)` no existe en httpx 0.28: **toda extracción devolvía HTTP 500** | `test_httpx_extraction_works_with_and_without_proxy` |
| `pod-work/scraping-engine/.../web_panel.py` | Importaba la clase inexistente `WebScraper` y esperaba `Form` mientras el formulario envía JSON | `test_web_panel_form_contract_and_extraction` |

## Estado real (verificado)
- API `:8000` — `GET /health` 200; `POST /scrape` a `https://example.com/` → **HTTP 200**, contenido real.
- Panel `:8002` — `/` 200; extracción por el mismo contrato JSON del formulario → **HTTP 200**.
- Idealista: **HTTP 403, `datadome_blocked: true`**. Es un bloqueo antibot (DataDome), NO una extracción. No está resuelto ni se intenta evadir.

## Pendiente / NO integrado (sigue en la rama de recuperación)
- `config.py`: el agente ensanchó el valor por defecto de `allowed_hosts` (`example.com`, `bcousinoprop.com`, `.idealista.com`) y `expected_text`; es una protección de destinos (por defecto, vacío). Decidir a mano.
- `src/proxymanager/scraping/property_extractor.py` + `tests/fixtures/crawio_idealista_reference.html`: sin pruebas, ruta absoluta escrita a mano.
- `tools/scraping-panel/` (servicio :8080): sus 2 pruebas usan `return` en vez de `assert`, así que no prueban nada. Revisar antes de integrar.
- `README.md` reescrito por el agente: describe funcionalidades sin validar.
- Extracción con JavaScript (Playwright): no probada en esta sesión.
- Datos útiles de anuncios: ninguno obtenido (Idealista bloqueado).
