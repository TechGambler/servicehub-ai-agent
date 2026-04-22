# servicehub-ai-agent
# 🤖 ServiceHub AI Agent

A conversational AI sales assistant built with **Python**, **LangGraph**, and **Google Gemini**.  
It detects user intent, answers questions from a local knowledge base using RAG, captures leads,  
and simulates submitting them to a CRM — all through a clean CLI interface.

---

## ✨ Features

- 🧠 **Intent Detection** — Classifies every message into `greeting`, `pricing`, `high_intent`, or `other` using Gemini
- 📚 **RAG (Retrieval-Augmented Generation)** — Answers pricing and policy questions grounded in `data.json`
- 🔄 **Multi-turn Memory** — Remembers the last few exchanges for natural, context-aware replies
- 🎯 **Lead Capture Flow** — Collects name → email → platform when a user shows buying intent
- 📡 **Mock CRM API** — Simulates submitting lead data to a CRM system after collection
- 🔒 **No hardcoded secrets** — API key is read from an environment variable

---

## 📁 Project Structure

```
servicehub-agent/
├── main.py          # CLI entry point — runs the chat loop
├── graph_agent.py   # LangGraph state machine (nodes + routing logic)
├── intent.py        # Intent detection using Gemini
├── rag.py           # RAG: loads data.json, queries Gemini for answers
├── tools.py         # mock_lead_capture() — simulates CRM API call
├── llm.py           # Gemini client setup and call_llm() helper
├── data.json        # Local knowledge base (pricing plans + policies)
├── requirements.txt # Python dependencies
└── README.md        # This file
```

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌─────────────┐
│ intent_node │  ← Gemini classifies the message
└──────┬──────┘
       │
┌──────▼──────┐
│ router_node │  ← Decides next node based on intent + stage
└──────┬──────┘
       │
  ┌────┴────────────┬──────────────┐
  ▼                 ▼              ▼
greet_node       rag_node      lead_node
(LLM greeting)  (RAG answer)  (name→email→platform→CRM)
  │                 │              │
  └────────┬────────┘              │
           ▼                       ▼
          END               mock_lead_capture()
                                   │
                                  END
```

**State shared across all nodes:**

| Field                  | Purpose                                  |
|------------------------|------------------------------------------|
| `user_input`           | Latest message from the user             |
| `intent`               | Detected intent for the current turn     |
| `response`             | Bot reply to print to the user           |
| `name`                 | Lead's full name (collected in lead flow)|
| `email`                | Lead's email address                     |
| `platform`             | Lead's preferred platform                |
| `stage`                | Controls which step of lead flow we're in|
| `conversation_history` | List of past turns for multi-turn context|

---

## 💬 Example Conversation

```
=========================================================
  Welcome to ServiceHub AI Assistant
  Type 'quit' or 'exit' to end the chat
=========================================================

You: Hi there!

Bot: Hey! 👋 I'm the ServiceHub assistant. I can help you explore our
     pricing plans, answer policy questions, or get you signed up.
     What can I help you with today?

──────────────────────────────────────────────────────

You: What plans do you offer?

Bot: Here's a quick overview of our plans:

     🔹 Basic Plan — $19/month
       • Up to 3 users
       • 5 GB storage
       • Email support (72-hour response)
       • Basic analytics dashboard

     🔹 Pro Plan — $59/month
       • Up to 20 users
       • 50 GB storage
       • Priority email & live chat support
       • Advanced analytics & API access

     🔹 Enterprise Plan — Custom pricing
       • Unlimited users & storage
       • 24/7 dedicated support with SLA
       • Custom integrations & onboarding

     All plans include a 14-day free trial — no credit card required!

──────────────────────────────────────────────────────

You: I want to sign up for the Pro plan

Bot: Great! I'd love to get you set up with ServiceHub. 🚀
     First, could you please share your full name?

You: Jane Smith

Bot: Nice to meet you, Jane Smith! What's your email address?

You: jane@example.com

Bot: Got it! And which platform are you interested in?
     Options: Web, iOS, Android, Desktop

You: Web

====================================================
  📡  MOCK CRM API CALL  —  Lead Submitted
====================================================
{
  "status": "success",
  "lead": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "platform": "Web",
    "source": "ServiceHub Chatbot",
    "captured_at": "2025-07-15 14:32:07"
  },
  "message": "Lead for 'Jane Smith' has been successfully recorded."
}
====================================================

Bot: ✅ Thank you, Jane Smith! Your details have been recorded.
     Our team will reach out to jane@example.com shortly about the Web platform.
     Is there anything else I can help you with?

You: What is your refund policy?

Bot: We offer a 30-day money-back guarantee on all paid plans. If you're not
     satisfied within the first 30 days, contact support@servicehub.com for
     a full refund — no questions asked.

You: exit

Bot: Thank you for chatting with ServiceHub. Goodbye! 👋
```

---

## ▶️ How to Run

See the **VS Code Setup Guide** below for full step-by-step instructions.

**Quick start (if already set up):**

```bash
cd servicehub-agent
source venv/bin/activate          # Windows: venv\Scripts\activate
export GEMINI_API_KEY="your-key"  # Windows: set GEMINI_API_KEY=your-key
python main.py
```
