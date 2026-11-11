# Siguiente entrega

TLS por proxy resuelto y verificado con diez conexiones; ver STATUS.md y el informe JSON. Cookies persistentes cifradas integradas en `/scrape` con pruebas locales. Rate limiting y auditoría hechos (ver STATUS.md). Validación de configuración (PROXYMANAGER_STRICT) y purga de auditoría hechas. Permisos por alcance y límites de cookies hechos. Fase 2 casi cerrada: falta revisión de seguridad y prueba funcional autorizada fuera del simulador antes de exponer el servicio. Hacer una prueba funcional autorizada fuera del entorno simulado.

El usuario confirmó VPS existente, sin DataDome. Esperando proveedor/host/usuario SSH o alias local para inspección de infraestructura. No comprar servicios. Preparar acceso académico a DataDome sin enviarlo a terceros sin autorización.

Las comprobaciones de salud usan ya workers persistentes con lease y reintentos (ver STATUS.md). Selección por salud y métricas por proxy hechas (ver STATUS.md). Prueba real con las diez conexiones HECHA (ver STATUS.md, 11 nov 17:33). Cola de benchmarks acotada implementada (ver STATUS.md). Siguiente: ejecutar `scripts/ip_survey.py` con un servicio de IP propio/aprobado; benchmark real escalonado (50 → 500 → …) en destino autorizado con presupuesto y aprobación explícita; panel (fase 5). Pruebas multiproceso reales pendientes.
