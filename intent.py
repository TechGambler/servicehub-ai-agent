"""
intent.py - Intent detection using a rule-based check first,
with Gemini LLM as fallback only when rules are uncertain.

Intents:
  greeting   - hello, hi, hey, etc.
  pricing    - plans, price, cost, features, trial, etc.
  high_intent- buy, sign up, get started, subscribe, purchase, etc.
  other      - everything else
"""

from llm import call_llm

# ---------------------------------------------------------------------------
# Rule-based keyword lists (fast, no API call)
# ---------------------------------------------------------------------------

GREETING_WORDS = {
    "hi", "hello", "hey", "howdy", "greetings", "good morning",
    "good afternoon", "good evening", "what's up", "sup"
}

PRICING_WORDS = {
    "price", "pricing", "plan", "plans", "cost", "how much",
    "features", "trial", "free trial", "compare", "comparison",
    "starter", "pro", "basic", "enterprise", "package", "tier"
}

HIGH_INTENT_WORDS = {
    "buy", "purchase", "sign up", "signup", "subscribe", "get started",
    "i want", "i'd like", "i would like", "register", "enroll",
    "start now", "let's go", "ready to", "take the"
}


def _rule_based(text: str) -> str | None:
    """
    Try to classify intent using keyword matching.
    Returns an intent string or None if uncertain.
    """
    lower = text.lower()

    # Check high_intent first — most specific
    if any(word in lower for word in HIGH_INTENT_WORDS):
        return "high_intent"

    if any(word in lower for word in PRICING_WORDS):
        return "pricing"

    # For greetings: only match if the message is short (avoids false positives)
    if any(word in lower for word in GREETING_WORDS) and len(text.split()) <= 6:
        return "greeting"

    return None  # Uncertain — fall back to LLM


def _llm_based(text: str) -> str:
    """Use Gemini to classify intent when rules are uncertain."""
    prompt = f"""You are an intent classifier for a SaaS product called ServiceHub.

Classify the following user message into EXACTLY ONE of these intents:
- greeting    : User is saying hello, hi, hey, good morning, etc.
- pricing     : User is asking about plans, pricing, cost, features, or trials.
- high_intent : User wants to buy, subscribe, sign up, get started, or purchase.
- other       : Anything else.

Reply with ONLY the intent label. No explanation. No punctuation.

User message: "{text}"

Intent:"""

    raw = call_llm(prompt).lower().strip()

    for intent in ["high_intent", "pricing", "greeting", "other"]:
        if intent in raw:
            return intent

    return "other"  # Safe default


def detect_intent(user_input: str) -> str:
    """
    Detect intent using rules first; LLM only as fallback.

    Args:
        user_input: Raw message from the user.

    Returns:
        One of: 'greeting', 'pricing', 'high_intent', 'other'
    """
    intent = _rule_based(user_input)
    if intent is not None:
        return intent
    return _llm_based(user_input)