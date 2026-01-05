# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Client config
    CLIENT_PUBLIC_KEY: str | None = os.getenv("CLIENT_PUBLIC_KEY")
    RELAY_IP: str = os.getenv("RELAY_IP")
    RELAY_PORT: str = os.getenv("RELAY_PORT")
    
    @classmethod
    def validate(cls):
        if not cls.CLIENT_PUBLIC_KEY:
            raise ValueError("CLIENT_PUBLIC_KEY is not set")
        if not cls.RELAY_IP:
            raise ValueError("RELAY_IP is not set")

settings = Settings()

