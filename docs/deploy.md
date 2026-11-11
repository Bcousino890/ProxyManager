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

## Dominio gratuito y temporal (para pruebas de horas)
No hace falta comprar ni registrar nada: con la IP pública del servidor, `A-B-C-D.sslip.io` resuelve a esa IP sin cuenta (por ejemplo `203.0.113.5` → `203-0-113-5.sslip.io`). Usa ese nombre como `PM_DOMAIN`; Caddy obtendrá el certificado de Let's Encrypt si 80/443 están abiertos. Es un servicio de terceros y compartido (límites de Let's Encrypt incluidos): válido para una prueba breve, no para producción. Alternativa sin dominio ni puertos públicos: túnel SSH al puerto 8000 del servidor. Para uso continuado, usa un dominio propio.

## Copias de seguridad de SQLite

Con la base persistente en `/data/proxymanager.db`, ejecuta `scripts/backup.sh /ruta/al/volumen/proxymanager.db /ruta/privada/backups 7` desde el host. Requiere `sqlite3` CLI. Usa `sqlite3 .backup` para una copia consistente mientras la API está activa, crea el directorio con modo 0700 y cada copia con 0600. El último argumento conserva siete días de copias (mínimo uno); solo elimina los archivos `proxymanager-*.sqlite3` antiguos de ese directorio. Programa el comando con el planificador del servidor y comprueba periódicamente que una copia puede abrirse y restaurarse. Mantén las copias fuera del volumen que se pueda borrar junto con la instancia.

La clave de cifrado `PROXYMANAGER_CREDENTIAL_KEY` debe guardarse y respaldarse **por separado** con acceso restringido. El script solo copia SQLite: no lee ni incluye `.env` ni la clave. Sin esa clave, las credenciales de proxies y cookies cifradas no se recuperan aunque la base se restaure.

## Antes de exponerlo
Siguen pendientes una revisión de seguridad independiente, despliegue autorizado y monitorización de las copias y alertas. Un solo proceso significa que no hay alta disponibilidad: un reinicio corta las ejecuciones en curso; los benchmarks quedan como `failed: interrupted`.
