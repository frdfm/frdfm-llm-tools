import json
import urllib.request
from .provider import get_provider_value
from frdfm_python_tools import get_env


class LLM:

    def __init__(
            self,
            generate_provider: str = None,
            generate_base_url: str = None,
            generate_api_key: str = None,
            generate_model: str = None,
            #
            choose_provider: str = None,
            choose_base_url: str = None,
            choose_api_key: str = None,
            choose_model: str = None,
            #
            generate_env_path: str = None,
            choose_env_path: str = None,
            #
            app_title: str = None,
            app_url: str = None,
            app_version: str = None,
            app_description: str = 'AI Agent',
            #
            system: str = ""
    ):
        #
        self.generate_provider = generate_provider

        provider_base_url_env_var_name = get_provider_value(generate_provider, "base_url_env_var_name")
        provider_api_key_env_var_name = get_provider_value(generate_provider, "api_key_env_var_name")
        provider_model_env_var_name = get_provider_value(generate_provider, "model_env_var_name")
        provider_base_url = get_provider_value(generate_provider, "base_url")

        self.generate_base_url = get_env(generate_base_url, provider_base_url_env_var_name, generate_env_path, provider_base_url)
        self.generate_api_key = get_env(generate_api_key, provider_api_key_env_var_name, generate_env_path)
        self.generate_model = get_env(generate_model, provider_model_env_var_name, generate_env_path)

        #
        self.choose_provider = choose_provider

        provider_base_url_env_var_name = get_provider_value(choose_provider, "base_url_env_var_name")
        provider_api_key_env_var_name = get_provider_value(choose_provider, "api_key_env_var_name")
        provider_model_env_var_name = get_provider_value(choose_provider, "model_env_var_name")
        provider_base_url = get_provider_value(choose_provider, "base_url")

        self.choose_base_url = get_env(choose_base_url, provider_base_url_env_var_name, choose_env_path, provider_base_url)
        self.choose_api_key = get_env(choose_api_key, provider_api_key_env_var_name, choose_env_path)
        self.choose_model = get_env(choose_model, provider_model_env_var_name, choose_env_path)

        #
        self.app_title = app_title
        self.app_url = app_url
        self.app_version = app_version
        self.app_description = app_description

        #
        self.system = system

    def __call__(self, *args, **kwargs):
        return self.generate(*args, **kwargs)

    def generate(
            self,
            prompt: str,
            trace_id: str = None
    ) -> str:

        return self._generate_openai_compatible(prompt, trace_id)

    def _generate_openai_compatible(
            self,
            prompt: str,
            trace_id: str = None
    ) -> str:
        if not self.generate_base_url:
            raise RuntimeError('base_url is not set')

        url = self.generate_base_url + '/chat/completions'
        messages = []
        if self.system:
            messages.append({'role': 'system', 'content': self.system})
        messages.append({'role': 'user', 'content': prompt})

        payload = {'model': self.generate_model, 'messages': messages}

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': self.app_description
        }
        if self.generate_api_key:
            headers['Authorization'] = 'Bearer ' + self.generate_api_key
        if self.app_title:
            headers['X-Title'] = self.app_title
            headers['X-OpenRouter-Title'] = self.app_title
            headers['x-litellm-agent-id'] = self.app_title
            headers['x-portkey-agent-id'] = self.app_title
        if self.app_url:
            headers['HTTP-Referer'] = self.app_url
        if trace_id:
            headers['X-Trace-Id'] = trace_id
        if self.app_title and self.app_version:
            headers['User-Agent'] = f'{self.app_title}/{self.app_version} ({self.app_description})'

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
            raise RuntimeError('OpenAI-compatible request failed for provider ' + self.generate_provider + ': ' + str(e))

    def choose(
        self,
        situation: str,
        choices: list[str],
        trace_id: str = None,
    ) -> str:

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

        return self._choose(
            situation,
            choices,
            trace_id,
        )

    def _choose(
        self,
        situation: str,
        choices: list[str],
        trace_id: str = None,
    ) -> str:

        url = self.choose_base_url + "/decisions"

        criteria = {
            choice: (
                "The correct decision is "
                + repr(choice)
                + "."
            )
            for choice in choices
        }

        payload = {
            "model": self.choose_model,
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

        if self.choose_api_key:
            headers["Authorization"] = (
                "Bearer " + self.choose_api_key
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
                + self.choose_provider
                + ": "
                + str(e)
            )

    def choose_probability(
        self,
        situation: str,
        choices: list[str],
        model: str = None,
    ):
        active_model = model or self.choose_model

        if not active_model:
            raise RuntimeError(
                "model is not set"
            )

        if not self.choose_base_url:
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

        if self.choose_api_key:
            headers["Authorization"] = (
                "Bearer " + self.choose_api_key
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
            self.choose_base_url + "/decisions",
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
                + self.choose_provider
                + ": "
                + str(e)
            )