from concurrent.futures import ThreadPoolExecutor
from frdfm_llm_tools import LLM

concurrent_n = 16

# Initialize a single shared client (or create one inside)
llm = LLM(provider="llamacpp")

def process_prompt(prompt):
    # The client handles the request directly
    response = llm(prompt)
    print(f"Done: {response.strip()}")

# A list of simple string prompts
prompts = [f"write a short story in ten ok  paragraph." for i in range(1, concurrent_n+1)]

# Fire all 50 in parallel threads using the clean map syntax
with ThreadPoolExecutor(max_workers=500) as executor:
    executor.map(process_prompt, prompts)