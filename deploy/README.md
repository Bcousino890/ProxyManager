# Despliegue en el VPS (carpeta propia, aislado de otros proyectos)

Requisitos: un VPS con Docker y Docker Compose, IPv4 pública. **Este repositorio no contrata ni
crea servidores**; esto se ejecuta en uno que ya tengas.

## 0. Comprobaciones antes de tocar nada

El VPS se usa para otras cosas, así que primero hay que no chocar con lo que ya corre ahí.

```bash
docker --version && docker compose version   # si falta, instala Docker Engine + plugin compose
sudo ss -tlnp | grep -E ':80 |:443 '          # ¿algo ya escucha en 80/443?
```

- **Si nada escucha en 80/443:** sigue la Opción A (Caddy propio, más simple).
- **Si ya hay un Nginx/Caddy/Traefik sirviendo otros proyectos:** sigue la Opción B (sin tocar
  esos puertos; el proxy existente apunta a ProxyManager).

## 1. Carpeta propia y aislada

Todo ProxyManager vive en una sola carpeta, separada de cualquier otro proyecto del VPS:

```bash
sudo mkdir -p /opt/proxymanager && sudo chown "$USER" /opt/proxymanager
git clone https://github.com/Bcousino890/ProxyManager /opt/proxymanager
cd /opt/proxymanager/deploy
cp .env.example .env   # rellenar DOMAIN, PROXYMANAGER_ADMIN_KEY y PROXYMANAGER_CREDENTIAL_KEY
```

`docker-compose.yml` fija `name: proxymanager`, así que **todos** sus contenedores, redes y
volúmenes quedan con el prefijo `proxymanager_`/`proxymanager-`, sin importar qué otras cosas
corran en el mismo Docker del VPS. Nada de este despliegue toca servicios, carpetas o unidades
`systemd` de otros proyectos.

```bash
set -a; source .env; set +a
python3 -m venv .venv-check && .venv-check/bin/pip install -q -e '..[test]'
.venv-check/bin/python -m proxymanager.doctor   # corrige cualquier [ERROR] antes de seguir
```

## 2A. Opción A — dominio sslip.io con Caddy propio (puertos 80/443 libres)

sslip.io resuelve `cualquier-nombre.A-B-C-D.sslip.io` a la IP `A.B.C.D`. Para la IP
`203.0.113.10`: `DOMAIN=proxymanager.203-0-113-10.sslip.io`.

```bash
docker compose up -d --build
```

Caddy emite el certificado Let's Encrypt al primer acceso a `https://$DOMAIN/`.

## 2B. Opción B — ya hay un proxy en el VPS (no se tocan 80/443)

No se levanta el contenedor `caddy`; la API publica su puerto solo en `localhost`, y el proxy que
ya tienes le añade un sitio nuevo.

```bash
docker compose up -d --build api   # sin --build caddy; solo el servicio api
```

Edita `docker-compose.yml` (o mejor, crea `deploy/docker-compose.override.yml` para no tocar el
original) para publicar la API en localhost, por ejemplo:

```yaml
services:
  api:
    ports:
      - "127.0.0.1:8100:8000"
```

y añade un sitio al proxy que ya tengas apuntando a `127.0.0.1:8100`. Ejemplo si ese otro proxy
también es Caddy, como bloque nuevo en su Caddyfile (sin tocar los bloques de tus otros
proyectos):

```
proxymanager.tu-dominio.example {
    reverse_proxy 127.0.0.1:8100
}
```

## 3. Verificar

```bash
.venv-check/bin/python -m proxymanager.smoke --base-url https://TU-DOMINIO \
  --target https://tu-sitio-autorizado.example/ --expected-text "texto esperado"
```

Abre `https://TU-DOMINIO/app/` (consola de clientes), `https://TU-DOMINIO/admin/` (panel de
administración), `https://TU-DOMINIO/docs/` (documentación pública). Guía completa en
`docs/real-testing.md`.

## 3B. Crea el primer administrador de inmediato

`POST /v1/admin/register` (el formulario de `/admin/` la primera vez) ya no pide la clave maestra: funciona como un alta normal, pero **solo una vez**. Mientras no exista ningún administrador, cualquiera que entre primero a `https://TU-DOMINIO/admin/` puede registrarse con control total. Entra y crea el tuyo en cuanto el servicio esté arriba, antes de compartir la URL con nadie. `PROXYMANAGER_ADMIN_KEY` sigue sirviendo como acceso de emergencia por cabecera si alguna vez pierdes el acceso.

## 4. Primeros pasos de administración

```bash
# crea tu propia cuenta en /app/, o recarga créditos a un cliente ya registrado:
curl -X POST https://TU-DOMINIO/v1/admin/credits -H 'x-api-key: ADMIN' -H 'content-type: application/json' \
  -d '{"email":"cliente@example.com","credits":5000,"plan":"pro"}'
```

Importa tus proxies en `/admin/` → *Proxies* (ver `handoff/NEXT-TASK.md`: las 10 conexiones del
propietario solo existen en su máquina y hay que importarlas e identificar su tipo/país reales
antes de venderlas como tales).

## 5. Manejador de desafíos ddguard (Idealista) — opcional, instalación aparte

**No lo instales si no vas a activarlo pronto.** Construye un navegador real dentro de la imagen
y es mucho más pesada. Pasos y aclaración de qué es automático y qué no: `docs/ddguard-vps.md`.
Resumen: `docker compose -f docker-compose.yml -f docker-compose.ddguard.yml up -d --build`, y
**no se activará nada en `/scrape`** hasta declarar la autorización en `/admin/` → *Desafíos*
(ver `docs/extending-challenge-handlers.md`).

## Notas

- sslip.io es un servicio de terceros gratuito sin garantías; para vender de forma seria conviene
  un dominio propio (cambia solo `DOMAIN`). Let's Encrypt limita certificados por dominio
  registrable y `sslip.io` es compartido: si el límite se agota, la emisión falla.
- Ejecuta **un solo proceso API** (los límites de tasa y la cola de salud están en memoria).
- Haz copias de seguridad del volumen `proxymanager_pmdata` (SQLite con cuentas, claves cifradas
  y catálogo de proxies): `docker run --rm -v proxymanager_pmdata:/data -v "$PWD":/backup alpine tar czf /backup/pmdata-$(date +%F).tgz -C /data .`
- Este despliegue no se ha ejecutado contra un VPS real todavía (ver `handoff/STATUS.md`): la
  sesión que lo instale debe seguir esta guía paso a paso y anotar en `handoff/STATUS.md` lo que
  de verdad funcionó, con la evidencia (salida de `doctor`/`smoke`, capturas si hace falta).
