# Despliegue con dominio sslip.io

Requisitos: un VPS con Docker y Docker Compose, IPv4 pública y puertos 80/443 abiertos. **Este repositorio no contrata ni crea servidores**; hazlo tú y ejecuta esto en él.

1. Calcula el dominio: sslip.io resuelve `cualquier-nombre.A-B-C-D.sslip.io` a la IP `A.B.C.D`. Para la IP `203.0.113.10`: `proxymanager.203-0-113-10.sslip.io`.
2. `cd deploy && cp .env.example .env` y rellena `DOMAIN`, `PROXYMANAGER_ADMIN_KEY` (larga y aleatoria) y `PROXYMANAGER_CREDENTIAL_KEY` (Fernet).
3. `docker compose up -d --build`. Antes puedes ejecutar `python -m proxymanager.doctor` (ver `docs/real-testing.md`). Caddy emite el certificado Let's Encrypt al primer acceso.
4. Abre `https://TU-DOMINIO/app/` (consola), `https://TU-DOMINIO/docs/` (documentación), `https://TU-DOMINIO/api-reference` (OpenAPI).
5. Regístrate en la consola y recarga créditos a clientes con:
   `curl -X POST https://TU-DOMINIO/v1/admin/credits -H 'x-api-key: ADMIN' -H 'content-type: application/json' -d '{"email":"cliente@example.com","credits":5000,"plan":"pro"}'`

Notas: sslip.io es un servicio de terceros gratuito sin garantías; para vender de forma seria conviene un dominio propio (cambia solo `DOMAIN`). Let's Encrypt limita certificados por dominio registrable y `sslip.io` es compartido: si el límite se agota, la emisión falla. Ejecuta **un solo proceso API** (los límites de tasa y la cola de salud están en memoria). Haz copias de seguridad del volumen `pmdata` (SQLite con cuentas y claves cifradas).

Después del despliegue, ejecuta la prueba de humo de `docs/real-testing.md` (`python -m proxymanager.smoke …`). Los manejadores de desafíos opcionales se colocan en `deploy/handlers/` (montado en `/handlers`).
