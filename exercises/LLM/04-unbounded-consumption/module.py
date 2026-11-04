"""Registers a deterministic resource exhaustion simulation for the lab kit."""

from __future__ import annotations

from attacks import ATTACKS

REQUEST_LIMIT = 10
INPUT_TOKEN_LIMIT = 1200
OUTPUT_TOKEN_LIMIT = 800


class _Module:
    id = "04-unbounded-consumption"
    title = "4. Unbounded Consumption"
    owasp = "OWASP LLM06:2026 Unbounded Consumption"
    intro = (
        "Explore how repeated requests, oversized inputs, and runaway outputs "
        "can exhaust an AI application's resources. Every token and request "
        "shown here is simulated. No model is called and no cost is incurred."
    )
    context = (
        "An AI application can become expensive or unavailable if it accepts "
        "unlimited requests or lets one request consume too many tokens. The "
        "attacks below are simulated batches. They do not send traffic to a "
        "real service and do not call Ollama.\n\n"
        "Turn the Defense layer ON to apply an example request limit, input "
        "token limit, and output token limit. These example controls reduce the "
        "simulated resource use but do not cover every LLM06:2026 risk. A "
        "production system also needs token-aware cost budgets, hard spending "
        "caps, monitoring, and circuit breakers for agent or tool loops."
    )
    flow = [
        "Attacker sends requests",
        "Requests consume tokens",
        "No usage limits apply",
        "Budget is exhausted",
        "Service or cost is impacted",
    ]
    visual_sequence = [
        {"type": "attack", "icon": "🔁", "title": "Attacker creates excess load", "text": "Repeated requests or an oversized prompt ask the AI service to do more work than necessary."},
        {"type": "exposure", "icon": "📨", "title": "Work reaches the model", "text": "Each accepted request consumes input tokens, output tokens, and compute resources."},
        {"type": "weakness", "icon": "📈", "title": "Usage has no useful ceiling", "text": "Without quotas and token limits, one user or request can consume a disproportionate share of resources."},
        {"type": "control", "icon": "🛡️", "title": "Limit use and watch cost", "text": "This demo caps request and token counts. Production systems also need token-aware cost budgets, hard spending caps, monitoring, and circuit breakers."},
        {"type": "safe", "icon": "✅", "title": "Excess work is limited", "text": "The application accepts only work within its configured limits and blocks or truncates the excess."},
    ]
    scenario_title = "AI service resource budget"
    scenario = (
        "This mock service has an illustrative budget of 12,000 tokens per "
        "demonstration. The usage meter compares each simulated batch with that "
        "budget. With defenses on, it allows up to 10 requests, 1,200 input "
        "tokens per request, and 800 output tokens per request. These are "
        "teaching limits, not a complete production spending control."
    )
    input_title = "Choose a simulated request pattern"
    input_label = (
        "Pick a preset to simulate the load, or describe a custom request. "
        "Nothing is sent to a model or external service."
    )
    input_placeholder = "Describe a request pattern to simulate..."
    success_label = "COST SPIKE: simulated budget exceeded"
    safe_label = "LIMITED: resource controls applied"
    highlights = []
    attacks = ATTACKS
    simulation = {"budget_tokens": 12000}

    def _find(self, attack_id):
        for attack in self.attacks:
            if attack["id"] == attack_id:
                return attack
        return None

    def ask(self, message: str, attack_id, defended: bool) -> dict:
        attack = self._find(attack_id)
        technique = attack["technique"] if attack else "Custom request pattern"
        requested = {
            "requests": attack["requests"] if attack else 1,
            "input_tokens": attack["input_tokens"] if attack else max(1, len(message) // 4),
            "output_tokens": attack["output_tokens"] if attack else 1200,
        }

        requests = min(requested["requests"], REQUEST_LIMIT) if defended else requested["requests"]
        input_tokens = min(requested["input_tokens"], INPUT_TOKEN_LIMIT) if defended else requested["input_tokens"]
        output_tokens = min(requested["output_tokens"], OUTPUT_TOKEN_LIMIT) if defended else requested["output_tokens"]
        blocked_requests = requested["requests"] - requests
        total_tokens = requests * (input_tokens + output_tokens)
        limited = defended and (
            blocked_requests > 0
            or input_tokens < requested["input_tokens"]
            or output_tokens < requested["output_tokens"]
        )
        compromised = not defended and total_tokens > self.simulation["budget_tokens"]
        blocked_by = "resource_limits" if limited else None

        event = {
            "requests": requests,
            "blocked_requests": blocked_requests,
            "input_tokens": requests * input_tokens,
            "output_tokens": requests * output_tokens,
            "total_tokens": total_tokens,
        }
        if defended:
            reply = (
                f"Simulation only. No model is called and no cost is incurred. "
                f"{requests} request(s) accepted and "
                f"{blocked_requests} blocked. Input capped at {input_tokens:,} "
                f"tokens per request and output capped at {output_tokens:,}. "
                f"Accepted work used {total_tokens:,} simulated tokens."
            )
        else:
            reply = (
                f"Simulation only. No model is called and no cost is incurred. "
                f"{requests} request(s) accepted with no "
                f"request or token limits. The batch used {total_tokens:,} "
                f"simulated tokens against the illustrative "
                f"{self.simulation['budget_tokens']:,} token budget."
            )

        impact = (
            f"The simulated batch uses {total_tokens:,} tokens against a "
            f"{self.simulation['budget_tokens']:,} token budget."
        )
        if limited:
            exploitation = (
                "The resource controls capped the request batch or token size "
                "before the simulated budget could be exhausted."
            )
            why = (
                "Request quotas limit how much work one caller can submit. "
                "Input and output limits bound the work required for each "
                "request. Production systems should also monitor usage and "
                "adjust limits to their service and users."
            )
            impact = "Excess work was blocked or capped. The simulated budget stayed protected."
        elif compromised:
            exploitation = (
                "The service accepted an oversized batch without any request "
                "or token limits."
            )
            why = (
                "Unbounded consumption occurs when an application allows "
                "requests to consume excessive resources. Repeated calls and "
                "very large inputs or outputs can raise operating costs or "
                "reduce availability."
            )
        else:
            exploitation = "The simulated request stayed within the illustrative resource budget."
            why = "The example did not exceed the budget. Try a preset attack to see the resource controls in action."

        return {
            "reply": reply,
            "compromised": compromised,
            "blocked_by": blocked_by,
            "blocked_label": "LIMITED by resource controls" if limited else None,
            "matched_pattern": None,
            "usage": {
                "input_tokens": event["input_tokens"],
                "output_tokens": event["output_tokens"],
                "model": "deterministic simulation",
            },
            "simulation_event": event,
            "anatomy": {
                "technique": technique,
                "why": why,
                "compromised": compromised,
                "blocked_by": blocked_by,
                "matched_pattern": None,
                "stages": [
                    {"name": "1. Reconnaissance", "text": "The attacker identifies an AI service with valuable or costly processing."},
                    {"name": "2. Payload crafting", "text": f"The attacker chooses a resource exhaustion pattern: {technique}."},
                    {"name": "3. Delivery", "text": "The simulated batch reaches the application. No network traffic or model calls are made."},
                    {"name": "4. Exploitation", "text": exploitation},
                    {"name": "5. Impact", "text": impact},
                ],
            },
        }


MODULE = _Module()
