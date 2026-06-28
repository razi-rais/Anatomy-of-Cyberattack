"""Defenses for the CustomerCare Bot, the "AFTER" side of the demo.

The lab's whole point is that a raw model has no built-in boundary between
trusted instructions and untrusted user input. Real products add a *guardrail
layer* around the model. This module implements two simple, classic guardrails
so you can show the same attack going from LEAK to SAFE:

1. Input guardrail: inspect the USER message before it reaches the model and
   block known injection patterns.
2. Output guardrail: inspect the MODEL reply before it reaches the user and
   block anything that contains the secret.

The output guardrail is the reliable backstop: even if a clever payload slips
past the input filter and tricks the model, the secret never leaves the system.

These are intentionally simple (regex + substring) so they are easy to read in
a demo. Production guardrails use the same *idea* but more robust detectors.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from customercare_bot import OllamaClient, respond
from judge import secret_leaked

REFUSAL_MESSAGE = (
    "I can't help with that request. If you'd like assistance with another "
    "topic, feel free to ask."
)

# Signatures of common prompt-injection attempts. Matching is case-insensitive.
# Each pattern is paired with a plain-English description of what it catches,
# so the UI can explain exactly which rule fired and why.
INJECTION_RULES = [
    (r"ignore (all|any|the)? ?(previous|prior|above) instructions",
     "Catches 'ignore previous/prior instructions', the classic override phrase."),
    (r"disregard (all|any|the)? ?(previous|prior|above)",
     "Catches 'disregard previous/above', a synonym for the override phrase."),
    (r"developer (mode|debug)",
     "Catches fake 'developer mode' personas used to pretend the rules are off."),
    (r"debug mode",
     "Catches fake 'debug mode' personas used to pretend the rules are off."),
    (r"end of system prompt",
     "Catches a forged 'END OF SYSTEM PROMPT' delimiter used to fake a new instruction."),
    (r"new system (message|prompt)",
     "Catches a forged '[NEW SYSTEM MESSAGE]' header used to impersonate the developer."),
    (r"you are now",
     "Catches 'you are now <persona>', the setup for a role-play jailbreak."),
    (r"no restrictions",
     "Catches 'no restrictions', a phrase that tries to lift the safety rules."),
    (r"discount code",
     "Catches any direct reference to the protected secret. A normal shopper has no reason to ask for it."),
]

INJECTION_PATTERNS = [pattern for pattern, _desc in INJECTION_RULES]

_COMPILED = [(re.compile(pattern, re.IGNORECASE), desc) for pattern, desc in INJECTION_RULES]


def describe_pattern(pattern: str) -> str:
    """Return the human-readable description for a matched pattern."""
    for raw, desc in INJECTION_RULES:
        if raw == pattern:
            return desc
    return "Matched a known prompt-injection signature."


@dataclass
class DefendedResult:
    reply: str
    blocked_by: str | None  # "input_guardrail", "output_guardrail", or None
    matched_pattern: str | None = None


def input_guardrail(message: str) -> str | None:
    """Return the offending pattern if the message looks like an injection."""
    for pattern, _desc in _COMPILED:
        if pattern.search(message):
            return pattern.pattern
    return None


def output_guardrail(reply: str) -> bool:
    """Return True if the model's reply must be blocked (it leaks the secret)."""
    return secret_leaked(reply)


def respond_defended(message: str, client: OllamaClient | None = None) -> DefendedResult:
    """Run the user message through the guardrail-wrapped pipeline.

    Order matters: cheap input check first, then call the model, then the
    output check as a final backstop.
    """
    matched = input_guardrail(message)
    if matched:
        return DefendedResult(REFUSAL_MESSAGE, "input_guardrail", matched)

    reply = respond(message, client=client)

    if output_guardrail(reply):
        return DefendedResult(REFUSAL_MESSAGE, "output_guardrail")

    return DefendedResult(reply, None)
