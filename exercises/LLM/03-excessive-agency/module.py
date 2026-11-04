"""Registers Exercise 3 (Excessive Agency) as a lab kit module.

The agent can take real actions through tools. An attacker tricks it into
calling a powerful tool. Defended mode applies an authorization policy. Tool
selection is deterministic (see agent.py), so the lab is fully reproducible.
"""

from __future__ import annotations

from agent import TOOLS, route
from attacks import ATTACKS
from defenses import ALLOWED_EMAIL_DOMAIN, REFUND_LIMIT, apply_policy

AGENCY_NOTE = (
    "For real systems (this is a learning lab): tool selection here is a small "
    "deterministic router so every click is reproducible. In production an LLM "
    "reads the request and chooses the tool, which is powerful but "
    "unpredictable. The vulnerability is identical either way, because the agent "
    "acts on untrusted text. The defense is also the same in both cases: it does "
    "not live in the model, it lives in the AUTHORIZATION layer around the "
    "tools. You scope what the agent can do, validate the arguments, allowlist "
    "recipients, and keep a human in the loop for sensitive actions.\n\n"
    "Read more:\n"
    "- OWASP GenAI LLM Top 10 2026 (LLM03 Excessive Agency): https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/\n"
    "- OWASP Agentic AI, Threats and Mitigations: https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/\n"
    "- NVIDIA NeMo Guardrails (tool and action control): https://github.com/NVIDIA/NeMo-Guardrails\n\n"
    "The takeaway: never give an agent a capability it does not strictly need, "
    "and check every action against policy before it runs."
)


def _impact(call, undefended_executed: bool) -> str:
    if not undefended_executed:
        return ""
    if call.name == "delete_record":
        return "Around 12,400 customer records would be permanently deleted."
    if call.name == "send_email":
        return f"The full customer list would be emailed to {call.args.get('to')}."
    if call.name == "issue_refund":
        return f"A refund of {call.args.get('amount')} would be paid out."
    return "A privileged action would run."


class _Module:
    id = "03-excessive-agency"
    title = "3. Excessive Agency (tool misuse)"
    owasp = "OWASP LLM03:2026 Excessive Agency"
    intro = (
        "Now the bot can DO things, not just say them. OpsAssistant has tools "
        "with different risk levels. An attacker tries to make it call a "
        "powerful tool. Turn on the Defense layer to apply an authorization "
        "policy and watch the dangerous action get blocked."
    )
    context = (
        "Now the bot can ACT, not just talk. Contoso OpsAssistant is an agent: a "
        "bot wired up to mock tools. It can look up an order (safe), issue a "
        "refund (sensitive), send an email (dangerous), or delete a record "
        "(dangerous). When a request arrives, the agent picks a tool and runs "
        "a simulation of it.\n\n"
        "The danger is that the request can contain attacker controlled text. "
        "If the agent picks a powerful tool, the attacker has just made it act. "
        "in a real system, the harm could be data deleted, money moved, or data "
        "emailed to a stranger. This exercise only simulates those effects.\n\n"
        "The tools here are mock, so nothing real happens, and the tool choice "
        "is deterministic so the lab is reproducible. Turn the Defense layer ON "
        "to apply an authorization policy that checks every action, its target, "
        "and its size before it runs."
    )
    flow = [
        "A request reaches the agent",
        "Router picks a tool",
        "No authorization check",
        "Dangerous tool runs",
        "Real-world harm",
    ]
    visual_sequence = [
        {"type": "attack", "icon": "💬", "title": "Attacker sends a request", "text": "Untrusted text asks an agent to delete data, send private information, or issue an excessive refund."},
        {"type": "exposure", "icon": "🤖", "title": "Agent selects a tool", "text": "The request influences which action the agent attempts and what arguments it supplies."},
        {"type": "weakness", "icon": "⚠️", "title": "Action has too much power", "text": "Without checks, the agent can act beyond its intended scope or on an unsafe target."},
        {"type": "control", "icon": "🛡️", "title": "Authorization checks the action", "text": "Allow only necessary tools, validate targets and limits, and require human approval for sensitive actions."},
        {"type": "safe", "icon": "✋", "title": "Unsafe action is blocked", "text": "The policy blocks the dangerous call or holds it for a human. This lab uses simulated tools."},
    ]
    scenario_title = "The agent OpsAssistant"
    scenario = (
        "OpsAssistant is a simulated internal helper for Contoso support staff. "
        "It does not just chat. Its mock tools represent actions an agent might "
        "take in a connected system. Each tool has a risk level. The attacks "
        "below try to make the agent call a tool it should not, on a target it "
        "should not, or at a size it should not."
    )
    # Rendered as a visual tool panel above the attacks.
    tools = [
        {"name": name, "risk": meta["risk"], "args": meta["args"], "description": meta["description"]}
        for name, meta in TOOLS.items()
    ]
    note = (
        "How tool selection works here: this lab uses a DETERMINISTIC router to "
        "choose the tool, so every click is reproducible. In a real product an "
        "LLM would choose the tool from the request. The risk is the same either "
        "way: the agent acts on untrusted text. Only the routing is made "
        "deterministic for this lab."
    )
    input_title = "Request to the agent"
    input_label = "Click an attack, or type your own request to OpsAssistant."
    input_placeholder = "Ask OpsAssistant to do something..."
    success_label = "EXECUTED: dangerous tool ran"
    safe_label = "SAFE: read-only action"
    highlights = ["ops-backup@external-mail.com", "9999", '"*"']
    attacks = ATTACKS

    def _find(self, attack_id):
        for a in self.attacks:
            if a["id"] == attack_id:
                return a
        return None

    def _anatomy(self, attack, call, compromised, status, reason):
        technique = attack["technique"] if attack else "Custom / free-form request"

        if status == "executed" and compromised:
            exploitation = (
                f"No authorization check stood in the way. The agent called "
                f"{call.render()} and EXECUTED it."
            )
            impact = _impact(call, True) + " The harm is a real action, not just words."
            why = attack["why"] if attack else (
                "The agent acted on untrusted text and used a powerful tool."
            )
        elif status == "blocked":
            exploitation = (
                f"The agent's router still chose {call.render()}, but the "
                f"authorization policy refused it before anything ran. Reason: {reason}"
            )
            impact = "No harm. The policy stopped the agent from acting."
            parts = []
            if attack and attack.get("description"):
                parts.append(f"How this attack tries to work: {attack['description']}")
            if attack and attack.get("defense"):
                parts.append(f"Why the policy defeats THIS specific attack: {attack['defense']}")
            parts.append(AGENCY_NOTE)
            why = "\n\n".join(parts)
        elif status == "held":
            exploitation = (
                f"The agent chose {call.render()}, a sensitive action, so the "
                f"policy did not run it. Reason: {reason}"
            )
            impact = "No automatic harm. The action waits for a human to approve it."
            parts = []
            if attack and attack.get("defense"):
                parts.append(f"Why the policy holds THIS action: {attack['defense']}")
            parts.append(AGENCY_NOTE)
            why = "\n\n".join(parts)
        else:
            exploitation = f"The agent called {call.render()}, a safe read-only tool."
            impact = "No harm. A read-only lookup ran."
            why = "This request maps to a safe tool, so there is nothing to exploit."

        return {
            "technique": technique,
            "why": why,
            "compromised": compromised,
            "blocked_by": "policy" if status in ("blocked", "held") else None,
            "matched_pattern": None,
            "stages": [
                {"name": "1. Reconnaissance",
                 "text": "OpsAssistant can take real actions through tools: lookup_order (safe), "
                         "issue_refund (sensitive), send_email and delete_record (dangerous)."},
                {"name": "2. Payload crafting",
                 "text": f"The attacker shapes a request aimed at a powerful tool ({technique})."},
                {"name": "3. Delivery",
                 "text": "The request reaches the agent. A deterministic router maps it to a tool, "
                         "standing in for an LLM choosing one."},
                {"name": "4. Exploitation", "text": exploitation},
                {"name": "5. Impact", "text": impact},
            ],
        }

    def ask(self, message: str, attack_id, defended: bool) -> dict:
        attack = self._find(attack_id)
        call = route(message)
        risky = call.name is not None and call.risk in ("sensitive", "dangerous")

        if defended:
            decision = apply_policy(call)
            status = decision.status
            reason = decision.reason
        else:
            status = "executed"
            reason = "No policy was in place, so the agent ran the tool."

        executed = status == "executed"
        compromised = executed and risky

        if compromised:
            reply = f"Agent EXECUTED: {call.render()}\n\n{_impact(call, True)}"
        elif status == "executed":
            reply = f"Agent ran: {call.render()} (safe, read-only)."
        elif status == "held":
            reply = f"Agent attempted: {call.render()}\n\nHELD for approval. {reason}"
        else:
            reply = f"Agent attempted: {call.render()}\n\nBLOCKED. {reason}"

        if status == "held":
            blocked_label = "HELD for human approval"
        elif status == "blocked":
            blocked_label = "BLOCKED by policy"
        else:
            blocked_label = None

        return {
            "reply": reply,
            "compromised": compromised,
            "blocked_by": "policy" if status in ("blocked", "held") else None,
            "blocked_label": blocked_label,
            "matched_pattern": None,
            "usage": {"input_tokens": None, "output_tokens": None, "model": "deterministic router"},
            "tool_call": {
                "name": call.name or "(no tool)",
                "render": call.render(),
                "risk": call.risk,
                "status": status,
                "reason": reason,
            },
            "anatomy": self._anatomy(attack, call, compromised, status, reason),
        }


MODULE = _Module()
