DEFAULT_MODEL = "gpt-4o-mini"

# Simple approximate pricing per 1M tokens (USD)
COST_PER_1M_TOKENS = {
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4.1-nano": {"input": 0.1, "output": 0.4},
    "gpt-5.0-nano": {"input": 0.03, "output": 0.4},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
}

DEFAULT_PRICING = {"input": 10.00, "output": 30.00} # Conservative fallback
