# Panel del Pod

Chat **agéntico** con Ollama que corre dentro del pod de Runpod. El modelo ejecuta herramientas reales
(`bash`, `read_file`, `write_file`, `list_dir`), lee los resultados y sigue hasta terminar; al final guarda
todo en `pod-work/` y lo sube a GitHub (rama `pod-sync`).

## Pod nuevo
```bash
git clone https://github.com/Bcousino890/ProxyManager.git /ProxyManager && cd /ProxyManager
git checkout pod-sync && bash tools/ollama-panel/setup.sh
```
Desde el Mac: `ssh -L 8787:127.0.0.1:8787 root@IP -p PUERTO` y abre <http://127.0.0.1:8787>.

## Uso
- **Agente / Chat**: en Agente el modelo usa herramientas; en Chat solo conversa.
- `!comando` ejecuta en el pod directamente (la salida se envía al modelo si la casilla está marcada). `/leer URL` trae una página.
- Comandos destructivos (`rm -r`, `git push --force`, `curl | sh`…) piden aprobación en la interfaz.
- «Subir a GitHub al terminar» hace commit + push automático tras cada tarea. Token: botón 🔑 (se guarda en `~/.pod-panel/github-token`, nunca en el repo) o `GITHUB_TOKEN`.
- Variables: `PANEL_PORT`, `PANEL_MODEL`, `PANEL_REPO`, `PANEL_WORKDIR`, `PANEL_BRANCH`, `POD_HOURLY_USD`, `POD_LIMIT_H`, `PANEL_NUM_CTX`, `PANEL_MAX_STEPS`.

Solo usa la biblioteca estándar de Python 3.
