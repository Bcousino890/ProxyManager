# Decisiones revisables

| Fecha | Decisión | Motivo | Condición de revisión |
|---|---|---|---|
| 2026-11-11 | Nombre: ProxyManager; repositorio independiente de la web Zinto | Instrucción del propietario | Nueva instrucción explícita |
| 2026-11-11 | Monolito modular Python/FastAPI + SQLite inicial | Coste y simplicidad para el TFG | Medición de carga o necesidades de operación |
| 2026-11-11 | Reglas por variables de entorno; deny by default para destinos | El propietario quiere flexibilidad, con autorización explícita | Nuevo requisito documentado |
| 2026-11-11 | Conexiones importadas como `unknown`/`ZZ` | No se verificó tipo ni país | Comprobación de IP de salida, ASN y proveedor |
| 2026-11-11 | Presupuesto indicativo de 25 USD; no controlador de gastos aún | Cifra inicial del encargo | Presupuesto aprobado y costes finales |

| 2026-11-11 | AWS por horas para pruebas; proveedor mensual se decide al final | Instrucción del propietario; evita compromiso temprano | Mediciones y precio final de 30 días |

| 2026-11-16 | Plataforma comercial: cuentas, claves `pm_live_` (solo hash), créditos por solicitud validada, consola `/app/`, docs `/docs/` (OpenAPI en `/api-reference`) | Instrucción del propietario: vender el servicio por API | Pasarela de pago, dominio propio o cambio de política |
| 2026-11-16 | `PROXYMANAGER_ALLOW_ANY_PUBLIC_HOST` (por defecto **false**): permite cualquier host HTTPS público manteniendo bloqueo de IP privadas y lista `BLOCKED_HOSTS` | Un servicio comercial no puede tener allowlist fija, pero el encargo original exige autorización de destinos | El propietario aprueba la política de uso aceptable y la activa conscientemente |
| 2026-11-16 | No se implementa evasión antibot, resolución de CAPTCHA ni rotación para esquivar bloqueos; la documentación pública lo dice | Restricción del encargo original (§1, §4) | Autorización expresa y alcance legal documentado |
| 2026-11-16 | Punto de extensión `challenges.py` (manejador opcional, vacío por defecto, opt-in por solicitud `solve_challenges`); sin implementación contra DataDome u otros | Petición del propietario de dejar la estructura para que un programador la conecte | Autorización expresa/instalación DataDome autorizada para pruebas |
| 2026-11-16 | `/scrape` elige proxies sanos (comprobación activa + pasiva), IP fija por sesión, un reintento | Petición del propietario | Mediciones reales de fallos |

No conviertas hipótesis en hechos. La documentación del proveedor no sustituye mediciones propias.
