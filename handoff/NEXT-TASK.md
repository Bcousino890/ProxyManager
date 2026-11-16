# Siguiente entrega

Plataforma de cliente (cuentas, claves, créditos, consola `/app/`, docs `/docs/`) implementada y probada localmente; ver STATUS.md (16 nov). Siguiente:

1. Desplegar con `deploy/README.md` en el VPS del propietario (pedir IP/acceso; no comprar nada sin autorización) y verificar HTTPS, `/app/`, `/docs/` y un `/scrape` real a un destino autorizado.
2. Decidir con el propietario la política de uso aceptable y activar `PROXYMANAGER_ALLOW_ANY_PUBLIC_HOST` solo entonces.
3. Pagos (Stripe u otro, requiere cuenta del propietario), verificación de correo y recuperación de contraseña.
4. Salud/rotación de proxies en la selección de `/scrape`, y worker persistente para benchmarks (los límites actuales son en memoria: un solo proceso).
