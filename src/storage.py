from pathlib import Path
import json
import os

class DeviceStorage:
    REQUIRED_FIELDS = ["serial", "assigned_ip", "relay_public_key"]

    def __init__(self, path="/etc/wireguard/device.json"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {}

    def is_empty(self):
        """Returns True if JSON missing or any required field is missing"""
        data = self.load()
        return not all(field in data and data[field] for field in self.REQUIRED_FIELDS)

    def create(self, data):
        """Create JSON file if missing or empty"""
        if not os.path.exists(self.path):
            self.save(data)
            os.chmod(self.path, 0o600)  # secure file permissions

    def save(self, data):
        """Save or update JSON file"""
        existing = self.load()
        existing.update(data)
        with open(self.path, "w") as f:
            json.dump(existing, f, indent=2)

DEVICE_FILE = Path(__file__).parent.parent / "device.json"
device_storage = DeviceStorage(DEVICE_FILE)

