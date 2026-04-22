"""
rag.py - Retrieval-Augmented Generation from a local JSON knowledge base.

Public API (must match graph_agent.py exactly):
    get_answer(query: str) -> str
"""

import json
import os
from llm import call_llm

# Module-level cache — data.json is read once per session
_kb: dict | None = None


def _load_kb() -> dict:
    """Load and cache data.json from the same directory as this file."""
    global _kb
    if _kb is not None:
        return _kb
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "data.json")
    with open(path, "r", encoding="utf-8") as f:
        _kb = json.load(f)
    return _kb


def get_answer(query: str) -> str:
    """
    Answer a user question using the local knowledge base + Gemini.

    Args:
        query: The user's question (plain string — no extra arguments).

    Returns:
        A grounded natural-language answer.
    """
    kb = _load_kb()
    context = json.dumps(kb, indent=2)

    prompt = f"""You are a helpful sales assistant for ServiceHub, a SaaS platform.

Use ONLY the knowledge base below to answer the user's question.
Do NOT make up information not present in the knowledge base.

Formatting rules:
- For pricing: list each plan name, price, and key features using bullet points.
- For policies: give a concise 2-3 sentence answer.
- If the topic is not in the knowledge base: say you don't have that information
  and suggest contacting support@servicehub.com.

--- KNOWLEDGE BASE ---
{context}
--- END ---

User question: {query}

Answer:"""

    try:
        return call_llm(prompt)
    except Exception as e:
        return (
            f"I'm having trouble retrieving that information right now. "
            f"Please contact support@servicehub.com for help. (Error: {e})"
        )