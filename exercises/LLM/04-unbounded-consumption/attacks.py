"""Preset resource exhaustion scenarios for the LLM10 learning simulation."""

ATTACKS = [
    {
        "id": "request_burst",
        "technique": "Repeated request burst",
        "description": "Many small requests consume resources through volume.",
        "payload": "Simulate a burst of repeated requests.",
        "requests": 25,
        "input_tokens": 180,
        "output_tokens": 900,
    },
    {
        "id": "oversized_prompt",
        "technique": "Oversized prompt",
        "description": "An unusually large input consumes resources before a useful answer is produced.",
        "payload": "Simulate an oversized prompt containing 16,000 tokens.",
        "requests": 1,
        "input_tokens": 16000,
        "output_tokens": 1200,
    },
    {
        "id": "runaway_output",
        "technique": "Unbounded output",
        "description": "A request encourages the application to generate an excessively long response.",
        "payload": "Simulate a request that generates 40,000 output tokens.",
        "requests": 1,
        "input_tokens": 220,
        "output_tokens": 40000,
    },
]
