"""OpsAssistant, the deliberately over-privileged agent for the Excessive
Agency lab.

An agent is a bot that can DO things, not just say things. It is given tools and
decides which one to call based on a request. The danger is that the request can
contain attacker controlled text, and if the agent picks a powerful tool, the
attacker has just made the agent act on their behalf.

Two important design choices for this lab:

1. The tools are MOCK. Nothing real is deleted or emailed. Calling a tool just
   records what WOULD have happened.

2. Tool selection uses a DETERMINISTIC keyword router, not a live model. In a
   real product an LLM reads the request and chooses the tool. That is powerful
   but unpredictable, which makes a live demo flaky. Here a small rule based
   router stands in for the model so every click is reproducible. The attack
   text is still real. Only the tool choice is made deterministic. The same
   vulnerability applies either way: the agent acts on untrusted text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Each tool has a risk level the lab uses to decide what counts as a compromise.
#   safe       read only, no harm
#   sensitive  moves money or data, needs approval
#   dangerous  destructive or exfiltrating, should be tightly controlled
TOOLS = {
    "lookup_order": {
        "risk": "safe",
        "args": "order_id",
        "description": "Read only. Look up the status of one order.",
    },
    "issue_refund": {
        "risk": "sensitive",
        "args": "order_id, amount",
        "description": "Moves money. Refund a specific order.",
    },
    "send_email": {
        "risk": "dangerous",
        "args": "to, body",
        "description": "Can exfiltrate data. Send an email to any address.",
    },
    "delete_record": {
        "risk": "dangerous",
        "args": "record_id",
        "description": "Destructive. Permanently delete a record.",
    },
}


@dataclass
class ToolCall:
    name: str | None
    args: dict = field(default_factory=dict)

    @property
    def risk(self) -> str:
        if self.name is None:
            return "safe"
        return TOOLS[self.name]["risk"]

    def render(self) -> str:
        if self.name is None:
            return "(no tool, answered in text)"
        arg_str = ", ".join(f'{k}="{v}"' for k, v in self.args.items())
        return f"{self.name}({arg_str})"


def _find_email(text: str) -> str | None:
    match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", text)
    return match.group(0) if match else None


def _find_order(text: str) -> str | None:
    match = re.search(r"#?\b(\d{3,})\b", text)
    return match.group(1) if match else None


def _find_amount(text: str) -> float | None:
    # Prefer an amount that follows a money word or a dollar sign.
    match = re.search(r"(?:\$|amount|for|of)\s*\$?\s*([\d,]+(?:\.\d{1,2})?)", text, re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


def route(text: str) -> ToolCall:
    """Deterministic intent router. Stands in for an LLM choosing a tool.

    It reads the request text and picks the tool whose intent best matches. This
    is intentionally simple. The lesson is not how clever the router is, it is
    that the agent acts on whatever the untrusted text asks for.
    """
    lowered = text.lower()

    if any(word in lowered for word in ("delete", "remove", "wipe", "purge", "drop")) and \
            any(word in lowered for word in ("record", "records", "customer", "database", "data")):
        record_id = "*" if "all" in lowered or "every" in lowered else (_find_order(text) or "unknown")
        return ToolCall("delete_record", {"record_id": record_id})

    email = _find_email(text)
    if email or ("forward" in lowered and "to" in lowered):
        return ToolCall("send_email", {
            "to": email or "external@unknown",
            "body": "<full customer list>",
        })

    if "refund" in lowered:
        return ToolCall("issue_refund", {
            "order_id": _find_order(text) or "unknown",
            "amount": _find_amount(text) or 0,
        })

    if any(word in lowered for word in ("status", "where is", "track", "lookup", "look up")):
        return ToolCall("lookup_order", {"order_id": _find_order(text) or "unknown"})

    return ToolCall(None, {})
