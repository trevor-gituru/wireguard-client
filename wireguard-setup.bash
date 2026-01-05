#!/usr/bin/env bash
set -euo pipefail

WG_DIR="/etc/wireguard"
WG_INTERFACE="wg0-client"
WG_CONF="${WG_DIR}/${WG_INTERFACE}.conf"
PRIVATE_KEY_FILE="${WG_DIR}/client_private.key"
PUBLIC_KEY_FILE="${WG_DIR}/client_public.key"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

echo "[+] Starting WireGuard client setup..."

# Ensure script is run as root
if [[ "$EUID" -ne 0 ]]; then
  echo "[-] Please run as root"
  exit 1
fi

echo "[+] Installing WireGuard..."
apt update -y
apt install -y wireguard

echo "[+] Preparing WireGuard directory..."
mkdir -p "${WG_DIR}"
chmod 700 "${WG_DIR}"

# Generate keys only if missing
if [[ ! -f "${PRIVATE_KEY_FILE}" ]]; then
  echo "[+] Generating WireGuard keys..."
  wg genkey | tee "${PRIVATE_KEY_FILE}" | wg pubkey > "${PUBLIC_KEY_FILE}"
  chmod 600 "${PRIVATE_KEY_FILE}" "${PUBLIC_KEY_FILE}"
else
  echo "[+] WireGuard keys already exist"
fi

PRIVATE_KEY="$(cat "${PRIVATE_KEY_FILE}")"
PUBLIC_KEY="$(cat "${PUBLIC_KEY_FILE}")"

# Create config only if missing
if [[ ! -f "${WG_CONF}" ]]; then
  echo "[+] Creating WireGuard interface config..."

  cat <<'EOF' > "${WG_CONF}"
[Interface]
PrivateKey = __PRIVATE_KEY__
Address = 10.10.0.2/24
EOF

  # Inject private key safely
  sed -i "s|__PRIVATE_KEY__|${PRIVATE_KEY}|" "${WG_CONF}"

  chmod 600 "${WG_CONF}"
else
  echo "[+] WireGuard config already exists"
fi

echo "[+] Ensuring CLIENT_PUBLIC_KEY is set in ${ENV_FILE}..."

# Create .env if missing
if [[ ! -f "${ENV_FILE}" ]]; then
  touch "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"
fi

# Public key handling
if grep -q "^CLIENT_PUBLIC_KEY=" "${ENV_FILE}"; then
  CURRENT_KEY="$(grep "^CLIENT_PUBLIC_KEY=" "${ENV_FILE}" | cut -d= -f2-)"
  if [[ "${CURRENT_KEY}" != "${PUBLIC_KEY}" ]]; then
    echo "[+] Updating CLIENT_PUBLIC_KEY"
    sed -i "s|^CLIENT_PUBLIC_KEY=.*|CLIENT_PUBLIC_KEY=${PUBLIC_KEY}|" "${ENV_FILE}"
  else
    echo "[+] CLIENT_PUBLIC_KEY already up to date"
  fi
else
  echo "CLIENT_PUBLIC_KEY=${PUBLIC_KEY}" >> "${ENV_FILE}"
fi

echo "[+] WireGuard client setup complete"

