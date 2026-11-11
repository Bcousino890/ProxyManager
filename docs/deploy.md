# Despliegue con Docker y HTTPS (sin ejecutar aún)

**Estado:** ficheros preparados y validados parcialmente. No se ha construido la imagen (el entorno de desarrollo no tenía demonio de Docker) ni se ha desplegado en ningún servidor. Requiere autorización del propietario para elegir servidor y gasto.

## Qué hay
- `Dockerfile`: Python 3.12 slim, usuario sin privilegios, volumen `/data` para SQLite, `HEALTHCHECK` sobre `/health`, **un único worker** (cola, límite de solicitudes y carga en vuelo son por proceso).
- `docker-compose.yml`: API (solo expuesta a la red interna, sistema de archivos de solo lectura, sin capacidades, `PROXYMANAGER_STRICT=1`) y Caddy (HTTPS automático con Let's Encrypt, HSTS).
- `deploy.env.example` → copiar a `.env` en el servidor. `.env` nunca se sube a git.

## Pasos (cuando el propietario decida el servidor)
1. Dominio con registro A/AAAA apuntando al servidor; puertos 80 y 443 abiertos; resto cerrado (SSH solo desde IPs propias).
2. En el servidor: clonar el repositorio, `cp deploy.env.example .env`, rellenar claves distintas (≥16 caracteres), clave Fernet y `PROXYMANAGER_ALLOWED_HOSTS` solo con destinos propios o autorizados.
3. `docker compose up -d --build`. Si la configuración es insegura el contenedor no arranca (modo estricto); mira `docker compose logs api`.
4. Importar proxies dentro del contenedor, sin dejar el archivo en el servidor al terminar:
   `docker compose run --rm -v /ruta/privada/data.txt:/tmp/data.txt:ro api python -m proxymanager.importer /tmp/data.txt --provider NOMBRE`
5. Abrir `https://TU_DOMINIO/panel`, comprobar proxies, y solo después autorizar pruebas externas.

## Antes de exponerlo
Siguen pendientes revisión de seguridad, copias de seguridad del volumen `/data` **y de la clave Fernet por separado** (sin la clave, las credenciales cifradas son irrecuperables), alertas y monitorización. Un solo proceso significa sin alta disponibilidad: un reinicio corta las ejecuciones en curso (los benchmarks quedan `failed: interrupted`).
