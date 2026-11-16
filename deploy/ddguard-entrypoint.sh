#!/usr/bin/env bash
# Arranca la pantalla virtual (Xvfb) y, solo si DDGUARD_HEADLESS=false, el puente noVNC para que
# una persona pueda ver el navegador y resolver un CAPTCHA deslizante a mano. Luego arranca la API.
# No expone nada a Internet por sí mismo: el puerto 6080 solo se publica si tú lo publicas en
# docker-compose, y se recomienda hacerlo solo en localhost + túnel SSH (ver deploy/README.md).
set -euo pipefail

Xvfb :99 -screen 0 1366x900x24 -nolisten tcp &
XVFB_PID=$!
trap 'kill $XVFB_PID 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  xdpyinfo -display :99 >/dev/null 2>&1 && break
  sleep 0.3
done

if [ "${DDGUARD_HEADLESS:-true}" = "false" ]; then
  if [ -n "${DDGUARD_VNC_PASSWORD:-}" ]; then
    mkdir -p "$HOME/.vnc"
    x11vnc -storepasswd "$DDGUARD_VNC_PASSWORD" "$HOME/.vnc/passwd"
    x11vnc -display :99 -forever -shared -rfbauth "$HOME/.vnc/passwd" -rfbport 5900 -nolookup -quiet &
  else
    echo "AVISO: DDGUARD_VNC_PASSWORD vacío; noVNC sin contraseña. Publica el puerto 6080 SOLO en localhost (ver deploy/README.md)." >&2
    x11vnc -display :99 -forever -shared -nopw -rfbport 5900 -nolookup -quiet &
  fi
  websockify --web /usr/share/novnc 6080 localhost:5900 &
fi

exec "$@"
