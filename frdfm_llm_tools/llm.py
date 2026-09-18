import json
import os
import urllib.request
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
            return base_url.rstrip("/")

        defaults = {
            "ollama": "http://localhost:11434/v1",
            "lmstudio": "http://localhost:1234/v1",
            "llamacpp": "http://127.0.0.1:8080/v1",
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
            "openrouter": "https://openrouter.ai/api/v1",
            "deepinfra": "https://api.deepinfra.com/v1/openai",
            "groq": "https://api.groq.com/openai/v1",
            "custom": ""
        }
        return defaults.get(self.provider, "").rstrip("/")

    def _resolve_api_key(self, key_path: str = None) -> str:
        """Resolves API key from path, environment variables, or a local <provider>.api_key file."""
        if key_path:
            path = Path(key_path)
            if path.exists():
                return path.read_text().strip()

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

        local_key_file = Path(f"{self.provider}.api_key")
        if local_key_file.exists():
            return local_key_file.read_text().strip()

        return "lm-studio" if self.provider == "lmstudio" else ""

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
        """Standardized string generation using built-in urllib."""
        active_model = model or self.model

        if self.provider == "anthropic":
            return self._generate_anthropic(prompt, active_model, system)
        else:
            return self._generate_openai_compatible(prompt, active_model, system)

    def _generate_openai_compatible(self, prompt: str, model: str, system: str) -> str:
        url = f"{self.base_url}/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"OpenAI-compatible request failed for provider '{self.provider}': {e}")

    def _generate_anthropic(self, prompt: str, model: str, system: str) -> str:
        url = f"{self.base_url}/messages"

        payload = {
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            payload["system"] = system

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data["content"][0]["text"]
        except Exception as e:
            raise RuntimeError(f"Anthropic request failed: {e}")

    def generate_structured(self, prompt: str, response_model):
        """Standardized structured output generation."""
        raise NotImplementedError