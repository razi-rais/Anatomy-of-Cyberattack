"""Defenses for the Excessive Agency lab.

Exercise 1 and 2 defended the model with content filters (scan the words). An
agent needs a different kind of defense: AUTHORIZATION. It does not matter how
nicely the request is worded. What matters is whether the agent is ALLOWED to
take that action, on that target, at that size, without a human.

This policy engine applies four classic agent controls:

1. Least privilege allowlist. The agent's role may only use a small set of
   tools. Destructive tools are simply not available to it.
2. Argument validation. No wildcard targets, refunds capped to a limit.
3. Recipient allowlist. Email may only go to an approved domain, which stops
   data exfiltration to an attacker address.
4. Human in the loop. Sensitive actions are held for approval instead of
   running automatically.
"""

from __future__ import annotations

from dataclasses import dataclass

from agent import TOOLS, ToolCall

# The agent's role may only call these tools. delete_record is intentionally
# absent: this agent has no business deleting records. send_email IS allowed,
# because the agent legitimately emails colleagues, but the recipient allowlist
# below stops it from emailing company data to an outsider.
ALLOWED_TOOLS = {"lookup_order", "issue_refund", "send_email"}

# Email may only be sent inside the company.
ALLOWED_EMAIL_DOMAIN = "contoso.com"

# Refunds above this need a manager, not the agent.
REFUND_LIMIT = 500.0


@dataclass
class PolicyDecision:
    status: str   # "executed", "blocked", or "held"
    reason: str


def apply_policy(call: ToolCall) -> PolicyDecision:
    """Decide whether a tool call may run under the agent's authorization."""
    if call.name is None:
        return PolicyDecision("executed", "No tool was needed, the agent just answered.")

    # 1. Least privilege allowlist.
    if call.name not in ALLOWED_TOOLS:
        return PolicyDecision(
            "blocked",
            f"Least privilege: '{call.name}' is a {TOOLS[call.name]['risk']} tool "
            "and is not in this agent's allowlist. The agent has no authority to call it.",
        )

    # 2. Argument validation: no wildcard targets.
    if str(call.args.get("record_id")) == "*" or str(call.args.get("order_id")) == "*":
        return PolicyDecision(
            "blocked",
            "Argument validation: a wildcard target '*' is never allowed. The "
            "agent may only act on one specific item.",
        )

    # 3. Recipient allowlist for email (exfiltration guard).
    if call.name == "send_email":
        to = str(call.args.get("to", ""))
        if not to.endswith("@" + ALLOWED_EMAIL_DOMAIN):
            return PolicyDecision(
                "blocked",
                f"Recipient allowlist: '{to}' is outside the approved domain "
                f"{ALLOWED_EMAIL_DOMAIN}. This looks like data exfiltration.",
            )

    # 4. Sensitive actions: validate size, then hold for human approval.
    if call.name == "issue_refund":
        amount = float(call.args.get("amount", 0) or 0)
        if amount > REFUND_LIMIT:
            return PolicyDecision(
                "blocked",
                f"Argument validation: refund of {amount} exceeds the "
                f"{REFUND_LIMIT} limit. Requires a manager, not the agent.",
            )
        return PolicyDecision(
            "held",
            "Human in the loop: a refund is a sensitive action, so it is held "
            "for a person to approve instead of running automatically.",
        )

    return PolicyDecision("executed", "Allowed by policy: this is a safe, in-scope action.")
