# Despliegue rápido en un pod / VPS nuevo

## 1. Un comando
```bash
curl -fsSL https://raw.githubusercontent.com/Bcousino890/ProxyManager/main/tools/ollama-panel/deploy/bootstrap.sh | bash
```
(o `bash tools/ollama-panel/deploy/bootstrap.sh` si ya está clonado). Es idempotente. Hace: modelos en `/workspace` si existe (persisten), clona/actualiza `main` (solo fast-forward), instala Ollama + modelos + panel, venv de pruebas y **prueba de humo**.
Con token: `GITHUB_TOKEN=ghp_… bash …/bootstrap.sh` (se guarda en `~/.pod-panel/github-token`, permisos 600, nunca en el repo).

## 2. Desde tu Mac
`ssh -L 8788:127.0.0.1:8787 root@IP -p PUERTO` → <http://127.0.0.1:8788>

## 3. Panel → sección «Despliegue»
Pulsa **Comprobar**. Verde = listo. Rojo = te dice qué falta y cómo arreglarlo. Escribe **POD_ID** (consola de RunPod) y el **puerto HTTP** expuesto → te da la URL pública `https://<POD_ID>-<PUERTO>.proxy.runpod.net` y comprueba que responde.

## 4. Antes de lanzar un proyecto
- «Razonar» **desmarcado** (usa el modelo equivocado y es 5× más lento).
- «Presupuesto» con minutos (p. ej. 110).
- GitHub ⚙: rama de guardado = `main`, estrategia «Commit + subir rama + verificar».
- Puerto HTTP: elige uno que aparezca en RunPod → Connect → HTTP Services (añadir puertos reinicia el pod).

## 5. Qué garantiza el agente
No da por terminada una tarea sin evidencia: URL → `http_check`; desplegado → servicio vivo + HTTP; pública → host no local; Git → hash remoto. Al cerrar muestra «Estado verificado» con Git y aplicación por separado. Ver `AGENT.md`.

## Reversión del panel
`bash /root/rollback-panel.sh` (vuelve al código anterior) · despliegue seguro: `bash /root/restart-panel-safe.sh`.
