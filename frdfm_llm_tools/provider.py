BASE_URLS = {
    "ollama": "http://localhost:11434/v1",
    "lmstudio": "http://localhost:1234/v1",
    "llamacpp": "http://127.0.0.1:8080/v1",
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "deepinfra": "https://api.deepinfra.com/v1/openai",
    "groq": "https://api.groq.com/openai/v1",
}

DECISION_BASE_URLS = {
    "openrouter": "https://openrouter.ai/api/alpha",
}

BASE_URL_ENV_VAR_NAMES = {
    "ollama": "OLLAMA_HOST",
    "lmstudio": "LM_STUDIO_BASE_URL",
    "llamacpp": "LLAMACPP_BASE_URL",
    "openai": "OPENAI_BASE_URL",
    "anthropic": "ANTHROPIC_BASE_URL",
    "openrouter": "OPENROUTER_BASE_URL",
    "deepinfra": "DEEPINFRA_BASE_URL",
    "groq": "GROQ_BASE_URL",
}

API_KEY_ENV_VAR_NAMES = {
    "ollama": None,
    "lmstudio": None,
    "llamacpp": None,
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "deepinfra": "DEEPINFRA_API_KEY",
    "groq": "GROQ_API_KEY",
}

MODEL_ENV_VAR_NAMES = {
    "ollama": "OLLAMA_MODEL",
    "lmstudio": "LM_STUDIO_MODEL",
    "llamacpp": "LLAMACPP_MODEL",
    "openai": "OPENAI_MODEL",
    "anthropic": "ANTHROPIC_MODEL",
    "openrouter": "OPENROUTER_MODEL",
    "deepinfra": "DEEPINFRA_MODEL",
    "groq": "GROQ_MODEL",
}

def get_provider_value(provider: str, name: str):
    values = {
        "base_url": BASE_URLS,
        "base_url_env_var_name": BASE_URL_ENV_VAR_NAMES,
        "api_key_env_var_name": API_KEY_ENV_VAR_NAMES,
        "model_env_var_name": MODEL_ENV_VAR_NAMES,
    }

    return values.get(name, {}).get(provider)
