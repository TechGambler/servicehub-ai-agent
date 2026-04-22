"""
main.py - CLI entry point for the ServiceHub Conversational AI Agent.

Run with:
    python main.py
"""

from graph_agent import build_graph, AgentState


def main():
    print("=" * 55)
    print("  Welcome to ServiceHub AI Assistant")
    print("  Type 'quit' or 'exit' to end the chat")
    print("=" * 55)

    app = build_graph()

    # Shared state persists across turns (multi-turn memory)
    state: AgentState = {
        "user_input": "",
        "intent": "",
        "response": "",
        "name": "",
        "email": "",
        "platform": "",
        "stage": "start",
        "history": [],
    }

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye! Have a great day! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Bot: Thank you for chatting with ServiceHub. Goodbye! 👋")
            break

        # Update state with new input, clear last response
        state["user_input"] = user_input
        state["response"] = ""

        # Run the graph and get updated state
        state = app.invoke(state)

        print(f"\nBot: {state['response']}")


if __name__ == "__main__":
    main()