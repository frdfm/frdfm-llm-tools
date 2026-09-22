import json
import os
import urllib.request
from pathlib import Path


def load_env_file(path: str) -> None:
    if not path:
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(path)
        return
    except Exception:
        pass

    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding='utf-8', errors='replace').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip(chr(34)).strip(chr(39))
        if key and key not in os.environ:
            os.environ[key] = value


class LLM:
    KNOWN_PROVIDERS = {
        'openai',
        'anthropic',
        'ollama',
        'lmstudio',
        'llamacpp',
        'openrouter',
        'deepinfra',
        'groq',
    }

    BASE_URLS = {
        'ollama': 'http://localhost:11434/v1',
        'lmstudio': 'http://localhost:1234/v1',
        'llamacpp': 'http://127.0.0.1:8080/v1',
        'openai': 'https://api.openai.com/v1',
        'anthropic': 'https://api.anthropic.com/v1',
        'openrouter': 'https://openrouter.ai/api/v1',
        'deepinfra': 'https://api.deepinfra.com/v1/openai',
        'groq': 'https://api.groq.com/openai/v1',
    }

    API_KEY_ENVS = {
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'ollama': 'OLLAMA_API_KEY',
        'lmstudio': 'LMSTUDIO_API_KEY',
        'llamacpp': 'LLAMACPP_API_KEY',
        'openrouter': 'OPENROUTER_API_KEY',
        'deepinfra': 'DEEPINFRA_API_KEY',
        'groq': 'GROQ_API_KEY',
    }

    DEFAULT_MODELS = {
        'ollama': 'llama3',
        'lmstudio': 'local-model',
        'llamacpp': 'default',
        'openai': 'gpt-4o',
        'anthropic': 'claude-3-5-sonnet-20241022',
        'openrouter': 'openai/gpt-4o',
        'deepinfra': 'meta-llama/Meta-Llama-3.1-70B-Instruct',
        'groq': 'llama-3.3-70b-versatile',
    }

    def __init__(
            self,
            provider: str = None,
            provider_base_url: str = None,
            provider_api_key_path: str = None,
            model: str = None,
            env_path: str = None):
        load_env_file(env_path)
        self.provider = self._resolve_provider(provider)
        self.base_url = self._resolve_base_url(provider_base_url)
        self.api_key = self._resolve_api_key(provider_api_key_path)
        self.model = self._resolve_model(model)

    def _resolve_provider(self, provider: str = None) -> str:
        provider = provider or os.getenv('LLM_PROVIDER') or os.getenv('OPENAI_PROVIDER')
        if not provider:
            return 'custom'
        norm = provider.lower().strip()
        return norm if norm in self.KNOWN_PROVIDERS else 'custom'

    def _resolve_base_url(self, base_url: str = None) -> str:
        base_url = base_url or os.getenv('OPENAI_BASE_URL') or os.getenv('LLM_BASE_URL')
        if base_url:
            return base_url.rstrip('/')
        return self.BASE_URLS.get(self.provider, '').rstrip('/')

    def _resolve_api_key(self, key_path: str = None) -> str:
        if key_path:
            path = Path(key_path)
            if path.exists():
                return path.read_text().strip()

        env_key = self.API_KEY_ENVS.get(self.provider)
        if env_key:
            env_val = os.getenv(env_key)
            if env_val:
                return env_val

        env_val = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY')
        if env_val:
            return env_val

        local_key_file = Path(self.provider + '.api_key')
        if local_key_file.exists():
            return local_key_file.read_text().strip()

        return 'lm-studio' if self.provider == 'lmstudio' else ''

    def _resolve_model(self, model: str = None) -> str:
        model = model or os.getenv('OPENAI_MODEL') or os.getenv('LLM_MODEL')
        if model:
            return model
        return self.DEFAULT_MODELS.get(self.provider, '')

    def __call__(self, prompt: str, system: str = '') -> str:
        return self.generate(prompt, system=system)

    def generate(self, prompt: str, model: str = None, system: str = '') -> str:
        active_model = model or self.model
        if not active_model:
            raise RuntimeError('model is not set')

        if self.provider == 'anthropic':
            return self._generate_anthropic(prompt, active_model, system)

        return self._generate_openai_compatible(prompt, active_model, system)

    def _generate_openai_compatible(self, prompt: str, model: str, system: str) -> str:
        if not self.base_url:
            raise RuntimeError('base_url is not set')

        url = self.base_url + '/chat/completions'
        messages = []
        if system:
            messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': prompt})

        payload = {'model': model, 'messages': messages}
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = 'Bearer ' + self.api_key

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST',
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['choices'][0]['message']['content']
        except Exception as e:
            raise RuntimeError('OpenAI-compatible request failed for provider ' + self.provider + ': ' + str(e))

    def _generate_anthropic(self, prompt: str, model: str, system: str) -> str:
        if not self.base_url:
            raise RuntimeError('base_url is not set')

        url = self.base_url + '/messages'
        payload = {
            'model': model,
            'max_tokens': 4096,
            'messages': [{'role': 'user', 'content': prompt}],
        }
        if system:
            payload['system'] = system

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST',
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['content'][0]['text']
        except Exception as e:
            raise RuntimeError('Anthropic request failed: ' + str(e))

    def generate_structured(self, prompt: str, response_model):
        raise NotImplementedError