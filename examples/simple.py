from frdfm_llm_tools import LLM

llm = LLM(env_path=r"d:\___env_var\deepinfra-qwen3.8-27B-Flash.env")
print(llm("Say hello world in one short sentence."))
