class LLM:
    def __init__(self, provider: str = "openai", model: str = "gpt-4o"):
        self.provider = provider
        self.model = model

    def __call__(self, prompt: str, system: str = "") -> str:
        """Allows calling the instance directly: llm("Hello!")"""
        return self.generate(prompt, system=system)

    def generate(self, prompt: str, system: str = "") -> str:
        """Standardized string generation."""
        return "Hi! I am not initialized yet!"

    def generate_structured(self, prompt: str, response_model):
        """Standardized structured output generation."""
        raise NotImplementedError
