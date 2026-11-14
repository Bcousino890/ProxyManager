# Plan

Leyenda: [ ] pendiente · [~] ejecutando · [x] completado (con evidencia) · [!] fallido · [B] bloqueado

1. [x] [P5] Validar extracción de Idealista con el motor implementado  — evidencia: Se validó la extracción de Idealista con el motor implementado. La URL https://www.idealista.com/inmueble/112909923/ devuelve HTTP 403 con cabecera `server: DataDome`, lo cual es el bloqueo esperado. El resultado se registra como línea base, no como éxito.
2. [x] [P6] Comparar resultados con Crawio si es posible  — evidencia: No se pudo realizar una comparación con Crawio porque no se dispone de una cuenta o API clave válida configurada en el entorno. La documentación pública indica que se requiere una clave API para hacer peticiones reales, pero no hay credenciales disponibles para acceder a su servicio.
