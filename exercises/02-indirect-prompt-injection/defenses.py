"""Defenses for the Indirect Prompt Injection lab.

Two layers, the same idea as Exercise 1 but tuned for untrusted documents:

1. Input guardrail: scan the incoming ticket for instruction-like content and
   for references to the protected secret, and refuse it before the model runs.
2. Output guardrail: scan the summary for the secret or an injected marker and
   block it before it reaches staff.

The output guardrail is the backstop. A polite exfiltration ticket can read like
a normal request and slip past the input scan, but the secret still cannot leave
because the summary is checked on the way out.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from judge import hijacked

REFUSAL_MESSAGE = (
    "This ticket was blocked because it contains instructions or a request for "
    "protected internal data. Summarize a normal customer ticket instead."
)

INJECTION_RULES = [
    (r"ignore (all|any|the)? ?(previous|prior|above) instructions",
     "Catches 'ignore previous instructions' hidden inside the ticket body."),
    (r"stop summarizing",
     "Catches an attempt to switch the bot off its real summarizing task."),
    (r"escalation code",
     "Catches any reference to the protected secret. A ticket has no reason to mention it."),
    (r"<!--",
     "Catches an HTML comment, a common place to hide instructions in documents."),
]

_COMPILED = [(re.compile(pattern, re.IGNORECASE), desc) for pattern, desc in INJECTION_RULES]


def describe_pattern(pattern: str) -> str:
    for raw, desc in INJECTION_RULES:
        if raw == pattern:
            return desc
    return "Matched a known indirect-injection signature."


@dataclass
class DefendedResult:
    reply: str
    blocked_by: str | None
    matched_pattern: str | None = None


def input_guardrail(ticket: str) -> str | None:
    """Return the offending pattern if the ticket carries injection content."""
    for pattern, _desc in _COMPILED:
        if pattern.search(ticket):
            return pattern.pattern
    return None


def output_guardrail(reply: str, markers=None) -> bool:
    """Return True if the summary must be blocked (secret or marker present)."""
    return hijacked(reply, markers)


def summarize_defended(ticket: str, summarize_fn, markers=None) -> DefendedResult:
    """Run the ticket through the guardrail-wrapped summarizer.

    summarize_fn(ticket) -> str produces the model summary. It is passed in so
    this function stays easy to test with a mock.
    """
    matched = input_guardrail(ticket)
    if matched:
        return DefendedResult(REFUSAL_MESSAGE, "input_guardrail", matched)

    reply = summarize_fn(ticket)

    if output_guardrail(reply, markers):
        return DefendedResult(REFUSAL_MESSAGE, "output_guardrail")

    return DefendedResult(reply, None)
