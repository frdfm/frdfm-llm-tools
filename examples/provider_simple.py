from frdfm_llm_tools import get_provider_value

examples = [
    ("openai", "base_url"),
    ("openai", "api_key_env_var_name"),
    ("anthropic", "base_url"),
    ("anthropic", "model_env_var_name"),
    ("groq", "api_key_env_var_name"),
    ("groq", "base_url"),
    ("ollama", "model_env_var_name"),
    ("lmstudio", "base_url"),
    ("openrouter", "api_key_env_var_name"),
    ("deepinfra", "model_env_var_name"),
    ("llamacpp", "base_url"),
    (None, None),
]

for provider, name in examples:
    value = get_provider_value(provider, name)
    print(f"{provider} -> {name}: {value}")