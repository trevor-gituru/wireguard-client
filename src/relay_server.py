# src/relay_server.py
import time
import requests
from src.config import settings
from src.logger import logger  # assumes you have src/logger.py with a configured logger

class RelayServerClient:
    def __init__(self):
        self.base_url = f"http://{settings.RELAY_IP}:{settings.RELAY_PORT}"

    def register_device(self, serial: str, public_key: str) -> dict | None:
        """
        Send registration request to the relay server.
        """
        try:
            resp = requests.post(
                f"{self.base_url}/devices/register",
                json={"serial": serial, "public_key": public_key},
                timeout=5
            )
            resp.raise_for_status()
            device = resp.json()
            logger.info("Device registered sucessfully: %s", device)
            return device
        except requests.exceptions.RequestException as e:
            logger.error("Register device failed: %s", e)
            return None

    def ensure_registered(
        self,
        serial: str,
        public_key: str,
        retries: int = 5,
        delay: int = 5
    ) -> dict | None:
        """
        Try to register the device with retries and delay between attempts.
        """
        for attempt in range(1, retries + 1):
            logger.info("Registering device (attempt %d/%d)", attempt, retries)
            device = self.register_device(serial, public_key)

            if device:
                return device

            logger.warning("Retrying in %ds...", delay)
            time.sleep(delay)

        logger.error("Failed to register device after %d retries", retries)
        return None

    def reachable(self, timeout: int = 3) -> bool:
        """
        Check if the relay VPN endpoint is reachable.
        """
        try:
            r = requests.get(
                f"http://10.10.0.1:{settings.RELAY_PORT}/health",
                timeout=timeout
            )
            if r.status_code == 200:
                logger.debug("Relay reachable")
                return True
            logger.warning("Relay returned status code %d", r.status_code)
            return False
        except requests.RequestException as e:
            logger.warning("Relay not reachable: %s", e)
            return False


# Create a singleton client instance
relay = RelayServerClient()

