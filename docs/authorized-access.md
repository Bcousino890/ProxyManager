# Acceso autorizado a sitios con protección anti-bots

**Qué hace ProxyManager:** detecta desafíos y bloqueos (CAPTCHA, 403/429, DataDome…) y los muestra como "bloqueado", separado del estado del proxy.
**Qué no hace, ni hará:** resolver CAPTCHA, falsear la huella del navegador ni esquivar la protección de un sitio de terceros. Si un sitio os autoriza, la solución es que **el propietario del sitio** la haga efectiva en su lado.

## Qué pedir al sitio (checklist)
1. **Autorización por escrito** del titular del sitio (no solo permiso verbal) con alcance, finalidad (p. ej. proyecto de la universidad), periodo y límites de volumen. Guardadla fuera del repositorio.
2. **Forma de identificaros**, a elegir con ellos:
   - lista permitida de la **IP pública** del servidor (o del rango de los proxies) en su protección;
   - un **User-Agent** propio que os identifique (`PROXYMANAGER_USER_AGENT`);
   - una **cabecera o token** que ellos os entreguen (`PROXYMANAGER_HOST_HEADERS`).
3. **Límites acordados**: solicitudes por segundo y ventana horaria. Aplicadlos con el límite `rps` de los benchmarks y la concurrencia por proxy (`PROXYMANAGER_PROXY_MAX_INFLIGHT`).
4. **Contacto técnico** al que avisar si algo va mal, y cómo parar de inmediato.

## Plantilla de mensaje (adaptar)
> Asunto: Solicitud de acceso técnico autorizado para un proyecto de investigación
> Hola, [nombre]. Somos [equipo] de [universidad/organización] y, según [referencia de la autorización], vamos a consultar [alcance: p. ej. N anuncios concretos] con fines de [finalidad]. Para evitar falsos bloqueos, ¿podéis incluir en lista permitida la IP pública [IP del servidor] y/o indicarnos la cabecera, token o User-Agent que prefiráis que usemos? Proponemos un máximo de [X] solicitudes por segundo entre [horas]. Contacto técnico: [nombre, correo, teléfono]. Si queréis que paremos, lo haremos de inmediato.

## Destinos autorizados desde el panel
Además de `PROXYMANAGER_ALLOWED_HOSTS` (entorno, no editable desde el panel), la sección **Destinos** permite añadir y quitar destinos a mano, sin reiniciar. Reglas: solo la clave de administración de entorno (no se puede delegar en claves adicionales), solo dominios completos (sin IP, puerto, ruta, comodines ni nombres internos), obligatoria la **referencia de la autorización** y una confirmación expresa, queda auditado quién y cuándo, y se siguen bloqueando direcciones privadas y todo lo que no sea HTTPS estándar. Quitar un destino surte efecto de inmediato. No guardes tokens en la referencia.

## Configuración en ProxyManager
Todo por entorno; nada de esto se muestra en la API, el panel, los registros ni el repositorio.
```bash
PROXYMANAGER_USER_AGENT="Proyecto-Universidad/1.0 (contacto@ejemplo.org)"
# Solo para hosts de PROXYMANAGER_ALLOWED_HOSTS; se envían únicamente a ese host exacto:
PROXYMANAGER_HOST_HEADERS='{"www.sitio-autorizado.example": {"X-Acceso-Autorizado": "TOKEN_ENTREGADO_POR_EL_SITIO"}}'
```
Se rechazan cabeceras reservadas (`Host`, `Cookie`, `X-API-Key`, `Content-Length`, …), valores con saltos de línea y, en modo estricto, hosts fuera de la lista permitida.

## Verificar que funciona
1. Una sola solicitud en el Playground contra una URL autorizada. Si sigue saliendo "bloqueado", el sitio aún no ha aplicado vuestra autorización: no insistáis ni subáis la carga; volved a hablar con ellos.
2. Si responde bien, subid gradualmente respetando los límites acordados y anotad la fecha y la evidencia en `handoff/STATUS.md` (sin datos del sitio ni credenciales).
