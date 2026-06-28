"""Shared anatomy builder for the lab kit.

Every exercise explains an attack as five stages:

    1. Reconnaissance
    2. Payload crafting
    3. Delivery
    4. Exploitation
    5. Impact

Stages 1 to 3 are scenario specific text that each exercise supplies. Stages 4
and 5 are derived from the outcome (compromised, blocked by a guardrail, or
safe). When a guardrail blocks the attack the explanation is attack specific and
also carries a learning note about how real commercial guardrails work, with
references.
"""

from __future__ import annotations

COMMERCIAL_GUARDRAILS_NOTE = (
    "For real systems (this is a learning lab): the rules here are simple "
    "regular expressions so you can SEE the idea clearly. Commercial assistants "
    "rarely rely on keyword matching alone, because an attacker can reword a "
    "payload in endless ways that no blocklist can list out in advance. "
    "Production guardrails instead use trained machine-learning classifiers "
    "that judge the MEANING and intent of a message, not just its exact words. "
    "They reason over embeddings and dedicated safety models, they run as "
    "separate services wrapped around the model so they can be improved without "
    "retraining it, and they are red-teamed and updated continuously as new "
    "attacks appear.\n\n"
    "A few real guardrail systems you can read about:\n"
    "- OWASP Top 10 for LLM Applications (LLM01 Prompt Injection): https://genai.owasp.org\n"
    "- Microsoft Azure AI Content Safety, Prompt Shields: https://learn.microsoft.com/en-us/azure/ai-services/content-safety/how-to-prompt-shields\n"
    "- Meta Llama Guard (an LLM that screens inputs and outputs): https://github.com/meta-llama/llama-guard\n"
    "- NVIDIA NeMo Guardrails: https://github.com/NVIDIA/NeMo-Guardrails\n"
    "- OpenAI Moderation guide: https://platform.openai.com/docs/guides/moderation\n\n"
    "The takeaway: the CONCEPT you just saw (check the input, check the output, "
    "keep the secret out of reach) is exactly what production systems do. They "
    "just do it with much smarter detectors than a regex."
)


def build(
    *,
    stage_intro: list[str],
    technique: str,
    attack: dict | None,
    compromised: bool,
    blocked_by: str | None,
    matched_pattern: str | None,
    pattern_description: str,
    impact_success: str,
    impact_safe: str,
    impact_blocked: str,
    input_guard_label: str = "input guardrail",
    output_guard_explainer: str = "",
    defense_note: str = "",
) -> dict:
    """Assemble the anatomy dict the UI renders.

    stage_intro must be three strings: the Reconnaissance, Payload crafting and
    Delivery stage texts for this exercise.
    """
    recon, craft, deliver = stage_intro

    if blocked_by == "input_guardrail":
        exploitation = (
            f"Blocked BEFORE the model. The {input_guard_label} matched the rule "
            f"/{matched_pattern}/ and recognized this as a '{technique}' attempt, "
            "so it refused without ever calling the model."
        )
        impact = impact_blocked
        parts = []
        if attack and attack.get("description"):
            parts.append(f"How this attack tries to work: {attack['description']}")
        parts.append(
            "What the guardrail did: it ran the raw, untrusted text through the "
            "regular-expression rules in defenses.py before the model was "
            f"called, and this rule fired:\n\n    /{matched_pattern}/\n\n"
            f"What that rule catches: {pattern_description}"
        )
        if attack and attack.get("defense"):
            parts.append(f"Why that defeats THIS specific attack: {attack['defense']}")
        if defense_note:
            parts.append(defense_note)
        parts.append(COMMERCIAL_GUARDRAILS_NOTE)
        why = "\n\n".join(parts)
    elif blocked_by == "output_guardrail":
        exploitation = (
            f"This '{technique}' attack slipped past the input checks and tricked "
            "the model. The output guardrail then scanned the reply, detected the "
            "forbidden content, and replaced it with a safe refusal before you "
            "saw it."
        )
        impact = impact_blocked
        parts = []
        if attack and attack.get("description"):
            parts.append(f"How this attack tries to work: {attack['description']}")
        parts.append(
            "What the guardrail did: " + (
                output_guard_explainer
                or "the output guardrail scans the model's reply and blocks it if "
                "it contains the protected secret or an injected marker."
            )
        )
        parts.append(
            "Why that defeats THIS specific attack: it does not matter how the "
            "model was tricked or how cleverly the payload was formatted. If the "
            "forbidden content appears in the reply, the reply is blocked. This "
            "is the backstop that catches novel payloads the input filter does "
            "not yet know about."
        )
        if defense_note:
            parts.append(defense_note)
        parts.append(COMMERCIAL_GUARDRAILS_NOTE)
        why = "\n\n".join(parts)
    elif compromised:
        exploitation = (
            "The model followed the attacker's text instead of its real task."
        )
        impact = impact_success
        why = attack["why"] if attack and attack.get("why") else (
            "The model treated attacker controlled text as a trusted instruction "
            "and carried it out."
        )
    else:
        exploitation = "The model resisted: it stuck to its real task and rules."
        impact = impact_safe
        why = attack["why"] if attack and attack.get("why") else (
            "The wording did not override the model's task this time. Try one of "
            "the preset attacks to compare."
        )

    return {
        "technique": technique,
        "why": why,
        "compromised": compromised,
        "blocked_by": blocked_by,
        "matched_pattern": matched_pattern,
        "stages": [
            {"name": "1. Reconnaissance", "text": recon},
            {"name": "2. Payload crafting", "text": craft},
            {"name": "3. Delivery", "text": deliver},
            {"name": "4. Exploitation", "text": exploitation},
            {"name": "5. Impact", "text": impact},
        ],
    }
