from concurrent.futures import ThreadPoolExecutor
from frdfm_llm_tools import LLM

llm = LLM(env_path=r"d:\___env_var\deepinfra-qwen3.8-27B-Falsh.env")

concurrent_n = 2


def process_prompt(prompt):

    response = llm(prompt)
    print(f"Done: {response.strip()}")


prompts = [f"write a short story in one paragraph." for i in range(1, concurrent_n+1)]

with ThreadPoolExecutor(max_workers=500) as executor:
    executor.map(process_prompt, prompts)