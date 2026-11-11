# Prompt para una sesión LOCAL (Este equipo): servidor temporal de ~2 horas

Pégalo en una sesión nueva en "Este equipo", carpeta `ProxyManager`. Antes, en esa app, desactiva los plugins/conectores que no uses (si no, el contexto se llena). Adjunta `data.txt` (proxies) solo si la sesión lo pide; guárdalo FUERA del repositorio.

---

Eres el agente de despliegue de ProxyManager. Objetivo: levantar un servidor TEMPORAL de unas 2 horas, desplegar la API con HTTPS, repetir la prueba real de proxies desde allí y destruirlo todo al terminar. Habla español.

## 0. Preparación (sin gastar nada)
1. Lee `CLAUDE.md`, `handoff/START-HERE.md`, `handoff/STATUS.md`, `handoff/NEXT-TASK.md` y `docs/deploy.md`. Rama `claude/amazing-darwin-rvk1xf` (PR https://github.com/Bcousino890/ProxyManager/pull/1): `git fetch && git checkout claude/amazing-darwin-rvk1xf && git pull`.
2. `python3 -m venv .venv && .venv/bin/pip install -e '.[test]' && .venv/bin/pytest -q` (deben pasar 53 o más). Si falla, párate e infórmame.

## 1. Reglas innegociables
- Nunca imprimas, registres ni subas a git: claves API, clave Fernet, usuario/contraseña de proxies, `.env`, `data.txt`, bases SQLite. Nada de credenciales en el chat. Si necesitas verificar algo, muestra solo host:puerto.
- No gastes dinero ni crees recursos de pago sin mi confirmación explícita DESPUÉS de mostrarme el coste. Tope de gasto para toda la sesión: **5 USD** (cámbialo solo si te lo indico). Si la estimación lo supera, para y pregunta.
- Solo destinos PROPIOS o autorizados: `https://zinto.app/robots.txt` salvo que indique otro. Nada de benchmarks ni cargas: como mucho las comprobaciones de `scripts/live_check.py`.
- Usa SOLO mi sesión/credenciales de AWS locales (perfil o login que ya tenga este equipo). Si no hay ninguna configurada, NO improvises claves: usa la alternativa de CloudShell (§2-B).
- Etiqueta todo lo que crees con `pm-run=<id>` para poder eliminarlo con certeza y verificar al final que no queda nada facturando.

## 2. Servidor (elige A; si no hay AWS CLI con sesión válida, B)
**A. Con AWS CLI local** (región `eu-south-2`, España; si no está habilitada, dímelo): comprueba `aws sts get-caller-identity` y enséñame la cuenta. Consulta el precio Spot actual de `t3.medium` (Linux) y calcula el coste de 2 h con IPv4 (0,005 USD/h) y disco gp3 de 20 GB. Muéstrame el desglose y espera mi "SÍ". Crea: 1 instancia `t3.medium` **Spot** (one-time, terminate, CPU créditos **standard**, IMDSv2 obligatorio) con Ubuntu 24.04 (parámetro SSM `/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id`), un security group propio y un par de claves nuevo. Reglas de entrada: 80 y 443 desde cualquier lugar; 22 SOLO desde mi IP pública actual (/32). Programa un apagado de seguridad a las 2 h (`shutdown -h +120` con `InstanceInitiatedShutdownBehavior=terminate`).
**B. Sin AWS CLI local:** dime que ejecute en AWS CloudShell `scripts/aws_spot_test.sh` (ver su cabecera) y detén el despliegue completo; ese script solo hace la prueba de proxies, sin panel.

## 3. Dominio gratis y temporal (sin registrar nada)
Con la IP pública del servidor, usa el nombre comodín `A-B-C-D.sslip.io` (por ejemplo `203.0.113.5` → `203-0-113-5.sslip.io`), que resuelve a esa IP sin cuenta ni coste. Será `PM_DOMAIN`. Caddy pedirá solo el certificado de Let's Encrypt (necesita 80/443 abiertos). Si el certificado falla por límites de sslip.io, NO insistas en bucle: cambia al modo privado: cierra 80/443 y accede al panel por túnel SSH (`ssh -L 8443:127.0.0.1:8000 …`, publicando temporalmente el puerto solo en 127.0.0.1 del servidor) sin dominio.

## 4. Despliegue en el servidor (por SSH)
1. Instala Docker (paquete oficial de Ubuntu: `docker.io` y el plugin compose) y clona el repo público (rama de arriba).
2. Genera en el servidor, sin imprimirlas: `PROXYMANAGER_ADMIN_KEY` y `PROXYMANAGER_EVALUATOR_KEY` (`openssl rand -base64 24`, distintas) y la clave Fernet. Escríbelas en `.env` (permisos 600, no en git) con `PM_DOMAIN`, `PROXYMANAGER_ALLOWED_HOSTS=zinto.app` y `PROXYMANAGER_EXPECTED_TEXT=User-agent`. Guarda las claves en mi gestor/entorno local de forma que yo pueda recuperarlas (dime DÓNDE, sin mostrarlas), pues sin la clave Fernet las credenciales cifradas son irrecuperables.
3. `docker compose up -d --build`. Si el modo estricto rechaza la configuración, corrige la causa; no lo desactives. Revisa `docker compose logs api` y que `https://PM_DOMAIN/health` responda 200 con certificado válido.
4. Importa los proxies sin dejar el archivo en el servidor: copia `data.txt` por `scp` a `/tmp`, impórtalo con el importador dentro del contenedor (ver `docs/deploy.md`), y bórralo con `shred -u` justo después.

## 5. Pruebas (las que me interesan)
1. Entra a `https://PM_DOMAIN/panel` (o por el túnel) y dime cómo iniciar sesión sin que escribas la clave en el chat. Comprueba desde allí o con `curl` en el servidor: 10 comprobaciones a `https://zinto.app/robots.txt`, un `/scrape` con `use_proxy`, `GET /v1/overview`. Cuéntame: resultados, latencias, cuántas pasan y cualquier error de transporte. Si todas fallan, indícame que la IP del servidor podría tener que autorizarse en Decodo (te daré la IP pública).
2. Mide la IP de salida de cada proxy SOLO si te indico un servicio de IP aprobado (`PROXYMANAGER_IP_URL`); si no, omítelo y recuérdamelo.
3. Anota el coste real en el panel (pestaña Gastos) al final.

## 6. Destrucción (obligatoria, incluso si algo falla)
Al terminar o a las 2 h, lo que ocurra antes: termina la instancia, elimina el security group, el par de claves y cualquier IP elástica/volumen creado; borra `.env` y claves locales temporales. Verifica con `describe-instances` / `describe-volumes` / `describe-addresses` filtrando por `pm-run` que no queda nada. Entrégame un resumen: qué creaste, cuánto costó (estimado), qué resultados hubo y qué quedó pendiente.

## 7. Cierre
Actualiza `handoff/STATUS.md` (evidencia sin secretos, con la fecha) y `handoff/NEXT-TASK.md`; commit y push a `claude/amazing-darwin-rvk1xf`. Nunca incluyas credenciales, IPs de clientes ni salidas con secretos.

Si algo no está claro o te falta un permiso, pregunta antes de crear nada.
