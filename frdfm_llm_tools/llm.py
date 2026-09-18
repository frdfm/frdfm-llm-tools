import os
from pathlib import Path


class LLM:
    def __init__(
            self,
            provider: str = "ollama",
            provider_base_url: str = None,
            provider_api_key_path: str = None,
            model: str = None):
        self.provider = provider
        self.model = model
        self.base_url = provider_base_url
        self.api_key = self._resolve_api_key(provider_api_key_path)

    def _resolve_api_key(self, key_path: str = None) -> str:
        """Resolves API key from a provided file path or falls back to environment variables."""
        if key_path:
            path = Path(key_path)
            if path.exists():
                return path.read_text().strip()

        # Fallback environment variable based on provider name
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "ollama": "OLLAMA_API_KEY"
        }
        env_key = env_var_map.get(self.provider.lower(), "LLM_API_KEY")
        return os.getenv(env_key, "api_key")

    def __call__(self, prompt: str, system: str = "") -> str:
        """Allows calling the instance directly: llm("Hello!")"""
        return self.generate(prompt, system=system)

    def generate(
            self,
            prompt: str,
            model: str = None,
            system: str = "") -> str:
        """Standardized string generation."""
        return "Hi! I am not initialized yet!!!"

    def generate_structured(self, prompt: str, response_model):
        """Standardized structured output generation."""
        raise NotImplementedError
