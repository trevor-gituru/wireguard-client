#!/bin/bash
set -e

# -----------------------------
# Get current directory and venv path
# -----------------------------
WORKDIR="$(pwd)"
VENV_PYTHON="$WORKDIR/venv/bin/python3"
SERVICE_NAME="wg-client"

SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
TIMER_PATH="/etc/systemd/system/${SERVICE_NAME}.timer"

# -----------------------------
# Create systemd service file
# -----------------------------
echo "[+] Creating systemd service at $SERVICE_PATH"

sudo tee $SERVICE_PATH > /dev/null <<EOF
[Unit]
Description=WireGuard Client Monitor
After=network.target wg-quick@wg0-client.service
Wants=wg-quick@wg0-client.service

[Service]
Type=simple
User=root
WorkingDirectory=${WORKDIR}
ExecStart=${VENV_PYTHON} -m src.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# -----------------------------
# Create systemd timer file
# -----------------------------
echo "[+] Creating systemd timer at $TIMER_PATH"

sudo tee $TIMER_PATH > /dev/null <<EOF
[Unit]
Description=Run WireGuard Client Monitor every 10 seconds

[Timer]
OnBootSec=20s
OnUnitActiveSec=30s
Unit=${SERVICE_NAME}.service
Persistent=true

[Install]
WantedBy=timers.target
EOF

# -----------------------------
# Reload, enable, and start
# -----------------------------
SERVICE_NAME="wg-client"
TIMER_NAME="wg-client.timer"

sudo systemctl daemon-reload
sudo systemctl enable $TIMER_NAME
sudo systemctl start $TIMER_NAME

# Optional: start service immediately once
sudo systemctl start ${SERVICE_NAME}.service

echo "[+] WireGuard client service and timer setup complete!"
echo "[+] You can check status with: systemctl status $TIMER_NAME"



