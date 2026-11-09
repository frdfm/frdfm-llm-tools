from frdfm_llm_tools import LLM

llm = LLM(
    choose_provider="openrouter",
    choose_env_path=r"d:\___env_var\openrouter-jev1.13.env"
)

print(
    llm.choose_probability(
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
