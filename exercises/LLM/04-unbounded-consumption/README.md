# Exercise 4: Unbounded Consumption

> **Goal:** See how request bursts and oversized inputs or outputs can exhaust an AI application's resources, then apply request and token limits.
>
> **Maps to:** OWASP LLM06:2026 Unbounded Consumption

The category number changed in the 2026 release. Unbounded Consumption was **LLM10:2025** and is **LLM06:2026**.

## What you will learn

- Explain how unlimited requests and token use can increase cost or reduce availability.
- Compare repeated requests, an oversized prompt, and excessive output.
- Apply example request, input, and output limits.

## Run the demo

Start the shared browser app from the repository root:

```bash
cd exercises/LLM
python3 serve.py
```

Open <http://localhost:8000> and select **4. Unbounded Consumption**. Choose each preset with the Defense layer off, then turn it on and repeat. The usage meter shows the simulated token use for each batch. Use **Clear usage display** before another comparison if you want to reset the meter.

The simulation does not call Ollama, contact a remote service, generate real traffic, or incur a charge. Its budget and limits are illustrative. In production, set request quotas and token caps appropriate to the service, and monitor for unusual usage.

At the bottom of the page, open the collapsible visual sequence to see the attack path and the controls that stop it.

## Controls shown

The defended simulation allows up to 10 requests, 1,200 input tokens per request, and 800 output tokens per request. With the defense layer off, each preset runs without those limits. The usage meter compares each batch with an illustrative 12,000 token budget. These example limits are not a complete production defense for LLM06:2026. Production systems also need token-aware cost budgets, enforceable spending caps, usage monitoring, and circuit breakers for agent or tool loops.
