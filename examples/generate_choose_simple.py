from frdfm_llm_tools import LLM

llm = LLM(
    generate_provider="deepinfra",
    generate_env_path=r"d:\___env_var\deepinfra-qwen3.8-27B-Flash.env",
    choose_provider="openrouter",
    choose_env_path=r"d:\___env_var\openrouter-jev1.13.env",
)

print(
    llm("Say hello world in one short sentence.")
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
        [
            "get their money back",
            "get a replacement product",
            "get some money as store credit instead of replacement or refund",
        ],
    )
)
