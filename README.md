<h1 align="center">Anatomy of a Cyberattack</h1>

<p align="center">
  Course resources and hands-on labs created by <strong>Razi Rais</strong>, copyright © 2026 Razi Rais, including AI security labs mapped to the OWASP GenAI LLM Top 10 2026.
</p>

<p align="center">
  <a href="https://github.com/razi-rais/Anatomy-of-Cyberattack">Demo source code on GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/">OWASP GenAI LLM Top 10 2026</a>
  &nbsp;·&nbsp;
  <a href="https://www.oreilly.com/live-events/anatomy-of-a-cyberattack/0642572013682/"><strong>Live training on O'Reilly</strong></a>
  &nbsp;·&nbsp;
  <a href="#hands-on-labs">Hands-on labs</a>
  &nbsp;·&nbsp;
  <a href="#reference-reports">Reference reports</a>
  &nbsp;·&nbsp;
  <a href="#connect">Connect</a>
</p>

---

## About this repository

This is the companion repository for the [**Anatomy of a Cyberattack**](https://www.oreilly.com/live-events/anatomy-of-a-cyberattack/0642572013682/) live training by [**Razi Rais**](https://razibinrais.com). It pairs short readings with self-contained labs you can run on your own machine. The labs walk through how real attacks take shape, where they break trust boundaries, and which controls stop them. Connect with Razi on [LinkedIn](https://www.linkedin.com/in/razirais) to attend upcoming webinars and stay current with recent happenings in AI and security.

The material covers two areas that increasingly overlap in practice:

- **AI application security.** How attackers manipulate large language models and agents, and how to defend them.
- **Web security.** How automated traffic and abuse reach web applications, and how to filter it before it does damage.

Every lab is backed by automated tests so you can verify that each attack and each defense behaves as described.

## Repository structure

```text
exercises/
  LLM/         LLM and agent security labs (four exercises plus a shared web runner)
  bots/        web security demo for bot and DDoS protection with Cloudflare Turnstile
  deepfakes/   reference material on synthetic media
```

## Hands-on labs

For setup instructions, a walkthrough with clear steps, and troubleshooting, see the [Getting Started guide](GETTING-STARTED.md).

### AI application security

Local labs on common ways large language model applications are attacked. The labels use the OWASP GenAI LLM Top 10 2026. Each lab explains an attack and shows controls that can reduce its impact.

| Lab | Attack pattern | OWASP GenAI LLM Top 10 2026 |
| --- | --- | --- |
| [Direct prompt injection](exercises/LLM/01-prompt-injection/) | A user crafts input that overrides the system instructions of a chatbot. | LLM01:2026 Prompt Injection |
| [Indirect prompt injection](exercises/LLM/02-indirect-prompt-injection/) | Malicious instructions arrive inside content the model is asked to summarize. | LLM01:2026 Prompt Injection |
| [Excessive agency](exercises/LLM/03-excessive-agency/) | An agent is tricked into calling tools it should not use. | LLM03:2026 Excessive Agency |
| [Unbounded consumption](exercises/LLM/04-unbounded-consumption/) | Repeated requests or oversized inputs and outputs consume excessive AI resources. | LLM06:2026 Unbounded Consumption |

These four labs cover three distinct 2026 categories. The two prompt injection labs share LLM01. The other covered categories are LLM03 and LLM06. The direct injection scenario also demonstrates extraction of a secret from hidden context, an outcome related to LLM08, but it does not teach the broader LLM08 risk as a separate lab.

The 2026 release changed several category numbers and broadened some scopes. Excessive Agency moved from LLM06 to LLM03. Unbounded Consumption moved from LLM10 to LLM06. System Prompt Leakage was broadened and renamed Hidden Context Exposure at LLM08. Prompt Injection remains LLM01. The [OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) is the current reference.

The other 2026 categories without a dedicated lab are **LLM02 Sensitive Information Disclosure**, **LLM04 Supply Chain**, **LLM05 Data and Model Poisoning**, **LLM07 Misinformation**, **LLM08 Hidden Context Exposure**, **LLM09 Vector and Embedding Weaknesses**, and **LLM10 Improper Output Handling**. LLM08 overlaps with the secret extraction example, but broader hidden-context exposure is not covered.

Run all four in one browser app with a dropdown to switch between them:

```bash
cd exercises/LLM
python3 serve.py
```

The first two LLM labs run against a local Ollama model. Internet access is needed for the initial Ollama and model downloads. After that, model requests stay on your computer. The excessive agency and unbounded consumption labs are deterministic simulations and do not use a model. Each exercise folder has its own README.

### Web security

A standalone demo that shows how a web application separates real visitors from automated abuse using Cloudflare Turnstile, with a server side verification step and clear architecture and sequence diagrams.

```bash
cd exercises/bots
python3 server.py
```

See [`exercises/bots/`](exercises/bots/) for the full walkthrough.

## Reference reports

Background reading that informs the labs:

- [OWASP GenAI LLM Top 10 2026, current release](<resources/OWASP-GENAI-LLM-TOP-10-2026-V1.0.PDF>)
- [OWASP Top 10 for Agentic Applications 2026](<resources/OWASP-TOP-10-AGENTIC-APPLICATIONS-2026.PDF>)
- [OWASP Guide for Preparing and Responding to Deepfake Events](<resources/OWASP-DEEPFAKE-EVENTS-GUIDE-2024.PDF>)
- [Microsoft Digital Defense Report 2026](<resources/MICROSOFT-DIGITAL-DEFENSE-REPORT-2026.PDF>)
- [FBI IC3 Internet Crime Report 2025](<resources/FBI-IC3-INTERNET-CRIME-REPORT-2025.PDF>)

## Responsible use

These labs are provided for educational purposes only. Do not use these techniques against any system without explicit authorization. Use them only on systems you own or are authorized to test, and always in line with applicable laws and your organization's policies.

The materials in this repository are provided "as is", without warranty of any kind, express or implied. The author assumes no liability and is not responsible for any misuse, damage, or loss arising from the use of this material. You are solely responsible for your own actions and for ensuring that your use complies with all applicable laws and regulations.

## Connect

This repository is part of the [**Anatomy of a Cyberattack**](https://www.oreilly.com/live-events/anatomy-of-a-cyberattack/0642572013682/) live training on O'Reilly.

Connect with Razi on [**LinkedIn**](https://www.linkedin.com/in/razirais) and follow along for other trainings and free webinars on AI and web security.

---

*Created by [**Razi Rais**](https://razibinrais.com) · Copyright © 2026 [Razi Rais](https://razibinrais.com) · [Demo source code on GitHub](https://github.com/razi-rais/Anatomy-of-Cyberattack) · Licensed under the [MIT License](LICENSE).*
