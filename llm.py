"""
llm.py - Single point of access for all Gemini LLM calls.

Model  : gemini-1.5-flash  (stable, fast, cost-efficient)
Key    : Read from GEMINI_API_KEY environment variable — never hardcoded.
"""

import os
from google import genai

# ---------------------------------------------------------------------------
# Model name in one place — change here to affect the whole project
# ---------------------------------------------------------------------------
model="gemini-1.0-pro"


def _get_client() -> genai.Client:
    """Build and return a Gemini client from the environment variable."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "\n[ERROR] GEMINI_API_KEY is not set.\n"
            "  Mac/Linux : export GEMINI_API_KEY='your-key'\n"
            "  Windows   : set GEMINI_API_KEY=your-key\n"
        )
    return genai.Client(api_key=api_key)


def call_llm(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the response text.

    Args:
        prompt: Full text prompt.

    Returns:
        Model response as a stripped string.

    Raises:
        ValueError  : GEMINI_API_KEY not set.
        Exception   : Any API-level error (caller should handle).
    """
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    return response.text.strip()