# ProxyManager: diseño inicial

ProxyManager es una plataforma de investigación para experimentos HTTP autorizados. El repositorio de Zinto es independiente. El nombre del producto es ProxyManager.

## Enfoque

Se elige un monolito modular Python/FastAPI, con SQLite y HTTPX, para reducir coste y facilitar evaluación. Las alternativas consideradas fueron microservicios (mayor operación) y una interfaz sin backend (no evaluable mediante API). La configuración irá en variables de entorno y persistirá las reglas operativas que cambien con el tiempo. Los límites de seguridad y la autorización de destinos seguirán explícitos.

## Primera entrega

API ejecutable con salud, autenticación por claves separadas, creación y consulta de sesiones, y solicitud HTTP a destinos autorizados con clasificación de resultado. Se prueban la denegación por defecto, aislamiento de sesiones y la diferencia entre HTTP 200 y contenido válido. El resto del TFG se desarrollará por fases; no se afirmará que DataDome real, 100.000 solicitudes o 30 días estén verificados sin evidencia.

## Restricciones

Sin pagos, tráfico de carga externo ni bypass de controles. La configuración es revisable: hosts, patrón de contenido esperado, TTL, límites, presupuesto y claves se definen fuera del código. El bloqueo de redes privadas y redirecciones forma parte del camino de solicitud. Antes de producción se requiere prueba de seguridad de resolución DNS y HTTPS.
