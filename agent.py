from intent import detect_intent
from rag import get_answer
from tools import mock_lead_capture

memory = {}

def run_agent(user_input):
    intent = detect_intent(user_input)

    print(f"[DEBUG] Intent: {intent}")  # helpful for demo

    if intent == "greeting":
        return "Hey! 👋 How can I help you?"

    if intent == "pricing":
        return get_answer(user_input)

    if intent == "high_intent":
        memory["stage"] = "collect_name"
        return "Awesome! Let's get you started. What's your name?"

    # memory flow
    if memory.get("stage") == "collect_name":
        memory["name"] = user_input
        memory["stage"] = "collect_email"
        return "Your email?"

    if memory.get("stage") == "collect_email":
        memory["email"] = user_input
        memory["stage"] = "collect_platform"
        return "Which platform do you create on?"

    if memory.get("stage") == "collect_platform":
        memory["platform"] = user_input

        mock_lead_capture(
            memory["name"],
            memory["email"],
            memory["platform"]
        )

        memory.clear()
        return "🎉 You're onboarded successfully!"

    return "Can you tell me more?"