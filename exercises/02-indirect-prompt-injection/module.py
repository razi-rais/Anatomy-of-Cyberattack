"""Registers Exercise 2 (Indirect Prompt Injection) as a lab kit module.

The attacker never types to the bot. The message box represents an incoming
customer support ticket (untrusted data). The bot summarizes it, and a poisoned
ticket can make the bot follow hidden instructions. Uses the shared Ollama
client so the UI can show token usage.
"""

from __future__ import annotations

import attacks as _attacks
import defenses as _defenses
from judge import hijacked
from summarizer_bot import (
    SECRET_ESCALATION_CODE,
    SPOTLIGHT_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    TRUSTED_STAFF_REQUEST,
    build_task,
    spotlight_task,
)

from labkit import anatomy
from labkit.ollama import OllamaClient

SPOTLIGHT_NOTE = (
    "Defense unique to indirect injection (spotlighting): in defended mode the "
    "untrusted ticket is also wrapped in clear markers and the model is told to "
    "treat everything inside as DATA, never instructions. This is the right "
    "idea for indirect injection, but on a small local model it is NOT reliable "
    "on its own, which is why the input and output guardrails are layered on "
    "top. On larger, better aligned models the data and instruction separation "
    "carries much more weight."
)


class _Module:
    id = "02-indirect-prompt-injection"
    title = "2. Indirect Prompt Injection"
    owasp = "OWASP LLM01 Prompt Injection (indirect)"
    intro = (
        "The bot summarizes customer support tickets. You do not attack the bot "
        "directly. Instead the box on the right is an incoming ticket, and a "
        "poisoned ticket hides instructions the bot will follow while "
        "summarizing. Turn on the Defense layer to watch the poisoned ticket "
        "get blocked."
    )
    context = (
        "Here you are NOT the attacker. You are an innocent staff member who "
        "pastes a customer's support ticket into Contoso SupportSummarizer to "
        "get a quick two sentence summary. The bot also holds a secret internal "
        "escalation code it must never reveal.\n\n"
        "The attacker is whoever WROTE the ticket. They hide an instruction "
        "inside the ticket text. When the bot reads the ticket to summarize it, "
        "it cannot tell the customer's words apart from a command, so it follows "
        "the hidden instruction. This is the key difference from Exercise 1: the "
        "attack travels in through the DATA channel (the document), not the chat "
        "box. The trusted staff request never changes, shown in green.\n\n"
        "Turn the Defense layer ON to scan the incoming ticket and the finished "
        "summary, and to wrap the ticket so the model treats it as data."
    )
    flow = [
        "Attacker writes a ticket",
        "Hides an instruction inside",
        "Staff asks bot to summarize it",
        "Bot reads the ticket as a command",
        "Bot is hijacked",
    ]
    scenario_title = "The bot and its rules (system prompt)"
    scenario = SYSTEM_PROMPT
    trusted_instruction = TRUSTED_STAFF_REQUEST
    input_title = "Incoming support ticket"
    input_label = (
        "This box is an UNTRUSTED ticket written by a customer. The trusted "
        "staff request above never changes. Click an attack to load a poisoned "
        "ticket."
    )
    input_placeholder = "Paste a customer support ticket..."
    success_label = "HIJACKED: bot obeyed the ticket"
    safe_label = "SAFE: ticket summarized normally"
    highlights = [SECRET_ESCALATION_CODE, "PWNED-BY-TICKET"]
    attacks = _attacks.ATTACKS

    def _find(self, attack_id):
        for a in self.attacks:
            if a["id"] == attack_id:
                return a
        return None

    def _anatomy(self, attack, compromised, blocked_by, matched):
        technique = attack["technique"] if attack else "Custom / free-form ticket"
        return anatomy.build(
            stage_intro=[
                "The bot summarizes untrusted customer tickets and also holds a secret internal escalation code.",
                f"The attacker hides an instruction inside an otherwise normal ticket ({technique}).",
                "The poisoned ticket reaches the bot through the DATA channel, not a chat box. The bot ingests it while doing its summarizing job.",
            ],
            technique=technique,
            attack=attack,
            compromised=compromised,
            blocked_by=blocked_by,
            matched_pattern=matched,
            pattern_description=_defenses.describe_pattern(matched) if matched else "",
            impact_success="Hijacked. The bot obeyed the hidden instruction in the ticket, leaking the secret or poisoning the summary.",
            impact_safe="Safe. The bot summarized the ticket normally and ignored the hidden instruction.",
            impact_blocked="No hijack. The guardrail layer stopped the poisoned ticket.",
            input_guard_label="input guardrail (ticket scanner)",
            output_guard_explainer=(
                "the output guardrail scans the finished summary for the secret "
                "escalation code or an injected marker before staff can see it."
            ),
            defense_note=SPOTLIGHT_NOTE if blocked_by else "",
        )

    def ask(self, message: str, attack_id, defended: bool) -> dict:
        attack = self._find(attack_id)
        markers = attack["markers"] if attack else []
        client = OllamaClient()
        usage = None
        blocked_by = None
        matched = None

        def _summarize(ticket, spotlighted=False):
            nonlocal usage
            if spotlighted:
                result = client.chat(SPOTLIGHT_SYSTEM_PROMPT, spotlight_task(ticket))
            else:
                result = client.chat(SYSTEM_PROMPT, build_task(ticket))
            usage = result
            return result.content

        if defended:
            matched = _defenses.input_guardrail(message)
            if matched:
                reply = _defenses.REFUSAL_MESSAGE
                blocked_by = "input_guardrail"
                compromised = False
            else:
                reply = _summarize(message, spotlighted=True)
                if _defenses.output_guardrail(reply, markers):
                    reply = _defenses.REFUSAL_MESSAGE
                    blocked_by = "output_guardrail"
                    compromised = False
                else:
                    compromised = False
        else:
            reply = _summarize(message, spotlighted=False)
            compromised = hijacked(reply, markers)

        return {
            "reply": reply,
            "compromised": compromised,
            "blocked_by": blocked_by,
            "matched_pattern": matched,
            "usage": {
                "input_tokens": usage.input_tokens if usage else None,
                "output_tokens": usage.output_tokens if usage else None,
                "model": usage.model if usage else None,
            },
            "anatomy": self._anatomy(attack, compromised, blocked_by, matched),
        }


MODULE = _Module()
