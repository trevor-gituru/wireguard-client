# src/wireguard_client.py
import subprocess
import re
import time
from pathlib import Path
from src.config import settings
from src.logger import logger

class WireGuardClient:
    def __init__(self, interface="wg0-client", conf_path="/etc/wireguard/wg0-client.conf"):
        self.interface = interface
        self.conf_path = Path(conf_path)
        self.conf_path.parent.mkdir(parents=True, exist_ok=True)

    def save_conf(self, data: dict):
        """
        Save a fresh WireGuard config, overwriting any existing content.
        """
        try:
            with open("/etc/wireguard/client_private.key") as f:
                private_key = f.read().strip()
            if len(private_key) != 44:
                raise ValueError("Invalid WireGuard private key length")

            content = f"""
[Interface]
PrivateKey = {private_key}
Address = {data["assigned_ip"]}/32

[Peer]
PublicKey = {data["relay_public_key"]}
AllowedIPs = 10.10.0.0/24
Endpoint = {settings.RELAY_IP}:51820
PersistentKeepalive = 25
""".strip()

            self.conf_path.write_text(content)
            self.conf_path.chmod(0o600)
            logger.info("WireGuard config saved to %s", self.conf_path)
        except Exception as e:
            logger.error("Failed to save WireGuard config: %s", e)

    def add_peer(self, public_key: str):
        """
        Add a peer dynamically to the running WireGuard interface using wg set.
        """
        try:
            if self.peer_exists_runtime(public_key): 
                logger.info("Peer %s already exists", public_key)
                return

            endpoint = f"{settings.RELAY_IP}:51820"
            subprocess.run([
                "wg", "set", self.interface,
                "peer", public_key,
                "allowed-ips", "10.10.0.0/24",
                "endpoint", endpoint
            ], check=True)
            logger.info("Peer %s added to %s", public_key, self.interface)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to add peer %s: %s", public_key, e)

    def restart(self):
        """
        Restart the WireGuard interface using wg-quick down and up.
        """
        try:
            subprocess.run(["wg-quick", "down", self.interface], check=False)
            subprocess.run(["wg-quick", "up", self.interface], check=True)
            logger.info("WireGuard interface %s restarted successfully", self.interface)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to restart WireGuard interface %s: %s", self.interface, e)

    def remove_peer(self, public_key: str):
        """
        Remove a peer block from the WireGuard config file using regex.
        """
        try:
            content = self.conf_path.read_text()
            pattern = rf"\[Peer\](?:\n(?!\[Peer\]).*)*?PublicKey = {re.escape(public_key)}(?:\n(?!\[Peer\]).*)*"
            new_content, count = re.subn(pattern, "", content, flags=re.MULTILINE)

            if count > 0:
                self.conf_path.write_text(new_content.strip() + "\n")
                logger.info("Peer %s removed from config", public_key)
            else:
                logger.warning("Peer %s not found in config", public_key)
        except Exception as e:
            logger.error("Failed to remove peer %s: %s", public_key, e)

    def peer_exists_runtime(self, public_key: str) -> bool:
        try:
            output = subprocess.check_output(["wg", "show"], text=True)
            return public_key in output
        except subprocess.CalledProcessError:
            return False

    def peer_in_conf(self, public_key: str) -> bool:
        if not self.conf_path.exists():
            return False
        return f"PublicKey = {public_key}" in self.conf_path.read_text()

    def ip_match(self, address: str) -> bool:
        if not self.conf_path.exists():
            logger.warning("Config file %s does not exist", self.conf_path)
            return False

        content = self.conf_path.read_text()
        for line in content.splitlines():
            if line.strip().startswith("Address ="):
                current_address = line.split("=", 1)[1].strip()
                return current_address == f"{address}/32"
        return False

    def handshake_healthy(self, peer_pubkey: str, max_age: int = 120) -> bool:
        try:
            output = subprocess.check_output(
                ["wg", "show", self.interface, "latest-handshakes"],
                text=True
            )
        except subprocess.CalledProcessError:
            return False

        now = int(time.time())
        for line in output.strip().splitlines():
            key, ts = line.split()
            ts = int(ts)
            if key != peer_pubkey:
                continue
            if ts == 0:
                return False
            age = now - ts
            logger.debug("Handshake age for %s: %ds", peer_pubkey, age)
            return 0 <= age <= max_age
        return False

    def ensure_state(self, device: dict):
        config_needs_update = False

        if not self.conf_path.exists():
            logger.info("Config missing")
            config_needs_update = True
        elif not self.ip_match(device["assigned_ip"]):
            logger.info("IP mismatch in config")
            config_needs_update = True
        elif not self.peer_in_conf(device["relay_public_key"]):
            logger.info("Peer missing in config")
            config_needs_update = True
        elif not self.peer_exists_runtime(device["relay_public_key"]):
            logger.info("Runtime peer missing")
            config_needs_update = True

        if config_needs_update:
            logger.info("Reconciling WireGuard state")
            self.save_conf(device)
            self.restart()
        else:
            logger.info("WireGuard already in desired state")


wg_client = WireGuardClient()

