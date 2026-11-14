#!/usr/bin/env bash
# Deja un pod/VPS NUEVO listo en un solo comando (idempotente: se puede repetir sin romper nada).
#   curl -fsSL https://raw.githubusercontent.com/Bcousino890/ProxyManager/main/tools/ollama-panel/deploy/bootstrap.sh | bash
#   o, con el repo ya clonado:  bash tools/ollama-panel/deploy/bootstrap.sh
# Variables: REPO_URL, BRANCH (por defecto main), REPO_DIR (/ProxyManager), GITHUB_TOKEN (opcional), SKIP_SMOKE=1
set -euo pipefail
REPO_URL="${REPO_URL:-https://github.com/Bcousino890/ProxyManager.git}"; BRANCH="${BRANCH:-main}"; REPO_DIR="${REPO_DIR:-/ProxyManager}"
say() { printf '\n\033[1m→ %s\033[0m\n' "$*"; }
# 1) Modelos en el volumen persistente si existe (sobreviven a recrear el pod)
if [ -d /workspace ]; then export OLLAMA_MODELS="${OLLAMA_MODELS:-/workspace/ollama}"; mkdir -p "$OLLAMA_MODELS"; say "Modelos en $OLLAMA_MODELS (persistente)"; fi
# 2) Herramientas base
say "Paquetes base"; (command -v git >/dev/null && command -v python3 >/dev/null && command -v curl >/dev/null) || { apt-get update -qq && apt-get install -y -qq git python3 python3-venv curl ca-certificates; }
git config --global --add safe.directory '*' 2>/dev/null || true
# 3) Repositorio (nunca force: si ya existe solo avanza si es fast-forward)
if [ -d "$REPO_DIR/.git" ]; then say "Repo existente: actualizando $BRANCH (ff-only)"; git -C "$REPO_DIR" fetch -q origin "$BRANCH" && { git -C "$REPO_DIR" checkout -q "$BRANCH" 2>/dev/null || git -C "$REPO_DIR" checkout -q -b "$BRANCH" "origin/$BRANCH"; git -C "$REPO_DIR" merge --ff-only -q "origin/$BRANCH" || echo "  (no es ff: se deja como está)"; }
else say "Clonando $REPO_URL ($BRANCH)"; git clone -q -b "$BRANCH" "$REPO_URL" "$REPO_DIR"; fi
# 4) Token de GitHub (opcional aquí; también se puede poner con el botón 🔑)
if [ -n "${GITHUB_TOKEN:-}" ]; then mkdir -p ~/.pod-panel; printf '%s' "$GITHUB_TOKEN" > ~/.pod-panel/github-token; chmod 600 ~/.pod-panel/github-token; say "Token guardado (permisos 600)"; fi
# 5) Ollama + modelos + panel (reutiliza setup.sh) con la rama de guardado correcta
say "Ollama, modelos y panel"; export PANEL_BRANCH="$BRANCH"; bash "$REPO_DIR/tools/ollama-panel/setup.sh"
# 6) Entorno de pruebas del panel (pytest en un venv aparte)
[ -x /root/.panel-test-venv/bin/python ] || { python3 -m venv /root/.panel-test-venv && /root/.panel-test-venv/bin/pip -q install pytest; }
# 7) Verificación real
if [ "${SKIP_SMOKE:-0}" != "1" ]; then say "Prueba de humo"; python3 "$REPO_DIR/tools/ollama-panel/deploy/smoke_test.py" || { echo "✖ La prueba de humo falló: mira el panel → Despliegue"; exit 1; }; fi
say "LISTO"
echo "  Panel:   http://127.0.0.1:${PANEL_PORT:-8787}   (desde tu Mac: ssh -L 8788:127.0.0.1:8787 root@IP -p PUERTO)"
echo "  Siguiente: panel → Despliegue → escribe POD_ID y el puerto HTTP expuesto → Comprobar."
echo "  URL pública (RunPod): https://<POD_ID>-<PUERTO>.proxy.runpod.net"
