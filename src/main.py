from src.storage import device_storage
from src.config import settings
from src.utils import get_serial_number, internet_reachable
from src.wireguard_client import wg_client
from src.relay_server import relay
from src.logger import logger
import time

def main():
    # 1. Ensure device is registered
    serial = get_serial_number()
    if device_storage.is_empty():
        device = relay.ensure_registered(
            serial=serial,
            public_key=settings.CLIENT_PUBLIC_KEY
        )
        if not device:
            logger.error("Device registration failed permanently, exiting")
            return

        device["serial"] = serial
        device_storage.save(device)
    else:
        device = device_storage.load()
        logger.info("Device already registered: %s", device)

    # 2. Ensure WireGuard state
    logger.debug("Reconciling WireGuard state")
    wg_client.ensure_state(device)
    time.sleep(5)
    # 3. Runtime connectivity checks
    if not internet_reachable():
        logger.warning("No internet, skipping VPN check")
    elif not relay.reachable(timeout=5):
        logger.warning("VPN not reachable, checking handshake")
        if not wg_client.handshake_healthy(device["relay_public_key"]):
            logger.info("Handshake stale, restarting WireGuard")
            wg_client.restart()
    else:
        logger.info("VPN reachable, no action needed")



if __name__ == "__main__":
    main()











