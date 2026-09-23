# frdfm-llm-tools
Simple LLM tools for commonly used local and remote providers.

## Installation

You can install the package (```frdfm-llm-tools```) via `pip`:

```bash
pip install git+https://github.com/frdfm/frdfm-llm-tools.git
```

## Usage

```python
from frdfm_llm_tools import LLM

llm = LLM(env_path=r"d:\___env_var\deepinfra-qwen3.8-27B-Flash.env")
print(llm("Hi!"))
```
