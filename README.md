# frdfm-llm-tools
Simple LLM tools for commonly used local and remote providers.

## Installation

You can install the package (```frdfm-llm-tools```) via `pip`:

```bash
pip install git+https://github.com/frdfm/frdfm-python-tools.git
pip install git+https://github.com/frdfm/frdfm-llm-tools.git
```

## Usage

```python
from frdfm_llm_tools import LLM

llm = LLM(
    generate_provider="deepinfra",
    generate_env_path=r"d:\___env_var\deepinfra-qwen3.8-27B-Flash.env"
)

print(
    llm("Say hello world in one short sentence.")
)
```


```python
from frdfm_llm_tools import LLM

llm = LLM(
    choose_provider="openrouter",
    choose_env_path=r"d:\___env_var\openrouter-jev1.13.env"
)

print(
    llm.choose(
        "The customer received the wrong product "
        "and wants the issue resolved as quickly as possible.",
        [
            "refund",
            "replacement",
            "store_credit",
        ],
    )
)
```
