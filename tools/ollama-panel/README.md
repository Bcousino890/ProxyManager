# Panel del Pod

Chat **agéntico** con Ollama que corre dentro del pod de Runpod. El modelo ejecuta herramientas reales
(`bash`, `read_file`, `write_file`, `list_dir`, `web_search`, `web_fetch`), lee los resultados y sigue hasta terminar; al final guarda
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
- **Archivos y fotos**: botón 📎, arrastrar y soltar o pegar capturas (Ctrl/Cmd+V). Se guardan en `pod-work/uploads/` (excluida de git: no se sube a GitHub). Las imágenes las interpreta `qwen2.5vl:7b`. «Razonar» usa `qwen3:30b` (piensa paso a paso) (descripción + texto transcrito); los archivos de texto se leen directamente.
- **Modos**: Agente (programar con pruebas), Investigar (varias fuentes + informe con citas en `pod-work/investigaciones/`) y Chat (sin herramientas).
- **Internet**: `web_fetch` lee cualquier URL. Los buscadores web (Google, Bing, DuckDuckGo, Brave) bloquean las IP de los pods, así que `web_search` usa las APIs abiertas de GitHub, Wikipedia, Stack Overflow y Hacker News. Para búsqueda web completa define `TAVILY_API_KEY` (plan gratuito en tavily.com) antes de arrancar.
- Variables: `PANEL_PORT`, `PANEL_MODEL`, `PANEL_REPO`, `PANEL_WORKDIR`, `PANEL_BRANCH`, `POD_HOURLY_USD`, `POD_LIMIT_H`, `PANEL_NUM_CTX`, `PANEL_MAX_STEPS`.

Solo usa la biblioteca estándar de Python 3.
