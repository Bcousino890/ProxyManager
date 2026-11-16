#!/usr/bin/env bash
# Visible browser on a headless VPS, reachable from your own browser, to solve a slider CAPTCHA
# by hand when ddguard asks for it. Free (no subscriptions). Ubuntu/Debian.
#   1) sudo bash deploy/novnc-setup.sh
#   2) Run your scraper with DISPLAY=:99 and BrowserSolver(headless=False)
#   3) Open http://YOUR_VPS_IP:6080/vnc.html (password from step 1) when the alert arrives.
set -euo pipefail
apt-get update -y
apt-get install -y xvfb x11vnc novnc websockify fluxbox
read -rsp "VNC password: " PW; echo
mkdir -p /etc/x11vnc && x11vnc -storepasswd "$PW" /etc/x11vnc/passwd
cat >/etc/systemd/system/xvfb.service <<UNIT
[Unit]
Description=Virtual display :99
[Service]
ExecStart=/usr/bin/Xvfb :99 -screen 0 1366x900x24
Restart=always
[Install]
WantedBy=multi-user.target
UNIT
cat >/etc/systemd/system/x11vnc.service <<UNIT
[Unit]
Description=VNC for :99
After=xvfb.service
[Service]
ExecStart=/usr/bin/x11vnc -display :99 -forever -shared -rfbauth /etc/x11vnc/passwd -localhost
Restart=always
[Install]
WantedBy=multi-user.target
UNIT
cat >/etc/systemd/system/novnc.service <<UNIT
[Unit]
Description=noVNC web client on :6080
After=x11vnc.service
[Service]
ExecStart=/usr/bin/websockify --web /usr/share/novnc 6080 localhost:5900
Restart=always
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now xvfb x11vnc novnc
echo "OK. export DISPLAY=:99  ->  open http://<VPS_IP>:6080/vnc.html"
echo "Tip: restrict port 6080 with your firewall (ufw allow from <your IP> to any port 6080)."
