#!/usr/bin/env bash
# Deja un pod nuevo listo: Ollama + modelo + Panel. Uso:  bash tools/ollama-panel/setup.sh
set -e
MODEL="${PANEL_MODEL:-qwen2.5-coder:14b}"
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v ollama >/dev/null || { echo "→ Instalando Ollama"; curl -fsSL https://ollama.com/install.sh | sh; }
if ! curl -fs localhost:11434/api/tags >/dev/null; then
  echo "→ Arrancando Ollama"; OLLAMA_KEEP_ALIVE=2h setsid nohup ollama serve >/tmp/ollama.log 2>&1 < /dev/null &
  for i in $(seq 30); do curl -fs localhost:11434/api/tags >/dev/null && break; sleep 1; done
fi
ollama list | grep -q "${MODEL%%:*}" || { echo "→ Descargando $MODEL"; ollama pull "$MODEL"; }
git config --global --add safe.directory '*' 2>/dev/null || true
fuser -k "${PANEL_PORT:-8787}/tcp" 2>/dev/null || true
cd "$HERE" && setsid nohup python3 server.py >/tmp/panel.log 2>&1 < /dev/null &
sleep 2
echo "✔ Panel en http://127.0.0.1:${PANEL_PORT:-8787}"
echo "  Desde tu Mac:  ssh -L 8787:127.0.0.1:8787 root@<IP-del-pod> -p <puerto>   y abre http://127.0.0.1:8787"
echo "  Token de GitHub (para subir): botón 🔑 del panel, o  export GITHUB_TOKEN=..."
