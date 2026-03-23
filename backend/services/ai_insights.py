import os
from typing import Optional


def generate_dns_insight(record_type: str, old_value: Optional[str], new_value: Optional[str]) -> str:
    """
    Generate a short, user-friendly explanation for how a DNS record change
    might impact resolution.

    Notes on "real LLM" structure (simulated):
    - system prompt (comment only): you are a DNS expert; respond with a single concise sentence.
    - user prompt (comment only): given record_type, old_value, and new_value, explain the potential impact.
    """

    # system prompt (example, comment only):
    # "You are a DNS resolution assistant. Provide concise, actionable guidance."
    #
    # user prompt structure (example, comment only):
    # {
    #   "record_type": "...",
    #   "old_value": "...",
    #   "new_value": "..."
    # }

    fallback = (
        f"A change in the {record_type} record may affect how this domain resolves. "
        "Verify configuration."
    )

    try:
        api_key = os.getenv("OPENAI_API_KEY")

        # "Real API" path is intentionally simulated; we never make a network call here.
        if api_key:
            # messages = [
            #   {"role": "system", "content": SYSTEM_PROMPT},
            #   {"role": "user", "content": USER_PROMPT}
            # ]
            # response = openai.chat.completions.create(... messages ...)
            #
            # Simulated response that still depends on the inputs.
            if old_value is not None and new_value is not None:
                return (
                    f"Detected a {record_type} change ({old_value} -> {new_value}). "
                    f"{fallback}"
                )

            return f"Detected a {record_type} change. {fallback}"

        # No API key: return a smart mock response (never raise).
        return fallback
    except Exception:
        # Fallback path ensures this never breaks the app.
        return fallback

