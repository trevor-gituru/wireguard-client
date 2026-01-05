import logging
import sys
from pathlib import Path

# Setup logger
log_path = Path("/var/log/wireguard-client.log")
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=log_path,
    filemode='a',
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
)

logger = logging.getLogger("wg-client")
logger.setLevel(logging.DEBUG)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


# Example usage
# logger.info("WireGuard client started")
# logger.debug("Checking VPN state for peer %s", device["relay_public_key"])
# logger.warning("VPN not reachable")
# logger.error("Failed to register device")

