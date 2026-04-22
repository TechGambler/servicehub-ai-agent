"""
graph_agent.py - LangGraph state machine for the ServiceHub AI Agent.

Flow:
    intent_node → router → greet_node | rag_node | lead_node
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

from intent import detect_intent
from rag import get_answer
from tools import mock_lead_capture
from llm import call_llm


# ---------------------------------------------------------------------------
# 1. Shared State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    user_input: str       # Latest user message
    intent: str           # Detected intent
    response: str         # Bot reply
    name: str             # Lead name
    email: str            # Lead email
    platform: str         # Lead platform
    stage: str            # Tracks lead capture progress
    history: list         # Conversation history [{role, content}, ...]


# ---------------------------------------------------------------------------
# 2. Nodes
# ---------------------------------------------------------------------------

def intent_node(state: AgentState) -> AgentState:
    """Detect intent only when not mid-lead-capture."""
    if state["stage"] not in ("start", "done"):
        return state  # Mid-capture: skip re-detection

    state["intent"] = detect_intent(state["user_input"])
    return state


def router_node(state: AgentState) -> str:
    """
    Conditional edge: return name of next node.
    Priority: active lead stage > intent-based routing.
    """
    stage = state["stage"]

    if stage in ("ask_name", "ask_email", "ask_platform", "submit"):
        return "lead_node"

    intent = state["intent"]

    if intent == "greeting":
        return "greet_node"
    elif intent == "pricing":
        return "rag_node"
    elif intent == "high_intent":
        state["stage"] = "ask_name"
        return "lead_node"
    else:
        return "rag_node"  # "other" → fall back to RAG


def greet_node(state: AgentState) -> AgentState:
    """Return a fixed greeting — no LLM call needed."""
    response = (
        "👋 Hi there! I'm the ServiceHub assistant.\n"
        "I can help you with pricing plans, policies, or getting you signed up.\n"
        "What would you like to know?"
    )
    state["response"] = response
    _add_history(state, state["user_input"], response)
    return state


def rag_node(state: AgentState) -> AgentState:
    """Answer pricing / policy questions using RAG."""
    # Simple, consistent call — matches def get_answer(query) in rag.py
    response = get_answer(state["user_input"])
    state["response"] = response
    _add_history(state, state["user_input"], response)
    return state


def lead_node(state: AgentState) -> AgentState:
    """
    Multi-step lead capture.

    Stage transitions:
        ask_name → (collect name) → ask_email
        ask_email → (collect email) → ask_platform
        ask_platform → (collect platform) → submit
        submit → call mock CRM → done
    """
    stage = state["stage"]
    user_input = state["user_input"].strip()

    if stage == "ask_name":
        if not state["name"]:
            # First arrival: ask for name
            response = (
                "Great! I'd love to get you started with ServiceHub. 🚀\n"
                "Could you please share your full name?"
            )
            state["response"] = response
            _add_history(state, user_input, response)
            # Mark that we are now waiting for the name answer
            state["stage"] = "ask_name"
            # Use a sentinel so next visit saves the input
            state["name"] = "__waiting__"
            return state
        else:
            # Second arrival: input IS the name
            state["name"] = user_input
            response = f"Nice to meet you, {state['name']}! What's your email address?"
            state["stage"] = "ask_email"
            state["response"] = response
            _add_history(state, user_input, response)
            return state

    if stage == "ask_email":
        state["email"] = user_input
        platforms = ", ".join(["Web", "iOS", "Android", "Desktop"])
        response = (
            f"Got it! Which platform are you interested in?\n"
            f"Options: {platforms}"
        )
        state["stage"] = "ask_platform"
        state["response"] = response
        _add_history(state, user_input, response)
        return state

    if stage == "ask_platform":
        state["platform"] = user_input
        state["stage"] = "submit"
        # Fall through to submit

    if stage == "submit":
        mock_lead_capture(
            name=state["name"],
            email=state["email"],
            platform=state["platform"],
        )
        response = (
            f"✅ Thank you, {state['name']}! Your details have been recorded.\n"
            f"Our team will reach out to {state['email']} about the "
            f"{state['platform']} platform soon.\n"
            "Is there anything else I can help you with?"
        )
        state["stage"] = "done"
        state["response"] = response
        _add_history(state, user_input, response)
        return state

    # Safety fallback
    state["response"] = "Something went wrong. How can I help you?"
    state["stage"] = "start"
    return state


# ---------------------------------------------------------------------------
# 3. Helpers
# ---------------------------------------------------------------------------

def _add_history(state: AgentState, user_msg: str, bot_msg: str):
    """Append latest exchange to history."""
    state["history"].append({"role": "user", "content": user_msg})
    state["history"].append({"role": "assistant", "content": bot_msg})


# ---------------------------------------------------------------------------
# 4. Build Graph
# ---------------------------------------------------------------------------

def build_graph():
    """Wire nodes and edges, return a compiled LangGraph app."""
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("intent_node", intent_node)
    graph.add_node("greet_node", greet_node)
    graph.add_node("rag_node", rag_node)
    graph.add_node("lead_node", lead_node)

    # Entry point
    graph.set_entry_point("intent_node")

    # Conditional routing after intent detection
    graph.add_conditional_edges(
        "intent_node",
        router_node,
        {
            "greet_node": "greet_node",
            "rag_node": "rag_node",
            "lead_node": "lead_node",
        },
    )

    # All terminal nodes end the graph
    graph.add_edge("greet_node", END)
    graph.add_edge("rag_node", END)
    graph.add_edge("lead_node", END)

    return graph.compile()