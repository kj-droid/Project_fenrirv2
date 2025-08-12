# fenrir/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Loads and provides configuration settings for the application."""
    def __init__(self):
        self.VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
        self.ALIENVAULT_OTX_API_KEY = os.getenv("ALIENVAULT_OTX_API_KEY")
        self.NVD_API_KEY = os.getenv("NVD_API_KEY")
        self.APP_NAME = "Fenrir Security Scanner"
        self.APP_VERSION = "0.1.0"

config = Config()
