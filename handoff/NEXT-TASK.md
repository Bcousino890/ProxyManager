# Siguiente entrega concreta: salud de proxies

Objetivo: convertir el catálogo existente en un gestor de conexiones verificable, sin usar proxies para eludir controles.

1. Añadir modelo persistente de resultados de salud: proxy, fecha, destino autorizado, estado, latencia, código y categoría de error. No guardar credenciales en logs.
2. Crear comprobación a un único destino HTTPS propio o autorizado, configurable mediante allowlist; una petición por proxy y límite de concurrencia. Si no hay clave de cifrado, no intentar conexiones con credenciales.
3. Exponer endpoint administrativo para lanzar comprobaciones y otro de lectura para consultar salud e historial. Mantener los trabajos largos fuera de la petición HTTP.
4. Probar autenticación, límites, destinos no autorizados, errores de proxy, respuestas válidas y ausencia de secretos en salida/DB de resultados. Usar transporte simulado en CI.
5. Ejecutar localmente solo contra `zinto.app` u otro destino propio autorizado y guardar evidencia sin credenciales. No asumir que diez puertos equivalen a diez IPs.
6. Actualizar `STATUS.md`, `DECISIONS.md` si cambian supuestos, README y tests. Commit y push de rama de trabajo.

Después: cookies y sesiones reales; investigación documentada de DataDome y laboratorio CAPTCHA; workers/benchmarks; panel; despliegue; validación; operación de 30 días. Sigue el [roadmap](../docs/roadmap.md) y el [encargo](original-brief.md).
