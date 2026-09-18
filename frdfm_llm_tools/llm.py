import os
from pathlib import Path


class LLM:
    def __init__(
            self,
            provider: str = "ollama",
            provider_base_url: str = None,
            provider_api_key_path: str = None,
            model: str = None):
        self.provider = self._resolve_provider(provider)
        self.base_url = self._resolve_base_url(provider_base_url)
        self.api_key = self._resolve_api_key(provider_api_key_path)
        self.model = model or self._get_default_model()

    def _resolve_provider(self, provider: str) -> str:
        """Normalizes provider name. Unknown providers default to 'custom'."""
        known_providers = {
            "openai",
            "anthropic",
            "ollama",
            "lmstudio",
            "llamacpp",
            "openrouter",
            "deepinfra",
            "groq"
        }
        norm = provider.lower().strip()
        return norm if norm in known_providers else "custom"

    def _resolve_base_url(self, base_url: str = None) -> str:
        """Resolves base URL from input or falls back to provider defaults."""
        if base_url:
            return base_url

        defaults = {
            "ollama": "http://localhost:11434",
            "lmstudio": "http://localhost:1234/v1",
            "llamacpp": "http://127.0.0.1:8080/v1",
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
            "openrouter": "https://openrouter.ai/api/v1",
            "deepinfra": "https://api.deepinfra.com/v1/openai",
            "groq": "https://api.groq.com/openai/v1",
            "custom": ""
        }
        return defaults.get(self.provider, "")

    def _resolve_api_key(self, key_path: str = None) -> str:
        """Resolves API key from path, environment variables, or a local <provider>.api_key file."""
        # 1. Check explicitly passed key path
        if key_path:
            path = Path(key_path)
            if path.exists():
                return path.read_text().strip()

        # 2. Check environment variables
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "ollama": "OLLAMA_API_KEY",
            "lmstudio": "LMSTUDIO_API_KEY",
            "llamacpp": "LLAMACPP_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "deepinfra": "DEEPINFRA_API_KEY",
            "groq": "GROQ_API_KEY",
            "custom": "CUSTOM_API_KEY"
        }
        env_key = env_var_map.get(self.provider, "LLM_API_KEY")
        env_val = os.getenv(env_key)
        if env_val:
            return env_val

        # 3. Check local directory for a file named <provider>.api_key
        local_key_file = Path(f"{self.provider}.api_key")
        if local_key_file.exists():
            return local_key_file.read_text().strip()

        # 4. Fallback defaults
        default_val = "lm-studio" if self.provider == "lmstudio" else "api_key"
        return default_val

    def _get_default_model(self) -> str:
        """Provides a sensible default model based on the active provider."""
        defaults = {
            "ollama": "llama3",
            "lmstudio": "local-model",
            "llamacpp": "default",
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "openrouter": "openai/gpt-4o",
            "deepinfra": "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "groq": "llama-3.3-70b-versatile",
            "custom": "default"
        }
        return defaults.get(self.provider, "default")

    def __call__(self, prompt: str, system: str = "") -> str:
        """Allows calling the instance directly: llm("Hello!")"""
        return self.generate(prompt, system=system)

    def generate(
            self,
            prompt: str,
            model: str = None,
            system: str = "") -> str:
        """Standardized string generation."""
        active_model = model or self.model
        return f"Hi! Using provider '{self.provider}' (Base URL: {self.base_url or 'default'}) with model '{active_model}'. Not fully initialized yet!"

    def generate_structured(self, prompt: str, response_model):
        """Standardized structured output generation."""
        raise NotImplementedError