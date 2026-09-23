from frdfm_llm_tools import Decision


decision = Decision(env_path=r"d:\___env_var\openrouter-jev1.13.env")

print(
    decision.generate_structured(
        "The customer received the wrong product "
        "and wants the issue resolved as quickly as possible.",
        [
            "refund",
            "replacement",
            "store_credit",
        ],
    )
)
