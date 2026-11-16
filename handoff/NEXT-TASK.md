# Siguiente entrega

Todo el código para pruebas reales está listo (ver STATUS.md, 16 nov). Pasos de quien continúe:

1. En el VPS: `deploy/README.md` → `docker compose up -d --build` (primera construcción de imagen sin verificar) → `doctor` → `smoke`. Pedir IP/acceso al propietario; no comprar nada sin autorización.
2. Importar las 10 conexiones en `/admin/` desde la máquina del propietario (no están en GitHub), verificar IP de salida/ASN/país antes de fijar tipo y país, y lanzar comprobaciones.
3. El programador implementa su manejador (`docs/extending-challenge-handlers.md`) solo contra un destino/instalación DataDome **autorizados**.
4. Pendiente de producto: pagos, verificación de correo, recuperación de contraseña, auditoría de acciones de administración, política de uso aceptable aprobada antes de `PROXYMANAGER_ALLOW_ANY_PUBLIC_HOST=true`.
