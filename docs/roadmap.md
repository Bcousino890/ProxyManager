# Ocho fases de ProxyManager

Estado al 11 de noviembre de 2026. Las reglas y los valores operativos son revisables; una fase con código aún requiere validación antes de declararse completada en operación.

| Fase | Estado | Evidencia y siguiente paso |
|---|---|---|
| 1. Investigación y arquitectura | Parcial | Diseño, fuentes de coste y decisiones iniciales documentadas; precios finales y alcance revisables. |
| 2. Backend funcional | Hecha en código | API, sesiones, cookies, proxies, comprobaciones y permisos con pruebas locales; falta revisión independiente y validación operativa. |
| 3. DataDome y CAPTCHA | Pendiente | Laboratorio local con CAPTCHA genérico; no hay acceso ni pruebas de DataDome real. |
| 4. Benchmark | Hecha en código | Cola, límites, métricas y resumen probados con transporte simulado; 100.000 solicitudes requieren destino, presupuesto y autorización específicos. |
| 5. Panel | Hecha en código | Gestión de proxies, sesiones, benchmarks, auditoría y gastos; prueba Chromium/axe local, pendiente validación operativa completa. |
| 6. Despliegue | Hecha en código | Docker, Caddy, configuración y copia de seguridad preparados; sin VPS, despliegue ni gasto real. |
| 7. Validación | Pendiente | [Plantilla](reports/validation-template.md) sin resultados; falta evaluación real, revisión de seguridad independiente y evidencia reproducible. |
| 8. Operación prolongada | Pendiente | Requiere 30 días reales de métricas, incidencias y costes. |

La medición de IP de salida, ASN y geolocalización necesita un servicio aprobado por el propietario. El seguimiento de fases y pruebas está en [handoff/STATUS.md](../handoff/STATUS.md); el [siguiente trabajo](../handoff/NEXT-TASK.md) evita duplicar tareas entre sesiones.
