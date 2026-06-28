# Hands-on Exercises: Anatomy of an LLM Attack

A set of small, self-contained labs that show how attacks against Large
Language Model (LLM) applications actually work, and how to defend against
them. Each lab is hands-on, runs **locally** with [Ollama](https://ollama.com),
and is backed by automated tests so you can trust the results.

## How the labs are structured

Every exercise follows the same shape so you always know what to expect:

- **The big idea**: the attack in plain language.
- **Anatomy of the attack**: the attack broken into five stages
  (Reconnaissance to Payload crafting to Delivery to Exploitation to Impact).
- **Step-by-step tasks**: each with a clear action and an expected result.
- **Defenses and mitigations**: what actually reduces the risk.
- **Validate it yourself**: a test suite that proves the lab works.

## Prerequisites (shared by all exercises)

1. [Ollama](https://ollama.com/download) installed and running.
2. A small chat model pulled locally:
   ```bash
   ollama pull qwen2.5:1.5b
   ```
3. Python 3.9+ (`python3 --version`). No third-party packages are required.

## Run the labs (one launcher, a dropdown to switch)

All exercises run in one web app with a dropdown at the top to switch between
them. Start it from this directory:

```bash
cd exercises
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

| # | Exercise | Attack pattern | OWASP |
|---|----------|----------------|-------|
| 1 | [Direct Prompt Injection](01-prompt-injection/) | Override a system prompt to leak a secret | LLM01 |
| 2 | [Indirect Prompt Injection](02-indirect-prompt-injection/) | Hide an attack inside a document the bot reads | LLM01 |
| 3 | [Excessive Agency](03-excessive-agency/) | Trick a tool-using agent into a dangerous action | LLM06 |

## Project layout

```
exercises/
  serve.py                       one launcher for all exercises
  labkit/                        shared web server, UI, model client
  01-prompt-injection/           Exercise 1 (direct)
  02-indirect-prompt-injection/  Exercise 2 (indirect)
  03-excessive-agency/           Exercise 3 (tool misuse)
  test_labkit.py                 integration tests for the launcher
```

_More exercises coming next._
