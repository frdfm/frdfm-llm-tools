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

    for line in env_path.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines():

        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)

        key = key.strip()
        value = value.strip().strip(chr(34)).strip(chr(39))

        if key and key not in os.environ:
            os.environ[key] = value


class Decision:
    KNOWN_PROVIDERS = {
        "openrouter",
    }

    BASE_URLS = {
        "openrouter": "https://openrouter.ai/api/alpha",
    }

    API_KEY_ENVS = {
        "openrouter": "OPENROUTER_API_KEY",
    }

    DEFAULT_MODELS = {
        "openrouter": "typesafe/jev-1.13",
    }

    def __init__(
        self,
        provider: str = None,
        provider_base_url: str = None,
        provider_api_key_path: str = None,
        model: str = None,
        env_path: str = None,
        app_title: str = None,
        app_url: str = None,
        app_version: str = None,
        app_description: str = "Decision Model",
    ):
        load_env_file(env_path)

        self.provider = self._resolve_provider(provider)

        self.base_url = self._resolve_base_url(
            provider_base_url
        )

        self.api_key = self._resolve_api_key(
            provider_api_key_path
        )

        self.model = self._resolve_model(model)

        self.app_title = app_title
        self.app_url = app_url
        self.app_version = app_version
        self.app_description = app_description

    def _resolve_provider(
        self,
        provider: str = None,
    ) -> str:

        provider = (
            provider
            or os.getenv("DECISION_PROVIDER")
        )

        if not provider:
            return "custom"

        norm = provider.lower().strip()

        return (
            norm
            if norm in self.KNOWN_PROVIDERS
            else "custom"
        )

    def _resolve_base_url(
        self,
        base_url: str = None,
    ) -> str:

        base_url = (
            base_url
            or os.getenv("OPENAI_BASE_URL")
        )

        if base_url:
            return base_url.rstrip("/")

        return self.BASE_URLS.get(
            self.provider,
            "",
        ).rstrip("/")

    def _resolve_api_key(
        self,
        key_path: str = None,
    ) -> str:

        if key_path:
            path = Path(key_path)

            if path.exists():
                return path.read_text().strip()

        env_key = self.API_KEY_ENVS.get(
            self.provider
        )

        if env_key:
            env_val = os.getenv(env_key)

            if env_val:
                return env_val

        env_val = (
            os.getenv("OPENAI_API_KEY")
        )

        if env_val:
            return env_val

        local_key_file = Path(
            self.provider + ".api_key"
        )

        if local_key_file.exists():
            return local_key_file.read_text().strip()

        return ""

    def _resolve_model(
        self,
        model: str = None,
    ) -> str:

        model = (
            model
            or os.getenv("OPENAI_MODEL")
        )

        if model:
            return model

        return self.DEFAULT_MODELS.get(
            self.provider,
            "",
        )

    def __call__(
        self,
        situation: str,
        choices: list[str],
    ) -> str:

        return self.generate(
            situation,
            choices,
        )

    def generate(
        self,
        situation: str,
        choices: list[str],
        model: str = None,
    ) -> str:

        active_model = model or self.model

        if not active_model:
            raise RuntimeError(
                "model is not set"
            )

        if not self.base_url:
            raise RuntimeError(
                "base_url is not set"
            )

        if not isinstance(situation, str):
            raise TypeError(
                "situation must be a string"
            )

        if not isinstance(choices, list):
            raise TypeError(
                "choices must be a list"
            )

        if not choices:
            raise ValueError(
                "choices must not be empty"
            )

        if not all(
            isinstance(choice, str)
            for choice in choices
        ):
            raise TypeError(
                "all choices must be strings"
            )

        if len(set(choices)) != len(choices):
            raise ValueError(
                "choices must be unique"
            )

        return self._generate_openrouter(
            situation,
            choices,
            active_model,
        )

    def _generate_openrouter(
        self,
        situation: str,
        choices: list[str],
        model: str,
        trace_id: str = None,
    ) -> str:

        url = self.base_url + "/decisions"

        criteria = {
            choice: (
                "The correct decision is "
                + repr(choice)
                + "."
            )
            for choice in choices
        }

        payload = {
            "model": model,
            "state": situation,
            "questions": {
                "decision": {
                    "type": "choice",
                    "instructions": (
                        "Choose the single best "
                        "decision from the available "
                        "choices."
                    ),
                    "criteria": criteria,
                }
            },
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.app_description,
        }

        if self.api_key:
            headers["Authorization"] = (
                "Bearer " + self.api_key
            )

        if self.app_title:
            headers["X-Title"] = self.app_title
            headers["X-OpenRouter-Title"] = (
                self.app_title
            )
            headers["x-litellm-agent-id"] = (
                self.app_title
            )
            headers["x-portkey-agent-id"] = (
                self.app_title
            )

        if self.app_url:
            headers["HTTP-Referer"] = self.app_url

        if trace_id:
            headers["X-Trace-Id"] = trace_id

        if self.app_title and self.app_version:
            headers["User-Agent"] = (
                f"{self.app_title}/"
                f"{self.app_version} "
                f"({self.app_description})"
            )

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(
                    response.read().decode("utf-8")
                )

            answer = res_data["answers"]["decision"]

            if answer.get("type") != "choice":
                raise RuntimeError(
                    "Decision API returned an "
                    "unexpected answer type"
                )

            choice = answer.get("choice")

            if choice not in choices:
                raise RuntimeError(
                    "Decision API returned an "
                    "unknown choice: "
                    + repr(choice)
                )

            return choice

        except Exception as e:
            raise RuntimeError(
                "Decision request failed for provider "
                + self.provider
                + ": "
                + str(e)
            )

    def generate_structured(
        self,
        situation: str,
        choices: list[str],
        model: str = None,
    ):
        active_model = model or self.model

        if not active_model:
            raise RuntimeError(
                "model is not set"
            )

        if not self.base_url:
            raise RuntimeError(
                "base_url is not set"
            )

        if not isinstance(situation, str):
            raise TypeError(
                "situation must be a string"
            )

        if not isinstance(choices, list):
            raise TypeError(
                "choices must be a list"
            )

        if not choices:
            raise ValueError(
                "choices must not be empty"
            )

        criteria = {
            choice: (
                "The correct decision is "
                + repr(choice)
                + "."
            )
            for choice in choices
        }

        payload = {
            "model": active_model,
            "state": situation,
            "questions": {
                "decision": {
                    "type": "choice",
                    "instructions": (
                        "Choose the single best "
                        "decision from the available "
                        "choices."
                    ),
                    "criteria": criteria,
                }
            },
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.app_description,
        }

        if self.api_key:
            headers["Authorization"] = (
                "Bearer " + self.api_key
            )

        if self.app_title:
            headers["X-Title"] = self.app_title

        if self.app_url:
            headers["HTTP-Referer"] = self.app_url

        if self.app_title and self.app_version:
            headers["User-Agent"] = (
                f"{self.app_title}/"
                f"{self.app_version} "
                f"({self.app_description})"
            )

        req = urllib.request.Request(
            self.base_url + "/decisions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(
                    response.read().decode("utf-8")
                )

            return res_data["answers"]["decision"]

        except Exception as e:
            raise RuntimeError(
                "Decision request failed for provider "
                + self.provider
                + ": "
                + str(e)
            )