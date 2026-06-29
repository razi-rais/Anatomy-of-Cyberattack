<h1 align="center">Anatomy of a Cyberattack</h1>

<p align="center">
  Course resources and hands-on labs by <strong>Razi Rais</strong>, focused on modern AI threats and web security.
</p>

<p align="center">
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
  LLM/         LLM and agent security labs (three exercises plus a shared web runner)
  bots/        web security demo for bot and DDoS protection with Cloudflare Turnstile
  deepfakes/   reference material on synthetic media
```

## Hands-on labs

### AI application security

Local labs on the most common ways large language models and agents are attacked. Each lab maps to an entry in the OWASP Top 10 for LLM and Agentic Applications, explains the anatomy of the attack, and shows the control that stops it.

| Lab | Attack pattern | OWASP |
| --- | --- | --- |
| [Direct prompt injection](exercises/LLM/01-prompt-injection/) | A user crafts input that overrides the system instructions of a chatbot. | LLM01 |
| [Indirect prompt injection](exercises/LLM/02-indirect-prompt-injection/) | Malicious instructions arrive inside content the model is asked to summarize. | LLM01 |
| [Excessive agency](exercises/LLM/03-excessive-agency/) | An agent is tricked into calling tools it should never have been allowed to use. | LLM06 |

Run all three in one browser app with a dropdown to switch between them:

```bash
cd exercises/LLM
python3 serve.py
```

The LLM labs run fully offline against a local Ollama model. Each exercise folder also has its own README and command line runner.

### Web security

A standalone demo that shows how a web application separates real visitors from automated abuse using Cloudflare Turnstile, with a server side verification step and clear architecture and sequence diagrams.

```bash
cd exercises/bots
python3 server.py
```

See [`exercises/bots/`](exercises/bots/) for the full walkthrough.

## Reference reports

Background reading that informs the labs:

- [OWASP Top 10 for LLM Applications](<OWSAP-TOP10-LLM.pdf>)
- [OWASP Top 10 for Agentic Applications](<OWASP-Top-10-for-Agentic-Applications..pdf>)
- [OWASP Guide for Preparing and Responding to Deepfake Events](<1 OWASP-Top10-for-LLM-Guide-for-Preparing-and-Responding-to-Deepfake-Events-9.23.24-1.pdf>)
- [Microsoft Digital Defense Report 2025](<Microsoft-Digital-Defense-Report-2025.pdf>)
- [FBI IC3 Internet Crime Report 2025](<2025_IC3Report.pdf>)

## Responsible use

These labs are provided for educational purposes only. Do not use these techniques against any system without explicit authorization. Use them only on systems you own or are authorized to test, and always in line with applicable laws and your organization's policies.

The materials in this repository are provided "as is", without warranty of any kind, express or implied. The author assumes no liability and is not responsible for any misuse, damage, or loss arising from the use of this material. You are solely responsible for your own actions and for ensuring that your use complies with all applicable laws and regulations.

## Connect

This repository is part of the [**Anatomy of a Cyberattack**](https://www.oreilly.com/live-events/anatomy-of-a-cyberattack/0642572013682/) live training on O'Reilly.

Connect with Razi on [**LinkedIn**](https://www.linkedin.com/in/razirais) and follow along for other trainings and free webinars on AI and web security.

---

*Created by **Razi Rais** · https://razibinrais.com · Licensed under the [MIT License](LICENSE).*
