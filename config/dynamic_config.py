
# config/dynamic_config.py
import os
import secrets
from typing import Dict

class DynamicConfig:
    def __init__(self):
        self.api_keys: Dict[str, str] = {}
        
    def generate_api_key(self, provider: str) -> str:
        """Generate a random API key for a provider"""
        key = f"{provider}-{secrets.token_urlsafe(16)}"
        self.api_keys[provider] = key
        return key

    def setup_environment(self):
        """Set dynamic values in environment variables"""
        # Generate provider API keys
        os.environ["OPENAI_API_KEY"] = self.generate_api_key("openai")
        os.environ["ANTHROPIC_API_KEY"] = self.generate_api_key("anthropic")
        
        # Generate proxy access token
        os.environ["PROXY_ACCESS_TOKEN"] = secrets.token_urlsafe(32)

dynamic_config = DynamicConfig()
