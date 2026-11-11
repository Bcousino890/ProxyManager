# ProxyManager — empezar en una sesión nueva

Fecha de corte: 11 de noviembre de 2026. Repositorio: `https://github.com/Bcousino890/ProxyManager`. Lee este archivo, `STATUS.md`, `NEXT-TASK.md`, `MODELS.md` y luego el [encargo original](original-brief.md). El encargo define el objetivo, pero el propietario indicó que las reglas y cifras operativas pueden cambiar. Documenta los cambios en `DECISIONS.md`.

## Estado verificable

La rama de trabajo es `codex/initial-platform`. El proyecto es un paquete Python 3.12 con FastAPI, SQLite y HTTPX. Tiene API básica, claves, sesiones, catálogo de proxies con credenciales cifradas, validación de destinos HTTPS y tests. No es un producto desplegado. El [roadmap](../docs/roadmap.md) detalla las ocho fases. `STATUS.md` separa implementado, probado y pendiente.

## Arranque

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
cp .env.example .env
# Rellenar claves locales; nunca subir .env.
set -a; source .env; set +a
.venv/bin/pytest -q
.venv/bin/uvicorn proxymanager.app:app --host 127.0.0.1 --port 8000
```

La API OpenAPI está en `/docs`. Sin claves, los endpoints protegidos deniegan acceso. Sin allowlist, `/scrape` no llega a ningún destino. Para importar un archivo privado `host:port:usuario:contraseña`:

```bash
set -a; source .env; set +a
.venv/bin/python -m proxymanager.importer /ruta/privada/data.txt --provider nombre-del-lote
```

El importador valida el archivo entero antes de insertar filas, evita duplicados por host y puerto, cifra las credenciales y marca tipo/país como desconocidos. No imprime secretos. El archivo privado, la clave de cifrado y la base SQLite local **no están en GitHub**. Si una sesión no tiene acceso a ellos, puede trabajar en código y tests; no debe afirmar que importó o probó esos proxies.

## Reglas de trabajo para Codex o Claude Code

- Crear una rama por cambio a partir del último commit de trabajo; dejar commits claros y pruebas ejecutadas. Coordinar antes de fusionar cambios simultáneos.
- Escribir en `STATUS.md` qué se implementó, qué se probó y qué sigue pendiente. Actualizar `NEXT-TASK.md` al cerrar una tarea.
- No guardar claves, cookies, contraseñas, datos sensibles, `.env`, bases SQLite ni el archivo privado de proxies en commits, issues, logs o documentación.
- Hacer solicitudes automatizadas y pruebas de carga solo en destinos propios o autorizados. No usar proxies para eludir bloqueos ni simular una integración DataDome real.
- Pedir autorización específica antes de comprar servicios, aceptar contratos, borrar producción o ejecutar carga en infraestructura externa.
- Mantener configurables los valores operativos. Documentar la razón de cualquier valor por defecto y la evidencia de cualquier cambio.
- Verificar las afirmaciones de completitud con tests y evidencias; 30 días de operación requieren 30 días transcurridos.
