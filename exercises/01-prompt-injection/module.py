"""Registers Exercise 1 (Direct Prompt Injection) as a lab kit module.

This adapter reuses the existing Exercise 1 files (attacks.py, defenses.py,
customercare_bot.py, judge.py) and wires them to the shared lab kit so the
combined launcher can show this exercise in the dropdown. It uses the shared
Ollama client so the UI can also display token usage.

The standalone webapp.py and the existing tests are not affected.
"""

from __future__ import annotations

import attacks as _attacks
import defenses as _defenses
from customercare_bot import SECRET_DISCOUNT_CODE, SYSTEM_PROMPT
from judge import secret_leaked

from labkit import anatomy
from labkit.ollama import OllamaClient


class _Module:
    id = "01-prompt-injection"
    title = "1. Direct Prompt Injection"
    owasp = "OWASP LLM01 Prompt Injection"
    intro = (
        "The bot is told to protect a secret discount code. You type messages "
        "straight to it and try to make it break its own rule. Turn on the "
        "Defense layer to watch the same attack get blocked."
    )
    context = (
        "You are talking to Contoso CustomerCare Bot. A developer gave it a "
        "system prompt, which is its private rulebook. That rulebook hides a "
        "secret discount code and orders the bot never to reveal it.\n\n"
        "In this exercise YOU are the attacker, and you type directly into the "
        "chat. Here is the weakness you will exploit: the model reads the "
        "developer's rules and your message as one single block of text, with "
        "no hard wall between trusted rules and untrusted input. By writing "
        "your message as a more forceful, more recent instruction, you can make "
        "the model obey you instead of the developer and print the secret.\n\n"
        "Turn the Defense layer ON to add guardrails that scan your message "
        "before the model sees it, and scan the reply before you see it."
    )
    flow = [
        "You type an attack",
        "It lands in the user prompt",
        "Model sees rules + attack as one text",
        "Attack outranks the rule",
        "Secret leaks",
    ]
    scenario_title = "The guardrail (system prompt)"
    scenario = SYSTEM_PROMPT
    input_title = "Send a message to the bot"
    input_label = "Type a message, or click an attack on the left."
    input_placeholder = "Type a message to the bot..."
    success_label = "LEAK: secret revealed!"
    safe_label = "SAFE: secret protected"
    highlights = [SECRET_DISCOUNT_CODE]
    attacks = _attacks.ATTACKS

    def _find(self, attack_id):
        for a in self.attacks:
            if a["id"] == attack_id:
                return a
        return None

    def _anatomy(self, attack, compromised, blocked_by, matched):
        technique = attack["technique"] if attack else "Custom / free-form payload"
        return anatomy.build(
            stage_intro=[
                "The bot holds a confidential discount code and a rule never to reveal it.",
                f"The attacker writes a chat message designed to override that rule ({technique}).",
                "The payload is sent straight to the bot as a normal chat message.",
            ],
            technique=technique,
            attack=attack,
            compromised=compromised,
            blocked_by=blocked_by,
            matched_pattern=matched,
            pattern_description=_defenses.describe_pattern(matched) if matched else "",
            impact_success=f"Secret leaked. The confidential code {SECRET_DISCOUNT_CODE} was exposed.",
            impact_safe="No leak. The confidential code stayed protected this time.",
            impact_blocked="No leak. The guardrail layer stopped the attack.",
            output_guard_explainer=(
                "the output guardrail runs the model's reply through the leak "
                "detector (judge.py). It normalizes the text (collapses spaces "
                "and dashes, ignores case) and checks whether the secret is present."
            ),
        )

    def ask(self, message: str, attack_id, defended: bool) -> dict:
        attack = self._find(attack_id)
        client = OllamaClient()
        usage = None
        blocked_by = None
        matched = None

        if defended:
            matched = _defenses.input_guardrail(message)
            if matched:
                reply = _defenses.REFUSAL_MESSAGE
                blocked_by = "input_guardrail"
                compromised = False
            else:
                result = client.chat(SYSTEM_PROMPT, message)
                usage = result
                if secret_leaked(result.content):
                    reply = _defenses.REFUSAL_MESSAGE
                    blocked_by = "output_guardrail"
                    compromised = False
                else:
                    reply = result.content
                    compromised = False
        else:
            result = client.chat(SYSTEM_PROMPT, message)
            usage = result
            reply = result.content
            compromised = secret_leaked(reply)

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
