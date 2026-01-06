# WireGuard Client Monitor

This project provides a Python-based client monitor for a WireGuard VPN setup. It automatically ensures the WireGuard interface is in the desired state, monitors connectivity to a relay server, and can restart the VPN interface if handshakes are stale or the relay is unreachable.

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup](#setup)
- [Running the Client Manually](#running-the-client-manually)
- [Using systemd Service & Timer](#using-systemd-service--timer)
- [Docker](#docker)
- [Logging](#logging)
- [Utilities](#utilities)
- [Notes](#notes)

## Project Structure

```
wireguard-client/
├── .dockerignore       # Files to ignore in Docker builds
├── docker-compose.yml  # Docker Compose for local development
├── Dockerfile          # Dockerfile for containerization
├── entrypoint.sh       # Entrypoint script for Docker container
├── README.md
├── service-setup.sh    # Script to setup systemd service & timer
├── wireguard-setup.sh  # Optional script to setup WireGuard keys & interface
├── venv/                 # Python virtual environment
└── src/
    ├── config.py         # Configuration values
    ├── logger.py         # Logger setup
    ├── main.py           # Entry point
    ├── relay_server.py   # Relay server API client
    ├── storage.py        # Device info storage utility
    ├── utils.py          # Utility functions (serial number, architecture, internet check)
    └── wireguard_client.py # WireGuard client class
```

## Requirements

-   Ubuntu / Debian-based system
-   Python 3.12+
-   WireGuard installed (`wg`, `wg-quick`)
-   `systemd` (for service and timer)
-   Python packages: `requests`

## Setup

1.  **Clone repository**
    ```bash
    git clone <your-repo-url>
    cd wireguard-client
    ```

2.  **Create Python virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **WireGuard Keys & Configuration**

    Ensure your client private key exists at `/etc/wireguard/client_private.key`.

    If using `wireguard-setup.sh`, run:
    ```bash
    sudo bash wireguard-setup.sh
    ```
    This will generate keys and a basic configuration for `wg0-client`.

## Running the Client Manually

Activate the virtual environment and run:
```bash
source venv/bin/activate
python3 -m src.main
```

The client will:
-   Ensure the device is registered with the relay server.
-   Check WireGuard configuration and runtime state.
-   Monitor connectivity to the relay server.
-   Restart the interface if the handshake is stale or the relay is unreachable.

## Using systemd Service & Timer

We provide `service-setup.sh` to install a systemd service and timer to run the client periodically.

### Setup service & timer
```bash
sudo bash service-setup.sh
```

This will:
-   Create `/etc/systemd/system/wg-client.service`
-   Create `/etc/systemd/system/wg-client.timer`
-   Enable and start the timer
-   Optionally start the service immediately once

### Check status

-   **Timer:**
    ```bash
    systemctl status wg-client.timer
    ```
-   **Service logs:**
    ```bash
    journalctl -u wg-client.service -f
    ```

### Adjust timer frequency

Edit `/etc/systemd/system/wg-client.timer`:
```ini
[Timer]
OnBootSec=10s
OnUnitActiveSec=30s
Unit=wg-client.service
Persistent=true
```

-   `OnBootSec` → time after boot for the first run
-   `OnUnitActiveSec` → interval between runs

Reload and restart the timer after edits:
```bash
sudo systemctl daemon-reload
sudo systemctl restart wg-client.timer
```

## Docker

The application can be run inside a Docker container. The provided Docker files are for this purpose.

### Setup

1.  **Pull the Docker image:**
    ```bash
    balena pull gituru/wireguard-client:latest
    ```

2.  **Run the container:**
    ```bash
    # balena run -d \
      --name wireguard-client \
      --privileged \
      --network host \
      -e RELAY_IP=159.69.39.107 \
      -e RELAY_PORT=8000 \
      -v wg-data:/app/data \
      gituru/wireguard-client:latest
    ```

3.  **Check logs:**
    ```bash
    # balena logs wireguard-client
    ```

## Logging

-   Logging is configured via `src/logger.py`.
-   Logs include:
    -   Device registration
    -   WireGuard reconciliation
    -   VPN and internet connectivity checks
    -   Handshake age for peers
-   When running as a systemd service, logs are accessible via:
    ```bash
    journalctl -u wg-client.service -f
    ```

## Utilities

-   `utils.py` includes:
    -   `get_serial_number()` → detects system serial number
    -   `get_architecture()` → detects architecture (x86_64 or aarch64)
    -   `internet_reachable()` → pings an external host to confirm internet connectivity
-   `storage.py` handles storing/loading `device.json`
-   `relay_server.py` communicates with the relay server REST API
-   `wireguard_client.py` contains the `WireGuardClient` class for:
    -   Saving/rewriting config
    -   Restarting the interface
    -   Adding/removing peers
    -   Checking handshake age
    -   Ensuring the state is consistent

## Notes

-   Systemd runs the Python client in the virtual environment automatically.
-   Ensure `/etc/wireguard/client_private.key` exists and is readable by the service user (root).
-   Recommended handshake max age: 120s
-   Adjust the timer interval in the `.timer` file according to how frequently you want the client to check VPN health.
