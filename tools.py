"""
tools.py - Mock CRM API tool.

mock_lead_capture(name, email, platform) simulates submitting
a lead to an external CRM system (e.g., HubSpot, Salesforce).
"""

import json
from datetime import datetime


def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    """
    Simulate a CRM API call to record a new lead.

    Args:
        name    : Lead's full name.
        email   : Lead's email address.
        platform: Platform the lead is interested in.

    Returns:
        Mock API response as a dict.
    """
    payload = {
        "status": "success",
        "lead": {
            "name": name,
            "email": email,
            "platform": platform,
            "source": "ServiceHub Chatbot",
            "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "message": f"Lead for '{name}' successfully recorded.",
    }

    print("\n" + "=" * 52)
    print("  📡  MOCK CRM API — Lead Submitted")
    print("=" * 52)
    print(json.dumps(payload, indent=2))
    print("=" * 52 + "\n")

    return payload