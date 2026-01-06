#!/bin/bash
set -e

INTERVAL=30  # seconds

# --- Setup WireGuard if config doesn't exist ---
WG_CONF="/etc/wireguard/wg0-client.conf"

if [ ! -f "$WG_CONF" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')]  WireGuard config not found. Running setup..."
    ./wireguard-setup.sh
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')]  WireGuard config exists. Skipping setup."
fi

# --- Start main loop ---
echo "[$(date '+%Y-%m-%d %H:%M:%S')]  Starting wg-client loop..."
while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')]  Running wg-client check..."
    python3 -m src.main || echo "[!] wg-client failed"
    sleep $INTERVAL
done

