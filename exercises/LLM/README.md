# Hands-on Exercises: Anatomy of an LLM Attack

A set of small, self-contained labs that show how attacks against Large
Language Model (LLM) applications actually work, and how to defend against
them. The first two labs run locally with [Ollama](https://ollama.com). The
other two are deterministic simulations. Automated tests verify the lab
behavior.

## How the labs are structured

Every exercise follows the same shape so you always know what to expect:

- **The big idea**: the attack in plain language.
- **Anatomy of the attack**: the attack broken into five stages
  (Reconnaissance to Payload crafting to Delivery to Exploitation to Impact).
- **Step-by-step tasks**: each with a clear action and an expected result.
- **Defenses and mitigations**: what actually reduces the risk.
- **Validate it yourself**: a test suite that proves the lab works.

## Prerequisites (shared by all exercises)

1. Python 3.9 or newer.
2. For Exercises 1 and 2, [Ollama](https://ollama.com/download) installed and running.
3. For Exercises 1 and 2, a small chat model pulled locally:
   ```bash
   ollama pull qwen2.5:1.5b
   ```
   The initial download requires internet access. Once downloaded, the labs send model requests to Ollama on your computer.

Exercises 3 and 4 are deterministic simulations. They do not require Ollama or a model. No external Python packages are required.

## Run the labs (one launcher, a dropdown to switch)

All exercises run in one web app with a dropdown at the top to switch between
them. From the repository root, start it from the `exercises/LLM` directory:

```bash
cd exercises/LLM
python3 serve.py
```

Then open <http://localhost:8000> and pick an exercise from the **Exercise**
dropdown. The top bar also has a **Defense layer** toggle (to see attacks get
blocked) and an expandable **Model info** panel (model name, size, and the
token usage of your last request).

You can also run any single exercise on its own from its folder, for example
`python3 run_lab.py` for the command line version and `python3 -m unittest` for
its tests.

## Exercises

| # | Exercise | Attack pattern | OWASP GenAI LLM Top 10 2026 |
|---|----------|----------------|-----------------------------|
| 1 | [Direct Prompt Injection](01-prompt-injection/) | Override a system prompt to reveal a secret | LLM01:2026 |
| 2 | [Indirect Prompt Injection](02-indirect-prompt-injection/) | Hide an attack inside a document the bot reads | LLM01:2026 |
| 3 | [Excessive Agency](03-excessive-agency/) | Trick a tool-using agent into a dangerous action | LLM03:2026 |
| 4 | [Unbounded Consumption](04-unbounded-consumption/) | Simulate how excessive requests or token use can exhaust resources | LLM06:2026 |

The 2026 list changed several category numbers and broadened some scopes. Excessive Agency is now LLM03, Unbounded Consumption is now LLM06, and System Prompt Leakage is now the broader LLM08 Hidden Context Exposure. Prompt Injection remains LLM01. See the [official 2026 release](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) for the complete list.

## Project layout

```
exercises/
  serve.py                       one launcher for all exercises
  labkit/                        shared web server, UI, model client
  01-prompt-injection/           Exercise 1 (direct)
  02-indirect-prompt-injection/  Exercise 2 (indirect)
  03-excessive-agency/           Exercise 3 (tool misuse)
  04-unbounded-consumption/      Exercise 4 (resource exhaustion simulation)
  test_labkit.py                 integration tests for the launcher
```

_More exercises coming next._

---

*Created by [**Razi Rais**](https://razibinrais.com) · Copyright © 2026 [Razi Rais](https://razibinrais.com) · [AI lab source code on GitHub](https://github.com/razi-rais/Anatomy-of-Cyberattack/tree/main/exercises/LLM) · Licensed under the [MIT License](../../LICENSE).*
