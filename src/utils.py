from src.config import settings
from src.storage import device_storage
import re
import requests
import subprocess

# src/utils.py
import subprocess
import re
from src.logger import logger

def get_architecture() -> str | None:
    """
    Detect system architecture (e.g., x86_64, aarch64).
    """
    try:
        arch = subprocess.check_output(["uname", "-m"], text=True).strip()
        logger.debug("Detected architecture: %s", arch)
        return arch
    except subprocess.CalledProcessError as e:
        logger.error("Failed to get architecture: %s", e)
        return None

def get_serial_number() -> str | None:
    """
    Get device serial number depending on architecture.
    """
    arch = get_architecture()
    if arch is None:
        logger.error("Cannot get serial number: architecture unknown")
        return None

    try:
        if arch == "aarch64":
            # ARM
            cmd = ["lshw", "-C", "system"]
            regex = r"serial:\s*(\w+)"
        elif arch == "x86_64":
            # x86
            cmd = ["dmidecode", "-s", "system-serial-number"]
            regex = r"(.+)"
        else:
            logger.error("Unsupported architecture: %s", arch)
            return None

        output = subprocess.check_output(cmd, text=True)
        match = re.search(regex, output)
        if match:
            serial = match.group(1).strip()
            logger.debug("Detected serial number: %s", serial)
            return serial

        logger.warning("Serial number not found in command output")
        return None

    except FileNotFoundError:
        logger.error("Command not found: %s", cmd[0])
        return None
    except subprocess.CalledProcessError as e:
        logger.error("Command failed: %s", e)
        return None


def internet_reachable(host="8.8.8.8") -> bool:
    try:
        subprocess.run(
            ["ping", "-c", "1", "-W", "1", host],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

