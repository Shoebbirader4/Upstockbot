import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv
import os

class ConfigLoader:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._load_secrets()
    
    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_secrets(self):
        secrets_path = Path("config/secrets.env")
        if secrets_path.exists():
            load_dotenv(secrets_path)
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def get_secret(self, key: str, default: str = None) -> str:
        return os.getenv(key, default)

config = ConfigLoader()
